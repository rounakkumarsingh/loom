# Loom Architecture

This document explains how Loom transforms Markdown into HTML.
It is intended for new contributors who want to understand the codebase before making changes.

---

## Overview

Loom follows a linear parsing pipeline that converts Markdown files
into static HTML pages without external dependencies.

---

## Parsing Pipeline

1. Markdown files are read from `content/`
2. Content is split into block-level elements
3. Inline formatting is parsed inside blocks
4. Parsed content is converted into a tree structure
5. The tree is rendered into HTML files in `docs/`

---

## Pipeline Diagram (ASCII)

Markdown (.md)
     |
     v
[ Block Parser ]
     |
     v
[ Inline Parser ]
     |
     v
[ TextNode Tree ]
     |
     v
[ HTMLNode Tree ]
     |
     v
HTML (.html)


---

## Module Responsibilities

| File | Responsibility |
|-----|----------------|
| main.py | Orchestrates parsing and rendering |
| block.py | Parses block-level Markdown |
| inline.py | Parses inline formatting |
| textnode.py | Intermediate text representation |
| htmlnode.py | Base HTML node |
| leafnode.py | HTML nodes without children |
| parentnode.py | HTML nodes with children |

---

## How to Add a New Block Type

1. Add block detection logic in `block.py`
2. Convert detected content into `TextNode` objects
3. Ensure the block maps correctly to an HTML node
4. Add tests to verify behavior

Use existing block implementations as references.

---

## Known Limitations

- Inline parser does not fully support nested formatting
- Regex-based parsing may fail on complex Markdown edge cases
- Not all CommonMark features are supported

---

## Where to Look When Debugging

- Block issues → `block.py`
- Inline formatting issues → `inline.py`
- Tree or structure issues → `textnode.py`
- HTML output issues → `htmlnode.py`, `leafnode.py`, `parentnode.py`
- Missing files or pages → `main.py`

---

## Design Philosophy

Loom prioritizes clarity and learning over completeness.
The codebase is intentionally simple to expose parsing fundamentals.
