"""Crop production by country from FAOSTAT "Production: Crops and livestock products" (QCL), CC BY 4.0.
FAO terms: CC BY 4.0, and FAO data may not be used in any commercial promotion or to imply FAO endorsement.
Fetch: mkdir -p .cache/faostat && curl -sSL -o '.cache/faostat/Production_Crops_Livestock_E_All_Data_(Normalized).zip' \
  'https://bulks-faostat.fao.org/production/Production_Crops_Livestock_E_All_Data_(Normalized).zip'
  (listed in https://bulks-faostat.fao.org/production/datasets_E.json as QCL)
Run:   python3 tools/build/fao.py
Output: data/resources/fao.json  {source, asOf, retrieved, note, years, series:{key:{label, units, values:{ISO3:[...]}}}}"""
import os, csv, io, json, zipfile, datetime
root = os.path.join(os.path.dirname(__file__), "..", "..")
ZIP = os.path.join(root, ".cache/faostat", "Production_Crops_Livestock_E_All_Data_(Normalized).zip")
URL = "https://bulks-faostat.fao.org/production/Production_Crops_Livestock_E_All_Data_(Normalized).zip"
ELEMENT = "5510"  # Production, tonnes
SERIES = {  # key: (FAO item code, label)
    "wheat": ("15", "Wheat, production"),
    "maize": ("56", "Maize (corn), production"),
    "rice": ("27", "Rice (paddy), production"),
    "soybeans": ("236", "Soya beans, production"),
    "coffee": ("656", "Coffee, green, production"),
    "cocoa": ("661", "Cocoa beans, production"),
    "sugarcane": ("156", "Sugar cane, production"),
    "palm_oil": ("257", "Palm oil, production"),
    "oil_palm_fruit": ("254", "Oil palm fruit, production"),
}
Y0 = 2000
# FAO area code -> ISO3. Countries only: aggregates (codes >= 5000), "China" (351 = mainland + HK + Macao + Taiwan)
# and dissolved states (USSR, Yugoslav SFR, Czechoslovakia, Serbia and Montenegro, Belgium-Luxembourg, Ethiopia PDR)
# are left out. "China; mainland" (41) -> CHN, Taiwan (214) -> TWN; Sudan (former, 206, to 2011) and Sudan (276) -> SDN.
ISO = {
    2:"AFG", 3:"ALB", 4:"DZA", 7:"AGO", 8:"ATG", 9:"ARG", 1:"ARM", 10:"AUS", 11:"AUT", 52:"AZE", 12:"BHS", 13:"BHR", 16:"BGD", 14:"BRB",
    57:"BLR", 255:"BEL", 23:"BLZ", 53:"BEN", 18:"BTN", 19:"BOL", 80:"BIH", 20:"BWA", 21:"BRA", 26:"BRN", 27:"BGR", 233:"BFA", 29:"BDI", 35:"CPV",
    115:"KHM", 32:"CMR", 33:"CAN", 37:"CAF", 39:"TCD", 40:"CHL", 96:"HKG", 128:"MAC", 41:"CHN", 214:"TWN", 44:"COL", 45:"COM", 46:"COG", 47:"COK",
    48:"CRI", 107:"CIV", 98:"HRV", 49:"CUB", 50:"CYP", 167:"CZE", 116:"PRK", 250:"COD", 54:"DNK", 72:"DJI", 55:"DMA", 56:"DOM", 58:"ECU", 59:"EGY",
    60:"SLV", 61:"GNQ", 178:"ERI", 63:"EST", 209:"SWZ", 238:"ETH", 64:"FRO", 66:"FJI", 67:"FIN", 68:"FRA", 69:"GUF", 70:"PYF", 74:"GAB", 75:"GMB",
    73:"GEO", 79:"DEU", 81:"GHA", 84:"GRC", 86:"GRD", 87:"GLP", 89:"GTM", 90:"GIN", 175:"GNB", 91:"GUY", 93:"HTI", 95:"HND", 97:"HUN", 99:"ISL",
    100:"IND", 101:"IDN", 102:"IRN", 103:"IRQ", 104:"IRL", 105:"ISR", 106:"ITA", 109:"JAM", 110:"JPN", 112:"JOR", 108:"KAZ", 114:"KEN", 83:"KIR", 118:"KWT",
    113:"KGZ", 120:"LAO", 119:"LVA", 121:"LBN", 122:"LSO", 123:"LBR", 124:"LBY", 126:"LTU", 256:"LUX", 129:"MDG", 130:"MWI", 131:"MYS", 132:"MDV", 133:"MLI",
    134:"MLT", 127:"MHL", 135:"MTQ", 136:"MRT", 137:"MUS", 138:"MEX", 145:"FSM", 141:"MNG", 273:"MNE", 143:"MAR", 144:"MOZ", 28:"MMR", 147:"NAM", 148:"NRU",
    149:"NPL", 150:"NLD", 153:"NCL", 156:"NZL", 157:"NIC", 158:"NER", 159:"NGA", 160:"NIU", 154:"MKD", 162:"NOR", 221:"OMN", 165:"PAK", 299:"PSE", 166:"PAN",
    168:"PNG", 169:"PRY", 170:"PER", 171:"PHL", 173:"POL", 174:"PRT", 177:"PRI", 179:"QAT", 117:"KOR", 146:"MDA", 182:"REU", 183:"ROU", 185:"RUS", 184:"RWA",
    188:"KNA", 189:"LCA", 191:"VCT", 244:"WSM", 193:"STP", 194:"SAU", 195:"SEN", 272:"SRB", 196:"SYC", 197:"SLE", 200:"SGP", 199:"SVK", 198:"SVN", 25:"SLB",
    201:"SOM", 202:"ZAF", 277:"SSD", 203:"ESP", 38:"LKA", 276:"SDN", 206:"SDN", 207:"SUR", 210:"SWE", 211:"CHE", 212:"SYR", 208:"TJK", 216:"THA", 176:"TLS",
    217:"TGO", 219:"TON", 220:"TTO", 222:"TUN", 223:"TUR", 213:"TKM", 227:"TUV", 226:"UGA", 230:"UKR", 225:"ARE", 229:"GBR", 215:"TZA", 231:"USA", 234:"URY",
    235:"UZB", 155:"VUT", 236:"VEN", 237:"VNM", 249:"YEM", 251:"ZMB", 181:"ZWE",
}
item_key = {code: k for k, (code, _) in SERIES.items()}
def sig(v):  # 3 significant figures, as in the other build scripts
    return None if v is None else float(f"{v:.3g}")

z = zipfile.ZipFile(ZIP)
data = {k: {} for k in SERIES}  # key -> ISO3 -> {year: value}
world = {k: {} for k in SERIES}
units, y1 = set(), Y0
with z.open("Production_Crops_Livestock_E_All_Data_(Normalized).csv") as f:
    for r in csv.DictReader(io.TextIOWrapper(f, "utf-8", errors="replace")):
        if r["Element Code"] != ELEMENT: continue
        k = item_key.get(r["Item Code"])
        if not k: continue
        y = int(r["Year"])
        if y < Y0 or r["Value"] == "": continue
        a, v = int(r["Area Code"]), float(r["Value"])
        if a == 5000: world[k][y] = v; continue
        iso = ISO.get(a)
        if not iso: continue
        units.add(r["Unit"])
        d = data[k].setdefault(iso, {})
        d[y] = d.get(y, 0) + v  # only Sudan has two area codes, and they do not overlap in time
        y1 = max(y1, y)
if units != {"t"}: raise SystemExit(f"unexpected units {units}")
YEARS = list(range(Y0, y1 + 1))
series = {}
for k, (code, label) in SERIES.items():
    vals = {iso: [sig(d.get(y)) for y in YEARS] for iso, d in sorted(data[k].items())}
    series[k] = {"label": label, "units": "tonnes", "values": {c: v for c, v in vals.items() if any(v)}}
info = json.load(open(os.path.join(os.path.dirname(ZIP), "datasets_E.json"))) if os.path.exists(os.path.join(os.path.dirname(ZIP), "datasets_E.json")) else None
updated = ""
if info:
    updated = next((d["DateUpdate"][:10] for d in info["Datasets"]["Dataset"] if d["DatasetCode"] == "QCL"), "")
doc = {
    "source": "faostat", "asOf": f"FAOSTAT QCL{', updated ' + updated if updated else ''}",
    "retrieved": datetime.date.today().isoformat(),
    "note": "FAO area codes mapped to ISO3; aggregates excluded; CHN = China mainland, TWN separate. Includes FAO "
            "estimated/imputed values. CC BY 4.0; no use in commercial promotion. " + URL,
    "years": YEARS, "series": series,
}
p = os.path.join(root, "data/resources/fao.json")
os.makedirs(os.path.dirname(p), exist_ok=True)
json.dump(doc, open(p, "w"), separators=(",", ":"))
print(p, os.path.getsize(p) // 1024, "KB; years", YEARS[0], "-", YEARS[-1], {k: len(s["values"]) for k, s in series.items()})
for k in SERIES:  # top 5 in each series' own latest year (processed palm oil lags crops by a year)
    yl = max(y for d in data[k].values() for y in d); i = YEARS.index(yl); w = world[k].get(yl)
    top = sorted(((c, v[i]) for c, v in series[k]["values"].items() if v[i]), key=lambda t: -t[1])[:5]
    print(k, yl, "world", w, ":", ", ".join(f"{c} {v:.3g} ({v / w:.0%})" if w else f"{c} {v:.3g}" for c, v in top))
