# Bolt's Journal - Critical Learnings

## 2025-05-18 - Consolidate fragmented list containers
**Learning:** In static HTML documents, wrapping each list item in its own `<ul>` tag needlessly inflates DOM node count and HTML document size. Consolidating list items into a single `<ul>` parent per semantic section reduces DOM nodes and improves document parsing performance.
**Action:** Always group list items in single container elements (`<ul>`/`<ol>`) per section when writing or refactoring static HTML.
