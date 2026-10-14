# Story format

A story is one JSON file in `stories/`, listed in `stories/index.json`. It names its datasets, and each scene declares what the map shows. No code. See `stories/oil.json`, `stories/resources.json`, `stories/debt.json` for complete examples.

## Workflow

1. **Data.** Check the licence at the primary source (rules in `CLAUDE.md` and `docs/LICENSING.md`). Write a build script `tools/build/<name>.py` that downloads raw files into `.cache/` (gitignored) and writes a small dataset to `data/<topic>/<name>.json` (keep each file under ~300 KB). Hand-typed facts are fine as a dataset too: give them `"source"` and cite where each number comes from in `"note"`.
2. **Register** the source in `js/sources.js` and `docs/LICENSING.md` (main session does this for helper agents).
3. **Story.** Write `stories/<id>.json`. Every number in `text` must be checked against the dataset or a cited source; prefer rounded numbers.
4. **Test.** From the repo root: `python3 -m http.server 8765 &` then `node tools/shoot.mjs @stories/<id>.json <outdir>` (works before the story is listed) or `node tools/shoot.mjs <id> <outdir>`. It screenshots every scene and switch option and prints legend, chart, data line and errors. Look at every screenshot. Then `node tools/check-licences.js`.

## Story fields

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Short slug, used in links: `#<id>/<scene>` |
| `cat` | yes | Table-of-contents section: `Energy`, `Geopolitics`, `Economics`, `Planet`, `Statistics`, `Rights`, `People` |
| `title`, `hook` | yes | Title and one-sentence teaser for the table of contents |
| `notes` | yes | Sources and caveats, shown under "Sources and notes" |
| `data` | yes | `{ "alias": "data/<topic>/<file>.json" }`, loaded when the story opens |
| `sources` | no | Extra source ids from `js/sources.js` (for hand-entered facts use `"editorial"`) |
| `scenes` | yes | Array of scenes, 4–8 is a good length |

`updated` (optional, `"yyyy-mm-dd"`) shows "Updated <date>" under the scene title: use it for stories about events that are still moving.

## Series (campaigns)

A series groups stories into ordered chapters with a landing page (`#c/<id>`), reading progress (kept in the browser), key dates and a change log. Define it in `stories/campaigns.json`:

```json
[{ "id": "trade-war", "title": "…", "hook": "one line for the table of contents", "intro": "a paragraph for the landing page",
   "updated": "2026-10-13", "scene": { "view": {…}, "fills": {"USA": "c2"} },
   "chapters": ["tw-liberation-day", "tw-china", …],
   "dates": [ { "d": 20250402, "t": "what happened" } ],
   "changelog": [ { "d": "2026-10-13", "t": "what changed in the series" } ] }]
```

Chapters are ordinary stories listed in `stories/index.json`. They appear under the series in the table of contents (not in their category), their kicker links back to the series, and Next/Back move between chapters. `scene` takes the same map fields as a story scene (no layers). To update a live series: change the chapters, bump `updated` in each changed story and in the series, and add a `changelog` line.

## Scene fields

| Field | Meaning |
|---|---|
| `title`, `text` | Heading and 1–4 sentences. Plain language, active voice, numbers rounded. |
| `view` | `{ "mode": "globe" \| "equal" \| "mercator", "center": [lon, lat], "zoom": 1 }`. `equal` is the flat Equal Earth map. Zoom 1 shows the whole globe; 2–3 a region. |
| `basemap` | `"political"` (default), `"satellite"`, `"night"`, `"terrain"` |
| `layers` | Array of layer specs (below). Each names a dataset alias in `data`. Its dataset's `source` appears in the UI automatically. |
| `timeline` | `{ "years": [2000, 2024] \| [list], "start": 2024, "captions": { "2008": "…" }, "format": "month" }`. `[a, b]` with a gap > 1 means every year from a to b. With `"format": "month"`, years are `yyyymm` numbers (e.g. `202003`); with `"format": "date"`, `yyyymmdd` (e.g. `20250402`, shown as "2 Apr 2025"). With a format, `years` is always a list, never a range. Deep time: years are astronomical (`0` = 1 BC, `-43` = 44 BC) and show as "44 BC", "AD 117" (AD below 1000, or always with `"era": true`); `"step": 25` with `[a, b]` gives every 25th year. `"calendar"` adds a second line under the year: `"auc"` (years since the founding of Rome), `"julian"` (for `"format": "date"`), or a browser calendar (`islamic-umalqura`, `hebrew`, `chinese`, `japanese`, `persian`, `buddhist`, `ethiopic`, `coptic`, `indian`). Store dates in the Gregorian calendar; `Cal.julianToGregorian()` in `js/calendar.js` converts Julian sources. Layers with `"year": "t"` follow the slider. |
| `chart` | Top-N bar chart in the panel: same data fields as a layer, plus `title`, `top` (default 8), `fmt`, `color`, `share: true` (percent of world total). |
| `switch` | Buttons that swap a placeholder: `{ "label": "Resource", "start": 0, "options": [ { "c": "lithium", "label": "Lithium", "text": "optional scene text for this option", … } ] }`. Any `{key}` in layers or chart is replaced by the option's value (`"series": "{c}_prod"`). |
| `legend` | Manual legend `[ { "color": "c1", "label": "…" } ]` (otherwise built from layers) |
| `fills` | `{ "ISO3": "c2" }` fixed country colours |
| `highlight` | `["ISO3", …]` outlined countries |
| `points` | Inline points `[ { "at": [lon, lat], "label": "…", "color": "c3", "r": 4 } ]` |
| `routes` | Inline lines `[ { "path": [[lon, lat], …], "color": "c1", "width": 2, "dash": false, "flow": true, "label": "…", "labelAt": 3, "dist": true } ]` (`dist` adds the great-circle length) |
| `circles` | `[ { "center": [lon, lat], "km": 3300, "color": "c2", "label": "…" } ]` |
| `modernBorders` | `false` hides today's country borders (for historical maps) |
| `countryLabels` | `true` shows country names (default off in stories, on in Explore) |
| `political` | `true` tints countries in political colours instead of plain land |
| `sources` | Extra source ids for this scene |
| `media` | Panel media: `{ "type": "image", "src", "alt", "caption", "credit", "licence", "href" }`, `{ "type": "quote", "text", "by" }`, `{ "type": "line", "data", "series", "countries": [ISO3…], "labels": { "ISO3": "line name" }, "title", "fmt" }` (dataset `"format": "month"` or `"date"` for yyyymm / yyyymmdd years), `{ "type": "area", "data", "series", "countries": [ISO3…], "labels", "title", "fmt" }` (stacked area, one band per country), `{ "type": "gantt", "title", "items": [ { "label", "from", "to", "color" } ], "from", "to" }` (bars for reigns, terms, wars; a marker follows the timeline). Images must be openly licensed and registered like any source. |

Colours: `c1` blue, `c2` magenta, `c3` amber, `c4` teal, `c5` violet, `muted` grey. They adapt to dark mode.

## Layer types

| `type` | Dataset shape | Parameters |
|---|---|---|
| `choropleth` | series | `series`, `year`, `per` (divide by another series, e.g. `"pop"`), `mult`, `log`, `reverse`, `vmin`/`vmax` (fixed scale, e.g. across a timeline), `diverging: true` with `mid` (blue below, red above), `nodataLabel`, `title`, `fmt` |
| `symbols` | series, or points list | Circles, area = value. `series`/`year` or `field`/`period` for point lists; `color`, `maxR` (px), `vmax` (fix the scale across years), `labels` (how many to label), `title`, `fmt` |
| `spikes` | series | Towers, height = value. `maxH` (share of map radius, 0.5–0.7), `width`, `labels`, `vmax`, `color`, `title`, `fmt` |
| `cartogram` | series | Countries resized by value, animated from their real shape. `maxK` (cap on enlargement, default 5), `labels`, `title`, `fmt` |
| `flows` | groups | Arcs from → to, width = value. `group`, `year`, `top`, `from: [ISO3]`, `to: [ISO3]`, `metric: "qty"` (use quantity), `vmax`, `maxW`, `color`, `title`, `fmt`. Users can tap a country to see only its flows. |
| `lines` | lines/points sets | `set`, `color`, `width`, `labels: true`, `flow: true` (animated), `dist: true` (length label), `dash`, `until` (show the path up to point n), `only: [names]` (subset), `forceColor: true` (layer colour wins over item colours). Items may set `color`, `width`, `dash`, `dist`, `until`. Items with `status` other than `"operating"` draw dashed. |
| `points` | lines/points sets | `set`, `color`, `r`, `labels: false` to hide names, `only: [names]`, `forceColor`; items may set `color`, `r` |
| `since` | sets | Countries coloured while a membership holds: `set`, `year`, `color`, `title`. Use with a timeline for "who joined when". |
| `pov` | disputed areas (`data/geopolitics/pov.json`) | Disputed areas drawn as one country sees them: `view` (two-letter code: `US`, `RU`, `UA`, `IN`, `PK`, `CN`, `TW`, `MA`, `ES`, `FR`, `GB`, `AR`, `JP`, `VN`, …), `areas` (names to show). Use with `political: true` and a `switch` over views. |
| `regions` | series keyed by admin-1 ids | States/provinces of one country: `country` (ISO3; geometry in `data/geo/admin1/<ISO3>.json`), or a region set spanning countries: `regionSet` (geometry in `data/geo/regions/<name>.json`, e.g. EU NUTS 2), `series`, `year`, `log`, `mult`, `labels: true`, `title`, `fmt` |
| `raster` | grid descriptor (`data/grids/*.json`) | A lon/lat grid image: `frame` (a frame label, or `"t"` for the timeline), `opacity`, `title`, `fmt` (e.g. `degc`, `ppkm2`). Tap shows the value. Before/after: add `compare` (a second frame label): `frame` shows left of a draggable divider, `compare` right; `leftLabel`/`rightLabel` name the sides. |
| `particles` | vector grid (`data/grids/wind.json`) | Animated streaks following a u/v field: `count`, `speed`, `color` |
| `shapes` | shapes over time | Polygons valid at the timeline date (`year: "t"` or a fixed year): empires, provinces, occupied areas. Coloured by `group` (colours and legend labels from the dataset's `groups`), each group outlined as one merged border (`outline: false` to skip), `labels` (default on), `inner: false` hides internal borders, `opacity`, `groups: [..]` to show only some. Tap shows name and dates. Pair with scene `"modernBorders": false` to hide today's borders. For control areas: `changes: true` marks what changed since the previous timeline step (lost: dashed edge, gained: bold edge); `front: true` draws the shared edge between different groups as a front line (`frontColor`). |
| `cards` | event items | Dated points with a story card: dots appear once their `date` has passed on the timeline (`window: n` keeps only the last n years, `"all"` shows all); tap opens the card (title, date, text, image, source). `list: true` adds a clickable list in the panel. Colours per `kind` from the dataset's `kinds`. |
| `places` | event items (`places`) | Labels whose name depends on the date: each place has `names: [{ "name", "from", "to" }]` |
| `moves` | event items (`moves`) | Routes whose points carry dates `[lon, lat, date]`: drawn up to the timeline date, with a marker where the mover is (`set`, `only`, `color`, `width`, `labels`) |
| `overlay` | overlay (`data/overlays/*.json`) | A scanned historical map, warped to lon/lat with `tools/build/warp_overlay.py` (control points → polynomial fit; prints the error per point). `opacity`, `slider: false` hides the opacity slider in the panel. Use only scans whose licence allows redistribution (public-domain maps, e.g. pre-1931 or US government). |
| `hatch` | sets (with `members`) | Overlapping memberships (EU, euro, Schengen): each set in `sets: [..]` is hatched at its own angle with its own colour (`colors`, `labels` with `{n}` = member count), so a country in several sets shows crossed lines; follows `year` like `since` |
| `pairs` | matrix | Pick a country: every other country is coloured by its value with `from` (ISO3), which is filled and outlined; tapping another country makes it the origin. `title` may use `{name}` for the origin's name; `log`, `fmt`, `vmin`/`vmax`, `fromColor` |
| `categories` | sets | One colour per category: `set`, `colors: { "yes": "c4", "no": "c2" }`; a set with `byYear: { "1860": { "USA-xx": "…" } }` instead of `values` follows the timeline (latest year at or before it), optional `names: { "yes": "…" }` to override the dataset labels (with a switch over sets, `names: { "<set>": { … } }`) |

## Dataset shapes

All datasets carry `"source"` (an id in `js/sources.js`), `"asOf"`, `"retrieved"`, and optionally `"note"`. Country codes are ISO3 (`USA`, `CHN`; Kosovo `XKX`, Taiwan `TWN`, Somaliland `SOL`, N. Cyprus `NCY`). No aggregates (World, regions) in country values.

**Series** (choropleth, symbols, spikes, cartogram, chart):
```json
{ "source": "eia-intl", "asOf": "2026-09-30", "retrieved": "2026-10-13", "years": [2000, 2001, …],
  "series": { "oil_prod": { "label": "…", "units": "…", "values": { "USA": [v2000, v2001, …] } } },
  "world": { "oil_prod": [v2000, …] } }
```
`world` is optional; `chart.share` uses it as the denominator if present. Add `"step": true` when values hold until the next listed date (e.g. tariff rates keyed by `yyyymmdd`): a layer asking for a date between two entries then gets the earlier one.

**Groups** (flows, chart with `group` + `side: "exports" | "imports"`):
```json
{ "source": "baci", "asOf": "…", "years": [2021, 2022], "units": { "value": "million USD" },
  "groups": { "crude": { "label": "Crude oil",
    "flows":   { "2024": [["CAN", "USA", 100505.3, 210091.8], …] },
    "exports": { "2024": { "SAU": 186874 } }, "imports": { "2024": { "CHN": … } } } } }
```
Flow rows are `[from, to, value, quantity_or_null]`, sorted by value.

**Points list** (symbols with `field`/`period`, chart):
```json
{ "source": "…", "periods": ["2023", "2024"], "points": [ { "id": "hormuz", "name": "Strait of Hormuz", "at": [56.4, 26.5], "oil": [21.8, 20.7] } ] }
```

**Lines and points sets** (lines, points):
```json
{ "source": "…", "lines": { "routes": [ { "name": "…", "status": "operating", "path": [[lon, lat], …], "labelAt": 2 } ] },
  "points": { "ports": [ { "name": "…", "at": [lon, lat] } ] } }
```

**Shapes over time** (shapes): TopoJSON inline as `topology` (or a path in `file`), object `shapes`; each feature's properties: `name`, `from`, `to` (astronomical years or `yyyymmdd`; `from` inclusive, `to` exclusive, `null` = open), `group`, optional `label`, `color`, `uncertain: true` (dashed edges), `note`, `at: [lon, lat]` (label position):
```json
{ "source": "…", "asOf": "…", "groups": { "rome": { "label": "Roman Empire", "color": "c2" } },
  "topology": { "type": "Topology", "objects": { "shapes": { "type": "GeometryCollection", "geometries": [
    { "type": "Polygon", "arcs": [[0]], "properties": { "name": "Gallia", "from": -50, "to": 476, "group": "rome" } } ] } }, "arcs": [ … ] } }
```
Build with mapshaper: `node tools/node_modules/mapshaper/bin/mapshaper in.geojson -simplify 10% -rename-layers shapes -o out.json format=topojson`.

**Event items** (cards, places, moves): dates are astronomical years or `yyyymmdd` (Gregorian; an item may say `"cal": "julian"` to show the Julian date its source uses):
```json
{ "source": "…", "asOf": "…", "kinds": { "war": { "label": "Battles", "color": "c2" } },
  "items": [ { "title": "Caesar crosses the Rubicon", "date": -480110, "at": [12.4, 44.1], "kind": "war",
               "text": "…", "source": "Suetonius, Divus Julius 31–33", "url": "…", "image": "…", "credit": "…", "alt": "…" } ],
  "places": [ { "at": [28.98, 41.01], "names": [ { "name": "Byzantium", "from": -660, "to": 330 }, { "name": "Constantinople", "from": 330, "to": 1930 } ] } ],
  "moves": { "army": [ { "name": "Hannibal", "color": "c3", "path": [[-0.98, 37.6, -218], [16.1, 41.3, -216]] } ] } }
```

**Matrix** (pairs): one row per origin, values in the order of `countries` (`null` = no data):
```json
{ "source": "…", "asOf": "…", "label": "Social connectedness", "units": "…", "countries": ["AFG", "ALB", …],
  "values": { "DEU": [12.1, 40.3, …], … } }
```

**Sets** (since, categories):
```json
{ "source": "…", "sets": {
  "nato":   { "label": "NATO members", "members": { "USA": 1949, "ALB": [1961, 1968] } },
  "un_vote": { "label": "UN vote", "values": { "USA": "yes", "CHN": "abstain" }, "labels": { "yes": "In favour" } } } }
```
`members` values are a start year, or `[start, end)`.

## Series features (October 2026)

Added for the history series; all optional.

- **Scene `stamp`**: `"stamp": "Control as of {t} · Wikipedia (volunteer-edited)"`: small text bottom right of the map, also in saved images; `{t}` is the current timeline step.
- **Timeline `spacing: "time"`**: uneven dates sit at their real distance on the slider (ticks mark each step). **`playSpeed`**: milliseconds per step when playing.
- **Switch options**: a layer value that is exactly `"{key}"` takes the option's value with its type (number, boolean, list), e.g. `"diverging": "{div}"`. An option can carry `"view"` to fly elsewhere.
- **`shapes`**: `"dots": true` draws each area's source point (`properties.at`) coloured by group (`dotR`, `dotMinZoom`); groups with `"hollow": true` draw rings. `"fill": false` hides the areas (dots only; areas stay tappable). `"changes": "flash"` (or `"flash": true`) briefly fills newly gained areas when the timeline moves (off with reduced motion).
- **`regions` categories**: `{ "type":"regions", "country":"USA", "data":"a", "set":"pres", "year":"t", "colors":{"dem":"c1","rep":"c2"}, "shade":{"min":50,"max":70}, "unit":"states" }` with dataset `sets.pres = { labels, byYear:{year:{regionId:cat}}, shareByYear:{year:{regionId:number}} }` (or `values`/`share` without years). Lighter = smaller share. Legend chips count regions per category; tap shows "Ohio · Republican · 55.1% · 2024" (`shareFmt` to change the number format).
- **Numeric `regions`**: `diverging`, `mid`, `vmin`, `vmax`, `reverse`, like `choropleth`.
- **`lines` and `points`**: items with `from`/`to` follow the timeline. `lines` `"labels": "once"` labels only the longest piece of each name.
- **`points`, `places`, `cards`**: `minZoom` (per layer or per item) hides them until the reader zooms in. `points` `icon` and card kinds `"icon"`: `swords` (drawn as crossed blades), and legend symbols `star`, `flag`, `anchor`, `crown`, `cross`.
- **Card dates**: `"date": [a, b]` is a range ("760–740 BC"); `"circa": true` prefixes "c.". Ranges sort and filter by their start. Years are astronomical (1 BC = 0, so 760 BC = -759).
- **`symbols` `"scale": "timeline"`**: one size scale across all timeline steps.
- **`flows`**: `outLabel`/`inLabel` rename the per-country totals ("exports"/"imports"); `"totals": false` drops them.
- **`lines` `"fade": true`**: lines not yet (or no longer) valid stay as faint dashed ghosts (`fadeColor`).
- **Media `multiples`**: `{ "type":"multiples", "layer":0, "years":[1976,1992,2008,2024], "title":"..." }` draws one small map per year for that scene layer (`regions` or `shapes`; the US uses an Albers projection with Alaska and Hawaii inset; `extent` [[lon,lat],[lon,lat]] to frame others). Tap a map to jump the timeline there. A margin chart works with the existing `line` media over a series keyed by region id, with `labels` for names.
- **`points` `"under": true`**: plain dots drawn beneath lines (no halo, no labels), e.g. forts under a wall. **`cards` `"kinds": ["war"]`** shows only those kinds.
- **Date ranges**: the era is written once ("AD 100–260", "264–241 BC") and twice only across it ("27 BC–AD 14").
- **`regions` change lists**: a set may instead give `"codes": {code: {"label", "cat"}}` and `"changes": {regionId: [[year, code], ...]}`; the value at a year is the last code at or before it (any year works), coloured by `codes[code].cat`, tap shows the code's label. `"only": ["church", ...]` colours just those categories.
- **`places` `"only": [names]`**: keeps places whose name or any period name is listed (so "Constantinople" keeps "Istanbul" after 1453).
- **`regions` `"countNote": {"US-DC": "DC"}`**: keeps an id out of the legend count and names it ("19 states + DC").
- **`shapes` legend order** follows the dataset's `groups` order (or the layer's `groups` list).
- **`cards` `window`** is always in years, also on `"format": "date"` timelines.
- **Story or scene `"pov": "UA"`**: disputed areas from `data/geopolitics/pov.json` are filled, outlined and tapped as part of the country that view assigns them to (keys as in that file's `views`, e.g. "UA" puts Crimea with Ukraine). The base map otherwise follows Natural Earth's de facto borders.
- **Gantt `row`**: items with the same `"row"` share one line (label from the first labelled item; each bar keeps its own tooltip); `"ticks": [1066, 1485]` draws faint guide lines.
- **Series `coming`**: in `stories/campaigns.json`, `"coming": [{"title": "...", "hook": "..."}]` lists planned chapters, greyed and not clickable.

## Elections explorer (`#elections`)

Reads `data/elections/world.json` (`{source, asOf, note, countries: {ISO3: {last: {date, type, turnout, winner, family, share}, n}}}`) and, when a country is tapped, `data/elections/<ISO3>.json` (`{elections: [{date, type, turnout, parties: [{name, share, seats, family}]}]}`). Party families: left, centre-left, centre, liberal, centre-right, right, green, regional, independent, other. Measures: winner's family, turnout, winner's share, years since the last election.

## Formats (`fmt`)

`int` (1,234), `num`, `dollar` ($6.22), `tpp` (tonnes/person), `mil` ("1,464 M"), `yrs`, `pct0`, `usd`, `eur`, `people`, `degc`, `ppkm2`, `d3:<format>` (any d3-format string, e.g. `d3:$.2f`), `kbd` thousand barrels/day → "1.2 m b/d", `mbd`, `bcm`, `bcfd`, `musd` (million USD → "$1.2 bn"), `busd` (billion USD → "$1.2 tn"), `t` (tonnes), `kt` (thousand tonnes), `kg`, `mt` (thousand tonnes → "Mt"), `pct` (value already in %), `bpp`, `m3pp`. Anything else: compact SI.

## Editor

- `editor.html` edits a story as JSON, checks datasets, layer types, aliases, switch placeholders and source ids, and previews it in Orbis (`index.html#@draft/<scene>`, read from this browser's storage). Unlisted files can also be opened directly: `index.html#@stories/<file>.json`.

## Writing rules
- One idea per scene; the map must show what the text says.
- Say where a number comes from in `notes`; flag estimates and gaps honestly.
- Contested facts (borders, casualties, control of territory): name the source and date in the text.
- Keep each dataset small; ship only what the story uses.
