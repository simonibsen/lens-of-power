"""Shared fixtures for Lens of Power tests."""

import sys
from pathlib import Path

import pytest
import yaml

# Add tools/ to path so we can import the modules
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

DATA = ROOT / "data"


@pytest.fixture
def config():
    """Load the real config.yaml."""
    with open(DATA / "config.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture
def thresholds(config):
    """Extract confidence thresholds from config."""
    return config["confidence_thresholds"]


@pytest.fixture
def minimal_config():
    """A minimal config for unit tests that don't need the full config."""
    return {
        "layers": [
            {"id": "thought_narrative", "name": "Thought & Narrative"},
            {"id": "economic", "name": "Economic"},
            {"id": "institutional", "name": "Institutional"},
        ],
        "positions": [
            {"id": 1, "label": "Exercising power"},
            {"id": 5, "label": "Observer / analyst"},
        ],
        "domains": [
            {"id": "us_foreign_policy", "description": "US military operations"},
            {"id": "platform_governance", "description": "Social media policy"},
        ],
        "analysis_source_types": ["news_article", "investigation", "report"],
        "null_case_outcomes": ["accepted", "plausible", "rejected"],
        "finding_statuses": ["observed", "inferred", "speculative"],
        "confidence_thresholds": {
            "preliminary": {"min_sources": 0, "min_ratio": 0.0},
            "supported": {"min_sources": 3, "min_ratio": 0.10},
            "established": {
                "min_sources": 5,
                "min_ratio": 0.20,
                "requires_no_unresolved_counter": True,
            },
        },
    }


@pytest.fixture
def sample_frontmatter():
    """Sample analysis frontmatter for testing."""
    return {
        "id": "2026-03-10-test-analysis",
        "title": "Test Analysis — Example Material",
        "source_name": "Test Source",
        "source_type": "news_article",
        "date": "2026-03-10",
        "position": [5],
        "domain": ["us_foreign_policy"],
        "layers_primary": ["thought_narrative", "institutional"],
        "layers_secondary": ["economic"],
        "layers_absent": [],
        "null_case": "rejected",
        "patterns_matched": [
            {
                "pattern": "inversion_of_stated_purpose",
                "status": "observed",
                "variant": None,
                "note": "Test observation",
            },
        ],
    }


@pytest.fixture
def sample_pattern():
    """A sample pattern entry for testing."""
    return {
        "id": "test_pattern",
        "name": "Test Pattern",
        "layers": ["thought_narrative", "economic"],
        "observed_in": [],
        "counter_evidence": [],
        "confidence_ratio": None,
        "confidence_level": None,
        "relevant_corpus_size": None,
    }
