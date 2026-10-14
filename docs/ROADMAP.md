# Orbis roadmap — finite release contract

Release: **orbis-roadmap-v1**. Scope frozen 14 October 2026; editorial cutoff **14 October 2026**. This document is the current delivery and acceptance plan. [ROADMAP-SCOPE.json](ROADMAP-SCOPE.json) lists every required story, campaign and atlas indicator. Changing required IDs, coverage, fallbacks or the cutoff is a scope change to record explicitly; implementing agents must not silently shrink the contract.

The roadmap defines work ready for review in this repository. Production deployment is a separate action and still requires Tommi's explicit authorization under `CLAUDE.md`. This rewrite does not start a Codex Goal, authorize external messages, or authorize automatic commits or deployment.

## Completion condition

The finite release is complete only when **M1-M10 all pass** the criteria below, every required story and indicator in the scope manifest exists, every required campaign contains its chapters in the specified order, and the acceptance ledger contains direct evidence for each milestone. Existing files and implemented features must be checked, not assumed complete. A documented blocker does not satisfy a deliverable.

The final release must have:

- The ten Phase A stories and the eight campaigns enumerated below, with all fixed chapters present (shared stories count once).
- Sources and redistribution terms checked for every imported dataset, map and media file; registered source IDs, as-of dates and claim-level citations for significant factual statements, numbers, borders, movements and casualty estimates.
- Successful desktop and mobile scene review, campaign navigation, deep links and embed checks, with no unresolved missing files, runtime errors or acceptance failures.
- The frozen 94-indicator atlas validated, plus working two-country comparison.
- A tested artifact-only refresh workflow and the four-chapter dated conflicts snapshot, with truthful per-source coverage dates.
- A final acceptance report with check results, reviewed screenshots, limitations and reproduction commands. No milestone may be marked complete solely because code exists or a licence checker passes.

Continuous scouting, future updates and the ideas appendix are outside this release's completion condition. Implementing a refresh mechanism is finite; operating it indefinitely is not.

## Milestones and delivery order

| Milestone | Fixed deliverable | Exit evidence |
|---|---|---|
| M1 | Ten Phase A stories: eight existing stories plus `night-light-change` and `empty-skies` | All ten pass the common chapter gate; light-change demonstrates dated before/after and empty-skies demonstrates a sourced bounded aviation comparison |
| M2a | Turkey first release: `tr-empire-pressure`, `tr-war-dissolution`, `tr-republic` | Three reviewed chapters, live campaign entry containing those three in order, landing page and next/back checks |
| M2 | Complete Turkey's seven chapters | Final seven-chapter campaign and common chapter gate; M2a is an intermediate release, not completion of M2 |
| M3 | Roman Empire: seven chapters | Chapter gate plus BC/AD display, historical names, dated shapes or cited overlays and at least one interactive historical timeline |
| M4 | United States: nine chapters | Chapter gate plus sourced territorial change, Indigenous land-loss coverage, dated movement and election categories; `us-abroad` may be reused after review |
| M5 | European Union: six chapters | Chapter gate plus overlapping memberships, group outlines, a sourced budget chart and a region comparison |
| M6 | World War II: eight chapters | Chapter gate plus dated occupation snapshots, a sourced campaign movement and Eastern/Pacific coverage; atrocities follow the editorial rules |
| M7 | Ukraine: seven chapters | Chapter gate plus event coverage, displacement and dated energy comparison; territory portrayal follows the fallback contract |
| M8 | Holy Roman Empire: six chapters | Chapter gate plus a dated territorial-patchwork view, names and empire context using the geometry fallback |
| M9 | Fixed atlas and refresh tooling | All frozen 94 indicators pass the atlas gate; artifact workflow passes the refresh gate |
| M10 | Four-chapter October 2026 conflicts snapshot | Chapter gate plus explicit coverage dates and reproducible UCDP/UNHCR-backed outputs where applicable |

Turkey scouting may overlap M1. A source-heavy M1 delay must not prevent M2a from progressing; M1 still must pass before the full release is complete. Build and review one complete Turkey chapter before expanding the first release. M9 may run alongside the series, but its refresh gate precedes M10. Resolve source risks early and continue independent milestones while a dependency is blocked.

The earlier five build waves are recorded as complete in [BUILD-PLAN.md](BUILD-PLAN.md). Most required renderer capabilities already exist; validate them through these stories. Add engine work only to satisfy a specific acceptance criterion. A separate MapLibre renderer, street-level detail and a custom WebGL vector renderer are not required by this release.

## Fixed chapter scope

Each new chapter has **4-8 substantive scenes**; existing reused stories retain their scene count if they cover the listed topic and pass review. Each scene must make a concrete geographic point using a map layer, annotation, chart or comparison. Text-only padding, placeholder scenes and empty campaigns fail acceptance. Chapter IDs are reserved by the scope manifest, not published by it.

### M1 — Phase A

Required IDs: `whales`, `launches`, `friends`, `roman-roads`, `colonies`, `night-light-change`, `empty-skies`, `fame`, `refugees`, `countryside`. The countryside story compares rural and urban net-migration patterns in 2000–2019, with its cumulative-rate methodology disclosed. The new night-light chapter compares two explicitly named observation dates. The empty-skies chapter uses a dated before/during/after aviation disruption comparison, with coverage and methodology stated; it does not require live flight tracking.

### M2 — Turkey: Anatolia, empire, republic

Campaign ID: `turkey-history`. Required reading order:

- `tr-anatolia` — Anatolia before the Ottomans.
- `tr-ottoman-world` — An Ottoman world.
- `tr-empire-pressure` — An empire under pressure.
- `tr-war-dissolution` — War and dissolution.
- `tr-republic` — Making the republic.
- `tr-changing-republic` — A changing republic.
- `tr-world` — Turkey in the world.

First release is the three M2a IDs above. Cover the land and its changing populations and states; distinguish earlier Anatolian civilisations from modern Turkey. Include Byzantine, Armenian, Greek, Kurdish and other histories where relevant. The war/dissolution chapter includes the Armenian genocide with sourced, plain-language accounts. Later chapters stop at the frozen editorial cutoff.

### M3 — The Roman Empire

Campaign ID: `roman-empire`. Required reading order:

- `rome-carthage` — Rome and Carthage.
- `rome-expansion` — Growth by conquest.
- `roman-roads` — Roads and cities.
- `rome-frontier` — The frontier.
- `rome-split` — East and West.
- `rome-fall` — The falls of Rome and Constantinople.
- `rome-legacy` — What remains.

`roman-roads` is reused after review; no duplicate chapter is needed. The fall chapter distinguishes the western and eastern endpoints.

### M4 — The United States

Campaign ID: `united-states`. Required reading order:

- `us-colonies` — Thirteen colonies.
- `us-expansion` — Territorial expansion.
- `us-indigenous-land` — Indigenous land loss.
- `us-statehood` — Becoming states.
- `us-civil-war` — The Civil War split.
- `us-frontier` — Railroads and the frontier.
- `us-immigration` — Immigration waves.
- `us-elections` — The electoral map.
- `us-abroad` — America abroad.

Territorial acquisition, statehood and Indigenous dispossession are separate subjects. Counties are required only for scenes that use them, not a complete historical county explorer.

### M5 — The European Union

Campaign ID: `european-union`. Required reading order:

- `eu-growth` — From the Coal and Steel Community to the EU.
- `eu-clubs` — Euro, Schengen and opt-outs.
- `eu-budget` — Who pays and who receives.
- `eu-regions` — Cohesion money and regions.
- `eu-brexit` — Brexit.
- `eu-candidates` — Candidates and enlargement.

### M6 — World War II

Campaign ID: `world-war-ii`. Required reading order:

- `ww2-before` — Europe before the war.
- `ww2-expansion` — Expansion and occupation.
- `ww2-east` — The Eastern Front.
- `ww2-pacific` — The Pacific.
- `ww2-holocaust` — The Holocaust.
- `ww2-bombing` — Bombing cities.
- `ww2-end` — The end of the war.
- `ww2-borders` — The postwar borders.

### M7 — The war in Ukraine

Campaign ID: `ukraine-war`. Required reading order:

- `ua-2014` — Crimea and Donbas.
- `ua-invasion` — The invasion.
- `ua-counteroffensives` — Kyiv, Kharkiv and Kherson.
- `ua-front` — The long front.
- `ua-energy` — Energy and night lights.
- `ua-refugees` — Refugees and displacement.
- `ua-snapshot` — Where things stood at the cutoff.

Aid tracking is outside this initial seven-chapter scope unless separately added with a cleared source; it must not substitute for a required chapter. The snapshot reports source coverage at or before the cutoff, not an unsupported claim about the current front.

### M8 — The Holy Roman Empire

Campaign ID: `holy-roman-empire`. Required reading order:

- `hre-charlemagne` — Charlemagne.
- `hre-1000` — The empire around 1000.
- `hre-patchwork` — The territorial patchwork.
- `hre-westphalia` — Westphalia.
- `hre-end` — Napoleon and the end.
- `hre-after` — What followed.

### M10 — Wars: October 2026 snapshot

Campaign ID: `conflicts-snapshot`. Required reading order:

- `wars-overview` — Overview of Ukraine, Sudan and Syria.
- `wars-ukraine` — Ukraine.
- `wars-sudan` — Sudan.
- `wars-syria` — Syria.

The overview compares only these three fixed case studies. It is not presented as an exhaustive list or ranking of active wars. Each country chapter explains the latest available source window at the cutoff; missing or lagged observations are visible. Existing conflict stories can supply data and scenes, but all four required IDs must exist and pass review.

## Common chapter acceptance gate

For every required story:

1. **Content and sources:** review every scene against cited evidence. Record citations at scene/notes level and, for claims not directly traceable there, in the acceptance ledger. Border/control snapshots and movement coordinates need a source for each date. Distinguish estimates, uncertainty and source disagreements; do not extrapolate sparse events into territory control. Newly fetched data must satisfy the two-tier policy in `CLAUDE.md` and [LICENSING.md](LICENSING.md).
2. **Data:** datasets load from declared paths, carry registered `source` and `asOf`, identify observation dates, units and coverage, and have no malformed values or unexplained gaps. Validate timeline endpoints and at least one interior transition in every time-dependent layer. Keep new git data files under 1 MB; target 300 KB per reduced dataset. External runtime imagery must work under the documented CSP or degrade to a sourced static view with a visible coverage note.
3. **Browser:** use `tools/shoot.mjs` to capture every scene and every switch option at **1280x800** and **390x844**. Inspect the images; exercise timeline controls, country selection, event cards, swipe and charts wherever used. Check labels, legends, sources and navigation are readable, with no clipped essential content, missing data, failed required requests or page errors.
4. **Navigation and access:** each story deep link and campaign landing link works after reload; next/back visits the correct available chapter. Verify keyboard access to relevant controls, readable scene descriptions and `?embed=1` on every campaign's first chapter and any newly changed shared control.
5. **Registration:** story file and index ID agree. Register only reviewed existing chapters in `stories/campaigns.json`; initially Turkey contains M2a, finally each campaign matches the manifest order. Update intros, dates and change logs when chapters are added. Existing reused stories appear under their campaign after registration; verify their direct links still work.
6. **Checks:** run `node tools/check-licences.js` and appropriate changed-feature checks. The final shared-engine regression pass covers every registered story using `tools/test-all.sh` or an equivalent runner, with failures inspected and resolved. The screenshot scripts print findings; their exit code alone is not proof of success.

## M9 — atlas acceptance gate

The manifest freezes **94 existing indicator IDs** from the catalogue at the time of this rewrite, including 18 non-World-Bank indicators. No open-ended indicator target is required. Previously skipped WGI and V-Dem indicators remain outside this release; skipped entries are not counted as delivered indicators.

- Every frozen ID has exactly one catalogue entry and a loadable dataset; check schema, source, licence badge/terms, units, year ordering, finite numeric values and explicit missing-data handling. Keep observation years separate from retrieval/as-of dates.
- Automatically open every indicator and exercise its first and last available timeline year; inspect at least one indicator from each topic and each source manually, on both target viewports. Verify search, topics, deep-link reload and no-data states.
- Country profiles show the selected country's values with source and year. Add a two-country comparison: select/change/clear either country, use the same indicator/year/units for both, and display missing values honestly. Compare Turkey/Austria on population and life expectancy at a shared available year and verify the UI against the dataset; include a missing-value case.
- Rebuild using `tools/build/atlas.py` followed by `tools/build/atlas_extra.py`, or documented cached inputs if a download is temporarily unavailable. Cached-input validation proves reproducibility for that snapshot, not freshness. Keep a before/after manifest check so rebuilds cannot silently drop frozen indicators.

## M9 — refresh acceptance gate

Implement one **artifact-only GitHub Actions workflow with manual dispatch**, plus a locally callable refresh command, for the fixed providers **UCDP conflict events and UNHCR displacement** used by M10. Resolve the actual registered source IDs, cleared endpoints and required credentials in the implementation. Keep output changes limited to the named snapshot datasets and metadata; do not rewrite sourced editorial prose automatically.

- Produce validated changed datasets, per-source coverage/retrieval dates and a change report as a review artifact. No automatic git commit, push, email, production deployment or scheduled activation is needed to meet this release contract.
- Exercise three deterministic cases: changed input produces a reviewable diff/change log; identical input produces no spurious dataset changes; malformed/unavailable input fails visibly and preserves the last good output. Fixtures/cached raw inputs are valid for these cases and must be labelled.
- Validate the Actions configuration and its invoked command locally. If a manual Actions run is available within authorized repository access, record the run/artifact link; otherwise record local results and explicitly state that hosted execution was not verified. Local verification satisfies this scoped tooling milestone, not a claim that a live schedule is operating.
- Document installation, source versions, credentials, invocation, failures and the proposed weekly activation procedure. Future weekly scheduling and automatic commits remain a separate decision. Ongoing operations are outside the goal.

## Source fallbacks and blocked work

These bounded fallbacks are part of the proposed release scope. Any fallback used must be named in the story notes and acceptance ledger and still deliver the listed chapter topics and interactions. They permit a different representation, not invented history or removal of required chapters.

| Dependency | Allowed release representation | Completion evidence |
|---|---|---|
| Ottoman / Roman / US historical geometry incomplete | Source-dated simplified snapshots, cleared historical-map overlays, or located events and cited schematic movements | Each displayed date/shape/path cites its source; maps disclose schematic or approximate geometry; required historical change remains understandable |
| WWII monthly fronts unavailable | Named dated occupation snapshots, cleared atlas scans and sourced campaign movements | Dates, territorial meaning and precision are explicit; no claim of a continuous monthly front |
| Ukraine front-line permissions unresolved | UCDP events, UNHCR flows, cleared imagery and optionally cleared settlement control points | Display explicitly distinguishes events/points from front-line polygons; includes source windows; no invented continuous control surface |
| HRE tiny territories unavailable | Empire outline and selected sourced territories plus a cleared patchwork map overlay | A readable dated patchwork scene and provenance for the selected geometry/map; no claim of exhaustive hundreds of territories |
| EU regional geometry unusable | A cleared regional dataset, or a cited regional comparison chart / located symbols with the same region-level values | Cohesion and regional differences are covered; a country-average fill alone does not pass the region criterion |
| Source temporarily offline | Versioned cached raw inputs with original provenance and coverage dates | Snapshot reproducible and labelled; freshness not asserted |

A missing source with no lawful, evidentially sound fallback is a blocker. Record the exact missing deliverable and needed decision, continue independent work, and leave the milestone incomplete. Do not count a permission request, unresolved citation or deferred chapter as delivered. External messages still need explicit user authorization.

## Acceptance ledger and goal-ready wording

Maintain one ledger at `docs/ROADMAP-ACCEPTANCE.md` during implementation. Required columns: milestone/story ID, status (`not started`, `in progress`, `blocked`, `passed`), artifact paths, source/content review evidence, desktop/mobile screenshot paths, interaction/navigation results, check commands/results, fallback/limitations and unresolved items. Use actual files, logs and observations, not an unsupported "reviewed" assertion. Record source review and visual review separately from automated checks. Leave temporary screenshots out of git unless they are intentionally small reference artifacts.

The ledger starts below with no release acceptance claimed. Scope changes require an entry describing the old and new requirement and their reason; reducing required chapters or acceptance checks requires explicit user agreement. New discovery does not automatically expand this finite release.

Suggested Goal completion contract:

> Complete release orbis-roadmap-v1 as frozen in docs/ROADMAP.md and docs/ROADMAP-SCOPE.json, following the milestone order and prioritising Turkey's M2a release. Continue until every required milestone and artifact passes its stated acceptance gate with direct evidence in docs/ROADMAP-ACCEPTANCE.md. Use only the documented source fallbacks, preserve source/licensing/editorial rules, and never count blocked or deferred work as completed. Keep work reviewable locally. Production deployment, external messages, scheduled activation and automatic commits need their separately stated authorization. Continuous maintenance and appendix ideas are outside this Goal.

## Reference material

The following feature status and source audit are inherited planning references, not new verification or release acceptance. Recheck applicable source terms when importing. F1-F12 and F17-F18 are recorded as built; F15 is implemented per story, F14 has the base atlas, F13 needs the scoped workflow, and F16 is needed only if a required scene cannot pass with its own historical detail.

## Feature reference and remaining work

Status below is the recorded implementation status, not proof of release validation. Effort is the original planning estimate: S = a day, M = a few days, L = a week or more. For built features, it does not represent remaining work.

| # | Status | Feature | Used by | Original effort | Design notes |
|---|---|---|---|---|---|
| F1 | Built; validate in stories | **Calendars and deep time** | Rome, HRE, all history | M | Store every date as astronomical year or `yyyymmdd` (proleptic Gregorian, year 0 = 1 BC). Display: "27 BC", "AD 117", "c. 800", optional second calendar line ("AUC 727", Julian date, Hijri, Hebrew, Chinese, Japanese, Persian: the browser's `Intl` handles all of these except Julian and AUC, which are a few lines of arithmetic). Scene setting `calendar`. Timeline that can mix scales (millennia → years). |
| F2 | Built; validate in stories | **Shapes over time** | Every history topic | L | New dataset shape: GeoJSON/TopoJSON features with `from`/`to` dates and properties (`name`, `group`, `parent`). Layer `shapes`: shows features valid at the timeline date, colours by property or category, labels, tap shows name and dates. Not tied to ISO codes. Generalises today's `borders` (CShapes snapshots). |
| F3 | Built; validate in stories | **Control areas and fronts** | WWII, Ukraine, conflicts now | M | Built on F2: polygons by date for "held by X"; the layer can highlight what changed since the previous date (gained / lost) and draw the boundary as a front line. |
| F4 | Built; validate in stories | **Dated movements** | Campaigns, journeys, Lewis and Clark | M | Lines whose points carry dates; the timeline reveals the path up to the current date, a marker moves along it. Extends `lines` (`until` already exists). |
| F5 | Built; validate in stories | **Event cards** | All history, conflicts | M | Points with title, date, short text, optional image and source; tap opens a card in the panel; optional list of events synced to the timeline. Extends `events` (now anonymous dots). |
| F6 | Built; validate in stories | **Historical place names** | Rome, HRE, WWII | S | Gazetteer entries with names valid for periods (Byzantium → Constantinople → Istanbul); labels follow the timeline. Source: Pleiades, Wikidata. |
| F7 | Built; validate in stories | **Historical map overlays** | HRE, WWII | M | Scans of public-domain maps, warped offline to lon/lat (GDAL, in `tools/`), shown as a raster patch with an opacity slider. The raster engine already draws patches with a bounding box. |
| F8 | Built; validate in stories | **Before / after swipe** | Night lights, Ukraine, Europe 1914/1919 | M | Split the map with a draggable divider: left and right show two dates or two layers. |
| F9 | Built; validate in stories | **Pick a country** | Friendships, trade partners, UN votes, migration | M | Dataset shape `matrix` (country × country). Layer `pairs`: tap a country, the others colour by their value with it. |
| F10 | Built; validate in stories | **Multi-country regions** | EU, US counties | M | `regions` today covers one country; extend to a region set spanning many (NUTS 2), with data keyed by region code. |
| F11 | Built; validate in stories | **Categories over time** | US elections, EU memberships | S | `categories` with a value per year, following the timeline. |
| F12 | Built; validate in stories | **More panel charts** | EU budget, rulers, population | M | Stacked area, small multiples, and a Gantt chart (reigns, presidencies, wars). |
| F13 | Open; M9 artifact workflow | **Scheduled data refresh** | Conflicts now, trade war, atlas | M | Bounded artifact-only refresh workflow for M9: rebuild a fixed source list, validate, produce diffs and change logs. Scheduled activation and automatic commits require a separate decision. |
| F14 | Base built; expand / validate | **Country atlas** | M9 | L | Indicator catalogue (`data/atlas/catalog.json`: id, name, topic, unit, source, licence tier, years); one small file per indicator (~50 KB) loaded on demand; picker with search and topics; timeline; tap a country → profile card with its key indicators; compare two countries. Licence badge per indicator, non-commercial ones marked. |
| F15 | Per-story build scripts | **Density grids from big point sets** | Whales, fires, GBIF, flights | S | Build-time tool that bins millions of points into a lon/lat grid for the `raster` layer; keeps files small. |
| F16 | Deferred until needed | **Detailed Europe** | HRE, EU regions | M | Natural Earth 1:10m (public domain) for Europe, loaded only when a story asks for it. |
| F17 | Built; validate in stories | **Overlapping memberships** | EU clubs, alliances | S | A country in several sets: hatching or multiple outlines instead of one fill. |
| F18 | Built; validate in stories | **Group outlines** | EU, eurozone, HRE, Roman Empire | S | Dissolve a group of shapes into one outer border (`topojson.merge`). |

## Recorded source audit by topic

Licence check completed 14 October 2026 (details and quotes in [DATA-CATALOG.md](DATA-CATALOG.md#licence-check-history-conflicts-and-indicators-october-2026)). "Base" = commercial use OK; "story" = allowed as a labelled story layer; "ask" = needs written permission first.

| Topic | Use | Story layer only | Ask first / avoid |
|---|---|---|---|
| Turkey | Scout existing historical coverage, cleared gazetteers, public-domain map scans and official statistics; audit new sources before import | Only after source-specific redistribution and licence checks | Ottoman / republican territorial coverage not yet inventoried; no continuous border dataset assumed |
| Roman Empire | Itiner-e roads (in use), Pleiades (in use), Stanford ORBIS route network (CC BY 3.0), DARE places and tiles (CC BY, pin version), DARMC CC0 sets | AWMC geodata (ODbL), historical-basemaps (GPL) | DARMC road network (no licence), Euratlas (proprietary) |
| Holy Roman Empire | Princes & Townspeople city→ruler histories 1100–1800 (CC0) | ETH Roller territories (CC BY-NC-SA, auto-generated, weak), HistoGIS Imperial Circles 1648/1792 (treat as BY-NC), IEG-Maps images (conflicting terms: confirm) | GeaCron, Centennia. The recorded audit found no suitable complete open HRE territory set; use the M8 fallback |
| United States | Newberry county boundaries 1629–2000, MEDSL presidential returns 1976–2024 (CC0), USFS Royce land cessions (CC BY 4.0), Library of Congress map scans, US Census | — | IPUMS NHGIS (no redistribution); USGS territorial-acquisition shapefile not found online |
| European Union | Cohesion Open Data (CC0), Eurobarometer aggregates (CC BY 4.0), EP election results (commercial reuse with source) | **GISCO NUTS geometry is non-commercial** (EuroGeographics) | Eurobarometer microdata (GESIS, unverified) |
| World War II | EHRI SAMU killing sites in Ukraine (CC BY 4.0), West Point atlas scans (public domain, per map), Library of Congress | CShapes 1938/1945 (in use) | EHRI/Stanford monthly borders 1938–45 ("scholarly", no commercial: write to the authors), THOR bombing (likely public domain, unverified), USHMM, Arolsen. The recorded audit found no suitable open front-line dataset; use the M6 fallback |
| Ukraine | UNHCR (in use), UCDP, Sentinel-2 and NASA GIBS imagery | Wikipedia control-points module (~1,000 points, CC BY-SA), DeepStateMap credited screenshots | DeepStateMap data/API, ISW/CTP, Kiel Support Tracker (no licence) |
| Conflicts now | UCDP Candidate monthly CSV (CC BY 4.0, file name changes per release; API now needs a token), GDELT (open, machine-coded), IPC hunger via HDX (CC0), UNHCR API (no key) | IDMC displacement (NC-SA: its own terms are stricter than HDX's) | ACLED and HDX HAPI conflict events (= ACLED), CFR tracker, CrisisWatch, ReliefWeb content |
| Country atlas | UNDP HDR (CC BY 3.0 IGO), Penn World Table 11 (CC BY), Ember (CC BY), UMD tree-cover loss, WRI Aqueduct, UCDP, UNHCR, IPC, ILOSTAT (S) | UNESCO UIS (SA), V-Dem (SA), WHO GHO (CC BY + WHO terms, values unchanged), Yale EPI (NC-SA), Freedom House (NC, data by request), TI CPI (ND: verbatim only), IDMC (NC-SA), UNdata, IMF (no bulk scraping) | IHME GBD, UN Comtrade, UN SDG database as such, UNICEF/IGME, UNODC, SIPRI; hold WID, ND-GAIN, RSF until terms are found. OWID only via each origin's own licence |

## Editorial rules for history and war

- **Name the source and date for every border, front line and casualty figure** in the scene text or notes. Disputed numbers are shown as ranges with both sources.
- **Never draw control areas or front lines ourselves** without a cited source for each date. Simplification is fine; invention is not.
- **Names by period**: places carry the name of the time, with today's name on first mention.
- **Calendars**: dates before 1582 are Julian unless stated; Russian dates before 1918 are given in both styles where it matters (the "October" Revolution was in November).
- **Live conflicts**: every scene shows "as of"; numbers that change weekly are not hard-coded in text without a date.
- **Atrocities and genocide**: plain language, sourced figures, no decorative visualisation (no animated pulses on mass-killing sites).
- **Point of view**: borders and names that differ by country use the existing point-of-view layer where it matters.


## Outside this release: ongoing operations and future ideas

Future scouting, additional indicators, new conflicts, post-cutoff historical/current events, scheduled operation, automatic data commits, source-permission outreach, languages, street-level imagery and AI authoring are follow-up work. They do not prevent completion of the frozen release. The retained ideas below are an appendix, not required deliverables; some already exist and must not be rebuilt merely because they appear here.

## Longer-term story ideas (check existing stories before scheduling)

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

## Longer-term visual ideas (some capabilities now exist)

- **Satellite and image layers:** night-lights imagery (NASA VIIRS), the vanishing Aral Sea, Amazon deforestation, Alpine glaciers retreating, Lagos sprawling.
- **Density grids:** true population density, temperature change 1880–today animated, sea-level rise flooding Bangladesh and the Netherlands.
- **Thousands of moving points:** every ship at sea, live flights, every earthquake since 1900, live wildfires (NASA FIRMS).
- **3D:** cumulative CO₂ as columns rising from each country; cities as population spikes.
- **Animated flow fields:** jet streams, the Gulf Stream, ocean plastic drifting into garbage patches.
- **Cartograms:** the world redrawn by population, GDP, emissions. Morphing the true map into a cartogram would be a signature moment, like the globe-to-flat flip.
- **Regions inside countries:** EU regions by income, Austria by Bundesland, US counties.
- **Street-level zoom:** Vienna's growth and the Ringstraße; one street in Mariupol before and after.

## Longer-term product ideas (some tools already exist)
- **Authoring:** stories as a structured file format plus a simple editor. An AI drafting assistant could write a story from sources, with mandatory citations per number and a human checking each one.
- **Data pipeline:** pull numbers at build time from Our World in Data, the World Bank and UN APIs. Every figure gets a source and an "as of" date automatically.
- **Languages:** English only for now (a German version was built and dropped; `t()` in `js/i18n.js` keeps the door open).
- **Embeds and a school edition:** stories embedded in articles and lessons, one link per scene (deep links already exist).
- **Social export:** render any story as a short video or image sequence.
- **Quiz mode:** "where is this?", "which is bigger?", streaks.
- **Personal layer:** "your city in the world": distances, flight curves and supply chains from wherever you are.


## Technical direction and remaining external dependencies

Keep D3 for the signature globe-to-flat scenes and the existing raster layer for imagery. Evaluate a separate MapLibre/PMTiles engine only when a concrete story needs street-level or detailed-front rendering; it is not a prerequisite for the Turkey first release. A custom WebGL vector renderer remains a larger long-term option.

External dependencies retained from the completed build plan: real pipeline routes need a distributable Global Energy Monitor download; daily front-line data needs cleared terms or written permission; street-level imagery / OSM needs a hosting and licensing decision; an AI authoring assistant needs an API key and a server. Labels, accessibility, large-data performance and narrative media should be tested on actual new scenes rather than treated as blanket absent capabilities.


## Additional backlog retained from the parallel history plan

These candidates were retained when the parallel history plan was consolidated on 14 October 2026. They do not add acceptance requirements or chapters to the frozen M1-M8 release. Existing alternate stories and series remain available in the catalogue; investigate overlap before scheduling further work.

- **Ruling houses:** the Spanish succession, Habsburg marriages, the collapse of monarchies in 1917-1918 and Scotland's kings.
- **Colonialism:** the Atlantic slave trade, the scramble for Africa, trading companies, the British Raj and colonial legacies.
- **History of Asia:** Chinese dynasties, the Mongol Empire, Silk Roads and Indian Ocean trade, Mughal and Maratha India, Tokugawa-to-Meiji Japan, Southeast Asian maritime states, Ottoman and Safavid empires, colonial Asia and independence, and the partition of India. Clear source terms and choose finite chapter scopes before importing new data.
- **Additional historical depth:** Roman cities and Rome's eastern rival; Ukraine grain exports and fires along the front; emperors and electors; tracing the HRE's 1648 territories from a cleared map (see [the tracing brief](briefs/HRE-TRACING.md)).
- **Elections explorer:** complete and verify the data build, replace unresolved Wikidata party IDs, correct the US latest-election selection, register any new sources and inspect country samples before registering the datasets. The explorer UI alone is not evidence that its data is complete.

These are future candidates, not a second delivery plan. The finite milestone scope and completion evidence above remain authoritative.
