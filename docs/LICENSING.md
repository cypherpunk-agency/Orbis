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
| `naturalearth` | Natural Earth: 1:110m countries (`data/world.js`), 1:50m countries (`data/world50.json`), 1:10m admin-1 (`data/geo/admin1/`), disputed areas (`data/geopolitics/pov.json`), rivers (`data/geopolitics/rivers.json`), date line (`data/statistics/dateline.json`) | Base | Public domain | Commercial | Optional; "Made with Natural Earth" |
| `d3` | D3 7.9.0 | Base | ISC | Commercial | Keep licence notice |
| `topojson` | topojson-client 3.1.0 | Base | ISC | Commercial | Keep licence notice |
| `fonts` | Source Serif 4, Barlow Semi Condensed | Base | SIL OFL 1.1 | Commercial | None for web use |
| `nasa-bluemarble` | NASA Blue Marble Next Generation, 4096×2048 texture via GIBS (`data/tex/satellite-4096.webp`) | Base | NASA open data (CC0) | Commercial | "NASA Earth Observatory"; acknowledge GIBS; no implied endorsement |
| `nasa-blackmarble` | NASA Black Marble 2016 night lights, 4096×2048 texture via GIBS (`data/tex/night-4096.webp`) | Base | NASA open data (CC0) | Commercial | "NASA Earth Observatory / NASA GSFC"; acknowledge GIBS |
| `nasa-relief` | NASA Blue Marble shaded relief + bathymetry, 4096×2048 via GIBS (`data/tex/terrain-4096.webp`) | Base | NASA open data (CC0) | Commercial | "NASA Earth Observatory"; acknowledge GIBS |
| `eia-intl` | US EIA international energy data, 2000–2024 (`data/energy/eia.json`) | Layer | US public domain | Commercial | "Source: U.S. Energy Information Administration"; no EIA logo |
| `eia-chokepoints` | EIA World Oil Transit Chokepoints, typed in (`data/energy/chokepoints.json`) | Layer | US public domain | Commercial | EIA, plus "based on Vortexa tanker tracking" |
| `baci` | CEPII BACI HS2017 V202601, trade 2021–2024 in energy, minerals, crops (`data/energy/trade.json`, `data/resources/trade.json`, `data/tradewar/sectors.json`) | Layer | Etalab Open Licence 2.0 | Commercial | CEPII BACI, version and update date; built from UN Comtrade |
| `usgs-mcs` | USGS Mineral Commodity Summaries 2026 data release (`data/resources/usgs.json`) | Layer | US public domain (CC0) | Commercial | "Source: U.S. Geological Survey" |
| `faostat` | FAOSTAT crop production 2000–2024 (`data/resources/fao.json`) | Layer | CC BY 4.0 | Commercial (not in commercial promotion) | FAO citation incl. access date; no implied endorsement |
| `imf-weo` | IMF WEO Oct 2026 government debt and GDP; Global Debt Database household/corporate debt, via DataMapper API, 6 requests (`data/finance/imf.json`) | Layer | IMF terms: reuse and redistribution with attribution; commercial reuse needs permission; no bulk automated download | **Non-commercial** | "Source: IMF …"; labelled non-commercial in the UI |
| `us-tic` | US Treasury TIC major foreign holders, December 2005–2025 (`data/finance/tic.json`) | Layer | US public domain | Commercial | Courtesy credit; custodial caveat in notes |
| `bis-cbs` | BIS consolidated banking statistics, Q4 2008–2025 (`data/finance/bis.json`) | Layer | BIS terms: unrestricted with citation, no paywall or extra charge | Commercial | "Source: BIS"; never behind a paywall |
| `wb-ids` | World Bank International Debt Statistics 2000–2024 (`data/finance/ids.json`, `ids_series.json`) | Layer | CC BY 4.0 | Commercial | "Source: World Bank, International Debt Statistics" |
| `wb-wdi` | World Development Indicators for the country atlas (`data/atlas/`); each indicator's licence is read from World Bank metadata at build time and only CC BY 4.0 ones are kept (e.g. SIPRI-sourced military spending is excluded) | Layer | CC BY 4.0 | Commercial | "Source: World Bank, World Development Indicators" |
| `wb-wgi` | Worldwide Governance Indicators (`data/atlas/`) | Layer | CC BY 4.0 (per metadata, checked at build) | Commercial | "Source: World Bank, Worldwide Governance Indicators" |
| `ghsl-pop` | GHSL GHS-POP R2023A population grid, epoch 2025, aggregated to 2048×1024 density (`data/grids/popdensity*`) | Layer | CC BY 4.0 (EC Decision 2011/833/EU) | Commercial | "European Commission, JRC: GHS-POP R2023A"; changes indicated |
| `nasa-gistemp` | NASA GISTEMP v4 temperature anomaly, decadal means 1880s–2020s + 2025 (`data/grids/warming*`) | Layer | NASA open data (no restrictions) | Commercial | "GISTEMP Team, 2026, NASA GISS" + Lenssen et al. 2024 |
| `noaa-gfs` | NOAA GFS 250 hPa winds, 2026-10-13 12 UTC (`data/grids/wind*`) | Layer | US public domain | Commercial | "NOAA/NCEP GFS"; no implied endorsement |
| `eurostat` | Eurostat regional statistics: population, GDP per inhabitant, Census 2021 country of birth for AT/DE (`data/regions/austria.json`, `germany.json`) | Layer | CC BY 4.0 (Eurostat reuse policy) | Commercial | "Source: Eurostat" with dataset codes |
| `us-census` | US Census Bureau population estimates Vintage 2025, ACS 2024 1-year median household income (`data/regions/usa.json`); goods trade by partner country, monthly FT-900 (`data/tradewar/`) | Layer | US public domain | Commercial | "Source: U.S. Census Bureau" |
| `us-treasury-fiscal` | Monthly Treasury Statement: customs duties, federal receipts (`data/tradewar/customs.json`) | Layer | US public domain; Fiscal Data allows commercial and non-commercial reuse | Commercial | "Source: U.S. Treasury, Monthly Treasury Statement" |
| `usitc` | USITC Table 1: imports, duties collected, ratio 1891–2025 (`data/tradewar/tariff_long.json`) | Layer | US public domain (17 USC 105) | Commercial | "Source: U.S. International Trade Commission" |
| `us-fedreg` | Federal Register proclamations, executive orders and USTR notices on tariffs, hand-compiled with citations (`data/tradewar/legal.json`, tariff-rate datasets) | Layer | US government work, public domain | Commercial | "Source: Federal Register" |
| `us-courts` | Court opinions quoted in the trade-war series | Layer | US government work, public domain | Commercial | Court names |
| `ustr` | USTR reciprocal-tariff methodology, Section 301 notices, deal announcements (`data/tradewar/tw_rates.json`, `tw_deals.json`) | Layer | US government work, public domain | Commercial | "Source: USTR" |
| `whitehouse` | White House fact sheets and joint statements on trade deals (`data/tradewar/tw_deals.json`) | Layer | US government work, public domain | Commercial | "Source: whitehouse.gov" |
| `us-cbp` | CBP CSMS messages on tariff collection dates | Layer | US government work, public domain | Commercial | "Source: U.S. Customs and Border Protection" |
| `kummu-gdp` | Kummu et al. 2025 subnational GDP per capita (PPP), Zenodo 18429133 (`data/regions/india_gdp.json`) | Layer | CC BY 4.0 | Commercial | Cite paper (Sci Data 12:178) and Zenodo record |
| `gcp-co2` | Global Carbon Budget 2025 national fossil CO2, 1950–2024, per person, cumulative since 1850 (`data/statistics/co2.json`) | Layer | CC BY 4.0 | Commercial | "Global Carbon Project, Global Carbon Budget 2025"; dataset DOI |
| `un-wpp` | UN World Population Prospects 2024, life expectancy 1950–2023 (`data/statistics/life-expectancy*.json`) | Layer | CC BY 3.0 IGO | Commercial | UN DESA Population Division (2024), WPP 2024 |
| `iana-tz` | IANA tz database 2026c, standard offset vs sun time per country (`data/statistics/timezones.json`) | Layer | Public domain | Commercial | Optional |
| `cia-factbook` | CIA World Factbook "Independence" field via factbook.json archive (`data/rights/independence.json`) | Layer | US public domain (archive CC0) | Commercial | "Source: CIA World Factbook"; no CIA seal |
| `amnesty-dp` | Amnesty International death penalty reports (end-2025 status, 2025 executions, 2008 abolition list), facts typed in (`data/rights/death_penalty.json`) | Layer | Reports CC BY-NC-ND 4.0; only facts used | **Non-commercial** (cautious) | "Source: Amnesty International …" |
| `ipu-suffrage` | IPU Women's Suffrage world chronology, years typed in (`data/rights/suffrage.json`) | Layer | IPU terms: non-commercial with acknowledgement; only facts used | **Non-commercial** (cautious) | "Source: Inter-Parliamentary Union" |
| `economist-bigmac` | The Economist Big Mac index 2000–2026: dollar price, raw and GDP-adjusted index (`data/economics/bigmac.json`) | Layer | CC BY 4.0 (Economist-generated data only; exchange rates and IMF GDP not shipped) | Commercial | "Source: The Economist, Big Mac index" |
| `ecdc-covid` | ECDC daily COVID-19 cases worldwide to 14 Dec 2020, month of first reported case (`data/people/covid-first.json`) | Layer | CC BY 4.0 | Commercial | ECDC acknowledgement text; modifications stated; no ECDC logo |
| `owid-covid` | Our World in Data COVID-19, deaths per million to end-2022, from WHO data (`data/people/covid-deaths.json`) | Layer | CC BY 4.0 (OWID); WHO data CC BY 4.0 + WHO terms | Commercial | "Our World in Data, based on WHO"; no misrepresentation |
| `usgs-quakes` | USGS ANSS ComCat, earthquakes M≥6 1900–2025 (`data/events/earthquakes.json`) | Layer | US public domain; ~47% of events (mostly pre-1973) from ISC-GEM, **CC BY-SA 3.0** (derived file shares alike) | Commercial | USGS credit + "ISC-GEM Catalogue © ISC and GEM Foundation, CC BY-SA 3.0" |
| `ucdp-ged` | UCDP GED 26.1 + Candidate events to Aug 2026, events and best-estimate deaths per 0.25° cell and month, Ukraine/Syria/Sudan (`data/events/conflict-*.json`) | Layer | CC BY 4.0 | Commercial | Cite Davies, Pettersson & Öberg (2026); Sundberg & Melander (2013); Hegre et al. (2020) |
| `cshapes` | CShapes 2.0 (ETH Zurich ICR), state borders incl. dependencies, snapshots 1886–2019 (`data/history/borders.json` index + `borders-<year>.json`) | Layer | CC BY-NC-SA 4.0 (derived files stay CC BY-NC-SA 4.0) | **Non-commercial** | "CShapes 2.0, Schvitz et al. 2022, ETH Zurich ICR"; share-alike |
| `orbis-schematic` | Drawn by Orbis: pipelines, sea lanes, terminals, refineries (`data/energy/infrastructure.json`), South China Sea claims and 200-nm lines (`data/geopolitics/south-china-sea.json`), container lanes (`data/economics/shipping-lanes.json`), historical journeys and routes (`data/people/journeys.json`, `silk-road.json`, `out-of-africa.json`) | Layer | Own work | Commercial | Marked as schematic |
| `editorial` | Rounded figures typed into stories, with citations in each dataset note (`data/legacy/`, `data/economics/ports.json`, `data/statistics/worldcup2026.json`, `data/regions/india.json`) | Layer | Facts (not copyrightable); cited in each story's notes | Commercial | Sources named in story notes |

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
