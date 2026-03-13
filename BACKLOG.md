# Framework Backlog

> Role: Living document capturing prioritized recommendations from SUGGEST
> mode diagnostics. Refreshed each time SUGGEST mode runs. Items are removed
> when completed or superseded. Dates track when each recommendation was
> first surfaced.

Last diagnostic: 2026-03-12 (41 analyses, 32 patterns, 29 principles, 7 instruments)

---

## Immediate priority

### 1. Source additional Position 2 testimony (2026-03-06, updated 2026-03-13)
SOURCE: Coverage gaps (Step 7)
Three Position 2 sources extracted: Terkel *Working* (workplace, 8 principles),
Desmond *Evicted* (housing, 7 principles), and Ehrenreich *Nickel and Dimed*
(low-wage service work, 6 principles). All three produced IC-1 flags for
Axioms 9 and 10 from below — three independent domains now confirm the
complication. Continue expanding. Candidates: Ai Weiwei memoir (Position 2/3,
non-Western), Desmond *Poverty, by America* (structural analysis).

---

## Short-term

### 2. Increase adversarial input rate to 20% (2026-03-09, updated 2026-03-13)
SOURCE: Selection bias (Step 2)
7/41 (17%) approaching the 20% threshold. NCSL youth soccer board meeting
added (null case accepted at HIGH). Continue including null-case-likely
inputs in future analyses. Candidates: municipal utility rate filing,
scientific instrument calibration paper, routine corporate earnings call.

### 3. Review PRELIMINARY patterns — prune or corroborate (2026-03-06, updated 2026-03-13)
SOURCE: Pattern gaps (Step 4), Red team 2 (2026-03-12), Pattern review (2026-03-13)
12 patterns at PRELIMINARY (38% of all patterns). Build pipeline bug fixed —
observed_in was not including analysis corroborations (+165 edges recovered).
Review completed 2026-03-13:
- **Flagged for retirement**: Economy of Violence (2 obs + counter-evidence,
  only Machiavelli; needs Kalyvas or retire after 10 more analyses)
- **Flagged for merger**: Categorical Blindness (2 obs + counter-evidence,
  self-identified as possible Axiom 8 + Division of Learning extension)
- **Near SUPPORTED threshold**: Ideological Judo (6 obs, 8.6%), Moral
  Infrastructure (6 obs, 8.7%) — both need ratio above 10%
- **Well-observed but ratio-limited**: Relay Class (6), Boomerang (5),
  Middle Stratum Trap (5), Dispossession Cycle (5) — broad layers make
  the 10% ratio threshold hard to reach
- **Threshold scaling issue noted**: the min_ratio=10% threshold penalizes
  broad-layer patterns where nearly all sources are "relevant." Consider
  adjusting thresholds when corpus exceeds 80 sources.

### 5. Non-anglophone extraction — Achille Mbembe *Necropolitics* (2026-03-06, updated 2026-03-12)
SOURCE: Coverage gaps (Step 7)
~80% US-focused corpus. Mbembe addresses: non-anglophone gap, Africa gap,
Physical & Coercive layer from below, Position 3 perspective. Likely
corroborates Economy of Violence, Constitutive Violence, Boomerang.
Alternative: Samir Amin (dependency theory, Economic layer, Global South).
Also: analyse material from Le Monde Diplomatique, The Wire India, or
Al Jazeera Arabic edition.

### 6. Build Surveillance layer instrument (2026-03-09, updated 2026-03-12)
SOURCE: Instrument gaps (Step 6), Layer coverage (Step 7)
Surveillance & Information is least-represented primary layer (10/36).
Four proposed instruments remain partial:
- Racializing Surveillance Detection Protocol — needs Benjamin, Eubanks, Noble
- Critical Biometric Consciousness Checklist — needs engineering sources
- Domestic Covert Action Technique Taxonomy — needs post-1971 sources
- Kleptocratic Infrastructure Detection — needs Burgis, Bullough, OCCRP
Extracting Benjamin (*Race After Technology*) advances the first AND
addresses the Surveillance layer gap.

### 7. Rebalance SAMPLE pool (2026-03-12)
SOURCE: Calibration (Step 2)
Calibration null case rate (80%) is above the 70% upper target. The pool
may be overweighted toward null-case-likely categories. Add 3-4 entries
in categories where power dynamics are more likely (government press
releases, corporate announcements, think tank policy papers) to bring
the expected null rate closer to 50%.

### 8. Extension discipline for pattern variants (2026-03-12)
SOURCE: Red team 2 (2026-03-12)
New pattern extensions (Anticipatory Obedience to inter-state, Relay Class
to voluntary alliance subordination) must include explicit falsification
conditions specific to the extension. Without answering "what would
demonstrate this extension doesn't apply?", the extension is assertion
not analysis. Consider adding a `falsification_condition` field to pattern
variant records in patterns.yaml.

### 9. Church Committee broader extraction (2026-03-09)
SOURCE: Extract gaps (Step 5)
CIA domestic activities chapters would test The Boomerang in a second
institutional context (currently only FBI). Domestic intelligence chapter
strengthens Targeting Gradient and Structural Demand for Covert Action.
AVAILABILITY: AARC Library (permanent link).

---

## Longer-term

### 10. YAML migration integrity check (2026-03-12)
SOURCE: Red team 2 (2026-03-12)
Verify that pattern notes and variant annotations survived the markdown-to-YAML
migration intact. Confirm no analytical nuance was lost in computed fields.
Spot-check 5 patterns' observed_in entries against original analysis files.

### 11. Contemporary circumvention successes (2026-03-06)
SOURCE: Circumventions audit
Circumvention documentation skews toward failure modes and historical
examples. Deliberately source measured-success cases:
- Victorious labor organizing campaigns (2020-present)
- Successful antitrust enforcement outcomes
- Effective ballot initiatives / electoral shifts

### 12. Comparative international analysis track (2026-03-06)
SOURCE: Selection bias (Step 2)
Run parallel analyses on same domains from different geopolitical
positions (e.g., Iran conflict: Guardian + Al Jazeera + IRGC statements;
corporate capture: US antitrust + EU competition law + Chinese state
capacity). Would test whether patterns hold cross-nationally.

### 13. Longitudinal case study (2026-03-06)
SOURCE: Red team observation
Most analyses are synchronic (snapshot). A diachronic case study
(same institution across 50 years) would test whether patterns thought
to be structural are actually contingent on specific historical
conjunctions. Candidate: US telecommunications regulation 1970-2020
(tests Capture Pipeline, Formal Transformation/Structural Continuity,
Peacetime Ratchet across the AT&T breakup and reconsolidation cycle).

### 14. Disaggregate Structural Demand for Propaganda (2026-03-06, updated 2026-03-09)
SOURCE: Pattern gaps (Step 4)
This pattern conflates supply-side (ruling demand for propaganda
production) with demand-side (subordinate psychological need for
coherent narrative). These may be distinct mechanisms. Now at 2/59
sources — PRELIMINARY. The Atlantic "gullicism" essay corroborated
the demand side; supply side still needs independent corroboration.

---

## Completed

### SAMPLE escalations — completed 2026-03-13
Both escalations acted on: DW Swiss broadcasting (Democracy-Oligarchy
Coexistence inverse variant, Peacetime Ratchet extension); Haaretz/Iran
(acted on via Reuters wire story analysis as Roy Iran speech analysis).

### Axioms 4 and 7 adversarial tests — completed 2026-03-12
Axiom 7 tested via NTSB DCA investigation (first challenge — stated purpose
matches actual function at institution level). Axiom 4 tested via AI
deepfakes in elections (first evidence — mechanism has clear structural
parallels; supported). Both adversarial inputs. See analyses.

### Position 2 testimony (Terkel) — completed 2026-03-12
Extracted Terkel *Working* — first Position 2 source, 8 principles, 7
pattern corroborations from the governed perspective, 2 IC-1 flags (Axiom 9:
workplace coercion visible; Axiom 10: understanding inert without leverage).

### Red team #2 — completed 2026-03-12
Second self-examination (IC-3). Confirmation bias risk downgraded HIGH →
MEDIUM. Key findings: null case never won organically, Axiom 4 untested,
Axiom 7 unchallenged, position 2 still absent, pattern extensions risk
unfalsifiability. Six recommendations produced (test Axioms 4/7, prune
patterns, extension discipline, position 2 acquisition, YAML migration
check). See `evidence/2026-03-12-red-team-second-self-examination.md`.

### Backlog #3: Reach SAMPLE calibration threshold — completed 2026-03-12
5 samples reached. Calibration null case rate: 80% (above 70% target —
pool rebalance recommended, see #9). Delta: +27pp vs analysis rate,
confirming positive selection bias in analysis diet.

### Backlog #1 (original): File unfiled counter-evidence entries — completed 2026-03-09
Filed Fanon/Economy of Violence perspective asymmetry (complicates Axiom 9)
and propaganda demand symmetry (complicates Axioms 5, 9). Added
counter-evidence filing check to methodology.md to prevent recurrence.

### Backlog #1 (Browne): File Browne IC-1 evidence entries — completed 2026-03-06
Filed Axiom 3 (forced visibility, 6th complication), Axiom 8 (constitutive
absence, new entry), Axiom 10 (dark sousveillance, 5th item). Commit
`f8db6c80`.

### Backlog #6: Project 2025 remaining chapters — completed 2026-03-08
All 10 chapters scanned (Option C). Produced 2 new principles (P7: Tax
Architecture as Structural Lock-In, P8: Financial Sovereignty Withdrawal).
Key finding: identical capture template across all domains confirms Capture
Pipeline as architectural feature.
