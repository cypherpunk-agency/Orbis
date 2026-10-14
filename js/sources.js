// ---------- data sources and licences ----------
// Single register of every source the site ships or shows. See docs/LICENSING.md for the policy.
// tier:  "base"  = the map itself and the engine; must allow commercial use.
//        "layer" = optional story layer; any licence that allows publishing in a public repo, shown in the UI.
// use:   "commercial"    = licence allows commercial use
//        "noncommercial" = licence forbids commercial use
//        "permission"    = used under a written grant (record where it is filed in `grant`)
// redistribute: licence allows publishing the file in a public repository (required for every source).
const SOURCES = {
  naturalearth: {
    name: "Natural Earth", what: "Country shapes (1:110m)", tier: "base",
    licence: "Public domain", licenceUrl: "https://www.naturalearthdata.com/about/terms-of-use/",
    url: "https://www.naturalearthdata.com/", use: "commercial", redistribute: true,
    credit: "Made with Natural Earth"
  },
  d3: {
    name: "D3", what: "Map rendering library", tier: "base",
    licence: "ISC", licenceUrl: "https://github.com/d3/d3/blob/main/LICENSE",
    url: "https://d3js.org/", use: "commercial", redistribute: true, credit: "D3 by Mike Bostock and contributors"
  },
  topojson: {
    name: "topojson-client", what: "Geometry decoding library", tier: "base",
    licence: "ISC", licenceUrl: "https://github.com/topojson/topojson-client/blob/master/LICENSE",
    url: "https://github.com/topojson/topojson-client", use: "commercial", redistribute: true, credit: "topojson-client by Mike Bostock"
  },
  fonts: {
    name: "Source Serif 4, Barlow Semi Condensed", what: "Typefaces", tier: "base",
    licence: "SIL OFL 1.1", licenceUrl: "https://openfontlicense.org/",
    url: "https://fonts.google.com/", use: "commercial", redistribute: true, credit: "Fonts under the SIL Open Font License"
  },
  "nasa-bluemarble": {
    name: "NASA Blue Marble", what: "Satellite basemap (Blue Marble Next Generation, via NASA GIBS)", tier: "base",
    licence: "NASA open data (CC0)", licenceUrl: "https://www.earthdata.nasa.gov/engage/open-data-services-software-policies/data-use-guidance",
    url: "https://science.nasa.gov/earth/earth-observatory/blue-marble-next-generation/", use: "commercial", redistribute: true,
    credit: "NASA Earth Observatory; imagery via NASA GIBS"
  },
  "nasa-blackmarble": {
    name: "NASA Black Marble", what: "Night-lights basemap (VIIRS Black Marble 2016, via NASA GIBS)", tier: "base",
    licence: "NASA open data (CC0)", licenceUrl: "https://www.earthdata.nasa.gov/engage/open-data-services-software-policies/data-use-guidance",
    url: "https://science.nasa.gov/earth/earth-observatory/earth-at-night/maps", use: "commercial", redistribute: true,
    credit: "NASA Earth Observatory / NASA GSFC; imagery via NASA GIBS"
  },
  "nasa-relief": {
    name: "NASA shaded relief", what: "Terrain basemap (Blue Marble shaded relief and bathymetry, via NASA GIBS)", tier: "base",
    licence: "NASA open data (CC0)", licenceUrl: "https://www.earthdata.nasa.gov/engage/open-data-services-software-policies/data-use-guidance",
    url: "https://nasa-gibs.github.io/gibs-api-docs/", use: "commercial", redistribute: true,
    credit: "NASA Earth Observatory; imagery via NASA GIBS"
  },
  "eia-intl": {
    name: "US EIA", what: "Oil and gas production, consumption and trade by country, 2000–2024 (international energy data)", tier: "layer",
    licence: "US public domain", licenceUrl: "https://www.eia.gov/about/copyrights_reuse.php",
    url: "https://www.eia.gov/international/data/world", use: "commercial", redistribute: true,
    credit: "Source: U.S. Energy Information Administration"
  },
  "eia-chokepoints": {
    name: "US EIA chokepoints", what: "Oil and LNG flows through maritime chokepoints, 2020–1H25", tier: "layer",
    licence: "US public domain", licenceUrl: "https://www.eia.gov/about/copyrights_reuse.php",
    url: "https://www.eia.gov/international/content/analysis/special_topics/World_Oil_Transit_Chokepoints", use: "commercial", redistribute: true,
    credit: "Source: U.S. Energy Information Administration, based on Vortexa tanker tracking and Panama Canal Authority data"
  },
  baci: {
    name: "CEPII BACI", what: "Bilateral trade in energy, minerals, crops and goods hit by US tariffs, 2021–2024 (HS2017, version 202601)", tier: "layer",
    licence: "Etalab Open Licence 2.0", licenceUrl: "https://www.etalab.gouv.fr/licence-ouverte-open-licence/",
    url: "https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37", use: "commercial", redistribute: true,
    credit: "CEPII BACI (Gaulier & Zignago 2010), version 202601, updated January 2026; built from UN Comtrade"
  },
  "usgs-mcs": {
    name: "USGS minerals", what: "Mineral Commodity Summaries 2026: mine production 2024–2025 and reserves by country", tier: "layer",
    licence: "US public domain (CC0)", licenceUrl: "https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits",
    url: "https://doi.org/10.5066/P1WKQ63T", use: "commercial", redistribute: true,
    credit: "Source: U.S. Geological Survey, Mineral Commodity Summaries 2026"
  },
  faostat: {
    name: "FAOSTAT", what: "Crop production by country, 2000–2024 (Production: Crops and livestock products)", tier: "layer",
    licence: "CC BY 4.0", licenceUrl: "https://www.fao.org/contact-us/terms/db-terms-of-use/en/",
    url: "https://www.fao.org/faostat/en/#data/QCL", use: "commercial", redistribute: true,
    credit: "Source: FAO, FAOSTAT (accessed 2026-10-13). Not to be used in commercial promotion"
  },
  "imf-weo": {
    name: "IMF", what: "General government gross debt and GDP (World Economic Outlook, October 2026); household and corporate debt (Global Debt Database), 2000–2024, via IMF DataMapper", tier: "layer",
    licence: "IMF terms, non-commercial", licenceUrl: "https://www.imf.org/en/About/copyright-and-terms",
    url: "https://www.imf.org/external/datamapper", use: "noncommercial", redistribute: true,
    credit: "Source: IMF World Economic Outlook (October 2026) and Global Debt Database, via IMF DataMapper"
  },
  "us-tic": {
    name: "US Treasury TIC", what: "Major foreign holders of US Treasury securities, December 2005–2025", tier: "layer",
    licence: "US public domain", licenceUrl: "https://www.usa.gov/government-copyright",
    url: "https://home.treasury.gov/data/treasury-international-capital-tic-system", use: "commercial", redistribute: true,
    credit: "Source: U.S. Department of the Treasury, Treasury International Capital (TIC) system"
  },
  "bis-cbs": {
    name: "BIS banking statistics", what: "Foreign claims of banks by nationality on each country, Q4 2008–2025 (consolidated banking statistics)", tier: "layer",
    licence: "BIS terms: free use with citation, never behind a paywall", licenceUrl: "https://data.bis.org/help/legal",
    url: "https://data.bis.org/topics/CBS", use: "commercial", redistribute: true,
    credit: "Source: BIS consolidated banking statistics"
  },
  "wb-ids": {
    name: "World Bank debt statistics", what: "Public external debt of low- and middle-income countries by creditor, external debt % of GNI, 2000–2024 (International Debt Statistics)", tier: "layer",
    licence: "CC BY 4.0", licenceUrl: "https://creativecommons.org/licenses/by/4.0/",
    url: "https://www.worldbank.org/en/programs/debt-statistics/ids", use: "commercial", redistribute: true,
    credit: "Source: World Bank, International Debt Statistics (CC BY 4.0)"
  },
  "wb-wdi": {
    name: "World Bank WDI", what: "World Development Indicators for the country atlas (only indicators whose metadata says CC BY 4.0; per-indicator original sources are named in each file)", tier: "layer",
    licence: "CC BY 4.0", licenceUrl: "https://datacatalog.worldbank.org/public-licenses#cc-by",
    url: "https://datatopics.worldbank.org/world-development-indicators/", use: "commercial", redistribute: true,
    credit: "Source: World Bank, World Development Indicators (CC BY 4.0)"
  },
  "wb-wgi": {
    name: "World Bank WGI", what: "Worldwide Governance Indicators: government effectiveness, rule of law, corruption control, voice, stability, regulatory quality", tier: "layer",
    licence: "CC BY 4.0", licenceUrl: "https://datacatalog.worldbank.org/public-licenses#cc-by",
    url: "https://www.worldbank.org/en/publication/worldwide-governance-indicators", use: "commercial", redistribute: true,
    credit: "Source: World Bank, Worldwide Governance Indicators (CC BY 4.0)"
  },
  "wb-wdi-nc": {
    name: "World Bank WDI (non-commercial)", what: "World Development Indicators whose original source licenses them for non-commercial use or share-alike only (named per indicator in the atlas)", tier: "layer",
    licence: "Per indicator, e.g. CC BY-NC 4.0", licenceUrl: "https://datacatalog.worldbank.org/public-licenses",
    url: "https://datatopics.worldbank.org/world-development-indicators/", use: "noncommercial", redistribute: true,
    credit: "Source: World Bank, World Development Indicators (licence per indicator)"
  },
  "wb-wgi-nc": {
    name: "World Bank WGI (non-commercial)", what: "Worldwide Governance Indicators published under a non-commercial or share-alike licence", tier: "layer",
    licence: "Per indicator", licenceUrl: "https://datacatalog.worldbank.org/public-licenses",
    url: "https://www.worldbank.org/en/publication/worldwide-governance-indicators", use: "noncommercial", redistribute: true,
    credit: "Source: World Bank, Worldwide Governance Indicators (licence per indicator)"
  },
  whalinghistory: {
    name: "Whaling History", what: "American Offshore Whaling Voyages and Logbook Data: voyages, home ports and logbook positions 1700s–1920s", tier: "layer",
    licence: "CC BY 4.0", licenceUrl: "https://creativecommons.org/licenses/by/4.0/",
    url: "https://whalinghistory.org/participate/download/", use: "commercial", redistribute: true,
    credit: "American Offshore Whaling Voyages and Logbook Data, whalinghistory.org: New Bedford Whaling Museum, Nantucket Historical Association, Mystic Seaport Museum, Inc. (CC BY 4.0)"
  },
  gcat: {
    name: "GCAT", what: "General Catalog of Artificial Space Objects: orbital launches, launch sites and satellites since 1957", tier: "layer",
    licence: "CC BY", licenceUrl: "https://planet4589.org/space/gcat/",
    url: "https://planet4589.org/space/gcat/", use: "commercial", redistribute: true,
    credit: "Data from GCAT (J. McDowell, planet4589.org/space/gcat)"
  },
  itinere: {
    name: "Itiner-e", what: "Roads of the Roman Empire (static version 2024)", tier: "layer",
    licence: "CC BY 4.0", licenceUrl: "https://creativecommons.org/licenses/by/4.0/",
    url: "https://doi.org/10.5281/zenodo.17122148", use: "commercial", redistribute: true,
    credit: "Itiner-e: de Soto, Pažout, Brughmans et al. (2025), Zenodo 17122148"
  },
  pleiades: {
    name: "Pleiades", what: "Gazetteer of ancient places (city locations)", tier: "layer",
    licence: "CC BY 3.0", licenceUrl: "https://creativecommons.org/licenses/by/3.0/us/",
    url: "https://pleiades.stoa.org/", use: "commercial", redistribute: true,
    credit: "Pleiades gazetteer, pleiades.stoa.org"
  },
  coldat: {
    name: "COLDAT (Colonial Dates Dataset)", what: "Start and end dates of European colonial rule", tier: "layer",
    licence: "CC0 1.0", licenceUrl: "https://creativecommons.org/publicdomain/zero/1.0/",
    url: "https://doi.org/10.7910/DVN/T9SDEW", use: "commercial", redistribute: true,
    credit: "Becker, Colonial Dates Dataset (COLDAT), Harvard Dataverse"
  },
  unhcr: {
    name: "UNHCR Refugee Population Statistics", what: "Refugees by origin and asylum country, end-year stocks 2000–2025", tier: "layer",
    licence: "CC BY-IGO 3.0", licenceUrl: "http://creativecommons.org/licenses/by/3.0/igo/legalcode",
    url: "https://data.humdata.org/dataset/unhcr-population-data-for-world", use: "commercial", redistribute: true,
    credit: "UNHCR Refugee Population Statistics Database (via HDX)"
  },
  "iom-mmp": {
    name: "IOM Missing Migrants Project", what: "Dead and missing migrants by place and year, 2014–2024", tier: "layer",
    licence: "CC BY-IGO 3.0", licenceUrl: "http://creativecommons.org/licenses/by/3.0/igo/legalcode",
    url: "https://data.humdata.org/dataset/iom-missing-migrants-project-data", use: "commercial", redistribute: true,
    credit: "IOM Missing Migrants Project (via HDX); merged into 0.5° cells by Orbis"
  },
  "niva-netmigration": {
    name: "Global net migration 2000–2019 (Niva et al. 2023)", what: "Gridded (5′) and admin-level net migration, 2000–2019", tier: "layer",
    licence: "CC BY 4.0", licenceUrl: "https://creativecommons.org/licenses/by/4.0/",
    url: "https://zenodo.org/records/7997134", use: "commercial", redistribute: true,
    credit: "Niva et al. (2023), Nature Human Behaviour 7: 2023–2037; aggregated to 10′ by Orbis"
  },
  "undp-hdr": {
    name: "UNDP Human Development Report", what: "HDR 2025 composite indices time series for the country atlas: HDI, inequality-adjusted HDI, Gender Inequality Index, planetary-pressures-adjusted HDI, expected and mean years of schooling", tier: "layer",
    licence: "CC BY 3.0 IGO", licenceUrl: "https://creativecommons.org/licenses/by/3.0/igo/",
    url: "https://hdr.undp.org/data-center/documentation-and-downloads", use: "commercial", redistribute: true,
    credit: "Source: UNDP, Human Development Report 2025 (CC BY 3.0 IGO)"
  },
  pwt: {
    name: "Penn World Table 11.0", what: "Human capital index, labour share, average hours worked and GDP price level for the country atlas", tier: "layer",
    licence: "CC BY 4.0", licenceUrl: "https://creativecommons.org/licenses/by/4.0/",
    url: "https://www.rug.nl/ggdc/productivity/pwt/", use: "commercial", redistribute: true,
    credit: "Source: Feenstra, Inklaar and Timmer, Penn World Table 11.0, Groningen Growth and Development Centre (CC BY 4.0)"
  },
  ember: {
    name: "Ember yearly electricity data", what: "Electricity mix for the country atlas: low-carbon, wind and solar, and coal shares; carbon intensity; demand per person (divided by World Bank population)", tier: "layer",
    licence: "CC BY 4.0", licenceUrl: "https://creativecommons.org/licenses/by/4.0/",
    url: "https://ember-energy.org/data/yearly-electricity-data/", use: "commercial", redistribute: true,
    credit: "Source: Ember, Yearly Electricity Data (CC BY 4.0)"
  },
  "unesco-uis": {
    name: "UNESCO Institute for Statistics", what: "Upper-secondary completion rate, primary out-of-school rate and researchers per million for the country atlas (UIS public data API)", tier: "layer",
    licence: "CC BY-SA 4.0", licenceUrl: "https://creativecommons.org/licenses/by-sa/4.0/",
    url: "https://uis.unesco.org/", use: "noncommercial", redistribute: true,
    credit: "Source: UNESCO Institute for Statistics (CC BY-SA 4.0; share-alike, so kept out of the base tier)"
  },
  "ghsl-pop": {
    name: "GHSL population grid", what: "Population density grid, 2025 (GHS-POP R2023A, 30 arc-second, aggregated)", tier: "layer",
    licence: "CC BY 4.0 (EC reuse decision 2011/833/EU)", licenceUrl: "https://eur-lex.europa.eu/eli/dec/2011/833/oj",
    url: "https://human-settlement.emergency.copernicus.eu/ghs_pop2023.php", use: "commercial", redistribute: true,
    credit: "European Commission, Joint Research Centre: GHS-POP R2023A (Schiavina et al. 2023); aggregated to density by Orbis"
  },
  "nasa-gistemp": {
    name: "NASA GISTEMP", what: "Surface temperature anomaly vs 1951–1980, decadal means 1880s–2020s and 2025 (2° grid)", tier: "layer",
    licence: "NASA open data (no restrictions)", licenceUrl: "https://www.earthdata.nasa.gov/engage/open-data-services-software-policies/data-use-guidance",
    url: "https://data.giss.nasa.gov/gistemp/", use: "commercial", redistribute: true,
    credit: "GISTEMP Team, 2026: GISS Surface Temperature Analysis, version 4, NASA GISS; Lenssen et al. 2024"
  },
  "noaa-gfs": {
    name: "NOAA GFS winds", what: "250 hPa jet-stream winds, GFS analysis 13 October 2026 12 UTC (1° grid)", tier: "layer",
    licence: "US public domain", licenceUrl: "https://www.weather.gov/disclaimer",
    url: "https://nomads.ncep.noaa.gov/", use: "commercial", redistribute: true,
    credit: "NOAA/NCEP Global Forecast System; no NOAA endorsement implied"
  },
  eurostat: {
    name: "Eurostat", what: "Regional population, GDP per inhabitant and Census 2021 country of birth for Austrian Bundesländer and German Länder (NUTS 1/2)", tier: "layer",
    licence: "CC BY 4.0 (Eurostat reuse policy)", licenceUrl: "https://ec.europa.eu/eurostat/help/copyright-notice",
    url: "https://ec.europa.eu/eurostat/data/database", use: "commercial", redistribute: true,
    credit: "Source: Eurostat (demo_r_d2jan, nama_10r_2gdp, cens_21cob_r3)"
  },
  "us-census": {
    name: "US Census Bureau", what: "State population estimates (Vintage 2025), median household income (ACS 2024 1-year), US goods trade by partner country, monthly (FT-900)", tier: "layer",
    licence: "US public domain", licenceUrl: "https://www.usa.gov/government-copyright",
    url: "https://www.census.gov/", use: "commercial", redistribute: true,
    credit: "Source: U.S. Census Bureau, Population Estimates Program, American Community Survey, and U.S. International Trade in Goods and Services"
  },
  "us-treasury-fiscal": {
    name: "US Treasury Fiscal Data", what: "Monthly Treasury Statement: customs duties and total federal receipts, monthly, 2017–2026", tier: "layer",
    licence: "US public domain", licenceUrl: "https://fiscaldata.treasury.gov/about-us/",
    url: "https://fiscaldata.treasury.gov/datasets/monthly-treasury-statement/", use: "commercial", redistribute: true,
    credit: "Source: U.S. Department of the Treasury, Bureau of the Fiscal Service, Monthly Treasury Statement"
  },
  "us-fedreg": {
    name: "US Federal Register", what: "Presidential proclamations, executive orders and USTR notices on US tariffs, 2025–2026", tier: "layer",
    licence: "US government work (public domain)", licenceUrl: "https://www.usa.gov/government-copyright",
    url: "https://www.federalregister.gov/", use: "commercial", redistribute: true,
    credit: "Source: Federal Register (Office of the Federal Register / GPO govinfo); compiled by Orbis"
  },
  "us-courts": {
    name: "US court opinions", what: "Supreme Court, Federal Circuit and Court of International Trade opinions on the 2025–2026 tariffs", tier: "layer",
    licence: "US government work (public domain)", licenceUrl: "https://www.usa.gov/government-copyright",
    url: "https://www.supremecourt.gov/opinions/slipopinion/25", use: "commercial", redistribute: true,
    credit: "Supreme Court of the United States; U.S. Court of Appeals for the Federal Circuit; U.S. Court of International Trade"
  },
  ustr: {
    name: "Office of the US Trade Representative", what: "Reciprocal tariff methodology (2025), Section 301 notices and trade-agreement press releases", tier: "layer",
    licence: "US government work (public domain)", licenceUrl: "https://www.usa.gov/government-copyright",
    url: "https://ustr.gov/", use: "commercial", redistribute: true,
    credit: "Source: USTR"
  },
  whitehouse: {
    name: "The White House", what: "Fact sheets and joint statements on trade deals and summits (2025–26)", tier: "layer",
    licence: "US government work (public domain)", licenceUrl: "https://www.usa.gov/government-copyright",
    url: "https://www.whitehouse.gov/", use: "commercial", redistribute: true,
    credit: "Source: whitehouse.gov"
  },
  "us-cbp": {
    name: "US Customs and Border Protection", what: "CSMS guidance on when tariffs were collected and stopped", tier: "layer",
    licence: "US government work (public domain)", licenceUrl: "https://www.usa.gov/government-copyright",
    url: "https://www.cbp.gov/trade/automated/cargo-systems-messaging-service", use: "commercial", redistribute: true,
    credit: "Source: U.S. Customs and Border Protection, CSMS"
  },
  usitc: {
    name: "US International Trade Commission", what: "US imports for consumption, duties collected and ratio of duties to value, 1891–2025 (Table 1)", tier: "layer",
    licence: "US public domain", licenceUrl: "https://www.usa.gov/government-copyright",
    url: "https://www.usitc.gov/documents/dataweb/ave_table.pdf", use: "commercial", redistribute: true,
    credit: "Source: U.S. International Trade Commission, Office of Analysis and Research Services"
  },
  "kummu-gdp": {
    name: "Kummu et al. GDP per capita", what: "Subnational GDP per capita (PPP) 1990–2024, admin-1 table (used for Indian states)", tier: "layer",
    licence: "CC BY 4.0", licenceUrl: "https://creativecommons.org/licenses/by/4.0/",
    url: "https://doi.org/10.5281/zenodo.18429133", use: "commercial", redistribute: true,
    credit: "Kummu, Kosonen & Masoumzadeh Sayyar (2025), Scientific Data 12:178; data Zenodo 18429133"
  },
  "gcp-co2": {
    name: "Global Carbon Project", what: "National fossil CO2 emissions 1950–2024, per person and cumulative since 1850 (Global Carbon Budget 2025)", tier: "layer",
    licence: "CC BY 4.0", licenceUrl: "https://creativecommons.org/licenses/by/4.0/", url: "https://zenodo.org/records/17417124",
    use: "commercial", redistribute: true, credit: "Global Carbon Project, Global Carbon Budget 2025 (Andrew & Peters, fossil CO2 dataset v2025v15, doi 10.5281/zenodo.17417124)"
  },
  "un-wpp": {
    name: "UN World Population Prospects", what: "Life expectancy at birth by country, 1950–2023 (WPP 2024)", tier: "layer",
    licence: "CC BY 3.0 IGO", licenceUrl: "http://creativecommons.org/licenses/by/3.0/igo/", url: "https://population.un.org/wpp/",
    use: "commercial", redistribute: true, credit: "United Nations, DESA, Population Division (2024). World Population Prospects 2024, Online Edition"
  },
  "iana-tz": {
    name: "IANA tz database", what: "Official standard time by country, release 2026c", tier: "layer",
    licence: "Public domain", licenceUrl: "https://github.com/eggert/tz/blob/main/LICENSE", url: "https://www.iana.org/time-zones",
    use: "commercial", redistribute: true, credit: "IANA time zone database"
  },
  "cia-factbook": {
    name: "CIA World Factbook", what: "Independence dates of today's countries (field 'Independence'), via the factbook.json public-domain archive", tier: "layer",
    licence: "US public domain", licenceUrl: "https://github.com/factbook/factbook.json", url: "https://github.com/factbook/factbook.json",
    use: "commercial", redistribute: true, credit: "Source: CIA World Factbook (no CIA seal)"
  },
  "amnesty-dp": {
    name: "Amnesty International", what: "Death penalty: abolition status end-2025, executions recorded in 2025, abolition years to 2008 (facts typed in from reports)", tier: "layer",
    licence: "Facts from reports licensed CC BY-NC-ND 4.0", licenceUrl: "https://creativecommons.org/licenses/by-nc-nd/4.0/", url: "https://www.amnesty.org/en/documents/act50/0778/2026/en/",
    use: "noncommercial", redistribute: true, credit: "Source: Amnesty International, Death Sentences and Executions 2025"
  },
  "ipu-suffrage": {
    name: "Inter-Parliamentary Union", what: "Years women won the right to vote (Women's Suffrage: A World Chronology), typed in as facts, plus cited additions", tier: "layer",
    licence: "IPU terms: non-commercial reuse with acknowledgement; years used as facts", licenceUrl: "https://www.ipu.org/terms-use", url: "http://archive.ipu.org/wmn-e/suffrage.htm",
    use: "noncommercial", redistribute: true, credit: "Source: Inter-Parliamentary Union, Women's Suffrage: A World Chronology"
  },
  "economist-bigmac": {
    name: "The Economist Big Mac index", what: "Big Mac prices in US dollars and the raw and GDP-adjusted index, 2000–2026", tier: "layer",
    licence: "CC BY 4.0", licenceUrl: "https://github.com/TheEconomist/big-mac-data#licence", url: "https://github.com/TheEconomist/big-mac-data",
    use: "commercial", redistribute: true, credit: "Source: The Economist, Big Mac index (CC BY 4.0)"
  },
  "ecdc-covid": {
    name: "ECDC COVID-19 cases", what: "Daily reported COVID-19 cases by country, 31 Dec 2019–14 Dec 2020 (archived); month of first reported case", tier: "layer",
    licence: "CC BY 4.0", licenceUrl: "https://www.ecdc.europa.eu/en/copyright", url: "https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide",
    use: "commercial", redistribute: true,
    credit: "Dataset provided by ECDC based on data provided by public health authorities, scientific institutes or health care providers in the relevant reporting countries and/or by WHO; modified by Orbis (first-case month)"
  },
  "owid-covid": {
    name: "Our World in Data COVID-19", what: "Confirmed COVID-19 deaths per million by 31 Dec 2022 (from WHO dashboard data)", tier: "layer",
    licence: "CC BY 4.0 (WHO data: CC BY 4.0 with WHO terms)", licenceUrl: "https://github.com/owid/covid-19-data/blob/master/public/data/README.md",
    url: "https://ourworldindata.org/coronavirus", use: "commercial", redistribute: true,
    credit: "Our World in Data, based on WHO COVID-19 dashboard data"
  },
  "usgs-quakes": {
    name: "USGS earthquake catalogue", what: "Earthquakes of magnitude 6 and above, 1900–2025 (ANSS Comprehensive Catalog; pre-1973 events largely from ISC-GEM)", tier: "layer",
    licence: "US public domain + ISC-GEM CC BY-SA 3.0", licenceUrl: "https://www.isc.ac.uk/iscgem/download.php",
    url: "https://earthquake.usgs.gov/fdsnws/event/1/", use: "commercial", redistribute: true,
    credit: "Source: U.S. Geological Survey, ANSS ComCat; ISC-GEM Global Instrumental Earthquake Catalogue © ISC and GEM Foundation, CC BY-SA 3.0"
  },
  "ucdp-ged": {
    name: "UCDP conflict events", what: "Organised-violence events (at least one death) by 0.25° cell and month: Ukraine, Syria, Sudan (GED 26.1 + Candidate events to Aug 2026)", tier: "layer",
    licence: "CC BY 4.0", licenceUrl: "https://creativecommons.org/licenses/by/4.0/",
    url: "https://ucdp.uu.se/downloads/", use: "commercial", redistribute: true,
    credit: "Source: UCDP GED 26.1 (Davies, Pettersson & Öberg 2026; Sundberg & Melander 2013) and UCDP Candidate Events (Hegre et al. 2020)"
  },
  cshapes: {
    name: "CShapes 2.0", what: "Historical state borders and dependent territories, 1886–2019 (snapshots for 15 dates)", tier: "layer",
    licence: "CC BY-NC-SA 4.0", licenceUrl: "https://creativecommons.org/licenses/by-nc-sa/4.0/",
    url: "https://icr.ethz.ch/data/cshapes/", use: "noncommercial", redistribute: true,
    credit: "CShapes 2.0: Schvitz, Rüegger, Girardin, Cederman, Weidmann, Gleditsch (2022), ETH Zurich ICR; simplified snapshots by Orbis, CC BY-NC-SA 4.0"
  },
  "orbis-schematic": {
    name: "Orbis schematic routes", what: "Pipelines, sea lanes and facility locations drawn by Orbis from public reporting; approximate", tier: "layer",
    licence: "Own work", licenceUrl: "", url: "", use: "commercial", redistribute: true,
    credit: "Drawn by Orbis; routes are schematic, not surveyed"
  },
  editorial: {
    name: "Orbis editorial figures", what: "Rounded figures typed into stories, cited in each story's notes", tier: "layer",
    licence: "Facts, cited per story", licenceUrl: "", url: "", use: "commercial", redistribute: true,
    credit: "Figures compiled by Orbis; sources in the notes"
  }
};

const USE_LABEL = { commercial: "Commercial use allowed", noncommercial: "Non-commercial only", permission: "Used with permission" };

if (typeof module !== "undefined") module.exports = { SOURCES, USE_LABEL };
