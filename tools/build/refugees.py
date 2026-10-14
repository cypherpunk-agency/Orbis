"""Refugees by country of origin and country of asylum, from the UNHCR Refugee Population Statistics API
(api.unhcr.org/population/v1, no key; UNHCR publishes the same tables on HDX under CC BY-IGO).
Population for the per-1,000 rate: UN World Population Prospects 2024 (CC BY 3.0 IGO), medium variant
(already cached by tools/build/wpp.py in .cache/wpp/).

Run: python3 tools/build/refugees.py
  downloads .cache/refugees/pop-<year>.json (end-year stocks, all origin x asylum pairs) and writes
  data/people/refugees-flows.json   groups: "ref" origin -> asylum flows (>= 5,000 people), per year
  data/people/refugees.json         series: hosted, hosted per 1,000 residents, originated, share in a neighbour
"Refugees" here = refugees under UNHCR's mandate + "other people in need of international protection" (OIP,
mostly Venezuelans in Latin America). Asylum seekers, IDPs and Palestine refugees under UNRWA's mandate are not included.
Neighbours = countries that share a land border in the Natural Earth 1:50m geometry (data/world50.json)."""
import os, json, csv, gzip, time, datetime, urllib.request, collections

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CACHE = os.path.join(root, ".cache/refugees")
YEARS = [2000, 2005, 2010, 2015, 2020, 2021, 2022, 2023, 2024, 2025]
MIN_FLOW = 5000
UA = {"User-Agent": "Orbis-data-build/1.0"}
os.makedirs(CACHE, exist_ok=True)


def fetch(year):
    fn = os.path.join(CACHE, f"pop-{year}.json")
    if not os.path.exists(fn):
        url = (f"https://api.unhcr.org/population/v1/population/?limit=20000&yearFrom={year}&yearTo={year}"
               "&coo_all=true&coa_all=true")
        d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120))
        assert d["maxPages"] == 1, "paging needed"
        json.dump(d["items"], open(fn, "w"))
        time.sleep(1)
    return json.load(open(fn))


num = lambda v: int(v) if isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit()) else 0

# land neighbours from shared topojson arcs
topo = json.load(open(os.path.join(root, "data/world50.json")))
arcs_of = collections.defaultdict(set)
def walk(a, iso):
    for x in a:
        if isinstance(x, list): walk(x, iso)
        else: arcs_of[x if x >= 0 else ~x].add(iso)
for g in topo["objects"]["countries"]["geometries"]:
    if g.get("arcs"): walk(g["arcs"], g["id"])
NB = collections.defaultdict(set)
for s in arcs_of.values():
    for a in s:
        NB[a] |= s - {a}
NB = {k: v for k, v in NB.items()}
geo = {g["id"] for g in topo["objects"]["countries"]["geometries"]}

# population (thousands), WPP 2024 medium variant: estimates to 2023, projection for 2024-25
pop = collections.defaultdict(dict)
with gzip.open(os.path.join(root, ".cache/wpp/WPP2024_Demographic_Indicators_Medium.csv.gz"), "rt", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        if r["LocTypeID"] == "4" and r["ISO3_code"] and int(r["Time"]) in YEARS and r["TPopulation1July"]:
            pop[r["ISO3_code"]][int(r["Time"])] = float(r["TPopulation1July"]) * 1000

flows, host, orig, nbshare, world = {}, {}, {}, {}, {}
world_nb = {}
skipped = collections.Counter()
for yi, y in enumerate(YEARS):
    pairs = collections.Counter()
    for it in fetch(y):
        o, a = it["coo_iso"], it["coa_iso"]
        v = num(it["refugees"]) + num(it["oip"])
        if not v: continue
        if o not in geo or a not in geo:
            skipped[(o, a)] += v
        pairs[(o, a)] += v
    tot = sum(pairs.values()); world[y] = tot
    nbv = 0
    oc, hc, onb = collections.Counter(), collections.Counter(), collections.Counter()
    for (o, a), v in pairs.items():
        if len(a) == 3 and a.isalpha(): hc[a] += v
        if o in geo: oc[o] += v   # skips 'UNK' (unknown origin) and 'XXA' (stateless)
        if a in NB.get(o, ()):
            nbv += v; onb[o] += v
    world_nb[y] = nbv
    for k, v in hc.items(): host.setdefault(k, [None] * len(YEARS))[yi] = v
    for k, v in oc.items():
        orig.setdefault(k, [None] * len(YEARS))[yi] = v
        if v >= 10000: nbshare.setdefault(k, [None] * len(YEARS))[yi] = round(onb[k] / v * 100, 1)
    rows = sorted(([o, a, v, None] for (o, a), v in pairs.items()
                   if v >= MIN_FLOW and o != a and o in geo and a in geo), key=lambda r: -r[2])
    flows[str(y)] = rows
    print(y, f"total {tot/1e6:.2f} M, in a neighbour {nbv/tot*100:.0f}%, flows kept {len(rows)}"
          f" covering {sum(r[2] for r in rows)/tot*100:.0f}%")

per1000 = {}
for k, a in host.items():
    if k not in pop or pop[k].get(YEARS[-1], 0) < 1e6: continue   # skip small territories (Aruba, Curaçao...)
    per1000[k] = [round(v / pop[k][y] * 1000, 1) if v is not None and pop[k].get(y) else None for v, y in zip(a, YEARS)]

today = datetime.date.today().isoformat()
common = {"source": "unhcr", "asOf": f"end-{YEARS[-1]}", "retrieved": today}
note = ("UNHCR Refugee Population Statistics, end-year stocks. 'Refugees' = refugees under UNHCR's mandate plus other people "
        "in need of international protection (mostly Venezuelans in Latin America). Excludes asylum seekers, internally "
        "displaced people and about 6 million Palestine refugees under UNRWA's mandate. Origin 'unknown' and stateless "
        "are counted in totals but not in flows.")
fl = dict(common, note=note + f" Flows of at least {MIN_FLOW:,} people.", years=YEARS,
          units={"value": "people"},
          groups={"ref": {"label": "Refugees", "flows": flows,
                          "exports": {str(y): {k: v[i] for k, v in orig.items() if v[i]} for i, y in enumerate(YEARS)},
                          "imports": {str(y): {k: v[i] for k, v in host.items() if v[i]} for i, y in enumerate(YEARS)}}})
ser = dict(common, note=note + " Per 1,000 residents uses UN WPP 2024 population (medium variant; 2024–25 projected), countries over 1 million people only. "
           "Neighbour = shares a land border (Natural Earth 1:50m).", years=YEARS,
           series={
               "hosted": {"label": "Refugees hosted", "units": "people", "values": host},
               "hosted_per1000": {"label": "Refugees hosted per 1,000 residents", "units": "per 1,000 residents", "values": per1000},
               "origin": {"label": "Refugees from this country", "units": "people", "values": orig},
               "nb_share": {"label": "Share of a country's refugees living in a neighbouring country", "units": "%", "values": nbshare},
           },
           world={"hosted": [world[y] for y in YEARS], 
                  "nb_share": [round(world_nb[y] / world[y] * 100, 1) for y in YEARS]})
os.makedirs(os.path.join(root, "data/people"), exist_ok=True)
for name, obj in (("refugees-flows.json", fl), ("refugees.json", ser)):
    p = os.path.join(root, "data/people", name)
    json.dump(obj, open(p, "w"), separators=(",", ":"), ensure_ascii=False)
    print("wrote", p, os.path.getsize(p))
print("codes not on the map (counted in world totals only):", skipped.most_common(8))
