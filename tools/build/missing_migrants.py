"""Deaths and disappearances on migration routes, 2014-2024, from the IOM Missing Migrants Project (CC BY-IGO, via HDX
dataset 'iom-missing-migrants-project-data', published by IOM).
Fetch (≈5 MB):
  curl -sSL -A "Orbis-data-build/1.0" -o .cache/missing-migrants/mmp.csv \
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vTCSf2bkolxhbxDOdGDqWhaJIYyA0QTrG6t1M1mGOXrUwP5IUx7JmXjpo5grMUjXcMBeaZRG6USOZCU/pub?gid=1801809492&single=true&output=csv"
  (the CSV resource linked from https://data.humdata.org/dataset/iom-missing-migrants-project-data)
Run: python3 tools/build/missing_migrants.py
Output: data/events/missing-migrants.json, events [lon, lat, year, dead_and_missing]: incidents merged into
  0.5-degree cells per year (cell centre = mean position of its incidents, weighted by deaths), plus per-route totals."""
import os, csv, json, datetime, collections

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
src = os.path.join(root, ".cache/missing-migrants/mmp.csv")
out = os.path.join(root, "data/events/missing-migrants.json")
CELL = 0.5
num = lambda s: float(s.replace(",", "").strip() or 0)

cells = collections.defaultdict(lambda: [0.0, 0.0, 0.0])  # sum lon*w, sum lat*w, w
by_year, by_route, by_region = collections.Counter(), collections.Counter(), collections.Counter()
n_inc = 0
for r in csv.DictReader(open(src, encoding="utf-8")):
    if not r["reported_date"]: continue
    v = num(r["total_dead_and_missing"])
    if v <= 0: continue
    y = int(r["reported_date"][:4])
    if not 2014 <= y <= 2024: continue  # preserve this chapter's declared observation window
    lat, lon = (float(x) for x in r["location_coodinates"].split(","))
    n_inc += 1
    by_year[y] += v; by_route[r["migration_route"] or "(no route given)"] += v; by_region[r["region"]] += v
    k = (y, int((lon + 180) // CELL), int((lat + 90) // CELL))
    c = cells[k]; c[0] += lon * v; c[1] += lat * v; c[2] += v
ev = sorted(([round(c[0] / c[2], 2), round(c[1] / c[2], 2), k[0], int(c[2])] for k, c in cells.items()), key=lambda e: (e[2], -e[3]))
total = sum(by_year.values())
d = {
    "source": "iom-mmp", "asOf": "2024-12-31", "retrieved": datetime.date.today().isoformat(),
    "note": (f"IOM Missing Migrants Project, incidents 2014–2024 ({n_inc:,} incidents with at least one person dead or missing, "
             f"{int(total):,} people). Dead and missing combined; incidents merged into 0.5° cells per year. "
             "Recorded deaths are a minimum: many bodies are never found, especially in deserts and at sea."),
    "fields": ["lon", "lat", "t"], "tUnit": "year", "vLabel": "Dead and missing", "vUnits": "people",
    "byYear": {str(k): int(v) for k, v in sorted(by_year.items())},
    "byRoute": {k: int(v) for k, v in by_route.most_common(25)},
    "byRegion": {k: int(v) for k, v in by_region.most_common()},
    "events": ev,
}
json.dump(d, open(out, "w"), separators=(",", ":"), ensure_ascii=False)
print(len(ev), "cells;", int(total), "people;", os.path.getsize(out), "bytes")
print(d["byYear"]); print(list(d["byRoute"].items())[:12]); print(d["byRegion"])
