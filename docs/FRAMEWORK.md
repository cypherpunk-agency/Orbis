# Orbis framework plan

Goal: one engine and one story format that cover as much of the roadmap as possible, with a demo story proving each capability. The first real stories: **oil**, **gas**, **debt** and **resources**.

Licensing follows `docs/LICENSING.md`: base data commercial-only, story layers any publishable licence, everything labelled in the UI.

---

## 1. Architecture

### 1.1 Rendering: three stacked layers, one projection

| Layer | Technology | Draws | Why |
|---|---|---|---|
| **Raster underlay** | WebGL (one canvas) | Satellite, night lights, relief, density grids, temperature fields | A textured lon/lat mesh projected **in the vertex shader** with the same globe / Equal Earth / Mercator maths and the same blend as today's morph. Raster layers therefore survive the signature globe-to-flat flip. |
| **Vector layer** | Canvas 2D + D3 (today's engine) | Countries, borders, choropleths, flows, lines, points, symbols, spikes, cartograms | Already works; keeps code small. |
| **Label layer** | DOM, absolutely positioned | Country names, place labels, annotations | Collision avoidance, crisp text, accessible to screen readers. |

All three read one shared view state (centre, zoom, projection pair, blend). A WebGL failure degrades to today's look.

**Deep zoom (later phase):** scenes that need street or front-line detail switch to **MapLibre GL v5** (native globe) reading the same self-hosted PMTiles. The switch happens during a fly-to so it reads as one camera move.

### 1.2 Base map modes (user-selectable, also set per scene)

| Mode | Phase-1 data (in engine, single texture) | Later (tile pyramid, MapLibre) |
|---|---|---|
| **Political** | Natural Earth 1:110m today → 1:50m countries + 1:10m simplified; admin-1 lazy-loaded; country labels | Natural Earth vector tiles z0–8 |
| **Satellite** | NASA Blue Marble NG, 8192×4096 (≈ 4.9 km/px) on phones, 16384×8192 (≈ 2.4 km/px) on desktop | Blue Marble z0–8 tiles (≈ 600 m/px) + regional Sentinel-2/Landsat patches to z13 (≈ 19 m/px) |
| **Night** | NASA Black Marble 2016, same sizes | z0–8 tiles |
| **Physical** | Natural Earth shaded relief + hypsometric tints | Copernicus GLO-90 hillshade z0–8 |

The political borders and labels can draw on top of satellite and night modes ("hybrid").

**Disputed borders:** switch to Natural Earth point-of-view editions (33 countries ship ready-made at 1:10m), e.g. "Kashmir as seen from India / Pakistan / China".

### 1.3 Story format: data, not code

Today stories are JavaScript with inline functions. Move to one JSON file per story, loaded on demand:

```jsonc
{
  "id": "oil", "cat": "Economics", "title": "The oil machine",
  "hook": "...", "sources": ["eia-intl", "gem-goit", "baci"],
  "scenes": [{
    "title": "Who pumps it", "text": "...",
    "view": { "mode": "globe", "center": [45, 25], "zoom": 1.2 },
    "basemap": "political",
    "layers": [
      { "type": "symbols", "data": "oil/production", "value": "mbd", "color": "c3", "source": "eia-intl" }
    ],
    "timeline": { "data": "oil/production", "years": [1980, 2024], "step": 1 }
  }]
}
```

- **Layer `source` drives the UI licence line automatically.** Scenes do not list sources by hand.
- **Every dataset file carries `source`, `asOf`, `units`, `retrieved`.** The tooltip and notes print them, which fixes the biggest public risk (unsourced numbers).
- A schema plus `tools/check-stories.js` validates stories, sources and licences in one run.

### 1.4 Layer catalogue

Each capability is one layer type with one demo story. ✔ = engine already has a version.

| # | Layer type | What it shows | Demo story | Phase |
|---|---|---|---|---|
| 1 | `basemap` political / satellite / night / physical | The planet itself | **Explore mode** + "The world at night" | 1 |
| 2 | `choropleth` ✔ | Country values, timeline-aware | **Debt**: debt per country | 1 |
| 3 | `symbols` | Proportional circles per country or point | **Oil**: who produces | 1 |
| 4 | `flows` | Origin → destination arcs, width ∝ value, animated, top-N, tap a country for its in/out | **Oil/Gas/Debt**: who sells/lends to whom | 1 |
| 5 | `lines` ✔ (hand-drawn) → data-driven | Pipelines, cables, sea routes, styled by attribute | **Gas**: pipelines | 1 |
| 6 | `points` ✔ → data-driven | Facilities: LNG terminals, refineries, mines, fields | **Gas**: LNG terminals | 1 |
| 7 | `raster` | Any equirectangular grid: imagery, density, anomaly; timeline via texture atlas | **Gas**: flaring at night; **Population density** | 1–2 |
| 8 | `spikes` (pseudo-3D) | Vertical bars rising off the globe surface | **Debt**: debt stock as towers | 2 |
| 9 | `cartogram` | Countries resized by value, morphing from true shape | **Resources**: world redrawn by production | 2 |
| 10 | `regions` | Admin-1 (states, Bundesländer) choropleths | **Austria by Bundesland** | 2 |
| 11 | `labels` | Collision-free country and place labels | All | 1 |
| 12 | `panel media` | Small chart, image, quote beside the map | **Resources**: top producers bar chart | 1 |
| 13 | `borders-over-time` | Year-specific borders (OpenHistoricalMap) | **Austria-Hungary 1914–1923** | 3 |
| 14 | `particles` | Animated flow fields (winds, currents) | **Jet streams** | 3 |
| 15 | `deep-zoom` | MapLibre scenes, PMTiles, regional imagery | **Front lines** (Ukraine) | 3 |
| 16 | `pov` | Disputed borders by viewpoint | **Same border, different truths** (upgrade) | 2 |

---

## 2. The four priority stories

### 2.1 Oil: from well to wheel
| Scene | Layers | Data (licence) |
|---|---|---|
| Who pumps it (1980→2024 timeline) | symbols | EIA international (public domain) |
| Where the fields are | points | GEM Oil & Gas Extraction Tracker (CC BY 4.0) |
| Pipelines | lines | GEM Oil Infrastructure Tracker (CC BY 4.0) |
| By sea: routes and chokepoints | lines (our own routes), symbols at chokepoints, raster backdrop | EIA chokepoints (public domain); World Bank shipping density (CC BY 4.0) |
| Who sells to whom | flows | CEPII BACI HS 2709 (Etalab 2.0) |
| Refineries | points | EDF OGIM (CC BY 4.0) |
| Who burns it (per person) | choropleth | EIA (public domain) |

### 2.2 Gas: pipes versus ships
| Scene | Layers | Data |
|---|---|---|
| Who produces | symbols, timeline | EIA |
| The pipeline web (Nord Stream, TurkStream, Power of Siberia) | lines | GEM Gas Infrastructure Tracker (CC BY 4.0) |
| LNG: export and import terminals | points | GEM GGIT |
| Pipe vs ship flows | flows (two styles) | BACI HS 271121 / 271111 |
| Europe's switch 2021 → 2024 | flows + timeline | BACI |
| Burned for nothing: flaring at night | raster (night) | NASA Black Marble (CC0) |

### 2.3 Debt: where it starts, where it goes
| Scene | Layers | Data |
|---|---|---|
| Who owes how much | choropleth, spikes | BIS total credit (≈ 44 economies), Eurostat/OECD, World Bank IDS |
| Who holds US debt | flows into USA | US Treasury TIC (public domain) |
| Banks lend across borders | flows | BIS consolidated banking statistics (free, no paywall) |
| China the lender | flows, points (projects) | World Bank IDS (CC BY 4.0), AidData (ODC-By) |
| The world redrawn by debt | cartogram | same |
| **Gap** | Global bilateral bond holdings and all-country public debt | IMF CPIS / Global Debt Database: allowed as a **non-commercial story layer only if IMF terms allow redistribution** (to verify) |

### 2.4 Resources: who has what
| Scene | Layers | Data |
|---|---|---|
| Pick a resource (lithium, cobalt, copper, rare earths, wheat, …) | symbols + panel bar chart, commodity switcher | USGS Mineral Commodity Summaries (CC0), FAOSTAT (CC BY 4.0) |
| Where the mines are | points | USGS MRDS (public domain, stale); Maus mining polygons (CC BY-SA) as a story layer |
| Where it flows | flows | BACI (Etalab 2.0) |
| The world redrawn by production | cartogram | USGS |
| Who restricts exports | choropleth | OECD export-restrictions inventory (CC BY 4.0, verify) |

---

## 3. Data volumes

### 3.1 Per story (shipped to the browser, gzipped)
| Story | Payload |
|---|---|
| Oil | ≈ 250–300 KB |
| Gas | ≈ 200–550 KB (trunk lines only vs all operating pipelines) |
| Debt | ≈ 80–100 KB |
| Resources | ≈ 150–300 KB (with/without mine points) |
| Optional shipping-density backdrop | +1–1.5 MB |

### 3.2 Base map, hosted
| Item | Phase 1 (single textures) | Later (tile pyramids) |
|---|---|---|
| Political vectors | ≈ 0.2–0.7 MB (50m + simplified 10m + admin-1 on demand) | 15–27 MB (Natural Earth z0–8 PMTiles) |
| Satellite | ≈ 5 MB (8k) + 18 MB (16k) | ≈ 0.6 GB (Blue Marble z0–8) |
| Night | ≈ 3 MB + 10 MB | ≈ 0.1–0.25 GB |
| Physical | ≈ 5–10 MB | ≈ 0.3–0.6 GB |
| Regional close-ups | n/a | +0.2–0.7 GB each (500×500 km to z13) |
| **Total** | **≈ 50 MB** | **≈ 1.2 GB + patches** |

What the levels buy: single 16k texture ≈ 2.4 km/px (sharp to ≈ 3× zoom on a retina screen); z8 tiles ≈ 600 m/px (regions and big cities); z13 patches ≈ 19 m/px (districts, fields, airports).

### 3.3 Processing (offline, not shipped)
Largest raw inputs: BACI ≈ 2.4 GB zipped, BIS LBS ≈ 360 MB, FAOSTAT trade ≈ 420 MB, Blue Marble full-res ≈ 0.5–1 GB, GEM files tens of MB. A one-time workspace of ≈ 10 GB is enough; nothing raw goes into git.

### 3.4 Where it lives
- **Git:** code, stories, reduced datasets (well under 50 MB total), phase-1 textures if under ~25 MB each (otherwise object storage).
- **Object storage + CDN** (e.g. Cloudflare R2, no egress fees): textures and PMTiles. One `pmtiles` file per layer, served with HTTP range requests; no tile server.

---

## 4. Data pipeline

```
tools/fetch/<source>.py   download raw → .cache/ (gitignored)
tools/build/<dataset>.py  reduce → data/<story>/<dataset>.json  { source, asOf, retrieved, units, rows }
tools/check-licences.js   every source registered, documented, policy-compliant
tools/check-stories.js    stories valid, every layer's dataset and source exist
```

Rebuilding a dataset is one command; the "as of" date comes from the source, not from hand entry.

---

## 5. Phases

**Status (phase 1 delivered):** data-file stories with lazy loading; layer types `symbols`, `flows`, data-driven `lines` and `points`, computed `choropleth`; panel bar chart; label collision avoidance; WebGL raster underlay with political / satellite / night base maps (4096×2048 textures, 370 KB and 243 KB); data pipeline for EIA, BACI and textures; **Oil** (8 scenes) and **Gas** (7 scenes) stories. Pipelines and terminals are schematic own work until the Global Energy Monitor files are downloaded. Still open from phase 1: `raster` as a story layer (beyond base maps), DOM label layer.


| Phase | Deliverable | Proves |
|---|---|---|
| **1. Framework + oil and gas** | JSON story format, lazy loading; layer types symbols, flows, data-driven lines/points, labels, panel chart; WebGL raster underlay with satellite and night base modes; data pipeline for EIA, GEM, BACI; **Oil** and **Gas** stories | Layers 1–7, 11, 12 |
| **2. Debt + resources** | spikes, cartogram, regions, POV borders; **Debt** and **Resources** stories; port the 18 launch stories to JSON with sourced data | Layers 8–10, 16 |
| **3. Time and depth** | Borders over time (OpenHistoricalMap), MapLibre deep zoom with PMTiles, particles | Layers 13–15 |

Phase 1 is the largest because it lays the foundations every later story reuses.

---

## 6. Open decisions
1. **Hosting** for textures and tiles (Cloudflare R2 suggested) and whether the repo will be public (the licence policy assumes it can be).
2. **IMF data** as a non-commercial debt layer: needs a check that IMF terms allow redistribution.
3. **Share-alike sign-offs** if wanted: Maus mining polygons (CC BY-SA), Protomaps/OSM tiles (ODbL) for the later detail layer.
4. **GEM downloads** go through a web form; someone needs to download them once (free).
