"""Surface temperature anomaly by decade from NASA GISTEMP v4 (2°×2°, 1200 km smoothing, base 1951–1980; public domain).
Download into .cache/warming/ and gunzip:
  https://data.giss.nasa.gov/pub/gistemp/gistemp1200_GHCNv4_ERSSTv5.nc.gz
Run: .cache/venv/py/bin/python tools/build/grids_warming.py   (needs numpy, pillow, netCDF4)
Output: data/grids/warming.json + data/grids/warming-<label>.png
  Frames "1880" … "2020" = mean of all available monthly anomalies in that decade (2020s: months published so far);
  a cell needs at least half of the decade's available months, otherwise it is nodata.
  Extra frame for the latest complete year (needs ≥ 9 of 12 months per cell).
  Native 2° grid (180×90), row 0 = 88–90°N, column 0 = 180–178°W. Encoding: linear over [-4, +4] °C (clamped), 0 = nodata."""
import os, json, datetime, warnings
import numpy as np, netCDF4
from PIL import Image

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
NC = os.path.join(root, ".cache/warming/gistemp1200_GHCNv4_ERSSTv5.nc")
OUT = os.path.join(root, "data/grids")
VMIN, VMAX = -4.0, 4.0

d = netCDF4.Dataset(NC)
lat, lon = d["lat"][:], d["lon"][:]
assert lat[0] < lat[-1] and abs(lon[0] + 179) < 1e-3
times = netCDF4.num2date(d["time"][:], d["time"].units)
years = np.array([t.year for t in times])
months = np.array([t.month for t in times])
ta = d["tempanomaly"][:]  # masked array, scaled to K
data = np.where(np.ma.getmaskarray(ta), np.nan, np.ma.getdata(ta)).astype(np.float64)
data = data[:, ::-1, :]  # row 0 = north

def mean_of(sel, need):
    sub = data[sel]
    n = np.isfinite(sub).sum(axis=0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        m = np.nanmean(sub, axis=0)
    m[n < need] = np.nan
    return m

def encode(m):
    img = np.zeros(m.shape, np.uint8)
    ok = np.isfinite(m)
    img[ok] = 1 + np.round((np.clip(m[ok], VMIN, VMAX) - VMIN) / (VMAX - VMIN) * 254).astype(np.uint8)
    return img

frames, stats = {}, {}
last_full = max(y for y in set(years) if (years == y).sum() == 12)
for dec in range(1880, int(years.max()) // 10 * 10 + 1, 10):
    sel = (years >= dec) & (years < dec + 10)
    frames[str(dec)] = mean_of(sel, sel.sum() / 2)
frames[str(last_full)] = mean_of(years == last_full, 9)

os.makedirs(OUT, exist_ok=True)
out = {}
coslat = np.cos(np.radians(lat[::-1]))[:, None] * np.ones((1, len(lon)))
for label, m in frames.items():
    png = f"data/grids/warming-{label}.png"
    Image.fromarray(encode(m), "L").save(os.path.join(root, png), optimize=True)
    out[label] = png
    ok = np.isfinite(m)
    gm = (m[ok] * coslat[ok]).sum() / coslat[ok].sum()
    print(f"{label}: coverage {ok.mean():.0%}, area-mean of covered cells {gm:+.2f} °C, "
          f"arctic(>64N) {np.nanmean(m[:13]):+.2f}")
last_month = times[-1]
desc = {
    "source": "nasa-gistemp",
    "asOf": f"{last_month.year}-{last_month.month:02d}",
    "retrieved": datetime.date.today().isoformat(),
    "note": f"GISTEMP v4 (GHCNv4 + ERSSTv5, 1200 km smoothing). Decadal means of monthly anomalies vs 1951–1980; "
            f"the 2020s frame averages {(years >= 2020).sum()} months (Jan 2020–{last_month.year}-{last_month.month:02d}). "
            f"Frame '{last_full}' is the annual mean for {last_full}. Cells with too few months are nodata. Clamped to ±4 °C.",
    "units": "°C vs 1951–1980",
    "grid": {"width": len(lon), "height": len(lat), "bbox": [-180, -90, 180, 90]},
    "encoding": {"type": "linear", "min": VMIN, "max": VMAX, "nodata": 0},
    "palette": "diverging",
    "frames": out,
}
json.dump(desc, open(os.path.join(OUT, "warming.json"), "w"), indent=1, ensure_ascii=False)
print("frames:", list(out))
