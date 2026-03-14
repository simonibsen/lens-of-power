# Lens of Power

This is an interpretive framework for studying power and control across
layers of society. It is both a knowledge base and an analytical tool.

## Structure

- `constitution.md` — Foundational axioms about how power operates
- `taxonomy.md` — The layers of power (thought, economic, legal, institutional, surveillance, physical)
- `methodology.md` — The analytical procedure (READ, ANALYZE, EXTRACT, RED TEAM, SUGGEST, SAMPLE modes)
- `patterns/INDEX.md` — Compact pattern lookup table (always loaded; generated from YAML)
- `patterns/` — Individual pattern files with full evidence trails (loaded selectively)
- `circumventions.md` — Observed responses to power concentration at two levels: structural (within-frame) and hegemonic (frame-level) (always loaded)
- `circumventions-detail.md` — Full evidence trails per circumvention (loaded for audits)
- `instruments/` — Imported analytical tools (logical fallacies, cognitive biases, etc.)
- `principles/INDEX.md` — Compact principles lookup table (always loaded; generated from YAML)
- `principles/` — Full principles files (loaded selectively)
- `sources/INDEX.md` — Source provenance lookup table (generated from YAML)
- `sources/` — Full provenance records per source (hash, archive links, extraction status)
- `sources/sample-pool.md` — Categorized source pool for SAMPLE mode (generated from YAML)
- `data/` — YAML data files (single source of truth for structured metadata)
- `data/analyses.yaml` — Analysis registry (authoritative for analysis metadata)
- `data/patterns.yaml` — Pattern corroboration data (observed_in is computed)
- `data/principles.yaml` — Extracted principle sources
- `data/calibration.yaml` — SAMPLE mode calibration tracking log
- `data/sample-pool.yaml` — Source pool for SAMPLE mode randomization
- `data/config.yaml` — Shared enumerations, thresholds, domain definitions, and hegemonic contexts
- `data/circumventions.yaml` — Circumvention types (structural + hegemonic) with observed instances
- `evidence/` — Concrete facts, data, cases that ground the framework
- `analyses/INDEX.md` — Analysis registry (generated from YAML)
- `analyses/` — Applied analyses of specific material
- `BACKLOG.md` — Prioritized recommendations from SUGGEST mode diagnostics (living document)
- `tools/build-viewer.py` — Generates `viewer.html` + `viewer-data.js`
- `tools/generate-indexes.py` — Generates INDEX.md files from YAML data
- `tools/build-all.py` — Orchestrator: runs build-viewer.py then generate-indexes.py
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
- Maintain integrity constraints (IC-1 through IC-7) as defined in `constitution.md`
- IC-1: Every axiom must be falsifiable. Flag contradicting evidence, do not suppress it.
- IC-2: Every analysis must consider the null case (non-power explanation).
- IC-3: Periodically red-team the framework itself.
- IC-4: Keep the framework up to date. Update patterns, evidence, taxonomy, README after each analysis.
- IC-5: The LLM is a biased instrument. Flag when training data likely overrepresents a perspective. Name blind spots. Do not hedge to appear balanced when evidence is not balanced.
- IC-6: All tooling must have automated tests. Write tests before or alongside code, never after. Run with `python3 -m pytest tests/ -v`.
- IC-7: Hegemonic complicity. The framework operates within the hegemonic order it studies. Name the framework's position rather than implying it stands outside it. Every analysis includes a hegemonic context (Step 0: CONTEXT) naming the background assumptions shared by the material and the analyst, and the forces that maintain them.

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

`tools/build-all.py` runs the full build pipeline:
1. `build-viewer.py` — computes corroboration, generates viewer.html + viewer-data.js
2. `generate-indexes.py` — generates INDEX.md files from YAML data

Run `python3 tools/build-all.py && open viewer.html` after writing any
analysis or extraction files.

INDEX.md files are generated from `data/*.yaml` and checked into git so
the framework context is always available without a build step. The YAML
files in `data/` are the single source of truth for structured metadata.
Do not hand-edit INDEX.md files — edit the YAML and regenerate.

The viewer has three top-level nav items: Dashboard (landing page with
integrity bar, corpus stats, recent analyses, works studied, layer
coverage, circumventions by tier, hegemonic context distribution),
Gap Analysis (framework health metrics, blind spots, hegemonic context
coverage), and a Visualizations dropdown (Force Graph, Layer Deep Dive,
Corroboration Matrix, Timeline, Layer Flow, Principle Lineage).

The sidebar groups items by type: Analyses, Principles, Instruments,
Patterns, Circumventions (structural in teal, hegemonic in amber),
Hegemonic Contexts, Evidence, and Red Team. Clicking any item opens
a detail view.
