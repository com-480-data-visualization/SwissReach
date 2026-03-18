---
layout: home

hero:
  name: "SwissReach"
  text: "Swiss public transport accessibility and everyday infrastructure insights."
  actions:
    - theme: brand
      text: Insights
      link: /insights
    - theme: alt
      text: Methodology
      link: /methodology

features:
  - title: Nationwide rail backbone
    details: Swiss GTFS is filtered to Swiss rail services and collapsed from raw stops into 1,938 logical rail stations.
  - title: Accessibility plus amenities
    details: The project now connects timetable reachability with supermarkets, schools, hospitals, and IKEA access.
  - title: Retail competition stories
    details: A dedicated supermarket dataset supports Migros vs Coop density analysis and broader food-retail mapping.
---

## Project Snapshot

SwissReach started as a **Swiss rail accessibility** project and has evolved into a broader analysis of what that accessibility means in practice. The current documentation combines timetable-based reachability, infrastructure-count analysis, and retail density views.

Current story layers:

- nationwide rail graph derived from the Swiss GTFS feed
- `1,938` logical rail stations after deduplication
- `30`-minute access counts for supermarkets, schools, and hospitals
- `60`-minute IKEA access coverage
- Migros vs Coop density comparisons based on the exported supermarket dataset

## Figure Preview

![30-minute amenity accessibility in Switzerland](/figures/amenity_access_30min.png)

## Documentation Structure

- [Insights](/insights): the three main analytical views, exported figures, and project framing note
- [Milestone 1 Report](/milestone1): dataset choice, project framing, exploratory findings, and scope decisions
- [Methodology](/methodology): preprocessing pipeline, reachability model, POI integration, and current limitations
- [Related Work](/related-work): references, inspirations, and originality of the current approach
