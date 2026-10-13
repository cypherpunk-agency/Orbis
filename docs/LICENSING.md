# Licensing policy

**Rule: Orbis only uses code, data, fonts and imagery that are licensed for commercial use.**
Non-commercial (NC) licences, "research only" terms, unclear terms, and "ask us" terms without a written grant are excluded.
Share-alike/copyleft licences (ODbL, CC BY-SA, GPL) need a deliberate decision before use, because they impose obligations on what we publish.

Before adding any dependency or dataset: check its licence at the primary source, add a row below, and add any required attribution to the page.

## In use

| Component | Licence | Commercial | Obligations |
|---|---|---|---|
| d3 7.9.0 | ISC | Yes | Keep licence notice |
| topojson-client 3.1.0 | ISC | Yes | Keep licence notice |
| World geometry (`data/world.js`, Natural Earth 1:110m via world-atlas) | Public domain | Yes | None (credit optional) |
| Source Serif 4, Barlow Semi Condensed (Google Fonts) | SIL OFL 1.1 | Yes | None for web use |
| Story figures (hand-entered) | Facts, not copyrightable | Yes | Cite sources per figure (data-pipeline task) |

## Evaluated candidates

| Source | Licence | Verdict | Notes |
|---|---|---|---|
| CShapes 2.0 (ETH Zurich) | CC BY-NC-SA 4.0 | **Excluded** | Non-commercial |
| historical-basemaps (aourednik) | GPL-3.0 | **Excluded** | Copyleft, plus unclear provenance ("collected from diverse sources") |
| Thenmap | Not stated | **Excluded** until written terms exist | |
| ACLED | Commercial use needs paid corporate licence | **Excluded** unless licensed | |
| ISW / Critical Threats maps | Brief excerpts only; everything else needs permission | **Excluded** unless written permission | |
| DeepStateMap | Visuals free incl. commercial with credit/logo/link; API needs prior approval for commercial entities; "identical copies" prohibited | **Needs written approval** before using their front-line data | Screenshots with credit are OK |
| OpenHistoricalMap | CC0 by default; some features tagged CC BY / CC BY-SA | **Preferred** for historical borders | Filter by `license=*` tag; credit "© OpenHistoricalMap contributors" |
| UCDP | CC BY 4.0 | **OK** | Cite dataset publications |
| Our World in Data | CC BY 4.0 for OWID's own data | **OK, per series** | Third-party series keep their original licence; check each |
| World Bank open data | CC BY 4.0 | **OK** | Attribution |
| MapLibre GL JS | BSD-3 | **OK** | Keep licence notice |
| Protomaps basemap tiles (self-hosted PMTiles) | ODbL (OSM data), styles CC0, code BSD-3 | **OK** | Visible "© OpenStreetMap" credit; self-host (hosted API needs sponsorship for commercial use) |
