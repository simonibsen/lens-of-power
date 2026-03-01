# Lens of Power

An interpretive framework for studying power and control across layers
of society — from control of thought to financial systems to policing —
and understanding how these layers interconnect.

This is a living analytical system. It accumulates knowledge over time
as works are studied and current events are analyzed. It is designed to
be used by both humans and LLMs.

## What this is

A structured spec containing:

- **Axioms** about how power operates (constitution)
- **A taxonomy** of the layers through which power acts
- **A methodology** for analyzing new information and extracting
  principles from bodies of work
- **Instruments** — imported analytical tools (logical fallacies,
  control hierarchies, etc.)
- **Principles** — generalizable truths extracted from specific works
- **Patterns** — cross-cutting structures observed across domains
- **Evidence** — concrete facts and data grounding the framework

## Quick start

If using Claude Code, navigate to this directory and use the `/lop` skill:

```
/lop analyze [article, event, policy, or URL]
/lop extract [book, film, theory, or historical account]
/lop instrument [source to evaluate as potential analytical tool]
/lop redteam
```

If using another LLM or working manually, load these files as context:

1. `constitution.md` — axioms and integrity constraints
2. `taxonomy.md` — the six layers of power
3. `methodology.md` — the analytical procedure
4. `patterns.md` — known cross-cutting patterns

Then follow the procedure in `methodology.md` for your chosen mode.

## Structure

```
lens-of-power/
├── constitution.md          Foundational axioms and integrity constraints
├── taxonomy.md              The six layers of power and their mechanisms
├── methodology.md           Analytical procedures (analyze/extract/instrument/redteam)
├── patterns.md              Cross-cutting patterns (grows over time)
├── instruments/             Imported analytical tools
│   ├── control-hierarchy.md   5-level escalation ladder for control ambition
│   ├── logical-fallacies.md   38 fallacies organized by power function
│   └── newspeak-checklist.md  Detecting language as an instrument of control
├── principles/              Extracted from specific works
│   └── orwell-1984.md        8 principles from Nineteen Eighty-Four
├── evidence/                Concrete facts, data, cases
│   └── README.md              Entry format specification
├── analyses/                Applied analyses of current material
└── tools/                   Utility scripts (article fetcher, etc.)
```

## Integrity constraints

The framework includes structural safeguards against becoming a closed
ideological system:

- **IC-1: Falsifiability** — Every axiom has an explicit falsification
  condition. Evidence that contradicts an axiom is recorded, not suppressed.
- **IC-2: Null case** — Every analysis must consider the non-power
  explanation. If incompetence, accident, or good faith fits the evidence
  equally well, the framework says so.
- **IC-3: Red team** — The framework is periodically turned on itself
  to detect confirmation bias and unfalsifiability.
- **IC-4: Living document** — The framework must evolve. Axioms,
  patterns, and the taxonomy are updated as evidence accumulates.
- **IC-5: LLM bias** — When executed by an LLM, the framework names
  the LLM's own training biases as a structural limitation.

## Design principles

- **LLM-native**: All files are written in directive style with structured
  output formats, designed to be executed directly by an LLM
- **Portable**: The spec files work with any LLM or can be followed manually
- **Modular**: Instruments, principles, and evidence can be added without
  restructuring
- **Version-controlled**: The git history is the framework's memory
