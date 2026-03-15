# Related Work

## Public Transport Isochrone References

Several existing projects show that public transport accessibility is a strong visualization topic:

- [Mapnificent](https://www.mapnificent.net/) is a classic browser-based public transport isochrone tool built on GTFS data. It demonstrates how compelling reachability maps can be when users can vary origin and time.
- [TravelTime](https://app.traveltime.com/) shows how travel-time maps can support accessibility stories across multiple transport modes and realistic transfer assumptions.

These references validate the general visual framing, but they do not replace the need for a project-specific angle.

## Standards That Matter For Extension

Two GTFS features are especially relevant for future work:

- [GTFS Pathways](https://gtfs.org/getting-started/features/pathways/) for modeling in-station movement, entrances, stairs, elevators, and traversal time
- [GTFS transfers.txt](https://gtfs.org/documentation/schedule/reference/#transferstxt) for minimum transfer times and route-specific transfer rules

They are important because the current Milestone 1 model still uses a simple fixed transfer dwell rather than detailed walking or station-internal navigation.

## Why SwissReach Is Still Original

SwissReach is not original because it invented the idea of an isochrone map. It is original because of the **combination** of choices it makes:

- a **nationwide Swiss** perspective rather than a single-city demo
- a **rail-first** scope that is intentionally narrow enough to stay feasible
- **station-level deduplication** to bridge raw GTFS data and visualization-friendly interaction
- a storytelling structure that mixes **network activity**, **single-origin reachability**, and **multi-origin comparison**

In other words, the originality is in turning a large, messy transit feed into a clear, data-vis-oriented narrative that can be completed within the course timeline.

## Design Inspirations

The current direction takes inspiration from three visualization ideas:

- **isochrone maps** for communicating time-based accessibility
- **hub rankings** for showing network centrality through traffic volume
- **comparison matrices** for making time-of-day and origin differences legible without forcing users to inspect one map at a time

That combination is particularly suitable for a VitePress-based project site because it supports both static storytelling and a path toward richer interactive views later.
