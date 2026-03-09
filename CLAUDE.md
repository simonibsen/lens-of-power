# Lens of Power

This is an interpretive framework for studying power and control across
layers of society. It is both a knowledge base and an analytical tool.

## Structure

- `constitution.md` — Foundational axioms about how power operates
- `taxonomy.md` — The layers of power (thought, economic, legal, institutional, surveillance, physical)
- `methodology.md` — The analytical procedure (READ, ANALYZE, EXTRACT, RED TEAM, SUGGEST, SAMPLE modes)
- `patterns/INDEX.md` — Compact pattern lookup table (always loaded)
- `patterns/` — Individual pattern files with full evidence trails (loaded selectively)
- `circumventions.md` — Observed responses to power concentration (always loaded)
- `circumventions-detail.md` — Full evidence trails per circumvention (loaded for audits)
- `instruments/` — Imported analytical tools (logical fallacies, cognitive biases, etc.)
- `principles/INDEX.md` — Compact principles lookup table (always loaded)
- `principles/` — Full principles files (loaded selectively)
- `sources/INDEX.md` — Source provenance lookup table
- `sources/` — Full provenance records per source (hash, archive links, extraction status)
- `sources/sample-pool.md` — Categorized source pool for SAMPLE mode randomization
- `calibration/sample-log.md` — Append-only tracking log for SAMPLE mode calibration runs
- `evidence/` — Concrete facts, data, cases that ground the framework
- `analyses/` — Applied analyses of specific material
- `BACKLOG.md` — Prioritized recommendations from SUGGEST mode diagnostics (living document)
- `tools/build-viewer.py` — Generates `viewer.html` + `viewer-data.js` (both checked in)
- `tools/fetch-article.py` — URL content extraction fallback
- `tests/` — Automated test suite (IC-6): unit tests, integration tests, YAML integrity checks

## Usage

Use the `/lop` skill to apply this framework:
- `/lop read [material]` — Understand material through the lens (concise prose analysis)
- `/lop analyze [material]` — Run the full analytical methodology on new information
- `/lop extract [source]` — Study a source for principles and/or instruments
- `/lop redteam` — Turn the framework on itself (integrity constraint IC-3)
- `/lop suggest` — Run a framework health diagnostic with prioritized recommendations
- `/lop sample` — Randomly select material and run a calibration read

When working in this project, always load `constitution.md`, `taxonomy.md`,
`methodology.md`, `patterns/INDEX.md`, `circumventions.md`, and `principles/INDEX.md`
as context for any analytical work. Load `circumventions-detail.md` for
circumvention audits. Load individual `patterns/*.md` or `principles/*.md`
files when detailed evidence trails or deep source comparison is needed.

## Conventions

- Write all framework files in LLM-directive style (structured, imperative, with clear output formats)
- Tag everything (axioms, layers, patterns) so content can be cross-referenced
- Evidence entries use the format defined in `evidence/README.md`
- Principles use the format defined in the EXTRACT mode section of `methodology.md`
- Patterns use the format defined in `patterns/INDEX.md` and individual `patterns/*.md` files
- Instruments use the format defined in the EXTRACT mode Step 4 of `methodology.md`
- Sources use the provenance format defined in the Source provenance section of `methodology.md`
- Maintain integrity constraints (IC-1, IC-2, IC-3, IC-4) as defined in `constitution.md`
- IC-1: Every axiom must be falsifiable. Flag contradicting evidence, do not suppress it.
- IC-2: Every analysis must consider the null case (non-power explanation).
- IC-3: Periodically red-team the framework itself.
- IC-4: Keep the framework up to date. Update patterns, evidence, taxonomy, README after each analysis.
- IC-5: The LLM is a biased instrument. Flag when training data likely overrepresents a perspective. Name blind spots. Do not hedge to appear balanced when evidence is not balanced.
- IC-6: All tooling must have automated tests. Write tests before or alongside code, never after. Run with `python3 -m pytest tests/ -v`.

## Branching

Before writing any output (analyses, extractions, evidence, pattern
updates), check the current branch:

- **On main**: Ask the user to create and switch to a working branch
  before writing. Do not write framework files directly to main.
- **Not on main**: Ask the user whether to write to the current branch.

The commit history tells the story of what was analyzed, what was
found, and how it updated the framework. Each commit is a
self-contained, traceable unit of work.

## Viewer

`tools/build-viewer.py` generates a static viewer from all framework
markdown files. Run `python3 tools/build-viewer.py` to rebuild. Output
is `viewer.html` + `viewer-data.js` (gitignored — generated on demand).

After writing any analysis or extraction files, always run
`python3 tools/build-viewer.py && open viewer.html` to verify.

The viewer has three top-level nav items: Dashboard (landing page with
integrity bar, corpus stats, recent analyses, works studied, layer
coverage), Gap Analysis (framework health metrics and blind spots),
and a Visualizations dropdown (Force Graph, Layer Deep Dive,
Corroboration Matrix, Timeline, Layer Flow, Principle Lineage).
Clicking any item in the sidebar opens a detail view.
