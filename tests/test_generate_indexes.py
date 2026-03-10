"""Tests for tools/generate-indexes.py."""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

# Import generate-indexes module
spec = importlib.util.spec_from_file_location(
    "generate_indexes",
    ROOT / "tools" / "generate-indexes.py",
)
generate_indexes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_indexes)

domain_text = generate_indexes.domain_text
layer_names = generate_indexes.layer_names
layers_text = generate_indexes.layers_text
generate_analyses_index = generate_indexes.generate_analyses_index
generate_patterns_index = generate_indexes.generate_patterns_index
generate_principles_index = generate_indexes.generate_principles_index
generate_sources_index = generate_indexes.generate_sources_index
generate_sample_pool = generate_indexes.generate_sample_pool


# ════════════════════════════════════════════════════════════════════
# domain_text
# ════════════════════════════════════════════════════════════════════


class TestDomainText:
    def test_known_ids(self):
        result = domain_text(["us_foreign_policy", "military"])
        assert result == "US foreign policy / military"

    def test_capitalizes_first_letter(self):
        result = domain_text(["military"])
        assert result == "Military"

    def test_unknown_id_passes_through(self):
        result = domain_text(["unknown_thing"])
        assert result == "Unknown thing"

    def test_empty_list(self):
        assert domain_text([]) == ""


# ════════════════════════════════════════════════════════════════════
# layer_names
# ════════════════════════════════════════════════════════════════════


class TestLayerNames:
    def test_known_ids(self):
        result = layer_names(["thought_narrative", "economic"])
        assert result == ["Thought & Narrative", "Economic"]

    def test_empty(self):
        assert layer_names([]) == []

    def test_none(self):
        assert layer_names(None) == []


# ════════════════════════════════════════════════════════════════════
# layers_text
# ════════════════════════════════════════════════════════════════════


class TestLayersText:
    def test_all_six_primary(self):
        all_ids = list(generate_indexes.ALL_LAYER_IDS)
        result = layers_text(all_ids, [], [])
        assert result == "All six"

    def test_simple_primary(self):
        result = layers_text(["thought_narrative", "economic"], [], [])
        assert result == "Thought & Narrative, Economic"


# ════════════════════════════════════════════════════════════════════
# generate_analyses_index
# ════════════════════════════════════════════════════════════════════


class TestGenerateAnalysesIndex:
    def test_basic_entry(self):
        data = {"entries": [{
            "id": "test-analysis",
            "source_date": "2026-01-01",
            "title": "Test Analysis",
            "domain": ["us_foreign_policy"],
            "layers_primary": ["thought_narrative"],
            "layers_secondary": [],
            "layers_absent": [],
            "null_case": "rejected",
            "null_case_level": "LOW",
            "file": "analyses/test-analysis.md",
            "adversarial": False,
            "origin": None,
            "ic5_flag": None,
            "cross_references": [],
        }]}
        result = generate_analyses_index(data)
        assert "### 2026-01-01 — Test Analysis" in result
        assert "Domain: US foreign policy" in result
        assert "Null case: rejected (LOW)" in result
        assert "File: `test-analysis.md`" in result

    def test_display_overrides_used(self):
        data = {"entries": [{
            "id": "test",
            "source_date": "2026-01-01",
            "title": "Test",
            "domain": ["us_foreign_policy"],
            "domain_text": "Custom domain text",
            "layers_primary": ["thought_narrative"],
            "layers_text": "Custom layers text",
            "null_case_text": "custom null case",
            "file": "analyses/test.md",
            "adversarial": False,
            "origin": None,
            "ic5_flag": None,
            "cross_references": [],
        }]}
        result = generate_analyses_index(data)
        assert "Domain: Custom domain text" in result
        assert "Layers: Custom layers text" in result
        assert "Null case: custom null case" in result

    def test_adversarial_with_note(self):
        data = {"entries": [{
            "id": "test",
            "source_date": "2026-01-01",
            "title": "Test",
            "domain": [],
            "layers_primary": [],
            "file": "analyses/test.md",
            "adversarial": True,
            "adversarial_note": "testing null case",
            "origin": None,
            "ic5_flag": None,
            "cross_references": [],
        }]}
        result = generate_analyses_index(data)
        assert "Adversarial input: yes — testing null case" in result

    def test_sample_mode_origin(self):
        data = {"entries": [{
            "id": "test",
            "date": "2026-03-08",
            "source_date": "2026-02",
            "title": "Test",
            "domain": [],
            "layers_primary": [],
            "file": "analyses/test.md",
            "adversarial": False,
            "origin": "sample",
            "ic5_flag": None,
            "cross_references": [],
        }]}
        result = generate_analyses_index(data)
        assert "Origin: SAMPLE mode (2026-03-08)" in result

    def test_cross_references_with_notes(self):
        data = {"entries": [{
            "id": "test",
            "source_date": "2026-01-01",
            "title": "Test",
            "domain": [],
            "layers_primary": [],
            "file": "analyses/test.md",
            "adversarial": False,
            "origin": None,
            "ic5_flag": None,
            "cross_references": ["other-analysis"],
            "cross_references_notes": {"other-analysis": "related analysis"},
        }]}
        result = generate_analyses_index(data)
        assert "`other-analysis.md` (related analysis)" in result


# ════════════════════════════════════════════════════════════════════
# generate_patterns_index
# ════════════════════════════════════════════════════════════════════


class TestGeneratePatternsIndex:
    def test_basic_pattern(self):
        patterns = {"entries": [{
            "id": "test_pattern",
            "name": "Test Pattern",
            "file": "patterns/test-pattern.md",
            "layers": ["thought_narrative"],
            "statement": "A test statement.",
            "confidence_level": "SUPPORTED",
            "confidence_ratio": 0.15,
            "relevant_corpus_size": 50,
            "corr_count": 8,
            "circumventions": [],
        }]}
        circs = {"entries": []}
        result = generate_patterns_index(patterns, circs)
        assert "## [Test Pattern](test-pattern.md)" in result
        assert "LAYERS: Thought & Narrative" in result
        assert "STATEMENT: A test statement." in result
        assert "CONFIDENCE: SUPPORTED (8 of 50 relevant sources, 15%)" in result

    def test_all_layers_shorthand(self):
        all_ids = list(generate_indexes.ALL_LAYER_IDS)
        patterns = {"entries": [{
            "id": "test",
            "name": "Test",
            "file": "patterns/test.md",
            "layers": all_ids,
            "statement": "Test.",
            "confidence_level": "PRELIMINARY",
            "confidence_ratio": 0.05,
            "relevant_corpus_size": 40,
            "corr_count": 2,
            "circumventions": [],
        }]}
        result = generate_patterns_index(patterns, {"entries": []})
        assert "LAYERS: All layers" in result

    def test_circumventions_resolved(self):
        patterns = {"entries": [{
            "id": "test",
            "name": "Test",
            "file": "patterns/test.md",
            "layers": ["thought_narrative"],
            "statement": "Test.",
            "confidence_level": "PRELIMINARY",
            "confidence_ratio": 0.05,
            "relevant_corpus_size": 40,
            "corr_count": 2,
            "circumventions": ["transparency"],
        }]}
        circs = {"entries": [{"id": "transparency", "name": "Transparency / Naming"}]}
        result = generate_patterns_index(patterns, circs)
        assert "CIRCUMVENTIONS: Transparency / Naming" in result


# ════════════════════════════════════════════════════════════════════
# generate_principles_index
# ════════════════════════════════════════════════════════════════════


class TestGeneratePrinciplesIndex:
    def test_uses_display_overrides(self):
        principles = {"entries": [{
            "id": "test-source",
            "source_display": "Test Author, *Test Book* (2020)",
            "position_display": "5 (academic)",
            "layers_text": "All six",
            "key_patterns_display": "Pattern A, Pattern B",
            "principles_list": ["Principle One", "Principle Two"],
            "key_patterns": [],
            "ic1_flags": [],
            "new_pattern_candidates": [],
            "provenance_tier": "training_data",
        }]}
        patterns = {"entries": []}
        result = generate_principles_index(principles, patterns)
        assert "SOURCE: Test Author, *Test Book* (2020)" in result
        assert "POSITION: 5 (academic)" in result
        assert "LAYERS: All six" in result
        assert "KEY PATTERNS: Pattern A, Pattern B" in result
        assert "PRINCIPLES: 2 — Principle One, Principle Two" in result

    def test_source_type_display(self):
        principles = {"entries": [{
            "id": "test",
            "source_display": "Author, *Book* (2020)",
            "position_display": "1 (ruler)",
            "layers_text": "All six",
            "key_patterns_display": "Pattern A",
            "principles_list": ["P1"],
            "key_patterns": [],
            "ic1_flags": [],
            "new_pattern_candidates": [],
            "provenance_tier": "primary_document",
            "source_type_display": "primary_document (see `sources/test.md`)",
        }]}
        result = generate_principles_index(principles, {"entries": []})
        assert "SOURCE TYPE: primary_document (see `sources/test.md`)" in result


# ════════════════════════════════════════════════════════════════════
# generate_sources_index
# ════════════════════════════════════════════════════════════════════


class TestGenerateSourcesIndex:
    def test_basic_source(self):
        data = {"entries": [{
            "id": "test-source",
            "source": "Author, *Book* (2020)",
            "provenance_tier": "primary_document",
            "hash": "sha256:abc123",
            "archive_urls": ["https://example.com/archive"],
            "archive_labels": {"https://example.com/archive": "Example Archive"},
            "extraction_status": "Full extraction",
            "quote_status": "verbatim",
        }]}
        result = generate_sources_index(data)
        assert "## test-source.md" in result
        assert "SOURCE: Author, *Book* (2020)" in result
        assert "ARCHIVE: [Example Archive](https://example.com/archive)" in result

    def test_archive_without_label_uses_url(self):
        data = {"entries": [{
            "id": "test",
            "source": "Source",
            "provenance_tier": "primary_document",
            "hash": "",
            "archive_urls": ["https://example.com"],
            "extraction_status": "Partial",
            "quote_status": "excerpts",
        }]}
        result = generate_sources_index(data)
        assert "[https://example.com](https://example.com)" in result


# ════════════════════════════════════════════════════════════════════
# generate_sample_pool
# ════════════════════════════════════════════════════════════════════


class TestGenerateSamplePool:
    def test_basic_pool(self):
        data = {"categories": [{
            "name": "Test Category",
            "entries": [{
                "outlet": "Test Outlet",
                "url": "example.com",
                "tags": {
                    "institution": "corporate",
                    "domain": ["politics", "economics"],
                    "geo": "us-national",
                    "audience": "general",
                    "position": 4,
                },
            }],
        }]}
        result = generate_sample_pool(data)
        assert "### Test Category" in result
        assert "**Test Outlet** (example.com)" in result
        assert "[INST:corporate]" in result
        assert "[DOMAIN:politics,economics]" in result


# ════════════════════════════════════════════════════════════════════
# Integration: round-trip
# ════════════════════════════════════════════════════════════════════


class TestIntegration:
    """Verify generated output matches hand-maintained originals."""

    def test_analyses_index_matches_original(self):
        """Generated analyses/INDEX.md should match the committed version."""
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "generate-indexes.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"generate-indexes.py failed:\n{result.stderr}"

        # Read generated output and compare with git HEAD
        generated = (ROOT / "analyses" / "INDEX.md").read_text()
        check = subprocess.run(
            ["git", "diff", "--stat", "analyses/INDEX.md"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        assert check.stdout.strip() == "", \
            f"analyses/INDEX.md differs from committed version:\n{check.stdout}"

    def test_principles_index_matches_original(self):
        """Generated principles/INDEX.md should match the committed version."""
        check = subprocess.run(
            ["git", "diff", "--stat", "principles/INDEX.md"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        assert check.stdout.strip() == "", \
            f"principles/INDEX.md differs from committed version:\n{check.stdout}"

    def test_sources_index_matches_original(self):
        """Generated sources/INDEX.md should match the committed version."""
        check = subprocess.run(
            ["git", "diff", "--stat", "sources/INDEX.md"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        assert check.stdout.strip() == "", \
            f"sources/INDEX.md differs from committed version:\n{check.stdout}"
