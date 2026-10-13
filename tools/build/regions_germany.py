"""Germany by Land (NUTS 1 = Länder): population, GDP per inhabitant, foreign-born share. Eurostat (CC BY 4.0).
Fetch: done by this script (Eurostat dissemination API, 3 requests), cached in .cache/germany/.
  demo_r_d2jan   population on 1 January, total
  nama_10r_2gdp  GDP at current market prices: EUR per inhabitant and PPS (EU27 2020) per inhabitant
  cens_21cob_r3  Census 2021 population by country of birth (FOR = foreign country, TOTAL)
Run: python3 tools/build/regions_germany.py
Output: data/regions/germany.json, series keyed by ISO 3166-2 ids of data/geo/admin1/DEU.json; "world" = Germany total."""
import os, json, datetime, urllib.request
root = os.path.join(os.path.dirname(__file__), "..", "..")
cache = os.path.join(root, ".cache/germany")
API = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
NUTS = {"DE1": "DE-BW", "DE2": "DE-BY", "DE3": "DE-BE", "DE4": "DE-BB", "DE5": "DE-HB", "DE6": "DE-HH",
        "DE7": "DE-HE", "DE8": "DE-MV", "DE9": "DE-NI", "DEA": "DE-NW", "DEB": "DE-RP", "DEC": "DE-SL",
        "DED": "DE-SN", "DEE": "DE-ST", "DEF": "DE-SH", "DEG": "DE-TH"}
NATION = "DE"
YEARS = list(range(2015, 2026))

def fetch(name, query):
    os.makedirs(cache, exist_ok=True)
    path = os.path.join(cache, name + ".json")
    if not os.path.exists(path):
        geo = "&".join(f"geo={g}" for g in [NATION, *NUTS])
        urllib.request.urlretrieve(f"{API}{query}&{geo}&sinceTimePeriod={YEARS[0]}", path)
    return json.load(open(path, encoding="utf-8"))

def table(d, **fix):
    """JSON-stat 2.0 -> {(geo, year): value} for the given fixed dimension values."""
    ids, size, dims = d["id"], d["size"], d["dimension"]
    idx = {k: dims[k]["category"]["index"] for k in ids}
    out = {}
    for geo, gi in idx["geo"].items():
        for t, ti in idx["time"].items():
            pos = 0
            for k, n in zip(ids, size):
                i = gi if k == "geo" else ti if k == "time" else idx[k][fix[k]] if k in fix else 0
                pos = pos * n + i
            v = d["value"].get(str(pos))
            if v is not None: out[(geo, int(t))] = v
    return out, d.get("updated", "")

pop, up1 = table(fetch("pop", "demo_r_d2jan?sex=T&age=TOTAL&unit=NR"))
gdp_d = fetch("gdp", "nama_10r_2gdp?unit=EUR_HAB&unit=PPS_EU27_2020_HAB")
eur, up2 = table(gdp_d, unit="EUR_HAB")
pps, _ = table(gdp_d, unit="PPS_EU27_2020_HAB")
cob_d = fetch("cob", "cens_21cob_r3?sex=T&age=TOTAL&unit=NR&c_birth=FOR&c_birth=TOTAL")
born_for, up3 = table(cob_d, c_birth="FOR")
born_tot, _ = table(cob_d, c_birth="TOTAL")

def vals(t, geo, nd=0):
    return [None if (geo, y) not in t else (round(t[(geo, y)], nd) if nd else int(round(t[(geo, y)]))) for y in YEARS]
def share(geo):
    return [round(100 * born_for[(geo, y)] / born_tot[(geo, y)], 1) if (geo, y) in born_for else None for y in YEARS]
series = {
    "pop": {"label": "Population on 1 January", "units": "people", "t": pop, "nd": 0},
    "gdp_pc": {"label": "GDP per inhabitant, current prices", "units": "EUR", "t": eur, "nd": 0},
    "gdp_pc_pps": {"label": "GDP per inhabitant in purchasing power standards (EU27 2020)", "units": "PPS", "t": pps, "nd": 0},
}
out = {"source": "eurostat", "asOf": max(up1, up2, up3)[:10], "retrieved": datetime.date.today().isoformat(), "years": YEARS,
       "series": {}, "world": {},
       "note": "Eurostat NUTS 1 regions, which in Germany are the 16 Länder (DE1 Baden-Württemberg = DE-BW … DEG Thüringen = DE-TH). "
               "Population: demo_r_d2jan, 1 January; from 2023 based on Census 2022 (Zensus), so 2022 to 2023 is a break, not a decline. GDP: nama_10r_2gdp (regional accounts, ESA 2010), EUR and PPS per inhabitant; "
               "the latest years are provisional. Foreign-born share: Census 2021 (cens_21cob_r3), people born outside Germany "
               "as % of the total population, 2021 only. 'world' holds the Germany total."}
for k, s in series.items():
    out["series"][k] = {"label": s["label"], "units": s["units"],
                        "values": {iso: vals(s["t"], n) for n, iso in NUTS.items()}}
    out["world"][k] = vals(s["t"], NATION)
out["series"]["foreign_born"] = {"label": "Born abroad (Census 2021)", "units": "% of population",
                                 "values": {iso: share(n) for n, iso in NUTS.items()}}
out["world"]["foreign_born"] = share(NATION)
for k, s in out["series"].items():
    last = max(i for i, y in enumerate(YEARS) if any(v[i] is not None for v in s["values"].values()))
    missing = [r for r, v in s["values"].items() if v[last] is None]
    print(f"{k}: latest {YEARS[last]}, regions {len(s['values'])}, missing {missing}")
dst = os.path.join(root, "data/regions/germany.json")
os.makedirs(os.path.dirname(dst), exist_ok=True)
json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(dst, os.path.getsize(dst), "bytes")
