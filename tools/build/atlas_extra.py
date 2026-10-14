"""Country atlas, non-World-Bank indicators: UNDP HDR, Penn World Table, Ember, UNESCO UIS.

Merges into data/atlas/catalog.json and writes data/atlas/<id>.json in the same series format as tools/build/atlas.py
(one file per indicator, series "v", values per ISO3 country, one slot per year). Idempotent: every run first removes
the catalog entries (and skipped notes) of the sources below, then adds them back; World Bank entries are untouched.
Run tools/build/atlas.py first: Ember demand per person divides by the World Bank population file it writes, and a
full atlas.py run rewrites the catalog without these entries, so re-run this script after it.

Licences (checked at the primary source on 2026-10-14):
  undp-hdr    CC BY 3.0 IGO   https://hdr.undp.org/data-center/documentation-and-downloads
  pwt         CC BY 4.0       https://www.rug.nl/ggdc/productivity/pwt/
  ember       CC BY 4.0       https://ember-energy.org/data/yearly-electricity-data/
  unesco-uis  CC BY-SA 4.0    https://uis.unesco.org/en/terms-use (share-alike: tier "commercial", catalog note says so)
Skipped: V-Dem v16 (CC BY-SA 4.0): every dataset download on v-dem.net goes through a form that requires an email
address, so it is not fetched here.

Usage: python3 tools/build/atlas_extra.py [--only undp-hdr,pwt,ember,unesco-uis]
"""
import argparse, csv, io, json, math, os, time, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
OUT = os.path.join(ROOT, "data/atlas")
CACHE = os.path.join(ROOT, ".cache/atlas_extra")
UA = {"User-Agent": "Orbis-build/1.0"}

HDR_URL = "https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Composite_indices_complete_time_series.csv"
PWT_URL = "https://dataverse.nl/api/access/datafile/554105"   # PWT 11.0 Excel, linked from rug.nl/ggdc/productivity/pwt
EMBER_URL = "https://files.ember-energy.org/public-downloads/generation/outputs/release_generation_yearly_global.csv"
UIS_API = "https://api.uis.unesco.org/api/public"

SOURCES = {
 "undp-hdr": {"licence": "CC BY 3.0 IGO", "tier": "commercial", "note": "",
              "credit": "UNDP Human Development Report 2025, composite indices time series"},
 "pwt": {"licence": "CC BY 4.0", "tier": "commercial", "note": "",
         "credit": "Penn World Table 11.0 (Feenstra, Inklaar and Timmer), Groningen Growth and Development Centre"},
 "ember": {"licence": "CC BY 4.0", "tier": "commercial", "note": "",
           "credit": "Ember, Yearly Electricity Data"},
 "unesco-uis": {"licence": "CC BY-SA 4.0", "tier": "noncommercial", "note": "share-alike",
                "credit": "UNESCO Institute for Statistics (UIS)"},
}
# V-Dem: listed in the catalog's "skipped" so the gap is documented next to the data
SKIPPED = [("VDEM.POLYARCHY", "V-Dem v16 electoral democracy index: download form requires an email address"),
           ("VDEM.LIBDEM", "V-Dem v16 liberal democracy index: download form requires an email address")]

# id, short name, topic, fmt, source, raw key, units, definition
INDICATORS = [
 ("HDR.HDI", "Human Development Index (0–1)", "People", "d3:.3f", "undp-hdr", "hdi", "Index (0–1)",
  "The Human Development Index is a summary measure of a long and healthy life, access to knowledge and a decent standard of living: the geometric mean of normalized indices for life expectancy, years of schooling and gross national income per person."),
 ("HDR.IHDI", "Inequality-adjusted HDI (0–1)", "People", "d3:.3f", "undp-hdr", "ihdi", "Index (0–1)",
  "The inequality-adjusted Human Development Index discounts each dimension of the HDI by how unequally it is shared across the population. Where there is no inequality it equals the HDI; the gap is the loss to inequality."),
 ("HDR.GII", "Gender Inequality Index (0–1, lower is more equal)", "People", "d3:.3f", "undp-hdr", "gii", "Index (0–1)",
  "The Gender Inequality Index measures the disadvantage of women in reproductive health (maternal mortality, adolescent births), empowerment (seats in parliament, secondary education) and the labour market. 0 means women and men fare equally, 1 means women fare as badly as possible."),
 ("HDR.PHDI", "Planetary-pressures-adjusted HDI (0–1)", "Environment", "d3:.3f", "undp-hdr", "phdi", "Index (0–1)",
  "The planetary pressures-adjusted Human Development Index lowers the HDI by a country's carbon dioxide emissions and material footprint per person. Where pressures on the planet are zero it equals the HDI."),
 ("HDR.EYS", "Expected years of schooling", "Education", "num", "undp-hdr", "eys", "Years",
  "Expected years of schooling is the number of years of schooling a child of school entrance age can expect to receive if today's age-specific enrolment rates hold throughout the child's life."),
 ("HDR.MYS", "Mean years of schooling, adults", "Education", "num", "undp-hdr", "mys", "Years",
  "Mean years of schooling is the average number of years of education received by people aged 25 and older."),
 ("PWT.HC", "Human capital index (PWT)", "Education", "num", "pwt", "hc", "Index",
  "Human capital index of the Penn World Table, based on average years of schooling and an assumed rate of return to education. It runs from 1 (no schooling) to about 4."),
 ("PWT.LABSH", "Labour share of GDP (%)", "Economy", "pct", "pwt", "labsh", "% of GDP at current national prices",
  "Share of labour compensation in GDP at current national prices, including an estimate of the labour income of the self-employed (Penn World Table)."),
 ("PWT.AVH", "Hours worked per worker a year", "Economy", "int", "pwt", "avh", "Hours per year",
  "Average annual hours worked by persons engaged (employees and self-employed), from the Penn World Table."),
 ("PWT.PL_GDPO", "Price level of GDP (USA = 1)", "Economy", "num", "pwt", "pl_gdpo", "Ratio (USA 2021 = 1)",
  "Price level of output-side GDP at current PPPs relative to the exchange rate (PPP divided by exchange rate), with the price level of the United States in 2021 set to 1 (Penn World Table). Below 1 means goods and services cost less than in the US at market exchange rates."),
 ("EMBER.CLEAN", "Low-carbon electricity (%)", "Environment", "pct", "ember", "Clean", "% of generation",
  "Share of electricity generated from low-carbon sources: nuclear plus renewables (hydro, wind, solar, bioenergy and other renewables), as a percentage of total generation (Ember)."),
 ("EMBER.WINDSOLAR", "Wind and solar electricity (%)", "Environment", "pct", "ember", "Wind and solar", "% of generation",
  "Share of electricity generated by wind and solar power, as a percentage of total generation (Ember)."),
 ("EMBER.COAL", "Coal electricity (%)", "Environment", "pct", "ember", "Coal", "% of generation",
  "Share of electricity generated by coal, as a percentage of total generation (Ember). Countries where Ember lists no coal generation are shown as 0."),
 ("EMBER.CO2INT", "Carbon intensity of electricity (gCO₂e/kWh)", "Environment", "int", "ember", "intensity", "gCO2e per kWh",
  "Lifecycle greenhouse gas emissions per kilowatt-hour of electricity generated, in grams of CO₂ equivalent (Ember)."),
 ("EMBER.DEMAND.PC", "Electricity use per person (MWh)", "Environment", "num", "ember", "demand_pc", "MWh per person",
  "Electricity demand (generation plus net imports) per person, in megawatt-hours a year: Ember demand divided by World Bank population (WDI SP.POP.TOTL, CC BY 4.0)."),
 ("UIS.CR.3", "Finish upper secondary school (%)", "Education", "pct", "unesco-uis", "CR.3", "% of age group",
  "Completion rate, upper secondary education: share of people aged 3–5 years above the intended age for the last grade of upper secondary school who have completed that grade (UNESCO UIS, from household surveys)."),
 ("UIS.ROFST.1.CP", "Out-of-school children, primary age (%)", "Education", "pct", "unesco-uis", "ROFST.1.CP", "% of primary-age children",
  "Out-of-school rate for children of primary school age: share of children of official primary school age who are not enrolled in primary or secondary education (UNESCO UIS)."),
 ("UIS.RESDEN.INHAB.TFTE", "Researchers per million people", "Education", "int", "unesco-uis", "RESDEN.INHAB.TFTE", "Researchers (FTE) per million inhabitants",
  "Researchers in full-time equivalents per million inhabitants (UNESCO UIS research and development statistics)."),
]
OWN = {i[0] for i in INDICATORS} | {s[0] for s in SKIPPED}
# source codes that differ from the ISO3 the atlas uses
ALIAS = {"KSV": "XKX", "KOS": "XKX", "ROM": "ROU", "ZAR": "COD", "TMP": "TLS"}


def fetch(url, path, binary=True):
    """Download url into the cache once; return the local path."""
    if not os.path.exists(path):
        for k in range(4):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r: data = r.read()
                break
            except Exception:
                if k == 3: raise
                time.sleep(2 ** (k + 1))
        open(path, "wb").write(data)
    return path


def sig(v, n=4):
    if v is None or v == 0 or not math.isfinite(v): return None if v is None or not math.isfinite(v) else v
    return round(v, max(0, n - 1 - int(math.floor(math.log10(abs(v))))))


def fnum(s):
    try:
        v = float(s)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def country_set():
    """ISO3 codes the atlas uses: World Bank economies (as in the population file) plus every country on the map."""
    wb = json.load(open(os.path.join(OUT, "SP.POP.TOTL.json")))
    world = json.load(open(os.path.join(ROOT, "data/world50.json")))
    geo = {g.get("id") for g in world["objects"]["countries"]["geometries"]}
    return set(wb["series"]["v"]["values"]) | {g for g in geo if g and len(g) == 3 and g.isalpha()}, wb


# ---------- readers: each returns {key: {iso3: {year: value}}}, asOf, unmatched codes ----------
def read_hdr(keys, ok):
    p = fetch(HDR_URL, os.path.join(CACHE, "hdr.csv"))
    raw = open(p, "rb").read().decode("utf-8-sig", errors="replace")
    out = {k: {} for k in keys}; miss = set()
    for r in csv.DictReader(io.StringIO(raw)):
        c = ALIAS.get(r["iso3"], r["iso3"])
        if c not in ok: miss.add(r["iso3"]); continue  # aggregates (ZZA.VHHD …) and places off the atlas
        for col, s in r.items():
            if not col or "_" not in col: continue
            k, y = col.rsplit("_", 1)
            if k in out and y.isdigit():
                v = fnum(s)
                if v is not None: out[k].setdefault(c, {})[int(y)] = v
    return out, "HDR 2025", miss


def read_pwt(keys, ok):
    import openpyxl
    p = fetch(PWT_URL, os.path.join(CACHE, "pwt.xlsx"))
    wb = openpyxl.load_workbook(p, read_only=True)
    rows = wb["Data"].iter_rows(values_only=True); head = list(next(rows)); ix = {h: j for j, h in enumerate(head)}
    out = {k: {} for k in keys}; miss = set()
    for r in rows:
        c = ALIAS.get(r[ix["countrycode"]], r[ix["countrycode"]])
        if c not in ok: miss.add(c); continue
        for k in keys:
            v = r[ix[k]]
            if isinstance(v, (int, float)) and math.isfinite(v):
                out[k].setdefault(c, {})[int(r[ix["year"]])] = v * 100 if k == "labsh" else v
    return out, "PWT 11.0", miss


def read_ember(keys, ok, wbpop):
    p = fetch(EMBER_URL, os.path.join(CACHE, "ember.csv"))
    gen = {}; share = {}; inten = {}; dem = {}; miss = set()
    for r in csv.DictReader(open(p, encoding="utf-8-sig")):
        if r["Area type"] != "Country or economy": continue
        c = ALIAS.get(r["ISO 3 code"], r["ISO 3 code"])
        if c not in ok: miss.add(r["ISO 3 code"] or r["Area"]); continue
        y = int(r["Year"]); src = r["Electricity source"]
        if src == "Total generation":
            gen[(c, y)] = fnum(r["Generation (TWh)"]); inten[(c, y)] = fnum(r["Emissions intensity (gCO2e/kWh)"])
        elif src == "Demand":
            dem[(c, y)] = fnum(r["Generation (TWh)"])
        else:
            share[(src, c, y)] = fnum(r["Share of generation (%)"])
    pop = wbpop["series"]["v"]["values"]; pys = wbpop["years"]
    out = {k: {} for k in keys}
    for (c, y), g in gen.items():
        if not g: continue  # no generation reported: shares undefined
        for k in keys:
            if k == "intensity": v = inten.get((c, y))
            elif k == "demand_pc":
                d = dem.get((c, y)); pp = pop.get(c, [None] * len(pys))[pys.index(y)] if y in pys and c in pop else None
                v = d * 1e6 / pp if d is not None and pp else None
            else:
                v = share.get((k, c, y))
                if v is None and k == "Coal": v = 0.0  # Ember lists no coal row where there is no coal generation
            if v is not None: out[k].setdefault(c, {})[y] = v
    asof = time.strftime("%Y-%m-%d", time.gmtime(os.path.getmtime(p)))
    return out, f"Ember yearly electricity data, downloaded {asof}", miss


def read_uis(keys, ok):
    out = {k: {} for k in keys}; miss = set()
    for k in keys:
        p = fetch(f"{UIS_API}/data/indicators?indicator={k}&geoUnitType=NATIONAL", os.path.join(CACHE, f"uis_{k}.json"))
        d = json.load(open(p))
        if d.get("hints"): print("UIS hints", k, d["hints"])
        for r in d["records"]:
            c = ALIAS.get(r["geoUnit"], r["geoUnit"]); v = r.get("value")
            if c not in ok: miss.add(r["geoUnit"]); continue
            if isinstance(v, (int, float)) and math.isfinite(v): out[k].setdefault(c, {})[int(r["year"])] = v
    try:
        ver = json.load(open(fetch(f"{UIS_API}/versions/default", os.path.join(CACHE, "uis_version.json"))))
        asof = f"UIS data version {ver.get('version')} ({(ver.get('publicationDate') or '')[:10]})"
    except Exception:
        asof = "UIS public data API"
    return out, asof, miss


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--only"); a = ap.parse_args()
    only = set(a.only.split(",")) if a.only else set(SOURCES)
    os.makedirs(CACHE, exist_ok=True)
    ok, wbpop = country_set()
    cat_path = os.path.join(OUT, "catalog.json")
    cat = json.load(open(cat_path))
    old = {c["id"]: c for c in cat["indicators"] if c["id"] in OWN}
    by_src = {}
    for ind in INDICATORS: by_src.setdefault(ind[4], []).append(ind)
    new = {}
    for sid, inds in by_src.items():
        if sid not in only:  # keep what an earlier run built for this source
            new.update({i[0]: old[i[0]] for i in inds if i[0] in old}); continue
        keys = [i[5] for i in inds]
        if sid == "undp-hdr": data, asof, miss = read_hdr(keys, ok)
        elif sid == "pwt": data, asof, miss = read_pwt(keys, ok)
        elif sid == "ember": data, asof, miss = read_ember(keys, ok, wbpop)
        else: data, asof, miss = read_uis(keys, ok)
        miss.discard(None); miss.discard("")
        if miss: print(f"{sid}: dropped codes not on the atlas: {' '.join(sorted(m for m in miss if m))}")
        S = SOURCES[sid]
        for iid, short, topic, fmt, _, key, units, definition in inds:
            vals = {c: d for c, d in data[key].items() if d}
            if not vals: print("no data", iid); continue
            years = sorted({y for d in vals.values() for y in d}); ys = list(range(years[0], years[-1] + 1))
            series = {c: [sig(d.get(y)) for y in ys] for c, d in sorted(vals.items())}
            note = f"{S['credit']}, {key}: {short}. Licence {S['licence']}" + (" (share-alike)" if S["note"] else "") + "."
            ds = {"source": sid, "asOf": asof, "retrieved": time.strftime("%Y-%m-%d"), "note": note,
                  "years": ys, "series": {"v": {"label": short, "units": units, "values": series}}}
            fn = f"data/atlas/{iid}.json"
            json.dump(ds, open(os.path.join(ROOT, fn), "w"), separators=(",", ":"))
            latest = ys[-1]
            entry = {"id": iid, "name": short, "long": f"{short} ({S['credit'].split(',')[0]})", "topic": topic, "fmt": fmt,
                     "units": units, "source": sid, "licence": S["licence"], "tier": S["tier"], "years": [ys[0], ys[-1]],
                     "countries": len(vals), "recent": sum(1 for d in vals.values() if any(y >= latest - 2 for y in d)),
                     "file": fn, "definition": definition}
            if S["note"]: entry["note"] = S["note"]
            new[iid] = entry
            print(f"{iid:24s} {len(vals):4d} countries {ys[0]}-{ys[-1]} {os.path.getsize(os.path.join(ROOT, fn)) // 1024} KB")
    # drop files of own indicators that this run no longer produces
    for iid, c in old.items():
        if iid not in new and os.path.exists(os.path.join(ROOT, c["file"])): os.remove(os.path.join(ROOT, c["file"]))
    # rebuild the indicator list: World Bank entries keep their order, own entries follow the last one of their topic
    base = [c for c in cat["indicators"] if c["id"] not in OWN]
    topics = cat["topics"]; merged = []
    for tp in topics:
        merged += [c for c in base if c["topic"] == tp] + [new[i[0]] for i in INDICATORS if i[0] in new and i[2] == tp]
    merged += [c for c in base if c["topic"] not in topics]
    cat["indicators"] = merged
    cat["skipped"] = [s for s in cat.get("skipped", []) if s["id"] not in OWN] + [{"id": i, "why": w} for i, w in SKIPPED]
    json.dump(cat, open(cat_path, "w"), indent=1, ensure_ascii=False)
    print(len(new), "extra indicators;", len(merged), "in catalog")


if __name__ == "__main__":
    main()
