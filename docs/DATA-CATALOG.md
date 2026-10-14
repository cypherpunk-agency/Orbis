# Data catalogue

Where to look for data, what we have found, and what we have ruled out. This is the idea pool for new stories. Sources already in use are registered in `js/sources.js` and listed in [LICENSING.md](LICENSING.md); everything here is a **candidate** until it goes through that register.

**How to use it.** Before writing a story, check this file for data. Before using any entry, re-read the licence at the primary page (column "Check"), then register it as usual (`CLAUDE.md`). When you scout a new repository or dataset, add a row. When you rule one out, move it to [Ruled out](#ruled-out) with the reason.

**Licence check level.** **P** read at the publisher's own page or API · **S** publisher statement seen only via a search summary: re-read before use · **U** unverified.
**Verdict.** **C-OK** commercial use allowed (usable in the base) · **Story** story layers only (non-commercial, share-alike or custom terms, redistribution allowed) · **U** unverified · **X** unusable.

Last scouting pass: 13 October 2026.

## Repositories

Portals, catalogues and publishers to search. Licences are set per dataset in almost all of them: the portal's default is only a hint.

| Repository | Scope | Licences | Access | How to search well | Updates | Reliability |
|---|---|---|---|---|---|---|
| [Zenodo](https://zenodo.org) (CERN/OpenAIRE) | Everything; many paper supplements | Per record; CC BY 4.0 most common, also CC0, "other-nc" | REST API, no key. Send `Accept: application/vnd.inveniordm.v1+json` and read `metadata.rights[].id` (the plain API shows `license: None`) | Search the paper title or first author; check every version, licences can differ (OpenSky 2020: CC BY and NC versions) | Continuous | High, licence machine-readable |
| [Harvard Dataverse](https://dataverse.harvard.edu) | Social science, economics, agriculture, history | CC0 by default; some custom terms | `/api/search?type=dataset`, `/api/datasets/:persistentId/`; read `license` or `termsOfUse`; no key | Dataset name plus author; read `termsOfUse` when `license` is null | Continuous | High |
| Other Dataverses (Sciences Po, DANS) | Same | Per dataset; some DANS records are closed access | Dataverse API | — | — | Medium–high |
| [Figshare](https://figshare.com) | Paper supplements | Per article, often CC BY 4.0 | `api.figshare.com/v2/articles/{id}` → `license.name` | Look up the DOI suffix | — | High |
| [HDX](https://data.humdata.org) (UN OCHA) | Humanitarian, migration, Meta Data for Good | Per dataset: CC BY-IGO, CC0, or "Other" (text in `license_other`) | CKAN API `package_search`, `package_show`; no key | Filter by organisation (IOM, UNHCR, Meta); always read `license_other` | Often weekly | Metadata high; data as good as its provider |
| [data.europa.eu](https://data.europa.eu) | EU and national portals | Per dataset; many CC BY 4.0; Eurostat free reuse | `/api/hub/search/search?q=`; no key | Very noisy: filter by catalogue (Eurostat, JRC) | Daily harvest | Varies |
| [JRC Data Catalogue](https://data.jrc.ec.europa.eu) | GHSL, land, water | Mostly CC BY 4.0 | Direct download | Search by product code (GHS-UCDB, GHS-POP) | Yearly releases | High |
| [data.gov](https://data.gov) / data.nasa.gov | US federal | US government work usually public domain, but many records say "not specified" | CKAN API | "Not specified" means: check the original publisher | — | Metadata thin |
| [NASA Earthdata](https://earthdata.nasa.gov), GIBS, FIRMS | Satellite products | NASA open data policy; citation requested | Earthdata login for bulk; GIBS tiles open (already used) | Search by product short name (VIIRS, MODIS) | Near real time | High |
| [Copernicus CDS](https://cds.climate.copernicus.eu) / Data Space | ERA5, land, atmosphere, Sentinel | CC BY (CDS); Copernicus free and open | Account and API key | Use dataset ids (`reanalysis-era5-single-levels`) | Daily | High |
| [NOAA NCEI](https://www.ncei.noaa.gov) / ERDDAP | Oceans, storms, drifters, climate | Public domain or CC0 (ERDDAP metadata); IBTrACS under WMO policy | ERDDAP CSV/NetCDF, no login | `/info/` pages show the licence attribute | Continuous | High |
| [GBIF](https://www.gbif.org) | 4 bn species records | Per dataset: CC BY 4.0, CC BY-NC 4.0, CC0 | API, no key; bulk download needs a free account (gives a citable DOI) | `facet=license`; filter to CC0/CC BY for commercial-safe use | Continuous | High |
| [OBIS](https://obis.org) | 229 M marine records | Per dataset: CC0, CC BY, CC BY-NC | api.obis.org, no key | Filter by taxon or area | Continuous | High |
| [Our World in Data](https://ourworldindata.org) | Thousands of indicators | OWID's own work CC BY 4.0; third-party data keeps its licence | `/grapher/<slug>.csv` and `.metadata.json` | Use the metadata to find the upstream source and its licence | Continuous | High; best place to find sources |
| [Wikidata](https://www.wikidata.org) | People, places, events with dates and coordinates | CC0 | SPARQL endpoint, dumps | Property paths (P625 coordinates, P571 inception, P19 birthplace) | Live | Medium; check completeness |
| [Global Energy Monitor](https://globalenergymonitor.org) | Coal, gas, oil, nuclear, steel, power trackers | CC BY 4.0 unless noted (methane plumes CC BY-NC-SA) | Download forms ask for name and email | Per-tracker download pages | Twice a year | High |
| [Utrecht Yoda](https://public.yoda.uu.nl) | HYDE | Not readable (bot wall) | — | Try with a browser | — | Licence unverified |
| [Illinois Data Bank](https://databank.illinois.edu) | Cline Center coups | Per dataset | JSON endpoint failed | — | — | — |
| [Global Data Lab](https://globaldatalab.org) | Subnational HDI | Custom: non-profit only | Free download | — | Yearly | Medium–high |

The history, conflict and indicator sources named in the [history and atlas plan](PLAN-HISTORY-ATLAS.md) were checked in October 2026: see [the licence check below](#licence-check-history-conflicts-and-indicators-october-2026). Still to scout: national statistics offices.

## Candidate datasets

Story ideas are hooks to test against the data, not checked facts.

### History, historical demography and economy

| Dataset | Licence | Verdict | Contents | Size | Layer | Story idea |
|---|---|---|---|---|---|---|
| [Maddison Project 2023](https://www.rug.nl/ggdc/historicaldevelopment/maddison/releases/maddison-project-database-2023) | CC BY 4.0 (P) | C-OK | GDP per head and population, 169 countries, year 1–2022 | < 5 MB | choropleth + timeline | The Great Divergence: China and India as rich as Western Europe in 1700, far poorer by 1913 |
| HYDE 3.3/3.4 (Utrecht, PBL) | U | U | Gridded population, cropland, pasture, 10,000 BCE–2023 | GB | raster timeline | Farming eats the planet |
| Historical Urban Population 3700 BC–AD 2000 (Reba et al., SEDAC) | U | U | ~2,000 cities, year, population | < 1 MB | symbols + timeline | The biggest city on Earth moves from Uruk to Tokyo |
| [COLDAT colonial dates](https://doi.org/10.7910/DVN/T9SDEW) | CC0 (P) | C-OK | Colonial start/end by colonizer | < 1 MB | choropleth, categories | How long were you a colony? |
| [Seshat Equinox-2020](https://seshat-db.com/downloads_page) | CC BY-NC-SA (S); form | Story | Polities since the Neolithic: territory, population, complexity | ~10 MB | points + timeline | The rise of the megastates |
| [V-Dem v16](https://www.v-dem.net) | CC BY-SA 4.0 (P) | Story | 500+ democracy indicators, 1789–2025 | ~300 MB | choropleth + timeline | The autocratic tide |
| [Cline Center coups v2.2.2](https://clinecenter.illinois.edu/project/research-themes/democracy-and-development/coup-detat-project) | CC BY (S) | C-OK pending check | 1,161 coup events 1945–2026 | < 1 MB | events, choropleth | The coup belt |
| [Notable people 3500 BC–2018](https://doi.org/10.21410/7E4/YLG6YR) (Laouenan et al.) | CC BY-SA 4.0 (P) | Story | 2.3 M people, birth/death places and years | 3 GB raw | points, flows | Where fame was born |
| [Itiner-e Roman roads](https://zenodo.org/records/17122148) | CC BY 4.0 (P) | C-OK | ~300,000 km of roads with certainty grades | 264 MB | lines | All roads lead to Rome |
| [Pleiades](https://pleiades.stoa.org/downloads) | CC BY 3.0 (P) | C-OK | ~40k ancient places with periods | ~100 MB | points, labels | Base gazetteer for the ancient world |
| [Viabundus](https://zenodo.org/records/16611998) | CC BY-SA (S) | Story | Roads, towns, tolls, fairs, N. Europe 1350–1650 | tens of MB | lines, points | Hanseatic highways |
| [SlaveVoyages](https://www.slavevoyages.org) | CC BY-NC (S) | Story | ~36,000 voyages 1514–1866 | ~20 MB | flows | Most enslaved Africans were taken to Brazil, few to North America |
| [Whaling history](https://whalinghistory.org/participate/download/) | CC BY 4.0 (P; logbooks: check readme) | C-OK | Voyages and daily logbook positions 1700s–1920s | 50–100 MB | points, flows | Where the whales were |
| CLIWOC via ICOADS (NOAA) | U (DANS copy closed; ICOADS likely public domain) | U | 280k ship observations 1750–1854 | — | points, particles | Sailing the trade winds |

### Economy and trade

| Dataset | Licence | Verdict | Contents | Size | Layer | Story idea |
|---|---|---|---|---|---|---|
| [Harvard Growth Lab trade](https://doi.org/10.7910/DVN/T4CHWJ) | CC0 (P); upstream UN Comtrade | C-OK | Bilateral trade, SITC 1962–, HS 1995– | 16 GB raw | flows, choropleth | Who makes what: each country's top export. A CC0 alternative to BACI |

### Transport and mobility

| Dataset | Licence | Verdict | Contents | Size | Layer | Story idea |
|---|---|---|---|---|---|---|
| [OpenSky flight lists 2019–22](https://zenodo.org/records/5815448) | CC BY 4.0 (P); newer version NC | C-OK | One row per flight | 2.6–7 GB | flows, choropleth | The sky went quiet, 2020 |
| [OurAirports](https://ourairports.com/data/) | Public domain (P) | C-OK | ~80k airfields | 13 MB | points | Airstrips everywhere: Alaska and the Amazon |
| [OpenFlights](https://openflights.org/data.php) | ODbL + DbCL (P) | Story | 67k routes, frozen 2014 | 3 MB | flows | Hubs: Dubai and Istanbul |
| [GRIP roads](https://zenodo.org/records/6420961) | CC BY 4.0 (P) | C-OK | 21 M km of roads, density grids | 8 GB | raster | The roadless world |
| NGA World Port Index, ASAM piracy | US gov., no copyright (S) | C-OK | 3,700 ports; ship attacks since 1978 | small | points, events | Pirates moved |

### Energy and infrastructure

| Dataset | Licence | Verdict | Contents | Size | Layer | Story idea |
|---|---|---|---|---|---|---|
| [WRI Global Power Plant DB 1.3](https://github.com/wri/global-power-plant-database) | CC BY 4.0 (P) | C-OK | 35k plants (frozen 2021) | 10 MB | symbols by fuel | Coal on one side, water on the other |
| GEM Coal / Nuclear / Power trackers | CC BY 4.0 unless noted (S) | C-OK | Every coal unit ≥ 30 MW, incl. cancelled | — | points, spikes + timeline | Still building coal |
| Global Wind Atlas 3, Global Solar Atlas 2 | CC BY 4.0 (S) | C-OK | 250 m wind, 1 km solar grids | GB | raster | Sun belt, wind belt |
| [Global Dam Watch 1.0](https://doi.org/10.6084/m9.figshare.25988293) | CC BY 4.0 (P) | C-OK | 41k barriers, 35k reservoirs | 127 MB | points, polygons | Damming the world's rivers |

### Space and night

| Dataset | Licence | Verdict | Contents | Size | Layer | Story idea |
|---|---|---|---|---|---|---|
| [GCAT](https://planet4589.org/space/gcat/) (McDowell) | CC BY 4.0 (P) | C-OK | Every launch and object since 1957 | tens of MB | points, events, chart | The launch explosion |
| [CNEOS fireballs](https://cneos.jpl.nasa.gov/fireballs/) (NASA JPL) | none stated (S) | U | ~1,000 bolides since 1988 | < 1 MB | points, spikes | Explosions in the sky |
| Meteorite Landings (data.nasa.gov) | "not specified" (P) | U | 34,513 meteorites | small | points | Found in Antarctica and the Sahara |
| [VIIRS night lights v2.2](https://eogdata.mines.edu/products/vnl/) | CC BY 4.0 (P) | C-OK | 500 m annual radiance 2012–2024 | ~1 GB/yr | raster, before/after | Lights out, lights on |
| Falchi night-sky brightness atlas (GFZ) | CC BY-NC 4.0 (S) | Story | 30″ grid | 2.9 GB | raster | Who can still see the Milky Way? |

### Environment and climate

| Dataset | Licence | Verdict | Contents | Size | Layer | Story idea |
|---|---|---|---|---|---|---|
| Hansen/UMD Global Forest Change 1.12 | CC BY 4.0 (P) | C-OK | 30 m forest loss 2000–2024 | huge | raster timeline | The new deforestation frontiers |
| JRC Global Surface Water 1984–2024 | free, no restriction (P) | C-OK | 30 m water occurrence | huge | raster | Lakes that vanished, lakes that appeared |
| ERA5 (Copernicus CDS) | CC BY (P) | C-OK | Hourly reanalysis since 1940 | huge | raster, particles | The heat of 2023–24; could replace GFS for wind |
| Berkeley Earth | CC BY-NC 4.0 (P) | Story | Land temperatures since 1750 | — | raster | Probably not needed next to GISTEMP |
| IBTrACS v04 (NOAA) | WMO open policy (P) | C-OK | Every tropical cyclone since the 1840s | 300 MB | lines, events | Where storms never cross |
| NOAA Global Drifter Program | CC0 (S) | C-OK | 25k drifting buoys since 1979 | — | lines, particles | Message in a bottle |
| NSIDC Sea Ice Index | free with citation (S) | C-OK | Monthly sea-ice extent | small | polygons | Update to `arctic` |
| Randolph Glacier Inventory 7.0 | CC BY 4.0 (P) | C-OK | 274k glacier outlines | — | polygons, points | Glaciers outside the poles |
| NASA FIRMS | NASA open data (S) | C-OK | Active fires, near real time | — | points + timeline | Africa burns most |

### Biodiversity and oceans

| Dataset | Licence | Verdict | Contents | Layer | Story idea |
|---|---|---|---|---|---|
| GBIF occurrences | per dataset (P) | C-OK if filtered to CC0/CC BY | Species records | points, density | Where we look, not where life is |
| OBIS | per dataset (S) | as GBIF | Marine records | points, density | Sampling bias at sea; one species' range |
| Global Fishing Watch | CC BY-NC 4.0 (P); login; no scraping | Story | Fishing effort, vessel detections | raster | Distant-water fleets |

### Migration and people

| Dataset | Licence | Verdict | Contents | Layer | Story idea |
|---|---|---|---|---|---|
| UNHCR refugee statistics | CC BY 4.0 + supplemental terms (S) | C-OK | Origin–asylum stocks since 1951 | flows, choropleth | Refugees stay close |
| IOM Missing Migrants (HDX) | CC BY-IGO (P) | C-OK | Geolocated deaths since 2014 | points | The deadliest border is the sea |
| [Global migration flows from online data](https://doi.org/10.7910/DVN/LPA925) (Chi et al.) | CC0 (P) | C-OK | Monthly bilateral flows 2019–22 | flows | 2022 in motion |
| [Net migration 1 km grid 2000–19](https://zenodo.org/records/7997134) (Niva et al.) | CC BY 4.0 (P) | C-OK | Gridded net migration | raster | Leaving the countryside |
| Meta Social Connectedness Index (HDX) | CC0 (P) | C-OK | Friendship intensity between countries and regions | choropleth from a chosen country, flows | Who your friends are |
| Meta Relative Wealth Index (HDX) | CC BY-NC 4.0 (P) | Story | 2.4 km wealth estimates | raster, points | Wealth at street level |
| Global Data Lab subnational HDI | custom non-profit (S) | Story | Regional HDI | regions | Two countries in one |
| [Wittgenstein Centre projections 2023](https://zenodo.org/records/20447835) | CC BY 4.0 (P) | C-OK | Population by education 1950–2100 | choropleth + timeline | Graduates in 2100 |

### Health

| Dataset | Licence | Verdict | Contents | Layer | Story idea |
|---|---|---|---|---|---|
| Malaria Atlas Project | CC BY 3.0 (S) | C-OK | Malaria maps | raster + timeline | Malaria's shrinking map |
| WHO Global Health Observatory | CC BY 4.0 + WHO terms on data.who.int; who.int data policy limits use to public-health purposes; publications CC BY-NC-SA 3.0 IGO (P; conflicting) | Story (ship values unchanged) | Health indicators | choropleth | Vaccination coverage |

### Science, education, culture

| Dataset | Licence | Verdict | Contents | Layer | Story idea |
|---|---|---|---|---|---|
| Nobel Prize API | CC0 (P) | C-OK | Laureates, birthplace, affiliation | flows | Born abroad, awarded in America |
| OpenAlex | CC0 (S) | C-OK | Works, institutions; 330 GB snapshot | points, flows | Who publishes the most science |
| PatentsView | CC BY 4.0 (S) | C-OK | US patents, geocoded inventors | points | A handful of metros hold most inventors |
| ORCID public data | CC0 (S) | C-OK (aggregates only) | Researcher careers | flows | Brain circulation |
| Glottolog 5.3, WALS | CC BY 4.0 (P) | C-OK | 8k languages, grammar features | points by category | Most languages put the verb last |
| ParlGov (Dataverse releases) | CC0 (P); current release unchecked | C-OK | Parties, elections, cabinets | choropleth + timeline | Who governs Europe |
| Wikidata (Olympics, universities, …) | CC0 | C-OK | Any entity with place and date | points, events | Olympic hosts by continent |

### Food, agriculture, cities

| Dataset | Licence | Verdict | Contents | Layer | Story idea |
|---|---|---|---|---|---|
| [MapSPAM 2020](https://doi.org/10.7910/DVN/SWPENT) | CC BY 4.0 via IFPRI terms (P) | C-OK | 46 crops, 5′ grid | raster, dominant crop | Where your coffee and cocoa grow |
| FAO Gridded Livestock of the World | CC0 (P) | C-OK | Livestock density | raster | Chickens outnumber people |
| GHSL Urban Centre Database R2024A | CC BY 4.0 (P) | C-OK | 11,422 urban centres, 471 indicators | symbols | The real megacities |

## Top story ideas from this pass

1. **Where the whales were** (whaling logbooks, CC BY 4.0).
2. **The launch explosion** (GCAT, CC BY 4.0).
3. **Who your friends are** (Meta SCI, CC0): pick a country, see its ties.
4. **All roads lead to Rome** (Itiner-e + Pleiades): also feeds the Roman Empire series.
5. **Lights out, lights on 2012–2024** (VIIRS v2.2): needs before/after.
6. **How long were you a colony?** (COLDAT, CC0).
7. **The sky went quiet, 2020** (OpenSky).
8. **Where fame was born** (notable people, CC BY-SA, story layer).
9. **Refugees stay close** (UNHCR + IOM).
10. **Distant-water fleets** (Global Fishing Watch, story layer) or **Leaving the countryside** (net migration grid).

Runners-up: Explosions in the sky (CNEOS, once cleared), The coup belt, Damming the world's rivers, The Great Divergence, Born abroad, awarded in America.

## Licence check: history, conflicts and indicators (October 2026)

Check level: P = read at the publisher's own page, file or API; S = secondary; U = unverified. Verdicts follow the two-tier rule in CLAUDE.md.

### History

| Source | Licence | Key terms (quoted or summarised) | Verdict | Check |
|---|---|---|---|---|
| historical-basemaps (aourednik) | GPL-3.0 | Derived files stay GPL | Story | P |
| AWMC geodata (GitHub) | ODbL 1.0 | Share-alike on the database; AWMC map tiles are separately CC BY-NC 3.0 | Story | P |
| DARMC (Harvard Dataverse) | CC0 per set, or none | Roman Road Network, Ports, Coin Hoards: "limited information on how it can be used" | CC0 sets base; others ask | P |
| DARE (Åhlfeldt) | CC BY (version unclear) | GeoJSON API and XYZ tiles work | Story once version pinned | S |
| Stanford ORBIS network | CC BY 3.0 | Edge/node CSVs | Base | P |
| Euratlas | Proprietary | "in no case the vector data themselves" may be disseminated | Ruled out | P |
| IEG-Maps (HRE 1378–1806) | "personal use" on own site; CC BY-NC 4.0 per GeoPortOst | Images only | Story if NC listing confirmed | P |
| HistoGIS HRE Imperial Circles | CC BY 4.0 site-wide, but vectorised from IEG-Maps | Weak licence chain | Story, treat as BY-NC | P |
| ETH Zürich HRE territories (Roller 2021) | CC BY-NC-SA 4.0 | Auto-generated from a modern map + Wikipedia | Story (quality caveat) | P |
| Princes & Townspeople (HRE cities) | CC0 1.0 | City→ruler histories c. 1100–1800, city points and borders | Base | P |
| GeaCron, Centennia | All rights reserved / paid | — | Ruled out | P |
| Wikidata | CC0 | 60 s query limit, 5 parallel queries, descriptive User-Agent required | Base | P |
| Wikipedia Russo-Ukrainian war map module | CC BY-SA 4.0 | ~1,012 settlement control points; front shading is only an image | Story | P |
| DeepStateMap | Proprietary | Credited screenshots free; API/data no transfer, no "identical objects" | Screenshots story; data ask | P |
| ISW / CTP | All rights reserved | Permission needed for graphics | Ask | P/S |
| UNHCR Operational Data Portal | CC BY 4.0 | — | Base | P |
| Kiel Ukraine Support Tracker | None stated | Working paper "All rights reserved" (S) | Ask | P |
| West Point history atlas | US federal work | USMA pages now 404; verify per plate | Base | S |
| Library of Congress maps | Free unless a Rights Advisory is present | Credit "Library of Congress, Geography and Map Division" | Base | P |
| David Rumsey Map Collection | CC BY-NC-SA 3.0 | "not for commercial use" | Story | P |
| Newberry Atlas of Historical County Boundaries | Open access | "any lawful purpose, commercial or non-commercial" | Base | P |
| IPUMS NHGIS | Custom | "will not redistribute the data without permission" | Ask | P |
| USGS territorial acquisitions | Public domain | Shapefile no longer online | Base, availability U | S |
| MEDSL US President 1976–2024 | CC0 | 514 KB CSV | Base | P |
| USFS Royce land cessions | CC BY 4.0 | 752 polygons | Base | P |
| Eurostat GISCO NUTS | GISCO terms | "will not be used for commercial purposes", © EuroGeographics | Story (NC) | P |
| EU Cohesion Open Data | CC0 (per dataset) | — | Base | P |
| European Parliament election results | EP reuse notice | Commercial reuse with source and URL | Base | P |
| Eurobarometer aggregates | CC BY 4.0 or EC reuse notice | Microdata via GESIS unverified | Base (aggregates) | P |
| EHRI/Stanford European borders 1938–45 | Custom note | "commercial use is strictly prohibited", "scholarly work" | Ask (write to authors) | P |
| EHRI SAMU killing sites (Ukraine) | CC BY 4.0 | — | Base (sensitive) | P |
| THOR aerial bombing | Presumed public domain | No licence text seen | U | S |
| USHMM, Arolsen Archives | Per item / no redistribution | — | Ask / ruled out for files | P |
| Copernicus Sentinel-2, NASA GIBS HLS | Open | HLS tiles stop at zoom 12 | Base | P |

### Ukraine war (checked 14 October 2026)

| Source | Licence | Key terms | Verdict | Check |
|---|---|---|---|---|
| NASA FIRMS fires (VIIRS/MODIS) | NASA open data (CC0 unless marked) | Country CSV per year without login; cite "NASA FIRMS". Suomi NPP ends 2 Nov 2026: move to NOAA-20/21 products | Base | P |
| OCHA COD-AB Ukraine (admin 1–3) | CC BY-IGO | Hromada boundaries | Base | P |
| OCHA Ukraine HNO/HNRP (people in need) | CC BY | 2022–2026 | Base | P |
| NRC front-line proximity by hromada | CC BY | Dec 2025 | Base | P |
| WHO attacks on health care, Ukraine | CC BY | Weekly since 24 Feb 2022 | Base | P |
| Black Sea Grain Initiative (UN JCC) | CC BY | Aug 2022 – Jul 2023, complete | Base | P |
| OCHA civilian casualties 2016–2021 | CC BY | No open table for 2022+ (OHCHR site terms forbid redistribution) | Base (2016–21); quote 2022+ totals only | P |
| data.gov.ua, Ukrstat | Open by law incl. commercial (link to source) / CC BY 4.0 | Martial law emptied most wartime series | Base (per dataset) | P |
| UNOSAT Kakhovka flood, city damage | CC BY-SA (some CC BY-IGO) | Copernicus EMS has no public Ukraine activation | Story (SA) | P |
| World Bank RDNA5 | Non-commercial reproduction | PDF tables only | Story (NC) | P |
| Mediazona/BBC named Russian dead | CC BY-SA 4.0 | Regional aggregates only, never names | Story (SA) | P |
| Air-raid sirens dataset (Vadimkin, GitHub) | MIT | Every alert since Mar 2022 | Story | P |
| VIINA (Zhukov) | ODbL | Events usable; its control layer derives from ISW/DeepState | Story (events only) | P |
| Insecurity Insight | CC BY-SA | Attacks on health and aid | Story (SA) | P |
| IOM DTM Ukraine | Non-commercial, no redistribution | Unlike IOM Missing Migrants | No (ask IOM) | P |
| KSE damage, Oryx, WarSpotting, alerts.in.ua, CSIS, Bellingcat TimeMap, Ukrenergo | All rights reserved / no licence | — | Ask | P/S |
| UNESCO damaged cultural sites | Terms unread (blocked) | — | U | S |

### Conflicts now

| Source | Licence | Key terms | Verdict | Check |
|---|---|---|---|---|
| UCDP GED + Candidate (monthly) | CC BY 4.0 | CSV downloads open; API now needs an emailed token; file names change per release | Base | P |
| GDELT 2.0 | Open terms | "unlimited and unrestricted use … commercial"; don't ship third-party article titles | Base | P |
| IPC acute food insecurity (HDX) | CC0 | IPC's own API needs a key | Base | P |
| IDMC displacement | CC BY-NC-SA 3.0 IGO (own API docs) vs CC BY-IGO (HDX) | Use the stricter one | Story (NC-SA) | P |
| UNHCR population API | CC BY 4.0 | No key needed | Base | S |
| HDX HAPI conflict events | ACLED terms | — | Ruled out | P |
| CFR Global Conflict Tracker, ReliefWeb content | Site terms | No public or commercial reuse / personal non-commercial | Ruled out | P |
| Crisis Group CrisisWatch | Unknown (site blocked scripts) | — | Ask | U |

### Country indicators

| Source | Licence | Key terms | Verdict | Check |
|---|---|---|---|---|
| UNDP HDR | CC BY 3.0 IGO | "for any purpose, even commercially" | Base | P |
| Penn World Table 11.0 | CC BY 4.0 | — | Base | P |
| Ember | CC BY 4.0 | Bulk CSV needs no key | Base | P |
| UMD tree-cover loss (GFW) | CC BY 4.0 | GFW API needs a key; other GFW sets per dataset | Base | P |
| WRI Aqueduct 4.0 | CC BY | — | Base | P |
| ILOSTAT | CC BY 4.0 (S) | ILO site blocked scripts | Base (confirm) | S |
| UNESCO UIS | CC BY-SA 4.0 | API needs no key | Story (SA) | P |
| V-Dem v16 | CC BY-SA 4.0 (OWID mislabels as CC BY) | — | Story (SA) | P |
| WHO GHO | See Health row above | Values must not be altered | Story | P |
| Yale EPI | CC BY-NC-SA 4.0 | — | Story (NC) | P |
| Freedom House | Custom: non-commercial OK | Data now via request form | Story (NC) | P |
| TI Corruption Perceptions Index | CC BY-ND 4.0 | Ship scores unchanged only | Story (verbatim) | P |
| UNdata | UNdata terms | Free to copy and redistribute with citation; commercial not addressed | Story | P |
| IMF DataMapper | IMF terms | No automated bulk download without permission | Story (in use, no scheduled scraping) | P |
| Our World in Data | Per origin | Read `origins[].license` per indicator; mixed-origin charts often fail | Per origin | P |
| OECD, World Inequality Database | CC BY 4.0 (S) | — | Hold until confirmed | S |
| ND-GAIN, RSF Press Freedom | No licence stated | — | Hold | U |
| UN SDG Global Database | UN site terms | Personal non-commercial, no redistribution | Ruled out (use custodian agencies) | P |
| IHME GBD | Non-commercial user agreement | No redistribution | Ruled out | P |
| UN Comtrade | Usage agreement | Redistribution prohibited without permission | Ruled out | P |

## Ruled out

Do not revisit unless a written grant is on file.

| Source | Why |
|---|---|
| Correlates of War (incl. World Religion Project) | No commercial use; no redistribution without written permission (S) |
| SIPRI Arms Transfers | Reproducing over 10% needs authorisation; commercial use carries a royalty (S) |
| WDPA / Protected Planet | No redistribution via downloads or interactive maps without permission (S) |
| IUCN Red List and BirdLife ranges | Redistribution not allowed (from memory, re-check if needed) |
| eBird Status & Trends | Commercial use needs permission; redistribution terms unreadable |
| ACLED (incl. HDX HAPI conflict events) | No redistribution (see LICENSING.md) |
| IHME GBD, UN Comtrade, UN SDG database, CFR tracker, ReliefWeb content | No redistribution (P, October 2026 check) |
| Euratlas, GeaCron, Centennia | Proprietary historical borders |
| Global Terrorism Database, EM-DAT, Ethnologue, Space-Track, IAEA PRIS | Restrictive or paid terms (from memory) |
| UCS Satellite Database | No licence stated, paused since 2023: use GCAT |
| Powell & Thyne coups | No licence stated: use Cline Center |
| International football results (martj42) | No licence; compiled from Wikipedia and RSSSF |
| p3k14c radiocarbon dates | Access restricted |
| Dutch-Asiatic Shipping (VOC) | Licence not found |
| International IDEA voter turnout | Data licence not stated |
| HYDE, Reba historical cities, Meteorite Landings | Licence not yet readable: re-check before use (listed above as U) |
