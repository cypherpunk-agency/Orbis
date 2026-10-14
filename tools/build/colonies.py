#!/usr/bin/env python3
"""Years under European colonial rule, by colonizer -> data/rights/colonies.json

Source: Bastian Becker, "Colonial Dates Dataset (COLDAT)", Harvard Dataverse, doi:10.7910/DVN/T9SDEW, V3 (2023-09-21), CC0 1.0.
File COLDAT_colonies.tab (wide format, one row per contemporary state). Eight colonizers only: Belgium, Britain, France,
Germany, Italy, the Netherlands, Portugal, Spain (no Russia, Ottoman Empire, Japan, United States, Denmark, Sweden).

Rule: mean aggregation (COLDAT colstart.*_mean / colend.*_mean, the average across its source datasets). Years under each
colonizer = end - start. Total years under colonial rule = length of the union of all colonizers' spans (overlaps such as
French and British Canada are counted once). Main colonizer = the one with the most years.
"""
import csv, json, os, re, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(ROOT, ".cache", "colonies")
OUT = os.path.join(ROOT, "data", "rights", "colonies.json")
os.makedirs(CACHE, exist_ok=True)
URL = "https://dataverse.harvard.edu/api/access/datafile/7416946?format=original"  # COLDAT_colonies.tab, V3
path = os.path.join(CACHE, "f7416946")
if not os.path.exists(path):
    with urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "Orbis-data-build/1.0"}), timeout=120) as r:
        open(path, "wb").write(r.read())

# COLDAT names (Correlates of War states) -> ISO3; names that match Natural Earth names in data/world.js are mapped automatically
FIX = {"Antigua & Barbuda": "ATG", "Bosnia & Herzegovina": "BIH", "Congo - Brazzaville": "COG", "Congo - Kinshasa": "COD",
       "Côte d’Ivoire": "CIV", "Micronesia (Federated States of)": "FSM", "Myanmar (Burma)": "MMR", "São Tomé & Príncipe": "STP",
       "St. Kitts & Nevis": "KNA", "St. Lucia": "LCA", "St. Vincent & Grenadines": "VCT", "Trinidad & Tobago": "TTO",
       "United States": "USA", "Central African Republic": "CAF", "Dominican Republic": "DOM", "Equatorial Guinea": "GNQ",
       "South Sudan": "SSD", "Solomon Islands": "SLB", "Marshall Islands": "MHL", "Cape Verde": "CPV", "Eswatini": "SWZ",
       "Czechia": "CZE", "North Macedonia": "MKD", "Kosovo": "XKX", "Timor-Leste": "TLS", "Taiwan": "TWN", "Bahamas": "BHS",
       "North Korea": "PRK", "South Korea": "KOR", "Laos": "LAO", "Brunei": "BRN", "Gambia": "GMB", "Comoros": "COM",
       "Maldives": "MDV", "Seychelles": "SYC", "Mauritius": "MUS", "Barbados": "BRB", "Grenada": "GRD", "Dominica": "DMA",
       "Kiribati": "KIR", "Nauru": "NRU", "Palau": "PLW", "Tuvalu": "TUV", "Tonga": "TON", "Samoa": "WSM", "Malta": "MLT",
       "Andorra": "AND", "Monaco": "MCO", "San Marino": "SMR", "Liechtenstein": "LIE", "Singapore": "SGP", "Bahrain": "BHR",
       "Guinea-Bissau": "GNB", "Vanuatu": "VUT", "Fiji": "FJI", "Papua New Guinea": "PNG", "United Arab Emirates": "ARE",
       "United Kingdom": "GBR", "Russia": "RUS", "Bolivia": "BOL", "Venezuela": "VEN", "Iran": "IRN", "Syria": "SYR",
       "Tanzania": "TZA", "Vietnam": "VNM", "Moldova": "MDA"}
w = open(os.path.join(ROOT, "data", "world.js")).read()
ne = {m.group(2): m.group(1) for m in re.finditer(r'"id":"([A-Z]{3})","properties":\{"name":"([^"]+)"', w)}

COLS = ["britain", "france", "spain", "portugal", "netherlands", "belgium", "germany", "italy"]
LABEL = {"britain": "Britain", "france": "France", "spain": "Spain", "portugal": "Portugal", "netherlands": "the Netherlands",
         "belgium": "Belgium", "germany": "Germany", "italy": "Italy"}
num = lambda s: None if s in ("NA", "", None) else float(s)

rows = list(csv.DictReader(open(path, encoding="utf-8")))
per = {c: {} for c in COLS}; total = {}; main = {}; spans = {}; nmulti = 0; unmapped = []
for r in rows:
    iso = FIX.get(r["country"]) or ne.get(r["country"])
    if not iso: unmapped.append(r["country"]); continue
    iv = []
    for c in COLS:
        if r[f"col.{c}"] != "1": continue
        a, b = num(r[f"colstart.{c}_mean"]), num(r[f"colend.{c}_mean"])
        if a is None or b is None: print("missing dates", r["country"], c, a, b); continue
        per[c][iso] = round(b - a)
        if per[c][iso] < 1: del per[c][iso]
        iv.append((a, b, c))
    if not iv: continue
    iv.sort(); u = 0; cur = None
    for a, b, _ in iv:
        if cur and a <= cur[1]: cur[1] = max(cur[1], b)
        else:
            if cur: u += cur[1] - cur[0]
            cur = [a, b]
    u += cur[1] - cur[0]
    total[iso] = round(u)
    main[iso] = max(iv, key=lambda x: x[1] - x[0])[2]
    spans[iso] = [[int(a), int(b), c] for a, b, c in iv]
    if len(iv) > 1: nmulti += 1
print("unmapped", unmapped)
print("colonies", len(total), "with several colonizers", nmulti)
for c in COLS: print(c, len(per[c]), "main for", sum(1 for v in main.values() if v == c))
top = sorted(total.items(), key=lambda kv: -kv[1])
print("longest", top[:20]); print("shortest", top[-12:])
import statistics
print("median", statistics.median(total.values()))

ser = {"col_years": {"label": "Years under European colonial rule", "units": "years", "values": {k: [v] for k, v in total.items()}}}
for c in COLS:
    ser[f"{c}_years"] = {"label": f"Years under {LABEL[c]}", "units": "years", "values": {k: [v] for k, v in per[c].items()}}
data = {
    "source": "coldat", "asOf": "2023-09-21", "retrieved": time.strftime("%Y-%m-%d"),
    "note": ("COLDAT V3 (Becker, Harvard Dataverse doi:10.7910/DVN/T9SDEW, CC0), mean aggregation across its source datasets. "
             "Only eight European colonizers are covered (Belgium, Britain, France, Germany, Italy, the Netherlands, Portugal, Spain); "
             "rule by Russia, the Ottoman Empire, Japan, the United States, Denmark or others is not counted. Years = end minus start "
             "year. 'col_years' merges overlapping spans of different colonizers. Countries are today's states; a colonial span counts "
             "when the colony made up at least 10% of today's territory."),
    "years": [2023],
    "series": ser,
    "sets": {"main": {"label": "Longest colonizer",
                      "values": {k: (v if v in COLS[:5] else "other") for k, v in main.items()},
                      "labels": dict({c: LABEL[c][0].upper() + LABEL[c][1:] for c in COLS[:5]}, other="Belgium, Germany or Italy")}},
    "spans": spans,
}
s = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
open(OUT, "w").write(s)
print(OUT, len(s) // 1024, "KB")
