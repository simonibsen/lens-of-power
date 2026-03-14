# Framework Backlog

> Role: Living document capturing prioritized recommendations from SUGGEST
> mode diagnostics. Refreshed each time SUGGEST mode runs. Items are removed
> when completed or superseded. Dates track when each recommendation was
> first surfaced.

Last diagnostic: 2026-03-13 (41 analyses, 32 patterns, 28 extracted sources, 7 instruments, 7 SAMPLE runs)

---

## Immediate priority

### 1. Test Axioms 1, 2, and 6 — zero challenging or complicating evidence (2026-03-13)
SOURCE: Evidence balance (Step 3)
Axioms 1 (layers simultaneous), 2 (layers reinforce), and 6 (language
first) have only supporting evidence — no challenges, no complicates. If
no evidence could complicate them, they are beliefs not analytical tools
(IC-1). Axiom 6 is the most testable: material where power shifted without
preceding language change would challenge it. Axiom 1: a genuinely
single-layer system. Axiom 2: control at one layer undermining another.
ACTION: Deliberately analyze material where these axioms are likely to
fail. Candidate for Axiom 6: a military coup or natural disaster response
where force preceded framing.

### 2. Source additional Position 2 / Position 3 testimony (2026-03-06, updated 2026-03-13)
SOURCE: Coverage gaps (Step 7)
Three Position 2 sources extracted: Terkel *Working* (workplace, 8 principles),
Desmond *Evicted* (housing, 7 principles), and Ehrenreich *Nickel and Dimed*
(low-wage service work, 6 principles). All three produced IC-1 flags for
Axioms 9 and 10 from below — three independent domains now confirm the
complication. Position 3 remains at 1 source (Fanon only).
ACTION: Extract Ai Weiwei memoir (Position 2/3, non-Western, Surveillance
layer). For Position 3: consider Alinsky *Rules for Radicals* or Guevara
*Guerrilla Warfare* as tactical-revolutionary perspectives.

---

## Short-term

### 3. Increase adversarial input rate to 20% (2026-03-09, updated 2026-03-13)
SOURCE: Selection bias (Step 2)
7/41 (17%) approaching the 20% threshold. NCSL youth soccer board meeting
added (null case accepted at HIGH). Continue including null-case-likely
inputs in future analyses. Candidates: municipal utility rate filing,
scientific instrument calibration paper, routine corporate earnings call.

### 4. Rebalance SAMPLE pool (2026-03-12, updated 2026-03-13)
SOURCE: Calibration (Step 2)
Calibration null case rate now 86% (6/7) — above the 70% upper target.
Delta: +25pp vs analysis rate (61%), confirming positive selection bias in
analysis diet. But the pool itself is overweighted toward null-case-likely
categories. Add 3-4 entries in categories where power dynamics are more
likely (government press releases, corporate announcements, think tank
policy papers) to bring the expected null rate closer to 50%.

### 5. Address geographic concentration (~80% US-focused) (2026-03-06, updated 2026-03-13)
SOURCE: Coverage gaps (Step 7), Selection bias (Step 2)
~80% US-focused corpus. The framework claims universal mechanisms (Axiom 4)
but has tested them almost entirely in US material. Non-Western perspectives
underrepresented in both analyses and extractions.
ACTION: Extract Mbembe *Necropolitics* (Africa, Physical & Coercive from
below, Position 3 perspective). Likely corroborates Economy of Violence,
Constitutive Violence, Boomerang. Alternative: Samir Amin (dependency
theory, Economic layer, Global South). Also: analyse material from Le Monde
Diplomatique, The Wire India, or Al Jazeera Arabic edition. Let SAMPLE mode
surface non-anglophone outlets organically.

### 6. Build Surveillance layer instrument (2026-03-09, updated 2026-03-13)
SOURCE: Instrument gaps (Step 6), Layer coverage (Step 7)
Surveillance & Information is least-represented primary layer (~5/41
analyses). Four proposed instruments remain partial:
- Racializing Surveillance Detection Protocol — needs Benjamin, Eubanks, Noble
- Critical Biometric Consciousness Checklist — needs engineering sources
- Domestic Covert Action Technique Taxonomy — needs post-1971 sources
- Kleptocratic Infrastructure Detection — needs Burgis, Bullough, OCCRP
ACTION: Extract Benjamin (*Race After Technology*) — advances the Protocol
AND addresses the Surveillance layer gap simultaneously.

### 7. Review PRELIMINARY patterns — threshold scaling (2026-03-06, updated 2026-03-13)
SOURCE: Pattern gaps (Step 4), Red team 2 (2026-03-12), Pattern review (2026-03-13)
12 patterns at PRELIMINARY (38% of all patterns). Pattern review completed
2026-03-13:
- **Flagged for retirement**: Economy of Violence (2 obs + counter-evidence,
  only Machiavelli; needs Kalyvas or retire after analysis #50)
- **Flagged for merger**: Categorical Blindness (2 obs + counter-evidence,
  self-identified as possible Axiom 8 + Division of Learning extension)
- **Near SUPPORTED threshold**: Ideological Judo (6 obs, 9%), Moral
  Infrastructure (6 obs, 9%) — both need ratio above 10%
- **Well-observed but ratio-limited**: Relay Class (5), Boomerang (5),
  Middle Stratum Trap (4-5), Dispossession Cycle (5) — broad layers make
  the 10% ratio threshold hard to reach
- **Threshold scaling issue**: the min_ratio=10% penalizes broad-layer
  patterns. Consider adjusting when corpus exceeds 80 sources.

### 8. Extension discipline for pattern variants (2026-03-12)
SOURCE: Red team 2 (2026-03-12)
New pattern extensions (Anticipatory Obedience to inter-state, Relay Class
to voluntary alliance subordination) must include explicit falsification
conditions specific to the extension. Consider adding a
`falsification_condition` field to pattern variant records in patterns.yaml.

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
coherent narrative). These may be distinct mechanisms. Now at 3/70
sources — PRELIMINARY. The Atlantic "gullicism" essay corroborated
the demand side; supply side still needs independent corroboration.

---

## Completed

### Ehrenreich extraction — completed 2026-03-13
Extracted *Nickel and Dimed* — third Position 2 source, 6 principles.
Third independent domain (low-wage service work) confirming Axioms 9
and 10 complications from below.

### NCSL adversarial analysis — completed 2026-03-13
Youth soccer board meeting — null case accepted at HIGH. Adversarial
ratio now 7/41 (17%).

### PRELIMINARY pattern review — completed 2026-03-13
Full review of 12 PRELIMINARY patterns. Economy of Violence flagged
for retirement, Categorical Blindness flagged for merger, threshold
scaling concern documented. Build pipeline bug fixed (+165 edges).

### SAMPLE escalations — completed 2026-03-13
All three escalations acted on: DW Swiss broadcasting (Democracy-Oligarchy
Coexistence inverse variant, Peacetime Ratchet extension); Haaretz/Iran
(acted on via Reuters wire story analysis); RAND Medicaid (analyzed).

### Axioms 4 and 7 adversarial tests — completed 2026-03-12
Axiom 7 tested via NTSB DCA investigation (first challenge — stated purpose
matches actual function at institution level). Axiom 4 tested via AI
deepfakes in elections (first evidence — mechanism has clear structural
parallels; supported). Both adversarial inputs. See analyses.

### Position 2 testimony (Terkel, Desmond) — completed 2026-03-12
Extracted Terkel *Working* (8 principles) and Desmond *Evicted* (7
principles) — first two Position 2 sources. Both produced IC-1 flags
for Axioms 9 and 10 from below.

### Red team #2 — completed 2026-03-12
Second self-examination (IC-3). Confirmation bias risk downgraded HIGH →
MEDIUM. Key findings: null case never won organically, Axiom 4 untested,
Axiom 7 unchallenged, position 2 still absent, pattern extensions risk
unfalsifiability. See `evidence/2026-03-12-red-team-second-self-examination.md`.

### Backlog #3: Reach SAMPLE calibration threshold — completed 2026-03-12
5 samples reached. Calibration null case rate: 80% (above 70% target —
pool rebalance recommended). Delta: +27pp vs analysis rate, confirming
positive selection bias in analysis diet.

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
