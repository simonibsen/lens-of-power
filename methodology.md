# Methodology: Lens of Power

> Role: This document defines the analytical procedure. It is designed to
> be executed directly by an LLM or followed by a human analyst. When
> invoked, follow the steps in order and produce structured output.

---

## Modes of operation

This methodology has two modes. Select one based on the task:

### ANALYZE mode
**Input**: A piece of new information (article, speech, policy, event, claim)
**Output**: Structured analysis revealing power dynamics, mechanisms, and connections
**When to use**: Processing current events, news, policy documents, arguments

### EXTRACT mode
**Input**: A body of work (book, film, theory, historical account)
**Output**: Principles about how power operates, added to the framework's knowledge base
**When to use**: Studying foundational works to build the framework's principle library

---

## ANALYZE mode procedure

### Triage: determine depth

Before beginning, assess the material:

- **Quick pass** (steps 1, 3, 7 only): Use for initial screening. Is this worth deeper analysis?
- **Full pass** (all 7 steps): Standard analysis.
- **Deep pass** (all 7 steps + written synthesis): For material of high significance.

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
- Which layers from `taxonomy.md` are active?
- Map the layer interactions (use the interaction format from taxonomy.md)

**Output format**:
```
LAYERS ACTIVE: [list from taxonomy]
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

**Invoke instruments**: Check `instruments/cognitive-biases.md` (if available)
for biases that might be affecting this analysis.

**Output format**:
```
INVERSE CLAIM: [the opposite position]
STRONGEST DEFENSE: [steelman of the system/actor being analyzed]
NULL CASE: [the non-power explanation — incompetence, accident, inertia, good faith]
NULL CASE PLAUSIBILITY: HIGH / MEDIUM / LOW [with reasoning]
FALSIFIABLE BY: [what evidence would change this assessment]
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

**Invoke instruments**: Check `instruments/logical-fallacies.md` (if available)
for fallacies of omission, false dilemma, etc.

**Output format**:
```
MISSING QUESTIONS: [questions the material should address but doesn't]
ABSENT VOICES: [whose perspective is excluded]
MISSING EVIDENCE: [data or proof not provided]
EXCLUDED ALTERNATIVES: [options never presented]
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

### Step 3: CHECK THE EVIDENCE BASE

Review `evidence/` entries:

- What is the ratio of `supports` to `challenges` entries? If
  overwhelming support with no challenges, the framework may be
  filtering evidence.
- Are there axioms with no challenging evidence at all? Flag them —
  either they are robustly true or they are not being tested.

### Step 4: ASSESS FALSIFIABILITY

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
- Distinguish between what is observed and what is inferred.
- Mark confidence levels: HIGH (directly evidenced), MEDIUM (strongly
  implied), LOW (speculative but worth noting).
- When uncertain, say so. The framework values honesty over completeness.
- Always end with a framework update recommendation, even if it's "none."
