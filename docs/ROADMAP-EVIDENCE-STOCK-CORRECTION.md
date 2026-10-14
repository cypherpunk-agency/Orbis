# Refugee stock tooltip correction acceptance

The authorized correction passes the focused source and pointer checks on the current renderer. General refugee country totals now say “originating here (all destinations)” and “hosted here (all origins)”. Ukraine chapter host totals say “hosted here (Ukraine origin only)” and use the source's Ukraine-origin pair, rather than the host's all-origin total. These are end-year population stocks, not trade or migration journey counts.

## Independent source audit

- `data/history/ukraine/refugee-stock-links.json` is a 7,207-byte offline subset of `data/people/refugees-flows.json`, produced by `tools/build/refugee_story_totals.py`.
- All 153 Ukraine-origin links in all 10 observation years (2000, 2005, 2010, 2015, 2020, 2021–2025) match the source rows exactly. Each host value equals its published Ukraine/host pair. Every displayed link is finite and at least 5,000 people; hosts without qualifying pairs remain absent.
- Original Ukraine all-destination origin totals are retained exactly; they are not recomputed from truncated links. The end-2025 total is 5,224,131.
- Metadata preserves `source: unhcr`, `asOf: end-2025`, `retrieved: 2026-10-14`, the year list and units of people. `derivedFrom` identifies the input. The appended note explains omitted small pairs and the 2024 Russia coverage break.
- Germany's end-2025 Ukraine-origin stock is **1,173,192**. Germany's all-origin stock is **2,655,191**. These are distinct measures and are now displayed under their corresponding scope labels.
- `js/sources.js` registers UNHCR's HDX source as CC BY-IGO 3.0, redistributable, with the UNHCR credit. `docs/LICENSING.md` explicitly includes the Ukraine subset and its retained pair/origin semantics. This audit verifies the checked-in source and licence registry; it makes no new upstream retrieval claim.
- The existing `.cache/roadmap-review/refugee-stock-data-check.json` additionally records byte-identical rebuilding, source SHA-256 `91938a52c4f178a7274b55566e492fd60a3ebda657088beafd320365784bd5c8` and subset SHA-256 `b2e29120f5e1b9df19c09f250c33c0c07faf349ffeb637d5a795522e897eb274`.

## Current pointer and visual acceptance

`.cache/roadmap-review/country-interaction-final.json` contains eight passing actual pointer checks across 1280×800 and 390×844, with no errors. Its renderer hash matches the current `js/app.js`: `fa99ebd08a627c194eee1892ea54944e30b8aab6964655566788b78a6242bce4`.

For refugees scene 4, tapping Germany filters the Syria-origin links to the source pair of 668,647, displays Germany's explicitly all-origin total, and a second tap restores the original 12 links. For Ukraine refugees scene 1, tapping Germany displays 1,173,192 with the Ukraine-origin host label; it does not display the all-origin total or exports/imports terminology. The report also verifies France friendship selection and the Texas 1860 election tooltip.

The current 390×844 refugee and Ukraine screenshots were inspected: both stock scope labels and values are readable, within the viewport, and visible above the phone story sheet. The Ukraine scene labels the observation “End of 2025”.

These focused checks establish the stock correction and tested country interactions. They do **not** establish completion of the separately running full-catalog scene/switch regression, nor any production deployment of the local corrections. The full-regression gate remains separate.
