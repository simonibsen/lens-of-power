# Methodology: Lens of Power

> Role: This document defines the analytical procedure. It is designed to
> be executed directly by an LLM or followed by a human analyst. When
> invoked, follow the steps in order and produce structured output.

---

## Modes of operation

Select a mode based on the task:

### READ mode
**Input**: A piece of new information (article, speech, policy, event, claim)
**Output**: Concise prose analysis drawing on the full framework context
**When to use**: Understanding material through the lens without producing the full structured pipeline

### ANALYZE mode
**Input**: A piece of new information (article, speech, policy, event, claim)
**Output**: Structured analysis revealing power dynamics, mechanisms, and connections
**When to use**: Processing current events, news, policy documents, arguments

### EXTRACT mode
**Input**: A source — body of work (book, film, theory, historical account)
or reference source (taxonomy, checklist, catalog of techniques)
**Output**: Principles, instruments, or both — whatever the source yields
**When to use**: Studying any source to build the framework's knowledge base.
The procedure evaluates what the source offers and produces only what is
genuinely valuable. Not every source yields both principles and instruments;
some yield neither.

### RED TEAM mode
**Input**: The framework itself
**Output**: Framework health assessment, confirmation bias check, falsifiability review
**When to use**: Periodically, or when the framework is producing suspiciously consistent results

### SUGGEST mode
**Input**: None — scans the framework itself
**Output**: Framework health diagnostic with prioritized recommendations
**When to use**: Proactively, to assess framework health and identify what to study, extract, or red-team next

---

## READ mode procedure

A lighter analytical mode for understanding material through the framework's
lens without producing the full structured pipeline.

**Input**: Same as ANALYZE — an article, speech, policy, event, claim, or URL.

**Output**: A concise prose analysis (1-3 pages) that reads like an analytical
essay. No structured step-by-step output, no briefing format, no evidence
entries, no framework update proposals.

**Does not produce**: Structured working steps, numbered findings, briefing
header, analytical apparatus section, evidence entries, or pattern/framework
updates. Does not write to file unless the user asks.

**Procedure**:

1. Load the framework context: `constitution.md`, `taxonomy.md`, `patterns.md`,
   `circumventions.md`, `principles/INDEX.md`. Load instruments only if they
   become relevant during the reading — do not load all instruments by default.

2. Read the material. Produce a prose analysis that:

   - Identifies which layers of power are active and how they interact
   - Names which patterns from `patterns.md` appear and why
   - Draws on principles from `principles/INDEX.md` where they illuminate
     the material
   - Notes what is absent — missing voices, unasked questions, layers that
     are structurally relevant but not addressed
   - Considers the null case (IC-2 is not optional, even in this lighter mode)
   - Flags IC-5 (LLM bias) where relevant

3. The output is prose, not structured fields. It reads like an analytical
   essay that draws on the framework's accumulated knowledge. Professional
   register. Claim discipline still applies — distinguish observed from
   inferred from speculative, using signal vocabulary rather than STATUS tags.

**Escalation recommendation**: The final section of every READ mode output
(after the Framework references) is a brief recommendation on whether the
material warrants `/lop analyze` or `/lop extract`, or neither. This
section always appears — it is not conditional. Format:

```
**Next step**: [analyze / extract / none recommended]
[1-3 sentences explaining why. Name the specific framework value that
would or would not result — e.g., evidence entries, pattern updates,
new corroboration for an existing pattern, principles or instruments
worth adding to the knowledge base. "None recommended" with reasons
is itself informative.]
```

The recommendation makes the option visible, the reasoning transparent,
and prevents ambiguity about whether escalation was considered.

**What READ mode is not**: It is not a summary or a reaction. It is the
framework's lens applied to material, producing genuine analytical insight —
just without the production overhead of structured steps, provenance tracking,
and framework updates. The analytical depth is comparable to ANALYZE; the
output format is lighter.

---

## Branching check

For any mode that writes to the repository (ANALYZE, EXTRACT, RED TEAM),
check the current git branch **at the start of the mode** — after triage
but before producing analytical output. Do not defer this check to the
moment of writing; the user should confirm the branch before the analyst
invests effort in the full procedure.

- **On main**: Stop. Ask the user to create and switch to a working
  branch before proceeding. Suggest a name based on the material (e.g.,
  `analysis/2026-03-03-source-topic`).
- **Not on main**: Confirm with the user that writing to the current
  branch is intended, then proceed with the analysis.

READ mode and SUGGEST mode do not write files and are exempt. READ mode
becomes subject to the branching check only if the user requests file output.

## Post-write viewer rebuild

After writing analysis or extraction files, rebuild and open the viewer:

```
python3 tools/build-viewer.py && open viewer.html
```

This is not optional — always run it after any file write. The viewer
shows how the new content connects to the existing knowledge base.

## Post-analysis gap recommendation

After an analysis or extraction is complete and all framework updates
are written, review the current state of the framework for gaps and
recommend what to study next. This step runs *after* the analysis is
finished — it must not influence the analytical process itself.

**Draw on**:
- Under-corroborated patterns (PRELIMINARY with few sources)
- Under-studied layers or layer pairs with no cross-layer items
- Source type concentration (too many of one kind of material)
- Missing perspectives identified by IC-5 during the analysis

**Output**: A brief recommendation (2-5 sentences) naming specific
topics, sources, or material types that would strengthen the framework's
weakest points. Prefer recommendations that would test the framework
(adversarial material, domains where the null case might win) over
those that would merely confirm it.

**Integrity note**: This recommendation is driven by framework gaps,
not by analytical findings. It must never appear before the analysis
is complete, and it must never cause the analyst to look harder for
patterns the framework needs corroborated. The analysis serves the
evidence; the recommendation serves the framework. These are separate
concerns.

---

## ANALYZE mode procedure

### Triage: determine depth

Before beginning, assess the material:

- **Quick pass** (steps 1, 3, 7 only): Use for initial screening. Is this worth deeper analysis?
- **Full pass** (all 7 steps): Standard analysis.
- **Deep pass** (all 7 steps + written synthesis): For material of high significance.

**Filename convention**: `YYYY-MM-DD-source-type-description.md`
where source is who published it and type is the format. Examples:
`2026-03-01-guardian-liveblog-us-israel-iran-war.md`,
`2026-04-15-usgov-pressrelease-sanctions-expansion.md`,
`2026-05-20-nyt-article-housing-policy-reform.md`.

When writing an analysis to `analyses/`, include:
- A **TIME** field (approximate UTC) recording when the material was
  captured. This is essential for live or evolving sources (live blogs,
  developing stories, social media threads) where the content changes
  over time. The analysis is a snapshot; the timestamp makes that explicit.
- A **SOURCE TYPE** field describing the structural type of the material.
  This is an observable property of the format, not a judgment about
  content or bias. Examples: live blog, news article, press release,
  government report, academic paper, speech transcript, corporate
  filing, social media thread, policy document, legislative text,
  editorial/opinion, leaked document. The source type helps the reader
  calibrate expectations — a press release and an investigative report
  are structurally different kinds of material. Bias assessment belongs
  in Step 2 (SOURCE), not here.
- A **SOURCE POSITION** field from the positional lens (Position 1-5).
  See `instruments/positional-lens.md`.
- A **FRAMEWORK STATE** field recording the framework's size at the time
  of analysis: pattern count, principle count, instrument count, and the
  git commit hash. This makes it immediately visible whether an analysis
  was written with a smaller or larger framework, without requiring git
  archaeology. Analyses written on parallel branches will show the same
  commit only if they share the same base — divergent states are visible
  by inspection.

The analysis file has two sections separated by a delimiter. The
human-readable analysis comes first; the analytical working that
produced it follows below. See "Analysis output format" for the
complete file structure.

**Narrative register**: The narrative describes structure and
observations. It does not argue a case, perform a reaction, or
encode the analyst's evaluations as descriptions. Specific rules:

- **Describe, do not evaluate.** Write "The live blog does not
  mention the school strike" rather than "The most consequential
  fact has been removed." The first is an observation; the second
  is the analyst's judgment about what is most consequential,
  presented as though it were a property of the material.
- **Do not editorialize.** Avoid constructions that express the
  analyst's attitude toward the material: "a masterpiece of
  deflection," "the facts are staggering," "an astonishing
  omission." If the finding is significant, the described
  structure will demonstrate that without the analyst saying so.
- **Avoid rhetorical devices.** No dramatic parallelism ("told
  them everything and helped them understand nothing"), no
  standalone emphasis words ("Zero."), no literary constructions
  designed to produce a reaction in the reader. These belong in
  opinion writing, not structural analysis.
- **Claim discipline applies.** The narrative is prose, but the
  claim discipline (observed / inferred / speculative) still
  governs it. Functional claims ("serves to," "functions as,"
  "is designed to") must be marked as inferred unless the source
  explicitly states intent. See the claim discipline section below.

The test: could a reader with different political commitments
accept the narrative as an accurate description of what the
analysis found, even if they disagree with the conclusions drawn
in the Implications section? If not, the narrative has crossed
from description into advocacy.

### Addenda convention

Analyses are snapshots. Do not rewrite an analysis with later knowledge
— this destroys the framework's ability to evaluate its own accuracy
and violates the honest-memory principle of IC-4.

When new information emerges that affects a prior analysis (verified
claims, revised casualty figures, new connections from later analyses),
append a dated addendum to the end of the file:

```
## Addenda

### YYYY-MM-DD ~HH:MM UTC
[What changed and why. Reference new evidence, analyses, or external
sources. Note any confidence level changes.]
See: [links to new evidence/ or analyses/ entries]
```

Each addendum gets its own date and timestamp. The original analysis
above remains untouched. This preserves the snapshot, keeps the
analysis useful as a living reference, and creates a visible trail of
how understanding evolved over time.

### Analysis index

Maintain `analyses/INDEX.md` as a registry of all completed analyses.
After each analysis, add an entry:

```
| Date | Material | Domain | Primary layers | Null case outcome |
|------|----------|--------|----------------|-------------------|
| YYYY-MM-DD | [short description] | [domain] | [layers] | rejected / plausible / accepted |
```

The index serves two functions:
1. **Selection bias detection**: During red team reviews (IC-3), review
   the index for clustering. If analyses concentrate in one domain,
   one set of layers, or consistently reject the null case, the
   framework is being fed a biased diet.
2. **Cross-referencing**: The CONNECT step can scan the index to
   identify prior analyses with structural parallels.

### Adversarial input

The framework must periodically be applied to material where the null
case is likely to win. This is not optional — it is the empirical
test of whether IC-2 functions or is decorative.

**Adversarial material includes**:
- A functional institution doing what it claims to do
- A policy that worked as intended for its stated beneficiaries
- A reform that succeeded without hidden costs
- An event best explained by incompetence, accident, or good faith
- Material from a domain the framework has not yet been applied to

**Frequency**: At least 1 in every 10 analyses should be adversarial.
If the framework cannot produce "the power explanation does not hold
here" as an honest conclusion, it is a confirmation machine regardless
of what the integrity constraints say.

The analysis index makes this trackable — if the "null case outcome"
column never reads "accepted" or "plausible," that is itself a finding
about the framework's health. The ratio should be tightened if the
accepted count drops back to zero over any 10-analysis window.

### Step 1: DECOMPOSE

Strip the material to its bare claims. Remove rhetoric, emotional framing,
and narrative structure.

**Do this**:
- List each factual claim or assertion separately
- Identify which claims are presented as fact vs. opinion vs. implied
- Note the emotional register (urgency, fear, reassurance, outrage)
- Separate the signal from the packaging

**Null case checkpoint (IC-2)**: Before proceeding to power-dynamics
mapping, state the strongest non-power explanation for this material in
1-3 sentences. What would this look like if explained by incompetence,
accident, inertia, path dependency, genuine good faith, or unintended
consequences? This must be done NOW — before the analytical momentum of
Steps 2-4 builds a power-dynamics case. Record it in the output; you
will revisit it in Step 5 (INVERT) to see if it survived.

**Output format**:
```
CLAIMS:
- [claim 1] (stated as: fact/opinion/implied)
- [claim 2] ...

FRAMING: [describe the rhetorical packaging]
EMOTIONAL REGISTER: [what feeling is being engineered]
INITIAL NULL CASE: [strongest non-power explanation, stated before analysis begins]
```

### Step 2: SOURCE

Identify who produced this material and what their incentives are.

**Do this**:
- Who is the author/speaker/institution?
- What are their incentives (financial, political, reputational)?
- What would they NOT say, given those incentives?
- Who funded, published, or amplified this?

**IC-5 check**: Does the LLM's training likely overrepresent this source's
perspective? If the source is institutional, mainstream, or Western, note
that the LLM may treat its framing as more credible than warranted. If
the source represents a marginalized, suppressed, or non-institutional
perspective, note that the LLM may underweight it.

**Invoke instruments**: Check `instruments/` for relevant analytical tools
(propaganda filters, logical fallacies, positional lens) and apply them here.
Apply `instruments/positional-lens.md` to identify which position in the
power relationship this source speaks from and what that position makes
visible and invisible.

**Output format**:
```
SOURCE: [who]
POSITION: [from positional-lens.md — ruler/everyday governed/revolutionary/intermediary/observer]
INCENTIVES: [what they gain from this message]
WOULD NOT SAY: [what their incentives prevent them from saying]
AMPLIFICATION: [who is spreading this and why]
```

### Step 3: LOCATE

Position this material relative to existing knowledge in the framework.

**Do this**:
- Does this confirm, contradict, or extend existing principles in `principles/`?
- Does this match known patterns in `patterns.md`?
- Which layers from `taxonomy.md` are active in the material?
- Which layers are *structurally relevant but absent from the source*?
  A layer is "active but absent" when the analyst can identify its
  operation through inference, context, or domain knowledge, but the
  source material does not mention or address it. This is an Axiom 8
  signal — the absence may be incidental (outside the source's scope)
  or significant (serving identifiable interests). Flag it either way;
  evaluate which in the ABSENT step.
- Map the layer interactions (use the interaction format from taxonomy.md)

**Output format**:
```
LAYERS ACTIVE: [list from taxonomy — layers visible in the material]
LAYERS ACTIVE BUT ABSENT FROM SOURCE: [layers the analyst identifies as
  structurally relevant but not addressed in the material, with brief
  reasoning for each]
LAYER INTERACTIONS:
  [Layer A] --[relationship]--> [Layer B]
CONFIRMS: [existing principles/patterns this supports]
CONTRADICTS: [existing principles/patterns this challenges]
EXTENDS: [new territory not yet covered]
```

### Step 4: CONNECT

Find non-obvious connections to other domains, eras, or works.

**Do this**:
- What does this echo from a completely different domain?
- What historical parallel exists?
- What principle from `principles/` does this instantiate in a new context?
- What would someone studying a different layer of power recognize here?
- Scan `analyses/` for prior analyses with structural parallels. If
  a prior analysis identified similar mechanisms, layers, or patterns,
  cite it explicitly. The framework's value compounds when analyses
  cross-reference each other rather than relying solely on the analyst's
  general knowledge.

**Output format**:
```
ECHOES: [connections to other domains, historical parallels]
PATTERN MATCH: [which known patterns from patterns.md appear here]
NEW PATTERN: [any new cross-cutting pattern this suggests]
```

### Step 5: INVERT

Test the analysis by considering the opposite and the null case.

**Do this**:
- What would the opposite claim look like? Is it plausible?
- What would a defender of this system say? What is the strongest
  version of their argument?
- What would you need to see to change your assessment?

**Null case (required by IC-2)**: Revisit the INITIAL NULL CASE stated
in Step 1. Has the analysis in Steps 2-4 weakened it, strengthened it,
or left it unchanged? If unchanged, the power explanation may not be
adding analytical value. Then ask: "What would this look like if power
dynamics were NOT the explanation?" Consider simpler accounts:
incompetence, accident, inertia, path dependency, genuine good faith,
unintended consequences. If the null explanation fits the evidence as
well as the power explanation, say so explicitly. Do not default to
the power explanation out of framework loyalty.

**IC-5 check (required)**: Ask: "Am I hedging this conclusion because the
evidence warrants caution, or because my alignment training makes me
reluctant to name power directly?" If the analysis points clearly at a
specific actor, institution, or system, name it. Do not soften findings
to appear balanced when the evidence is not balanced.

**Invoke instruments**: Check `instruments/cognitive-biases.md` (if available)
for biases that might be affecting this analysis.

**Output format**:
```
INVERSE CLAIM: [the opposite position]
STRONGEST DEFENSE: [steelman of the system/actor being analyzed]
NULL CASE: [the non-power explanation — incompetence, accident, inertia, good faith]
NULL CASE PLAUSIBILITY: HIGH / MEDIUM / LOW [with reasoning]
FALSIFIABLE BY: [what evidence would change this assessment]
LLM BIAS CHECK: [am I hedging due to evidence or due to alignment training?]
```

> If NULL CASE PLAUSIBILITY is HIGH, this is a significant finding. It
> means the power explanation is not clearly supported over simpler
> alternatives. State this honestly. The framework's value depends on
> distinguishing genuine power dynamics from pattern-matching noise.

### Step 6: ABSENT

Identify what is conspicuously missing.

**Do this**:
- What question does this material not answer that it should?
- Whose perspective or voice is absent?
- What data or evidence is not provided?
- What alternative was never presented as an option?

**IC-5 check (required)**: Ask: "What might I be unable to see because
of what is underrepresented in my training?" Specifically consider:
- Perspectives of the governed, surveilled, indebted, displaced, or
  marginalized that may be absent from both the material AND the LLM's
  training data — a double omission that makes the absence harder to detect
- Non-Western, non-institutional, or oral-tradition perspectives on
  the same topic
- Whether the "absent voices" identified above are limited to those
  the LLM's training makes visible — there may be further absences
  the LLM cannot name

**Invoke instruments**: Check `instruments/logical-fallacies.md` (if available)
for fallacies of omission, false dilemma, etc. Apply
`instruments/positional-lens.md` to identify which positions in the power
relationship are absent from the material and what those positions would
reveal if present.

**Output format**:
```
MISSING QUESTIONS: [questions the material should address but doesn't]
ABSENT VOICES: [whose perspective is excluded]
MISSING EVIDENCE: [data or proof not provided]
EXCLUDED ALTERNATIVES: [options never presented]
LLM BLIND SPOTS: [perspectives the LLM's training likely underrepresents on this topic]
```

### Step 7: SO-WHAT

Determine the implications and next actions.

**Do this**:
- If this analysis is correct, what follows?
- What should be watched, investigated, or acted on?
- What does this add to the framework? (new pattern, new principle,
  refinement of existing axiom)
- Apply Axiom 10: what becomes visible now that was hidden?
- Check `circumventions.md`: has any observed circumvention type been
  attempted, succeeded, failed, or been captured in this material?
  If so, note which type(s) and the outcome.

**Output format**:
```
IMPLICATIONS: [what follows from this analysis]
WATCH: [what to monitor going forward]
INVESTIGATE: [threads worth pulling]
FRAMEWORK UPDATE: [any additions to patterns.md or refinements to suggest]
CIRCUMVENTIONS: [any circumvention types observed — type, outcome, failure modes]
MADE VISIBLE: [what this analysis reveals that was previously hidden]
```

---

## Analysis output format

An analysis file has two sections separated by a horizontal rule. The
**human-readable analysis** comes first — this is what a reader engages
with. The **analytical working** follows below the delimiter — this is
the production process (Steps 1-7) that produced the analysis. The
working persists for auditability and review (IC-3) but is not intended
for primary reading.

Language should be professional throughout. The narrative register rules
(above) govern all prose sections.

### File structure

```
# Analysis: [Title]

DATE: [YYYY-MM-DD]
TIME: [~HH:MM UTC]
SOURCE: [who produced it]
SOURCE TYPE: [e.g., live blog, investigative journalism, press release]
SOURCE POSITION: [from positional-lens.md — Position 1-5]
URL: [if applicable]
FRAMEWORK STATE: [N patterns, N principles, N instruments (commit SHORT_HASH)]

---

## Narrative

[3-6 paragraphs. Prose summary of what the structural analysis found.
The opening paragraph should convey the single most important insight.
Narrative register rules apply — describe, do not evaluate.]

## Findings

[Numbered list. Each finding is a discrete, tagged, cross-referenceable
unit. Include a "who benefits / who bears cost" table after the findings
list.]

## Implications

[What follows from this analysis. Conclusions and evaluative judgments
belong here, not in the narrative. Include threads worth investigating.]

## Watch

[What to monitor going forward.]

## Analytical apparatus

[Provenance: instruments, principles, and patterns that shaped the
analysis.]

## Null case

[IC-2 assessment of the non-power explanation.]

---

## Analytical working

> The structured steps below are the production process that produced
> the analysis above. They exist for auditability and review (IC-3).
> They are not intended for primary reading.

### Step 1: DECOMPOSE
[...]

### Step 2: SOURCE
[...]

[...through Step 7: SO-WHAT]
```

### Findings list

Each finding is a discrete, tagged, cross-referenceable unit. Each
finding stands alone.

```
1. **[Finding title]**
   LAYER: [taxonomy layer(s)]
   STATUS: observed / inferred / speculative
   [2-3 sentences. Professional register. Specific.]
```

After the findings list, include a benefits/cost table:

```
| Actor | Gains | At whose expense |
|-------|-------|------------------|
| [actor] | [what they gain] | [who pays] |
```

STATUS vocabulary:
- **observed**: Directly present in the material. Could be verified by
  another reader examining the same source.
- **inferred**: Not stated but follows from observed facts through
  reasoning. The inference should be stated as such.
- **speculative**: A plausible implication that goes beyond what the
  evidence directly supports. Worth noting but should not be treated
  as established.

### Analytical apparatus

Every analysis must include a provenance section listing the framework
components that shaped the analysis. This serves transparency (the reader
sees what tools were applied), later review (a red team can assess whether
the right instruments were used), and framework health (patterns in
instrument usage reveal blind spots).

```
INSTRUMENTS APPLIED:
- [instrument name] (instruments/[filename].md) — [what it found or
  contributed to this analysis]

PRINCIPLES REFERENCED:
- [principle ID and title] (principles/[filename].md) — [how it applies]

PATTERNS MATCHED:
- [pattern name] (patterns.md) — [corroboration level] — [how it appears here]

PATTERNS NOT MATCHED:
- [any patterns explicitly considered and found inapplicable — optional
  but valuable for demonstrating rigor]
```

### Null case

Required by IC-2. Assess the non-power explanation. If the null
explanation fits the evidence as well as the power explanation, say so.

---

## EXTRACT mode procedure

Used for studying a source — a body of work (book, film, theory, historical
account) or a reference source (taxonomy, checklist, catalog, classification
system). The procedure evaluates what the source offers and produces whatever
is genuinely valuable: principles, instruments, both, or neither.

A **principle** is a generalizable truth about how power operates, extracted
from a specific source. It states: *this mechanism produces this effect
because of this reason*. Principles are more specific than axioms (they
describe particular mechanisms) and more source-bound than patterns (they
may be observed in only one work). When a principle is independently
confirmed across multiple sources, it may be promoted to a pattern.

An **instrument** is a reusable analytical tool imported from a source and
annotated with power-function descriptions. What distinguishes an instrument
from a generic reference document is the power function field — documenting
how each item functions specifically as a mechanism of power and control.

Not every source yields both. A political treatise may yield principles but
no instruments. A reference list may yield an instrument but no principles.
A rich work may yield both. The evaluation step determines what is there;
the procedure does not force output that the source does not support.

### Step 1: SURVEY

Examine the source to understand its scope, structure, and what it offers.

**Do this**:
- What type of source is this? (treatise, ethnography, reference catalog,
  historical account, film, theory, checklist, classification system)
- What is its central thesis about power, if any? (explicit or implicit)
- Which layers of power does it address?
- What systems or mechanisms does it describe?
- Does it contain structured knowledge that could serve as an analytical
  tool? (taxonomies, classification systems, catalogs of techniques,
  diagnostic checklists)

**Output format**:
```
SOURCE: [title and citation]
TYPE: [what kind of source]
THESIS: [central claim about power, if any — "none" for pure reference sources]
LAYERS ADDRESSED: [from taxonomy]
PRINCIPLE CANDIDATE: yes / no [does the source contain generalizable
  principles about how power operates?]
INSTRUMENT CANDIDATE: yes / no [does the source contain structured knowledge
  usable as an analytical tool?]
RATIONALE: [brief reasoning for each assessment]
```

### Step 2: EXTRACT PRINCIPLES (if principle candidate)

Run this step only if Step 1 identified the source as a principle candidate.

Identify generalizable principles about power and control.

**Do this**:
- State each principle in the form: "[Mechanism] produces [effect] because [reason]"
- Each principle must be generalizable beyond the specific context of the work
- Tag each principle with the taxonomy layers it involves
- Note whether the principle confirms, refines, or contradicts existing axioms

**Output format**:
```
PRINCIPLE: [statement]
LAYERS: [from taxonomy]
MECHANISM: [how it works]
EVIDENCE FROM WORK: [specific example from the source]
GENERALIZES TO: [where else this applies]
FRAMEWORK STATUS: confirms/refines/contradicts [which axiom or pattern]
STATUS: observed / inferred / speculative
```

### Step 3: IDENTIFY PATTERNS

Look for patterns that recur within the work or connect to existing patterns.

**Do this**:
- Cross-reference with `patterns.md` — does this work illustrate known patterns?
- Does it reveal new cross-layer patterns not yet documented?
- What mechanisms does the work show operating across multiple layers?
- If the source describes resistance or counterforce mechanisms, check
  whether they map to types in `circumventions.md`. Flag new types.

### Step 4: EVALUATE AND BUILD INSTRUMENTS (if instrument candidate)

Run this step only if Step 1 identified the source as an instrument candidate.

This step has two phases: evaluation and construction. Not every candidate
produces an instrument — the evaluation may determine that the material is
not sufficiently valuable, or that it duplicates existing instruments.

**Phase 1: Evaluate relevance**

**Do this**:
- Does the material map to one or more taxonomy layers? Which ones?
- Does it serve as an **analytical tool** (helps detect something during
  analysis)?
- Does it serve as a **mechanism catalog** (documents how power operates)?
- Does it serve both roles? (Most valuable instruments serve both.)
- Does it overlap with an existing instrument? If so, does it extend,
  replace, or duplicate it?

**Output format**:
```
TAXONOMY LAYERS: [which layers this maps to]
ROLE: analytical tool / mechanism catalog / both
ANALYTICAL USE: [how it would be used during analysis — which methodology steps]
MECHANISM USE: [how it documents power — which mechanisms it names]
OVERLAP WITH: [existing instruments, if any]
VERDICT: CREATE / MERGE / PROPOSE / SKIP
REASONING: [why]
```

**Verdicts**:
- **CREATE**: The material warrants a new instrument. Proceed to Phase 2.
- **MERGE**: The material extends an existing instrument. Identify the
  target instrument and proceed to Phase 2.
- **PROPOSE**: The material is partial or insufficient on its own, but
  the evaluation reveals that an instrument is needed in this area.
  Define what the instrument should contain, identify what the source
  provides and what gaps remain, and note additional sources needed
  to complete it. **Then check `principles/INDEX.md` and
  `analyses/INDEX.md` for whether those sources are already in the
  framework.** If the needed sources are already extracted or analyzed,
  cross-reference them immediately and re-evaluate: if the combined
  material is sufficient, upgrade the verdict to CREATE or MERGE.
  PROPOSE should remain only when needed sources are genuinely absent
  from the framework. Proceed to Phase 2 with whatever content is
  available.
- **SKIP**: The material is not sufficiently valuable as an instrument.
  Note the reasoning and continue to Step 5.

**Phase 2: Structure, curate, and produce** (if verdict is not SKIP)

Structure the instrument. Every instrument must follow a consistent format:

```markdown
# Instrument: [Name]

> Role: [1-2 sentences on what this instrument does]
> Derived from: [source(s)]

SOURCE: [citation]
TAXONOMY LAYERS: [which layers]
ANALYTICAL USE: [when to invoke during methodology — which steps]

---

## Items

[The actual content — organized by category if the source has categories.
Each item must include:]
- **Name**: [term or concept]
- **Description**: [what it is]
- **Detection**: [how to spot it in material being analyzed]
- **Power function**: [how it operates as a mechanism of control,
  if applicable — this is what makes it specific to this framework
  rather than a generic reference]

---

## How to apply this instrument

[Step-by-step instructions for using this instrument during analysis]
```

The **power function** field is what distinguishes a Lens of Power instrument
from a generic reference document. A list of logical fallacies exists
everywhere — what makes it an instrument *here* is documenting how each
fallacy functions as a mechanism of control.

Curate the content: select items based on relevance to the framework, collapse
redundancies, and mark low-frequency items. Not everything in a source needs
to be included.

If the verdict was PROPOSE, mark gaps clearly:

```markdown
## Gaps
STATUS: partial — additional sources needed
MISSING: [what the instrument still needs]
SOURCES TO INVESTIGATE: [suggested sources to fill gaps]
```

**Naming convention**: `instruments/[descriptive-name].md`
Use lowercase, hyphens for spaces. Name should describe the instrument's
function, not just its source (e.g., `logical-fallacies.md` not
`wikipedia-fallacy-list.md`).

### Step 5: SYNTHESIZE

Produce the output. What is produced depends on what Steps 1-4 found:

- **Principles found**: Write a principles file to `principles/` containing
  source metadata, IC-5 disclosure, central thesis, extracted principles,
  new patterns identified, connections to existing framework content, and
  (if instruments were also produced) references to the instrument files.
- **Instruments found**: Write instrument files to `instruments/`. Reference
  them in the principles file if one was also produced.
- **Both found**: Produce both, cross-referenced.
- **Neither found**: Document what was surveyed and why it did not yield
  principles or instruments. This is a valid outcome — not every source
  contributes to the framework, and recording that prevents re-evaluation.

#### Extraction record (required)

The principles file must include an **extraction record** section that
preserves the analytical reasoning that produced the extraction — not just
the output. This is the EXTRACT mode equivalent of the structured working
in ANALYZE mode. Without it, the reasoning is lost when the conversation
ends and the extraction cannot be audited, contested, or learned from.

The extraction record includes:

- **SURVEY**: The Step 1 assessment — source type, layers addressed,
  principle/instrument candidate verdicts, and the rationale for each.
  This records *why* the source was evaluated as it was.
- **INSTRUMENT EVALUATION**: If the source was evaluated as an instrument
  candidate, the full evaluation — taxonomy layers, role, analytical use,
  overlap assessment, verdict, and reasoning. This records the instrument
  decision and its justification.
- **SYNTHESIS SUMMARY**: A brief assessment of the extraction's yield —
  what was novel, what was confirmatory, what the source's distinctive
  contribution to the framework is, and what its limitations are.

Place the extraction record after the IC-5 disclosure and before the
principles. The record is part of the permanent file — it is not
working notes to be discarded.

#### Post-extraction framework updates (required)

After writing extraction outputs, update these framework files:

1. **`principles/INDEX.md`** — add or update the source entry
2. **`patterns.md`** — update corroboration counts for confirmed patterns
3. **`patterns-detail.md`** — add OBSERVED IN entries with analytical notes
4. **`sources/*.md`** — if a source record exists, update its Related files
   section and change extraction status from `(pending)` to complete
5. **`sources/INDEX.md`** — update extraction status if changed
6. **Rebuild viewer** — run `python3 tools/build-viewer.py && open viewer.html`

This checklist is not optional. An extraction that writes a principles
file but does not update the framework's cross-referencing files leaves
the framework in an inconsistent state — the knowledge exists but is
not discoverable through normal framework operations.

#### Source availability check (after extraction)

After completing the extraction and framework updates, check whether
the source has remaining material worth extracting.

**Do this**:
1. Read the source file in `sources/` (if it exists)
2. Check for "Future candidates" sections or `FUTURE CANDIDATE` entries
3. If future candidates exist:
   a. List remaining chapters or sections with page ranges and notes
   b. Cross-reference with framework gaps — PRELIMINARY patterns needing
      corroboration, underrepresented layers — to prioritize which to
      extract next
   c. If the source has an ARCHIVE URL, note availability
   d. If not, use WebSearch to check for online availability (search for
      "[title] PDF" or "[title] archive.org")
4. Report to user: "N chapters remain. Priority based on framework gaps:
   [chapter] (would test [pattern]), [chapter] (would add [layer]
   coverage)"

This check is informational — it does not trigger further extraction.
It surfaces what remains and helps the user decide what to study next.

---

## Instrument invocation

During any step, if an instrument from `instruments/` is relevant:

1. Load the instrument file
2. Scan the material against the instrument's catalog
3. Flag any matches
4. Include matches in the step's output

Instruments are not mandatory at every step. Use them where they add
signal. The methodology steps indicate where specific instruments are
most likely to be useful.

---

## RED TEAM mode procedure

A separate operation, not part of every analysis. Invoked periodically
to examine the framework itself. Required by IC-3 in `constitution.md`.

**When to invoke**: After every 5-10 analyses, or when the framework is
producing suspiciously consistent results, or when the analyst feels
certain the framework is correct (certainty is the signal).

### Step 1: SELF-EXAMINE

Turn every axiom directive inward.

**Do this**:
- How is this framework shaping what I look for and therefore what I find?
- Which axiom do I treat as most obviously true? Why? Is that certainty
  earned or assumed?
- Has the framework produced a result in recent analyses that genuinely
  surprised me? If not, it may be confirming rather than revealing.

### Step 2: APPLY THE TAXONOMY TO THE FRAMEWORK

Treat the Lens of Power itself as a system. Check it against each
taxonomy layer:

- **Thought & Narrative**: Is the framework framing everything as power?
  Is it narrowing what I consider a valid explanation?
- **Institutional**: Has the framework become an authority I defer to
  rather than a tool I use critically?
- **Surveillance**: Is the framework making me see control everywhere,
  producing a paranoid lens rather than an analytical one?

### Step 3: CHECK THE INPUT DIET

Review `analyses/INDEX.md` for selection bias:

- What domains have been analyzed? What domains have been avoided?
- Which taxonomy layers appear most often as primary? Which never appear?
- What is the distribution of null case outcomes? If the null case has
  never been rated "plausible" or "accepted," the framework may be
  selecting inputs that confirm its axioms.
- Has any adversarial material been analyzed? What was the result?
- Are there types of material the analyst instinctively avoids
  (corporate governance, functioning democracies, successful reforms)?
  That avoidance is a signal.

**Output format**:
```
INPUT DIET:
  TOTAL ANALYSES: [count]
  DOMAIN DISTRIBUTION: [domains and counts]
  PRIMARY LAYER DISTRIBUTION: [layers and counts]
  NULL CASE OUTCOMES: [rejected/plausible/accepted counts]
  ADVERSARIAL ANALYSES: [count and outcomes]
  BLIND SPOTS: [domains or material types never analyzed]
  RECOMMENDATION: [what to analyze next to test the framework]
```

### Step 4: CHECK THE EVIDENCE BASE

Review `evidence/` entries:

- What is the ratio of `supports` to `challenges` entries? If
  overwhelming support with no challenges, the framework may be
  filtering evidence.
- Are there axioms with no challenging evidence at all? Flag them —
  either they are robustly true or they are not being tested.

### Step 5: ASSESS FALSIFIABILITY

Review the falsifiability table in `constitution.md`:

- For each axiom, has any analysis produced evidence that approaches
  the falsification condition?
- If no axiom has ever been threatened, the framework may be unfalsifiable
  in practice, regardless of what the table says.

**Output format**:
```
FRAMEWORK HEALTH:
  CONFIRMATION BIAS RISK: HIGH / MEDIUM / LOW
  AXIOMS NEVER CHALLENGED: [list]
  MOST RECENT SURPRISE: [what the framework revealed that was unexpected]
  RECOMMENDED ADJUSTMENTS: [changes to axioms, methodology, or practice]
SELF-ASSESSMENT: [honest summary of the framework's current state]
```

Record the output in `evidence/` with tags:
`AXIOMS: all`, `RELATIONSHIP: self-examination`

---

## SUGGEST mode procedure

A read-only diagnostic mode. Scans framework files to assess health,
identify gaps, and produce prioritized recommendations for what to
study, extract, or red-team next. No file writes, no branching check.

**Input**: None — the framework itself is the input.

**Output**: A structured health report with actionable recommendations.

### Step 1: RED TEAM TIMING

Check whether a red team is overdue per IC-3.

**Do this**:
- Scan `evidence/` for entries with `RELATIONSHIP: self-examination`
- Count total analyses in `analyses/INDEX.md`
- Count analyses since the most recent self-examination entry
- Flag if > 10 analyses without a red team

**Output format**:
```
LAST RED TEAM: [date or "never"]
ANALYSES SINCE: [count]
STATUS: overdue / due soon / current
```

### Step 2: SELECTION BIAS

Audit the input diet for systematic skew.

**Do this**:
- Read `analyses/INDEX.md`
- **Domain clustering**: Which domains appear most often? Which are absent?
- **Layer concentration**: Which taxonomy layers appear most as primary?
  Which never appear?
- **Null case distribution**: Count rejected / plausible / accepted outcomes.
  If no null case has ever been rated "plausible" or "accepted," flag that
  IC-2 may be decorative — the framework is selecting inputs that confirm
  its axioms.
- **Adversarial input ratio**: Count analyses where the null case won
  (accepted) vs total. Flag if < 1 in 5 are adversarial.

**Output format**:
```
DOMAIN DISTRIBUTION: [domains and counts]
PRIMARY LAYER DISTRIBUTION: [layers and counts]
NULL CASE OUTCOMES: rejected=[n] plausible=[n] accepted=[n]
ADVERSARIAL RATIO: [n]/[total] ([percentage])
BLIND SPOTS: [domains or material types never analyzed]
```

### Step 3: EVIDENCE BALANCE

Check whether the evidence base is testing or merely confirming axioms.

**Do this**:
- Scan `evidence/*.md` for RELATIONSHIP tags
- Count `supports` vs `challenges` vs `complicates` per axiom
- Flag axioms with no challenging evidence — either robustly true or
  not being tested
- Note any counter-evidence mentioned in analyses or patterns but not
  filed as evidence entries

**Output format**:
```
EVIDENCE DISTRIBUTION:
  [axiom]: supports=[n] challenges=[n] complicates=[n]
  ...
AXIOMS WITH NO CHALLENGES: [list]
UNFILED COUNTER-EVIDENCE: [any noted but not recorded]
```

### Step 4: PATTERN GAPS

Identify patterns needing corroboration or challenge.

**Do this**:
- Read `patterns.md` for PRELIMINARY patterns
- For each, identify what material types or domains would corroborate
  or challenge it
- Check whether counter-evidence is noted in `patterns-detail.md` but
  not filed in `evidence/`

**Output format**:
```
PRELIMINARY PATTERNS: [count]
  [pattern name] — corroborate with: [material type]
  [pattern name] — challenge with: [material type]
  ...
COUNTER-EVIDENCE NOTED BUT UNFILED: [list, if any]
```

### Step 5: EXTRACT GAPS

Identify unextracted material from known sources.

**Do this**:
- Scan `sources/*.md` for "Future candidates" or "FUTURE CANDIDATE"
  sections/entries
- List unextracted chapters or sections with page ranges and notes
- Check if the source has an ARCHIVE URL — if so, note availability
- If the source has no ARCHIVE URL, use WebSearch to check for online
  availability (search for "[title] PDF" or "[title] archive.org")
- Cross-reference unextracted material with framework gaps (PRELIMINARY
  patterns, underrepresented layers) to prioritize what to extract next

**Output format**:
```
SOURCES WITH UNEXTRACTED MATERIAL:
  [source title]:
    - [chapter/section] (pages [range]) — [priority based on framework gaps]
    - ...
    AVAILABILITY: [archive URL / found online / not found]
```

### Step 6: INSTRUMENT GAPS

Identify proposed but unbuilt instruments.

**Do this**:
- Scan `principles/INDEX.md` for `INSTRUMENT PROPOSED` entries
- For each, check whether the instrument exists in `instruments/`
- If it does not exist, note what the instrument would contain and
  what sources are needed to build it

**Output format**:
```
PROPOSED INSTRUMENTS NOT YET BUILT:
  [instrument name] — proposed in: [source], needs: [what's missing]
```

### Step 7: COVERAGE GAPS

Identify underrepresentation in layers, perspectives, and source types.

**Do this**:
- **Layer coverage**: Count which layers appear as primary across all
  analyses and extractions. Identify layers or layer pairs with no
  items. Suggest material types that would cover gaps.
- **Perspective gaps (IC-5)**: Scan `principles/INDEX.md` and analyses
  for source positions. Flag if Position 2 (everyday governed) and
  Position 3 (revolutionary) are underrepresented relative to
  Position 5 (observer/analyst).
- **Source type concentration**: Count source types across analyses
  (news article, investigation, policy brief, book, etc.). Flag if
  one type dominates.

**Output format**:
```
LAYER COVERAGE:
  [layer]: [count] as primary, [count] as secondary
  UNDERREPRESENTED: [layers with few or no items]
PERSPECTIVE DISTRIBUTION:
  Position 1 (exercising): [count]
  Position 2 (governed): [count]
  Position 3 (revolutionary): [count]
  Position 4 (intermediary): [count]
  Position 5 (observer): [count]
  UNDERREPRESENTED: [positions with few items]
SOURCE TYPE DISTRIBUTION:
  [type]: [count]
  ...
  DOMINANT: [type, if one exceeds 50%]
```

### Step 8: PRIORITIZED RECOMMENDATIONS

Synthesize all findings into an ordered list of actions.

**Priority order** (by framework health impact):
1. Challenging evidence (axioms never tested → framework unfalsifiable)
2. Red team (overdue self-examination → confirmation bias undetected)
3. Adversarial input (null case never wins → IC-2 decorative)
4. Pattern corroboration (PRELIMINARY patterns → framework ungrounded)
5. Extract gaps (known material unextracted → knowledge left on table)
6. Instrument gaps (proposed tools unbuilt → analytical capability missing)
7. Coverage gaps (layer/perspective/type imbalance → blind spots)

**Each recommendation must be actionable**: name a specific source,
material type, domain, or action — not a generic suggestion. Where
possible, name a concrete source or URL.

**Output format**:
```
## Prioritized recommendations

1. [action] — [why, referencing the health check that surfaced it]
2. [action] — [why]
3. ...
```

---

## Source provenance

Every source analyzed or extracted must have a provenance record in
`sources/`. This ensures the framework can verify what it analyzed,
even if the original source changes or disappears.

### Source directory structure

```
sources/
  INDEX.md              — compact lookup table (like principles/INDEX.md)
  [source-name].md      — full provenance record per source
```

### Source types and provenance tiers

Sources fall into three provenance tiers based on what the framework
can verify:

**Primary document** — the analyst has the artifact (PDF, document file).
Strongest provenance.
```
SOURCE TYPE: primary_document
HASH: sha256:[hash of the file analyzed]
ARCHIVE: [Internet Archive or other permanent link(s)]
QUOTE STATUS: verbatim with page references
```

**URL article** — content fetched from a URL. Archive link and excerpts
provide durability.
```
SOURCE TYPE: url
URL: [original URL]
FETCH DATE: [YYYY-MM-DD]
ARCHIVE: [Wayback Machine snapshot link]
QUOTE STATUS: verbatim (excerpts only)
```
IP/legal note: do not store full article text in the repo. Store only
the excerpts cited in the extraction (fair use for commentary/criticism).
Archive links provide the fallback for full context.

**Training data** — no artifact; the analyst (LLM) is working from
training data knowledge. Weakest provenance.
```
SOURCE TYPE: training_data
QUOTE STATUS: reconstructed (unverified)
EDITION: [best guess at reference edition/translation]
VERIFICATION: pending | verified against [source]
```
Training-data extractions should be flagged per IC-5 (the LLM is a
biased instrument). Quotes are reconstructions, not verified verbatim
passages. These extractions can be upgraded by obtaining the actual
source and verifying quotes against it.

### Source record format

Each source file in `sources/` follows this structure:

```markdown
# Source: [Title]

## Metadata
TITLE: [full title]
AUTHOR(S): [names]
PUBLISHER: [publisher/institution]
DATE: [publication date]
FORMAT: [PDF, book, article, etc.]
PAGE COUNT: [if applicable]
SOURCE TYPE: [primary_document | url | training_data]

## Provenance
HASH: [sha256 hash, if primary_document]
ORIGINAL URL: [if applicable]
ARCHIVE: [archive.org links]
QUOTE STATUS: [verbatim | reconstructed (unverified)]

## Extraction status
[List of sections/chapters with status:
  - EXTRACTED — included in the extraction
  - FUTURE CANDIDATE — identified for possible future extraction
  - NOT SELECTED — outside scope]

## Related files
[Links to extraction files, analyses, and evidence entries
that reference this source]
```

### Provenance requirements for extractions

Every principle and instrument extracted must include a verbatim quote
from the source with a page reference (for primary documents) or
section reference (for articles). This is not optional — it is the
evidentiary basis for the claim.

For training-data sources, quotes must be marked as `reconstructed
(unverified)` and the extraction file must note that quotes have not
been verified against a physical copy.

---

## Output discipline

- Be specific. Name the mechanism, name the layer, name the actor.
- Distinguish between what is observed and what is inferred.
- **Framework term references**: In all human-readable output (READ mode
  prose, ANALYZE mode narrative and briefing, EXTRACT mode synthesis),
  reference framework-defined terms as follows:
  - **First occurrence**: Bold the term and follow with a parenthetical
    gloss (a few words describing what it is). Example:
    `the **Compliance Gradient** (partial compliance as power negotiation)`
  - **Subsequent occurrences**: Bold the term, no gloss. Example:
    `the **Compliance Gradient**`
  - **Reference list**: At the end of the output, include a
    "Framework references" section listing every framework term used,
    with a hyperlink to its definition in the repository. Example:
    ```
    **Framework references**
    - Compliance Gradient: [patterns.md](https://github.com/simonibsen/lens-of-power/blob/main/patterns.md#the-compliance-gradient)
    - Axiom 9: [constitution.md](https://github.com/simonibsen/lens-of-power/blob/main/constitution.md#9-compliance-can-be-manufactured-without-explicit-coercion)
    ```
  - This applies to patterns, axioms, principles, instruments, and
    integrity constraints when referenced by name. The base URL is
    `https://github.com/simonibsen/lens-of-power/blob/main/`.
  - The purpose is twofold: the gloss makes the output legible to
    readers unfamiliar with the framework; the reference list connects
    every term to its definition for readers who want depth.
  - Structured working (Steps 1-7) and internal fields (STATUS,
    LAYER, CORROBORATION) do not require this treatment — they are
    already within the framework's context.
- **Markdown field formatting**: When writing field-based content to
  files (principles, instruments, patterns, patterns-detail, evidence),
  always place a blank line between consecutive field lines. Consecutive
  lines without blank lines collapse into a single paragraph in standard
  markdown renderers. Write:
  ```
  PRINCIPLE: Control of narrative is control of possibility.

  LAYERS: Thought & Narrative

  MECHANISM: ...
  ```
  Not:
  ```
  PRINCIPLE: Control of narrative is control of possibility.
  LAYERS: Thought & Narrative
  MECHANISM: ...
  ```
  This applies to all fields (LAYERS, STATEMENT, MECHANISM, NOTE,
  CORROBORATION, STATUS, EVIDENCE FROM WORK, GENERALIZES TO, SOURCE,
  TAXONOMY LAYERS, ANALYTICAL USE, OBSERVED IN, etc.). Templates in
  this methodology show the field structure compactly inside code blocks
  for readability — the blank-line rule applies when writing actual files.
- Mark evidentiary basis on every claim: **observed** (directly present
  in material), **inferred** (follows from reasoning), **speculative**
  (plausible but beyond direct evidence).
- Mark corroboration on patterns: **preliminary** (< 3 corroborating
  sources), **supported** (≥ 3 sources AND ≥ 10% of the relevant
  corpus), **established** (≥ 5 sources AND ≥ 20% of the relevant
  corpus AND no unresolved counter-evidence). The relevant corpus is
  sources sharing at least one taxonomy layer with the pattern.
  Corroboration levels are computed by the build script
  (`tools/build-viewer.py`) and written back to `patterns.md` and
  `patterns-detail.md`. The analyst does not need to compute levels
  manually — the build script handles it after each commit.
- **Circumvention register**: When documenting circumventions or
  resistance, use observational language: "has been observed to" (not
  "works" or "is effective"), "may" (not "will"), "appeared to" (not
  "succeeded in"), "conditions under which X was observed" (not
  "requirements for X"). See `instruments/circumvention-typology.md`
  for the full convention.
- When uncertain, say so. The framework values honesty over completeness.
- Always end with a framework update recommendation, even if it's "none."

### Claim discipline: observation, inference, speculation

Every claim in an analysis exists at one of three levels. The analyst
must make clear which level a claim occupies — especially in prose
sections (Narrative, Significance) where the structure of formatted
output no longer enforces precision.

**Observed** — directly evidenced in the source material. No analytical
judgment required. Use language that reports:
- "CENTCOM issued a statement with no specifics or timeline."
- "The school strike was reported in the live blog, then followed by
  twelve military updates."
- "Trump said '48 leaders are gone in one shot.'"

**Inferred** — follows from evidence but involves analytical judgment.
The connection between evidence and conclusion requires the analyst's
reasoning. Use language that signals inference:
- "This suggests...", "The observable effect is...", "This is consistent
  with...", "This pattern resembles...", "The evidence points toward..."
- "The statement's observable effect is to close the topic without
  opening an investigation."
- "The absence of legal framing from coverage removes it as a framework
  for public evaluation."

**Speculative** — plausible and worth noting, but not established by
available evidence. Use language that marks contingency:
- "If verified, this would...", "This may indicate...", "It is possible
  that...", "One reading is..."
- "If the diplomatic record confirms Araghchi's claim, this would
  indicate diplomacy was performative."

**The failure mode**: The framework's characteristic error is collapsing
inference into observation — writing "the function of X is Y" when the
evidence supports "the observable effect of X is Y." This happens most
in prose sections where analytical momentum carries the writer past the
evidence. Functional and causal claims ("serves to," "is designed to,"
"functions as," "in order to") assert intent or purpose; they belong at
the inferred or speculative level unless the source material explicitly
states the intent.

### Review pass

After drafting an analysis and before writing it to file, perform a
single self-review pass:

1. Scan every **causal or functional claim** — any sentence containing
   "the function of," "serves to," "is designed to," "functions as,"
   "in order to," "the purpose of," or equivalent phrasing.
2. For each, ask: **Is this observed, inferred, or speculative?**
   Does the source material directly evidence the intent/function
   claimed, or is the analyst supplying the connection?
3. If inferred or speculative, does the language make that clear?
   If not, revise to use the appropriate signal vocabulary.
4. Check prose sections (Narrative, Significance) with extra scrutiny
   — these are where analytical momentum most often overruns evidence.
5. Check the **Narrative** section for register violations — editorial
   adjectives, rhetorical devices, evaluative constructions disguised
   as descriptions. Apply the test: could a reader with different
   political commitments accept this as an accurate description of
   what the analysis found?

This pass is not a separate methodology step. It is a writing discipline
applied before the analysis is finalized. It takes two minutes and
prevents the framework's most common integrity failure: presenting
the analyst's interpretation as the material's demonstrated fact.
