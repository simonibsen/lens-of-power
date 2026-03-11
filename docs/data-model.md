# Data Model

```mermaid
erDiagram
    ANALYSIS ||--o{ PATTERN_MATCH : "matches"
    ANALYSIS }o--o{ ANALYSIS : "cross-references"
    ANALYSIS ||--|{ LAYER : "layers (primary)"
    ANALYSIS }o--o{ LAYER : "layers (secondary)"
    ANALYSIS }o--o{ LAYER : "layers (absent)"
    ANALYSIS }o--|{ DOMAIN : "domain"
    ANALYSIS }o--|| POSITION : "source position"
    ANALYSIS }o--o| CALIBRATION_ENTRY : "escalated from"

    PATTERN_MATCH }o--|| PATTERN : "pattern"
    PATTERN_MATCH ||--|| FINDING_STATUS : "status"

    PATTERN ||--|{ LAYER : "layers"
    PATTERN }o--o{ CIRCUMVENTION : "counteracted by"
    PATTERN ||--o{ OBSERVED_IN : "observed in (computed)"
    PATTERN }o--o{ EVIDENCE : "counter-evidence (computed)"

    PRINCIPLE ||--|{ LAYER : "layers"
    PRINCIPLE ||--o{ KEY_PATTERN : "key patterns"
    PRINCIPLE }o--o{ IC1_FLAG : "ic1 flags"
    PRINCIPLE }o--o{ INSTRUMENT : "produced"
    PRINCIPLE }o--o{ INSTRUMENT : "proposed"
    PRINCIPLE }o--|| POSITION : "position"
    PRINCIPLE }o--o| SOURCE_RECORD : "provenance"

    KEY_PATTERN }o--|| PATTERN : "pattern"

    IC1_FLAG }o--|| AXIOM : "challenges"

    CIRCUMVENTION ||--|{ LAYER : "layers"
    CIRCUMVENTION ||--|{ PATTERN : "counteracts"

    EVIDENCE }o--|| AXIOM : "relationship"

    SOURCE_RECORD ||--|| PROVENANCE_TIER : "tier"

    CALIBRATION_ENTRY }o--|| NULL_CASE_OUTCOME : "null case"

    ANALYSIS {
        string id PK
        string title
        date source_date
        string source_name
        string source_type
        string url
        string null_case
        string null_case_level
        boolean adversarial
        string origin
        string ic5_flag
        string commit
    }

    PATTERN {
        string id PK
        string name
        string file
        string statement
        float confidence_ratio "computed"
        string confidence_level "computed"
        int relevant_corpus_size "computed"
        int corr_count "computed"
    }

    PRINCIPLE {
        string id PK
        string source_name
        string source_title
        int source_year
        string provenance_tier
        string[] principles_list
    }

    INSTRUMENT {
        string id PK
        string file
        string status
    }

    CIRCUMVENTION {
        string id PK
        string name
    }

    EVIDENCE {
        string id PK
        string relationship
        string[] patterns
    }

    AXIOM {
        int id PK
        string short
    }

    LAYER {
        string id PK
        string name
    }

    DOMAIN {
        string id PK
        string description
    }

    POSITION {
        int id PK
        string label
    }

    SOURCE_RECORD {
        string id PK
        string source
        string provenance_tier
        string hash
        string[] archive_urls
        string extraction_status
    }

    CALIBRATION_ENTRY {
        date date
        string outlet
        string article
        string category
        string null_case
        string escalation
        string escalated_to
    }

    PATTERN_MATCH {
        string variant
        string note
    }

    KEY_PATTERN {
        string variant
        string note
    }

    OBSERVED_IN {
        string source_id
        string source_type
        string variant
        string note
    }

    IC1_FLAG {
        int axiom
        string note
    }

    PROVENANCE_TIER {
        string id PK
    }

    NULL_CASE_OUTCOME {
        string id PK
    }

    FINDING_STATUS {
        string id PK
    }
```

## Key relationships

- **ANALYSIS → PATTERN**: Many-to-many via `patterns_matched` (each match carries status, variant, note)
- **PRINCIPLE → PATTERN**: Many-to-many via `key_patterns` (same structure as analysis matches)
- **PATTERN.observed_in**: **Computed** — union of analysis matches + principle key_patterns
- **PATTERN.confidence**: **Computed** — from observed_in count vs. relevant corpus, using config thresholds
- **PATTERN.counter_evidence**: **Computed** — from evidence entries with `challenges`/`complicates` relationship
- **CIRCUMVENTION ↔ PATTERN**: Bidirectional — circumvention counteracts pattern(s); pattern lists its circumventions
- **PRINCIPLE → AXIOM**: IC-1 flags record when a source challenges an axiom's falsification condition
- **CALIBRATION_ENTRY → ANALYSIS**: Optional — when a SAMPLE mode read escalates to a full analysis
