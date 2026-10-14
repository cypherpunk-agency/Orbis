# M6 dated CShapes display-name correction

Checked 14 October 2026. This bounded correction applies to `ww2-borders`; root integration should also select the same index in `ww2-before`, which displays the 1938 snapshot.

`tools/build/ww2_border_names.py` derives `data/history/ww2/borders-names.json` and the two `borders-names-{1938,1950}.json` files from the existing licensed snapshots. `ww2_history.py` invokes that builder and selects the derived index for `ww2-borders`. The original upstream snapshots remain untouched.

| Snapshot | Upstream consolidated alias | Display name | Evidence |
| --- | --- | --- | --- |
| 1938-01-01, 1950-01-01 | Italy/Sardinia | Italy | [US Office of the Historian](https://history.state.gov/countries/italy/summary): Italian unification in 1861; Kingdom of Italy and its post-1946 republican successor |
| 1938-01-01, 1950-01-01 | Turkey (Ottoman Empire) | Turkey | [US House resolution, primary record](https://www.govinfo.gov/content/pkg/BILLS-115hres924ih/pdf/BILLS-115hres924ih.pdf): Turkish Republic established 29 October 1923 |
| 1938-01-01 | Germany (Prussia) | Germany | [US Office of the Historian](https://history.state.gov/countries/germany): German Empire established 1871 and twentieth-century diplomatic history under Germany |

The 1950 `BRD` German Federal Republic and `DDR` German Democratic Republic names remain distinct and unchanged. This is a narrow display-name correction, not a comprehensive audit of every historical upstream alias. Original aliases are preserved in `sourceName`. Provenance records exact snapshot dates, input paths, SHA-256 hashes and each correction. The builder reverses its own property edits and asserts full equality with the input topology: arcs, transform, geometry, feature IDs, ownership, every other property and all numerical values are unchanged. The existing CShapes CC BY-NC-SA 4.0 story-layer licence continues to apply; no new external dataset is introduced. Metadata supplies `source`, `asOf`, `retrieved`, `note`, and per-snapshot provenance.

Verification used the actual draft chapter at `#@stories/ww2-borders.json`, with Chrome/Playwright against the local server:

- `tools/shoot.mjs`: all four scenes and both scene-2 switch selections captured at 1280×800 and 390×844, no errors. Images in `.cache/roadmap-review/m6-names/{desktop,mobile}/`; both contact sheets and the original tooltip captures were visually inspected. Dates, distinct German-state labels, card locators and selected switches are readable.
- `tools/review-interactions.mjs`: both viewports, switch keyboard selections, event cards/source links, notes, deep-link reload, scene forward/back navigation and embed passed. `.cache/roadmap-review/m6-names/interactions.json` has `errors: []`.
- Actual map taps at known interior points: Italy and Turkey at both dates, Germany in 1938, and both German states in 1950. All fourteen displayed names matched; `.cache/roadmap-review/m6-names/taps.json` has `errors: []` and corresponding screenshots. One long German Federal Republic tooltip slightly clips at the left edge on mobile; root was notified because tooltip positioning belongs to the shared renderer.
- `node tools/check-licences.js`: passed, 68 sources / 101 listed stories at the time of this check. The unlisted draft explicitly names the already registered `cshapes` source. Root must run final scope/registry checks after M6 integration.

Bare `#ww2-borders` checks initially timed out because this chapter was not yet registered. Those failed attempts are superseded by the explicit draft-URL runs above; they are not counted as passing evidence.
