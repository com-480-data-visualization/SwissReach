# Milestone 1 Report

This document presents the current project state according to the four required sections in `README.md`: `Dataset`, `Problematic`, `Exploratory Data Analysis`, and `Related work`.

## Project Note

SwissReach was defined and a substantial share of the exploratory work was completed **before** the EPFL `COM-490` assignment was published. The original intention of the project, a Swiss public-transport accessibility visualization study, unfortunately overlapped almost completely with Assignment 1 of `COM-490 Large-Scale Data Science in the Real World`.

To avoid any suspicion that the two projects were too similar, SwissReach was extended with a more distinctive analytical layer: **infrastructure-count visualization**. The final direction therefore keeps the Swiss rail accessibility backbone, but adds views about supermarkets, schools, hospitals, IKEA access, and retail density.

## Dataset

SwissReach uses three main data families:

- **Swiss GTFS static timetable** from `opentransportdata.swiss`
- **SwissBoundaries3D** national boundary geometry from `swisstopo`
- **OpenStreetMap POIs and exported supermarket records** for the infrastructure layers

The project relies on established public data rather than scraping. The main preprocessing burden lies in **scope control**:

- remove cross-border stops from the raw GTFS feed
- isolate rail services from the full public transport network
- collapse platform-level stops into logical stations for visualization

Current size after each filtering step:

| Stage | Count |
| --- | ---: |
| Raw GTFS stops | 95,415 |
| Stops inside Switzerland | 75,775 |
| Rail stop entries | 4,105 |
| Logical rail stations | 1,938 |

## Problematic

The central question of the project is the following:

**How does rail accessibility vary across Switzerland, and how does that accessibility translate into access to everyday infrastructure and retail choice?**

Milestone 1 adopts a **rail-first** scope rather than a full multimodal routing framework for three reasons:

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

Filtering to rail services reduces the network substantially, and deduplicating platforms into logical stations makes the resulting representation more suitable for map-based visualization.

![Swiss rail stations](/figures/swiss_rail_stations.png)

![Deduplicated Swiss rail stations](/figures/swiss_rail_stations_deduplicated.png)

One of the main Milestone 1 findings is that the analysis becomes substantially more tractable when it is modeled at the **station** level rather than at the raw stop or platform level.

### 3. Station activity

The activity view measures the number of unique active rail trips per logical station within a selected time window.

![Top 10 busiest rail stations in the morning peak](/figures/busiest_rail_stations_morning_peak.png)

This view adds a second analytical dimension beyond geography by highlighting central transfer hubs that are not necessarily dominant in the spatial distribution alone.

### 4. Reachability from a single origin

From Lausanne at `08:00`, the current rail-only model reaches `1,663` stations within a 6-hour window.

![Lausanne reachability at 08:00 within 6 hours](/figures/lausanne_reachability_0800_6h.png)

### 5. Multi-origin comparison

A comparison of four major origins across four departure times extends the analysis beyond a single-city example. The strongest result in the current export is `Zürich HB` at `12:00`, which reaches `1,535` stations (`92.3%` of the rail network) within 6 hours.

The weakest of the sampled cases is `Genève` at `18:00`, with `1,383` reachable stations (`83.2%`).

![Reachability comparison across origins and departure times](/figures/reachability_comparison_heatmap.png)

The corresponding comparison table is available as [CSV](/data/reachability_comparison.csv).

## Scope

Milestone 1 presents the project as a **nationwide Swiss rail accessibility visualization**. Multimodal transport is treated as a later extension of the analytical framework.

The following components remain **out of scope** at this stage:

- buses, trams, cable cars, and boats as first-class modes
- explicit walking links between nearby stops
- cross-border continuation outside Swiss territory
- full path reconstruction for itinerary explanations

## Assessment of the Current Analysis

The current analysis is sufficient for Milestone 1 because it already provides:

- a credible public dataset choice
- non-trivial but manageable preprocessing
- clear exploratory findings
- a visualization question that can scale into a broader final analysis project

The remaining work for the final report concerns sharper communication of **scope, assumptions, limitations, and originality**, rather than additional engineering complexity.

## Future Work

Three extensions are planned for the final visualization.

### 1. Travel cost as a second dimension

The current model encodes reachability as a single scalar — **travel time**. The planned extension adds **ticket price** as a parallel dimension, turning the problem into a two-vector accessibility question: *where can you reach within T minutes and CHF B?*

Swiss Federal Railways publishes a fare formula based on distance and fare class. This makes it straightforward to attach a cost estimate to every computed itinerary and expose a **budget slider** alongside the existing time window. The visual encoding would shift from a single colour scale to a 2-D mapping, for example using hue for travel time and opacity for affordability, or a bivariate colour scheme.

This extension is meaningful for the audience of commuters and students, for whom cost is often the binding constraint rather than time.

### 2. Full multimodal network (bus, tram, and local services)

The current scope is deliberately rail-only. The full GTFS feed already contains bus, tram, and other local services. Incorporating them requires:

- extending the routing graph to include all public transport modes
- modelling walking transfers between nearby stops
- handling the much larger stop count (~75 000 stops vs. ~1 700 stations)

The visual payoff is substantial: rail-only reachability severely underestimates accessibility in rural areas where a train station may be several kilometres from the actual destination. A multimodal map would show a markedly different — and more honest — picture of national accessibility.

### 3. Continuous-time slider and free origin selection

The current interface offers four fixed departure times and four fixed origins. The planned final interface replaces both with continuous controls:

- a **time-of-day slider** that shows how the reachable region expands or contracts as departure time moves through the day
- a **free origin picker** that lets the user click any point on the map (or type any Swiss address) and immediately recompute reachability from that location

The continuous time slider turns the static map into an animation frame, making the temporal rhythm of the timetable directly visible. Free origin selection makes the tool genuinely useful rather than illustrative, allowing a user to answer the question *"what can I reach from my town at 07:15?"* rather than only from the four pre-selected cities.
