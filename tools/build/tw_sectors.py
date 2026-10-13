"""US imports of goods hit by Section 232 tariffs (2025-2026), from CEPII BACI (HS2017, Etalab 2.0).
Same source and structure as tools/build/baci.py; only flows INTO the United States are kept.
Run: python3 tools/build/tw_sectors.py   (after tools/fetch/sources.sh has put the BACI zip in .cache/baci)
Output: data/tradewar/sectors.json
  {source, asOf, retrieved, units, years, groups:{key:{label, hs, flows:{year:[[exporter, "USA", value_musd, qty_kt], ...]},
                                                       exports:{year:{ISO3: value_musd}}, imports:{year:{"USA": total}}}}}
  "exports" here means exports TO THE UNITED STATES, so a chart with side "exports" ranks US suppliers."""
import os, json, zipfile, datetime, collections, csv, io
root = os.path.join(os.path.dirname(__file__), "..", "..")
VERSION = "V202601"
ZIP = os.path.join(root, ".cache/baci", f"BACI_HS17_{VERSION}.zip")
YEARS = [2024]
USA = "842"
GROUPS = {  # key: (label, HS codes or prefixes, HS2017)
    "steel": ("Iron and steel mill products (HS 7206-7229)", tuple(str(h) for h in range(7206, 7230))),
    "aluminium": ("Aluminium and aluminium articles (HS 76)", ("76",)),
    "copper": ("Semi-finished copper: bars, wire, plates, foil, tubes, fittings (HS 7407-7413)",
               ("7407", "7408", "7409", "7410", "7411", "7412", "7413")),
    "cars": ("Passenger cars (HS 8703)", ("8703",)),
    "parts": ("Car and vehicle parts (HS 8708)", ("8708",)),
    "trucks": ("Heavy trucks, road tractors and buses (HS 870120, 870422, 870423, 870432, 8702)",
               ("870120", "870422", "870423", "870432", "8702")),
    "lumber": ("Softwood lumber (HS 440711, 440712, 440719)", ("440711", "440712", "440719")),
    "pharma": ("Pharmaceutical products (HS 30)", ("30",)),
    "chips": ("Integrated circuits (HS 8542)", ("8542",)),
}
TOP = 40  # flows kept per group
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
            if j != USA or k[:2] not in CH2: continue
            g = group_of(k)
            if not g: continue
            acc = pair[g][codes.get(i, i)]
            acc[0] += float(v)
            try: acc[1] += float(q)
            except ValueError: pass
    for g in GROUPS:
        top = sorted(pair[g].items(), key=lambda kv: -kv[1][0])
        total = sum(v for _, (v, q) in top)
        # BACI values are thousand USD, quantities tonnes -> million USD, thousand tonnes
        out[g]["flows"][y] = [[a, "USA", round(v / 1000, 1), round(q / 1000, 1)] for a, (v, q) in top[:TOP]]
        out[g]["exports"][y] = {a: round(v / 1000) for a, (v, q) in top if v >= 1000}
        out[g]["imports"][y] = {"USA": round(total / 1000)}
        shares = ", ".join(f"{a} {v / total:.0%}" for a, (v, q) in top[:5])
        print(f"{y} {g:10s} total ${total / 1e6:6.1f} bn  top: {shares}")
# "all": the nine groups added up
allp = collections.Counter()
for g in GROUPS:
    for a, v in out[g]["exports"][YEARS[0]].items(): allp[a] += v
tot = sum(out[g]["imports"][YEARS[0]]["USA"] for g in GROUPS)
out["all"] = {"label": "All nine product groups above", "hs": [], "flows": {YEARS[0]: [[a, "USA", v, None] for a, v in allp.most_common(TOP)]},
              "exports": {YEARS[0]: dict(allp.most_common())}, "imports": {YEARS[0]: {"USA": tot}}}
print("all total $", tot / 1000, "bn top:", ", ".join(f"{a} {v / tot:.0%}" for a, v in allp.most_common(8)))
doc = {"source": "baci", "asOf": f"BACI HS17 {VERSION}", "retrieved": datetime.date.today().isoformat(),
       "units": {"value": "million USD", "qty": "thousand tonnes"}, "years": YEARS,
       "note": "US imports only (importer = USA), by exporting country, 2024, CEPII BACI HS2017 version 202601 (reconciled UN Comtrade data, "
               "values FOB). 'exports' lists each country's exports to the United States; 'imports' holds the US total. "
               "Product groups approximate the Section 232 tariff scopes, which are defined by HTSUS 8- and 10-digit lines and annexes: "
               "steel = HS 7206-7229 (excludes derivative articles in chapter 73 and elsewhere); aluminium = HS 76; "
               "copper = semi-finished products HS 7407-7413 (refined cathodes, ores and scrap are exempt from the copper tariff, Proclamation 10962); "
               "cars = HS 8703; parts = HS 8708 (the tariff also covers engines, electrical parts and others outside 8708); "
               "trucks = road tractors, trucks over 5 t and buses (Proclamation 10984 covers medium- and heavy-duty vehicles by HTSUS line); "
               "lumber = coniferous sawn wood (Proclamation 10976 also covers some logs, upholstered furniture and kitchen cabinets); "
               "pharma = all of HS 30 (the Section 232 tariff, Proclamation 11020, applies only to patented drugs and their ingredients; generics are exempt); "
               "chips = integrated circuits HS 8542 (the Section 232 tariff, Proclamation 11002, applies only to certain advanced computing chips and derivatives not used in the US).",
       "groups": out}
p = os.path.join(root, "data/tradewar/sectors.json")
os.makedirs(os.path.dirname(p), exist_ok=True)
json.dump(doc, open(p, "w"), separators=(",", ":"))
print(p, os.path.getsize(p) // 1024, "KB")
