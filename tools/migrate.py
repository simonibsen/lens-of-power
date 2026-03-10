#!/usr/bin/env python3
"""
migrate.py — Populate YAML data files from existing markdown sources.

One-time migration script. Reads all markdown files and populates the
YAML data layer in data/. After running, the YAML files become the
source of truth for structured data.

Usage:
    python3 tools/migrate.py [--dry-run]

With --dry-run, prints what would be written without modifying files.
"""

import yaml
import re
import os
import sys
from pathlib import Path
from collections import defaultdict
from datetime import date

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# ════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════

LAYER_MAP = {
    "Thought & Narrative": "thought_narrative",
    "Economic": "economic",
    "Legal & Regulatory": "legal_regulatory",
    "Institutional": "institutional",
    "Surveillance & Information": "surveillance_information",
    "Physical & Coercive": "physical_coercive",
}

ALL_LAYERS = list(LAYER_MAP.values())

# Reverse map for some edge cases
LAYER_MAP_LOWER = {k.lower(): v for k, v in LAYER_MAP.items()}


def parse_layers(text: str) -> list[str]:
    """Parse layer text to list of layer IDs."""
    text = text.strip()
    if text.startswith("All six") or text.startswith("All layers") or text == "All six":
        return list(ALL_LAYERS)
    if text.startswith("All non-Physical"):
        return [l for l in ALL_LAYERS if l != "physical_coercive"]
    layers = []
    # Handle compound descriptions like "All six (Thought & Narrative and Economic primary)"
    for layer_name, layer_id in LAYER_MAP.items():
        if layer_name in text:
            layers.append(layer_id)
    if not layers:
        # Try splitting by comma
        for part in re.split(r",\s*", text):
            clean = re.sub(r"\s*\([^)]*\)", "", part).strip()
            if clean in LAYER_MAP:
                layers.append(LAYER_MAP[clean])
    return layers


def parse_layers_with_classification(text: str) -> tuple[list, list, list]:
    """Parse layers text into (primary, secondary, absent) lists.

    Handles formats like:
    - "Physical & Coercive (primary), Economic, Thought & Narrative"
    - "All six (Physical & Coercive, Economic, Legal & Regulatory primary)"
    - "Five primary (...), Physical & Coercive active but absent"
    """
    primary = []
    secondary = []
    absent = []

    text = text.strip()

    # Check for "active but absent" markers
    absent_match = re.findall(
        r"(\w[\w\s&]+?)\s*(?:\()?active but absent(?:\))?", text
    )
    for am in absent_match:
        am = am.strip().rstrip(",")
        if am in LAYER_MAP:
            absent.append(LAYER_MAP[am])

    # Check for explicit "(primary)" markers
    primary_matches = re.findall(
        r"(\w[\w\s&]+?)\s*\(primary\)", text
    )
    for pm in primary_matches:
        pm = pm.strip().rstrip(",")
        if pm in LAYER_MAP:
            primary.append(LAYER_MAP[pm])

    # Handle "All six" or "All layers" with primary annotations
    if text.startswith("All six") or text.startswith("All layers") or text.startswith("All non-Physical"):
        if text.startswith("All non-Physical"):
            all_mentioned = [l for l in ALL_LAYERS if l != "physical_coercive"]
        else:
            all_mentioned = list(ALL_LAYERS)
        if primary:
            secondary = [l for l in all_mentioned if l not in primary and l not in absent]
        else:
            # "All six (all primary — ...)"
            if "all primary" in text.lower():
                primary = [l for l in all_mentioned if l not in absent]
            else:
                primary = [l for l in all_mentioned if l not in absent]
        return primary, secondary, absent

    # Handle "Five primary (...)" or "N primary (...)"
    five_match = re.match(r"(?:Five|Four|Three|Two)\s+primary\s*\(([^)]+)\)", text)
    if five_match:
        inner = five_match.group(1)
        for layer_name, layer_id in LAYER_MAP.items():
            if layer_name in inner:
                primary.append(layer_id)
        # Everything else mentioned is secondary or absent
        for layer_name, layer_id in LAYER_MAP.items():
            if layer_id not in primary and layer_id not in absent and layer_name in text:
                secondary.append(layer_id)
        return primary, secondary, absent

    # Standard parsing: look at each layer mentioned
    for layer_name, layer_id in LAYER_MAP.items():
        if layer_name not in text:
            continue
        if layer_id in absent:
            continue
        if layer_id in primary:
            continue
        # Check if this layer has "(primary)" after it
        pat = re.escape(layer_name) + r"\s*\(primary\)"
        if re.search(pat, text):
            if layer_id not in primary:
                primary.append(layer_id)
        else:
            secondary.append(layer_id)

    # If no explicit primary markers, all non-absent are primary
    if not primary:
        primary = secondary
        secondary = []

    return primary, secondary, absent


def pattern_name_to_id(name: str) -> str:
    """Convert display name to snake_case ID."""
    name = name.strip()
    # Strip leading articles
    name = re.sub(r"^(The|A|An)\s+", "", name)
    # Handle special cases
    name = name.replace("/", " ")
    name = name.replace("–", " ")
    name = name.replace("—", " ")
    name = name.replace("-", " ")
    # Remove non-alphanumeric (keep spaces)
    name = re.sub(r"[^a-zA-Z0-9\s]", "", name)
    # Collapse whitespace and convert
    name = re.sub(r"\s+", "_", name.strip()).lower()
    return name


def parse_position(text: str) -> tuple[list[int], str]:
    """Parse position text like '5 (fiction as analytical model)' -> ([5], 'fiction as analytical model')"""
    text = text.strip()
    # Handle "Hybrid (2/4 — citizen/media intermediary)" or "Hybrid (5/activist)"
    hybrid_match = re.match(r"Hybrid\s*\(([^)]+)\)", text)
    if hybrid_match:
        inner = hybrid_match.group(1)
        # Extract numbers
        nums = [int(n) for n in re.findall(r"\d+", inner)]
        # Note is everything after the numbers/slashes
        note_part = re.sub(r"[\d/]+\s*[—–-]?\s*", "", inner).strip()
        return nums, note_part or inner

    # Standard: "5 (note)" or "4 (intermediary — advisor to rulers)"
    match = re.match(r"(\d+)\s*\(([^)]+)\)", text)
    if match:
        return [int(match.group(1))], match.group(2).strip()

    # Just a number
    match = re.match(r"(\d+)", text)
    if match:
        return [int(match.group(1))], ""

    return [5], text  # default


def parse_null_case(text: str) -> tuple[str, str]:
    """Parse null case like 'rejected (LOW for operation; MEDIUM for school strike)'.
    Returns (outcome, level_text).
    """
    text = text.strip()
    match = re.match(r"(accepted|plausible|rejected)\s*\(([^)]+(?:\([^)]*\))*[^)]*)\)", text)
    if match:
        return match.group(1), match.group(2).strip()
    # Try simpler format
    match = re.match(r"(accepted|plausible|rejected)", text)
    if match:
        remainder = text[match.end():].strip().strip("()")
        return match.group(1), remainder or "unspecified"
    return "plausible", text


def extract_file_stem(filepath: str) -> str:
    """Extract ID from file path like 'analyses/foo.md' -> 'foo'."""
    return Path(filepath).stem


# ════════════════════════════════════════════════════════════════════
# Parse analyses/INDEX.md
# ════════════════════════════════════════════════════════════════════

def parse_analysis_index() -> list[dict]:
    """Parse analyses/INDEX.md into a list of analysis metadata dicts."""
    index_path = ROOT / "analyses" / "INDEX.md"
    text = index_path.read_text()
    entries = []

    # Split on ### headings
    blocks = re.split(r"^### ", text, flags=re.MULTILINE)

    for block in blocks[1:]:  # Skip header
        lines = block.strip().split("\n")
        heading = lines[0].strip()

        # Parse heading: "2026-03-01 — Title (optional domain desc)"
        heading_match = re.match(r"([\d\-]+)\s*[—–-]\s*(.+)", heading)
        if not heading_match:
            print(f"  WARN: Could not parse heading: {heading[:60]}")
            continue

        date_str = heading_match.group(1)
        title = heading_match.group(2).strip()

        entry = {
            "date": date_str,
            "title": title,
            "domain_raw": "",
            "layers_raw": "",
            "null_case_raw": "",
            "file": None,
            "adversarial": False,
            "ic5_flag": None,
            "cross_references": [],
            "origin": None,
        }

        # Parse indented fields
        body = "\n".join(lines[1:])
        for line in lines[1:]:
            line = line.strip()
            if line.startswith("Domain:"):
                entry["domain_raw"] = line[len("Domain:"):].strip()
            elif line.startswith("Layers:"):
                entry["layers_raw"] = line[len("Layers:"):].strip()
            elif line.startswith("Null case:"):
                entry["null_case_raw"] = line[len("Null case:"):].strip()
            elif line.startswith("File:"):
                fname = re.search(r"`([^`]+)`", line)
                if fname:
                    entry["file"] = f"analyses/{fname.group(1)}"
            elif line.startswith("Adversarial input:"):
                entry["adversarial"] = "yes" in line.lower()
            elif line.startswith("IC-5 flag:"):
                entry["ic5_flag"] = line[len("IC-5 flag:"):].strip()
            elif line.startswith("Cross-references:"):
                refs = re.findall(r"`([^`]+)`", line)
                entry["cross_references"] = [extract_file_stem(r) for r in refs]
            elif line.startswith("Origin:"):
                entry["origin"] = "sample" if "SAMPLE" in line else line[len("Origin:"):].strip()

        entries.append(entry)

    return entries


# ════════════════════════════════════════════════════════════════════
# Parse analysis file headers
# ════════════════════════════════════════════════════════════════════

def parse_analysis_file(filepath: Path) -> dict:
    """Parse an analysis file header for URL, SOURCE TYPE, TIME, POSITION, findings."""
    text = filepath.read_text()
    result = {
        "url": None,
        "source_type_raw": None,
        "source_name": None,
        "time": None,
        "position_raw": None,
        "findings": [],
    }

    # Parse header fields (before first ---)
    header_match = re.split(r"^---\s*$", text, maxsplit=1, flags=re.MULTILINE)
    header = header_match[0] if header_match else text[:2000]

    for line in header.split("\n"):
        line = line.strip()
        if line.startswith("URL:"):
            result["url"] = line[len("URL:"):].strip()
        elif line.startswith("SOURCE TYPE:"):
            result["source_type_raw"] = line[len("SOURCE TYPE:"):].strip()
        elif line.startswith("SOURCE:"):
            result["source_name"] = line[len("SOURCE:"):].strip()
        elif line.startswith("TIME:"):
            result["time"] = line[len("TIME:"):].strip()
        elif line.startswith("SOURCE POSITION:"):
            result["position_raw"] = line[len("SOURCE POSITION:"):].strip()

    # Parse findings for patterns_matched
    # Strategy 1: New format with [PATTERNS: ...] [OBSERVED/INFERRED/SPECULATIVE]
    findings = []
    seen_patterns = set()

    finding_pattern = re.compile(
        r"\[PATTERNS?:\s*([^\]]+)\]\s*\[(OBSERVED|INFERRED|SPECULATIVE)"
        r"(?:\s*[—–-]\s*([^\]]*))?\]",
        re.IGNORECASE,
    )

    for match in finding_pattern.finditer(text):
        patterns_str = match.group(1).strip()
        status = match.group(2).lower()

        pattern_names = [p.strip() for p in patterns_str.split(",")]
        for pn in pattern_names:
            if pn:
                pid = pattern_name_to_id(pn)
                if pid not in seen_patterns:
                    seen_patterns.add(pid)
                    findings.append({
                        "pattern": pid,
                        "status": status,
                        "variant": None,
                        "note": "",
                    })

    # Strategy 2: "### Pattern matches" section with "1. **Pattern Name** — LEVEL —"
    pm_match = re.search(r"### Pattern matches\s*\n(.*?)(?=\n### |\n## |\Z)", text, re.DOTALL)
    if pm_match:
        pm_text = pm_match.group(1)
        for m in re.finditer(r"\d+\.\s+\*\*([^*]+)\*\*\s*[—–-]\s*(ESTABLISHED|SUPPORTED|PRELIMINARY)", pm_text):
            pname = m.group(1).strip()
            pid = pattern_name_to_id(pname)
            if pid not in seen_patterns:
                seen_patterns.add(pid)
                findings.append({
                    "pattern": pid,
                    "status": "observed",
                    "variant": None,
                    "note": "",
                })

    # Strategy 3: Scan findings/pattern-matches sections for known pattern names
    # This catches all format variants by looking for the actual pattern display names
    # We'll populate known_pattern_names at call time (set externally)
    result["_raw_text"] = text  # Store for later pattern scanning

    result["findings"] = findings
    return result


def normalize_source_type(raw: str) -> str:
    """Normalize source type string to config enum value."""
    if not raw:
        return "news_article"
    raw_lower = raw.lower()
    mapping = {
        "news article": "news_article",
        "live blog": "live_blog",
        "wire": "wire_story",
        "wire story": "wire_story",
        "investigation": "investigation",
        "investigative": "investigation",
        "investigative data": "investigative_data",
        "investigative data analysis": "investigative_data",
        "policy brief": "policy_brief",
        "policy analysis": "policy_brief",
        "academic": "academic_paper",
        "academic paper": "academic_paper",
        "government": "government_document",
        "government document": "government_document",
        "government minutes": "government_minutes",
        "report": "report",
        "database": "database",
        "essay": "essay",
        "encyclopedia": "encyclopedia",
        "military press release": "military_press_release",
        "research": "research",
    }
    for key, val in mapping.items():
        if key in raw_lower:
            return val
    return "news_article"


def parse_domains(raw: str) -> list[str]:
    """Parse domain text to list of domain IDs."""
    domain_keywords = {
        "foreign policy": "us_foreign_policy",
        "military": "military",
        "platform governance": "platform_governance",
        "surveillance capitalism": "surveillance_capitalism",
        "domestic policy": "domestic_policy",
        "institutional capture": "institutional_capture",
        "ai": "ai_policy",
        "media consolidation": "media_consolidation",
        "media": "media_consolidation",
        "energy": "energy_economics",
        "oil": "energy_economics",
        "press freedom": "press_freedom",
        "information warfare": "information_warfare",
        "policing": "policing",
        "police": "policing",
        "local gov": "local_governance",
        "municipal": "local_governance",
        "privacy": "privacy_regulation",
        "healthcare": "healthcare_policy",
        "medicaid": "healthcare_policy",
        "campaign finance": "campaign_finance",
        "lobbying": "campaign_finance",
        "labour": "labour",
        "labor": "labour",
        "education": "education",
        "environment": "environment",
        "climate": "environment",
        "housing": "housing",
        "postcolonial": "postcolonial",
        "reparation": "postcolonial",
        "decoloni": "postcolonial",
        "financial reg": "financial_regulation",
        "banking": "financial_regulation",
        "geopolitics": "geopolitics",
        "trade": "geopolitics",
        "sanction": "geopolitics",
        "occupation": "military_occupation",
        "settlement": "military_occupation",
        "settler": "military_occupation",
        "ethics": "ethics_disclosure",
        "disclosure": "ethics_disclosure",
        "conflict of interest": "ethics_disclosure",
        "war powers": "war_powers",
        "sovereign wealth": "sovereign_wealth",
        "immigration": "domestic_policy",
        "civil liberties": "domestic_policy",
        "dark money": "institutional_capture",
        "donor": "institutional_capture",
        "religion": "institutional_capture",
        "datacenter": "ai_policy",
    }
    raw_lower = raw.lower()
    domains = []
    for keyword, domain_id in domain_keywords.items():
        if keyword in raw_lower and domain_id not in domains:
            domains.append(domain_id)
    return domains or ["domestic_policy"]


# ════════════════════════════════════════════════════════════════════
# Parse patterns-detail.md (OBSERVED IN)
# ════════════════════════════════════════════════════════════════════

def parse_patterns_detail() -> dict:
    """Parse patterns-detail.md.

    Returns dict keyed by pattern_id, each value has:
        observed_in: list of {source_id, source_type, note}
        evidence: list of evidence file stems
    """
    filepath = ROOT / "patterns-detail.md"
    text = filepath.read_text()

    result = {}
    # Split into pattern sections
    sections = re.split(r"^### ", text, flags=re.MULTILINE)

    for section in sections[1:]:  # Skip header
        lines = section.strip().split("\n")
        pattern_name = lines[0].strip()
        pattern_id = pattern_name_to_id(pattern_name)

        observed_in = []
        evidence = []

        # Find OBSERVED IN section
        full_text = "\n".join(lines[1:])

        # Extract OBSERVED IN block
        obs_match = re.search(
            r"OBSERVED IN:\s*(.*?)(?=\n(?:EVIDENCE|CORROBORATION|CIRCUMVENTIONS|$))",
            full_text,
            re.DOTALL,
        )
        if obs_match:
            obs_text = obs_match.group(1).strip()
            # Parse markdown links: [filepath](url) followed by note text
            # Links are separated by commas/newlines
            link_pattern = re.compile(
                r"\[((?:principles|analyses)/[^\]]+\.md)\]\([^)]+\)"
            )
            # Split obs_text by links
            parts = link_pattern.split(obs_text)
            links = link_pattern.findall(obs_text)

            for i, link_path in enumerate(links):
                source_id = Path(link_path).stem
                source_type = "principle" if link_path.startswith("principles/") else "analysis"

                # Get the note text after this link (before next link)
                if i + 1 < len(parts):
                    note_text = parts[i + 1 + 1] if i + 1 + 1 < len(parts) else ""
                else:
                    note_text = ""

                # Actually, parts alternate: [before_first_link, link1, between1_2, link2, ...]
                # parts[0] = before first link
                # parts[1] = link1 text
                # parts[2] = text between link1 and link2
                # etc.
                # We want the text AFTER each link, which is at index i*2 + 2 in original split
                # But using findall + split is off. Let me use a different approach.
                pass

            # Better approach: use finditer with positions
            observed_in = []
            link_iter = list(link_pattern.finditer(obs_text))
            for idx, m in enumerate(link_iter):
                link_path = m.group(1)
                source_id = Path(link_path).stem
                source_type = "principle" if link_path.startswith("principles/") else "analysis"

                # Note is everything after this match until next link or end
                start = m.end()
                end = link_iter[idx + 1].start() if idx + 1 < len(link_iter) else len(obs_text)
                note_raw = obs_text[start:end].strip()

                # Clean up note: remove leading/trailing punctuation and commas
                note_raw = note_raw.strip(",").strip()
                # Remove leading P-refs like "P2" or "P1, P8"
                note_raw = re.sub(r"^P\d+(?:,\s*P\d+)*\s*", "", note_raw).strip()
                # Remove wrapping parentheses
                if note_raw.startswith("(") and note_raw.endswith(")"):
                    note_raw = note_raw[1:-1].strip()
                elif note_raw.startswith("("):
                    # Find matching close paren
                    depth = 0
                    close_idx = -1
                    for ci, ch in enumerate(note_raw):
                        if ch == "(":
                            depth += 1
                        elif ch == ")":
                            depth -= 1
                            if depth == 0:
                                close_idx = ci
                                break
                    if close_idx > 0:
                        note_raw = note_raw[1:close_idx].strip()

                # Truncate long notes
                if len(note_raw) > 300:
                    note_raw = note_raw[:297] + "..."

                observed_in.append({
                    "source_id": source_id,
                    "source_type": source_type,
                    "variant": None,
                    "note": note_raw,
                })

        # Extract EVIDENCE references
        ev_match = re.search(r"EVIDENCE:\s*(.+?)(?:\n|$)", full_text)
        if ev_match:
            ev_text = ev_match.group(1).strip()
            ev_files = re.findall(r"evidence/([^\s,]+\.md)", ev_text)
            evidence = [Path(f).stem for f in ev_files]

        result[pattern_id] = {
            "observed_in": observed_in,
            "evidence": evidence,
        }

    return result


# ════════════════════════════════════════════════════════════════════
# Parse patterns.md (compact definitions)
# ════════════════════════════════════════════════════════════════════

def parse_patterns() -> list[dict]:
    """Parse patterns.md for pattern definitions."""
    filepath = ROOT / "patterns.md"
    text = filepath.read_text()
    patterns = []

    sections = re.split(r"^### ", text, flags=re.MULTILINE)

    for section in sections[1:]:
        lines = section.strip().split("\n")
        name = lines[0].strip()
        pid = pattern_name_to_id(name)

        full = "\n".join(lines[1:])

        layers_m = re.search(r"LAYERS:\s*(.+)", full)
        layers = parse_layers(layers_m.group(1)) if layers_m else []

        corr_m = re.search(r"CORROBORATION:\s*(\w+)\s*\((\d+)\s+of\s+(\d+)", full)
        confidence_level = corr_m.group(1) if corr_m else "PRELIMINARY"
        obs_count = int(corr_m.group(2)) if corr_m else 0
        corpus_size = int(corr_m.group(3)) if corr_m else 0

        circ_m = re.search(r"CIRCUMVENTIONS:\s*(.+)", full)
        circumventions = []
        if circ_m:
            for c in circ_m.group(1).split(","):
                c = c.strip()
                if c:
                    circumventions.append(pattern_name_to_id(c))

        patterns.append({
            "id": pid,
            "name": name,
            "layers": layers,
            "circumventions": circumventions,
            "confidence_level": confidence_level,
            "obs_count": obs_count,
            "corpus_size": corpus_size,
        })

    return patterns


# ════════════════════════════════════════════════════════════════════
# Parse principles/INDEX.md
# ════════════════════════════════════════════════════════════════════

def parse_principles_index() -> list[dict]:
    """Parse principles/INDEX.md into principle entries."""
    filepath = ROOT / "principles" / "INDEX.md"
    text = filepath.read_text()
    entries = []

    sections = re.split(r"^## ", text, flags=re.MULTILINE)

    for section in sections[1:]:
        lines = section.strip().split("\n")
        filename = lines[0].strip()
        if not filename.endswith(".md"):
            continue

        pid = filename.replace(".md", "")
        full = "\n".join(lines[1:])

        # SOURCE
        source_m = re.search(r"SOURCE:\s*(.+?)(?:\n(?!  )|\Z)", full, re.DOTALL)
        source_raw = source_m.group(1).strip() if source_m else ""

        # Parse source into name, title, year
        src_match = re.match(r"(.+?),\s*\*(.+?)\*\s*\((\d{4})\)", source_raw)
        if src_match:
            source_name = src_match.group(1).strip()
            source_title = src_match.group(2).strip()
            source_year = int(src_match.group(3))
        else:
            # Try without italics
            src_match2 = re.match(r"(.+?),\s*(.+?)\s*\((\d{4})\)", source_raw)
            if src_match2:
                source_name = src_match2.group(1).strip()
                source_title = src_match2.group(2).strip()
                source_year = int(src_match2.group(3))
            else:
                source_name = source_raw
                source_title = ""
                source_year = 0

        # POSITION
        pos_m = re.search(r"POSITION:\s*(.+)", full)
        position, position_note = parse_position(pos_m.group(1)) if pos_m else ([5], "")

        # PRINCIPLES (count — list)
        princ_m = re.search(r"PRINCIPLES:\s*\d+\s*[—–-]\s*(.+?)(?:\n(?!\s)|$)", full, re.DOTALL)
        principles_list = []
        if princ_m:
            raw = princ_m.group(1).strip()
            # Split by commas, but respect parenthetical notes
            depth = 0
            current = ""
            for ch in raw:
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                if ch == "," and depth == 0:
                    if current.strip():
                        principles_list.append(current.strip())
                    current = ""
                else:
                    current += ch
            if current.strip():
                principles_list.append(current.strip())

        # LAYERS
        layers_m = re.search(r"LAYERS:\s*(.+)", full)
        layers = parse_layers(layers_m.group(1)) if layers_m else []

        # KEY PATTERNS
        kp_m = re.search(r"KEY PATTERNS:\s*(.+?)(?:\n|$)", full)
        key_pattern_names = []
        if kp_m:
            for p in re.split(r",\s*", kp_m.group(1).strip()):
                p = p.strip()
                if p:
                    key_pattern_names.append(p)

        # IC-1 FLAGS
        ic1_m = re.search(r"IC-1 FLAGS:\s*(.+?)(?:\n(?!\s)|$)", full, re.DOTALL)
        ic1_flags = []
        if ic1_m:
            raw = ic1_m.group(1).strip()
            for part in re.split(r",\s*(?=Axiom)", raw):
                ax_m = re.match(r"Axiom\s+(\d+)\s*\(([^)]+)\)", part.strip())
                if ax_m:
                    ic1_flags.append({
                        "axiom": int(ax_m.group(1)),
                        "note": ax_m.group(2).strip(),
                    })

        # INSTRUMENT
        inst_m = re.search(r"INSTRUMENT:\s*(.+?)(?:\n|$)", full)
        instruments_produced = []
        if inst_m:
            for i_file in re.findall(r"instruments/([^.\s,]+)", inst_m.group(1)):
                instruments_produced.append(i_file.replace(".md", ""))

        # INSTRUMENT PROPOSED
        inst_prop_m = re.search(r"INSTRUMENT PROPOSED:\s*(.+?)(?:\n|$)", full)
        instruments_proposed = []
        if inst_prop_m:
            # Extract instrument names (these won't have file paths)
            raw = inst_prop_m.group(1).strip()
            for part in raw.split(","):
                part = part.strip()
                if part:
                    # Convert to ID
                    iid = pattern_name_to_id(part.split("(")[0].strip())
                    instruments_proposed.append(iid)

        # SOURCE TYPE
        st_m = re.search(r"SOURCE TYPE:\s*(.+)", full)
        provenance_tier = "training_data"
        if st_m:
            st = st_m.group(1).strip()
            if "primary_document" in st:
                provenance_tier = "primary_document"
            elif "url" in st.lower():
                provenance_tier = "url"

        entries.append({
            "id": pid,
            "file": f"principles/{filename}",
            "source_name": source_name,
            "source_title": source_title,
            "source_year": source_year,
            "position": position,
            "position_note": position_note,
            "provenance_tier": provenance_tier,
            "layers": layers,
            "principles_list": principles_list,
            "key_pattern_names": key_pattern_names,
            "ic1_flags": ic1_flags,
            "instruments_proposed": instruments_proposed,
            "instruments_produced": instruments_produced,
        })

    return entries


# ════════════════════════════════════════════════════════════════════
# Parse evidence/*.md
# ════════════════════════════════════════════════════════════════════

def parse_evidence_files() -> list[dict]:
    """Parse all evidence files."""
    evidence_dir = ROOT / "evidence"
    entries = []

    for fpath in sorted(evidence_dir.glob("*.md")):
        if fpath.name == "README.md":
            continue

        text = fpath.read_text()
        eid = fpath.stem

        entry = {
            "id": eid,
            "file": f"evidence/{fpath.name}",
            "title": "",
            "date_recorded": "",
            "source": "",
            "source_url": None,
            "evidence_source_type": "case_study",
            "axioms": [],
            "patterns": [],
            "layers": [],
            "relationship": "supports",
            "content_summary": "",
        }

        # Parse title from first heading
        title_m = re.match(r"#\s*(.+)", text)
        if title_m:
            title = title_m.group(1).strip()
            # Remove "Evidence: " prefix if present
            title = re.sub(r"^Evidence:\s*", "", title)
            entry["title"] = title

        # First, join continuation lines (lines not starting with a known field)
        # into the previous field's value
        known_fields = [
            "DATE RECORDED:", "DATE:", "SOURCE TYPE:", "SOURCE:", "URL:",
            "AXIOMS:", "PATTERNS:", "LAYERS:", "RELATIONSHIP:", "#",
        ]
        joined_lines = []
        for line in text.split("\n"):
            stripped = line.strip()
            is_field = any(stripped.startswith(f) for f in known_fields)
            if is_field or stripped == "" or stripped.startswith("##"):
                joined_lines.append(stripped)
            elif joined_lines and joined_lines[-1]:
                # Continuation line — append to previous
                joined_lines[-1] = joined_lines[-1] + " " + stripped
            else:
                joined_lines.append(stripped)

        for line in joined_lines:
            if line.startswith("DATE RECORDED:") or (line.startswith("DATE:") and not entry["date_recorded"]):
                entry["date_recorded"] = line.split(":", 1)[1].strip()
            elif line.startswith("SOURCE TYPE:"):
                entry["evidence_source_type"] = line.split(":", 1)[1].strip().replace(" ", "_")
            elif line.startswith("SOURCE:") and not entry["source"]:
                entry["source"] = line.split(":", 1)[1].strip()
            elif line.startswith("URL:"):
                entry["source_url"] = line.split(":", 1)[1].strip()
                if entry["source_url"].startswith(" "):
                    entry["source_url"] = entry["source_url"].strip()
            elif line.startswith("AXIOMS:"):
                entry["axioms"] = [int(a.strip()) for a in line.split(":", 1)[1].split(",") if a.strip().isdigit()]
            elif line.startswith("PATTERNS:"):
                pats = line.split(":", 1)[1].strip()
                if pats.lower() == "all":
                    entry["patterns"] = ["all"]
                else:
                    entry["patterns"] = [pattern_name_to_id(p.strip()) for p in pats.split(",") if p.strip()]
            elif line.startswith("LAYERS:"):
                entry["layers"] = parse_layers(line.split(":", 1)[1])
            elif line.startswith("RELATIONSHIP:"):
                entry["relationship"] = line.split(":", 1)[1].strip()

        # Normalize evidence_source_type
        est = entry["evidence_source_type"].lower().replace("-", "_").replace(" ", "_")
        valid_types = ["statistic", "case_study", "quote", "document", "event", "data", "self_examination"]
        if est not in valid_types:
            if "cross" in est or "synthesis" in est:
                est = "self_examination"
            elif "event" in est:
                est = "event"
            else:
                est = "case_study"
        entry["evidence_source_type"] = est

        entries.append(entry)

    return entries


# ════════════════════════════════════════════════════════════════════
# Parse circumventions.md + circumventions-detail.md
# ════════════════════════════════════════════════════════════════════

def parse_circumventions() -> list[dict]:
    """Parse circumventions.md for definitions."""
    filepath = ROOT / "circumventions.md"
    text = filepath.read_text()
    entries = []

    sections = re.split(r"^### ", text, flags=re.MULTILINE)

    for section in sections[1:]:
        lines = section.strip().split("\n")
        name = lines[0].strip()
        cid = pattern_name_to_id(name)
        full = "\n".join(lines[1:])

        layers_m = re.search(r"LAYERS:\s*(.+)", full)
        layers = parse_layers(layers_m.group(1)) if layers_m else []

        counteracts_m = re.search(r"COUNTERACTS:\s*(.+)", full)
        counteracts = []
        if counteracts_m:
            for p in counteracts_m.group(1).split(","):
                p = p.strip()
                if p:
                    counteracts.append(pattern_name_to_id(p))

        # Parse OBSERVED IN (flat list from compact version)
        obs_m = re.search(r"OBSERVED IN:\s*(.+?)(?:\n\n|\nPOWER|\Z)", full, re.DOTALL)
        observed_in = []
        if obs_m:
            obs_text = obs_m.group(1).strip()
            # Extract file references
            file_refs = re.findall(r"(principles|analyses)/([^,\s]+\.md)", obs_text)
            for source_dir, fname in file_refs:
                sid = Path(fname).stem
                stype = "principle" if source_dir == "principles" else "analysis"
                observed_in.append({
                    "source_id": sid,
                    "source_type": stype,
                    "note": "",
                })

        entries.append({
            "id": cid,
            "name": name,
            "layers": layers,
            "counteracts": counteracts,
            "observed_in": observed_in,
        })

    return entries


def parse_circumventions_detail() -> dict:
    """Parse circumventions-detail.md for detailed OBSERVED IN notes.

    Returns dict keyed by circumvention ID, value is list of
    {source_id, source_type, note}.
    """
    filepath = ROOT / "circumventions-detail.md"
    text = filepath.read_text()
    result = {}

    sections = re.split(r"^### ", text, flags=re.MULTILINE)

    for section in sections[1:]:
        lines = section.strip().split("\n")
        name = lines[0].strip()
        cid = pattern_name_to_id(name)
        full = "\n".join(lines[1:])

        # Find OBSERVED IN block
        obs_match = re.search(
            r"OBSERVED IN:\s*\n((?:- .+\n?)+)",
            full,
        )
        observed_in = []
        if obs_match:
            obs_block = obs_match.group(1)
            for item in re.split(r"\n- ", obs_block):
                item = item.strip().lstrip("- ")
                if not item:
                    continue
                # Extract link
                link_m = re.search(r"\[((?:principles|analyses)/[^\]]+\.md)\]\([^)]+\)", item)
                if link_m:
                    link_path = link_m.group(1)
                    source_id = Path(link_path).stem
                    source_type = "principle" if link_path.startswith("principles/") else "analysis"
                    # Note is everything after the link
                    note = item[link_m.end():].strip()
                    if note.startswith(":"):
                        note = note[1:].strip()
                    if len(note) > 300:
                        note = note[:297] + "..."
                    observed_in.append({
                        "source_id": source_id,
                        "source_type": source_type,
                        "note": note,
                    })
                else:
                    # Non-linked entry (e.g., "TBIJ Portland investigation (2026): ...")
                    observed_in.append({
                        "source_id": "unknown",
                        "source_type": "analysis",
                        "note": item[:300],
                    })

        result[cid] = observed_in

    return result


# ════════════════════════════════════════════════════════════════════
# Parse sources/INDEX.md
# ════════════════════════════════════════════════════════════════════

def parse_sources_index() -> list[dict]:
    """Parse sources/INDEX.md."""
    filepath = ROOT / "sources" / "INDEX.md"
    text = filepath.read_text()
    entries = []

    sections = re.split(r"^## ", text, flags=re.MULTILINE)

    for section in sections[1:]:
        lines = section.strip().split("\n")
        filename = lines[0].strip()
        if not filename.endswith(".md"):
            continue

        sid = filename.replace(".md", "")
        full = "\n".join(lines[1:])

        entry = {
            "id": sid,
            "file": f"sources/{filename}",
            "source": "",
            "provenance_tier": "training_data",
            "hash": None,
            "archive_urls": [],
            "extraction_status": "",
            "quote_status": "",
        }

        for line in lines[1:]:
            line = line.strip()
            if line.startswith("SOURCE:") and not entry["source"]:
                entry["source"] = line[len("SOURCE:"):].strip()
            elif line.startswith("SOURCE TYPE:"):
                st = line[len("SOURCE TYPE:"):].strip()
                if "primary" in st:
                    entry["provenance_tier"] = "primary_document"
                elif "url" in st:
                    entry["provenance_tier"] = "url"
            elif line.startswith("HASH:"):
                entry["hash"] = line[len("HASH:"):].strip()
            elif line.startswith("ARCHIVE:"):
                url_m = re.search(r"\[([^\]]+)\]\(([^)]+)\)", line)
                if url_m:
                    entry["archive_urls"].append(url_m.group(2))
                else:
                    entry["archive_urls"].append(line[len("ARCHIVE:"):].strip())
            elif line.startswith("EXTRACTION STATUS:"):
                entry["extraction_status"] = line[len("EXTRACTION STATUS:"):].strip()
            elif line.startswith("QUOTE STATUS:"):
                entry["quote_status"] = line[len("QUOTE STATUS:"):].strip()

        entries.append(entry)

    return entries


# ════════════════════════════════════════════════════════════════════
# Parse instruments
# ════════════════════════════════════════════════════════════════════

def parse_instruments() -> list[dict]:
    """Parse instrument files for metadata."""
    instruments_dir = ROOT / "instruments"
    entries = []

    for fpath in sorted(instruments_dir.glob("*.md")):
        text = fpath.read_text()
        iid = fpath.stem

        entry = {
            "id": iid,
            "file": f"instruments/{fpath.name}",
            "name": "",
            "status": "complete",
            "layers": [],
            "derived_from": [],
        }

        # Parse title
        title_m = re.match(r"#\s*(?:Instrument:\s*)?(.+)", text)
        if title_m:
            entry["name"] = title_m.group(1).strip()

        # Parse TAXONOMY LAYERS
        layers_m = re.search(r"TAXONOMY LAYERS:\s*(.+)", text)
        if layers_m:
            entry["layers"] = parse_layers(layers_m.group(1))

        # Parse SOURCE or Derived from
        source_m = re.search(r"(?:SOURCE|Derived from):\s*(.+?)(?:\n\n|\n(?=[A-Z]))", text, re.DOTALL)
        if source_m:
            raw = source_m.group(1).strip()
            # Extract principle references
            refs = re.findall(r"([\w-]+)\s*\(\d{4}\)", raw)
            entry["derived_from"] = refs if refs else [raw[:100]]

        entries.append(entry)

    return entries


# ════════════════════════════════════════════════════════════════════
# Build YAML output
# ════════════════════════════════════════════════════════════════════

def yaml_header(filename: str) -> str:
    """Return the existing header comments from a YAML file."""
    fpath = DATA / filename
    if not fpath.exists():
        return ""

    lines = fpath.read_text().split("\n")
    header = []
    past_initial_comments = False
    for line in lines:
        if line.startswith("#") or line == "" or line.startswith("  #"):
            header.append(line)
        elif line.startswith("entries:") or line.startswith("stats:"):
            break
        else:
            if not past_initial_comments:
                header.append(line)
            else:
                break
    return "\n".join(header)


class YamlDumper(yaml.SafeDumper):
    """Custom YAML dumper for readable output."""
    pass


def str_representer(dumper, data):
    """Use literal block style for long strings, double-quoted for dates."""
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    if re.match(r"^\d{4}-\d{2}(-\d{2})?$", data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')
    if re.match(r"^~", data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


def none_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:null", "null")


YamlDumper.add_representer(str, str_representer)
YamlDumper.add_representer(type(None), none_representer)


def dump_yaml(data: dict) -> str:
    """Dump data dict to YAML string."""
    return yaml.dump(
        data,
        Dumper=YamlDumper,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )


# ════════════════════════════════════════════════════════════════════
# Main migration
# ════════════════════════════════════════════════════════════════════

def main():
    dry_run = "--dry-run" in sys.argv
    warnings = []

    print("=" * 60)
    print("Lens of Power — YAML Migration")
    print("=" * 60)

    # ── Step 1: Parse all sources ──────────────────────────────

    print("\n[1/8] Parsing analyses/INDEX.md...")
    analysis_index = parse_analysis_index()
    print(f"  Found {len(analysis_index)} analysis entries")

    print("\n[2/8] Parsing analysis file headers...")
    analysis_details = {}
    for entry in analysis_index:
        if entry["file"]:
            fpath = ROOT / entry["file"]
            if fpath.exists():
                analysis_details[entry["file"]] = parse_analysis_file(fpath)
            else:
                warnings.append(f"Analysis file not found: {entry['file']}")

    print("\n[3/8] Parsing patterns.md + patterns-detail.md...")
    pattern_defs = parse_patterns()
    pattern_detail = parse_patterns_detail()
    print(f"  Found {len(pattern_defs)} patterns, {len(pattern_detail)} with OBSERVED IN")

    print("\n[4/8] Parsing principles/INDEX.md...")
    principle_entries = parse_principles_index()
    print(f"  Found {len(principle_entries)} principle entries")

    print("\n[5/8] Parsing evidence files...")
    evidence_entries = parse_evidence_files()
    print(f"  Found {len(evidence_entries)} evidence entries")

    print("\n[6/8] Parsing circumventions...")
    circumvention_defs = parse_circumventions()
    circumvention_detail = parse_circumventions_detail()
    print(f"  Found {len(circumvention_defs)} circumvention types")

    print("\n[7/8] Parsing sources/INDEX.md...")
    source_entries = parse_sources_index()
    print(f"  Found {len(source_entries)} source entries")

    print("\n[8/8] Parsing instruments...")
    instrument_entries = parse_instruments()
    print(f"  Found {len(instrument_entries)} instruments")

    # ── Step 2: Build cross-references ─────────────────────────

    print("\n── Building cross-references ──")

    # Build principle key_patterns from patterns-detail.md
    # Reverse map: for each principle, what patterns reference it?
    principle_key_patterns = defaultdict(list)
    for pat_id, detail in pattern_detail.items():
        for obs in detail.get("observed_in", []):
            if obs["source_type"] == "principle":
                principle_key_patterns[obs["source_id"]].append({
                    "pattern": pat_id,
                    "variant": obs.get("variant"),
                    "note": obs.get("note", ""),
                })

    # Build analysis patterns_matched from patterns-detail.md
    analysis_patterns_matched = defaultdict(list)
    for pat_id, detail in pattern_detail.items():
        for obs in detail.get("observed_in", []):
            if obs["source_type"] == "analysis":
                analysis_patterns_matched[obs["source_id"]].append({
                    "pattern": pat_id,
                    "status": "observed",  # Default; will be updated from file
                    "variant": obs.get("variant"),
                    "note": obs.get("note", ""),
                })

    # Build known pattern name -> ID map for scanning
    known_patterns = {pdef["name"]: pdef["id"] for pdef in pattern_defs}

    # Update status from analysis file findings and scan for pattern names
    for entry in analysis_index:
        if not entry["file"]:
            continue
        details = analysis_details.get(entry["file"], {})
        file_findings = details.get("findings", [])
        analysis_id = extract_file_stem(entry["file"])

        # Build a map of pattern_id -> status from findings
        finding_status_map = {}
        for f in file_findings:
            finding_status_map[f["pattern"]] = f["status"]

        # Update the patterns_matched entries
        for pm in analysis_patterns_matched.get(analysis_id, []):
            if pm["pattern"] in finding_status_map:
                pm["status"] = finding_status_map[pm["pattern"]]

        # If analysis still has no patterns_matched, scan full text for known pattern names
        if not analysis_patterns_matched.get(analysis_id):
            raw_text = details.get("_raw_text", "")
            if raw_text:
                found_pids = set()
                for pname, pid in known_patterns.items():
                    # Look for pattern name in analytical sections (not just header)
                    # Require it appears in a context suggesting it's a finding
                    # (near patterns.md reference, in CONFIRMS, or in bold)
                    contexts = [
                        r"\b" + re.escape(pname) + r"\b.*?patterns\.md",
                        r"patterns\.md.*?\b" + re.escape(pname) + r"\b",
                        r"CONFIRMS:.*?\b" + re.escape(pname) + r"\b",
                        r"PATTERN MATCH:.*?\b" + re.escape(pname) + r"\b",
                        r"\*\*" + re.escape(pname) + r"\*\*",
                    ]
                    for ctx in contexts:
                        if re.search(ctx, raw_text, re.DOTALL):
                            found_pids.add(pid)
                            break

                for pid in found_pids:
                    if pid not in {pm["pattern"] for pm in analysis_patterns_matched.get(analysis_id, [])}:
                        analysis_patterns_matched[analysis_id].append({
                            "pattern": pid,
                            "status": "observed",
                            "variant": None,
                            "note": "",
                        })

    # Build counter_evidence from evidence entries
    pattern_counter_evidence = defaultdict(list)
    for ev in evidence_entries:
        if ev["relationship"] in ("challenges", "complicates"):
            for pat_id in ev.get("patterns", []):
                pattern_counter_evidence[pat_id].append(ev["id"])

    # ── Step 3: Build YAML data ────────────────────────────────

    print("\n── Building YAML data ──")

    # --- analyses.yaml ---
    analyses_data = []
    for entry in analysis_index:
        if not entry["file"]:
            warnings.append(f"Analysis missing file: {entry['title']}")
            continue

        analysis_id = extract_file_stem(entry["file"])
        details = analysis_details.get(entry["file"], {})

        # Parse position from details
        pos_raw = details.get("position_raw", "")
        if pos_raw:
            # Extract position number
            pos_match = re.search(r"Position\s+(\d+)", pos_raw)
            position = [int(pos_match.group(1))] if pos_match else [5]
        else:
            position = [5]

        # Parse layers with classification
        layers_primary, layers_secondary, layers_absent = parse_layers_with_classification(
            entry["layers_raw"]
        )

        # Parse null case
        null_outcome, null_level = parse_null_case(entry["null_case_raw"])

        # Parse source name from details
        source_name_raw = details.get("source_name") or ""
        # Strip year/date suffix
        source_name = re.sub(r"\s*\([^)]*\d{4}[^)]*\)$", "", source_name_raw).strip()

        # Source date from analysis date or entry date
        source_date = entry["date"]

        # Get patterns_matched
        pm = analysis_patterns_matched.get(analysis_id, [])
        if not pm:
            # Try to get from findings
            pm = details.get("findings", [])

        # Count findings
        findings_count = len(pm)

        analyses_data.append({
            "id": analysis_id,
            "file": entry["file"],
            "date": entry["date"],
            "time": details.get("time"),
            "source_date": source_date,
            "title": entry["title"],
            "source_name": source_name or "unknown",
            "source_type": normalize_source_type(details.get("source_type_raw", "")),
            "position": position,
            "url": details.get("url"),
            "domain": parse_domains(entry["domain_raw"]),
            "layers_primary": layers_primary,
            "layers_secondary": layers_secondary,
            "layers_absent": layers_absent,
            "null_case": null_outcome,
            "null_case_level": null_level,
            "adversarial": entry["adversarial"],
            "origin": entry["origin"],
            "ic5_flag": entry["ic5_flag"],
            "cross_references": entry["cross_references"] if entry["cross_references"] else [],
            "patterns_matched": pm,
            "findings_count": findings_count,
            "commit": None,
        })

    print(f"  analyses.yaml: {len(analyses_data)} entries")

    # --- patterns.yaml ---
    # Map pattern IDs that we know originated from specific extractions
    originated_by_map = {
        "categorical_blindness": "hooks-aint-i-a-woman",
        "boomerang": "arendt-origins-of-totalitarianism",
        "structural_demand_for_propaganda": "ellul-propaganda",
    }

    patterns_data = []
    for pdef in pattern_defs:
        pid = pdef["id"]
        detail = pattern_detail.get(pid, {})

        obs_in = detail.get("observed_in", [])
        counter_ev = pattern_counter_evidence.get(pid, [])

        # Compute confidence
        corpus_size = pdef["corpus_size"]
        obs_count = len(obs_in) if obs_in else pdef["obs_count"]
        ratio = obs_count / corpus_size if corpus_size > 0 else 0.0

        patterns_data.append({
            "id": pid,
            "name": pdef["name"],
            "file": None,
            "layers": pdef["layers"],
            "circumventions": pdef["circumventions"],
            "originated_by": originated_by_map.get(pid),
            "observed_in": obs_in,
            "counter_evidence": counter_ev,
            "confidence_ratio": round(ratio, 4) if corpus_size > 0 else None,
            "confidence_level": pdef["confidence_level"],
            "relevant_corpus_size": corpus_size if corpus_size > 0 else None,
        })

    print(f"  patterns.yaml: {len(patterns_data)} entries")

    # --- principles.yaml ---
    principles_data = []
    for pentry in principle_entries:
        pid = pentry["id"]

        # Use key_patterns from patterns-detail reverse map
        key_patterns = principle_key_patterns.get(pid, [])

        # If none from reverse map, build from INDEX flat names
        if not key_patterns and pentry["key_pattern_names"]:
            for kpn in pentry["key_pattern_names"]:
                key_patterns.append({
                    "pattern": pattern_name_to_id(kpn),
                    "variant": None,
                    "note": "",
                })

        principles_data.append({
            "id": pid,
            "file": pentry["file"],
            "source_name": pentry["source_name"],
            "source_title": pentry["source_title"],
            "source_year": pentry["source_year"],
            "position": pentry["position"],
            "position_note": pentry["position_note"],
            "provenance_tier": pentry["provenance_tier"],
            "layers": pentry["layers"],
            "principles_list": pentry["principles_list"],
            "key_patterns": key_patterns,
            "ic1_flags": pentry["ic1_flags"],
            "instruments_proposed": pentry["instruments_proposed"],
            "instruments_produced": pentry["instruments_produced"],
        })

    print(f"  principles.yaml: {len(principles_data)} entries")

    # --- evidence.yaml ---
    evidence_data = []
    for ev in evidence_entries:
        evidence_data.append({
            "id": ev["id"],
            "file": ev["file"],
            "title": ev["title"],
            "date_recorded": ev["date_recorded"],
            "source": ev["source"],
            "source_url": ev["source_url"],
            "evidence_source_type": ev["evidence_source_type"],
            "axioms": ev["axioms"],
            "patterns": ev["patterns"],
            "layers": ev["layers"],
            "relationship": ev["relationship"],
        })

    print(f"  evidence.yaml: {len(evidence_data)} entries")

    # --- circumventions.yaml ---
    circumventions_data = []
    for cdef in circumvention_defs:
        cid = cdef["id"]
        # Merge compact and detail observed_in
        detail_obs = circumvention_detail.get(cid, [])
        obs_in = detail_obs if detail_obs else cdef["observed_in"]

        circumventions_data.append({
            "id": cid,
            "name": cdef["name"],
            "layers": cdef["layers"],
            "counteracts": cdef["counteracts"],
            "observed_in": obs_in,
        })

    print(f"  circumventions.yaml: {len(circumventions_data)} entries")

    # --- sources.yaml ---
    sources_data = []
    for src in source_entries:
        sources_data.append({
            "id": src["id"],
            "file": src["file"],
            "source": src["source"],
            "provenance_tier": src["provenance_tier"],
            "hash": src["hash"],
            "archive_urls": src["archive_urls"],
            "extraction_status": src["extraction_status"],
            "quote_status": src["quote_status"],
        })

    print(f"  sources.yaml: {len(sources_data)} entries")

    # --- instruments.yaml ---
    instruments_data = []
    for inst in instrument_entries:
        instruments_data.append({
            "id": inst["id"],
            "file": inst["file"],
            "name": inst["name"],
            "status": inst["status"],
            "layers": inst["layers"],
            "derived_from": inst["derived_from"],
        })

    print(f"  instruments.yaml: {len(instruments_data)} entries")

    # ── Step 4: Write YAML files ───────────────────────────────

    print("\n── Writing YAML files ──")

    files_to_write = {
        "analyses.yaml": {"entries": analyses_data},
        "patterns.yaml": {"entries": patterns_data},
        "principles.yaml": {"entries": principles_data},
        "evidence.yaml": {"entries": evidence_data},
        "circumventions.yaml": {"entries": circumventions_data},
        "sources.yaml": {"entries": sources_data},
        "instruments.yaml": {"entries": instruments_data},
    }

    for filename, data in files_to_write.items():
        filepath = DATA / filename
        header = yaml_header(filename)

        yaml_str = dump_yaml(data)

        # Combine header and data
        output = header.rstrip("\n") + "\n\n" + yaml_str

        if dry_run:
            print(f"  [DRY RUN] Would write {filepath}")
            # Show first 20 lines
            for line in output.split("\n")[:20]:
                print(f"    {line}")
            print("    ...")
        else:
            filepath.write_text(output)
            print(f"  Wrote {filepath}")

    # ── Step 5: Report ─────────────────────────────────────────

    print("\n" + "=" * 60)
    print("Migration Summary")
    print("=" * 60)
    print(f"  Analyses:       {len(analyses_data)}")
    print(f"  Patterns:       {len(patterns_data)}")
    print(f"  Principles:     {len(principles_data)}")
    print(f"  Evidence:       {len(evidence_data)}")
    print(f"  Circumventions: {len(circumventions_data)}")
    print(f"  Sources:        {len(sources_data)}")
    print(f"  Instruments:    {len(instruments_data)}")
    print(f"  Calibration:    (already populated, not modified)")

    if warnings:
        print(f"\n  Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"    - {w}")

    # Validation checks
    print("\n── Validation ──")

    # Check all analysis IDs are unique
    analysis_ids = [a["id"] for a in analyses_data]
    dupes = [x for x in analysis_ids if analysis_ids.count(x) > 1]
    if dupes:
        print(f"  WARN: Duplicate analysis IDs: {set(dupes)}")
    else:
        print(f"  OK: All {len(analysis_ids)} analysis IDs unique")

    # Check all pattern IDs are unique
    pattern_ids = [p["id"] for p in patterns_data]
    dupes = [x for x in pattern_ids if pattern_ids.count(x) > 1]
    if dupes:
        print(f"  WARN: Duplicate pattern IDs: {set(dupes)}")
    else:
        print(f"  OK: All {len(pattern_ids)} pattern IDs unique")

    # Check principle key_patterns reference valid patterns
    valid_pids = set(pattern_ids)
    for pentry in principles_data:
        for kp in pentry.get("key_patterns", []):
            if kp["pattern"] not in valid_pids:
                print(f"  WARN: Principle {pentry['id']} references unknown pattern: {kp['pattern']}")

    # Check analysis patterns_matched reference valid patterns
    for aentry in analyses_data:
        for pm in aentry.get("patterns_matched", []):
            if pm["pattern"] not in valid_pids:
                print(f"  WARN: Analysis {aentry['id']} references unknown pattern: {pm['pattern']}")

    # Check evidence patterns reference valid patterns
    for ev in evidence_data:
        for pid in ev.get("patterns", []):
            if pid not in valid_pids:
                print(f"  WARN: Evidence {ev['id']} references unknown pattern: {pid}")

    # Verify YAML parses cleanly
    if not dry_run:
        print("\n── YAML validation ──")
        for filename in files_to_write:
            filepath = DATA / filename
            try:
                with open(filepath) as f:
                    loaded = yaml.safe_load(f)
                entry_count = len(loaded.get("entries", []))
                print(f"  OK: {filename} ({entry_count} entries)")
            except yaml.YAMLError as e:
                print(f"  FAIL: {filename}: {e}")

    print("\nDone." + (" (dry run — no files modified)" if dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
