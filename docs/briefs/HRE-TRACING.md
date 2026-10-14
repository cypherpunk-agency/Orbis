# Brief: trace Holy Roman Empire territories from public-domain maps

You are adding **territory polygons of the Holy Roman Empire** to Orbis (a static map-stories site; repo root has `CLAUDE.md`, read it first). No openly licensed vector data of the Empire's territories exists, so you build it by georeferencing public-domain historical maps and tracing their territories.

## Goal
One TopoJSON dataset of HRE territories at **three dates: 1648 (after Westphalia), 1789 (eve of the Revolution), 1803 (before the end)**. Start with 1648; do the others only if 1648 is done well. Aim for the ~60–120 largest territories per date plus the Imperial Circles; group the tiny ones (imperial knights, small abbeys, counties under ~300 km²) into "other small territories" rather than guessing their borders.

## Sources (public domain only)
Use only scans that are public domain both as works (author dead > 70 years, published before 1931) **and** as scans (the scan provider's terms do not add restrictions). Good candidates:
- **William R. Shepherd, Historical Atlas (1911 / 1923 editions)**: plates "Germany about 1648", "Germany in 1786", "Germany 1803". Scans at the University of Texas Perry-Castañeda Library map collection (states the historical atlas maps are public domain) and Wikimedia Commons.
- **G. Droysen, Allgemeiner Historischer Handatlas (1886)** and **F. W. Putzger, Historischer Schul-Atlas (editions before 1931)**: on Wikimedia Commons, check each file's PD tag.
- Library of Congress Geography and Map Division items **without** a Rights Advisory.
Do NOT use: David Rumsey scans (CC BY-NC-SA: allowed only as a story layer, but tracing would inherit it; ask first), IEG-Maps, Euratlas, GeaCron, Centennia, or any modern atlas.
Record for every map: title, author, edition/year, plate, scan URL, the provider's licence statement (quote it), and the date you accessed it.

## Method
1. **Download** the highest-resolution scan into `.cache/hre_trace/` (gitignored). Never commit scans.
2. **Georeference**: write `gcps.json` with at least **12 ground control points** spread over the whole map: cities whose modern coordinates are certain (cathedral or old-town centre; take coordinates from Wikidata, CC0). Order 2 polynomial; order 3 only with 20+ points. Run
   `python3 tools/build/warp_overlay.py <scan> gcps.json hre-1648-shepherd --width 3000`
   (numpy + Pillow, no GDAL). It prints the error per point: drop or fix any point above ~3 px. Mean error must be below ~2 px.
   The resulting overlay (`data/overlays/hre-1648-shepherd.webp/.json`) can ship as an `overlay` layer: keep it ≤ 400 KB.
3. **Trace**: on the warped image (now lon/lat), extract territories by colour:
   - quantise the image to the map's palette (k-means on colours, ~10–20 clusters), clean with morphological opening/closing, remove text and hatching;
   - vectorise each connected region (e.g. scikit-image `find_contours` or rasterio-free marching squares), convert pixel → lon/lat with the overlay's bbox;
   - **manually assign** each polygon its territory name by reading the map label (look at crops of the warped image). If a polygon's identity is unclear, mark `"uncertain": true` rather than guessing;
   - snap shared borders (build a topology so neighbours share arcs), dissolve slivers, simplify (aim ≤ 300 KB for the whole file; Visvalingam or Douglas–Peucker at ~0.01–0.02°).
4. **Check**: overlay your polygons on the warped scan and on today's coastline; spot-check 10 territories against a second public-domain map. Large mismatches (> ~10 km) mean a bad GCP or wrong label.

## Output (the format Orbis reads; see `docs/STORY-FORMAT.md`, layer `shapes`)
- `data/history/hre-territories.json`: a dataset `{ "source": "<source id>", "asOf": "...", "retrieved": "...", "note": "...", "groups": { "<group>": {"label": "...", "color": "c1"} }, "topology": <TopoJSON> }` with one object `shapes`. Each geometry's `properties`:
  - `name` (territory, English with the German name in `name_de`), `from`, `to` (years, e.g. 1648 / 1789 — a polygon valid from 1648 until the next traced date), `group` (one of: `habsburg`, `brandenburg-prussia`, `bavaria`, `saxony`, `palatinate`, `ecclesiastical`, `imperial-city`, `other-secular`, `foreign` (e.g. Swedish Pomerania), `small` (grouped minor territories)),
  - `circle` (Imperial Circle, if known), `uncertain` (true/false), `src` (which map it was traced from).
- `tools/build/hre_trace.py`: the reproducible pipeline (download, warp, quantise, vectorise, simplify), with the hand-assigned names in a small `hre_names_1648.json` next to it.
- A source entry for `js/sources.js` and a row for `docs/LICENSING.md` per map, in the formats already used there (`tier: "layer"`, `use: "commercial"` for public-domain scans), and a note in the dataset: "Traced by Orbis from <map>, <year>; borders as drawn by the map, accuracy roughly ±10 km; small territories grouped."

## Rules
- Licence: CLAUDE.md two-tier rule; register every map; run `node tools/check-licences.js`.
- HTTP: a generic User-Agent (e.g. `Orbis-data-build/1.0`); never send an email address or personal information anywhere; don't register for accounts.
- Files ≤ ~300 KB (overlay images ≤ ~400 KB). No raw scans in git.
- Do not edit `js/`, `css/`, `index.html` or other stories. Work on a branch, or leave changes uncommitted, and report back.

## Report
Maps used (with quoted licence statements), GCP errors, number of territories per date and how many are `uncertain`, file sizes, registry entries and LICENSING rows, screenshots of the polygons over the scan, and anything you could not resolve.
