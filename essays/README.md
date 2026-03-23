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

The essay's value is *generative* (it identifies what to study next) and
*preservative* (it captures structural thinking). It does not produce
framework content. The extraction of the sources the essay references
produces framework content. The essay tells the analyst *why* to extract
a source. That is the boundary.

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
