"""Refugees from Ukraine by host country, and people displaced inside Ukraine, from the UNHCR Refugee
Population Statistics API (api.unhcr.org/population/v1, no key, CC BY 4.0; source id `unhcr`).
End-year stocks. "Refugees" = refugees under UNHCR's mandate, which for Ukrainians in Europe includes people with
temporary protection. IDPs: the figure UNHCR's database carries for Ukraine (from IOM/IDMC estimates).
Run: python3 tools/build/ua_refugees.py -> data/people/ua-refugees.json"""
import os, json, time, datetime, urllib.request, gzip, csv

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CACHE = os.path.join(ROOT, ".cache/ua_refugees")
os.makedirs(CACHE, exist_ok=True)
UA = {"User-Agent": "Orbis-data-build/1.0"}
YEARS = list(range(2014, 2026))
num = lambda v: v if isinstance(v, (int, float)) else 0


def get(url, fn):
    fn = os.path.join(CACHE, fn)
    if not os.path.exists(fn):
        d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120))
        assert d.get("maxPages", 1) == 1, "paging needed"
        json.dump(d["items"], open(fn, "w")); time.sleep(1)
    return json.load(open(fn))


B = "https://api.unhcr.org/population/v1/population/?limit=1000"
tot = {it["year"]: it for it in get(f"{B}&yearFrom={YEARS[0]}&yearTo={YEARS[-1]}&coo=UKR", "totals.json")}
hosts = {}
for y in YEARS:
    for it in get(f"{B}&yearFrom={y}&yearTo={y}&coo=UKR&coa_all=true", f"hosts-{y}.json"):
        iso = it["coa_iso"]
        if not iso or iso == "UKR" or len(iso) != 3:
            continue
        hosts.setdefault(iso, {})[y] = num(it["refugees"]) + num(it.get("oip"))

# population, UN WPP 2024 medium variant (cached by tools/build/wpp.py; CC BY 3.0 IGO), for refugees per 1,000 residents
pop = {}
with gzip.open(os.path.join(ROOT, ".cache/wpp/WPP2024_Demographic_Indicators_Medium.csv.gz"), "rt", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        if r["LocTypeID"] == "4" and r["ISO3_code"] and int(r["Time"]) in YEARS and r["TPopulation1July"]:
            pop.setdefault(r["ISO3_code"], {})[int(r["Time"])] = float(r["TPopulation1July"]) * 1000

vals = {iso: [v.get(y) or None for y in YEARS] for iso, v in hosts.items() if max(v.values()) >= 1000}
out = {
    "source": "unhcr", "asOf": "end-2025", "retrieved": datetime.date.today().isoformat(),
    "note": "UNHCR Refugee Population Statistics (api.unhcr.org/population/v1), end-year stocks, country of origin Ukraine. "
            "'Refugees' are refugees under UNHCR's mandate (including people under temporary protection in Europe) plus "
            "'other people in need of international protection'; asylum seekers are not included. Host countries with "
            "fewer than 1,000 at every year-end are left out. Year-end stocks, not arrivals: people who went home or moved "
            "on are not counted. 'idp' is the internally displaced figure in UNHCR's database for Ukraine (based on IOM "
            "and IDMC estimates). Per 1,000 residents: host population from UN World Population Prospects 2024 (medium variant). Built by tools/build/ua_refugees.py.",
    "years": YEARS,
    "series": {
        "ref": {"label": "Refugees from Ukraine (end of year)", "units": "people", "values": vals},
        "ref_per1000": {"label": "Refugees from Ukraine per 1,000 residents", "units": "per 1,000 residents",
                        "values": {iso: [round(v[k] / pop[iso][y] * 1000, 1) if v[k] and pop.get(iso, {}).get(y) else None
                                         for k, y in enumerate(YEARS)] for iso, v in vals.items()}},
        "total": {"label": "Refugees from Ukraine, all host countries", "units": "people",
                  "values": {"UKR": [num(tot[y]["refugees"]) + num(tot[y].get("oip")) for y in YEARS]}},
        "idp": {"label": "Displaced inside Ukraine", "units": "people",
                "values": {"UKR": [num(tot[y]["idps"]) for y in YEARS]}},
    },
}
fn = os.path.join(ROOT, "data/people/ua-refugees.json")
json.dump(out, open(fn, "w"), separators=(",", ":"))
print(fn, os.path.getsize(fn), "hosts", len(vals))
for y in (2022, 2023, 2025):
    k = YEARS.index(y)
    top = sorted(((v[k] or 0, i) for i, v in vals.items()), reverse=True)[:10]
    print(y, out["series"]["total"]["values"]["UKR"][k], out["series"]["idp"]["values"]["UKR"][k], top)
