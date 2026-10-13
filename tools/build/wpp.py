"""Life expectancy at birth from UN World Population Prospects 2024 (CC BY 3.0 IGO).
Fetch:
  mkdir -p .cache/wpp && cd .cache/wpp
  curl -o WPP2024_Demographic_Indicators_Medium.csv.gz \
    "https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/CSV_FILES/WPP2024_Demographic_Indicators_Medium.csv.gz"
Run: python3 tools/build/wpp.py
Output: data/statistics/life-expectancy.json, series (1950-2023, annual estimates; no projections):
  lex      life expectancy at birth, both sexes, years
        data/statistics/life-expectancy-gaps.json, series with years [2021, 2023]:
  lex_drop fall from 2019 to the lower of 2020/2021, years (stored in the 2021 slot)
  lex_gap  female minus male life expectancy at birth, years (2023 only)
  lex_gap_pct  the same gap as % of male life expectancy (2023 only; map-friendly with fmt "pct")"""
import os, csv, gzip, json, datetime
root = os.path.join(os.path.dirname(__file__), "..", "..")
src = os.path.join(root, ".cache/wpp/WPP2024_Demographic_Indicators_Medium.csv.gz")
out = os.path.join(root, "data/statistics/life-expectancy.json")
YEARS = list(range(1950, 2024))
def sig(v):
    if v is None: return None
    v = float(f"{v:.3g}")
    return int(v) if v == int(v) else v
lex, gap, gap_pct, world = {}, {}, {}, {}
with gzip.open(src, "rt", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        y = int(r["Time"])
        if y not in YEARS: continue
        i = YEARS.index(y)
        if r["Location"] == "World" and r["LocTypeID"] == "1":
            world[i] = float(r["LEx"])
        if r["LocTypeID"] != "4" or not r["ISO3_code"]: continue   # countries and areas only
        iso = r["ISO3_code"]
        lex.setdefault(iso, [None] * len(YEARS))[i] = sig(float(r["LEx"])) if r["LEx"] else None
        if y == YEARS[-1] and r["LExFemale"] and r["LExMale"]:   # latest year only
            fe, ma = float(r["LExFemale"]), float(r["LExMale"])
            gap[iso] = [None, round(fe - ma, 1)]
            gap_pct[iso] = [None, round((fe - ma) / ma * 100, 1)]
# pandemic dip: years of life expectancy lost from 2019 to the lower of 2020 and 2021, stored in the 2021 slot
i19, i20, i21 = YEARS.index(2019), YEARS.index(2020), YEARS.index(2021)
drop = {}
for iso, a in lex.items():
    if None in (a[i19], a[i20], a[i21]): continue
    drop[iso] = [max(0, round(a[i19] - min(a[i20], a[i21]), 1)), None]
data = {
    "source": "un-wpp", "asOf": "2024-07-11", "retrieved": datetime.date.today().isoformat(),
    "note": "United Nations, Department of Economic and Social Affairs, Population Division (2024). World Population Prospects 2024, Online Edition. "
            "CC BY 3.0 IGO. Estimates 1950-2023 (life expectancy at birth, period measure). Values for years without vital registration are UN model estimates.",
    "years": YEARS,
    "series": {
        "lex": {"label": "Life expectancy at birth", "units": "years", "values": lex},
    },
    "world": {"lex": [round(world[i], 1) for i in range(len(YEARS))]},
}
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(data, open(out, "w"), separators=(",", ":"))
small = {k: data[k] for k in ("source", "asOf", "retrieved", "note")}
small.update({"years": [2021, 2023], "series": {
    "lex_drop": {"label": "Fall in life expectancy, 2019 to lowest of 2020-21 (stored as 2021)", "units": "years", "values": drop},
    "lex_gap": {"label": "Women's minus men's life expectancy, 2023", "units": "years", "values": gap},
    "lex_gap_pct": {"label": "Women's life expectancy above men's, 2023", "units": "% of men's", "values": gap_pct}}})
out2 = out.replace(".json", "-gaps.json")
json.dump(small, open(out2, "w"), separators=(",", ":"))
print(out2, os.path.getsize(out2) // 1024, "KB")
print(out, os.path.getsize(out) // 1024, "KB,", len(lex), "countries")
