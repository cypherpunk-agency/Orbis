# M8 — Holy Roman Empire evidence

Six required chapters contain 26 substantive scenes: six in `hre-patchwork`, four in each other chapter. Scope: `hre-charlemagne`, `hre-1000`, `hre-patchwork`, `hre-westphalia`, `hre-end`, `hre-after`. Root owns final index/campaign registration, campaign navigation and release acceptance. This report does not substitute for those checks.

## Source and editorial audit

Original factual annotations are `editorial`, with a URL on every event card. No institutional prose, museum photographs or modern copyrighted document translations were imported. Coordinates are approximate named-city or regional locators, identified as such in data and notes; they are not archaeological surveys, sovereignty polygons or invented battle/control lines.

| Chapter | Evidence reviewed | Geographic treatment |
|---|---|---|
| Charlemagne | [UNESCO Aachen](https://whc.unesco.org/en/list/3/): preferred residence, chapel c.790–800, burial 814; [Habsburger glossary](https://www.habsburger.net/en/glossary/holy-roman-empire): Rome coronation 800; [Met Ottonian Art](https://www.metmuseum.org/essays/ottonian-art): Otto king 936 | Aachen/Rome comparison; Carolingian imperial revival distinguished from later Saxon empire |
| Around 1000 | Met Ottonian Art: Aachen 936/Rome 962, Bernward’s Hildesheim; [UNESCO Quedlinburg](https://whc.unesco.org/en/list/535/): Saxon-Ottonian royal centre 919–1024 | Named royal/church centres; 1000 is a cultural-period anchor, not a founding date or territorial snapshot |
| Patchwork | [Golden Bull primary text, GHDI](https://germanhistorydocs.org/en/from-the-reformations-to-the-thirty-years-war-1500-1648/the-golden-bull-1356): Frankfurt election, Mainz/Trier/Cologne spiritual electors; [UNESCO Regensburg](https://whc.unesco.org/en/list/1155/): Perpetual Diet 1663–1806; Reilly 1796 map | Date-stamped historical map fallback, overview plus Rhine–Main close view; institutions annotated with city names |
| Westphalia | [Primary peace treaties, GHDI](https://germanhistorydocs.org/en/from-the-reformations-to-the-thirty-years-war-1500-1648/peace-treaties-of-westphalia-october-14-24-1648); [Habsburger peace history](https://www.habsburger.net/en/chapter/peace-last): Münster/Osnabrück; UNESCO Regensburg for continuity | Treaty-city comparison and institutional geography. The much later 1796 map is explicitly not a 1648-border map. Primary treaty day is 14/24 October (Julian/Gregorian) |
| End | [GHDI introduction](https://germanhistorydocs.org/en/the-holy-roman-empire-1648-1815/introduction): 1803 Final Recess; [House of Austria](https://www.habsburger.net/en/chapter/house-austria-habsburgs-and-empire): Austrian imperial title 1804; [primary abdication declaration](https://germanhistorydocs.org/en/the-holy-roman-empire-1648-1815/ghdi:document-5355): Vienna 6 August 1806 and separate Rhine union | Institutional/regional locators, not boundaries of the Rhine Confederation or troop movements |
| After | [German Federal Act, 1815, GHDI](https://germanhistorydocs.org/en/from-vormaerz-to-prussian-dominance-1815-1866/german-federal-act-june-8-1815), articles 4/9 and abstract: named free cities/Frankfurt assembly; [Vienna settlement](https://www.habsburger.net/en/chapter/new-ordering-europe-181415); UNESCO Aachen/Regensburg heritage | Vienna/Frankfurt comparison, northern free cities and surviving imperial buildings; no modern sovereignty inferred |

Dates/coverage: historical events 800–1815; present-day heritage annotations reviewed at editorial cutoff 2026-10-14. Data `asOf` identifies historical synthesis; `retrieved` is the source-review date. No live measurements, casualty estimates, numeric territorial areas or modern state proxy fills are used. Dates before 1582 use the historical calendar convention; later explicit Gregorian/dual-day dates are identified. Names in annotations and the retained German historical map label the named places and institutions of their period.

## Imported map: provenance, licence and precision

[Reilly/Benedicti, Karte von der Deutschland, Vienna 1796, Rumsey 11151.021](https://www.davidrumsey.com/luna/servlet/detail/RUMSEY~8~1~278984~90052027). The archival record identifies a hand-coloured administrative map and offers a full image download: `https://www.davidrumsey.com/rumsey/download.pl?image=/162/11151021.jp2`. Download succeeded, 12,564 × 8,492 pixels. The map is contemporaneous cartography, not a later reconstruction drawn by this project.

[Rumsey permissions](https://www.davidrumsey.com/about/copyright-and-permissions) permits reproduction/transmission with credit and links CC BY-NC-SA 3.0. Apply that stricter licence to the adapted optional layer despite the eighteenth-century underlying map being public domain. Credit: David Rumsey Map Collection, David Rumsey Map Center, Stanford University Libraries. Root registered `hre-reilly1796` and its licensing row.

Pinned downloaded JP2 SHA-256: `2c7bad5e0f9566d1fefaf283a321b3c459b3de014c6fe5ac80728756e69801bb`. Rebuild rejects a changed archive file pending review. Cached input lives under `.cache/roadmap-review/M8/reilly1796.jp2` and is not shipped.

Published `data/history/hre/reilly1796.json` records every named control, source-image pixel coordinate, geographic coordinate, residual, URL, hash, licence, credit, box and limits. Nine approximate anchors: Texel, Helgoland, Rügen, Gdańsk, Strasbourg, Basel, Lake Constance, Venice and Trieste. Second-order inverse polynomial fit; mean residual 139.1 source pixels, maximum 309.3 (roughly 20/44 pixels in the 1800-wide preview). These are approximate visual controls; residual consistency is not proof of historical border accuracy. The map is cropped to its main panel, retaining original colouring/names; approximate coast alignment is visible and disclosed. No fresh sovereignty polygons are traced. Overview preserves context, close view makes the dense coloured divisions visible; readable city annotations supplement fine print. This close view covers a regional subset of the empire.

Output WebP: 2400 × 1467, 800,958 bytes, below the 1 MB file ceiling. Each event dataset is below 5 KB. Builder is offline for the normal editorial rebuild; `--overlay` uses the pinned cached scan or downloads the named archive file. Commands:

```powershell
python tools/build/hre_history.py
python tools/build/hre_history.py --overlay
```

## Browser evidence

Reports and captures live under `.cache/roadmap-review/M8/`. The serial runner `.cache/review_hre.ps1` invokes `tools/shoot.mjs` for every scene at 1280×800 and 390×844 and `tools/review-interactions.mjs` for both viewports. Draft links use `#@stories/<id>.json/<scene>` with reload. Final registration/campaign links require root integration checks.

The source/data schema audit confirmed matching IDs, four to six scenes each, existing declared files, registered source fields and explicit units/as-of metadata. Images are manually inspected, including the patchwork overview/close view; screenshot exit codes alone are not acceptance evidence.

## Required imperial outline and selected territories

The root release audit identified that city locators plus the 1796 scan alone did not satisfy the exact M8 fallback contract. `hre-patchwork` now also contains a source-derived circa-1789 imperial outline and the source’s named Habsburg/Brandenburg holdings inside that outline.

Source: [Alphathon’s Map Holy Roman Empire 1789.svg](https://commons.wikimedia.org/wiki/File:Map_Holy_Roman_Empire_1789.svg), original April 2013 upload, revision by Fenn-O-maniC on 17 October 2021. [Observed SVG download](https://upload.wikimedia.org/wikipedia/commons/2/2d/Map_Holy_Roman_Empire_1789.svg), pinned SHA-256 `b227139b3117be2373a6eb5c671afe4de428ae723ddea3ef3be5c9385fbb9916`. Source title and embedded description explicitly say circa 1789; the original upload comment also says circa 1789. The current Commons summary incorrectly says 1279 and points to an earlier template map. That conflict is disclosed; no date is inferred from the filename alone. The 2024 re-upload’s CC0 claim was disregarded because the original creator and embedded metadata require **CC BY-SA 3.0**.

`tools/build/hre_geometry.py` extracts all 189 source paths with the creator-defined dark-green imperial-membership fill. The source description identifies pale green as extra-imperial possessions; those paths are excluded. Named source paths `Habsburg Holy Roman Empire` and `Brandenburg` supply the two selected holdings without drawing any new border. Compound subpaths are sampled and nested holes retained. A one-preview-pixel closing/opening repair removes narrow shared-edge slivers arising from independently sampled curves; this numerical repair is disclosed. Simplification is 0.7 preview pixels with topology preservation. Source-ring orientation is explicitly converted to D3’s spherical convention so polygons cover the bounded territory rather than the rest of the globe.

Approximate source-to-geographic inversion uses 12 named coastal controls, a second-order polynomial, mean residual **43.9 km**, maximum **100.2 km**. Those are control-fit residuals, not evidence of historical border accuracy. The source is a modern historical reconstruction with coarse alignment; it is suitable for the overview, not an exact legal border, territorial-area statistic or settlement-level query. Source interpretation excludes extra-imperial dynastic holdings and is not substituted with modern national outlines. Each feature is marked uncertain, valid in the display year 1789 only; `to:1790` is the exclusive display step, not a claim that these borders stayed unchanged until then.

The output `data/history/hre/territories1789.json` records source URLs, revision date, units, licence, hash, all source membership-path IDs, every control and residual, and the extracted topology. It is approximately 39 KB. Full original base-map contributor attribution is retained in `data/history/hre/attribution.txt`; adaptations carry CC BY-SA 3.0. Root registered `hre-alphathon1789` and its licensing row. Builder rejects a changed SVG pending a source audit.

```powershell
python -m pip install --target .cache/roadmap-review/M8/python svgpathtools==1.8.0 shapely==2.2.0
python tools/build/hre_geometry.py
python tools/build/hre_history.py
```

An actual cached rebuild of editorial chapters plus derived geometry produced byte-identical outputs across 15 files; `.cache/roadmap-review/M8/reproduction.json` records the hashes. The large archived-map warp was built from the pinned downloaded JP2, with image/descriptor provenance recorded above; its cached source remains available for the `--overlay` command.

The dedicated real-browser check `.cache/check_hre_geometry.mjs` passed at both viewports: all three spherical feature areas are small and positive (imperial outline 0.01470 steradians, selected holdings 0.00415/0.00281); actual pointer taps return the correct imperial/Habsburg/Brandenburg names and dated limitations; opacity 0/50/100 visibly changes the rendering and ArrowLeft changes 100 to 99. Report `.cache/roadmap-review/M8/geometry-controls.json` has `errors: []`. Captures `shape-tap-<width>-<scene>.png` preserve the pointer result.

All six chapter interaction reports pass on both viewports, including the final name/spacing revisions. The final inventory has 52 scene captures (26 × two viewports), no switches in these chapters, no failed required requests or runtime errors. Every scene was visually inspected in contact sheets; individual patchwork views, treaty-city views, Hildesheim and the revised free-city/concluding views were also checked at full size. Labels intentionally suppressed by collision avoidance remain named in readable event lists, and the principal comparison scenes have individually readable labels. Mobile panels scroll to notes/source badges; no essential panel text is horizontally clipped. Timeline controls exercise 800/814, 936/962, 1648/1663, and 1803/1804/1806; Play, keyboard card activation, source links, notes, next/back within stories, reload deep links and embed pass in the interaction reports. Dedicated geometry/opacity checks also pass. The licence checker passed with 68 sources and 101 stories at this handoff snapshot. Final campaign registration/navigation and shared regression remain root responsibilities; this report does not claim those have passed.
