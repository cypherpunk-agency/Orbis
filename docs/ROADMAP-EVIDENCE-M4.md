# M4 — United States chapter evidence

Editorial cutoff and factual review: 14 October 2026. Build: `python tools/build/us_history.py`.

Nine required chapters are implemented, with 39 scenes. Source/content review and chapter browser verification are complete. All 39 scenes were captured at both required sizes and visually inspected, including final recaptures after the corrections below. All nine final interaction reports contain two viewport passes and zero errors. This document certifies chapter readiness; root still owns index/campaign registration, campaign navigation and the shared acceptance ledger before M4 can pass in full.

## Artifacts and factual traceability

Every chapter has a matching `data/history/usa/<id>.json`, with retrieval/coverage metadata, original factual annotations and source-linked event cards. Every scene's factual source URL is enumerated by heading in story notes. Supplementary evidence for Plymouth's date, railway approach locations, state affiliations, later surrenders and Tahlequah is also in story notes. Points are approximate named locations, not measured territorial extents.

| ID | Scenes | Factual evidence reviewed | Distinct geographic coverage |
|---|---:|---|---|
| `us-colonies` | 4 | NPS Jamestown short history and FAQ; NPS Wampanoag account; National Archives Declaration and 1783 Treaty of Paris | Jamestown, Plymouth, Philadelphia and the thirteen named states on modern reference outlines |
| `us-expansion` | 5 | National Archives Louisiana treaty; NPS Expedition by Date; State Department Texas/Mexican War, Oregon treaty and Alaska purchase histories | New Orleans, continental crossing, Mexican cession example, Oregon gateway, Alaska |
| `us-indigenous-land` | 4 | NPS Trail of Tears history and New Echota account; Cherokee Nation Our Journey; National Archives Dawes Act | Southeast homeland, treaty site, removal departure/destination areas, federal allotment policy |
| `us-statehood` | 4 | Senate state introductions for Delaware, California, Alaska and Hawaii | Four located constitutional/admission cases distinguish admission from acquisition |
| `us-civil-war` | 5 | NPS Road to Secession, Civil War Facts, Border States, Fort Sumter and Appomattox/later surrenders; National Archives Emancipation Proclamation | Late-1861 affiliations, harbour attack, divided border states, issuing government, surrender site |
| `us-frontier` | 4 | National Archives Homestead Act; NPS Homestead landscape, Golden Spike ceremony, Chinese labour and Promontory geographic account | Nebraska land claim, Sacramento/Omaha approaches and meeting site, Chinese workers' western connection |
| `us-immigration` | 4 | Library of Congress 1851–1900 immigration history; National Archives Ellis Island report and Chinese Exclusion Act; NPS Angel Island | European origins, New York inspection, Pacific exclusion, San Francisco detention |
| `us-elections` | 5 | National Archives certified electoral allocations for 1860 and 2020, including explanatory footnotes | State categories, New Jersey split, modern result, Maine/Nebraska splits, Alaska/Hawaii |
| `us-abroad` | 4 | State Department 1898 Spanish-American War and 1949 NATO histories; Senate Hawaii introduction in the statehood chapter | Philippines/Guam, Puerto Rico/Cuba distinction, Hawaii, Atlantic alliance signing |

## Representations and limits

The roadmap's documented US historical-geometry fallback is used: located acquisition/dispossession events and a source-dated schematic movement. No historical territorial polygons, continuous land-loss surface, battle-control surface, railway survey or immigrant-volume flows have been invented.

Lewis and Clark's movement has four NPS-documented stops: St Charles on 16 May 1804, Rocheport on 7 June 1804, Three Forks on 25 July 1805 and Cape Disappointment on 15 November 1805. Rounded coordinates locate those named places; straight connecting segments are schematic and intermediate marker positions are interpolated, disclosed in the notes.

Natural Earth modern admin-1 geometry supplies reference outlines for the thirteen successor states, late-1861 affiliations and electoral categories. It is not historical geometry. Maine/Virginia and other outlines differ from their earlier extents. West Virginia is omitted in the 1861 affiliation map because it was then part of Virginia; Nevada is omitted because its admission was later. Kentucky and Missouri's rival Confederate governments are disclosed; the map records the states remaining in the Union, not every government's claim. Electoral categories show certified allocation rather than popular-vote shares: New Jersey is split in 1860, Maine/Nebraska in 2020, and unadmitted 1860 states are unfilled. No county detail is needed by these scenes.

The Indigenous chapter is a bounded Cherokee-removal/allotment case study, not exhaustive continental Indigenous history. It identifies the nonrepresentative New Echota signatories, forced displacement, and the distinction between federal acquisition claims and Indigenous consent. No casualty figure is used. The immigration chapter covers nineteenth/early twentieth-century gateways and exclusion rather than claiming a complete modern migration series.

`us-abroad` retains its existing ID and four scene indices, but now explicitly covers historical overseas acquisition/alliance. Its former derivative 2025 military-count/base prose was replaced after review because it did not have direct primary factual evidence sufficient for this release. Existing `#us-abroad/N` links still identify the same story ID, but their editorial content changes. Root should update index title/hook and any base-specific links elsewhere. The old standalone dataset is left untouched for other potential uses.

## Sources and redistribution

No source prose, scanned maps, photos or third-party archival assets were downloaded or redistributed. Facts are independently paraphrased as Orbis editorial annotations under the existing `editorial` source ID. Modern outline geometry already uses the registered `naturalearth` public-domain source. Root confirmed no new source registry ID is required for these annotations. NPS disclaimer and National Archives privacy/use terms were read; their third-party/media exceptions are respected by importing no media. No new licensing row is proposed.

## Verification

Screenshots and logs are local review artifacts under `.cache/roadmap-review/M4/<id>/desktop`, `/mobile`, `desktop.log`, `mobile.log` and `interactions.json`. Screenshot filenames follow `_stories_us_<topic>_json-N.png`. Contact sheets are local review conveniences, not shipped content.

Initial checks on port 8766 encountered server refusal/startup timeouts during parallel load. Those are infrastructure failures, not a passing browser review. Root supplied a quiet threaded server at port 8767; final checks run one browser at a time and replace unsuccessful logs. After initial image inspection, map labels were shortened to named locations because long heading labels clipped at mobile width.

Reproduction in PowerShell:

```powershell
$env:NODE_PATH='C:\Users\tommi\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules'
$env:ORBIS_BROWSER='C:\Program Files\Google\Chrome\Application\chrome.exe'
$env:ORBIS_BASE_URL='http://127.0.0.1:8767/'
node tools/shoot.mjs @stories/us-expansion.json .cache/roadmap-review/M4/us-expansion/desktop
node tools/shoot.mjs @stories/us-expansion.json .cache/roadmap-review/M4/us-expansion/mobile 390 844
node tools/review-interactions.mjs @stories/us-expansion.json .cache/roadmap-review/M4/us-expansion/interactions.json
node tools/check-licences.js
```

Apply the three browser commands to all nine chapter IDs. The interaction runner checks every scene after reload at both viewport sizes, event-card opening/source display/keyboard close where cards are present, timeline first/middle/last positions, next/back, notes, horizontal overflow and embed mode. Root's category fixture separately verifies discrete state colours, category labels on tap, transitions and accessible counts.

Final chapter checks passed: nine matching scope IDs, 4–5 scenes per chapter, 39 scenes total, matching dataset paths, metadata and HTTPS event citations; datasets are 2.5–5.7 KB each. `git diff --check -- stories/us-abroad.json` passed. The final licence checker passed (`64 sources, 80 stories` at that point); root must repeat after final registration.

Visual observations: named-place labels are readable on the final mobile views; the Indigenous departure/destination labels no longer overlap; the allotment government point and Pacific immigration gateway are in view; continental category scenes show the contiguous states; a separate electoral scene shows Alaska and Hawaii. All scene text remains readable in the scrollable mobile panel, and desktop sources/notes/navigation are visible. Every event-card scene was exercised using the clickable list, with source-linked cards opening and keyboard close working. The dated expedition passed first/interior/last slider checks. Every story passed reload deep links, within-story next/back and embed mode at both sizes. Final report paths are `.cache/roadmap-review/M4/<id>/interactions.json`; screenshot logs all end in `no errors`.

The category interaction is verified by root's discrete-region fixture, with `.cache/roadmap-review/categories-before.png` and `categories-after.png` as its visual evidence. Campaign landing/next-chapter checks and global shared-engine regression remain root-owned acceptance work.

## Coordinator integration

All nine chapters are registered in manifest order. `node tools/review-campaigns.mjs united-states .cache/roadmap-review/us-campaign-final.json` passed at 1280×800 and 390×844: landing/order, first/last deep-link reload for every chapter, all forward/back chapter boundaries, final landing and first-chapter embed. Updated `us-abroad` keeps its direct ID and is reachable within this campaign; its previous troop-estimate content was replaced with sourced historical content, as documented above. Source checker passed at integration (64 sources, 88 registered stories). Shared release regression remains pending.

## Source-conflict correction

Independent release review found an NPS conflict: the short chronology and St Charles page summary say 14 May, while the detailed page directly quotes Clark’s journal dated 16 May describing arrival. The first movement waypoint and its timeline now use 16 May 1804, with the direct quotation’s source and disagreement documented in builder/data/story notes. Other selected waypoint dates are unchanged. Targeted browser recheck follows below.
