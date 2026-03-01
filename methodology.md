# Methodology: Lens of Power

> Role: This document defines the analytical procedure. It is designed to
> be executed directly by an LLM or followed by a human analyst. When
> invoked, follow the steps in order and produce structured output.

---

## Modes of operation

Select a mode based on the task:

### ANALYZE mode
**Input**: A piece of new information (article, speech, policy, event, claim)
**Output**: Structured analysis revealing power dynamics, mechanisms, and connections
**When to use**: Processing current events, news, policy documents, arguments

### EXTRACT mode
**Input**: A body of work (book, film, theory, historical account)
**Output**: Principles about how power operates, added to the framework's knowledge base
**When to use**: Studying foundational works to build the framework's principle library

### INSTRUMENT mode
**Input**: A source containing a body of knowledge that may be useful as an analytical tool (taxonomy, checklist, catalog of techniques, classification system)
**Output**: Evaluation of whether it should become an instrument, and if so, the instrument file itself
**When to use**: Evaluating potential new instruments from any source (reference pages, academic works, lists, catalogs)

### RED TEAM mode
**Input**: The framework itself
**Output**: Framework health assessment, confirmation bias check, falsifiability review
**When to use**: Periodically, or when the framework is producing suspiciously consistent results

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
- A **Narrative** section at the top — a readable prose essay (3-6
  paragraphs) summarizing the key findings for a human reader. The
  structured steps follow below it as the canonical analytical record.

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

**Frequency**: At least 1 in every 5 analyses should be adversarial.
If the framework cannot produce "the power explanation does not hold
here" as an honest conclusion, it is a confirmation machine regardless
of what the integrity constraints say.

The analysis index makes this trackable — if the "null case outcome"
column never reads "accepted" or "plausible," that is itself a finding
about the framework's health.

### Step 1: DECOMPOSE

Strip the material to its bare claims. Remove rhetoric, emotional framing,
and narrative structure.

**Do this**:
- List each factual claim or assertion separately
- Identify which claims are presented as fact vs. opinion vs. implied
- Note the emotional register (urgency, fear, reassurance, outrage)
- Separate the signal from the packaging

**Output format**:
```
CLAIMS:
- [claim 1] (stated as: fact/opinion/implied)
- [claim 2] ...

FRAMING: [describe the rhetorical packaging]
EMOTIONAL REGISTER: [what feeling is being engineered]
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
(propaganda filters, logical fallacies) and apply them here.

**Output format**:
```
SOURCE: [who]
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

**Null case (required by IC-2)**: Ask: "What would this look like if
power dynamics were NOT the explanation?" Consider simpler accounts:
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
for fallacies of omission, false dilemma, etc.

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

**Output format**:
```
IMPLICATIONS: [what follows from this analysis]
WATCH: [what to monitor going forward]
INVESTIGATE: [threads worth pulling]
FRAMEWORK UPDATE: [any additions to patterns.md or refinements to suggest]
MADE VISIBLE: [what this analysis reveals that was previously hidden]
```

---

## EXTRACT mode procedure

Used for bodies of work (books, films, theories, historical accounts).
The goal is to distill principles about how power operates and add them
to the framework's knowledge base.

### Step 1: SURVEY

Read/review the work with the taxonomy layers as a lens.

**Do this**:
- Which layers of power does this work address?
- What is the work's central thesis about power (explicit or implicit)?
- What systems or mechanisms does it describe?

### Step 2: EXTRACT PRINCIPLES

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
```

### Step 3: IDENTIFY PATTERNS

Look for patterns that recur within the work or connect to existing patterns.

**Do this**:
- Cross-reference with `patterns.md` — does this work illustrate known patterns?
- Does it reveal new cross-layer patterns not yet documented?
- What mechanisms does the work show operating across multiple layers?

### Step 4: NOTE INSTRUMENTS

Identify any analytical tools, taxonomies, or frameworks within the work
that could be added to `instruments/`.

**Do this**:
- Does the work provide a useful classification system?
- Does it name mechanisms that belong in the taxonomy?
- Does it describe techniques of control that should be cataloged?

### Step 5: SYNTHESIZE

Produce the output document for `principles/`.

**Output format**: A markdown file containing:
- Source metadata (title, author, year)
- Central thesis about power
- Extracted principles (from step 2)
- New patterns identified (from step 3)
- Suggested instrument additions (from step 4)
- Connections to existing framework content

---

## INSTRUMENT mode procedure

Used to evaluate a source for potential inclusion as an instrument in
`instruments/`. Instruments are imported bodies of knowledge that serve
as analytical tools during analysis. This procedure ensures consistent
evaluation and formatting.

### Step 1: SURVEY SOURCE

Examine the source material to understand its scope and structure.

**Do this**:
- What does this source contain? (taxonomy, checklist, catalog, classification, techniques)
- How is it organized? (categories, hierarchy, flat list)
- How comprehensive is it? (exhaustive, representative, partial)
- What is the source's authority? (academic, community, institutional, individual)

**Output format**:
```
SOURCE: [title and URL/citation]
CONTENT TYPE: taxonomy / checklist / catalog / classification / techniques
ORGANIZATION: [how it is structured]
SCOPE: exhaustive / representative / partial
AUTHORITY: [basis for credibility]
ITEM COUNT: [approximate number of items]
```

### Step 2: EVALUATE RELEVANCE

Determine whether this source is useful to the framework.

**Do this**:
- Does it map to one or more taxonomy layers? Which ones?
- Does it serve as an **analytical tool** (helps detect something during analysis)?
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
- **CREATE**: The source warrants a new instrument. Proceed to Step 3.
- **MERGE**: The source extends an existing instrument. Identify the
  target instrument and proceed to Step 3.
- **PROPOSE**: The source is partial or insufficient on its own, but
  the evaluation reveals that an instrument is needed in this area.
  Define what the instrument should contain, identify what the source
  provides and what gaps remain, and note additional sources needed
  to complete it. Proceed to Step 3 with the partial content available.
- **SKIP**: The source is not relevant or useful. Stop here and explain why.

### Step 3: STRUCTURE

Design the instrument format. Every instrument must follow a consistent
structure to be usable during analysis.

**Required sections for every instrument**:

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

If the verdict was PROPOSE, mark gaps clearly:

```markdown
## Gaps
STATUS: partial — additional sources needed
MISSING: [what the instrument still needs]
SOURCES TO INVESTIGATE: [suggested sources to fill gaps]
```

### Step 4: CURATE

Not everything in a source needs to be included. Select items based on
relevance to the framework.

**Do this**:
- Which items are most relevant to power and control analysis?
- Which items appear frequently in real-world exercises of power?
- Which items are redundant with each other? (Collapse if so.)
- Are there items that are theoretically interesting but rarely
  encountered in practice? (Include but mark as LOW frequency.)

**Output format**:
```
INCLUDED: [count] items
EXCLUDED: [count] items
EXCLUSION RATIONALE: [why excluded items were dropped]
CATEGORIES: [how items are grouped]
```

### Step 5: PRODUCE

Write the instrument file to `instruments/`.

**Naming convention**: `instruments/[descriptive-name].md`
Use lowercase, hyphens for spaces. Name should describe the instrument's
function, not just its source (e.g., `logical-fallacies.md` not
`wikipedia-fallacy-list.md`).

After writing, verify:
- Does it follow the required structure from Step 3?
- Does every item have a **power function** annotation?
- Are the **how to apply** instructions specific enough for an LLM to follow?
- Is the instrument referenced in the right methodology steps?

**Output format**:
```
INSTRUMENT CREATED: instruments/[filename].md
ITEM COUNT: [number of items included]
METHODOLOGY STEPS: [which steps should invoke this instrument]
RELATED INSTRUMENTS: [any existing instruments this connects to]
```

Offer to update `methodology.md` if specific steps should reference
the new instrument.

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

## Output discipline

- Be specific. Name the mechanism, name the layer, name the actor.
- Mark confidence levels: HIGH (directly evidenced), MEDIUM (strongly
  implied), LOW (speculative but worth noting).
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

This pass is not a separate methodology step. It is a writing discipline
applied before the analysis is finalized. It takes two minutes and
prevents the framework's most common integrity failure: presenting
the analyst's interpretation as the material's demonstrated fact.
