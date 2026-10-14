# M5–M8 completion audit

Audited against the current `ROADMAP.md`, `ROADMAP-SCOPE.json`, chapter files, declared datasets and saved browser reports on 14 October 2026. This is evidence for the coordinator's acceptance ledger; it does not mark milestones passed. **Final regression of every registered story on the merged renderer remains pending.** Earlier successful chapter reports cannot establish that gate.

## Fixed scope and common gates

| Milestone | Required IDs inspected | Current scenes | Evidence/status |
|---|---|---:|---|
| M5 | `eu-growth`, `eu-clubs`, `eu-budget`, `eu-regions`, `eu-brexit`, `eu-candidates` | 31: 6/5/5/5/5/5 | All six files match their IDs and have 4–8 substantive geographic scenes. |
| M6 | `ww2-before`, `ww2-expansion`, `ww2-east`, `ww2-pacific`, `ww2-holocaust`, `ww2-bombing`, `ww2-end`, `ww2-borders` | 36: 4/6/4/5/4/5/4/4 | All eight files match their IDs and have 4–8 substantive geographic scenes. |
| M7 | `ua-2014`, `ua-invasion`, `ua-counteroffensives`, `ua-front`, `ua-energy`, `ua-refugees`, `ua-snapshot` | 28: 4 each | All seven files match their IDs and have four substantive geographic scenes. |
| M8 | `hre-charlemagne`, `hre-1000`, `hre-patchwork`, `hre-westphalia`, `hre-end`, `hre-after` | 26: 4/4/6/4/4/4 | All six files match their IDs and have 4–8 substantive geographic scenes. |

| Common requirement | Inspected evidence | Assessment |
|---|---|---|
| Claim-level sources, dates, precision and lawful imports | [M5 source audit](ROADMAP-EVIDENCE-M5.md), [M6 source audit](ROADMAP-EVIDENCE-M6.md), [M7 source audit](ROADMAP-EVIDENCE-M7.md), [M8 source audit](ROADMAP-EVIDENCE-M8.md); current chapter notes and linked annotation data | Recorded primary-source review distinguishes original factual annotations from imported imagery/geometry. Dated source windows and fallbacks remain explicit in current files. No new source import was made by this audit. |
| Declared files, source/as-of metadata, coverage, units, bounded assets | Current `data/history/{eu,ww2,ukraine,hre}/` files; M5 data-validation, M6 data-audit, M8 provenance; current Ukraine event and refugee datasets | Largest files in those four folders are respectively 268,692 / 290,086 / 439,890 / 800,958 bytes, all below 1 MB. Larger NASA/HRE images retain legibility with documented reasons. Observation and retrieval dates are separate. Final scope/licence commands remain coordinator checks. |
| Every scene/switch at both target viewports, manual visual review | Milestone evidence records all-scene inspection: M5 78 captures, M6 76, M7 56, M8 52. Chapter interaction reports in `.cache/roadmap-review/M5/<id>/interactions.json`, `M6/<id>/interactions.json`, `m7/<id>-interactions.json`, `M8/<id>-interactions.json` | Independently parsed all 27 reports: each has both viewports, scene counts matching its current chapter, and empty errors. Earlier full visual reviews are recorded separately from automated outcomes. These reports predate the final merged-renderer gate. |
| Timeline endpoints/interior, keyboard cards/switches, charts/media/opacity, notes and embeds | Chapter interaction reports plus M5 extra-review, M6 specific/report, M7 media-review, M8 geometry-controls | Applicable controls have direct results; detailed milestone-specific checks below. Generic country tooltip implementation remains Claude's responsibility; this audit did not alter it. |
| Registered campaigns in exact frozen order; landing, deep links, next/back, embed | Current `stories/campaigns.json`; `.cache/roadmap-review/{eu,wwii,ukraine,hre}-campaign-final.json`; inspected `tools/review-campaigns.mjs` | All four registered arrays equal manifest order. Each final report contains 1280×800 and 390×844, exact expected order, passed first/last reloads, chapter boundaries and embed, empty errors. Runner actually reloads links, starts the campaign, visits every boundary forward/back and returns to landing after the last chapter. |
| Final shared-engine regression of every registered story | Coordinator's current normal-motion regression workers | **Pending.** Historic chapter passes and source checks are insufficient to close this common gate. Additional catalogue stories do not expand the finite chapter scope but are included in this regression requirement. |

## M5 specific gates

| Requirement | Direct evidence | Assessment |
|---|---|---|
| Overlapping EU/euro/Schengen membership | Current `eu-clubs.json`, `memberships.json`; `.cache/roadmap-review/M5/extra-review.json` | Overlapping hatches and membership switch are present. Both-view timeline observations show euro 20→21 and Schengen 27→29; EU growth and Brexit dates have expected intermediate counts. Dates describe actual selected observation steps. |
| EU group outline | `union-outline.json`, growth scene 6 and candidates scene 5; extra-review outline legends; fixed-dates.json | EU27 topology and named cutoff are present; corrected fixed-date rendering has explicit boundary checks. Modern geometry is disclosed for historical membership context. |
| Sourced budget chart and arithmetic | `budget.json`; `.cache/roadmap-review/M5/sources/budget-reconciliation.json`, `data-validation.json`, `extra-review.json` | All 15 ordinary/NGEU/cohesion year-and-measure sums for 2021–2025 reconcile to workbook EU27 columns. Independently calculated largest residual is €0.000000000102 million, below €0.02 million tolerance. Financing excludes customs; receipts include ordinary plus NGEU; derived signed difference is explicitly not operating balance or membership welfare. Browser chart values match named outputs. |
| Same region-level values under approved geometry fallback | `regions.json`, `eu-regions.json`; extra-review regional chart | Eight NUTS2 GDP/head PPS values share 2023 and EU27=100; located symbols and chart use those same observations. Country cohesion spending is a separate comparison, not invented regional money. No GISCO restricted geometry is imported. This satisfies the documented regional chart/symbol fallback. |

## M6 specific gates

| Requirement | Direct evidence | Assessment |
|---|---|---|
| Dated occupation snapshots | `ww2-expansion.json` data `occupationEvidence`; `.cache/roadmap-review/M6/specific/report.json` | Both views exercise 9 Apr/10 Jun 1940 and 5/8 May 1945 and report correct Danish/Norwegian national categories. Bornholm exception and use of modern reference outlines are explicit; no continuous monthly front is implied. |
| Sourced campaign movement | Expansion `movementEvidence` and scene 5 | Normandy 6 Jun 1944, Paris 25 Aug 1944 and Remagen 7 Mar 1945 have individual dated citations; connectors/interpolation are schematic, not a traced unit route. Chapter timeline controls cover this layer. |
| Eastern and Pacific coverage; cleared atlas fallback | Four Eastern scenes, five Pacific scenes; `map-provenance.json`; M6 specific media/opacity report | Northern-Europe scan has 11 controls, mean/max residual 4.42/6.38 source pixels; approximation is disclosed. Rejected Pacific warp is not shipped: original 1 Aug 1942 Allied-command scan loads with credit and original link, explicitly not Japanese occupation. Both retained original hashes were verified in data-audit. |
| Sensitive material and historical names | Current `ww2-holocaust.json`, bombing notes; [dated name audit](ROADMAP-EVIDENCE-M6-NAMES.md), derived borders-names files | Holocaust scenes use static card locators and plain sourced accounts, no pulses/victim scaling/invented deportation paths. Six-million context is attributed to USHMM, not allocated to sites. Bombing avoids disputed precision. Both before/borders chapters select normalized dated names index; original upstream aliases retained, geometry/date/numeric properties unchanged. Narrow alias corrections are not represented as a full upstream gazetteer audit. |

## M7 specific gates

| Requirement | Direct evidence | Assessment |
|---|---|---|
| Event coverage and truthful cutoff snapshot | `conflict-ukraine.json`; current `ua-snapshot.json`; snapshot interaction report | Independently computed 5,710 cells, sum 37,424 events, min/max months 202202/202608. Snapshot opens August and exposes Jun/Jul/Aug controls. GED/Candidate distinction, preliminary coverage, country exclusions and event-versus-control distinction remain visible. No September/October observations are implied. |
| Displacement and coverage break | Current refugee chapter, `refugees.json`, `refugees-flows.json`, M7 source audit | Independently read Ukraine-origin stocks for 2021–25: 27,562 / 5,684,177 / 5,960,362 / 5,120,036 / 5,224,131. Russia's 2023→24 statistical coverage break is expressly qualified. Lines are origin/asylum stock links, not journeys; fixed 1.5-million width maximum avoids annual rescaling. Internal displacement is a separate dated national estimate. |
| Dated energy comparison and cleared imagery | `lights.json`, `ua-energy.json`; `.cache/roadmap-review/m7/media-review.json` | January/March/May 2022 NASA composites have individual raw URLs/hashes/credits and local WebPs. Actual mobile media reports show all three images loaded, natural width 1073, rendered width 350, meaningful alt text. Display imagery is not georeferenced radiance, population or current control. |
| Territory fallback and live-conflict dates | Current seven chapter notes and scene updated date; M7 source audit | Modern basemap is orientation rather than legal recognition. Source-linked approximate city locators, UCDP events, stock links and cleared dated images satisfy the documented fallback without inferred front polygons. Editorial cutoff 14 Oct 2026 remains distinct from Aug 2026/2025/May 2022 source windows. |

## M8 specific gates

| Requirement | Direct evidence | Assessment |
|---|---|---|
| Empire outline and selected sourced territories | `territories1789.json`, `attribution.txt`, patchwork scenes 3–4; geometry-controls.json | Exact source membership paths and named Habsburg/Brandenburg selections are recorded; extra-imperial holdings excluded. All three spherical feature areas are bounded/positive. Both-view actual taps identify the correct geometry and dated limitations. Source reconstruction is circa 1789; conflicting Commons summary date is disclosed and resolved using embedded metadata/original upload. |
| Cleared, readable dated patchwork overlay | `reilly1796.json`, WebP, patchwork scenes 5–6; geometry-controls opacity results; M8 visual review | CC BY-NC-SA 3.0 optional scan has pinned archive hash, nine controls, mean/max residual 139.1/309.3 source pixels. Independent audit opened desktop close view and mobile selected-holdings capture: archive divisions and period labels are readable, outline and both selected groups render bounded geography. Opacity 0/50/100 and keyboard 100→99 have actual both-view results. |
| Names and empire context | All six current chapters; M8 source/content table | Aachen/Rome, Saxon centres, Golden Bull, Westphalian treaty cities, 1803/1804/1806 institutional changes and 1815 successor context are separately covered; 1796 scan is not presented as a 1648 border map. Treaty dual date is explicit. |
| Precision and reproducibility | `territories1789.json` controls; `.cache/roadmap-review/M8/reproduction.json` | SVG inversion mean/max residual 43.9/100.2 km is disclosed as coarse control fit, not legal accuracy. Saved 15-file rebuild passed. Current 12 hashes remain byte-identical; three chapter hashes differ exclusively LF/CRLF: converting current `hre-end`, `hre-patchwork`, `hre-westphalia` to CRLF exactly reproduces saved hashes. No substantive reproduction discrepancy remains. |

## Remaining acceptance action

No missing finite M5–M8 topic or unsupported fallback was identified in this audit. Preserve the named approximations and dated coverage qualifications. The coordinator must inspect the completed current-renderer regression and run final scope/licence checks before changing the milestone/story ledger to `passed`. This document does not claim hosted deployment evidence as substitute for content/browser acceptance.

## Historical checkpoint before the authorized stock correction (superseded)

The final shared-renderer regression and source/scope commands now pass; [regression evidence](ROADMAP-EVIDENCE-REGRESSION.md) records complete current-hash coverage. M5/M6/M8 pass. A subsequent actual pointer check found that `ua-refugees` names unfiltered all-origin country totals under its Ukraine-origin title; [precise rendered/source comparison](ROADMAP-EVIDENCE-COUNTRY-INTERACTIONS.md) documents Germany 2,655,191 versus the Ukraine-origin link 1,173,192. Its numerical source data and displayed arcs remain correct, but the tooltip semantic gate remains open under Claude’s ownership. M7 is therefore still in progress.

## Current integrated correction

After the user explicitly authorized missing corrections, root fixed the refugee stock labels and derived Ukraine-only host totals using the existing licensed source. Current actual pointer tests pass both sizes; the independent [stock correction audit](ROADMAP-EVIDENCE-STOCK-CORRECTION.md) verifies every retained pair and source total. The integrated `78c1fd6` full-catalog visual regression also passes all current hashes and expected captures. The historical pending-Claude paragraphs above are superseded; the final current control/campaign suite now passes, including all 108 actual Play/Pause cases. All scoped milestones in this audit pass, with source and geometry limitations retained.
