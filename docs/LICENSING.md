# Licensing policy

## The rule: two tiers

| Tier | What it covers | Licence requirement |
|---|---|---|
| **Base** | The map itself and the engine: country geometry, basemap imagery, borders, code libraries, fonts, anything every story depends on | **Must allow commercial use.** Copyleft or share-alike (GPL, CC BY-SA, ODbL) needs explicit sign-off. |
| **Story layer** | Optional data shown inside a story or as a switchable overlay; the site works without it | **Any licence**, including non-commercial or used-with-permission, **provided the files may be published in a public open-source repository.** |

Excluded at every tier: terms that forbid redistribution, unclear or missing terms, and "ask us" terms without a written grant on file.

### Obligations for every source
1. **Register it** in `js/sources.js` (tier, licence, use, credit) and add a row to the register below using its id in backticks.
2. **Label it in the UI.** Every story and scene lists its sources with their licence in the "Data" line under the story. Each chip carries licence-element badges read from the licence: **PD** / **CC0** (no rights reserved), **BY** (attribution), **SA** (share-alike), **NC** (non-commercial), **ND** (no derivatives), **PERM** (used with permission). Share-alike sources get a teal dot, non-commercial and permission-only sources an orange one. Tapping a chip opens the full register at that source, with the full licence name and a link to its text.
3. **Keep it switchable.** A story layer must never be needed for the base map to work.
4. **Run the check:** `node tools/check-licences.js` fails if a source is unregistered, undocumented, has a base-tier source without commercial rights, cannot be published, or has a `use` that contradicts its licence text.

### `use` values in `js/sources.js`
| `use` | Meaning | Examples |
|---|---|---|
| `commercial` | Commercial use allowed, no share-alike | Public domain, CC0, CC BY, CC BY-IGO |
| `sharealike` | Commercial use allowed, but adaptations must keep the same licence | CC BY-SA, GPL, ODbL |
| `noncommercial` | No commercial use | CC BY-NC, CC BY-NC-SA, CC BY-NC-ND, custom non-commercial terms |
| `permission` | Used under a written grant (needs a `grant` reference) | — |

> Non-commercial layers stay non-commercial wherever they appear. If the site is ever monetised (ads, paid tiers, client work), those layers must be removed, licensed, or kept off the commercial surface.

## Register (sources in use)

| Id | Source | Tier | Licence | Use | Credit |
|---|---|---|---|---|---|
| `naturalearth` | Natural Earth: 1:110m countries (`data/world.js`), 1:50m countries (`data/world50.json`), 1:10m admin-1 (`data/geo/admin1/`), disputed areas (`data/geopolitics/pov.json`; the UN view rules in `data/geopolitics/un-view.json` are Orbis editorial, citing UN resolutions), rivers (`data/geopolitics/rivers.json`), date line (`data/statistics/dateline.json`) | Base | Public domain | Commercial | Optional; "Made with Natural Earth" |
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
| `wb-wdi` | World Development Indicators for the country atlas (`data/atlas/`) and aviation indicator IS.AIR.DPRT (`data/people/empty-skies.json`); each indicator's licence is read from World Bank metadata at build time: CC BY/CC0 go here, non-commercial or share-alike ones under `wb-wdi-nc`, and indicators whose terms restrict redistribution (e.g. SIPRI military spending) are excluded | Layer | CC BY 4.0 | Commercial | "Source: World Bank, World Development Indicators" |
| `wb-wgi` | Worldwide Governance Indicators (`data/atlas/`) | Layer | CC BY 4.0 (per metadata, checked at build) | Commercial | "Source: World Bank, Worldwide Governance Indicators" |
| `wb-wdi-nc`, `wb-wgi-nc` | Atlas indicators whose World Bank metadata names a non-commercial or share-alike licence; shown with an "NC" badge | Layer | Per indicator (e.g. CC BY-NC 4.0) | Non-commercial | As named per indicator |
| `whalinghistory` | American Offshore Whaling Voyages (2026-06-19) and Logbook Data (2025-09-16), whalinghistory.org (`data/history/whales.json`, `data/grids/whales*`) | Layer | CC BY 4.0 (download page + package readme) | Commercial | "whalinghistory.org: New Bedford Whaling Museum, Nantucket Historical Association, Mystic Seaport Museum" |
| `gcat` | GCAT release 1.8.8, data update 2026-10-13, J. McDowell (`data/statistics/launches.json`) | Layer | CC BY (stated on planet4589.org/space/gcat) | Commercial | "Data from GCAT (J. McDowell, planet4589.org/space/gcat)" |
| `itinere` | Itiner-e Roman roads, static version 2024 (Zenodo 17122148) (`data/history/roman-roads*.json`) | Layer | CC BY 4.0 | Commercial | "Itiner-e: de Soto, Pažout, Brughmans et al. (2025)" |
| `pleiades` | Pleiades gazetteer, city locations (`data/history/roman-roads-named.json`) | Layer | CC BY 3.0 US | Commercial | "Pleiades gazetteer, pleiades.stoa.org" |
| `coldat` | COLDAT V3, doi:10.7910/DVN/T9SDEW (`data/rights/colonies.json`) | Layer | CC0 1.0 | Commercial | "Becker, COLDAT, Harvard Dataverse" |
| `unhcr` | UNHCR refugee statistics, end-year stocks 2000–2025 (`data/people/refugees*.json`) | Layer | CC BY-IGO 3.0 (UNHCR's HDX dataset) | Commercial | "UNHCR Refugee Population Statistics Database" |
| `iom-mmp` | IOM Missing Migrants Project 2014–2024 (`data/events/missing-migrants.json`) | Layer | CC BY-IGO 3.0 (IOM's HDX dataset) | Commercial | "IOM Missing Migrants Project" |
| `niva-netmigration` | Niva et al. 2023 net migration 2000–2019, Zenodo 7997134 (`data/grids/netmigration*`, `data/people/net-migration*.json`) | Layer | CC BY 4.0 | Commercial | "Niva et al. (2023), Nature Human Behaviour" |
| `undp-hdr` | UNDP Human Development Report 2025 composite indices, 1990–2023 (`data/atlas/HDR.*.json`) | Layer | CC BY 3.0 IGO | Commercial | "Source: UNDP, Human Development Report 2025" |
| `pwt` | Penn World Table 11.0, 1950–2023 (`data/atlas/PWT.*.json`) | Layer | CC BY 4.0 | Commercial | "Feenstra, Inklaar and Timmer, Penn World Table 11.0, GGDC" |
| `ember` | Ember yearly electricity data, 1985–2025 (`data/atlas/EMBER.*.json`); demand per person uses World Bank population (`wb-wdi`) | Layer | CC BY 4.0 | Commercial | "Source: Ember" |
| `unesco-uis` | UNESCO UIS public data API, February 2026 release (`data/atlas/UIS.*.json`) | Layer | CC BY-SA 4.0 (share-alike) | Share-alike | "Source: UNESCO Institute for Statistics" |
| `meta-sci` | Meta Social Connectedness Index, country level, HDX release (snapshot 25 Jan 2026) (`data/people/sci.json`) | Layer | CC0 1.0 (HDX licence field) | Commercial | "Meta Social Connectedness Index, via HDX" |
| `bhht` | Cross-verified database of notable people 3500 BC–2018, doi:10.21410/7E4/RDAG3O (`data/people/fame-*.json`, `data/grids/fame*`) | Layer | CC BY-NC-SA 4.0 (shipped LICENSE.txt; the record page says CC BY-SA 4.0, stricter followed) | Non-commercial, share-alike | "Laouenan et al. (2022), Scientific Data" |
| `historical-basemaps` | historical-basemaps by A. Ourednik, commit da7a4b7 (`data/history/rome-hb-*.json`, `data/history/hre-outline.json`, `data/history/royals-realms.json`, `data/history/col-empires-hb.json`, `data/history/col-area.json`) | Layer | GPL-3.0 (derived files stay GPL-3.0) | Share-alike | "historical-basemaps by André Ourednik"; borders approximate |
| `awmc` | AWMC geodata, commit 7ecf8bc (`data/history/rome-awmc.json`) | Layer | ODbL 1.0 (derived data stays ODbL; kept separate from GPL files) | Share-alike | "Ancient World Mapping Center, UNC" |
| `wp-ua-control` | Wikipedia Module:Russo-Ukrainian war detailed/overview map, 12 dated revisions (`data/history/ua-control*.json`) | Layer | CC BY-SA 4.0 (derived files stay CC BY-SA) | Share-alike | "Wikipedia contributors"; areas are an Orbis approximation (Voronoi cells around settlements) |
| `newberry-ahcb` | Newberry AHCB US historical states and territories (`data/history/us-states.json`, `us-acquisitions.json`, `us-union.json`) | Layer | Open access ("any lawful purpose, commercial or non-commercial") | Commercial | "Atlas of Historical County Boundaries, The Newberry Library" |
| `usfs-royce` | USFS Tribal Land Cessions (Royce 1899, 2018 digitisation) (`data/history/us-cessions.json`) | Layer | CC BY 4.0 (catalog.data.gov licence field) | Commercial | "USDA Forest Service ... after C. C. Royce (1899)" |
| `medsl-president` | MEDSL U.S. President 1976–2024, v10 (`data/history/us-elections.json`; US popular vote in `data/elections/`) | Layer | CC0 1.0 | Commercial | "MIT Election Data and Science Lab" |
| `parlgov` | ParlGov 2024 Release, lower-house elections 1945–2023 (`data/elections/`) | Layer | CC0 1.0 | Commercial | "Döring & Manow, ParlGov" |
| `princes-townspeople` | Princes and Townspeople vols. 1–2 (Harvard Dataverse): town rulers 1300–1807 (`data/history/hre-rulers.json`, `hre-ruler-counts.json`) and town areas (`data/geo/regions/hre-cities.json`) | Layer | CC0 1.0 | Commercial | "Princes and Townspeople, Cantoni, Mohr, Weigand" |
| `histogis-circles` | HistoGIS Imperial Circles 1648 and 1792 (A. Piechl after A. Kunz, IEG-Maps) (`data/history/hre-circles.json`) | Layer | CC BY 4.0 per HistoGIS; treated as BY-NC (traced from IEG-Maps, whose own terms are personal use / CC BY-NC) | Story layer only (NC badge) | "A. Piechl, HistoGIS (ÖAW), after A. Kunz, IEG-Maps" |
| `eth-hre-territories` | ETH Zurich, Roller 2021, HRE territories in the 16th century (`data/history/hre-territories-1500s.json`) | Layer | CC BY-NC-SA 4.0 (derived file stays BY-NC-SA) | Story layer only (NC badge) | "Ramona Roller, ETH Zurich" |
| `wikidata` | Wikidata SPARQL: monarchs of England/GB/UK with reign starts and house (`data/history/royals-england.json`); form of government (`data/politics/forms.json`); national elections since 1945 (`data/elections/`) | Layer | CC0 1.0 | Commercial | "Wikidata (CC0)"; volunteer-edited, cross-checked against Wikipedia lists |
| `vdem` | V-Dem v16 Regimes of the World 1900–2025 via OWID grapher (`data/politics/regimes.json`, `regime_counts.json`; rules in `forms.json`) | Layer | CC BY-SA 4.0 (v-dem.net; OWID mislabels it CC BY); derived files stay CC BY-SA | Share-alike | "V-Dem v16, Regimes of the World (Lührmann et al. 2018), via Our World in Data" |
| `eog-vnl` | EOG VIIRS Nighttime Lights annual VNL V2 2012–2024 via Zenodo mirror 17294744 (`data/grids/lights*`, `data/planet/lights.json`) | Layer | CC BY 4.0 | Commercial | "This product was made utilizing VIIRS Nighttime Lights data produced by the Earth Observation Group, Payne Institute for Public Policy, Colorado School of Mines" |
| `opensky-covid` | OpenSky Network COVID-19 flight list, Zenodo 5815448 v21.12 (`data/statistics/flights*.json`) | Layer | CC BY 4.0 | Commercial | "OpenSky Network; Strohmeier et al., ESSD 13, 2021" |
| `ourairports` | OurAirports airports.csv, airport-to-country lookup for the flight data | Layer | Public domain | Commercial | Optional |
| `shepherd-1648-utexas` | Shepherd, Historical Atlas (1923/1926), plate "Central Europe about 1648", UT Austin scan, warped by Orbis (`data/overlays/hre-1648-shepherd.*`) | Layer | Public domain (US publication before 1931; UT Libraries: "No permissions are needed"; Commons: PD Old) | Commercial | "University of Texas Libraries" |
| `ghsl-pop` | GHSL GHS-POP R2023A population grid, epoch 2025, aggregated to 2048×1024 density (`data/grids/popdensity*`) | Layer | CC BY 4.0 (EC Decision 2011/833/EU) | Commercial | "European Commission, JRC: GHS-POP R2023A"; changes indicated |
| `nasa-gistemp` | NASA GISTEMP v4 temperature anomaly, decadal means 1880s–2020s + 2025 (`data/grids/warming*`) | Layer | NASA open data (no restrictions) | Commercial | "GISTEMP Team, 2026, NASA GISS" + Lenssen et al. 2024 |
| `noaa-gfs` | NOAA GFS 250 hPa winds, 2026-10-13 12 UTC (`data/grids/wind*`) | Layer | US public domain | Commercial | "NOAA/NCEP GFS"; no implied endorsement |
| `eurostat` | Eurostat regional statistics: population, GDP per inhabitant, Census 2021 country of birth for AT/DE (`data/regions/austria.json`, `germany.json`); selected 2023 EU NUTS 2 GDP/head PPS comparison (`data/history/eu/regions.json`, `nama_10r_2gdp`) | Layer | CC BY 4.0 (Eurostat reuse policy) | Commercial | "Source: Eurostat" with dataset codes; frozen 2025-02-11 release for EU comparison, region locators rather than statistical-boundary polygons |
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
| `usgs-quakes` | USGS ANSS ComCat, earthquakes M≥6 1900–2025 (`data/events/earthquakes.json`) | Layer | US public domain; ~47% of events (mostly pre-1973) from ISC-GEM, **CC BY-SA 3.0** (derived file shares alike) | Share-alike (ISC-GEM part) | USGS credit + "ISC-GEM Catalogue © ISC and GEM Foundation, CC BY-SA 3.0" |
| `ucdp-ged` | UCDP GED 26.1 + Candidate events to Aug 2026, events and best-estimate deaths per 0.25° cell and month, Ukraine/Syria/Sudan (`data/events/conflict-*.json`) | Layer | CC BY 4.0 | Commercial | Cite Davies, Pettersson & Öberg (2026); Sundberg & Melander (2013); Hegre et al. (2020) |
| `cshapes` | CShapes 2.0 (ETH Zurich ICR), state borders incl. dependencies, snapshots 1886–2019 (`data/history/borders.json` index, `data/history/col-empires-cs.json` + `borders-<year>.json`) | Layer | CC BY-NC-SA 4.0 (derived files stay CC BY-NC-SA 4.0) | **Non-commercial** | "CShapes 2.0, Schvitz et al. 2022, ETH Zurich ICR"; share-alike |
| `orbis-schematic` | Drawn by Orbis: pipelines, sea lanes, terminals, refineries (`data/energy/infrastructure.json`), South China Sea claims and 200-nm lines (`data/geopolitics/south-china-sea.json`), container lanes (`data/economics/shipping-lanes.json`), historical journeys and routes (`data/people/journeys.json`, `silk-road.json`, `out-of-africa.json`) | Layer | Own work | Commercial | Marked as schematic |
| `nasa-night-change` | NASA Black Marble paired reprocessed 2012/2016 colour display composites (`data/grids/night-light-change*`), from NASA's flat-map downloads | Layer | NASA imagery, public use with credit ([NASA media guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/)) | Commercial; no endorsement or logo use | NASA Earth Observatory / NASA GSFC; Orbis resizing and WebP compression disclosed; display imagery is not calibrated radiance |
| `rome-mitchell1880` | Mitchell 1880 Roman Empire atlas scan, Rumsey identifier 0586.072 (`data/history/rome/mitchell1880.webp`) | Layer | [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/), following [Rumsey terms](https://www.davidrumsey.com/about/copyright-and-permissions) | **Non-commercial** | David Rumsey Map Collection, David Rumsey Map Center, Stanford University Libraries; Orbis georeferencing, inset masking and compression; approximate interpretation, derived image retains licence |
| `eu-budget` | European Commission spending and revenue workbook, 2000–2025; selected observations (`data/history/eu/budget.json`) | Layer | [CC BY 4.0 under Commission reuse policy](https://commission.europa.eu/legal-notice_en), unless individually marked otherwise | Commercial | European Commission; Orbis subset and derived differences disclosed; allocated expenditure and contributions are defined in chapter notes |
| `nasa-ukraine-lights` | NASA Kyiv monthly night-light display composites, January/March/May 2022 (`data/history/ukraine/kyiv-lights-*.webp`) | Layer | NASA imagery, public use with credit ([media guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/)) | Commercial; no endorsement | NASA Earth Observatory / Joshua Stevens; Black Marble data Ranjay Shrestha / NASA GSFC; Orbis WebP compression; display imagery, no calibrated radiance or control-area inference |
| `us-army-atlas` | US Army Center of Military History maps, American Military History (1989), UT Library scans; Northern Europe 1944–1945 and Pacific Areas 1 August 1942 (`data/history/ww2/`) | Layer | US federal government public domain; [UT reuse FAQ](https://maps.lib.utexas.edu/maps/faq.html), [primary catalogue/publisher](https://maps.lib.utexas.edu/maps/historical/history_ww2.html) | Commercial | Courtesy University of Texas Libraries, The University of Texas at Austin; Orbis approximate georeferencing/compression; Pacific command areas must not be described as occupation |
| `hre-reilly1796` | Reilly/Benedicti 1796 Karte von der Deutschland, [Rumsey catalogue](https://www.davidrumsey.com/luna/servlet/detail/RUMSEY~8~1~278984~90052027) (`data/history/hre/`) | Layer | [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/) following [Rumsey terms](https://www.davidrumsey.com/about/copyright-and-permissions) | **Non-commercial** | David Rumsey Map Collection, David Rumsey Map Center, Stanford University Libraries; Orbis approximate georeferencing/compression disclosed; derived scan retains licence |
| `hre-alphathon1789` | Creator-defined HRE membership and selected territorial SVG paths, [Map Holy Roman Empire 1789](https://commons.wikimedia.org/wiki/File:Map_Holy_Roman_Empire_1789.svg) (`data/history/hre/territories1789.json`) | Layer | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) | Commercial with share-alike obligations | Alphathon, 2021 revision Fenn-O-maniC, maix/base-map contributors; full inherited attribution in `data/history/hre/attribution.txt`; Orbis extraction/simplification/approximate transform; SVG title/original upload establish c. 1789 despite conflicting copied page summary; derived geometry retains licence |
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
