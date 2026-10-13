"""US 'reciprocal' and related country-wide tariff rates, 2 April 2025 to today, plus the US-China tariff ladder.
Hand-compiled from primary documents (Federal Register, USTR, CBP CSMS); the 2 April 2025 Annex I is parsed from the
Federal Register PDF and the formula behind it is re-computed from US Census 2024 trade data as published in March 2025.

Fetch (into .cache/tw/, skipped when the file is there):
  eo14257_2025-06063.pdf   https://www.govinfo.gov/content/pkg/FR-2025-04-07/pdf/2025-06063.pdf  (EO 14257, Annex I on pp. 15049-50)
  country_2025-03-10.xlsx  Census FT-900 country file as of 10 March 2025 (2024 annual data before the June 2025 revision),
                           https://web.archive.org/web/20250310082419id_/https://www.census.gov/foreign-trade/balance/country.xlsx
Run:   python3 tools/build/tw_rates.py      (needs pdftotext from poppler-utils, openpyxl)
Output:
  data/tradewar/tw_rates.json   series keyed by date (yyyymmdd 'years'):
      rate       headline additional US tariff on most goods of the country in force on that date, in % (see note)
      announced  Annex I rate of 2 April 2025 (10% baseline elsewhere); filled at 20250402 only
      deficit    2024 US goods deficit with the partner as % of US imports from it (the 'tariffs charged to the USA'
                 column of the 2 April chart); filled at 20250402 only, deficit partners only
      formula    max(10, deficit / 2, rounded up); filled at 20250402 only
  data/tradewar/tw_china.json   series 'rate' keyed by date: CHN = additional US tariff on goods from China (new
      2025-26 measures), USA = China's across-the-board additional tariff on goods from the US; step points.
"""
import os, re, json, math, ast, subprocess, urllib.request, datetime
import openpyxl

root = os.path.join(os.path.dirname(__file__), "..", "..")
cache = os.path.join(root, ".cache/tw"); out_dir = os.path.join(root, "data/tradewar")
UA = {"User-Agent": "Orbis-data-build/1.0"}
os.makedirs(cache, exist_ok=True); os.makedirs(out_dir, exist_ok=True)
FILES = {
    "eo14257_2025-06063.pdf": "https://www.govinfo.gov/content/pkg/FR-2025-04-07/pdf/2025-06063.pdf",
    "country_2025-03-10.xlsx": "https://web.archive.org/web/20250310082419id_/https://www.census.gov/foreign-trade/balance/country.xlsx",
}
for fn, url in FILES.items():
    p = os.path.join(cache, fn)
    if not os.path.exists(p):
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r, open(p, "wb") as f: f.write(r.read())

EU = "AUT BEL BGR HRV CYP CZE DNK EST FIN FRA DEU GRC HUN IRL ITA LVA LTU LUX MLT NLD POL PRT ROU SVK SVN ESP SWE ALA".split()
CHINA = ["CHN", "HKG", "MAC"]  # EO 14257 and later orders treat Hong Kong and Macau goods as China's
NAME = {  # names used in the annexes and USTR notices -> ISO3 (European Union expands to EU)
 "Afghanistan":"AFG","Algeria":"DZA","Angola":"AGO","Argentina":"ARG","Australia":"AUS","The Bahamas":"BHS","Bahrain":"BHR",
 "Bangladesh":"BGD","Bolivia":"BOL","Bosnia and Herzegovina":"BIH","Botswana":"BWA","Brazil":"BRA","Brunei":"BRN",
 "Cambodia":"KHM","Cameroon":"CMR","Canada":"CAN","Chad":"TCD","Chile":"CHL","China":"CHN","Colombia":"COL","Costa Rica":"CRI",
 "Cote d'Ivoire":"CIV","Côte d'Ivoire":"CIV","Democratic Republic of the Congo":"COD","Dominican Republic":"DOM","Ecuador":"ECU",
 "Egypt":"EGY","El Salvador":"SLV","Equatorial Guinea":"GNQ","Falkland Islands":"FLK","Fiji":"FJI","Ghana":"GHA",
 "Guatemala":"GTM","Guyana":"GUY","Honduras":"HND","Hong Kong":"HKG","Iceland":"ISL","India":"IND","Indonesia":"IDN","Iraq":"IRQ",
 "Israel":"ISR","Japan":"JPN","Jordan":"JOR","Kazakhstan":"KAZ","Kuwait":"KWT","Laos":"LAO","Lesotho":"LSO","Libya":"LBY",
 "Liechtenstein":"LIE","Madagascar":"MDG","Malawi":"MWI","Malaysia":"MYS","Mauritius":"MUS","Mexico":"MEX","Moldova":"MDA",
 "Morocco":"MAR","Mozambique":"MOZ","Myanmar (Burma)":"MMR","Namibia":"NAM","Nauru":"NRU","New Zealand":"NZL","Nicaragua":"NIC",
 "Nigeria":"NGA","North Macedonia":"MKD","Norway":"NOR","Oman":"OMN","Pakistan":"PAK","Papua New Guinea":"PNG","Peru":"PER",
 "Philippines":"PHL","Qatar":"QAT","Russia":"RUS","Saudi Arabia":"SAU","Serbia":"SRB","Singapore":"SGP","South Africa":"ZAF",
 "South Korea":"KOR","Sri Lanka":"LKA","Switzerland":"CHE","Syria":"SYR","Taiwan":"TWN","Thailand":"THA",
 "Trinidad and Tobago":"TTO","Tunisia":"TUN","Turkey":"TUR","Uganda":"UGA","United Arab Emirates":"ARE","United Kingdom":"GBR",
 "Uruguay":"URY","Vanuatu":"VUT","Venezuela":"VEN","Vietnam":"VNM","Zambia":"ZMB","Zimbabwe":"ZWE",
}
def expand(d):
    out = {}
    for n, v in d.items():
        if n == "European Union": out.update({c: v for c in EU})
        else: out[NAME[n]] = v
    return out

# --- Annex I of EO 14257 (2 April 2025), parsed from the Federal Register PDF ---------------------------------------
txt = subprocess.run(["pdftotext", "-layout", "-f", "9", "-l", "10", os.path.join(cache, "eo14257_2025-06063.pdf"), "-"],
                     capture_output=True, text=True, check=True).stdout
APR = {}
for line in txt.splitlines():
    m = re.match(r"^\s{20,}([A-Z][A-Za-z' ().]+?)\s{3,}(\d+)%\s*$", line)
    if m: APR[m.group(1).strip()] = int(m.group(2))
assert len(APR) == 57, len(APR)
APR = expand(APR)

# --- Annex I of EO 14326 (31 July 2025, in force 7 August 2025). The annex is an image in the Federal Register
# (90 FR 37967-37969); transcribed by hand. EU: 15% including the MFN duty (0% extra where MFN >= 15%).
AUG = expand({
 "Afghanistan":15,"Algeria":30,"Angola":15,"Bangladesh":20,"Bolivia":15,"Bosnia and Herzegovina":30,"Botswana":15,"Brazil":10,
 "Brunei":25,"Cambodia":19,"Cameroon":15,"Chad":15,"Costa Rica":15,"Côte d'Ivoire":15,"Democratic Republic of the Congo":15,
 "Ecuador":15,"Equatorial Guinea":15,"European Union":15,"Falkland Islands":10,"Fiji":15,"Ghana":15,"Guyana":15,"Iceland":15,
 "India":25,"Indonesia":19,"Iraq":35,"Israel":15,"Japan":15,"Jordan":15,"Kazakhstan":25,"Laos":40,"Lesotho":15,"Libya":30,
 "Liechtenstein":15,"Madagascar":15,"Malawi":15,"Malaysia":19,"Mauritius":15,"Moldova":25,"Mozambique":15,"Myanmar (Burma)":40,
 "Namibia":15,"Nauru":15,"New Zealand":15,"Nicaragua":18,"Nigeria":15,"North Macedonia":15,"Norway":15,"Pakistan":19,
 "Papua New Guinea":15,"Philippines":19,"Serbia":35,"South Africa":30,"South Korea":15,"Sri Lanka":20,"Switzerland":39,
 "Syria":41,"Taiwan":20,"Thailand":19,"Trinidad and Tobago":15,"Tunisia":25,"Turkey":15,"Uganda":15,"United Kingdom":10,
 "Vanuatu":15,"Venezuela":15,"Vietnam":20,"Zambia":15,"Zimbabwe":15})
assert len(AUG) == 69 - 1 + len(EU), len(AUG)

# --- Section 301 'forced labour' tariffs, USTR notice 2026-15181 (91 FR 47318), in force 24 July 2026 -----------------
# 10%: listed below; EU and Taiwan 10% net of MFN; Japan, Korea, Switzerland 12.5% net of MFN; all other 60 economies 12.5%.
FL10 = ["Argentina","Bangladesh","Cambodia","Canada","Ecuador","El Salvador","Guatemala","Honduras","India","Indonesia","Jordan",
        "Malaysia","Mexico","Pakistan","Sri Lanka","United Kingdom","Trinidad and Tobago","European Union","Taiwan"]
FL125 = ["Algeria","Angola","Australia","The Bahamas","Bahrain","Brazil","Chile","China","Colombia","Costa Rica","Dominican Republic",
         "Egypt","Guyana","Hong Kong","Iraq","Israel","Japan","Kazakhstan","Kuwait","Libya","Morocco","New Zealand","Nicaragua",
         "Nigeria","Norway","Oman","Peru","Philippines","Qatar","Russia","Saudi Arabia","Singapore","South Africa","South Korea",
         "Switzerland","Thailand","Turkey","United Arab Emirates","Uruguay","Venezuela","Vietnam"]
FL = {**expand({n: 10 for n in FL10}), **expand({n: 12.5 for n in FL125})}
assert len(FL10) + len(FL125) == 60

# --- universe: every country the map draws, minus the US and its territories, column-2 countries (not covered by the
# reciprocal tariffs: CBP CSMS 64649265), and uninhabited or disputed areas without separate customs data
world = json.load(open(os.path.join(root, "data/world50.json")))
ids = sorted(g.get("id") or g["properties"].get("iso3") for g in world["objects"]["countries"]["geometries"])
SKIP = set("USA PRI GUM VIR ASM MNP RUS BLR CUB PRK ATA HMD ATF SGS IOT IOA ATC KAS ESH NCY SOL".split())
U = [c for c in ids if c not in SKIP]

DATES = [20250402, 20250405, 20250409, 20250410, 20250514, 20250801, 20250806, 20250807, 20250827,
         20251110, 20251114, 20260207, 20260224, 20260722, 20260724, 20261013]

def rate(c, d):
    if c == "LIE" and d >= 20260724: return None  # not among the 60 economies; whether Swiss treatment extends is not stated
    r = 0
    # IEEPA 'fentanyl' duties (EO 14193/14194/14195 as amended; 14325 for Canada at 35% from 1 Aug 2025; 14357 China 10%)
    if d < 20260224:
        if c in CHINA: r += 20 if d < 20251110 else 10
        if c == "CAN": r += 35 if d >= 20250801 else 25
        if c == "MEX": r += 25
    # IEEPA reciprocal tariff (EO 14257 and amendments); Canada and Mexico are outside it
    if c not in ("CAN", "MEX") and 20250405 <= d < 20260224:
        if c in CHINA:
            r += 10 if d < 20250409 else 84 if d < 20250410 else 125 if d < 20250514 else 10
        elif d == 20250409: r += APR.get(c, 10)
        elif d < 20250807: r += 10
        elif c in ("CHE", "LIE") and d >= 20251114: r += 15
        else: r += AUG.get(c, 10)
    if c == "BRA" and 20250806 <= d < 20260224: r += 40           # EO 14323
    if c == "IND" and 20250827 <= d < 20260207: r += 25           # EO 14329, ended by EO 14384
    if 20260224 <= d < 20260724: r += 10                          # Section 122 surcharge, Proclamation 11012
    if c == "BRA" and d >= 20260722: r += 25                      # Section 301 Brazil, USTR notice 2026-14542
    if d >= 20260724: r += FL.get(c, 0)                           # Section 301 forced labour, USTR notice 2026-15181
    return r

# --- the 2 April formula, re-computed from Census 2024 data as published before Annex I ------------------------------
src = open(os.path.join(os.path.dirname(__file__), "tw_census.py")).read()
CEN = ast.literal_eval(re.search(r"ISO = (\{.*?\})\n", src, re.S).group(1))
wb = openpyxl.load_workbook(os.path.join(cache, "country_2025-03-10.xlsx"), read_only=True); ws = wb.active
rows = list(ws.iter_rows(values_only=True)); h = rows[0]; iI, iE = h.index("IYR"), h.index("EYR")
T = {}
for r in rows[1:]:
    if str(r[0]) != "2024": continue
    code, name = str(r[1]), r[2]
    if code == "0003": key = "EU"
    elif code in CEN: key = CEN[code]
    else: continue
    T[key] = (r[iI], r[iE])
deficit, formula = {}, {}
for c in U:
    k = "EU" if c in EU else ("CHN" if c in CHINA else c)
    if c in ("HKG", "MAC"): continue  # not listed separately in April; they took China's rate
    if k not in T: continue
    m, x = T[k]
    if not m or m <= 0: continue
    raw = (m - x) / m * 100
    if raw > 0: deficit[c] = round(raw, 1)
    formula[c] = max(10, math.ceil(round(raw) / 2)) if c not in ("CAN", "MEX") else None
check = [(c, formula[c], APR[c]) for c in APR if c in formula and formula[c] is not None]
exact = sum(1 for c, f, a in check if f == a)
miss = sorted({c for c, f, a in check if f != a} - set(EU))
print(f"formula check: {exact}/{len(check)} annex rates reproduced exactly (EU members counted individually); off: {miss}")

n = len(DATES)
def series(fn): return {c: [fn(c, d) for d in DATES] for c in U}
def first(vals): return {c: [v] + [None] * (n - 1) for c, v in vals.items() if v is not None}
ann = {c: (APR.get(c, 10) if c not in ("CAN", "MEX") else None) for c in U}
for c in CHINA: ann[c] = 34

today = datetime.date.today().isoformat()
note = ("Headline additional US tariff on most goods of each country, in percent, in force on each date (12:01 a.m. US Eastern). "
 "Adds up the country-wide measures only: IEEPA 'fentanyl' duties (EO 14193 Canada, 14194 Mexico, 14195 China, as amended by "
 "EO 14228, 14231/14232, 14325, 14357), IEEPA reciprocal tariffs (EO 14257 of 2 Apr 2025, FR 2025-06063, 10% baseline from 5 Apr, "
 "Annex I rates from 9 Apr; EO 14259 China 84% on 9 Apr; EO 14266 pause and China 125% from 10 Apr; EO 14298 China 10% from "
 "14 May; EO 14326 Annex I rates from 7 Aug 2025, FR 2025-15010; Switzerland and Liechtenstein 15% from 14 Nov 2025, FR 2025-23316), "
 "Brazil +40% (EO 14323, from 6 Aug 2025), India +25% for Russian oil (EO 14329, from 27 Aug 2025; ended 7 Feb 2026 by EO 14384), "
 "then, after the Supreme Court ruled on 20 Feb 2026 (Learning Resources v. Trump) that IEEPA does not authorise tariffs, CBP stopped "
 "collecting all IEEPA duties from 24 Feb 2026 (EO 14389; CSMS 67834313) and a 10% Section 122 surcharge applied to all countries "
 "24 Feb-24 Jul 2026 (Proclamation 11012, FR 2026-03824; CSMS 67844987; an announced rise to 15% was never proclaimed). From 22 Jul "
 "2026 Section 301 adds 25% on Brazil (USTR FR 2026-14542) and from 24 Jul 2026 Section 301 'forced labour' tariffs of 10% or 12.5% "
 "apply to 60 economies (memorandum FR 2026-15274, USTR notice FR 2026-15181); other countries then pay no country-wide extra tariff. "
 "Not included: sector tariffs under Section 232 (steel, aluminium, copper, cars, trucks, lumber, pharmaceuticals, semiconductors...), "
 "older Section 301 tariffs on China (7.5-100%), Section 338 duties on some Canadian goods (from 22 Aug 2026), product exemptions "
 "(e.g. energy, many farm goods from 14 Nov 2025, EO 14360) and the USMCA exemption that covers most goods from Canada and Mexico. "
 "EU (from 7 Aug 2025), Japan, South Korea and Switzerland (from 14 Nov 2025): the rate is 'all-in', i.e. includes the normal MFN duty; "
 "the 2026 Section 301 rates for the EU, Taiwan, Japan, South Korea and Switzerland are likewise net of MFN. Hong Kong and Macau take "
 "China's rates. Russia, Belarus, Cuba and North Korea (column-2 countries, outside the reciprocal tariffs) are not shown. "
 "Liechtenstein after 24 Jul 2026 is left blank. 'announced' = Annex I of EO 14257 (57 partners, EU as one; everyone else 10%). "
 "'deficit' = (US imports - US exports) / US imports, 2024, Census FT-900 data as published 6 Mar 2025 (archived copy of "
 "census.gov/foreign-trade/balance/country.xlsx, 10 Mar 2025). 'formula' = max(10, deficit rounded to a whole percent, halved and "
 f"rounded up), the USTR method (ustr.gov 'Reciprocal Tariff Calculations': rate = deficit / (4 x 0.25 x imports)) halved per EO 14257: "
 f"it reproduces {exact} of {len(check)} Annex I rates exactly (EU members counted individually) and the rest within 1 point "
 f"({', '.join(miss)}).")
out = {
 "source": "us-fedreg", "asOf": "2026-10-13", "retrieved": today, "note": note, "step": True, "format": "date",
 "years": DATES,
 "series": {
  "rate": {"label": "Additional US tariff, country-wide", "units": "%", "values": series(rate)},
  "announced": {"label": "Rate announced on 2 April 2025", "units": "%", "values": first(ann)},
  "deficit": {"label": "US goods deficit as % of US imports, 2024", "units": "%", "values": first(deficit)},
  "formula": {"label": "Rate from the April formula", "units": "%", "values": first(formula)},
 },
}
json.dump(out, open(os.path.join(out_dir, "tw_rates.json"), "w"), separators=(",", ":"))

# --- US-China ladder (step points: the day before each change repeats the old rate) ----------------------------------
US_ON_CN = [(20250101, 0), (20250204, 10), (20250304, 20), (20250405, 30), (20250409, 104), (20250410, 145),
            (20250514, 30), (20251110, 20), (20260224, 10), (20260724, 12.5)]
CN_ON_US = [(20250101, 0), (20250410, 84), (20250412, 125), (20250514, 10)]  # across-the-board only; last confirmed 20 Feb 2026
END, CN_END = 20261013, 20260220
def prev(d):
    x = datetime.date(d // 10000, d // 100 % 100, d % 100) - datetime.timedelta(days=1)
    return x.year * 10000 + x.month * 100 + x.day
pts = set([END, CN_END])
for d, _ in US_ON_CN + CN_ON_US:
    pts.add(d)
    if d > 20250101: pts.add(prev(d))
Y = sorted(pts)
def stepv(tab, d, end):
    if d > end: return None
    return [v for t, v in tab if t <= d][-1]
china = {
 "source": "us-fedreg", "asOf": "2026-10-13", "retrieved": today, "step": True, "format": "date",
 "note": ("CHN = additional US tariff on most goods from China (and Hong Kong, Macau) introduced since 2025, in percent: IEEPA "
  "'fentanyl' duties 10% from 4 Feb 2025 (EO 14195) and 20% from 4 Mar 2025 (EO 14228), cut to 10% from 10 Nov 2025 (EO 14357); "
  "IEEPA reciprocal 10% from 5 Apr, 84% on 9 Apr (EO 14259), 125% from 10 Apr (EO 14266), 10% from 14 May 2025 (EO 14298, after the "
  "Geneva joint statement of 12 May; the remaining 24 points stayed suspended, EO 14334 and 14358); all IEEPA duties ended 24 Feb 2026 "
  "(Supreme Court, 20 Feb 2026; EO 14389); Section 122 surcharge 10% 24 Feb-24 Jul 2026 (Proclamation 11012); Section 301 'forced "
  "labour' tariff 12.5% from 24 Jul 2026 (USTR FR 2026-15181). Excludes the Section 301 tariffs of 2018-19 (7.5-25% on about two-thirds "
  "of imports from China, raised to up to 100% on some goods in 2024) and Section 232 sector tariffs, which apply on top. "
  "USA = China's additional tariff on all goods from the US: 34% announced 4 Apr and raised to 84% before it took effect on 10 Apr "
  "(State Council Tariff Commission), 125% from 12 Apr, 10% from 14 May 2025 (24 points suspended; suspension extended for a year from "
  "10 Nov 2025, Tariff Commission announcement 2025 No. 10). Not shown: China's targeted tariffs of 10-15% on coal, LNG, crude oil, "
  "farm machinery and cars (from 10 Feb 2025) and on US farm goods (10 Mar 2025, lifted 10 Nov 2025). China's line stops at 20 Feb "
  "2026: no official notice changing the 10% was found, so its later level is not shown. Step points: the day before each change "
  "repeats the old rate."),
 "years": Y,
 "series": {"rate": {"label": "Extra tariff on goods from …", "units": "%", "values": {
   "CHN": [stepv(US_ON_CN, d, END) for d in Y], "USA": [stepv(CN_ON_US, d, CN_END) for d in Y]}}},
}
json.dump(china, open(os.path.join(out_dir, "tw_china.json"), "w"), separators=(",", ":"))
print("wrote tw_rates.json", len(U), "countries x", len(DATES), "dates; tw_china.json", len(Y), "dates")
