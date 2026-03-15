# Milestone 1

This page maps the current project state to the four required sections in `README.md`: `Dataset`, `Problematic`, `Exploratory Data Analysis`, and `Related work`.

## Dataset

SwissReach uses two standard public datasets:

- **Swiss GTFS static timetable** from `opentransportdata.swiss`
- **SwissBoundaries3D** national boundary geometry from `swisstopo`

This is a good Milestone 1 fit because the project relies on established public data rather than scraping. The main preprocessing burden is therefore not data collection, but **scope control**:

- remove cross-border stops from the raw GTFS feed
- isolate rail services from the full public transport network
- collapse platform-level stops into logical stations for visualization

Current size after each filtering step:

| Stage | Count |
| --- | ---: |
| Raw GTFS stops | 95,415 |
| Stops inside Switzerland | 75,775 |
| Rail stop entries | 3,628 |
| Logical rail stations | 1,663 |

## Problematic

The project question is:

**How does rail accessibility vary across Switzerland depending on where and when a trip starts?**

For Milestone 1, we deliberately keep the scope **rail-first** instead of promising full multimodal routing. This choice is intentional:

- it matches the current implementation
- it keeps the data-cleaning burden manageable
- it is already rich enough for a compelling visualization story

Target audience:

- students and commuters comparing rail accessibility
- readers interested in national-scale transport inequality
- course evaluators assessing whether the project idea is feasible and visually meaningful

## Exploratory Data Analysis

### 1. Nationwide filtering

The raw GTFS feed contains many cross-border stops. Filtering them against the Swiss national outline immediately improves spatial validity.

![Swiss public transport stops inside the national boundary](/figures/swiss_public_transport_stops.png)

### 2. Rail extraction and station deduplication

Filtering to rail services reduces the network substantially, and deduplicating platforms into logical stations makes the map much more suitable for front-end rendering.

![Swiss rail stations](/figures/swiss_rail_stations.png)

![Deduplicated Swiss rail stations](/figures/swiss_rail_stations_deduplicated.png)

This is one of the most important Milestone 1 findings: the project becomes much more tractable once it is modeled at the **station** level instead of the raw stop/platform level.

### 3. Station activity

The activity view counts unique active rail trips per logical station in a selected time window.

![Top 10 busiest rail stations in the morning peak](/figures/busiest_rail_stations_morning_peak.png)

This adds a second narrative dimension beyond geography: some stations matter because they are central transfer hubs even if they are not visually dominant on the map.

### 4. Reachability from a single origin

From Lausanne at `08:00`, the current rail-only model reaches `1,500` of the `1,663` logical rail stations within a 6-hour window.

![Lausanne reachability at 08:00 within 6 hours](/figures/lausanne_reachability_0800_6h.png)

### 5. Multi-origin comparison

To move beyond a single-city story, we compare four major origins across four departure times. The best result in the current export is `Zürich HB` at `12:00`, which reaches `1,535` stations (`92.3%` of the rail network) within 6 hours.

The weakest of the sampled cases is `Genève` at `18:00`, with `1,383` reachable stations (`83.2%`).

![Reachability comparison across origins and departure times](/figures/reachability_comparison_heatmap.png)

The exported comparison table is also available as [CSV](/data/reachability_comparison.csv).

## Scope Decision

Milestone 1 should present the project as a **nationwide Swiss rail accessibility visualization**, with multimodal transport as a future extension.

This means the following are **out of scope for now**:

- buses, trams, cable cars, and boats as first-class modes
- explicit walking links between nearby stops
- cross-border continuation outside Swiss territory
- full path reconstruction for itinerary explanations

## Why The Current Analysis Is Enough

The current analysis is strong enough for Milestone 1 because it already demonstrates:

- a credible public dataset choice
- non-trivial but manageable preprocessing
- clear exploratory findings
- a visualization question that can scale into the final project

What still needs care in the final report is not more raw engineering, but sharper communication about **scope, assumptions, limitations, and originality**.
