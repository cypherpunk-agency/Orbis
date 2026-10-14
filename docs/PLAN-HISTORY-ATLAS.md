# Plan: history, wars, calendars, conflicts now, country atlas

What we want to tell next, what the engine and data are missing, and the order to build it in. Companion files: [DATA-CATALOG.md](DATA-CATALOG.md) (where data comes from), [STORY-FORMAT.md](STORY-FORMAT.md) (how stories are written), [LICENSING.md](LICENSING.md) (what we may use).

Status 14 October 2026: engine features built: F1 calendars, F2 shapes over time, F3 control areas and fronts, F4 dated movements, F5 event cards, F6 historical names, F7 map overlays (+ warp tool), F8 before/after swipe, F9 pick a country, F10 regions spanning countries, F11 categories over time, F12 stacked area and Gantt charts, F14 country atlas (World Bank base tier), F17 overlapping memberships, F18 group outlines. Open: F13 scheduled refresh (needs decision 3), F15 density grids (done per story in build scripts), F16 detailed Europe (deferred: historical shapes carry their own detail). Phase A stories are being built; licence checks for the history, conflict and indicator sources are done (section 3).

## Summary

Six new tracks, in this order:

| Phase | Track | Demo | Key new features |
|---|---|---|---|
| A | **Ten data stories** from the catalogue | Whales, launches, friendships, Roman roads, colonies, night lights, empty skies, fame, refugees, fleets | Pick-a-country layer, density grids, before/after |
| B | **Deep time** | Roman Empire, United States | Calendars, shapes over time, event cards, historical names, Gantt and stacked charts |
| C | **Wars** | World War II, war in Ukraine | Front lines and control areas, dated movements, historical map overlays, swipe |
| D | **Unions and empires** | European Union, Holy Roman Empire | Multi-country regions, group outlines, detailed Europe |
| E | **Country atlas** | Pick any indicator for any country and year | Indicator catalogue, picker, country profile, compare |
| F | **Conflicts now** | Today's major wars, kept current | Scheduled data refresh, "as of" stamps, change log |
| — | **Scouting** (continuous) | New stories from new data | [DATA-CATALOG.md](DATA-CATALOG.md) |

Phases A–D can overlap: the engine work is serial, data and stories run in parallel, as before.

## 1. What each topic needs

### United States
Chapters: thirteen colonies → territorial expansion (purchases, cessions, wars) → Indigenous land loss → statehood order → the Civil War split → railroads and the frontier → immigration waves → the electoral map over time → the US abroad (link to existing `us-abroad`).

Needs: **shapes over time** (states and territories with start/end dates, not today's ISO units), **categorical timeline** (election winner per state per year), **dated movements** (Lewis and Clark, Trail of Tears), **event cards** (battles, treaties), US **counties over time** for the detailed chapters.

### European Union
Chapters: from the Coal and Steel Community to 27 (existing `since` layer) → euro, Schengen and opt-outs (overlapping memberships) → who pays and who receives (budget balances) → cohesion money by region → Brexit → candidates.

Needs: **multi-country regions** (NUTS 2 across all member states), **group outlines** (draw the EU's outer border, the eurozone's, Schengen's), **overlapping categories** (a country in several clubs), **stacked charts** (budget over time).

### Roman Empire
Chapters: Rome and Carthage → growth by conquest (509 BC – AD 117) → roads (Itiner-e) and cities (Pleiades) → the frontier (limes) → split East and West → fall in the West 476 / East 1453 → what is left (roads under motorways, Latin languages, place names).

Needs: **calendars and deep time** (years BC, Roman AUC dating, uncertain dates "c."), **shapes over time** (provinces and the empire's extent by year), **historical place names** (Londinium, Lutetia), **event cards**, a timeline that spans 2,000 years without losing detail.

### Holy Roman Empire
Chapters: Charlemagne 800 → the Empire around 1000 → the patchwork: hundreds of territories (around 1648) → the Peace of Westphalia → Napoleon and the end in 1806 → what followed (German Confederation, Germany, Austria).

Needs: **detailed Europe geometry** (tiny territories at regional zoom), **shapes over time** with a **hierarchy** (territories inside the Empire, Empire outline around them), **Julian/Gregorian** dates (Catholic and Protestant states switched at different times), historical map **overlays** where no vector data exists.

### World War II
Chapters: Europe 1938 → expansion 1939–42 (Axis control at its peak) → the Eastern Front → the Pacific → the Holocaust (carefully: places, numbers with sources) → the bombing of cities → 1945 and the new borders (existing `borders-in-time`).

Needs: **control areas over time** (occupied territory by month, with gained/lost highlighted), **front lines**, **dated movements** (offensives, convoys), **event cards**, **historical map overlays** (public-domain US Army maps where vectors don't exist), casualty **ranges** (sources disagree).

### War in Ukraine
Chapters: 2014 (Crimea, Donbas) → February 2022 invasion → the Kyiv retreat and Kharkiv counter-offensive → the long front → strikes on energy (night lights, existing UCDP events) → refugees (UNHCR) → aid (Kiel tracker) → where things stand.

Needs: **control areas over time** (the hardest licence question: see Data), **before/after** (night lights, imagery), **flows** (refugees), **"as of" stamps and refresh** (shared with Conflicts now).

## 2. Feature gaps

Effort: S = a day, M = a few days, L = a week or more.

| # | Feature | Used by | Effort | Design notes |
|---|---|---|---|---|
| F1 | **Calendars and deep time** | Rome, HRE, all history | M | Store every date as astronomical year or `yyyymmdd` (proleptic Gregorian, year 0 = 1 BC). Display: "27 BC", "AD 117", "c. 800", optional second calendar line ("AUC 727", Julian date, Hijri, Hebrew, Chinese, Japanese, Persian: the browser's `Intl` handles all of these except Julian and AUC, which are a few lines of arithmetic). Scene setting `calendar`. Timeline that can mix scales (millennia → years). |
| F2 | **Shapes over time** | Every history topic | L | New dataset shape: GeoJSON/TopoJSON features with `from`/`to` dates and properties (`name`, `group`, `parent`). Layer `shapes`: shows features valid at the timeline date, colours by property or category, labels, tap shows name and dates. Not tied to ISO codes. Generalises today's `borders` (CShapes snapshots). |
| F3 | **Control areas and fronts** | WWII, Ukraine, conflicts now | M | Built on F2: polygons by date for "held by X"; the layer can highlight what changed since the previous date (gained / lost) and draw the boundary as a front line. |
| F4 | **Dated movements** | Campaigns, journeys, Lewis and Clark | M | Lines whose points carry dates; the timeline reveals the path up to the current date, a marker moves along it. Extends `lines` (`until` already exists). |
| F5 | **Event cards** | All history, conflicts | M | Points with title, date, short text, optional image and source; tap opens a card in the panel; optional list of events synced to the timeline. Extends `events` (now anonymous dots). |
| F6 | **Historical place names** | Rome, HRE, WWII | S | Gazetteer entries with names valid for periods (Byzantium → Constantinople → Istanbul); labels follow the timeline. Source: Pleiades, Wikidata. |
| F7 | **Historical map overlays** | HRE, WWII | M | Scans of public-domain maps, warped offline to lon/lat (GDAL, in `tools/`), shown as a raster patch with an opacity slider. The raster engine already draws patches with a bounding box. |
| F8 | **Before / after swipe** | Night lights, Ukraine, Europe 1914/1919 | M | Split the map with a draggable divider: left and right show two dates or two layers. |
| F9 | **Pick a country** | Friendships, trade partners, UN votes, migration | M | Dataset shape `matrix` (country × country). Layer `pairs`: tap a country, the others colour by their value with it. |
| F10 | **Multi-country regions** | EU, US counties | M | `regions` today covers one country; extend to a region set spanning many (NUTS 2), with data keyed by region code. |
| F11 | **Categories over time** | US elections, EU memberships | S | `categories` with a value per year, following the timeline. |
| F12 | **More panel charts** | EU budget, rulers, population | M | Stacked area, small multiples, and a Gantt chart (reigns, presidencies, wars). |
| F13 | **Scheduled data refresh** | Conflicts now, trade war, atlas | M | GitHub Actions job that reruns build scripts weekly, runs the licence check, and commits only when data changed; scenes show "as of"; series change logs (exist) record what moved. |
| F14 | **Country atlas** | Phase E | L | Indicator catalogue (`data/atlas/catalog.json`: id, name, topic, unit, source, licence tier, years); one small file per indicator (~50 KB) loaded on demand; picker with search and topics; timeline; tap a country → profile card with its key indicators; compare two countries. Licence badge per indicator, non-commercial ones marked. |
| F15 | **Density grids from big point sets** | Whales, fires, GBIF, flights | S | Build-time tool that bins millions of points into a lon/lat grid for the `raster` layer; keeps files small. |
| F16 | **Detailed Europe** | HRE, EU regions | M | Natural Earth 1:10m (public domain) for Europe, loaded only when a story asks for it. |
| F17 | **Overlapping memberships** | EU clubs, alliances | S | A country in several sets: hatching or multiple outlines instead of one fill. |
| F18 | **Group outlines** | EU, eurozone, HRE, Roman Empire | S | Dissolve a group of shapes into one outer border (`topojson.merge`). |

## 3. Data, by topic

Licence check completed 14 October 2026 (details and quotes in [DATA-CATALOG.md](DATA-CATALOG.md#licence-check-history-conflicts-and-indicators-october-2026)). "Base" = commercial use OK; "story" = allowed as a labelled story layer; "ask" = needs written permission first.

| Topic | Use | Story layer only | Ask first / avoid |
|---|---|---|---|
| Roman Empire | Itiner-e roads (in use), Pleiades (in use), Stanford ORBIS route network (CC BY 3.0), DARE places and tiles (CC BY, pin version), DARMC CC0 sets | AWMC geodata (ODbL), historical-basemaps (GPL) | DARMC road network (no licence), Euratlas (proprietary) |
| Holy Roman Empire | Princes & Townspeople city→ruler histories 1100–1800 (CC0) | ETH Roller territories (CC BY-NC-SA, auto-generated, weak), HistoGIS Imperial Circles 1648/1792 (treat as BY-NC), IEG-Maps images (conflicting terms: confirm) | GeaCron, Centennia. **No openly licensed HRE territory polygons exist** (decision 2) |
| United States | Newberry county boundaries 1629–2000, MEDSL presidential returns 1976–2024 (CC0), USFS Royce land cessions (CC BY 4.0), Library of Congress map scans, US Census | — | IPUMS NHGIS (no redistribution); USGS territorial-acquisition shapefile not found online |
| European Union | Cohesion Open Data (CC0), Eurobarometer aggregates (CC BY 4.0), EP election results (commercial reuse with source) | **GISCO NUTS geometry is non-commercial** (EuroGeographics) | Eurobarometer microdata (GESIS, unverified) |
| World War II | EHRI SAMU killing sites in Ukraine (CC BY 4.0), West Point atlas scans (public domain, per map), Library of Congress | CShapes 1938/1945 (in use) | EHRI/Stanford monthly borders 1938–45 ("scholarly", no commercial: write to the authors), THOR bombing (likely public domain, unverified), USHMM, Arolsen. **No open front-line dataset exists** |
| Ukraine | UNHCR (in use), UCDP, Sentinel-2 and NASA GIBS imagery | Wikipedia control-points module (~1,000 points, CC BY-SA), DeepStateMap credited screenshots | DeepStateMap data/API, ISW/CTP, Kiel Support Tracker (no licence) |
| Conflicts now | UCDP Candidate monthly CSV (CC BY 4.0, file name changes per release; API now needs a token), GDELT (open, machine-coded), IPC hunger via HDX (CC0), UNHCR API (no key) | IDMC displacement (NC-SA: its own terms are stricter than HDX's) | ACLED and HDX HAPI conflict events (= ACLED), CFR tracker, CrisisWatch, ReliefWeb content |
| Country atlas | UNDP HDR (CC BY 3.0 IGO), Penn World Table 11 (CC BY), Ember (CC BY), UMD tree-cover loss, WRI Aqueduct, UCDP, UNHCR, IPC, ILOSTAT (S) | UNESCO UIS (SA), V-Dem (SA), WHO GHO (CC BY + WHO terms, values unchanged), Yale EPI (NC-SA), Freedom House (NC, data by request), TI CPI (ND: verbatim only), IDMC (NC-SA), UNdata, IMF (no bulk scraping) | IHME GBD, UN Comtrade, UN SDG database as such, UNICEF/IGME, UNODC, SIPRI; hold WID, ND-GAIN, RSF until terms are found. OWID only via each origin's own licence |

## 4. Editorial rules for history and war

- **Name the source and date for every border, front line and casualty figure** in the scene text or notes. Disputed numbers are shown as ranges with both sources.
- **Never draw control areas or front lines ourselves** without a cited source for each date. Simplification is fine; invention is not.
- **Names by period**: places carry the name of the time, with today's name on first mention.
- **Calendars**: dates before 1582 are Julian unless stated; Russian dates before 1918 are given in both styles where it matters (the "October" Revolution was in November).
- **Live conflicts**: every scene shows "as of"; numbers that change weekly are not hard-coded in text without a date.
- **Atrocities and genocide**: plain language, sourced figures, no decorative visualisation (no animated pulses on mass-killing sites).
- **Point of view**: borders and names that differ by country use the existing point-of-view layer where it matters.

## 5. Roadmap

Each phase ends as before: browser check of every scene, `node tools/check-licences.js`, push.

**Phase A: ten data stories** (from the catalogue's top list)
- Engine: F9 pick a country, F15 density grids, F8 before/after.
- Stories: Where the whales were · The launch explosion · Who your friends are · All roads lead to Rome · How long were you a colony? · Lights out, lights on · The sky went quiet · Where fame was born · Refugees stay close · Distant-water fleets (or Leaving the countryside if Global Fishing Watch needs a login we can't use).

**Phase B: deep time**
- Engine: F1 calendars, F2 shapes over time, F5 event cards, F6 historical names, F11 categories over time, F12 charts, F18 outlines.
- Series: *The Roman Empire* (6–8 chapters), *The United States* (8–10 chapters).

**Phase C: wars**
- Engine: F3 control areas and fronts, F4 dated movements, F7 historical map overlays (+ `tools/` warping script).
- Series: *World War II* (8 chapters), *The war in Ukraine* (7 chapters).

**Phase D: unions and empires**
- Engine: F10 multi-country regions, F16 detailed Europe, F17 overlapping memberships.
- Series: *The European Union* (6 chapters), *The Holy Roman Empire* (6 chapters).

**Phase E: country atlas**
- Engine: F14.
- Data: commercially usable indicators (World Bank CC BY, OWID-own, UN sources as cleared) plus non-commercial or share-alike ones (WHO, V-Dem, IMF), labelled "NC". Only terms that restrict redistribution exclude an indicator.

**Phase F: conflicts now**
- Engine: F13 scheduled refresh: declined; refresh by hand with the build scripts, "as of" date on every view.
- Series: *Wars now*: one chapter per major active conflict, plus an overview map; refreshed weekly.

**Continuous: scouting.** Each phase adds what it finds to the catalogue; ideas that need no new features go straight to stories.

## 6. Size budget

| Data | Estimate |
|---|---|
| Repository data today | 8.9 MB |
| Phase A (10 stories, ≤ 300 KB per dataset) | + 2–4 MB |
| History series (shapes by period, simplified) | + 3–6 MB, loaded per chapter |
| Detailed Europe (1:10m) | + ~1.5 MB, only when asked |
| Country atlas, 300 indicators × ~50 KB | + ~15 MB, one file per indicator, loaded on pick |
| Historical map overlays (WebP) | ~200–500 KB each; few |

Nothing over ~1 MB per file in git; big rasters are pre-cut or fetched at runtime (as with NASA GIBS).

## 7. Decisions for you

1. ~~Ukraine control of territory~~ **Decided (14 Oct 2026):** Wikipedia's settlement control points (CC BY-SA 4.0, story layer), labelled as volunteer-edited, dated by page revision, with UCDP events alongside. Areas drawn from the points are an approximation and are marked as such.
2. **Holy Roman Empire detail** (open): no openly licensed territory polygons exist. Options: trace outlines from public-domain maps; ETH Roller polygons (NC-SA, auto-generated); Imperial Circles (HistoGIS, treat as NC) + city-by-ruler points (Princes & Townspeople, CC0) + warped scans for the patchwork.
3. ~~Scheduled refresh~~ **Decided: no.** Data that changes (conflicts now, Ukraine) is refreshed by running the build scripts by hand; every view shows its "as of" date.
4. ~~Atlas non-commercial tier~~ **Decided:** the atlas is an optional layer, so non-commercial and share-alike indicators are included with an "NC" badge; only terms that restrict redistribution (or are unclear) exclude an indicator.
