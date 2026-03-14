#!/usr/bin/env python3
"""Build a self-contained viewer.html from Lens of Power framework files.

Primary data source: YAML files in data/ (structured metadata, cross-references).
Markdown files are read for prose content (detail view rendering).

Usage: python3 tools/build-viewer.py
Output: viewer.html + viewer-data.js
"""

import json
import os
import re
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "viewer.html"
OUT_DATA = ROOT / "viewer-data.js"

LAYER_NAMES = [
    "Thought & Narrative",
    "Economic",
    "Legal & Regulatory",
    "Institutional",
    "Surveillance & Information",
    "Physical & Coercive",
]

LAYER_ID_TO_NAME = {
    "thought_narrative": "Thought & Narrative",
    "economic": "Economic",
    "legal_regulatory": "Legal & Regulatory",
    "institutional": "Institutional",
    "surveillance_information": "Surveillance & Information",
    "physical_coercive": "Physical & Coercive",
}


def layer_ids_to_names(ids: list) -> list:
    """Convert layer IDs to display names."""
    return [LAYER_ID_TO_NAME.get(lid, lid) for lid in (ids or [])]


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------

def load_yaml(filename: str) -> dict:
    """Load a YAML file from data/."""
    path = DATA / filename
    if not path.exists():
        return {"entries": []}
    with open(path) as f:
        return yaml.safe_load(f) or {"entries": []}


# ---------------------------------------------------------------------------
# Parsing helpers (kept for markdown content reading)
# ---------------------------------------------------------------------------

def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_title(content: str) -> str:
    """Extract the first H1 title from markdown."""
    m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return m.group(1).strip() if m else ""




# ---------------------------------------------------------------------------
# Metadata parsing (still used by build)
# ---------------------------------------------------------------------------


def parse_constitution(path: Path):
    """Extract axiom names from constitution.md."""
    content = read_file(path)
    axioms = re.findall(r"^### (\d+\.\s+.+)$", content, re.MULTILINE)
    return axioms


def parse_axiom_definitions(path: Path) -> list:
    """Extract axiom ID, title, and first paragraph from constitution.md."""
    content = read_file(path)
    defs = []
    parts = re.split(r"^### (\d+\.\s+.+)$", content, flags=re.MULTILINE)
    # parts: [preamble, heading1, body1, heading2, body2, ...]
    for i in range(1, len(parts) - 1, 2):
        heading = parts[i].strip()
        body = parts[i + 1].strip()
        m = re.match(r"(\d+)\.\s+(.+)", heading)
        if not m:
            continue
        num, title = m.group(1), m.group(2)
        # First paragraph: text before first blank line or > block
        para_lines = []
        for line in body.split("\n"):
            if not line.strip():
                if para_lines:
                    break
                continue
            if line.strip().startswith(">"):
                break
            para_lines.append(line.strip())
        short = " ".join(para_lines)
        if len(short) > 200:
            short = short[:197] + "..."
        defs.append({"id": f"Axiom {num}", "title": title, "short": short})
    return defs


def parse_ic_definitions(path: Path) -> list:
    """Extract IC constraint ID, title, and first paragraph from constitution.md."""
    content = read_file(path)
    defs = []
    for m in re.finditer(
        r"^### (IC-\d+):\s+(.+?)\n\n(.+?)(?=\n\n>|\n\n###|\n\n\||\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    ):
        ic_id, title, body = m.group(1), m.group(2), m.group(3).strip()
        short = body.split("\n")[0].strip()
        if len(short) > 200:
            short = short[:197] + "..."
        defs.append({"id": ic_id, "title": title, "short": short})
    return defs


def parse_position_definitions(path: Path) -> list:
    """Extract position ID, title, and description from positional-lens.md."""
    content = read_file(path)
    defs = []
    for m in re.finditer(
        r"^### Position (\d+):\s+(.+?)$\n.*?- \*\*Description\*\*:\s*(.+?)(?=\n- \*\*)",
        content,
        re.MULTILINE | re.DOTALL,
    ):
        num, title = m.group(1), m.group(2)
        desc = m.group(3).strip().replace("\n  ", " ").replace("\n", " ")
        # Take first sentence
        first_sent = re.split(r"(?<=[.!?])\s", desc)[0]
        if len(first_sent) > 200:
            first_sent = first_sent[:197] + "..."
        defs.append({"id": f"Position {num}", "title": title, "short": first_sent})
    return defs


def parse_taxonomy(path: Path):
    """Extract layer names from taxonomy.md."""
    content = read_file(path)
    layers = re.findall(r"^### \d+\.\s+(.+)$", content, re.MULTILINE)
    return layers


# ---------------------------------------------------------------------------
# README and taxonomy section extraction
# ---------------------------------------------------------------------------

def extract_readme_sections(path: Path) -> dict:
    """Extract key sections from README.md as markdown content."""
    content = read_file(path)
    sections = {}
    targets = {
        "core_concepts": "## Core concepts",
        "how_framework_grows": "## How the framework grows",
        "integrity_constraints": "## Integrity constraints",
    }
    for key, heading in targets.items():
        pattern = re.escape(heading) + r"(.*?)(?=\n## |\Z)"
        m = re.search(pattern, content, re.DOTALL)
        if m:
            sections[key] = m.group(1).strip()
    return sections


def extract_layer_descriptions(path: Path) -> list:
    """Extract layer names and first-paragraph descriptions from taxonomy.md."""
    content = read_file(path)
    layers = []
    parts = re.split(r"^### \d+\.\s+", content, flags=re.MULTILINE)
    for part in parts[1:]:
        lines = part.strip().split("\n")
        name = lines[0].strip()
        desc_lines = []
        for line in lines[1:]:
            if not line.strip():
                if desc_lines:
                    break
                continue
            if line.strip().startswith("**"):
                break
            desc_lines.append(line.strip())
        description = " ".join(desc_lines)
        layers.append({"name": name, "description": description})
    return layers


# ---------------------------------------------------------------------------
# Corroboration computation
# ---------------------------------------------------------------------------

def compute_corroboration(nodes, edges):
    """Compute dynamic corroboration metrics for each pattern.

    A source is "relevant" to a pattern if they share at least one taxonomy
    layer.  Corroboration = corroborating sources / relevant sources.

    Thresholds (hybrid — minimum count AND minimum hit rate):
      PRELIMINARY:  < 3 corroborating sources
      SUPPORTED:    >= 3 corroborating AND hit rate >= 10%
      ESTABLISHED:  >= 5 corroborating AND hit rate >= 20%
                    AND no unresolved counter-evidence
    """
    node_map = {n["id"]: n for n in nodes}
    patterns = [n for n in nodes if n["type"] == "pattern"]
    sources = [n for n in nodes if n["type"] in ("analysis", "principle")]

    # Build corroboration edges: which sources reference each pattern
    corroborating = {}  # pattern_id -> set of source_ids
    for e in edges:
        if e["type"] == "observed_in":
            corroborating.setdefault(e["source"], set()).add(e["target"])
        elif e["type"] in ("key_pattern", "matches"):
            corroborating.setdefault(e["target"], set()).add(e["source"])

    for p in patterns:
        p_layers = set(p["meta"].get("layer_list", []))
        pid = p["id"]

        # Relevant sources: those sharing at least one layer with the pattern
        relevant = set()
        for s in sources:
            s_layers = set(s["meta"].get("layer_list", []))
            if p_layers & s_layers:
                relevant.add(s["id"])

        corr_set = corroborating.get(pid, set())
        corr_count = len(corr_set)
        # Floor: can't have fewer relevant than corroborating
        rel_count = max(len(relevant), corr_count)
        hit_rate = corr_count / rel_count if rel_count > 0 else 0

        # Detect counter-evidence from existing text
        existing_corr = p["meta"].get("corroboration", "")
        has_counter = "counter" in existing_corr.lower()

        # Determine level
        if corr_count >= 5 and hit_rate >= 0.20 and not has_counter:
            level = "ESTABLISHED"
        elif corr_count >= 3 and hit_rate >= 0.10:
            level = "SUPPORTED"
        else:
            level = "PRELIMINARY"

        p["meta"]["corroboration"] = f"{level} ({corr_count} of {rel_count} relevant sources, {hit_rate:.0%})"
        p["meta"]["corr_level"] = level
        p["meta"]["corr_count"] = corr_count
        p["meta"]["corr_relevant"] = rel_count
        p["meta"]["corr_hit_rate"] = round(hit_rate, 3)
        p["meta"]["corr_has_counter"] = has_counter


def sync_corroboration_to_yaml(nodes):
    """Write computed corroboration values back to data/patterns.yaml.

    Updates confidence_level, confidence_ratio, and relevant_corpus_size
    so that generate-indexes.py can produce accurate CONFIDENCE lines.
    """
    patterns = [n for n in nodes if n["type"] == "pattern"]
    yaml_path = ROOT / "data" / "patterns.yaml"
    if not yaml_path.exists():
        return

    original = yaml_path.read_text(encoding="utf-8")
    data = yaml.safe_load(original)
    if not data:
        return

    # Build pattern title → computed values mapping
    computed = {}
    for p in patterns:
        computed[p["title"]] = {
            "confidence_level": p["meta"].get("corr_level", "PRELIMINARY"),
            "confidence_ratio": p["meta"].get("corr_hit_rate", 0.0),
            "relevant_corpus_size": p["meta"].get("corr_relevant", 0),
            "corr_count": p["meta"].get("corr_count", 0),
        }

    entries = data.get("entries", [])
    changed = False
    for entry in entries:
        name = entry.get("name", "")
        if name in computed:
            c = computed[name]
            for key in ("confidence_level", "confidence_ratio", "relevant_corpus_size", "corr_count"):
                if entry.get(key) != c[key]:
                    entry[key] = c[key]
                    changed = True

    if changed:
        # Preserve header comment
        marker = "\nentries:\n"
        idx = original.find(marker)
        header = original[:idx + 1] if idx != -1 else ""
        dumped = yaml.dump(
            {"entries": entries},
            default_flow_style=False,
            allow_unicode=True,
            width=120,
            sort_keys=False,
        )
        yaml_path.write_text(header + dumped, encoding="utf-8")
        print("Updated corroboration in data/patterns.yaml")


# ---------------------------------------------------------------------------
# Framework health metrics
# ---------------------------------------------------------------------------

def compute_health_metrics(nodes):
    """Compute framework health metrics from parsed nodes."""
    analyses = [n for n in nodes if n["type"] == "analysis"]
    evidence = [n for n in nodes if n["type"] == "evidence"]

    # 1. Evidence balance: count by relationship, overall and per axiom
    evidence_balance = {}
    axiom_balance = {}
    for e in evidence:
        rel = (e["meta"].get("relationship") or "").strip().lower()
        if rel in ("supports", "challenges", "complicates", "self-examination"):
            evidence_balance[rel] = evidence_balance.get(rel, 0) + 1
        axioms_str = e["meta"].get("axioms") or ""
        for ax in re.findall(r'\d+', axioms_str):
            if ax not in axiom_balance:
                axiom_balance[ax] = {}
            axiom_balance[ax][rel] = axiom_balance[ax].get(rel, 0) + 1

    # 2. Null case distribution from analysis content
    null_cases = {"rejected": 0, "plausible": 0, "accepted": 0}
    for a in analyses:
        content = a.get("content", "")
        m = re.search(
            r'\*?\*?Null case(?:\s+plausibility)?\*?\*?:?\s*'
            r'(HIGH|MEDIUM|LOW|rejected|plausible|accepted)',
            content, re.IGNORECASE,
        )
        if m:
            val = m.group(1).upper()
            if val == "HIGH":
                null_cases["accepted"] += 1
            elif val in ("MEDIUM", "MEDIUM-LOW"):
                null_cases["plausible"] += 1
            elif val == "LOW":
                null_cases["rejected"] += 1
            elif val.lower() in null_cases:
                null_cases[val.lower()] += 1

    # 3. Red team timing — use date+time for precise ordering
    def make_timestamp(node):
        """Build a sortable 'YYYY-MM-DD HH:MM' string from date + time fields."""
        d = node["meta"].get("date") or ""
        if not re.match(r'\d{4}-\d{2}-\d{2}', d):
            return ""
        d = d[:10]  # trim to YYYY-MM-DD
        t = node["meta"].get("time") or node.get("content", "")
        # Extract HH:MM from time field like "~18:00 UTC" or "TIME RECORDED: ~15:00 UTC"
        tm = re.search(r'TIME RECORDED:\s*~?(\d{1,2}:\d{2})', t)
        if not tm:
            tm = re.search(r'~?(\d{1,2}:\d{2})\s*UTC', node["meta"].get("time") or "")
        # If no time found, use 23:59 so same-day entries without times
        # sort after any timestamped entry on the same day.
        return d + " " + tm.group(1) if tm else d + " 23:59"

    last_red_team = None
    last_red_team_ts = ""
    last_red_team_id = None
    red_team_ids = []
    for e in evidence:
        rel = (e["meta"].get("relationship") or "").strip().lower()
        if rel == "self-examination":
            red_team_ids.append(e["id"])
            ts = make_timestamp(e)
            if ts and (not last_red_team_ts or ts > last_red_team_ts):
                last_red_team = (e["meta"].get("date") or "")[:10]
                last_red_team_ts = ts
                last_red_team_id = e["id"]
    analyses_since_red_team = len(analyses)
    if last_red_team_ts:
        analyses_since_red_team = sum(
            1 for a in analyses
            if make_timestamp(a) > last_red_team_ts
        )

    # 4. Calibration stats from data/calibration.yaml
    calibration = {"total": 0, "accepted": 0, "plausible": 0, "rejected": 0,
                   "unacted_escalations": 0}
    cal_yaml_path = ROOT / "data" / "calibration.yaml"
    if cal_yaml_path.exists():
        cal_data = yaml.safe_load(cal_yaml_path.read_text(encoding="utf-8")) or {}
        cal_stats = cal_data.get("stats", {})
        calibration["total"] = cal_stats.get("total_runs", 0) or cal_stats.get("total_samples", 0)
        calibration["accepted"] = cal_stats.get("accepted", 0) or cal_stats.get("null_accepted", 0)
        calibration["plausible"] = cal_stats.get("plausible", 0) or cal_stats.get("null_plausible", 0)
        calibration["rejected"] = cal_stats.get("rejected", 0) or cal_stats.get("null_rejected", 0)
        # Count unacted escalations from entries
        for entry in cal_data.get("entries", []):
            esc = (entry.get("escalation") or "").lower()
            if esc in ("analyze", "extract"):
                calibration["unacted_escalations"] += 1

    # 5. Adversarial ratio — from data/analyses.yaml
    adversarial_files = set()
    analyses_yaml_data = load_yaml("analyses.yaml")
    for a in analyses_yaml_data.get("entries", []):
        if a.get("adversarial"):
            adversarial_files.add(a["id"])
    # Also scan analysis content for legacy entries
    for a in analyses:
        if re.search(r'Adversarial input:\s*yes', a.get("content", ""), re.IGNORECASE):
            adversarial_files.add(a["id"])
    # Also scan INDEX.md for "Adversarial input: yes" entries (belt and suspenders)
    index_path = ROOT / "analyses" / "INDEX.md"
    if index_path.exists():
        index_text = index_path.read_text(encoding="utf-8")
        for block in re.split(r'\n###\s+', index_text):
            if re.search(r'Adversarial input:\s*yes', block, re.IGNORECASE):
                fm = re.search(r'File:\s*`?([^`\n]+\.md)', block)
                if fm:
                    adversarial_files.add("analyses/" + fm.group(1))
    adversarial_count = len(adversarial_files)

    return {
        "evidence_balance": evidence_balance,
        "axiom_balance": axiom_balance,
        "null_cases": null_cases,
        "last_red_team": last_red_team,
        "last_red_team_id": last_red_team_id,
        "red_team_ids": red_team_ids,
        "analyses_since_red_team": analyses_since_red_team,
        "total_analyses": len(analyses),
        "adversarial_count": adversarial_count,
        "calibration": calibration,
    }


# ---------------------------------------------------------------------------
# Main build (YAML-based)
# ---------------------------------------------------------------------------

def build():
    """Build viewer data from YAML + markdown files.

    YAML provides structured metadata and cross-references.
    Markdown provides prose content for the detail view.
    """
    nodes = []
    edges = []
    node_ids = set()

    def add_node(n):
        if n["id"] not in node_ids:
            nodes.append(n)
            node_ids.add(n["id"])

    # Load all YAML data
    config = load_yaml("config.yaml")
    analyses_yaml = load_yaml("analyses.yaml")
    patterns_yaml = load_yaml("patterns.yaml")
    principles_yaml = load_yaml("principles.yaml")
    evidence_yaml = load_yaml("evidence.yaml")
    circumventions_yaml = load_yaml("circumventions.yaml")
    instruments_yaml = load_yaml("instruments.yaml")
    calibration_yaml = load_yaml("calibration.yaml")

    # --- Patterns (from YAML + patterns/*.md content) ---
    pattern_content_map = {}
    patterns_dir = ROOT / "patterns"
    for entry in patterns_yaml.get("entries", []):
        pfile = entry.get("file")
        if pfile:
            ppath = ROOT / pfile
            if ppath.exists():
                pattern_content_map[entry["name"]] = read_file(ppath)

    for entry in patterns_yaml.get("entries", []):
        pid = "pattern:" + entry["name"]
        layer_names = layer_ids_to_names(entry.get("layers", []))
        obs_count = len(entry.get("observed_in", []))
        corpus = entry.get("relevant_corpus_size") or 0
        ratio = entry.get("confidence_ratio") or 0
        level = entry.get("confidence_level") or "PRELIMINARY"
        corr_str = f"{level} ({obs_count} of {corpus} relevant sources, {ratio:.0%})" if corpus else level
        counter_ev = entry.get("counter_evidence", [])

        # Extract STATEMENT from pattern markdown content
        pcontent = pattern_content_map.get(entry["name"], "")
        stmt_match = re.search(r"STATEMENT:\s*(.+?)(?:\n\n|\nMECHANISM:)", pcontent, re.DOTALL)
        statement = stmt_match.group(1).strip().replace("\n", " ") if stmt_match else ""

        add_node({
            "id": pid,
            "type": "pattern",
            "title": entry["name"],
            "content": pcontent,
            "meta": {
                "layers": ", ".join(layer_names),
                "layer_list": layer_names,
                "statement": statement,
                "mechanism": "",
                "corroboration": corr_str,
                "corr_level": level,
                "corr_count": obs_count,
                "corr_relevant": corpus,
                "corr_hit_rate": round(ratio, 3) if ratio else 0,
                "corr_has_counter": len(counter_ev) > 0,
            },
        })

        # Edges: pattern -> circumventions
        for cid in entry.get("circumventions", []):
            # Find circumvention display name
            for c in circumventions_yaml.get("entries", []):
                if c["id"] == cid:
                    edges.append({
                        "source": "circumvention:" + c["name"],
                        "target": pid,
                        "type": "counteracts",
                    })
                    break

        # Edges: observed_in
        for obs in entry.get("observed_in", []):
            src_id = obs["source_id"]
            src_type = obs["source_type"]
            if src_type == "principle":
                ref = f"principles/{src_id}.md"
            else:
                ref = f"analyses/{src_id}.md"
            edges.append({
                "source": pid,
                "target": ref,
                "type": "observed_in",
            })

        # Edges: counter_evidence
        for ev_id in counter_ev:
            edges.append({
                "source": f"evidence/{ev_id}.md",
                "target": pid,
                "type": "evidence_for",
            })

    # --- Circumventions (from YAML + circumventions.md content) ---
    circ_md = ROOT / "circumventions.md"
    circ_content_map = {}
    if circ_md.exists():
        parts = re.split(r"^### ", read_file(circ_md), flags=re.MULTILINE)
        for part in parts[1:]:
            name = part.split("\n")[0].strip()
            circ_content_map[name] = "### " + part.strip()

    for entry in circumventions_yaml.get("entries", []):
        cid = "circumvention:" + entry["name"]
        layer_names = layer_ids_to_names(entry.get("layers", []))

        # Extract STATEMENT and OUTCOME RANGE from circumvention content
        ccontent = circ_content_map.get(entry["name"], "")
        c_stmt_match = re.search(r"STATEMENT:\s*(.+?)(?:\n\n|\nCOUNTERACTS:|\nMECHANISM:|\nOUTCOME)", ccontent, re.DOTALL)
        c_statement = c_stmt_match.group(1).strip().replace("\n", " ") if c_stmt_match else ""
        c_or_match = re.search(r"OUTCOME RANGE:\s*(.+?)(?:\n\n|\nMECHANISM:|\nFAILURE|\nOBSERVED|\Z)", ccontent, re.DOTALL)
        c_outcome = c_or_match.group(1).strip().replace("\n", " ") if c_or_match else ""

        add_node({
            "id": cid,
            "type": "circumvention",
            "title": entry["name"],
            "content": ccontent,
            "meta": {
                "layers": ", ".join(layer_names),
                "layer_list": layer_names,
                "counteracts": ", ".join(entry.get("counteracts", [])),
                "statement": c_statement,
                "outcome_range": c_outcome,
                "mechanism": "",
                "failure_modes": "",
                "power_response": "",
                "tier": entry.get("tier", "structural"),
            },
        })

        # Edges: counteracts patterns
        for pat_id in entry.get("counteracts", []):
            for p in patterns_yaml.get("entries", []):
                if p["id"] == pat_id:
                    edges.append({
                        "source": cid,
                        "target": "pattern:" + p["name"],
                        "type": "counteracts",
                    })
                    break

        # Edges: observed_in
        for obs in entry.get("observed_in", []):
            src_id = obs["source_id"]
            src_type = obs["source_type"]
            if src_type == "principle":
                ref = f"principles/{src_id}.md"
            else:
                ref = f"analyses/{src_id}.md"
            edges.append({
                "source": cid,
                "target": ref,
                "type": "observed_in",
            })

    # --- Hegemonic Contexts (from config.yaml) ---
    hc_list = config.get("hegemonic_contexts", [])
    hc_id_to_name = {}
    for ctx in hc_list:
        hc_node_id = "hegemonic:" + ctx["id"]
        hc_id_to_name[ctx["id"]] = ctx["name"]
        add_node({
            "id": hc_node_id,
            "type": "hegemonic_context",
            "title": ctx["name"],
            "content": ctx.get("description", ""),
            "meta": {},
        })

    # --- Analyses (from YAML + analysis file content) ---
    # Build pattern ID -> display name map
    pattern_id_to_name = {p["id"]: p["name"] for p in patterns_yaml.get("entries", [])}

    for entry in analyses_yaml.get("entries", []):
        fpath = ROOT / entry["file"]
        content = read_file(fpath) if fpath.exists() else ""
        layer_names = layer_ids_to_names(
            entry.get("layers_primary", []) +
            entry.get("layers_secondary", [])
        )

        # Hegemonic contexts for this analysis
        analysis_hc_ids = entry.get("hegemonic_contexts", []) or []
        analysis_hc_names = [hc_id_to_name[hid] for hid in analysis_hc_ids if hid in hc_id_to_name]
        hc_names_str = ", ".join(analysis_hc_names)

        add_node({
            "id": entry["file"],
            "type": "analysis",
            "title": extract_title(content) if content else entry.get("title", ""),
            "content": content,
            "meta": {
                "date": entry.get("date", ""),
                "time": entry.get("time", ""),
                "source_type": entry.get("source_type", ""),
                "mode": "",
                "source": entry.get("source_name", ""),
                "hegemonic_context": entry.get("hegemonic_context", ""),
                "hegemonic_contexts_list": hc_names_str,
                "layer_list": layer_names,
            },
        })

        # Edges: analysis -> hegemonic contexts
        for hid in analysis_hc_ids:
            hc_node_id = "hegemonic:" + hid
            if hc_node_id in node_ids:
                edges.append({
                    "source": entry["file"],
                    "target": hc_node_id,
                    "type": "operates_within",
                })

        # Edges: analysis -> patterns matched
        for pm in entry.get("patterns_matched", []):
            pname = pattern_id_to_name.get(pm["pattern"])
            if pname:
                edges.append({
                    "source": entry["file"],
                    "target": "pattern:" + pname,
                    "type": "matches",
                })

        # Edges: cross-references
        for xref in entry.get("cross_references", []):
            edges.append({
                "source": entry["file"],
                "target": f"analyses/{xref}.md",
                "type": "references",
            })

        # Edges: instrument references (scan content)
        if content:
            for iref in re.findall(r"instruments/[\w\-]+\.md", content):
                edges.append({
                    "source": entry["file"],
                    "target": iref,
                    "type": "applies_instrument",
                })

    # --- Principles (from YAML + principle file content) ---
    for entry in principles_yaml.get("entries", []):
        fpath = ROOT / entry["file"]
        content = read_file(fpath) if fpath.exists() else ""
        layer_names = layer_ids_to_names(entry.get("layers", []))

        principle_names = entry.get("principles_list", [])

        add_node({
            "id": entry["file"],
            "type": "principle",
            "title": extract_title(content) if content else f"Principles: {entry.get('source_display', entry.get('source_name', ''))}",
            "content": content,
            "meta": {
                "source": entry.get("source_display") or f"{entry.get('source_name', '')}, *{entry.get('source_title', '')}* ({entry.get('source_year', '')})",
                "type": "",
                "layers": ", ".join(layer_names),
                "layer_list": layer_names,
                "principle_count": len(principle_names),
                "principle_names": principle_names,
            },
        })

        # Edges: key_patterns
        for kp in entry.get("key_patterns", []):
            pname = pattern_id_to_name.get(kp["pattern"])
            if pname:
                edges.append({
                    "source": entry["file"],
                    "target": "pattern:" + pname,
                    "type": "key_pattern",
                })

        # Edges: instruments
        for inst_id in entry.get("instruments_produced", []):
            edges.append({
                "source": entry["file"],
                "target": f"instruments/{inst_id}.md",
                "type": "produces_instrument",
            })

    # --- Instruments (from YAML + instrument file content) ---
    for entry in instruments_yaml.get("entries", []):
        fpath = ROOT / entry["file"]
        content = read_file(fpath) if fpath.exists() else ""
        layer_names = layer_ids_to_names(entry.get("layers", []))

        items = re.findall(r"^### (.+)$", content, re.MULTILINE) if content else []

        add_node({
            "id": entry["file"],
            "type": "instrument",
            "title": extract_title(content) if content else entry.get("name", ""),
            "content": content,
            "meta": {
                "source": ", ".join(entry.get("derived_from", [])),
                "layers": ", ".join(layer_names),
                "layer_list": layer_names,
                "item_count": len(items),
            },
        })

    # --- Evidence (from YAML + evidence file content) ---
    for entry in evidence_yaml.get("entries", []):
        fpath = ROOT / entry["file"]
        content = read_file(fpath) if fpath.exists() else ""
        layer_names = layer_ids_to_names(entry.get("layers", []))

        add_node({
            "id": entry["file"],
            "type": "evidence",
            "title": extract_title(content) if content else entry.get("title", ""),
            "content": content,
            "meta": {
                "date": entry.get("date_recorded", ""),
                "source": entry.get("source", ""),
                "source_type": entry.get("evidence_source_type", ""),
                "axioms": ", ".join(str(a) for a in entry.get("axioms", [])),
                "layers": ", ".join(layer_names),
                "layer_list": layer_names,
                "relationship": entry.get("relationship", ""),
            },
        })

        # Edges: evidence -> patterns
        for pat_id in entry.get("patterns", []):
            pname = pattern_id_to_name.get(pat_id)
            if pname:
                edges.append({
                    "source": entry["file"],
                    "target": "pattern:" + pname,
                    "type": "evidence_for",
                })

    # --- Constitution & Taxonomy (metadata, not nodes) ---
    axioms = []
    constitution_path = ROOT / "constitution.md"
    if constitution_path.exists():
        axioms = parse_constitution(constitution_path)

    layer_list = []
    taxonomy_path = ROOT / "taxonomy.md"
    if taxonomy_path.exists():
        layer_list = parse_taxonomy(taxonomy_path)

    # --- README sections ---
    readme_sections = {}
    readme_path = ROOT / "README.md"
    if readme_path.exists():
        readme_sections = extract_readme_sections(readme_path)

    # --- Layer descriptions ---
    layer_descriptions = []
    if taxonomy_path.exists():
        layer_descriptions = extract_layer_descriptions(taxonomy_path)

    # --- Glossary data: axiom defs, IC defs, position defs ---
    axiom_definitions = []
    ic_definitions = []
    if constitution_path.exists():
        axiom_definitions = parse_axiom_definitions(constitution_path)
        ic_definitions = parse_ic_definitions(constitution_path)

    position_definitions = []
    positional_lens_path = ROOT / "instruments" / "positional-lens.md"
    if positional_lens_path.exists():
        position_definitions = parse_position_definitions(positional_lens_path)

    # --- Deduplicate and validate edges ---
    valid_edges = []
    seen = set()
    for e in edges:
        key = (e["source"], e["target"], e["type"])
        if key not in seen and e["source"] in node_ids and e["target"] in node_ids:
            valid_edges.append(e)
            seen.add(key)

    # --- Compute dynamic corroboration (updates pattern nodes) ---
    compute_corroboration(nodes, valid_edges)
    sync_corroboration_to_yaml(nodes)

    # --- Compute framework health metrics ---
    health = compute_health_metrics(nodes)

    data = {
        "nodes": nodes,
        "edges": valid_edges,
        "meta": {
            "axioms": axioms,
            "layers": layer_list,
            "readme_sections": readme_sections,
            "layer_descriptions": layer_descriptions,
            "axiom_definitions": axiom_definitions,
            "ic_definitions": ic_definitions,
            "position_definitions": position_definitions,
            "health": health,
        },
    }

    print(f"Nodes: {len(nodes)}")
    for t in ["analysis", "principle", "instrument", "pattern", "circumvention", "hegemonic_context", "evidence"]:
        count = sum(1 for n in nodes if n["type"] == t)
        print(f"  {t}: {count}")
    print(f"Edges: {len(valid_edges)}")

    return data


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lens of Power — Framework Viewer</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script src="viewer-data.js?v=__BUILD_TS__"></script>
<style>
:root {
  --bg: #0d1117;
  --bg-sidebar: #161b22;
  --bg-card: #1c2128;
  --border: #30363d;
  --text: #e6edf3;
  --text-muted: #8b949e;
  --text-link: #58a6ff;
  --blue: #388bfd;
  --green: #3fb950;
  --orange: #d29922;
  --purple: #a371f7;
  --gray: #8b949e;
  --red: #f85149;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  height: 100vh;
  overflow: hidden;
}
#app { display: flex; height: 100vh; }

/* Sidebar */
#sidebar {
  width: 300px;
  min-width: 300px;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
#sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border);
}
#sidebar-header h1 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
#search {
  width: 100%;
  padding: 8px 12px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  font-size: 14px;
  outline: none;
}
#search:focus { border-color: var(--blue); }
#search::placeholder { color: var(--text-muted); }

#filters {
  display: flex;
  gap: 4px;
  margin-top: 10px;
  flex-wrap: wrap;
}
.filter-btn {
  padding: 3px 8px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: transparent;
  color: var(--text-muted);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.15s;
}
.filter-btn.active { border-color: currentColor; }
.filter-btn[data-type="analysis"].active { color: var(--blue); background: rgba(56,139,253,0.1); }
.filter-btn[data-type="principle"].active { color: var(--green); background: rgba(63,185,80,0.1); }
.filter-btn[data-type="instrument"].active { color: var(--orange); background: rgba(210,153,34,0.1); }
.filter-btn[data-type="pattern"].active { color: var(--purple); background: rgba(163,113,247,0.1); }
.filter-btn[data-type="circumvention"].active { color: #1abc9c; background: rgba(26,188,156,0.1); }
.filter-btn[data-type="hegemonic_context"].active { color: #da7756; background: rgba(218,119,86,0.1); }
.filter-btn[data-type="evidence"].active { color: var(--gray); background: rgba(139,148,158,0.1); }
.filter-btn[data-type="redteam"].active { color: var(--red); background: rgba(248,81,73,0.1); }

#sidebar-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}
.sidebar-group { margin-bottom: 4px; }
.sidebar-group-header {
  padding: 6px 16px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}
.sidebar-group-header .count {
  font-weight: 400;
  opacity: 0.7;
}
.sidebar-group-header .chevron {
  font-size: 10px;
  transition: transform 0.15s;
}
.sidebar-group.collapsed .chevron { transform: rotate(-90deg); }
.sidebar-group.collapsed .sidebar-group-items { display: none; }
.sidebar-item {
  padding: 6px 16px 6px 24px;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  border-left: 2px solid transparent;
  transition: background 0.1s;
}
.sidebar-item:hover { background: rgba(255,255,255,0.04); }
.sidebar-item.active {
  background: rgba(56,139,253,0.1);
  border-left-color: var(--blue);
}
.sidebar-item .type-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
  vertical-align: middle;
}
.sidebar-item .item-subtitle {
  display: block;
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 1px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.sidebar-item .item-badges {
  display: inline-flex;
  gap: 4px;
  float: right;
  margin-top: 2px;
}
.sidebar-item .badge {
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 8px;
  font-weight: 500;
  line-height: 1.4;
}
.badge-degree {
  background: rgba(255,255,255,0.06);
  color: var(--text-muted);
}
.badge-established { background: rgba(63,185,80,0.15); color: var(--green); }
.badge-supported { background: rgba(210,153,34,0.15); color: var(--orange); }
.badge-preliminary { background: rgba(139,148,158,0.1); color: var(--text-muted); }

/* Sidebar resize handle */
#sidebar-resize {
  width: 4px;
  cursor: col-resize;
  background: transparent;
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  z-index: 10;
  transition: background 0.15s;
}
#sidebar-resize:hover, #sidebar-resize.dragging {
  background: var(--blue);
}
#sidebar { position: relative; }

/* Search clear button */
.search-wrap {
  position: relative;
}
.search-wrap #search {
  padding-right: 28px;
}
#search-clear {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 14px;
  padding: 2px 4px;
  line-height: 1;
  display: none;
}
#search-clear:hover { color: var(--text); }

/* Main panel */
#main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
#main-header {
  padding: 12px 24px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 12px;
}
#view-toggle {
  display: flex;
  gap: 0;
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: visible;
}
.view-btn:first-child { border-radius: 5px 0 0 5px; }
.view-btn:last-child, .view-dropdown:last-child .view-dropdown-btn { border-radius: 0 5px 5px 0; }
.view-btn {
  padding: 6px 14px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}
.view-btn.active {
  background: var(--bg-card);
  color: var(--text);
}
#main-title {
  font-size: 16px;
  font-weight: 600;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
#content-area {
  flex: 1;
  overflow: hidden;
  position: relative;
}

/* Detail view */
#detail-view {
  height: 100%;
  overflow-y: auto;
  padding: 32px 48px;
  max-width: 900px;
  display: none;
}
#detail-view .meta-bar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.meta-tag {
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}
.meta-tag.type-analysis { background: rgba(56,139,253,0.15); color: var(--blue); }
.meta-tag.type-principle { background: rgba(63,185,80,0.15); color: var(--green); }
.meta-tag.type-instrument { background: rgba(210,153,34,0.15); color: var(--orange); }
.meta-tag.type-pattern { background: rgba(163,113,247,0.15); color: var(--purple); }
.meta-tag.type-circumvention { background: rgba(26,188,156,0.15); color: #1abc9c; }
.meta-tag.type-evidence { background: rgba(139,148,158,0.15); color: var(--gray); }

#detail-content {
  line-height: 1.7;
  font-size: 15px;
}
#detail-content h1 { font-size: 24px; margin: 0 0 16px 0; }
#detail-content h2 { font-size: 20px; margin: 28px 0 12px 0; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
#detail-content h3 { font-size: 16px; margin: 20px 0 8px 0; }
#detail-content p { margin: 0 0 12px 0; }
#detail-content ul, #detail-content ol { margin: 0 0 12px 24px; }
#detail-content li { margin-bottom: 4px; }
#detail-content blockquote {
  border-left: 3px solid var(--border);
  padding: 4px 16px;
  color: var(--text-muted);
  margin: 0 0 12px 0;
}
#detail-content code {
  background: var(--bg-card);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}
#detail-content pre {
  background: var(--bg-card);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0 0 12px 0;
}
#detail-content pre code { background: none; padding: 0; }
#detail-content table {
  border-collapse: collapse;
  margin: 0 0 12px 0;
  width: 100%;
}
#detail-content th, #detail-content td {
  border: 1px solid var(--border);
  padding: 8px 12px;
  text-align: left;
  font-size: 14px;
}
#detail-content th { background: var(--bg-card); }
#detail-content a, .cross-ref {
  color: var(--text-link);
  text-decoration: none;
  cursor: pointer;
}
#detail-content a:hover, .cross-ref:hover { text-decoration: underline; }
#detail-content hr { border: none; border-top: 1px solid var(--border); margin: 24px 0; }
#detail-content strong { color: #f0f3f6; }

/* Analysis TOC */
.analysis-toc {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px 18px;
  margin-bottom: 24px;
}
.toc-title {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.toc-link {
  display: block;
  padding: 3px 0;
  color: var(--text-link);
  text-decoration: none;
  font-size: 13px;
}
.toc-link:hover { text-decoration: underline; }
.toc-link.toc-briefing {
  font-weight: 600;
  color: var(--green);
}
.back-to-top {
  float: right;
  font-size: 11px;
  font-weight: 400;
  color: var(--text-muted);
  text-decoration: none;
  cursor: pointer;
}
.back-to-top:hover { color: var(--text-link); }

/* Glossary tooltips */
.glossary-term { position: relative; cursor: help; }
.glossary-term.glossary-nav { cursor: pointer; color: var(--text-link); }
.glossary-term.glossary-nav:hover { text-decoration: underline; }
.glossary-first { border-bottom: 1px dotted var(--text-muted); }
#glossary-tooltip {
  position: fixed; z-index: 1000;
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 8px; padding: 12px 16px;
  max-width: 340px; font-size: 13px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.5);
  pointer-events: none; display: none;
}
#glossary-tooltip .gt-title {
  font-weight: 600; font-size: 13px; margin-bottom: 2px; color: var(--text);
}
#glossary-tooltip .gt-type {
  font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px;
  color: var(--text-muted); margin-bottom: 6px;
}
#glossary-tooltip .gt-def {
  font-size: 12px; color: var(--text-muted); line-height: 1.5;
}

/* Collapsible sections */
.collapsible-h2 { cursor: pointer; user-select: none; }
.collapsible-h2:hover { color: var(--text-link); }
.section-chevron {
  font-size: 10px; margin-right: 8px; display: inline-block;
  transition: transform 0.15s; color: var(--text-muted);
}
.collapsible-section { /* visible by default */ }
.collapsible-section.collapsed { display: none; }
.toc-link.toc-collapsed { color: var(--text-muted); font-style: italic; }
.toc-link.toc-collapsed::after { content: ' (collapsed)'; font-size: 10px; }

/* Connected items panel */
#connected-panel {
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
}
#connected-panel h3 {
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  margin-bottom: 12px;
}
.connected-item {
  display: inline-block;
  padding: 4px 12px;
  margin: 0 6px 6px 0;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}
.connected-item:hover { background: rgba(255,255,255,0.06); }
.corroboration-sources {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

/* Graph view */
#graph-view {
  width: 100%;
  height: 100%;
  display: none;
  position: relative;
}
#graph-view svg { width: 100%; height: 100%; }
.graph-node { cursor: pointer; }
.graph-node circle { stroke-width: 2px; transition: r 0.15s; }
.graph-node text {
  font-size: 10px;
  fill: var(--text-muted);
  pointer-events: none;
}
.graph-link { stroke-opacity: 0.3; }
.graph-link.highlight { stroke-opacity: 0.8; stroke-width: 2.5px !important; }
.graph-node.highlight circle { stroke-width: 3px; }
.graph-node.dimmed { opacity: 0.1; pointer-events: none; }
.graph-link.dimmed { stroke-opacity: 0.03; }
.graph-locked .graph-node.dimmed { pointer-events: none; }
.graph-locked .graph-node:not(.dimmed) { cursor: pointer; }
.graph-locked .graph-node:not(.dimmed) circle { filter: brightness(1.2); }

/* Reset button */
.view-reset-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 5px 12px;
  background: var(--bg-sidebar);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text-muted);
  font-size: 12px;
  cursor: pointer;
  z-index: 50;
  transition: all 0.15s;
}
.view-reset-btn:hover {
  color: var(--text);
  border-color: var(--text-muted);
}
#graph-hint {
  position: absolute;
  bottom: 12px;
  right: 12px;
  font-size: 11px;
  color: var(--text-muted);
  opacity: 0.5;
  pointer-events: none;
}

/* Graph legend */
#graph-legend {
  position: absolute;
  bottom: 16px;
  right: 16px;
  background: var(--bg-sidebar);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 11px;
  z-index: 50;
  max-width: 220px;
  display: none;
}
.legend-section { margin-bottom: 10px; }
.legend-section:last-child { margin-bottom: 0; }
.legend-title {
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
  font-size: 10px;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 3px;
  color: var(--text-muted);
}
.legend-clickable { cursor: pointer; border-radius: 4px; padding: 2px 4px; margin-left: -4px; transition: background 0.15s; }
.legend-clickable:hover { background: rgba(255,255,255,0.08); }
.legend-off { opacity: 0.35; }
.legend-active { background: rgba(255,255,255,0.1); }
.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.legend-line {
  width: 16px;
  height: 2px;
  flex-shrink: 0;
  border-radius: 1px;
}

/* Dashboard view */
#dashboard-view {
  height: 100%;
  overflow-y: auto;
  padding: 32px 48px;
  max-width: 960px;
}
.stats-bar {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 8px;
  padding: 10px 14px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 6px;
}
.stats-bar-label {
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-right: 4px;
  min-width: 60px;
}
.stats-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 50px;
}
.stats-value {
  font-size: 18px;
  font-weight: 700;
  line-height: 1.2;
}
.stats-label {
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.stats-bar[style*="cursor"] { transition: border-color 0.15s; }
.stats-bar[style*="cursor"]:hover { border-color: var(--accent); }
.corroboration-bar {
  margin-bottom: 24px;
}
.dashboard-section {
  margin-bottom: 36px;
}
.dashboard-section > h2,
.dashboard-section-header > h2 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
  color: var(--text);
  flex: 1;
}
.dashboard-content {
  line-height: 1.7;
  font-size: 14px;
  color: var(--text-muted);
}
.dashboard-content h3 { color: var(--text); font-size: 15px; margin: 20px 0 8px 0; }
.dashboard-content p { margin: 0 0 10px 0; }
.dashboard-content ul, .dashboard-content ol { margin: 0 0 10px 24px; }
.dashboard-content li { margin-bottom: 3px; }
.dashboard-content blockquote {
  border-left: 3px solid var(--border);
  padding: 4px 16px;
  color: var(--text-muted);
  margin: 0 0 10px 0;
}
.dashboard-content code {
  background: var(--bg-card);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}
.dashboard-content pre {
  background: var(--bg-card);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0 0 10px 0;
  font-size: 12px;
}
.dashboard-content pre code { background: none; padding: 0; }
.dashboard-content table {
  border-collapse: collapse;
  margin: 0 0 10px 0;
  width: 100%;
}
.dashboard-content th, .dashboard-content td {
  border: 1px solid var(--border);
  padding: 6px 10px;
  text-align: left;
  font-size: 13px;
}
.dashboard-content th { background: var(--bg-card); color: var(--text); }
.dashboard-content strong { color: var(--text); }
.dashboard-content em { color: var(--text-muted); }
.dashboard-content a { color: var(--text-link); text-decoration: none; }
.layer-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
}
.layer-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px 16px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}
.layer-card:hover {
  border-color: var(--purple);
  background: rgba(163,113,247,0.04);
}
.layer-card-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 6px;
  color: var(--text);
}
.layer-card-desc {
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-muted);
}
.outcome-range-block {
  background: rgba(26,188,156,0.06);
  border: 1px solid rgba(26,188,156,0.2);
  border-radius: 8px;
  padding: 14px 18px;
  margin-bottom: 20px;
}
.outcome-range-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #1abc9c;
  margin-bottom: 6px;
}
.outcome-range-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text);
}
.circumvention-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}
.circumvention-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px 16px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}
.circumvention-card:hover {
  border-color: #1abc9c;
  background: rgba(26,188,156,0.04);
}
.circumvention-card-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 6px;
  color: #1abc9c;
}
.circumvention-card-stmt {
  font-size: 12px;
  line-height: 1.5;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.circumvention-card-counteracts {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.circumvention-counteracts-tag {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 8px;
  background: rgba(163,113,247,0.1);
  color: var(--purple);
}
.hegemonic-context-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}
.hegemonic-context-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px 16px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}
.hegemonic-context-card:hover {
  border-color: #da7756;
  background: rgba(218,119,86,0.04);
}
.hc-card-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 6px;
  color: #da7756;
}
.hc-card-desc {
  font-size: 12px;
  line-height: 1.5;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.hc-card-bar {
  height: 4px;
  background: rgba(255,255,255,0.06);
  border-radius: 2px;
  margin-bottom: 4px;
  overflow: hidden;
}
.hc-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s;
}
.hc-card-count {
  font-size: 11px;
  color: var(--text-muted);
}
.works-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}
.work-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px 16px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}
.work-card:hover {
  border-color: var(--green);
  background: rgba(63,185,80,0.04);
}
.work-card-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
  color: var(--text);
}
.work-card-source {
  font-size: 12px;
  line-height: 1.4;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.work-card-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
}
.work-count {
  color: var(--green);
  font-weight: 500;
}
.work-layers {
  color: var(--text-muted);
}

/* Recent analyses cards */
.recent-analyses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 12px;
}
.recent-analysis-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px 18px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}
.recent-analysis-card:hover {
  border-color: var(--blue);
  background: rgba(56,139,253,0.04);
}
.recent-analysis-date {
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 4px;
}
.recent-analysis-title {
  font-weight: 600;
  font-size: 14px;
  color: var(--text);
  margin-bottom: 4px;
}
.recent-analysis-source {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.recent-analysis-briefing {
  font-size: 12px;
  line-height: 1.5;
  color: var(--text-muted);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Layer coverage bar */
.layer-card-coverage {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.layer-coverage-bar {
  flex: 1;
  height: 4px;
  background: rgba(255,255,255,0.06);
  border-radius: 2px;
  overflow: hidden;
}
.layer-coverage-fill {
  height: 100%;
  border-radius: 2px;
  background: var(--purple);
  transition: width 0.3s;
}
.layer-coverage-count {
  font-size: 11px;
  color: var(--text-muted);
  min-width: 40px;
  text-align: right;
}

/* Expandable grids — collapse to ~2 rows */
.dashboard-grid-expandable {
  max-height: 340px;
  overflow: hidden;
  transition: max-height 0.3s ease;
}
.dashboard-grid-expandable.expanded {
  max-height: none;
}
.show-all-toggle {
  display: inline-block;
  margin-top: 10px;
  padding: 4px 0;
  font-size: 13px;
  color: var(--text-link);
  cursor: pointer;
  background: none;
  border: none;
  font-family: inherit;
}
.show-all-toggle:hover {
  text-decoration: underline;
}

/* View navigation cards */
.view-nav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}
.view-nav-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  text-align: center;
}
.view-nav-card:hover {
  border-color: var(--blue);
  background: rgba(56,139,253,0.04);
}
.view-nav-icon {
  font-size: 24px;
  margin-bottom: 8px;
  opacity: 0.7;
}
.view-nav-label {
  font-weight: 600;
  font-size: 13px;
  color: var(--text);
  margin-bottom: 4px;
}
.view-nav-desc {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.4;
}

/* Collapsible documentation sections */
.dashboard-section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: default;
}
.dashboard-section-header.collapsible {
  cursor: pointer;
}
.dashboard-section-header.collapsible:hover h2 {
  color: var(--text-link);
}
.dashboard-section-header .section-chevron {
  font-size: 12px;
  color: var(--text-muted);
  transition: transform 0.15s;
}
.dashboard-section.collapsed .section-chevron {
  transform: rotate(-90deg);
}
.dashboard-section.collapsed .dashboard-content {
  display: none;
}

/* Layers view */
#layers-view {
  width: 100%;
  height: 100%;
  display: none;
  overflow-y: auto;
  padding: 32px 48px;
  max-width: 960px;
}
.layer-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.layer-tab {
  padding: 6px 16px;
  border-radius: 16px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}
.layer-tab:hover { color: var(--text); border-color: var(--text-muted); }
.layer-tab.active {
  color: var(--purple);
  border-color: var(--purple);
  background: rgba(163,113,247,0.08);
}
.layer-detail { margin-top: 24px; }
.layer-description {
  color: var(--text-muted);
  font-size: 14px;
  line-height: 1.5;
  margin: 0 0 24px 0;
}
.layer-cooccur-section { margin-bottom: 28px; }
.layer-cooccur-section h3,
.layer-items-section h3 {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin: 0 0 12px 0;
}
.cooccur-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}
.cooccur-label {
  min-width: 140px;
  font-size: 13px;
  color: var(--text);
}
.cooccur-bar {
  flex: 1;
  height: 6px;
  background: rgba(255,255,255,0.06);
  border-radius: 3px;
  overflow: hidden;
  max-width: 300px;
}
.cooccur-fill {
  height: 100%;
  border-radius: 3px;
  background: var(--purple);
}
.cooccur-count {
  font-size: 12px;
  color: var(--text-muted);
  min-width: 30px;
  text-align: right;
}
.layer-items-section { margin-bottom: 24px; }
.layer-item-row {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.1s;
  gap: 10px;
}
.layer-item-row:hover { background: rgba(255,255,255,0.04); }
.layer-item-title {
  flex: 1;
  font-size: 13px;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.layer-item-meta {
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
}
.layer-item-corr {
  display: flex;
  align-items: center;
  gap: 6px;
}
.layer-item-corr-bar {
  width: 60px;
  height: 4px;
  background: rgba(255,255,255,0.06);
  border-radius: 2px;
  overflow: hidden;
}
.layer-item-corr-fill {
  height: 100%;
  border-radius: 2px;
}
.layer-item-corr-level {
  font-size: 11px;
  font-weight: 500;
}

/* Matrix view */
#matrix-view {
  width: 100%;
  height: 100%;
  overflow: auto;
  display: none;
  padding: 24px;
}
.matrix-container {
  min-width: max-content;
}
.matrix-table {
  border-collapse: collapse;
  font-size: 12px;
}
.matrix-table th {
  position: sticky;
  top: 0;
  background: var(--bg);
  z-index: 2;
  padding: 0;
}
.matrix-table th.matrix-corner {
  position: sticky;
  left: 0;
  z-index: 3;
}
.matrix-col-header {
  writing-mode: vertical-lr;
  transform: rotate(180deg);
  padding: 8px 4px;
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
  white-space: nowrap;
  max-height: 180px;
  overflow: hidden;
  cursor: pointer;
}
.matrix-col-header:hover { color: var(--text); }
.matrix-row-header {
  position: sticky;
  left: 0;
  background: var(--bg);
  z-index: 1;
  padding: 4px 12px 4px 8px;
  text-align: left;
  font-weight: 500;
  white-space: nowrap;
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
  color: var(--text-muted);
  border-right: 1px solid var(--border);
}
.matrix-row-header:hover { color: var(--text); }
.matrix-corr {
  font-size: 9px;
  font-weight: 400;
  margin-left: 6px;
  padding: 1px 5px;
  border-radius: 8px;
  vertical-align: middle;
}
.matrix-corr-ESTABLISHED { background: rgba(63,185,80,0.2); color: var(--green); }
.matrix-corr-SUPPORTED { background: rgba(210,153,34,0.2); color: var(--orange); }
.matrix-corr-PRELIMINARY { background: rgba(139,148,158,0.2); color: var(--gray); }
.matrix-cell {
  padding: 0;
  text-align: center;
  min-width: 28px;
  height: 28px;
  border: 1px solid rgba(48,54,61,0.4);
  cursor: default;
}
.matrix-cell.filled {
  cursor: pointer;
}
.matrix-dot {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 3px;
}
.matrix-row:hover .matrix-row-header { color: var(--text); }
.matrix-row.highlight .matrix-row-header { color: var(--text); font-weight: 600; }
.matrix-row.dimmed { opacity: 0.2; }
.matrix-count {
  position: sticky;
  right: 0;
  background: var(--bg);
  padding: 4px 8px;
  text-align: center;
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 600;
  border-left: 1px solid var(--border);
}

/* Graph tooltip */
#graph-tooltip {
  position: fixed;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 13px;
  pointer-events: none;
  display: none;
  max-width: 300px;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}
#graph-tooltip .tt-title { font-weight: 600; margin-bottom: 4px; }
#graph-tooltip .tt-type { font-size: 11px; color: var(--text-muted); }

/* Visualizations dropdown */
.view-dropdown {
  position: relative;
  display: inline-block;
}
.view-dropdown-btn {
  padding: 6px 14px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}
.view-dropdown-btn.active {
  background: var(--bg-card);
  color: var(--text);
}
.view-dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  min-width: 240px;
  background: var(--bg-sidebar);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 4px 0;
  z-index: 100;
  display: none;
  box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}
.view-dropdown-menu.open { display: block; }
.view-dropdown-item {
  padding: 7px 16px;
  font-size: 13px;
  color: var(--text-muted);
  cursor: pointer;
  transition: background 0.1s;
}
.view-dropdown-item:hover { background: rgba(255,255,255,0.04); }
.view-dropdown-item.active { color: var(--purple); }
.view-dropdown-sep {
  height: 1px;
  background: var(--border);
  margin: 4px 0;
}

/* Timeline view */
#timeline-view {
  height: 100%;
  overflow-y: auto;
  padding: 32px 48px;
  max-width: 960px;
  display: none;
}
.timeline-stats {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  margin-bottom: 24px;
  padding: 14px 18px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
  color: var(--text-muted);
}
.timeline-stats strong { color: var(--text); }
.timeline-track {
  position: relative;
  margin-left: 80px;
  border-left: 2px solid var(--border);
  padding-left: 24px;
}
.timeline-event {
  position: relative;
  margin-bottom: 20px;
}
.timeline-date {
  position: absolute;
  left: -104px;
  width: 72px;
  text-align: right;
  font-size: 12px;
  color: var(--text-muted);
  top: 2px;
}
.timeline-dot {
  position: absolute;
  left: -31px;
  top: 4px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid var(--bg);
}
.timeline-body {
  padding: 10px 14px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.1s;
}
.timeline-body:hover { background: rgba(255,255,255,0.04); }
.timeline-body-title {
  font-weight: 600;
  font-size: 14px;
  color: var(--text);
  margin-bottom: 6px;
}
.timeline-body-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
}
.timeline-layer-pill {
  padding: 1px 8px;
  border-radius: 10px;
  font-size: 11px;
  background: rgba(163,113,247,0.1);
  color: var(--purple);
}
.timeline-new-badge {
  padding: 1px 6px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 600;
  background: rgba(63,185,80,0.15);
  color: var(--green);
}
.timeline-pattern-count {
  font-size: 12px;
  color: var(--text-muted);
}

/* Flow view */
#flow-view {
  height: 100%;
  overflow-y: auto;
  padding: 32px 48px;
  max-width: 960px;
  display: none;
}
.flow-grid table {
  border-collapse: separate;
  border-spacing: 3px;
  margin-bottom: 28px;
}
.flow-cell {
  width: 48px;
  height: 48px;
  border-radius: 4px;
  cursor: pointer;
  position: relative;
  text-align: center;
  font-size: 11px;
  line-height: 48px;
  color: var(--text-muted);
  transition: outline 0.1s;
}
.flow-cell.active-cell { outline: 2px solid var(--purple); outline-offset: -1px; }
.flow-cell.diagonal { color: var(--text); font-weight: 600; }
.flow-header-cell {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
  padding: 4px 6px;
  white-space: nowrap;
}
.flow-header-cell.row-header { text-align: right; }
.flow-corridor-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}
.flow-corridor-label {
  min-width: 220px;
  font-size: 13px;
  color: var(--text);
}
.flow-corridor-bar {
  flex: 1;
  height: 6px;
  background: rgba(255,255,255,0.06);
  border-radius: 3px;
  overflow: hidden;
  max-width: 200px;
}
.flow-corridor-fill {
  height: 100%;
  border-radius: 3px;
  background: var(--purple);
}
.flow-corridor-count {
  font-size: 12px;
  color: var(--text-muted);
  min-width: 30px;
  text-align: right;
}
.flow-detail {
  margin-top: 16px;
  padding: 16px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
}

/* Gaps view */
#gaps-view {
  height: 100%;
  overflow-y: auto;
  padding: 32px 48px;
  max-width: 960px;
  display: none;
}
.gaps-section {
  margin-bottom: 28px;
}
.gaps-section h3 {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin: 0 0 12px 0;
}
.health-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.health-card { background: var(--bg-card); border-radius: 8px; padding: 16px; }
.health-card h4[title] { margin: 0 0 8px 0; font-size: 13px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; cursor: help; border-bottom: 1px dotted var(--text-muted); display: inline-block; }
.health-card h4:not([title]) { margin: 0 0 8px 0; font-size: 13px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
.gaps-section > h3[title] { cursor: help; border-bottom: 1px dotted var(--text-muted); display: inline-block; }
.health-metric { font-size: 24px; font-weight: 600; margin-bottom: 8px; }
.health-detail { font-size: 12px; color: var(--text-muted); }
.health-status-ok { color: var(--green); }
.health-status-warn { color: var(--orange); }
.health-status-critical { color: var(--red); }
.health-stacked-bar { display: flex; height: 20px; border-radius: 4px; overflow: hidden; margin: 8px 0; }
.health-stacked-bar > div { height: 100%; }
.health-legend { display: flex; gap: 12px; flex-wrap: wrap; font-size: 11px; color: var(--text-muted); }
.health-warning { font-size: 12px; color: var(--orange); margin-top: 4px; }
.health-bar { border-left: 3px solid var(--text-muted); padding-left: 12px; }
.health-bar:hover { border-left-color: var(--accent); }
.health-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; vertical-align: middle; }
.health-dot.health-status-ok { background: var(--green); }
.health-dot.health-status-warn { background: var(--orange); }
.health-dot.health-status-critical { background: var(--red); }
.health-link { color: inherit; text-decoration: underline; text-decoration-style: dotted; text-underline-offset: 3px; cursor: pointer; }
.health-link:hover { text-decoration-style: solid; }
.gaps-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.1s;
}
.gaps-row:hover { background: rgba(255,255,255,0.04); }
.gaps-label {
  min-width: 200px;
  font-size: 13px;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.gaps-bar {
  flex: 1;
  height: 6px;
  background: rgba(255,255,255,0.06);
  border-radius: 3px;
  overflow: hidden;
  max-width: 200px;
}
.gaps-fill {
  height: 100%;
  border-radius: 3px;
}
.gaps-meta {
  font-size: 12px;
  color: var(--text-muted);
  min-width: 100px;
  text-align: right;
  white-space: nowrap;
}
.gaps-severity {
  font-size: 10px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 8px;
}
.gaps-severity-critical { background: rgba(248,81,73,0.15); color: var(--red); }
.gaps-severity-moderate { background: rgba(210,153,34,0.15); color: var(--orange); }
.gaps-severity-minor { background: rgba(139,148,158,0.1); color: var(--text-muted); }
.gaps-corridor-missing {
  font-size: 13px;
  color: var(--text-muted);
  padding: 4px 0;
}

/* Lineage view */
#redteam-view {
  height: 100%;
  overflow-y: auto;
  padding: 32px 48px;
  max-width: 960px;
  display: none;
}
#redteam-view .redteam-report { margin-bottom: 32px; }
#redteam-view .redteam-report h2 { font-size: 16px; margin: 20px 0 8px; }
#redteam-view .redteam-report h3 { font-size: 14px; margin: 16px 0 6px; }
#redteam-view .redteam-report p { font-size: 13px; line-height: 1.6; margin-bottom: 8px; color: var(--text); }
#redteam-view .redteam-report ul, #redteam-view .redteam-report ol { font-size: 13px; line-height: 1.6; margin: 0 0 8px 20px; }
#redteam-view .redteam-report blockquote { border-left: 3px solid var(--red); padding-left: 12px; color: var(--text-muted); margin: 8px 0; }
#redteam-view .redteam-related { margin-top: 24px; }
#redteam-view .redteam-related h3 { font-size: 13px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.3px; margin: 0 0 12px 0; }
#redteam-view .redteam-item { display: flex; align-items: center; gap: 8px; padding: 6px 10px; border-radius: 6px; cursor: pointer; font-size: 13px; transition: background 0.1s; }
#redteam-view .redteam-item:hover { background: rgba(255,255,255,0.04); }
#redteam-view .redteam-item-meta { color: var(--text-muted); font-size: 11px; margin-left: auto; }
#lineage-view {
  height: 100%;
  overflow-y: auto;
  padding: 32px 48px;
  max-width: 960px;
  display: none;
}
.lineage-cluster {
  margin-bottom: 24px;
  padding: 16px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
}
.lineage-pattern-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}
.lineage-pattern-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--purple);
  cursor: pointer;
}
.lineage-pattern-name:hover { text-decoration: underline; }
.lineage-count {
  font-size: 11px;
  color: var(--text-muted);
  background: rgba(255,255,255,0.06);
  padding: 2px 8px;
  border-radius: 10px;
}
.lineage-pattern-statement {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 12px;
  line-height: 1.4;
}
.lineage-members {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.lineage-member-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 12px;
  cursor: pointer;
  transition: border-color 0.15s;
}
.lineage-member-card:hover {
  border-color: var(--green);
}
.lineage-member-title {
  font-weight: 600;
  font-size: 12px;
  color: var(--text);
}
.lineage-member-source {
  font-size: 11px;
  color: var(--text-muted);
}
.lineage-section {
  margin-bottom: 28px;
}
.lineage-section h3 {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin: 0 0 12px 0;
}
.lineage-standalone-row {
  display: flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.1s;
  gap: 10px;
}
.lineage-standalone-row:hover { background: rgba(255,255,255,0.04); }
.lineage-standalone-title {
  font-size: 13px;
  color: var(--text);
  flex: 1;
}
.lineage-standalone-source {
  font-size: 12px;
  color: var(--text-muted);
}

/* Scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }
</style>
</head>
<body>
<div id="app">
  <div id="sidebar">
    <div id="sidebar-header">
      <h1>Lens of Power</h1>
      <div class="search-wrap">
        <input type="text" id="search" placeholder="Search items...">
        <button id="search-clear" title="Clear search">&times;</button>
      </div>
      <div id="filters">
        <button class="filter-btn active" data-type="analysis">Analyses</button>
        <button class="filter-btn active" data-type="principle">Principles</button>
        <button class="filter-btn active" data-type="instrument">Instruments</button>
        <button class="filter-btn active" data-type="pattern">Patterns</button>
        <button class="filter-btn active" data-type="circumvention">Circumventions</button>
        <button class="filter-btn active" data-type="hegemonic_context">Hegemony</button>
        <button class="filter-btn active" data-type="evidence">Evidence</button>
        <button class="filter-btn active" data-type="redteam" id="redteam-nav-btn">Red Team</button>
      </div>
    </div>
    <div id="sidebar-list"></div>
    <div id="sidebar-resize"></div>
  </div>
  <div id="main">
    <div id="main-header">
      <div id="view-toggle">
        <button class="view-btn active" data-view="dashboard">Dashboard</button>
        <button class="view-btn" data-view="gaps">Gap Analysis</button>
        <div class="view-dropdown">
          <button class="view-dropdown-btn" id="viz-dropdown-btn">Visualizations &#9662;</button>
          <div class="view-dropdown-menu" id="viz-dropdown-menu">
            <div class="view-dropdown-item" data-view="graph">Force Graph</div>
            <div class="view-dropdown-item" data-view="layers">Layer Deep Dive</div>
            <div class="view-dropdown-item" data-view="matrix">Corroboration Matrix</div>
            <div class="view-dropdown-sep"></div>
            <div class="view-dropdown-item" data-view="timeline">Timeline</div>
            <div class="view-dropdown-item" data-view="flow">Layer Flow</div>
            <div class="view-dropdown-item" data-view="lineage">Principle Lineage</div>
          </div>
        </div>
      </div>
      <div id="main-title"></div>
    </div>
    <div id="content-area">
      <div id="dashboard-view"></div>
      <div id="detail-view"></div>
      <div id="graph-view">
        <div id="graph-legend"></div>
        <button class="view-reset-btn" id="graph-reset" title="Reset zoom and focus">Reset</button>
        <div id="graph-hint">Hover + Space to lock selection</div>
      </div>
      <div id="layers-view"></div>
      <div id="matrix-view"></div>
      <div id="timeline-view"></div>
      <div id="flow-view"></div>
      <div id="gaps-view"></div>
      <div id="lineage-view"></div>
      <div id="redteam-view"></div>
      <div id="graph-tooltip">
        <div class="tt-title"></div>
        <div class="tt-type"></div>
      </div>
    </div>
  </div>
</div>

<script>
// Data loaded from external file (viewer-data.js)

const TYPE_COLORS = {
  analysis: '#388bfd',
  principle: '#3fb950',
  instrument: '#d29922',
  pattern: '#a371f7',
  circumvention: '#1abc9c',
  hegemonic_context: '#da7756',
  evidence: '#8b949e',
};

const TYPE_LABELS = {
  analysis: 'Analyses',
  principle: 'Principles',
  instrument: 'Instruments',
  pattern: 'Patterns',
  circumvention: 'Circumventions',
  hegemonic_context: 'Hegemonic Contexts',
  evidence: 'Evidence',
};

const TYPE_ORDER = ['analysis', 'principle', 'instrument', 'pattern', 'circumvention', 'hegemonic_context', 'evidence'];

const LAYER_NAMES = [
  'Thought & Narrative',
  'Economic',
  'Legal & Regulatory',
  'Institutional',
  'Surveillance & Information',
  'Physical & Coercive',
];

const EDGE_COLORS = {
  observed_in: '#58a6ff',
  key_pattern: '#a371f7',
  counteracts: '#1abc9c',
  evidence: '#8b949e',
  evidence_for: '#8b949e',
  matches: '#3fb950',
  references: '#d29922',
  applies_instrument: '#f0883e',
  produces_instrument: '#db6d28',
};

const EDGE_LABELS = {
  observed_in: 'observed in',
  key_pattern: 'key pattern',
  counteracts: 'counteracts',
  evidence: 'evidence',
  evidence_for: 'evidence for',
  matches: 'matches',
  references: 'references',
  applies_instrument: 'applies instrument',
  produces_instrument: 'produces instrument',
  operates_within: 'operates within',
};

// State
let activeFilters = new Set(TYPE_ORDER);
let currentView = 'dashboard';
let selectedNode = null;
let searchQuery = '';
let sidebarCollapseState = {};

// Configure marked.js: treat single newlines as <br> for metadata fields
marked.use({ breaks: true });

// Index
const nodeMap = {};
DATA.nodes.forEach(n => { nodeMap[n.id] = n; });

// Build adjacency and degree
const adjacency = {};
const nodeDegree = {};
DATA.nodes.forEach(n => { adjacency[n.id] = { incoming: [], outgoing: [] }; nodeDegree[n.id] = 0; });
DATA.edges.forEach(e => {
  if (adjacency[e.source]) { adjacency[e.source].outgoing.push(e); nodeDegree[e.source]++; }
  if (adjacency[e.target]) { adjacency[e.target].incoming.push(e); nodeDegree[e.target]++; }
});

// ---------------------------------------------------------------------------
// Glossary for tooltips
// ---------------------------------------------------------------------------
const GLOSSARY = {};
// Patterns: "serial regime change" -> {term, type, def, nodeId}
DATA.nodes.filter(n => n.type === 'pattern').forEach(n => {
  const key = n.title.replace(/^The\s+/i, '').toLowerCase();
  const stmt = (n.meta && n.meta.statement) || '';
  GLOSSARY[key] = { term: n.title, type: 'pattern', def: stmt, nodeId: n.id };
});
// Circumventions
DATA.nodes.filter(n => n.type === 'circumvention').forEach(n => {
  GLOSSARY[n.title.toLowerCase()] = { term: n.title, type: 'circumvention', def: (n.meta && n.meta.statement) || '', nodeId: n.id };
});
// Axioms: "axiom 6" -> short def
(DATA.meta.axiom_definitions || []).forEach(a => {
  GLOSSARY[a.id.toLowerCase()] = { term: a.id + ': ' + a.title, type: 'axiom', def: a.short };
});
// ICs: "ic-2" -> short def
(DATA.meta.ic_definitions || []).forEach(ic => {
  GLOSSARY[ic.id.toLowerCase()] = { term: ic.id + ': ' + ic.title, type: 'integrity constraint', def: ic.short };
});
// Positions: "position 4" -> short def
(DATA.meta.position_definitions || []).forEach(p => {
  GLOSSARY[p.id.toLowerCase()] = { term: p.id + ': ' + p.title, type: 'position', def: p.short };
});
// Layers: match display names
(DATA.meta.layer_descriptions || []).forEach(l => {
  GLOSSARY[l.name.toLowerCase()] = { term: l.name, type: 'layer', def: l.description };
});

// Build sorted keys for regex (longest first to avoid partial matches)
const GLOSSARY_KEYS = Object.keys(GLOSSARY).sort((a, b) => b.length - a.length);
const GLOSSARY_RE = GLOSSARY_KEYS.length > 0
  ? new RegExp('\\b(' + GLOSSARY_KEYS.map(k => k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|') + ')\\b', 'gi')
  : null;

function addGlossaryTooltips(container) {
  if (!GLOSSARY_RE) return;
  const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, {
    acceptNode: function(node) {
      const p = node.parentElement;
      if (!p) return NodeFilter.FILTER_REJECT;
      if (p.closest('code, pre, h1, h2, h3, .cross-ref, .glossary-term, .meta-bar, nav, .analysis-toc'))
        return NodeFilter.FILTER_REJECT;
      return NodeFilter.FILTER_ACCEPT;
    }
  });
  const textNodes = [];
  while (walker.nextNode()) textNodes.push(walker.currentNode);

  const seen = new Set();
  textNodes.forEach(function(node) {
    GLOSSARY_RE.lastIndex = 0;
    if (!GLOSSARY_RE.test(node.textContent)) return;
    GLOSSARY_RE.lastIndex = 0;
    const frag = document.createDocumentFragment();
    let lastIdx = 0;
    const text = node.textContent;
    let match;
    while ((match = GLOSSARY_RE.exec(text)) !== null) {
      const key = match[1].toLowerCase();
      const entry = GLOSSARY[key];
      if (!entry) continue;
      if (match.index > lastIdx)
        frag.appendChild(document.createTextNode(text.slice(lastIdx, match.index)));
      const span = document.createElement('span');
      span.className = 'glossary-term';
      if (entry.nodeId) {
        span.classList.add('glossary-nav');
        span.addEventListener('click', (function(nid) {
          return function() {
            var tip = document.getElementById('glossary-tooltip');
            if (tip) tip.style.display = 'none';
            selectNode(nid, { forceDetail: true });
          };
        })(entry.nodeId));
      }
      if (!seen.has(key)) {
        span.classList.add('glossary-first');
        seen.add(key);
      }
      span.dataset.term = key;
      span.textContent = match[0];
      frag.appendChild(span);
      lastIdx = match.index + match[0].length;
    }
    if (lastIdx < text.length)
      frag.appendChild(document.createTextNode(text.slice(lastIdx)));
    if (lastIdx > 0) node.parentNode.replaceChild(frag, node);
  });
}

// Tooltip element (single shared instance)
(function() {
  const tip = document.createElement('div');
  tip.id = 'glossary-tooltip';
  tip.innerHTML = '<div class="gt-title"></div><div class="gt-type"></div><div class="gt-def"></div>';
  document.body.appendChild(tip);

  document.getElementById('detail-view').addEventListener('mouseover', function(e) {
    const el = e.target.closest('.glossary-term');
    if (!el) return;
    const entry = GLOSSARY[el.dataset.term];
    if (!entry) return;
    tip.querySelector('.gt-title').textContent = entry.term;
    tip.querySelector('.gt-type').textContent = entry.type;
    tip.querySelector('.gt-def').textContent = entry.def;
    tip.style.display = 'block';
    const rect = el.getBoundingClientRect();
    let left = rect.left;
    let top = rect.bottom + 6;
    if (left + 340 > window.innerWidth) left = window.innerWidth - 350;
    if (top + 120 > window.innerHeight) top = rect.top - 6 - tip.offsetHeight;
    tip.style.left = left + 'px';
    tip.style.top = top + 'px';
  });
  document.getElementById('detail-view').addEventListener('mouseout', function(e) {
    const el = e.target.closest('.glossary-term');
    if (!el) return;
    tip.style.display = 'none';
  });
  document.getElementById('detail-view').addEventListener('click', function(e) {
    const el = e.target.closest('.glossary-term');
    if (!el) return;
    const entry = GLOSSARY[el.dataset.term];
    if (entry && entry.nodeId && nodeMap[entry.nodeId]) {
      tip.style.display = 'none';
      selectNode(entry.nodeId, { forceDetail: true });
    }
  });
})();

// Graph state (persistent across rebuilds for focus mode)
let graphSvg = null;
let graphZoom = null;
let graphNodeSel = null;
let graphLinkSel = null;
let activeLayerIdx = 0;

// ---------------------------------------------------------------------------
// Sidebar
// ---------------------------------------------------------------------------
function getDisplayTitle(node) {
  if (node.type === 'analysis') {
    return node.title.replace(/^Analysis:\s*/i, '');
  }
  if (node.type === 'principle') {
    return node.title.replace(/^Principles:\s*/i, '');
  }
  return node.title;
}

function getSubtitle(node) {
  if (node.type === 'analysis') {
    const parts = [];
    if (node.meta.source) parts.push(node.meta.source);
    if (node.meta.date) {
      let ts = node.meta.date;
      if (node.meta.time) ts += ' ' + node.meta.time;
      parts.push(ts);
    }
    return parts.join(' — ');
  }
  if (node.type === 'evidence') {
    const parts = [];
    if (node.meta.source) parts.push(node.meta.source);
    if (node.meta.date) parts.push(node.meta.date);
    return parts.join(' — ');
  }
  if (node.type === 'principle') {
    return node.meta.source || '';
  }
  if (node.type === 'circumvention') {
    return node.meta.tier === 'hegemonic' ? 'hegemonic' : 'structural';
  }
  return '';
}

function buildSidebar() {
  const list = document.getElementById('sidebar-list');

  // Save expand/collapse state before clearing
  list.querySelectorAll('.sidebar-group').forEach(g => {
    const type = g.dataset.type;
    if (type) sidebarCollapseState[type] = g.classList.contains('collapsed');
  });

  list.innerHTML = '';
  const q = searchQuery.toLowerCase();

  TYPE_ORDER.forEach(type => {
    if (!activeFilters.has(type)) return;
    let items = DATA.nodes
      .filter(n => n.type === type)
      .filter(n => !q || n.title.toLowerCase().includes(q) || n.content.toLowerCase().includes(q));
    if (type === 'analysis') {
      items.sort((a, b) => (b.meta.date || '').localeCompare(a.meta.date || ''));
    } else if (type === 'circumvention') {
      // Sort hegemonic circumventions first, then alphabetical within each tier
      items.sort((a, b) => {
        const ta = a.meta.tier === 'hegemonic' ? 0 : 1;
        const tb = b.meta.tier === 'hegemonic' ? 0 : 1;
        if (ta !== tb) return ta - tb;
        return a.title.localeCompare(b.title);
      });
    } else {
      items.sort((a, b) => a.title.localeCompare(b.title));
    }

    if (items.length === 0) return;

    const group = document.createElement('div');
    group.className = 'sidebar-group';
    group.dataset.type = type;
    group.innerHTML =
      '<div class="sidebar-group-header">' +
        '<span class="chevron">&#9660;</span>' +
        TYPE_LABELS[type] + ' <span class="count">(' + items.length + ')</span>' +
      '</div>' +
      '<div class="sidebar-group-items"></div>';

    const header = group.querySelector('.sidebar-group-header');
    header.addEventListener('click', () => { group.classList.toggle('collapsed'); });

    const container = group.querySelector('.sidebar-group-items');
    items.forEach(n => {
      const item = document.createElement('div');
      item.className = 'sidebar-item' + (selectedNode && selectedNode.id === n.id ? ' active' : '');
      item.dataset.nodeId = n.id;
      const displayTitle = getDisplayTitle(n);
      const subtitle = getSubtitle(n);

      // Build badges
      let badges = '';
      const degree = nodeDegree[n.id] || 0;
      if (n.type === 'pattern') {
        const corr = (n.meta.corroboration || '').split(' ')[0];
        const cls = corr === 'ESTABLISHED' ? 'badge-established' :
                    corr === 'SUPPORTED' ? 'badge-supported' : 'badge-preliminary';
        const label = corr === 'ESTABLISHED' ? 'EST' :
                      corr === 'SUPPORTED' ? 'SUP' : 'PRE';
        badges = '<span class="item-badges"><span class="badge ' + cls + '">' + label + '</span></span>';
      } else if (degree > 2) {
        badges = '<span class="item-badges"><span class="badge badge-degree">' + degree + '</span></span>';
      }

      const dotColor = (type === 'circumvention' && n.meta.tier === 'hegemonic') ? '#da7756' : TYPE_COLORS[type];
      let html = badges +
        '<span class="type-dot" style="background:' + dotColor + '"></span>' + escapeHtml(displayTitle);
      if (subtitle) {
        html += '<span class="item-subtitle">' + escapeHtml(subtitle) + '</span>';
      }
      item.innerHTML = html;
      item.addEventListener('click', () => selectNode(n.id));
      container.appendChild(item);
    });

    list.appendChild(group);
  });

  // Restore expand/collapse state
  list.querySelectorAll('.sidebar-group').forEach(g => {
    const type = g.dataset.type;
    if (type && sidebarCollapseState[type]) g.classList.add('collapsed');
  });

  // Red Team section — show self-examination evidence items
  // Only show when all filters are active or when in redteam view
  const allFiltersOn = activeFilters.size === TYPE_ORDER.length;
  const rtIds = (DATA.meta.health || {}).red_team_ids || [];
  if (rtIds.length > 0 && (allFiltersOn || currentView === 'redteam')) {
    const rtGroup = document.createElement('div');
    rtGroup.className = 'sidebar-group sidebar-redteam';
    rtGroup.dataset.type = 'redteam';
    rtGroup.innerHTML =
      '<div class="sidebar-group-header">' +
        '<span class="chevron">&#9660;</span>' +
        'Red Team <span class="count">(' + rtIds.length + ')</span>' +
      '</div>' +
      '<div class="sidebar-group-items"></div>';
    const rtHeader = rtGroup.querySelector('.sidebar-group-header');
    rtHeader.addEventListener('click', () => { rtGroup.classList.toggle('collapsed'); });
    const rtContainer = rtGroup.querySelector('.sidebar-group-items');
    rtIds.forEach(id => {
      const n = nodeMap[id];
      if (!n) return;
      const item = document.createElement('div');
      item.className = 'sidebar-item' + (selectedNode && selectedNode.id === n.id ? ' active' : '');
      item.dataset.nodeId = n.id;
      item.innerHTML =
        '<span class="type-dot" style="background:var(--red)"></span>' +
        escapeHtml(getDisplayTitle(n)) +
        '<span class="item-subtitle">' + escapeHtml(n.meta.date || '') + '</span>';
      item.addEventListener('click', () => selectNode(n.id));
      rtContainer.appendChild(item);
    });
    if (sidebarCollapseState['redteam']) rtGroup.classList.add('collapsed');
    list.appendChild(rtGroup);
  }
}

// ---------------------------------------------------------------------------
// Dashboard view
// ---------------------------------------------------------------------------
function buildDashboard() {
  const view = document.getElementById('dashboard-view');

  const typeCounts = {};
  TYPE_ORDER.forEach(t => { typeCounts[t] = 0; });
  DATA.nodes.forEach(n => { typeCounts[n.type] = (typeCounts[n.type] || 0) + 1; });

  const patterns = DATA.nodes.filter(n => n.type === 'pattern');
  const corroboration = { ESTABLISHED: 0, SUPPORTED: 0, PRELIMINARY: 0 };
  patterns.forEach(p => {
    const c = (p.meta.corroboration || '').split(' ')[0];
    if (corroboration.hasOwnProperty(c)) corroboration[c]++;
  });

  // Compute layer coverage counts
  const layerCoverage = {};
  LAYER_NAMES.forEach(l => { layerCoverage[l] = 0; });
  DATA.nodes.forEach(n => {
    if (n.meta && n.meta.layer_list) {
      n.meta.layer_list.forEach(l => {
        if (layerCoverage.hasOwnProperty(l)) layerCoverage[l]++;
      });
    }
  });
  const maxCoverage = Math.max(1, ...Object.values(layerCoverage));

  let html = '';


  // --- Recent Analyses ---
  const analyses = DATA.nodes
    .filter(n => n.type === 'analysis')
    .sort((a, b) => (b.meta.date || '').localeCompare(a.meta.date || ''));
  if (analyses.length > 0) {
    html += '<div class="dashboard-section"><h2>Recent Analyses</h2><div class="recent-analyses-grid dashboard-grid-expandable" data-section="analyses">';
    analyses.forEach(a => {
      const title = getDisplayTitle(a);
      const dateParts = [];
      if (a.meta.date) dateParts.push(a.meta.date);
      if (a.meta.time) dateParts.push(a.meta.time);
      const dateStr = dateParts.join(' ');
      // Extract first sentence of briefing from content
      let briefing = '';
      const briefMatch = a.content.match(/## Briefing[\s\S]*?\n\n([\s\S]*?)(?:\n\n## |\n---)/);
      if (briefMatch) {
        briefing = briefMatch[1].replace(/\*\*/g, '').replace(/\n/g, ' ').trim();
        if (briefing.length > 200) briefing = briefing.substring(0, 200) + '...';
      }
      html += '<div class="recent-analysis-card" data-id="' + a.id + '">';
      html += '<div class="recent-analysis-date">' + escapeHtml(dateStr) + '</div>';
      html += '<div class="recent-analysis-title">' + escapeHtml(title) + '</div>';
      if (a.meta.source) html += '<div class="recent-analysis-source">' + escapeHtml(a.meta.source) + '</div>';
      if (briefing) html += '<div class="recent-analysis-briefing">' + escapeHtml(briefing) + '</div>';
      html += '</div>';
    });
    html += '</div>';
    if (analyses.length > 6) {
      html += '<button class="show-all-toggle" data-section="analyses">Show all ' + analyses.length + ' analyses</button>';
    }
    html += '</div>';
  }

  // --- Works studied ---
  const principles = DATA.nodes.filter(n => n.type === 'principle');
  if (principles.length > 0) {
    const sorted = principles.slice().sort((a, b) => (b.meta.principle_count || 0) - (a.meta.principle_count || 0));
    html += '<div class="dashboard-section"><h2>Works Studied</h2><div class="works-grid dashboard-grid-expandable" data-section="works">';
    sorted.forEach(p => {
      const title = getDisplayTitle(p);
      const source = p.meta.source || '';
      const count = p.meta.principle_count || 0;
      const layers = (p.meta.layer_list || []);
      html += '<div class="work-card" data-id="' + p.id + '">' +
        '<div class="work-card-title">' + escapeHtml(title) + '</div>' +
        '<div class="work-card-source">' + escapeHtml(source) + '</div>' +
        '<div class="work-card-meta">' +
          '<span class="work-count">' + count + ' principles</span>' +
          '<span class="work-layers">' + layers.length + ' layers</span>' +
        '</div>' +
      '</div>';
    });
    html += '</div>';
    if (sorted.length > 6) {
      html += '<button class="show-all-toggle" data-section="works">Show all ' + sorted.length + ' works</button>';
    }
    html += '</div>';
  }

  // --- Layers of Power with coverage ---
  const layerDescs = DATA.meta.layer_descriptions || [];
  if (layerDescs.length > 0) {
    html += '<div class="dashboard-section"><h2>Layers of Power</h2><div class="layer-cards">';
    layerDescs.forEach(l => {
      const count = layerCoverage[l.name] || 0;
      const pct = Math.round((count / maxCoverage) * 100);
      html += '<div class="layer-card" data-layer="' + escapeHtml(l.name) + '">' +
        '<div class="layer-card-name">' + escapeHtml(l.name) + '</div>' +
        '<div class="layer-card-desc">' + escapeHtml(l.description) + '</div>' +
        '<div class="layer-card-coverage">' +
          '<div class="layer-coverage-bar"><div class="layer-coverage-fill" style="width:' + pct + '%"></div></div>' +
          '<span class="layer-coverage-count">' + count + ' items</span>' +
        '</div>' +
      '</div>';
    });
    html += '</div></div>';
  }

  // --- Circumventions (two tiers) ---
  const circumventions = DATA.nodes.filter(n => n.type === 'circumvention');
  if (circumventions.length > 0) {
    const structural = circumventions.filter(c => (c.meta.tier || 'structural') === 'structural');
    const hegemonic = circumventions.filter(c => c.meta.tier === 'hegemonic');

    html += '<div class="dashboard-section"><h2>Circumventions</h2>' +
      '<p style="color:var(--text-muted);font-size:13px;margin-bottom:14px">Observed responses to power concentration at two tiers. <strong>Structural</strong> circumventions contest specific power arrangements within the existing hegemonic frame. <strong>Hegemonic</strong> circumventions contest the frame itself.</p>';

    // Tier 1: Structural
    html += '<h3 style="color:var(--text-secondary);font-size:14px;margin:16px 0 8px;border-bottom:1px solid var(--border);padding-bottom:4px">Structural <span style="color:var(--text-muted);font-weight:normal">(' + structural.length + ')</span></h3>' +
      '<div class="circumvention-cards">';
    structural.forEach(c => {
      const counteracts = (c.meta.counteracts || '').split(',').map(s => s.trim()).filter(Boolean);
      html += '<div class="circumvention-card" data-id="' + c.id + '">' +
        '<div class="circumvention-card-name">' + escapeHtml(c.title) + '</div>' +
        '<div class="circumvention-card-stmt">' + escapeHtml(c.meta.statement || '') + '</div>';
      if (counteracts.length > 0) {
        html += '<div class="circumvention-card-counteracts">';
        counteracts.forEach(p => {
          html += '<span class="circumvention-counteracts-tag">' + escapeHtml(p) + '</span>';
        });
        html += '</div>';
      }
      html += '</div>';
    });
    html += '</div>';

    // Tier 2: Hegemonic
    if (hegemonic.length > 0) {
      html += '<h3 style="color:#da7756;font-size:14px;margin:20px 0 8px;border-bottom:1px solid rgba(218,119,86,0.3);padding-bottom:4px">Hegemonic <span style="color:var(--text-muted);font-weight:normal">(' + hegemonic.length + ')</span></h3>' +
        '<div class="circumvention-cards">';
      hegemonic.forEach(c => {
        const counteracts = (c.meta.counteracts || '').split(',').map(s => s.trim()).filter(Boolean);
        html += '<div class="circumvention-card" style="border-color:rgba(218,119,86,0.3)" data-id="' + c.id + '">' +
          '<div class="circumvention-card-name" style="color:#da7756">' + escapeHtml(c.title) + '</div>' +
          '<div class="circumvention-card-stmt">' + escapeHtml(c.meta.statement || '') + '</div>';
        if (counteracts.length > 0) {
          html += '<div class="circumvention-card-counteracts">';
          counteracts.forEach(p => {
            html += '<span class="circumvention-counteracts-tag" style="background:rgba(218,119,86,0.15);color:#da7756">' + escapeHtml(p) + '</span>';
          });
          html += '</div>';
        }
        html += '</div>';
      });
      html += '</div>';
    }

    html += '</div>';
  }

  // --- Hegemonic Contexts (IC-7) ---
  const hcNodes = DATA.nodes.filter(n => n.type === 'hegemonic_context');
  if (hcNodes.length > 0) {
    // Count analyses per context via edges
    const hcAnalysisCounts = {};
    hcNodes.forEach(hc => { hcAnalysisCounts[hc.id] = 0; });
    const totalAnalyses = DATA.nodes.filter(n => n.type === 'analysis').length;
    DATA.edges.forEach(e => {
      if (e.type === 'operates_within' && hcAnalysisCounts.hasOwnProperty(e.target)) {
        hcAnalysisCounts[e.target]++;
      }
    });
    const hcSorted = hcNodes.slice().sort((a, b) => (hcAnalysisCounts[b.id] || 0) - (hcAnalysisCounts[a.id] || 0));
    const maxHC = Math.max(1, ...Object.values(hcAnalysisCounts));

    html += '<div class="dashboard-section"><h2>Hegemonic Contexts (IC-7)</h2>' +
      '<p style="color:var(--text-muted);font-size:13px;margin-bottom:14px">Background assumptions shared by analyses and analyst. See IC-7.</p>' +
      '<div class="hegemonic-context-cards">';
    hcSorted.forEach(hc => {
      const count = hcAnalysisCounts[hc.id] || 0;
      const pct = Math.round((count / maxHC) * 100);
      const muted = count === 0 ? ' style="opacity:0.5"' : '';
      html += '<div class="hegemonic-context-card" data-id="' + hc.id + '"' + muted + '>' +
        '<div class="hc-card-name">' + escapeHtml(hc.title) + '</div>' +
        '<div class="hc-card-desc">' + escapeHtml(hc.content) + '</div>' +
        '<div class="hc-card-bar">' +
          '<div class="hc-bar-fill" style="width:' + pct + '%;background:#da7756"></div>' +
        '</div>' +
        '<div class="hc-card-count">' + count + ' of ' + totalAnalyses + ' analyses</div>' +
      '</div>';
    });
    html += '</div></div>';
  }

  // --- Documentation sections (collapsible) ---
  const sections = DATA.meta.readme_sections || {};
  if (sections.core_concepts) {
    html += '<div class="dashboard-section">' +
      '<div class="dashboard-section-header collapsible"><span class="section-chevron">&#9660;</span><h2>Core Concepts</h2></div>' +
      '<div class="dashboard-content">' + marked.parse(sections.core_concepts) + '</div></div>';
  }
  if (sections.how_framework_grows) {
    html += '<div class="dashboard-section">' +
      '<div class="dashboard-section-header collapsible"><span class="section-chevron">&#9660;</span><h2>How the Framework Grows</h2></div>' +
      '<div class="dashboard-content">' + marked.parse(sections.how_framework_grows) + '</div></div>';
  }
  if (sections.integrity_constraints) {
    html += '<div class="dashboard-section">' +
      '<div class="dashboard-section-header collapsible"><span class="section-chevron">&#9660;</span><h2>Integrity Constraints</h2></div>' +
      '<div class="dashboard-content">' + marked.parse(sections.integrity_constraints) + '</div></div>';
  }

  view.innerHTML = html;

  // Work card click handlers
  view.querySelectorAll('.work-card').forEach(card => {
    card.addEventListener('click', () => {
      const id = card.dataset.id;
      if (id && nodeMap[id]) selectNode(id, { forceDetail: true });
    });
  });

  // Recent analysis card click handlers
  view.querySelectorAll('.recent-analysis-card').forEach(card => {
    card.addEventListener('click', () => {
      const id = card.dataset.id;
      if (id && nodeMap[id]) selectNode(id, { forceDetail: true });
    });
  });

  // Layer card click handlers — navigate to Layers view with that layer selected
  view.querySelectorAll('.layer-card').forEach(card => {
    card.addEventListener('click', () => {
      const layerName = card.dataset.layer;
      const idx = LAYER_NAMES.indexOf(layerName);
      if (idx >= 0) activeLayerIdx = idx;
      switchView('layers');
    });
  });

  // Circumvention card click handlers
  view.querySelectorAll('.circumvention-card').forEach(card => {
    card.addEventListener('click', () => {
      const id = card.dataset.id;
      if (id && nodeMap[id]) selectNode(id, { forceDetail: true });
    });
  });

  // Hegemonic context card click handlers
  view.querySelectorAll('.hegemonic-context-card').forEach(card => {
    card.addEventListener('click', () => {
      const id = card.dataset.id;
      if (id && nodeMap[id]) selectNode(id, { forceDetail: true });
    });
  });

  // Expand/collapse toggle for dashboard grids
  function setupExpandToggle(section) {
    const btn = view.querySelector('.show-all-toggle[data-section="' + section + '"]');
    const grid = view.querySelector('.dashboard-grid-expandable[data-section="' + section + '"]');
    if (!btn || !grid) return;
    btn.addEventListener('click', () => {
      const expanded = grid.classList.toggle('expanded');
      btn.textContent = expanded ? 'Show fewer' : btn.dataset.label;
    });
    btn.dataset.label = btn.textContent;
  }
  setupExpandToggle('analyses');
  setupExpandToggle('works');

  // Collapsible documentation section handlers
  view.querySelectorAll('.dashboard-section-header.collapsible').forEach(header => {
    header.addEventListener('click', () => {
      header.closest('.dashboard-section').classList.toggle('collapsed');
    });
  });
}

// ---------------------------------------------------------------------------
// Detail view
// ---------------------------------------------------------------------------
function showDetail(nodeId) {
  const node = nodeMap[nodeId];
  if (!node) return;

  const view = document.getElementById('detail-view');

  // Meta bar
  let metaHtml = '<div class="meta-bar"><span class="meta-tag type-' + node.type + '">' + node.type + '</span>';
  if (node.meta) {
    Object.entries(node.meta).forEach(([k, v]) => {
      if (v && typeof v === 'string' && v.length < 100 && k !== 'statement' && k !== 'mechanism' && k !== 'layer_list') {
        metaHtml += '<span class="meta-tag" style="background:rgba(255,255,255,0.06);color:var(--text-muted)">' + k + ': ' + escapeHtml(v) + '</span>';
      }
    });
  }
  metaHtml += '</div>';

  // Render markdown
  let rendered = marked.parse(node.content);
  rendered = rendered.replace(
    /(?:(?:principles|analyses|instruments|evidence)\/[\w\-]+\.md)/g,
    function(match) {
      if (nodeMap[match]) {
        return '<span class="cross-ref" data-target="' + match + '">' + escapeHtml(nodeMap[match].title || match) + '</span>';
      }
      return match;
    }
  );

  // Second pass: link parenthetical references like (relay class) to patterns
  const patternLookup = {};
  DATA.nodes.forEach(n => {
    if (n.type === 'pattern') {
      const key = n.title.replace(/^The\s+/i, '').toLowerCase();
      patternLookup[key] = n.id;
    }
  });
  rendered = rendered.replace(
    /\(([^)<]{2,60})\)/g,
    function(match, term) {
      const key = term.toLowerCase();
      if (patternLookup[key]) {
        return '(<span class="cross-ref" data-target="' +
          patternLookup[key] + '">' + escapeHtml(term) + '</span>)';
      }
      return match;
    }
  );

  // Third pass: for circumvention/pattern nodes, add a lookup so parenthetical
  // references to circumvention names also get linked (extending pass 2)
  if (node.type === 'circumvention' || node.type === 'pattern') {
    const circumventionLookup = {};
    DATA.nodes.forEach(n => {
      if (n.type === 'circumvention') {
        circumventionLookup[n.title.toLowerCase()] = n.id;
      }
    });
    rendered = rendered.replace(
      /\(([^)<]{2,60})\)/g,
      function(match, term) {
        const key = term.toLowerCase();
        if (circumventionLookup[key]) {
          return '(<span class="cross-ref" data-target="' +
            circumventionLookup[key] + '">' + escapeHtml(term) + '</span>)';
        }
        return match;
      }
    );
  }

  // Connected items
  const adj = adjacency[nodeId] || { incoming: [], outgoing: [] };
  const connected = new Map();
  adj.outgoing.forEach(e => {
    const target = nodeMap[e.target];
    if (target) connected.set(e.target, { node: target, type: e.type, direction: 'outgoing' });
  });
  adj.incoming.forEach(e => {
    const source = nodeMap[e.source];
    if (source) connected.set(e.source, { node: source, type: e.type, direction: 'incoming' });
  });

  let connectedHtml = '';
  if (connected.size > 0) {
    connectedHtml = '<div id="connected-panel"><h3>Connected Items</h3>';
    connected.forEach((info, id) => {
      const color = TYPE_COLORS[info.node.type];
      connectedHtml += '<span class="connected-item" data-target="' + id + '" style="border-color:' + color + '40">' +
        '<span class="type-dot" style="background:' + color + '"></span>' +
        escapeHtml(info.node.title) +
        '<span style="color:var(--text-muted);font-size:11px;margin-left:4px">' + info.type + '</span>' +
      '</span>';
    });
    connectedHtml += '</div>';
  }

  // For circumventions: prepend styled outcome range block
  let outcomeHtml = '';
  if (node.type === 'circumvention' && node.meta.outcome_range) {
    outcomeHtml = '<div class="outcome-range-block">' +
      '<div class="outcome-range-label">Outcome range</div>' +
      '<div class="outcome-range-text">' + escapeHtml(node.meta.outcome_range) + '</div>' +
    '</div>';
  }

  // For hegemonic contexts: custom detail rendering
  if (node.type === 'hegemonic_context') {
    // Find all analyses that operate within this context
    const hcAnalyses = [];
    DATA.edges.forEach(e => {
      if (e.type === 'operates_within' && e.target === node.id) {
        const an = nodeMap[e.source];
        if (an) hcAnalyses.push(an);
      }
    });
    const totalAnalyses = DATA.nodes.filter(n => n.type === 'analysis').length;

    let hcHtml = metaHtml;
    hcHtml += '<div id="detail-content">';
    hcHtml += '<h1>' + escapeHtml(node.title) + '</h1>';
    hcHtml += '<p style="font-size:14px;line-height:1.7;margin:16px 0 24px 0">' + escapeHtml(node.content) + '</p>';
    hcHtml += '<div style="font-size:13px;color:var(--text-muted);margin-bottom:16px"><strong>' + hcAnalyses.length + '</strong> of <strong>' + totalAnalyses + '</strong> analyses operate within this background</div>';

    if (hcAnalyses.length > 0) {
      hcHtml += '<h3 style="margin-bottom:12px">Tagged Analyses</h3>';
      hcAnalyses.sort((a, b) => (b.meta.date || '').localeCompare(a.meta.date || ''));
      hcAnalyses.forEach(a => {
        const color = TYPE_COLORS.analysis;
        hcHtml += '<span class="connected-item" data-target="' + a.id + '" style="border-color:' + color + '40">' +
          '<span class="type-dot" style="background:' + color + '"></span>' +
          escapeHtml(getDisplayTitle(a)) +
          '<span style="color:var(--text-muted);font-size:11px;margin-left:4px">' + (a.meta.date || '') + '</span>' +
        '</span>';
      });
    }

    hcHtml += '</div>';
    view.innerHTML = hcHtml;
    view.scrollTop = 0;

    // Wire up click handlers for linked analyses
    view.querySelectorAll('.connected-item[data-target]').forEach(el => {
      el.addEventListener('click', () => selectNode(el.dataset.target, { forceDetail: true }));
    });
    return;
  }

  view.innerHTML = metaHtml + outcomeHtml + '<div id="detail-content">' + rendered + '</div>' + connectedHtml;
  view.scrollTop = 0;

  // For analyses: reorder sections, build TOC, add collapsible controls
  if (node.type === 'analysis') {
    const content = view.querySelector('#detail-content');
    if (content) {
      // Remove markdown-generated "Contents" section (viewer builds its own TOC)
      const allH2s = content.querySelectorAll('h2');
      allH2s.forEach(h => {
        if (h.textContent.trim().toLowerCase() === 'contents') {
          let sib = h.nextElementSibling;
          while (sib && sib.tagName !== 'H2') {
            const next = sib.nextElementSibling;
            sib.remove();
            sib = next;
          }
          h.remove();
        }
      });

      // --- Section reordering ---
      // Collect each H2 and its content as a group
      const h2s = Array.from(content.querySelectorAll('h2'));
      if (h2s.length > 1) {
        const sectionGroups = [];
        let afterHr = false;
        h2s.forEach(function(h) {
          const nodes = [h];
          let sib = h.nextElementSibling;
          while (sib && sib.tagName !== 'H2') {
            if (sib.tagName === 'HR') afterHr = true;
            nodes.push(sib);
            sib = sib.nextElementSibling;
          }
          const text = h.textContent.toLowerCase().trim();
          sectionGroups.push({ heading: h, nodes: nodes, text: text, afterHr: afterHr });
        });

        // Priority order for reordering (index = priority, lower = earlier)
        const priorityPatterns = [
          /^briefing|^summary$/,
          /^narrative/,
          /^so what|^implications/,
          /^circumvention/,
          /^finding/,
          /^watch/,
          /^null case/,
        ];
        function getPriority(text) {
          for (var i = 0; i < priorityPatterns.length; i++) {
            if (priorityPatterns[i].test(text)) return i;
          }
          return 100; // unprioritized
        }

        // Separate into above-HR (human-readable) and below-HR (working/apparatus)
        const aboveHr = sectionGroups.filter(function(s) { return !s.afterHr; });
        const belowHr = sectionGroups.filter(function(s) { return s.afterHr; });

        // Sort above-HR sections by priority
        aboveHr.sort(function(a, b) { return getPriority(a.text) - getPriority(b.text); });

        // Remove all H2 sections from DOM, then re-insert in order
        // First, find the HR element
        const hrEl = content.querySelector('hr');
        sectionGroups.forEach(function(s) {
          s.nodes.forEach(function(n) { if (n.parentNode) n.parentNode.removeChild(n); });
        });

        // Re-insert: above-HR sections, then HR, then below-HR sections
        const insertBefore = hrEl || null;
        aboveHr.forEach(function(s) {
          s.nodes.forEach(function(n) {
            if (insertBefore) content.insertBefore(n, insertBefore);
            else content.appendChild(n);
          });
        });
        // Below-HR sections stay in original order (after the HR)
        belowHr.forEach(function(s) {
          s.nodes.forEach(function(n) { content.appendChild(n); });
        });

        // --- Collapsible sections ---
        const defaultCollapsedRe = /^analytical working|^analytical apparatus|^apparatus|^material summary|^step \d/;
        const reorderedH2s = Array.from(content.querySelectorAll('h2'));
        let hitHr = false;
        reorderedH2s.forEach(function(h) {
          // Check if this H2 follows an HR (below the delimiter = working)
          let prev = h.previousElementSibling;
          while (prev && prev.tagName !== 'H2' && prev.tagName !== 'HR') prev = prev.previousElementSibling;
          if (prev && prev.tagName === 'HR') hitHr = true;

          const text = h.textContent.toLowerCase().trim();
          const shouldCollapse = hitHr || defaultCollapsedRe.test(text);

          // Wrap section content in collapsible div
          const wrapper = document.createElement('div');
          wrapper.className = 'collapsible-section' + (shouldCollapse ? ' collapsed' : '');
          let sib = h.nextElementSibling;
          while (sib && sib.tagName !== 'H2' && sib.tagName !== 'HR') {
            const next = sib.nextElementSibling;
            wrapper.appendChild(sib);
            sib = next;
          }
          h.after(wrapper);

          // Add chevron toggle
          const chevron = document.createElement('span');
          chevron.className = 'section-chevron';
          chevron.innerHTML = shouldCollapse ? '&#9654;' : '&#9660;';
          h.prepend(chevron);
          h.classList.add('collapsible-h2');
          h.addEventListener('click', function(e) {
            if (e.target.classList.contains('back-to-top')) return;
            wrapper.classList.toggle('collapsed');
            chevron.innerHTML = wrapper.classList.contains('collapsed') ? '&#9654;' : '&#9660;';
            // Update TOC link style
            var tocLink = content.querySelector('.toc-link[href="#' + h.id + '"]');
            if (tocLink) {
              if (wrapper.classList.contains('collapsed')) tocLink.classList.add('toc-collapsed');
              else tocLink.classList.remove('toc-collapsed');
            }
          });
        });

        // --- Build TOC ---
        const finalH2s = content.querySelectorAll('h2');
        let tocHtml = '<nav class="analysis-toc"><div class="toc-title">Contents</div>';
        // Add metadata entry if there's content before the first H2
        const firstH2 = finalH2s[0];
        if (firstH2) {
          let hasPreContent = false;
          let sib = content.firstElementChild;
          while (sib && sib !== firstH2) {
            if (sib.tagName !== 'NAV' && sib.textContent.trim()) { hasPreContent = true; break; }
            sib = sib.nextElementSibling;
          }
          if (hasPreContent) {
            const metaAnchor = document.createElement('span');
            metaAnchor.id = 'section-meta';
            content.insertBefore(metaAnchor, content.firstElementChild);
            tocHtml += '<a class="toc-link" href="#section-meta">Metadata</a>';
          }
        }
        finalH2s.forEach(function(h, i) {
          h.id = 'section-' + i;
          let text = h.textContent.replace(/[\u25B6\u25BC]/g, '').trim(); // Remove chevron chars
          const hText = text.toLowerCase().trim();
          const isBriefing = hText.includes('briefing') || hText === 'summary';
          const isSoWhat = /^so what|^implications/.test(hText);
          // Format step headings: "Step 3: LOCATE" -> "3. Locate"
          const stepMatch = text.match(/^Step (\d+):\s*(.+)/);
          if (stepMatch) {
            const name = stepMatch[2].toLowerCase().replace(/(^|[-])(\w)/g, function(m, sep, c) { return sep + c.toUpperCase(); });
            text = stepMatch[1] + '. ' + name;
          }
          // Check if this section is collapsed
          const wrapper = h.nextElementSibling;
          const isCollapsed = wrapper && wrapper.classList && wrapper.classList.contains('collapsed');
          let cls = 'toc-link';
          if (isBriefing) cls += ' toc-briefing';
          if (isSoWhat) cls += ' toc-briefing'; // Highlight So What too
          if (isCollapsed) cls += ' toc-collapsed';
          tocHtml += '<a class="' + cls + '" href="#section-' + i + '">' + escapeHtml(text) + '</a>';
        });
        tocHtml += '</nav>';
        content.insertAdjacentHTML('afterbegin', tocHtml);

        // Add "back to top" link after each H2 heading
        content.querySelectorAll('h2').forEach(h => {
          const topLink = document.createElement('a');
          topLink.className = 'back-to-top';
          topLink.href = '#analysis-toc';
          topLink.textContent = 'Contents';
          h.appendChild(topLink);
        });

        const tocNav = content.querySelector('.analysis-toc');
        if (tocNav) tocNav.id = 'analysis-toc';

        // Smooth scroll for TOC links and back-to-top links
        content.querySelectorAll('.toc-link, .back-to-top').forEach(a => {
          a.addEventListener('click', (e) => {
            e.preventDefault();
            const target = content.querySelector(a.getAttribute('href'));
            if (target) {
              // If clicking a TOC link for a collapsed section, expand it first
              const h2 = target;
              if (h2.classList && h2.classList.contains('collapsible-h2')) {
                const wrapper = h2.nextElementSibling;
                if (wrapper && wrapper.classList.contains('collapsed')) {
                  h2.click();
                }
              }
              target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
          });
        });
      }

      // --- Add glossary tooltips to analysis content ---
      addGlossaryTooltips(content);
    }
  }

  // For patterns: append corroborating source links after the CORROBORATION line
  if (node.type === 'pattern') {
    const content = view.querySelector('#detail-content');
    if (content) {
      // Collect corroborating sources from edges
      const adj = adjacency[nodeId] || { incoming: [], outgoing: [] };
      const sourceIds = new Set();
      adj.outgoing.forEach(e => {
        if (e.type === 'observed_in' && nodeMap[e.target]) sourceIds.add(e.target);
      });
      adj.incoming.forEach(e => {
        if ((e.type === 'key_pattern' || e.type === 'matches') && nodeMap[e.source]) sourceIds.add(e.source);
      });
      if (sourceIds.size > 0) {
        // Find the paragraph containing CORROBORATION
        const paras = content.querySelectorAll('p');
        let corrPara = null;
        paras.forEach(p => {
          if (p.textContent.match(/^CORROBORATION:/)) corrPara = p;
        });
        if (corrPara) {
          // Hit-rate bar
          const corrCount = node.meta.corr_count || 0;
          const corrRel = node.meta.corr_relevant || 0;
          const hitRate = node.meta.corr_hit_rate || 0;
          const level = node.meta.corr_level || 'PRELIMINARY';
          const barColor = level === 'ESTABLISHED' ? 'var(--green)' : level === 'SUPPORTED' ? 'var(--orange)' : 'var(--text-muted)';
          const pct = corrRel > 0 ? Math.round(hitRate * 100) : 0;
          let barHtml = '<div style="margin:10px 0 6px 0;display:flex;align-items:center;gap:10px">' +
            '<div style="flex:1;height:6px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden;max-width:200px">' +
              '<div style="width:' + pct + '%;height:100%;background:' + barColor + ';border-radius:3px"></div>' +
            '</div>' +
            '<span style="font-size:12px;color:var(--text-muted)">' + corrCount + ' / ' + corrRel + ' relevant sources (' + pct + '%)</span>' +
          '</div>';
          corrPara.insertAdjacentHTML('afterend', barHtml);

          // Source links
          let linksHtml = '<div class="corroboration-sources">';
          sourceIds.forEach(id => {
            const sn = nodeMap[id];
            const color = TYPE_COLORS[sn.type];
            linksHtml += '<span class="connected-item corroboration-source" data-target="' + id + '" style="border-color:' + color + '40">' +
              '<span class="type-dot" style="background:' + color + '"></span>' +
              escapeHtml(sn.title) +
            '</span>';
          });
          linksHtml += '</div>';
          corrPara.nextElementSibling.insertAdjacentHTML('afterend', linksHtml);
        }
      }
    }
  }

  // Add glossary tooltips to all non-analysis node types too
  if (node.type !== 'analysis') {
    const detailContent = view.querySelector('#detail-content');
    if (detailContent) addGlossaryTooltips(detailContent);
  }

  // Attach click handlers for cross-refs
  view.querySelectorAll('.cross-ref, .connected-item').forEach(el => {
    el.addEventListener('click', () => {
      const target = el.dataset.target;
      if (target && nodeMap[target]) selectNode(target, { forceDetail: true });
    });
  });

  document.getElementById('main-title').textContent = getDisplayTitle(node);
}

// ---------------------------------------------------------------------------
// Graph view
// ---------------------------------------------------------------------------
function buildGraph() {
  const container = document.getElementById('graph-view');
  // Remove only the SVG, keep legend
  const oldSvg = container.querySelector('svg');
  if (oldSvg) oldSvg.remove();

  const width = container.clientWidth;
  const height = container.clientHeight;

  // Deep-copy nodes and edges so d3 mutations don't corrupt DATA
  const filteredNodes = DATA.nodes
    .filter(n => activeFilters.has(n.type))
    .map(n => Object.assign({}, n));
  const filteredIds = new Set(filteredNodes.map(n => n.id));
  const filteredEdges = DATA.edges
    .map(e => ({
      source: typeof e.source === 'object' ? e.source.id : e.source,
      target: typeof e.target === 'object' ? e.target.id : e.target,
      type: e.type,
    }))
    .filter(e => filteredIds.has(e.source) && filteredIds.has(e.target));

  const svg = d3.select(container).insert('svg', ':first-child')
    .attr('width', width)
    .attr('height', height);

  const g = svg.append('g');

  // Zoom
  const zoom = d3.zoom()
    .scaleExtent([0.1, 4])
    .on('zoom', (event) => g.attr('transform', event.transform));
  svg.call(zoom);

  // Simulation
  const simulation = d3.forceSimulation(filteredNodes)
    .force('link', d3.forceLink(filteredEdges).id(d => d.id).distance(80))
    .force('charge', d3.forceManyBody().strength(-200))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(d => nodeRadius(d) + 4));

  // Links
  const link = g.append('g')
    .selectAll('line')
    .data(filteredEdges)
    .join('line')
    .attr('class', 'graph-link')
    .attr('stroke', d => EDGE_COLORS[d.type] || '#30363d')
    .attr('stroke-width', 1);

  // Edge hover targets (wider invisible lines)
  const linkHover = g.append('g')
    .selectAll('line')
    .data(filteredEdges)
    .join('line')
    .attr('stroke', 'transparent')
    .attr('stroke-width', 8)
    .style('cursor', 'pointer');

  // Nodes
  const node = g.append('g')
    .selectAll('g')
    .data(filteredNodes)
    .join('g')
    .attr('class', 'graph-node')
    .call(d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended));

  node.append('circle')
    .attr('r', d => nodeRadius(d))
    .attr('fill', d => TYPE_COLORS[d.type])
    .attr('stroke', d => TYPE_COLORS[d.type]);

  node.append('text')
    .text(d => d.title.length > 25 ? d.title.substring(0, 25) + '...' : d.title)
    .attr('x', d => nodeRadius(d) + 4)
    .attr('y', 4);

  // Tooltip
  const tooltip = document.getElementById('graph-tooltip');
  let lockedNodeId = null;
  let hoveredNodeId = null;

  function positionTooltip(event) {
    const pad = 12;
    const tw = tooltip.offsetWidth;
    const th = tooltip.offsetHeight;
    let x = event.clientX + pad;
    let y = event.clientY - 20;
    if (x + tw > window.innerWidth - pad) x = event.clientX - tw - pad;
    if (y + th > window.innerHeight - pad) y = window.innerHeight - th - pad;
    if (y < pad) y = pad;
    tooltip.style.left = x + 'px';
    tooltip.style.top = y + 'px';
  }

  function unlockHighlight() {
    lockedNodeId = null;
    clearHighlight(node, link);
    tooltip.style.display = 'none';
    svg.classed('graph-locked', false);
  }

  // Keyboard: Space to lock/unlock, Escape to unlock
  function graphKeyHandler(e) {
    if (currentView !== 'graph') return;
    if (e.code === 'Space' && hoveredNodeId && !lockedNodeId) {
      e.preventDefault();
      lockedNodeId = hoveredNodeId;
      highlightNeighborhood(lockedNodeId, node, link);
      svg.classed('graph-locked', true);
    } else if ((e.code === 'Space' || e.code === 'Escape') && lockedNodeId) {
      e.preventDefault();
      unlockHighlight();
    }
  }
  document.addEventListener('keydown', graphKeyHandler);

  // Node hover
  node.on('mouseover', (event, d) => {
    hoveredNodeId = d.id;
    tooltip.querySelector('.tt-title').textContent = d.title;
    tooltip.querySelector('.tt-type').textContent = d.type;
    if (lockedNodeId) {
      tooltip.querySelector('.tt-type').textContent = d.type + ' (Space to unlock)';
    }
    tooltip.style.display = 'block';
    positionTooltip(event);
    if (!lockedNodeId) highlightNeighborhood(d.id, node, link);
  });

  node.on('mousemove', (event) => positionTooltip(event));

  node.on('mouseout', () => {
    hoveredNodeId = null;
    tooltip.style.display = 'none';
    if (!lockedNodeId) clearHighlight(node, link);
  });

  node.on('click', (event, d) => {
    selectNode(d.id, { forceDetail: true });
    if (lockedNodeId) unlockHighlight();
  });

  // Click on background to unlock
  svg.on('click', (event) => {
    if (event.target === svg.node() || event.target.tagName === 'svg') {
      if (lockedNodeId) unlockHighlight();
    }
  });

  // Edge hover
  linkHover.on('mouseover', (event, d) => {
    const srcId = typeof d.source === 'object' ? d.source.id : d.source;
    const tgtId = typeof d.target === 'object' ? d.target.id : d.target;
    tooltip.querySelector('.tt-title').textContent = EDGE_LABELS[d.type] || d.type;
    tooltip.querySelector('.tt-type').textContent =
      (nodeMap[srcId] ? nodeMap[srcId].title : srcId) + ' \u2192 ' +
      (nodeMap[tgtId] ? nodeMap[tgtId].title : tgtId);
    tooltip.style.display = 'block';
    positionTooltip(event);
  });

  linkHover.on('mousemove', (event) => positionTooltip(event));

  linkHover.on('mouseout', () => {
    tooltip.style.display = 'none';
  });

  simulation.on('tick', () => {
    link
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y);
    linkHover
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y);
    node.attr('transform', d => 'translate(' + d.x + ',' + d.y + ')');
  });

  // Store references for focus mode
  graphSvg = svg;
  graphZoom = zoom;
  graphNodeSel = node;
  graphLinkSel = link;

  // Build legend
  buildGraphLegend();

  // If a node is selected, focus on it
  if (selectedNode) {
    setTimeout(() => focusGraphNode(selectedNode.id), 300);
  }

  function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
  }
  function dragged(event) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
  }
  function dragended(event) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
  }
}

function nodeRadius(d) {
  const degree = nodeDegree[d.id] || 0;
  return Math.max(5, Math.min(18, 4 + degree * 1.2));
}

function highlightNeighborhood(nodeId, nodeSel, linkSel) {
  const connIds = new Set([nodeId]);
  DATA.edges.forEach(e => {
    const src = typeof e.source === 'object' ? e.source.id : e.source;
    const tgt = typeof e.target === 'object' ? e.target.id : e.target;
    if (src === nodeId) connIds.add(tgt);
    if (tgt === nodeId) connIds.add(src);
  });

  nodeSel.classed('highlight', n => n.id === nodeId);
  nodeSel.classed('dimmed', n => !connIds.has(n.id));
  linkSel.classed('highlight', e => {
    const src = typeof e.source === 'object' ? e.source.id : e.source;
    const tgt = typeof e.target === 'object' ? e.target.id : e.target;
    return src === nodeId || tgt === nodeId;
  });
  linkSel.classed('dimmed', e => {
    const src = typeof e.source === 'object' ? e.source.id : e.source;
    const tgt = typeof e.target === 'object' ? e.target.id : e.target;
    return src !== nodeId && tgt !== nodeId;
  });
}

function clearHighlight(nodeSel, linkSel) {
  nodeSel.classed('highlight', false).classed('dimmed', false);
  linkSel.classed('highlight', false).classed('dimmed', false);
}

function focusGraphNode(nodeId) {
  if (!graphNodeSel || !graphLinkSel || !graphSvg) return;

  // Find node in simulation data (has x/y), not DATA.nodes (no x/y due to shallow copies)
  let d = null;
  graphNodeSel.each(function(n) { if (n.id === nodeId) d = n; });
  if (!d || d.x === undefined) return;

  // Lock highlight so it persists after sidebar click
  lockedNodeId = nodeId;
  highlightNeighborhood(nodeId, graphNodeSel, graphLinkSel);
  graphSvg.classed('graph-locked', true);

  // Zoom to node
  const container = document.getElementById('graph-view');
  const width = container.clientWidth;
  const height = container.clientHeight;
  const scale = 1.5;
  const transform = d3.zoomIdentity
    .translate(width / 2 - d.x * scale, height / 2 - d.y * scale)
    .scale(scale);
  graphSvg.transition().duration(750).call(graphZoom.transform, transform);
}

function buildGraphLegend() {
  const legend = document.getElementById('graph-legend');
  let html = '<div class="legend-section"><div class="legend-title">Nodes</div>';
  TYPE_ORDER.forEach(t => {
    const active = activeFilters.has(t);
    html += '<div class="legend-item legend-clickable' + (active ? '' : ' legend-off') + '" data-node-type="' + t + '">' +
      '<span class="legend-dot" style="background:' + TYPE_COLORS[t] + '"></span>' + TYPE_LABELS[t] + '</div>';
  });
  html += '</div><div class="legend-section"><div class="legend-title">Edges</div>';

  // Only show edge types present in data
  const edgeTypesPresent = new Set(DATA.edges.map(e => e.type));
  Object.entries(EDGE_COLORS).forEach(([type, color]) => {
    if (edgeTypesPresent.has(type)) {
      html += '<div class="legend-item legend-clickable" data-edge-type="' + type + '">' +
        '<span class="legend-line" style="background:' + color + '"></span>' + (EDGE_LABELS[type] || type) + '</div>';
    }
  });
  html += '</div>';
  legend.innerHTML = html;
  legend.style.display = 'block';

  // Node type click: toggle filter and rebuild graph
  legend.querySelectorAll('[data-node-type]').forEach(el => {
    el.addEventListener('click', (e) => {
      const type = el.dataset.nodeType;
      if (e.shiftKey) {
        if (activeFilters.has(type)) activeFilters.delete(type);
        else activeFilters.add(type);
      } else {
        if (activeFilters.size === 1 && activeFilters.has(type)) {
          TYPE_ORDER.forEach(t => activeFilters.add(t));
        } else {
          activeFilters.clear();
          activeFilters.add(type);
        }
      }
      document.querySelectorAll('.filter-btn').forEach(b => {
        b.classList.toggle('active', activeFilters.has(b.dataset.type));
      });
      buildSidebar();
      buildGraph();
    });
  });

  // Edge type click: highlight those edges
  legend.querySelectorAll('[data-edge-type]').forEach(el => {
    el.addEventListener('click', () => {
      const type = el.dataset.edgeType;
      if (!graphLinkSel || !graphNodeSel) return;
      // Toggle: if already highlighting this type, clear
      if (legend._activeEdgeType === type) {
        clearHighlight(graphNodeSel, graphLinkSel);
        legend._activeEdgeType = null;
        legend.querySelectorAll('[data-edge-type]').forEach(e => e.classList.remove('legend-active'));
        return;
      }
      legend._activeEdgeType = type;
      legend.querySelectorAll('[data-edge-type]').forEach(e => e.classList.toggle('legend-active', e.dataset.edgeType === type));
      // Highlight matching edges and their connected nodes
      const connIds = new Set();
      graphLinkSel.classed('highlight', e => {
        if (e.type === type) {
          connIds.add(typeof e.source === 'object' ? e.source.id : e.source);
          connIds.add(typeof e.target === 'object' ? e.target.id : e.target);
          return true;
        }
        return false;
      });
      graphLinkSel.classed('dimmed', e => e.type !== type);
      graphNodeSel.classed('dimmed', n => !connIds.has(n.id));
      graphNodeSel.classed('highlight', false);
    });
  });
}

// ---------------------------------------------------------------------------
// Layers view
// ---------------------------------------------------------------------------
function buildLayers() {
  const container = document.getElementById('layers-view');
  const layerDescs = DATA.meta.layer_descriptions || [];

  // 1. Compute co-occurrence matrix (how many items span each pair of layers)
  const cooccur = Array.from({length: 6}, () => Array(6).fill(0));
  DATA.nodes.forEach(n => {
    if (!n.meta || !n.meta.layer_list) return;
    const indices = n.meta.layer_list
      .map(l => LAYER_NAMES.indexOf(l))
      .filter(i => i >= 0);
    // Deduplicate
    const unique = [...new Set(indices)];
    unique.forEach(i => { cooccur[i][i]++; }); // diagonal = total in layer
    for (let a = 0; a < unique.length; a++) {
      for (let b = a + 1; b < unique.length; b++) {
        cooccur[unique[a]][unique[b]]++;
        cooccur[unique[b]][unique[a]]++;
      }
    }
  });

  // 2. Collect items in the active layer, grouped by type
  const activeName = LAYER_NAMES[activeLayerIdx];
  const inLayer = DATA.nodes.filter(n =>
    n.meta && n.meta.layer_list && n.meta.layer_list.includes(activeName)
  );
  const patterns = inLayer.filter(n => n.type === 'pattern');
  const principles = inLayer.filter(n => n.type === 'principle');
  const analyses = inLayer.filter(n => n.type === 'analysis');
  const evidence = inLayer.filter(n => n.type === 'evidence');
  const instruments = inLayer.filter(n => n.type === 'instrument');

  // 3. Build HTML
  let html = '';

  // Tab pills
  html += '<div class="layer-tabs">';
  LAYER_NAMES.forEach((name, i) => {
    html += '<button class="layer-tab' + (i === activeLayerIdx ? ' active' : '') +
      '" data-idx="' + i + '">' + escapeHtml(name) + '</button>';
  });
  html += '</div>';

  // Layer description
  const desc = layerDescs[activeLayerIdx] ? layerDescs[activeLayerIdx].description : '';
  html += '<div class="layer-detail">';
  if (desc) {
    html += '<p class="layer-description">' + escapeHtml(desc) + '</p>';
  }

  // Co-occurrence bars (other 5 layers, sorted by count desc)
  const others = LAYER_NAMES
    .map((name, i) => ({ name, idx: i, count: cooccur[activeLayerIdx][i] }))
    .filter(o => o.idx !== activeLayerIdx)
    .sort((a, b) => b.count - a.count);
  const maxCooccur = others.length > 0 ? Math.max(others[0].count, 1) : 1;

  html += '<div class="layer-cooccur-section"><h3>Co-occurs with</h3>';
  others.forEach(o => {
    const pct = Math.round((o.count / maxCooccur) * 100);
    html += '<div class="cooccur-row">' +
      '<span class="cooccur-label">' + escapeHtml(o.name) + '</span>' +
      '<div class="cooccur-bar"><div class="cooccur-fill" style="width:' + pct + '%"></div></div>' +
      '<span class="cooccur-count">' + o.count + '</span>' +
    '</div>';
  });
  html += '</div>';

  // Helper for corroboration color
  function corrColor(level) {
    if (level === 'ESTABLISHED') return 'var(--green)';
    if (level === 'SUPPORTED') return 'var(--orange)';
    return 'var(--text-muted)';
  }

  // Patterns section
  if (patterns.length > 0) {
    const corrRank = { ESTABLISHED: 0, SUPPORTED: 1, PRELIMINARY: 2 };
    patterns.sort((a, b) => {
      const ra = corrRank[a.meta.corr_level] ?? 9;
      const rb = corrRank[b.meta.corr_level] ?? 9;
      if (ra !== rb) return ra - rb;
      return (b.meta.corr_hit_rate || 0) - (a.meta.corr_hit_rate || 0);
    });
    html += '<div class="layer-items-section"><h3>Patterns (' + patterns.length + ')</h3>';
    patterns.forEach(p => {
      const level = p.meta.corr_level || 'PRELIMINARY';
      const hitRate = p.meta.corr_hit_rate || 0;
      const pct = Math.round(hitRate * 100);
      const color = corrColor(level);
      html += '<div class="layer-item-row" data-id="' + p.id + '">' +
        '<span class="layer-item-title">' + escapeHtml(p.title) + '</span>' +
        '<span class="layer-item-corr">' +
          '<span class="layer-item-corr-bar"><span class="layer-item-corr-fill" style="width:' + pct + '%;background:' + color + '"></span></span>' +
          '<span class="layer-item-corr-level" style="color:' + color + '">' + level + '</span>' +
        '</span>' +
      '</div>';
    });
    html += '</div>';
  }

  // Principles (works studied) section
  if (principles.length > 0) {
    principles.sort((a, b) => {
      const ca = a.meta.principle_count || 0;
      const cb = b.meta.principle_count || 0;
      return cb - ca;
    });
    html += '<div class="layer-items-section"><h3>Works Studied (' + principles.length + ')</h3>';
    principles.forEach(p => {
      const count = p.meta.principle_count || '';
      const source = p.meta.source || '';
      html += '<div class="layer-item-row" data-id="' + p.id + '">' +
        '<span class="layer-item-title">' + escapeHtml(p.title) + '</span>' +
        (source ? '<span class="layer-item-meta">' + escapeHtml(source) + '</span>' : '') +
        (count ? '<span class="layer-item-meta">' + count + ' principles</span>' : '') +
      '</div>';
    });
    html += '</div>';
  }

  // Analyses section
  if (analyses.length > 0) {
    analyses.sort((a, b) => (b.meta.date || '').localeCompare(a.meta.date || ''));
    html += '<div class="layer-items-section"><h3>Analyses (' + analyses.length + ')</h3>';
    analyses.forEach(a => {
      const date = a.meta.date || '';
      html += '<div class="layer-item-row" data-id="' + a.id + '">' +
        '<span class="layer-item-title">' + escapeHtml(a.title.replace(/^Analysis:\s*/i, '')) + '</span>' +
        (date ? '<span class="layer-item-meta">' + date + '</span>' : '') +
      '</div>';
    });
    html += '</div>';
  }

  // Evidence section
  if (evidence.length > 0) {
    html += '<div class="layer-items-section"><h3>Evidence (' + evidence.length + ')</h3>';
    evidence.forEach(e => {
      html += '<div class="layer-item-row" data-id="' + e.id + '">' +
        '<span class="layer-item-title">' + escapeHtml(e.title) + '</span>' +
      '</div>';
    });
    html += '</div>';
  }

  // Instruments section
  if (instruments.length > 0) {
    html += '<div class="layer-items-section"><h3>Instruments (' + instruments.length + ')</h3>';
    instruments.forEach(inst => {
      html += '<div class="layer-item-row" data-id="' + inst.id + '">' +
        '<span class="layer-item-title">' + escapeHtml(inst.title) + '</span>' +
      '</div>';
    });
    html += '</div>';
  }

  html += '</div>'; // close layer-detail

  container.innerHTML = html;

  // Attach tab click handlers
  container.querySelectorAll('.layer-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      activeLayerIdx = parseInt(btn.dataset.idx);
      buildLayers();
    });
  });

  // Attach item click handlers
  container.querySelectorAll('.layer-item-row').forEach(el => {
    el.addEventListener('click', () => selectNode(el.dataset.id, { forceDetail: true }));
  });
}

// ---------------------------------------------------------------------------
// Matrix view (Corroboration Matrix)
// ---------------------------------------------------------------------------
function buildMatrix() {
  const container = document.getElementById('matrix-view');

  // Rows = patterns, sorted by corroboration then source count
  const patterns = DATA.nodes.filter(n => n.type === 'pattern');

  // Columns = source works (principles + analyses)
  const sources = DATA.nodes.filter(n => n.type === 'principle' || n.type === 'analysis');

  // Build mapping: which sources corroborate which patterns
  // Use all relevant edge types
  const matrix = {}; // pattern_id -> Set of source_ids
  DATA.edges.forEach(e => {
    if (e.type === 'observed_in') {
      // observed_in goes pattern -> source
      if (!matrix[e.source]) matrix[e.source] = new Set();
      matrix[e.source].add(e.target);
    }
    if (e.type === 'key_pattern') {
      // key_pattern goes source -> pattern
      if (!matrix[e.target]) matrix[e.target] = new Set();
      matrix[e.target].add(e.source);
    }
    if (e.type === 'matches') {
      // matches goes analysis -> pattern
      if (!matrix[e.target]) matrix[e.target] = new Set();
      matrix[e.target].add(e.source);
    }
    if (e.type === 'evidence_for') {
      // evidence_for goes evidence -> pattern (skip, not a source work)
    }
  });

  // Filter sources to only those that appear in at least one pattern
  const activeSources = sources.filter(s => {
    for (const pid in matrix) {
      if (matrix[pid] && matrix[pid].has(s.id)) return true;
    }
    return false;
  });

  // Sort patterns: ESTABLISHED first, then SUPPORTED, then PRELIMINARY, then by source count
  const corrRank = { ESTABLISHED: 0, SUPPORTED: 1, PRELIMINARY: 2 };
  patterns.sort((a, b) => {
    const ca = (a.meta.corroboration || '').split(' ')[0];
    const cb = (b.meta.corroboration || '').split(' ')[0];
    const ra = corrRank[ca] !== undefined ? corrRank[ca] : 3;
    const rb = corrRank[cb] !== undefined ? corrRank[cb] : 3;
    if (ra !== rb) return ra - rb;
    const countA = matrix[a.id] ? matrix[a.id].size : 0;
    const countB = matrix[b.id] ? matrix[b.id].size : 0;
    return countB - countA;
  });

  // Sort sources by number of patterns they contribute to (descending)
  activeSources.sort((a, b) => {
    let countA = 0, countB = 0;
    for (const pid in matrix) {
      if (matrix[pid].has(a.id)) countA++;
      if (matrix[pid].has(b.id)) countB++;
    }
    return countB - countA;
  });

  if (patterns.length === 0 || activeSources.length === 0) {
    container.innerHTML = '<h2 style="padding:24px;color:var(--text-muted)">No corroboration data available.</h2>';
    return;
  }

  // Build HTML table
  let html = '<h2 style="margin:0 0 4px 0;font-size:18px;font-weight:600">Corroboration Matrix</h2>' +
    '<p style="margin:0 0 16px 0;font-size:13px;color:var(--text-muted)">' + patterns.length + ' patterns \u00D7 ' + activeSources.length + ' sources. Click row/column headers for details.</p>' +
    '<div class="matrix-container"><table class="matrix-table">';

  // Header row
  html += '<thead><tr><th class="matrix-corner"></th>';
  activeSources.forEach(s => {
    const title = getDisplayTitle(s);
    html += '<th><div class="matrix-col-header" data-id="' + s.id + '" title="' + escapeHtml(title) + '">' + escapeHtml(title) + '</div></th>';
  });
  html += '<th class="matrix-corner" style="border-left:1px solid var(--border)">#</th>';
  html += '</tr></thead>';

  // Body rows
  html += '<tbody>';
  patterns.forEach(p => {
    const corr = (p.meta.corroboration || '').split(' ')[0];
    const pSources = matrix[p.id] || new Set();
    const count = pSources.size;

    html += '<tr class="matrix-row" data-id="' + p.id + '">';
    html += '<td class="matrix-row-header" data-id="' + p.id + '" title="' + escapeHtml(p.title) + '">' +
      escapeHtml(p.title) +
      '<span class="matrix-corr matrix-corr-' + corr + '">' + corr + '</span>' +
    '</td>';

    activeSources.forEach(s => {
      const has = pSources.has(s.id);
      const color = has ? (TYPE_COLORS[s.type] || '#3fb950') : 'transparent';
      html += '<td class="matrix-cell' + (has ? ' filled' : '') + '">' +
        (has ? '<span class="matrix-dot" style="background:' + color + '"></span>' : '') +
      '</td>';
    });

    html += '<td class="matrix-count">' + count + '</td>';
    html += '</tr>';
  });
  html += '</tbody></table></div>';

  container.innerHTML = html;

  // Click handlers
  container.querySelectorAll('.matrix-row-header').forEach(el => {
    el.addEventListener('click', () => {
      const id = el.dataset.id;
      if (id && nodeMap[id]) selectNode(id, { forceDetail: true });
    });
  });
  container.querySelectorAll('.matrix-col-header').forEach(el => {
    el.addEventListener('click', () => {
      const id = el.dataset.id;
      if (id && nodeMap[id]) selectNode(id, { forceDetail: true });
    });
  });

  // Row hover: highlight the row
  container.querySelectorAll('.matrix-row').forEach(row => {
    row.addEventListener('mouseover', () => {
      container.querySelectorAll('.matrix-row').forEach(r => {
        r.classList.toggle('dimmed', r !== row);
      });
      row.classList.add('highlight');
    });
    row.addEventListener('mouseout', () => {
      container.querySelectorAll('.matrix-row').forEach(r => {
        r.classList.remove('dimmed');
        r.classList.remove('highlight');
      });
    });
  });
}

// ---------------------------------------------------------------------------
// Timeline view
// ---------------------------------------------------------------------------
function buildTimeline() {
  const view = document.getElementById('timeline-view');
  const analyses = DATA.nodes
    .filter(n => n.type === 'analysis')
    .sort((a, b) => (a.meta.date || '').localeCompare(b.meta.date || ''));

  if (analyses.length === 0) {
    view.innerHTML = '<h2>Framework Evolution</h2><p style="color:var(--text-muted)">No analyses yet.</p>';
    return;
  }

  // Collect matched patterns per analysis
  const analysisPatterns = {};
  DATA.edges.forEach(e => {
    if (e.type === 'matches') {
      if (!analysisPatterns[e.source]) analysisPatterns[e.source] = new Set();
      analysisPatterns[e.source].add(e.target);
    }
  });

  // Track first-seen patterns (chronological order)
  const seenPatterns = new Set();
  const timelineData = analyses.map(a => {
    const pats = analysisPatterns[a.id] || new Set();
    const newPats = [];
    pats.forEach(pid => {
      if (!seenPatterns.has(pid)) {
        seenPatterns.add(pid);
        newPats.push(pid);
      }
    });
    return { analysis: a, patterns: pats, newPatterns: newPats };
  });

  // Reverse for display (newest first)
  timelineData.reverse();

  const allPatterns = DATA.nodes.filter(n => n.type === 'pattern');
  const dateRange = analyses[analyses.length - 1].meta.date + ' — ' + analyses[0].meta.date;

  let html = '<h2>Framework Evolution</h2>';
  html += '<div class="timeline-stats">';
  html += '<span><strong>' + analyses.length + '</strong> analyses</span>';
  html += '<span><strong>' + allPatterns.length + '</strong> patterns</span>';
  html += '<span>' + dateRange + '</span>';
  html += '</div>';

  html += '<div class="timeline-track">';
  timelineData.forEach(item => {
    const a = item.analysis;
    const title = getDisplayTitle(a);
    const dotColor = TYPE_COLORS[a.meta.source_type] || TYPE_COLORS.analysis;
    const layers = a.meta.layer_list || [];
    const patCount = item.patterns.size;
    const newPats = item.newPatterns;

    html += '<div class="timeline-event">';
    html += '<div class="timeline-date">' + escapeHtml(a.meta.date || '') + '</div>';
    html += '<div class="timeline-dot" style="background:' + dotColor + '"></div>';
    html += '<div class="timeline-body" data-id="' + a.id + '">';
    html += '<div class="timeline-body-title">' + escapeHtml(title) + '</div>';
    if (patCount > 0) {
      html += '<span class="timeline-pattern-count">' + patCount + ' patterns matched</span>';
    }
    if (newPats.length > 0) {
      newPats.forEach(pid => {
        const pn = nodeMap[pid];
        if (pn) html += ' <span class="timeline-new-badge">NEW: ' + escapeHtml(pn.title) + '</span>';
      });
    }
    html += '<div class="timeline-body-meta">';
    layers.forEach(l => {
      html += '<span class="timeline-layer-pill">' + escapeHtml(l) + '</span>';
    });
    html += '</div></div></div>';
  });
  html += '</div>';

  view.innerHTML = html;
  view.querySelectorAll('.timeline-body').forEach(el => {
    el.addEventListener('click', () => selectNode(el.dataset.id, { forceDetail: true }));
  });
}

// ---------------------------------------------------------------------------
// Layer Flow view
// ---------------------------------------------------------------------------
function buildFlow() {
  const view = document.getElementById('flow-view');

  // Compute 6x6 co-occurrence matrix
  const cooccur = Array.from({length: 6}, () => Array(6).fill(0));
  const crossItems = Array.from({length: 6}, () => Array.from({length: 6}, () => []));

  DATA.nodes.forEach(n => {
    if (!n.meta || !n.meta.layer_list) return;
    const indices = [...new Set(n.meta.layer_list.map(l => LAYER_NAMES.indexOf(l)).filter(i => i >= 0))];
    indices.forEach(i => { cooccur[i][i]++; });
    for (let a = 0; a < indices.length; a++) {
      for (let b = a + 1; b < indices.length; b++) {
        cooccur[indices[a]][indices[b]]++;
        cooccur[indices[b]][indices[a]]++;
        crossItems[indices[a]][indices[b]].push(n);
        crossItems[indices[b]][indices[a]].push(n);
      }
    }
  });

  const shortNames = LAYER_NAMES.map(n => n.split(' ')[0]);
  const maxOff = Math.max(1, ...cooccur.flat().filter((v, i) => Math.floor(i / 6) !== i % 6));
  const maxDiag = Math.max(1, ...LAYER_NAMES.map((_, i) => cooccur[i][i]));

  let html = '<h2>Cross-Layer Power Flows</h2>';
  html += '<p style="color:var(--text-muted);margin-bottom:20px">Items that span multiple layers reveal how power transfers across domains.</p>';

  // Grid table
  html += '<div class="flow-grid"><table><tr><td class="flow-header-cell"></td>';
  shortNames.forEach(n => { html += '<td class="flow-header-cell" style="text-align:center">' + n + '</td>'; });
  html += '</tr>';

  for (let r = 0; r < 6; r++) {
    html += '<tr><td class="flow-header-cell row-header">' + shortNames[r] + '</td>';
    for (let c = 0; c < 6; c++) {
      const val = cooccur[r][c];
      if (r === c) {
        const op = Math.max(0.1, val / maxDiag);
        html += '<td class="flow-cell diagonal" style="background:rgba(56,139,253,' + op.toFixed(2) + ')" data-r="' + r + '" data-c="' + c + '" title="' + LAYER_NAMES[r] + ': ' + val + ' items">' + val + '</td>';
      } else {
        const op = val > 0 ? Math.max(0.15, val / maxOff) : 0;
        html += '<td class="flow-cell" style="background:rgba(163,113,247,' + op.toFixed(2) + ')" data-r="' + r + '" data-c="' + c + '" title="' + LAYER_NAMES[r] + ' + ' + LAYER_NAMES[c] + ': ' + val + '">' + (val || '') + '</td>';
      }
    }
    html += '</tr>';
  }
  html += '</table></div>';

  // Top corridors
  const corridors = [];
  for (let a = 0; a < 6; a++) {
    for (let b = a + 1; b < 6; b++) {
      if (cooccur[a][b] > 0) corridors.push({ a, b, count: cooccur[a][b] });
    }
  }
  corridors.sort((x, y) => y.count - x.count);
  const maxCorr = corridors.length > 0 ? corridors[0].count : 1;

  if (corridors.length > 0) {
    html += '<div class="layer-items-section"><h3>Strongest Corridors</h3>';
    corridors.forEach(c => {
      const pct = Math.round((c.count / maxCorr) * 100);
      html += '<div class="flow-corridor-row">' +
        '<span class="flow-corridor-label">' + escapeHtml(LAYER_NAMES[c.a]) + ' &#8596; ' + escapeHtml(LAYER_NAMES[c.b]) + '</span>' +
        '<div class="flow-corridor-bar"><div class="flow-corridor-fill" style="width:' + pct + '%"></div></div>' +
        '<span class="flow-corridor-count">' + c.count + '</span>' +
      '</div>';
    });
    html += '</div>';
  }

  html += '<div id="flow-detail-panel"></div>';

  view.innerHTML = html;

  // Cell click: show items
  view.querySelectorAll('.flow-cell').forEach(cell => {
    cell.addEventListener('click', () => {
      const r = parseInt(cell.dataset.r), c = parseInt(cell.dataset.c);
      view.querySelectorAll('.flow-cell').forEach(fc => fc.classList.remove('active-cell'));
      cell.classList.add('active-cell');
      const panel = document.getElementById('flow-detail-panel');
      let items;
      if (r === c) {
        items = DATA.nodes.filter(n => n.meta && n.meta.layer_list && n.meta.layer_list.includes(LAYER_NAMES[r]));
      } else {
        items = crossItems[r][c];
      }
      if (items.length === 0) { panel.innerHTML = ''; return; }
      setTimeout(() => panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 50);
      let dhtml = '<div class="flow-detail"><h3 style="font-size:13px;font-weight:600;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.3px;margin:0 0 10px 0">' +
        (r === c ? LAYER_NAMES[r] + ' items' : LAYER_NAMES[r] + ' + ' + LAYER_NAMES[c]) +
        ' (' + items.length + ')</h3>';
      items.forEach(n => {
        const color = TYPE_COLORS[n.type];
        dhtml += '<div class="layer-item-row" data-id="' + n.id + '">' +
          '<span class="type-dot" style="background:' + color + '"></span>' +
          '<span class="layer-item-title">' + escapeHtml(getDisplayTitle(n)) + '</span>' +
          '<span class="layer-item-meta">' + n.type + '</span></div>';
      });
      dhtml += '</div>';
      panel.innerHTML = dhtml;
      panel.querySelectorAll('.layer-item-row').forEach(el => {
        el.addEventListener('click', () => selectNode(el.dataset.id, { forceDetail: true }));
      });
    });
  });
}

// ---------------------------------------------------------------------------
// Gap Analysis view
// ---------------------------------------------------------------------------
function buildGaps() {
  const view = document.getElementById('gaps-view');
  let html = '<h2>Gap Analysis</h2>';
  html += '<p style="color:var(--text-muted);margin-bottom:24px">Blind spots, weak corroboration, and understudied areas.</p>';

  // 0. Framework Health
  const health = DATA.meta.health || {};
  html += '<div class="gaps-section"><h3 title="Structural health metrics for the integrity constraints. Green means the constraint is functioning; red means it may be failing or untested.">Framework Health</h3>';
  html += '<div class="health-cards">';

  // Evidence balance card
  const eb = health.evidence_balance || {};
  const totalEv = Object.values(eb).reduce((a,b) => a+b, 0) || 1;
  html += '<div class="health-card">';
  html += '<h4 title="Ratio of evidence entries that support vs. challenge vs. complicate axioms. A healthy framework has challenging evidence — if every entry supports the axioms, IC-1 (falsifiability) may not be functioning.">Evidence Balance</h4>';
  html += '<div class="health-stacked-bar">';
  const evColors = { supports: 'var(--green)', challenges: 'var(--red)', complicates: 'var(--orange)', 'self-examination': 'var(--purple)' };
  ['supports','challenges','complicates','self-examination'].forEach(r => {
    const c = eb[r] || 0;
    if (c > 0) html += '<div style="width:' + Math.round(c/totalEv*100) + '%;background:' + evColors[r] + '" title="' + r + ': ' + c + '"></div>';
  });
  html += '</div>';
  html += '<div class="health-legend">';
  ['supports','challenges','complicates','self-examination'].forEach(r => {
    html += '<span><span style="background:' + evColors[r] + ';width:8px;height:8px;border-radius:2px;display:inline-block;margin-right:4px;vertical-align:middle"></span>' + r + ': ' + (eb[r]||0) + '</span>';
  });
  html += '</div>';
  // Warning for unchallenged axioms
  const ab = health.axiom_balance || {};
  const unchallenged = (DATA.meta.axioms || []).filter((_, i) => {
    const ax = String(i + 1);
    return !ab[ax] || !ab[ax].challenges;
  });
  if (unchallenged.length > 0 && (DATA.meta.axioms||[]).length > 0) {
    html += '<div class="health-warning">' + unchallenged.length + ' of ' + (DATA.meta.axioms||[]).length + ' axioms have no challenging evidence</div>';
  }
  html += '</div>';

  // Null case card
  const nc = health.null_cases || {};
  const totalNC = (nc.rejected||0) + (nc.plausible||0) + (nc.accepted||0) || 1;
  html += '<div class="health-card">';
  html += '<h4 title="How often analyses conclude that power dynamics are NOT the best explanation. Rejected means the power reading is stronger; accepted means the non-power explanation wins. IC-2 requires every analysis to consider the null case — if none are ever accepted, the framework may be confirming itself.">Null Case Distribution</h4>';
  html += '<div class="health-stacked-bar">';
  const ncColors = { rejected: '#e74c3c', plausible: 'var(--orange)', accepted: 'var(--green)' };
  ['rejected','plausible','accepted'].forEach(r => {
    const c = nc[r] || 0;
    if (c > 0) html += '<div style="width:' + Math.round(c/totalNC*100) + '%;background:' + ncColors[r] + '" title="' + r + ': ' + c + '"></div>';
  });
  html += '</div>';
  html += '<div class="health-legend">';
  ['rejected','plausible','accepted'].forEach(r => {
    html += '<span><span style="background:' + ncColors[r] + ';width:8px;height:8px;border-radius:2px;display:inline-block;margin-right:4px;vertical-align:middle"></span>' + r + ': ' + (nc[r]||0) + '</span>';
  });
  html += '</div>';
  if ((nc.accepted||0) === 0) {
    html += '<div class="health-warning">No accepted null cases — IC-2 may be decorative</div>';
  }
  html += '</div>';

  // Red team status card
  html += '<div class="health-card">';
  html += '<h4 title="IC-3 requires the framework to periodically examine itself for confirmation bias and unfalsifiability. A red team turns its own analytical tools on itself. Overdue if more than 10 analyses have passed since the last one.">Red Team Status (IC-3)</h4>';
  const lrt = health.last_red_team;
  const lrtId = health.last_red_team_id;
  const asrt = health.analyses_since_red_team || 0;
  const rtClass = !lrt ? 'health-status-critical' : asrt > 15 ? 'health-status-critical' : asrt > 10 ? 'health-status-warn' : 'health-status-ok';
  if (lrtId) {
    html += '<div class="health-metric ' + rtClass + '"><a href="#" class="health-link" data-id="' + lrtId + '">' + lrt + '</a></div>';
  } else {
    html += '<div class="health-metric ' + rtClass + '">' + (lrt || 'Never') + '</div>';
  }
  html += '<div class="health-detail">' + asrt + ' analyses since last red team' + (asrt > 10 ? ' (threshold: 10)' : '') + '</div>';
  html += '</div>';

  // Adversarial ratio card
  html += '<div class="health-card">';
  html += '<h4 title="Analyses deliberately chosen because the non-power explanation is likely to win. Tests whether IC-2 (null case) actually functions or is decorative. Target: at least 1 in 10 analyses should be adversarial.">Adversarial Input</h4>';
  const advCount = health.adversarial_count || 0;
  const advTotal = health.total_analyses || 0;
  const advRatio = advTotal > 0 ? advCount / advTotal : 0;
  const advClass = advRatio >= 0.1 ? 'health-status-ok' : advCount > 0 ? 'health-status-warn' : 'health-status-critical';
  html += '<div class="health-metric ' + advClass + '">' + advCount + ' / ' + advTotal + '</div>';
  html += '<div class="health-detail">Target: 1 in 10 analyses (' + Math.round(advRatio * 100) + '% actual)</div>';
  html += '</div>';

  // Calibration card
  const cal = health.calibration || {};
  const calTotal = cal.total || 0;
  html += '<div class="health-card">';
  html += '<h4 title="SAMPLE mode randomly selects material (including sports, recipes, science) and runs a READ analysis. The null case rate measures the false positive rate — how often it finds power dynamics in material where they may be absent. Target: 30-60%.">Calibration (SAMPLE)</h4>';
  if (calTotal === 0) {
    html += '<div class="health-metric health-status-critical">No samples</div>';
    html += '<div class="health-detail">Run /lop sample to begin calibration</div>';
  } else {
    const calNull = (cal.accepted || 0) + (cal.plausible || 0);
    const calRate = Math.round(calNull / calTotal * 100);
    const calClass = calTotal < 5 ? 'health-status-warn' : (calRate >= 30 && calRate <= 60) ? 'health-status-ok' : 'health-status-critical';
    html += '<div class="health-metric ' + calClass + '">' + calRate + '%</div>';
    html += '<div class="health-stacked-bar" style="margin-bottom:4px">';
    const calColors = { accepted: 'var(--green)', plausible: 'var(--orange)', rejected: '#e74c3c' };
    ['accepted','plausible','rejected'].forEach(r => {
      const c = cal[r] || 0;
      if (c > 0) html += '<div style="width:' + Math.round(c/calTotal*100) + '%;background:' + calColors[r] + '" title="' + r + ': ' + c + '"></div>';
    });
    html += '</div>';
    html += '<div class="health-legend">';
    ['accepted','plausible','rejected'].forEach(r => {
      html += '<span><span style="background:' + calColors[r] + ';width:8px;height:8px;border-radius:2px;display:inline-block;margin-right:4px;vertical-align:middle"></span>' + r + ': ' + (cal[r]||0) + '</span>';
    });
    html += '</div>';
    html += '<div class="health-detail">' + calTotal + ' samples — target null rate: 30\u201360%' + (calTotal < 5 ? ' (need 5+ for significance)' : '') + '</div>';
    if ((cal.unacted_escalations || 0) > 0) {
      html += '<div class="health-warning">' + cal.unacted_escalations + ' unacted escalation' + (cal.unacted_escalations > 1 ? 's' : '') + ' in sample log</div>';
    }
  }
  html += '</div>';

  // Hegemonic Context Distribution card (IC-7)
  const hcGapNodes = DATA.nodes.filter(n => n.type === 'hegemonic_context');
  if (hcGapNodes.length > 0) {
    const hcGapCounts = {};
    hcGapNodes.forEach(hc => { hcGapCounts[hc.id] = 0; });
    const gapTotalAnalyses = DATA.nodes.filter(n => n.type === 'analysis').length;
    DATA.edges.forEach(e => {
      if (e.type === 'operates_within' && hcGapCounts.hasOwnProperty(e.target)) {
        hcGapCounts[e.target]++;
      }
    });
    const hcGapSorted = hcGapNodes.slice().sort((a, b) => (hcGapCounts[b.id] || 0) - (hcGapCounts[a.id] || 0));
    const maxHCGap = Math.max(1, ...Object.values(hcGapCounts));
    const taggedCount = DATA.nodes.filter(n => n.type === 'analysis' && (adjacency[n.id] || {outgoing:[]}).outgoing.some(e => e.type === 'operates_within')).length;

    html += '<div class="health-card" style="grid-column: 1 / -1">';
    html += '<h4 title="IC-7 requires naming the background assumptions (hegemonic contexts) within which analyses operate. Untagged analyses have not yet identified their hegemonic context. Contexts with zero analyses may represent blind spots.">Hegemonic Context (IC-7)</h4>';
    html += '<div class="health-detail" style="margin-bottom:8px">' + taggedCount + ' of ' + gapTotalAnalyses + ' analyses tagged</div>';
    hcGapSorted.forEach(hc => {
      const count = hcGapCounts[hc.id] || 0;
      const pct = maxHCGap > 0 ? Math.round((count / maxHCGap) * 100) : 0;
      const fillColor = count === 0 ? 'var(--text-muted)' : '#da7756';
      html += '<div class="gaps-row" data-id="' + hc.id + '" style="margin-bottom:2px">' +
        '<span class="gaps-label">' + escapeHtml(hc.title) + '</span>' +
        '<div class="gaps-bar"><div class="gaps-fill" style="width:' + pct + '%;background:' + fillColor + '"></div></div>' +
        '<span class="gaps-meta">' + count + '</span>' +
      '</div>';
    });
    if (taggedCount === 0) {
      html += '<div class="health-warning">No analyses tagged with hegemonic contexts yet</div>';
    }
    html += '</div>';
  }

  html += '</div>'; // close health-cards
  html += '</div>'; // close gaps-section

  // 1. Under-corroborated patterns (sorted weakest first)
  const patterns = DATA.nodes.filter(n => n.type === 'pattern').slice();
  patterns.sort((a, b) => (a.meta.corr_hit_rate || 0) - (b.meta.corr_hit_rate || 0));

  html += '<div class="gaps-section"><h3 title="Patterns sorted by corroboration strength. PRELIMINARY patterns have been observed in fewer than 3 independent sources. SUPPORTED and ESTABLISHED patterns have stronger evidence bases. Weak patterns need either more corroborating analyses or deliberate challenge.">Under-corroborated Patterns</h3>';
  patterns.forEach(p => {
    const hitRate = p.meta.corr_hit_rate || 0;
    const level = p.meta.corr_level || 'PRELIMINARY';
    const pct = Math.round(hitRate * 100);
    const count = p.meta.corr_count || 0;
    const rel = p.meta.corr_relevant || 0;
    const fillColor = level === 'PRELIMINARY' ? 'var(--red)' : level === 'SUPPORTED' ? 'var(--orange)' : 'var(--green)';
    const sevClass = level === 'PRELIMINARY' ? 'gaps-severity-critical' : level === 'SUPPORTED' ? 'gaps-severity-moderate' : 'gaps-severity-minor';
    html += '<div class="gaps-row" data-id="' + p.id + '">' +
      '<span class="gaps-label">' + escapeHtml(p.title) + '</span>' +
      '<div class="gaps-bar"><div class="gaps-fill" style="width:' + pct + '%;background:' + fillColor + '"></div></div>' +
      '<span class="gaps-severity ' + sevClass + '">' + level + '</span>' +
      '<span class="gaps-meta">' + count + '/' + rel + ' sources</span>' +
    '</div>';
  });
  html += '</div>';

  // 2. Under-studied layers
  const layerCounts = {};
  LAYER_NAMES.forEach(l => { layerCounts[l] = 0; });
  DATA.nodes.forEach(n => {
    if (n.meta && n.meta.layer_list) {
      n.meta.layer_list.forEach(l => { if (layerCounts.hasOwnProperty(l)) layerCounts[l]++; });
    }
  });
  const maxLayer = Math.max(1, ...Object.values(layerCounts));
  const layersSorted = LAYER_NAMES.slice().sort((a, b) => layerCounts[a] - layerCounts[b]);

  html += '<div class="gaps-section"><h3 title="The six taxonomy layers ranked by how many framework items (analyses, patterns, principles) reference them. Layers with fewer items represent blind spots — the framework may be under-examining those dimensions of power.">Under-studied Layers</h3>';
  layersSorted.forEach(l => {
    const count = layerCounts[l];
    const pct = Math.round((count / maxLayer) * 100);
    const gap = 100 - pct;
    const fillColor = gap > 60 ? 'var(--red)' : gap > 30 ? 'var(--orange)' : 'var(--green)';
    html += '<div class="gaps-row">' +
      '<span class="gaps-label">' + escapeHtml(l) + '</span>' +
      '<div class="gaps-bar"><div class="gaps-fill" style="width:' + pct + '%;background:' + fillColor + '"></div></div>' +
      '<span class="gaps-meta">' + count + ' items</span>' +
    '</div>';
  });
  html += '</div>';

  // 3. Missing layer corridors
  const cooccur = Array.from({length: 6}, () => Array(6).fill(0));
  DATA.nodes.forEach(n => {
    if (!n.meta || !n.meta.layer_list) return;
    const indices = [...new Set(n.meta.layer_list.map(l => LAYER_NAMES.indexOf(l)).filter(i => i >= 0))];
    for (let a = 0; a < indices.length; a++) {
      for (let b = a + 1; b < indices.length; b++) {
        cooccur[indices[a]][indices[b]]++;
        cooccur[indices[b]][indices[a]]++;
      }
    }
  });

  const missing = [];
  for (let a = 0; a < 6; a++) {
    for (let b = a + 1; b < 6; b++) {
      if (cooccur[a][b] === 0) missing.push([a, b]);
    }
  }

  html += '<div class="gaps-section"><h3 title="Layer pairs that have no framework item spanning both. These are unexplored interactions — for example, if no analysis examines how Economic and Surveillance layers reinforce each other, that corridor is missing.">Missing Layer Corridors</h3>';
  if (missing.length === 0) {
    html += '<p style="color:var(--text-muted);font-size:13px">All layer pairs have at least one shared item.</p>';
  } else {
    missing.forEach(pair => {
      html += '<div class="gaps-corridor-missing">' + escapeHtml(LAYER_NAMES[pair[0]]) + ' &#8596; ' + escapeHtml(LAYER_NAMES[pair[1]]) + ' — <em>no items span both</em></div>';
    });
  }
  html += '</div>';

  // 4. Source type diversity
  const sourceTypes = {};
  DATA.nodes.filter(n => n.type === 'analysis').forEach(a => {
    const st = a.meta.source_type || 'unknown';
    sourceTypes[st] = (sourceTypes[st] || 0) + 1;
  });
  const stSorted = Object.entries(sourceTypes).sort((a, b) => a[1] - b[1]);
  const maxST = stSorted.length > 0 ? stSorted[stSorted.length - 1][1] : 1;

  html += '<div class="gaps-section"><h3>Source Type Diversity</h3>';
  if (stSorted.length === 0) {
    html += '<p style="color:var(--text-muted);font-size:13px">No analyses yet.</p>';
  } else {
    stSorted.forEach(([st, count]) => {
      const pct = Math.round((count / maxST) * 100);
      const fillColor = count <= 1 ? 'var(--orange)' : 'var(--purple)';
      html += '<div class="gaps-row">' +
        '<span class="gaps-label">' + escapeHtml(st) + '</span>' +
        '<div class="gaps-bar"><div class="gaps-fill" style="width:' + pct + '%;background:' + fillColor + '"></div></div>' +
        '<span class="gaps-meta">' + count + ' analyses</span>' +
      '</div>';
    });
  }
  html += '</div>';

  // 5. Isolated items (degree <= 1)
  const isolated = DATA.nodes.filter(n => (nodeDegree[n.id] || 0) <= 1);

  html += '<div class="gaps-section"><h3>Isolated Items (degree &#8804; 1)</h3>';
  if (isolated.length === 0) {
    html += '<p style="color:var(--text-muted);font-size:13px">No isolated items.</p>';
  } else {
    isolated.forEach(n => {
      const color = TYPE_COLORS[n.type];
      html += '<div class="gaps-row" data-id="' + n.id + '">' +
        '<span class="type-dot" style="background:' + color + ';display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:8px;vertical-align:middle"></span>' +
        '<span class="gaps-label">' + escapeHtml(getDisplayTitle(n)) + '</span>' +
        '<span class="gaps-meta">' + n.type + '</span>' +
      '</div>';
    });
  }
  html += '</div>';

  view.innerHTML = html;
  view.querySelectorAll('.gaps-row[data-id]').forEach(el => {
    el.addEventListener('click', () => selectNode(el.dataset.id, { forceDetail: true }));
  });
  view.querySelectorAll('.health-link[data-id]').forEach(el => {
    el.addEventListener('click', (e) => { e.preventDefault(); selectNode(el.dataset.id, { forceDetail: true }); });
  });
  // Styled tooltips for titled elements in gap analysis
  var tip = document.getElementById('glossary-tooltip');
  view.querySelectorAll('[title]').forEach(function(el) {
    var titleText = el.getAttribute('title');
    el.removeAttribute('title'); // Remove native tooltip so it doesn't double-show
    el.addEventListener('mouseover', function() {
      tip.querySelector('.gt-title').textContent = el.textContent.trim();
      tip.querySelector('.gt-type').textContent = 'metric';
      tip.querySelector('.gt-def').textContent = titleText;
      tip.style.display = 'block';
      var rect = el.getBoundingClientRect();
      var left = rect.left;
      var top = rect.bottom + 6;
      if (left + 340 > window.innerWidth) left = window.innerWidth - 350;
      if (top + 120 > window.innerHeight) top = rect.top - 6 - tip.offsetHeight;
      tip.style.left = left + 'px';
      tip.style.top = top + 'px';
    });
    el.addEventListener('mouseout', function() {
      tip.style.display = 'none';
    });
  });
}

// ---------------------------------------------------------------------------
// Red Team view
// ---------------------------------------------------------------------------
function buildRedTeam() {
  const view = document.getElementById('redteam-view');
  const health = DATA.meta.health || {};
  const rtIds = health.red_team_ids || [];
  const latestId = health.last_red_team_id;

  let html = '<h2>Red Team (IC-3)</h2>';
  html += '<p style="color:var(--text-muted);margin-bottom:24px">Self-examination reports and framework integrity checks.</p>';

  if (rtIds.length === 0) {
    html += '<p style="color:var(--red)">No red team reports yet. IC-3 requires periodic self-examination.</p>';
    view.innerHTML = html;
    return;
  }

  // Status summary
  const asrt = health.analyses_since_red_team || 0;
  const rtClass = asrt > 15 ? 'health-status-critical' : asrt > 10 ? 'health-status-warn' : 'health-status-ok';
  html += '<div style="margin-bottom:24px;padding:12px 16px;background:var(--bg-card);border-radius:8px;font-size:13px">';
  html += '<strong>' + rtIds.length + '</strong> red team report' + (rtIds.length !== 1 ? 's' : '') + ' &middot; ';
  html += '<span class="' + rtClass + '">' + asrt + ' analyses since last red team</span>';
  html += '</div>';

  // Render most recent report
  const latest = nodeMap[latestId];
  if (latest) {
    html += '<div class="redteam-report">';

    // Render markdown content with cross-reference linking
    let rendered = marked.parse(latest.content);

    // Link file paths to viewer nodes
    rendered = rendered.replace(
      /(?:(?:principles|analyses|instruments|evidence)\/[\w\-]+\.md)/g,
      function(match) {
        if (nodeMap[match]) {
          return '<span class="cross-ref" data-target="' + match + '">' + escapeHtml(nodeMap[match].title || match) + '</span>';
        }
        return match;
      }
    );

    // Link parenthetical references to patterns
    const patternLookup = {};
    DATA.nodes.forEach(n => {
      if (n.type === 'pattern') {
        const key = n.title.replace(/^The\s+/i, '').toLowerCase();
        patternLookup[key] = n.id;
      }
    });
    rendered = rendered.replace(
      /\(([^)<]{2,60})\)/g,
      function(match, term) {
        const key = term.toLowerCase();
        if (patternLookup[key]) {
          return '(<span class="cross-ref" data-target="' + patternLookup[key] + '">' + escapeHtml(term) + '</span>)';
        }
        return match;
      }
    );

    html += rendered;
    html += '</div>';

    // Connected items for the latest report
    const adj = adjacency[latestId] || { incoming: [], outgoing: [] };
    const connected = new Map();
    adj.outgoing.forEach(e => {
      const target = nodeMap[e.target];
      if (target) connected.set(e.target, { node: target, type: e.type });
    });
    adj.incoming.forEach(e => {
      const source = nodeMap[e.source];
      if (source) connected.set(e.source, { node: source, type: e.type });
    });

    if (connected.size > 0) {
      html += '<div class="redteam-related"><h3>Related Items</h3>';
      connected.forEach((info, id) => {
        const color = TYPE_COLORS[info.node.type];
        html += '<div class="redteam-item" data-id="' + id + '">' +
          '<span class="type-dot" style="background:' + color + ';display:inline-block;width:8px;height:8px;border-radius:50%"></span>' +
          escapeHtml(getDisplayTitle(info.node)) +
          '<span class="redteam-item-meta">' + info.node.type + ' &middot; ' + info.type + '</span>' +
        '</div>';
      });
      html += '</div>';
    }
  }

  // If there are older reports, list them
  if (rtIds.length > 1) {
    html += '<div class="redteam-related" style="margin-top:32px"><h3>All Red Team Reports</h3>';
    rtIds.forEach(id => {
      const n = nodeMap[id];
      if (!n) return;
      const isCurrent = id === latestId;
      html += '<div class="redteam-item" data-id="' + id + '">' +
        '<span class="type-dot" style="background:var(--red);display:inline-block;width:8px;height:8px;border-radius:50%"></span>' +
        escapeHtml(getDisplayTitle(n)) +
        (isCurrent ? '<span class="redteam-item-meta" style="color:var(--green)">latest</span>' : '') +
        '<span class="redteam-item-meta">' + (n.meta.date || '') + '</span>' +
      '</div>';
    });
    html += '</div>';
  }

  view.innerHTML = html;

  // Wire up click handlers
  view.querySelectorAll('.redteam-item[data-id]').forEach(el => {
    el.addEventListener('click', () => selectNode(el.dataset.id, { forceDetail: true }));
  });
  view.querySelectorAll('.cross-ref[data-target]').forEach(el => {
    el.addEventListener('click', () => selectNode(el.dataset.target, { forceDetail: true }));
  });
}

// ---------------------------------------------------------------------------
// Principle Lineage view
// ---------------------------------------------------------------------------
function buildLineage() {
  const view = document.getElementById('lineage-view');
  const principles = DATA.nodes.filter(n => n.type === 'principle');
  const patterns = DATA.nodes.filter(n => n.type === 'pattern');

  if (principles.length < 2) {
    view.innerHTML = '<h2>Principle Lineage</h2><p style="color:var(--text-muted)">Need at least 2 principle extractions.</p>';
    return;
  }

  // For each pattern, find which principle sources connect to it
  const patternSources = {};  // patternId -> Set of principle ids
  patterns.forEach(p => { patternSources[p.id] = new Set(); });
  DATA.edges.forEach(e => {
    const src = typeof e.source === 'object' ? e.source.id : e.source;
    const tgt = typeof e.target === 'object' ? e.target.id : e.target;
    if (e.type === 'key_pattern' && patternSources[tgt]) {
      // source (principle) -> target (pattern)
      if (nodeMap[src] && nodeMap[src].type === 'principle') patternSources[tgt].add(src);
    }
    if (e.type === 'observed_in' && patternSources[src]) {
      // source (pattern) -> target (principle)
      if (nodeMap[tgt] && nodeMap[tgt].type === 'principle') patternSources[src].add(tgt);
    }
  });

  // Build convergence list: patterns with 2+ sources
  const convergences = patterns
    .filter(p => patternSources[p.id] && patternSources[p.id].size >= 2)
    .map(p => ({
      pattern: p,
      sources: [...patternSources[p.id]].map(id => nodeMap[id]).filter(Boolean),
    }))
    .sort((a, b) => b.sources.length - a.sources.length);

  // Track which sources appear in any convergence
  const convergedSources = new Set();
  convergences.forEach(c => c.sources.forEach(s => convergedSources.add(s.id)));

  let html = '<h2>Principle Lineage</h2>';
  html += '<p style="color:var(--text-muted);margin-bottom:24px">Patterns that multiple sources independently identified — convergence across different thinkers and traditions.</p>';

  if (convergences.length > 0) {
    convergences.forEach(c => {
      const pat = c.pattern;
      html += '<div class="lineage-cluster">';
      html += '<div class="lineage-pattern-header">';
      html += '<span class="lineage-pattern-name" data-id="' + pat.id + '">' + escapeHtml(pat.title) + '</span>';
      html += '<span class="lineage-count">' + c.sources.length + ' sources</span>';
      html += '</div>';
      if (pat.meta && pat.meta.statement) {
        html += '<div class="lineage-pattern-statement">' + escapeHtml(pat.meta.statement) + '</div>';
      }
      html += '<div class="lineage-members">';
      c.sources.forEach(s => {
        const title = getDisplayTitle(s);
        const source = s.meta.source || '';
        html += '<div class="lineage-member-card" data-id="' + s.id + '">' +
          '<div class="lineage-member-title">' + escapeHtml(title) + '</div>' +
          '<div class="lineage-member-source">' + escapeHtml(source) + '</div>' +
        '</div>';
      });
      html += '</div></div>';
    });
  } else {
    html += '<p style="color:var(--text-muted)">No patterns have been identified by multiple sources yet.</p>';
  }

  // Sources with no convergence
  const standalone = principles.filter(p => !convergedSources.has(p.id));
  if (standalone.length > 0) {
    html += '<div class="lineage-section"><h3>No Shared Patterns Yet</h3>';
    html += '<p style="color:var(--text-muted);margin-bottom:12px;font-size:13px">These sources haven\'t yet been linked to patterns seen by other sources.</p>';
    standalone.forEach(p => {
      html += '<div class="lineage-standalone-row" data-id="' + p.id + '">' +
        '<span style="background:' + TYPE_COLORS.principle + ';display:inline-block;width:8px;height:8px;border-radius:50%;flex-shrink:0"></span>' +
        '<span class="lineage-standalone-title">' + escapeHtml(getDisplayTitle(p)) + '</span>' +
        '<span class="lineage-standalone-source">' + escapeHtml(p.meta.source || '') + '</span>' +
      '</div>';
    });
    html += '</div>';
  }

  view.innerHTML = html;

  // Click handlers
  view.querySelectorAll('.lineage-member-card, .lineage-standalone-row').forEach(el => {
    el.addEventListener('click', () => selectNode(el.dataset.id, { forceDetail: true }));
  });
  view.querySelectorAll('.lineage-pattern-name').forEach(el => {
    el.addEventListener('click', () => {
      const id = el.dataset.id;
      if (id && nodeMap[id]) selectNode(id, { forceDetail: true });
    });
  });
}

// ---------------------------------------------------------------------------
// Navigation
// ---------------------------------------------------------------------------
function selectNode(nodeId, options) {
  options = options || {};
  selectedNode = nodeMap[nodeId] || null;
  buildSidebar();
  if (!selectedNode) return;

  if (currentView === 'graph' && !options.forceDetail) {
    focusGraphNode(nodeId);
    document.getElementById('main-title').textContent = getDisplayTitle(selectedNode);
    return;
  }

  if (currentView !== 'detail') switchView('detail');
  showDetail(nodeId);
}

const VIZ_VIEWS = ['graph', 'layers', 'matrix', 'timeline', 'flow', 'lineage'];
const VIZ_LABELS = {
  graph: 'Force Graph', layers: 'Layer Deep Dive', matrix: 'Corroboration Matrix',
  timeline: 'Timeline', flow: 'Layer Flow', gaps: 'Gap Analysis',
  lineage: 'Principle Lineage',
};
const ALL_VIEWS = ['dashboard', 'detail', 'gaps', 'redteam', ...VIZ_VIEWS];

function switchView(view) {
  currentView = view;

  // Top-level buttons
  document.querySelectorAll('.view-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.view === view);
  });

  // Red Team button — active when in redteam view, or when all filters are on
  const rtBtn = document.getElementById('redteam-nav-btn');
  if (rtBtn) rtBtn.classList.toggle('active', view === 'redteam' || activeFilters.size === TYPE_ORDER.length);

  // Dropdown button state
  const isViz = VIZ_VIEWS.includes(view);
  const dropBtn = document.getElementById('viz-dropdown-btn');
  dropBtn.classList.toggle('active', isViz);
  dropBtn.textContent = isViz ? (VIZ_LABELS[view] + ' \u25BE') : 'Visualizations \u25BE';

  // Dropdown item highlighting
  document.querySelectorAll('.view-dropdown-item').forEach(item => {
    item.classList.toggle('active', item.dataset.view === view);
  });

  // Close dropdown
  document.getElementById('viz-dropdown-menu').classList.remove('open');

  // Toggle visibility of all views
  ALL_VIEWS.forEach(v => {
    const el = document.getElementById(v + '-view');
    if (el) el.style.display = v === view ? 'block' : 'none';
  });

  // Scroll the active view to top
  const activeView = document.getElementById(view + '-view');
  if (activeView) activeView.scrollTop = 0;

  // Hide graph legend when not in graph view
  const legend = document.getElementById('graph-legend');
  if (legend) legend.style.display = view === 'graph' ? 'block' : 'none';

  // Clear or set the header title
  if (view === 'detail' && selectedNode) {
    document.getElementById('main-title').textContent = getDisplayTitle(selectedNode);
  } else if (view !== 'detail') {
    document.getElementById('main-title').textContent = '';
  }

  // Lazy-build triggers
  if (view === 'graph') setTimeout(() => buildGraph(), 50);
  if (view === 'layers') setTimeout(() => buildLayers(), 50);
  if (view === 'matrix') setTimeout(() => buildMatrix(), 50);
  if (view === 'timeline') setTimeout(() => buildTimeline(), 50);
  if (view === 'flow') setTimeout(() => buildFlow(), 50);
  if (view === 'gaps') setTimeout(() => buildGaps(), 50);
  if (view === 'lineage') setTimeout(() => buildLineage(), 50);
  if (view === 'redteam') setTimeout(() => buildRedTeam(), 50);

  // If switching to detail with a selected node, show it
  if (view === 'detail' && selectedNode) showDetail(selectedNode.id);
}

// ---------------------------------------------------------------------------
// Utils
// ---------------------------------------------------------------------------
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ---------------------------------------------------------------------------
// Event listeners
// ---------------------------------------------------------------------------
const searchInput = document.getElementById('search');
const searchClear = document.getElementById('search-clear');

function updateSearchClear() {
  searchClear.style.display = searchInput.value ? 'block' : 'none';
}

searchInput.addEventListener('input', (e) => {
  searchQuery = e.target.value;
  updateSearchClear();
  buildSidebar();
});

searchClear.addEventListener('click', () => {
  searchInput.value = '';
  searchQuery = '';
  updateSearchClear();
  searchInput.focus();
  buildSidebar();
});

document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    const type = btn.dataset.type;
    const isRedTeam = (type === 'redteam');

    if (isRedTeam) {
      // Red Team: toggle between redteam view and dashboard
      if (currentView === 'redteam') {
        TYPE_ORDER.forEach(t => activeFilters.add(t));
        switchView('dashboard');
      } else {
        activeFilters.clear();
        switchView('redteam');
      }
    } else if (e.shiftKey) {
      // Shift+click: toggle this one filter (old behavior)
      if (activeFilters.has(type)) activeFilters.delete(type);
      else activeFilters.add(type);
    } else {
      // Click: exclusive select
      if (activeFilters.size === 1 && activeFilters.has(type)) {
        // Already solo — restore all
        TYPE_ORDER.forEach(t => activeFilters.add(t));
      } else {
        activeFilters.clear();
        activeFilters.add(type);
      }
    }

    const allOn = activeFilters.size === TYPE_ORDER.length;
    document.querySelectorAll('.filter-btn').forEach(b => {
      if (b.dataset.type === 'redteam') {
        b.classList.toggle('active', currentView === 'redteam' || allOn);
      } else {
        b.classList.toggle('active', activeFilters.has(b.dataset.type));
      }
    });
    buildSidebar();
    if (currentView === 'graph') buildGraph();
    if (currentView === 'layers') buildLayers();
  });
});

document.querySelectorAll('.view-btn').forEach(btn => {
  btn.addEventListener('click', () => switchView(btn.dataset.view));
});

// Dropdown toggle
const vizDropBtn = document.getElementById('viz-dropdown-btn');
const vizDropMenu = document.getElementById('viz-dropdown-menu');
vizDropBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  vizDropMenu.classList.toggle('open');
});
document.querySelectorAll('.view-dropdown-item').forEach(item => {
  item.addEventListener('click', () => {
    switchView(item.dataset.view);
  });
});
// Close dropdown on outside click
document.addEventListener('click', () => {
  vizDropMenu.classList.remove('open');
});

// Reset buttons
document.getElementById('graph-reset').addEventListener('click', () => {
  if (graphSvg && graphZoom) {
    graphSvg.transition().duration(500).call(graphZoom.transform, d3.zoomIdentity);
    if (graphNodeSel && graphLinkSel) clearHighlight(graphNodeSel, graphLinkSel);
  }
});

// Sidebar resize
(function() {
  const sidebar = document.getElementById('sidebar');
  const handle = document.getElementById('sidebar-resize');
  let startX, startWidth;

  handle.addEventListener('mousedown', (e) => {
    e.preventDefault();
    startX = e.clientX;
    startWidth = sidebar.offsetWidth;
    handle.classList.add('dragging');
    document.addEventListener('mousemove', onDrag);
    document.addEventListener('mouseup', stopDrag);
  });

  function onDrag(e) {
    const w = Math.max(200, Math.min(600, startWidth + e.clientX - startX));
    sidebar.style.width = w + 'px';
    sidebar.style.minWidth = w + 'px';
  }

  function stopDrag() {
    handle.classList.remove('dragging');
    document.removeEventListener('mousemove', onDrag);
    document.removeEventListener('mouseup', stopDrag);
  }
})();

// Keyboard shortcuts and navigation
document.addEventListener('keydown', (e) => {
  if (e.key === '/' && document.activeElement !== searchInput) {
    e.preventDefault();
    searchInput.focus();
  }
  if (e.key === 'Escape') {
    searchInput.blur();
    searchInput.value = '';
    searchQuery = '';
    updateSearchClear();
    buildSidebar();
    vizDropMenu.classList.remove('open');
    if (currentView === 'graph' && graphNodeSel && graphLinkSel) {
      clearHighlight(graphNodeSel, graphLinkSel);
    }
  }

  // Arrow key navigation in sidebar
  if ((e.key === 'ArrowDown' || e.key === 'ArrowUp' || e.key === 'Enter') && document.activeElement !== searchInput) {
    const items = Array.from(document.querySelectorAll('.sidebar-item'));
    if (items.length === 0) return;

    if (e.key === 'Enter') {
      const active = document.querySelector('.sidebar-item.active');
      if (active && active.dataset.nodeId) {
        selectNode(active.dataset.nodeId, { forceDetail: true });
      }
      return;
    }

    e.preventDefault();
    const currentIdx = items.findIndex(el => el.classList.contains('active'));
    let nextIdx;
    if (e.key === 'ArrowDown') {
      nextIdx = currentIdx < 0 ? 0 : Math.min(currentIdx + 1, items.length - 1);
    } else {
      nextIdx = currentIdx < 0 ? 0 : Math.max(currentIdx - 1, 0);
    }

    const nodeId = items[nextIdx].dataset.nodeId;
    if (nodeId) {
      selectedNode = nodeMap[nodeId] || null;
      items.forEach(el => el.classList.remove('active'));
      items[nextIdx].classList.add('active');
      items[nextIdx].scrollIntoView({ block: 'nearest' });
      document.getElementById('main-title').textContent = getDisplayTitle(selectedNode);
    }
  }
});

// Init
buildSidebar();
buildDashboard();
</script>
</body>
</html>"""


def main():
    data = build()
    data_json = json.dumps(data, ensure_ascii=False)

    # Write data as external JS file
    OUT_DATA.write_text(f"const DATA = {data_json};\n", encoding="utf-8")
    print(f"\nWrote {OUT_DATA} ({OUT_DATA.stat().st_size / 1024:.0f} KB)")

    # Write HTML (no embedded data), with cache-busting timestamp
    import time
    html = HTML_TEMPLATE.replace("__BUILD_TS__", str(int(time.time())))
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
