# Orbis

Stories on a turning world: 57 short, guided map stories, including the 8-chapter series *America's trade war*, about power, money, numbers and people, each one moving an interactive globe/flat map.

Static site, no build step. Open `index.html` through any static server:

```sh
python3 -m http.server 8000   # then http://localhost:8000
```

## Layout

- `index.html` — page shell (top bar, story sheet, table of contents)
- `css/style.css` — theme tokens (light/dark) and layout
- `js/sources.js` — register of every data source and its licence (shown in the UI)
- `js/blocs.js` — country groups for Explore mode
- `js/i18n.js` — interface strings and language choice (`?lang=de`); translated stories live in `stories/<lang>/`
- `editor.html` — story editor: edit JSON, check it, preview it in Orbis (`#@draft`), download it
- `js/app.js` — rendering (d3 canvas, globe/equal-area/Mercator morphing), story navigation, explore mode
- `data/world.js` — world country topology (`WORLD`, TopoJSON)
- `js/raster.js` — WebGL layer that draws satellite / night imagery and follows the globe-to-flat morph
- `stories/*.json` — data-file stories (listed in `stories/index.json`), loaded on demand with their datasets
- `data/energy/`, `data/tex/` — reduced datasets and basemap textures, each with `source` and `asOf`
- `tools/fetch/sources.sh`, `tools/build/*.py` — download raw data into `.cache/` (gitignored) and rebuild the datasets

### Story file format

Scenes declare layers instead of code (choropleth, symbols, spikes, cartogram, flows, lines, points, since, categories, regions, raster, particles, events, historical borders, point-of-view borders), plus timelines, switches, charts and panel media. Full reference: [docs/STORY-FORMAT.md](docs/STORY-FORMAT.md).

See [docs/FRAMEWORK.md](docs/FRAMEWORK.md) for the framework plan, [docs/ROADMAP.md](docs/ROADMAP.md) for limits and the story backlog, and [docs/LICENSING.md](docs/LICENSING.md) for the licence policy (`node tools/check-licences.js`).

Deep links: `#<story-id>/<scene>` (e.g. `#map-lies/2`), `#c/<series-id>` (e.g. `#c/trade-war`), `#explore`, `#quiz`, `#city`, `#@stories/<file>.json` (unlisted story), `#@draft` (editor preview). Add `?embed=1` for a chrome-less embed and `?lang=de` for German.

Tests: `sh tools/test-all.sh` screenshots every scene of every story (needs `npm install` in `tools/`).

External libraries load from CDN: d3 7.9.0, topojson-client 3.1.0, Google Fonts.
