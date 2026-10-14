# Story merge preservation

14 October 2026. Each add/add conflict was compared between Git stages 2 and 3. These chapters implement distinct approaches and use different dataset paths, so both versions are retained. The finite-roadmap version keeps its original ID and complete source bytes; the incoming `origin/main` chapter is published under an explicit `-alternate` ID. Incoming titles already differ naturally.

| Original ID | Finite-roadmap title (scenes) | Incoming title (scenes) | Incoming retained ID |
| --- | --- | --- | --- |
| empty-skies | The sky went quiet (5) | The sky went quiet, 2020 (5) | empty-skies-alternate |
| hre-end | Napoleon and the end (4) | 1806: the end of the Empire (5) | hre-end-alternate |
| hre-patchwork | The territorial patchwork (6) | A patchwork of lords (6) | hre-patchwork-alternate |
| hre-westphalia | Westphalia (4) | Westphalia and the ten circles (5) | hre-westphalia-alternate |
| rome-fall | The falls of Rome and Constantinople (4) | The fall: West 476, East 1453 (5) | rome-fall-alternate |
| rome-frontier | The frontier (4) | The frontier and the split (7) | rome-frontier-alternate |
| ua-2014 | Crimea and Donbas (4) | 2014: Crimea and Donbas (6) | ua-2014-alternate |
| ua-front | The long front (4) | The long front, 2023–2026 (6) | ua-front-alternate |
| ua-refugees | Refugees and displacement (4) | Refugees: millions leave, millions displaced (5) | ua-refugees-alternate |
| us-elections | The electoral map (5) | Red states, blue states (5) | us-elections-alternate |
| us-expansion | Territorial expansion (5) | From sea to sea (7) | us-expansion-alternate |

For every incoming chapter, JSON equality was verified against stage 3 after restoring the original ID: all notes, source lists, dataset mappings, scenes and other fields are unchanged. Original chapter bytes were retained exactly from stage 2. Catalog and campaign reconciliation is recorded separately by the catalog owner. This check preserves content; it does not substitute for browser regression or source review of incoming stories.

## Builder conflicts

- `tools/build/empty_skies.py` retains the finite-roadmap World Bank carrier-takeoff builder (`data/people/empty-skies.json`). Incoming OpenSky monthly-flight aggregation is preserved as `tools/build/empty_skies_alternate.py`, writing `data/statistics/flights.json`, `flights-flows.json`, and `flights-totals.json`.
- `tools/build/us_history.py` retains finite-roadmap chapters and `data/history/usa/` datasets. Incoming Newberry/Royce/MIT data builder is preserved as `tools/build/us_history_alternate.py`, writing the incoming `data/history/us-*.json` datasets.

Both incoming builders were inspected for output calls: neither writes story JSON, and their dataset output paths are distinct from finite-roadmap datasets. Headers and invocation/provenance references name the alternate builder; algorithm, source terms and original output names are preserved. All four builders parse with Python AST. No builders were executed during this merge, so no datasets were regenerated or downloaded.


## Independent shared-engine merge review

14 October 2026. Readonly comparison of the merged `js/app.js` with `origin/main` and the finite-roadmap implementation at `30cea01` found no concrete semantic merge regression in the reviewed paths.

- The complete `tap(x,y)` block is identical to `origin/main` (4,300 characters). Claude's country-click and tooltip behavior is preserved.
- The complete subnational `LAYER.regions` implementation and `multiples` renderer are identical to `origin/main`. The UN/de facto border-view configuration and handlers and timeline spacing/slider functions are also unchanged from incoming main.
- Cards retain incoming date-range start handling, kind filtering, icons, sorting and windows; the finite-roadmap date-precision change additionally passes the reference date to `tUnit`. No registered story uses a finite card window with a fixed full-date layer outside a date timeline.
- The finite-roadmap category-to-regions delegation covers five registered USA scene layers; their dataset set mappings and label structure match the retained regions handler.
- Historical, shape, overlay, vector-field and raster caches use each current story's declared dataset path, so local aliases cannot accidentally reuse another story's cached dataset. The resolution happens synchronously before asynchronous image/topology callbacks.
- No conflict markers remain in `js/app.js`. Momentum and valid-projection crossfade changes remain separate from the incoming tap handler.

This source review is independent of the root's full browser regression and does not assert completion of that runtime gate.

## Pre-deployment verification

The merged country tap/tooltip handler matches origin/main exactly. node syntax checks, all139 story dataset mappings, check-roadmap (59 finite stories/285 scenes) and check-licences (83 sources/139 registered stories) pass. Navigation-merged/results.json passes desktop, mobile and reduced motion, including actual viewport-resize interruption. The sweep encountered Playwright pointer-click timeouts; debt, borders, chokepoints and arctic passed isolated reduced-motion checks, and demography passed the full normal-motion captures at both viewports. Reports remain under .cache/roadmap-review/merged-isolated and demography-normal. These targeted checks do not claim completion of the full catalog regression: final roadmap acceptance remains in progress. The user explicitly requested a main and production push.
