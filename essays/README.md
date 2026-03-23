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

Essays are **not** evidence entries, pattern observations, or analytical
findings. They should not be cited as evidentiary basis for framework
updates. They may be cross-referenced from patterns and principles as
places where structural arguments were developed, but the cross-reference
should note the epistemic status.

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
