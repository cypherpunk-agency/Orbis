# Current scene-date audit: finite M1–M8 scope

Audited 14 October 2026 against upstream `78c1fd6`, the scene-date additions in `39d6064`, and the current working tree. This is a focused editorial review of newly introduced `scene.when` labels, not a new source import or a replacement for the chapter source audits.

Scope: all 59 unique finite stories, with 199 explicit `when` labels. Inspected each label with its scene narrative, notes, fixed layer date or timeline and the referenced shipped dataset metadata. Historical event dates follow the existing cited editorial records; observation, publication and retrieval dates were distinguished. No engine or story files were edited by this auditor.

## Findings requiring correction

1. `whales`, scene 1: `1700s–1920s` is the broad voyage-catalogue span from the notes, whereas its displayed layer is the logbook-position raster. `data/grids/whales.json` explicitly dates those observations to **1780s–1920s**. Use the narrower mapped-observation span for the new label.
2. `fame`, scene 5: `1500–1980s` follows only one sentence's narrative comparison. The visible country map is labelled **births 1950–2018**, and the accompanying line chart includes the **1990** birth-decade frame in `data/people/fame-women-trend.json`. Use a label covering the represented birth cohorts (for example **Births 1500–2018**) or omit the single scene label and retain the two figures' explicit windows. The existing quantitative narrative is unchanged.

Root corrected both story labels to the recommended observation spans. The current-renderer regression checks their current story hashes; any captures made before those corrections must be superseded. The US and Ukraine builders also retain the reviewed explicit display dates when regenerated. This editorial correction does not by itself claim runtime success.

## Date distinctions checked

- `friends`: Jan 2026 is the observation snapshot, supported by `data/people/sci.json` (`asOf` 2026-01-25, active-user window preceding that date), rather than the October 2026 retrieval.
- `roman-roads`: circa 300 BC–AD 300 describes the accumulated ancient network; the 2024 static version and September 2025 publication metadata do not describe a Roman observation year. It is explicitly not a network simultaneously complete on one date.
- `fame`: 3500 BC–2018 is the biographical coverage, rather than the research paper's 2022 publication.
- `countryside`: 2000–2019 describes the summed annual migration rates. The 2025 population weighting is disclosed separately and does not turn those migration estimates into 2025 observations.
- `night-light-change`: 2012 and 2016 are composite observation years; metadata separately describes the 2017 release.
- `empty-skies`: labels 2019/2020/2021 match the selected World Bank observations, rather than its 2026 source-update date.
- `refugees` and `ua-refugees`: annual stock labels refer to end 2025; the IOM missing-migrant scene refers to 2014–2024. None is labelled as an October 2026 observation.
- `eu-regions`: 2023 identifies the GDP observations in the February 2025 release. Its 2021–2027 policy scene explicitly distinguishes programme eligibility from the 2023 comparison.
- `eu-budget`: 2025 denotes expenditure/financing observations, rather than the 2026 workbook release.
- `eu-growth`, `eu-clubs`, `eu-candidates`: Oct 2026 denotes the explicitly frozen institutional snapshot. The July 2026 accession-conference scene and Turkey's standstill since 2018 agree with their named dated references.
- `tr-republic`, scene 2: 24 July 1923 labels the treaty event. The text expressly identifies its geometry as 1 January 1925 and says it does not establish that all borders were settled at Lausanne.
- `ww2-borders`, scene 3: 1949 labels the founding of the German states. The narrative expressly dates the displayed diplomatic snapshot to 1 January 1950. The Poland comparison is labelled 1938–1950.
- `ua-energy` and `ua-snapshot`: NASA's Kyiv comparison remains Jan–May 2022; UCDP timelines stop at August 2026 and annual displacement data stops in 2025. Publication/retrieval/cutoff is not substituted for these observations.
- `hre-patchwork`: circa 1789 labels the source-defined territorial reconstruction; 1796 labels the Reilly archival portrayal. The source SVG's 2021 revision and the modern georeferencing are separate provenance dates.
- Roman BC events preserve astronomical internal years: 146 BC corresponds to -145, 44 BC to -43 and 27 BC to -26. Conventional BC labels do not copy the raw negative year as a BC magnitude.

Mixed historical context is explicit: `tr-anatolia` scene 6 dates Seljuk Konya to the 12th–13th centuries and compares it with later Ottoman Bursa; `eu-candidates` scene 4 dates Turkey's standstill from 2018 while separately stating Georgia's 2024 halt. These are narrative period labels, not assertions that every referenced place or event shares one observation date.

## Complete label inventory

Blank labels remain blank where the story has no single time anchor; timeline scenes retain their own spans. The inventory is the inspected pre-correction state.

| Story | Explicit scene labels (one-based scene number) |
| --- | --- |
| `whales` | 1: 1700sâ€“1920s; 5: Sep 1871; 6: 1840sâ€“1920s |
| `launches` | 2: Late 1960sâ€“1991; 3: 2001â€“2017; 4: 2025; 5: 2010sâ€“2025; 6: 2015â€“2025 |
| `friends` | 1: Jan 2026; 2: Jan 2026; 3: Jan 2026; 4: Jan 2026; 5: Jan 2026; 6: Jan 2026; 7: Jan 2026 |
| `roman-roads` | 1: c. 300 BCâ€“AD 300; 2: c. 300 BCâ€“AD 300; 3: c. 300 BCâ€“AD 300; 6: c. 300 BCâ€“AD 300 |
| `colonies` | 2: 1462â€“1975; 3: 1500sâ€“1820s; 4: c. 1880â€“1960s |
| `night-light-change` | 1: 2012â€“2016; 2: 2012â€“2016; 3: 2012â€“2016; 4: 2012â€“2016; 5: 2012â€“2016 |
| `empty-skies` | 1: 2019; 3: 2020; 4: 2020â€“2021; 5: 2019â€“2021 |
| `fame` | 1: 3500 BCâ€“2018; 5: 1500â€“1980s |
| `refugees` | 2: 2025; 3: 2025; 5: 2025; 7: 2014â€“2024 |
| `countryside` | 1: 2000â€“2019; 2: 2000â€“2019; 3: 2000â€“2019; 4: 2000â€“2019; 5: 2000â€“2019; 6: 2000â€“2019 |
| `tr-anatolia` | 1: 10thâ€“9th millennium BC; 2: 2nd millennium BC; 3: Hellenistic and Roman eras; 4: Byzantine era; 5: 10thâ€“11th centuries; 6: 12thâ€“13th centuries |
| `tr-ottoman-world` | 2: 1453; 3: 16th century |
| `tr-empire-pressure` | 1: 1886 |
| `tr-war-dissolution` | 1: 1914; 3: 1915â€“1916 |
| `tr-republic` | 2: 24 Jul 1923; 3: Jan 1923; 6: 1925 |
| `tr-changing-republic` | 1: 27 May 1960; 4: 1961; 5: Jul 2015â€“Dec 2016; 6: 2017â€“2018; 7: 6 Feb 2023 |
| `tr-world` | 1: Since 1936; 2: Feb 1952; 4: 1961; 6: Dec 2025 |
| `rome-carthage` | 4: 146 BC |
| `rome-expansion` | 1: To 44 BC |
| `rome-frontier` | 3: 2nd century AD |
| `rome-split` | 1: AD 293; 4: AD 402 |
| `rome-fall` | 2: After AD 476 |
| `rome-legacy` | None; dates remain in timeline, figure labels or text |
| `us-colonies` | 1: 1607; 3: 1776; 4: 1783 |
| `us-expansion` | 1: 1803; 3: 1845â€“1848; 4: 1846; 5: 1867 |
| `us-indigenous-land` | 1: 1830; 2: 1835; 3: 1838â€“1839; 4: 1887 |
| `us-statehood` | 1: 1787; 2: 1850; 3: Jan 1959; 4: Aug 1959 |
| `us-civil-war` | 1: Late 1861; 2: 12 Apr 1861; 4: 1863; 5: 9 Apr 1865 |
| `us-frontier` | 1: 1862; 2: 1863; 3: May 1869; 4: 10 May 1869 |
| `us-immigration` | 1: 19th century; 2: 1892â€“1954; 3: 1882; 4: 1910â€“1940 |
| `us-elections` | 1: 1860; 2: 1860; 3: 2020; 4: 2020; 5: 2020 |
| `us-abroad` | 1: 1898; 2: 1898; 3: 1898; 4: 1949 |
| `eu-growth` | 1: 1951â€“1952; 2: 1957â€“1958; 6: Oct 2026 |
| `eu-clubs` | 1: Oct 2026; 3: Oct 2026; 5: Oct 2026 |
| `eu-budget` | 1: 2025; 2: 2025; 3: 2025; 5: 2025 |
| `eu-regions` | 1: 2023; 2: 2023; 3: 2021â€“2027; 4: 2025 |
| `eu-brexit` | 2: Jun 2016 |
| `eu-candidates` | 1: Oct 2026; 2: Oct 2026; 3: Jul 2026; 4: Since 2018 |
| `ww2-before` | 1: 1 Jan 1938; 2: 12 Mar 1938; 3: 29â€“30 Sep 1938; 4: 23 Aug 1939 |
| `ww2-expansion` | 1: Sep 1939; 3: Jun 1940; 4: Jun 1944â€“May 1945; 6: May 1945 |
| `ww2-east` | 1: 22 Jun 1941; 3: Janâ€“Feb 1943; 4: Spring 1945 |
| `ww2-pacific` | 1: 7 Dec 1941; 2: Jun 1942; 3: 7 Aug 1942; 4: 1 Aug 1942; 5: 1 Apr 1945 |
| `ww2-holocaust` | 1: 1940; 2: 29â€“30 Sep 1941; 3: 1942; 4: 15 Apr 1945 |
| `ww2-bombing` | 1: 7 Sep 1940; 2: 14 Nov 1940; 3: 13â€“14 Feb 1945; 4: 6 Aug 1945; 5: 9 Aug 1945 |
| `ww2-end` | 1: 7 May 1945; 2: 8 May 1945; 3: 14 Aug 1945; 4: 2 Sep 1945 |
| `ww2-borders` | 1: 1945; 2: 1938â€“1950; 3: 1949; 4: 1945 |
| `ua-2014` | 1: Mar 2014; 2: 2014â€“2022; 3: 2014â€“2022; 4: 2014â€“2021 |
| `ua-invasion` | 1: 24 Feb 2022; 4: 2 Mar 2022 |
| `ua-counteroffensives` | 1: Mar 2022; 2: 2022; 3: Nov 2022; 4: 2022â€“2023 |
| `ua-front` | 3: Jun 2023 |
| `ua-energy` | 1: Jan 2022; 2: Mar 2022; 3: May 2022; 4: Jun 2023 |
| `ua-refugees` | 1: End of 2025; 3: End of 2025 |
| `ua-snapshot` | 3: Janâ€“May 2022 |
| `hre-charlemagne` | 1: c. 790â€“800; 2: 800; 4: 936 |
| `hre-1000` | 1: 936; 3: c. 1000; 4: c. 1000 |
| `hre-patchwork` | 1: 1356; 2: From 1663; 3: c. 1789; 4: c. 1789; 5: 1796; 6: 1796 |
| `hre-westphalia` | 1: 1648; 2: 1648; 4: 1796 |
| `hre-end` | 1: 1803; 2: 1804; 3: 1806 |
| `hre-after` | 1: 1815; 2: 1815; 3: 1815 |

No other contradictory newly added date was identified within this focused scope. This conclusion does not assert fresh verification of remote sources or of runtime rendering; those are covered by the milestone evidence and current regression.
