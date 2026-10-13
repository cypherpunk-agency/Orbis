"""Detailed country geometry (Natural Earth 1:50m, public domain) as TopoJSON with ids matching data/world.js.
Run: python3 tools/build/world.py   (needs: cd tools && npm install; raw file in .cache/ne/)
Download: https://naciscdn.org/naturalearth/50m/cultural/ne_50m_admin_0_countries.zip (or the GeoJSON from the
natural-earth-vector repository) into .cache/ne/ne_50m_admin_0_countries.geojson
Output: data/world50.json  objects.countries, each with id (ISO3-style) and properties {name, lx, ly} (label point)."""
import json, os, subprocess, tempfile
root = os.path.join(os.path.dirname(__file__), "..", "..")
src = json.load(open(os.path.join(root, ".cache/ne/ne_50m_admin_0_countries.geojson")))
# ADM0_A3 codes that differ from the ids used by data/world.js (and by ISO-coded datasets)
FIX = {"KOS": "XKX", "CYN": "NCY", "SAH": "ESH", "PSX": "PSE", "SDS": "SSD", "SOL": "SOL"}
feats = []
for f in src["features"]:
    p = f["properties"]
    iso = p.get("ISO_A3")  # not ISO_A3_EH: that one maps dependencies (e.g. Indian Ocean Ter.) onto their sovereign
    a3 = p["ADM0_A3"]
    fid = FIX.get(a3) or (iso if iso and iso != "-99" else a3)
    feats.append({"type": "Feature", "id": fid, "geometry": f["geometry"],
                  "properties": {"id": fid, "name": p["NAME"], "lx": round(p["LABEL_X"], 2), "ly": round(p["LABEL_Y"], 2)}})
ids = [f["id"] for f in feats]
dups = {i for i in ids if ids.count(i) > 1}
assert not dups, dups
with tempfile.TemporaryDirectory() as d:
    tmp = os.path.join(d, "countries.json")
    json.dump({"type": "FeatureCollection", "features": feats}, open(tmp, "w"))
    out = os.path.join(root, "data/world50.json")
    subprocess.run([os.path.join(root, "tools/node_modules/.bin/mapshaper"), tmp, "-o", "format=topojson",
                    "quantization=100000", "id-field=id", out], check=True)
print(out, os.path.getsize(out) // 1024, "KB,", len(feats), "countries")
