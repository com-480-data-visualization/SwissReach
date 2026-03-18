# Related Work

## Public Transport Isochrone References

Existing projects show that public transport accessibility is a well-established visualization topic:

- [Mapnificent](https://www.mapnificent.net/) is a classic browser-based public transport isochrone tool built on GTFS data. It illustrates the analytical value of varying origin and departure time in reachability maps.
- [TravelTime](https://app.traveltime.com/) shows how travel-time maps can support accessibility stories across multiple transport modes and realistic transfer assumptions.

These references validate the general visual framing, but they do not remove the need for a project-specific analytical angle.

## Standards That Matter For Extension

Two GTFS features are especially relevant for future work:

- [GTFS Pathways](https://gtfs.org/getting-started/features/pathways/) for modeling in-station movement, entrances, stairs, elevators, and traversal time
- [GTFS transfers.txt](https://gtfs.org/documentation/schedule/reference/#transferstxt) for minimum transfer times and route-specific transfer rules

These standards are important because the current Milestone 1 model still uses a fixed transfer dwell rather than detailed walking or station-internal navigation.

## Originality

The originality of SwissReach lies in the **combination** of design choices:

- a **nationwide Swiss** perspective rather than a single-city demo
- a **rail-first** scope that remains narrow enough to stay feasible
- **station-level deduplication** to bridge raw GTFS data and visualization-friendly interaction
- an analytical structure that mixes **network activity**, **single-origin reachability**, **amenity access**, and **retail comparison**

The resulting contribution lies in transforming a large transit feed into a clear, data-visualization-oriented narrative that remains feasible within the course timeline.

It is also important to note that the topic was chosen and partly explored before the EPFL `COM-490` assignment was released. Once it became clear that the original public-transport accessibility idea overlapped heavily with Assignment 1, the project was intentionally extended with amenity-count and retail-density analyses in order to create clearer analytical separation.

## Design Inspirations

The current design draws on three visualization ideas:

- **isochrone maps** for communicating time-based accessibility
- **hub rankings** for showing network centrality through traffic volume
- **comparison matrices** for making time-of-day and origin differences legible without forcing users to inspect one map at a time

This combination is particularly suitable for a VitePress-based project site because it supports both static reporting and a path toward richer interactive views.
