#!/usr/bin/env python3
"""Build everything: recompute patterns, build viewer, generate INDEX files.

Pipeline:
  1. Recompute patterns.yaml observed_in + counter_evidence + confidence
     from analyses.yaml + principles.yaml + evidence.yaml
  2. Build viewer (generates viewer.html + viewer-data.js)
  3. Generate INDEX.md files from YAML

Usage: python3 tools/build-all.py
"""

import subprocess
import sys
from pathlib import Path

import importlib.util

import yaml

ROOT = Path(__file__).resolve().parent.parent

# Import from post-analysis.py (hyphenated filename requires importlib)
_spec = importlib.util.spec_from_file_location(
    "post_analysis", ROOT / "tools" / "post-analysis.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
compute_confidence = _mod.compute_confidence
recompute_counter_evidence = _mod.recompute_counter_evidence
recompute_observed_in = _mod.recompute_observed_in


def load_yaml(name: str) -> dict:
    path = ROOT / "data" / name
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(name: str, data: dict) -> None:
    """Write YAML preserving header comments."""
    path = ROOT / "data" / name
    original = path.read_text(encoding="utf-8")
    marker = "\nentries:\n"
    idx = original.find(marker)
    header = original[: idx + 1] if idx != -1 else ""
    dumped = yaml.dump(
        {"entries": data["entries"]},
        default_flow_style=False,
        allow_unicode=True,
        width=120,
        sort_keys=False,
    )
    # Preserve stats section if present (calibration.yaml)
    stats_marker = "\nstats:\n"
    stats_idx = original.find(stats_marker)
    stats_section = original[stats_idx:] if stats_idx != -1 else ""
    path.write_text(header + dumped + stats_section, encoding="utf-8")


def recompute_patterns():
    """Recompute observed_in, counter_evidence, and confidence for all patterns."""
    config = load_yaml("config.yaml")
    analyses_data = load_yaml("analyses.yaml")
    patterns_data = load_yaml("patterns.yaml")
    principles_data = load_yaml("principles.yaml")
    evidence_data = load_yaml("evidence.yaml")

    analyses_entries = analyses_data.get("entries", [])
    patterns_entries = patterns_data.get("entries", [])
    principles_entries = principles_data.get("entries", [])
    evidence_entries = evidence_data.get("entries", [])

    recompute_observed_in(patterns_entries, analyses_entries, principles_entries)
    recompute_counter_evidence(patterns_entries, evidence_entries)

    thresholds = config["confidence_thresholds"]
    for p in patterns_entries:
        compute_confidence(p, analyses_entries, principles_entries, thresholds)

    levels = {"ESTABLISHED": 0, "SUPPORTED": 0, "PRELIMINARY": 0}
    for p in patterns_entries:
        lvl = p.get("confidence_level")
        if lvl in levels:
            levels[lvl] += 1

    patterns_data["entries"] = patterns_entries
    write_yaml("patterns.yaml", patterns_data)
    print(f"Recomputed patterns: {levels['ESTABLISHED']} ESTABLISHED, "
          f"{levels['SUPPORTED']} SUPPORTED, {levels['PRELIMINARY']} PRELIMINARY",
          flush=True)


def run(script: str):
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / script)],
        cwd=str(ROOT),
        capture_output=False,
    )
    if result.returncode != 0:
        print(f"Error: {script} failed with exit code {result.returncode}", file=sys.stderr)
        sys.exit(result.returncode)


def main():
    # 1. Recompute patterns.yaml from authoritative sources
    recompute_patterns()

    # 2. Build viewer (computes corroboration → syncs to patterns.yaml)
    run("build-viewer.py")

    # 3. Generate INDEX.md files from YAML
    run("generate-indexes.py")

    print("\nAll builds complete.")


if __name__ == "__main__":
    main()
