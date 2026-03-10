#!/usr/bin/env python3
"""One-time migration: extract display text from hand-maintained INDEX.md files
and add display-override fields to data/*.yaml.

After running, the generate-indexes.py script uses these override fields to
produce INDEX.md files that match the hand-maintained originals exactly.

Usage: python3 tools/migrate-display-fields.py
"""

import re
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def preserve_header_write(path: Path, entries_key: str, entries: list):
    """Write YAML preserving the header comment block above 'entries:'."""
    original = path.read_text()
    # Split at the entries key line
    marker = f"\n{entries_key}:\n"
    idx = original.find(marker)
    if idx == -1:
        # Try without leading newline (start of file)
        marker = f"{entries_key}:\n"
        if original.startswith(marker):
            header = ""
        else:
            print(f"  Warning: could not find '{entries_key}:' in {path.name}", file=sys.stderr)
            return
    else:
        header = original[:idx + 1]  # include the trailing newline before entries:

    dumped = yaml.dump(
        {entries_key: entries},
        default_flow_style=False,
        allow_unicode=True,
        width=120,
        sort_keys=False,
    )
    path.write_text(header + dumped)


# ---------------------------------------------------------------------------
# Parse analyses/INDEX.md
# ---------------------------------------------------------------------------

def parse_analyses_index() -> dict:
    """Parse analyses/INDEX.md into {filename_stem: {field: value}}."""
    text = (ROOT / "analyses" / "INDEX.md").read_text()
    entries = {}
    current = None

    for line in text.split("\n"):
        m = re.match(r"^### (.+)$", line)
        if m:
            current = {"header": m.group(1)}
            continue
        if current is None:
            continue

        line_stripped = line.strip()
        if line_stripped.startswith("Domain:"):
            current["domain_text"] = line_stripped[len("Domain:"):].strip()
        elif line_stripped.startswith("Layers:"):
            current["layers_text"] = line_stripped[len("Layers:"):].strip()
        elif line_stripped.startswith("Null case:"):
            current["null_case_text"] = line_stripped[len("Null case:"):].strip()
        elif line_stripped.startswith("Adversarial input:"):
            rest = line_stripped[len("Adversarial input:"):].strip()
            if "—" in rest:
                current["adversarial_note"] = rest.split("—", 1)[1].strip()
        elif line_stripped.startswith("File:"):
            fname = line_stripped[len("File:"):].strip().strip("`")
            stem = Path(fname).stem
            entries[stem] = current
            current = None

    return entries


# ---------------------------------------------------------------------------
# Parse principles/INDEX.md
# ---------------------------------------------------------------------------

def parse_principles_index() -> dict:
    """Parse principles/INDEX.md into {file_stem: {field: value}}."""
    text = (ROOT / "principles" / "INDEX.md").read_text()
    entries = {}
    current = None
    current_id = None

    for line in text.split("\n"):
        m = re.match(r"^## (.+)\.md$", line)
        if m:
            if current and current_id:
                entries[current_id] = current
            current_id = m.group(1)
            current = {}
            continue
        if current is None:
            continue

        if line.startswith("LAYERS:"):
            current["layers_text"] = line[len("LAYERS:"):].strip()
        elif line.startswith("KEY PATTERNS:"):
            current["key_patterns_display"] = line[len("KEY PATTERNS:"):].strip()
        elif line.startswith("NEW PATTERN CANDIDATE:"):
            current.setdefault("new_pattern_candidates", []).append(
                line[len("NEW PATTERN CANDIDATE:"):].strip()
            )
        elif line.startswith("SOURCE TYPE:"):
            val = line[len("SOURCE TYPE:"):].strip()
            if val != "training_data":
                current["provenance_display"] = val

    if current and current_id:
        entries[current_id] = current

    return entries


# ---------------------------------------------------------------------------
# Parse sources/INDEX.md
# ---------------------------------------------------------------------------

def parse_sources_index() -> dict:
    """Parse sources/INDEX.md into {file_stem: {field: value}}."""
    text = (ROOT / "sources" / "INDEX.md").read_text()
    entries = {}
    current = None
    current_id = None

    for line in text.split("\n"):
        m = re.match(r"^## (.+)\.md$", line)
        if m:
            if current and current_id:
                entries[current_id] = current
            current_id = m.group(1)
            current = {}
            continue
        if current is None:
            continue

        if line.startswith("ARCHIVE:"):
            # Parse [Label](URL) format
            link_m = re.search(r"\[(.+?)\]\((.+?)\)", line)
            if link_m:
                label, url = link_m.group(1), link_m.group(2)
                current.setdefault("archive_labels", {})[url] = label

    if current and current_id:
        entries[current_id] = current

    return entries


# ---------------------------------------------------------------------------
# Apply to YAML
# ---------------------------------------------------------------------------

def migrate_analyses():
    print("Migrating analyses.yaml...")
    index_data = parse_analyses_index()
    yaml_path = DATA / "analyses.yaml"
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    modified = 0
    for entry in data.get("entries", []):
        eid = entry["id"]
        if eid in index_data:
            idx = index_data[eid]
            if "domain_text" in idx:
                entry["domain_text"] = idx["domain_text"]
            if "layers_text" in idx:
                entry["layers_text"] = idx["layers_text"]
            if "null_case_text" in idx:
                entry["null_case_text"] = idx["null_case_text"]
            if "adversarial_note" in idx:
                entry["adversarial_note"] = idx["adversarial_note"]
            modified += 1
        else:
            print(f"  Warning: no INDEX entry for {eid}", file=sys.stderr)

    preserve_header_write(yaml_path, "entries", data["entries"])
    print(f"  Updated {modified} entries")


def migrate_principles():
    print("Migrating principles.yaml...")
    index_data = parse_principles_index()
    yaml_path = DATA / "principles.yaml"
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    modified = 0
    for entry in data.get("entries", []):
        eid = entry["id"]
        if eid in index_data:
            idx = index_data[eid]
            if "layers_text" in idx:
                entry["layers_text"] = idx["layers_text"]
            if "key_patterns_display" in idx:
                entry["key_patterns_display"] = idx["key_patterns_display"]
            if "new_pattern_candidates" in idx:
                entry["new_pattern_candidates"] = idx["new_pattern_candidates"]
            if "provenance_display" in idx:
                entry["provenance_display"] = idx["provenance_display"]
            modified += 1

    preserve_header_write(yaml_path, "entries", data["entries"])
    print(f"  Updated {modified} entries")


def migrate_sources():
    print("Migrating sources.yaml...")
    index_data = parse_sources_index()
    yaml_path = DATA / "sources.yaml"
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    modified = 0
    for entry in data.get("entries", []):
        eid = entry["id"]
        if eid in index_data:
            idx = index_data[eid]
            if "archive_labels" in idx:
                entry["archive_labels"] = idx["archive_labels"]
            modified += 1

    preserve_header_write(yaml_path, "entries", data["entries"])
    print(f"  Updated {modified} entries")


def main():
    migrate_analyses()
    migrate_principles()
    migrate_sources()
    print("Done.")


if __name__ == "__main__":
    main()
