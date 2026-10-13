"""South China Sea: schematic claim lines and features, drawn by Orbis (own work, source id "orbis-schematic").
- 200-nautical-mile lines: each coastal state's coastline (Natural Earth 1:50m, public domain) buffered by 370.4 km
  with mapshaper, then clipped to the sea and thinned. These are the outer limits a coastline could generate from
  the mainland and large islands only. They are NOT agreed boundaries: real EEZ limits stop at median lines or
  agreed boundaries, and baselines differ from the Natural Earth coast. Schematic.
- Nine-dash line: China has never published coordinates for it. The nine dashes below were traced by hand,
  approximately, from the map China attached to its notes verbale CML/17/2009 and CML/18/2009 to the UN
  (7 May 2009). Approximate to within tens of kilometres.
- Features: positions of reefs and islands (rounded, public geographic facts).
Needs: .cache/ne/ne_50m_admin_0_countries.geojson (see tools/build/world.py) and tools/node_modules (mapshaper).
Run:    python3 tools/build/south_china_sea.py
Output: data/geopolitics/south-china-sea.json  {lines: {nineDash, limits200}, points: {...}}"""
import os, json, math, subprocess, tempfile, datetime
root = os.path.join(os.path.dirname(__file__), "..", "..")
NE = os.path.join(root, ".cache/ne/ne_50m_admin_0_countries.geojson")
OUT = os.path.join(root, "data/geopolitics/south-china-sea.json")
MS = os.path.join(root, "tools/node_modules/.bin/mapshaper")
BOX = (103.0, 0.5, 123.0, 23.5)  # lon/lat window of the sea
STATES = {"VNM": ("Vietnam", "c4"), "PHL": ("Philippines", "c1"), "MYS": ("Malaysia", "c5"), "BRN": ("Brunei", "c3"),
          "IDN": ("Indonesia (Natuna)", "muted")}

# approximate dash end points [lon, lat], traced from the 2009 map (west to east, south then north)
NINE_DASH = [
    [[109.6, 16.6], [109.4, 15.0]],   # 1 east of central Vietnam
    [[109.9, 12.4], [109.6, 10.9]],   # 2 off southern Vietnam
    [[109.5, 7.9], [110.4, 6.5]],     # 3 north-east of the Natuna Islands
    [[111.9, 3.6], [113.2, 3.6]],     # 4 south of James Shoal, off Sarawak
    [[114.6, 5.9], [115.5, 7.2]],     # 5 off Brunei and Sabah
    [[117.0, 8.9], [117.9, 10.3]],    # 6 west of Palawan
    [[119.0, 13.1], [119.0, 14.7]],   # 7 west of Mindoro and Luzon
    [[119.5, 17.2], [119.9, 18.7]],   # 8 north-west of Luzon
    [[120.8, 20.5], [121.6, 21.6]],   # 9 Bashi Channel, between Luzon and Taiwan
]
FEATURES = {
    "groups": [
        {"name": "Paracel Islands", "at": [112.0, 16.5]},
        {"name": "Spratly Islands", "at": [114.3, 9.8]},
        {"name": "Scarborough Shoal", "at": [117.76, 15.15]},
    ],
    "built": [  # the seven Spratly features China built up 2013-2016
        {"name": "Fiery Cross Reef", "at": [112.89, 9.55]},
        {"name": "Subi Reef", "at": [114.08, 10.92]},
        {"name": "Mischief Reef", "at": [115.53, 9.90]},
        {"name": "Johnson South Reef", "at": [114.28, 9.72]},
        {"name": "Gaven Reefs", "at": [114.23, 10.21]},
        {"name": "Hughes Reef", "at": [114.50, 9.92]},
        {"name": "Cuarteron Reef", "at": [112.86, 8.86]},
    ],
    "flashpoints": [
        {"name": "Woody Island (Paracels)", "at": [112.33, 16.83]},
        {"name": "Scarborough Shoal", "at": [117.76, 15.15]},
        {"name": "Second Thomas Shoal", "at": [115.87, 9.73]},
    ],
}
LABEL_NEAR = {"VNM": (112.5, 14.0), "PHL": (117.6, 19.8), "MYS": (108.0, 7.2), "BRN": (113.6, 7.2), "IDN": (105.0, 5.6)}

def hav(a, b):
    la1, la2 = math.radians(a[1]), math.radians(b[1]); dl = math.radians(b[0] - a[0])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))

def rings_of(g):
    if g["type"] == "Polygon": return g["coordinates"]
    return [r for p in g["coordinates"] for r in p]

def inside(pt, rings):  # even-odd rule over all rings
    x, y, c = pt[0], pt[1], False
    for r in rings:
        for i in range(len(r) - 1):
            (x1, y1), (x2, y2) = r[i][:2], r[i + 1][:2]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                c = not c
    return c

ne = json.load(open(NE))
land = [f for f in ne["features"] if f["geometry"]]
land_polys = []  # (bbox, rings) of every polygon near the sea
for f in land:
    g = f["geometry"]
    for poly in ([g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]):
        xs = [p[0] for p in poly[0]]; ys = [p[1] for p in poly[0]]
        bb = (min(xs), min(ys), max(xs), max(ys))
        if bb[2] < 95 or bb[0] > 130 or bb[3] < -5 or bb[1] > 30: continue
        land_polys.append((bb, poly))
def on_land(p):
    return any(bb[0] <= p[0] <= bb[2] and bb[1] <= p[1] <= bb[3] and inside(p, poly) for bb, poly in land_polys)

with tempfile.TemporaryDirectory() as d:
    out = os.path.join(d, "buf.json")
    flt = "[" + ",".join('"%s"' % k for k in STATES) + "].indexOf(ADM0_A3)>=0"
    subprocess.run([MS, NE, "-filter", flt, "-clip", "bbox=95,-8,130,30", "-each", "iso=ADM0_A3",
                    "-filter-fields", "iso", "-buffer", "370.4", "units=km", "-o", out, "format=geojson"],
                   check=True, capture_output=True)
    buf = json.load(open(out))

coast = {}
for f in land:
    a3 = f["properties"]["ADM0_A3"]
    if a3 in STATES:
        coast[a3] = [p for r in rings_of(f["geometry"]) for p in r[::3] if 95 < p[0] < 130 and -8 < p[1] < 30]

limits = []
for f in buf["features"]:
    iso = f["properties"]["iso"]; name, color = STATES[iso]
    dists = []
    for ring in rings_of(f["geometry"]):
        seg = []
        for i, p in enumerate(ring):
            ok = (BOX[0] <= p[0] <= BOX[2] and BOX[1] <= p[1] <= BOX[3] and not on_land(p)
                  and not (p[0] > 117.8 and p[1] < 11.8)        # Sulu and Celebes seas: outside the story
                  and not (iso == "IDN" and p[0] > 112))         # Indonesia: only the Natuna sector
            if ok:
                seg.append([round(p[0], 2), round(p[1], 2)])
                if i % 20 == 0: dists.append(min(hav(p, c) for c in coast[iso]))
            if (not ok or i == len(ring) - 1) and seg:
                # thin to a vertex every ~15 km
                thin = [seg[0]]
                for q in seg[1:]:
                    if hav(thin[-1], q) > 15: thin.append(q)
                if thin[-1] != seg[-1]: thin.append(seg[-1])
                if len(thin) > 6: limits.append({"name": "", "iso": iso, "color": color, "path": thin})
                seg = []
    if dists:
        print(iso, "200-nm line: distance to coast min %.0f / max %.0f km (target 370)" % (min(dists), max(dists)))
# a ring's first and last pieces meet at the ring's start point: join them
for iso in STATES:
    pcs = [l for l in limits if l["iso"] == iso]
    for a in pcs:
        for b in pcs:
            if a is not b and a in limits and b in limits and a["path"][-1] == b["path"][0]:
                a["path"] += b["path"][1:]; limits.remove(b)
# label the longest piece of each state
for iso, (name, color) in STATES.items():
    pieces = [l for l in limits if l["iso"] == iso]
    if pieces:
        best = max(pieces, key=lambda l: len(l["path"])); best["name"] = name + ", 200 nm"
        t = LABEL_NEAR[iso]
        best["labelAt"] = min(range(len(best["path"])), key=lambda i: hav(best["path"][i], t))
per_state = {}
for l in limits: per_state.setdefault("limits" + l.pop("iso"), []).append(l)
dash = [{"name": "China's nine-dash line (approximate)" if i == 0 else "", "path": p, "labelAt": 0} for i, p in enumerate(NINE_DASH)]
data = {
    "source": "orbis-schematic", "asOf": "2026-10-13", "retrieved": datetime.date.today().isoformat(),
    "note": "Drawn by Orbis, schematic. Nine-dash line: approximate, traced by hand from the map attached to China's notes "
            "verbale CML/17/2009 and CML/18/2009 to the UN; China has published no coordinates. 200-nm lines: Natural Earth "
            "1:50m coastlines buffered by 370.4 km (mainland and large islands only), not agreed EEZ boundaries. "
            "Feature positions rounded.",
    "lines": {"nineDash": dash, "limits200": limits, **per_state},
    "points": FEATURES,
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(data, open(OUT, "w"), separators=(",", ":"))
print(OUT, os.path.getsize(OUT) // 1024, "KB,", len(limits), "200-nm pieces")
