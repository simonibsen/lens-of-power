---
name: lop
description: Apply the Lens of Power interpretive framework to read or analyze material for power dynamics, extract principles and instruments from a source, or red-team the framework itself.
argument-hint: <read|analyze|extract|redteam> [material, work, or source]
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
4. `patterns.md` — compact pattern definitions (ALWAYS load)
5. `principles/INDEX.md` — compact principles lookup table (ALWAYS load)

Load selectively as needed:
6. `patterns-detail.md` — full evidence trails for patterns (load for RED TEAM mode, pattern audits, or when checking specific pattern evidence)
7. `instruments/` — load any instruments relevant to the material
8. `principles/[source].md` — load full principles file only when deep comparison with a specific source is needed (the INDEX has enough for cross-referencing)
9. `evidence/` — scan for evidence relevant to the material

## Determine mode

Parse `$ARGUMENTS` to determine the mode:

- If the first argument is `read` or the user wants to understand material
  through the lens without full production output: use **READ mode** from
  methodology.md
- If the first argument is `analyze` or the user is providing current material
  (article, news, speech, policy, event): use **ANALYZE mode** from methodology.md
- If the first argument is `extract` or the user is providing a source to
  study (book, film, theory, historical account, reference page, list, catalog,
  classification system): use **EXTRACT mode** from methodology.md. The extract
  procedure evaluates what the source offers — principles, instruments, or
  both — and produces only what is genuinely valuable.
- If the first argument is `redteam`: use **RED TEAM mode** from methodology.md

If unclear, ask the user which mode to use.

## Branching check (before analytical work)

For modes that write to the repository (ANALYZE, EXTRACT, RED TEAM),
check the current git branch **before producing any analytical output**.
Run `git branch --show-current` and:

- **On main**: Stop. Ask the user to create and switch to a working
  branch. Do not proceed with the analysis until the branch is resolved.
- **Not on main**: Confirm with the user that writing to the current
  branch is intended, then proceed.

This check must happen early — after loading the framework and
determining the mode, but before triage or any analytical steps. The
user should not receive a full analysis and then be asked about branches.

READ mode is exempt (no file output by default).

## Execute

Follow the procedure defined in `methodology.md` for the selected mode.
Apply all axiom directives from `constitution.md` throughout.
Apply all integrity constraints (IC-1 through IC-5) from `constitution.md`.
Use the taxonomy layers from `taxonomy.md` as your analytical checklist.
Cross-reference `patterns.md` at every step where the methodology calls for it.

## Integrity constraints (non-negotiable)

- **IC-1 (Falsifiability)**: If evidence challenges an axiom, flag it.
  Do not suppress it. Record in `evidence/` with `RELATIONSHIP: challenges`.
- **IC-2 (Null case)**: In ANALYZE mode step 5 (INVERT), you MUST consider
  the non-power explanation. If it is equally plausible, say so.
- **IC-3 (Red team)**: In RED TEAM mode, apply the framework to itself
  with full honesty. The framework's legitimacy depends on this.
- **IC-5 (LLM bias)**: Flag when training data likely overrepresents a
  perspective. Name blind spots. Do not hedge to appear balanced when
  evidence is not balanced.

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

### For READ mode:
Produce the prose analysis defined in the READ mode procedure of methodology.md.
Output directly to the conversation — do not write to file unless the user asks.
No structured steps, no briefing format, no evidence entries, no framework
update proposals. IC-2 and IC-5 still apply. End with Framework references,
then an escalation recommendation (analyze / extract / none) with reasons,
as defined in methodology.md.

### For ANALYZE mode:
Produce the structured step-by-step output defined in methodology.md,
followed by the briefing document in the hybrid format (briefing header +
findings list + analytical apparatus). The briefing format is defined in
the "Analysis output format" section of methodology.md.

The analytical apparatus section is required — it lists every instrument,
principle, and pattern that shaped the analysis, with sources.

If the analysis produces framework updates, offer to write them to the
appropriate files (patterns.md, evidence/, etc.).

### For EXTRACT mode:
Produce the output defined in methodology.md. The extract procedure
evaluates the source for both principles and instruments:

- If principles are found, offer to write them to `principles/`
- If instruments are found, offer to write them to `instruments/`
- If both are found, produce both with cross-references
- If neither is found, document what was surveyed and why

### For RED TEAM mode:
Produce the output defined in the RED TEAM mode section of methodology.md
and offer to write the results to `evidence/`.

## Framework term references

In all human-readable output, follow the framework term reference
convention defined in the Output discipline section of methodology.md:
first occurrence gets **bold** with a parenthetical gloss; subsequent
occurrences get **bold** without gloss. Collect all framework term
links in a "Framework references" section at the end of the output.
Base URL: `https://github.com/simonibsen/lens-of-power/blob/main/`

## Tone

Be direct and specific. Name actors, mechanisms, and layers explicitly.
Distinguish observation from inference. Mark evidentiary basis and
corroboration levels per the output discipline in methodology.md.
Use professional language throughout.
Do not hedge excessively — this framework exists to make things visible.
But do not overreach — the integrity constraints exist to keep the
framework honest.
