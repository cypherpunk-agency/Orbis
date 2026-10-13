#!/usr/bin/env python3
"""Abolition of the death penalty -> data/rights/death_penalty.json (sets for `since` and `categories` layers).

Facts typed by hand (no download). Sources:
- Status at 31 Dec 2025: Amnesty International, Death Sentences and Executions 2025 (ACT 50/0778/2026), Annex II.
- Recorded executions in 2025: same report, Annex I.
- Year of abolition for all crimes (A) and for ordinary crimes (AO): Amnesty International, List of abolitionist and
  retentionist countries (31 December 2008), ACT 50/002/2009, for countries that had abolished by then.
- Later abolitions: year the abolishing law, constitution or ruling took effect, as reported by Amnesty's annual
  death penalty reports (see LATER below); Lebanon: parliamentary vote of 11 August 2026 (AP).
"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Amnesty 2008 list, "Date (A)" for all crimes
A2008 = {"ALB":2007,"AND":1990,"AGO":1992,"ARG":2008,"ARM":2003,"AUS":1985,"AUT":1968,"AZE":1998,"BEL":1996,"BTN":2004,
 "BIH":2001,"BGR":1998,"KHM":1989,"CAN":1998,"CPV":1981,"COL":1910,"COK":2007,"CRI":1877,"CIV":2000,"HRV":1990,"CYP":2002,
 "CZE":1990,"DNK":1978,"DJI":1995,"DOM":1966,"ECU":1906,"EST":1998,"FIN":1972,"FRA":1981,"GEO":1997,"DEU":1987,"GRC":2004,
 "GNB":1993,"HTI":1987,"VAT":1969,"HND":1956,"HUN":1990,"ISL":1928,"IRL":1990,"ITA":1994,"LIE":1987,"LTU":1998,"LUX":1979,
 "MKD":1991,"MLT":2000,"MUS":1995,"MEX":2005,"MDA":1995,"MCO":1962,"MNE":2002,"MOZ":1990,"NAM":1990,"NPL":1997,"NLD":1982,
 "NZL":1989,"NIC":1979,"NOR":1979,"PAN":1922,"PRY":1992,"PHL":2006,"POL":1997,"PRT":1976,"ROU":1989,"RWA":2007,"WSM":2004,
 "SMR":1865,"STP":1990,"SEN":2004,"SRB":2002,"XKX":2002,"SYC":1993,"SVK":1990,"SVN":1989,"ZAF":1997,"ESP":1995,"SWE":1972,
 "CHE":1992,"TLS":1999,"TUR":2004,"TKM":1999,"UKR":1999,"GBR":1998,"URY":1907,"UZB":2008,"VEN":1863}
# Listed by Amnesty in 2008 as abolitionist with no date: no death penalty since independence (Factbook independence year)
SINCE_INDEPENDENCE = {"KIR":1979,"MHL":1986,"FSM":1986,"PLW":1994,"SLB":1978,"TUV":1978,"VUT":1980}
# Abolished for all crimes after 2008
LATER = {"BDI":2009,"TGO":2009,"BOL":2009,"GAB":2010,"KGZ":2010,"LVA":2012,"COG":2015,"FJI":2015,"MDG":2015,"SUR":2015,
 "BEN":2016,"NRU":2016,"GIN":2017,"MNG":2017,"TCD":2020,"KAZ":2021,"SLE":2021,"CAF":2022,"PNG":2022,"ZMB":2022,"LBN":2026}
# Abolished for ordinary crimes first ("Date (AO)", Amnesty 2008, plus later)
AO = {"ALB":2000,"ARG":1984,"AUS":1984,"AUT":1950,"CAN":1976,"CYP":1983,"DNK":1933,"FIN":1949,"GRC":1993,"ITA":1947,"MLT":1971,
 "NPL":1990,"NLD":1870,"NZL":1961,"NOR":1905,"PRT":1867,"SMR":1848,"ZAF":1995,"ESP":1978,"SWE":1921,"CHE":1942,"TUR":2002,
 "GBR":1973,"SLB":1966,"BOL":1997,"FJI":1979,"KAZ":2007,"KGZ":2007,"LVA":1999,
 # still abolitionist for ordinary crimes only at the end of 2025
 "BRA":1979,"CHL":2001,"SLV":1983,"ISR":1954,"PER":1979,"GTM":2017,"BFA":2018,"GNQ":2022,"ZWE":2024}

allc = {**A2008, **SINCE_INDEPENDENCE, **LATER}
ordinary = {k: ([v, allc[k]] if k in allc else v) for k, v in AO.items()}

# Amnesty Annex II, status at 31 Dec 2025 (Lebanon moved to "all" after its August 2026 vote)
STATUS_ALL = ["ALB","AND","AGO","ARG","ARM","AUS","AUT","AZE","BEL","BEN","BTN","BOL","BIH","BGR","BDI","CPV","KHM","CAN",
 "TCD","CAF","COL","COG","COK","CRI","CIV","HRV","CYP","CZE","DNK","DJI","DOM","ECU","EST","FJI","FIN","FRA","GAB","GEO",
 "DEU","GRC","GIN","GNB","HTI","HND","HUN","ISL","IRL","ITA","KAZ","KIR","XKX","KGZ","LVA","LIE","LTU","LUX","MDG","MLT",
 "MHL","MUS","MEX","FSM","MDA","MCO","MNG","MNE","MOZ","NAM","NRU","NPL","NLD","NZL","NIC","NIU","MKD","NOR","PLW","PAN",
 "PNG","PRY","PHL","POL","PRT","ROU","RWA","WSM","SMR","STP","SEN","SRB","SYC","SLE","SVK","SVN","SLB","ZAF","ESP","SUR",
 "SWE","CHE","TLS","TGO","TUR","TKM","TUV","UKR","GBR","URY","UZB","VUT","VAT","VEN","ZMB"]
STATUS_ORD = ["BRA","BFA","CHL","SLV","GNQ","GTM","ISR","PER","ZWE"]
STATUS_PRACTICE = ["DZA","BRN","CMR","ERI","SWZ","GHA","GRD","KEN","LAO","LBR","MWI","MDV","MLI","MRT","MAR","ESH","NER",
 "RUS","KOR","LKA","TJK","TZA","TON","TUN"]   # Amnesty lists "Morocco/Western Sahara" as one entry
STATUS_RETAIN = ["AFG","ATG","BHS","BHR","BGD","BRB","BLR","BLZ","BWA","CHN","COM","CUB","COD","DMA","EGY","ETH","GMB","GUY",
 "IND","IDN","IRN","IRQ","JAM","JPN","JOR","KWT","LBN","LSO","LBY","MYS","MMR","NGA","PRK","OMN","PAK","PSE","QAT","KNA",
 "LCA","VCT","SAU","SGP","SOM","SSD","SDN","SYR","TWN","THA","TTO","UGA","ARE","USA","VNM","YEM"]
assert len(STATUS_ALL) == 113 and len(STATUS_ORD) == 9 and len(STATUS_PRACTICE) == 24 and len(STATUS_RETAIN) == 54, \
    (len(STATUS_ALL), len(STATUS_ORD), len(STATUS_PRACTICE), len(STATUS_RETAIN))
assert set(STATUS_ALL) - {"NIU"} == set(allc) - {"LBN"}, (set(STATUS_ALL) ^ set(allc))
status = {**{k: "retain" for k in STATUS_RETAIN}, **{k: "practice" for k in STATUS_PRACTICE},
          **{k: "ordinary" for k in STATUS_ORD}, **{k: "all" for k in STATUS_ALL}}
status["LBN"] = "all"
# Somaliland and Northern Cyprus are drawn separately on the map; Amnesty counts them with Somalia and Cyprus
status["SOL"] = "retain"; status["NCY"] = "all"

# Recorded executions in 2025 (Amnesty Annex I; minimum figures). China, Iraq, North Korea, Viet Nam: executions
# confirmed but no credible minimum figure.
EXEC = {"IRN":2159,"SAU":356,"YEM":51,"USA":47,"EGY":23,"SOM":17,"KWT":17,"SGP":17,"AFG":6,"ARE":3,"JPN":1,"SSD":1,"TWN":1}
EXECUTED = list(EXEC) + ["CHN","IRQ","PRK","VNM"]
assert len(EXECUTED) == 17

by1977 = sorted(k for k, v in allc.items() if v <= 1977)
assert len(by1977) == 16, by1977

out = {
  "source": "amnesty-dp", "asOf": "2025-12-31", "retrieved": "2026-10-13",
  "note": ("Status at 31 December 2025 and recorded executions in 2025: Amnesty International, Death Sentences and Executions "
           "2025 (ACT 50/0778/2026), Annexes I and II; Lebanon shown as abolitionist after its parliament's vote of 11 August 2026. "
           "Years of abolition up to 2008: Amnesty International, List of abolitionist and retentionist countries (31 December 2008, "
           "ACT 50/002/2009), 'Date (A)' and 'Date (AO)'; Kosovo takes Serbia's date. Kiribati, Marshall Islands, Micronesia, Palau, "
           "Solomon Islands, Tuvalu and Vanuatu have had no death penalty since independence; their independence year is used. "
           "Later abolitions (year the law, constitution or court ruling took effect): Burundi, Togo 2009; Bolivia 2009 (constitution); "
           "Gabon 2010; Kyrgyzstan 2010 (constitution); Latvia 2012; Congo, Fiji, Madagascar, Suriname 2015; Benin, Nauru 2016; "
           "Guinea, Mongolia 2017; Chad 2020; Kazakhstan, Sierra Leone 2021; Central African Republic, Papua New Guinea, Zambia 2022; "
           "Lebanon 2026. Facts typed in; no Amnesty text is reproduced."),
  "years": [2025],
  "series": {"executions": {"label": "Recorded executions, 2025 (minimum)", "units": "people", "values": {k: [v] for k, v in EXEC.items()}}},
  "sets": {
    "abolished": {"label": "Abolished for all crimes", "members": dict(sorted(allc.items()))},
    "ordinary": {"label": "Abolished except for war or military crimes", "members": dict(sorted(ordinary.items()))},
    "status": {"label": "Death penalty today", "values": dict(sorted(status.items())),
               "labels": {"all": "Abolished for all crimes", "ordinary": "Only for exceptional crimes (e.g. in wartime)",
                          "practice": "On the books, no executions for 10+ years", "retain": "Retains it"}},
    "executed": {"label": "Carried out executions in 2025", "values": {k: "yes" for k in sorted(EXECUTED)},
                 "labels": {"yes": "Carried out executions in 2025"}},
  }
}
path = os.path.join(ROOT, "data", "rights", "death_penalty.json")
json.dump(out, open(path, "w"), ensure_ascii=False, separators=(",", ":"))
print("wrote", path, len(allc), "abolished;", "by 1977:", by1977)
for y in (1977, 1989, 2000, 2008, 2015, 2025): print(y, sum(1 for v in allc.values() if v <= y))
