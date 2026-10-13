"""US goods trade by partner country, monthly, from the US Census Bureau (FT-900 country file; US government work, public domain).
Fetch: downloads https://www.census.gov/foreign-trade/balance/country.xlsx into .cache/tw/ if it is not there
       (delete the cached file to refresh).
Run:   python3 tools/build/tw_census.py
Output (Census basis, not seasonally adjusted, general imports / total exports; imports in million USD, balances and changes in billion USD):
  data/tradewar/imports.json   years = yyyymm 201712..latest; imp12 = imports over the 12 months ending that month;
                               imp_m = imports in that month (top partners only); share12 = % of all US imports (12 months)
  data/tradewar/shift.json     one frame (years [latest yyyymm]): change in imports, latest 12 months vs calendar 2024 and 2017;
                               trade balance and exports by partner, 2024 vs latest 12 months
  data/tradewar/balance.json   years = yyyymm 201712..latest; bal12 = exports - imports over 12 months, by partner;
                               total_bal12 / total_imp12 / total_exp12 keyed "USA" = the US total with the world (for line charts)
  data/tradewar/balance_long.json  years 1990..last full year; bal / imp / exp keyed "USA" = annual totals with the world
Partners: Census country codes mapped to ISO3; aggregates (EU, regions, World, NAFTA/USMCA, ATP), former states
(USSR, Yugoslavia, Czechoslovakia, Netherlands Antilles), "Unidentified" and "International organizations" are dropped.
The US total comes from Census line 0015 "World, Not Seasonally Adjusted"."""
import os, json, datetime, urllib.request, collections
import openpyxl

root = os.path.join(os.path.dirname(__file__), "..", "..")
cache = os.path.join(root, ".cache/tw")
out_dir = os.path.join(root, "data/tradewar")
URL = "https://www.census.gov/foreign-trade/balance/country.xlsx"
SRC = os.path.join(cache, "country.xlsx")
UA = {"User-Agent": "Orbis-data-build/1.0"}
os.makedirs(cache, exist_ok=True); os.makedirs(out_dir, exist_ok=True)
if not os.path.exists(SRC):
    with urllib.request.urlopen(urllib.request.Request(URL, headers=UA)) as r, open(SRC, "wb") as f: f.write(r.read())

ISO = {  # Census Schedule C country code -> ISO3
 "1010":"GRL","1220":"CAN","1610":"SPM","2010":"MEX","2050":"GTM","2080":"BLZ","2110":"SLV","2150":"HND","2190":"NIC",
 "2230":"CRI","2250":"PAN","2320":"BMU","2360":"BHS","2390":"CUB","2410":"JAM","2430":"TCA","2440":"CYM","2450":"HTI",
 "2470":"DOM","2481":"AIA","2482":"VGB","2483":"KNA","2484":"ATG","2485":"MSR","2486":"DMA","2487":"LCA","2488":"VCT",
 "2489":"GRD","2720":"BRB","2740":"TTO","2774":"SXM","2777":"CUW","2779":"ABW","2831":"GLP","2839":"MTQ","3010":"COL",
 "3070":"VEN","3120":"GUY","3150":"SUR","3170":"GUF","3310":"ECU","3330":"PER","3350":"BOL","3370":"CHL","3510":"BRA",
 "3530":"PRY","3550":"URY","3570":"ARG","3720":"FLK","4000":"ISL","4010":"SWE","4031":"SJM","4039":"NOR","4050":"FIN",
 "4091":"FRO","4099":"DNK","4120":"GBR","4190":"IRL","4210":"NLD","4231":"BEL","4239":"LUX","4271":"AND","4272":"MCO",
 "4279":"FRA","4280":"DEU","4330":"AUT","4351":"CZE","4359":"SVK","4370":"HUN","4411":"LIE","4419":"CHE","4470":"EST",
 "4490":"LVA","4510":"LTU","4550":"POL","4621":"RUS","4622":"BLR","4623":"UKR","4631":"ARM","4632":"AZE","4633":"GEO",
 "4634":"KAZ","4635":"KGZ","4641":"MDA","4642":"TJK","4643":"TKM","4644":"UZB","4700":"ESP","4710":"PRT","4720":"GIB",
 "4730":"MLT","4751":"SMR","4752":"VAT","4759":"ITA","4791":"HRV","4792":"SVN","4793":"BIH","4794":"MKD","4801":"SRB",
 "4802":"SRB","4803":"XKX","4804":"MNE","4810":"ALB","4840":"GRC","4850":"ROU","4870":"BGR","4890":"TUR","4910":"CYP",
 "5020":"SYR","5040":"LBN","5050":"IRQ","5070":"IRN","5080":"ISR","5081":"ISR","5082":"PSE","5083":"PSE","5110":"JOR",
 "5130":"KWT","5170":"SAU","5180":"QAT","5200":"ARE","5210":"YEM","5230":"OMN","5250":"BHR","5310":"AFG","5330":"IND",
 "5350":"PAK","5360":"NPL","5380":"BGD","5420":"LKA","5460":"MMR","5490":"THA","5520":"VNM","5530":"LAO","5550":"KHM",
 "5570":"MYS","5590":"SGP","5600":"IDN","5601":"TLS","5610":"BRN","5650":"PHL","5660":"MAC","5682":"BTN","5683":"MDV",
 "5700":"CHN","5740":"MNG","5790":"PRK","5800":"KOR","5820":"HKG","5830":"TWN","5880":"JPN","6021":"AUS","6022":"NFK",
 "6023":"CCK","6024":"CXR","6029":"HMD","6040":"PNG","6141":"NZL","6142":"COK","6143":"TKL","6144":"NIU","6150":"WSM",
 "6223":"SLB","6224":"VUT","6225":"PCN","6226":"KIR","6227":"TUV","6412":"NCL","6413":"WLF","6414":"PYF","6810":"MHL",
 "6820":"FSM","6830":"PLW","6862":"NRU","6863":"FJI","6864":"TON","7140":"MAR","7210":"DZA","7230":"TUN","7250":"LBY",
 "7290":"EGY","7320":"SDN","7321":"SDN","7323":"SSD","7370":"ESH","7380":"GNQ","7410":"MRT","7420":"CMR","7440":"SEN",
 "7450":"MLI","7460":"GIN","7470":"SLE","7480":"CIV","7490":"GHA","7500":"GMB","7510":"NER","7520":"TGO","7530":"NGA",
 "7540":"CAF","7550":"GAB","7560":"TCD","7580":"SHN","7600":"BFA","7610":"BEN","7620":"AGO","7630":"COG","7642":"GNB",
 "7643":"CPV","7644":"STP","7650":"LBR","7660":"COD","7670":"BDI","7690":"RWA","7700":"SOM","7740":"ETH","7741":"ERI",
 "7749":"ETH","7770":"DJI","7780":"UGA","7790":"KEN","7800":"SYC","7810":"IOT","7830":"TZA","7850":"MUS","7870":"MOZ",
 "7880":"MDG","7881":"MYT","7890":"COM","7904":"REU","7905":"ATF","7910":"ZAF","7920":"NAM","7930":"BWA","7940":"ZMB",
 "7950":"SWZ","7960":"ZWE","7970":"MWI","7990":"LSO"}
DROP = {"4350", "4610", "4790", "4799", "2771", "5160", "8220", "8500"}  # former states, neutral zone, unidentified, int'l orgs
WORLD = "0015"

wb = openpyxl.load_workbook(SRC, read_only=True)
ws = wb.worksheets[0]
hdr = None
imp = collections.defaultdict(dict); exp = collections.defaultdict(dict)  # key -> {yyyymm: value}
unmapped = set()
for r in ws.iter_rows(values_only=True):
    if hdr is None: hdr = r; continue
    if r[0] is None: break
    y, code, name = int(r[0]), str(r[1]).zfill(4), r[2]
    if code == WORLD: key = "WORLD"
    elif code in ISO: key = ISO[code]
    elif code in DROP or code.startswith("00"): continue
    else: unmapped.add((code, name)); continue
    for m in range(12):
        vi, ve = r[3 + m], r[16 + m]
        ym = y * 100 + m + 1
        if vi is None or ve is None: continue
        imp[key][ym] = imp[key].get(ym, 0) + float(vi)
        exp[key][ym] = exp[key].get(ym, 0) + float(ve)
if unmapped: raise SystemExit(f"unmapped Census codes: {sorted(unmapped)}")
# latest month = last month with non-zero world imports (future months are zero-filled)
months = sorted(ym for ym, v in imp["WORLD"].items() if v > 0)
LAST = months[-1]
ALL = [ym for ym in months]
def prev12(ym):  # the 12 months ending at ym
    y, m = divmod(ym, 100); out = []
    for _ in range(12):
        out.append(y * 100 + m); m -= 1
        if m == 0: y, m = y - 1, 12
    return out
def t12(d, ym):
    return sum(d.get(x, 0.0) for x in prev12(ym))
FRAMES = [ym for ym in ALL if ym >= 201712]
countries = sorted(k for k in imp if k != "WORLD")
r0 = lambda v: None if v is None else round(v)  # whole million USD
rb = lambda v: None if v is None else round(v / 1000, 1)  # million -> billion, 1 decimal
today = datetime.date.today().isoformat()
LMON = datetime.date(LAST // 100, LAST % 100, 1).strftime("%B %Y")
AS_OF = f"Census FT-900 country file, data through {LMON}"

def has_trade(c): return any(imp[c].get(ym, 0) or exp[c].get(ym, 0) for ym in ALL if ym >= 201701)
countries = [c for c in countries if has_trade(c)]

# ---------- imports.json ----------
wimp12 = [t12(imp["WORLD"], ym) for ym in FRAMES]
imp12 = {c: [r0(t12(imp[c], ym)) for ym in FRAMES] for c in countries}
share12 = {c: [round(t12(imp[c], ym) / w * 100, 2) for ym, w in zip(FRAMES, wimp12)] for c in countries}
latest12 = {c: imp12[c][-1] for c in countries}
TOPM = sorted(countries, key=lambda c: -latest12[c])[:30]
for c in ("CHN", "VNM", "MEX", "TWN", "CAN", "IRL", "IND", "THA"):
    if c not in TOPM: TOPM.append(c)
doc = {"source": "us-census", "asOf": AS_OF, "retrieved": today,
       "note": ("US general imports of goods by country of origin, Census basis, million USD, not seasonally adjusted. "
                "Years are yyyymm. imp12 = sum of the 12 months ending in that month (Dec = calendar year). "
                "imp_m = that month alone, for the 30 largest suppliers plus a few the stories name. share12 = % of all US goods imports "
                "over the same 12 months. Aggregates (EU, regions, World) are not in the country values; the world total is in 'world'. "
                "Built by tools/build/tw_census.py from https://www.census.gov/foreign-trade/balance/country.xlsx."),
       "format": "month", "years": FRAMES,
       "series": {
           "imp12": {"label": "US imports, 12 months to date", "units": "million USD", "values": imp12},
           "share12": {"label": "Share of US imports, 12 months", "units": "%", "values": share12},
           "imp_m": {"label": "US imports in the month", "units": "million USD",
                     "values": {c: [r0(imp[c].get(ym)) for ym in FRAMES] for c in TOPM}},
           "total_imp12": {"label": "All US goods imports, 12 months", "units": "million USD", "values": {"USA": [r0(v) for v in wimp12]}},
       },
       "world": {"imp12": [r0(v) for v in wimp12]}}
json.dump(doc, open(os.path.join(out_dir, "imports.json"), "w"), separators=(",", ":"))

# ---------- shift.json ----------
def cal(d, y): return sum(d.get(y * 100 + m, 0.0) for m in range(1, 13))
cur = {c: t12(imp[c], LAST) for c in countries}
y24 = {c: cal(imp[c], 2024) for c in countries}
y17 = {c: cal(imp[c], 2017) for c in countries}
wcur, w24, w17 = t12(imp["WORLD"], LAST), cal(imp["WORLD"], 2024), cal(imp["WORLD"], 2017)
def pct(a, b): return round((a / b - 1) * 100, 1) if b >= 100 else None  # only partners with >= $100 m base
shift = {"source": "us-census", "asOf": AS_OF, "retrieved": today,
         "note": (f"Change in US goods imports by origin: the 12 months to {LMON} compared with calendar 2024 and calendar 2017. "
                  "Billion USD (chg_*), million USD (imp_*) and percent (pct_*; only partners with at least $100 m of imports in the base year). "
                  "share_* = % of all US goods imports. Census basis, not seasonally adjusted. Built by tools/build/tw_census.py."),
         "years": [LAST],
         "series": {
             "chg_2024": {"label": f"Change in US imports, 12 months to {LMON} vs 2024", "units": "billion USD",
                          "values": {c: [rb(cur[c] - y24[c])] for c in countries}},
             "pct_2024": {"label": f"Change in US imports vs 2024", "units": "%", "values": {c: [pct(cur[c], y24[c])] for c in countries}},
             "chg_2017": {"label": f"Change in US imports, 12 months to {LMON} vs 2017", "units": "billion USD",
                          "values": {c: [rb(cur[c] - y17[c])] for c in countries}},
             "pct_2017": {"label": "Change in US imports vs 2017", "units": "%", "values": {c: [pct(cur[c], y17[c])] for c in countries}},
             "imp_2017": {"label": "US imports, 2017", "units": "million USD", "values": {c: [r0(y17[c])] for c in countries}},
             "imp_2024": {"label": "US imports, 2024", "units": "million USD", "values": {c: [r0(y24[c])] for c in countries}},
             "imp_latest": {"label": f"US imports, 12 months to {LMON}", "units": "million USD", "values": {c: [r0(cur[c])] for c in countries}},
             "share_2017": {"label": "Share of US imports, 2017", "units": "%", "values": {c: [round(y17[c] / w17 * 100, 2)] for c in countries}},
             "share_2024": {"label": "Share of US imports, 2024", "units": "%", "values": {c: [round(y24[c] / w24 * 100, 2)] for c in countries}},
             "share_latest": {"label": f"Share of US imports, 12 months to {LMON}", "units": "%", "values": {c: [round(cur[c] / wcur * 100, 2)] for c in countries}},
         },
         "world": {"imp_2017": [r0(w17)], "imp_2024": [r0(w24)], "imp_latest": [r0(wcur)]}}
ecur = {c: t12(exp[c], LAST) for c in countries}; e24 = {c: cal(exp[c], 2024) for c in countries}
shift["series"].update({
    "bal_2024": {"label": "US goods trade balance, 2024", "units": "billion USD", "values": {c: [rb(e24[c] - y24[c])] for c in countries}},
    "bal_latest": {"label": f"US goods trade balance, 12 months to {LMON}", "units": "billion USD", "values": {c: [rb(ecur[c] - cur[c])] for c in countries}},
    "bal_chg": {"label": f"Change in US goods trade balance, 12 months to {LMON} vs 2024", "units": "billion USD",
                "values": {c: [rb((ecur[c] - cur[c]) - (e24[c] - y24[c]))] for c in countries}},
    "exp_chg": {"label": f"Change in US goods exports, 12 months to {LMON} vs 2024", "units": "billion USD", "values": {c: [rb(ecur[c] - e24[c])] for c in countries}},
    "exp_latest": {"label": f"US goods exports, 12 months to {LMON}", "units": "million USD", "values": {c: [r0(ecur[c])] for c in countries}},
})
shift["note"] += (" bal_* = US goods trade balance with the partner (exports minus imports, billion USD; negative = US deficit), "
                  "bal_chg = latest 12 months minus 2024 (negative = the deficit grew). exp_* = US exports to the partner.")
json.dump(shift, open(os.path.join(out_dir, "shift.json"), "w"), separators=(",", ":"))

# ---------- balance.json ----------
bal12 = {c: [rb(t12(exp[c], ym) - t12(imp[c], ym)) for ym in FRAMES] for c in countries}
wexp12 = [t12(exp["WORLD"], ym) for ym in FRAMES]
bal = {"source": "us-census", "asOf": AS_OF, "retrieved": today,
       "note": ("US goods trade balance (exports minus imports) with each partner over the 12 months ending each month, billion USD, "
                "Census basis, not seasonally adjusted; negative = US deficit. Years are yyyymm (Dec = calendar year). "
                "bal24 / bal_latest / bal_chg: calendar 2024, the latest 12 months and the change between them. "
                "total_* keyed 'USA' are US totals with the whole world (Census line 'World, Not Seasonally Adjusted'). "
                "Built by tools/build/tw_census.py."),
       "format": "month", "years": FRAMES,
       "series": {
           "bal12": {"label": "US goods trade balance, 12 months", "units": "billion USD", "values": bal12},
           "exp12": {"label": "US exports, 12 months", "units": "billion USD", "values": {c: [rb(t12(exp[c], ym)) for ym in FRAMES] for c in countries}},
           "total_bal12": {"label": "US goods trade balance with the world, 12 months", "units": "billion USD",
                           "values": {"USA": [rb(e - i) for e, i in zip(wexp12, wimp12)]}},
           "total_imp12": {"label": "US goods imports, 12 months", "units": "billion USD", "values": {"USA": [rb(v) for v in wimp12]}},
           "total_exp12": {"label": "US goods exports, 12 months", "units": "billion USD", "values": {"USA": [rb(v) for v in wexp12]}},
       }}
json.dump(bal, open(os.path.join(out_dir, "balance.json"), "w"), separators=(",", ":"))

# ---------- balance_long.json ----------
LY = [y for y in range(1990, LAST // 100 + 1) if (y * 100 + 12) <= LAST]
blong = {"source": "us-census", "asOf": AS_OF, "retrieved": today,
         "note": ("Annual US goods trade with the world, billion USD, Census basis (exports minus general imports). "
                  "Built by tools/build/tw_census.py."),
         "years": LY,
         "series": {
             "bal": {"label": "US goods trade balance", "units": "billion USD", "values": {"USA": [rb(cal(exp["WORLD"], y) - cal(imp["WORLD"], y)) for y in LY]}},
             "imp": {"label": "US goods imports", "units": "billion USD", "values": {"USA": [rb(cal(imp["WORLD"], y)) for y in LY]}},
             "exp": {"label": "US goods exports", "units": "billion USD", "values": {"USA": [rb(cal(exp["WORLD"], y)) for y in LY]}},
         }}
json.dump(blong, open(os.path.join(out_dir, "balance_long.json"), "w"), separators=(",", ":"))

for f in ("imports.json", "shift.json", "balance.json", "balance_long.json"):
    print(f, os.path.getsize(os.path.join(out_dir, f)) // 1024, "KB")
print("latest month", LAST, "| world imports 12m", r0(wcur), "2024", r0(w24), "2017", r0(w17))
for c in ("CHN", "MEX", "CAN", "VNM", "TWN", "DEU", "JPN", "KOR", "IRL", "IND", "THA", "CHE"):
    print(c, "2017", r0(y17[c]), "2024", r0(y24[c]), "latest", r0(cur[c]), "share", round(y17[c]/w17*100,1), round(y24[c]/w24*100,1), round(cur[c]/wcur*100,1))
