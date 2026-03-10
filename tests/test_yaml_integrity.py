"""Tests for YAML data integrity.

Validates that the YAML data files are internally consistent and
match the config.yaml schema. These tests catch issues that would
otherwise only surface when running post-analysis.py or build-viewer.py.
"""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


@pytest.fixture(scope="module")
def config():
    with open(DATA / "config.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def analyses():
    with open(DATA / "analyses.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def patterns():
    with open(DATA / "patterns.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def principles():
    with open(DATA / "principles.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def evidence():
    with open(DATA / "evidence.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def circumventions():
    with open(DATA / "circumventions.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def instruments():
    with open(DATA / "instruments.yaml") as f:
        return yaml.safe_load(f)


# ════════════════════════════════════════════════════════════════════
# Config schema
# ════════════════════════════════════════════════════════════════════


class TestConfigSchema:
    def test_has_layers(self, config):
        assert "layers" in config
        assert len(config["layers"]) == 6

    def test_has_confidence_thresholds(self, config):
        t = config["confidence_thresholds"]
        assert "established" in t
        assert "supported" in t
        assert "preliminary" in t
        assert t["established"]["min_sources"] > t["supported"]["min_sources"]

    def test_has_required_enumerations(self, config):
        for key in ["analysis_source_types", "null_case_outcomes",
                     "finding_statuses", "relationship_types"]:
            assert key in config, f"Missing enumeration: {key}"
            assert len(config[key]) > 0


# ════════════════════════════════════════════════════════════════════
# Cross-file referential integrity
# ════════════════════════════════════════════════════════════════════


class TestReferentialIntegrity:
    """Verify that IDs referenced across files actually exist."""

    def test_analysis_layers_valid(self, config, analyses):
        valid = {l["id"] for l in config["layers"]}
        for a in analyses["entries"]:
            for field in ["layers_primary", "layers_secondary", "layers_absent"]:
                for layer in a.get(field) or []:
                    assert layer in valid, \
                        f"Analysis {a['id']}: invalid {field} layer '{layer}'"

    def test_analysis_source_types_valid(self, config, analyses):
        valid = set(config["analysis_source_types"])
        for a in analyses["entries"]:
            assert a["source_type"] in valid, \
                f"Analysis {a['id']}: invalid source_type '{a['source_type']}'"

    def test_analysis_null_case_valid(self, config, analyses):
        valid = set(config["null_case_outcomes"])
        for a in analyses["entries"]:
            assert a["null_case"] in valid, \
                f"Analysis {a['id']}: invalid null_case '{a['null_case']}'"

    def test_analysis_patterns_exist(self, analyses, patterns):
        pattern_ids = {p["id"] for p in patterns["entries"]}
        for a in analyses["entries"]:
            for pm in a.get("patterns_matched") or []:
                assert pm["pattern"] in pattern_ids, \
                    f"Analysis {a['id']}: references unknown pattern '{pm['pattern']}'"

    def test_principle_patterns_exist(self, principles, patterns):
        pattern_ids = {p["id"] for p in patterns["entries"]}
        for pr in principles["entries"]:
            for kp in pr.get("key_patterns") or []:
                assert kp["pattern"] in pattern_ids, \
                    f"Principle {pr['id']}: references unknown pattern '{kp['pattern']}'"

    def test_evidence_patterns_exist(self, evidence, patterns):
        pattern_ids = {p["id"] for p in patterns["entries"]}
        for e in evidence["entries"]:
            for pid in e.get("patterns") or []:
                assert pid in pattern_ids, \
                    f"Evidence {e['id']}: references unknown pattern '{pid}'"

    def test_pattern_circumventions_exist(self, patterns, circumventions):
        circ_ids = {c["id"] for c in circumventions["entries"]}
        for p in patterns["entries"]:
            for cid in p.get("circumventions") or []:
                assert cid in circ_ids, \
                    f"Pattern {p['id']}: references unknown circumvention '{cid}'"

    def test_pattern_layers_valid(self, config, patterns):
        valid = {l["id"] for l in config["layers"]}
        for p in patterns["entries"]:
            for layer in p.get("layers") or []:
                assert layer in valid, \
                    f"Pattern {p['id']}: invalid layer '{layer}'"

    def test_analysis_files_exist(self, analyses):
        for a in analyses["entries"]:
            fpath = ROOT / a["file"]
            assert fpath.exists(), \
                f"Analysis {a['id']}: file does not exist: {a['file']}"

    def test_principle_files_exist(self, principles):
        for p in principles["entries"]:
            fpath = ROOT / p["file"]
            assert fpath.exists(), \
                f"Principle {p['id']}: file does not exist: {p['file']}"

    def test_pattern_files_exist(self, patterns):
        for p in patterns["entries"]:
            if p.get("file"):
                fpath = ROOT / p["file"]
                assert fpath.exists(), \
                    f"Pattern {p['id']}: file does not exist: {p['file']}"


# ════════════════════════════════════════════════════════════════════
# ID uniqueness
# ════════════════════════════════════════════════════════════════════


class TestIdUniqueness:
    def test_analysis_ids_unique(self, analyses):
        ids = [a["id"] for a in analyses["entries"]]
        assert len(ids) == len(set(ids)), f"Duplicate analysis IDs: {_dupes(ids)}"

    def test_pattern_ids_unique(self, patterns):
        ids = [p["id"] for p in patterns["entries"]]
        assert len(ids) == len(set(ids)), f"Duplicate pattern IDs: {_dupes(ids)}"

    def test_principle_ids_unique(self, principles):
        ids = [p["id"] for p in principles["entries"]]
        assert len(ids) == len(set(ids)), f"Duplicate principle IDs: {_dupes(ids)}"

    def test_evidence_ids_unique(self, evidence):
        ids = [e["id"] for e in evidence["entries"]]
        assert len(ids) == len(set(ids)), f"Duplicate evidence IDs: {_dupes(ids)}"

    def test_circumvention_ids_unique(self, circumventions):
        ids = [c["id"] for c in circumventions["entries"]]
        assert len(ids) == len(set(ids)), f"Duplicate circumvention IDs: {_dupes(ids)}"


# ════════════════════════════════════════════════════════════════════
# Computed field consistency
# ════════════════════════════════════════════════════════════════════


class TestComputedFields:
    def test_findings_count_matches(self, analyses):
        """findings_count should equal len(patterns_matched)."""
        for a in analyses["entries"]:
            expected = len(a.get("patterns_matched") or [])
            assert a.get("findings_count") == expected, \
                f"Analysis {a['id']}: findings_count={a.get('findings_count')} != {expected}"

    def test_confidence_levels_valid(self, patterns):
        valid = {"ESTABLISHED", "SUPPORTED", "PRELIMINARY", None}
        for p in patterns["entries"]:
            assert p.get("confidence_level") in valid, \
                f"Pattern {p['id']}: invalid confidence_level '{p.get('confidence_level')}'"

    def test_observed_in_source_types_valid(self, patterns):
        valid = {"analysis", "principle"}
        for p in patterns["entries"]:
            for obs in p.get("observed_in") or []:
                assert obs["source_type"] in valid, \
                    f"Pattern {p['id']}: invalid observed_in source_type '{obs['source_type']}'"


def _dupes(lst):
    seen = set()
    dupes = []
    for x in lst:
        if x in seen:
            dupes.append(x)
        seen.add(x)
    return dupes
