"""Population density grid from GHSL GHS-POP R2023A, epoch 2025, 30 arc-second, EPSG:4326 (EU JRC, CC BY 4.0).
Download (≈220 MB) into .cache/popdensity/ and unzip the .tif:
  https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_POP_GLOBE_R2023A/GHS_POP_E2025_GLOBE_R2023A_4326_30ss/V1-0/GHS_POP_E2025_GLOBE_R2023A_4326_30ss_V1_0.zip
Run: .cache/venv/py/bin/python tools/build/grids_popdensity.py   (needs numpy, pillow, rasterio)
Output: data/grids/popdensity.json + data/grids/popdensity-2025.png
  People are summed into each output cell (every 30" source pixel goes to the cell holding its centre),
  then divided by the cell's true area on the sphere -> people per km² of total (land + water) area.
  Encoding: log10, bytes 1..255 over [1, 10000] people/km² (clamped); 0 = no people."""
import os, json, datetime
import numpy as np, rasterio
from PIL import Image

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TIF = os.path.join(root, ".cache/popdensity/GHS_POP_E2025_GLOBE_R2023A_4326_30ss_V1_0.tif")
OUT = os.path.join(root, "data/grids")
W, H = 2048, 1024
VMIN, VMAX = 1.0, 10000.0
R = 6371.0088  # km

src = rasterio.open(TIF)
t = src.transform
col_lon = t.c + (np.arange(src.width) + 0.5) * t.a
ocol = np.clip(np.floor((col_lon + 180) / 360 * W).astype(int), 0, W - 1)
starts = np.flatnonzero(np.r_[True, np.diff(ocol) != 0])  # ocol is monotonic
bins = ocol[starts]
people = np.zeros((H, W))
BLOCK = 512
for r0 in range(0, src.height, BLOCK):
    n = min(BLOCK, src.height - r0)
    a = src.read(1, window=((r0, r0 + n), (0, src.width))).astype(np.float64)
    a[~np.isfinite(a) | (a < 0)] = 0
    row_lat = t.f + (np.arange(r0, r0 + n) + 0.5) * t.e
    orow = np.clip(np.floor((90 - row_lat) / 180 * H).astype(int), 0, H - 1)
    colsum = np.add.reduceat(a, starts, axis=1)  # (n, len(bins))
    for ro in np.unique(orow):
        people[ro, bins] += colsum[orow == ro].sum(axis=0)
total = people.sum()
print(f"total people: {total/1e9:.3f} bn")

lat_edges = np.radians(90 - np.arange(H + 1) * 180 / H)
area = R * R * np.radians(360 / W) * (np.sin(lat_edges[:-1]) - np.sin(lat_edges[1:]))  # km² per row
dens = people / area[:, None]
img = np.zeros((H, W), np.uint8)
m = people > 0
lv = (np.log10(np.clip(dens[m], VMIN, VMAX)) - np.log10(VMIN)) / (np.log10(VMAX) - np.log10(VMIN))
img[m] = 1 + np.round(lv * 254).astype(np.uint8)
os.makedirs(OUT, exist_ok=True)
png = "data/grids/popdensity-2025.png"
Image.fromarray(img, "L").save(os.path.join(root, png), optimize=True)
desc = {
    "source": "ghsl-pop", "asOf": "2025",
    "retrieved": datetime.date.today().isoformat(),
    "note": "GHS-POP R2023A epoch 2025 (modelled from 2020-round census data), 30 arc-second grid summed into cells; "
            "density = residents / total cell area (land and water). Values clamped to 1–10,000 people/km²; 0 = no residents.",
    "units": "people per km²",
    "grid": {"width": W, "height": H, "bbox": [-180, -90, 180, 90]},
    "encoding": {"type": "log", "min": VMIN, "max": VMAX, "nodata": 0},
    "palette": "sequential",
    "frames": {"2025": png},
}
json.dump(desc, open(os.path.join(OUT, "popdensity.json"), "w"), indent=1, ensure_ascii=False)
print("wrote", png, os.path.getsize(os.path.join(root, png)), "bytes")
