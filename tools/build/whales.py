"""Where the whales were: American offshore whaling, from whalinghistory.org (CC BY 4.0).
Downloads into .cache/whales/ (≈6.5 MB zipped):
  https://whalinghistory.org/aowv/AmericanOffshoreWhalingVoyages.zip   (voyages_<date>.txt, readme: CC BY 4.0)
  https://whalinghistory.org/aowl/AmericanOffshoreWhalingLogbookData.zip (aowl_<date>.txt, readme: CC BY 4.0)
Run: python3 tools/build/whales.py   (needs numpy, pillow)
Outputs
  data/grids/whales.json + whales-<decade>.png  Logbook positions by decade on a 2° grid, as a share of that decade's positions.
  data/grids/whales-strikes.json + whales-<species>.png  Whales struck (logbook "Strike" encounters) per 2° cell, all years.
  data/history/whales.json  Home ports (voyages per decade, points list) and yearly series (voyages out, oil returned).
"""
import os, io, csv, json, glob, zipfile, datetime, collections, urllib.request
import numpy as np
from PIL import Image

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CACHE = os.path.join(root, ".cache/whales")
UA = {"User-Agent": "Orbis-data-build/1.0"}
ZIPS = {"aowv": "https://whalinghistory.org/aowv/AmericanOffshoreWhalingVoyages.zip",
        "aowl": "https://whalinghistory.org/aowl/AmericanOffshoreWhalingLogbookData.zip"}
csv.field_size_limit(10**9)
TODAY = datetime.date.today().isoformat()


def fetch(key):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, key + ".zip")
    if not os.path.exists(p):
        with urllib.request.urlopen(urllib.request.Request(ZIPS[key], headers=UA)) as r, open(p, "wb") as f:
            f.write(r.read())
    return zipfile.ZipFile(p)


def table(z, prefix):
    name = [n for n in z.namelist() if os.path.basename(n).startswith(prefix) and n.endswith(".txt")][0]
    txt = io.TextIOWrapper(z.open(name), encoding="utf-8")
    return list(csv.DictReader(txt, delimiter="\t", quoting=csv.QUOTE_NONE)), os.path.basename(name)


logs, logname = table(fetch("aowl"), "aowl_")
voys, voyname = table(fetch("aowv"), "voyages_")
print(len(logs), "log rows;", len(voys), "voyage rows")

# ---------- grids: 2° cells, row 0 = 88–90°N, col 0 = 180–178°W ----------
W, H = 180, 90
def cell(la, lo):
    lo = ((lo + 180) % 360) - 180
    return min(H - 1, max(0, int((90 - la) // 2))), min(W - 1, max(0, int((lo + 180) // 2)))

DECADES = [1820, 1830, 1840, 1850, 1860, 1870, 1880, 1890, 1900, 1910]
dec_of = lambda y: 1910 if y >= 1910 else (y // 10 * 10)
pos = {d: np.zeros((H, W)) for d in DECADES + ["all"]}
SPECIES = {"Sperm": "sperm", "Right": "right", "Bowhead": "bowhead", "Humpback": "humpback"}
strikes = {k: np.zeros((H, W)) for k in SPECIES.values()}
nlog = collections.Counter(); logvoy = set(); region = collections.defaultdict(collections.Counter)
for r in logs:
    try:
        la, lo, y = float(r["Lat"]), float(r["Lon"]), int(r["Year"])
    except ValueError:
        continue
    i, j = cell(la, lo); logvoy.add(r["VoyageID"]); pos["all"][i, j] += 1
    if y >= 1820:
        d = dec_of(y); pos[d][i, j] += 1; nlog[d] += 1
    if r["Encounter"] == "Strike" and r["Species"] in SPECIES:
        # one row = one logbook day; NStruck is often 0 or blank on strike days, so count days, not whales
        strikes[SPECIES[r["Species"]]][i, j] += 1
    # Arctic (north of 60°N in the Bering/Chukchi/Okhotsk sector) for the text
    if la >= 60 and (lo <= -140 or lo >= 140):
        region[dec_of(y) if y >= 1820 else 0]["arctic"] += 1
nall = int(pos["all"].sum())
print("positions", nall, "voyages with positions", len(logvoy), "per decade", dict(nlog))
print("arctic share by decade", {d: round(100 * region[d]["arctic"] / nlog[d], 1) for d in DECADES})

def encode_log(a, vmin, vmax):
    img = np.zeros(a.shape, np.uint8); m = a > 0
    t = (np.log10(np.clip(a[m], vmin, vmax)) - np.log10(vmin)) / (np.log10(vmax) - np.log10(vmin))
    img[m] = 1 + np.round(t * 254).astype(np.uint8)
    return img

OUT = os.path.join(root, "data/grids"); os.makedirs(OUT, exist_ok=True)
SMIN, SMAX = 0.0001, 0.02   # share of the decade's positions per cell
frames = {}
for d in DECADES + ["all"]:
    share = pos[d] / pos[d].sum()
    png = f"data/grids/whales-{d}.png"
    Image.fromarray(encode_log(share, SMIN, SMAX), "L").save(os.path.join(root, png), optimize=True)
    frames[str(d)] = png
    top = np.unravel_index(np.argmax(share), share.shape)
    print(d, "max cell share %.3f at lat %d lon %d" % (share.max(), 89 - 2 * top[0], -179 + 2 * top[1]))
json.dump({
    "source": "whalinghistory", "asOf": logname.replace("aowl_", "").replace(".txt", ""), "retrieved": TODAY,
    "note": f"American Offshore Whaling Logbook Data ({nall:,} daily noon positions from {len(logvoy):,} voyages, 1780s–1920s; "
            "compiled from the Maury abstracts, the Census of Marine Life and Townsend logbook transcriptions). Each 2° cell shows its share "
            "of all positions logged in that decade, so decades with few surviving logbooks are comparable with busy ones; frame '1910' "
            "covers 1910–1927, frame 'all' every position. Logbooks are a sample of voyages: most positions are from the 1830s–1850s.",
    "units": "share of the decade's logbook positions",
    "grid": {"width": W, "height": H, "bbox": [-180, -90, 180, 90]},
    "encoding": {"type": "log", "min": SMIN, "max": SMAX, "nodata": 0},
    "palette": "sequential", "frames": frames,
}, open(os.path.join(OUT, "whales.json"), "w"), indent=1, ensure_ascii=False)

KMIN, KMAX = 1, 100
sframes = {}
for k, a in strikes.items():
    png = f"data/grids/whales-{k}.png"
    Image.fromarray(encode_log(a, KMIN, KMAX), "L").save(os.path.join(root, png), optimize=True)
    sframes[k] = png
    print(k, "strikes", int(a.sum()))
json.dump({
    "source": "whalinghistory", "asOf": logname.replace("aowl_", "").replace(".txt", ""), "retrieved": TODAY,
    "note": "Logbook days on which whales of a species were struck (encounter type 'Strike'; the whale count NStruck is often blank or 0, so days are counted) per 2° cell, all years, from the American Offshore Whaling Logbook Data. "
            f"Sperm {int(strikes['sperm'].sum()):,}, right {int(strikes['right'].sum()):,}, bowhead {int(strikes['bowhead'].sum()):,}, "
            f"humpback {int(strikes['humpback'].sum()):,} strike days. Only voyages with transcribed logbooks are included. Clamped at 100 per cell.",
    "units": "days with whales struck",
    "grid": {"width": W, "height": H, "bbox": [-180, -90, 180, 90]},
    "encoding": {"type": "log", "min": KMIN, "max": KMAX, "nodata": 0},
    "palette": "sequential", "frames": sframes,
}, open(os.path.join(OUT, "whales-strikes.json"), "w"), indent=1, ensure_ascii=False)

# ---------- voyages: one row per voyage (voyageRank 1) ----------
V = [v for v in voys if v["voyageRank"].strip() == "1"]
def yr(s):
    try: return int(s.strip()[:4])
    except ValueError: return None
def port(s):
    s = " ".join(s.replace("\xa0", " ").split()).rstrip(" ?")
    return {"Rochester, MA (Mattapoisett)": "Mattapoisett, MA", "Sippican, MA": "Marion, MA"}.get(s, s)
# home-port coordinates (town centres / harbours, editorial)
PORTS = {
    "New Bedford, MA": ("New Bedford", [-70.92, 41.63]), "Nantucket, MA": ("Nantucket", [-70.10, 41.28]),
    "Provincetown, MA": ("Provincetown", [-70.18, 42.05]), "San Francisco, CA": ("San Francisco", [-122.42, 37.80]),
    "New London, CT": ("New London", [-72.10, 41.35]), "Sag Harbor, NY": ("Sag Harbor", [-72.29, 41.00]),
    "Fairhaven, MA": ("Fairhaven", [-70.90, 41.64]), "Boston, MA": ("Boston", [-71.05, 42.36]),
    "Westport, MA": ("Westport", [-71.08, 41.51]), "Stonington, CT": ("Stonington", [-71.91, 41.34]),
    "Edgartown, MA": ("Edgartown", [-70.51, 41.39]), "Warren, RI": ("Warren", [-71.28, 41.73]),
    "Dartmouth, MA": ("Dartmouth", [-70.97, 41.57]), "Newport, RI": ("Newport", [-71.31, 41.49]),
    "Mattapoisett, MA": ("Mattapoisett", [-70.82, 41.66]), "Greenport, NY": ("Greenport", [-72.36, 41.10]),
    "New York, NY": ("New York", [-74.01, 40.70]), "Mystic, CT": ("Mystic", [-71.97, 41.35]),
    "Hudson, NY": ("Hudson", [-73.79, 42.25]), "Providence, RI": ("Providence", [-71.40, 41.82]),
    "Salem, MA": ("Salem", [-70.89, 42.52]), "Bristol, RI": ("Bristol", [-71.27, 41.67]),
    "Fall River, MA": ("Fall River", [-71.16, 41.70]), "Falmouth, MA": ("Falmouth", [-70.62, 41.55]),
    "Marion, MA": ("Marion", [-70.76, 41.70]), "Honolulu, HI": ("Honolulu", [-157.86, 21.31]),
}
PDEC = list(range(1750, 1930, 10))
pc = collections.defaultdict(lambda: [0] * len(PDEC)); unplaced = collections.Counter()
peryear_out = collections.Counter(); oil_in = collections.Counter(); sperm_in = collections.Counter(); bone_in = collections.Counter()
for v in V:
    yo, yi = yr(v["yearOut"]), yr(v["yearIn"])
    if yo: peryear_out[yo] += 1
    if yi:
        for col, ctr in (("oil", oil_in), ("sperm", sperm_in), ("bone", bone_in)):
            try: ctr[yi] += float(v[col] or 0)
            except ValueError: pass
    if not yo or yo < 1750 or yo >= 1930: continue
    p = port(v["port"])
    if p in PORTS: pc[p][PDEC.index(yo // 10 * 10)] += 1
    else: unplaced[p] += 1
nplaced = sum(sum(a) for a in pc.values())
print("voyages", len(V), "placed in ports", nplaced, "unplaced top", unplaced.most_common(8))
tot_port = {p: sum(a) for p, a in pc.items()}
print("port totals", sorted(tot_port.items(), key=lambda a: -a[1])[:8])
years = list(range(1780, 1926))
peak = max(peryear_out.items(), key=lambda a: a[1])
print("peak year out", peak, "1840s mean", sum(peryear_out[y] for y in range(1840, 1850)) / 10,
      "1900s mean", sum(peryear_out[y] for y in range(1900, 1910)) / 10)
barrels = {y: oil_in[y] + sperm_in[y] for y in years}
print("peak barrels", max(barrels.items(), key=lambda a: a[1]), "bone peak", max(bone_in.items(), key=lambda a: a[1]))
arctic71 = [v for v in V if yr(v["yearIn"]) == 1871 and v["returnCode"].strip() == "A"
            and "sept" in v["end"].lower() and any(k in v["end"].lower() for k in ("belcher", "arctic", "ice"))]
print("abandoned in the Arctic 1871:", len(arctic71))
json.dump({
    "source": "whalinghistory", "asOf": voyname.replace("voyages_", "").replace(".txt", ""), "retrieved": TODAY,
    "note": f"American Offshore Whaling Voyages ({len(V):,} voyages, one row per voyage). Ports: voyages leaving each home port per decade "
            f"(by year out; {len(pc)} largest ports placed by Orbis at the town centre, {nplaced:,} voyages). Series: voyages leaving per year (year out) "
            "and barrels of sperm oil plus whale oil landed per year (year in; voyages without returns recorded count as zero). "
            f"In 1871, {len(arctic71)} voyages in the database ended with the ship abandoned in the Arctic ice (mostly near Point Belcher, Alaska, 14 Sept 1871).",
    "periods": [str(d) for d in PDEC],
    "points": [{"id": p.split(",")[0].lower().replace(" ", "-"), "name": PORTS[p][0], "at": PORTS[p][1], "voy": pc[p]}
               for p in sorted(pc, key=lambda p: -tot_port[p])],
    "years": years,
    "series": {
        "voyages": {"label": "Whaling voyages leaving US ports per year", "units": "voyages", "values": {"USA": [peryear_out[y] for y in years]}},
        "oil": {"label": "Sperm and whale oil landed, thousand barrels", "units": "thousand barrels",
                "values": {"USA": [round(barrels[y] / 1000, 1) for y in years]}},
    },
}, open(os.path.join(root, "data/history/whales.json"), "w"), ensure_ascii=False, separators=(",", ":"))
for f in ["data/history/whales.json", "data/grids/whales.json"] + list(frames.values()) + list(sframes.values()):
    print(f, os.path.getsize(os.path.join(root, f)))
