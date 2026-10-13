"""Official clock time versus sun time, by country, plus the International Date Line.
Inputs (all public domain):
  - IANA time zone database (tz), as installed in /usr/share/zoneinfo (zone.tab + compiled zones; version printed below).
    Each country's official STANDARD offset is taken from its first zone in zone.tab (the main one, e.g. Europe/Madrid
    for Spain, not the Canaries), as the lower of its UTC offsets on 15 January and 15 July 2026 (i.e. without summer time).
  - Natural Earth: country label points from data/world50.json give each country's "middle" longitude; solar (geographic)
    offset = longitude / 15 hours. International Date Line from ne_50m_geographic_lines (public domain):
      mkdir -p .cache/tz && curl -L -o .cache/tz/geolines.json \
        https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_geographic_lines.geojson
  - ISO2 -> ISO3 codes from the UN WPP 2024 file already in .cache/wpp (see wpp.py).
Run: python3 tools/build/timezones.py
Output: data/statistics/timezones.json (sets: clock = ahead/behind/right/several; offset = official standard offset label)
        data/statistics/dateline.json   (lines: dateline)"""
import os, csv, gzip, json, datetime
from zoneinfo import ZoneInfo
root = os.path.join(os.path.dirname(__file__), "..", "..")
TZDIR = "/usr/share/zoneinfo"
AHEAD = 0.75   # hours; clocks at least this far ahead of the sun at the country's middle longitude
SLIGHT = 0.25  # hours; "a little ahead" (or behind) from here
# Countries spanning several official zones on their main territory: not classed as a whole.
SEVERAL = {"USA", "CAN", "RUS", "BRA", "AUS", "MEX", "IDN", "MNG", "COD", "KIR", "FSM", "GRL", "PYF"}
EXTRA = {"XKX": "Europe/Belgrade", "SOL": "Africa/Mogadishu", "NCY": "Asia/Famagusta"}   # not in zone.tab
version = open(os.path.join(TZDIR, "tzdata.zi")).readline().strip().replace("# version ", "")
iso3 = {}
with gzip.open(os.path.join(root, ".cache/wpp/WPP2024_Demographic_Indicators_Medium.csv.gz"), "rt", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        if r["ISO2_code"] and r["ISO3_code"]: iso3[r["ISO2_code"]] = r["ISO3_code"]
iso3.update({"TW": "TWN", "XK": "XKX"})
first = {}
for line in open(os.path.join(TZDIR, "zone.tab")):
    if line.startswith("#"): continue
    cc, coord, zone = line.split("\t")[:3]
    if cc in iso3 and iso3[cc] not in first: first[iso3[cc]] = zone.strip()
first.update(EXTRA)
def std_offset(zone):
    z = ZoneInfo(zone)
    return min(datetime.datetime(2026, m, 15, 12, tzinfo=z).utcoffset().total_seconds() / 3600 for m in (1, 7))
world = json.load(open(os.path.join(root, "data/world50.json")))
lon = {g["id"]: g["properties"]["lx"] for g in world["objects"]["countries"]["geometries"] if g["properties"].get("lx") is not None}
def label(h):
    s = "+" if h >= 0 else "−"
    h = abs(h); m = round((h - int(h)) * 60)
    return f"UTC{s}{int(h)}" + (f":{m:02d}" if m else "")
clock, offset, diff = {}, {}, {}
for c, zone in sorted(first.items()):
    if c not in lon: continue
    off = std_offset(zone)
    offset[c] = label(off)
    if c in SEVERAL:
        clock[c] = "several"; continue
    d = off - lon[c] / 15
    if d > 12: d -= 24
    if d < -12: d += 24
    diff[c] = round(d, 2)
    clock[c] = "ahead" if d >= AHEAD else "little" if d >= SLIGHT else "behind" if d <= -SLIGHT else "right"
retrieved = datetime.date.today().isoformat()
out = {
    "source": "iana-tz", "asOf": "2026", "retrieved": retrieved,
    "note": f"Official standard time (no summer time) from the IANA tz database {version}, main zone of each country. "
            "Sun time from each country's middle longitude (Natural Earth label point) divided by 15 degrees per hour. "
            f"'Ahead' means at least 45 minutes, 'a little ahead' 15-45 minutes, 'behind' at least 15 minutes behind. Countries with several zones on their main territory are not classed.",
    "sets": {
        "clock": {"label": "Clock versus sun", "values": clock,
                  "labels": {"ahead": "Clocks 45 min or more ahead of the sun", "little": "15 to 45 min ahead",
                             "right": "Within 15 min of sun time", "behind": "15 min or more behind the sun", "several": "Several time zones"}},
        "offset": {"label": "Official standard time", "values": offset},
    },
    "hoursAheadOfSun": diff,
}
json.dump(out, open(os.path.join(root, "data/statistics/timezones.json"), "w"), separators=(",", ":"), ensure_ascii=False)
# International Date Line, collinear points dropped
gl = json.load(open(os.path.join(root, ".cache/tz/geolines.json")))
idl = next(f for f in gl["features"] if f["properties"].get("name") == "International Date Line")
def simplify(pts):
    pts = [p for i, p in enumerate(pts) if i == 0 or p != pts[i - 1]]
    keep = [pts[0]]
    for a, b, c in zip(pts, pts[1:], pts[2:]):
        cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if abs(cross) > 0.002: keep.append(b)
    keep.append(pts[-1])
    return [[round(x, 2), round(y, 2)] for x, y in keep]
parts = [simplify(p) for p in idl["geometry"]["coordinates"]]
dl = {"source": "naturalearth", "asOf": "2018", "retrieved": retrieved,
      "note": "International Date Line from Natural Earth 1:50m geographic lines (public domain), simplified.",
      "lines": {"dateline": [{"name": "International Date Line" if i == 1 else "", "status": "operating", "path": p} for i, p in enumerate(parts)]}}
json.dump(dl, open(os.path.join(root, "data/statistics/dateline.json"), "w"), separators=(",", ":"))
from collections import Counter
print("tz", version, Counter(clock.values()), {k: diff.get(k) for k in ("CHN", "ESP", "FRA", "IND", "NPL", "ARG", "ISL", "GBR", "DEU", "PRT", "BEL", "NLD", "IRL", "MAR", "VEN", "CHL")})
print([(k, v) for k, v in sorted(diff.items(), key=lambda kv: -kv[1])][:25])
print([(k, v) for k, v in sorted(diff.items(), key=lambda kv: kv[1])][:15])
