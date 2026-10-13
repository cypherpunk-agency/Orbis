"""Reduce the EIA international bulk file to the series the energy stories use.
Run: python3 tools/build/eia.py   (after tools/fetch/sources.sh)
Output: data/energy/eia.json  {source, asOf, retrieved, years, series:{key:{label, units, values:{ISO3:[...]}}}}"""
import json, os, datetime
root = os.path.join(os.path.dirname(__file__), "..", "..")
SERIES = {  # key: (EIA series name, units). Crude trade (ends 2020), refining (2014) and flaring (2017) are too stale; trade comes from BACI.
    "oil_prod":   ("Petroleum and other liquids production", "thousand barrels per day"),
    "oil_cons":   ("Petroleum and other liquids consumption", "thousand barrels per day"),
    "gas_prod":   ("Dry natural gas production", "billion cubic meters"),
    "gas_cons":   ("Dry natural gas consumption", "billion cubic meters"),
    "gas_exp":    ("Dry natural gas exports", "billion cubic meters"),
    "gas_imp":    ("Dry natural gas imports", "billion cubic meters"),
    "pop":        ("Population", "people in thousands"),
}
Y0, Y1 = 2000, 2024
YEARS = list(range(Y0, Y1 + 1))
want = {(n, u): k for k, (n, u) in SERIES.items()}
out = {k: {} for k in SERIES}
as_of = ""
def sig(v):  # 3 significant figures keeps the file small without visible loss
    if v is None: return None
    return float(f"{v:.3g}")
for line in open(os.path.join(root, ".cache/eia/INTL.txt")):
    d = json.loads(line)
    sid, name = d.get("series_id", ""), d.get("name", "")
    if not sid.endswith(".A") or d.get("f") != "A": continue
    geo = d.get("geography", "")
    if len(geo) != 3 or not geo.isalpha(): continue  # countries only, not regions
    base = name.rsplit(", ", 2)[0] if name.endswith(", Annual") else None
    if not base: continue
    k = want.get((base, d.get("units")))
    if not k: continue
    vals = {int(y): v for y, v in d["data"] if isinstance(v, (int, float))}
    row = [sig(vals.get(y)) for y in YEARS]
    if any(v for v in row): out[k][geo] = row
    as_of = max(as_of, d.get("last_updated", "")[:10])
doc = {
    "source": "eia-intl", "asOf": as_of, "retrieved": datetime.date.today().isoformat(),
    "years": YEARS,
    "series": {k: {"label": SERIES[k][0], "units": SERIES[k][1], "values": out[k]} for k in SERIES},
}
p = os.path.join(root, "data/energy/eia.json")
json.dump(doc, open(p, "w"), separators=(",", ":"))
print(p, os.path.getsize(p) // 1024, "KB;", {k: len(v) for k, v in out.items()})
