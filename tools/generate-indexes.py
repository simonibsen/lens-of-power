#!/usr/bin/env python3
"""Generate INDEX.md files from YAML data.

Reads data/*.yaml and produces:
  - analyses/INDEX.md
  - patterns/INDEX.md
  - principles/INDEX.md
  - sources/INDEX.md
  - sources/sample-pool.md  (from data/sample-pool.yaml)

These files are checked into git but are generated, not hand-maintained.
The YAML files in data/ are the single source of truth.

Usage: python3 tools/generate-indexes.py
"""

import sys
import textwrap
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------

def load_yaml(filename: str) -> dict:
    path = DATA / filename
    if not path.exists():
        print(f"Warning: {path} not found", file=sys.stderr)
        return {"entries": []}
    with open(path) as f:
        return yaml.safe_load(f) or {"entries": []}


# ---------------------------------------------------------------------------
# Display name mappings
# ---------------------------------------------------------------------------

LAYER_ID_TO_NAME = {
    "thought_narrative": "Thought & Narrative",
    "economic": "Economic",
    "legal_regulatory": "Legal & Regulatory",
    "institutional": "Institutional",
    "surveillance_information": "Surveillance & Information",
    "physical_coercive": "Physical & Coercive",
}

ALL_LAYER_IDS = list(LAYER_ID_TO_NAME.keys())

DOMAIN_ID_TO_NAME = {
    "us_foreign_policy": "US foreign policy",
    "military": "military",
    "platform_governance": "platform governance",
    "surveillance_capitalism": "surveillance capitalism",
    "domestic_policy": "domestic policy",
    "institutional_capture": "institutional capture",
    "ai_policy": "AI policy",
    "media_consolidation": "media consolidation",
    "energy_economics": "energy economics",
    "press_freedom": "press freedom",
    "information_warfare": "information warfare",
    "policing": "policing",
    "local_governance": "local governance",
    "privacy_regulation": "privacy regulation",
    "healthcare_policy": "healthcare policy",
    "campaign_finance": "campaign finance",
    "labour": "labour",
    "education": "education",
    "environment": "environment",
    "housing": "housing",
    "postcolonial": "postcolonial",
    "financial_regulation": "financial regulation",
    "geopolitics": "geopolitics",
    "military_occupation": "military occupation",
    "ethics_disclosure": "ethics disclosure",
    "war_powers": "war powers",
    "sovereign_wealth": "sovereign wealth",
}


def domain_text(domain_ids: list) -> str:
    """Convert domain IDs to a human-readable string."""
    names = [DOMAIN_ID_TO_NAME.get(d, d.replace("_", " ")) for d in domain_ids]
    text = " / ".join(names)
    # Capitalize first letter of the combined string
    if text:
        text = text[0].upper() + text[1:]
    return text


def layer_names(layer_ids: list) -> list:
    """Convert layer IDs to display names, preserving order."""
    return [LAYER_ID_TO_NAME.get(lid, lid) for lid in (layer_ids or [])]


def layers_text(primary: list, secondary: list, absent: list) -> str:
    """Produce the Layers: display line from structured fields."""
    primary = primary or []
    secondary = secondary or []
    absent = absent or []
    all_ids = set(ALL_LAYER_IDS)

    # All six primary
    if set(primary) == all_ids:
        parts = ["All six"]
        # Add annotations about secondary/absent if present
        extra = []
        if absent:
            extra.append(f"{', '.join(layer_names(absent))} active but absent")
        if extra:
            parts[0] += f" ({'; '.join(extra)})"
        return parts[0]

    # Five primary — "All non-X"
    if len(primary) == 5 and len(set(primary) & all_ids) == 5:
        missing = all_ids - set(primary)
        missing_name = layer_names(list(missing))[0]
        result = f"All non-{missing_name.split(' & ')[0].split(' ')[0]}"
        extra = []
        if secondary:
            extra.append(f"{len(primary)} layers")
        if absent:
            anames = ", ".join(layer_names(absent))
            extra.append(f"{anames} active but absent")
        if extra:
            result += f" ({'; '.join(extra)})"
        return result

    # General case: list primary layers
    primary_names = layer_names(primary)
    parts = []

    if secondary or absent:
        # Complex annotation
        pnames = ", ".join(primary_names)
        annotations = []
        if secondary:
            snames = ", ".join(layer_names(secondary))
            annotations.append(snames)
        if absent:
            anames = ", ".join(layer_names(absent))
            annotations.append(f"{anames} (active but absent)")
        if annotations:
            # Show primary as "(primary)" and list all
            all_mentioned = list(primary_names)
            for s in layer_names(secondary):
                all_mentioned.append(s)
            # Simple format: primary layers listed, annotations in parens
            result = ", ".join(primary_names)
            if secondary:
                result += f", {', '.join(layer_names(secondary))}"
            return result
        return pnames
    else:
        return ", ".join(primary_names)


# ---------------------------------------------------------------------------
# Pattern name/file lookups
# ---------------------------------------------------------------------------

def build_pattern_lookup(patterns_yaml: dict) -> dict:
    """Build id → {name, file} lookup."""
    return {p["id"]: p for p in patterns_yaml.get("entries", [])}


def build_circumvention_lookup(circ_yaml: dict) -> dict:
    """Build id → name lookup."""
    return {c["id"]: c["name"] for c in circ_yaml.get("entries", [])}


# ---------------------------------------------------------------------------
# analyses/INDEX.md
# ---------------------------------------------------------------------------

ANALYSES_HEADER = """\
# Analysis Index

> Role: Registry of all completed analyses. Used to detect selection bias
> (IC-3), identify clustering, and track null case outcomes. Review this
> index during red team reviews.
>
> If the null case column never reads "plausible" or "accepted," the
> framework may be functioning as a confirmation machine (see IC-3 in
> `constitution.md`).

---
"""


def generate_analyses_index(analyses_yaml: dict) -> str:
    lines = [ANALYSES_HEADER]

    for a in analyses_yaml.get("entries", []):
        date = a.get("source_date") or a.get("date", "")
        title = a.get("title", "")
        # Use display override fields when present, fall back to computed
        domains = a.get("domain_text") or domain_text(a.get("domain", []))
        layers = a.get("layers_text") or layers_text(
            a.get("layers_primary", []),
            a.get("layers_secondary", []),
            a.get("layers_absent", []),
        )
        null_case_display = a.get("null_case_text") or (
            f"{a.get('null_case', '')} ({a.get('null_case_level', '')})"
        )
        filename = Path(a.get("file", "")).name

        block = f"### {date} — {title}\n"
        block += f"  Domain: {domains}\n"
        block += f"  Layers: {layers}\n"
        block += f"  Null case: {null_case_display}\n"

        if a.get("adversarial"):
            block += f"  Adversarial input: yes"
            if a.get("adversarial_note"):
                block += f" — {a['adversarial_note']}"
            block += "\n"

        if a.get("origin") == "sample":
            origin_date = a.get("date", "")
            block += f"  Origin: SAMPLE mode ({origin_date})\n"

        if a.get("ic5_flag"):
            block += f"  IC-5 flag: {a['ic5_flag']}\n"

        if a.get("cross_references"):
            notes = a.get("cross_references_notes", {})
            ref_parts = []
            for ref in a["cross_references"]:
                ref_str = f"`{ref}.md`" if not ref.endswith(".md") else f"`{ref}`"
                note = notes.get(ref)
                if note:
                    ref_str += f" ({note})"
                ref_parts.append(ref_str)
            block += f"  Cross-references: {', '.join(ref_parts)}\n"

        block += f"  File: `{filename}`\n"

        lines.append(block)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# patterns/INDEX.md
# ---------------------------------------------------------------------------

PATTERNS_HEADER = """\
# Patterns Index

> Compact lookup table for cross-referencing during analysis.
> Load this instead of individual pattern files. Load full files only
> when detailed evidence trails or analytical notes are needed.

---
"""


def generate_patterns_index(patterns_yaml: dict, circ_yaml: dict) -> str:
    circ_lookup = build_circumvention_lookup(circ_yaml)
    lines = [PATTERNS_HEADER]

    for p in patterns_yaml.get("entries", []):
        name = p["name"]
        filename = Path(p.get("file", "")).name if p.get("file") else f"{p['id']}.md"
        raw_layers = p.get("layers", [])
        if set(raw_layers) == set(ALL_LAYER_IDS):
            layer_list = ["All layers"]
        else:
            layer_list = layer_names(raw_layers)

        # CONFIDENCE line — corr_count and confidence_ratio are computed
        # by build-viewer.py and synced to this YAML
        level = p.get("confidence_level") or "PRELIMINARY"
        corpus = p.get("relevant_corpus_size") or 0
        ratio = p.get("confidence_ratio") or 0.0
        corr_count = p.get("corr_count") or len(p.get("observed_in", []))
        pct = round(ratio * 100)
        confidence = f"{level} ({corr_count} of {corpus} relevant sources, {pct}%)"

        # Wrap statement at ~72 chars for readability
        statement = p.get("statement", "").strip()
        wrapped = textwrap.fill(statement, width=72, initial_indent="STATEMENT: ",
                                subsequent_indent="")

        block = f"## [{name}]({filename})\n"
        block += f"LAYERS: {', '.join(layer_list)}\n"
        block += f"{wrapped}\n"
        block += f"CONFIDENCE: {confidence}\n"

        circs = p.get("circumventions", [])
        if circs:
            circ_names = [circ_lookup.get(c, c) for c in circs]
            block += f"CIRCUMVENTIONS: {', '.join(circ_names)}\n"

        lines.append(block)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# principles/INDEX.md
# ---------------------------------------------------------------------------

PRINCIPLES_HEADER = """\
# Principles Index

> Compact lookup table for cross-referencing during extraction and analysis.
> Load this instead of individual principles files. Load full files only
> when deep comparison with a specific source is needed.

---
"""


def generate_principles_index(principles_yaml: dict, patterns_yaml: dict) -> str:
    pattern_lookup = build_pattern_lookup(patterns_yaml)
    lines = [PRINCIPLES_HEADER]

    for pr in principles_yaml.get("entries", []):
        file_id = pr["id"]
        principles_list = pr.get("principles_list", [])
        key_patterns = pr.get("key_patterns", [])
        ic1_flags = pr.get("ic1_flags", [])
        new_patterns = pr.get("new_pattern_candidates", [])

        # SOURCE — use display override or compute from fields
        source_line = pr.get("source_display")
        if not source_line:
            sn = pr.get("source_name", "")
            st = pr.get("source_title", "")
            sy = pr.get("source_year", "")
            source_line = f"{sn}, *{st}* ({sy})"

        # POSITION — use display override or compute
        pos_str = pr.get("position_display")
        if not pos_str:
            position = pr.get("position", [])
            position_note = pr.get("position_note", "")
            pos_nums = "/".join(str(p) for p in position)
            if len(position) > 1:
                pos_str = f"Hybrid ({pos_nums} — {position_note})"
            else:
                pos_str = f"{pos_nums} ({position_note})"

        # PRINCIPLES count and list
        principles_str = f"{len(principles_list)} — {', '.join(principles_list)}"

        # LAYERS — use display override when present
        layers = layer_names(pr.get("layers", []))
        layers_str = pr.get("layers_text")
        if not layers_str:
            if len(layers) == 6:
                layers_str = "All six"
            else:
                layers_str = ", ".join(layers)

        # KEY PATTERNS — use display override when present
        kp_str = pr.get("key_patterns_display")
        if not kp_str:
            kp_names = []
            for kp in key_patterns:
                pid = kp["pattern"]
                pdata = pattern_lookup.get(pid, {})
                pname = pdata.get("name", pid)
                variant = kp.get("variant")
                if variant:
                    pname += f" ({variant})"
                kp_names.append(pname)
            kp_str = ", ".join(kp_names)

        # Build block — SOURCE TYPE position varies by entry
        source_type_display = pr.get("source_type_display")

        block = f"## {file_id}.md\n"
        block += f"SOURCE: {source_line}\n"
        block += f"POSITION: {pos_str}\n"

        # Some entries have SOURCE TYPE before PRINCIPLES (original ordering)
        if source_type_display:
            block += f"SOURCE TYPE: {source_type_display}\n"

        block += f"PRINCIPLES: {principles_str}\n"
        block += f"LAYERS: {layers_str}\n"

        # CHAPTERS SCANNED (Project 2025)
        chapters = pr.get("chapters_scanned")
        if chapters:
            block += f"CHAPTERS SCANNED: {chapters}\n"

        block += f"KEY PATTERNS: {kp_str}\n"

        if ic1_flags:
            flags = []
            for fl in ic1_flags:
                flags.append(f"Axiom {fl['axiom']} ({fl['note']})")
            block += f"IC-1 FLAGS: {', '.join(flags)}\n"

        if new_patterns:
            for np in new_patterns:
                block += f"NEW PATTERN CANDIDATE: {np}\n"

        # INSTRUMENT lines — use display overrides when present
        inst_display = pr.get("instruments_produced_display", [])
        if inst_display:
            for inst in inst_display:
                block += f"INSTRUMENT: {inst}\n"

        inst_proposed_display = pr.get("instruments_proposed_display", [])
        if inst_proposed_display:
            for inst in inst_proposed_display:
                block += f"INSTRUMENT PROPOSED: {inst}\n"

        lines.append(block)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# sources/INDEX.md
# ---------------------------------------------------------------------------

SOURCES_HEADER = """\
# Sources Index

> Compact lookup table for source provenance. Each entry records what
> was analyzed, how it was obtained, and what the provenance tier is.
> Load full source files only when verifying provenance or checking
> extraction coverage.

---
"""


def generate_sources_index(sources_yaml: dict) -> str:
    lines = [SOURCES_HEADER]

    for s in sources_yaml.get("entries", []):
        sid = s["id"]
        source = s.get("source", "")
        tier = s.get("provenance_tier", "")
        hash_val = s.get("hash", "")
        archives = s.get("archive_urls", [])
        extraction = s.get("extraction_status", "")
        quote = s.get("quote_status", "")

        block = f"## {sid}.md\n\n"
        block += f"SOURCE: {source}\n\n"
        block += f"SOURCE TYPE: {tier}\n\n"
        if hash_val:
            block += f"HASH: {hash_val}\n\n"
        archive_labels = s.get("archive_labels", {})
        if archives:
            for url in archives:
                label = archive_labels.get(url, url)
                block += f"ARCHIVE: [{label}]({url})\n\n"
        block += f"EXTRACTION STATUS: {extraction}\n\n"
        block += f"QUOTE STATUS: {quote}\n"

        lines.append(block)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# sources/sample-pool.md
# ---------------------------------------------------------------------------

SAMPLE_POOL_HEADER = """\
# Sample Pool

> Role: Source pool for SAMPLE mode randomization. Entries are categorized
> by outlet type and tagged on four axes to enable coverage tracking.
> The pool is designed to include a mix of sources likely to exhibit power
> dynamics and sources where power dynamics may be absent (null-case-likely),
> ensuring the framework's calibration sample space produces genuine null cases.
>
> Maintenance: Add entries when the pool's axis coverage has gaps. Remove
> entries only if an outlet ceases to exist. Do not curate for "relevance"
> — the point is randomness.
>
> Generated from data/sample-pool.yaml — do not edit directly.

---

## Axis definitions

- **INST** (institutional type): corporate, independent, wire, government, trade, local, nonprofit, academic
- **DOMAIN** (subject domain): politics, economics, technology, culture, science, local-gov, sports, lifestyle, health, environment, military, legal
- **GEO** (geographic focus): us-national, us-local, uk, eu, global-south, asia, middle-east, africa, non-anglophone
- **AUD** (audience): general, professional, investor, policymaker, academic
- **POS** (framework position): 1–5 per positional-lens.md

---

## Entries
"""


def _format_tag(key: str, value) -> str:
    """Format a single axis tag for display."""
    abbrev = {"institution": "INST", "domain": "DOMAIN", "geo": "GEO",
              "audience": "AUD", "position": "POS"}
    tag_name = abbrev.get(key, key.upper())
    if isinstance(value, list):
        return f"[{tag_name}:{','.join(str(v) for v in value)}]"
    return f"[{tag_name}:{value}]"


def generate_sample_pool(pool_yaml: dict) -> str:
    lines = [SAMPLE_POOL_HEADER]

    for cat in pool_yaml.get("categories", []):
        lines.append(f"### {cat['name']}\n")
        for entry in cat.get("entries", []):
            outlet = entry["outlet"]
            url = entry["url"]
            tags = entry.get("tags", {})
            tag_parts = []
            for key in ["institution", "domain", "geo", "audience", "position"]:
                if key in tags:
                    tag_parts.append(_format_tag(key, tags[key]))
            tags_str = " ".join(tag_parts)
            lines.append(f"- **{outlet}** ({url}) — {tags_str}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Load all YAML
    analyses = load_yaml("analyses.yaml")
    patterns = load_yaml("patterns.yaml")
    principles = load_yaml("principles.yaml")
    sources = load_yaml("sources.yaml")
    circumventions = load_yaml("circumventions.yaml")

    # Generate and write INDEX files
    analyses_idx = generate_analyses_index(analyses)
    (ROOT / "analyses" / "INDEX.md").write_text(analyses_idx, encoding="utf-8")
    print("Generated analyses/INDEX.md")

    patterns_idx = generate_patterns_index(patterns, circumventions)
    (ROOT / "patterns" / "INDEX.md").write_text(patterns_idx, encoding="utf-8")
    print("Generated patterns/INDEX.md")

    principles_idx = generate_principles_index(principles, patterns)
    (ROOT / "principles" / "INDEX.md").write_text(principles_idx, encoding="utf-8")
    print("Generated principles/INDEX.md")

    sources_idx = generate_sources_index(sources)
    (ROOT / "sources" / "INDEX.md").write_text(sources_idx, encoding="utf-8")
    print("Generated sources/INDEX.md")

    # Generate sample pool markdown (if YAML exists)
    pool_path = DATA / "sample-pool.yaml"
    if pool_path.exists():
        pool = load_yaml("sample-pool.yaml")
        pool_md = generate_sample_pool(pool)
        (ROOT / "sources" / "sample-pool.md").write_text(pool_md, encoding="utf-8")
        print("Generated sources/sample-pool.md")

    print("Done.")


if __name__ == "__main__":
    main()
