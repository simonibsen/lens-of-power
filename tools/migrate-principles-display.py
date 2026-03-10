#!/usr/bin/env python3
"""One-time migration: extract exact display lines from principles/INDEX.md
and store them as display override fields in data/principles.yaml.

Extracts: source_display, position_display, instruments_produced_display,
instruments_proposed_display, source_type_display, chapters_scanned.
"""

import re
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def parse_principles_index():
    """Parse principles/INDEX.md into {id: {field: exact_line_content}}."""
    text = (ROOT / "principles" / "INDEX.md").read_text()
    entries = {}
    current_id = None
    current = None

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

        # Extract exact line content for each field
        if line.startswith("SOURCE:"):
            current["source_display"] = line[len("SOURCE:"):].strip()
        elif line.startswith("POSITION:"):
            current["position_display"] = line[len("POSITION:"):].strip()
        elif line.startswith("INSTRUMENT PROPOSED:"):
            current.setdefault("instruments_proposed_display", []).append(
                line[len("INSTRUMENT PROPOSED:"):].strip()
            )
        elif line.startswith("INSTRUMENT:"):
            current.setdefault("instruments_produced_display", []).append(
                line[len("INSTRUMENT:"):].strip()
            )
        elif line.startswith("SOURCE TYPE:"):
            current["source_type_display"] = line[len("SOURCE TYPE:"):].strip()
        elif line.startswith("CHAPTERS SCANNED:"):
            current["chapters_scanned"] = line[len("CHAPTERS SCANNED:"):].strip()

    if current and current_id:
        entries[current_id] = current

    return entries


def main():
    index_data = parse_principles_index()
    yaml_path = ROOT / "data" / "principles.yaml"

    original = yaml_path.read_text()
    data = yaml.safe_load(original)

    modified = 0
    for entry in data.get("entries", []):
        eid = entry["id"]
        if eid in index_data:
            idx = index_data[eid]
            for field in ("source_display", "position_display",
                          "instruments_produced_display", "instruments_proposed_display",
                          "source_type_display", "chapters_scanned"):
                if field in idx:
                    entry[field] = idx[field]
            modified += 1
            # Print what was set
            for k, v in idx.items():
                val_str = str(v)[:70]
                print(f"  {eid}: {k}={val_str}")

    # Preserve header
    marker = "\nentries:\n"
    pos = original.find(marker)
    header = original[:pos + 1] if pos != -1 else ""
    dumped = yaml.dump(
        {"entries": data["entries"]},
        default_flow_style=False,
        allow_unicode=True,
        width=120,
        sort_keys=False,
    )
    yaml_path.write_text(header + dumped)
    print(f"\nUpdated {modified} entries")


if __name__ == "__main__":
    main()
