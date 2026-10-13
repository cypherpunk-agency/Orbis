"""Admin-1 (states, provinces, Länder) geometry per country from Natural Earth 1:10m (public domain).
Fetch:
  mkdir -p .cache/admin1 && curl -L -o .cache/admin1/ne_10m_admin_1_states_provinces.zip \
    https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_1_states_provinces.zip
Run: python3 tools/build/admin1.py [ISO3 ...]
Needs the mapshaper CLI in tools/node_modules (npm install in tools/).
Output: data/geo/admin1/<ISO3>.json, TopoJSON, one object "regions".
  Feature id = ISO 3166-2 code from NE `iso_3166_2` (e.g. "AT-9", "US-CA", "IN-MH"); NE placeholder codes ending in
  "~" lose the "~" (e.g. "CN-X01" Paracel Islands, "AU-X02" Jervis Bay Territory); if NE has no code, its adm1_code.
  Parts that share a code are dissolved (Lord Howe Island into AU-NSW); Macquarie Island is merged into AU-TAS.
  properties: name (NE `name`, local-language form where NE uses it), lx, ly = NE label point (longitude, latitude).
  Units are NE's admin-1 level: FRA départements, ITA provinces, ESP provinces, GBR counties/unitary authorities.
  Each file is simplified (Visvalingam, keep-shapes) until it is <= MAX_KB."""
import os, sys, json, zipfile, subprocess
root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
cache = os.path.join(root, ".cache/admin1")
out_dir = os.path.join(root, "data/geo/admin1")
MS = os.path.join(root, "tools/node_modules/.bin/mapshaper")
COUNTRIES = "AUT DEU USA IND CHN BRA NGA FRA ITA ESP GBR CAN AUS MEX RUS IDN ZAF JPN".split()
MAX_KB = 150
PCTS = [30, 20, 14, 10, 7, 5, 3.5, 2.5, 1.8, 1.2, 0.8]  # percentage of removable vertices retained, tried in turn
REMAP = {"AU-X03~": "AU-TAS"}  # Macquarie Island is part of Tasmania

def run(*args):
    r = subprocess.run([MS, *args], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr)
    return r.stderr

zpath = os.path.join(cache, "ne_10m_admin_1_states_provinces.zip")
shp = os.path.join(cache, "ne_10m_admin_1_states_provinces.shp")
if not os.path.exists(shp):
    zipfile.ZipFile(zpath).extractall(cache)
countries = sys.argv[1:] or COUNTRIES
sel = os.path.join(cache, "selected.geojson")
if not os.path.exists(sel):
    expr = "[" + ",".join(f"'{c}'" for c in COUNTRIES) + "].indexOf(adm0_a3) > -1"
    run("-i", shp, "encoding=utf8", "-filter", expr,
        "-filter-fields", "adm0_a3,iso_3166_2,adm1_code,name,note,latitude,longitude",
        "-o", sel, "format=geojson", "precision=0.000001")
feats = json.load(open(sel, encoding="utf-8"))["features"]
os.makedirs(out_dir, exist_ok=True)
for c in countries:
    rows = [f for f in feats if f["properties"].get("adm0_a3") == c]
    if not rows: raise SystemExit(f"no features for {c}")
    label = {}
    for f in rows:
        p = f["properties"]
        raw = p["iso_3166_2"] or ""
        rid = REMAP.get(raw) or (raw.rstrip("~") if raw and not raw.endswith("-") else p["adm1_code"])
        f["properties"] = {"id": rid}
        main = raw.rstrip("~") == rid  # this part carries the region's own name and label point
        if rid not in label or (main and not label[rid][0]):
            name = p["name"] or ("Minor islands" if "minor island" in (p["note"] or "") else rid)
            label[rid] = (main, name, round(p["longitude"], 3), round(p["latitude"], 3))
    tmp = os.path.join(cache, f"{c}.geojson")
    json.dump({"type": "FeatureCollection", "features": rows}, open(tmp, "w", encoding="utf-8"))
    dst = os.path.join(out_dir, f"{c}.json")
    for pct in PCTS:
        run("-i", tmp, "-dissolve", "id", "-simplify", f"{pct}%", "keep-shapes",
            "-rename-layers", "regions",
            "-o", dst, "format=topojson", "quantization=100000", "id-field=id", "force")
        kb = os.path.getsize(dst) / 1024
        if kb <= MAX_KB: break
    topo = json.load(open(dst, encoding="utf-8"))
    for g in topo["objects"]["regions"]["geometries"]:
        _, name, lx, ly = label[g["id"]]
        g["properties"] = {"name": name, "lx": lx, "ly": ly}
    s = json.dumps(topo, ensure_ascii=False, separators=(",", ":"))
    open(dst, "w", encoding="utf-8").write(s)
    print(f"{c}: {len(topo['objects']['regions']['geometries'])} regions, simplify {pct}%, {len(s.encode()) / 1024:.0f} KB")
