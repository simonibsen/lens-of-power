#!/usr/bin/env python3
"""Build a self-contained viewer.html from Lens of Power framework files.

Reads all markdown files, extracts structured metadata and cross-references,
and outputs a single HTML file with embedded JSON data. Uses marked.js (CDN)
for markdown rendering and D3.js (CDN) for graph visualization.

Usage: python3 tools/build-viewer.py
Output: viewer.html
"""

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "viewer.html"
OUT_DATA = ROOT / "viewer-data.js"

LAYER_NAMES = [
    "Thought & Narrative",
    "Economic",
    "Legal & Regulatory",
    "Institutional",
    "Surveillance & Information",
    "Physical & Coercive",
]


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_title(content: str) -> str:
    """Extract the first H1 title from markdown."""
    m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return m.group(1).strip() if m else ""


def extract_field(content: str, field: str) -> str:
    """Extract a single-line field value like 'DATE: 2026-03-01'."""
    pattern = rf"^{re.escape(field)}:\s*(.+)$"
    m = re.search(pattern, content, re.MULTILINE)
    return m.group(1).strip() if m else ""


def extract_field_multiline(content: str, field: str) -> str:
    """Extract a field that may span multiple lines (until the next field or blank line + heading)."""
    pattern = rf"^{re.escape(field)}:\s*(.+?)(?=\n[A-Z][A-Z _]+:|(?:\n\s*\n))"
    m = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    # Fallback: single line
    return extract_field(content, field)


def split_list(value: str) -> list:
    """Split a comma-or-semicolon separated string into a list of stripped items."""
    if not value:
        return []
    items = re.split(r"[,;]", value)
    return [i.strip() for i in items if i.strip()]


def extract_file_refs(text: str) -> list:
    """Extract file path references like principles/foo.md, analyses/bar.md, etc."""
    return re.findall(
        r"(?:principles|analyses|instruments|evidence)/[\w\-]+\.md",
        text,
    )


# ---------------------------------------------------------------------------
# Layer parsing
# ---------------------------------------------------------------------------

def parse_layers_string(s: str) -> list:
    """Parse a LAYERS field value into a list of canonical layer names."""
    if not s:
        return []
    s = s.strip()
    # Strip trailing parenthetical annotations like "(Physical as foundation)"
    base = re.sub(r"\s*\(.*?\)\s*$", "", s).strip().lower()
    if base in ("all layers", "all six"):
        return list(LAYER_NAMES)
    if base == "all non-physical":
        return [l for l in LAYER_NAMES if l != "Physical & Coercive"]
    result = []
    for part in s.split(","):
        part = re.sub(r"\(.*?\)", "", part).strip()
        if not part:
            continue
        for canon in LAYER_NAMES:
            if part.lower() == canon.lower() or canon.lower().startswith(part.lower()):
                if canon not in result:
                    result.append(canon)
                break
    return result


# ---------------------------------------------------------------------------
# Pattern name normalization
# ---------------------------------------------------------------------------

def pattern_id(name: str) -> str:
    return "pattern:" + name.strip()


def normalize_pattern_ref(ref: str) -> str:
    """Normalize loose pattern references to canonical names."""
    ref = ref.strip()
    canon = ref
    return canon


# ---------------------------------------------------------------------------
# Parse each file type
# ---------------------------------------------------------------------------

def parse_patterns(path: Path):
    """Parse patterns.md into a list of pattern nodes."""
    content = read_file(path)
    nodes = []
    parts = re.split(r"^### ", content, flags=re.MULTILINE)
    for part in parts[1:]:
        lines = part.strip()
        name = lines.split("\n")[0].strip()
        layers = extract_field(lines, "LAYERS")
        statement = extract_field(lines, "STATEMENT")
        mechanism = extract_field(lines, "MECHANISM")
        corroboration = extract_field(lines, "CORROBORATION")
        nodes.append({
            "id": pattern_id(name),
            "type": "pattern",
            "title": name,
            "content": "### " + part.strip(),
            "meta": {
                "layers": layers,
                "layer_list": parse_layers_string(layers),
                "statement": statement,
                "mechanism": mechanism,
                "corroboration": corroboration,
            },
        })
    return nodes


def parse_patterns_detail(path: Path):
    """Parse patterns-detail.md for OBSERVED IN and EVIDENCE edges."""
    content = read_file(path)
    edges = []
    parts = re.split(r"^### ", content, flags=re.MULTILINE)
    for part in parts[1:]:
        name = part.split("\n")[0].strip()
        pid = pattern_id(name)

        observed = extract_field_multiline(part, "OBSERVED IN")
        if observed:
            for fref in extract_file_refs(observed):
                edges.append({
                    "source": pid,
                    "target": fref,
                    "type": "observed_in",
                })

        evidence = extract_field_multiline(part, "EVIDENCE")
        if evidence:
            for fref in extract_file_refs(evidence):
                edges.append({
                    "source": pid,
                    "target": fref,
                    "type": "evidence",
                })
    return edges


def parse_analysis(path: Path):
    """Parse an analysis file into a node and edges."""
    content = read_file(path)
    rel = str(path.relative_to(ROOT))
    title = extract_title(content)
    date = extract_field(content, "DATE")
    time_field = extract_field(content, "TIME")
    source_type = extract_field(content, "SOURCE TYPE")
    mode = extract_field(content, "MODE")
    source = extract_field(content, "SOURCE")

    node = {
        "id": rel,
        "type": "analysis",
        "title": title,
        "content": content,
        "meta": {
            "date": date,
            "time": time_field,
            "source_type": source_type,
            "mode": mode,
            "source": source,
        },
    }

    edges = []

    pattern_section = re.search(
        r"(?:###\s*Pattern matches|PATTERNS MATCHED:)(.*?)(?=\n###|\n---|\Z)",
        content, re.DOTALL | re.IGNORECASE,
    )
    if pattern_section:
        text = pattern_section.group(1)
        for line in text.split("\n"):
            line = line.strip().lstrip("- ")
            if line and not line.startswith("#"):
                name = re.split(r"\s*\(", line)[0].strip()
                if name and len(name) > 3:
                    edges.append({
                        "source": rel,
                        "target": pattern_id(name),
                        "type": "matches",
                    })

    cross_ref = re.search(
        r"###\s*Framework cross-reference(.*?)(?=\n---|\n##[^#]|\Z)",
        content, re.DOTALL,
    )
    if cross_ref:
        text = cross_ref.group(1)
        for fref in extract_file_refs(text):
            edges.append({
                "source": rel,
                "target": fref,
                "type": "references",
            })

    sources_section = re.search(
        r"###\s*Framework files referenced(.*?)(?=\n---|\n##[^#]|\Z)",
        content, re.DOTALL,
    )
    if sources_section:
        text = sources_section.group(1)
        for fref in extract_file_refs(text):
            edges.append({
                "source": rel,
                "target": fref,
                "type": "references",
            })

    for fref in re.findall(r"instruments/[\w\-]+\.md", content):
        edges.append({
            "source": rel,
            "target": fref,
            "type": "applies_instrument",
        })

    return node, edges


def parse_principle_index(path: Path):
    """Parse principles/INDEX.md for KEY PATTERNS, INSTRUMENT refs, and LAYERS."""
    content = read_file(path)
    edges = []
    index_layers = {}

    parts = re.split(r"^## ", content, flags=re.MULTILINE)
    for part in parts[1:]:
        lines = part.strip()
        filename = lines.split("\n")[0].strip()
        if not filename.endswith(".md"):
            continue
        fref = "principles/" + filename

        # LAYERS
        layers_str = extract_field(lines, "LAYERS")
        if layers_str:
            index_layers[fref] = parse_layers_string(layers_str)

        # KEY PATTERNS
        kp = extract_field(lines, "KEY PATTERNS")
        if kp:
            for pname in split_list(kp):
                pname = pname.strip()
                if pname:
                    edges.append({
                        "source": fref,
                        "target": pattern_id(pname),
                        "type": "key_pattern",
                    })

        # INSTRUMENT refs
        inst_line = extract_field(lines, "INSTRUMENT")
        if inst_line:
            for iref in extract_file_refs(inst_line):
                edges.append({
                    "source": fref,
                    "target": iref,
                    "type": "produces_instrument",
                })
        inst_line2 = extract_field(lines, "INSTRUMENT PROPOSED")
        if inst_line2:
            for iref in extract_file_refs(inst_line2):
                edges.append({
                    "source": fref,
                    "target": iref,
                    "type": "produces_instrument",
                })

    return edges, index_layers


def parse_principle(path: Path):
    """Parse a principles/*.md file into a node."""
    content = read_file(path)
    rel = str(path.relative_to(ROOT))
    title = extract_title(content)
    source = extract_field(content, "SOURCE")
    ptype = extract_field(content, "TYPE")
    layers_section = re.search(
        r"##\s*Layers active(.*?)(?=\n---|\n##[^#]|\Z)",
        content, re.DOTALL,
    )
    layers = ""
    if layers_section:
        layer_text = layers_section.group(1)
        layer_names = re.findall(
            r"\|\s*(Thought & Narrative|Economic|Legal & Regulatory|Institutional|Surveillance & Information|Physical & Coercive)",
            layer_text,
        )
        if layer_names:
            layers = ", ".join(layer_names)

    principle_names = re.findall(r"^### P\d+:\s*(.+)$", content, re.MULTILINE)
    principle_count = len(principle_names)

    node = {
        "id": rel,
        "type": "principle",
        "title": title,
        "content": content,
        "meta": {
            "source": source,
            "type": ptype,
            "layers": layers,
            "layer_list": parse_layers_string(layers),
            "principle_count": principle_count,
            "principle_names": principle_names,
        },
    }
    return node


def parse_instrument(path: Path):
    """Parse an instruments/*.md file into a node."""
    content = read_file(path)
    rel = str(path.relative_to(ROOT))
    title = extract_title(content)
    source = extract_field(content, "SOURCE")
    layers = extract_field(content, "TAXONOMY LAYERS")

    items = re.findall(r"^### (.+)$", content, re.MULTILINE)

    node = {
        "id": rel,
        "type": "instrument",
        "title": title,
        "content": content,
        "meta": {
            "source": source,
            "layers": layers,
            "layer_list": parse_layers_string(layers),
            "item_count": len(items),
        },
    }
    return node


def parse_evidence(path: Path):
    """Parse an evidence/*.md file into a node and edges."""
    content = read_file(path)
    rel = str(path.relative_to(ROOT))
    title = extract_title(content)
    date = extract_field(content, "DATE RECORDED")
    source = extract_field(content, "SOURCE")
    source_type = extract_field(content, "SOURCE TYPE")
    axioms = extract_field(content, "AXIOMS")
    patterns = extract_field(content, "PATTERNS")
    layers = extract_field(content, "LAYERS")
    relationship = extract_field(content, "RELATIONSHIP")

    node = {
        "id": rel,
        "type": "evidence",
        "title": title,
        "content": content,
        "meta": {
            "date": date,
            "source": source,
            "source_type": source_type,
            "axioms": axioms,
            "layers": layers,
            "layer_list": parse_layers_string(layers),
            "relationship": relationship,
        },
    }

    edges = []
    if patterns:
        for pname in split_list(patterns):
            pname = pname.strip()
            if pname:
                edges.append({
                    "source": rel,
                    "target": pattern_id(pname),
                    "type": "evidence_for",
                })

    return node, edges


def parse_constitution(path: Path):
    """Extract axiom names from constitution.md."""
    content = read_file(path)
    axioms = re.findall(r"^### (\d+\.\s+.+)$", content, re.MULTILINE)
    return axioms


def parse_taxonomy(path: Path):
    """Extract layer names from taxonomy.md."""
    content = read_file(path)
    layers = re.findall(r"^### \d+\.\s+(.+)$", content, re.MULTILINE)
    return layers


# ---------------------------------------------------------------------------
# README and taxonomy section extraction
# ---------------------------------------------------------------------------

def extract_readme_sections(path: Path) -> dict:
    """Extract key sections from README.md as markdown content."""
    content = read_file(path)
    sections = {}
    targets = {
        "core_concepts": "## Core concepts",
        "how_framework_grows": "## How the framework grows",
        "integrity_constraints": "## Integrity constraints",
    }
    for key, heading in targets.items():
        pattern = re.escape(heading) + r"(.*?)(?=\n## |\Z)"
        m = re.search(pattern, content, re.DOTALL)
        if m:
            sections[key] = m.group(1).strip()
    return sections


def extract_layer_descriptions(path: Path) -> list:
    """Extract layer names and first-paragraph descriptions from taxonomy.md."""
    content = read_file(path)
    layers = []
    parts = re.split(r"^### \d+\.\s+", content, flags=re.MULTILINE)
    for part in parts[1:]:
        lines = part.strip().split("\n")
        name = lines[0].strip()
        desc_lines = []
        for line in lines[1:]:
            if not line.strip():
                if desc_lines:
                    break
                continue
            if line.strip().startswith("**"):
                break
            desc_lines.append(line.strip())
        description = " ".join(desc_lines)
        layers.append({"name": name, "description": description})
    return layers


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------

def build():
    nodes = []
    edges = []
    node_ids = set()

    def add_node(n):
        if n["id"] not in node_ids:
            nodes.append(n)
            node_ids.add(n["id"])

    # --- Patterns ---
    patterns_path = ROOT / "patterns.md"
    if patterns_path.exists():
        for n in parse_patterns(patterns_path):
            add_node(n)

    # --- Patterns detail (edges only) ---
    detail_path = ROOT / "patterns-detail.md"
    if detail_path.exists():
        edges.extend(parse_patterns_detail(detail_path))

    # --- Analyses ---
    analyses_dir = ROOT / "analyses"
    if analyses_dir.exists():
        for f in sorted(analyses_dir.glob("*.md")):
            if f.name == "INDEX.md":
                continue
            n, e = parse_analysis(f)
            add_node(n)
            edges.extend(e)

    # --- Principles ---
    principles_dir = ROOT / "principles"
    index_layers = {}
    if principles_dir.exists():
        index_path = principles_dir / "INDEX.md"
        if index_path.exists():
            idx_edges, index_layers = parse_principle_index(index_path)
            edges.extend(idx_edges)

        for f in sorted(principles_dir.glob("*.md")):
            if f.name == "INDEX.md":
                continue
            n = parse_principle(f)
            # Merge layer_list from INDEX if available (authoritative source)
            if n["id"] in index_layers:
                n["meta"]["layer_list"] = index_layers[n["id"]]
            add_node(n)

    # --- Instruments ---
    instruments_dir = ROOT / "instruments"
    if instruments_dir.exists():
        for f in sorted(instruments_dir.glob("*.md")):
            n = parse_instrument(f)
            add_node(n)

    # --- Evidence ---
    evidence_dir = ROOT / "evidence"
    if evidence_dir.exists():
        for f in sorted(evidence_dir.glob("*.md")):
            if f.name == "README.md":
                continue
            n, e = parse_evidence(f)
            add_node(n)
            edges.extend(e)

    # --- Constitution & Taxonomy (metadata, not nodes) ---
    axioms = []
    constitution_path = ROOT / "constitution.md"
    if constitution_path.exists():
        axioms = parse_constitution(constitution_path)

    layer_names = []
    taxonomy_path = ROOT / "taxonomy.md"
    if taxonomy_path.exists():
        layer_names = parse_taxonomy(taxonomy_path)

    # --- README sections ---
    readme_sections = {}
    readme_path = ROOT / "README.md"
    if readme_path.exists():
        readme_sections = extract_readme_sections(readme_path)

    # --- Layer descriptions ---
    layer_descriptions = []
    if taxonomy_path.exists():
        layer_descriptions = extract_layer_descriptions(taxonomy_path)

    # --- Deduplicate and validate edges ---
    valid_edges = []
    seen = set()
    for e in edges:
        key = (e["source"], e["target"], e["type"])
        if key not in seen and e["source"] in node_ids and e["target"] in node_ids:
            valid_edges.append(e)
            seen.add(key)

    data = {
        "nodes": nodes,
        "edges": valid_edges,
        "meta": {
            "axioms": axioms,
            "layers": layer_names,
            "readme_sections": readme_sections,
            "layer_descriptions": layer_descriptions,
        },
    }

    print(f"Nodes: {len(nodes)}")
    for t in ["analysis", "principle", "instrument", "pattern", "evidence"]:
        count = sum(1 for n in nodes if n["type"] == t)
        print(f"  {t}: {count}")
    print(f"Edges: {len(valid_edges)}")

    return data


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lens of Power — Framework Viewer</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script src="viewer-data.js"></script>
<style>
:root {
  --bg: #0d1117;
  --bg-sidebar: #161b22;
  --bg-card: #1c2128;
  --border: #30363d;
  --text: #e6edf3;
  --text-muted: #8b949e;
  --text-link: #58a6ff;
  --blue: #388bfd;
  --green: #3fb950;
  --orange: #d29922;
  --purple: #a371f7;
  --gray: #8b949e;
  --red: #f85149;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  height: 100vh;
  overflow: hidden;
}
#app { display: flex; height: 100vh; }

/* Sidebar */
#sidebar {
  width: 300px;
  min-width: 300px;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
#sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border);
}
#sidebar-header h1 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
#search {
  width: 100%;
  padding: 8px 12px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  font-size: 14px;
  outline: none;
}
#search:focus { border-color: var(--blue); }
#search::placeholder { color: var(--text-muted); }

#filters {
  display: flex;
  gap: 4px;
  margin-top: 10px;
  flex-wrap: wrap;
}
.filter-btn {
  padding: 3px 8px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: transparent;
  color: var(--text-muted);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.15s;
}
.filter-btn.active { border-color: currentColor; }
.filter-btn[data-type="analysis"].active { color: var(--blue); background: rgba(56,139,253,0.1); }
.filter-btn[data-type="principle"].active { color: var(--green); background: rgba(63,185,80,0.1); }
.filter-btn[data-type="instrument"].active { color: var(--orange); background: rgba(210,153,34,0.1); }
.filter-btn[data-type="pattern"].active { color: var(--purple); background: rgba(163,113,247,0.1); }
.filter-btn[data-type="evidence"].active { color: var(--gray); background: rgba(139,148,158,0.1); }

#sidebar-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}
.sidebar-group { margin-bottom: 4px; }
.sidebar-group-header {
  padding: 6px 16px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}
.sidebar-group-header .count {
  font-weight: 400;
  opacity: 0.7;
}
.sidebar-group-header .chevron {
  font-size: 10px;
  transition: transform 0.15s;
}
.sidebar-group.collapsed .chevron { transform: rotate(-90deg); }
.sidebar-group.collapsed .sidebar-group-items { display: none; }
.sidebar-item {
  padding: 6px 16px 6px 24px;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  border-left: 2px solid transparent;
  transition: background 0.1s;
}
.sidebar-item:hover { background: rgba(255,255,255,0.04); }
.sidebar-item.active {
  background: rgba(56,139,253,0.1);
  border-left-color: var(--blue);
}
.sidebar-item .type-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
  vertical-align: middle;
}
.sidebar-item .item-subtitle {
  display: block;
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 1px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.sidebar-item .item-badges {
  display: inline-flex;
  gap: 4px;
  float: right;
  margin-top: 2px;
}
.sidebar-item .badge {
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 8px;
  font-weight: 500;
  line-height: 1.4;
}
.badge-degree {
  background: rgba(255,255,255,0.06);
  color: var(--text-muted);
}
.badge-established { background: rgba(63,185,80,0.15); color: var(--green); }
.badge-supported { background: rgba(210,153,34,0.15); color: var(--orange); }
.badge-preliminary { background: rgba(139,148,158,0.1); color: var(--text-muted); }

/* Sidebar resize handle */
#sidebar-resize {
  width: 4px;
  cursor: col-resize;
  background: transparent;
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  z-index: 10;
  transition: background 0.15s;
}
#sidebar-resize:hover, #sidebar-resize.dragging {
  background: var(--blue);
}
#sidebar { position: relative; }

/* Search clear button */
.search-wrap {
  position: relative;
}
.search-wrap #search {
  padding-right: 28px;
}
#search-clear {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 14px;
  padding: 2px 4px;
  line-height: 1;
  display: none;
}
#search-clear:hover { color: var(--text); }

/* Main panel */
#main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
#main-header {
  padding: 12px 24px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 12px;
}
#view-toggle {
  display: flex;
  gap: 0;
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
}
.view-btn {
  padding: 6px 14px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}
.view-btn.active {
  background: var(--bg-card);
  color: var(--text);
}
#main-title {
  font-size: 16px;
  font-weight: 600;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
#content-area {
  flex: 1;
  overflow: hidden;
  position: relative;
}

/* Detail view */
#detail-view {
  height: 100%;
  overflow-y: auto;
  padding: 32px 48px;
  max-width: 900px;
  display: none;
}
#detail-view .meta-bar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.meta-tag {
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}
.meta-tag.type-analysis { background: rgba(56,139,253,0.15); color: var(--blue); }
.meta-tag.type-principle { background: rgba(63,185,80,0.15); color: var(--green); }
.meta-tag.type-instrument { background: rgba(210,153,34,0.15); color: var(--orange); }
.meta-tag.type-pattern { background: rgba(163,113,247,0.15); color: var(--purple); }
.meta-tag.type-evidence { background: rgba(139,148,158,0.15); color: var(--gray); }

#detail-content {
  line-height: 1.7;
  font-size: 15px;
}
#detail-content h1 { font-size: 24px; margin: 0 0 16px 0; }
#detail-content h2 { font-size: 20px; margin: 28px 0 12px 0; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
#detail-content h3 { font-size: 16px; margin: 20px 0 8px 0; }
#detail-content p { margin: 0 0 12px 0; }
#detail-content ul, #detail-content ol { margin: 0 0 12px 24px; }
#detail-content li { margin-bottom: 4px; }
#detail-content blockquote {
  border-left: 3px solid var(--border);
  padding: 4px 16px;
  color: var(--text-muted);
  margin: 0 0 12px 0;
}
#detail-content code {
  background: var(--bg-card);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}
#detail-content pre {
  background: var(--bg-card);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0 0 12px 0;
}
#detail-content pre code { background: none; padding: 0; }
#detail-content table {
  border-collapse: collapse;
  margin: 0 0 12px 0;
  width: 100%;
}
#detail-content th, #detail-content td {
  border: 1px solid var(--border);
  padding: 8px 12px;
  text-align: left;
  font-size: 14px;
}
#detail-content th { background: var(--bg-card); }
#detail-content a, .cross-ref {
  color: var(--text-link);
  text-decoration: none;
  cursor: pointer;
}
#detail-content a:hover, .cross-ref:hover { text-decoration: underline; }
#detail-content hr { border: none; border-top: 1px solid var(--border); margin: 24px 0; }
#detail-content strong { color: #f0f3f6; }

/* Analysis TOC */
.analysis-toc {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px 18px;
  margin-bottom: 24px;
}
.toc-title {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.toc-link {
  display: block;
  padding: 3px 0;
  color: var(--text-link);
  text-decoration: none;
  font-size: 13px;
}
.toc-link:hover { text-decoration: underline; }
.toc-link.toc-briefing {
  font-weight: 600;
  color: var(--green);
}

/* Connected items panel */
#connected-panel {
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
}
#connected-panel h3 {
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  margin-bottom: 12px;
}
.connected-item {
  display: inline-block;
  padding: 4px 12px;
  margin: 0 6px 6px 0;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}
.connected-item:hover { background: rgba(255,255,255,0.06); }

/* Graph view */
#graph-view {
  width: 100%;
  height: 100%;
  display: none;
  position: relative;
}
#graph-view svg { width: 100%; height: 100%; }
.graph-node { cursor: pointer; }
.graph-node circle { stroke-width: 2px; transition: r 0.15s; }
.graph-node text {
  font-size: 10px;
  fill: var(--text-muted);
  pointer-events: none;
}
.graph-link { stroke-opacity: 0.3; }
.graph-link.highlight { stroke-opacity: 0.8; stroke-width: 2.5px !important; }
.graph-node.highlight circle { stroke-width: 3px; }
.graph-node.dimmed { opacity: 0.1; }
.graph-link.dimmed { stroke-opacity: 0.03; }

/* Reset button */
.view-reset-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 5px 12px;
  background: var(--bg-sidebar);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text-muted);
  font-size: 12px;
  cursor: pointer;
  z-index: 50;
  transition: all 0.15s;
}
.view-reset-btn:hover {
  color: var(--text);
  border-color: var(--text-muted);
}

/* Graph legend */
#graph-legend {
  position: absolute;
  bottom: 16px;
  right: 16px;
  background: var(--bg-sidebar);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 11px;
  z-index: 50;
  max-width: 220px;
  display: none;
}
.legend-section { margin-bottom: 10px; }
.legend-section:last-child { margin-bottom: 0; }
.legend-title {
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
  font-size: 10px;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 3px;
  color: var(--text-muted);
}
.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.legend-line {
  width: 16px;
  height: 2px;
  flex-shrink: 0;
  border-radius: 1px;
}

/* Dashboard view */
#dashboard-view {
  height: 100%;
  overflow-y: auto;
  padding: 32px 48px;
  max-width: 960px;
}
.stats-bar {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  margin-bottom: 16px;
  padding: 16px 20px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
}
.stats-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 70px;
}
.stats-value {
  font-size: 24px;
  font-weight: 700;
  line-height: 1.2;
}
.stats-label {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.corroboration-bar {
  margin-bottom: 32px;
}
.dashboard-section {
  margin-bottom: 36px;
}
.dashboard-section > h2,
.dashboard-section-header > h2 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
  color: var(--text);
  flex: 1;
}
.dashboard-content {
  line-height: 1.7;
  font-size: 14px;
  color: var(--text-muted);
}
.dashboard-content h3 { color: var(--text); font-size: 15px; margin: 20px 0 8px 0; }
.dashboard-content p { margin: 0 0 10px 0; }
.dashboard-content ul, .dashboard-content ol { margin: 0 0 10px 24px; }
.dashboard-content li { margin-bottom: 3px; }
.dashboard-content blockquote {
  border-left: 3px solid var(--border);
  padding: 4px 16px;
  color: var(--text-muted);
  margin: 0 0 10px 0;
}
.dashboard-content code {
  background: var(--bg-card);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}
.dashboard-content pre {
  background: var(--bg-card);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0 0 10px 0;
  font-size: 12px;
}
.dashboard-content pre code { background: none; padding: 0; }
.dashboard-content table {
  border-collapse: collapse;
  margin: 0 0 10px 0;
  width: 100%;
}
.dashboard-content th, .dashboard-content td {
  border: 1px solid var(--border);
  padding: 6px 10px;
  text-align: left;
  font-size: 13px;
}
.dashboard-content th { background: var(--bg-card); color: var(--text); }
.dashboard-content strong { color: var(--text); }
.dashboard-content em { color: var(--text-muted); }
.dashboard-content a { color: var(--text-link); text-decoration: none; }
.layer-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
}
.layer-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px 16px;
}
.layer-card-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 6px;
  color: var(--text);
}
.layer-card-desc {
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-muted);
}
.works-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}
.work-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px 16px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}
.work-card:hover {
  border-color: var(--green);
  background: rgba(63,185,80,0.04);
}
.work-card-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
  color: var(--text);
}
.work-card-source {
  font-size: 12px;
  line-height: 1.4;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.work-card-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
}
.work-count {
  color: var(--green);
  font-weight: 500;
}
.work-layers {
  color: var(--text-muted);
}

/* Recent analyses cards */
.recent-analyses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 12px;
}
.recent-analysis-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px 18px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}
.recent-analysis-card:hover {
  border-color: var(--blue);
  background: rgba(56,139,253,0.04);
}
.recent-analysis-date {
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 4px;
}
.recent-analysis-title {
  font-weight: 600;
  font-size: 14px;
  color: var(--text);
  margin-bottom: 4px;
}
.recent-analysis-source {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.recent-analysis-briefing {
  font-size: 12px;
  line-height: 1.5;
  color: var(--text-muted);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Layer coverage bar */
.layer-card-coverage {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.layer-coverage-bar {
  flex: 1;
  height: 4px;
  background: rgba(255,255,255,0.06);
  border-radius: 2px;
  overflow: hidden;
}
.layer-coverage-fill {
  height: 100%;
  border-radius: 2px;
  background: var(--purple);
  transition: width 0.3s;
}
.layer-coverage-count {
  font-size: 11px;
  color: var(--text-muted);
  min-width: 40px;
  text-align: right;
}

/* View navigation cards */
.view-nav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}
.view-nav-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  text-align: center;
}
.view-nav-card:hover {
  border-color: var(--blue);
  background: rgba(56,139,253,0.04);
}
.view-nav-icon {
  font-size: 24px;
  margin-bottom: 8px;
  opacity: 0.7;
}
.view-nav-label {
  font-weight: 600;
  font-size: 13px;
  color: var(--text);
  margin-bottom: 4px;
}
.view-nav-desc {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.4;
}

/* Collapsible documentation sections */
.dashboard-section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: default;
}
.dashboard-section-header.collapsible {
  cursor: pointer;
}
.dashboard-section-header.collapsible:hover h2 {
  color: var(--text-link);
}
.dashboard-section-header .section-chevron {
  font-size: 12px;
  color: var(--text-muted);
  transition: transform 0.15s;
}
.dashboard-section.collapsed .section-chevron {
  transform: rotate(-90deg);
}
.dashboard-section.collapsed .dashboard-content {
  display: none;
}

/* Layers view */
#layers-view {
  width: 100%;
  height: 100%;
  display: none;
}
#layers-view svg { width: 100%; height: 100%; }
.layers-col-header {
  font-size: 11px;
  font-weight: 600;
  fill: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.layers-item rect {
  transition: opacity 0.15s;
}
.layers-item text {
  font-size: 10px;
  pointer-events: none;
}

/* Matrix view */
#matrix-view {
  width: 100%;
  height: 100%;
  overflow: auto;
  display: none;
  padding: 24px;
}
.matrix-container {
  min-width: max-content;
}
.matrix-table {
  border-collapse: collapse;
  font-size: 12px;
}
.matrix-table th {
  position: sticky;
  top: 0;
  background: var(--bg);
  z-index: 2;
  padding: 0;
}
.matrix-table th.matrix-corner {
  position: sticky;
  left: 0;
  z-index: 3;
}
.matrix-col-header {
  writing-mode: vertical-lr;
  transform: rotate(180deg);
  padding: 8px 4px;
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
  white-space: nowrap;
  max-height: 180px;
  overflow: hidden;
  cursor: pointer;
}
.matrix-col-header:hover { color: var(--text); }
.matrix-row-header {
  position: sticky;
  left: 0;
  background: var(--bg);
  z-index: 1;
  padding: 4px 12px 4px 8px;
  text-align: left;
  font-weight: 500;
  white-space: nowrap;
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
  color: var(--text-muted);
  border-right: 1px solid var(--border);
}
.matrix-row-header:hover { color: var(--text); }
.matrix-corr {
  font-size: 9px;
  font-weight: 400;
  margin-left: 6px;
  padding: 1px 5px;
  border-radius: 8px;
  vertical-align: middle;
}
.matrix-corr-ESTABLISHED { background: rgba(63,185,80,0.2); color: var(--green); }
.matrix-corr-SUPPORTED { background: rgba(210,153,34,0.2); color: var(--orange); }
.matrix-corr-PRELIMINARY { background: rgba(139,148,158,0.2); color: var(--gray); }
.matrix-cell {
  padding: 0;
  text-align: center;
  min-width: 28px;
  height: 28px;
  border: 1px solid rgba(48,54,61,0.4);
  cursor: default;
}
.matrix-cell.filled {
  cursor: pointer;
}
.matrix-dot {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 3px;
}
.matrix-row:hover .matrix-row-header { color: var(--text); }
.matrix-row.highlight .matrix-row-header { color: var(--text); font-weight: 600; }
.matrix-row.dimmed { opacity: 0.2; }
.matrix-count {
  position: sticky;
  right: 0;
  background: var(--bg);
  padding: 4px 8px;
  text-align: center;
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 600;
  border-left: 1px solid var(--border);
}

/* Graph tooltip */
#graph-tooltip {
  position: absolute;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 13px;
  pointer-events: none;
  display: none;
  max-width: 300px;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}
#graph-tooltip .tt-title { font-weight: 600; margin-bottom: 4px; }
#graph-tooltip .tt-type { font-size: 11px; color: var(--text-muted); }

/* Scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }
</style>
</head>
<body>
<div id="app">
  <div id="sidebar">
    <div id="sidebar-header">
      <h1>Lens of Power</h1>
      <div class="search-wrap">
        <input type="text" id="search" placeholder="Search items...">
        <button id="search-clear" title="Clear search">&times;</button>
      </div>
      <div id="filters">
        <button class="filter-btn active" data-type="analysis">Analyses</button>
        <button class="filter-btn active" data-type="principle">Principles</button>
        <button class="filter-btn active" data-type="instrument">Instruments</button>
        <button class="filter-btn active" data-type="pattern">Patterns</button>
        <button class="filter-btn active" data-type="evidence">Evidence</button>
      </div>
    </div>
    <div id="sidebar-list"></div>
    <div id="sidebar-resize"></div>
  </div>
  <div id="main">
    <div id="main-header">
      <div id="view-toggle">
        <button class="view-btn active" data-view="dashboard">Dashboard</button>
        <button class="view-btn" data-view="detail">Content</button>
        <button class="view-btn" data-view="graph">Graph</button>
        <button class="view-btn" data-view="layers">Layers</button>
        <button class="view-btn" data-view="matrix">Matrix</button>
      </div>
      <div id="main-title"></div>
    </div>
    <div id="content-area">
      <div id="dashboard-view"></div>
      <div id="detail-view"></div>
      <div id="graph-view">
        <div id="graph-legend"></div>
        <button class="view-reset-btn" id="graph-reset" title="Reset zoom and focus">Reset</button>
      </div>
      <div id="layers-view">
        <button class="view-reset-btn" id="layers-reset" title="Reset zoom">Reset</button>
      </div>
      <div id="matrix-view"></div>
      <div id="graph-tooltip">
        <div class="tt-title"></div>
        <div class="tt-type"></div>
      </div>
    </div>
  </div>
</div>

<script>
// Data loaded from external file (viewer-data.js)

const TYPE_COLORS = {
  analysis: '#388bfd',
  principle: '#3fb950',
  instrument: '#d29922',
  pattern: '#a371f7',
  evidence: '#8b949e',
};

const TYPE_LABELS = {
  analysis: 'Analyses',
  principle: 'Principles',
  instrument: 'Instruments',
  pattern: 'Patterns',
  evidence: 'Evidence',
};

const TYPE_ORDER = ['analysis', 'principle', 'instrument', 'pattern', 'evidence'];

const LAYER_NAMES = [
  'Thought & Narrative',
  'Economic',
  'Legal & Regulatory',
  'Institutional',
  'Surveillance & Information',
  'Physical & Coercive',
];

const EDGE_COLORS = {
  observed_in: '#58a6ff',
  key_pattern: '#a371f7',
  evidence: '#8b949e',
  evidence_for: '#8b949e',
  matches: '#3fb950',
  references: '#d29922',
  applies_instrument: '#f0883e',
  produces_instrument: '#db6d28',
};

const EDGE_LABELS = {
  observed_in: 'observed in',
  key_pattern: 'key pattern',
  evidence: 'evidence',
  evidence_for: 'evidence for',
  matches: 'matches',
  references: 'references',
  applies_instrument: 'applies instrument',
  produces_instrument: 'produces instrument',
};

// State
let activeFilters = new Set(TYPE_ORDER);
let currentView = 'dashboard';
let selectedNode = null;
let searchQuery = '';

// Index
const nodeMap = {};
DATA.nodes.forEach(n => { nodeMap[n.id] = n; });

// Build adjacency and degree
const adjacency = {};
const nodeDegree = {};
DATA.nodes.forEach(n => { adjacency[n.id] = { incoming: [], outgoing: [] }; nodeDegree[n.id] = 0; });
DATA.edges.forEach(e => {
  if (adjacency[e.source]) { adjacency[e.source].outgoing.push(e); nodeDegree[e.source]++; }
  if (adjacency[e.target]) { adjacency[e.target].incoming.push(e); nodeDegree[e.target]++; }
});

// Graph state (persistent across rebuilds for focus mode)
let graphSvg = null;
let graphZoom = null;
let graphNodeSel = null;
let graphLinkSel = null;
let layersSvg = null;
let layersZoom = null;

// ---------------------------------------------------------------------------
// Sidebar
// ---------------------------------------------------------------------------
function getDisplayTitle(node) {
  if (node.type === 'analysis') {
    return node.title.replace(/^Analysis:\s*/i, '');
  }
  if (node.type === 'principle') {
    return node.title.replace(/^Principles:\s*/i, '');
  }
  return node.title;
}

function getSubtitle(node) {
  if (node.type === 'analysis') {
    const parts = [];
    if (node.meta.source) parts.push(node.meta.source);
    if (node.meta.date) {
      let ts = node.meta.date;
      if (node.meta.time) ts += ' ' + node.meta.time;
      parts.push(ts);
    }
    return parts.join(' — ');
  }
  if (node.type === 'evidence') {
    const parts = [];
    if (node.meta.source) parts.push(node.meta.source);
    if (node.meta.date) parts.push(node.meta.date);
    return parts.join(' — ');
  }
  if (node.type === 'principle') {
    return node.meta.source || '';
  }
  return '';
}

function buildSidebar() {
  const list = document.getElementById('sidebar-list');
  list.innerHTML = '';
  const q = searchQuery.toLowerCase();

  TYPE_ORDER.forEach(type => {
    if (!activeFilters.has(type)) return;
    const items = DATA.nodes
      .filter(n => n.type === type)
      .filter(n => !q || n.title.toLowerCase().includes(q) || n.content.toLowerCase().includes(q))
      .sort((a, b) => type === 'analysis'
        ? (b.meta.date || '').localeCompare(a.meta.date || '')
        : a.title.localeCompare(b.title));

    if (items.length === 0) return;

    const group = document.createElement('div');
    group.className = 'sidebar-group';
    group.innerHTML =
      '<div class="sidebar-group-header">' +
        '<span class="chevron">&#9660;</span>' +
        TYPE_LABELS[type] + ' <span class="count">(' + items.length + ')</span>' +
      '</div>' +
      '<div class="sidebar-group-items"></div>';

    const header = group.querySelector('.sidebar-group-header');
    header.addEventListener('click', () => { group.classList.toggle('collapsed'); });

    const container = group.querySelector('.sidebar-group-items');
    items.forEach(n => {
      const item = document.createElement('div');
      item.className = 'sidebar-item' + (selectedNode && selectedNode.id === n.id ? ' active' : '');
      item.dataset.nodeId = n.id;
      const displayTitle = getDisplayTitle(n);
      const subtitle = getSubtitle(n);

      // Build badges
      let badges = '';
      const degree = nodeDegree[n.id] || 0;
      if (n.type === 'pattern') {
        const corr = (n.meta.corroboration || '').split(' ')[0];
        const cls = corr === 'ESTABLISHED' ? 'badge-established' :
                    corr === 'SUPPORTED' ? 'badge-supported' : 'badge-preliminary';
        const label = corr === 'ESTABLISHED' ? 'EST' :
                      corr === 'SUPPORTED' ? 'SUP' : 'PRE';
        badges = '<span class="item-badges"><span class="badge ' + cls + '">' + label + '</span></span>';
      } else if (degree > 2) {
        badges = '<span class="item-badges"><span class="badge badge-degree">' + degree + '</span></span>';
      }

      let html = badges +
        '<span class="type-dot" style="background:' + TYPE_COLORS[type] + '"></span>' + escapeHtml(displayTitle);
      if (subtitle) {
        html += '<span class="item-subtitle">' + escapeHtml(subtitle) + '</span>';
      }
      item.innerHTML = html;
      item.addEventListener('click', () => selectNode(n.id));
      container.appendChild(item);
    });

    list.appendChild(group);
  });
}

// ---------------------------------------------------------------------------
// Dashboard view
// ---------------------------------------------------------------------------
function buildDashboard() {
  const view = document.getElementById('dashboard-view');

  const typeCounts = {};
  TYPE_ORDER.forEach(t => { typeCounts[t] = 0; });
  DATA.nodes.forEach(n => { typeCounts[n.type] = (typeCounts[n.type] || 0) + 1; });

  const patterns = DATA.nodes.filter(n => n.type === 'pattern');
  const corroboration = { ESTABLISHED: 0, SUPPORTED: 0, PRELIMINARY: 0 };
  patterns.forEach(p => {
    const c = (p.meta.corroboration || '').split(' ')[0];
    if (corroboration.hasOwnProperty(c)) corroboration[c]++;
  });

  // Compute layer coverage counts
  const layerCoverage = {};
  LAYER_NAMES.forEach(l => { layerCoverage[l] = 0; });
  DATA.nodes.forEach(n => {
    if (n.meta && n.meta.layer_list) {
      n.meta.layer_list.forEach(l => {
        if (layerCoverage.hasOwnProperty(l)) layerCoverage[l]++;
      });
    }
  });
  const maxCoverage = Math.max(1, ...Object.values(layerCoverage));

  let html = '';

  // --- Stats bar ---
  html += '<div class="stats-bar">';
  TYPE_ORDER.forEach(t => {
    html += '<div class="stats-item"><span class="stats-value" style="color:' + TYPE_COLORS[t] + '">' + typeCounts[t] + '</span><span class="stats-label">' + TYPE_LABELS[t] + '</span></div>';
  });
  html += '<div class="stats-item"><span class="stats-value">' + DATA.edges.length + '</span><span class="stats-label">Connections</span></div>';
  html += '</div>';

  html += '<div class="stats-bar corroboration-bar">';
  html += '<div class="stats-item"><span class="stats-value" style="color:var(--green)">' + corroboration.ESTABLISHED + '</span><span class="stats-label">Established</span></div>';
  html += '<div class="stats-item"><span class="stats-value" style="color:var(--orange)">' + corroboration.SUPPORTED + '</span><span class="stats-label">Supported</span></div>';
  html += '<div class="stats-item"><span class="stats-value" style="color:var(--text-muted)">' + corroboration.PRELIMINARY + '</span><span class="stats-label">Preliminary</span></div>';
  html += '</div>';

  // --- Recent Analyses ---
  const analyses = DATA.nodes
    .filter(n => n.type === 'analysis')
    .sort((a, b) => (b.meta.date || '').localeCompare(a.meta.date || ''))
    .slice(0, 3);
  if (analyses.length > 0) {
    html += '<div class="dashboard-section"><h2>Recent Analyses</h2><div class="recent-analyses-grid">';
    analyses.forEach(a => {
      const title = getDisplayTitle(a);
      const dateParts = [];
      if (a.meta.date) dateParts.push(a.meta.date);
      if (a.meta.time) dateParts.push(a.meta.time);
      const dateStr = dateParts.join(' ');
      // Extract first sentence of briefing from content
      let briefing = '';
      const briefMatch = a.content.match(/## Briefing[\s\S]*?\n\n([\s\S]*?)(?:\n\n## |\n---)/);
      if (briefMatch) {
        briefing = briefMatch[1].replace(/\*\*/g, '').replace(/\n/g, ' ').trim();
        if (briefing.length > 200) briefing = briefing.substring(0, 200) + '...';
      }
      html += '<div class="recent-analysis-card" data-id="' + a.id + '">';
      html += '<div class="recent-analysis-date">' + escapeHtml(dateStr) + '</div>';
      html += '<div class="recent-analysis-title">' + escapeHtml(title) + '</div>';
      if (a.meta.source) html += '<div class="recent-analysis-source">' + escapeHtml(a.meta.source) + '</div>';
      if (briefing) html += '<div class="recent-analysis-briefing">' + escapeHtml(briefing) + '</div>';
      html += '</div>';
    });
    html += '</div></div>';
  }

  // --- Works studied ---
  const principles = DATA.nodes.filter(n => n.type === 'principle');
  if (principles.length > 0) {
    const sorted = principles.slice().sort((a, b) => (b.meta.principle_count || 0) - (a.meta.principle_count || 0));
    html += '<div class="dashboard-section"><h2>Works Studied</h2><div class="works-grid">';
    sorted.forEach(p => {
      const title = getDisplayTitle(p);
      const source = p.meta.source || '';
      const count = p.meta.principle_count || 0;
      const layers = (p.meta.layer_list || []);
      html += '<div class="work-card" data-id="' + p.id + '">' +
        '<div class="work-card-title">' + escapeHtml(title) + '</div>' +
        '<div class="work-card-source">' + escapeHtml(source) + '</div>' +
        '<div class="work-card-meta">' +
          '<span class="work-count">' + count + ' principles</span>' +
          '<span class="work-layers">' + layers.length + ' layers</span>' +
        '</div>' +
      '</div>';
    });
    html += '</div></div>';
  }

  // --- Layers of Power with coverage ---
  const layerDescs = DATA.meta.layer_descriptions || [];
  if (layerDescs.length > 0) {
    html += '<div class="dashboard-section"><h2>Layers of Power</h2><div class="layer-cards">';
    layerDescs.forEach(l => {
      const count = layerCoverage[l.name] || 0;
      const pct = Math.round((count / maxCoverage) * 100);
      html += '<div class="layer-card">' +
        '<div class="layer-card-name">' + escapeHtml(l.name) + '</div>' +
        '<div class="layer-card-desc">' + escapeHtml(l.description) + '</div>' +
        '<div class="layer-card-coverage">' +
          '<div class="layer-coverage-bar"><div class="layer-coverage-fill" style="width:' + pct + '%"></div></div>' +
          '<span class="layer-coverage-count">' + count + ' items</span>' +
        '</div>' +
      '</div>';
    });
    html += '</div></div>';
  }

  // --- View navigation cards ---
  html += '<div class="dashboard-section"><h2>Explore</h2><div class="view-nav-grid">';
  html += '<div class="view-nav-card" data-view="graph">' +
    '<div class="view-nav-icon">&#9678;</div>' +
    '<div class="view-nav-label">Force Graph</div>' +
    '<div class="view-nav-desc">Connections between all framework items</div></div>';
  html += '<div class="view-nav-card" data-view="layers">' +
    '<div class="view-nav-icon">&#9638;</div>' +
    '<div class="view-nav-label">Layer Map</div>' +
    '<div class="view-nav-desc">Items organized by power layer</div></div>';
  html += '<div class="view-nav-card" data-view="matrix">' +
    '<div class="view-nav-icon">&#9635;</div>' +
    '<div class="view-nav-label">Corroboration Matrix</div>' +
    '<div class="view-nav-desc">Which sources confirm which patterns</div></div>';
  html += '</div></div>';

  // --- Documentation sections (collapsible) ---
  const sections = DATA.meta.readme_sections || {};
  if (sections.core_concepts) {
    html += '<div class="dashboard-section">' +
      '<div class="dashboard-section-header collapsible"><span class="section-chevron">&#9660;</span><h2>Core Concepts</h2></div>' +
      '<div class="dashboard-content">' + marked.parse(sections.core_concepts) + '</div></div>';
  }
  if (sections.how_framework_grows) {
    html += '<div class="dashboard-section">' +
      '<div class="dashboard-section-header collapsible"><span class="section-chevron">&#9660;</span><h2>How the Framework Grows</h2></div>' +
      '<div class="dashboard-content">' + marked.parse(sections.how_framework_grows) + '</div></div>';
  }
  if (sections.integrity_constraints) {
    html += '<div class="dashboard-section">' +
      '<div class="dashboard-section-header collapsible"><span class="section-chevron">&#9660;</span><h2>Integrity Constraints</h2></div>' +
      '<div class="dashboard-content">' + marked.parse(sections.integrity_constraints) + '</div></div>';
  }

  view.innerHTML = html;

  // Work card click handlers
  view.querySelectorAll('.work-card').forEach(card => {
    card.addEventListener('click', () => {
      const id = card.dataset.id;
      if (id && nodeMap[id]) selectNode(id, { forceDetail: true });
    });
  });

  // Recent analysis card click handlers
  view.querySelectorAll('.recent-analysis-card').forEach(card => {
    card.addEventListener('click', () => {
      const id = card.dataset.id;
      if (id && nodeMap[id]) selectNode(id, { forceDetail: true });
    });
  });

  // View navigation card click handlers
  view.querySelectorAll('.view-nav-card').forEach(card => {
    card.addEventListener('click', () => {
      const v = card.dataset.view;
      if (v) switchView(v);
    });
  });

  // Collapsible documentation section handlers
  view.querySelectorAll('.dashboard-section-header.collapsible').forEach(header => {
    header.addEventListener('click', () => {
      header.closest('.dashboard-section').classList.toggle('collapsed');
    });
  });
}

// ---------------------------------------------------------------------------
// Detail view
// ---------------------------------------------------------------------------
function showDetail(nodeId) {
  const node = nodeMap[nodeId];
  if (!node) return;

  const view = document.getElementById('detail-view');

  // Meta bar
  let metaHtml = '<div class="meta-bar"><span class="meta-tag type-' + node.type + '">' + node.type + '</span>';
  if (node.meta) {
    Object.entries(node.meta).forEach(([k, v]) => {
      if (v && typeof v === 'string' && v.length < 100 && k !== 'statement' && k !== 'mechanism' && k !== 'layer_list') {
        metaHtml += '<span class="meta-tag" style="background:rgba(255,255,255,0.06);color:var(--text-muted)">' + k + ': ' + escapeHtml(v) + '</span>';
      }
    });
  }
  metaHtml += '</div>';

  // Render markdown
  let rendered = marked.parse(node.content);
  rendered = rendered.replace(
    /(?:(?:principles|analyses|instruments|evidence)\/[\w\-]+\.md)/g,
    function(match) {
      if (nodeMap[match]) {
        return '<span class="cross-ref" data-target="' + match + '">' + escapeHtml(nodeMap[match].title || match) + '</span>';
      }
      return match;
    }
  );

  // Connected items
  const adj = adjacency[nodeId] || { incoming: [], outgoing: [] };
  const connected = new Map();
  adj.outgoing.forEach(e => {
    const target = nodeMap[e.target];
    if (target) connected.set(e.target, { node: target, type: e.type, direction: 'outgoing' });
  });
  adj.incoming.forEach(e => {
    const source = nodeMap[e.source];
    if (source) connected.set(e.source, { node: source, type: e.type, direction: 'incoming' });
  });

  let connectedHtml = '';
  if (connected.size > 0) {
    connectedHtml = '<div id="connected-panel"><h3>Connected Items</h3>';
    connected.forEach((info, id) => {
      const color = TYPE_COLORS[info.node.type];
      connectedHtml += '<span class="connected-item" data-target="' + id + '" style="border-color:' + color + '40">' +
        '<span class="type-dot" style="background:' + color + '"></span>' +
        escapeHtml(info.node.title) +
        '<span style="color:var(--text-muted);font-size:11px;margin-left:4px">' + info.type + '</span>' +
      '</span>';
    });
    connectedHtml += '</div>';
  }

  view.innerHTML = metaHtml + '<div id="detail-content">' + rendered + '</div>' + connectedHtml;

  // For analyses: generate TOC and move briefing to top
  if (node.type === 'analysis') {
    const content = view.querySelector('#detail-content');
    if (content) {
      // Remove markdown-generated "Contents" section (viewer builds its own TOC)
      const allH2s = content.querySelectorAll('h2');
      allH2s.forEach(h => {
        if (h.textContent.trim().toLowerCase() === 'contents') {
          // Remove everything between this H2 and the next H2
          let sib = h.nextElementSibling;
          while (sib && sib.tagName !== 'H2') {
            const next = sib.nextElementSibling;
            sib.remove();
            sib = next;
          }
          h.remove();
        }
      });

      // Collect H2 headings for TOC
      const h2s = content.querySelectorAll('h2');
      if (h2s.length > 1) {
        // Add IDs to headings
        h2s.forEach((h, i) => { h.id = 'section-' + i; });

        // Find the briefing/summary section and move it before the first H2
        let briefingH2 = null;
        h2s.forEach(h => {
          const ht = h.textContent.toLowerCase().trim();
          if (ht.includes('briefing') || ht === 'summary') briefingH2 = h;
        });
        if (briefingH2 && h2s.length > 2) {
          // Collect all nodes belonging to the briefing section
          const briefingNodes = [briefingH2];
          let sib = briefingH2.nextElementSibling;
          while (sib && sib.tagName !== 'H2') {
            briefingNodes.push(sib);
            sib = sib.nextElementSibling;
          }
          // Insert before the first H2 (Narrative)
          const firstH2 = h2s[0];
          briefingNodes.forEach(n => content.insertBefore(n, firstH2));
        }

        // Build TOC (re-query since DOM changed)
        const updatedH2s = content.querySelectorAll('h2');
        let tocHtml = '<nav class="analysis-toc"><div class="toc-title">Contents</div>';
        updatedH2s.forEach((h, i) => {
          h.id = 'section-' + i;
          const text = h.textContent.replace(/^Step \d+:\s*/, '');
          const hText = h.textContent.toLowerCase().trim();
          const isBriefing = hText.includes('briefing') || hText === 'summary';
          tocHtml += '<a class="toc-link' + (isBriefing ? ' toc-briefing' : '') + '" href="#section-' + i + '">' + escapeHtml(text) + '</a>';
        });
        tocHtml += '</nav>';
        content.insertAdjacentHTML('afterbegin', tocHtml);

        // TOC smooth scroll
        content.querySelectorAll('.toc-link').forEach(a => {
          a.addEventListener('click', (e) => {
            e.preventDefault();
            const target = content.querySelector(a.getAttribute('href'));
            if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          });
        });
      }
    }
  }

  // Attach click handlers for cross-refs
  view.querySelectorAll('.cross-ref, .connected-item').forEach(el => {
    el.addEventListener('click', () => {
      const target = el.dataset.target;
      if (target && nodeMap[target]) selectNode(target, { forceDetail: true });
    });
  });

  document.getElementById('main-title').textContent = getDisplayTitle(node);
}

// ---------------------------------------------------------------------------
// Graph view
// ---------------------------------------------------------------------------
function buildGraph() {
  const container = document.getElementById('graph-view');
  // Remove only the SVG, keep legend
  const oldSvg = container.querySelector('svg');
  if (oldSvg) oldSvg.remove();

  const width = container.clientWidth;
  const height = container.clientHeight;

  const filteredNodes = DATA.nodes.filter(n => activeFilters.has(n.type));
  const filteredIds = new Set(filteredNodes.map(n => n.id));
  const filteredEdges = DATA.edges.filter(e => filteredIds.has(e.source) && filteredIds.has(e.target));

  const svg = d3.select(container).insert('svg', ':first-child')
    .attr('width', width)
    .attr('height', height);

  const g = svg.append('g');

  // Zoom
  const zoom = d3.zoom()
    .scaleExtent([0.1, 4])
    .on('zoom', (event) => g.attr('transform', event.transform));
  svg.call(zoom);

  // Simulation
  const simulation = d3.forceSimulation(filteredNodes)
    .force('link', d3.forceLink(filteredEdges).id(d => d.id).distance(80))
    .force('charge', d3.forceManyBody().strength(-200))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(d => nodeRadius(d) + 4));

  // Links
  const link = g.append('g')
    .selectAll('line')
    .data(filteredEdges)
    .join('line')
    .attr('class', 'graph-link')
    .attr('stroke', d => EDGE_COLORS[d.type] || '#30363d')
    .attr('stroke-width', 1);

  // Edge hover targets (wider invisible lines)
  const linkHover = g.append('g')
    .selectAll('line')
    .data(filteredEdges)
    .join('line')
    .attr('stroke', 'transparent')
    .attr('stroke-width', 8)
    .style('cursor', 'pointer');

  // Nodes
  const node = g.append('g')
    .selectAll('g')
    .data(filteredNodes)
    .join('g')
    .attr('class', 'graph-node')
    .call(d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended));

  node.append('circle')
    .attr('r', d => nodeRadius(d))
    .attr('fill', d => TYPE_COLORS[d.type])
    .attr('stroke', d => TYPE_COLORS[d.type]);

  node.append('text')
    .text(d => d.title.length > 25 ? d.title.substring(0, 25) + '...' : d.title)
    .attr('x', d => nodeRadius(d) + 4)
    .attr('y', 4);

  // Tooltip
  const tooltip = document.getElementById('graph-tooltip');

  // Node hover
  node.on('mouseover', (event, d) => {
    tooltip.querySelector('.tt-title').textContent = d.title;
    tooltip.querySelector('.tt-type').textContent = d.type;
    tooltip.style.display = 'block';
    tooltip.style.left = (event.pageX + 12) + 'px';
    tooltip.style.top = (event.pageY - 20) + 'px';

    highlightNeighborhood(d.id, node, link);
  });

  node.on('mousemove', (event) => {
    tooltip.style.left = (event.pageX + 12) + 'px';
    tooltip.style.top = (event.pageY - 20) + 'px';
  });

  node.on('mouseout', () => {
    tooltip.style.display = 'none';
    clearHighlight(node, link);
  });

  node.on('click', (event, d) => {
    selectNode(d.id, { forceDetail: true });
  });

  // Edge hover
  linkHover.on('mouseover', (event, d) => {
    const srcId = typeof d.source === 'object' ? d.source.id : d.source;
    const tgtId = typeof d.target === 'object' ? d.target.id : d.target;
    tooltip.querySelector('.tt-title').textContent = EDGE_LABELS[d.type] || d.type;
    tooltip.querySelector('.tt-type').textContent =
      (nodeMap[srcId] ? nodeMap[srcId].title : srcId) + ' \u2192 ' +
      (nodeMap[tgtId] ? nodeMap[tgtId].title : tgtId);
    tooltip.style.display = 'block';
    tooltip.style.left = (event.pageX + 12) + 'px';
    tooltip.style.top = (event.pageY - 20) + 'px';
  });

  linkHover.on('mousemove', (event) => {
    tooltip.style.left = (event.pageX + 12) + 'px';
    tooltip.style.top = (event.pageY - 20) + 'px';
  });

  linkHover.on('mouseout', () => {
    tooltip.style.display = 'none';
  });

  simulation.on('tick', () => {
    link
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y);
    linkHover
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y);
    node.attr('transform', d => 'translate(' + d.x + ',' + d.y + ')');
  });

  // Store references for focus mode
  graphSvg = svg;
  graphZoom = zoom;
  graphNodeSel = node;
  graphLinkSel = link;

  // Build legend
  buildGraphLegend();

  // If a node is selected, focus on it
  if (selectedNode) {
    setTimeout(() => focusGraphNode(selectedNode.id), 300);
  }

  function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
  }
  function dragged(event) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
  }
  function dragended(event) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
  }
}

function nodeRadius(d) {
  const degree = nodeDegree[d.id] || 0;
  return Math.max(5, Math.min(18, 4 + degree * 1.2));
}

function highlightNeighborhood(nodeId, nodeSel, linkSel) {
  const connIds = new Set([nodeId]);
  DATA.edges.forEach(e => {
    const src = typeof e.source === 'object' ? e.source.id : e.source;
    const tgt = typeof e.target === 'object' ? e.target.id : e.target;
    if (src === nodeId) connIds.add(tgt);
    if (tgt === nodeId) connIds.add(src);
  });

  nodeSel.classed('highlight', n => n.id === nodeId);
  nodeSel.classed('dimmed', n => !connIds.has(n.id));
  linkSel.classed('highlight', e => {
    const src = typeof e.source === 'object' ? e.source.id : e.source;
    const tgt = typeof e.target === 'object' ? e.target.id : e.target;
    return src === nodeId || tgt === nodeId;
  });
  linkSel.classed('dimmed', e => {
    const src = typeof e.source === 'object' ? e.source.id : e.source;
    const tgt = typeof e.target === 'object' ? e.target.id : e.target;
    return src !== nodeId && tgt !== nodeId;
  });
}

function clearHighlight(nodeSel, linkSel) {
  nodeSel.classed('highlight', false).classed('dimmed', false);
  linkSel.classed('highlight', false).classed('dimmed', false);
}

function focusGraphNode(nodeId) {
  if (!graphNodeSel || !graphLinkSel || !graphSvg) return;

  const d = DATA.nodes.find(n => n.id === nodeId);
  if (!d || d.x === undefined) return;

  highlightNeighborhood(nodeId, graphNodeSel, graphLinkSel);

  // Zoom to node
  const container = document.getElementById('graph-view');
  const width = container.clientWidth;
  const height = container.clientHeight;
  const scale = 1.5;
  const transform = d3.zoomIdentity
    .translate(width / 2 - d.x * scale, height / 2 - d.y * scale)
    .scale(scale);
  graphSvg.transition().duration(750).call(graphZoom.transform, transform);
}

function buildGraphLegend() {
  const legend = document.getElementById('graph-legend');
  let html = '<div class="legend-section"><div class="legend-title">Nodes</div>';
  TYPE_ORDER.forEach(t => {
    html += '<div class="legend-item"><span class="legend-dot" style="background:' + TYPE_COLORS[t] + '"></span>' + TYPE_LABELS[t] + '</div>';
  });
  html += '</div><div class="legend-section"><div class="legend-title">Edges</div>';

  // Only show edge types present in data
  const edgeTypesPresent = new Set(DATA.edges.map(e => e.type));
  Object.entries(EDGE_COLORS).forEach(([type, color]) => {
    if (edgeTypesPresent.has(type)) {
      html += '<div class="legend-item"><span class="legend-line" style="background:' + color + '"></span>' + (EDGE_LABELS[type] || type) + '</div>';
    }
  });
  html += '</div>';
  legend.innerHTML = html;
  legend.style.display = 'block';
}

// ---------------------------------------------------------------------------
// Layers view
// ---------------------------------------------------------------------------
function buildLayers() {
  const container = document.getElementById('layers-view');
  container.innerHTML = '';

  const width = container.clientWidth;
  const height = container.clientHeight;

  // Filter to items with layer assignments
  const layerItems = DATA.nodes.filter(n =>
    n.meta && n.meta.layer_list && n.meta.layer_list.length > 0 && activeFilters.has(n.type)
  );

  const MARGIN = 20;
  const COL_GAP = 8;
  const COL_WIDTH = (width - 2 * MARGIN - 5 * COL_GAP) / 6;
  const ITEM_H = 28;
  const ITEM_PAD = 4;
  const HEADER_H = 50;

  const svg = d3.select(container).append('svg')
    .attr('width', width)
    .attr('height', height);

  const g = svg.append('g');

  // Zoom
  const lZoom = d3.zoom().scaleExtent([0.2, 3]).on('zoom', e => g.attr('transform', e.transform));
  svg.call(lZoom);
  layersSvg = svg;
  layersZoom = lZoom;

  // Column headers and separators
  LAYER_NAMES.forEach((name, i) => {
    const cx = MARGIN + i * (COL_WIDTH + COL_GAP) + COL_WIDTH / 2;
    // Wrap long names
    const words = name.split(' ');
    if (words.length <= 2) {
      g.append('text')
        .attr('x', cx).attr('y', 20)
        .attr('text-anchor', 'middle')
        .attr('class', 'layers-col-header')
        .text(name);
    } else {
      const mid = Math.ceil(words.length / 2);
      g.append('text')
        .attr('x', cx).attr('y', 16)
        .attr('text-anchor', 'middle')
        .attr('class', 'layers-col-header')
        .text(words.slice(0, mid).join(' '));
      g.append('text')
        .attr('x', cx).attr('y', 28)
        .attr('text-anchor', 'middle')
        .attr('class', 'layers-col-header')
        .text(words.slice(mid).join(' '));
    }

    // Column background
    g.append('rect')
      .attr('x', MARGIN + i * (COL_WIDTH + COL_GAP))
      .attr('y', HEADER_H)
      .attr('width', COL_WIDTH)
      .attr('height', Math.max(height, layerItems.length * (ITEM_H + ITEM_PAD) + HEADER_H + 100))
      .attr('fill', i % 2 === 0 ? 'rgba(255,255,255,0.01)' : 'transparent')
      .attr('rx', 4);
  });

  // Assign items to primary column
  const columns = Array.from({length: 6}, () => []);
  layerItems.forEach(item => {
    const primaryLayer = item.meta.layer_list[0];
    const colIdx = LAYER_NAMES.indexOf(primaryLayer);
    if (colIdx >= 0) columns[colIdx].push(item);
  });

  // Sort within columns by type then title
  const typeRank = { pattern: 0, principle: 1, instrument: 2, evidence: 3, analysis: 4 };
  columns.forEach(col => {
    col.sort((a, b) => (typeRank[a.type] || 9) - (typeRank[b.type] || 9) || a.title.localeCompare(b.title));
  });

  // Position items
  const itemPositions = {};
  const connectionGroup = g.append('g');

  columns.forEach((col, colIdx) => {
    let y = HEADER_H + 10;
    col.forEach(item => {
      const layers = item.meta.layer_list;
      const colIndices = layers.map(l => LAYER_NAMES.indexOf(l)).filter(i => i >= 0);
      const minCol = Math.min(...colIndices);
      const maxCol = Math.max(...colIndices);

      let itemX, itemW;
      if (minCol === maxCol) {
        itemX = MARGIN + colIdx * (COL_WIDTH + COL_GAP) + 3;
        itemW = COL_WIDTH - 6;
      } else {
        itemX = MARGIN + minCol * (COL_WIDTH + COL_GAP) + 3;
        itemW = (maxCol - minCol + 1) * (COL_WIDTH + COL_GAP) - COL_GAP - 6;
      }

      itemPositions[item.id] = {
        x: itemX + itemW / 2,
        y: y + ITEM_H / 2,
      };

      const group = g.append('g')
        .attr('class', 'layers-item')
        .datum(item)
        .style('cursor', 'pointer');

      group.append('rect')
        .attr('x', itemX)
        .attr('y', y)
        .attr('width', itemW)
        .attr('height', ITEM_H)
        .attr('rx', 4)
        .attr('fill', TYPE_COLORS[item.type] + '18')
        .attr('stroke', TYPE_COLORS[item.type] + '50')
        .attr('stroke-width', 1);

      const maxChars = Math.floor(itemW / 6.5);
      const label = item.title.length > maxChars ? item.title.substring(0, maxChars - 1) + '\u2026' : item.title;
      group.append('text')
        .attr('x', itemX + 8)
        .attr('y', y + ITEM_H / 2 + 3.5)
        .attr('fill', TYPE_COLORS[item.type])
        .text(label);

      group.on('click', (event, d) => selectNode(d.id, { forceDetail: true }));

      y += ITEM_H + ITEM_PAD;
    });
  });

  // Draw connections
  const layerItemIds = new Set(layerItems.map(n => n.id));
  const layerEdges = DATA.edges.filter(e =>
    layerItemIds.has(e.source) && layerItemIds.has(e.target) &&
    itemPositions[e.source] && itemPositions[e.target]
  );

  layerEdges.forEach(e => {
    const src = itemPositions[e.source];
    const tgt = itemPositions[e.target];
    const dx = tgt.x - src.x;
    const dy = tgt.y - src.y;
    connectionGroup.append('path')
      .attr('d', 'M' + src.x + ',' + src.y +
        ' C' + (src.x + dx * 0.4) + ',' + src.y +
        ' ' + (tgt.x - dx * 0.4) + ',' + tgt.y +
        ' ' + tgt.x + ',' + tgt.y)
      .attr('fill', 'none')
      .attr('stroke', EDGE_COLORS[e.type] || '#30363d')
      .attr('stroke-width', 1)
      .attr('stroke-opacity', 0.15)
      .datum(e);
  });

  // Hover highlighting
  g.selectAll('.layers-item')
    .on('mouseover', (event, d) => {
      const id = d.id;
      const connectedIds = new Set([id]);
      DATA.edges.forEach(e => {
        if (e.source === id) connectedIds.add(e.target);
        if (e.target === id) connectedIds.add(e.source);
      });

      g.selectAll('.layers-item').each(function(itemD) {
        d3.select(this).attr('opacity', connectedIds.has(itemD.id) ? 1 : 0.15);
      });
      connectionGroup.selectAll('path').each(function(edgeD) {
        const isConn = edgeD.source === id || edgeD.target === id;
        d3.select(this).attr('stroke-opacity', isConn ? 0.7 : 0.03);
      });
    })
    .on('mouseout', () => {
      g.selectAll('.layers-item').attr('opacity', 1);
      connectionGroup.selectAll('path').attr('stroke-opacity', 0.15);
    });
}

// ---------------------------------------------------------------------------
// Matrix view (Corroboration Matrix)
// ---------------------------------------------------------------------------
function buildMatrix() {
  const container = document.getElementById('matrix-view');

  // Rows = patterns, sorted by corroboration then source count
  const patterns = DATA.nodes.filter(n => n.type === 'pattern');

  // Columns = source works (principles + analyses)
  const sources = DATA.nodes.filter(n => n.type === 'principle' || n.type === 'analysis');

  // Build mapping: which sources corroborate which patterns
  // Use all relevant edge types
  const matrix = {}; // pattern_id -> Set of source_ids
  DATA.edges.forEach(e => {
    if (e.type === 'observed_in') {
      // observed_in goes pattern -> source
      if (!matrix[e.source]) matrix[e.source] = new Set();
      matrix[e.source].add(e.target);
    }
    if (e.type === 'key_pattern') {
      // key_pattern goes source -> pattern
      if (!matrix[e.target]) matrix[e.target] = new Set();
      matrix[e.target].add(e.source);
    }
    if (e.type === 'matches') {
      // matches goes analysis -> pattern
      if (!matrix[e.target]) matrix[e.target] = new Set();
      matrix[e.target].add(e.source);
    }
    if (e.type === 'evidence_for') {
      // evidence_for goes evidence -> pattern (skip, not a source work)
    }
  });

  // Filter sources to only those that appear in at least one pattern
  const activeSources = sources.filter(s => {
    for (const pid in matrix) {
      if (matrix[pid] && matrix[pid].has(s.id)) return true;
    }
    return false;
  });

  // Sort patterns: ESTABLISHED first, then SUPPORTED, then PRELIMINARY, then by source count
  const corrRank = { ESTABLISHED: 0, SUPPORTED: 1, PRELIMINARY: 2 };
  patterns.sort((a, b) => {
    const ca = (a.meta.corroboration || '').split(' ')[0];
    const cb = (b.meta.corroboration || '').split(' ')[0];
    const ra = corrRank[ca] !== undefined ? corrRank[ca] : 3;
    const rb = corrRank[cb] !== undefined ? corrRank[cb] : 3;
    if (ra !== rb) return ra - rb;
    const countA = matrix[a.id] ? matrix[a.id].size : 0;
    const countB = matrix[b.id] ? matrix[b.id].size : 0;
    return countB - countA;
  });

  // Sort sources by number of patterns they contribute to (descending)
  activeSources.sort((a, b) => {
    let countA = 0, countB = 0;
    for (const pid in matrix) {
      if (matrix[pid].has(a.id)) countA++;
      if (matrix[pid].has(b.id)) countB++;
    }
    return countB - countA;
  });

  // Build HTML table
  let html = '<div class="matrix-container"><table class="matrix-table">';

  // Header row
  html += '<thead><tr><th class="matrix-corner"></th>';
  activeSources.forEach(s => {
    const title = getDisplayTitle(s);
    html += '<th><div class="matrix-col-header" data-id="' + s.id + '" title="' + escapeHtml(title) + '">' + escapeHtml(title) + '</div></th>';
  });
  html += '<th class="matrix-corner" style="border-left:1px solid var(--border)">#</th>';
  html += '</tr></thead>';

  // Body rows
  html += '<tbody>';
  patterns.forEach(p => {
    const corr = (p.meta.corroboration || '').split(' ')[0];
    const pSources = matrix[p.id] || new Set();
    const count = pSources.size;

    html += '<tr class="matrix-row" data-id="' + p.id + '">';
    html += '<td class="matrix-row-header" data-id="' + p.id + '" title="' + escapeHtml(p.title) + '">' +
      escapeHtml(p.title) +
      '<span class="matrix-corr matrix-corr-' + corr + '">' + corr + '</span>' +
    '</td>';

    activeSources.forEach(s => {
      const has = pSources.has(s.id);
      const color = has ? (TYPE_COLORS[s.type] || '#3fb950') : 'transparent';
      html += '<td class="matrix-cell' + (has ? ' filled' : '') + '">' +
        (has ? '<span class="matrix-dot" style="background:' + color + '"></span>' : '') +
      '</td>';
    });

    html += '<td class="matrix-count">' + count + '</td>';
    html += '</tr>';
  });
  html += '</tbody></table></div>';

  container.innerHTML = html;

  // Click handlers
  container.querySelectorAll('.matrix-row-header').forEach(el => {
    el.addEventListener('click', () => {
      const id = el.dataset.id;
      if (id && nodeMap[id]) selectNode(id, { forceDetail: true });
    });
  });
  container.querySelectorAll('.matrix-col-header').forEach(el => {
    el.addEventListener('click', () => {
      const id = el.dataset.id;
      if (id && nodeMap[id]) selectNode(id, { forceDetail: true });
    });
  });

  // Row hover: highlight the row
  container.querySelectorAll('.matrix-row').forEach(row => {
    row.addEventListener('mouseover', () => {
      container.querySelectorAll('.matrix-row').forEach(r => {
        r.classList.toggle('dimmed', r !== row);
      });
      row.classList.add('highlight');
    });
    row.addEventListener('mouseout', () => {
      container.querySelectorAll('.matrix-row').forEach(r => {
        r.classList.remove('dimmed');
        r.classList.remove('highlight');
      });
    });
  });
}

// ---------------------------------------------------------------------------
// Navigation
// ---------------------------------------------------------------------------
function selectNode(nodeId, options) {
  options = options || {};
  selectedNode = nodeMap[nodeId] || null;
  buildSidebar();
  if (!selectedNode) return;

  if (currentView === 'graph' && !options.forceDetail) {
    focusGraphNode(nodeId);
    document.getElementById('main-title').textContent = getDisplayTitle(selectedNode);
    return;
  }

  if (currentView !== 'detail') switchView('detail');
  showDetail(nodeId);
}

function switchView(view) {
  currentView = view;
  document.querySelectorAll('.view-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.view === view);
  });
  document.getElementById('dashboard-view').style.display = view === 'dashboard' ? 'block' : 'none';
  document.getElementById('detail-view').style.display = view === 'detail' ? 'block' : 'none';
  document.getElementById('graph-view').style.display = view === 'graph' ? 'block' : 'none';
  document.getElementById('layers-view').style.display = view === 'layers' ? 'block' : 'none';
  document.getElementById('matrix-view').style.display = view === 'matrix' ? 'block' : 'none';

  // Hide graph legend when not in graph view
  const legend = document.getElementById('graph-legend');
  if (legend) legend.style.display = view === 'graph' ? 'block' : 'none';

  if (view === 'graph') setTimeout(() => buildGraph(), 50);
  if (view === 'layers') setTimeout(() => buildLayers(), 50);
  if (view === 'matrix') setTimeout(() => buildMatrix(), 50);

  // If switching to detail with a selected node, show it
  if (view === 'detail' && selectedNode) showDetail(selectedNode.id);
}

// ---------------------------------------------------------------------------
// Utils
// ---------------------------------------------------------------------------
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ---------------------------------------------------------------------------
// Event listeners
// ---------------------------------------------------------------------------
const searchInput = document.getElementById('search');
const searchClear = document.getElementById('search-clear');

function updateSearchClear() {
  searchClear.style.display = searchInput.value ? 'block' : 'none';
}

searchInput.addEventListener('input', (e) => {
  searchQuery = e.target.value;
  updateSearchClear();
  buildSidebar();
});

searchClear.addEventListener('click', () => {
  searchInput.value = '';
  searchQuery = '';
  updateSearchClear();
  searchInput.focus();
  buildSidebar();
});

document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    btn.classList.toggle('active');
    const type = btn.dataset.type;
    if (activeFilters.has(type)) activeFilters.delete(type);
    else activeFilters.add(type);
    buildSidebar();
    if (currentView === 'graph') buildGraph();
    if (currentView === 'layers') buildLayers();
  });
});

document.querySelectorAll('.view-btn').forEach(btn => {
  btn.addEventListener('click', () => switchView(btn.dataset.view));
});

// Reset buttons
document.getElementById('graph-reset').addEventListener('click', () => {
  if (graphSvg && graphZoom) {
    graphSvg.transition().duration(500).call(graphZoom.transform, d3.zoomIdentity);
    if (graphNodeSel && graphLinkSel) clearHighlight(graphNodeSel, graphLinkSel);
  }
});
document.getElementById('layers-reset').addEventListener('click', () => {
  if (layersSvg && layersZoom) {
    layersSvg.transition().duration(500).call(layersZoom.transform, d3.zoomIdentity);
  }
});

// Sidebar resize
(function() {
  const sidebar = document.getElementById('sidebar');
  const handle = document.getElementById('sidebar-resize');
  let startX, startWidth;

  handle.addEventListener('mousedown', (e) => {
    e.preventDefault();
    startX = e.clientX;
    startWidth = sidebar.offsetWidth;
    handle.classList.add('dragging');
    document.addEventListener('mousemove', onDrag);
    document.addEventListener('mouseup', stopDrag);
  });

  function onDrag(e) {
    const w = Math.max(200, Math.min(600, startWidth + e.clientX - startX));
    sidebar.style.width = w + 'px';
    sidebar.style.minWidth = w + 'px';
  }

  function stopDrag() {
    handle.classList.remove('dragging');
    document.removeEventListener('mousemove', onDrag);
    document.removeEventListener('mouseup', stopDrag);
  }
})();

// Keyboard shortcuts and navigation
document.addEventListener('keydown', (e) => {
  if (e.key === '/' && document.activeElement !== searchInput) {
    e.preventDefault();
    searchInput.focus();
  }
  if (e.key === 'Escape') {
    searchInput.blur();
    searchInput.value = '';
    searchQuery = '';
    updateSearchClear();
    buildSidebar();
    if (currentView === 'graph' && graphNodeSel && graphLinkSel) {
      clearHighlight(graphNodeSel, graphLinkSel);
    }
  }

  // Arrow key navigation in sidebar
  if ((e.key === 'ArrowDown' || e.key === 'ArrowUp' || e.key === 'Enter') && document.activeElement !== searchInput) {
    const items = Array.from(document.querySelectorAll('.sidebar-item'));
    if (items.length === 0) return;

    if (e.key === 'Enter') {
      const active = document.querySelector('.sidebar-item.active');
      if (active && active.dataset.nodeId) {
        selectNode(active.dataset.nodeId, { forceDetail: true });
      }
      return;
    }

    e.preventDefault();
    const currentIdx = items.findIndex(el => el.classList.contains('active'));
    let nextIdx;
    if (e.key === 'ArrowDown') {
      nextIdx = currentIdx < 0 ? 0 : Math.min(currentIdx + 1, items.length - 1);
    } else {
      nextIdx = currentIdx < 0 ? 0 : Math.max(currentIdx - 1, 0);
    }

    const nodeId = items[nextIdx].dataset.nodeId;
    if (nodeId) {
      selectedNode = nodeMap[nodeId] || null;
      items.forEach(el => el.classList.remove('active'));
      items[nextIdx].classList.add('active');
      items[nextIdx].scrollIntoView({ block: 'nearest' });
      document.getElementById('main-title').textContent = getDisplayTitle(selectedNode);
    }
  }
});

// Init
buildSidebar();
buildDashboard();
</script>
</body>
</html>"""


def main():
    data = build()
    data_json = json.dumps(data, ensure_ascii=False)

    # Write data as external JS file
    OUT_DATA.write_text(f"const DATA = {data_json};\n", encoding="utf-8")
    print(f"\nWrote {OUT_DATA} ({OUT_DATA.stat().st_size / 1024:.0f} KB)")

    # Write HTML (no embedded data)
    OUT.write_text(HTML_TEMPLATE, encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
