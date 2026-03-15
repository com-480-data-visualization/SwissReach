---
layout: home

hero:
  name: "SwissReach Docs"
  text: "Swiss Rail Accessibility for EPFL COM-480"
  tagline: "Milestone 1 documentation for a nationwide Swiss rail accessibility analysis."
  actions:
    - theme: brand
      text: Milestone 1
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

SwissReach focuses on **Swiss rail accessibility** rather than full multimodal journey planning. This scope matches the current implementation and the Milestone 1 requirement to demonstrate **feasibility, data understanding, and a clear visualization question**.

Key numbers from the current exported analysis:

- `95,415` raw GTFS stops
- `75,775` stops inside Switzerland
- `3,628` rail stop entries
- `1,663` logical rail stations after deduplication
- `1,500 / 1,663` stations reachable from Lausanne within 6 hours at `08:00`

## Figure Preview

![Swiss rail reachability from Lausanne](/figures/lausanne_reachability_0800_6h.png)

## Documentation Structure

- [Milestone 1](/milestone1): dataset choice, project framing, exploratory findings, and scope decisions
- [Methodology](/methodology): preprocessing pipeline, reachability model, and current limitations
- [Related Work](/related-work): references, inspirations, and originality of the current approach
