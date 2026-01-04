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
  [Spec] (https://spec.commonmark.org/0.31.2/#atx-headings)

- [ ] Setext headings (not used in current content)
  [Spec] (https://spec.commonmark.org/0.31.2/#setext-headings)

### Paragraphs & Text
- [x] Paragraphs  
  [Spec] (https://spec.commonmark.org/0.31.2/#paragraphs)

- [x] Emphasis (italic)  
  [Spec] (https://spec.commonmark.org/0.31.2/#emphasis-and-strong-emphasis)

- [x] Strong emphasis (bold)  
  [Spec] (https://spec.commonmark.org/0.31.2/#emphasis-and-strong-emphasis)

### Block Elements
- [x] Blockquotes  
  [Spec] (https://spec.commonmark.org/0.31.2/#block-quotes)

- [x] Horizontal rules (thematic breaks)  
  [Spec] (https://spec.commonmark.org/0.31.2/#thematic-breaks)

### Code
- [x] Inline code  
  [Spec] (https://spec.commonmark.org/0.31.2/#code-spans)

- [x] Fenced code blocks  
  [Spec] (https://spec.commonmark.org/0.31.2/#fenced-code-blocks)

### Lists
- [x] Bullet lists  
  [Spec] (https://spec.commonmark.org/0.31.2/#bullet-lists)

- [x] Ordered lists  
  [Spec] (https://spec.commonmark.org/0.31.2/#ordered-lists)

### Links & Media
- [x] Inline links  
  [Spec] (https://spec.commonmark.org/0.31.2/#links)

- [x] Images  
  [Spec] (https://spec.commonmark.org/0.31.2/#images)

### HTML & Escaping
- [ ] Inline HTML  
  [Spec] (https://spec.commonmark.org/0.31.2/#raw-html)

- [ ] HTML blocks  
  [Spec] (https://spec.commonmark.org/0.31.2/#html-blocks)

- [ ] Backslash escapes  
  [Spec] (https://spec.commonmark.org/0.31.2/#backslash-escapes)

---

## GitHub Flavored Markdown (GFM)

- [x] Tables  
  [Spec] (https://github.github.com/gfm/#tables-extension)

- [x] Strikethrough  
  [Spec] (https://github.github.com/gfm/#strikethrough-extension)

- [x] Task list items  
  [Spec] (https://github.github.com/gfm/#task-list-items-extension)

- [ ] Autolinks  
  [Spec] (https://github.github.com/gfm/#autolinks-extension)

---

## Notes

- This checklist reflects the current behavior of the renderer.
- Unsupported features may be added incrementally in future releases.
- Contributors should only mark features as supported once fully implemented
  and tested.
