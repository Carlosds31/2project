## 2026-09-08 - DOM Node Consolidation for Static HTML Documents
**Learning:** Fragmented list structures using multiple `<ul>` wrappers for single `<li>` elements add unnecessary DOM nodes (increasing memory footprint and DOM tree depth) and cause redundant layout recalculations.
**Action:** When working on HTML list rendering, ensure list items belonging to the same semantic section share a single container list element (`<ul>` or `<ol>`).
