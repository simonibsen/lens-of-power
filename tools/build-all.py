#!/usr/bin/env python3
"""Build everything: viewer + generated INDEX files.

Runs build-viewer.py first (computes corroboration, syncs to patterns.yaml),
then generate-indexes.py (reads YAML, produces INDEX.md files).

Usage: python3 tools/build-all.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


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
    # 1. Build viewer (computes corroboration → syncs to patterns.yaml)
    run("build-viewer.py")

    # 2. Generate INDEX.md files from YAML
    run("generate-indexes.py")

    print("\nAll builds complete.")


if __name__ == "__main__":
    main()
