# Current country interaction acceptance

Verified 14 October 2026 against integrated main `78c1fd6` plus the authorized local story/data corrections. Renderer SHA256: `fa99ebd08a627c194eee1892ea54944e30b8aab6964655566788b78a6242bce4`. `tools/review-country-interactions.mjs` sends real desktop mouse clicks and phone touchscreen taps at 1280×800 and 390×844. All eight checks pass with no browser/assertion errors. Report: `.cache/roadmap-review/country-interaction-final.json`.

| Story/action, both viewports | Observed/source-checked result |
| --- | --- |
| `friends`, scene 1: tap France at 2°E, 47°N | SCI origin changes Portugal→France, France becomes highlighted, country values match the source France row exactly, and the legend names France. Its missing self-pair is the source's null diagonal, not a missing country row. |
| `refugees`, scene 4: tap Germany at 10°E, 51°N, then again | The 12 Syria-origin stock links filter to Syria–Germany **668,647**, then restore exactly. Tooltip labels explicitly distinguish “originating here (all destinations)” and “hosted here (all origins)”; Germany's all-origin host total is **2,655,191**. No exports/imports terminology remains. These are end-2025 stocks, not journeys. |
| `ua-refugees`, scene 1: tap Germany | The Ukraine-origin host tooltip shows **1,173,192**, exactly the source Ukraine–Germany pair, with “hosted here (Ukraine origin only)”. It excludes Germany's all-origin total and exports/imports terminology. |
| `us-elections`, scene 1: tap interior Texas at 99°W, 31°N | Tooltip reads Texas / Breckinridge · 1860, matching the underlying certified electoral-allocation category on modern reference geometry. |

Retained `.cache/roadmap-review/country-{1280,390}-*.png` captures show before/after friendship selection, refugee filter/clear, Ukraine scope/value and Texas category. Current mobile refugee/Ukraine captures were visually inspected: labels and counts fit above the phone sheet.

## Authorized source/configuration correction

The latest upstream commits did not contain this refugee semantic correction. After initially assigning tooltips to Claude, the user explicitly instructed root to fix missing corrections. Root supplied supported layer label overrides in `refugees`, and a Ukraine-only stock-link subset for `ua-refugees`. Generic app/CSS still match upstream; the projection/layer probes exist only in the test response, with no shipped debug API.

`tools/build/refugee_story_totals.py` deterministically derives `data/history/ukraine/refugee-stock-links.json` from the existing licensed `data/people/refugees-flows.json`. Every Ukraine-origin pair and Ukraine's all-destination origin total is preserved. Host totals contain only the respective Ukraine pair. Published links below 5,000 remain absent, never zero-filled; the Russia coverage break remains documented. Source/observation metadata and attribution are retained. The Ukraine builder reproduces the subset/story configuration; licence registration explicitly includes the subset.

The [independent stock audit](ROADMAP-EVIDENCE-STOCK-CORRECTION.md) checks all **153 pairs across ten years**, original origin totals, exact host values and metadata. `.cache/roadmap-review/refugee-stock-data-check.json` also verifies byte-identical rebuilding. The 7,207-byte output SHA256 is `b2e29120f5e1b9df19c09f250c33c0c07faf349ffeb637d5a795522e897eb274`.

## Historical defect and supersession

Earlier rendered output attached Germany's all-origin 2,655,191 to the title “Ukraine-origin refugee stocks”; the actual Ukraine-origin pair was 1,173,192. Generic default labels also called refugee stocks exports/imports. `.cache/roadmap-review/ua-tooltip-observation.json` retains that actual desktop/phone observation. Those semantic issues are now resolved and rechecked; the old observation is not the accepted current result.

Current Explore France facts/story links, Back to Explore, phone collapse/expand and Close to Explore separately pass in `.cache/roadmap-review/current-ui/results.json`. The complete current catalog regression and chapter/campaign suites are documented in [regression evidence](ROADMAP-EVIDENCE-REGRESSION.md). Local acceptance does not claim deployment of these corrections.

Reproduce with the installed Playwright module through `NODE_PATH`, `ORBIS_BROWSER` set to Chrome and `ORBIS_BASE_URL` to the local quiet review server, then run `node tools/review-country-interactions.mjs`.
