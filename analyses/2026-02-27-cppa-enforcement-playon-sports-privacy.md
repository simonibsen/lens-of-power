# Analysis: CPPA enforcement order against PlayOn Sports — routine privacy regulation

DATE: 2026-02-27

TIME: ~20:00 UTC (order dated February 27, 2026)

SOURCE: California Privacy Protection Agency, Enforcement Division

SOURCE TYPE: regulatory enforcement order (stipulated final order)

SOURCE POSITION: Position 1/4 (regulator exercising authority; intermediary claiming to represent consumer interests)

URL: https://privacy.ca.gov/wp-content/uploads/sites/357/2026/03/Order-of-Decision_PlayOn_Enforcement.pdf

FRAMEWORK STATE: 32 patterns, 23 principles, 6 instruments (commit 65ca5d39)

---

## Narrative

The California Privacy Protection Agency issued a stipulated final order against PlayOn Sports (2080 Media, Inc.), a high school event ticketing company operating GoFan, MaxPreps, and the NFHS Network. PlayOn serves approximately 1,400 California schools and is the official ticketing partner for 80% of all state athletic associations nationwide, having sold over 30 million tickets. The order documents CCPA violations during the period January 2023 through December 2024: PlayOn collected personal information via first- and third-party cookies and MetaPixel, sold and shared that information with advertising, social media, and analytics partners, failed to provide effective opt-out mechanisms, failed to recognize opt-out preference signals, and displayed consent banners that required clicking "Agree" with no alternative — on mobile devices, the banner covered the ticket-use area, making agreement a precondition for using an already-purchased ticket.

The enforcement action follows a standard regulatory pattern. The CPPA opened an investigation in 2024 and subsequently received a consumer complaint. PlayOn cooperated with the investigation, self-remediated its practices in December 2024 — before learning of the investigation, according to the order — and agreed to a stipulated settlement. The order imposes an administrative fine of $1,100,000, requires compliance with all applicable CCPA provisions, mandates quarterly tracking technology scans, requires board-reviewed risk assessments, and requires age-appropriate notice language for services directed at high school audiences. PlayOn neither admits nor denies liability.

The document's absences are scope-appropriate rather than analytically significant. The order does not quantify consumer harm, does not situate PlayOn's practices within industry baselines, and does not address whether the opt-out regulatory model is structurally adequate. These are legitimate analytical questions, but they are outside the scope of an enforcement order, which identifies violations and imposes remedies. The absence of these questions does not serve identifiable interests — it reflects the document's institutional function.

This is the first analysis where the framework's null case assessment is rated HIGH. The non-power explanation — a mid-size company with sloppy privacy practices caught by a functioning regulator — fits the evidence better than any power-dynamics explanation. PlayOn's violations are real but mundane: an outdated privacy policy, missing opt-out infrastructure, a poorly designed consent banner. The company fixed the problems, cooperated with the investigation, and accepted the fine. The regulator investigated, found violations, and issued an order. The process operated as designed.

## Findings

1. **CCPA enforcement operated as designed**
   LAYER: Legal & Regulatory
   STATUS: observed
   The CPPA identified violations, investigated, obtained cooperation, and issued a stipulated order with a fine and compliance requirements. The enforcement process followed the statutory framework without observable deviation or capture.

2. **PlayOn self-remediated before investigation contact**
   LAYER: Legal & Regulatory, Institutional
   STATUS: observed
   PlayOn updated its website, privacy policy, and notice banners in December 2024, before the Enforcement Division contacted the company. This is consistent with a company recognizing its compliance gap and correcting it independently.

3. **Consent architecture eliminated meaningful choice**
   LAYER: Surveillance & Information, Legal & Regulatory
   STATUS: observed
   PlayOn's mobile consent banner covered the ticket-use area, requiring consumers to click "Agree" to tracking in order to use a ticket they had already purchased. No alternative was provided. This structurally eliminated the possibility of informed refusal.

4. **Data selling was operationally marginal**
   LAYER: Economic, Surveillance & Information
   STATUS: observed
   PlayOn ran only one targeted advertising campaign during the two-year relevant period. The tracking infrastructure existed and personal information was sold and shared, but advertising revenue appears to have been a minor part of PlayOn's business model. The violations were structural (the tracking was in place) rather than a core revenue strategy.

5. **Fine proportionality is indeterminate**
   LAYER: Economic, Legal & Regulatory
   STATUS: inferred
   PlayOn's annual gross revenue exceeds $26.625 million (the CCPA applicability threshold). The $1.1M fine represents at most approximately 4% of this minimum. Whether this constitutes a meaningful deterrent or a cost of doing business cannot be determined from the order alone.

6. **Market position created structural dependency**
   LAYER: Economic
   STATUS: inferred
   PlayOn operates as the official ticketing partner for 80% of state associations and is sometimes the only ticket-sale method for events. Consumers who wished to attend high school events had no practical alternative to using PlayOn's platform and accepting its tracking. This dependency is a market condition rather than a manufactured one, but it amplified the impact of the consent architecture violation.

| Actor | Gains | At whose expense |
|-------|-------|------------------|
| CPPA | Institutional legitimacy; precedent-setting enforcement | PlayOn (fine, compliance costs) |
| PlayOn | Resolution of investigation; release from claims | $1.1M fine + ongoing compliance obligations |
| Consumers (students, families) | Improved privacy practices going forward | No direct remedy for past data selling; burden of opting out remains on them |
| Ad/analytics partners | Not addressed | Relationship with PlayOn may be curtailed |

## Implications

This enforcement action does not reveal hidden power dynamics. It documents a regulator performing its statutory function against a company that violated privacy law through compliance neglect rather than strategic exploitation. The framework's value in this analysis is not in what it reveals about PlayOn but in what it reveals about the framework itself: the capacity to produce an honest "the null case holds here" was previously untested.

The secondary analytical question — whether the CCPA's opt-out model, which places the burden on consumers rather than businesses, is structurally adequate — is worth investigating but falls outside this enforcement order's scope. A structural critique of the opt-out model would require analyzing the regulatory framework itself, not an individual enforcement action within it.

## Watch

- Whether the CPPA pursues enforcement against larger companies (Meta, Google, major ad networks) with similar vigor or concentrates on mid-size targets with less capacity to litigate
- Whether the risk assessment mandate (particularly the board-reviewed assessment requirement) produces meaningful privacy governance at PlayOn or becomes a compliance formality
- Whether the $1.1M fine produces any observable change in industry-wide ticketing-platform privacy practices

## Analytical apparatus

INSTRUMENTS APPLIED:
- Positional lens (instruments/positional-lens.md) — identified CPPA as Position 1/4 (regulator/intermediary); identified absent voices (Position 2: consumers; Position 3: structural critics of the opt-out model)

PRINCIPLES REFERENCED:
- None directly applied. The material did not activate framework principles because the null case held.

PATTERNS MATCHED:
- Inversion of Stated Purpose — PARTIAL match only. PlayOn's privacy policy claimed it did not sell personal information while it did. The consent banner stated "agreement" while structurally eliminating the possibility of refusal. However, these inversions appear to reflect compliance negligence rather than strategic deployment of the pattern. The inversion is present in form but absent in intent.

PATTERNS NOT MATCHED:
- Layered Redundancy — not applicable; single-mechanism compliance failure
- Capture Pipeline — not applicable; no institutional capture observed
- Division of Learning — technically present (PlayOn knew more about consumers' data than consumers did) but generic to all tracking-technology businesses rather than strategically deployed
- Manufactured Scarcity — PlayOn's monopolistic market position exists but is a market condition, not a manufactured one
- Democracy-Oligarchy Coexistence — not applicable

## Null case

**Initial null case** (stated at Step 1, before analysis): PlayOn is a mid-size sports tech company that grew fast, neglected privacy compliance, and got caught by a new regulator exercising its mandate. The violations are real but mundane. The company fixed the problems before knowing it was under investigation. This is routine regulatory enforcement.

**Null case after analysis** (Step 5 revisitation): The initial null case survived the full analytical procedure without weakening. Steps 2-4 identified no evidence that power dynamics exceed what the null case explains. The consent banner architecture (Finding 3) and market dependency (Finding 6) are the closest to power-dynamics findings, but both are better explained by poor design and market conditions than by strategic control.

**Null case plausibility**: HIGH. The non-power explanation fits the evidence better than the power-dynamics explanation.

**IC-5 note**: The LLM's training likely overrepresents the regulatory and institutional perspective on this material. Perspectives of the affected consumers — particularly minors and families in communities where PlayOn is the only ticketing option — are absent from both the source material and likely from training data. However, their inclusion would not change the null case assessment; it would deepen the harm analysis without introducing a power-dynamics explanation that the evidence does not support.

---

## Analytical working

> The structured steps below are the production process that produced
> the analysis above. They exist for auditability and review (IC-3).
> They are not intended for primary reading.

### Step 1: DECOMPOSE

CLAIMS:
- PlayOn operates GoFan, MaxPreps, NFHS Network for high school events (fact)
- 80% of state associations; 30M+ tickets; ~1,400 CA schools (fact)
- Collected personal info via cookies, MetaPixel; sold/shared with ad partners (fact)
- Notice banners required "Agree" with no alternative; mobile banner covered ticket-use area (fact, supported by screenshots)
- Failed to recognize/honor opt-out preference signals (fact)
- Privacy policy not updated July 2022 – February 2024; falsely claimed no selling (fact)
- Self-remediated December 2024, before learning of investigation (fact)
- Ran only one targeted ad campaign during relevant period (fact)
- Fine: $1,100,000; compliance requirements; quarterly scans; risk assessments (order)
- PlayOn neither admits nor denies liability (legal)

FRAMING: Legal-administrative. Resolution-oriented. Violations as compliance failures.
EMOTIONAL REGISTER: Neutral/bureaucratic.
INITIAL NULL CASE: Routine enforcement of compliance failure by a functioning regulator. Company neglected privacy, got caught, cooperated, fixed it.

### Step 2: SOURCE

SOURCE: CPPA Enforcement Division
POSITION: Position 1 (regulator) with Position 4 characteristics (intermediary/consumer representative)
INCENTIVES: Institutional legitimacy for a new agency. Successful enforcement cases demonstrate function.
WOULD NOT SAY: Whether the fine is proportionate, whether enforcement is adequate at industry scale, whether the opt-out model is structurally sufficient.
AMPLIFICATION: Published as part of agency enforcement record.

IC-5: Training data likely overrepresents regulatory/institutional perspective.

### Step 3: LOCATE

LAYERS ACTIVE: Legal & Regulatory (primary), Surveillance & Information, Economic
LAYERS ACTIVE BUT ABSENT FROM SOURCE: Thought & Narrative (consent banner as manufactured consent — scope-appropriate absence for enforcement order)
LAYER INTERACTIONS: Legal & Regulatory --constrains--> Surveillance & Information; Economic --motivates--> Surveillance & Information; Legal & Regulatory --remedies--> Economic
CONFIRMS: None strongly.
CONTRADICTS: None.
EXTENDS: Test case for null-case-accepted result.

### Step 4: CONNECT

ECHOES: Meta consent architecture (2026-03-01 analysis) — structural resemblance in the "agree-or-don't-use" pattern, but different scale and intent.
PATTERN MATCH: Inversion of Stated Purpose — partial (form present, strategic intent absent).
NEW PATTERN: None.

### Step 5: INVERT

INVERSE CLAIM: CPPA using PlayOn for legitimacy-building. Plausible at margins but not supported over null case.
STRONGEST DEFENSE: PlayOn cooperated, self-remediated before contact, ran only one ad campaign. Consistent with compliance neglect, not strategic exploitation.
NULL CASE: HIGH plausibility. Non-power explanation fits evidence better.
FALSIFIABLE BY: Evidence of selective prosecution (targeting small firms while avoiding large ones).
LLM BIAS CHECK: Not hedging. Null case is genuinely strong.

### Step 6: ABSENT

MISSING QUESTIONS: Consumer harm quantification; fine proportionality; industry baseline.
ABSENT VOICES: Position 2 (consumers), Position 3 (structural critics of opt-out model).
MISSING EVIDENCE: Independence of self-remediation; CPPA enforcement portfolio context.
EXCLUDED ALTERNATIVES: Non-commercial ticketing platforms; opt-in regulatory models.
LLM BLIND SPOTS: Consumer experience; minor/family perspectives.

### Step 7: SO-WHAT

IMPLICATIONS: Framework can produce honest null-case-accepted result. Secondary question (opt-out model adequacy) warrants separate analysis.
WATCH: CPPA enforcement trajectory; risk assessment outcomes; industry response.
INVESTIGATE: None required from this material.
FRAMEWORK UPDATE: First HIGH null case. Record as adversarial-input data point for framework health.
MADE VISIBLE: The framework's capacity to distinguish power-dynamics material from non-power-dynamics material.
