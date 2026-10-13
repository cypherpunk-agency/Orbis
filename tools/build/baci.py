"""Bilateral energy trade flows from CEPII BACI (HS2017, Etalab 2.0).
Run: python3 tools/build/baci.py   (after tools/fetch/sources.sh; unzips the needed years)
Output: data/energy/trade.json
  {source, asOf, retrieved, units, years, groups:{key:{label, flows:{year:[[exporter, importer, value_musd, qty_kt], ...]},
                                                       exports:{year:{ISO3: value_musd}}, imports:{...}}}}"""
import os, json, zipfile, datetime, collections, csv, io
root = os.path.join(os.path.dirname(__file__), "..", "..")
VERSION = "V202601"
ZIP = os.path.join(root, ".cache/baci", f"BACI_HS17_{VERSION}.zip")
YEARS = [2021, 2022, 2023, 2024]
GROUPS = {  # key: (label, HS6 prefix)
    "crude": ("Crude oil", ("270900",)),
    "products": ("Refined oil products", ("2710",)),
    "lng": ("Liquefied natural gas (LNG)", ("271111",)),
    "pipegas": ("Natural gas by pipeline", ("271121",)),
}
TOP = 80  # flows kept per group and year
ISO_FIX = {"S19": "TWN"}  # BACI "Other Asia, nes" is Taiwan

z = zipfile.ZipFile(ZIP)
codes = {}
with z.open(f"country_codes_{VERSION}.csv") as f:
    for r in csv.DictReader(io.TextIOWrapper(f, "utf-8", errors="replace")):
        codes[r["country_code"]] = ISO_FIX.get(r["country_iso3"], r["country_iso3"])
def group_of(k):
    for g, (_, prefixes) in GROUPS.items():
        if k.startswith(prefixes): return g
out = {g: {"label": GROUPS[g][0], "flows": {}, "exports": {}, "imports": {}} for g in GROUPS}
for y in YEARS:
    pair = {g: collections.defaultdict(lambda: [0.0, 0.0]) for g in GROUPS}
    with z.open(f"BACI_HS17_Y{y}_{VERSION}.csv") as f:
        rd = csv.reader(io.TextIOWrapper(f, "utf-8"))
        next(rd)
        for t, i, j, k, v, q in rd:
            if not k.startswith("27"): continue
            g = group_of(k)
            if not g: continue
            acc = pair[g][(codes.get(i, i), codes.get(j, j))]
            acc[0] += float(v)
            try: acc[1] += float(q)
            except ValueError: pass
    for g in GROUPS:
        exp, imp = collections.Counter(), collections.Counter()
        for (a, b), (v, q) in pair[g].items():
            exp[a] += v; imp[b] += v
        top = sorted(pair[g].items(), key=lambda kv: -kv[1][0])[:TOP]
        # BACI values are thousand USD, quantities tonnes -> million USD, thousand tonnes
        out[g]["flows"][y] = [[a, b, round(v / 1000, 1), round(q / 1000, 1)] for (a, b), (v, q) in top]
        out[g]["exports"][y] = {c: round(v / 1000) for c, v in exp.most_common() if v >= 1000}
        out[g]["imports"][y] = {c: round(v / 1000) for c, v in imp.most_common() if v >= 1000}
    print(y, {g: len(pair[g]) for g in GROUPS})
doc = {"source": "baci", "asOf": f"BACI HS17 {VERSION}", "retrieved": datetime.date.today().isoformat(),
       "units": {"value": "million USD", "qty": "thousand tonnes"}, "years": YEARS, "groups": out}
p = os.path.join(root, "data/energy/trade.json")
json.dump(doc, open(p, "w"), separators=(",", ":"))
print(p, os.path.getsize(p) // 1024, "KB")
