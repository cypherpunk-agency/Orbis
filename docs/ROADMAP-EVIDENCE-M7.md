# M7 — Ukraine review evidence

Seven chapters, in the frozen order: `ua-2014`, `ua-invasion`, `ua-counteroffensives`, `ua-front`, `ua-energy`, `ua-refugees`, `ua-snapshot`. Each has four scenes, for 28 scenes total.

## Reproduction and provenance

Run `python tools/build/ukraine_history.py` for the deterministic offline chapter and annotation build. Run `python tools/build/ukraine_lights.py` for the separately cached NASA downloads and compressed display images. Existing UCDP and UNHCR files retain their independent builders and source metadata; this chapter builder does not silently refresh them.

- [UN General Assembly, 27 March 2014](https://press.un.org/en/2014/ga11493.doc.htm): Crimea referendum and territorial integrity.
- [OHCHR, occupation and aftermath report, 20 March 2024](https://ukraine.un.org/sites/default/files/2024-04/2024-03-20-OHCHR-Report-Occupation-Aftermath-en.pdf): paragraphs 29–32 for 2014 context, northern withdrawal and end-November 2022 recovery; paragraph 163 for recovery services. The public UN copy was downloaded and extracted for verification because the OHCHR-hosted download returned HTTP 403. No PDF or source prose is shipped.
- [OHCHR eastern Ukraine detention study](https://ukraine.ohchr.org/en/arbitrary-detention-torture-and-ill-treatment-context-armed-conflict-EN): window 14 April 2014–30 April 2021 and case-study locations. The window is not portrayed as the start of every incident.
- [General Assembly, 2 March 2022](https://press.un.org/en/2022/ga12407.doc.htm): demand for withdrawal.
- [UN Kherson convoy, 14 November 2022](https://ukraine.un.org/en/207300-ukraine-humanitarians-bring-water-food-medicines-and-other-essential-supplies-thousands): city regained three days earlier, independently dating the 11 November marker.
- [UN Kakhovka assessment](https://ukraine.un.org/en/235545-potential-long-term-impact-destruction-kakhovka-dam): 6 June 2023 destruction, downstream flooding and upstream water loss. No culprit attribution or flood extent is inferred by the marker.
- [NASA Kyiv comparison, 30 June 2022](https://science.nasa.gov/earth/earth-observatory/tracking-night-lights-in-ukraine-150002/): January/March/May display imagery. Registered source `nasa-ukraine-lights`; credit Joshua Stevens / NASA Earth Observatory, Black Marble data Ranjay Shrestha / NASA GSFC. Exact image URLs and raw SHA256 checksums are in `data/history/ukraine/lights.json`.
- [UNHCR year-end 2025 emergency impact report](https://www.unhcr.org/sites/default/files/2026-01/unhcr-2025-emergencies-and-protracted-crises-impact-report.pdf): separate operational estimate of 3.7 million IDPs and 5.9 million refugees. The chapter explicitly distinguishes this estimate from the annual statistical series.
- [UNHCR Global Trends 2024](https://www.unhcr.org/sites/default/files/2025-06/global-trends-report-2024.pdf): Russia coverage break in the annual refugee series. The existing annual stock and flow metadata preserve category definitions and the 5,000-person flow threshold.

All annotations are original factual paraphrases, registered as `editorial`, with individual source links. Coordinates are approximate city or region anchors, not surveyed battlefield footprints. No source photos, restricted maps, continuous control polygons or reconstructed fronts are imported.

## Fixed observation windows and numerical checks

Editorial cutoff is 14 October 2026. UCDP GED 26.1 plus Candidate 26.0.8 ends in August 2026; annual refugee stocks end in 2025; the imagery ends in May 2022. The snapshot chapter keeps those dates separate and does not claim to depict current October control.

The included Ukraine UCDP dataset has 5,710 monthly cell records whose values sum to 37,424 events, ranging from February 2022 to August 2026. The cells have side length 0.25 degrees. Country-only/unlocated records are excluded by the existing build; events assigned to Russia are excluded. Candidate records are preliminary. Circle area counts events, not deaths, troop strength or territory. No apparent absence of circles is described as safety.

The annual Ukraine-origin refugee series is `[27,562, 5,684,177, 5,960,362, 5,120,036, 5,224,131]` for 2021–2025. The decline across 2023–2024 is explicitly qualified by the removal of Russia's roughly 1.2 million Ukrainians from that statistical coverage. Flow lines connect origin and asylum countries and are stocks, not observed migration journeys. Flow widths use a fixed 1.5-million-person maximum across the annual timeline, including its small 2021 baseline. Internal displacement uses a separately dated national estimate, not a Kyiv city count.

New annotation files are 1.1–3.7 KB each. NASA display WebPs are 436–440 KB each, below the 1 MB release gate; their larger-than-300-KB size retains the published image detail. They are panel images without georeferencing or a radiance tooltip. The map does not infer military control or population from darkness.

## Browser review

Browser evidence is stored under `.cache/roadmap-review/m7/`: `desktop/` and `mobile/` have all-scene screenshots and capture logs; each chapter's `*-interactions.json` covers controls at 1280×800 and 390×844, including keyboard cards, timeline endpoints/middle/play where present, scene navigation, direct-link reloads, notes, overflow and embed mode. These files are generated by `tools/shoot.mjs` and `tools/review-interactions.mjs` against the local server.

All 28 scenes have passed captures at both viewports and all seven interaction reports have two views with empty errors. All desktop/mobile scene screenshots were visually inspected in contact sheets and selected full-size views. The extra media-review.json check confirmed all three mobile NASA images load at native width 1073, remain within the 390-pixel viewport and have alt text; mobile/ua-energy-image-1.png through -3.png show the complete images after scrolling and were inspected. Visual findings were corrected and the affected chapters rerun: a stale year in the refugee flow legend, per-frame flow-width scaling, NASA publication-date ambiguity, and the cutoff scene initially opening at June instead of August. The modern basemap is disclosed as an orientation convention, not legal recognition or control. Campaign registration, campaign cross-chapter navigation and release acceptance remain root integration checks. This evidence document does not mark those checks as passed before they are run.

## Coordinator integration

All seven chapters are registered in `ukraine-war` in the frozen manifest order. `node tools/review-campaigns.mjs ukraine-war .cache/roadmap-review/ukraine-campaign-final.json` passed at 1280×800 and 390×844: every chapter's first/last deep-link reload, all forward/back chapter boundaries and embed, with `errors: []`. The campaign checks previously reserved for root integration have therefore completed. Final merged-renderer regression and release acceptance remain pending.
