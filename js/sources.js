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
    name: "CEPII BACI", what: "Bilateral trade in energy, minerals and crops, 2021–2024 (HS2017, version 202601)", tier: "layer",
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
