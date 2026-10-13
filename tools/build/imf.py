"""Government, household and corporate debt by country from the IMF DataMapper API (WEO + Global Debt Database).
Fetch (IMF terms forbid automated bulk download, so only these few single-indicator requests, run by hand):
  mkdir -p .cache/imf && cd .cache/imf
  curl -o indicators.json https://www.imf.org/external/datamapper/api/v1/indicators
  curl -o countries.json  https://www.imf.org/external/datamapper/api/v1/countries
  for i in GGXWDG_NGDP NGDPD HH_LS NFC_LS; do curl -o $i.json https://www.imf.org/external/datamapper/api/v1/$i; done
Run: python3 tools/build/imf.py
Output: data/finance/imf.json  {source, asOf, retrieved, note, years, series:{key:{label, units, values:{ISO3:[...]}}}}"""
import json, os, datetime
root = os.path.join(os.path.dirname(__file__), "..", "..")
cache = os.path.join(root, ".cache/imf")
SERIES = {  # key: (DataMapper indicator, label, units)
    "gov_debt_gdp": ("GGXWDG_NGDP", "General government gross debt", "% of GDP"),
    "gdp_usd":      ("NGDPD", "GDP, current prices", "billion USD"),
    "hh_debt_gdp":  ("HH_LS", "Household debt, loans and debt securities", "% of GDP"),
    "nfc_debt_gdp": ("NFC_LS", "Non-financial corporate debt, loans and debt securities", "% of GDP"),
}
YEARS = list(range(2000, 2025))  # no WEO projections beyond 2024
ISO_FIX = {"UVK": "XKX", "KOS": "XKX", "WBG": "PSE"}  # IMF codes -> ISO3 used by the map
def sig(v):
    if v is None: return None
    return float(f"{v:.3g}")
ind = json.load(open(os.path.join(cache, "indicators.json")))["indicators"]
countries = set(json.load(open(os.path.join(cache, "countries.json")))["countries"])  # excludes regional aggregates
raw = {}
for k, (code, label, units) in SERIES.items():
    vals = json.load(open(os.path.join(cache, code + ".json")))["values"][code]
    out = {}
    for c, byyear in vals.items():
        if c not in countries: continue
        row = [byyear.get(str(y)) for y in YEARS]
        row = [float(v) if isinstance(v, (int, float)) else None for v in row]
        if not any(v is not None for v in row): continue
        iso = ISO_FIX.get(c, c)
        if iso in out:  # IMF lists Kosovo twice (KOS, UVK): keep the fuller row
            if sum(v is not None for v in out[iso]) >= sum(v is not None for v in row): continue
        out[iso] = row
    raw[k] = out
# gross debt in USD = % of GDP x GDP
raw["gov_debt_usd"] = {}
for c, row in raw["gov_debt_gdp"].items():
    g = raw["gdp_usd"].get(c)
    if not g: continue
    raw["gov_debt_usd"][c] = [d / 100 * x if d is not None and x is not None else None for d, x in zip(row, g)]
labels = {k: (l, u) for k, (_, l, u) in SERIES.items()}
labels["gov_debt_usd"] = ("General government gross debt", "billion USD")
src = {k: ind[c]["source"] for k, (c, _, _) in SERIES.items()}
doc = {
    "source": "imf-weo", "asOf": f"{src['gov_debt_gdp']}; {src['hh_debt_gdp']}",
    "retrieved": datetime.date.today().isoformat(),
    "note": ("IMF DataMapper. Government debt and GDP from the World Economic Outlook; recent years may be IMF staff "
             "estimates for some countries (DataMapper does not flag which). Household and non-financial corporate debt "
             "from the Global Debt Database (loans and debt securities). gov_debt_usd = gov_debt_gdp/100 x gdp_usd, "
             "computed by Orbis. Countries only; regional aggregates dropped. 3 significant figures."),
    "years": YEARS,
    "series": {k: {"label": labels[k][0], "units": labels[k][1],
                   "values": {c: [sig(v) for v in row] for c, row in sorted(raw[k].items())}}
               for k in ["gov_debt_gdp", "gdp_usd", "gov_debt_usd", "hh_debt_gdp", "nfc_debt_gdp"]},
}
p = os.path.join(root, "data/finance/imf.json")
json.dump(doc, open(p, "w"), separators=(",", ":"))
print(p, os.path.getsize(p) // 1024, "KB;", {k: len(v["values"]) for k, v in doc["series"].items()})
for k, s in doc["series"].items():
    for yi in range(len(YEARS) - 1, -1, -1):
        n = sum(1 for r in s["values"].values() if r[yi] is not None)
        if n > 20: break
    top = sorted(((r[yi], c) for c, r in s["values"].items() if r[yi] is not None), reverse=True)[:5]
    print(k, YEARS[yi], f"{n} countries", top, "JPN", s["values"].get("JPN", [None] * 25)[yi])
