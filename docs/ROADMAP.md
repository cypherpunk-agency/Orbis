# Orbis roadmap

Status: limits of the current build, story backlog, and suggested technical path.

Base data must allow commercial use; story layers may use any licence that lets us publish the files in an open repository (two-tier rule in `CLAUDE.md`, details in [LICENSING.md](LICENSING.md)).

**Next:** the plan for history series, wars, calendars, a live conflicts view and a country atlas is in [PLAN-HISTORY-ATLAS.md](PLAN-HISTORY-ATLAS.md); data ideas are in [DATA-CATALOG.md](DATA-CATALOG.md).

## Current technical limits

### Geometry
- **Coarse world map only.** There is a single 1:110 million map with 177 countries, so coastlines turn blocky beyond about 3× zoom. Small states like Singapore, Malta and Bahrain are missing entirely.
- **No detail levels.** A real map swaps in more detailed geometry as you zoom in. This one shows the same shapes at every zoom.
- **Today's borders only.** Countries can change colour over time, but their shapes can't. That's the core blocker for historical maps.
- **No regions inside countries.** There are no provinces, states or Bundesländer, and no cities.
- **One version of every disputed border.** Kashmir, Crimea and Western Sahara can't be redrawn from different countries' points of view.

### Rendering
- **The whole world redraws every frame.** It uses a 2D canvas, which is fine at this detail. At 10× more detail or thousands of points, it would stutter on phones.
- **Only shapes, lines and dots.** There are no images such as satellite photos or night lights, no density grids, no 3D bars, and no animated wind or ocean currents.
- **Labels can overlap.** Nothing keeps them apart (visible on the Atlantic cables), and the base map itself has no country names.
- **Routes are hand-drawn.** Sea routes occasionally clip land, and pipelines are schematic.

### Data
- **Every number is typed in by hand and approximate.** There is no data pipeline, no "as of" date per figure, and no automatic link to the source. For a public product, this is the biggest risk.
- **Nothing updates live.**

### Storytelling and authoring
- **Text and map only.** There are no photos, quotes, audio, video or small charts beside the map.
- **Stories are code.** Nobody but a developer can write one.
- **English only.**
- **All stories load up front.** That's fine at 18 stories; at 100 they need to load on demand.
- **Little screen-reader access.** The text is accessible, but what the map shows isn't described.

## Historical maps and wars

This needs two different capabilities, built as separate layers.

### 1. Borders that change over time (years)
- **Data:**
  - **OpenHistoricalMap** (CC0 by default) is the preferred source. Filter out features tagged CC BY-SA.
  - Excluded for licensing (see `LICENSING.md`): CShapes 2.0 (non-commercial), historical-basemaps (GPL-3.0), Thenmap (no stated licence).
- **What we'd add:** the year slider swaps in the borders valid for that year, instead of recolouring today's shapes. Countries cross-fade or reshape between snapshots.
- **Stories this unlocks:**
  - Austria-Hungary falls apart, 1914–1923 (strong local hook for a Vienna-based project).
  - Europe in 1914, 1939, 1945 and 1991.
  - Africa's decolonisation, 1950–1980.
  - Yugoslavia breaks up.
  - Partition of India, 1947.
  - Germany divided and reunited.
  - Poland moves west by 200 km.

### 2. Front lines inside a war (days or weeks)
- **Data for Ukraine:**
  - **UCDP** (CC BY 4.0) for located conflict events: usable now.
  - **DeepStateMap** tracks the front daily. Commercial data use needs their written approval; political perspective also needs weighing.
  - **ISW / Critical Threats** need written permission beyond brief excerpts. **ACLED** needs a paid corporate licence.
  - Without a licensed front-line source, front lines must be drawn in-house from open reporting, with sources cited per date.
- **What we'd add:**
  - detailed geometry and a detailed map engine for these scenes
  - a date scrubber with annotated events
  - smooth reshaping of the controlled area between dates
  - a before/after swipe comparison
  - city labels
- **Stories this unlocks:**
  - Ukraine 2022 to today: the invasion, the Kyiv withdrawal, the Kharkiv and Kherson counteroffensives, the long attrition after 2023.
  - Syria 2011–2024, ending with the fall of Assad.
  - Sudan since 2023.
  - Historical fronts: WWII on the Eastern Front; Napoleon's march on Moscow (Minard's chart on a globe).

### Editorial catches
- **Who controls what is contested.** Every frame needs a source and a date. Showing two sources side by side is more honest than picking one.
- **Map changes hide people.** Pair the shifting map with a human-cost layer: UNHCR refugee numbers, UN civilian casualty counts.
- **Tone.** Playing back a war on a slider can feel like a game. A slower pace and restrained colours help.

## More stories with today's engine

The timeline-plus-colouring feature already handles "rights and change over time" stories cheaply.

### Geopolitics
- Nuclear-armed states, and the countries that gave up their weapons (South Africa, Ukraine).
- US military bases abroad.
- The South China Sea: overlapping claims and the nine-dash line.
- Water conflicts: Ethiopia's Nile dam, the Indus, the Mekong dams.
- Sanctions on Russia: who imposes them and who doesn't.
- UN votes on Ukraine: how the world split.

### Economics
- Where AI runs: data centres, chips and electricity.
- The world's top container ports (nine of the top ten are in Asia).
- Grain from Ukraine and Russia: Egypt's and Lebanon's dependence, and the 2022 shock.
- Who owns US government debt.
- The Big Mac index: price levels around the world.

### Statistics
- Carbon emissions three ways: total, per person, historical cumulative. The rankings flip each time.
- Life expectancy, 1950 to today, on a timeline.
- Time-zone oddities: China runs on one zone; Spain sits on the "wrong" one.
- The 2026 World Cup, using map data alone.

### Rights over time (timeline stories)
- Women's right to vote, by year.
- Abolition of the death penalty, by year.
- Independence days of all countries.

### People
- Great journeys: Magellan and Elcano's circumnavigation, Zheng He's fleets, Ibn Battuta.
- The Silk Road.
- Humans spreading out of Africa.
- Hungary 1956: about 180,000 refugees cross into Austria.
- How COVID spread from Wuhan.

## Stories that need new capabilities

- **Satellite and image layers:** night-lights imagery (NASA VIIRS), the vanishing Aral Sea, Amazon deforestation, Alpine glaciers retreating, Lagos sprawling.
- **Density grids:** true population density, temperature change 1880–today animated, sea-level rise flooding Bangladesh and the Netherlands.
- **Thousands of moving points:** every ship at sea, live flights, every earthquake since 1900, live wildfires (NASA FIRMS).
- **3D:** cumulative CO₂ as columns rising from each country; cities as population spikes.
- **Animated flow fields:** jet streams, the Gulf Stream, ocean plastic drifting into garbage patches.
- **Cartograms:** the world redrawn by population, GDP, emissions. Morphing the true map into a cartogram would be a signature moment, like the globe-to-flat flip.
- **Regions inside countries:** EU regions by income, Austria by Bundesland, US counties.
- **Street-level zoom:** Vienna's growth and the Ringstraße; one street in Mariupol before and after.

## Expansion ideas
- **Authoring:** stories as a structured file format plus a simple editor. An AI drafting assistant could write a story from sources, with mandatory citations per number and a human checking each one.
- **Data pipeline:** pull numbers at build time from Our World in Data, the World Bank and UN APIs. Every figure gets a source and an "as of" date automatically.
- **Languages:** English only for now (a German version was built and dropped; `t()` in `js/i18n.js` keeps the door open).
- **Embeds and a school edition:** stories embedded in articles and lessons, one link per scene (deep links already exist).
- **Social export:** render any story as a short video or image sequence.
- **Quiz mode:** "where is this?", "which is bigger?", streaks.
- **Personal layer:** "your city in the world": distances, flight curves and supply chains from wherever you are.

## Recommended technical path
- **Keep D3** for the world-scale, signature globe-to-flat scenes.
- **Add MapLibre with self-hosted vector tiles** (Protomaps single-file format) for deep-zoom scenes like front lines and cities. Each scene picks its engine; the switch can happen during a zoom.
- **Alternative: one custom WebGL renderer** doing the projection morph on the GPU. Cleanest long-term and handles detail at scale, but about 3–5× the effort.

## Suggested order
1. **Data pipeline with sources.** Prerequisite for going public.
2. **Borders over time (OpenHistoricalMap).** Big impact, moderate effort; unlocks a whole category including Austria-Hungary.
3. **Deep-zoom engine and front lines.** Ukraine as the flagship story.
4. **Cartograms.** A second signature moment.
