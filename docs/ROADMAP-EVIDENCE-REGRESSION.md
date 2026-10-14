# Current shared-renderer regression

Verified 14 October 2026 against integrated main `78c1fd6` plus the authorized local source/story corrections. Renderer SHA256: `fa99ebd08a627c194eee1892ea54944e30b8aab6964655566788b78a6242bce4`. Generic app/CSS match that upstream commit. No renderer change occurred during the full pass. The two observation-date labels were corrected before their respective stories were captured.

## Complete coverage

Three normal-motion workers completed **139 registered stories, 278 viewport results, 1,434 scene views, 274 switch-option views and 1,708 screenshots**, at 1280×800 and 390×844. All error arrays are empty. The independent completeness checker verifies every expected story/scene/title/option, current story hash, current renderer hash, accessible map description, viewport dimensions and required screenshot file/size. No missing, stale, duplicate or failed cases remain.

- Full source reports: `.cache/roadmap-review/current-main-{0,1,2}/results.json`.
- Consolidated report, with actual capture directories: `.cache/roadmap-review/current-regression-final/results.json`.
- Completeness: `.cache/roadmap-review/current-regression-final/completeness.json`.

The runner uses actual Next buttons for all scenes, waits for title/network/camera readiness, checks browser/HTTP failures and horizontal overflow, and captures each scene and visible switch option. This complements the chapter-control/campaign suites and source audits; it does not replace them. Earlier commit `3d58554` reports remain historical evidence in `regression-final`, not current proof.

## Focused review

All finite chapter source/visual audits remain linked from the acceptance ledger. Current contact sheets `.cache/roadmap-review/current-contact/current-{1280,390}-{0,1}.png` were inspected for NASA imagery/swipe, the approximate Rome atlas, dated US categories, EU budget, Pacific geography, Ukraine media and HRE geometry/archive close-up. Updated mobile whale/fame date labels and refugee tooltip captures were separately inspected.

Current actual SCI source-country selection, refugee-link filter/clear, scoped refugee stocks and US state-category pointer checks passed eight assertions across both sizes, with exact source values. See [country interaction evidence](ROADMAP-EVIDENCE-COUNTRY-INTERACTIONS.md) and the [independent stock audit](ROADMAP-EVIDENCE-STOCK-CORRECTION.md). Germany's Ukraine-origin host stock is correctly 1,173,192, distinguished from the general all-origin stock of 2,655,191. This authorized correction uses story configuration and a reproducible source subset, without generic tooltip renderer/CSS changes.

`.cache/roadmap-review/current-ui/results.json` separately passes current Explore France facts/story links, return/close to Explore, phone collapse/expand and scrolling to decoded Ukraine/WWII images. Current images were inspected. The first phone-toggle assertion ran before asynchronous settling completed; waiting for the actual aria state passed without any product change.

`.cache/roadmap-review/current-builder-reproduction.json` verifies all 33 regenerated US/Ukraine JSON files against the current checkout, including explicit scene display dates and the source-derived stock subset. [Scene-date audit](ROADMAP-EVIDENCE-CURRENT-DATES.md) distinguishes observation dates from release/retrieval dates across 59 finite stories.

Final isolated normal/embed motion checks pass all three configurations each. The consolidated current control suite passes 59 chapters, 570 scene-control views and seven exact campaign orders/boundaries/deep links/embeds. Separate Play/Pause proof covers all 108 expected timeline cases, with actual displayed-label/frame advancement from the first observation and a restored Play state after pausing. Reports: `.cache/roadmap-review/current-controls/suite-final.json` and `current-play/chunk-{0,1}.json`. Parallel mouse timeouts are retained; isolated mouse retries pass, and keyboard chapter steps complement the successful mouse-based visual/campaign suites. The stopped fame child is explicitly superseded by its passing isolated report. Initial playback-test range assumptions were corrected to respect the existing two-endpoint inclusive-range contract; no product change was needed.

## Reproduction

Set `NODE_PATH` to the installed Playwright module, `ORBIS_BROWSER` to Chrome and `ORBIS_BASE_URL` to the quiet local review server. Run `node tools/review-all.mjs <output-dir> [story-id ...]` for full normal-motion scene/switch captures. Validate with `node tools/check-roadmap-regression.mjs .cache/roadmap-review/current-regression-final`. Run `node tools/check-roadmap.mjs` and `node tools/check-licences.js` for finite scope/source-register checks. Screenshots and JSON caches remain local.
