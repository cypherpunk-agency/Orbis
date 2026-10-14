"""European colonialism series (stories col-*): colonial empires as shapes over time, plus derived area totals.

Writes, under data/history/:
  col-empires-hb.json  shapes over time 1500-1886 (historical-basemaps, GPL-3.0: this derived file stays GPL-3.0)
  col-empires-cs.json  shapes over time 1886-2019 (CShapes 2.0, CC BY-NC-SA 4.0: this derived file stays CC BY-NC-SA 4.0)
  col-area.json        series: colonial land area by colonial power (million km2) and share of the world's land,
                       computed from the two files' unsimplified geometry (method in "note")

Sources and licences (checked at the primary pages, 2026-10-14):
- historical-basemaps by Andre Ourednik, https://github.com/aourednik/historical-basemaps, LICENSE = GNU GPL v3
  (commit da7a4b7, the same commit the Rome series uses). Already registered as `historical-basemaps` (story layer).
- CShapes 2.0, ETH Zurich ICR, https://icr.ethz.ch/data/cshapes/ (CC BY-NC-SA 4.0), the R-package topojson that carries
  `status` and `owner` (cached by tools/build/borders.py in .cache/cshapes/). Registered as `cshapes` (story layer).

Method
- Eight colonial powers, as in COLDAT (data/rights/colonies.json): Britain, France, Spain, Portugal, the Netherlands,
  Belgium, Germany, Italy. Their home territory is drawn in the same colour; other dependent territories (US, Japan,
  Denmark, South Africa, Australia, New Zealand, Russia, Austria-Hungary) form one grey group "other".
- historical-basemaps: snapshots 1500, 1530, 1650, 1715, 1783, 1815, 1880. Each polity is assigned to a power from its
  NAME / SUBJECTO / PARTOF fields (rules in hb_power), with corrections listed in HB_FIX. A snapshot holds until the next.
- CShapes: every country-period whose status is colony, protectorate, mandate or occupied and whose owner is one of the
  eight (GW codes in CS_POWER), plus the eight home states. Status at the END of each year: a period counts in year Y
  if it starts on or before 31 Dec Y and ends on or after 31 Dec Y.
- Gains and losses: for each power the territory at each step is cut into pieces that keep their own from/to, so the
  map can flash only what was gained (and dash what was lost). Thin slivers from redrawn borders are dropped.
Run: python3 tools/build/colonial_series.py   (needs shapely and the mapshaper CLI in tools/node_modules)
"""
import os, sys, json, re, math, subprocess, urllib.request, datetime
from shapely.geometry import shape, mapping, Point
from shapely.ops import unary_union
from shapely import make_valid

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CACHE = os.path.join(ROOT, ".cache", "colonial")
OUT = os.path.join(ROOT, "data", "history")
MS = os.path.join(ROOT, "tools", "node_modules", "mapshaper", "bin", "mapshaper")
UA = {"User-Agent": "Orbis-data-build/1.0"}
TODAY = datetime.date.today().isoformat()
HB = "https://raw.githubusercontent.com/aourednik/historical-basemaps/da7a4b735ecef70aebdc9c73e409d8a2500d50f3/geojson/world_%s.geojson"
CS_TOPO = os.path.join(ROOT, ".cache", "cshapes", "cshapes_2_gw.topojson")

HB_YEARS = [1500, 1530, 1650, 1715, 1783, 1815, 1880]
HB_END = 1886
CS_END = 2020
POWERS = ["britain", "france", "spain", "portugal", "netherlands", "belgium", "germany", "italy"]
GROUPS = {
    "britain": {"label": "Britain", "color": "c1"}, "france": {"label": "France", "color": "c2"},
    "spain": {"label": "Spain", "color": "c3"}, "portugal": {"label": "Portugal", "color": "c4"},
    "netherlands": {"label": "The Netherlands", "color": "c5"}, "belgium": {"label": "Belgium", "color": "c8"},
    "germany": {"label": "Germany", "color": "c6"}, "italy": {"label": "Italy", "color": "c7"},
    "other": {"label": "Other powers (US, Japan, Denmark, …)", "color": "muted"}}
ISO = {"britain": "GBR", "france": "FRA", "spain": "ESP", "portugal": "PRT", "netherlands": "NLD", "belgium": "BEL",
       "germany": "DEU", "italy": "ITA"}

# ---------- historical-basemaps ----------
HOME = {  # names of the home states per power (in historical-basemaps' own spelling)
    "spain": {"Spain"}, "portugal": {"Portugal"}, "france": {"France"},
    "britain": {"England", "England and Ireland", "United Kingdom", "United Kingdom of Great Britain and Ireland", "Scotland"},
    "netherlands": {"Dutch Republic", "Netherlands", "United Kingdom of Netherlands", "        "},
    "belgium": {"Belgium"}, "germany": {"Germany"}, "italy": {"Italy"}}
RULES = [  # (power, regex on "NAME|SUBJECTO|PARTOF"), first match wins
    ("netherlands", r"netherl|neterl|dutch"),
    ("britain", r"united kingdom|\buk\b|\(uk\)|england|british|britain|rupert"),
    ("france", r"\bfrance\b|french|\(fr\)|new france"),
    ("spain", r"\bspain\b|spanish|\(spain\)|viceroyalty of (peru|new spain|new granada)"),
    ("portugal", r"portug|viceroyalty of brazil|^mozambique\|"),
]
NOT_COLONIAL = re.compile(r"austrian netherlands|habsburg netherlands|hindu kingdoms|kingdom of sardinia|^milan|franche|naples|sicily", re.I)
# corrections (year, NAME) -> power or None; each with its reason
HB_FIX = {
    (1783, "Quebec"): "britain",       # France ceded Canada to Britain in 1763 (Treaty of Paris; Wikipedia 'Province of Quebec (1763-1791)')
    (1783, "Luisiana"): "spain",       # Louisiana west of the Mississippi was Spanish 1762-1801 (Wikipedia 'Louisiana (New Spain)')
    (1815, "United Provinces of the Río de la Plata"): None,  # independent in fact since 1810, declared 1816
    (1815, "Cape Colony"): "britain", (1880, "Cape Colony"): "britain",  # British from 1806/1814 (Wikipedia 'Cape Colony')
    (1880, "Ceylon"): "britain",       # British crown colony from 1802 (Wikipedia 'British Ceylon')
    (1880, "Belize"): "britain",       # British Honduras, crown colony 1862 (Wikipedia 'British Honduras')
    (1650, "Philippines"): "spain", (1715, "Philippines"): "spain", (1783, "Philippines"): "spain",
    (1815, "Philippines"): "spain", (1880, "Philippines"): "spain",  # Spanish 1565-1898 (Wikipedia 'Captaincy General of the Philippines')
    (1880, "Cuba"): "spain", (1880, "Puerto Rico"): "spain",  # Spanish until 1898
}
UNCERTAIN = {"Dutch East Indies", "Netherlands Indies"}  # drawn as the whole archipelago, long before Dutch rule reached it
EUROPE = (-25, 34, 45, 72)


def fetch(url, path):
    if not os.path.exists(path):
        print("download", url, file=sys.stderr)
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
            open(path, "wb").write(r.read())
    return path


def hb_power(year, p):
    name = (p.get("NAME") or "").strip()
    if (year, name) in HB_FIX: return HB_FIX[(year, name)]
    for pw, names in HOME.items():
        if name in names and name.strip(): return pw
    s = "|".join(str(p.get(k) or "") for k in ("NAME", "SUBJECTO", "PARTOF"))
    if NOT_COLONIAL.search(s): return None
    for pw, rx in RULES:
        if re.search(rx, s, re.I): return pw
    return None


def ring_km2(r):
    a = 0.0
    for i in range(len(r) - 1):
        x1, y1 = r[i][:2]; x2, y2 = r[i + 1][:2]
        a += math.radians(x2 - x1) * (2 + math.sin(math.radians(y1)) + math.sin(math.radians(y2)))
    return abs(a) * 6371.0088 ** 2 / 2


def km2(g):
    if g.is_empty: return 0.0
    polys = [g] if g.geom_type == "Polygon" else [x for x in getattr(g, "geoms", []) if x.geom_type == "Polygon"]
    return sum(ring_km2(list(p.exterior.coords)) - sum(ring_km2(list(h.coords)) for h in p.interiors) for p in polys)


def clean(g):
    g = make_valid(g)
    if g.geom_type == "GeometryCollection":
        g = unary_union([x for x in g.geoms if x.geom_type in ("Polygon", "MultiPolygon")])
    return g.buffer(0)


def parts(g):
    return [g] if g.geom_type == "Polygon" else [x for x in getattr(g, "geoms", []) if x.geom_type == "Polygon"]


def drop_slivers(g):
    """keep compact parts (islands too); drop thin slivers and specks left by redrawn borders"""
    keep = []
    for p in parts(g):
        a = km2(p)
        if a < 30: continue
        compact = 4 * math.pi * p.area / (p.length ** 2) if p.length else 0
        if a < 3000 and compact < 0.25: continue
        if a < 15000 and compact < 0.06: continue
        keep.append(p)
    return unary_union(keep) if keep else None


def in_europe(g):
    c = g.representative_point()
    return EUROPE[0] <= c.x <= EUROPE[2] and EUROPE[1] <= c.y <= EUROPE[3]


def decompose(steps, end, names_at):
    """steps: [(year, geometry or None)], ascending. Returns pieces [(geom, from, to)] such that the union of the pieces
    valid at each step equals that step's geometry (minus slivers)."""
    pieces, active = [], []
    for y, G in steps:
        G = G if G is not None and not G.is_empty else None
        nxt = []
        for g, f in active:
            keep = g.intersection(G) if G is not None else None
            gone = g.difference(G) if G is not None else g
            gone = drop_slivers(clean(gone)) if gone is not None and not gone.is_empty else None
            if gone is not None: pieces.append((gone, f, y))
            if keep is not None and not keep.is_empty:
                keep = drop_slivers(clean(keep))
                if keep is not None: nxt.append((keep, f))
        if G is not None:
            have = unary_union([g for g, f in nxt]) if nxt else None
            add = G.difference(have) if have is not None else G
            add = drop_slivers(clean(add)) if not add.is_empty else None
            if add is not None: nxt.append((add, y))
        active = nxt
    for g, f in active: pieces.append((g, f, end))
    return pieces


def name_for(piece, f, names_at):
    """name of the source polygon that contains the piece's representative point at its first year"""
    pt = piece.representative_point()
    for g, nm in names_at.get(f, []):
        if g.contains(pt): return nm
    best = max(names_at.get(f, []), key=lambda x: x[0].intersection(piece).area, default=(None, ""))
    return best[1]


def to_topo(features, out, keep_pct, extra):
    tmp = os.path.join(CACHE, os.path.basename(out) + ".geojson")
    json.dump({"type": "FeatureCollection", "features": features}, open(tmp, "w"))
    topo = tmp.replace(".geojson", ".topo.json")
    subprocess.run(["node", MS, "-quiet", "-i", tmp, "-simplify", "weighted", "%s%%" % keep_pct, "keep-shapes",
                    "-filter-slivers", "min-area=200km2", "-rename-layers", "shapes",
                    "-o", topo, "format=topojson", "quantization=20000"], check=True)
    t = json.load(open(topo))
    d = dict(extra); d["topology"] = t
    json.dump(d, open(out, "w"), ensure_ascii=False, separators=(",", ":"))
    print(out, os.path.getsize(out) // 1024, "KB", len(features), "features", file=sys.stderr)


def snap_simplify(g, tol=0.02):
    return clean(g.simplify(tol, preserve_topology=True))


def build_hb():
    os.makedirs(CACHE, exist_ok=True)
    by_power = {p: [] for p in POWERS}
    names = {p: {} for p in POWERS}
    area = {}  # (power, year) -> colonial km2 (home excluded); world land per year
    land = {}
    for y in HB_YEARS:
        g = json.load(open(fetch(HB % y, os.path.join(CACHE, "hb_%s.geojson" % y))))
        acc = {p: [] for p in POWERS}
        tot = 0.0
        for f in g["features"]:
            if not f["geometry"]: continue
            geom = clean(shape(f["geometry"]))
            c = geom.representative_point()
            if c.y > -60: tot += km2(geom)
            pw = hb_power(y, f["properties"])
            if not pw: continue
            nm = (f["properties"].get("NAME") or "").strip() or pw
            home = nm in HOME[pw]
            if not home and in_europe(geom): continue
            acc[pw].append((geom, nm, home))
        land[y] = tot
        for pw in POWERS:
            col = [x[0] for x in acc[pw] if not x[2]]
            area[(pw, y)] = sum(km2(x) for x in col)  # features do not overlap within a snapshot
            u = unary_union([snap_simplify(x[0]) for x in acc[pw]]) if acc[pw] else None
            by_power[pw].append((y, u))
            names[pw][y] = [(snap_simplify(x[0]), x[1] + ("" if x[2] else "")) for x in acc[pw]]
    feats = []
    for pw in POWERS:
        for geom, f, t in decompose(by_power[pw], HB_END, names[pw]):
            nm = name_for(geom, f, names[pw])
            props = {"name": nm, "from": f, "to": t, "group": pw}
            if nm in UNCERTAIN:
                props["uncertain"] = True
                props["note"] = "historical-basemaps draws the whole archipelago; Dutch rule covered only parts of it before the late 19th century"
            feats.append({"type": "Feature", "properties": props, "geometry": mapping(geom)})
    note = ("Borders: historical-basemaps by André Ourednik (GitHub aourednik/historical-basemaps, commit da7a4b7, GPL-3.0), "
            "snapshots 1500, 1530, 1650, 1715, 1783, 1815 and 1880; each holds until the next (1880 until 1886, where CShapes "
            "takes over). The project marks its borders as approximate. They show claimed territory: in many colonies "
            "European control reached only the coasts and a few inland areas, and small forts and trading posts are not "
            "drawn. Orbis assigned polities to the eight colonial powers by their names and overlords, corrected three "
            "errors (1783: Quebec British since 1763, Louisiana Spanish 1762-1801; 1815: Río de la Plata independent in "
            "fact since 1810), cut each empire into pieces with their own dates so gains can be highlighted, and "
            "simplified the shapes. The Dutch East Indies are drawn as the whole archipelago from 1650 (dashed): Dutch "
            "rule covered only parts of it until the late 19th century. This derived file is distributed under the GNU GPL v3.")
    to_topo(feats, os.path.join(OUT, "col-empires-hb.json"), 6,
            {"source": "historical-basemaps", "asOf": "2026-09-15", "retrieved": TODAY,
             "licence": "GPL-3.0 (derived from historical-basemaps; this file stays under the GNU GPL v3)",
             "note": note, "groups": {k: v for k, v in GROUPS.items() if k != "other"}})
    return area, land


# ---------- CShapes ----------
CS_POWER = {200: "britain", 220: "france", 230: "spain", 235: "portugal", 210: "netherlands", 211: "belgium",
            255: "germany", 325: "italy"}
CS_OTHER = {2, 390, 740, 560, 900, 920, 365, 300}
DEP = {"colony", "protectorate", "mandate", "occupied"}


def yr_span(start, end):
    """end-of-year convention: counts in year Y if start <= Y-12-31 <= end -> [from, to)"""
    s = datetime.date.fromisoformat(start); e = datetime.date.fromisoformat(end)
    f = s.year
    t = e.year + 1 if (e.month, e.day) == (12, 31) else e.year
    return f, t


def build_cs():
    geo = os.path.join(CACHE, "cshapes_gw.geojson")
    if not os.path.exists(geo):
        subprocess.run(["node", MS, "-quiet", "-i", CS_TOPO, "-o", geo, "format=geojson"], check=True)
    fc = json.load(open(geo))
    items = {p: [] for p in POWERS + ["other"]}
    land_items = []
    for f in fc["features"]:
        p = f["properties"]
        if not f["geometry"]: continue
        a, b = yr_span(p["start"], p["end"])
        if a >= b: continue
        st, ow, gw = p.get("status"), int(p.get("owner") or -1), int(p.get("gwcode"))
        g = None
        if st in DEP and (ow in CS_POWER or ow in CS_OTHER):
            pw = CS_POWER.get(ow, "other"); home = False
        elif st == "independent" and gw in CS_POWER:
            pw = CS_POWER[gw]; home = True
        else:
            pw = None
        geom = clean(shape(f["geometry"]))
        land_items.append((geom, a, b))
        if pw: items[pw].append((geom, a, b, p["country_name"], home, gw))
    area, feats = {}, []
    for pw in POWERS + ["other"]:
        its = items[pw]
        years = sorted({x[1] for x in its} | {x[2] for x in its})
        years = [y for y in years if y < CS_END]
        steps, names = [], {}
        for y in years:
            live = [x for x in its if x[1] <= y < x[2]]
            names[y] = [(snap_simplify(x[0], 0.01), x[3]) for x in live]
            steps.append((y, unary_union([n[0] for n in names[y]]) if live else None))
        for geom, f, t in decompose(steps, CS_END, names):
            nm = name_for(geom, f, names)
            feats.append({"type": "Feature", "properties": {"name": nm, "from": f, "to": t if t < CS_END else None, "group": pw},
                          "geometry": mapping(geom)})
        area[pw] = its
    note = ("Borders: CShapes 2.0 (Schvitz, Rüegger, Girardin, Cederman, Weidmann, Gleditsch 2022), ETH Zurich ICR, "
            "CC BY-NC-SA 4.0, from the version in the cshapes R package that records each dependency's status and ruling "
            "state. Shown: colonies, protectorates, mandates and occupied territories of Britain, France, Spain, Portugal, "
            "the Netherlands, Belgium, Germany and Italy, and their home states; dependencies of the United States, Japan, "
            "Denmark, South Africa, Australia, New Zealand, Russia and Austria-Hungary in grey. Status at the end of each "
            "year. CShapes follows the Gleditsch-Ward state list: self-governing dominions (Canada from 1886, Australia "
            "from 1901, New Zealand from 1907, South Africa from 1910) count as independent; the Congo Free State "
            "(1885-1908), King Leopold II's personal possession, is listed under Belgium; changes under about 10,000 km² "
            "are left out. Orbis cut each empire into pieces with their own dates so gains and losses can be highlighted, "
            "and simplified the shapes. This derived file is distributed under CC BY-NC-SA 4.0, like its source.")
    to_topo(feats, os.path.join(OUT, "col-empires-cs.json"), 5,
            {"source": "cshapes", "asOf": "CShapes 2.0", "retrieved": TODAY,
             "licence": "CC BY-NC-SA 4.0 (derived from CShapes 2.0; this file stays CC BY-NC-SA 4.0)",
             "note": note, "groups": GROUPS})
    return items, land_items


AREA_YEARS_CS = [1890, 1900, 1913, 1920, 1938, 1945, 1950, 1955, 1960, 1965, 1970, 1975, 1990]


def main():
    area_hb, land_hb = build_hb()
    items, land_items = build_cs()
    years = HB_YEARS + AREA_YEARS_CS
    vals = {ISO[p]: [] for p in POWERS}
    share = {ISO[p]: [] for p in POWERS}
    world, wshare = [], []
    cs_land = {}
    for y in AREA_YEARS_CS:
        cs_land[y] = sum(km2(g) for g, a, b in land_items if a <= y < b and g.representative_point().y > -60)
    for y in years:
        tot = 0.0
        L = land_hb[y] if y in land_hb else cs_land[y]
        for p in POWERS:
            if y in land_hb:
                a = area_hb[(p, y)]
            else:
                live = [x[0] for x in items[p] if x[1] <= y < x[2] and not x[4]]
                a = km2(unary_union(live)) if live else 0.0
            vals[ISO[p]].append(round(a / 1e6, 2)); share[ISO[p]].append(round(100 * a / L, 1)); tot += a
        world.append(round(tot / 1e6, 2)); wshare.append(round(100 * tot / L, 1))
    note = ("Land area of the colonies, protectorates, mandates and occupied territories of each power (home country "
            "excluded), in million km², and as a share of the world's land outside Antarctica. Computed by Orbis on the "
            "spherical earth from unsimplified borders: historical-basemaps (GPL-3.0) for 1500-1880, CShapes 2.0 "
            "(CC BY-NC-SA 4.0) for 1890 onwards, status at the end of each year. The two sources differ: historical-"
            "basemaps draws claimed territory (the Dutch East Indies as the whole archipelago from 1650, Brazil and "
            "Australia to their modern borders), while CShapes counts self-governing dominions (Canada, Australia after "
            "1901, New Zealand after 1907, South Africa after 1910) as independent. Treat the numbers as rough orders of "
            "magnitude. Population shares are not computed: neither source has population.")
    d = {"source": "historical-basemaps", "asOf": "2026-09-15", "retrieved": TODAY, "note": note, "years": years,
         "series": {"col_area": {"label": "Colonial land area", "units": "million km²", "values": {k: v for k, v in vals.items()}},
                    "col_share": {"label": "Share of the world's land", "units": "%", "values": share}},
         "world": {"col_area": world, "col_share": wshare}}
    json.dump(d, open(os.path.join(OUT, "col-area.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    for i, y in enumerate(years):
        print(y, "total %.1f M km2 = %.1f%%" % (world[i], wshare[i]), {k: v[i] for k, v in vals.items() if v[i]}, file=sys.stderr)


if __name__ == "__main__":
    main()
