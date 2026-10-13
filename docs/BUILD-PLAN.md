# Build plan: all stories and features

Goal: every capability in `FRAMEWORK.md` and every story in `ROADMAP.md`, built in five waves. Each wave ends with a browser check of every scene, `node tools/check-licences.js`, and a push.

## Working defaults (change any of these and the plan adapts)

| Topic | Default |
|---|---|
| File size | No file over ~1 MB in git; deep-zoom imagery is fetched at runtime from NASA GIBS (CC0), so nothing large is hosted |
| Share-alike | Not used in the base. Allowed in story layers if publishable (e.g. CShapes NC-SA, historical-basemaps GPL), labelled in the UI |
| War front lines | No licensed daily front-line source (ISW, DeepStateMap need permission). Conflict stories use UCDP events (CC BY 4.0) and dated, cited editorial annotations |
| AI drafting assistant | Deferred: needs an API key and a server, which a static site does not have |
| German | Translated by Claude, marked "translation under review" until a person checks it |

## Who builds what

- **Engine** (`js/`): built serially by the main session, because every feature touches the renderer.
- **Data + stories**: built in parallel by helper agents. Each agent only adds files under `tools/build/`, `data/<topic>/`, `stories/`, and returns registry entries; the main session registers sources, reviews numbers and text, tests every scene and commits.
- **Contract** between them: `docs/STORY-FORMAT.md`.

## Wave 1: foundations

| Feature | Notes |
|---|---|
| `since` layer | Colour countries from the year they joined/adopted something; replaces the JavaScript-only bloc timelines |
| Detailed geometry + level of detail | Natural Earth 1:50m loaded when zoomed in; small states become real shapes |
| Tap to focus | Tapping a country in a flows scene shows only its flows |
| Country labels | Names on the base map, collision-free, by zoom |
| `STORY-FORMAT.md` | Complete reference of the JSON format |
| Debt story | Finish with IMF (non-commercial), TIC, BIS, World Bank data |
| Port the 18 launch stories | To JSON, numbers sourced where a dataset exists |

## Wave 2: stories on the current engine (agents, in parallel)

- **Geopolitics:** nuclear-armed states; US military bases abroad; sanctions on Russia; UN votes on Ukraine; South China Sea claims; water conflicts (Nile, Indus, Mekong).
- **Economics:** top container ports; who owns US debt (in Debt); Big Mac index; where AI runs (if a licensable data-centre dataset exists).
- **Statistics:** CO₂ three ways; life expectancy 1950–today; time-zone oddities; World Cup 2026.
- **Rights over time:** women's suffrage; death-penalty abolition; independence days.
- **People:** great journeys (Magellan–Elcano, Zheng He, Ibn Battuta); the Silk Road; out of Africa; Hungary 1956; COVID's spread.

## Wave 3: grids, regions, borders by viewpoint, media

| Feature | Demo story |
|---|---|
| `raster` story layer (colour any lon/lat grid, with timeline) | Where people really live (population density); a warming world 1880–today |
| Terrain basemap | Used by water conflicts and journeys |
| `regions` (admin-1) | Austria by Bundesland; the US and India by state |
| Point-of-view borders | Same border, different truths (Kashmir, Crimea, Western Sahara) |
| Panel media: image, quote, line chart | People stories (Hungary 1956), trends |

## Wave 4: time and depth

| Feature | Demo story |
|---|---|
| Borders over time | Austria-Hungary falls apart; Europe 1914/1939/1945/1991; decolonisation; Yugoslavia; partition of India; Germany divided; Poland moves west |
| Many points with a timeline | Every big earthquake since 1900 |
| Particles (wind field) | Jet streams |
| Deep zoom (MapLibre + runtime NASA tiles) | Ukraine since 2022 (UCDP events); Syria 2011–2024; Sudan; Napoleon's march (Minard) |

## Wave 5: product

German; embed mode; save image / record video of a story; quiz mode; "your city in the world"; scene descriptions for screen readers; story editor (JSON with live preview).

## Blocked or deferred (needs a decision or outside input)

- Real pipeline routes: Global Energy Monitor download via their form.
- Front-line maps: written permission from ISW or DeepStateMap.
- Street-level imagery, OSM detail: hosting decision and ODbL sign-off.
- AI drafting assistant: API key and a small server.
