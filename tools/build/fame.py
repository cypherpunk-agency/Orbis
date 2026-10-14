"""Where fame was born: notable people 3500 BC - 2018 (Laouenan, Bhargava, Eymeoud, Gergaud, Plique, Wasmer,
"A cross-verified database of notable people, 3500BC-2018AD", Scientific Data 2022).
Primary record: data.sciencespo, "A Brief History of Human Time - Cross-verified Dataset",
  https://doi.org/10.21410/7E4/RDAG3O  (sibling of the "Codes & Datasets" record doi:10.21410/7E4/YLG6YR).
  Terms of use on both records: CC BY-SA 4.0; the LICENSE.txt shipped with both records is CC BY-NC-SA 4.0.
  We follow the stricter one (BY-NC-SA): story layer only.
Fetch (≈260 MB, into .cache/fame/):
  curl -A Orbis-data-build/1.0 -L -o .cache/fame/cross-verified-database.csv.gz \
    https://data.sciencespo.fr/api/access/datafile/4432
Needs also .cache/ne/ne_10m_populated_places_simple.geojson and .cache/ne/ne_50m_admin_0_countries.geojson (Natural Earth).
Run: .cache/venv/py/bin/python tools/build/fame.py   (numpy, pillow); then the raw .gz may be deleted.
Outputs (years: the source writes BC years as negatives without a year 0; we convert to astronomical, -500 -> -499):
  data/grids/fame.json + data/grids/fame-<era>.png   births per 0.5° cell, one frame per era and "all"
  data/people/fame-cities.json    births per city (within 25 km of a Natural Earth populated place), per era
  data/people/fame-centre.json    centre of gravity of birthplaces per era (moves set "centre")
  data/people/fame-capitals.json  people with both places known: born here vs died here, per city
  data/people/fame-women.json     share of women among people born 1950-2018, by first citizenship
  data/people/fame-women-trend.json  share of women by birth decade, 1500s-2000s (one line, key WLD = everyone)"""
import os, csv, gzip, json, math, datetime
from collections import Counter, defaultdict
import numpy as np
from PIL import Image

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW = os.path.join(root, ".cache/fame/cross-verified-database.csv.gz")
TODAY = datetime.date.today().isoformat()
SRC = "bhht"
CITE = ("Laouenan et al. (2022), A cross-verified database of notable people, 3500BC-2018AD, Scientific Data 9:290; "
        "data.sciencespo doi:10.21410/7E4/RDAG3O. ")
# era starts, astronomical years; each era runs to the next start (last to 2018)
ERAS = [-3499, -499, 1, 500, 1000, 1300, 1500, 1600, 1700, 1750, 1800, 1850, 1900, 1925, 1950, 1975]
EDGES = np.array(ERAS + [2019])

def num(x):
    try: return float(x)
    except ValueError: return math.nan

# ---------- read (streaming) ----------
csv.field_size_limit(10**8)
B, G, BLO, BLA, DLO, DLA, CIT = [], [], [], [], [], [], []
with gzip.open(RAW, "rt", encoding="utf-8", errors="replace", newline="") as fh:
    for r in csv.DictReader(fh):
        B.append(num(r["birth"])); g = r["gender"]; G.append(1 if g == "Male" else 2 if g == "Female" else 0)
        BLO.append(num(r["bplo1"])); BLA.append(num(r["bpla1"])); DLO.append(num(r["dplo1"])); DLA.append(num(r["dpla1"]))
        CIT.append(r["citizenship_1_b"])
B = np.array(B); B = np.where(B < 0, B + 1, B)  # astronomical years
G = np.array(G, np.int8); BLO, BLA, DLO, DLA = map(np.array, (BLO, BLA, DLO, DLA)); CIT = np.array(CIT)
N = len(B)
hasb = np.isfinite(B) & np.isfinite(BLO) & np.isfinite(BLA)
era = np.full(N, -1); era[np.isfinite(B)] = np.searchsorted(EDGES, B[np.isfinite(B)], side="right") - 1
era[(era < 0) | (era >= len(ERAS))] = -1
print(N, "people;", int(np.isfinite(B).sum()), "with birth year;", int(hasb.sum()), "with birth year and place")
def lab(y): return f"{-y + 1} BC" if y <= 0 else f"AD {y}" if y < 1000 else str(y)
ERA_LABEL = [f"{lab(a)}–{lab(b - 1) if b - 1 > 0 else lab(b - 1)}" for a, b in zip(ERAS, ERAS[1:] + [2019])]

# ---------- raster grids: births per 0.5° cell ----------
W, H, VMIN, VMAX = 720, 360, 1.0, 3000.0
os.makedirs(os.path.join(root, "data/grids"), exist_ok=True)
col = np.clip(np.floor((BLO + 180) / 360 * W), 0, W - 1)
row = np.clip(np.floor((90 - BLA) / 180 * H), 0, H - 1)
frames = {}
def grid(mask, label):
    c = np.zeros((H, W)); np.add.at(c, (row[mask].astype(int), col[mask].astype(int)), 1)
    img = np.zeros((H, W), np.uint8); m = c > 0
    lv = (np.log10(np.clip(c[m], VMIN, VMAX)) - math.log10(VMIN)) / (math.log10(VMAX) - math.log10(VMIN))
    img[m] = 1 + np.round(lv * 254).astype(np.uint8)
    png = f"data/grids/fame-{label}.png"
    Image.fromarray(img, "L").save(os.path.join(root, png), optimize=True)
    frames[label] = png
    print(f"  grid {label}: {int(mask.sum())} births, max cell {int(c.max())}, {os.path.getsize(os.path.join(root, png))//1024} KB")
for i, y in enumerate(ERAS): grid(hasb & (era == i), str(y))
grid(hasb, "all")
json.dump({
    "source": SRC, "asOf": "2018", "retrieved": TODAY,
    "note": CITE + "Notable people (Wikipedia/Wikidata) counted at their birthplace in 0.5° cells; one frame per era of birth, "
            "labelled by the era's first year (astronomical: -499 = 500 BC), and 'all'. Log scale, clamped to 1–3,000 people per cell; 0 = none. "
            f"{int(hasb.sum()):,} of {N:,} people have both a birth year and a birthplace.",
    "units": "notable people born per cell",
    "grid": {"width": W, "height": H, "bbox": [-180, -90, 180, 90]},
    "encoding": {"type": "log", "min": VMIN, "max": VMAX, "nodata": 0},
    "palette": "sequential", "frames": frames,
}, open(os.path.join(root, "data/grids/fame.json"), "w"), indent=1, ensure_ascii=False)

# ---------- snap places to Natural Earth cities (largest place within 25 km) ----------
pp = json.load(open(os.path.join(root, ".cache/ne/ne_10m_populated_places_simple.geojson")))["features"]
RENAME = {"København": "Copenhagen", "Antwerpen": "Antwerp", "Makkah": "Mecca", "Xian": "Xi'an", "Sparti": "Sparta",
          "Al Hillah": "Hillah (Babylon)", "Antakya": "Antakya (Antioch)", "Washington, D.C.": "Washington", "St. Petersburg": "St Petersburg"}
def nm(s): s = " ".join(s.split()); return RENAME.get(s, s)
PL = [(nm(p["properties"]["name"]), p["properties"]["adm0_a3"], p["geometry"]["coordinates"], p["properties"]["pop_max"] or 0,
       p["properties"]["adm0cap"]) for p in pp]
bucket = defaultdict(list)
for i, (_, _, (lo, la), _, _) in enumerate(PL): bucket[(math.floor(lo), math.floor(la))].append(i)
R_KM = 25
def snap(lo, la):
    best, bp = None, -1
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for i in bucket.get((math.floor(lo) + dx, math.floor(la) + dy), ()):
                plo, pla = PL[i][2]
                d = 111.2 * math.hypot((plo - lo) * math.cos(math.radians(la)), pla - la)
                if d <= R_KM and PL[i][3] > bp: best, bp = i, PL[i][3]
    return -1 if best is None else best
cache = {}
def snap_all(lo, la, mask):
    out = np.full(N, -1)
    for k in np.flatnonzero(mask):
        key = (round(lo[k], 3), round(la[k], 3))
        if key not in cache: cache[key] = snap(*key)
        out[k] = cache[key]
    return out
bcity = snap_all(BLO, BLA, hasb)
hasd = np.isfinite(DLO) & np.isfinite(DLA)
both = hasb & hasd
dcity = snap_all(DLO, DLA, both)
print("births snapped to a city:", int((bcity >= 0).sum()), "of", int(hasb.sum()))

# births per city per era
per = defaultdict(lambda: [0] * (len(ERAS) + 1))
for k in np.flatnonzero(bcity >= 0):
    c = bcity[k]; per[c][-1] += 1
    if era[k] >= 0: per[c][era[k]] += 1
keep = set()
for j in range(len(ERAS) + 1):
    keep |= {c for c, _ in sorted(per.items(), key=lambda kv: -kv[1][j])[:60] if per[c][j] > 0}
pts = [{"id": f"c{c}", "name": PL[c][0], "at": [round(PL[c][2][0], 2), round(PL[c][2][1], 2)],
        "born": [v if v else None for v in per[c]]} for c in sorted(keep, key=lambda c: -per[c][-1])]
json.dump({"source": SRC, "asOf": "2018", "retrieved": TODAY,
           "note": CITE + "Births per city: birthplaces within 25 km of a Natural Earth populated place are counted at the largest such place "
                   "(modern names: Istanbul for Byzantium/Constantinople). Periods are eras of birth, labelled by their first year "
                   "(astronomical: -499 = 500 BC); 'all' = every era. Top 60 cities per era.",
           "periods": [str(y) for y in ERAS] + ["all"], "points": pts},
          open(os.path.join(root, "data/people/fame-cities.json"), "w"), separators=(",", ":"), ensure_ascii=False)
for j in (0, 1, 2, 3, 4, 5, 6, 9, 12, 15, 16):
    top = sorted(per.items(), key=lambda kv: -kv[1][j])[:6]
    print("  top cities", ([str(y) for y in ERAS] + ["all"])[j], [(PL[c][0], v[j]) for c, v in top])

# ---------- centre of gravity of birthplaces per era ----------
lo, la = np.radians(BLO), np.radians(BLA)
X, Y, Z = np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)
path, cent = [], []
for i, y in enumerate(ERAS):
    m = hasb & (era == i)
    x, yy, z = X[m].mean(), Y[m].mean(), Z[m].mean()
    clon, clat = math.degrees(math.atan2(yy, x)), math.degrees(math.atan2(z, math.hypot(x, yy)))
    path.append([round(clon, 1), round(clat, 1), y]); cent.append((y, int(m.sum()), round(clon, 1), round(clat, 1)))
    print(f"  centre {ERA_LABEL[i]}: n={int(m.sum())} lon {clon:.1f} lat {clat:.1f}")
json.dump({"source": SRC, "asOf": "2018", "retrieved": TODAY,
           "note": CITE + "Centre of gravity of notable people's birthplaces in each era of birth: the mean of their positions as 3-D vectors, "
                   "projected back to the Earth's surface. Dates are each era's first year (astronomical). Eras: " + "; ".join(
                       f"{ERA_LABEL[i]} ({n:,} people, {lon}, {lat})" for i, (y, n, lon, lat) in enumerate(cent)) + ".",
           "moves": {"centre": [{"name": "Centre of notable births", "color": "c2", "path": path}]}},
          open(os.path.join(root, "data/people/fame-centre.json"), "w"), indent=1, ensure_ascii=False)

# ---------- pull of cities: born here vs died here (people with both places known) ----------
born, died = Counter(bcity[both & (bcity >= 0)].tolist()), Counter(dcity[both & (dcity >= 0)].tolist())
top = sorted(set(c for c, _ in born.most_common(80)) | set(c for c, _ in died.most_common(80)), key=lambda c: -died.get(c, 0))
cap = [{"id": f"c{c}", "name": PL[c][0], "at": [round(PL[c][2][0], 2), round(PL[c][2][1], 2)],
        "n": [born.get(c, 0), died.get(c, 0)], "capital": bool(PL[c][4])} for c in top]
json.dump({"source": SRC, "asOf": "2018", "retrieved": TODAY,
           "note": CITE + f"Only the {int(both.sum()):,} people with both a birthplace and a place of death; places snapped to the largest "
                   "Natural Earth populated place within 25 km. Period 'born' = notable people born there, 'died' = notable people who died there.",
           "periods": ["born", "died"], "points": cap},
          open(os.path.join(root, "data/people/fame-capitals.json"), "w"), separators=(",", ":"), ensure_ascii=False)
for c in top[:25]:
    print(f"  {PL[c][0]:<20} cap={PL[c][4]} born {born.get(c,0):>6} died {died.get(c,0):>6} ratio {died.get(c,0)/max(1,born.get(c,0)):.2f}")

# ---------- women ----------
dec = list(range(1500, 2000, 10))
share = []
for d0 in dec:
    m = (B >= d0) & (B < d0 + 10); f, mm = int((m & (G == 2)).sum()), int((m & (G == 1)).sum())
    share.append(round(100 * f / (f + mm), 1) if f + mm >= 500 else None)
print("  women by decade", list(zip(dec, share)))
json.dump({"source": SRC, "asOf": "2018", "retrieved": TODAY,
           "note": CITE + "Share of women among notable people with a recorded gender (men + women), by decade of birth. "
                   "Key WLD = all people in the database, not a country. Stops at the 1990s: few people born after 2000 are in the database yet.",
           "years": dec, "series": {"female": {"label": "Women among notable people, by decade of birth", "units": "%",
                                               "values": {"WLD": share}}}},
          open(os.path.join(root, "data/people/fame-women-trend.json"), "w"), separators=(",", ":"))

ne = json.load(open(os.path.join(root, ".cache/ne/ne_50m_admin_0_countries.geojson")))["features"]
NAME = {}
for f in ne:
    p = f["properties"]; iso = p["ISO_A3"] if p["ISO_A3"] != "-99" else p["ADM0_A3"]
    for k in ("ADMIN", "NAME", "NAME_LONG", "NAME_EN", "SOVEREIGNT"):
        if p.get(k): NAME.setdefault(p[k].replace(" ", "_"), iso)
NAME.update({"US": "USA", "United_Kingdom": "GBR", "England": "GBR", "Scotland": "GBR", "Wales": "GBR", "Russia": "RUS",
             "South_Korea": "KOR", "North_Korea": "PRK", "Czech_Republic": "CZE", "Ivory_Coast": "CIV", "Congo": "COD",
             "Macedonia": "MKD", "Swaziland": "SWZ", "East_Timor": "TLS", "The_Bahamas": "BHS", "Kosovo": "XKX", "Taiwan": "TWN",
             "Northern_Cyprus": "NCY", "Palestine": "PSE", "Federated_States_of_Micronesia": "FSM", "Cape_Verde": "CPV",
             "Dominican_republic": "DOM", "São_Tomé_and_Príncipe": "STP", "Vatican_City": "VAT", "Hong_Kong": "HKG", "Macau": "MAC",
             "Laos": "LAO", "Vietnam": "VNM", "Brunei": "BRN", "Syria": "SYR", "Iran": "IRN", "Moldova": "MDA", "Tanzania": "TZA",
             "Bolivia": "BOL", "Venezuela": "VEN", "Serbia": "SRB", "Guinea-Bissau": "GNB", "Bosnia_and_Herzegovina": "BIH"})
m = B >= 1950
iso = np.array([NAME.get(c, "") for c in CIT])
unm = Counter(CIT[m & (iso == "") & (CIT != "")].tolist())
print("  unmatched citizenships (born 1950+):", unm.most_common(15))
vals = {}
for c in sorted(set(iso[m].tolist()) - {""}):
    k = m & (iso == c); f, mm = int((k & (G == 2)).sum()), int((k & (G == 1)).sum())
    if f + mm >= 200: vals[c] = [round(100 * f / (f + mm), 1)]
fm = int((m & (G == 2)).sum()); mm_ = int((m & (G == 1)).sum())
print(f"  women born 1950-2018: {100*fm/(fm+mm_):.1f}% of {fm+mm_}; countries {len(vals)}")
for c in ("USA", "DEU", "GBR", "FRA", "ITA", "JPN", "IND", "CHN", "KOR", "SWE", "RUS", "BRA", "NGA", "SAU", "PHL", "AUS", "ESP"):
    print("   ", c, vals.get(c))
json.dump({"source": SRC, "asOf": "2018", "retrieved": TODAY,
           "note": CITE + "Share of women among notable people born 1950–2018 with a recorded gender, by first citizenship "
                   "(the database's own assignment). Countries with fewer than 200 such people are left out.",
           "years": [1950], "series": {"female": {"label": "Women among notable people born 1950–2018", "units": "%", "values": vals}}},
          open(os.path.join(root, "data/people/fame-women.json"), "w"), separators=(",", ":"))
CONT = {}
for f in ne:
    p = f["properties"]; CONT.setdefault(p["ISO_A3"] if p["ISO_A3"] != "-99" else p["ADM0_A3"], p["CONTINENT"])
for c in ("GBR", "FRA", "NOR", "XKX", "NCY"): CONT[c] = "Europe"
CONT["USA"] = "North America"
for nmx in ("Czechoslovakia", "Yugoslavia", "Austria-Hungary", "Holy_Roman_Empire", "Serbia_and_Montenegro", "Denmark-Norway"): NAME[nmx] = "EUR"
CONT["EUR"] = "Europe"
iso = np.array([NAME.get(c, "") for c in CIT])
shares = []
for lo_, hi_ in ((500, 1500), (1500, 1800), (1800, 1900), (1900, 1950), (1950, 1975), (1975, 2019)):
    k = (B >= lo_) & (B < hi_) & (iso != ""); n = int(k.sum())
    eu = int(sum(1 for c in iso[k] if CONT.get(c) == "Europe")); na = int(np.isin(iso[k], ["USA", "CAN"]).sum()); asia = int(sum(1 for c in iso[k] if CONT.get(c) == "Asia"))
    shares.append(f"born {lab(lo_)}–{hi_ - 1}: {100 * eu / n:.0f}% Europe, {100 * na / n:.0f}% USA and Canada, {100 * asia / n:.0f}% Asia (n={n:,})")
print("  continent shares:", shares)
cpath = os.path.join(root, "data/people/fame-centre.json"); cj = json.load(open(cpath))
cj["note"] += " Share by first citizenship (people with one recorded): " + "; ".join(shares) + "."
json.dump(cj, open(cpath, "w"), indent=1, ensure_ascii=False)
for f in ("fame-cities", "fame-centre", "fame-capitals", "fame-women", "fame-women-trend"):
    print(f, os.path.getsize(os.path.join(root, f"data/people/{f}.json")) // 1024, "KB")
