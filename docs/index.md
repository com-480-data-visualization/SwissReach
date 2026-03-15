---
layout: home

hero:
  name: "SwissReach"
  text: "Nationwide rail accessibility in Switzerland."
  actions:
    - theme: brand
      text: Milestone 1 Report
      link: /milestone1
    - theme: alt
      text: Methodology
      link: /methodology

features:
  - title: Nationwide scope
    details: The analysis starts from the full Swiss GTFS feed, filters the network to Swiss territory, and preserves a country-scale perspective.
  - title: Station-level modeling
    details: Platform-level GTFS stops are collapsed into logical rail stations to support readable maps and efficient rendering.
  - title: Reachability storytelling
    details: Station activity, single-origin reachability, and multi-origin comparisons provide the main analytical views.
---

## Project Snapshot

SwissReach focuses on **Swiss rail accessibility** rather than full multimodal journey planning. The current documentation presents the dataset, preprocessing pipeline, and timetable-based reachability analysis behind the project.

Key numbers from the current exported analysis:

- `95,415` raw GTFS stops
- `75,775` stops inside Switzerland
- `3,628` rail stop entries
- `1,663` logical rail stations after deduplication
- `1,500 / 1,663` stations reachable from Lausanne within 6 hours at `08:00`

## Figure Preview

![Swiss rail reachability from Lausanne](/figures/lausanne_reachability_0800_6h.png)
## Documentation Structure

- [Milestone 1 Report](/milestone1): dataset choice, project framing, exploratory findings, and scope decisions
- [Methodology](/methodology): preprocessing pipeline, reachability model, and current limitations
- [Related Work](/related-work): references, inspirations, and originality of the current approach

