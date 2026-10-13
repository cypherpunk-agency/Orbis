# Orbis

Stories on a turning world: 18 short, guided map stories about power, money, numbers and people, each one moving an interactive globe/flat map.

Static site, no build step. Open `index.html` through any static server:

```sh
python3 -m http.server 8000   # then http://localhost:8000
```

## Layout

- `index.html` — page shell (top bar, story sheet, table of contents)
- `css/style.css` — theme tokens (light/dark) and layout
- `js/sources.js` — register of every data source and its licence (shown in the UI)
- `js/stories.js` — reference data (blocs, memberships, routes, datasets) and the `STORIES` array
- `js/app.js` — rendering (d3 canvas, globe/equal-area/Mercator morphing), story navigation, explore mode
- `data/world.js` — world country topology (`WORLD`, TopoJSON)

See [docs/FRAMEWORK.md](docs/FRAMEWORK.md) for the framework plan, [docs/ROADMAP.md](docs/ROADMAP.md) for limits and the story backlog, and [docs/LICENSING.md](docs/LICENSING.md) for the licence policy (`node tools/check-licences.js`).

Deep links: `#<story-id>/<scene>` (e.g. `#map-lies/2`) or `#explore`.

External libraries load from CDN: d3 7.9.0, topojson-client 3.1.0, Google Fonts.
