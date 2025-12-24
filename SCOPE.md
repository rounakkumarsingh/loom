# CommonMark Compliance

This document describes which CommonMark and GitHub Flavored Markdown (GFM)
features are currently supported by **loom**.

Reference specification:
- CommonMark v0.31.2 — https://spec.commonmark.org/0.31.2/
- GitHub Flavored Markdown — https://github.github.com/gfm/

Only features that are fully working and verified via rendered output are marked as supported.

---

## CommonMark Core

### Headings
- [x] ATX headings  
  https://spec.commonmark.org/0.31.2/#atx-headings

- [ ] Setext headings (not used in current content)
  https://spec.commonmark.org/0.31.2/#setext-headings

### Paragraphs & Text
- [x] Paragraphs  
  https://spec.commonmark.org/0.31.2/#paragraphs

- [x] Emphasis (italic)  
  https://spec.commonmark.org/0.31.2/#emphasis-and-strong-emphasis

- [x] Strong emphasis (bold)  
  https://spec.commonmark.org/0.31.2/#emphasis-and-strong-emphasis

### Block Elements
- [x] Blockquotes  
  https://spec.commonmark.org/0.31.2/#block-quotes

- [x] Horizontal rules (thematic breaks)  
  https://spec.commonmark.org/0.31.2/#thematic-breaks

### Code
- [x] Inline code  
  https://spec.commonmark.org/0.31.2/#code-spans

- [x] Fenced code blocks  
  https://spec.commonmark.org/0.31.2/#fenced-code-blocks

### Lists
- [x] Bullet lists  
  https://spec.commonmark.org/0.31.2/#bullet-lists

- [x] Ordered lists  
  https://spec.commonmark.org/0.31.2/#ordered-lists

### Links & Media
- [x] Inline links  
  https://spec.commonmark.org/0.31.2/#links

- [x] Images  
  https://spec.commonmark.org/0.31.2/#images

### HTML & Escaping
- [ ] Inline HTML  
  https://spec.commonmark.org/0.31.2/#raw-html

- [ ] HTML blocks  
  https://spec.commonmark.org/0.31.2/#html-blocks

- [ ] Backslash escapes  
  https://spec.commonmark.org/0.31.2/#backslash-escapes

---

## GitHub Flavored Markdown (GFM)

- [x] Tables  
  https://github.github.com/gfm/#tables-extension

- [x] Strikethrough  
  https://github.github.com/gfm/#strikethrough-extension

- [x] Task list items  
  https://github.github.com/gfm/#task-list-items-extension

- [ ] Autolinks  
  https://github.github.com/gfm/#autolinks-extension

---

## Notes

- This checklist reflects the current behavior of the renderer.
- Unsupported features may be added incrementally in future releases.
- Contributors should only mark features as supported once fully implemented
  and tested.
