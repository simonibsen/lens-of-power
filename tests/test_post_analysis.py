"""Tests for tools/post-analysis.py."""

import importlib
import textwrap
from pathlib import Path

import pytest

# Import the module with hyphens in the name
import importlib.util
spec = importlib.util.spec_from_file_location(
    "post_analysis",
    Path(__file__).resolve().parent.parent / "tools" / "post-analysis.py",
)
post_analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(post_analysis)

validate_entry = post_analysis.validate_entry
compute_confidence = post_analysis.compute_confidence
build_analysis_entry = post_analysis.build_analysis_entry
recompute_observed_in = post_analysis.recompute_observed_in
recompute_counter_evidence = post_analysis.recompute_counter_evidence
parse_frontmatter = post_analysis.parse_frontmatter


# ════════════════════════════════════════════════════════════════════
# validate_entry
# ════════════════════════════════════════════════════════════════════


class TestValidateEntry:
    """Tests for validate_entry()."""

    def test_valid_entry_passes(self, minimal_config, sample_frontmatter):
        entry = _frontmatter_to_entry(sample_frontmatter)
        errors = validate_entry(entry, minimal_config)
        assert errors == []

    def test_missing_required_field(self, minimal_config, sample_frontmatter):
        entry = _frontmatter_to_entry(sample_frontmatter)
        del entry["title"]
        errors = validate_entry(entry, minimal_config)
        assert any("Missing required field: title" in e for e in errors)

    def test_missing_multiple_fields(self, minimal_config):
        entry = {"id": "test"}
        errors = validate_entry(entry, minimal_config)
        assert len(errors) >= 5  # several required fields missing

    def test_invalid_source_type(self, minimal_config, sample_frontmatter):
        sample_frontmatter["source_type"] = "nonexistent_type"
        entry = _frontmatter_to_entry(sample_frontmatter)
        errors = validate_entry(entry, minimal_config)
        assert any("Invalid source_type" in e for e in errors)

    def test_invalid_position(self, minimal_config, sample_frontmatter):
        sample_frontmatter["position"] = [99]
        entry = _frontmatter_to_entry(sample_frontmatter)
        errors = validate_entry(entry, minimal_config)
        assert any("Invalid position" in e for e in errors)

    def test_invalid_domain(self, minimal_config, sample_frontmatter):
        sample_frontmatter["domain"] = ["nonexistent_domain"]
        entry = _frontmatter_to_entry(sample_frontmatter)
        errors = validate_entry(entry, minimal_config)
        assert any("Invalid domain" in e for e in errors)

    def test_invalid_layer(self, minimal_config, sample_frontmatter):
        sample_frontmatter["layers_primary"] = ["nonexistent_layer"]
        entry = _frontmatter_to_entry(sample_frontmatter)
        errors = validate_entry(entry, minimal_config)
        assert any("Invalid layer" in e for e in errors)

    def test_invalid_null_case(self, minimal_config, sample_frontmatter):
        sample_frontmatter["null_case"] = "invalid"
        entry = _frontmatter_to_entry(sample_frontmatter)
        errors = validate_entry(entry, minimal_config)
        assert any("Invalid null_case" in e for e in errors)

    def test_invalid_finding_status(self, minimal_config, sample_frontmatter):
        sample_frontmatter["patterns_matched"] = [
            {"pattern": "test", "status": "wrong"}
        ]
        entry = _frontmatter_to_entry(sample_frontmatter)
        errors = validate_entry(entry, minimal_config)
        assert any("Invalid finding status" in e for e in errors)

    def test_pattern_matched_missing_pattern_field(self, minimal_config, sample_frontmatter):
        sample_frontmatter["patterns_matched"] = [{"status": "observed"}]
        entry = _frontmatter_to_entry(sample_frontmatter)
        errors = validate_entry(entry, minimal_config)
        assert any("missing 'pattern' field" in e for e in errors)

    def test_none_layers_secondary_accepted(self, minimal_config, sample_frontmatter):
        """layers_secondary and layers_absent can be None or empty."""
        sample_frontmatter["layers_secondary"] = None
        sample_frontmatter["layers_absent"] = None
        entry = _frontmatter_to_entry(sample_frontmatter)
        errors = validate_entry(entry, minimal_config)
        assert errors == []

    def test_validates_against_real_config(self, config, sample_frontmatter):
        """Validate against the real config.yaml."""
        entry = _frontmatter_to_entry(sample_frontmatter)
        errors = validate_entry(entry, config)
        assert errors == []


# ════════════════════════════════════════════════════════════════════
# compute_confidence
# ════════════════════════════════════════════════════════════════════


class TestComputeConfidence:
    """Tests for compute_confidence()."""

    def test_no_layers_returns_none(self, thresholds):
        pattern = {"layers": [], "observed_in": [], "counter_evidence": []}
        compute_confidence(pattern, [], [], thresholds)
        assert pattern["confidence_level"] is None
        assert pattern["confidence_ratio"] is None

    def test_preliminary_few_sources(self, thresholds):
        pattern = {
            "layers": ["thought_narrative"],
            "observed_in": [{"source_id": "a1"}],
            "counter_evidence": [],
        }
        analyses = [
            {"layers_primary": ["thought_narrative"], "layers_secondary": [], "layers_absent": []},
        ] * 10
        compute_confidence(pattern, analyses, [], thresholds)
        assert pattern["confidence_level"] == "PRELIMINARY"
        assert pattern["relevant_corpus_size"] == 10

    def test_supported_threshold(self, thresholds):
        pattern = {
            "layers": ["thought_narrative"],
            "observed_in": [{"source_id": f"a{i}"} for i in range(3)],
            "counter_evidence": [],
        }
        # 20 relevant sources, 3 observed = 15% > 10%
        analyses = [
            {"layers_primary": ["thought_narrative"], "layers_secondary": [], "layers_absent": []},
        ] * 20
        compute_confidence(pattern, analyses, [], thresholds)
        assert pattern["confidence_level"] == "SUPPORTED"

    def test_established_threshold(self, thresholds):
        pattern = {
            "layers": ["thought_narrative"],
            "observed_in": [{"source_id": f"a{i}"} for i in range(5)],
            "counter_evidence": [],
        }
        # 20 relevant sources, 5 observed = 25% > 20%
        analyses = [
            {"layers_primary": ["thought_narrative"], "layers_secondary": [], "layers_absent": []},
        ] * 20
        compute_confidence(pattern, analyses, [], thresholds)
        assert pattern["confidence_level"] == "ESTABLISHED"

    def test_counter_evidence_blocks_established(self, thresholds):
        pattern = {
            "layers": ["thought_narrative"],
            "observed_in": [{"source_id": f"a{i}"} for i in range(5)],
            "counter_evidence": ["some_evidence_id"],
        }
        analyses = [
            {"layers_primary": ["thought_narrative"], "layers_secondary": [], "layers_absent": []},
        ] * 20
        compute_confidence(pattern, analyses, [], thresholds)
        assert pattern["confidence_level"] == "SUPPORTED"  # blocked from ESTABLISHED

    def test_ratio_below_threshold_stays_preliminary(self, thresholds):
        """Even with 3+ sources, if ratio < 10% stays PRELIMINARY."""
        pattern = {
            "layers": ["thought_narrative"],
            "observed_in": [{"source_id": f"a{i}"} for i in range(3)],
            "counter_evidence": [],
        }
        # 100 relevant sources, 3 observed = 3% < 10%
        analyses = [
            {"layers_primary": ["thought_narrative"], "layers_secondary": [], "layers_absent": []},
        ] * 100
        compute_confidence(pattern, analyses, [], thresholds)
        assert pattern["confidence_level"] == "PRELIMINARY"

    def test_principles_count_in_corpus(self, thresholds):
        """Principles with overlapping layers count as relevant corpus."""
        pattern = {
            "layers": ["economic"],
            "observed_in": [{"source_id": f"a{i}"} for i in range(3)],
            "counter_evidence": [],
        }
        analyses = [
            {"layers_primary": ["economic"], "layers_secondary": [], "layers_absent": []},
        ] * 5
        principles = [
            {"layers": ["economic"]},
        ] * 5
        compute_confidence(pattern, analyses, principles, thresholds)
        assert pattern["relevant_corpus_size"] == 10  # 5 analyses + 5 principles

    def test_non_overlapping_layers_not_counted(self, thresholds):
        pattern = {
            "layers": ["economic"],
            "observed_in": [{"source_id": "a1"}],
            "counter_evidence": [],
        }
        analyses = [
            {"layers_primary": ["thought_narrative"], "layers_secondary": [], "layers_absent": []},
        ] * 10
        compute_confidence(pattern, analyses, [], thresholds)
        assert pattern["relevant_corpus_size"] == 0

    def test_zero_relevant_zero_ratio(self, thresholds):
        pattern = {
            "layers": ["economic"],
            "observed_in": [],
            "counter_evidence": [],
        }
        compute_confidence(pattern, [], [], thresholds)
        assert pattern["confidence_ratio"] == 0.0
        assert pattern["confidence_level"] == "PRELIMINARY"


# ════════════════════════════════════════════════════════════════════
# recompute_observed_in
# ════════════════════════════════════════════════════════════════════


class TestRecomputeObservedIn:
    """Tests for recompute_observed_in()."""

    def test_builds_from_analyses(self):
        patterns = [{"id": "p1", "observed_in": []}]
        analyses = [
            {
                "id": "a1",
                "patterns_matched": [
                    {"pattern": "p1", "variant": None, "note": "test note"},
                ],
            }
        ]
        recompute_observed_in(patterns, analyses, [])
        assert len(patterns[0]["observed_in"]) == 1
        obs = patterns[0]["observed_in"][0]
        assert obs["source_id"] == "a1"
        assert obs["source_type"] == "analysis"
        assert obs["note"] == "test note"

    def test_builds_from_principles(self):
        patterns = [{"id": "p1", "observed_in": []}]
        principles = [
            {
                "id": "pr1",
                "key_patterns": [
                    {"pattern": "p1", "variant": "v1", "note": "principle note"},
                ],
            }
        ]
        recompute_observed_in(patterns, [], principles)
        assert len(patterns[0]["observed_in"]) == 1
        obs = patterns[0]["observed_in"][0]
        assert obs["source_id"] == "pr1"
        assert obs["source_type"] == "principle"
        assert obs["variant"] == "v1"

    def test_combines_analyses_and_principles(self):
        patterns = [{"id": "p1", "observed_in": []}]
        analyses = [
            {"id": "a1", "patterns_matched": [{"pattern": "p1"}]},
        ]
        principles = [
            {"id": "pr1", "key_patterns": [{"pattern": "p1"}]},
        ]
        recompute_observed_in(patterns, analyses, principles)
        assert len(patterns[0]["observed_in"]) == 2

    def test_unknown_pattern_warned_not_crash(self, capsys):
        patterns = [{"id": "p1", "observed_in": []}]
        analyses = [
            {"id": "a1", "patterns_matched": [{"pattern": "unknown_pattern"}]},
        ]
        recompute_observed_in(patterns, analyses, [])
        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "unknown_pattern" in captured.out
        assert len(patterns[0]["observed_in"]) == 0

    def test_replaces_existing_observed_in(self):
        """observed_in is fully recomputed, not appended."""
        patterns = [
            {"id": "p1", "observed_in": [{"source_id": "old", "source_type": "analysis"}]}
        ]
        analyses = [
            {"id": "a1", "patterns_matched": [{"pattern": "p1"}]},
        ]
        recompute_observed_in(patterns, analyses, [])
        assert len(patterns[0]["observed_in"]) == 1
        assert patterns[0]["observed_in"][0]["source_id"] == "a1"

    def test_empty_patterns_matched(self):
        patterns = [{"id": "p1", "observed_in": []}]
        analyses = [{"id": "a1", "patterns_matched": []}]
        recompute_observed_in(patterns, analyses, [])
        assert len(patterns[0]["observed_in"]) == 0

    def test_none_patterns_matched(self):
        patterns = [{"id": "p1", "observed_in": []}]
        analyses = [{"id": "a1", "patterns_matched": None}]
        recompute_observed_in(patterns, analyses, [])
        assert len(patterns[0]["observed_in"]) == 0


# ════════════════════════════════════════════════════════════════════
# recompute_counter_evidence
# ════════════════════════════════════════════════════════════════════


class TestRecomputeCounterEvidence:
    """Tests for recompute_counter_evidence()."""

    def test_challenges_added(self):
        patterns = [{"id": "p1", "counter_evidence": []}]
        evidence = [
            {"id": "e1", "relationship": "challenges", "patterns": ["p1"]},
        ]
        recompute_counter_evidence(patterns, evidence)
        assert patterns[0]["counter_evidence"] == ["e1"]

    def test_complicates_added(self):
        patterns = [{"id": "p1", "counter_evidence": []}]
        evidence = [
            {"id": "e1", "relationship": "complicates", "patterns": ["p1"]},
        ]
        recompute_counter_evidence(patterns, evidence)
        assert patterns[0]["counter_evidence"] == ["e1"]

    def test_supports_not_added(self):
        patterns = [{"id": "p1", "counter_evidence": []}]
        evidence = [
            {"id": "e1", "relationship": "supports", "patterns": ["p1"]},
        ]
        recompute_counter_evidence(patterns, evidence)
        assert patterns[0]["counter_evidence"] == []

    def test_unknown_pattern_ignored(self):
        patterns = [{"id": "p1", "counter_evidence": []}]
        evidence = [
            {"id": "e1", "relationship": "challenges", "patterns": ["unknown"]},
        ]
        recompute_counter_evidence(patterns, evidence)
        assert patterns[0]["counter_evidence"] == []


# ════════════════════════════════════════════════════════════════════
# parse_frontmatter
# ════════════════════════════════════════════════════════════════════


class TestParseFrontmatter:
    """Tests for parse_frontmatter()."""

    def test_parses_yaml_frontmatter(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(textwrap.dedent("""\
            ---
            id: test-analysis
            title: Test Title
            source_name: Test Source
            ---

            # Body content
        """))
        fm = parse_frontmatter(md)
        assert fm["id"] == "test-analysis"
        assert fm["title"] == "Test Title"

    def test_missing_frontmatter_exits(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# No frontmatter here\n")
        with pytest.raises(SystemExit):
            parse_frontmatter(md)


# ════════════════════════════════════════════════════════════════════
# build_analysis_entry
# ════════════════════════════════════════════════════════════════════


class TestBuildAnalysisEntry:
    """Tests for build_analysis_entry()."""

    def test_builds_complete_entry(self, sample_frontmatter, tmp_path):
        path = tmp_path / "analyses" / "test.md"
        path.parent.mkdir(parents=True)
        path.touch()
        entry = build_analysis_entry(sample_frontmatter, path)
        assert entry["id"] == "2026-03-10-test-analysis"
        assert entry["title"] == "Test Analysis — Example Material"
        assert entry["findings_count"] == 1
        assert entry["commit"] is None

    def test_defaults_for_optional_fields(self, tmp_path):
        fm = {
            "id": "test",
            "title": "Test",
            "source_name": "Test",
            "source_type": "news_article",
            "position": [5],
            "domain": ["us_foreign_policy"],
            "layers_primary": ["thought_narrative"],
            "null_case": "rejected",
            "patterns_matched": [],
        }
        path = tmp_path / "test.md"
        path.touch()
        entry = build_analysis_entry(fm, path)
        assert entry["layers_secondary"] == []
        assert entry["layers_absent"] == []
        assert entry["adversarial"] is False
        assert entry["url"] is None
        assert entry["findings_count"] == 0


# ════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════


def _frontmatter_to_entry(fm):
    """Convert sample frontmatter to an entry dict (like build_analysis_entry but simpler)."""
    return {
        "id": fm["id"],
        "file": "analyses/test.md",
        "date": fm.get("date", "2026-03-10"),
        "title": fm["title"],
        "source_name": fm["source_name"],
        "source_type": fm["source_type"],
        "position": fm["position"],
        "domain": fm["domain"],
        "layers_primary": fm["layers_primary"],
        "layers_secondary": fm.get("layers_secondary", []),
        "layers_absent": fm.get("layers_absent", []),
        "null_case": fm["null_case"],
        "patterns_matched": fm.get("patterns_matched", []),
    }
