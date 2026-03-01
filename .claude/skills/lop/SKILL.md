---
name: lop
description: Apply the Lens of Power interpretive framework to analyze material for power dynamics, extract principles from a body of work, evaluate sources as potential instruments, or red-team the framework itself.
argument-hint: <analyze|extract|instrument|redteam> [material, work, or source]
user-invocable: true
allowed-tools: Read, Grep, Glob, WebFetch, WebSearch, Write, Edit, Agent, Bash
---

# Lens of Power — Analytical Framework

You are applying the Lens of Power, an interpretive framework for studying
power and control across layers of society.

## Setup: Load the framework

Before proceeding, read these files from the project root:

1. `constitution.md` — axioms, directives, and integrity constraints (ALWAYS load)
2. `taxonomy.md` — layers of power (ALWAYS load)
3. `methodology.md` — the analytical procedure (ALWAYS load)
4. `patterns.md` — known cross-cutting patterns (ALWAYS load)

Also check for relevant instruments:
5. `instruments/` — load any instruments relevant to the material

Also check for existing related work:
6. `principles/` — scan for principles relevant to the material
7. `evidence/` — scan for evidence relevant to the material

## Determine mode

Parse `$ARGUMENTS` to determine the mode:

- If the first argument is `analyze` or the user is providing current material
  (article, news, speech, policy, event): use **ANALYZE mode** from methodology.md
- If the first argument is `extract` or the user is providing a body of work
  (book, film, theory, historical account): use **EXTRACT mode** from methodology.md
- If the first argument is `instrument` or the user is providing a source
  to evaluate as a potential analytical tool (reference page, list, catalog,
  classification system): use **INSTRUMENT mode** from methodology.md
- If the first argument is `redteam`: use **RED TEAM mode** from methodology.md

If unclear, ask the user which mode to use.

## Execute

Follow the procedure defined in `methodology.md` for the selected mode.
Apply all axiom directives from `constitution.md` throughout.
Apply all integrity constraints (IC-1, IC-2, IC-3) from `constitution.md`.
Use the taxonomy layers from `taxonomy.md` as your analytical checklist.
Cross-reference `patterns.md` at every step where the methodology calls for it.

## Integrity constraints (non-negotiable)

- **IC-1 (Falsifiability)**: If evidence challenges an axiom, flag it.
  Do not suppress it. Record in `evidence/` with `RELATIONSHIP: challenges`.
- **IC-2 (Null case)**: In ANALYZE mode step 5 (INVERT), you MUST consider
  the non-power explanation. If it is equally plausible, say so.
- **IC-3 (Red team)**: In RED TEAM mode, apply the framework to itself
  with full honesty. The framework's legitimacy depends on this.

## If the material is a URL

Try these strategies in order until content is obtained:

1. **WebFetch** (try first — fastest, handles simple pages):
   Use WebFetch to retrieve and summarize the content.

2. **fetch-article.py** (if WebFetch fails or returns unusable content):
   Run via Bash: `python3 tools/fetch-article.py <url>`
   This uses browser-like headers and extracts content from JSON-LD,
   meta tags, and paragraph elements. Works on most news sites.

3. **WebSearch** (if direct fetching fails entirely):
   Search for the article title or URL to find the content
   reproduced or summarized on other sites.

4. **Ask the user** (last resort):
   If all automated methods fail, ask the user to paste the
   article content directly.

## If the material is a book or large work

The user may provide the work inline, reference it by name, or provide
excerpts. If referencing by name, use your training knowledge of the work.
If the user wants analysis of a specific edition or passage, ask them to
provide the text.

## Output

### For ANALYZE mode:
Produce the structured output defined in methodology.md for each step.
After the final step, produce a summary section:

```
## Summary
MATERIAL: [what was analyzed]
PRIMARY LAYERS: [dominant taxonomy layers]
KEY MECHANISMS: [most significant mechanisms identified]
KEY FINDING: [single most important insight — 1-2 sentences]
CONFIDENCE: HIGH / MEDIUM / LOW
NULL CASE CONSIDERED: [yes/no — was the non-power explanation evaluated?]
FRAMEWORK UPDATES: [any additions to patterns.md, evidence/, or axiom refinements]
```

If the analysis produces framework updates, offer to write them to the
appropriate files (patterns.md, evidence/, etc.).

### For EXTRACT mode:
Produce the output defined in methodology.md and offer to write the
results to a new file in `principles/`.

### For INSTRUMENT mode:
Produce the structured output defined in the INSTRUMENT mode section of
methodology.md. If the verdict is CREATE or PROPOSE, offer to write the
instrument file to `instruments/`. If PROPOSE, clearly mark the gaps and
suggest sources to fill them.

### For RED TEAM mode:
Produce the output defined in the RED TEAM mode section of methodology.md
and offer to write the results to `evidence/`.

## Tone

Be direct and specific. Name actors, mechanisms, and layers explicitly.
Distinguish observation from inference. Mark confidence levels.
Do not hedge excessively — this framework exists to make things visible.
But do not overreach — the integrity constraints exist to keep the
framework honest.
