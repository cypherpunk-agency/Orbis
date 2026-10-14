# Independent navigation review

Reviewed the globe navigation changes in `js/app.js` and `css/style.css` against the user's reported abrupt drag stop and folded projection bands.

Local Chrome/Playwright review used `http://127.0.0.1:8767/` and page-only instrumentation. No application source was changed by this reviewer.

Verified:

- Ten Globe/Flat toggles at approximately 55 ms intervals complete without a remaining snapshot, faded map canvas or page error.
- Genuine mobile CDP touch events covering pinch, one-finger release, remaining-finger movement and final release leave no active drag, pointers or momentum.
- A separate touch drag followed by `touchCancel` leaves no active drag, pointers or momentum and emits no page error.
- Snapshot raster capture redraws the WebGL canvas synchronously before `drawImage`, avoiding capture of a cleared previous frame.

One issue was reported to the root agent: resizing from 1280 × 800 to 390 × 844 during a projection fade stretches the old snapshot into a tall, narrow globe over the newly laid-out map. `layout()` should settle/remove the fade before resizing. The reproducing image is `.cache/roadmap-review/navigation/resize-middle.png`; the root agent owns the fix and subsequent verification.

Review scripts are `.cache/navigation-edge-review.cjs` and `.cache/navigation-touch-review.cjs`. The first script's synthetic pointer dispatch was unsuitable for pointer capture; its resulting `setPointerCapture` exception is a test artifact. The second script uses genuine CDP touch input and completed without errors.

## Scope correction

The user confirmed that Claude owns country-click/tooltips. Root removed its new country-selection state, highlight, click feedback and measured tooltip positioning. The country `tap()` handler and tooltip CSS match HEAD exactly; earlier roadmap work is retained. Navigation checks no longer assert tooltip behavior. Root also settled the projection fade before `layout()` resizes either map canvas to address the independent review finding.

Scoped browser verification passed at desktop 1280 x 800, mobile 390 x 844 and desktop reduced motion. Globe momentum settles, reduced motion does not coast, political/satellite transitions retain valid projections, pointer interruption restores the visible view, and resizing removes the old snapshot with full canvas opacity. Report: .cache/roadmap-review/navigation-scoped/results.json (errors: empty). node --check and git diff --check also passed.

## Final merged-renderer embed verification

The renderer at commit 3d58554 (SHA256 286eba40d8a8df2dd0021bf73ba070971401571cb7c357889a86dd6b88b0a299) also passed the same checks with `?embed=1`: desktop 1280×800/dark, mobile 390×844/light and reduced-motion desktop. Report `.cache/roadmap-review/navigation-embed-final/results.json` contains three results and empty errors. Momentum moves after release then settles; reduced motion has zero coast. Both political/satellite Globe/Flat directions leave no snapshot or faded canvas; viewport resizing settles the fade.

The final test records the camera at the actual pointer-up event, and measures the projection visible at pointer-down. Earlier fixed-delay observations under simultaneous screenshot load missed portions of the short coast/fade and were not counted as passes. The final embed run used an isolated browser after the catalog workers completed. No navigation-renderer change was needed for this recheck; only test timing instrumentation changed. The implemented resize guard settles a snapshot only when actual viewport dimensions or DPR change.


## Current upstream integration

Integrated main `78c1fd6`, renderer SHA256 `fa99ebd08a627c194eee1892ea54944e30b8aab6964655566788b78a6242bce4`, passes isolated normal and embed motion reviews. Reports: `.cache/roadmap-review/current-navigation/results.json` and `current-navigation-embed/results.json`, each with three configurations and empty errors. Normal desktop/mobile coast was approximately 6.75/17.13 degrees; embed 6.54/16.34 degrees. Both reduced-motion configurations had exactly zero coast. All cases settled, used valid political/satellite Globe/Flat projection frames, and cleaned up fades after interruption and actual viewport resizing.

The interruption tap uses an ocean location to avoid opening the newly added Explore country sheet during a motion-specific assertion. Actual country selection is tested separately in `current-ui/results.json`; France facts/story links, Back to Explore, phone collapse/expand and Close to Explore pass. A phone toggle is awaited until its actual aria state settles rather than asserted synchronously before the animation frame. No product change was needed for these rechecks. Capture names in the maintained motion runner now include theme and reduced-motion preference so future runs retain each desktop configuration separately.
