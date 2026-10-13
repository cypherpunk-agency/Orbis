"""Shared rivers for the "water-wars" story: Nile, Indus and Mekong systems from Natural Earth 1:10m rivers and lake
centerlines (public domain), heavily simplified; plus dam locations typed in (rounded public facts).
Fetch:  mkdir -p .cache/ne-rivers && curl -sSfL -o .cache/ne-rivers/r10.zip \
          https://naciscdn.org/naturalearth/10m/physical/ne_10m_rivers_lake_centerlines.zip && \
        (cd .cache/ne-rivers && unzip -o r10.zip)
Needs:  tools/node_modules (mapshaper)
Run:    python3 tools/build/rivers.py
Output: data/geopolitics/rivers.json  lines sets {nile, indusWest, indusEast, mekong}, points sets {nileDams, indusDams,
        mekongDams, chinaDams}"""
import os, json, subprocess, tempfile, datetime
root = os.path.join(os.path.dirname(__file__), "..", "..")
SHP = os.path.join(root, ".cache/ne-rivers/ne_10m_rivers_lake_centerlines.shp")
OUT = os.path.join(root, "data/geopolitics/rivers.json")
MS = os.path.join(root, "tools/node_modules/.bin/mapshaper")
# set -> {Natural Earth name: label shown on the map}
SETS = {
    "nile": {"Nile": "Nile", "Abay": "Blue Nile", "El Bahr el Azraq": "", "Victoria Nile": "", "Albert Nile": "",
             "Bahr el Jebel": "", "El Bahr el Abyad": "White Nile", "Atbara": "Atbara", "Sobat": ""},
    "indusWest": {"Indus": "Indus", "Jhelum": "Jhelum", "Chenab": "Chenab"},
    "indusEast": {"Ravi": "Ravi", "Beas": "", "Sutlej": "Sutlej"},
    "mekong": {"Mekong": "Mekong", "Lancang": "Lancang (upper Mekong)"},
}
BOXES = {"nile": (20, -5, 40, 33), "indusWest": (65, 22, 82, 37), "indusEast": (65, 22, 82, 37), "mekong": (93, 8, 110, 35)}
DAMS = {
    "nileDams": [
        {"name": "Grand Ethiopian Renaissance Dam", "at": [35.09, 11.21]},
        {"name": "Aswan High Dam", "at": [32.88, 23.97]},
    ],
    "indusDams": [
        {"name": "Tarbela (Pakistan)", "at": [72.69, 34.09]},
        {"name": "Kishanganga (India)", "at": [74.73, 34.65]},
        {"name": "Baglihar (India)", "at": [75.13, 33.15]},
        {"name": "Ratle (India, under construction)", "at": [75.66, 33.29]},
    ],
    "chinaDams": [
        {"name": "Xiaowan", "at": [100.09, 24.71]},
        {"name": "Nuozhadu", "at": [100.43, 22.65]},
        {"name": "Jinghong", "at": [100.77, 22.05]},
    ],
    "mekongDams": [
        {"name": "Xayaburi (Laos)", "at": [101.82, 19.25]},
        {"name": "Don Sahong (Laos)", "at": [105.83, 13.95]},
    ],
}
names = sorted({n for s in SETS.values() for n in s})
flt = "[" + ",".join('"%s"' % n for n in names) + "].indexOf(name)>=0"
with tempfile.TemporaryDirectory() as d:
    out = os.path.join(d, "r.json")
    subprocess.run([MS, SHP, "-filter", flt, "-filter-fields", "name", "-simplify", "interval=4000", "keep-shapes",
                    "-o", out, "format=geojson", "precision=0.01"], check=True, capture_output=True)
    gj = json.load(open(out))
lines = {k: [] for k in SETS}
for f in gj["features"]:
    n = f["properties"]["name"]; g = f["geometry"]
    parts = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
    for setk, m in SETS.items():
        if n not in m: continue
        x0, y0, x1, y1 = BOXES[setk]
        for p in parts:
            p = [[round(x, 2), round(y, 2)] for x, y in p]
            if len(p) < 2 or not all(x0 <= x <= x1 and y0 <= y <= y1 for x, y in p): continue
            lines[setk].append({"name": "", "label": m[n], "path": p})
# label only the longest piece of each river
for setk, items in lines.items():
    for lab in {i["label"] for i in items if i["label"]}:
        best = max((i for i in items if i["label"] == lab), key=lambda i: len(i["path"]))
        best["name"] = lab; best["labelAt"] = len(best["path"]) // (6 if lab.startswith("Lancang") else 2)
    for i in items: i.pop("label")
data = {"source": "naturalearth", "asOf": "2026-10-13", "retrieved": datetime.date.today().isoformat(),
        "note": "Rivers: Natural Earth 1:10m rivers and lake centerlines (public domain), only the Nile, Indus and Mekong "
                "systems, simplified to about 4 km. Dam positions typed in by Orbis, rounded.",
        "lines": lines, "points": DAMS}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(data, open(OUT, "w"), separators=(",", ":"))
print(OUT, os.path.getsize(OUT) // 1024, "KB;", {k: (len(v), sum(len(i["path"]) for i in v)) for k, v in lines.items()})
