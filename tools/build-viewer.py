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
# Pattern name normalization
# ---------------------------------------------------------------------------

def pattern_id(name: str) -> str:
    return "pattern:" + name.strip()


def normalize_pattern_ref(ref: str) -> str:
    """Normalize loose pattern references to canonical names.

    Handles abbreviations seen in the corpus, e.g.
    'Peacetime Ratchet' -> 'The Peacetime Ratchet'.
    """
    ref = ref.strip()
    # Strip leading article for matching
    canon = ref
    return canon


# ---------------------------------------------------------------------------
# Parse each file type
# ---------------------------------------------------------------------------

def parse_patterns(path: Path):
    """Parse patterns.md into a list of pattern nodes."""
    content = read_file(path)
    nodes = []
    # Split on ### headings
    parts = re.split(r"^### ", content, flags=re.MULTILINE)
    for part in parts[1:]:  # skip preamble
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

        # Extract OBSERVED IN block (may span many lines)
        observed = extract_field_multiline(part, "OBSERVED IN")
        if observed:
            for fref in extract_file_refs(observed):
                edges.append({
                    "source": pid,
                    "target": fref,
                    "type": "observed_in",
                })

        # Extract EVIDENCE refs
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
    source_type = extract_field(content, "SOURCE TYPE")
    mode = extract_field(content, "MODE")

    node = {
        "id": rel,
        "type": "analysis",
        "title": title,
        "content": content,
        "meta": {
            "date": date,
            "source_type": source_type,
            "mode": mode,
        },
    }

    edges = []

    # Extract pattern matches from the analysis body
    # Look for "### Pattern matches" section or PATTERNS MATCHED field
    # Also search for pattern names referenced in the body
    pattern_section = re.search(
        r"(?:###\s*Pattern matches|PATTERNS MATCHED:)(.*?)(?=\n###|\n---|\Z)",
        content, re.DOTALL | re.IGNORECASE,
    )
    if pattern_section:
        text = pattern_section.group(1)
        # Find pattern names: lines starting with "- " that reference known patterns
        for line in text.split("\n"):
            line = line.strip().lstrip("- ")
            if line and not line.startswith("#"):
                # Take the part before any parenthetical
                name = re.split(r"\s*\(", line)[0].strip()
                if name and len(name) > 3:
                    edges.append({
                        "source": rel,
                        "target": pattern_id(name),
                        "type": "matches",
                    })

    # Extract framework cross-reference section for pattern refs
    cross_ref = re.search(
        r"###\s*Framework cross-reference(.*?)(?=\n---|\n##[^#]|\Z)",
        content, re.DOTALL,
    )
    if cross_ref:
        text = cross_ref.group(1)
        # Extract all file refs
        for fref in extract_file_refs(text):
            edges.append({
                "source": rel,
                "target": fref,
                "type": "references",
            })

    # Extract file refs from Sources section
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

    # Extract instrument references
    for fref in re.findall(r"instruments/[\w\-]+\.md", content):
        edges.append({
            "source": rel,
            "target": fref,
            "type": "applies_instrument",
        })

    return node, edges


def parse_principle_index(path: Path):
    """Parse principles/INDEX.md for KEY PATTERNS and INSTRUMENT refs."""
    content = read_file(path)
    edges = []

    # Split by ## headings (each is a principle file)
    parts = re.split(r"^## ", content, flags=re.MULTILINE)
    for part in parts[1:]:
        lines = part.strip()
        filename = lines.split("\n")[0].strip()
        if not filename.endswith(".md"):
            continue
        fref = "principles/" + filename

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

    return edges


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
        # Try to extract from a table or from the text
        layer_text = layers_section.group(1)
        layer_names = re.findall(
            r"\|\s*(Thought & Narrative|Economic|Legal & Regulatory|Institutional|Surveillance & Information|Physical & Coercive)",
            layer_text,
        )
        if layer_names:
            layers = ", ".join(layer_names)

    # Count principles (### P\d+ headings)
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

    # Extract item names (### headings under categories)
    items = re.findall(r"^### (.+)$", content, re.MULTILINE)

    node = {
        "id": rel,
        "type": "instrument",
        "title": title,
        "content": content,
        "meta": {
            "source": source,
            "layers": layers,
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
    if principles_dir.exists():
        # Parse INDEX.md for edges
        index_path = principles_dir / "INDEX.md"
        if index_path.exists():
            edges.extend(parse_principle_index(index_path))

        for f in sorted(principles_dir.glob("*.md")):
            if f.name == "INDEX.md":
                continue
            n = parse_principle(f)
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
}
#graph-view svg { width: 100%; height: 100%; }
.graph-node { cursor: pointer; }
.graph-node circle { stroke-width: 2px; transition: r 0.15s; }
.graph-node:hover circle { r: 10; }
.graph-node text {
  font-size: 10px;
  fill: var(--text-muted);
  pointer-events: none;
}
.graph-link { stroke-opacity: 0.3; }
.graph-link.highlight { stroke-opacity: 0.8; stroke-width: 2px; }
.graph-node.highlight circle { r: 10; stroke-width: 3px; }
.graph-node.dimmed { opacity: 0.15; }
.graph-link.dimmed { stroke-opacity: 0.05; }

/* Welcome */
#welcome {
  padding: 48px;
  color: var(--text-muted);
  max-width: 600px;
}
#welcome h2 { color: var(--text); margin-bottom: 16px; font-size: 20px; }
#welcome p { margin-bottom: 12px; line-height: 1.6; }
#welcome kbd {
  background: var(--bg-card);
  border: 1px solid var(--border);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

/* Scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

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
</style>
</head>
<body>
<div id="app">
  <div id="sidebar">
    <div id="sidebar-header">
      <h1>Lens of Power</h1>
      <input type="text" id="search" placeholder="Search items...">
      <div id="filters">
        <button class="filter-btn active" data-type="analysis">Analyses</button>
        <button class="filter-btn active" data-type="principle">Principles</button>
        <button class="filter-btn active" data-type="instrument">Instruments</button>
        <button class="filter-btn active" data-type="pattern">Patterns</button>
        <button class="filter-btn active" data-type="evidence">Evidence</button>
      </div>
    </div>
    <div id="sidebar-list"></div>
  </div>
  <div id="main">
    <div id="main-header">
      <div id="view-toggle">
        <button class="view-btn active" data-view="detail">Content</button>
        <button class="view-btn" data-view="graph">Graph</button>
      </div>
      <div id="main-title"></div>
    </div>
    <div id="content-area">
      <div id="detail-view">
        <div id="welcome">
          <h2>Framework Viewer</h2>
          <p>Select an item from the sidebar to view its content and cross-references.</p>
          <p>Switch to <kbd>Graph</kbd> view to see the interconnection structure.</p>
          <p>Use the filter buttons to show/hide item types. Type in the search box to filter by title or content.</p>
        </div>
      </div>
      <div id="graph-view"></div>
      <div id="graph-tooltip">
        <div class="tt-title"></div>
        <div class="tt-type"></div>
      </div>
    </div>
  </div>
</div>

<script>
// Embedded data
const DATA = __DATA_PLACEHOLDER__;

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

// State
let activeFilters = new Set(TYPE_ORDER);
let currentView = 'detail';
let selectedNode = null;
let searchQuery = '';

// Index
const nodeMap = {};
DATA.nodes.forEach(n => { nodeMap[n.id] = n; });

// Build adjacency
const adjacency = {};
DATA.nodes.forEach(n => { adjacency[n.id] = { incoming: [], outgoing: [] }; });
DATA.edges.forEach(e => {
  if (adjacency[e.source]) adjacency[e.source].outgoing.push(e);
  if (adjacency[e.target]) adjacency[e.target].incoming.push(e);
});

// --- Sidebar ---
function buildSidebar() {
  const list = document.getElementById('sidebar-list');
  list.innerHTML = '';
  const q = searchQuery.toLowerCase();

  TYPE_ORDER.forEach(type => {
    if (!activeFilters.has(type)) return;
    const items = DATA.nodes
      .filter(n => n.type === type)
      .filter(n => !q || n.title.toLowerCase().includes(q) || n.content.toLowerCase().includes(q))
      .sort((a, b) => a.title.localeCompare(b.title));

    if (items.length === 0) return;

    const group = document.createElement('div');
    group.className = 'sidebar-group';
    group.innerHTML = `
      <div class="sidebar-group-header">
        <span class="chevron">&#9660;</span>
        ${TYPE_LABELS[type]} <span class="count">(${items.length})</span>
      </div>
      <div class="sidebar-group-items"></div>
    `;

    const header = group.querySelector('.sidebar-group-header');
    header.addEventListener('click', () => {
      group.classList.toggle('collapsed');
    });

    const container = group.querySelector('.sidebar-group-items');
    items.forEach(n => {
      const item = document.createElement('div');
      item.className = 'sidebar-item' + (selectedNode && selectedNode.id === n.id ? ' active' : '');
      item.innerHTML = `<span class="type-dot" style="background:${TYPE_COLORS[type]}"></span>${escapeHtml(n.title)}`;
      item.addEventListener('click', () => selectNode(n.id));
      container.appendChild(item);
    });

    list.appendChild(group);
  });
}

// --- Detail view ---
function showDetail(nodeId) {
  const node = nodeMap[nodeId];
  if (!node) return;

  const view = document.getElementById('detail-view');
  const welcome = document.getElementById('welcome');
  if (welcome) welcome.style.display = 'none';

  // Meta bar
  let metaHtml = `<div class="meta-bar"><span class="meta-tag type-${node.type}">${node.type}</span>`;
  if (node.meta) {
    Object.entries(node.meta).forEach(([k, v]) => {
      if (v && typeof v === 'string' && v.length < 100 && k !== 'statement' && k !== 'mechanism') {
        metaHtml += `<span class="meta-tag" style="background:rgba(255,255,255,0.06);color:var(--text-muted)">${k}: ${escapeHtml(v)}</span>`;
      }
    });
  }
  metaHtml += '</div>';

  // Render markdown
  let rendered = marked.parse(node.content);
  // Replace file path references with clickable links
  rendered = rendered.replace(
    /(?:(?:principles|analyses|instruments|evidence)\/[\w\-]+\.md)/g,
    (match) => {
      if (nodeMap[match]) {
        return `<span class="cross-ref" data-target="${match}">${escapeHtml(nodeMap[match].title || match)}</span>`;
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
      connectedHtml += `<span class="connected-item" data-target="${id}" style="border-color:${color}40">
        <span class="type-dot" style="background:${color}"></span>
        ${escapeHtml(info.node.title)}
        <span style="color:var(--text-muted);font-size:11px;margin-left:4px">${info.type}</span>
      </span>`;
    });
    connectedHtml += '</div>';
  }

  view.innerHTML = metaHtml + '<div id="detail-content">' + rendered + '</div>' + connectedHtml;

  // Attach click handlers for cross-refs
  view.querySelectorAll('.cross-ref, .connected-item').forEach(el => {
    el.addEventListener('click', () => {
      const target = el.dataset.target;
      if (target && nodeMap[target]) selectNode(target);
    });
  });

  document.getElementById('main-title').textContent = node.title;
}

// --- Graph view ---
let simulation = null;
let graphSvg = null;

function buildGraph() {
  const container = document.getElementById('graph-view');
  container.innerHTML = '';

  const width = container.clientWidth;
  const height = container.clientHeight;

  const filteredNodes = DATA.nodes.filter(n => activeFilters.has(n.type));
  const filteredIds = new Set(filteredNodes.map(n => n.id));
  const filteredEdges = DATA.edges.filter(e => filteredIds.has(e.source) && filteredIds.has(e.target));

  const svg = d3.select(container).append('svg')
    .attr('width', width)
    .attr('height', height);

  const g = svg.append('g');

  // Zoom
  const zoom = d3.zoom()
    .scaleExtent([0.1, 4])
    .on('zoom', (event) => g.attr('transform', event.transform));
  svg.call(zoom);

  // Simulation
  simulation = d3.forceSimulation(filteredNodes)
    .force('link', d3.forceLink(filteredEdges).id(d => d.id).distance(80))
    .force('charge', d3.forceManyBody().strength(-200))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(20));

  // Links
  const link = g.append('g')
    .selectAll('line')
    .data(filteredEdges)
    .join('line')
    .attr('class', 'graph-link')
    .attr('stroke', '#30363d')
    .attr('stroke-width', 1);

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
    .attr('r', d => d.type === 'pattern' ? 8 : 6)
    .attr('fill', d => TYPE_COLORS[d.type])
    .attr('stroke', d => TYPE_COLORS[d.type]);

  node.append('text')
    .text(d => d.title.length > 25 ? d.title.substring(0, 25) + '...' : d.title)
    .attr('x', 12)
    .attr('y', 4);

  // Tooltip
  const tooltip = document.getElementById('graph-tooltip');

  node.on('mouseover', (event, d) => {
    tooltip.querySelector('.tt-title').textContent = d.title;
    tooltip.querySelector('.tt-type').textContent = d.type;
    tooltip.style.display = 'block';
    tooltip.style.left = (event.pageX + 12) + 'px';
    tooltip.style.top = (event.pageY - 20) + 'px';

    // Highlight connected
    const connIds = new Set([d.id]);
    filteredEdges.forEach(e => {
      const src = typeof e.source === 'object' ? e.source.id : e.source;
      const tgt = typeof e.target === 'object' ? e.target.id : e.target;
      if (src === d.id) connIds.add(tgt);
      if (tgt === d.id) connIds.add(src);
    });

    node.classed('highlight', n => connIds.has(n.id));
    node.classed('dimmed', n => !connIds.has(n.id));
    link.classed('highlight', e => {
      const src = typeof e.source === 'object' ? e.source.id : e.source;
      const tgt = typeof e.target === 'object' ? e.target.id : e.target;
      return src === d.id || tgt === d.id;
    });
    link.classed('dimmed', e => {
      const src = typeof e.source === 'object' ? e.source.id : e.source;
      const tgt = typeof e.target === 'object' ? e.target.id : e.target;
      return src !== d.id && tgt !== d.id;
    });
  });

  node.on('mousemove', (event) => {
    tooltip.style.left = (event.pageX + 12) + 'px';
    tooltip.style.top = (event.pageY - 20) + 'px';
  });

  node.on('mouseout', () => {
    tooltip.style.display = 'none';
    node.classed('highlight', false).classed('dimmed', false);
    link.classed('highlight', false).classed('dimmed', false);
  });

  node.on('click', (event, d) => {
    selectNode(d.id);
    switchView('detail');
  });

  simulation.on('tick', () => {
    link
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y);
    node.attr('transform', d => `translate(${d.x},${d.y})`);
  });

  graphSvg = svg;

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

// --- Navigation ---
function selectNode(nodeId) {
  selectedNode = nodeMap[nodeId] || null;
  buildSidebar();
  if (selectedNode) showDetail(nodeId);
}

function switchView(view) {
  currentView = view;
  document.querySelectorAll('.view-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.view === view);
  });
  document.getElementById('detail-view').style.display = view === 'detail' ? 'block' : 'none';
  document.getElementById('graph-view').style.display = view === 'graph' ? 'block' : 'none';

  if (view === 'graph') {
    // Rebuild graph when switching to it
    setTimeout(() => buildGraph(), 50);
  }
}

// --- Utils ---
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// --- Event listeners ---
document.getElementById('search').addEventListener('input', (e) => {
  searchQuery = e.target.value;
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
  });
});

document.querySelectorAll('.view-btn').forEach(btn => {
  btn.addEventListener('click', () => switchView(btn.dataset.view));
});

// Keyboard shortcut
document.addEventListener('keydown', (e) => {
  if (e.key === '/' && document.activeElement !== document.getElementById('search')) {
    e.preventDefault();
    document.getElementById('search').focus();
  }
  if (e.key === 'Escape') {
    document.getElementById('search').blur();
    document.getElementById('search').value = '';
    searchQuery = '';
    buildSidebar();
  }
});

// Init
buildSidebar();
</script>
</body>
</html>"""


def main():
    data = build()
    data_json = json.dumps(data, ensure_ascii=False)
    html = HTML_TEMPLATE.replace("__DATA_PLACEHOLDER__", data_json)
    OUT.write_text(html, encoding="utf-8")
    print(f"\nWrote {OUT}")
    print(f"Size: {OUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
