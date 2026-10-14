"""Territorial control in Ukraine over time, from Wikipedia's settlement control map
"Module:Russo-Ukrainian war detailed map" (and, from April 2024, the "overview map" module it extends).
Licence: CC BY-SA 4.0 (Wikipedia text and modules), story layer only; attribution to Wikipedia contributors.

The module lists ~1,000 settlements (and some infrastructure icons) with a marker for Ukrainian, Russian or
contested control. It is edited by volunteers; markers follow their reading of news reports and maps.
For each target date this script reads the last revision saved on or before that date (MediaWiki API,
prop=revisions lists the revision ids;
the content of each chosen revision is read with index.php?action=raw&oldid=<id>), extracts the settlement points and their control mark, and writes:

  data/history/ua-control.json   shapes over time: one Voronoi cell per settlement point, clipped to Ukraine
                                  (internationally recognised borders, incl. Crimea), valid from one target date to
                                  the next while its control mark is unchanged; group ua / ru / con. The cells are
                                  an APPROXIMATION of control areas (nearest listed settlement), not a front line.
  data/history/ua-control-points.json   lines/points sets: the settlement points themselves at each date
                                  ("ua_<date>", "ru_<date>", "con_<date>"), for scenes that show the raw points.

Rate limits: Wikimedia throttles anonymous API use hard; the script waits between calls, backs off on 429,
and caches every revision under .cache/ua_control/. User-Agent names the project, no personal data.
Run: python3 tools/build/ua_control.py   (needs mapshaper in tools/node_modules and scipy, shapely)
"""
import os, re, json, time, sys, datetime, subprocess, urllib.request, urllib.parse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CACHE = os.path.join(ROOT, ".cache/ua_control")
os.makedirs(CACHE, exist_ok=True)
UA = {"User-Agent": "Orbis-data-build/1.0 (https://github.com/cypherpunk-agency/Orbis)"}
DETAILED = "Module:Russo-Ukrainian war detailed map"
OVERVIEW = "Module:Russo-Ukrainian war overview map"
# target dates (yyyymmdd): end of day; the revision in force at that moment is used
DATES = [20220325, 20220410, 20220831, 20221005, 20221115, 20230601, 20231231,
         20240601, 20241231, 20250601, 20251231, 20261007]


def api(params):
    params = dict(params, format="json", formatversion="2", maxlag="5")
    url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
    for k in range(10):
        try:
            b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read()
            time.sleep(4)
            return json.loads(b)
        except Exception as e:
            w = 30 * (k + 1)
            print(f"  retry in {w}s: {e}", file=sys.stderr)
            time.sleep(w)
    raise SystemExit("MediaWiki API failed")


def revisions(title):
    """All revisions of `title` (id, timestamp), oldest first; listed once via the API and cached."""
    fn = os.path.join(CACHE, "revs_" + re.sub(r"\W+", "_", title) + ".json")
    if not os.path.exists(fn):
        revs, cont = [], {}
        while True:
            d = api(dict(action="query", prop="revisions", titles=title, rvprop="timestamp|ids",
                         rvlimit="max", rvdir="newer", **cont))
            revs += d["query"]["pages"][0].get("revisions", [])
            if "continue" not in d:
                break
            cont = {"rvcontinue": d["continue"]["rvcontinue"]}
        json.dump(revs, open(fn, "w"))
    return json.load(open(fn))


def revision_at(title, ymd):
    """Last revision of `title` saved on or before the end of day ymd -> {revid, timestamp, content} or None.
    Content comes from index.php?action=raw&oldid=..., which is cached by Wikimedia and not throttled like the API."""
    s = str(ymd)
    cut = f"{s[:4]}-{s[4:6]}-{s[6:]}T23:59:59Z"
    before = [r for r in revisions(title) if r["timestamp"] <= cut]
    if not before:
        return None
    r = before[-1]
    fn = os.path.join(CACHE, f"rev_{r['revid']}.lua")
    if not os.path.exists(fn):
        url = f"https://en.wikipedia.org/w/index.php?action=raw&oldid={r['revid']}"
        for k in range(6):
            try:
                b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read()
                break
            except Exception as e:
                print(f"  retry raw in {20*(k+1)}s: {e}", file=sys.stderr); time.sleep(20 * (k + 1))
        else:
            raise SystemExit("raw fetch failed")
        open(fn, "wb").write(b); time.sleep(2)
    return {"revid": r["revid"], "timestamp": r["timestamp"], "content": open(fn, encoding="utf-8").read()}


MARKS = {  # marker file -> control group (settlement markers only; icons, arcs and grey dots are skipped)
    "Location dot blue.svg": "ua", "Location dot red.svg": "ru",
    "80x80-red-blue-anim.gif": "con", "Map-ctl2-red+blue.svg": "con",
}
MK = {"ukr": "Location dot blue.svg", "rus": "Location dot red.svg", "con": "80x80-red-blue-anim.gif",
      "shr": "Map-ctl2-red+blue.svg"}
ENTRY = re.compile(r"\{[^{}]*?\blat\s*=[^{}]*\}")


def field(e, k):
    m = re.search(r"\b" + k + r'\s*=\s*(?:"([^"]*)"|([\w.]+))', e)
    return None if not m else (m.group(1) if m.group(1) is not None else m.group(2))


def parse(content):
    """Settlement points in one module revision -> list of (name, lon, lat, group)."""
    out = []
    for e in ENTRY.findall(re.sub(r"--\[\[.*?\]\]", "", content, flags=re.S)):
        mark = field(e, "mark") or ""
        if mark.startswith("mk."):
            mark = MK.get(mark[3:], "")
        g = MARKS.get(mark)
        if not g:
            continue
        try:
            lat, lon = float(field(e, "lat")), float(field(e, "long"))
        except (TypeError, ValueError):
            continue
        lab = field(e, "label") or field(e, "link") or ""
        m = re.match(r"\[\[([^|\]]+)(?:\|([^\]]+))?\]\]", lab.strip())
        name = (m.group(2) or m.group(1)) if m else lab
        name = re.sub(r",.*$", "", re.sub(r"\s*\(.*?\)", "", name)).strip()
        if name:
            out.append((name, round(lon, 3), round(lat, 3), g))
    return out


def ukraine_outline():
    """Ukraine within its internationally recognised borders (incl. Crimea and Sevastopol), from Natural Earth
    1:10m admin-1 (public domain), simplified."""
    from shapely.geometry import shape
    from shapely.ops import unary_union
    src = os.path.join(ROOT, ".cache/admin1/ne_10m_admin_1_states_provinces.shp")
    if not os.path.exists(src):
        raise SystemExit("run tools/build/admin1.py first (downloads Natural Earth 1:10m admin-1)")
    gj = os.path.join(CACHE, "ua_adm1.geojson")
    if not os.path.exists(gj):
        subprocess.run(["node", os.path.join(ROOT, "tools/node_modules/mapshaper/bin/mapshaper"), "-i", src,
                        "encoding=utf8", "-filter", 'iso_3166_2.indexOf("UA-")==0', "-filter-fields",
                        "name,iso_3166_2", "-o", gj, "format=geojson"], check=True, capture_output=True)
    fs = json.load(open(gj))["features"]
    u = unary_union([shape(f["geometry"]) for f in fs]).simplify(0.01)
    return u, {f["properties"]["iso_3166_2"]: shape(f["geometry"]) for f in fs}


def ymd_of(ts):
    return int(ts[:10].replace("-", ""))


def build():
    import shapely
    from shapely.geometry import Point, MultiPoint, mapping
    from shapely.ops import unary_union
    ukr, adm = ukraine_outline()
    area = ukr.buffer(0.03)
    steps = []  # (revision date, {key: (name, lon, lat, group)}, revision info)
    for ymd in DATES:
        d, o = revision_at(DETAILED, ymd), revision_at(OVERVIEW, ymd)
        pts = {}
        for rev in (o, d):  # the detailed module extends the overview: its entries win
            if rev:
                for n, x, y, g in parse(rev["content"]):
                    if area.contains(Point(x, y)):
                        pts[(n, round(x, 2), round(y, 2))] = (n, x, y, g)
        stamp = max(ymd_of(r["timestamp"]) for r in (d, o) if r)
        info = {"target": ymd, "detailed": [d["revid"], d["timestamp"]], "overview": o and [o["revid"], o["timestamp"]]}
        steps.append((stamp, pts, info))
        c = {g: sum(1 for p in pts.values() if p[3] == g) for g in ("ua", "ru", "con")}
        print(ymd, "rev", stamp, len(pts), c)
    dates = [s[0] for s in steps]
    assert len(set(dates)) == len(dates), "two targets share a revision"

    # --- points: one item per settlement and period of unchanged control
    COL = {"ua": "c1", "ru": "c2", "con": "c3"}
    keys = sorted({k for _, pts, _ in steps for k in pts})
    items = []
    for k in keys:
        cur = None
        for i, (dt, pts, _) in enumerate(steps):
            g = pts[k][3] if k in pts else None
            if cur and cur["group"] != g:
                cur["to"] = dt; items.append(cur); cur = None
            if g and not cur:
                cur = {"name": k[0], "at": [pts[k][1], pts[k][2]], "group": g, "color": COL[g], "from": dt, "to": None}
        if cur:
            items.append(cur)
    for it in items:
        it.pop("group")

    # --- areas: Voronoi cells around every settlement ever listed, clipped to Ukraine; each cell takes the control
    # mark of its own settlement at that date, or (if unlisted then) of the nearest listed settlement
    uniq = {}
    for k in keys:
        last = [pts[k] for _, pts, _ in steps if k in pts][-1]
        uniq.setdefault((last[1], last[2]), k)
    sites = list(uniq.items())
    cells = shapely.voronoi_polygons(MultiPoint([Point(xy) for xy, _ in sites]), extend_to=area.envelope.buffer(1))
    cellmap = []
    for c in cells.geoms:
        for j, (xy, k) in enumerate(sites):
            if c.contains(Point(xy)):
                cellmap.append((j, c)); break
    hist = {}
    import numpy as np
    for _, pts, _ in steps:
        lk = list(pts.values())
        arr = np.array([[p[1], p[2]] for p in lk])
        for j, (xy, k) in enumerate(sites):
            if k in pts:
                g = pts[k][3]
            else:
                g = lk[int(((arr - np.array(xy)) ** 2).sum(1).argmin())][3]
            hist.setdefault(j, []).append(g)
    # dissolve cells with the same control history, split into connected parts
    by = {}
    for j, c in cellmap:
        cc = c.intersection(ukr)
        if not cc.is_empty:
            by.setdefault(tuple(hist[j]), []).append(cc)
    feats = []
    for h, polys in by.items():
        merged = unary_union(polys)
        parts = list(merged.geoms) if hasattr(merged, "geoms") else [merged]
        for part in parts:
            if part.geom_type != "Polygon" or part.area < 1e-5:
                continue
            i = 0
            while i < len(h):
                j = i
                while j + 1 < len(h) and h[j + 1] == h[i]:
                    j += 1
                feats.append({"type": "Feature", "geometry": mapping(part), "properties": {
                    "name": {"ua": "Held by Ukraine", "ru": "Held by Russia", "con": "Contested"}[h[i]],
                    "group": h[i], "from": dates[i] if i > 0 else None, "to": dates[j + 1] if j + 1 < len(h) else None}})
                i = j + 1
    tmp = os.path.join(CACHE, "cells.geojson")
    json.dump({"type": "FeatureCollection", "features": feats}, open(tmp, "w"))
    tj = os.path.join(CACHE, "cells.topo.json")
    subprocess.run(["node", os.path.join(ROOT, "tools/node_modules/mapshaper/bin/mapshaper"), tmp,
                    "-simplify", "dp", "interval=800", "keep-shapes", "-rename-layers", "shapes",
                    "-o", tj, "format=topojson", "quantization=20000"], check=True, capture_output=True)
    topo = json.load(open(tj))
    today = datetime.date.today().isoformat()
    revs = "; ".join(f"{s[2]['target']}: detailed rev {s[2]['detailed'][0]} ({s[2]['detailed'][1][:10]})" +
                     (f", overview rev {s[2]['overview'][0]} ({s[2]['overview'][1][:10]})" if s[2]["overview"] else "")
                     for s in steps)
    first = steps[0][0]
    base = ("Wikipedia, 'Module:Russo-Ukrainian war detailed map' (from April 2024 together with "
            "'Module:Russo-Ukrainian war overview map', which it extends), by Wikipedia contributors, CC BY-SA 4.0. "
            "Volunteer-edited: each settlement carries a marker for Ukrainian, Russian or contested control, set by "
            "editors from news reports and other maps. Each timeline step is the revision in force on a target date; "
            "the step's date is the date of that revision (the module is edited irregularly, so a revision can be "
            "weeks old on its target date). Revisions used: " + revs + ". Infrastructure icons, grey markers and arc "
            "markers are left out; places outside Ukraine's internationally recognised borders (e.g. in Russia's "
            "Kursk region) are left out. Built by tools/build/ua_control.py.")
    out_a = {"source": "wp-ua-control", "asOf": steps[-1][2]["detailed"][1][:10], "retrieved": today,
             "note": "APPROXIMATION. Areas are not drawn from a front-line map: every place in Ukraine is given the "
                     "control marker of the nearest settlement listed in the Wikipedia module at that date (Voronoi "
                     "cells around the settlement points, clipped to Ukraine's internationally recognised borders "
                     "from Natural Earth). Cells with the same history are merged. Edges between groups are therefore "
                     "only roughly where the front was, and areas far from listed places (open steppe, the rear) are "
                     "guesses. Before " + str(first) + " the cells carry the first step's marks. " + base,
             "dates": dates,
             "groups": {"ua": {"label": "Held by Ukraine (approx.)", "color": "c1"},
                        "ru": {"label": "Held by Russia (approx.)", "color": "c2"},
                        "con": {"label": "Contested (approx.)", "color": "c3"}},
             "topology": topo}
    out_p = {"source": "wp-ua-control", "asOf": out_a["asOf"], "retrieved": today,
             "note": "Settlement control markers as listed in each revision. " + base, "dates": dates,
             "points": {"settlements": items}}
    for fn, o in (("data/history/ua-control.json", out_a), ("data/history/ua-control-points.json", out_p)):
        json.dump(o, open(os.path.join(ROOT, fn), "w"), separators=(",", ":"), ensure_ascii=False)
        print(fn, os.path.getsize(os.path.join(ROOT, fn)))
    print("features", len(topo["objects"]["shapes"]["geometries"]), "point items", len(items))


if __name__ == "__main__":
    if "--fetch-only" in sys.argv:
        for ymd in DATES:
            for t in (DETAILED, OVERVIEW):
                r = revision_at(t, ymd)
                print(ymd, t, r and (r["revid"], r["timestamp"], len(r["content"])))
    else:
        build()
