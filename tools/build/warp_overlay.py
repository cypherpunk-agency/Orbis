"""Warp a scanned historical map onto longitude/latitude for the `overlay` layer.

Usage:
  python3 tools/build/warp_overlay.py <scan.png|jpg> <gcps.json> <out-name> [--width 2048] [--quality 80]

gcps.json describes the scan and its ground control points (pixel x, pixel y, lon, lat):
  { "title": "Europe in 1648", "source": "<source id>", "asOf": "1648", "note": "...",
    "bbox": [-12, 35, 32, 60],            # optional output box (lon0, lat0, lon1, lat1); default: GCP extent + 5%
    "order": 2,                           # optional polynomial order (1 = affine, needs 3 GCPs; 2 needs 6; 3 needs 10)
    "gcps": [[412, 980, -9.14, 38.71], ...] }

Writes data/overlays/<out-name>.webp (equirectangular, transparent outside the scan) and data/overlays/<out-name>.json
(dataset with image path and bbox). Prints the fit error in pixels for each control point; anything above a few
pixels usually means a mistyped point. No GDAL needed: numpy + Pillow only.
"""
import json, sys, os, argparse
import numpy as np
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")

def terms(lon, lat, order):
    t = [np.ones_like(lon), lon, lat]
    if order >= 2: t += [lon * lon, lon * lat, lat * lat]
    if order >= 3: t += [lon ** 3, lon * lon * lat, lon * lat * lat, lat ** 3]
    return np.stack(t, axis=-1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scan"); ap.add_argument("gcps"); ap.add_argument("name")
    ap.add_argument("--width", type=int, default=2048); ap.add_argument("--quality", type=int, default=80)
    a = ap.parse_args()
    meta = json.load(open(a.gcps))
    g = np.array(meta["gcps"], dtype=float)
    order = meta.get("order") or (3 if len(g) >= 10 else 2 if len(g) >= 6 else 1)
    need = {1: 3, 2: 6, 3: 10}[order]
    if len(g) < need: sys.exit(f"order {order} needs at least {need} control points, got {len(g)}")
    # fit lon/lat -> pixel (inverse mapping, so every output pixel can look up its source)
    A = terms(g[:, 2], g[:, 3], order)
    cx, *_ = np.linalg.lstsq(A, g[:, 0], rcond=None)
    cy, *_ = np.linalg.lstsq(A, g[:, 1], rcond=None)
    err = np.hypot(A @ cx - g[:, 0], A @ cy - g[:, 1])
    for p, e in zip(g, err): print(f"  GCP lon {p[2]:8.3f} lat {p[3]:7.3f}: {e:6.1f} px")
    print(f"order {order}, mean error {err.mean():.1f} px, max {err.max():.1f} px")

    src = np.asarray(Image.open(a.scan).convert("RGBA"))
    H0, W0 = src.shape[:2]
    if "bbox" in meta: lon0, lat0, lon1, lat1 = meta["bbox"]
    else:
        lon0, lon1, lat0, lat1 = g[:, 2].min(), g[:, 2].max(), g[:, 3].min(), g[:, 3].max()
        dx, dy = (lon1 - lon0) * 0.05, (lat1 - lat0) * 0.05
        lon0, lon1, lat0, lat1 = lon0 - dx, lon1 + dx, lat0 - dy, lat1 + dy
    W = a.width; H = max(1, round(W * (lat1 - lat0) / (lon1 - lon0)))
    lon = np.linspace(lon0, lon1, W, endpoint=False) + (lon1 - lon0) / W / 2
    lat = np.linspace(lat1, lat0, H, endpoint=False) - (lat1 - lat0) / H / 2
    LON, LAT = np.meshgrid(lon, lat)
    T = terms(LON, LAT, order)
    px, py = T @ cx, T @ cy
    # bilinear sampling; transparent outside the scan
    x0 = np.floor(px).astype(int); y0 = np.floor(py).astype(int); fx = (px - x0)[..., None]; fy = (py - y0)[..., None]
    inside = (x0 >= 0) & (y0 >= 0) & (x0 < W0 - 1) & (y0 < H0 - 1)
    x0c = np.clip(x0, 0, W0 - 2); y0c = np.clip(y0, 0, H0 - 2)
    s = src.astype(float)
    out = (s[y0c, x0c] * (1 - fx) * (1 - fy) + s[y0c, x0c + 1] * fx * (1 - fy) + s[y0c + 1, x0c] * (1 - fx) * fy + s[y0c + 1, x0c + 1] * fx * fy)
    out[~inside] = 0
    os.makedirs(os.path.join(ROOT, "data/overlays"), exist_ok=True)
    img_path = f"data/overlays/{a.name}.webp"
    Image.fromarray(out.astype(np.uint8), "RGBA").save(os.path.join(ROOT, img_path), "WEBP", quality=a.quality)
    ds = {k: meta[k] for k in ("source", "asOf", "note", "title") if k in meta}
    ds.update({"retrieved": meta.get("retrieved"), "image": img_path, "bbox": [round(v, 4) for v in (lon0, lat0, lon1, lat1)],
               "fit": {"order": order, "gcps": len(g), "meanErrorPx": round(float(err.mean()), 1)}})
    json.dump(ds, open(os.path.join(ROOT, f"data/overlays/{a.name}.json"), "w"), indent=1)
    print("wrote", img_path, f"{os.path.getsize(os.path.join(ROOT, img_path)) // 1024} KB", f"{W}x{H}")

if __name__ == "__main__":
    main()
