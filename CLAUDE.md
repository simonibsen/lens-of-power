# Lens of Power

This is an interpretive framework for studying power and control across
layers of society. It is both a knowledge base and an analytical tool.

## Structure

- `constitution.md` — Foundational axioms about how power operates
- `taxonomy.md` — The layers of power (thought, economic, legal, institutional, surveillance, physical)
- `methodology.md` — The analytical procedure (ANALYZE, EXTRACT, RED TEAM modes)
- `patterns.md` — Compact pattern definitions (always loaded)
- `patterns-detail.md` — Full evidence trails per pattern (loaded for audits)
- `instruments/` — Imported analytical tools (logical fallacies, cognitive biases, etc.)
- `principles/INDEX.md` — Compact principles lookup table (always loaded)
- `principles/` — Full principles files (loaded selectively)
- `evidence/` — Concrete facts, data, cases that ground the framework
- `analyses/` — Applied analyses of specific material

## Usage

Use the `/lop` skill to apply this framework:
- `/lop analyze [material]` — Run the analytical methodology on new information
- `/lop extract [source]` — Study a source for principles and/or instruments
- `/lop redteam` — Turn the framework on itself (integrity constraint IC-3)

When working in this project, always load `constitution.md`, `taxonomy.md`,
`methodology.md`, `patterns.md`, and `principles/INDEX.md` as context for
any analytical work. Load `patterns-detail.md` for audits and red team
reviews. Load individual `principles/*.md` files only when deep comparison
with a specific source is needed.

## Conventions

- Write all framework files in LLM-directive style (structured, imperative, with clear output formats)
- Tag everything (axioms, layers, patterns) so content can be cross-referenced
- Evidence entries use the format defined in `evidence/README.md`
- Principles use the format defined in the EXTRACT mode section of `methodology.md`
- Patterns use the format defined in `patterns.md`
- Instruments use the format defined in the EXTRACT mode Step 4 of `methodology.md`
- Maintain integrity constraints (IC-1, IC-2, IC-3, IC-4) as defined in `constitution.md`
- IC-1: Every axiom must be falsifiable. Flag contradicting evidence, do not suppress it.
- IC-2: Every analysis must consider the null case (non-power explanation).
- IC-3: Periodically red-team the framework itself.
- IC-4: Keep the framework up to date. Update patterns, evidence, taxonomy, README after each analysis.
- IC-5: The LLM is a biased instrument. Flag when training data likely overrepresents a perspective. Name blind spots. Do not hedge to appear balanced when evidence is not balanced.

## Branching

Each analysis gets its own branch. The branch contains the analysis
file, any evidence entries it produces, and any spec updates it
triggers (new patterns, methodology refinements, taxonomy additions).

**Branch naming**: `analysis/YYYY-MM-DD-short-name`
Example: `analysis/2026-03-01-us-israel-iran-war`

**Workflow**:
1. Create the branch from `main` before starting the analysis
2. Commit the analysis, evidence, and any spec updates it motivates
3. Merge to `main` when the analysis is finalized and reviewed

This keeps `main` clean and makes each analysis a self-contained,
traceable unit of work — the commit history tells the story of what
was analyzed, what was found, and how it updated the framework.

Spec-only work (new instruments, methodology redesign, constitution
changes not triggered by a specific analysis) goes directly on `main`
or on a descriptive feature branch.
