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
| `cat` | yes | Table-of-contents section: `Energy`, `Geopolitics`, `Economics`, `Statistics`, `People`, `Rights` |
| `title`, `hook` | yes | Title and one-sentence teaser for the table of contents |
| `notes` | yes | Sources and caveats, shown under "Sources and notes" |
| `data` | yes | `{ "alias": "data/<topic>/<file>.json" }`, loaded when the story opens |
| `sources` | no | Extra source ids from `js/sources.js` (for hand-entered facts use `"editorial"`) |
| `scenes` | yes | Array of scenes, 4–8 is a good length |

## Scene fields

| Field | Meaning |
|---|---|
| `title`, `text` | Heading and 1–4 sentences. Plain language, active voice, numbers rounded. |
| `view` | `{ "mode": "globe" \| "equal" \| "mercator", "center": [lon, lat], "zoom": 1 }`. `equal` is the flat Equal Earth map. Zoom 1 shows the whole globe; 2–3 a region. |
| `basemap` | `"political"` (default), `"satellite"`, `"night"` |
| `layers` | Array of layer specs (below). Each names a dataset alias in `data`. Its dataset's `source` appears in the UI automatically. |
| `timeline` | `{ "years": [2000, 2024] \| [list], "start": 2024, "captions": { "2008": "…" }, "format": "month" }`. `[a, b]` with a gap > 1 means every year from a to b. With `"format": "month"`, years are `yyyymm` numbers (e.g. `202003`). Layers with `"year": "t"` follow the slider. |
| `chart` | Top-N bar chart in the panel: same data fields as a layer, plus `title`, `top` (default 8), `fmt`, `color`, `share: true` (percent of world total). |
| `switch` | Buttons that swap a placeholder: `{ "label": "Resource", "start": 0, "options": [ { "c": "lithium", "label": "Lithium", "text": "optional scene text for this option", … } ] }`. Any `{key}` in layers or chart is replaced by the option's value (`"series": "{c}_prod"`). |
| `legend` | Manual legend `[ { "color": "c1", "label": "…" } ]` (otherwise built from layers) |
| `fills` | `{ "ISO3": "c2" }` fixed country colours |
| `highlight` | `["ISO3", …]` outlined countries |
| `points` | Inline points `[ { "at": [lon, lat], "label": "…", "color": "c3", "r": 4 } ]` |
| `routes` | Inline lines `[ { "path": [[lon, lat], …], "color": "c1", "width": 2, "dash": false, "flow": true, "label": "…", "labelAt": 3, "dist": true } ]` (`dist` adds the great-circle length) |
| `circles` | `[ { "center": [lon, lat], "km": 3300, "color": "c2", "label": "…" } ]` |
| `countryLabels` | `true` shows country names (default off in stories, on in Explore) |
| `sources` | Extra source ids for this scene |

Colours: `c1` blue, `c2` magenta, `c3` amber, `c4` teal, `c5` violet, `muted` grey. They adapt to dark mode.

## Layer types

| `type` | Dataset shape | Parameters |
|---|---|---|
| `choropleth` | series | `series`, `year`, `per` (divide by another series, e.g. `"pop"`), `mult`, `log`, `reverse`, `title`, `fmt` |
| `symbols` | series, or points list | Circles, area = value. `series`/`year` or `field`/`period` for point lists; `color`, `maxR` (px), `vmax` (fix the scale across years), `labels` (how many to label), `title`, `fmt` |
| `spikes` | series | Towers, height = value. `maxH` (share of map radius, 0.5–0.7), `width`, `labels`, `vmax`, `color`, `title`, `fmt` |
| `cartogram` | series | Countries resized by value, animated from their real shape. `maxK` (cap on enlargement, default 5), `labels`, `title`, `fmt` |
| `flows` | groups | Arcs from → to, width = value. `group`, `year`, `top`, `from: [ISO3]`, `to: [ISO3]`, `metric: "qty"` (use quantity), `vmax`, `maxW`, `color`, `title`, `fmt`. Users can tap a country to see only its flows. |
| `lines` | lines/points sets | `set`, `color`, `width`, `labels: true`, `flow: true` (animated). Items with `status` other than `"operating"` draw dashed. |
| `points` | lines/points sets | `set`, `color`, `r`, `labels: false` to hide names |
| `since` | sets | Countries coloured while a membership holds: `set`, `year`, `color`, `title`. Use with a timeline for "who joined when". |
| `categories` | sets | One colour per category: `set`, `colors: { "yes": "c4", "no": "c2" }` |

## Dataset shapes

All datasets carry `"source"` (an id in `js/sources.js`), `"asOf"`, `"retrieved"`, and optionally `"note"`. Country codes are ISO3 (`USA`, `CHN`; Kosovo `XKX`, Taiwan `TWN`, Somaliland `SOL`, N. Cyprus `NCY`). No aggregates (World, regions) in country values.

**Series** (choropleth, symbols, spikes, cartogram, chart):
```json
{ "source": "eia-intl", "asOf": "2026-09-30", "retrieved": "2026-10-13", "years": [2000, 2001, …],
  "series": { "oil_prod": { "label": "…", "units": "…", "values": { "USA": [v2000, v2001, …] } } },
  "world": { "oil_prod": [v2000, …] } }
```
`world` is optional; `chart.share` uses it as the denominator if present.

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

**Sets** (since, categories):
```json
{ "source": "…", "sets": {
  "nato":   { "label": "NATO members", "members": { "USA": 1949, "ALB": [1961, 1968] } },
  "un_vote": { "label": "UN vote", "values": { "USA": "yes", "CHN": "abstain" }, "labels": { "yes": "In favour" } } } }
```
`members` values are a start year, or `[start, end)`.

## Formats (`fmt`)

`kbd` thousand barrels/day → "1.2 m b/d", `mbd`, `bcm`, `bcfd`, `musd` (million USD → "$1.2 bn"), `busd` (billion USD → "$1.2 tn"), `t` (tonnes), `kt` (thousand tonnes), `kg`, `mt` (thousand tonnes → "Mt"), `pct` (value already in %), `bpp`, `m3pp`. Anything else: compact SI.

## Writing rules
- One idea per scene; the map must show what the text says.
- Say where a number comes from in `notes`; flag estimates and gaps honestly.
- Contested facts (borders, casualties, control of territory): name the source and date in the text.
- Keep each dataset small; ship only what the story uses.
