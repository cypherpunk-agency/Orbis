"""Bilateral trade in critical minerals and staple crops from CEPII BACI (HS2017, Etalab 2.0).
Same source and structure as tools/build/baci.py (energy); only the product groups differ.
Run: python3 tools/build/baci_resources.py   (after tools/fetch/sources.sh has put the BACI zip in .cache/baci)
Output: data/resources/trade.json
  {source, asOf, retrieved, units, years, groups:{key:{label, hs, flows:{year:[[exporter, importer, value_musd, qty_kt], ...]},
                                                       exports:{year:{ISO3: value_musd}}, imports:{...}}}}"""
import os, json, zipfile, datetime, collections, csv, io
root = os.path.join(os.path.dirname(__file__), "..", "..")
VERSION = "V202601"
ZIP = os.path.join(root, ".cache/baci", f"BACI_HS17_{VERSION}.zip")
YEARS = [2021, 2022, 2023, 2024]
GROUPS = {  # key: (label, HS6 codes or prefixes)
    "lithium": ("Lithium chemicals (oxide, hydroxide, carbonate)", ("282520", "283691")),
    "lithium_ore": ("Mineral substances n.e.s. incl. lithium ore (spodumene)", ("253090",)),
    "cobalt": ("Cobalt (ores, intermediates, unwrought metal, oxides)", ("260500", "810520", "282200")),
    "copper_ore": ("Copper ores and concentrates", ("260300",)),
    "copper_refined": ("Refined copper cathodes", ("740311",)),
    "nickel": ("Nickel (ores, mattes, unwrought metal)", ("260400", "750110", "750210")),
    "rare_earths": ("Rare-earth metals and compounds", ("280530", "284690")),
    "graphite": ("Natural graphite", ("250410", "250490")),
    "iron_ore": ("Iron ores and concentrates", ("260111", "260112")),
    "wheat": ("Wheat and meslin", ("100119", "100199")),
    "soybeans": ("Soya beans", ("120190",)),
    "maize": ("Maize (corn)", ("100590",)),
    "rice": ("Rice (paddy, husked, milled, broken)", ("1006",)),
}
TOP = 60  # flows kept per group and year
ISO_FIX = {"S19": "TWN"}  # BACI "Other Asia, nes" is Taiwan
CH2 = {p[:2] for _, ps in GROUPS.values() for p in ps}

z = zipfile.ZipFile(ZIP)
codes = {}
with z.open(f"country_codes_{VERSION}.csv") as f:
    for r in csv.DictReader(io.TextIOWrapper(f, "utf-8", errors="replace")):
        codes[r["country_code"]] = ISO_FIX.get(r["country_iso3"], r["country_iso3"])
def group_of(k):
    for g, (_, prefixes) in GROUPS.items():
        if k.startswith(prefixes): return g
out = {g: {"label": GROUPS[g][0], "hs": list(GROUPS[g][1]), "flows": {}, "exports": {}, "imports": {}} for g in GROUPS}
for y in YEARS:
    pair = {g: collections.defaultdict(lambda: [0.0, 0.0]) for g in GROUPS}
    with z.open(f"BACI_HS17_Y{y}_{VERSION}.csv") as f:
        rd = csv.reader(io.TextIOWrapper(f, "utf-8"))
        next(rd)
        for t, i, j, k, v, q in rd:
            if k[:2] not in CH2: continue
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
       "units": {"value": "million USD", "qty": "thousand tonnes"}, "years": YEARS,
       "note": "HS 253090 is a residual code: lithium ore (spodumene) dominates Australia->China but other minerals are included. "
               "HS 284690 excludes cerium compounds. Cobalt, nickel and lithium groups sum different processing stages.",
       "groups": out}
p = os.path.join(root, "data/resources/trade.json")
os.makedirs(os.path.dirname(p), exist_ok=True)
json.dump(doc, open(p, "w"), separators=(",", ":"))
print(p, os.path.getsize(p) // 1024, "KB")
for g in ("cobalt", "lithium", "lithium_ore"):
    print(g, 2024, out[g]["flows"][2024][:5])
