"""Largest populated places (Natural Earth 1:10m populated places, public domain) for 'your city' and labels.
Run: python3 tools/build/places.py
Raw: https://naciscdn.org/naturalearth/10m/cultural/ne_10m_populated_places_simple.zip -> .cache/ne/ne_10m_populated_places_simple.geojson
Output: data/geo/places.json  {source, asOf, fields:[name, iso3, lon, lat, pop, capital], places:[...]}"""
import json, os, datetime
root = os.path.join(os.path.dirname(__file__), "..", "..")
src = json.load(open(os.path.join(root, ".cache/ne/ne_10m_populated_places_simple.geojson")))
rows = []
for f in src["features"]:
    p = f["properties"]
    pop = p.get("pop_max") or 0
    iso = p.get("adm0_a3") or ""
    fix = {"KOS": "XKX", "SDS": "SSD", "PSX": "PSE", "SAH": "ESH", "CYN": "NCY"}
    rows.append([p["name"], fix.get(iso, iso), round(p["longitude"], 3), round(p["latitude"], 3), int(pop), 1 if p.get("adm0cap") else 0])
caps = [r for r in rows if r[5]]
big = sorted([r for r in rows if not r[5]], key=lambda r: -r[4])[:1500 - len(caps)]
out = sorted(caps + big, key=lambda r: -r[4])
doc = {"source": "naturalearth", "asOf": "Natural Earth v5.1", "retrieved": datetime.date.today().isoformat(),
       "fields": ["name", "iso3", "lon", "lat", "pop", "capital"], "places": out}
p = os.path.join(root, "data/geo/places.json")
json.dump(doc, open(p, "w"), separators=(",", ":"), ensure_ascii=False)
print(p, os.path.getsize(p) // 1024, "KB,", len(out), "places,", len(caps), "capitals")
