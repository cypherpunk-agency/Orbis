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
  editorial: {
    name: "Orbis editorial figures", what: "Rounded figures typed into stories, cited in each story's notes", tier: "layer",
    licence: "Facts, cited per story", licenceUrl: "", url: "", use: "commercial", redistribute: true,
    credit: "Figures compiled by Orbis; sources in the notes"
  }
};

const USE_LABEL = { commercial: "Commercial use allowed", noncommercial: "Non-commercial only", permission: "Used with permission" };

if (typeof module !== "undefined") module.exports = { SOURCES, USE_LABEL };
