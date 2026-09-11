## 2026-09-11 - DOM Tree Node Reduction in Static Markup
**Learning:** Wrapping individual list items (`<li>`) in separate `<ul>` containers increases DOM tree size, memory consumption, and browser reflow/repaint calculations. Consolidating list items into single `<ul>` parents per section significantly simplifies DOM depth and rendering performance.
**Action:** Consolidate redundant element wrappers into parent collection elements whenever applicable.
