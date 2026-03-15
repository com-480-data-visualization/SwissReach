---
layout: home

hero:
  name: "SwissReach Docs"
  text: "Swiss Rail Accessibility for EPFL COM-480"
  tagline: "A rail-first Milestone 1 prototype for nationwide reachability, station activity, and timetable-based storytelling."
  actions:
    - theme: brand
      text: Milestone 1
      link: /milestone1
    - theme: alt
      text: Methodology
      link: /methodology

features:
  - title: Nationwide scope
    details: Start from the full Swiss GTFS feed, filter to Swiss territory, and preserve a country-scale view instead of a single-city case study.
  - title: Station-level modeling
    details: Collapse platform-level GTFS stops into logical rail stations to keep the analysis map readable and front-end friendly.
  - title: Reachability storytelling
    details: Combine station activity, single-origin reachability, and multi-origin comparisons to validate the visualization concept for the final project.
---

## Project Snapshot

SwissReach currently focuses on **Swiss rail accessibility**, not full multimodal journey planning. This keeps Milestone 1 aligned with the existing codebase and with the course requirement to demonstrate **feasibility, data understanding, and a clear visualization question**.

Key numbers from the current exported analysis:

- `95,415` raw GTFS stops
- `75,775` stops inside Switzerland
- `3,628` rail stop entries
- `1,663` logical rail stations after deduplication
- `1,500 / 1,663` stations reachable from Lausanne within 6 hours at `08:00`

## Figure Preview

![Swiss rail reachability from Lausanne](/figures/lausanne_reachability_0800_6h.png)

## What This Documentation Covers

- [Milestone 1](/milestone1): dataset choice, project framing, exploratory findings, and scope decisions
- [Methodology](/methodology): preprocessing pipeline, reachability model, and current limitations
- [Related Work](/related-work): references, inspirations, and why this approach is still distinctive
