"""World mine production and reserves for critical and major minerals, USGS Mineral Commodity Summaries 2026 (CC0).
Data release: https://www.sciencebase.gov/catalog/item/69837e43b66b01367d7ec7c7  (doi:10.5066/P1WKQ63T,
landing page https://www.usgs.gov/data/mineral-commodity-summaries-2026-data-release)
Fetch:  mkdir -p .cache/usgs && curl -sSL -o .cache/usgs/MCS2026_Commodities_Data.csv \
  'https://www.sciencebase.gov/catalog/file/get/69837e43b66b01367d7ec7c7?f=__disk__d3%2Fac%2F84%2Fd3ac8466552946c5e8caa2c2c6338d9e1aff655d'
Run:    python3 tools/build/usgs.py
Output: data/resources/usgs.json  {source, asOf, retrieved, note, years, series:{key:{label, units, commodity, critical,
        values:{ISO3:[2024, 2025]}, withheld?}}, world:{key:[..], key_other:[..]}, worldNotes:{key: text}}"""
import os, csv, json, re, datetime
root = os.path.join(os.path.dirname(__file__), "..", "..")
CSV = os.path.join(root, ".cache/usgs/MCS2026_Commodities_Data.csv")
URL = "https://www.sciencebase.gov/catalog/item/69837e43b66b01367d7ec7c7"
YEARS = [2024, 2025]  # 2025 values are USGS estimates; reserves are given for 2025 only
# key: (USGS commodity, Statistics_detail of the country rows, label, units)
SERIES = {
    "lithium_prod":   ("Lithium", "Mine production", "Lithium, mine production", "metric tons, lithium content"),
    "lithium_res":    ("Lithium", "Reserves", "Lithium, reserves", "metric tons, lithium content"),
    "cobalt_prod":    ("Cobalt", "Mine production", "Cobalt, mine production", "metric tons, cobalt content"),
    "cobalt_res":     ("Cobalt", "Reserves", "Cobalt, reserves", "metric tons, cobalt content"),
    "copper_prod":    ("Copper", "Mine production", "Copper, mine production", "thousand metric tons, copper content"),
    "copper_refined_prod": ("Copper", "Refinery production", "Copper, refinery production", "thousand metric tons, copper content"),
    "copper_res":     ("Copper", "Reserves", "Copper, reserves", "thousand metric tons, copper content"),
    "nickel_prod":    ("Nickel", "Mine production", "Nickel, mine production", "metric tons, nickel content"),
    "nickel_res":     ("Nickel", "Reserves", "Nickel, reserves", "metric tons, nickel content"),
    "rare_earths_prod": ("Rare Earths", "Mine production", "Rare earths, mine production", "metric tons, rare-earth-oxide (REO) equivalent"),
    "rare_earths_res":  ("Rare Earths", "Reserves", "Rare earths, reserves", "metric tons, rare-earth-oxide (REO) equivalent"),
    "graphite_prod":  ("Graphite (Natural)", "Mine production", "Natural graphite, mine production", "metric tons"),
    "graphite_res":   ("Graphite (Natural)", "Reserves", "Natural graphite, reserves", "metric tons"),
    "manganese_prod": ("Manganese", "Mine production", "Manganese, mine production", "thousand metric tons, manganese content"),
    "manganese_res":  ("Manganese", "Reserves", "Manganese, reserves", "thousand metric tons, manganese content"),
    "platinum_prod":  ("Platinum", "Mine production: Platinum", "Platinum, mine production", "kilograms"),
    "palladium_prod": ("Palladium", "Mine production: Palladium", "Palladium, mine production", "kilograms"),
    "pgm_res":        ("Platinum-Group Metals", "PGM reserves", "Platinum-group metals, reserves", "kilograms, PGM content"),
    "gallium_prod":   ("Gallium", "Primary production", "Gallium, primary (low-purity) production", "kilograms, gallium content"),
    "tungsten_prod":  ("Tungsten", "Mine production", "Tungsten, mine production", "metric tons, tungsten content"),
    "tungsten_res":   ("Tungsten", "Reserves", "Tungsten, reserves", "metric tons, tungsten content"),
    "bauxite_prod":   ("Bauxite", "Bauxite, mine production", "Bauxite, mine production", "thousand metric dry tons"),
    "bauxite_res":    ("Bauxite", "Bauxite reserves", "Bauxite, reserves", "thousand metric dry tons"),
    "alumina_prod":   ("Alumina", "Alumina, refinery production", "Alumina, refinery production", "thousand metric dry tons"),
    "iron_ore_prod":  ("Iron Ore", "Mine production: Usable ore", "Iron ore, mine production (usable ore)", "thousand metric tons, usable ore"),
    "iron_ore_fe_prod": ("Iron Ore", "Mine production: Iron content", "Iron ore, mine production (iron content)", "thousand metric tons, iron content"),
    "iron_ore_res":   ("Iron Ore", "Reserves (million metric tons): Crude ore", "Iron ore, reserves (crude ore)", "million metric tons, crude ore"),
    "iron_ore_fe_res": ("Iron Ore", "Reserves (million metric tons): Iron content", "Iron ore, reserves (iron content)", "million metric tons, iron content"),
    "gold_prod":      ("Gold", "Mine production", "Gold, mine production", "metric tons, gold content"),
    "gold_res":       ("Gold", "Reserves", "Gold, reserves", "metric tons, gold content"),
    "silver_prod":    ("Silver", "Mine production", "Silver, mine production", "metric tons, silver content"),
    "silver_res":     ("Silver", "Reserves", "Silver, reserves", "metric tons, silver content"),
    "silicon_prod":   ("Silicon", "Silicon metal", "Silicon metal, production", "thousand metric tons, silicon content"),
    "ferrosilicon_prod": ("Silicon", "Ferrosilicon", "Ferrosilicon, production", "thousand metric tons, silicon content"),
    "antimony_prod":  ("Antimony", "Mine production", "Antimony, mine production", "metric tons, antimony content"),
    "antimony_res":   ("Antimony", "Reserves", "Antimony, reserves", "metric tons, antimony content"),
    "vanadium_prod":  ("Vanadium", "Mine production", "Vanadium, mine production", "metric tons, vanadium content"),
    "vanadium_res":   ("Vanadium", "Reserves", "Vanadium, reserves", "metric tons, vanadium content"),
    "tin_prod":       ("Tin", "Mine production", "Tin, mine production", "metric tons, tin content"),
    "tin_res":        ("Tin", "Reserves", "Tin, reserves", "metric tons, tin content"),
    "zinc_prod":      ("Zinc", "Mine production", "Zinc, mine production", "thousand metric tons, zinc content"),
    "zinc_res":       ("Zinc", "Reserves", "Zinc, reserves", "thousand metric tons, zinc content"),
    "lead_prod":      ("Lead", "Mine production", "Lead, mine production", "thousand metric tons, lead content"),
    "lead_res":       ("Lead", "Reserves", "Lead, reserves", "thousand metric tons, lead content"),
    "phosphate_prod": ("Phosphate Rock", "Mine production", "Phosphate rock, mine production", "thousand metric tons, marketable phosphate rock"),
    "phosphate_res":  ("Phosphate Rock", "Reserves", "Phosphate rock, reserves", "thousand metric tons, marketable phosphate rock"),
    "potash_prod":    ("Potash", "Mine production", "Potash, mine production", "thousand metric tons, K2O equivalent"),
    "potash_res":     ("Potash", "Reserves: K2O equivalent", "Potash, reserves", "thousand metric tons, K2O equivalent"),
    "ilmenite_prod":  ("Titanium Mineral Concentrates", "Mine production: Ilmenite", "Titanium: ilmenite, mine production", "thousand metric tons, TiO2 content"),
    "ilmenite_res":   ("Titanium Mineral Concentrates", "Reserves: Ilmenite", "Titanium: ilmenite, reserves", "thousand metric tons, TiO2 content"),
    "rutile_prod":    ("Titanium Mineral Concentrates", "Mine production: Rutile", "Titanium: rutile, mine production", "thousand metric tons, TiO2 content"),
    "rutile_res":     ("Titanium Mineral Concentrates", "Reserves: Rutile", "Titanium: rutile, reserves", "thousand metric tons, TiO2 content"),
    "titanium_sponge_prod": ("Titanium Sponge Metal", "Titanium sponge metal production", "Titanium sponge metal, production", "metric tons"),
}
ISO = {
    "Algeria": "DZA", "Argentina": "ARG", "Australia": "AUS", "Austria": "AUT", "Belarus": "BLR", "Bhutan": "BTN",
    "Bolivia": "BOL", "Brazil": "BRA", "Burma": "MMR", "Canada": "CAN", "Chile": "CHL", "China": "CHN",
    "Congo (Kinshasa)": "COD", "Cuba": "CUB", "Côte d’Ivoire": "CIV", "Egypt": "EGY", "Finland": "FIN", "France": "FRA",
    "Gabon": "GAB", "Germany": "DEU", "Ghana": "GHA", "Greece": "GRC", "Greenland": "GRL", "Guatemala": "GTM",
    "Guinea": "GIN", "Iceland": "ISL", "India": "IND", "Indonesia": "IDN", "Iran": "IRN", "Ireland": "IRL",
    "Israel": "ISR", "Jamaica": "JAM", "Japan": "JPN", "Jordan": "JOR", "Kazakhstan": "KAZ", "Kenya": "KEN",
    "Korea, North": "PRK", "Korea, Republic of": "KOR", "Kyrgyzstan": "KGZ", "Laos": "LAO", "Madagascar": "MDG",
    "Malaysia": "MYS", "Mali": "MLI", "Mauritania": "MRT", "Mexico": "MEX", "Morocco": "MAR", "Mozambique": "MOZ",
    "New Caledonia": "NCL", "Nigeria": "NGA", "Norway": "NOR", "Pakistan": "PAK", "Papua New Guinea": "PNG",
    "Peru": "PER", "Philippines": "PHL", "Poland": "POL", "Portugal": "PRT", "Russia": "RUS", "Rwanda": "RWA",
    "Saudi Arabia": "SAU", "Senegal": "SEN", "Sierra Leone": "SLE", "South Africa": "ZAF", "Spain": "ESP",
    "Sri Lanka": "LKA", "Sweden": "SWE", "Syria": "SYR", "Tajikistan": "TJK", "Tanzania": "TZA", "Thailand": "THA",
    "Togo": "TGO", "Tunisia": "TUN", "Turkey": "TUR", "Ukraine": "UKR", "United Arab Emirates": "ARE",
    "United Kingdom": "GBR", "United States": "USA", "Uzbekistan": "UZB", "Vietnam": "VNM", "Zambia": "ZMB",
    "Zimbabwe": "ZWE", "Kosovo": "XKX", "Turkiye": "TUR", "Burundi": "BDI", "Colombia": "COL", "Ethiopia": "ETH",
    "Namibia": "NAM", "Nicaragua": "NIC", "Venezuela": "VEN", "Ecuador": "ECU", "Mongolia": "MNG", "Armenia": "ARM",
    "Georgia": "GEO", "Botswana": "BWA", "Eritrea": "ERI", "Sudan": "SDN", "Burkina Faso": "BFA", "Suriname": "SUR",
    "Guyana": "GUY", "Dominican Republic": "DOM", "Serbia": "SRB", "Bulgaria": "BGR", "Romania": "ROU",
    "Slovakia": "SVK", "Montenegro": "MNE", "Bosnia and Herzegovina": "BIH", "North Macedonia": "MKD",
    "Oman": "OMN", "Qatar": "QAT", "Bahrain": "BHR", "Kuwait": "KWT", "Taiwan": "TWN", "Italy": "ITA",
    "Netherlands": "NLD", "Belgium": "BEL", "Estonia": "EST", "Hungary": "HUN", "Czechia": "CZE", "Zaire": "COD",
}

def sig(v):  # 3 significant figures, as in the other build scripts
    return None if v is None else float(f"{v:.3g}")
def num(s):
    """'82,700' -> 82700.0; '>140,000,000' -> 140000000.0 (flag kept by caller); W, NA, —, s, Large -> None."""
    s = s.strip().lstrip("<>").replace(",", "")
    try: return float(s)
    except ValueError: return None

rows = [r for r in csv.DictReader(open(CSV, encoding="cp1252")) if r["Section"].startswith("World")]
YI = {y: i for i, y in enumerate(YEARS)}
series, world, wnotes, unknown = {}, {}, {}, set()
for key, (com, detail, label, units) in SERIES.items():
    sub = [r for r in rows if r["Commodity"] == com]
    if not sub: raise SystemExit(f"no rows for {com}")
    world_details = {detail.lower(), detail.lower() + ": rounded", detail.lower() + ", rounded"}
    vals, wd, other, withheld, crit = {}, [None] * len(YEARS), [None] * len(YEARS), set(), set()
    for r in sub:
        y = int(r["Year"]) if r["Year"].isdigit() else None
        if y not in YI: continue
        d, c, raw = r["Statistics_detail"], r["Country"], r["Value"].strip()
        crit.add(r["Is critical mineral 2025"])
        if c == "World total" and d.lower() in world_details:
            # prefer the unrounded total where both exist
            if wd[YI[y]] is None or d.lower() == detail.lower(): wd[YI[y]] = num(raw)
            if not raw.replace(",", "").isdigit(): wnotes[key] = f"{y} world total given as '{raw}'"
            n = r["Notes"].strip()
            if n.startswith("Estimated. -- "): wnotes[key] = n[len("Estimated. -- "):]
            continue
        if d != detail: continue
        if c == "Other countries":
            other[YI[y]] = num(raw); continue
        iso = ISO.get(c)
        if not iso: unknown.add(c); continue
        if raw == "W": withheld.add(iso)
        vals.setdefault(iso, [None] * len(YEARS))[YI[y]] = sig(num(raw))
    vals = {k: v for k, v in vals.items() if any(x is not None for x in v)}
    if not vals: raise SystemExit(f"{key}: no country values (detail '{detail}')")
    s = {"label": label, "units": units, "commodity": com, "critical": "Yes" in crit, "values": vals}
    if withheld: s["withheld"] = sorted(withheld)
    series[key] = s
    world[key] = [sig(v) for v in wd]
    if any(v is not None for v in other): world[key + "_other"] = [sig(v) for v in other]
if unknown: raise SystemExit(f"unmapped USGS country names: {sorted(unknown)}")

doc = {
    "source": "usgs-mcs", "asOf": "Mineral Commodity Summaries 2026 data release (2026-02-06), doi:10.5066/P1WKQ63T",
    "retrieved": datetime.date.today().isoformat(),
    "note": "2025 values are USGS estimates; reserves are for 2025 only. Withheld (W) and unquantified values "
            "(NA, small, large) are null; 'withheld' lists countries with W. World totals and 'Other countries' "
            "are in 'world', not in values. Germanium and uranium have no world table in MCS 2026. " + URL,
    "years": YEARS, "series": series, "world": world, "worldNotes": wnotes,
}
p = os.path.join(root, "data/resources/usgs.json")
os.makedirs(os.path.dirname(p), exist_ok=True)
json.dump(doc, open(p, "w"), separators=(",", ":"), ensure_ascii=False)
print(p, os.path.getsize(p) // 1024, "KB;", len(series), "series")
for k in ["lithium_prod", "cobalt_prod", "rare_earths_prod", "graphite_prod", "copper_prod", "nickel_prod"]:
    v, w = series[k]["values"], world[k][-1]
    top = sorted(((c, x[-1]) for c, x in v.items() if x[-1] is not None), key=lambda t: -t[1])[:5]
    print(f"{k} 2025 world {w}:", ", ".join(f"{c} {x:g} ({x / w:.0%})" if w else f"{c} {x:g}" for c, x in top))
