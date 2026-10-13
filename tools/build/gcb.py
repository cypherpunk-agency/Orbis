"""National fossil CO2 emissions from the Global Carbon Project (Global Carbon Budget 2025, CC BY 4.0).
Dataset: Andrew & Peters, "The Global Carbon Project's fossil CO2 emissions dataset", version 2025v15,
Zenodo https://zenodo.org/records/17417124 (licence: Creative Commons Attribution 4.0 International).
Fetch:
  mkdir -p .cache/co2 && cd .cache/co2
  for f in GCB2025v15_MtCO2_flat.csv GCB2025v15_MtCO2_flat_metadata.json; do
    curl -L -o $f "https://zenodo.org/records/17417124/files/$f?download=1"; done
Run: python3 tools/build/gcb.py
Output: data/statistics/co2.json, series (1950-2024, annual):
  co2      fossil CO2 emissions, thousand tonnes CO2 (fmt "mt")
  co2_pc   fossil CO2 per person, kg CO2 (fmt "kg")
  co2_cum  cumulative fossil CO2 since 1850 up to that year, thousand tonnes CO2 (fmt "mt")
  world: global totals (incl. international aviation and shipping, which no country is assigned)."""
import os, csv, json, datetime
root = os.path.join(os.path.dirname(__file__), "..", "..")
src = os.path.join(root, ".cache/co2/GCB2025v15_MtCO2_flat.csv")
out = os.path.join(root, "data/statistics/co2.json")
YEARS = list(range(1950, 2025))
CUM_FROM = 1850
SKIP = {"", "WLD", "XIA", "XIS", "ATA"}   # aggregates, bunkers, Antarctica
RENAME = {"KSV": "XKX"}                   # GCB uses KSV for Kosovo
def sig(v):
    if v is None: return None
    v = float(f"{v:.3g}")
    return int(v) if v == int(v) else v
def num(s):
    return float(s) if s not in ("", None) else None
tot, pc = {}, {}
for r in csv.DictReader(open(src, encoding="utf-8")):
    iso = r["ISO 3166-1 alpha-3"].strip()
    y = int(r["Year"])
    if iso in ("",): continue
    iso = RENAME.get(iso, iso)
    tot.setdefault(iso, {})[y] = num(r["Total"])
    pc.setdefault(iso, {})[y] = num(r["Per Capita"])
series = {k: {} for k in ("co2", "co2_pc", "co2_cum")}
for iso in sorted(tot):
    if iso in SKIP: continue
    t = tot[iso]
    if not any(t.get(y) for y in YEARS): continue
    series["co2"][iso] = [sig(t[y] * 1000) if t.get(y) is not None else None for y in YEARS]
    series["co2_pc"][iso] = [sig(pc[iso][y] * 1000) if pc[iso].get(y) is not None else None for y in YEARS]
    cum, arr = 0.0, []
    for y in range(CUM_FROM, YEARS[-1] + 1):
        cum += t.get(y) or 0
        if y in YEARS: arr.append(sig(cum * 1000) if cum > 0 else None)
    series["co2_cum"][iso] = arr
w = tot["WLD"]
wcum, wc = 0.0, []
for y in range(CUM_FROM, YEARS[-1] + 1):
    wcum += w.get(y) or 0
    if y in YEARS: wc.append(sig(wcum * 1000))
data = {
    "source": "gcp-co2", "asOf": "2025-10-22", "retrieved": datetime.date.today().isoformat(),
    "note": "Global Carbon Budget 2025, fossil CO2 emissions dataset v2025v15 (Andrew & Peters, Zenodo 10.5281/zenodo.17417124), CC BY 4.0. "
            "Fossil fuels and cement, territorial basis; excludes land-use change. Historical emissions are allocated to today's borders. "
            "Cumulative = sum of annual emissions from 1850. World totals include international aviation and shipping.",
    "years": YEARS,
    "series": {
        "co2": {"label": "Fossil CO2 emissions", "units": "thousand tonnes CO2", "values": series["co2"]},
        "co2_pc": {"label": "Fossil CO2 emissions per person", "units": "kg CO2 per person", "values": series["co2_pc"]},
        "co2_cum": {"label": "Cumulative fossil CO2 since 1850", "units": "thousand tonnes CO2", "values": series["co2_cum"]},
    },
    "world": {
        "co2": [sig(w[y] * 1000) for y in YEARS],
        "co2_cum": wc,
    },
}
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(data, open(out, "w"), separators=(",", ":"))
print(out, os.path.getsize(out) // 1024, "KB,", len(series["co2"]), "countries")
