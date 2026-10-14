# M3 Roman Empire evidence

Reviewed on 2026-10-14. Six new chapters implement the required topics with four geographic scenes each. `roman-roads` is reused and reviewed by the coordinating agent under M1; this agent has not changed it. Live index/campaign registration and source-registry integration belong to the coordinator.

## Artifacts

| Required chapter | Artifact | Representation |
|---|---|---|
| Rome and Carthage | `stories/rome-carthage.json` | Dated Sicily, Italy and Africa event anchors; disputed Alpine crossing and Zama locality explicitly disclosed |
| Growth by conquest | `stories/rome-expansion.json` | Republican/imperial chronology, Britain/Dacia/Parthia anchors and a cited historical atlas overlay |
| Roads and cities | `stories/roman-roads.json` | Existing Itiner-e/Pleiades story, retained unchanged |
| The frontier | `stories/rome-frontier.json` | Wall endpoints, Forth–Clyde anchor, Rhine and Danube context; no invented wall/border polygons |
| East and West | `stories/rome-split.json` | Dated governmental centres, Ravenna and interactive Byzantium/Constantinople name change |
| The falls of Rome and Constantinople | `stories/rome-fall.json` | Separates Rome's sack, western deposition, eastern survival, 1204/1261 and 1453 |
| What remains | `stories/rome-legacy.json` | Located monuments/infrastructure at Rome, Pont du Gard, Hadrian's Wall, Ravenna and Constantinople |

`tools/build/rome_history.py` deterministically writes six `data/history/rome/rome-*.json` event datasets and six stories. `--overlay` additionally processes the cached source scan. All event cards contain a specific source label, source URL, astronomical date and approximate city/site location. Story notes disclose that locations are anchors, not battlefield footprints or territorial proxies. BC/AD and AUC labels appear on the historical timelines. Dates used as regional/period anchors (AD 117, AD 142 and AD 150) are distinguished from instantaneous conquest/construction claims.

## Source audit

Factual annotations are original Orbis synthesis under the existing `editorial` source; no institution's prose or illustrations were copied. The following were read during this implementation, and the cards link directly to relevant texts:

- [Polybius, Histories 1](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Polybius/1*.html), [3](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Polybius/3*.html), [15](https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Polybius/15*.html): Punic chronology and campaign locations. Ancient narratives are acknowledged as source accounts; the Alpine pass and Zama battlefield are not resolved by invented geometry.
- [Appian, Punic Wars, section 133](https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0230%3Atext%3DPun.%3Achapter%3D20%3Asection%3D133): destruction of Carthage. The initial guessed LacusCurtius URL was rejected because that host does not publish the Foreign Wars; the final card uses the verified Perseus reference.
- Met: [The Roman Republic](https://www.metmuseum.org/essays/the-roman-republic), [The Roman Empire](https://www.metmuseum.org/essays/the-roman-empire-27-b-c-393-a-d), [Byzantium](https://www.metmuseum.org/essays/byzantium-ca-330-1453), and [Byzantium: Faith and Power](https://www.metmuseum.org/exhibitions/listings/2004/byzantium-faith-and-power): republican crisis, imperial chronology, division and eastern continuity. The conventional western endpoint is not presented as the termination of every Roman institution.
- [English Heritage: Hadrian's Wall](https://www.english-heritage.org.uk/visit/places/hadrians-wall/hadrians-wall-history-and-stories/history/): AD 43, AD 122, wall endpoint names and later frontier changes.
- UNESCO: [Frontiers of the Roman Empire](https://whc.unesco.org/en/list/430/), [Danube Limes](https://whc.unesco.org/en/list/1608/), [Rome](https://whc.unesco.org/en/list/91/), [Pont du Gard](https://whc.unesco.org/en/list/344/), [Ravenna](https://whc.unesco.org/en/list/788/): geography and heritage context. Ravenna's detailed statement supplies AD 402. Pont du Gard's detailed statement dates the aqueduct to the middle of the first century; its short summary conflicts with that statement, so the detailed statement is used and the conflict noted.

The geographic anchors have regional/site precision only. The source texts identify the named locality; no source makes the exact hand-rounded coordinates a surveyed perimeter or battlefield location. There are no casualty, population or territory-area statistics to validate in these six chapters.

## Historical geometry fallback and licence

The documented Roman geometry fallback uses a cleared historical-map overlay rather than a newly invented extent polygon. Mitchell's **1880** map is a retrospective nineteenth-century reconstruction titled "Map of the Roman Empire in its greatest extent"; no precise AD 117 snapshot is attributed to it.

- [Catalogue](https://www.davidrumsey.com/luna/servlet/detail/RUMSEY~8~1~30544~1140071), image identifier **0586.072**.
- [Commons file description](https://commons.wikimedia.org/wiki/File:Map_of_the_Roman_Empire_in_its_greatest_extent._(with)_Ancient_Greece._(By_S._Augustus_Mitchell._1880)_(IA_dr_map-of-the-roman-empire-in-its-greatest-extent-with-ancient-greece-by-0586072).jpg).
- Exact downloaded scan: `https://upload.wikimedia.org/wikipedia/commons/e/e2/Map_of_the_Roman_Empire_in_its_greatest_extent._%28with%29_Ancient_Greece._%28By_S._Augustus_Mitchell._1880%29_%28IA_dr_map-of-the-roman-empire-in-its-greatest-extent-with-ancient-greece-by-0586072%29.jpg`.
- Cache: `.cache/roadmap-review/M3/mitchell1880.jpg` (5868 × 5069 pixels).
- Commons has a public-domain template but also an explicit Rumsey CC BY-NC-SA 3.0 notice. The stricter [Rumsey terms](https://www.davidrumsey.com/about/copyright-and-permissions) are honoured for this optional story layer. Credit **David Rumsey Map Collection, David Rumsey Map Center, Stanford Libraries**; adaptation **CC BY-NC-SA 3.0**; commercial reuse requires separate permission. This layer does not enter the base map.
- Proposed registry ID: `rome-mitchell1880`, `tier: layer`, `use: noncommercial`, `redistribute: true`; no private permission grant is claimed.
- Outputs: `data/history/rome/mitchell1880.webp` (260770 bytes) and `data/history/rome/mitchell1880.json`.

Ten hand-located coastal/city controls fit a second-order polynomial. The builder records every `[sourcePixelX, sourcePixelY, longitude, latitude]` control in the descriptor's `gcps`. The original preview controls (at width 1400) are London (396,418), Lisbon (184,693), Gibraltar (254,758), Rome (588,635), Carthage (535,730), Constantinople (788,607), Alexandria (875,852), Crete (790,758), Marseille (467,560), Cyprus (922,750); longitude/latitude values are in the descriptor and builder. The mask retains the main panel between preview x 132–1300 and y 210–910, removing the unrelated Greek inset at x ≥ 767 and y < 537. The output extent is `[-12,27,48,59]`, 1400 pixels wide. Fit residuals are mean **51.7** and maximum **109.6 original scan pixels**. This is an overview, not survey-quality georeferencing; coastlines and northern areas retain visible disagreement. The scene, descriptor and notes say so. The initial distorted warp was rejected visually; these are the corrected controls.

## Actual verification

Commands use installed Chrome, `NODE_PATH` for the bundled Playwright, and the local review server. Individual commands:

```powershell
python tools/build/rome_history.py --overlay
node tools/shoot.mjs '@stories/<id>.json' .cache/roadmap-review/M3/<id>/desktop
node tools/shoot.mjs '@stories/<id>.json' .cache/roadmap-review/M3/<id>/mobile 390 844
node tools/review-interactions.mjs '@stories/<id>.json' .cache/roadmap-review/M3/<id>/interactions.json
```

All six new story JSONs and their referenced data files parse; each has four scenes. `git diff --check` for owned files passed. Desktop captures exist for all 24 scenes and reported no errors. They were visually inspected together in `.cache/roadmap-review/M3/contact.png`, with the corrected overlay additionally inspected full size. Mobile captures and interaction checks are recorded per chapter in the same directory; final completion is recorded below after those checks finish.

The interaction runner exercises each timeline at its first/middle/last positions, play, keyboard event-card opening with a source link, notes, Next/Back, embed mode, and horizontal-overflow checks in both desktop and mobile viewports. Overlay opacity is a real slider; its numerical state is also tested separately. Campaign chapter-to-chapter navigation and the reused road chapter remain coordinator integration checks.

One mobile expansion capture attempt timed out while the original single-threaded server was under load. The retry uses the coordinator's quiet threaded server at port 8767; the failed attempt is not counted as a passed review.

### Final review results

All six new chapters have 4 desktop and 4 mobile screenshots (48 scene captures total). The mobile expansion retry succeeded with no errors. All six `interactions.json` reports contain two completed viewports and `errors: []`; each confirms embed mode. Desktop contact sheets and all mobile scene strips were visually inspected: text is readable, the sheet scrolls to its controls, event locations match the described geographic regions, and the approximate overlay is present. The fall chapter's corrected eastern continuity date (AD 476) was recaptured on desktop and is already present in the mobile captures. `roman-roads` screenshots belong to M1, so are not counted among these 48.

`.cache/roadmap-review/M3/extra-checks.json` records an additional single-browser check at port 8767: the wall scene rendered after a six-second wait; the overlay opacity input changed to `20`, and the Mitchell source was visible in the attribution. The resulting `long-wait-wall.png` and `opacity-20.png` were inspected. The coordinator verified the camera's Britain-wide overview: zoom is a global scale factor, not a web-map zoom level, so the extent at zoom 12 is expected. Both wall endpoint dots are visible, and both cards are available from the list; the nearby east map label is suppressed to avoid collision. No engine change is required.

The coordinator registered the source under the stricter Rumsey terms. `node tools/check-licences.js` passed: **63 sources, 70 stories** at the time of this run. Owned JSON files parse and `git diff --check` passed. Shared campaign registration, complete chapter navigation and the reused road chapter are the coordinator's remaining integration checks; the six new chapter checks are complete.

## Coordinator campaign integration

All seven chapters are registered in manifest order, including the unchanged `roman-roads` reuse. `node tools/review-campaigns.mjs roman-empire .cache/roadmap-review/rome-campaign-final.json` passed in both target viewports: landing/order, every first/last deep-link reload, all forward/back chapter boundaries, final landing and first-chapter embed. Root inspected all reused road-scene desktop/mobile contact-sheet captures under M1. Final shared-engine release regression remains pending.
