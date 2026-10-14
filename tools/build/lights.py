"""Night lights 2012-2024 from the EOG VIIRS Nighttime Lights (VNL) V2 annual composites (average_masked), CC BY 4.0.
EOG's own download server (eogdata.mines.edu) needs an account, so this uses the open, unmodified-value mirror on Zenodo
by T. Hengl / OpenGeoHub (record 17294744, CC BY 4.0): VNL V2 'average_masked' 2012-2024 at 15 arc-seconds,
values = radiance x 10 (nW/cm²/sr x 10, i.e. 0.1 nW steps) for 2012-2021 but plain radiance rounded to whole
nW/cm²/sr for 2022-2024 (scale detected per file; rounding is unbiased in totals, checked on 2021: < 0.001 %).
Because int16 x 10 saturates, 2012-2021 pixels stop at 3276.7 nW/cm²/sr; every year is capped there (gas flares). Years 2000-2011 in that record are extrapolated and NOT used here.
The script downloads each year (≈ 65 MB, resumable, size checked against the Zenodo record) into .cache/lights/:
  https://zenodo.org/records/17294744/files/nightlights.average_viirs.v21_m_500m_s_<Y>0101_<Y>1231_go_epsg4326_v20250904.tif
Run: .cache/venv/py/bin/python tools/build/lights.py   (needs numpy, pillow, rasterio)
Steps
  1. Each year's 86400 x 35849 grid is summed (radiance x pixel area) into 2.5-arc-minute cells -> .cache/lights/sum-<Y>.npy
  2. Country totals ("sum of lights") per year from Natural Earth 1:50m shapes (data/world50.json) rasterised at 2.5'
     -> data/planet/lights.json (series sol, chg)
  3. Grids at 5 arc-minutes (4320 x 2160): mean radiance for the years in FRAMES (data/grids/lights.json)
     and ratios later / earlier year for the pairs in CHANGES (data/grids/lights-change.json)."""
import os, json, datetime, glob, subprocess
import numpy as np, rasterio
from rasterio import features
from rasterio.transform import from_origin
from PIL import Image

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CACHE = os.path.join(root, ".cache/lights")
YEARS = list(range(2012, 2025))
FN = "nightlights.average_viirs.v21_m_500m_s_{y}0101_{y}1231_go_epsg4326_v20250904.tif"
R = 6371.0088
CW, CH = 8640, 4320            # 2.5' cells, row 0 = 90N
CDEG = 360 / CW
TODAY = datetime.date.today().isoformat()
CAP = 3276.7                                        # common pixel cap, nW/cm²/sr (see cell_sums)
FRAMES = (2012, 2016, 2021, 2022, 2024)                  # years shipped as light frames
CHANGES = {"2012–2024": (2012, 2024), "2021–2024": (2021, 2024)}              # change frames: label -> (earlier, later)


def fetch(y):
    """download one year from Zenodo (resumable) and check its size against the record"""
    p = os.path.join(CACHE, "record.json")
    if not os.path.exists(p):
        subprocess.run(["curl", "-sS", "-f", "-A", "Orbis-data-build/1.0", "-H", "Accept: application/vnd.inveniordm.v1+json",
                        "-o", p, "https://zenodo.org/api/records/17294744"], check=True)
    rec = json.load(open(p))
    assert [r["id"] for r in rec["metadata"]["rights"]] == ["cc-by-4.0"], "licence changed"
    fn = FN.format(y=y); size = rec["files"]["entries"][fn]["size"]; out = os.path.join(CACHE, fn)
    for _ in range(6):
        if os.path.exists(out) and os.path.getsize(out) == size:
            return out
        subprocess.run(["curl", "-sS", "-f", "-L", "-C", "-", "-A", "Orbis-data-build/1.0", "-o", out,
                        f"https://zenodo.org/records/17294744/files/{fn}?download=1"])
    raise RuntimeError("could not download " + fn)


def cell_sums(y):
    """sum over 15" pixels of radiance (nW/cm²/sr) x pixel area (km²), per 2.5' cell."""
    out = os.path.join(CACHE, f"sum-{y}.npy")
    if os.path.exists(out):
        return np.load(out)
    src = rasterio.open(fetch(y))
    t = src.transform
    assert abs(t.a - 1 / 240) < 1e-9 and t.c == -180 and src.width == 86400
    # the mirror stores 2012-2021 as radiance x 10 (0.1 nW steps) and 2022-2024 as plain radiance (whole nW steps):
    # detect the scale from a well-lit strip around 50°N (99th percentile ~400 when x 10, ~35 when plain)
    probe = src.read(1, window=((9000, 9400), (0, 86400)))
    probe = probe[probe > 0]
    scale = 10.0 if np.percentile(probe, 99) > 150 else 1.0
    assert scale == (10.0 if y <= 2021 else 1.0), "unexpected scale"
    print(y, "scale", scale)
    acc = np.zeros((CH, CW))
    B = 1024
    for r0 in range(0, src.height, B):
        n = min(B, src.height - r0)
        a = src.read(1, window=((r0, r0 + n), (0, src.width))).astype(np.float64)
        a[a < 0] = 0
        a /= scale  # -> nW/cm²/sr
        # 2012-2021 saturate at 32767 / 10 = 3276.7 nW/cm²/sr (int16 x 10); 2022-2024 run up to 32767. Without a common
        # cap, gas flares (the only pixels that bright, besides a few spots such as the Las Vegas Strip) jump in 2022.
        np.minimum(a, CAP, out=a)
        lat = t.f + (np.arange(r0, r0 + n) + 0.5) * t.e
        px_area = (R * np.radians(1 / 240)) ** 2 * np.cos(np.radians(lat))
        a *= px_area[:, None]
        cs = a.reshape(n, CW, 10).sum(axis=2)
        orow = np.clip(np.floor((90 - lat) / CDEG).astype(int), 0, CH - 1)
        np.add.at(acc, orow, cs)
    np.save(out, acc.astype(np.float32))
    print("year", y, "total", acc.sum())
    return acc.astype(np.float32)


def topo_features(path):
    t = json.load(open(path))
    sc, tr = t["transform"]["scale"], t["transform"]["translate"]
    arcs = []
    for arc in t["arcs"]:
        x = y = 0; pts = []
        for dx, dy in arc:
            x += dx; y += dy
            pts.append([x * sc[0] + tr[0], y * sc[1] + tr[1]])
        arcs.append(pts)
    def ring(ix):
        pts = []
        for i in ix:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            pts.extend(a if not pts else a[1:])
        return pts
    obj = list(t["objects"].values())[0]
    for g in obj["geometries"]:
        if g["type"] == "Polygon":
            geom = {"type": "Polygon", "coordinates": [ring(r) for r in g["arcs"]]}
        elif g["type"] == "MultiPolygon":
            geom = {"type": "MultiPolygon", "coordinates": [[ring(r) for r in p] for p in g["arcs"]]}
        else:
            continue
        yield g["id"], geom


def main():
    sums = {y: cell_sums(y) for y in YEARS}

    # ---- country totals
    ids, shapes = [], []
    for iso, geom in topo_features(os.path.join(root, "data/world50.json")):
        ids.append(iso); shapes.append((geom, len(ids)))
    lab = features.rasterize(shapes, out_shape=(CH, CW), transform=from_origin(-180, 90, CDEG, CDEG),
                             fill=0, dtype="int32", all_touched=False)
    tot = {}
    for y in YEARS:
        s = np.bincount(lab.ravel(), weights=sums[y].ravel().astype(np.float64), minlength=len(ids) + 1)
        tot[y] = s
        print(y, "world", round(s.sum() / 1e6, 2), "M  in countries", round(s[1:].sum() / s.sum() * 100, 1), "%")
    sol, chg = {}, {}
    for i, iso in enumerate(ids, start=1):
        v = [tot[y][i] for y in YEARS]
        if v[0] <= 0 and v[-1] <= 0:
            continue
        sol[iso] = [round(x / 1000, 2) for x in v]  # thousand units
        if v[0] >= 50:   # skip specks: < 50 units in 2012 makes % change meaningless
            chg[iso] = [round((x / v[0] - 1) * 100, 1) for x in v]
    world = [round(tot[y].sum() / 1000, 2) for y in YEARS]
    ds = {
        "source": "eog-vnl", "asOf": "2024", "retrieved": TODAY, "years": YEARS,
        "note": "EOG VIIRS Nighttime Lights V2 annual 'average_masked' (background, fires and aurora zeroed out), 2012 (from April) to 2024, "
                "via the Zenodo mirror 17294744 (Hengl/OpenGeoHub, CC BY 4.0). sol = sum over the country of radiance × pixel area "
                "(nW/cm²/sr × km², in thousands), countries from Natural Earth 1:50m rasterised at 2.5′. "
                "chg = % change against 2012 (countries with a 2012 total of at least 0.05 thousand). "
                "Pixels are capped at 3,277 nW/cm²/sr in every year (the mirror's 2012–2021 files saturate there). Gas flares are "
                "not masked out and add light in oil-producing regions; flaring countries (Iraq, Iran, Libya) still jump in 2022, "
                "which looks like a processing change. Single-year jumps (e.g. Russia and Ukraine in 2021) may reflect snow or "
                "processing, so compare changes over several years. Built by tools/build/lights.py.",
        "series": {
            "sol": {"label": "Night light (sum of radiance × area)", "units": "thousand nW/cm²/sr·km²", "values": sol},
            "chg": {"label": "Change in night light since 2012", "units": "%", "values": chg},
        },
        "world": {"sol": world},
    }
    os.makedirs(os.path.join(root, "data/planet"), exist_ok=True)
    json.dump(ds, open(os.path.join(root, "data/planet/lights.json"), "w"), separators=(",", ":"))

    # ---- grids at 5' (4320 x 2160)
    GW, GH = 4320, 2160
    lat_e = np.radians(90 - np.arange(GH + 1) * 180 / GH)
    garea = R * R * np.radians(360 / GW) * (np.sin(lat_e[:-1]) - np.sin(lat_e[1:]))  # km² per cell row
    def down(a):
        return a.astype(np.float64).reshape(GH, 2, GW, 2).sum(axis=(1, 3))
    def mean_rad(y):
        return down(sums[y]) / garea[:, None]  # area-weighted mean radiance nW/cm²/sr

    LMIN, LMAX = 0.6, 60.0
    frames = {}
    for y in FRAMES:
        m = mean_rad(y)
        img = np.zeros(m.shape, np.uint8)
        ok = m >= LMIN * 0.999
        lv = (np.log10(np.clip(m[ok], LMIN, LMAX)) - np.log10(LMIN)) / (np.log10(LMAX) - np.log10(LMIN))
        img[ok] = 1 + np.round(lv * 254).astype(np.uint8)
        png = f"data/grids/lights-{y}.png"
        Image.fromarray(img, "L").save(os.path.join(root, png), optimize=True)
        frames[str(y)] = png
        print(png, os.path.getsize(os.path.join(root, png)))
    json.dump({
        "source": "eog-vnl", "asOf": "2024", "retrieved": TODAY,
        "note": "EOG VIIRS Nighttime Lights V2 annual average_masked (via Zenodo 17294744). Mean radiance over each 5′ cell "
                "(≈ 9 km), land and water; cells below 0.6 nW/cm²/sr left blank, clamped at 60. The 2012 composite starts in April 2012, when VIIRS data begin; pixels capped at 3,277 (gas flares).",
        "units": "nW/cm²/sr",
        "grid": {"width": GW, "height": GH, "bbox": [-180, -90, 180, 90]},
        "encoding": {"type": "log", "min": LMIN, "max": LMAX, "nodata": 0},
        "palette": "sequential", "frames": frames,
    }, open(os.path.join(root, "data/grids/lights.json"), "w"), indent=1, ensure_ascii=False)

    # change grids: ratio later / earlier year; a cell needs some light in at least one of the two years
    TH = 0.5
    FLOOR = 0.1  # avoids division by zero: 'from nothing' saturates at the top of the scale
    RMIN, RMAX = 0.1, 10.0
    cframes = {}
    for label, (y0, y1) in CHANGES.items():
        a, b = mean_rad(y0), mean_rad(y1)
        lit = (a >= TH) | (b >= TH)
        ratio = (b + FLOOR) / (a + FLOOR)
        img = np.zeros(a.shape, np.uint8)
        lv = (np.log10(np.clip(ratio[lit], RMIN, RMAX)) - np.log10(RMIN)) / (np.log10(RMAX) - np.log10(RMIN))
        img[lit] = 1 + np.round(lv * 254).astype(np.uint8)
        png = f"data/grids/lights-change-{y0}-{y1}.png"
        Image.fromarray(img, "L").save(os.path.join(root, png), optimize=True)
        cframes[label] = png
        print(png, os.path.getsize(os.path.join(root, png)))
    json.dump({
        "source": "eog-vnl", "asOf": "2024", "retrieved": TODAY,
        "note": "Ratio of mean radiance, later year ÷ earlier year, per 5′ cell (≈ 9 km) from EOG VNL V2 annual average_masked "
                "(via Zenodo 17294744). Frames: " + ", ".join(f"'{k}' = {a}→{b}" for k, (a, b) in CHANGES.items()) + ". "
                "Shown where either year reaches 0.5 nW/cm²/sr; 0.1 is added to both years before dividing, so newly lit cells "
                "saturate at the top. Clamped to 0.1–10 (1 = no change). The 2012 composite starts in April 2012, when VIIRS data begin.",
        "units": "light, later ÷ earlier year",
        "grid": {"width": GW, "height": GH, "bbox": [-180, -90, 180, 90]},
        "encoding": {"type": "log", "min": RMIN, "max": RMAX, "nodata": 0},
        "palette": "diverging", "frames": cframes,
    }, open(os.path.join(root, "data/grids/lights-change.json"), "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
