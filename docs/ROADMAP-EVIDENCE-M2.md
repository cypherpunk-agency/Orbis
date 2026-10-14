# M2 — Turkey: supplemental chapter evidence

## Integrating-session first release and campaign checks

The three first-release chapters are `tr-empire-pressure` (5 scenes), `tr-war-dissolution` (5) and `tr-republic` (6). `tools/build/turkey_first_release.py` writes their cited events and CShapes subsets deterministically. Five geometry observations preserve selected original topology arcs and exact snapshot dates: 1886-01-01, 1900-07-01, 1914-07-01, 1920-01-01 and 1925-01-01. They show legal-state observations, excluding dependencies and small changes, rather than occupation or battle control. Derived files retain CC BY-NC-SA 4.0; modern display names are corrected without changing source geometry.

Primary references checked: [TBMM chronology](https://www.tbmm.gov.tr/history/) for Ottoman constitutional/parliamentary events and the new assembly; [1876 constitutional text](https://en.wikisource.org/wiki/Ottoman_constitution_of_1876) for cited institutional articles; [National Army Museum Gallipoli account](https://www.nam.ac.uk/explore/gallipoli) for landings and evacuation; [USHMM Armenian genocide overview](https://encyclopedia.ushmm.org/content/en/article/the-armenian-genocide-1915-16-overview) for the 1915–1916 account and attributed range; [MEB chronology](https://meb.gov.tr/ataturk/Hayati/Kronoloji) for national struggle and republican milestones; [Lausanne political clauses](https://www.mfa.gov.tr/lausanne-peace-treaty-part-i_-political-clauses.en.mfa) and [exchange convention](https://www.mfa.gov.tr/lausanne-peace-treaty-vi_-convention-concerning-the-exchange-of-greek-and-turkish-populations-signed-at-lausanne_.en.mfa) for borders, unresolved Iraq settlement and compulsory exchange/exemptions. Sakarya is dated to its cited beginning, 23 August 1921. Locators are approximate; no source prose or restricted photographs are redistributed.

First-release desktop/mobile captures in `.cache/roadmap-review/{desktop,mobile}/tr_*.png` were reviewed. Republic's new independence-war scene was additionally inspected full size in both viewports. Reports `turkey-pressure-interactions.json`, `turkey-war-interactions.json` and `turkey-republic-interactions.json` each contain two viewport results and empty error arrays, covering dates, Play, cards, sources, switches, notes, navigation and embeds.

After integrating all seven chapters in manifest order, `node tools/review-campaigns.mjs turkey-history .cache/roadmap-review/turkey-campaign-final.json` passed at 1280×800 and 390×844: campaign landing/order, every chapter's first/last deep-link reload, every forward/back chapter boundary, final return to landing, and first-chapter embed. Registered licence check passed at the integration checkpoint (63 sources, 80 stories including Rome). Final shared-engine release regression remains a separate pending gate.

Review date and editorial cutoff: **14 October 2026**. This evidence covers the four chapters added after the root session's three-chapter first release. The first three files were not modified by this agent. Final campaign registration, campaign landing/next/back checks and release acceptance remain the integrating session's responsibility.

## Deliverables and reproduction

| ID | Scenes | Representation |
|---|---:|---|
| `tr-anatolia` | 6 | Located archaeological sites and historical centres: Göbekli Tepe, Hattusha, Greek/Roman Ephesus, Byzantine Constantinople, Armenian Ani, Seljuk Konya and Ottoman Bursa |
| `tr-ottoman-world` | 6 | Early capital/hinterland, conquest, wider empire, provincial production, dated Sinan commissions and layered architecture |
| `tr-changing-republic` | 7 | Institutional events, national urban-share timeline/line chart, labour migration relationship, dated Kurdish-community rights reporting, presidential-system transition and 2023 earthquake epicentre |
| `tr-world` | 6 | Straits, NATO, Cyprus, Germany, EU accession sequence and a dated Syria refuge/return account |

Run `python tools/build/turkey_remaining.py`. It deterministically writes these stories, four cited editorial event datasets and one small Turkey-only World Bank urban-share subset. It does not fetch or overwrite the first three chapters, index, campaign, source register or licence table.

Run `python tools/build/turkey_review.py` with the local quiet threaded server available; it defaults to `http://127.0.0.1:8767/` and respects `ORBIS_BASE_URL`. It invokes `tools/shoot.mjs` at **1280×800** and **390×844**, plus `tools/review-interactions.mjs` in both viewports. One browser process runs at a time. Outputs are under `.cache/roadmap-review/M2/<story>/`; screenshots and runtime logs are local evidence, not deployed assets.

The original 8766 server stopped accepting requests after its request-output buffer filled. A concurrent early review also exposed the screenshot script's fixed startup delay. The root session added readiness waits and supplied the quiet threaded 8767 server. These infrastructure failures were not counted as passing reviews. A media object/array schema error in the urban scene was corrected in the generator and regenerated before final review.

## Sources, coverage and redistribution

All new narrative prose is original factual annotation; **no institutional article prose, photographs, scans or source PDFs are redistributed**. Editorial locators use the existing `editorial` source. The urban subset retains the existing `wb-wdi` source and **CC BY 4.0** metadata. Existing Natural Earth base geography remains public domain. No new source registration is proposed.

Every substantive scene has a numbered source reference in its story notes. Event cards contain their own source URL. Approximate site/city locators are contextual annotations, not surveyed footprints or measured migration routes. The approved located-event historical-geometry fallback is used explicitly. No new historical boundary, ethnic polygon, occupation area or continuous front was invented.

| Claims | Primary or authoritative evidence | Limits |
|---|---|---|
| Göbekli Tepe tenth/ninth millennia BC; Hittite Hattusha; Hellenistic/Roman Ephesus | [UNESCO Göbekli Tepe](https://whc.unesco.org/en/list/1572/), [Hattusha](https://whc.unesco.org/en/list/377/), [Ephesus](https://whc.unesco.org/en/list/1018/) | Archaeological-site locators; no reconstruction of coastlines or empire extents |
| Byzantine monuments; Armenian Bagratid Ani and later dynasties; Seljuk Konya; early Ottoman Bursa | [UNESCO Istanbul](https://whc.unesco.org/en/list/356/), [Ani](https://whc.unesco.org/en/list/1518/), [Konya tentative-list submission](https://whc.unesco.org/en/tentativelists/1404/), [Bursa and Cumalıkızık](https://whc.unesco.org/en/list/1452/) | Konya is a national tentative-list submission, not an inscribed World Heritage property; the story identifies the description's provenance |
| 1453 conquest, Selim I's expansion, regional production and cultural traditions | [The Met: Ottomans before 1600](https://www.metmuseum.org/essays/the-art-of-the-ottomans-before-1600) | Schematic selected-city view, no precise territorial snapshots |
| Süleymaniye 1550–1557; Selimiye 1568–1574 | [The Met: age of Süleyman](https://www.metmuseum.org/essays/the-age-of-suleyman-the-magnificent-r-1520-1566) | Construction-period endpoints, not precise inauguration dates |
| 1960 coup, 1971 memorandum, 1980 coup, constitutional change | [Grand National Assembly history](https://www.tbmm.gov.tr/history/), [OSCE 2018 election report](https://cdn.osce.org/sites/default/files/f/documents/9/4/397046_0.pdf) | National institutional account, not regional political support |
| Urban share 23.43% in 1960 and 89.34% in 2024; city context | Cached `data/atlas/SP.URB.TOTL.IN.ZS.json` ([indicator](https://data.worldbank.org/indicator/SP.URB.TOTL.IN.ZS?locations=TR)), [World Bank urbanization review](https://www.worldbank.org/en/country/turkey/publication/turkey-urbanization-review) | National definitions and UN World Urbanization Prospects revision; not a constant built-up-area or city population measure. Retains provider as-of 2026-10-08/retrieved 2026-10-14 and 1960–2025 observations |
| 1961 recruitment relationship | [German Foreign Office retrospective](https://www.auswaertiges-amt.de/de/aussenpolitik/anwerbeabkommen/2493338) | Bonn/Istanbul are reference points, not actual migrant origins or routes |
| July 2015–December 2016 southeastern rights concerns, Kurdish displacement, Nusaybin and Diyarbakır | [OHCHR report](https://www.ohchr.org/Documents/Countries/TR/OHCHR_South-East_TurkeyReport_10March2017.pdf), corroborated directly in [UNRIC March 2017 library newsletter, page 9](https://unric.org/en/wp-content/uploads/sites/15/2018/12/libnews-march2017.pdf) | OHCHR endpoint returned HTTP 403; the UNRIC PDF was downloaded locally and its official synopsis read. Allegations are attributed, no casualty estimate or contemporary ethnic/control map |
| 6 February 2023 M7.8 epicentre | [USGS event](https://earthquake.usgs.gov/earthquakes/eventpage/us6000jllz/executive) | USGS epicentre 37.032° E / 37.226° N; no damage/casualty surface |
| Montreux 1936; Turkey/Greece NATO accession 1952 | [NATO's historical account](https://www.nato.int/cps/en/natohq/declassified_191048.htm) | Modern country shapes expressly identified; no Cold War deployment map |
| Cyprus coup/landings in July 1974; 1983 secession ruling | [UNFICYP historical account](https://unficyp.unmissions.org/en/events-summer-1974), [Security Council resolution 541](https://digitallibrary.un.org/record/58970?v=pdf) | No occupation boundary. Nicosia locates the island, not the UN adoption site |
| EU candidate 1999, negotiations 2005, effective standstill 2018 | [Council of the EU](https://www.consilium.europa.eu/en/policies/turkiye/) | Institutional locators; candidate status is expressly distinguished from membership |
| Growing demand for voluntary Syrian return | [UNHCR 8 December 2025 account](https://www.unhcr.org/tr/en/news/press-releases/unhcr-historic-return-displaced-syrians-presents-opportunity-and-urgent) | No asserted total or condition at the October 2026 cutoff; the source observation date appears in scene prose |

## Final checks

The final sequential 8767 review completed successfully: **all eight desktop/mobile screenshot runs reported `no errors`; all four interaction runs returned two viewports and empty error arrays**. All 25 scenes were visually inspected in both sizes, including the corrected urban line chart and the filtered Sinan timeline. All four chapter first-scene embed checks passed. The interaction reports record timeline endpoints/interior labels, Play advancement, event-card keyboard activation/source links, notes expansion and scene Next/Back navigation. No horizontal overflow was reported. Campaign chapter-to-chapter navigation remains a separate integrating-session gate; unlisted-story checks do not prove it.

`node tools/check-licences.js` passed at the supplemental-chapter checkpoint (62 sources, 70 then-registered stories). The scoped `git diff --check` passed. `.cache/roadmap-review/M2/data-validation.json` records IDs/counts, file sizes, source/as-of metadata, event availability at timeline start/interior/end and numeric checks. The five added datasets are 1.1–3.7 KB each. All urban values are finite or explicit nulls, years are unique and ordered, and checked observations are 23.43% (1960), 52.79% (1992), 89.34% (2024).

Local first-release evidence is owned by the integrating session. This supplemental report supports the four added chapters and does not independently declare the full M2 campaign accepted.

Campaign order for integration: `tr-anatolia`, `tr-ottoman-world`, `tr-empire-pressure`, `tr-war-dissolution`, `tr-republic`, `tr-changing-republic`, `tr-world`.

Known visual limits: the Natural Earth map is intentionally broad context. Nearby city/monument markers can share pixels and some labels are suppressed by map decluttering; narrative names and source notes remain accessible. Mobile panels scroll to reveal lower timelines, chart, source links and navigation. These are selected geographic accounts, not exhaustive histories of all communities, sites or provinces.
