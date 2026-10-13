"""Bilateral official debt owed by low- and middle-income countries, from World Bank International Debt Statistics (CC BY 4.0).
Fetch:
  mkdir -p .cache/ids .cache/wb && cd .cache/ids
  curl -O https://databank.worldbank.org/data/download/IDS_CSV.zip            # debtor totals (World counterpart only)
  curl -o counterparts.json "https://api.worldbank.org/v2/sources/6/counterpart-area?format=json&per_page=1000"
  for y in $(seq 2000 2024); do curl -o blat_$y.json \
    "https://api.worldbank.org/v2/sources/6/country/all/series/DT.DOD.BLAT.CD/counterpart-area/all/time/YR$y?format=json&per_page=50000"; done
  curl -o ../wb/countries.json "https://api.worldbank.org/v2/country?format=json&per_page=400"
Run: python3 tools/build/ids.py
Output: data/finance/ids.json (flow file, group "bilateral": creditor -> debtor PPG debt stock, billion USD)
        data/finance/ids_series.json (series: ext_debt_gni, china_share, china_share_bilateral, bilateral_china_usd)"""
import os, json, csv, io, zipfile, datetime, collections, re, unicodedata
root = os.path.join(os.path.dirname(__file__), "..", "..")
cache = os.path.join(root, ".cache/ids")
YEARS = list(range(2000, 2025))
N_CREDITORS = 15     # creditor countries whose flows are kept (largest bilateral lenders in the latest year)
MIN_FLOW = 0.05      # billion USD; smaller creditor -> debtor stocks are dropped from flows (still in totals)
def sig(v):
    if v is None: return None
    return float(f"{v:.3g}")
wb = json.load(open(os.path.join(root, ".cache/wb/countries.json")))[1]
COUNTRIES = {c["id"]: c["name"] for c in wb if c["region"]["id"] != "NA"}
def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z]", "", s)
byname = {norm(n): k for k, n in COUNTRIES.items()}
CP_FIX = {  # IDS counterpart names that differ from WB country names
    "Germany, Fed. Rep. of": "DEU", "Turkiye": "TUR", "Bosnia-Herzegovina": "BIH", "Russian Federation": "RUS",
    "Cote D`Ivoire, Republic Of": "CIV", "Sao Tome & Principe": "STP", "Somalia, Fed. Rep.": "SOM", "Venezuela, Republic Bolivarian": "VEN",
    "Iran, Islamic Republic Of": "IRN", "Yemen, Republic Of": "YEM", "Korea, D.P.R. of": "PRK", "Korea, Republic of": "KOR",
    "Lao People's Democratic Rep.": "LAO", "Macao": "MAC", "Hong Kong": "HKG", "Brunei": "BRN", "Viet Nam": "VNM",
    "Trinidad & Tobago": "TTO", "Antigua": "ATG", "St. Kitts And Nevis": "KNA", "St. Lucia": "LCA",
    "St. Vincent & The Grenadines": "VCT", "Virgin Is.(US)": "VIR", "Micronesia Fed Sts": "FSM", "Egypt": "EGY",
    "Gambia, The": "GMB", "Congo, Rep.": "COG", "Congo, Dem. Rep.": "COD", "Kyrgyz Republic": "KGZ", "Slovak Republic": "SVK",
    "Syrian Arab Republic": "SYR", "Taiwan, China": "TWN", "Taiwan": "TWN", "Kosovo": "XKX", "Bahamas": "BHS",
    "Neth. Antilles": "ANT", "Reunion": "REU", "Guadeloupe": "GLP", "French Polynesia": "PYF", "New Caledonia (Fr.)": "NCL",
    "Anguilla": "AIA", "Czechia": "CZE", "Eswatini": "SWZ", "Cabo Verde": "CPV", "Iraq": "IRQ", "Libya": "LBY",
}
cps = json.load(open(os.path.join(cache, "counterparts.json")))["source"][0]["concept"][0]["variable"]
CP = {}
for c in cps:
    iso = CP_FIX.get(c["value"]) or byname.get(norm(c["value"]))
    if iso: CP[c["id"]] = iso
unmatched = collections.Counter()
pair = {y: {} for y in YEARS}  # (creditor, debtor) -> USD
for y in YEARS:
    d = json.load(open(os.path.join(cache, f"blat_{y}.json")))["source"]["data"]
    for o in d:
        if not o["value"]: continue
        v = {x["concept"]: x for x in o["variable"]}
        deb, cid = v["Country"]["id"], v["Counterpart-Area"]["id"]
        if deb not in COUNTRIES: continue  # regional / income aggregates
        cr = CP.get(cid)
        if not cr:
            unmatched[(cid, v["Counterpart-Area"]["value"])] += o["value"]
            continue
        pair[y][(cr, deb)] = pair[y].get((cr, deb), 0) + o["value"]
# debtor totals from the bulk file (World counterpart)
z = zipfile.ZipFile(os.path.join(cache, "IDS_CSV.zip"))
tot = collections.defaultdict(dict)
with z.open("IDS_ALLCountries_Data.csv") as f:
    rd = csv.reader(io.TextIOWrapper(f, "latin-1"))
    h = next(rd)
    yi = {y: h.index(str(y)) for y in YEARS}
    for r in rd:
        s, c = r[5].strip(), r[1].strip()
        if s in ("DT.DOD.DECT.GN.ZS", "DT.DOD.DPPG.CD", "DT.DOD.BLAT.CD") and c in COUNTRIES and r[3] == "WLD":
            tot[s][c] = [float(r[yi[y]]) if r[yi[y]] else None for y in YEARS]
last = YEARS[-1]
lent = collections.Counter()
for (a, b), v in pair[last].items(): lent[a] += v
creditors = [c for c, _ in lent.most_common(N_CREDITORS)]
flows, exp, imp = {}, {}, {}
for y in YEARS:
    e, i = collections.Counter(), collections.Counter()
    for (a, b), v in pair[y].items():
        e[a] += v; i[b] += v
    flows[y] = [[a, b, sig(v / 1e9), None] for (a, b), v in sorted(pair[y].items(), key=lambda kv: -kv[1])
                if a in creditors and v / 1e9 >= MIN_FLOW]
    exp[y] = {c: sig(v / 1e9) for c, v in e.most_common() if v >= 1e7}
    imp[y] = {c: sig(v / 1e9) for c, v in i.most_common() if v >= 1e7}
retrieved = datetime.date.today().isoformat()
as_of = json.load(open(os.path.join(cache, f"blat_{last}.json")))["lastupdated"]
doc = {"source": "wb-ids", "asOf": f"International Debt Statistics, updated {as_of}", "retrieved": retrieved,
       "note": ("Public and publicly guaranteed (PPG) external debt stocks owed to official bilateral creditors, end of year, "
                "billion USD (IDS series DT.DOD.BLAT.CD by counterpart). Flow = creditor country -> debtor; flows kept for the "
                f"{N_CREDITORS} largest bilateral creditors in {last} and stocks >= {MIN_FLOW} bn. exports = total bilateral PPG "
                "debt owed to the creditor by IDS reporting countries (lent); imports = the debtor's total bilateral PPG debt (owed). "
                "Debtors are the ~120 low- and middle-income countries reporting to the World Bank DRS only. Lending by Chinese "
                "state banks booked as commercial (e.g. China Development Bank) is under private creditors and not included here."),
       "units": {"value": "billion USD"}, "years": YEARS, "creditors": creditors,
       "groups": {"bilateral": {"label": "Debt owed to bilateral creditors (PPG)", "flows": flows, "exports": exp, "imports": imp}}}
p = os.path.join(root, "data/finance/ids.json")
json.dump(doc, open(p, "w"), separators=(",", ":"))
print(p, os.path.getsize(p) // 1024, "KB; flows/yr", {y: len(flows[y]) for y in (YEARS[0], last)})
print("unmatched counterparts with bilateral claims (bn):", [(k, round(v / 1e9, 2)) for k, v in unmatched.most_common(15)])
# debtor series
debtors = sorted({b for y in YEARS for (_, b) in pair[y]} | set(tot["DT.DOD.DECT.GN.ZS"]))
china, chs, chb = {}, {}, {}
for c in debtors:
    cn = [pair[y].get(("CHN", c)) for y in YEARS]
    bl = [imp[y].get(c) for y in YEARS]
    pg = tot["DT.DOD.DPPG.CD"].get(c, [None] * len(YEARS))
    if any(cn):
        china[c] = [sig(v / 1e9) if v else 0.0 for v in cn]
        chs[c] = [sig(100 * (v or 0) / g) if g else None for v, g in zip(cn, pg)]
        chb[c] = [sig(100 * (v or 0) / 1e9 / b) if b else None for v, b in zip(cn, bl)]
gni = {c: [sig(v) for v in row] for c, row in tot["DT.DOD.DECT.GN.ZS"].items() if any(v is not None for v in row)}
ser = {"source": "wb-ids", "asOf": doc["asOf"], "retrieved": retrieved,
       "note": ("World Bank IDS, reporting low- and middle-income countries only. ext_debt_gni = total external debt stocks, % of GNI "
                "(DT.DOD.DECT.GN.ZS). china_share = PPG external debt owed to China (official bilateral) as % of all PPG external debt "
                "(DT.DOD.DPPG.CD); china_share_bilateral = same as % of bilateral PPG debt; bilateral_china_usd in billion USD. "
                "Chinese lending booked under private creditors is excluded, so China's role is understated for some countries."),
       "years": YEARS,
       "series": {"ext_debt_gni": {"label": "External debt stocks", "units": "% of GNI", "values": gni},
                  "china_share": {"label": "Share of public external debt owed to China (bilateral)", "units": "% of PPG external debt", "values": chs},
                  "china_share_bilateral": {"label": "China's share of bilateral public debt", "units": "% of bilateral PPG debt", "values": chb},
                  "bilateral_china_usd": {"label": "Public external debt owed to China (bilateral)", "units": "billion USD", "values": china}}}
p2 = os.path.join(root, "data/finance/ids_series.json")
json.dump(ser, open(p2, "w"), separators=(",", ":"))
print(p2, os.path.getsize(p2) // 1024, "KB;", {k: len(v["values"]) for k, v in ser["series"].items()})
print("creditors", creditors)
print("lent", last, list(exp[last].items())[:8])
print("owed", last, list(imp[last].items())[:5])
print("top flows", flows[last][:8])
top_c = collections.Counter(max(((v, a) for (a, b), v in pair[last].items() if b == d), default=(0, None))[1] for d in imp[last])
print("top bilateral creditor per debtor:", top_c.most_common(6))
li = YEARS.index(last)
print("china_share top", sorted(((r[li], c) for c, r in chs.items() if r[li] is not None), reverse=True)[:8])
print("ext_debt_gni top", sorted(((r[li], c) for c, r in gni.items() if r[li] is not None), reverse=True)[:5])
