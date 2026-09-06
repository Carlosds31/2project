# Bolt's Journal - Critical Learnings

## 2025-05-10 - DOM Tree Optimization for Static Menu
**Learning:** Wrapping individual list items in separate `<ul>` elements inflates DOM depth and node count unnecessarily, leading to higher memory consumption and layout calculation overhead during rendering.
**Action:** Group list items (`<li>`) within a single semantic `<ul>` per section to streamline the DOM tree and reduce rendering workload.
