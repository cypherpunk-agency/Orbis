# M5 — European Union chapter evidence

Reviewed on **14 October 2026**, matching the frozen editorial cutoff. This report supports the six required chapter files. Index/campaign registration and final campaign navigation are owned by the integrating session; unlisted chapter reviews alone do not establish those gates.

## Fixed deliverables

| ID | Scenes | Required geographic content |
|---|---:|---|
| `eu-growth` | 6 | ECSC/EEC foundations, successive enlargement timelines, EU27 merged group outline |
| `eu-clubs` | 5 | Overlapping EU/euro/Schengen hatches, Bulgaria's 2026 euro adoption, Denmark's opt-out, 2025 Schengen land participation, membership switch |
| `eu-budget` | 5 | Defined financing, ordinary/NGEU/combined expenditure switch, signed derived comparison, 2021–2025 timeline, administrative allocation geography |
| `eu-regions` | 5 | Same-year/unit NUTS2 comparison, regional policy thresholds, sourced national cohesion expenditure, GDP accounting cautions |
| `eu-brexit` | 5 | Referendum/notification cards, regional vote contrasts, dated 28→27 member change, Ireland/Northern Ireland context, relocated agencies |
| `eu-candidates` | 5 | Nine dated candidates, Western Balkans/applicant distinction, July 2026 accession conferences, stalled paths, candidate geography beside EU outline |

Total: **31 substantive scenes**. No required chapter was omitted. Final campaign order: `eu-growth`, `eu-clubs`, `eu-budget`, `eu-regions`, `eu-brexit`, `eu-candidates`.

## Sources and representation

Significant claims have scene-numbered references in story notes. Brexit event cards carry individual source links. Institutional/city/region reference points are approximate locators, not surveyed footprints or observed movements.

- Memberships and original narrative annotations use the existing `editorial` source. [Official EU profiles](https://european-union.europa.eu/principles-countries-history/eu-countries_en) and the [Council enlargement list](https://www.consilium.europa.eu/en/topics/eu-enlargement/) were checked at the cutoff. [ECB's 1 January 2026 release](https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.pr260101~c830245e42.en.html) confirms Bulgaria as the 21st euro member. The [Council Schengen account](https://www.consilium.europa.eu/policies/schengen-area/) and [12 December 2024 decision](https://www.consilium.europa.eu/en/press/press-releases/2024/12/12/schengen-council-decides-to-lift-land-border-controls-with-bulgaria-and-romania/) support 29 countries after land controls ended on 1 January 2025. The Schengen data starts with a **1 January 2024 observation** for the 27 already participating countries, not invented accession dates.
- EU/EEC timelines retain exact May 2004 and July 2013 entry dates. The UK interval ends on 1 February 2020, following departure at midnight CET on 31 January. [Council's withdrawal account](https://www.consilium.europa.eu/en/policies/the-eu-uk-withdrawal-agreement/) supports notification, transition, Windsor Framework and agency relocation. [Electoral Commission results](https://www.electoralcommission.org.uk/research-reports-and-data/our-reports-and-data-past-elections-and-referendums/results-and-turnout-eu-referendum) support rounded valid-vote shares. Regional markers are not ward-level election geometry.
- Historical membership colours use **today's country geometry for context**, not historical sovereign borders. West Germany's founding role is stated expressly; modern Germany is a locator. The dated EU27 merged outline is a public-domain Natural Earth subset, using the existing `naturalearth` source. It preserves shared topology and suppresses internal EU borders. Special overseas/treaty territorial applications are not reconstructed.
- `eu-budget` is a newly registered optional Commission source. [Spending/revenue page](https://commission.europa.eu/strategy-and-policy/eu-budget/long-term-eu-budget/2021-2027/spending-and-revenue_en) identifies the **2000–2025 workbook released 29 September 2026**. The [Commission legal notice](https://commission.europa.eu/legal-notice_en) permits reuse under **CC BY 4.0 unless otherwise indicated**. The original workbook was downloaded directly and inspected; no individual restrictive notice or third-party data notice was identified. Only reduced/rounded 2021–2025 country data and named arithmetic ship, with source and modifications acknowledged. Raw XLSX remains ignored local cache.
- The existing `eurostat` source covers the selected NUTS2 GDP comparison. [Eurostat's 11 February 2025 release](https://ec.europa.eu/eurostat/en/web/products-eurostat-news/w/ddn-20250211-2) supplies frozen **2023 GDP/head PPS, EU27=100** observations. [Eurostat reuse policy](https://ec.europa.eu/eurostat/help/copyright-notice) permits commercial/noncommercial reuse with attribution; the subset notes Orbis's modifications and Eurostat's non-responsibility. No third-party restricted-country data are included.
- Approved EU geometry fallback: **located regional symbols and a regional comparison chart**, with the same eight NUTS2 values. No NUTS polygons or invented regional funding allocations were added. The [Commission cohesion programming account](https://cohesiondata.ec.europa.eu/stories/s/Outcome-of-2021-2027-programming-cohesion-policy/d6tf-zqvc/) supports the 75%/100% category thresholds. Regional 2023 GDP does not retroactively determine the official 2021–2027 eligibility classification. National 2025 cohesion expenditure is explicitly a separate country-level comparison.
- Candidate/negotiation status is dated, rather than presented as an accession forecast. A [14 July 2026 Council account](https://www.consilium.europa.eu/en/press/news/20260714-four-accession-conferences-in-one-day/) supports the Ukraine/Moldova external-relations conferences. [Turkey](https://www.consilium.europa.eu/en/policies/turkiye/) and [Georgia](https://www.consilium.europa.eu/en/policies/georgia/) pages explain their different halted processes; candidate status alone does not imply active negotiations. Kosovo's base-map depiction does not settle recognition.

No institutional photographs, article prose, map scans or logos are redistributed.

## Budget definition and validation

Country financing = workbook `TOTAL Own resources` + `TOTAL Balances and adjustments` − `Customs duties`. Sugar levies are zero for the selected years. This represents VAT/GNI/plastics financing with adjustments, not customs collected at a member's ports.

Country expenditure = the country column of `TOTAL EXPENDITURE` + its `TOTAL NGEU` allocation. The country columns in the ordinary table exclude the separate earmarked/NGEU allocation. The derived signed comparison is **expenditure minus this defined financing**. It is not the Commission operating budgetary balance, household income, or the welfare benefit of EU membership.

The ordinary cohesion series uses exactly `Economic, Social and territorial cohesion`; it does not use the broader `Cohesion, Resilience and Values` heading or silently add NGEU.

For **each year 2021–2025**, all 27 selected ordinary, NGEU and cohesion country allocations reconcile to the workbook's EU27 allocation column within €0.02 million tolerance. This is different from the larger total containing earmarked/unallocated/non-EU columns. Evidence: `.cache/roadmap-review/M5/sources/budget-reconciliation.json`.

Checked 2025 examples, EUR million:

| Measure | Germany | France | Italy | Poland |
|---|---:|---:|---:|---:|
| Defined financing | 28,983.18 | 22,961.73 | 17,395.82 | 6,966.58 |
| Ordinary allocation | 12,212.70 | 16,391.30 | 13,258.05 | 13,180.30 |
| NGEU allocation | 345.41 | 2,244.35 | 10,161.62 | 2,396.86 |
| Derived expenditure minus financing | −16,425.06 | −4,326.08 | 6,023.85 | 8,610.58 |

For exact rounded output, use `data/history/eu/budget.json`; this displayed table is explanatory, not the acceptance assertion source.

## Browser evidence and checks

The sequential `python tools/build/eu_review.py` run on the quiet threaded `http://127.0.0.1:8767/` server completed with **no failures**: twelve desktop/mobile screenshot runs and six two-viewport interaction reports. It captures every scene and switch option at **1280×800** and **390×844** (78 canonical captures). Every scene and option was visually inspected. Timelines, Play, keyboard switches, event-card activation/source links, notes, scene next/back, direct reloads, horizontal overflow and first-scene embeds passed.

Manual review caught a silent empty-map bug in the original fixed-date outline scene: date bounds became years while a literal layer date stayed `YYYYMMDD`. The integrating session corrected shared date normalization and verified before/start/cutoff/end boundaries. Its evidence is `.cache/roadmap-review/fixed-dates.json`. The corrected growth and candidates outline scenes were recaptured and visually inspected in both viewports. The corrected growth scene-6 captures replace the earlier empty canonical captures.

`python tools/build/eu_verify_extra.py` passed in **both viewports with no errors**. `.cache/roadmap-review/M5/extra-review.json` asserts semantic membership counts at every selected timeline step: EU 9→10→12, 12→15, 25→27→28; euro 20→21→21; full Schengen 27→29→29; Brexit 28→27→27. It also asserts the EU27 outline legend, captures both required outlines with the latest engine and checks exact chart values. Scrolled mobile chart captures confirm budget and regional comparison readability below the initial panel fold. The first regional chart abbreviates its longest display label with an ellipsis; the full region name remains in scene prose and accessible chart text.

`python tools/build/eu_verify_data.py` passed: source/as-of/retrieval metadata, ordered years, 27 finite country series with five observations each, signed arithmetic, eight positive region values, valid coordinates, fixed IDs and 4–8 scene counts. **Cached input rebuilds are byte-identical.** Evidence: `.cache/roadmap-review/M5/data-validation.json`. New JSON files are 1.8–269 KB, below the 1 MB gate and within the 300 KB target.

`node tools/check-licences.js` passed at the final supplemental checkpoint (66 sources, 88 then-registered stories). Scoped `git diff --check` passed. Root registration changes will require their own final licence/scope/global/campaign checks; this report does not claim production deployment or final campaign acceptance.

## Reproduction

1. Run `python tools/build/eu_data.py`, then `python tools/build/eu_stories.py`. The data builder downloads the licensed workbook only if its named cache is absent; otherwise it uses the frozen cached snapshot. `openpyxl` is required.
2. Run `python tools/build/eu_verify_data.py` for metadata/arithmetic/count/rebuild checks.
3. Serve the repository locally with a quiet threaded server; set `ORBIS_BASE_URL` if it differs from port 8767.
4. Run `python tools/build/eu_review.py`, then `python tools/build/eu_verify_extra.py`. These tools use the installed Chrome/Playwright paths and one browser process at a time.
5. Run `python tools/build/eu_contacts.py` for manual contact sheets. Inspect canonical and scrolled captures; do not treat zero exit status alone as visual proof.

Limitations are named in scene prose/notes: current geography in historical membership views, partial region selection, approximate regional/city locators, national rather than invented regional money, nominal/cash accounting rather than welfare, dates and territorial exceptions in club membership, and procedural status rather than accession predictions.

## Coordinator integration

All six chapters registered in manifest order. `node tools/review-campaigns.mjs european-union .cache/roadmap-review/eu-campaign-final.json` passed both target viewports: landing/order, every first/last deep-link reload, all next/back chapter boundaries, final landing and first-chapter embed. `node tools/check-roadmap.mjs M1 M2 M3 M4 M5` passed (38 unique stories, 195 scenes, 60 dataset references). Source checker passed at registration (66 sources, 94 stories). Final shared regression remains pending.
