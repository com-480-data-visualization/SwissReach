# Final website plan

This page outlines how we intend to structure the **final SwissReach web experience**: two main narrative tracks, with light interactivity and a clear progression from overview to everyday outcomes.

## Two narrative tracks

1. **The transport network itself** — where services run, and how far you can get from stations.
2. **How transport connects people to supermarkets** — putting reachability in the context of real daily destinations.

## 1. Landing page

**Theme**  
What SwissReach is, in one breath.

**One-line pitch**  
See how Swiss public transport shapes **everyday reachability** — not just where lines run, but what becomes practical to reach.

**Content**

- A concise title and hero.
- A single **pan-Swiss basemap**: either all public-transport stop locations or a light reachability backdrop.
- Two short sentences of context.

**Goal**  
Signal immediately that this is **not** a generic map toy: the site is about **reachability** and its consequences for daily life.

## 2. First story: Transport

### 2.1 Modes and spatial footprint

**Content**

- **Switzerland**: rail stations / platforms (rail-focused backbone).
- **Vaud**: bus stops (local, everyday mobility).

**Suggested visuals**

- Swiss rail stop / station map.
- Vaud bus stop map.

**Light interaction**

- Toggle **Rail / Bus**.
- Toggle **Switzerland / Vaud**.

**Takeaway**  
The national story is dominated by **rail** as the backbone; **bus** is the right lens for local, day-to-day movement.

### 2.2 Reachability from the network

**Content**

- **Switzerland**: **train + short walking** transfers between nearby stops/stations.
- **Vaud**: **bus + walking** with the same transfer idea.
- Show **isochrone-style** reach from selected origins: how far you can get in fixed time budgets.
- Optional highlights: busiest hubs, strongest coverage, or “largest reachable footprint” examples.

**Suggested visuals**

- Representative station: **10 / 20 / 30 minute** reachability map.
- Pan-Swiss view: **ranking or coverage** of how many stations each origin can reach within a window.
- Vaud: local **travel-time** or cumulative reach map.

**Light interaction**

- Time slider: **10 / 20 / 30 minutes**.
- Pick a station to drill into local reachability.

**Takeaway**  
Networks differ not only in **geometry** (where stops sit) but in **performance** (who can reach whom, and how fast). National rail and regional bus obey different logics at different scales.

## 3. Second story: Supermarkets

### 3.1 Where supermarkets are

**Content**

- Switzerland-wide supermarket locations.
- **Canton-level** brand mix; **Vaud** as a worked example.

**Suggested visuals**

- National supermarket scatter / density.
- Vaud: brand-specific footprint (e.g. Migros vs Coop vs discount chains).

**Light interaction**

- **Select canton**.
- Filter: **All brands** / Migros / Coop / Lidl / Aldi / Denner (and other labels as data allow).

**Takeaway**  
Retail geography is uneven in its own right; **brand strategies** may show different spatial coverage patterns.

### 3.2 Supermarket reachability

**Content**

- **Switzerland**: from each **rail** station, how many supermarkets lie within **30 minutes** (train + walk).
- **Vaud**: **bus + walk** reachability to supermarkets in a local window.

**Suggested visuals**

- National map: **30-minute** supermarket access from stations.
- Vaud: bus-based supermarket reach map.
- Optional small multiples or a control for **10 / 20 / 30 minutes**.

**Light interaction**

- Time presets: **10 / 20 / 30 minutes**.
- Mode toggle: **Train + walk** / **Bus + walk** (aligned with the transport section).

**Takeaway**  
The value of a transport network shows up when you ask **“what can I actually do?”** — e.g. how many food stores are realistically reachable. **“Where can I get to?”** often explains daily life better than **“where is the stop?”**.

## 4. Closing / synthesis page

**Theme**  
What **transport accessibility** means in everyday life.

**Content**

- A deliberate **contrast**:
  - **Left**: regions or corridors where the **transport network** is strong (fast, wide coverage from key hubs).
  - **Right**: regions where **supermarket reachability** is strong (many stores within the same time budget).

**Takeaway**  
A strong network on paper does **not** always line up with strong access to daily resources. The **national rail backbone** and **local bus fabric** play different roles in how people experience accessibility.

## 5. Methods (short)

**Content**

- Data sources (GTFS, boundaries, supermarket / POI layers).
- How **reachability** is computed (time-expanded graph, walking links, horizons).
- How transport layers are **joined** to supermarket layers for the retail story.

**Suggested visual**

- A simple **pipeline diagram**: raw data → cleaned network → reachability → linked outcomes.

**Goal**  
Give the site intellectual closure without turning into a full technical paper.

*This plan is a living roadmap; section order and exact controls may shift as prototypes land.*
