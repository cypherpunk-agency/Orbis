# Merge preservation: origin/main tools/build/us_history.py; standalone alternate-data builder.
# Writes only the original remote dataset paths documented below; no story JSON is written.
# Finite-roadmap data are generated separately by us_history.py and remain in distinct paths.
#!/usr/bin/env python3
"""The United States series: states and territories over time, acquisitions, statehood, the Civil War split,
Indigenous land cessions and presidential elections -> data/history/us-*.json

Sources (all downloaded into .cache/us_*/, never committed):
  - Newberry Library, Atlas of Historical County Boundaries (AHCB), "US Historical States & Territories (1783-2000)",
    generalized .01 degree shapefile US_AtlasHCB_StateTerr_Gen01.zip. Terms (publications.newberry.org/ahcb/download):
    "readily available to download ... and reused for any lawful purpose, commercial or non-commercial, without licensing
    or permission fees". 220 records, one per state/territory version, with START_DATE / END_DATE (inclusive).
  - USDA Forest Service, "Tribal Land Cessions in the United States" (Royce cessions, 2018; Office of Tribal Relations,
    NPS NAGPRA, EPA and Claudio Saunt). GeoJSON from data-usfs.hub.arcgis.com item e4e788be8cfc4d1f8ff280a81ffaa69c,
    licence CC BY 4.0 (catalog.data.gov distribution "license": creativecommons.org/licenses/by/4.0/).
  - MIT Election Data and Science Lab, "U.S. President 1976-2024", Harvard Dataverse doi:10.7910/DVN/42MVDX, V10, CC0 1.0.

Run: python3 tools/build/us_history_alternate.py      (needs tools/node_modules mapshaper, Python shapely >= 2)
Outputs (each <= ~300 KB, TopoJSON object "shapes", properties name/from/to/group/label/note as in docs/STORY-FORMAT.md):
  data/history/us-states.json        every state and territory version 1783-2000, grouped by status
  data/history/us-acquisitions.json  land added to the United States, one shape per acquisition, + cards
  data/history/us-union.json         states by date of admission, and the Union/Confederacy split 1860-1870, + cards
  data/history/us-cessions.json      Royce land cessions 1784-1894, grouped by period, + cards
  data/history/us-elections.json     presidential winner by state 1976-2024 (shapes per state and election)
Dates: Newberry and Royce dates are Gregorian (all after 1752 in the British colonies). `to` is exclusive: Newberry's
inclusive END_DATE + 1 day; END_DATE 2000-12-31 (the atlas's end) means "still valid" (null).
"""
import csv, datetime, json, os, subprocess, sys, urllib.request, zipfile
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from shapely import make_valid

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MS = os.path.join(ROOT, "tools/node_modules/.bin/mapshaper")
OUT = os.path.join(ROOT, "data", "history")
TODAY = datetime.date.today().isoformat()
UA = {"User-Agent": "Orbis-data-build/1.0"}
os.makedirs(OUT, exist_ok=True)


def fetch(url, path):
    if os.path.exists(path): return path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
        open(path + ".part", "wb").write(r.read())
    os.rename(path + ".part", path)
    return path


def ms(*args):
    r = subprocess.run([MS, *args], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr)
    return r.stderr


def nextday(n):
    d = datetime.date(n // 10000, n // 100 % 100, n % 100) + datetime.timedelta(days=1)
    return d.year * 10000 + d.month * 100 + d.day


def fixgeom(g):
    g = make_valid(g)
    if g.geom_type == "GeometryCollection":
        g = unary_union([p for p in g.geoms if p.geom_type in ("Polygon", "MultiPolygon")])
    return g


def write_topo(name, feats, meta, pcts=(12, 8, 5, 3.5, 2.5, 1.8, 1.2), max_kb=290, quant=1e5, slivers=True):
    """feats: list of (shapely geometry, properties). Writes data/history/<name>.json with an inline topology,
    simplified (shared arcs, keep-shapes) until the whole file is <= max_kb. pcts: Visvalingam percentages, or
    numbers >= 100 = a distance interval in metres (better for large overlapping polygons, which percentage
    simplification can turn into triangles)."""
    cache = os.path.join(ROOT, ".cache", "us_build"); os.makedirs(cache, exist_ok=True)
    gj = os.path.join(cache, name + ".geojson"); tj = os.path.join(cache, name + ".topo.json")
    fc = {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": mapping(g), "properties": p} for g, p in feats]}
    json.dump(fc, open(gj, "w"))
    for pct in pcts:
        simp = [f"interval={pct}"] if pct >= 100 else [f"{pct}%", "visvalingam"]
        ms("-i", gj, "-simplify", *simp, "keep-shapes", *(["-filter-slivers"] if slivers else []),
           "-rename-layers", "shapes", "-o", tj, "format=topojson", f"quantization={int(quant)}")
        topo = json.load(open(tj))
        doc = dict(meta); doc["topology"] = topo
        s = json.dumps(doc, ensure_ascii=False, separators=(",", ":"))
        if len(s) / 1024 <= max_kb: break
    open(os.path.join(OUT, name + ".json"), "w").write(s)
    print(f"{name}.json: {len(s)/1024:.0f} KB, simplify {pct}{' m' if pct >= 100 else '%'}, {len(feats)} shapes")


# ---------------------------------------------------------------- Newberry states and territories
NB = os.path.join(ROOT, ".cache", "us_states")
zp = fetch("https://publications.newberry.org/ahcb/downloads/gis/US_AtlasHCB_StateTerr_Gen01.zip",
           os.path.join(NB, "US_AtlasHCB_StateTerr_Gen01.zip"))
nbgj = os.path.join(NB, "statesterr.geojson")
if not os.path.exists(nbgj):
    zipfile.ZipFile(zp).extractall(os.path.join(NB, "Gen01"))
    shp = [os.path.join(d, f) for d, _, fs in os.walk(os.path.join(NB, "Gen01")) for f in fs if f.endswith(".shp")][0]
    ms("-i", shp, "encoding=utf8", "-o", nbgj, "format=geojson", "precision=0.00001")
NBF = []
for f in json.load(open(nbgj))["features"]:
    p = f["properties"]
    if p["ID"] == "ds_deseret": continue  # proposed state of Deseret: never recognised, overlaps Utah Territory
    NBF.append({"id": p["ID"], "name": p["FULL_NAME"], "short": p["NAME"], "type": p["TERR_TYPE"], "start": int(p["START_N"]),
                "end": int(p["END_N"]), "geom": fixgeom(shape(f["geometry"])), "change": p["CHANGE"]})
OPEN_END = 20001231
to_of = lambda r: None if r["end"] >= OPEN_END else nextday(r["end"])
valid = lambda r, d: r["start"] <= d <= r["end"]
abbr = lambda r: r["id"].split("_")[0].upper()

GROUP = {"State": "state", "District of Columbia": "state", "Territory": "territory", "Unorganized Territory": "unorg"}
OTHER = {"or_country": "claim", "ub_area": "claim", "tx_republic": "independent", "vt_republic": "independent"}
TYPE_NOTE = {"state": "State", "territory": "Organized territory", "unorg": "Unorganized federal land",
             "claim": "Claimed, boundary not settled", "independent": "Independent republic, not part of the US"}


def label_of(r):
    n = r["short"]
    for a, b in ((" Territory", " Terr."), (" Unorg. FT", ""), (" Unorganized Federal Territory", "")):
        n = n.replace(a, b)
    return n


feats = []
for r in NBF:
    g = OTHER.get(r["id"]) or GROUP[r["type"]]
    p = {"name": r["name"], "from": r["start"], "to": to_of(r), "group": g, "label": label_of(r), "note": TYPE_NOTE[g]}
    if g == "claim": p["uncertain"] = True
    feats.append((r["geom"], p))
write_topo("us-states", feats, {
    "source": "newberry-ahcb", "asOf": "AHCB US Historical States & Territories, generalized .01 degree", "retrieved": TODAY,
    "note": "Newberry Library, Atlas of Historical County Boundaries: one shape per version of each state and territory, "
            "3 Sep 1783 to 2000 (the atlas ends in 2000; later versions stay open). Groups follow the atlas's TERR_TYPE: "
            "states (and the District of Columbia), organized territories, unorganized federal territory and land not yet "
            "organized (purchases, cessions); 'claimed' = the Oregon Country (joint occupation with Britain 1818-1846) and "
            "the unsettled boundary north of the Louisiana Purchase; 'independent' = the Vermont Republic and the Republic "
            "of Texas, shown for context. The proposed State of Deseret (1849-1851) is left out. Simplified by Orbis.",
    "groups": {"state": {"label": "States", "color": "c1"}, "territory": {"label": "Organized territories", "color": "c4"},
               "unorg": {"label": "Unorganized federal land", "color": "c3"},
               "claim": {"label": "Claimed, not settled", "color": "c5"},
               "independent": {"label": "Independent republics", "color": "muted"}}})

# ---------------------------------------------------------------- acquisitions: land that became part of the US, by date
US_GROUPS = ("state", "territory", "unorg")
grp = lambda r: OTHER.get(r["id"]) or GROUP[r["type"]]
inside = [r for r in NBF if grp(r) in US_GROUPS]
dates = sorted({r["start"] for r in inside})
prev = None; gains = []
for d in dates:
    ext = unary_union([r["geom"] for r in inside if valid(r, d)]).buffer(0)
    if prev is None: gains.append((d, ext))
    else:
        g = ext.difference(prev.buffer(0.02))  # ignore boundary re-surveys narrower than ~2 km
        g = unary_union([p for p in (g.geoms if hasattr(g, "geoms") else [g]) if p.area > 0.05])  # > ~500 km2
        if not g.is_empty: gains.append((d, g))
    prev = ext
for d, g in gains: print("gain", d, round(g.area, 2))

ACQ = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "us_history_events.json")))
# clip each acquisition to the country as it is today: land given up later (e.g. the part of the Louisiana Purchase
# south and west of the 1819 Adams-Onis line, later re-acquired with Texas) is counted once, with its final acquisition
final = unary_union([r["geom"] for r in inside if valid(r, OPEN_END)]).buffer(0)
feats = []; later = None
geoms = {}
for a in reversed(ACQ["acquisitions"]):  # land gained twice (lost in 1819, regained 1845-1848) belongs to the later step
    parts = [g for d, g in gains if a["dates"][0] <= d <= a["dates"][1]]
    if not parts: raise SystemExit("no gain for " + a["name"])
    g = unary_union(parts).intersection(final.buffer(0.02))
    if later is not None: g = g.difference(later)
    later = g if later is None else unary_union([later, g])
    geoms[a["name"]] = g
for a in ACQ["acquisitions"]:
    g = geoms[a["name"]]
    feats.append((g, {"name": a["name"], "from": a["from"], "to": None, "group": a["how"], "label": a["label"], "note": a["note"]}))
used = [(d, g) for d, g in gains if any(a["dates"][0] <= d <= a["dates"][1] for a in ACQ["acquisitions"])]
left = [(d, round(g.area, 2)) for d, g in gains if (d, g) not in used]
print("gains not assigned to an acquisition:", left)
meta = {"source": "newberry-ahcb", "asOf": "AHCB US Historical States & Territories", "retrieved": TODAY,
        "note": "Each shape is the land that first appears in the Newberry atlas's states and territories on the dates "
                "of one acquisition (union of all versions valid on that date, minus the union the day before; slivers "
                "under ~500 km2 and boundary re-surveys narrower than ~2 km dropped). Claims (Oregon Country before 1846) "
                "and the independent Republic of Texas are not counted until they joined. Card facts: see each card's source.",
        "groups": ACQ["acq_groups"], "kinds": ACQ["acq_kinds"], "items": ACQ["acq_cards"]}
write_topo("us-acquisitions", feats, meta, pcts=(20, 12, 8, 5))

# ---------------------------------------------------------------- statehood order and the Civil War split
ADMIT = ACQ["admission"]  # postal code -> yyyymmdd (Constitution ratified for the original 13; admission for the rest)
now = {}
for r in NBF:
    if r["type"] in ("State", "District of Columbia") and r["end"] >= OPEN_END: now[abbr(r)] = r
ERA = [(17900529, "orig"), (18210810, "e1821"), (18590214, "e1859"), (18961231, "e1896"), (19591231, "e1959")]
feats = []
for code, r in sorted(now.items()):
    if code == "DC": continue
    d = ADMIT[code]; era = next(e for lim, e in ERA if d <= lim)
    feats.append((r["geom"], {"name": r["short"], "from": d, "to": None, "group": era, "label": code,
                              "note": "Joined the Union " + datetime.date(d // 10000, d // 100 % 100, d % 100).strftime("%-d %b %Y")}))
# Civil War: every state/territory version valid between Nov 1860 and Jul 1870, split at secession and readmission
CW = ACQ["civil_war"]; W0, W1 = 18601106, 18700716
for r in NBF:
    if r["end"] < W0 or r["start"] > W1: continue
    g0 = grp(r)
    if g0 not in US_GROUPS: continue
    code = abbr(r); a, b = max(r["start"], W0), min(nextday(r["end"]), W1)
    if code == "DC": continue  # federal district, not a state
    if g0 != "state": cuts = [(a, b, "cw_terr")]
    elif code in CW["seceded"]:
        s, back = CW["seceded"][code], CW["readmitted"][code]
        cuts = [(a, min(b, s), "cw_slave"), (max(a, s), min(b, back), "cw_csa"), (max(a, back), b, "cw_back")]
    elif code in CW["slave_union"]: cuts = [(a, min(b, CW["abolition"]), "cw_slave"), (max(a, CW["abolition"]), b, "cw_union")]
    else: cuts = [(a, min(b, CW["abolition"]), "cw_free"), (max(a, CW["abolition"]), b, "cw_union")]
    for x, y, gname in cuts:
        if x >= y: continue
        feats.append((r["geom"], {"name": r["name"], "from": x, "to": y, "group": gname, "label": label_of(r) if g0 != "state" else code,
                                  "note": CW["notes"].get(gname, "")}))
meta = {"source": "newberry-ahcb", "asOf": "AHCB US Historical States & Territories", "retrieved": TODAY,
        "note": "Two shape sets in one topology. Statehood (groups orig, e1821, e1859, e1896, e1959): today's state "
                "shapes, valid from the day each state ratified the Constitution (the original 13) or was admitted "
                "(Newberry START_DATE of the first state version; checked against the US Statutes dates). Civil War "
                "(groups cw_*): every state and territory version valid 6 Nov 1860 - 15 Jul 1870, split at the date of each "
                "state's ordinance of secession and of its readmission to representation in Congress. Dates in the "
                "build script's events file (tools/build/us_history_events.json) with their sources.",
        "groups": ACQ["union_groups"], "kinds": ACQ["union_kinds"], "items": ACQ["union_cards"]}
write_topo("us-union", feats, meta, pcts=(10, 6, 4, 2.5, 1.8, 1.2))

# ---------------------------------------------------------------- Royce land cessions
RC = os.path.join(ROOT, ".cache", "us_royce")
rp = fetch("https://data-usfs.hub.arcgis.com/api/download/v1/items/e4e788be8cfc4d1f8ff280a81ffaa69c/geojson?layers=0",
           os.path.join(RC, "royce.geojson"))
P = "edws_usaBdyPol_TribalCededLands"
PERIOD = [(18291231, "r1", "1784-1829"), (18491231, "r2", "1830-1849"), (18691231, "r3", "1850-1869"), (18941231, "r4", "1870-1894")]
feats = []; skipped = 0; byp = {}
for f in json.load(open(rp))["features"]:
    p = f["properties"]; ds = p.get(P + "Tablecessdate1")
    if not ds or not f["geometry"]: skipped += 1; continue
    d = int(ds[:10].replace("-", ""))
    lim, g, lab = next(x for x in PERIOD if d <= x[0])
    tribe = (p.get(P + "Tableschdtrb") or "").strip()
    geom = fixgeom(shape(f["geometry"]))
    if geom.is_empty: skipped += 1; continue
    byp[g] = byp.get(g, 0) + 1
    feats.append((geom, {"name": tribe or "Royce cession " + str(p.get(P + "cessnum")), "from": d, "to": None, "group": g,
                         "note": "Royce no. " + str(p.get(P + "cessnum"))}))
print("royce: kept", len(feats), "skipped", skipped, byp)
# area ceded per period (equal-area km2, overlaps counted once) for the story text
import math
from shapely.ops import transform
def albers(g):
    # Albers equal-area conic for the conterminous US (standard parallels 29.5, 45.5; centre 23N 96W)
    p1, p2, l0, f0, R = map(math.radians, (29.5, 45.5, -96, 23, 0)); R = 6371.0
    n = (math.sin(p1) + math.sin(p2)) / 2; C = math.cos(p1) ** 2 + 2 * n * math.sin(p1); r0 = R * math.sqrt(C - 2 * n * math.sin(f0)) / n
    def fw(x, y, z=None):
        import numpy as np
        lo, la = np.radians(x), np.radians(y); r = R * np.sqrt(C - 2 * n * np.sin(la)) / n; th = n * (lo - l0)
        return r * np.sin(th), r0 - r * np.cos(th)
    return transform(fw, g)
cum = None
for lim, g, lab in PERIOD:
    u = unary_union([geom for geom, p in feats if p["from"] <= lim])
    print("royce cumulative to", lab, round(albers(u).area / 1e6, 2), "million km2")
print("conterminous US (Newberry 2000 states, km2):",
      round(albers(unary_union([r["geom"] for c, r in now.items() if c not in ("AK", "HI")])).area / 1e6, 2), "million")
meta = {"source": "usfs-royce", "asOf": "USFS Tribal Land Cessions in the United States (2018)", "retrieved": TODAY,
        "note": "Land cessions from Charles C. Royce's schedule 'Indian Land Cessions in the United States' (18th Annual "
                "Report of the Bureau of American Ethnology, 1899), digitised by the US Forest Service with the National Park "
                "Service, the EPA and Claudio Saunt (2018). Each shape is one Royce area, dated by its first cession date "
                "(treaty, act of Congress or executive order); name = the nation or band as Royce's schedule names it. "
                "Areas overlap where land was ceded more than once. Simplified by Orbis.",
        "groups": {g: {"label": lab, "color": c} for (lim, g, lab), c in zip(PERIOD, ("c3", "c2", "c5", "c1"))},
        "kinds": ACQ["cession_kinds"], "items": ACQ["cession_cards"]}
write_topo("us-cessions", feats, meta, pcts=(3000, 4000, 5000, 6500, 8000, 10000), quant=5e4, slivers=False)

# ---------------------------------------------------------------- presidential elections 1976-2024
# Shown with the `regions` layer over data/geo/admin1/USA.json (ids US-OH ...): a sets dataset (winner and share by year)
# plus a series (Republican minus Democratic share, percentage points) for line charts.
MD = os.path.join(ROOT, ".cache", "us_medsl")
mp = fetch("https://dataverse.harvard.edu/api/access/datafile/13887042", os.path.join(MD, "1976-2024-president.csv"))
res = {}
for row in csv.DictReader(open(mp, encoding="utf-8")):
    k = (int(row["year"]), "US-" + row["state_po"]); v = int(row["candidatevotes"]); t = int(row["totalvotes"])
    e = res.setdefault(k, {"tot": t, "c": {}, "lines": {}})
    cand, party = row["candidate"] or "OTHER", row["party_simplified"] or "OTHER"
    e["c"][cand] = e["c"].get(cand, 0) + v  # fusion voting (New York etc.): a candidate's votes on all lines are summed
    e["lines"].setdefault(cand, {})[party] = e["lines"].get(cand, {}).get(party, 0) + v
for e in res.values():  # each candidate's party = the line with most of their votes; totals per party
    e["party"] = {c: max(l.items(), key=lambda kv: kv[1])[0] for c, l in e["lines"].items()}
    e["p"] = {}
    for c, v in e["c"].items(): e["p"][e["party"][c]] = e["p"].get(e["party"][c], 0) + v
PARTY = {"DEMOCRAT": "dem", "REPUBLICAN": "rep"}
years = sorted({y for y, s in res}); ids = sorted({s for y, s in res})
by, share, margin, nat = {}, {}, {i: [] for i in ids}, {}
for y in years:
    by[str(y)], share[str(y)] = {}, {}
    for i in ids:
        e = res[(y, i)]
        cand, v = max(e["c"].items(), key=lambda kv: kv[1]); party = e["party"][cand]
        by[str(y)][i] = PARTY.get(party, "other"); share[str(y)][i] = round(100 * v / e["tot"], 1)
        margin[i].append(round(100 * (e["p"].get("REPUBLICAN", 0) - e["p"].get("DEMOCRAT", 0)) / e["tot"], 1))
    tot = sum(res[(y, i)]["tot"] for i in ids)
    nat[y] = {p: round(100 * sum(res[(y, i)]["p"].get(p, 0) for i in ids) / tot, 1) for p in ("DEMOCRAT", "REPUBLICAN")}
    cnt = {}
    for i in ids: cnt[by[str(y)][i]] = cnt.get(by[str(y)][i], 0) + 1
    print(y, cnt, "national D/R %:", nat[y]["DEMOCRAT"], nat[y]["REPUBLICAN"],
          "closest:", sorted(ids, key=lambda i: abs(margin[i][-1]))[:3])
doc = {"source": "medsl-president", "asOf": "U.S. President 1976-2024, V10 (Harvard Dataverse, 4 Sep 2026)", "retrieved": TODAY,
       "note": "Winner of the popular vote in each state and DC (most votes; a candidate's votes on several party lines "
               "are summed). Maine (since 1972) and Nebraska (since 1992) can split their electoral votes by district; "
               "the map shows the statewide winner only. Shares are of all votes cast for president in the state. "
               "Margin = Republican minus Democratic share, in percentage points.",
       "sets": {"pres": {"label": "Presidential election winner", "labels": {"dem": "Democrat", "rep": "Republican", "other": "Other"},
                         "byYear": by, "shareByYear": share}},
       "years": years,
       "series": {"margin": {"label": "Republican minus Democratic share", "units": "percentage points", "values": margin}},
       "national": {str(y): {"dem": nat[y]["DEMOCRAT"], "rep": nat[y]["REPUBLICAN"]} for y in years}}
s = json.dumps(doc, ensure_ascii=False, separators=(",", ":"))
open(os.path.join(OUT, "us-elections.json"), "w").write(s)
print(f"us-elections.json: {len(s)/1024:.0f} KB")
