# Licensing policy

## The rule: two tiers

| Tier | What it covers | Licence requirement |
|---|---|---|
| **Base** | The map itself and the engine: country geometry, basemap imagery, borders, code libraries, fonts, anything every story depends on | **Must allow commercial use.** Copyleft or share-alike (GPL, CC BY-SA, ODbL) needs explicit sign-off. |
| **Story layer** | Optional data shown inside a story or as a switchable overlay; the site works without it | **Any licence**, including non-commercial or used-with-permission, **provided the files may be published in a public open-source repository.** |

Excluded at every tier: terms that forbid redistribution, unclear or missing terms, and "ask us" terms without a written grant on file.

### Obligations for every source
1. **Register it** in `js/sources.js` (tier, licence, use, credit) and add a row to the register below using its id in backticks.
2. **Label it in the UI.** Every story and scene lists its sources with their licence in the "Data" line under the story. Non-commercial and permission-only sources get a warning dot. "All licences" opens the full register.
3. **Keep it switchable.** A story layer must never be needed for the base map to work.
4. **Run the check:** `node tools/check-licences.js` fails if a source is unregistered, undocumented, has a base-tier source without commercial rights, or cannot be published.

> Non-commercial layers stay non-commercial wherever they appear. If the site is ever monetised (ads, paid tiers, client work), those layers must be removed, licensed, or kept off the commercial surface.

## Register (sources in use)

| Id | Source | Tier | Licence | Use | Credit |
|---|---|---|---|---|---|
| `naturalearth` | Natural Earth 1:110m countries (via world-atlas) | Base | Public domain | Commercial | Optional; "Made with Natural Earth" |
| `d3` | D3 7.9.0 | Base | ISC | Commercial | Keep licence notice |
| `topojson` | topojson-client 3.1.0 | Base | ISC | Commercial | Keep licence notice |
| `fonts` | Source Serif 4, Barlow Semi Condensed | Base | SIL OFL 1.1 | Commercial | None for web use |
| `nasa-bluemarble` | NASA Blue Marble Next Generation, 4096×2048 texture via GIBS (`data/tex/satellite-4096.webp`) | Base | NASA open data (CC0) | Commercial | "NASA Earth Observatory"; acknowledge GIBS; no implied endorsement |
| `nasa-blackmarble` | NASA Black Marble 2016 night lights, 4096×2048 texture via GIBS (`data/tex/night-4096.webp`) | Base | NASA open data (CC0) | Commercial | "NASA Earth Observatory / NASA GSFC"; acknowledge GIBS |
| `eia-intl` | US EIA international energy data, 2000–2024 (`data/energy/eia.json`) | Layer | US public domain | Commercial | "Source: U.S. Energy Information Administration"; no EIA logo |
| `eia-chokepoints` | EIA World Oil Transit Chokepoints, typed in (`data/energy/chokepoints.json`) | Layer | US public domain | Commercial | EIA, plus "based on Vortexa tanker tracking" |
| `baci` | CEPII BACI HS2017 V202601, trade 2021–2024 in energy, minerals, crops (`data/energy/trade.json`, `data/resources/trade.json`) | Layer | Etalab Open Licence 2.0 | Commercial | CEPII BACI, version and update date; built from UN Comtrade |
| `usgs-mcs` | USGS Mineral Commodity Summaries 2026 data release (`data/resources/usgs.json`) | Layer | US public domain (CC0) | Commercial | "Source: U.S. Geological Survey" |
| `faostat` | FAOSTAT crop production 2000–2024 (`data/resources/fao.json`) | Layer | CC BY 4.0 | Commercial (not in commercial promotion) | FAO citation incl. access date; no implied endorsement |
| `orbis-schematic` | Pipelines, sea lanes, terminals, refineries drawn by Orbis (`data/energy/infrastructure.json`) | Layer | Own work | Commercial | Marked as schematic |
| `editorial` | Rounded figures typed into stories | Layer | Facts (not copyrightable); cited in each story's notes | Commercial | Sources named in story notes |

## Evaluated candidates

Verdict columns: whether the source may be used as **base** data, and as a **story layer** under the rules above.

### Geometry, borders, maps

| Source | Licence | Base | Layer | Notes |
|---|---|---|---|---|
| Natural Earth 1:10m / 1:50m, admin-1, point-of-view borders | Public domain | Yes | Yes | |
| OpenHistoricalMap | CC0 by default; some features CC BY / CC BY-SA | Yes (CC0 features) | Yes | Filter by `license=*` tag; credit "© OpenHistoricalMap contributors" |
| CShapes 2.0 (ETH Zurich) | CC BY-NC-SA 4.0 | No | Yes (non-commercial, share-alike) | Derived files must stay CC BY-NC-SA |
| historical-basemaps (aourednik) | GPL-3.0 | No | Yes (copyleft) | Derived files stay GPL; provenance uneven before 1800 |
| Thenmap | No licence stated | No | No | Until written terms exist |
| Protomaps basemap (self-hosted PMTiles) | ODbL (OSM data), styles CC0, code BSD-3 | Sign-off needed | Yes | Visible "© OpenStreetMap"; self-host |
| MapLibre GL JS | BSD-3 | Yes | Yes | |
| Natural Earth rasters (shaded relief, hypsometric tints) | Public domain | Yes | Yes | ~1.85 km/px |
| NASA Blue Marble Next Generation | NASA: CC0 / not subject to US copyright | Yes | Yes | 500 m/px; credit "NASA Earth Observatory"; no implied endorsement |
| NASA Black Marble (VIIRS night lights 2012, 2016) | NASA CC0 | Yes | Yes | 500 m/px |
| NASA GIBS (as download source for NASA layers) | Per layer, NASA CC0 | Yes | Yes | Acknowledge GIBS; `Reference_*` label layers not checked |
| Landsat (USGS) | Public domain | Yes | Yes | 30 m; build own mosaic |
| Copernicus Sentinel-2 scenes | Copernicus free, full and open | Yes | Yes | Required: "Contains modified Copernicus Sentinel data [year]" |
| Copernicus DEM GLO-90 / GLO-30 | ESA licence, commercial allowed, pass-through conditions | Yes | Yes | Long mandatory credit + disclaimer; bind redistributees |
| CDSE Sentinel-2 quarterly mosaics | Portal content non-commercial; status of mosaics unclear | No | No | Until written confirmation |
| EOX Sentinel-2 cloudless 2018–2025 | CC BY-NC-SA 4.0 | No | Yes (non-commercial, share-alike) | |
| EOX Sentinel-2 cloudless 2016 | CC BY 4.0, but only reachable via non-commercial WMTS | No | No | Unless EOX provides a download in writing |
| USGS world geologic provinces | Public domain | Yes | Yes | |
| Maus et al. mining polygons | CC BY-SA 4.0 | Sign-off needed | Yes (share-alike) | |
| Eurostat searoute sea lanes | EUPL 1.2; upstream ORNL network unlicensed | No | Check upstream first | |

### Energy

| Source | Licence | Base | Layer | Notes |
|---|---|---|---|---|
| Global Energy Monitor trackers (oil and gas pipelines, LNG terminals, extraction fields) | CC BY 4.0 | Yes | Yes | Route geometry via download form (GeoJSON/GPKG) |
| US EIA international data, chokepoint volumes | US public domain | Yes | Yes | No EIA logo; repeat "Vortexa" source note on chokepoint figures |
| EDF OGIM (refineries, facilities) | CC BY 4.0 | Yes | Yes | Aggregates many sources; spot-check refinery rows |
| CEPII BACI bilateral trade | Etalab Open Licence 2.0 | Yes | Yes | Built from UN Comtrade; record version and update date in credit |
| World Bank / IMF shipping traffic density | CC BY 4.0 | Yes | Yes | 500 m raster, 2015–2021 |
| OPEC Annual Statistical Bulletin | Non-commercial reproduction allowed | No | Yes (non-commercial) | |
| UNdata energy statistics | "May be copied freely… provided UNdata is cited" | Probably | Yes | Back-up to EIA |
| Energy Institute Statistical Review (and OWID energy series derived from it) | Quotes allowed; extensive reproduction needs permission; S&P data prohibited | No | Single cited figures only | Trade-movement matrices excluded |
| IEA World Energy Balances | Paid licence for derived products | No | No | |
| UN Comtrade | Redistribution prohibited | No | No | |
| IMF PortWatch | IMF terms (see below) | No | Verify redistribution first | |
| JODI | No data licence | No | No | |

### Finance and debt

| Source | Licence | Base | Layer | Notes |
|---|---|---|---|---|
| World Bank International Debt Statistics | CC BY 4.0 | Yes | Yes | Creditor breakdown incl. China |
| BIS banking statistics (LBS, CBS) and total credit | Unrestricted with citation; not behind a paywall or extra charge | Yes | Yes | Never put BIS data behind a paywall |
| US Treasury TIC foreign holders | Public domain / CC0 | Yes | Yes | Custodial basis inflates Cayman, Belgium, Luxembourg |
| Eurostat | CC BY 4.0 (check third-party datasets) | Yes | Yes | |
| OECD data | CC BY 4.0 by default | Likely; verify by hand | Yes | Terms page blocks automated reading |
| AidData Chinese development finance 3.0 | ODC-By (project data); ODbL (OSM-derived geometry) | Yes (project data) | Yes | |
| IMF data (CPIS, Global Debt Database, WEO) | Commercial reuse needs permission; bulk download needs permission | No | Verify redistribution terms first | Only bilateral bond-holdings source; would fill the biggest debt gap |

### Resources and trade

| Source | Licence | Base | Layer | Notes |
|---|---|---|---|---|
| USGS Mineral Commodity Summaries | CC0 / public domain | Yes | Yes | 90 commodities, country production and reserves |
| USGS MRDS mine locations | Public domain | Yes | Yes | Stale (no updates since 2011) |
| FAOSTAT | CC BY 4.0, no use in commercial promotion | Yes | Yes | Not in ads or marketing |
| OECD export restrictions on raw materials | CC BY 4.0 by default | Likely; verify by hand | Yes | |
| BGS World Mineral Statistics | Non-commercial academic and research use only | No | No | Not an academic project |

### Conflict

| Source | Licence | Base | Layer | Notes |
|---|---|---|---|---|
| UCDP | CC BY 4.0 | Yes | Yes | |
| DeepStateMap | Visual materials free with credit; data copies prohibited; API needs approval | No | Credited screenshots only; data needs written approval | |
| ISW / Critical Threats | Brief excerpts only; everything else needs permission | No | Only with written permission on file | |
| ACLED | Redistribution prohibited without corporate licence | No | No | |
