"""Disputed areas with their owner as seen from different countries (Natural Earth 1:10m, public domain).
Run: python3 tools/build/pov.py   (needs tools/node_modules mapshaper)
Raw: https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_0_disputed_areas.geojson
Output: data/geopolitics/pov.json  {source, asOf, views:{code: ISO3}, areas: TopoJSON (object "areas", properties {name, o:{view: owner ISO3 or null}})}"""
import json, os, subprocess, tempfile, datetime
root = os.path.join(os.path.dirname(__file__), "..", "..")
raw = os.path.join(root, ".cache/ne/disputed.geojson")
src = json.load(open(raw))
FIX = {"SAH": "ESH", "KOS": "XKX", "CYN": "NCY", "PSX": "PSE", "SDS": "SSD"}
VIEW_ISO = {"US": "USA", "FR": "FRA", "RU": "RUS", "ES": "ESP", "CN": "CHN", "TW": "TWN", "IN": "IND", "NP": "NPL", "PK": "PAK",
            "DE": "DEU", "GB": "GBR", "BR": "BRA", "IL": "ISR", "PS": "PSE", "SA": "SAU", "EG": "EGY", "MA": "MAR", "PT": "PRT",
            "AR": "ARG", "JP": "JPN", "KO": "KOR", "VN": "VNM", "TR": "TUR", "ID": "IDN", "PL": "POL", "GR": "GRC", "IT": "ITA",
            "NL": "NLD", "SE": "SWE", "BD": "BGD", "UA": "UKR"}
def owner(code):
    if not isinstance(code, str) or code.startswith("B") and code[1:].isdigit() or code in ("KAS",): return None  # no owner / still disputed
    return FIX.get(code, code)
feats = []
for i, f in enumerate(src["features"]):
    p = f["properties"]
    o = {v: owner(p.get("ADM0_A3_" + v)) for v in VIEW_ISO}
    if len(set(o.values())) <= 1: continue  # every viewpoint agrees: nothing to show
    feats.append({"type": "Feature", "id": i, "geometry": f["geometry"], "properties": {"name": p["NAME"], "o": json.dumps(o)}})
with tempfile.TemporaryDirectory() as d:
    a = os.path.join(d, "areas.json"); b = os.path.join(d, "out.json")
    json.dump({"type": "FeatureCollection", "features": feats}, open(a, "w"))
    subprocess.run([os.path.join(root, "tools/node_modules/.bin/mapshaper"), a, "-simplify", "15%", "keep-shapes",
                    "-o", "format=topojson", "quantization=100000", b], check=True, capture_output=True)
    topo = json.load(open(b))
topo["objects"] = {"areas": list(topo["objects"].values())[0]}
for g in topo["objects"]["areas"]["geometries"]:
    g["properties"]["o"] = json.loads(g["properties"]["o"])
doc = {"source": "naturalearth", "asOf": "Natural Earth v5.1 disputed areas", "retrieved": datetime.date.today().isoformat(),
       "note": "Owner of each disputed area as shown on Natural Earth's point-of-view maps; null = shown as disputed / no owner.",
       "views": VIEW_ISO, "areas": topo}
out = os.path.join(root, "data/geopolitics/pov.json")
json.dump(doc, open(out, "w"), separators=(",", ":"))
print(out, os.path.getsize(out) // 1024, "KB,", len(feats), "areas:", ", ".join(sorted({f["properties"]["name"] for f in feats})))
