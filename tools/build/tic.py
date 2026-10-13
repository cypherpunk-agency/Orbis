"""Major foreign holders of US Treasury securities, December of each year, from the US Treasury TIC system (public domain).
Fetch:
  mkdir -p .cache/tic && cd .cache/tic
  curl -O https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/mfhhis01.txt   # history 2000-2025
  curl -O https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table5.txt # current 13 months
Run: python3 tools/build/tic.py
Output: data/finance/tic.json  flow file, group "treasuries": flows holder -> USA, exports = held by country,
  imports = {"USA": grand total}; "other" = aggregates that are not countries (Caribbean banking centres, oil exporters, all other)."""
import os, json, re, datetime, csv
root = os.path.join(os.path.dirname(__file__), "..", "..")
cache = os.path.join(root, ".cache/tic")
YEARS = list(range(2005, 2026))
ISO = {
    "Japan": "JPN", "China, Mainland": "CHN", "United Kingdom": "GBR", "Belgium": "BEL", "Luxembourg": "LUX",
    "Switzerland": "CHE", "Cayman Islands": "CYM", "Canada": "CAN", "Ireland": "IRL", "France": "FRA", "Taiwan": "TWN",
    "Singapore": "SGP", "Hong Kong": "HKG", "Norway": "NOR", "India": "IND", "Brazil": "BRA", "Saudi Arabia": "SAU",
    "Korea, South": "KOR", "United Arab Emirates": "ARE", "Bermuda": "BMU", "Israel": "ISR", "Germany": "DEU",
    "El Salvador": "SLV", "Mexico": "MEX", "Thailand": "THA", "Spain": "ESP", "Australia": "AUS", "Netherlands": "NLD",
    "Kuwait": "KWT", "Italy": "ITA", "Philippines": "PHL", "Sweden": "SWE", "Poland": "POL", "Colombia": "COL",
    "Chile": "CHL", "Turkey": "TUR", "Russia": "RUS", "Peru": "PER", "Vietnam": "VNM", "Malaysia": "MYS", "Iraq": "IRQ",
    "Indonesia": "IDN", "Denmark": "DNK", "South Africa": "ZAF", "Kazakhstan": "KAZ", "Oman": "OMN", "Egypt": "EGY",
    "Bahamas": "BHS", "Uruguay": "URY", "Finland": "FIN",
}
OTHER = {"Oil Exporters": "Oil exporters (discontinued after Feb 2016)",
         "Carib Bnkng Ctrs": "Caribbean banking centres (discontinued after Feb 2016)",
         "All Other": "All other", "Grand Total": "Grand total", "For. Official": "Of which: foreign official"}
SKIP = {"Treasury Bills", "T-Bonds & Notes", "Belgium-Luxembourg"}
def clean(name):
    name = re.sub(r"\s*\d+/\s*$", "", name.strip().strip('"').strip())  # drop footnote marks like "United Kingdom 2/"
    return name.strip()
held, other = {}, {}
year = None
for row in csv.reader(open(os.path.join(cache, "mfhhis01.txt"), encoding="latin-1"), delimiter="\t"):
    if not row: continue
    name = clean(row[0])
    if name == "Country":
        year = int(row[1]) if row[1].strip().isdigit() else None
        continue
    if year not in YEARS or len(row) < 2: continue
    v = row[1].strip()
    if not re.match(r"^[\d.]+$", v): continue
    v = float(v)  # first column of each block is December
    if name in SKIP: continue
    if name in OTHER: other.setdefault(year, {})[OTHER[name]] = v
    elif name in ISO: held.setdefault(year, {})[ISO[name]] = v
    else: raise SystemExit(f"unmapped TIC row {name!r} ({year})")
# cross-check the latest December against the current table
cur = list(csv.reader(open(os.path.join(cache, "slt_table5.txt"), encoding="latin-1"), delimiter="\t"))
hdr = next(r for r in cur if r and r[0] == "Country")
col = hdr.index(f"{YEARS[-1]}-12") if f"{YEARS[-1]}-12" in hdr else None
if col:
    for r in cur:
        if r and r[0] in ISO and abs(float(r[col]) - held[YEARS[-1]][ISO[r[0]]]) > 0.11:
            print("WARN current table differs", r[0], r[col], held[YEARS[-1]][ISO[r[0]]])
as_of = next((l.strip().strip('"') for l in open(os.path.join(cache, "mfhhis01.txt"), encoding="latin-1")
              if re.match(r"^\d+/\d+/\d{4}", l)), "")
g = {"label": "Foreign holdings of US Treasury securities (December)", "flows": {}, "exports": {}, "imports": {}, "other": {}}
for y in YEARS:
    h = held.get(y, {})
    g["flows"][y] = [[c, "USA", round(v, 1), None] for c, v in sorted(h.items(), key=lambda kv: -kv[1])]
    g["exports"][y] = {c: round(v, 1) for c, v in sorted(h.items(), key=lambda kv: -kv[1])}
    g["imports"][y] = {"USA": other[y]["Grand total"]}
    g["other"][y] = other[y]
doc = {"source": "us-tic", "asOf": f"TIC Major Foreign Holders history file, dated {as_of.split(chr(9))[0]}",
       "retrieved": datetime.date.today().isoformat(),
       "note": ("US Treasury bills, bonds and notes held by foreign residents at end-December, billion USD. Flow = holder -> USA; "
                "exports = holdings by the country, imports.USA = grand total of foreign holdings. Countries listed by Treasury only "
                "(the rest is in other['All other']). 'other' holds non-country aggregates. Custodial caveat: holdings are attributed "
                "to the country of the custodian, so securities held in custody in Belgium, Luxembourg, the UK, Switzerland or "
                "Caribbean centres may belong to investors elsewhere (e.g. China). Series breaks at each annual survey; "
                "December 2011 onward include SLT data. UK includes Channel Islands and Isle of Man."),
       "units": {"value": "billion USD"}, "years": YEARS, "groups": {"treasuries": g}}
p = os.path.join(root, "data/finance/tic.json")
json.dump(doc, open(p, "w"), separators=(",", ":"))
print(p, os.path.getsize(p) // 1024, "KB;", {y: len(held.get(y, {})) for y in YEARS})
for y in (YEARS[0], 2011, YEARS[-1]):
    print(y, g["flows"][y][:5], g["other"][y])
