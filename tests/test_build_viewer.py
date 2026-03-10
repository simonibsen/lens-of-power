"""Tests for tools/build-viewer.py."""

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

# Import build-viewer module
spec = importlib.util.spec_from_file_location(
    "build_viewer",
    ROOT / "tools" / "build-viewer.py",
)
build_viewer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_viewer)

extract_title = build_viewer.extract_title
layer_ids_to_names = build_viewer.layer_ids_to_names
compute_corroboration = build_viewer.compute_corroboration
sync_corroboration_to_yaml = build_viewer.sync_corroboration_to_yaml


# ════════════════════════════════════════════════════════════════════
# extract_title
# ════════════════════════════════════════════════════════════════════


class TestExtractTitle:
    def test_extracts_h1(self):
        assert extract_title("# My Title\n\nBody") == "My Title"

    def test_extracts_first_h1(self):
        assert extract_title("# First\n\n# Second") == "First"

    def test_ignores_h2(self):
        assert extract_title("## Not H1\n\n# Actual") == "Actual"

    def test_empty_string(self):
        assert extract_title("") == ""

    def test_no_heading(self):
        assert extract_title("Just text\nMore text") == ""

    def test_strips_whitespace(self):
        assert extract_title("#   Spaced Title  \n") == "Spaced Title"


# ════════════════════════════════════════════════════════════════════
# layer_ids_to_names
# ════════════════════════════════════════════════════════════════════


class TestLayerIdsToNames:
    def test_converts_known_ids(self):
        result = layer_ids_to_names(["thought_narrative", "economic"])
        assert result == ["Thought & Narrative", "Economic"]

    def test_all_six_layers(self):
        ids = [
            "thought_narrative", "economic", "legal_regulatory",
            "institutional", "surveillance_information", "physical_coercive",
        ]
        result = layer_ids_to_names(ids)
        assert len(result) == 6
        assert "Physical & Coercive" in result

    def test_unknown_id_passes_through(self):
        result = layer_ids_to_names(["unknown_layer"])
        assert result == ["unknown_layer"]

    def test_empty_list(self):
        assert layer_ids_to_names([]) == []

    def test_none_input(self):
        assert layer_ids_to_names(None) == []


# ════════════════════════════════════════════════════════════════════
# compute_corroboration
# ════════════════════════════════════════════════════════════════════


class TestComputeCorroboration:
    """Tests for the viewer's corroboration computation."""

    def _make_pattern_node(self, name, layers):
        return {
            "id": f"pattern:{name}",
            "type": "pattern",
            "title": name,
            "content": "",
            "meta": {
                "layers": ", ".join(layers),
                "layer_list": layers,
                "corroboration": "",
            },
        }

    def _make_source_node(self, node_id, node_type, layers):
        return {
            "id": node_id,
            "type": node_type,
            "title": node_id,
            "content": "",
            "meta": {"layer_list": layers},
        }

    def test_basic_corroboration(self):
        pattern = self._make_pattern_node("Test", ["Thought & Narrative"])
        source = self._make_source_node("analyses/a1.md", "analysis", ["Thought & Narrative"])
        nodes = [pattern, source]
        edges = [{"source": "analyses/a1.md", "target": "pattern:Test", "type": "matches"}]

        compute_corroboration(nodes, edges)

        assert pattern["meta"]["corr_count"] == 1
        assert pattern["meta"]["corr_relevant"] == 1
        assert pattern["meta"]["corr_level"] == "PRELIMINARY"

    def test_non_overlapping_layers(self):
        pattern = self._make_pattern_node("Test", ["Economic"])
        source = self._make_source_node("analyses/a1.md", "analysis", ["Thought & Narrative"])
        nodes = [pattern, source]
        edges = [{"source": "analyses/a1.md", "target": "pattern:Test", "type": "matches"}]

        compute_corroboration(nodes, edges)

        # Source doesn't share layers, so relevant = max(0, 1) = 1
        assert pattern["meta"]["corr_count"] == 1

    def test_established_level(self):
        pattern = self._make_pattern_node("Test", ["Thought & Narrative"])
        nodes = [pattern]
        edges = []
        for i in range(10):
            src = self._make_source_node(f"analyses/a{i}.md", "analysis", ["Thought & Narrative"])
            nodes.append(src)
            edges.append({"source": f"analyses/a{i}.md", "target": "pattern:Test", "type": "matches"})

        compute_corroboration(nodes, edges)

        assert pattern["meta"]["corr_level"] == "ESTABLISHED"
        assert pattern["meta"]["corr_count"] == 10

    def test_counter_evidence_blocks_established(self):
        pattern = self._make_pattern_node("Test", ["Thought & Narrative"])
        pattern["meta"]["corroboration"] = "some counter-evidence noted"
        nodes = [pattern]
        edges = []
        for i in range(10):
            src = self._make_source_node(f"analyses/a{i}.md", "analysis", ["Thought & Narrative"])
            nodes.append(src)
            edges.append({"source": f"analyses/a{i}.md", "target": "pattern:Test", "type": "matches"})

        compute_corroboration(nodes, edges)

        assert pattern["meta"]["corr_level"] == "SUPPORTED"
        assert pattern["meta"]["corr_has_counter"] is True


# ════════════════════════════════════════════════════════════════════
# sync_corroboration_to_yaml
# ════════════════════════════════════════════════════════════════════


class TestSyncCorroborationToYaml:
    """Tests for sync_corroboration_to_yaml()."""

    def test_updates_confidence_in_yaml(self, tmp_path, monkeypatch):
        """Verify it writes updated confidence to data/patterns.yaml."""
        import yaml

        # Create data/patterns.yaml
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        yaml_file = data_dir / "patterns.yaml"
        yaml_file.write_text(
            "# Header comment\n"
            "entries:\n"
            + yaml.dump({"entries": [{
                "id": "test_pattern",
                "name": "Test Pattern",
                "confidence_level": "PRELIMINARY",
                "confidence_ratio": 0.1,
                "relevant_corpus_size": 10,
                "corr_count": 1,
            }]}, default_flow_style=False)
        )

        # Monkeypatch ROOT
        monkeypatch.setattr(build_viewer, "ROOT", tmp_path)

        nodes = [{
            "id": "pattern:Test Pattern",
            "type": "pattern",
            "title": "Test Pattern",
            "meta": {
                "corr_level": "ESTABLISHED",
                "corr_hit_rate": 0.8,
                "corr_relevant": 10,
                "corr_count": 8,
            },
        }]

        sync_corroboration_to_yaml(nodes)

        with open(yaml_file) as f:
            data = yaml.safe_load(f)
        entry = data["entries"][0]
        assert entry["confidence_level"] == "ESTABLISHED"
        assert entry["confidence_ratio"] == 0.8
        assert entry["corr_count"] == 8


# ════════════════════════════════════════════════════════════════════
# Integration: full build
# ════════════════════════════════════════════════════════════════════


class TestBuildIntegration:
    """Integration tests that run build-viewer.py against real data."""

    @staticmethod
    def _load_viewer_data():
        """Parse viewer-data.js into a Python dict."""
        content = (ROOT / "viewer-data.js").read_text()
        assert content.startswith("const DATA = "), "viewer-data.js format mismatch"
        json_str = content[len("const DATA = "):].rstrip().rstrip(";")
        return json.loads(json_str)

    def test_build_produces_output(self):
        """Run build-viewer.py and verify it produces valid output."""
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "build-viewer.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"build-viewer.py failed:\n{result.stderr}"
        assert (ROOT / "viewer-data.js").exists()
        assert (ROOT / "viewer.html").exists()

    def test_viewer_data_is_valid_json(self):
        """viewer-data.js should contain valid JSON."""
        data = self._load_viewer_data()
        assert "nodes" in data
        assert "edges" in data

    def test_node_counts(self):
        """Verify expected node types are present."""
        data = self._load_viewer_data()
        types = {}
        for node in data["nodes"]:
            t = node["type"]
            types[t] = types.get(t, 0) + 1

        assert types.get("pattern", 0) == 32
        assert types.get("analysis", 0) >= 30
        assert types.get("principle", 0) >= 20
        assert types.get("circumvention", 0) >= 5
        assert types.get("evidence", 0) >= 10
        assert types.get("instrument", 0) >= 5

    def test_edges_present(self):
        """Verify edges exist and have expected types."""
        data = self._load_viewer_data()
        edge_types = {e["type"] for e in data["edges"]}
        assert "observed_in" in edge_types
        assert "matches" in edge_types
        assert "counteracts" in edge_types
        assert "key_pattern" in edge_types

    def test_all_patterns_have_confidence(self):
        """Every pattern node should have corroboration metadata."""
        data = self._load_viewer_data()
        for node in data["nodes"]:
            if node["type"] == "pattern":
                meta = node["meta"]
                assert "corr_level" in meta, f"Pattern {node['title']} missing corr_level"
                assert meta["corr_level"] in ("ESTABLISHED", "SUPPORTED", "PRELIMINARY"), \
                    f"Pattern {node['title']} has invalid corr_level: {meta['corr_level']}"

    def test_no_orphan_edges(self):
        """Every edge should reference existing node IDs."""
        data = self._load_viewer_data()
        node_ids = {n["id"] for n in data["nodes"]}
        for edge in data["edges"]:
            assert edge["source"] in node_ids, \
                f"Orphan edge source: {edge['source']} (type: {edge['type']})"
            assert edge["target"] in node_ids, \
                f"Orphan edge target: {edge['target']} (type: {edge['type']})"
