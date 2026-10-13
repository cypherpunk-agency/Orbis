"""Earthquakes of magnitude >= 6.0, 1900-2025, from the USGS ANSS Comprehensive Catalog (ComCat). US public domain.
Source: USGS FDSN event web service https://earthquake.usgs.gov/fdsnws/event/1/
Fetch (decadal chunks, endtime exclusive):
  mkdir -p .cache/earthquakes && for d in $(seq 1900 10 2020); do e=$((d+10)); [ $e -gt 2026 ] && e=2026; \
    curl -sSf -o .cache/earthquakes/q_$d.csv "https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime=$d-01-01&endtime=$e-01-01&minmagnitude=6&orderby=time-asc&eventtype=earthquake"; done
Run:    python3 tools/build/events_earthquakes.py
Output: data/events/earthquakes.json  {source, asOf, retrieved, note, fields:[lon,lat,t,v], tUnit:"year", vLabel, vUnits,
        events:[[lon, lat, year, magnitude], ...]}"""
import os, csv, json, glob, datetime, collections
root = os.path.join(os.path.dirname(__file__), "..", "..")
CACHE = os.path.join(root, ".cache/earthquakes")
OUT = os.path.join(root, "data/events/earthquakes.json")
FIRST, LAST = 1900, 2025

files = sorted(glob.glob(os.path.join(CACHE, "q_*.csv")))
if not files:
    raise SystemExit("no downloads in .cache/earthquakes (see docstring)")
retrieved = datetime.date.fromtimestamp(min(os.path.getmtime(f) for f in files)).isoformat()

rows, seen = [], set()
for f in files:
    with open(f, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["type"] != "earthquake" or not r["mag"] or r["id"] in seen:
                continue
            seen.add(r["id"])
            year = int(r["time"][:4])
            mag = float(r["mag"])
            if not (FIRST <= year <= LAST) or mag < 6.0:
                continue
            rows.append({"time": r["time"], "year": year, "lon": float(r["longitude"]), "lat": float(r["latitude"]),
                         "mag": mag, "place": r["place"], "magType": r["magType"], "net": r["net"]})
rows.sort(key=lambda r: r["time"])

events = [[round(r["lon"], 2), round(r["lat"], 2), r["year"], round(r["mag"], 1)] for r in rows]
isc = sum(1 for r in rows if r["net"].startswith("iscgem"))
dec = collections.Counter(r["year"] // 10 * 10 for r in rows)
top = sorted(rows, key=lambda r: (-r["mag"], r["time"]))[:10]
top_txt = "; ".join(f'{r["time"][:10]} {r["place"]} M{r["mag"]:.1f}' for r in top)
dec_txt = ", ".join(f"{d}s{' (to ' + str(LAST) + ')' if d + 9 > LAST else ''} {dec[d]}" for d in sorted(dec))

note = (f"All events of type 'earthquake' with preferred magnitude >= 6.0 in ComCat, {FIRST}-{LAST} ({len(rows)} events). "
        "Magnitude is the catalogue's preferred magnitude (about 90% moment magnitude Mw; most pre-1973 events come from the ISC-GEM catalogue, the rest mostly from the USGS NEIC), "
        "rounded to 1 decimal; positions rounded to 0.01 deg. The early decades are less complete: fewer seismographs "
        "recorded fewer moderate (M6) events, so rising counts before about 1960 reflect better detection, not more earthquakes. "
        f"{isc} events ({isc * 100 // len(rows)}%, nearly all before 1973) are contributed to ComCat by the ISC-GEM Global "
        "Instrumental Earthquake Catalogue (International Seismological Centre and GEM Foundation, CC BY-SA 3.0); "
        "the rest are USGS or US regional network solutions (US public domain). "
        f"Ten largest: {top_txt}. Events per decade: {dec_txt}.")

out = {"source": "usgs-quakes", "asOf": f"USGS ComCat as queried {retrieved}", "retrieved": retrieved, "note": note,
       "fields": ["lon", "lat", "t", "v"], "tUnit": "year", "vLabel": "Magnitude", "vUnits": "magnitude (preferred, mostly Mw)",
       "events": events}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))

print(f"{OUT}: {len(events)} events, {os.path.getsize(OUT)/1024:.0f} KB")
print("per decade:", dec_txt)
print("ISC-GEM events:", isc, collections.Counter(r["net"] for r in rows).most_common(6))
print("by magnitude:", sorted(collections.Counter(int(e[3]) for e in events).items()))
print("top 10:")
for r in top:
    print(f'  {r["time"][:10]}  M{r["mag"]:.1f} {r["magType"]:4}  {r["place"]}')
