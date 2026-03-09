#!/usr/bin/env python3
"""
post-analysis.py — Automate the post-analysis workflow.

Reads YAML frontmatter from an analysis markdown file, adds/updates the
entry in data/analyses.yaml, recomputes patterns.yaml observed_in and
confidence levels, and rebuilds the viewer.

Usage:
    python3 tools/post-analysis.py analyses/2026-03-10-example-analysis.md
"""

import yaml
import re
import sys
import subprocess
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


# ════════════════════════════════════════════════════════════════════
# YAML Dumper (matches migrate.py)
# ════════════════════════════════════════════════════════════════════

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
# File helpers
# ════════════════════════════════════════════════════════════════════

def yaml_header(filepath: Path) -> str:
    """Return the existing header comments from a YAML file.

    Reads everything before the 'entries:' line so we can prepend it
    when rewriting the file.
    """
    if not filepath.exists():
        return ""

    lines = filepath.read_text().split("\n")
    header = []
    for line in lines:
        if line.startswith("#") or line == "" or line.startswith("  #"):
            header.append(line)
        elif line.startswith("entries:") or line.startswith("stats:"):
            break
        else:
            header.append(line)
    return "\n".join(header)


def load_yaml(filename: str) -> dict:
    """Load a YAML file from data/."""
    filepath = DATA / filename
    if not filepath.exists():
        print(f"  ERROR: {filepath} not found")
        sys.exit(1)
    with open(filepath) as f:
        return yaml.safe_load(f)


def write_yaml(filename: str, data: dict) -> None:
    """Write a YAML file to data/, preserving header comments."""
    filepath = DATA / filename
    header = yaml_header(filepath)
    body = dump_yaml(data)
    with open(filepath, "w") as f:
        if header:
            f.write(header)
            if not header.endswith("\n"):
                f.write("\n")
        f.write(body)


def parse_frontmatter(filepath: Path) -> dict:
    """Parse YAML frontmatter from a markdown file (between --- delimiters)."""
    text = filepath.read_text()
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        print(f"  ERROR: No YAML frontmatter found in {filepath}")
        sys.exit(1)
    return yaml.safe_load(match.group(1))


# ════════════════════════════════════════════════════════════════════
# Validation
# ════════════════════════════════════════════════════════════════════

def validate_entry(entry: dict, config: dict) -> list[str]:
    """Validate an analysis entry against config.yaml enumerations.

    Returns a list of error messages (empty if valid).
    """
    errors = []

    valid_layers = [l["id"] for l in config["layers"]]
    valid_source_types = config["analysis_source_types"]
    valid_domains = [d["id"] for d in config["domains"]]
    valid_positions = [p["id"] for p in config["positions"]]
    valid_null_case = config["null_case_outcomes"]
    valid_statuses = config["finding_statuses"]

    # Required fields
    for field in ["id", "title", "source_name", "source_type", "position",
                  "domain", "layers_primary", "null_case", "patterns_matched"]:
        if field not in entry or entry[field] is None:
            errors.append(f"Missing required field: {field}")

    if errors:
        return errors  # Can't validate further without required fields

    # source_type
    if entry["source_type"] not in valid_source_types:
        errors.append(
            f"Invalid source_type: {entry['source_type']!r} "
            f"(valid: {valid_source_types})"
        )

    # positions
    for p in entry.get("position", []):
        if p not in valid_positions:
            errors.append(f"Invalid position: {p} (valid: {valid_positions})")

    # domains
    for d in entry.get("domain", []):
        if d not in valid_domains:
            errors.append(f"Invalid domain: {d!r} (valid: {valid_domains})")

    # layers
    for layer_field in ["layers_primary", "layers_secondary", "layers_absent"]:
        for layer in entry.get(layer_field, []) or []:
            if layer not in valid_layers:
                errors.append(
                    f"Invalid layer in {layer_field}: {layer!r} "
                    f"(valid: {valid_layers})"
                )

    # null_case
    if entry["null_case"] not in valid_null_case:
        errors.append(
            f"Invalid null_case: {entry['null_case']!r} "
            f"(valid: {valid_null_case})"
        )

    # patterns_matched
    for pm in entry.get("patterns_matched", []):
        if "pattern" not in pm:
            errors.append("patterns_matched entry missing 'pattern' field")
        if pm.get("status") and pm["status"] not in valid_statuses:
            errors.append(
                f"Invalid finding status: {pm['status']!r} "
                f"(valid: {valid_statuses})"
            )

    return errors


# ════════════════════════════════════════════════════════════════════
# Confidence computation
# ════════════════════════════════════════════════════════════════════

def compute_confidence(
    pattern: dict,
    analyses_entries: list[dict],
    principles_entries: list[dict],
    thresholds: dict,
) -> None:
    """Recompute confidence fields on a pattern dict in place."""
    pattern_layers = set(pattern.get("layers", []))
    if not pattern_layers:
        pattern["confidence_ratio"] = None
        pattern["confidence_level"] = None
        pattern["relevant_corpus_size"] = None
        return

    # Count relevant corpus: analyses + principles whose layers overlap
    relevant = 0
    for a in analyses_entries:
        a_layers = set(
            (a.get("layers_primary") or [])
            + (a.get("layers_secondary") or [])
            + (a.get("layers_absent") or [])
        )
        if a_layers & pattern_layers:
            relevant += 1

    for p in principles_entries:
        p_layers = set(p.get("layers") or [])
        if p_layers & pattern_layers:
            relevant += 1

    observed_count = len(pattern.get("observed_in") or [])

    if relevant == 0:
        ratio = 0.0
    else:
        ratio = round(observed_count / relevant, 4)

    # Apply thresholds
    established = thresholds["established"]
    supported = thresholds["supported"]

    has_counter = bool(pattern.get("counter_evidence"))

    if (
        observed_count >= established["min_sources"]
        and ratio >= established["min_ratio"]
        and (not established.get("requires_no_unresolved_counter") or not has_counter)
    ):
        level = "ESTABLISHED"
    elif (
        observed_count >= supported["min_sources"]
        and ratio >= supported["min_ratio"]
    ):
        level = "SUPPORTED"
    else:
        level = "PRELIMINARY"

    pattern["confidence_ratio"] = ratio
    pattern["confidence_level"] = level
    pattern["relevant_corpus_size"] = relevant


# ════════════════════════════════════════════════════════════════════
# Core workflow
# ════════════════════════════════════════════════════════════════════

def build_analysis_entry(frontmatter: dict, analysis_path: Path) -> dict:
    """Build a complete analyses.yaml entry from frontmatter + computed fields."""
    today = date.today().isoformat()

    # Relative path from project root
    try:
        rel_path = str(analysis_path.resolve().relative_to(ROOT))
    except ValueError:
        rel_path = str(analysis_path)

    entry = {
        "id": frontmatter["id"],
        "file": rel_path,
        "date": frontmatter.get("date", today),
        "time": frontmatter.get("time", None),
        "source_date": frontmatter.get("source_date", frontmatter.get("date", today)),
        "title": frontmatter["title"],
        "source_name": frontmatter["source_name"],
        "source_type": frontmatter["source_type"],
        "position": frontmatter["position"],
        "url": frontmatter.get("url", None),
        "domain": frontmatter["domain"],
        "layers_primary": frontmatter["layers_primary"],
        "layers_secondary": frontmatter.get("layers_secondary", []),
        "layers_absent": frontmatter.get("layers_absent", []),
        "null_case": frontmatter["null_case"],
        "null_case_level": frontmatter.get("null_case_level", ""),
        "adversarial": frontmatter.get("adversarial", False),
        "origin": frontmatter.get("origin", None),
        "ic5_flag": frontmatter.get("ic5_flag", None),
        "cross_references": frontmatter.get("cross_references", []),
        "patterns_matched": frontmatter.get("patterns_matched", []),
        "findings_count": len(frontmatter.get("patterns_matched", [])),
        "commit": None,
    }

    return entry


def recompute_observed_in(
    patterns_entries: list[dict],
    analyses_entries: list[dict],
    principles_entries: list[dict],
) -> None:
    """Recompute observed_in for ALL patterns from analyses + principles."""

    # Build a lookup: pattern_id -> list of observed_in entries
    observed = {}
    for p in patterns_entries:
        observed[p["id"]] = []

    # From analyses
    for a in analyses_entries:
        for pm in a.get("patterns_matched") or []:
            pid = pm["pattern"]
            if pid not in observed:
                print(f"  WARNING: Analysis {a['id']} references unknown pattern: {pid}")
                continue
            observed[pid].append({
                "source_id": a["id"],
                "source_type": "analysis",
                "variant": pm.get("variant", None),
                "note": pm.get("note", ""),
            })

    # From principles
    for p in principles_entries:
        for kp in p.get("key_patterns") or []:
            pid = kp["pattern"]
            if pid not in observed:
                print(f"  WARNING: Principle {p['id']} references unknown pattern: {pid}")
                continue
            observed[pid].append({
                "source_id": p["id"],
                "source_type": "principle",
                "variant": kp.get("variant", None),
                "note": kp.get("note", ""),
            })

    # Write back
    for p in patterns_entries:
        p["observed_in"] = observed[p["id"]]


def recompute_counter_evidence(
    patterns_entries: list[dict],
    evidence_entries: list[dict],
) -> None:
    """Recompute counter_evidence for all patterns from evidence.yaml."""
    counters = {}
    for p in patterns_entries:
        counters[p["id"]] = []

    for e in evidence_entries:
        rel = e.get("relationship", "")
        if rel in ("challenges", "complicates"):
            for pid in e.get("patterns") or []:
                if pid in counters:
                    counters[pid].append(e["id"])

    for p in patterns_entries:
        p["counter_evidence"] = counters[p["id"]]


# ════════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════════

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/post-analysis.py <analysis-file.md>")
        print("Example: python3 tools/post-analysis.py analyses/2026-03-10-example.md")
        sys.exit(1)

    analysis_path = Path(sys.argv[1])
    if not analysis_path.is_absolute():
        analysis_path = ROOT / analysis_path
    if not analysis_path.exists():
        print(f"ERROR: File not found: {analysis_path}")
        sys.exit(1)

    print("=" * 60)
    print("Lens of Power — Post-Analysis Workflow")
    print("=" * 60)

    # ── Step 1: Parse frontmatter ──────────────────────────────

    print(f"\n[1/5] Parsing frontmatter from {analysis_path.name}...")
    frontmatter = parse_frontmatter(analysis_path)
    print(f"  ID: {frontmatter.get('id')}")
    print(f"  Title: {frontmatter.get('title')}")
    print(f"  Patterns matched: {len(frontmatter.get('patterns_matched', []))}")

    # ── Step 2: Load data files ────────────────────────────────

    print("\n[2/5] Loading data files...")
    config = load_yaml("config.yaml")
    analyses_data = load_yaml("analyses.yaml")
    patterns_data = load_yaml("patterns.yaml")
    principles_data = load_yaml("principles.yaml")
    evidence_data = load_yaml("evidence.yaml")

    analyses_entries = analyses_data.get("entries", [])
    patterns_entries = patterns_data.get("entries", [])
    principles_entries = principles_data.get("entries", [])
    evidence_entries = evidence_data.get("entries", [])

    print(f"  Analyses: {len(analyses_entries)}")
    print(f"  Patterns: {len(patterns_entries)}")
    print(f"  Principles: {len(principles_entries)}")
    print(f"  Evidence: {len(evidence_entries)}")

    # ── Step 3: Build and validate entry ───────────────────────

    print(f"\n[3/5] Building analysis entry...")
    entry = build_analysis_entry(frontmatter, analysis_path)

    errors = validate_entry(entry, config)
    if errors:
        print("\n  VALIDATION ERRORS:")
        for e in errors:
            print(f"    - {e}")
        sys.exit(1)
    print("  Validation passed.")

    # Add or update in analyses.yaml
    existing_idx = None
    for i, a in enumerate(analyses_entries):
        if a["id"] == entry["id"]:
            existing_idx = i
            break

    if existing_idx is not None:
        analyses_entries[existing_idx] = entry
        print(f"  Updated existing entry: {entry['id']}")
    else:
        analyses_entries.append(entry)
        print(f"  Added new entry: {entry['id']}")

    analyses_data["entries"] = analyses_entries

    # ── Step 4: Recompute patterns ─────────────────────────────

    print(f"\n[4/5] Recomputing patterns...")

    # Recompute observed_in from all analyses + principles
    recompute_observed_in(patterns_entries, analyses_entries, principles_entries)

    # Recompute counter_evidence from evidence
    recompute_counter_evidence(patterns_entries, evidence_entries)

    # Recompute confidence for every pattern
    thresholds = config["confidence_thresholds"]
    for p in patterns_entries:
        compute_confidence(p, analyses_entries, principles_entries, thresholds)

    # Summary
    levels = {"ESTABLISHED": 0, "SUPPORTED": 0, "PRELIMINARY": 0}
    for p in patterns_entries:
        lvl = p.get("confidence_level")
        if lvl in levels:
            levels[lvl] += 1
    print(f"  Confidence levels: {levels['ESTABLISHED']} ESTABLISHED, "
          f"{levels['SUPPORTED']} SUPPORTED, {levels['PRELIMINARY']} PRELIMINARY")

    patterns_data["entries"] = patterns_entries

    # ── Write files ────────────────────────────────────────────

    print("\n  Writing analyses.yaml...")
    write_yaml("analyses.yaml", analyses_data)

    print("  Writing patterns.yaml...")
    write_yaml("patterns.yaml", patterns_data)

    # ── Step 5: Rebuild viewer ─────────────────────────────────

    print(f"\n[5/5] Rebuilding viewer...")
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "build-viewer.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  ERROR: build-viewer.py failed:")
        print(result.stderr)
        sys.exit(1)
    print("  Viewer rebuilt successfully.")

    # ── Done ───────────────────────────────────────────────────

    print("\n" + "=" * 60)
    print("Done. Files updated:")
    print(f"  data/analyses.yaml  ({len(analyses_entries)} entries)")
    print(f"  data/patterns.yaml  ({len(patterns_entries)} entries)")
    print("  viewer.html + viewer-data.js")
    print("=" * 60)


if __name__ == "__main__":
    main()
