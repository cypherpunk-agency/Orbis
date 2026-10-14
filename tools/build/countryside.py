"""Net migration 2000-2019 on a grid, from Niva et al. (2023), 'World's human migration patterns in 2000-2019 unveiled
by high-resolution data', Nature Human Behaviour 7: 2023-2037; data Zenodo record 7997134 (CC BY 4.0).
Fetch (≈55 MB) into .cache/countryside/:
  https://zenodo.org/api/records/7997134/files/raster_netMgr_2000_2019_20yrSum.tif/content
  https://zenodo.org/api/records/7997134/files/polyg_adm0_dataNetMgr.gpkg/content
  https://zenodo.org/api/records/7997134/files/polyg_adm1_dataNetMgr.gpkg/content
(the full record is ~660 MB; only these three files, ~19 MB, are needed)
Population weights: GHSL GHS-POP R2023A epoch 2025, 30" (.cache/popdensity/, see grids_popdensity.py).
Run: .cache/venv/py/bin/python tools/build/countryside.py   (numpy, pillow, rasterio)
Output:
  data/grids/netmigration.json + data/grids/netmigration-2000-2019.png
     the 5' grid (sum of annual net-migration rates, per 1,000 residents, 2000-2019) averaged into 10' cells,
     weighted by population; shown as % of the population. Cells with fewer than 1,000 residents are left empty.
     Linear encoding, clamped to ±50 %, diverging palette (blue = net loss, red = net gain).
  data/people/net-migration.json   series by country:
     nm20      national net migration 2000-2019, % of population (gpkg adm0 'netMgr_20yrsum' / 10)
     pop_loss  % of residents (GHS-POP 2025) living in 5' cells that lost people to migration over 2000-2019
     area_loss % of populated cells (>= 100 residents) that lost people to migration
  data/people/net-migration-adm1.json   provinces/states of CHN and USA (ids as in data/geo/admin1/<ISO3>.json):
     nm20      net migration 2000-2019, % of population (gpkg adm1 'netMgr_20yrsum' / 10)"""
import os, json, sqlite3, datetime, unicodedata
import numpy as np, rasterio
from rasterio import features
from PIL import Image

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
C = os.path.join(root, ".cache/countryside")
NM = os.path.join(C, "raster_netMgr_2000_2019_20yrSum.tif")
POP = os.path.join(root, ".cache/popdensity/GHS_POP_E2025_GLOBE_R2023A_4326_30ss_V1_0.tif")
LIM = 50.0  # %
F = 2       # 5' -> 10'

nm = rasterio.open(NM)
a = nm.read(1).astype(np.float64) / 10.0  # per 1,000 -> %
H5, W5 = a.shape

# population on the 5' grid: sum 10x10 blocks of the 30" GHS-POP grid (aligned at -180/90)
ps = rasterio.open(POP)
t = ps.transform
col_lon = t.c + (np.arange(ps.width) + 0.5) * t.a
ocol = np.clip(np.floor((col_lon + 180) * 12).astype(int), 0, W5 - 1)   # every 30" pixel goes to the 5' cell holding its centre
starts = np.flatnonzero(np.r_[True, np.diff(ocol) != 0]); bins = ocol[starts]
pop = np.zeros((H5, W5))
for r0 in range(0, ps.height, 1200):
    n = min(1200, ps.height - r0)
    b = ps.read(1, window=((r0, r0 + n), (0, ps.width))).astype(np.float64)
    b[~np.isfinite(b) | (b < 0)] = 0
    rows = np.clip(np.floor((90 - (t.f + (np.arange(r0, r0 + n) + 0.5) * t.e)) * 12).astype(int), 0, H5 - 1)
    s = np.add.reduceat(b, starts, axis=1)
    for ro in np.unique(rows):
        pop[ro, bins] += s[rows == ro].sum(axis=0)
print(f"population {pop.sum()/1e9:.2f} bn")

ok = np.isfinite(a)
# 10' cells: population-weighted mean
w = np.where(ok, pop, 0); v = np.where(ok, a, 0)
H, W = H5 // F, W5 // F
ws = w.reshape(H, F, W, F).sum(axis=(1, 3)); vs = (v * w).reshape(H, F, W, F).sum(axis=(1, 3))
mean = np.where(ws > 0, vs / np.maximum(ws, 1e-9), np.nan)
show = ws >= 1000
img = np.zeros((H, W), np.uint8)
tt = (np.clip(mean[show], -LIM, LIM) + LIM) / (2 * LIM)
img[show] = 1 + np.round(tt * 254).astype(np.uint8)
png = "data/grids/netmigration-2000-2019.png"
Image.fromarray(img, "L").save(os.path.join(root, png), optimize=True)
print("png", os.path.getsize(os.path.join(root, png)))
today = datetime.date.today().isoformat()
desc = {
    "source": "niva-netmigration", "asOf": "2019", "retrieved": today,
    "note": "Niva et al. (2023), net migration 2000–2019: annual net-migration rates (5′ grid, estimated as reported population "
            "change minus births plus deaths) summed over 20 years, here averaged into 10′ cells weighted by population (GHS-POP 2025) "
            "and shown as % of residents. Positive = more people moved in than out. Clamped to ±50 %; cells with fewer than 1,000 "
            "residents left empty. The authors warn that single cells are noisy: read patterns, not pixels.",
    "units": "% of residents, 2000–2019",
    "grid": {"width": W, "height": H, "bbox": [-180, -90, 180, 90]},
    "encoding": {"type": "linear", "min": -LIM, "max": LIM, "nodata": 0},
    "palette": "diverging",
    "frames": {"2000–2019": png},
}
json.dump(desc, open(os.path.join(root, "data/grids/netmigration.json"), "w"), indent=1, ensure_ascii=False)

# country raster from the site's own 1:50m geometry (topojson decoded here)
topo = json.load(open(os.path.join(root, "data/world50.json")))
sc, tr = topo["transform"]["scale"], topo["transform"]["translate"]
arcs = []
for arc in topo["arcs"]:
    x = y = 0; pts = []
    for dx, dy in arc:
        x += dx; y += dy; pts.append((x * sc[0] + tr[0], y * sc[1] + tr[1]))
    arcs.append(pts)
def ring(ix):
    out = []
    for i in ix:
        p = arcs[i] if i >= 0 else arcs[~i][::-1]
        out.extend(p if not out else p[1:])
    return out
shapes, isos = [], []
for k, g in enumerate(topo["objects"]["countries"]["geometries"]):
    if g["type"] == "Polygon": polys = [g["arcs"]]
    elif g["type"] == "MultiPolygon": polys = g["arcs"]
    else: continue
    geom = {"type": "MultiPolygon", "coordinates": [[ring(r) for r in p] for p in polys]}
    shapes.append((geom, k + 1)); isos.append(g["id"])
cid = features.rasterize(shapes, out_shape=(H5, W5), transform=nm.transform, fill=0, dtype="int32", all_touched=False)

pop_loss, area_loss = {}, {}
for k, iso in enumerate(isos):
    m = (cid == k + 1) & ok & (pop >= 100)
    if m.sum() < 20 or pop[m].sum() < 1e6: continue
    lose = a[m] < 0
    pop_loss[iso] = [round(float(pop[m][lose].sum() / pop[m].sum() * 100), 1)]
    area_loss[iso] = [round(float(lose.mean() * 100), 1)]
m = ok & (pop >= 100)
print(f"world: {pop[m][a[m] < 0].sum()/pop[m].sum()*100:.0f}% of people in losing cells; {(a[m] < 0).mean()*100:.0f}% of populated cells lose")

con = sqlite3.connect(os.path.join(C, "polyg_adm0_dataNetMgr.gpkg"))
nm20 = {iso: [round(v / 10, 1)] for iso, v in con.execute('select iso3, netMgr_20yrsum from polyg_adm0_dataNetMgr') if v is not None and iso}
ser = {
    "source": "niva-netmigration", "asOf": "2019", "retrieved": today,
    "note": "Niva et al. (2023). nm20: national net migration 2000–2019 (sum of annual rates), % of population. pop_loss: share of "
            "residents (GHS-POP 2025) living in 5′ cells with net out-migration over 2000–2019; area_loss: share of populated 5′ cells "
            "(at least 100 residents) with net out-migration. Countries over 1 million people. Country areas from Natural Earth 1:50m.",
    "years": [2019],
    "series": {
        "nm20": {"label": "Net migration 2000–2019, % of population", "units": "%", "values": nm20},
        "pop_loss": {"label": "People living in places that lost residents to migration, 2000–2019", "units": "%", "values": pop_loss},
        "area_loss": {"label": "Populated places that lost residents to migration, 2000–2019", "units": "% of populated cells", "values": area_loss},
    },
}
p = os.path.join(root, "data/people/net-migration.json")
json.dump(ser, open(p, "w"), separators=(",", ":"), ensure_ascii=False)
print("wrote", p, os.path.getsize(p))
for iso in ["CHN", "IND", "NGA", "NER", "MLI", "TCD", "BFA", "ESP", "BGR", "DEU", "POL", "USA", "BRA", "ROU", "ITA", "FRA", "JPN", "RUS", "LTU", "ALB"]:
    print(iso, nm20.get(iso), pop_loss.get(iso), area_loss.get(iso))

# provinces / states (the authors' adm1 polygons), matched by name to the site's admin-1 geometry
norm = lambda x: unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode().lower().replace(" ", "").replace("-", "")
ALIAS = {"neimongol": "innermongol", "ningxiahui": "ningxia", "xinjianguygur": "xinjiang"}
con1 = sqlite3.connect(os.path.join(C, "polyg_adm1_dataNetMgr.gpkg"))
adm1 = {}
for iso in ["CHN", "USA"]:
    geo = json.load(open(os.path.join(root, f"data/geo/admin1/{iso}.json")))["objects"]["regions"]["geometries"]
    ids = {norm(g["properties"]["name"]): g["id"] for g in geo}
    for name, v in con1.execute("select NAME_1, netMgr_20yrsum from polyg_adm1_dataNetMgr where iso3=?", (iso,)):
        k = ALIAS.get(norm(name), norm(name))
        if k in ids and v is not None: adm1[ids[k]] = [round(v / 10, 1)]
        else: print("unmatched", iso, name)
ser1 = {"source": "niva-netmigration", "asOf": "2019", "retrieved": today,
        "note": "Niva et al. (2023), adm1 polygons: net migration 2000–2019 (sum of annual rates per 1,000), shown as % of population. "
                "Chinese provinces and US states; ids match data/geo/admin1/.",
        "years": [2019],
        "series": {"nm20": {"label": "Net migration 2000–2019, % of population", "units": "%", "values": adm1}}}
p = os.path.join(root, "data/people/net-migration-adm1.json")
json.dump(ser1, open(p, "w"), separators=(",", ":"), ensure_ascii=False)
print("wrote", p, os.path.getsize(p))
print(sorted(adm1.items(), key=lambda kv: kv[1][0]))
