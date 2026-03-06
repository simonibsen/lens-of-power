# Lens of Power

An interpretive framework for studying how power and control operate across
layers of society — from language and narrative, through economics and law,
to surveillance and physical force — and understanding how these layers
reinforce each other.

This is a living analytical system. It accumulates knowledge over time
as works are studied and current events are analyzed. It is designed to
be used by both humans and LLMs.

> [!TIP]
> **Quick start**: Navigate to this directory and use the `/lop` skill:
> ```
> /lop read [article, event, policy, or URL]      — understand through the lens
> /lop analyze [article, event, policy, or URL]    — full production analysis
> /lop extract [book, film, theory, reference source, or catalog]
> /lop redteam                                     — turn the framework on itself
> /lop suggest                                     — framework health diagnostic
> ```
> Works with Claude Code. For other LLMs or manual use, load `constitution.md`,
> `taxonomy.md`, `methodology.md`, and `patterns.md` as context, then follow the
> procedure in `methodology.md`.

## Viewer

![Viewer dashboard](docs/viewer-dashboard.png)

The framework includes an interactive viewer that visualizes the entire
knowledge base and the connections between items.

```
open viewer.html
```

The viewer has three top-level nav items: **Dashboard** (landing page with
recent analyses, works studied, layer coverage), **Gap Analysis** (framework
health metrics and blind spots), and a **Visualizations** dropdown (Force
Graph, Layer Deep Dive, Corroboration Matrix, Timeline, Layer Flow,
Principle Lineage). Clicking any item in the sidebar opens a detail view.

## Table of contents

- [What this is for](#what-this-is-for)
- [Core concepts](#core-concepts) — axiom, layer, principle, pattern, circumvention, instrument, evidence, analysis
- [How to use it](#how-to-use-it)
- [Working with Claude](#working-with-claude) — steering, session flow, mid-session direction
- [The five modes](#the-five-modes)
  - [Read](#lop-read--understand-material-through-the-lens) — concise prose analysis
  - [Analyze](#lop-analyze--analyze-new-material) — full 7-step analysis with briefing output
  - [Extract](#lop-extract--study-a-source-for-principles-and-instruments) — study a source for principles and instruments
  - [Red team](#lop-redteam--turn-the-framework-on-itself) — turn the framework on itself
  - [Suggest](#lop-suggest--framework-health-diagnostic) — framework health diagnostic
- [How the framework grows](#how-the-framework-grows)
- [Structure](#structure) — directory layout
- [Integrity constraints](#integrity-constraints) — IC-1 through IC-5
- [Architecture and design patterns](#architecture-and-design-patterns)

## What this is for

The Lens of Power is a lens, not a theory. It does not generate original
insight about how power works — the scholars it draws from are the source
of insight. What the framework does is make their observations *available
at the moment of analysis*: when you read a policy document, the
principles Machiavelli articulated about appearance and reality are loaded
alongside Scott's observations about everyday resistance and Zuboff's
account of surveillance capitalism. The framework is the filing system
and the checklist — it organizes other people's hard-won observations so
they can be applied to new material in structured, transparent analysis.

The value is in cross-referencing across disciplines. A mechanism
described by Orwell in fiction, confirmed by Fanon in revolutionary
practice, and documented by Piketty in economic data is more than an
academic exercise — it is a structural pattern that can be recognized
when it appears in tomorrow's news. No single author could see all of
that; the framework holds their observations together.

The integrity constraints exist because a structured analytical tool that
always confirms its priors is worse than no tool at all. Every axiom has
a falsification condition. Every analysis must consider the non-power
explanation. The framework is periodically turned on itself. These are
not decorative — they are what distinguish an analytical tool from an
ideology.

Most exercises of power depend on not being seen clearly. Policy is
presented in terms of its stated purpose rather than its function.
Economic structures are presented as natural rather than constructed.
Language is shaped to make certain questions difficult to ask. The
framework provides a structured method for seeing through these layers.
It is useful for:

- **Analyzing current events**: News coverage, political speeches, policy
  announcements, corporate communications. The framework strips rhetoric
  to expose underlying mechanisms and identifies which layers of power
  are active, which are absent from discussion, and who benefits from the
  framing.
- **Studying foundational works**: Books, films, theories, and historical
  accounts that describe how power operates. The framework extracts
  generalizable principles and adds them to its knowledge base, making
  each subsequent analysis richer.
- **Building analytical tools**: Reference material (taxonomies of logical
  fallacies, catalogs of propaganda techniques, classification systems)
  can be evaluated and imported as instruments — reusable tools applied
  during analysis.
- **Detecting patterns across domains**: The framework's highest-value
  output is the identification of recurring structures of power that
  appear across different eras, cultures, and political systems. A
  mechanism observed in Orwell, confirmed in Machiavelli, and inverted
  by Fanon is more than an academic exercise — it is a pattern that can
  be recognized in tomorrow's news.

The framework includes structural safeguards against becoming a closed
ideological system: every axiom has a falsification condition, every
analysis must consider the non-power explanation, and the framework is
periodically turned on itself through red team reviews.

## Core concepts

The framework is built from eight distinct types of knowledge. Each has a
specific role, a distinct lifecycle, and a different relationship to truth.
The decomposition follows a functional principle: each concept exists
because merging it with another would lose a distinction the framework
depends on.

- **Axiom vs. pattern**: Axioms are premises — they guide what to look
  for. Patterns are findings — they emerged from looking. Axioms have
  falsification conditions; patterns have corroboration levels. The
  framework needs both because the questions it asks (axioms) must be
  separable from the answers it finds (patterns).
- **Principle vs. pattern**: A principle is source-bound ("Machiavelli
  observed X"). A pattern is source-independent ("X recurs across five
  independent sources"). The promotion path from principle to pattern
  tracks how knowledge matures — collapsing them would lose the
  distinction between a single observation and a confirmed regularity.
- **Instrument vs. principle**: Principles describe what power does.
  Instruments describe how to detect what power does. A taxonomy of
  propaganda techniques is not a finding about power — it is a tool
  applied during analysis. The distinction matters because instruments
  are procedural (invoked at specific methodology steps) while
  principles are referential (compared against during analysis).
- **Evidence vs. analysis**: Evidence is atomic (a fact, a data point,
  a case). Analysis is composite (the structured output of applying the
  full methodology). Evidence can directly challenge an axiom; analyses
  produce findings that may generate evidence. They have different
  lifecycles — evidence is permanent; analyses are snapshots.
- **Layer**: The domain model. Without layers as a first-class concept,
  the multi-domain analysis that is the framework's core value has no
  structure. Layers are relatively stable compared to the other concepts;
  they define where to look rather than what was found.

The eight types: **axiom** (what to look for), **layer** (where to look),
**principle** (what was found in one source), **pattern** (what recurs across
sources), **circumvention** (what has been observed to push back),
**instrument** (a reusable detection tool), **evidence** (ground truth),
and **analysis** (the output of applying the framework).

### Axiom

A foundational assumption about how power operates. Axioms are the
framework's starting premises — they guide what to look for during
analysis. Each axiom has a **directive** (a question the analyst must ask)
and a **falsification condition** (what evidence would disprove it). Axioms
are not permanent truths; they are the best current model, subject to
revision when evidence warrants it.

There are currently 10 axioms. They live in `constitution.md`.

*Example*: Axiom 3 — "Power is most effective when its contingency is
invisible." Directive: ask what is being presented as natural or inevitable.
Falsification: a system where mechanism, contingency, and capacity to act
are all visible yet the system remains stable without escalating coercion.

### Layer

One of six domains through which power operates simultaneously. Layers are
the framework's **analytical checklist** — every analysis maps which layers
are active, how they interact, and which are conspicuously absent from the
material.

The six layers are: Thought & Narrative, Economic, Legal & Regulatory,
Institutional, Surveillance & Information, Physical & Coercive. They are
defined in `taxonomy.md`.

*Example*: A policy that restricts protest may operate at the Legal &
Regulatory layer (criminalization), the Physical & Coercive layer
(police enforcement), and the Thought & Narrative layer (framing
protesters as threats to public order) — simultaneously.

### Principle

A generalizable truth about how power operates, extracted from a specific
source. A principle states: *this mechanism produces this effect because of
this reason*. Principles are more specific than axioms (they describe
particular mechanisms rather than general properties of power) and more
source-bound than patterns (they may be observed in only one work).

Principles are tagged with taxonomy layers, the source they come from,
and their relationship to existing axioms (confirms, refines, or
contradicts). They live in `principles/`.

*Example*: Machiavelli P5 — "Authority grounded in fear is more durable
than authority grounded in affection, because fear is maintained by the
ruler while affection is controlled by the subject."

**Relationship to patterns**: When a principle is independently confirmed
across multiple sources from different eras or perspectives, it may be
promoted to a pattern.

### Pattern

A recurring structure of power observed across multiple independent
sources, domains, eras, or contexts. Patterns are the framework's
**highest-value output** — they describe mechanisms that repeat despite
different surface forms. The same structural dynamic appearing in Orwell's
fiction, Machiavelli's political theory, and Scott's ethnography is not
a coincidence; it is a pattern.

Patterns have corroboration levels: PRELIMINARY (observed in one context;
may not generalize), SUPPORTED (confirmed across meaningfully independent
contexts), ESTABLISHED (confirmed across multiple independent contexts
with no unresolved counter-evidence). Ratings are qualitative — justified
by the independence and diversity of confirming sources, not by counting
to a threshold. They live in `patterns.md`.

*Example*: The Middle Stratum Trap — "The middle tier of a power hierarchy
is the most heavily controlled because it is the most capable of organizing
resistance, and its marginal privilege prevents downward solidarity."
Observed in Orwell (Outer Party vs. Proles), Machiavelli (the nobles as
the dangerous middle), and Fanon (the national bourgeoisie as relay class).
ESTABLISHED corroboration.

**Relationship to principles**: Patterns emerge from principles. A
principle observed in one source is a finding. The same structural dynamic
confirmed across three independent sources becomes a pattern.

### Circumvention

An observed response to power concentration, documented across the corpus.
Circumventions catalog what has been seen to push back against specific
patterns — under what conditions, with what outcomes, and how power systems
responded. They are the framework's counterforce record: without them, the
framework would diagnose how power operates but remain silent on what has
been observed to contest it.

Circumventions use observational language throughout: "has been observed to,"
"may," "appeared to." They are descriptive, not prescriptive — the framework
records what has happened, not what should be pursued.

Each circumvention type has fields for which layers it operates on, which
patterns it counteracts, its mechanism, failure modes, outcome range, and
documented power responses. They live in `circumventions.md` (compact
reference) and `circumventions-detail.md` (full evidence trails).

*Example*: Everyday Resistance — "Foot-dragging, feigned ignorance,
pilfering, false compliance, gossip, anonymous sabotage, and other 'weapons
of the weak' have been observed to constitute a continuous, low-visibility
terrain of power negotiation." Counteracts the Compliance Gradient and the
Hidden Transcript. Observed in Scott and Cobb. Outcome range: continuous
negotiation of domination terms documented, but structural transformation
through everyday resistance alone not observed.

**Relationship to patterns**: Circumventions are linked to the patterns they
have been observed to counteract. A pattern's CIRCUMVENTIONS field lists
which types have been documented as responses to that mechanism.

### Instrument

A reusable analytical tool imported from an external source and annotated
with **power-function** descriptions specific to this framework. Instruments
are applied during specific methodology steps to detect mechanisms in
material being analyzed. Every analysis lists which instruments were applied
and what they found.

What distinguishes an instrument from a generic reference document is the
power function field — documenting how each item (a logical fallacy, a
propaganda technique, a control mechanism) functions specifically as a
mechanism of power. They live in `instruments/`.

*Example*: `logical-fallacies.md` — 38 fallacies organized not by formal
classification but by power function: legitimation, deflection, constraint,
emotional override, evidentiary manipulation, burden manipulation. Each
fallacy is annotated with how it operates as a mechanism of control.

**Relationship to analysis**: Instruments are invoked during analysis steps
and listed in the analytical apparatus. Their usage across analyses reveals
which tools are relied on most (and which are neglected — a potential blind
spot).

### Evidence

A concrete fact, data point, documented case, quote, or observation that
grounds the framework in reality. Evidence is **not interpretation** — it
is raw material that supports, challenges, or illustrates axioms and
patterns. Each entry is tagged with the axioms and patterns it relates to
and with its relationship to them (supports / challenges / illustrates).

Evidence lives in `evidence/`.

*Example*: A documented case of a government program named for the opposite
of its function, tagged as supporting Axiom 7 (stated purpose vs. function)
and the Inversion of Stated Purpose pattern.

**Relationship to axioms**: Evidence that challenges an axiom is the most
valuable kind — it tests whether the framework's assumptions hold. IC-1
requires that challenging evidence is never suppressed.

### Analysis

The output of applying the ANALYZE mode to new material. An analysis
consists of **structured working** (the 7 methodology steps) followed by a
**briefing** (human-readable findings with full provenance). Analyses are
snapshots — they capture what was known at a specific point in time and are
never retroactively modified.

Analyses produce **findings** — discrete, tagged conclusions that may
generate new evidence entries, confirm or challenge existing patterns, or
suggest axiom refinements. They live in `analyses/`.

### How the concepts relate

```
Sources ──extract──> Principles ──confirmed across sources──> Patterns
                         │                                        │
                         └──── both tested against ───────────> Axioms
                                                                  │
Evidence ──supports/challenges─────────────────────────────────────┘

Circumventions ──counteract──> Patterns
       │
       └──observed in──> Principles, Analyses

Instruments ──applied during──> Analyses ──produce──> Findings
                                   │                      │
                                   │                      ├──> new Evidence
                                   │                      ├──> new/updated Patterns
                                   │                      └──> Axiom refinements
                                   │
                                   └──listed in──> Analytical Apparatus
```

## How to use it

### With Claude Code

Navigate to this directory and use the `/lop` skill:

```
/lop read [article, event, policy, or URL]
/lop analyze [article, event, policy, or URL]
/lop extract [book, film, theory, reference source, or catalog]
/lop redteam
/lop suggest
```

### With another LLM or manually

Load these files as context:

1. `constitution.md` — axioms and integrity constraints
2. `taxonomy.md` — the six layers of power
3. `methodology.md` — the analytical procedure
4. `patterns.md` — compact pattern definitions
5. `circumventions.md` — observed responses to power concentration
6. `principles/INDEX.md` — compact principles lookup table

Load `patterns-detail.md`, `circumventions-detail.md`, and individual
`principles/*.md` files only when deeper comparison is needed. Then follow the procedure in `methodology.md`
for your chosen mode.

## Working with Claude

The `/lop` skill invokes structured modes, but the invocation itself is
conversational. You can direct Claude to emphasize specific layers,
apply specific instruments, draw comparisons, or ask particular questions
— all in natural language alongside the mode keyword.

### Steering with natural language

```
/lop analyze https://example.com/article — focus on the propaganda elements
/lop analyze [paste policy text] — what's happening at the economic layer?
/lop extract The Prince — compare with Scott on resistance from below
/lop analyze this speech — what's missing? who isn't mentioned?
```

The mode determines the procedure. The natural-language direction
determines where within that procedure to push hardest, what comparisons
to draw, and what questions to prioritize.

### What a session looks like

**Read session**: You provide material (a URL, pasted text, or a
description of an event). Claude applies the full framework context —
axioms, layers, patterns, principles — and produces a concise prose
analysis directly in the conversation. No structured steps, no file
output, no framework update proposals. You can follow up with questions,
push on the null case, or ask Claude to go deeper on a specific layer.
If the material turns out to warrant the full production pipeline, you
can follow up with `/lop analyze` on the same material.

**Analysis session**: You provide material (a URL, pasted text, or a
description of an event). Claude runs the 7-step analysis procedure,
producing structured working followed by a briefing. You can intervene at
any step — redirect emphasis, challenge a claim level, or ask Claude to
apply a specific instrument. When the analysis is complete, Claude
proposes framework updates (new evidence entries, pattern updates, axiom
refinements). You approve, revise, or reject each proposal. The analysis
and any updates are committed on a dedicated branch with full provenance.

**Extraction session**: You name a source (a book, film, theory, or
reference work). Claude surveys it for principles and instruments,
evaluating what the source genuinely offers rather than forcing output it
doesn't support. You refine the framing of proposed principles, discuss
generalizability, and decide what merits inclusion. Instruments are
annotated with power-function descriptions before being committed.

**Comparative analysis**: You provide two or more sources covering the
same event or topic — different outlets, different eras, different
positions in the power relationship. The framework analyzes each and then
reveals what each makes visible and invisible, where their framings
converge and diverge, and what structural dynamics only become apparent
in the comparison.

**Suggest session**: You run `/lop suggest` with no arguments. Claude
scans the entire framework — analyses, evidence, patterns, sources,
instruments — and produces a health report with prioritized
recommendations for what to analyze, extract, or red team next. This is
a planning tool: it identifies gaps (underrepresented layers, domains,
positions), flags when adversarial inputs or red teams are overdue, and
suggests specific material that would strengthen the framework.

### What you can ask mid-session

The process is interactive throughout. At any point during a session you
can:

- **Go deeper**: "Expand on finding 3 — what's the historical precedent?"
- **Compare**: "How does this relate to what Fanon says about the national
  bourgeoisie?"
- **Challenge**: "I think finding 5 is speculative, not inferred — the
  evidence doesn't support that claim level."
- **Apply an instrument**: "Run the propaganda typology on the second
  paragraph."
- **Push on the null case**: "The null explanation feels too weak here —
  make the strongest version of it."
- **Redirect**: "Skip the economic layer, this is primarily operating at
  thought and narrative."

Claude will adjust the analysis in response. The integrity constraints
still apply — IC-2 cannot be skipped, IC-5 is always active — but
within those constraints, the analytical emphasis is yours to direct.

## The five modes

### `/lop read` — Understand material through the lens

**Input**: An article, speech, policy document, event, claim, or URL.

**What it does**: Applies the full framework — axioms, layers, patterns,
principles, instruments — to the material, but produces a concise prose
analysis rather than the full structured pipeline. The output reads like
an analytical essay: it identifies which layers are active, names the
patterns at work, notes what is absent, and considers the null case. IC-2
and IC-5 are not optional.

**What it does not do**: No structured step-by-step working, no numbered
findings, no briefing format, no evidence entries, no pattern updates, no
framework update proposals. Does not write to file unless asked.

**When to use read vs. analyze**: Use `read` when the goal is to
*understand* something through the lens — to see which layers are active,
which patterns appear, and what is absent. Use `analyze` when the goal is
to *produce a formal analysis* for the knowledge base — structured working,
briefing, evidence entries, pattern updates, and full provenance tracking.
The analytical depth is comparable; the output format and production
overhead differ.

### `/lop analyze` — Analyze new material

**Input**: An article, speech, policy document, event, claim, or URL.

**Depth levels**:
- *Quick pass* (steps 1, 3, 7): Initial screening. Is this worth deeper
  analysis?
- *Full pass* (all 7 steps): Standard analysis.
- *Deep pass* (all 7 steps + written briefing): For material of high
  significance.

#### The 7-step analysis process

**Step 1: DECOMPOSE** — Strip the material to its bare claims. Remove
rhetoric, emotional framing, and narrative structure. Separate what is
stated as fact from what is opinion or implied. Identify the emotional
register — what feeling is being engineered? The goal is to see the
signal beneath the packaging.

**Step 2: SOURCE** — Identify who produced this material and what their
incentives are. Apply the positional lens instrument to determine where
the source sits in the power relationship (ruler, everyday governed,
revolutionary, intermediary, or external observer). Ask: what would this
source *not* say, given their position and incentives? Check for logical
fallacies in how the source frames its claims.

**Step 3: LOCATE** — Position the material relative to the framework's
existing knowledge. Map which taxonomy layers are active and how they
interact. Cross-reference against known principles and patterns. Identify
what the material confirms, contradicts, or extends.

**Step 4: CONNECT** — Find non-obvious connections to other domains, eras,
or works. What historical parallel exists? What principle from `principles/`
does this instantiate in a new context? This step is where the framework's
accumulated knowledge produces its highest value — a pattern recognized
across four independent sources is more revealing than any single analysis.

**Step 5: INVERT** — Test the analysis by considering the opposite and the
null case. What would a defender of this system say? What is the strongest
version of their argument? Then, as required by IC-2: what would this look
like if power dynamics were *not* the explanation? Consider incompetence,
accident, inertia, genuine good faith. If the null explanation fits the
evidence equally well, say so. The framework's credibility depends on this
honesty.

**Step 6: ABSENT** — Identify what is conspicuously missing. What question
does the material not answer? Whose perspective is excluded? What data is
not provided? Apply the positional lens to identify which positions in the
power relationship are absent. Apply IC-5: what might the LLM be unable to
see because of its own training biases?

**Step 7: SO-WHAT** — Determine implications. If this analysis is correct,
what follows? What should be monitored? What does this add to the
framework? Apply Axiom 10: what becomes visible now that was hidden before?

#### The briefing

After the structured working, a deep-pass analysis produces a **briefing**
— a human-readable document in professional language. The briefing uses a
hybrid format:

- **Header**: Key finding (1-2 sentences), source position, a
  who-benefits/who-bears-cost table, and what is absent. A reader can stop
  here and have the essential insight.
- **Findings list**: Numbered, discrete findings. Each is tagged with
  taxonomy layer and evidentiary basis (observed/inferred/speculative).
  Each stands alone and is cross-referenceable from other analyses.
- **Analytical apparatus**: Full provenance — every instrument applied and
  what it contributed, every principle referenced, every pattern matched
  (and optionally, patterns considered but not matched). This makes the
  analytical process transparent and auditable.
- **Null case**: The non-power explanation and its plausibility.
- **Watch list**: Threads to monitor going forward.

### `/lop extract` — Study a source for principles and instruments

**Input**: Any source worth studying — a book, film, theory, historical
account, reference catalog, taxonomy, checklist, or classification system
(by name, inline text, or excerpts).

**What it does**: Surveys the source and evaluates what it offers. Not
every source yields the same things:

- A political treatise may yield **principles** (generalizable truths about
  how power operates) but no instruments.
- A reference catalog may yield an **instrument** (a reusable analytical
  tool) but no principles.
- A rich work may yield **both** — Fanon's *Wretched of the Earth* produced
  9 principles and 2 instrument proposals.
- Some sources may yield **neither**, and that is a valid outcome worth
  recording.

The procedure does not force output the source does not support. It
evaluates what is there and produces only what is genuinely valuable.

**For principles**: Each is tagged with taxonomy layers, mechanism,
evidence, and framework status (confirms/refines/contradicts existing
axioms). Principles are written to `principles/`.

**For instruments**: Each is evaluated for relevance, structured with
power-function annotations on every item, and written to `instruments/`.
What distinguishes a Lens of Power instrument from a generic reference
document is the **power function** field — documenting how each entry
(a logical fallacy, a propaganda technique, a control mechanism) functions
specifically as a mechanism of power.

Each extraction strengthens the framework. A pattern observed in one source
is tentative; the same pattern confirmed across three independent sources
from different eras and perspectives becomes a high-confidence structural
finding.

### `/lop redteam` — Turn the framework on itself

**Input**: The framework itself.

**What it does**: Examines the framework for confirmation bias,
unfalsifiability, and self-reinforcing patterns. Turns every axiom
directive inward. Checks the evidence base for imbalance. Assesses
whether the framework is revealing or merely confirming.

**Output**: A framework health assessment with confirmation bias risk
rating, list of axioms never challenged, most recent surprising result,
and recommended adjustments.

> [!CAUTION]
> This mode is required by IC-3 and should be invoked after every 5-10
> analyses, or whenever the framework is producing suspiciously consistent
> results. Certainty is the signal that a red team is overdue.

### `/lop suggest` — Framework health diagnostic

**Input**: None — scans the framework itself.

**What it does**: Reads `analyses/INDEX.md`, scans `evidence/`,
`patterns.md`, `principles/INDEX.md`, `sources/`, and `instruments/` to
assess the current state of the framework. Checks for clustering by
domain, layer, or source type. Evaluates adversarial input ratio, null
case distribution, evidence balance, and red team timing. Searches the
web for source availability when recommending material.

**Output**: A structured health report with prioritized recommendations
for what to analyze, extract, or red team next. Categories include: gap
closure (underrepresented layers, domains, or positions), adversarial
inputs (material likely to produce null-case-accepted results), red team
timing, source diversification, and pattern corroboration opportunities.

This mode is read-only — it does not write files, does not require a
working branch, and does not modify the framework. It is a diagnostic
that helps the user decide what to do next.

## How the framework grows

> [!NOTE]
> The framework is designed to accumulate knowledge over time. Each
> extraction, analysis, or red team review may produce new principles,
> evidence, patterns, or axiom refinements. The git history records every
> structural change with its rationale.

1. **Extractions** add principles to `principles/`. Each principle is
   tagged with taxonomy layers and cross-referenced against axioms and
   patterns.
2. **Analyses** test principles and patterns against new material. When
   a pattern appears in a new context, its confidence increases. When
   evidence challenges an axiom, it is recorded. Analyses also document
   circumventions — resistance mechanisms observed in the material.
3. **Instruments** add reusable analytical tools. Each instrument is
   invoked during specific methodology steps and listed in the analytical
   apparatus of every analysis that uses it.
4. **Patterns** are promoted as evidence accumulates. A pattern observed
   in one source is PRELIMINARY. Confirmation across meaningfully
   independent contexts warrants SUPPORTED or ESTABLISHED.
5. **Circumventions** accumulate as the corpus documents responses to
   power concentration. Each type tracks its outcome range — what has
   been observed to succeed, fail, or be captured — and is linked to
   the patterns it counteracts.
6. **Red team reviews** prevent the framework from calcifying. They check
   for confirmation bias, test falsifiability, and recommend adjustments.

## Structure

```
lens-of-power/
├── constitution.md          Foundational axioms (10) and integrity constraints (IC-1 through IC-5)
├── taxonomy.md              The six layers of power and their mechanisms
├── methodology.md           Analytical procedures and output formats (5 modes)
├── patterns.md              Compact pattern definitions (always loaded)
├── patterns-detail.md       Full evidence trails per pattern (loaded for audits)
├── circumventions.md        Observed responses to power concentration (always loaded)
├── circumventions-detail.md Full evidence trails per circumvention (loaded for audits)
├── instruments/             Imported analytical tools (7 instruments)
│   ├── circumvention-typology.md  Detection guide for observed responses to power
│   ├── control-hierarchy.md   5-level escalation ladder for control ambition
│   ├── institutional-capture-playbook.md  Multi-stage capture detection (Powell/Whitehouse/Ziklag/P2025)
│   ├── logical-fallacies.md   38 fallacies organized by power function
│   ├── newspeak-checklist.md  Detecting language as an instrument of control
│   ├── positional-lens.md    Identifying source position in power relationships
│   └── propaganda-typology.md 5-axis propaganda classification (Ellul + Stanley)
├── principles/              Extracted from specific works (23 sources)
│   ├── INDEX.md               Compact lookup table (always loaded)
│   ├── orwell-1984.md         8 principles from Nineteen Eighty-Four
│   ├── machiavelli-the-prince.md  7 principles from The Prince
│   ├── scott-weapons-of-the-weak.md  12 principles from Weapons of the Weak
│   ├── fanon-wretched-of-the-earth.md  9 principles from The Wretched of the Earth
│   ├── zuboff-age-of-surveillance-capitalism.md  10 principles from The Age of Surveillance Capitalism
│   ├── snyder-on-tyranny.md  7 principles from On Tyranny
│   ├── piketty-capital-in-the-twenty-first-century.md  8 principles from Capital
│   ├── scheidel-the-great-leveler.md  5 principles from The Great Leveler
│   ├── winters-oligarchy.md  5 principles from Oligarchy
│   ├── hartmann-hidden-history-american-oligarchy.md  4 principles from Hidden History
│   ├── graeber-debt-the-first-5000-years.md  7 principles from Debt
│   ├── powell-memo.md          4 principles from the Powell Memo (1971)
│   ├── whitehouse-the-scheme.md  4 principles from The Scheme
│   ├── cobb-most-southern-place-on-earth.md  6 principles from Most Southern Place
│   ├── stanley-how-propaganda-works.md  5 principles from How Propaganda Works
│   ├── hooks-aint-i-a-woman.md  6 principles from Ain't I a Woman?
│   ├── arendt-origins-of-totalitarianism.md  7 principles from Origins of Totalitarianism
│   ├── ellul-propaganda.md  5 principles from Propaganda
│   ├── mishra-western-model-broken.md  4 principles (Guardian 2014)
│   ├── guriev-rachinsky-role-of-oligarchs.md  4 principles (JEP 2005)
│   ├── alley-very-bad-people.md  5 principles from Very Bad People
│   ├── schimpfossl-oligarch-moralities-of-wealth.md  5 principles (EEPSC 2024)
│   └── project-2025-mandate-for-leadership.md  6 principles from Mandate for Leadership
├── sources/                 Source provenance records
│   └── INDEX.md               Compact lookup table
├── evidence/                Concrete facts, data, cases (16 entries)
│   └── README.md              Entry format specification
├── analyses/                Applied analyses of current material (24 analyses)
│   └── INDEX.md               Analysis registry (selection bias tracking)
└── tools/                   Utility scripts
    ├── build-viewer.py        Static viewer generator (produces viewer.html + viewer-data.js)
    └── fetch-article.py       URL content extraction (fallback for WebFetch)
```

## Integrity constraints

> [!IMPORTANT]
> The framework includes five structural safeguards against becoming a
> closed ideological system. These are non-negotiable — a framework for
> studying power that cannot examine its own power over the analyst is a
> failed instrument.

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
  the LLM's own training biases as a structural limitation. The LLM is
  a biased instrument — powerful but shaped by the same forces the
  framework examines.

## Architecture and design patterns

The framework's architecture borrows extensively from software engineering.
This is deliberate — the same structural principles that make software
systems reliable, maintainable, and auditable apply to analytical
frameworks. Understanding the architectural parallels clarifies why the
framework is structured the way it is and suggests where it might be
extended.

### Separation of concerns

Each file has a single, well-defined responsibility:

| File | Responsibility | Software analogue |
|------|---------------|-------------------|
| `constitution.md` | What to look for (axioms) | Configuration / constants |
| `taxonomy.md` | Domain model (the six layers) | Type definitions / schema |
| `methodology.md` | How to process (procedures) | Business logic / pipeline |
| `patterns.md` | Compact pattern definitions | Index / materialized view |
| `patterns-detail.md` | Full evidence trails | Database / knowledge store |
| `circumventions.md` | Observed counterforce types | Counterforce index |
| `circumventions-detail.md` | Full counterforce evidence | Counterforce store |
| `instruments/` | Pluggable detection tools | Plugin modules |
| `principles/` | Source-bound knowledge | Reference data |
| `evidence/` | Ground truth | Test fixtures / assertions |
| `analyses/` | Processed output | Logs / reports |

No file does two jobs. The constitution does not contain procedure. The
methodology does not contain findings. The taxonomy does not contain
evidence. This makes it possible to modify one component without
destabilizing the others — the same reason software separates concerns.

### Plugin architecture

Instruments are modular plugins. Each has a defined interface:

- **Name and role** (what the plugin does)
- **Source** (where it came from)
- **Taxonomy layers** (what domain it operates in)
- **Analytical use** (which pipeline steps invoke it)
- **Items** with a consistent schema (name, description, detection, power
  function)
- **Application instructions** (how to run the plugin)

New instruments can be added without modifying the methodology — they
register themselves by stating which steps should invoke them. Existing
instruments can be updated without affecting others. This is the Open/Closed
Principle: the analysis pipeline is open for extension (new instruments)
but closed for modification (adding an instrument does not require changing
the pipeline itself).

### Processing pipeline

The 7-step analysis is a linear processing pipeline with defined inputs
and outputs at each stage:

```
Material → DECOMPOSE → SOURCE → LOCATE → CONNECT → INVERT → ABSENT → SO-WHAT → Briefing
              ↓           ↓        ↓         ↓         ↓        ↓         ↓
           Claims     Position   Layers   Echoes    Null    Missing   Implications
                      Incentives Patterns  Links    case    voices    Watch list
```

Each step takes the material plus the output of previous steps and
produces structured output in a defined format. This is the Pipeline
pattern — data flows through a sequence of transformations, each adding
a layer of analysis. The structured output formats are the pipeline's
**contracts**: each step guarantees a specific output shape that
downstream steps can rely on.

### Schema / contract design

Every output type has a defined schema:

- **Principles**: PRINCIPLE / LAYERS / MECHANISM / EVIDENCE FROM WORK /
  GENERALIZES TO / FRAMEWORK STATUS / STATUS (observed/inferred/speculative)
- **Patterns**: LAYERS / STATEMENT / MECHANISM / OBSERVED IN / EVIDENCE /
  CORROBORATION (preliminary/supported/established) / CIRCUMVENTIONS
- **Circumventions**: LAYERS / COUNTERACTS / STATEMENT / OUTCOME RANGE /
  MECHANISM / FAILURE MODES / OBSERVED IN / POWER RESPONSE
- **Evidence entries**: DATE / SOURCE / SOURCE TYPE / AXIOMS / PATTERNS /
  LAYERS / RELATIONSHIP / CONTENT / SIGNIFICANCE
- **Findings**: LAYER / STATUS (observed/inferred/speculative)
- **Analytical apparatus**: INSTRUMENTS APPLIED / PRINCIPLES REFERENCED /
  PATTERNS MATCHED

These schemas serve the same function as API contracts or database schemas:
they ensure consistency across entries, enable cross-referencing, and make
automated or semi-automated processing possible. A pattern entry from 2026
has the same structure as one from 2030 — they can be compared, aggregated,
and queried.

### Observability and audit logging

The analytical apparatus section in every analysis is structured logging.
It records:

- Which instruments were applied and what they detected
- Which principles were referenced and how they applied
- Which patterns were matched and at what confidence
- Which patterns were considered but not matched

This serves three purposes. **Transparency**: a reader can see exactly what
shaped the analysis. **Auditability**: a red team review can assess whether
the right tools were applied and whether instrument selection introduced
bias. **Health monitoring**: aggregate instrument usage across analyses
reveals which tools are overused, which are neglected, and where blind
spots may exist.

### Test-driven development

The falsifiability table in `constitution.md` is a pre-defined test suite
for the axioms. Each axiom has a falsification condition stated in advance
— the evidence that would disprove it. This inverts the normal relationship
between theory and evidence: instead of looking for evidence that confirms
the axioms, the framework defines what *disconfirming* evidence would look
like and actively watches for it.

IC-2 (null case) extends this to every analysis: each analysis must test
itself against the simplest non-power explanation. This is the analytical
equivalent of writing tests before writing code — the failure condition is
defined before the analysis begins.

### Chaos engineering and red teaming

IC-3 requires periodically turning the framework on itself — examining it
for confirmation bias, unfalsifiability, and self-reinforcing patterns.
This is chaos engineering applied to an analytical system: deliberately
stress-testing the framework's assumptions to find weaknesses before they
compound.

> [!WARNING]
> The red team procedure applies the framework's own taxonomy to itself:
> Is the framework functioning as Thought & Narrative control (framing
> everything as power)? Has it become an Institutional authority (deferred
> to rather than used critically)? Is it producing Surveillance effects
> (making the analyst see control everywhere)?

### Two-scale rating system

The framework uses two distinct scales that measure different things:

- **Evidentiary basis** (observed / inferred / speculative) — how a claim
  is grounded in its source material. Applies to findings and individual
  principle claims. An observed claim is verifiable by another reader; a
  speculative one extends beyond direct evidence.
- **Corroboration** (preliminary / supported / established) — how widely
  a pattern has been confirmed across meaningfully independent contexts.
  Applies to patterns. Ratings are qualitative: justified by the
  independence and diversity of confirming sources (different eras,
  domains, positions in the power relationship), not by counting to a
  numeric threshold. A preliminary pattern is a hypothesis. An
  established pattern is a tool.

These are not decorative — they are metadata that determines how a
finding or pattern can be used. This is analogous to test coverage
metrics or reliability ratings in engineering: the system tracks not
just what it knows but how well it knows it.

### Version control as institutional memory

The git history records every structural change to the framework with a
description of what changed and why. IC-4 requires that axiom changes
name the axiom, describe the change, and cite the evidence that prompted
it. This is the same discipline applied to database migrations or API
versioning: the system maintains a complete, auditable record of its own
evolution.

### Summary of architectural parallels

| Framework component | Software pattern |
|---|---|
| Axioms with falsification conditions | Pre-defined test cases |
| Taxonomy layers | Domain model / type system |
| 7-step analysis pipeline | Processing pipeline with contracts |
| Instruments | Plugin architecture (Open/Closed) |
| Structured output schemas | API contracts / database schemas |
| Analytical apparatus | Structured audit logging / observability |
| Two-scale ratings (evidentiary basis + corroboration) | Reliability metrics / test coverage |
| IC-2 null case | Assertion testing per analysis |
| IC-3 red teaming | Chaos engineering / fault injection |
| IC-4 living document | Continuous integration / maintenance |
| IC-5 LLM bias disclosure | Dependency vulnerability scanning |
| Git history with rationale | Database migrations / changelog |

### Design principles

- **LLM-native**: All files are written in directive style with structured
  output formats, designed to be executed directly by an LLM
- **Portable**: The spec files work with any LLM or can be followed manually
- **Modular**: Instruments, principles, and evidence can be added without
  restructuring (Open/Closed Principle)
- **Transparent**: Every analysis lists its full analytical apparatus
  (observability)
- **Self-correcting**: Integrity constraints, falsifiability conditions,
  and red team reviews prevent the framework from becoming ideology
  (chaos engineering)
- **Contractual**: Every output type has a defined schema that enables
  cross-referencing and aggregation
- **Version-controlled**: The git history is the framework's memory
