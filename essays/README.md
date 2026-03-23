# Essays

> Role: Framework-informed synthesis writing that draws on the accumulated
> knowledge base to make structural arguments about topics. Essays are
> distinct from analyses (which examine specific material) and extractions
> (which study specific sources). They are products of conversation between
> the analyst and the framework, triggered by the analyst's questions and
> concerns.

## Epistemic status

Essays occupy a **different epistemic level** than analyses, principles,
patterns, or evidence. They are:

- **Synthesis, not documentation.** They combine insights from multiple
  framework components to make arguments that go beyond what any single
  source documents.
- **Analyst-shaped.** They are products of specific prompts, concerns,
  and conversational context. A different analyst with different questions
  would produce different essays.
- **Structurally grounded but not independently verified.** The structural
  arguments derive from the framework's accumulated patterns and principles,
  which are themselves grounded in documented sources. But the synthesis
  itself has not been independently corroborated.

## What essays CAN and CANNOT do

**Essays CAN**:
- Be cross-referenced from pattern or principle notes as "a place where
  this pattern was applied to [topic]" — a pointer, not evidence
- Serve as a starting point when the analyst returns to a topic
- Identify gaps that suggest what to extract or analyze next (e.g.,
  "Braverman would ground this argument in documented evidence")
- Preserve a line of structural thinking for future reference

**Essays CANNOT**:
- Be cited as evidentiary basis for pattern promotion or confidence changes
- Produce principles, evidence entries, or instrument updates
- Be treated as documented findings in any framework context
- Substitute for extraction of the sources they reference — if an essay
  argues that a mechanism exists, the mechanism must be independently
  documented through extraction or analysis before it enters the framework

## Authorship

Essays are produced by the LLM in response to the human's questions,
drawing on the framework's accumulated findings. The human prompts,
directs, and judges; the LLM synthesises and articulates. Both
contributions shape the output. See the "The analyst" section of
`methodology.md` for the framework's definition of this composite.

## Function

Essays serve three functions:

1. **Synthesis** — they connect findings across multiple analyses,
   patterns, and principles to make structural arguments that no single
   source or analysis contains. The framework's components are discrete;
   essays are where the analyst assembles them into coherent arguments
   about how mechanisms interact across domains.
2. **Sense-making** — they help the analyst (and reader) understand what
   the framework's accumulated findings mean for a specific question or
   concern. An essay takes the question "what does the framework say
   about X?" and produces a reasoned answer grounded in the corpus.
3. **Direction** — they identify gaps that suggest what to extract or
   analyze next (e.g., "Braverman would ground this argument in
   documented evidence").

Essays do not produce framework content (patterns, principles, evidence,
instruments). The extraction of the sources essays reference produces
framework content. The distinction: essays are the analyst's thinking
*with* the framework; analyses and extractions are the framework's
documented findings. Both have value; they have different evidentiary
status.

## IC-3 obligation

The existence of the essays category must be scrutinized during red team
reviews (IC-3). The red team should ask:

1. Has the essays category introduced ungrounded claims into the
   framework's knowledge base through cross-references?
2. Are pattern or principle notes citing essays as though they were
   independently documented findings?
3. Has the framework's evidentiary standard been degraded by the
   presence of synthesis output alongside documented analysis?
4. Is the epistemic distinction between essays and analyses clear
   to a reader encountering the framework for the first time?

If the answer to any of 1-3 is yes, the cross-references should be
revised or removed. The essays themselves are not the risk — the risk
is contamination of the evidentiary base through careless citation.

## Provenance

Each essay records:
- **Date** of the conversation that produced it
- **Prompt** — the analyst's question or concern that triggered the essay
- **Framework state** at time of writing (commit hash, pattern/principle counts)
- **IC-5 disclosure** — the LLM bias relevant to the topic
