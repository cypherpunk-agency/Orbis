"""Cross-border bank lending by bank nationality from the BIS consolidated banking statistics (CBS).
BIS terms: free of charge with citation ("Source: BIS consolidated banking statistics"), never behind a paywall.
Fetch:
  mkdir -p .cache/bis && curl -o .cache/bis/WS_CBS_PUB_csv_flat.zip https://data.bis.org/static/bulk/WS_CBS_PUB_csv_flat.zip
  mkdir -p .cache/wb && curl -o .cache/wb/countries.json "https://api.worldbank.org/v2/country?format=json&per_page=400"  # ISO2 -> ISO3
Run: python3 tools/build/bis.py   (first run streams the 4.7 GB CSV once and caches the Q4 rows in .cache/bis/cbs_q4.csv)
Output: data/finance/bis.json  flow file, group "banks": [bank nationality, counterparty country, foreign claims bn USD, null]"""
import os, json, csv, zipfile, io, datetime, collections
root = os.path.join(os.path.dirname(__file__), "..", "..")
cache = os.path.join(root, ".cache/bis")
YEARS = list(range(2008, 2026))
TOP = 150
SUB = os.path.join(cache, "cbs_q4.csv")
# Foreign claims = total claims of domestic banks excluding domestic positions (bank type 4R), all instruments,
# all maturities, all currencies, all sectors. Basis U = ultimate risk (guarantor), F = immediate counterparty.
WANT = {"L_MEASURE": "S", "CBS_BANK_TYPE": "4R", "L_POSITION": "C", "L_INSTR": "A", "REM_MATURITY": "A",
        "CURR_TYPE_BOOK": "TO1", "L_CP_SECTOR": "A"}
if not os.path.exists(SUB):
    z = zipfile.ZipFile(os.path.join(cache, "WS_CBS_PUB_csv_flat.zip"))
    with z.open(z.namelist()[0]) as f, open(SUB + ".tmp", "w", newline="") as o:
        rd = csv.reader(io.TextIOWrapper(f, "utf-8"))
        h = [c.split(":")[0] for c in next(rd)]
        ix = {k: h.index(k) for k in list(WANT) + ["CBS_BASIS", "L_REP_CTY", "L_CP_COUNTRY", "TIME_PERIOD", "OBS_VALUE", "UNIT_MULT"]}
        w = csv.writer(o)
        w.writerow(["basis", "rep", "rep_name", "cp", "cp_name", "period", "value", "mult"])
        for r in rd:
            p = r[ix["TIME_PERIOD"]]
            if not p.endswith("Q4") or not r[ix["OBS_VALUE"]]: continue
            if any(r[ix[k]].split(":")[0] != v for k, v in WANT.items()): continue
            b = r[ix["CBS_BASIS"]].split(":")[0]
            if b not in ("U", "F"): continue
            rep, cp = (r[ix[k]].split(": ", 1) for k in ("L_REP_CTY", "L_CP_COUNTRY"))
            w.writerow([b, rep[0], rep[1], cp[0], cp[1], p[:4], r[ix["OBS_VALUE"]], r[ix["UNIT_MULT"]].split(":")[0]])
    os.rename(SUB + ".tmp", SUB)
wb = json.load(open(os.path.join(root, ".cache/wb/countries.json")))[1]
ISO = {c["iso2Code"]: c["id"] for c in wb if c["region"]["id"] != "NA"}  # countries only
ISO.update({"TW": "TWN", "XK": "XKX", "KS": "XKX", "GG": "GGY", "JE": "JEY", "AI": "AIA", "AN": "ANT", "CK": "COK",
            "FK": "FLK", "MS": "MSR", "SH": "SHN", "WF": "WLF", "VA": "VAT", "NU": "NIU", "PS": "PSE", "EH": "ESH",
            "BQ": "BES", "PM": "SPM", "TK": "TKL", "IO": "IOT", "GS": "SGS", "UM": "UMI", "NF": "NFK", "CX": "CXR",
            "CC": "CCK", "PN": "PCN", "BL": "BLM", "HM": "HMD", "TF": "ATF", "AQ": "ATA", "BV": "BVT", "SJ": "SJM"})
ISO.pop("JG", None)  # WB "Channel Islands" aggregate
rows = list(csv.DictReader(open(SUB)))
names, skipped = {}, collections.Counter()
val = {b: collections.defaultdict(dict) for b in "UF"}  # basis -> year -> (rep, cp) -> bn USD
for r in rows:
    y = int(r["period"])
    if y not in YEARS: continue
    a, b = ISO.get(r["rep"]), ISO.get(r["cp"])
    if not a or not b:
        skipped[(r["cp"], r["cp_name"]) if a else (r["rep"], r["rep_name"])] += 1
        continue
    if a == b: continue
    names[b] = r["cp_name"]
    val[r["basis"]][y][(a, b)] = float(r["value"]) * 10 ** (int(r["mult"]) - 9)
# ultimate-risk basis where the reporter publishes it, immediate-borrower basis otherwise (per reporter and year)
flows, exp, imp, basis_used = {}, {}, {}, {}
for y in YEARS:
    u, f = val["U"][y], val["F"][y]
    reps_u = {a for a, _ in u}
    pair = dict(u)
    pair.update({k: v for k, v in f.items() if k[0] not in reps_u})
    basis_used[y] = {"ultimate_risk": sorted(reps_u), "immediate_borrower": sorted({a for a, _ in f} - reps_u)}
    e, i = collections.Counter(), collections.Counter()
    for (a, b), v in pair.items():
        e[a] += v; i[b] += v
    def sig(v): return float(f"{v:.3g}")
    flows[y] = [[a, b, sig(v), None] for (a, b), v in sorted(pair.items(), key=lambda kv: -kv[1])[:TOP] if v > 0]
    exp[y] = {c: sig(v) for c, v in e.most_common() if v >= 0.05}
    imp[y] = {c: sig(v) for c, v in i.most_common() if v >= 0.05}
doc = {"source": "bis-cbs", "asOf": f"BIS CBS bulk file (WS_CBS_PUB), {YEARS[-1]}-Q4 latest",
       "retrieved": datetime.date.today().isoformat(),
       "note": ("Foreign claims of banks by nationality (domestic banks, consolidated, excl. domestic positions) on each counterparty "
                "country, end of Q4, billion USD. Ultimate-risk (guarantor) basis where the reporting country publishes it, "
                "otherwise immediate-counterparty basis (see basisByYear). Flow = bank home country -> borrower country; "
                "top 150 pairs per year. exports = total foreign claims by bank nationality (lent), imports = claims on the "
                "country summed over reporting bank systems (borrowed); both sum over country counterparties only, so regional "
                "and residual BIS aggregates are excluded. Only ~30 countries report, so 'imports' misses lending by "
                "non-reporting banking systems (e.g. China)."),
       "units": {"value": "billion USD"}, "years": YEARS,
       "basisByYear": basis_used,
       "groups": {"banks": {"label": "Bank foreign claims by nationality", "flows": flows, "exports": exp, "imports": imp}}}
p = os.path.join(root, "data/finance/bis.json")
json.dump(doc, open(p, "w"), separators=(",", ":"))
print(p, os.path.getsize(p) // 1024, "KB; rows", len(rows), "skipped codes:", sorted(skipped)[:80])
for y in (2008, YEARS[-1]):
    print(y, "pairs", len(flows[y]), flows[y][:5])
    print("  lent", list(exp[y].items())[:6], "\n  borrowed", list(imp[y].items())[:6])
    print("  basis", basis_used[y])
