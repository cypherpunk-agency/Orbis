"""Jet-stream winds: 250 hPa u/v from one NOAA GFS analysis (1°×1°, public domain).
Download the analysis (f000) for a cycle into .cache/wind/ with the NOMADS GRIB filter, e.g. 2026-10-13 12 UTC:
  curl --http1.1 -o .cache/wind/gfs.20261013.t12z.pgrb2.1p00.f000.250mb.grib2 \
    "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?dir=%2Fgfs.20261013%2F12%2Fatmos&file=gfs.t12z.pgrb2.1p00.f000&var_UGRD=on&var_VGRD=on&lev_250_mb=on"
  (NOMADS keeps only the last ~10 days; older cycles: https://www.ncei.noaa.gov/products/weather-climate-models/global-forecast)
Run: .cache/venv/py/bin/python tools/build/grids_wind.py [grib2 file]   (needs numpy, pillow, eccodes)
  Without an argument it uses the newest *.grib2 in .cache/wind/.
Output: data/grids/wind.json + data/grids/wind-<YYYYMMDDHH>.png
  The 360×181 point grid (90°N…90°S, 0…359°E) is resampled to 360×180 cells (bbox -180,-90,180,90; row 0 = 89.5°N centre)
  by averaging the 2×2 surrounding grid points. RGB PNG: R = u (eastward), G = v (northward),
  byte = 128 + value·127/MAX, clamped to 1..255, so 128 = 0 m/s; B unused (0)."""
import os, sys, glob, json, datetime
import numpy as np, eccodes
from PIL import Image

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(root, "data/grids")
MAX = 100.0  # m/s

path = sys.argv[1] if len(sys.argv) > 1 else max(glob.glob(os.path.join(root, ".cache/wind/*.grib2")), key=os.path.getmtime)
fields, when = {}, None
with open(path, "rb") as f:
    while (g := eccodes.codes_grib_new_from_file(f)) is not None:
        name = eccodes.codes_get(g, "shortName")
        assert eccodes.codes_get(g, "level") == 250 and eccodes.codes_get(g, "stepRange") == "0"
        ni, nj = eccodes.codes_get(g, "Ni"), eccodes.codes_get(g, "Nj")
        assert (ni, nj) == (360, 181) and eccodes.codes_get(g, "latitudeOfFirstGridPointInDegrees") == 90
        assert eccodes.codes_get(g, "longitudeOfFirstGridPointInDegrees") == 0 and eccodes.codes_get(g, "jScansPositively") == 0
        fields[name] = eccodes.codes_get_values(g).reshape(nj, ni)
        when = datetime.datetime.strptime(f"{eccodes.codes_get(g, 'dataDate')}{eccodes.codes_get(g, 'dataTime'):04d}", "%Y%m%d%H%M")
        eccodes.codes_release(g)

def to_cells(a):
    a = np.roll(a, -180, axis=1)        # column 0 = 180°W
    a = np.concatenate([a, a[:, :1]], 1)  # wrap: 361 columns, 180°W … 180°E
    return (a[:-1, :-1] + a[1:, :-1] + a[:-1, 1:] + a[1:, 1:]) / 4  # 180 × 360 cell centres

u, v = to_cells(fields["u"]), to_cells(fields["v"])
enc = lambda a: np.clip(np.round(128 + a * 127 / MAX), 1, 255).astype(np.uint8)
rgb = np.dstack([enc(u), enc(v), np.zeros(u.shape, np.uint8)])
label = when.strftime("%Y%m%d%H")
png = f"data/grids/wind-{label}.png"
os.makedirs(OUT, exist_ok=True)
Image.fromarray(rgb, "RGB").save(os.path.join(root, png), optimize=True)
spd = np.hypot(u, v)
print(f"{when:%Y-%m-%d %H} UTC: max speed {spd.max():.1f} m/s, share > {MAX:g}: {(spd > MAX).mean():.3%}")
desc = {
    "source": "noaa-gfs",
    "asOf": when.strftime("%Y-%m-%dT%H:%MZ"),
    "retrieved": datetime.date.today().isoformat(),
    "note": f"NOAA NCEP GFS 0.25°-model analysis (f000) on the 1° output grid, {when:%d %b %Y %H}:00 UTC, 250 hPa (≈10 km, jet-stream level). "
            f"Grid points averaged to 1° cells. Components clamped to ±{MAX:g} m/s.",
    "units": "m/s",
    "grid": {"width": 360, "height": 180, "bbox": [-180, -90, 180, 90]},
    "encoding": {"type": "vector", "min": -MAX, "max": MAX},
    "palette": "sequential",
    "frames": {str(when.year): png},
}
json.dump(desc, open(os.path.join(OUT, "wind.json"), "w"), indent=1, ensure_ascii=False)
print("wrote", png, os.path.getsize(os.path.join(root, png)), "bytes")
