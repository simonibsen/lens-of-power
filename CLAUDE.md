# Lens of Power

This is an interpretive framework for studying power and control across
layers of society. It is both a knowledge base and an analytical tool.

## Structure

- `constitution.md` — Foundational axioms about how power operates
- `taxonomy.md` — The layers of power (thought, economic, legal, institutional, surveillance, physical)
- `methodology.md` — The analytical procedure (7-step ANALYZE mode, 5-step EXTRACT mode)
- `patterns.md` — Cross-cutting patterns observed across domains (grows over time)
- `instruments/` — Imported analytical tools (logical fallacies, cognitive biases, etc.)
- `principles/` — Generalizable truths extracted from specific works
- `evidence/` — Concrete facts, data, cases that ground the framework
- `analyses/` — Applied analyses of specific material

## Usage

Use the `/lop` skill to apply this framework:
- `/lop analyze [material]` — Run the analytical methodology on new information
- `/lop extract [work]` — Extract principles from a body of work
- `/lop redteam` — Turn the framework on itself (integrity constraint IC-3)

When working in this project, always load `constitution.md`, `taxonomy.md`,
and `methodology.md` as context for any analytical work. Load `patterns.md`
and relevant `instruments/` files as needed per the methodology's instructions.

## Conventions

- Write all framework files in LLM-directive style (structured, imperative, with clear output formats)
- Tag everything (axioms, layers, patterns) so content can be cross-referenced
- Evidence entries use the format defined in `evidence/README.md`
- Principles use the format defined in the EXTRACT mode section of `methodology.md`
- Patterns use the format defined in `patterns.md`
- Maintain integrity constraints (IC-1, IC-2, IC-3) as defined in `constitution.md`
- IC-1: Every axiom must be falsifiable. Flag contradicting evidence, do not suppress it.
- IC-2: Every analysis must consider the null case (non-power explanation).
- IC-3: Periodically red-team the framework itself.
