# M6 — World War II chapter evidence

Editorial cutoff and source review: 14 October 2026. Build with `python tools/build/ww2_history.py`; rebuild the retained cleared map assets with `python tools/build/ww2_history_maps.py` (network download is opt-in).

The eight required chapters contain 36 geographic scenes. This document describes chapter readiness; root owns index/campaign registration, campaign navigation, global regressions and the shared acceptance ledger before the complete M6 gate passes.

## Traceability and scope

Each chapter has a matching `data/history/ww2/<id>.json`, retrieval/coverage metadata and source-linked factual events. Story notes enumerate sources by scene heading and disclose supplementary evidence. Original factual synthesis uses the existing `editorial` source, rather than importing museum text or assigning a new licence to its websites. Event locations are rounded named-place references, never inferred fronts, camp perimeters or blast radii.

| Chapter | Scenes | Reviewed factual evidence | Geographic content |
|---|---:|---|---|
| `ww2-before` | 4 | ETH CShapes; USHMM Anschluss, Munich timeline and German–Soviet pact | 1 January 1938 diplomatic boundaries; Vienna, Munich and Moscow |
| `ww2-expansion` | 6 | USHMM Poland, Norway and France; Danish National Museum occupation/liberation; Norwegian government May 1945 account; US Army campaign summary and First Army Remagen history | Poland; four Denmark/Norway occupation-status snapshots; France; cleared western atlas; dated schematic Normandy–Paris–Remagen milestones; Bornholm exception |
| `ww2-east` | 4 | USHMM Soviet Union/Eastern Front; Deutsches Historisches Museum Leningrad | Minsk invasion reference, besieged Leningrad, Stalingrad and Berlin endpoint |
| `ww2-pacific` | 5 | NPS Pearl Harbor; US Navy Midway, Guadalcanal and Okinawa accounts; cleared US Army atlas | Hawaii, Midway, Solomons, original Allied-command map with Hawaii/Australia anchors, Okinawa |
| `ww2-holocaust` | 4 | USHMM Warsaw, Kyiv/Babyn Yar, Auschwitz and Holocaust introduction; UK National Archives Bergen-Belsen liberation report | Selected ghetto, mass-shooting site, killing centre and liberation site; explicit non-exhaustive coverage |
| `ww2-bombing` | 5 | Historic England Blitz; Coventry Cathedral; DHM Dresden; US National Archives Hiroshima/Nagasaki; 1946 Manhattan Engineer District primary report transcription for terrain context | Five located civilian bombing cases; dates and attackers, without invented destruction polygons or contested death estimates |
| `ww2-end` | 4 | US National Archives German surrender documents and VJ-Day records | Reims and Berlin signatures; Washington announcement, distinct from Tokyo Bay formal signing |
| `ww2-borders` | 4 | Potsdam agreement, State Department German state formation, ETH CShapes, Wrocław municipal historical account | Potsdam administration, Poland 1938/1950 comparison, two German states in 1950, population-transfer context |

## Occupation, movement and historical geometry

The Nordic occupation dataset has four exact dates: 9 April 1940 (Denmark occupied, Norway fighting); 10 June 1940 (both occupied); 5 May 1945 (Denmark's main liberation, Norway occupied); 8 May 1945 (both main liberation/capitulation dates). Denmark's Bornholm exception has its own scene. Country colours classify national status on explicitly declared modern reference outlines; they cannot assert every island's local control. Sources and precision are recorded in `occupationEvidence`.

The western movement contains three cited selected milestones: Normandy 6 June 1944, Paris 25 August 1944 and Remagen 7 March 1945. `movementEvidence` stores each waypoint/date/source. Connectors and interpolation are explicitly schematic, not a single unit's route. No invented daily front is drawn.

CShapes appears only as optional CC BY-NC-SA 4.0 diplomatic snapshots dated 1 January 1938 and 1 January 1950. Neither the postwar comparison nor German state map is labelled a 1945 occupation-zone map. Small historical changes and intervening control cannot be inferred from these two dates. Upstream consolidated alias labels (such as Italy/Sardinia) are suppressed; explicit dated selected-place labels identify Austria, Czechoslovakia, Germany, Poland and the two German states where needed.

## Cleared atlas assets and fallbacks

The `us-army-atlas` registry/licensing entry was added by root. The University of Texas [WWII catalogue](https://maps.lib.utexas.edu/maps/historical/history_ww2.html) identifies these maps as US Army Center of Military History cartography from *American Military History* (1989); its [FAQ](https://maps.lib.utexas.edu/maps/faq.html) explains the public-domain maps and marked exceptions. Both downloaded scans were inspected, including their attribution areas, and retained unmodified. Credit is supplied to the University of Texas Libraries and Army CMH.

`map-provenance.json` records original URLs, dates, dimensions, SHA-256 hashes and control points. Northern Europe retains a second-order overview fit using 11 rounded city controls (mean residual 4.42 pixels, maximum 6.38 pixels). Those fitted-control residuals are not an independent accuracy guarantee. The overlay's bbox is [-6, 46, 16, 55]; its original arrows span June 1944–May 1945 and never represent one simultaneous front. Opacity permits comparison with reference geography.

The Pacific fit was rejected (mean 21.78 pixels, maximum 44.5 pixels). That chapter displays the original 1 August 1942 scan as panel media, with an original-file link and attribution. Printed lines are Allied command boundaries, explicitly distinguished from Japanese occupation. No Pacific warp is shipped or used. Modern anchors locate Hawaii and Australia without fabricating a central-ocean event.

Current West Point atlases require permission to reprint and were excluded. Candidate Library of Congress US Army wartime maps had promising item-level rights statements, but attempted downloads returned 403; they were excluded. These exclusions prompted the documented Army/UT catalogue fallback, rather than unverified imagery or invented geometry.

## Atrocity presentation

The Holocaust scenes use static muted points, sourced prose, site names and dates. They contain no decorative pulses, victim scaling, speculative deportation lines or imported victim photographs. Six million Jewish victims is attributed to USHMM as Holocaust context, not allocated among these selected sites; other targeted victims are acknowledged. The point set is explicitly incomplete. Bombing scenes also avoid precision claims for disputed totals, blast circles and impact grids.

## Verification

Review artifacts are under `.cache/roadmap-review/M6/<chapter>/`. The standard scene captures include every scene and both Poland switch options at 1280×800 and 390×844. Each chapter's `interactions.json` tests both viewports: scene deep links, navigation, source-note expansion, keyboard event-card opening/closing, timeline controls where present, switch focus/activation, overflow and embed mode. Additional assertions/screenshots under `specific/` exercise all four Nordic dates, category counts and country taps, atlas opacity endpoints, and the loaded Pacific media/credit/original link.

Visual review corrected the initially small western overlay, added essential small-state/reference labels, suppressed historically misleading auto aliases, and removed a misleading central-ocean event from the command-map scene. A targeted media assertion caught and corrected an object-versus-array error that had silently hidden the original image. The Pacific image requires ordinary panel scrolling on mobile; its loaded image, caption, credit and original link now pass the actual visible-media assertion. These are finite selected cases and overview cartography, not a complete WWII battle/control database.

The completed data audit records 36 scenes, 76 required scene/switch screenshots, eight two-viewport interaction reports with no errors, two verified original-map SHA-256 hashes, valid local references and 4–8 scenes per chapter. The additional two-viewport occupation/opacity/media report passes with no errors and has 14 inspected screenshots. The licence checker passes (67 sources, 101 stories at time of final check); targeted whitespace/diff checking passes. Atlas assets are 237,615 and 290,086 bytes for the retained original JPEGs and 134,562 bytes for the overview WebP. Final affected scene captures and controls were repeated after the label/media corrections.
