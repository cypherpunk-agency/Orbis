#!/usr/bin/env python3
"""Data for the series "Ruling houses of Europe" (chapters royals-england, royals-europe, royals-cousins, royals-today).

Writes:
  data/geo/regions/royal-crowns.json   Europe's crowns as modern areas: countries, plus England/Scotland/N. Ireland,
                                       German and Italian groups of regions, Kaliningrad (Natural Earth, public domain)
  data/history/royals-crowns.json      which house ruled each area, 1500-2026 (codes + change lists; Wikipedia lists)
  data/history/royals-england.json     monarchs of England, Great Britain and the UK with house (Wikidata, CC0),
                                       checked against Wikipedia's lists of English and British monarchs
  data/history/royals-realms.json      lands of the English/British and Scottish crowns, snapshots 1000-1815
                                       (historical-basemaps, GPL-3.0: this derived file stays GPL-3.0)
  data/history/royals-cards-*.json     event cards (typed by Orbis from the cited Wikipedia articles)
  data/history/royals-cousins.json     courts, family lines and thrones held by descendants of Victoria and Christian IX
  data/history/royals-today.json       today's monarchies by type, Commonwealth realms, Europe's reigning houses

Sources (licences re-read at the primary pages, 14 Oct 2026):
- Natural Earth admin-0 1:50m and admin-1 1:10m, public domain (naturalearthdata.com/about/terms-of-use).
- Wikidata, CC0 (wikidata.org/wiki/Wikidata:Licensing), SPARQL endpoint query.wikidata.org, generic User-Agent.
- historical-basemaps by André Ourednik, GNU GPL v3 (cached by tools/build/hre_series.py in .cache/hre/hb/).
- Facts in cards and in the house tables: English Wikipedia articles named per item (facts only; no text copied).

Run: python3 tools/build/royals.py   (needs tools/node_modules/mapshaper; NE files in .cache/ne and .cache/admin1)
"""
import json, os, subprocess, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(ROOT, ".cache", "royals")
HIST = os.path.join(ROOT, "data", "history")
GEO = os.path.join(ROOT, "data", "geo", "regions")
MS = os.path.join(ROOT, "tools", "node_modules", "mapshaper", "bin", "mapshaper")
TODAY = time.strftime("%Y-%m-%d")
UA = {"User-Agent": "Orbis-data-build/1.0", "Accept": "application/sparql-results+json"}
for d in (CACHE, HIST, GEO):
    os.makedirs(d, exist_ok=True)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import royals_data as RD  # hand-typed tables (houses by crown, cards, today's monarchies), each row cited


def dump(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
    print(os.path.relpath(path, ROOT), os.path.getsize(path) // 1024, "KB")


# ---------------------------------------------------------------- geometry
EUROPE = ["ALB", "AUT", "BEL", "BGR", "BIH", "BLR", "CHE", "CYP", "CZE", "DNK", "ESP", "EST", "FIN", "FRA", "GRC",
          "HRV", "HUN", "IRL", "ISL", "LTU", "LUX", "LVA", "MDA", "MKD", "MLT", "MNE", "NLD", "NOR", "POL", "PRT",
          "ROU", "SRB", "SVK", "SVN", "SWE", "TUR", "UKR", "XKX"]
# groups of first-level regions (Natural Earth admin-1 fields) that stand for a historical crown
DEU = {"DE-PRU": ["DE-BB", "DE-BE"], "DE-BAV": ["DE-BY"], "DE-SAX": ["DE-SN"], "DE-HAN": ["DE-NI", "DE-HB"]}
ITA = {"IT-SAV": ["Piemonte", "Valle d'Aosta"], "IT-SAR": ["Sardegna"], "IT-LIG": ["Liguria"], "IT-LOM": ["Lombardia"],
       "IT-VEN": ["Veneto", "Friuli-Venezia Giulia"], "IT-TRE": ["Trentino-Alto Adige"], "IT-TUS": ["Toscana"],
       "IT-NAP": ["Campania", "Abruzzo", "Molise", "Apulia", "Basilicata", "Calabria"], "IT-SIC": ["Sicily"],
       "IT-PAP": ["Lazio", "Umbria", "Marche", "Emilia-Romagna"]}
GBR = {"GB-ENG": ["England", "Wales"], "GB-SCT": ["Scotland"], "GB-NIR": ["Northern Ireland"]}
NAMES = {"DE-PRU": "Brandenburg and Berlin", "DE-BAV": "Bavaria", "DE-SAX": "Saxony", "DE-HAN": "Lower Saxony (Hanover)",
         "DE-OTH": "Rest of Germany", "IT-SAV": "Piedmont", "IT-SAR": "Sardinia", "IT-LIG": "Liguria (Genoa)",
         "IT-LOM": "Lombardy (Milan)", "IT-VEN": "Veneto and Friuli (Venice)", "IT-TRE": "Trentino-South Tyrol",
         "IT-TUS": "Tuscany", "IT-NAP": "Southern Italy (Naples)", "IT-SIC": "Sicily", "IT-PAP": "Central Italy (Papal States)",
         "GB-ENG": "England and Wales", "GB-SCT": "Scotland", "GB-NIR": "Northern Ireland", "RU-KGD": "Kaliningrad (Königsberg)",
         "RUS": "Russia (European part)"}
BBOX = "-25,34,60,71.5"


def ms(*args):
    subprocess.run([MS, args[0], "-quiet", *args[1:]], check=True)


def build_geo():
    a1 = os.path.join(ROOT, ".cache", "admin1", "ne_10m_admin_1_states_provinces.shp")
    a0 = os.path.join(ROOT, ".cache", "ne", "ne_50m_admin_0_countries.geojson")
    tmp = os.path.join(CACHE, "geo")
    os.makedirs(tmp, exist_ok=True)

    def unit_expr(table, field):
        parts = []
        for u, keys in table.items():
            parts.append(" || ".join(f'{field}=={json.dumps(k)}' for k in keys) + f' ? {json.dumps(u)} : ')
        return "".join(parts)

    # admin-1 groups: Germany, Italy, United Kingdom, Kaliningrad vs rest of Russia
    expr = ("u = adm0_a3=='DEU' ? (" + unit_expr(DEU, "iso_3166_2") + "'DE-OTH') : adm0_a3=='ITA' ? (" +
            unit_expr(ITA, "region") + "'IT-OTH') : adm0_a3=='GBR' ? (" + unit_expr(GBR, "geonunit") +
            "'GB-OTH') : adm0_a3=='RUS' ? (iso_3166_2=='RU-KGD' ? 'RU-KGD' : 'RUS') : null")
    ms(a1, "-filter", "['DEU','ITA','GBR','RUS'].indexOf(adm0_a3)>-1", "-each", expr, "-clip", "bbox=" + BBOX,
       "-dissolve", "u", "-o", os.path.join(tmp, "a1.geojson"), "force")
    ms(a0, "-each", "u = ADM0_A3=='KOS' ? 'XKX' : (ISO_A3!='-99' ? ISO_A3 : ADM0_A3)", "-filter", f"{json.dumps(EUROPE)}.indexOf(u)>-1",
       "-clip", "bbox=" + BBOX, "-filter-fields", "u", "-o", os.path.join(tmp, "a0.geojson"), "force")
    a = json.load(open(os.path.join(tmp, "a1.geojson")))
    b = json.load(open(os.path.join(tmp, "a0.geojson")))
    units = {}
    for f in a["features"] + b["features"]:
        u = f["properties"]["u"]
        assert u and u not in ("GB-OTH", "IT-OTH"), u
        units[u] = f
    feats = []
    for u, f in sorted(units.items()):
        f["properties"] = {"u": u, "name": NAMES.get(u) or u}
        feats.append(f)
    merged = os.path.join(tmp, "units.geojson")
    json.dump({"type": "FeatureCollection", "features": feats}, open(merged, "w"))
    out = os.path.join(GEO, "royal-crowns.json")
    ms(merged, "-simplify", "weighted", "4%", "keep-shapes", "-filter-islands", "min-area=60km2",
       "-each", "lx=this.innerX, ly=this.innerY", "-rename-layers", "regions",
       "-o", out, "format=topojson", "id-field=u", "quantization=20000", "precision=0.001", "force")
    # round label points, add display names from NAMES or Natural Earth country names
    t = json.load(open(out))
    nm = {f["properties"]["u"]: f["properties"]["name"] for f in feats}
    import re
    for g in t["objects"]["regions"]["geometries"]:
        p = g["properties"]
        g["properties"] = {"name": nm[g["id"]] if g["id"] in NAMES else country_name(g["id"]),
                           "lx": round(p["lx"] or 0, 2), "ly": round(p["ly"] or 0, 2)}
    for k, v in LABEL_AT.items():
        for g in t["objects"]["regions"]["geometries"]:
            if g["id"] == k:
                g["properties"]["lx"], g["properties"]["ly"] = v
    dump(out, t)
    return sorted(units)


LABEL_AT = {"RUS": [40.0, 56.0], "NOR": [9.5, 61.0], "SWE": [15.0, 60.5], "FIN": [26.0, 62.5], "TUR": [33.0, 39.0]}
_CN = None


def country_name(iso):
    global _CN
    if _CN is None:
        t = json.load(open(os.path.join(ROOT, "data", "world50.json")))
        _CN = {g["id"]: g["properties"]["name"] for g in t["objects"]["countries"]["geometries"]}
    return _CN.get(iso, iso)


# ---------------------------------------------------------------- houses by crown
def build_crowns(units):
    codes, changes = {}, {}
    for u, rows in RD.CROWNS.items():
        assert u in units, ("unknown area", u)
        ch = []
        for i, (yr, label, cat) in enumerate(rows):
            assert cat in RD.CATS, (u, yr, cat)
            c = f"{u}.{i}"
            codes[c] = {"label": label, "cat": cat}
            ch.append([yr, c])
        assert [r[0] for r in ch] == sorted(r[0] for r in ch), ("unsorted", u)
        changes[u] = ch
    missing = sorted(set(units) - set(RD.CROWNS))
    assert not missing, ("areas without a history", missing)
    d = {"source": "editorial", "asOf": "2026-10-14", "retrieved": TODAY,
         "note": RD.CROWNS_NOTE,
         "sets": {"crowns": {"label": "Ruling house", "labels": {k: v[0] for k, v in RD.CATS.items()},
                             "codes": codes, "changes": changes}}}
    dump(os.path.join(HIST, "royals-crowns.json"), d)


# ---------------------------------------------------------------- Wikidata: monarchs of England / GB / UK
SPARQL = """SELECT ?pos ?m ?mLabel ?start ?end ?famLabel ?art WHERE {
  VALUES ?pos { wd:Q18810062 wd:Q18810066 wd:Q111722535 wd:Q9134365 }
  ?m p:P39 ?st . ?st ps:P39 ?pos .
  OPTIONAL { ?st pq:P580 ?start } OPTIONAL { ?st pq:P582 ?end }
  OPTIONAL { ?m wdt:P53 ?fam }
  OPTIONAL { ?art schema:about ?m ; schema:isPartOf <https://en.wikipedia.org/> }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
} ORDER BY ?start"""


def wikidata(name, q):
    path = os.path.join(CACHE, name + ".json")
    if not os.path.exists(path):
        url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": q})
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
            open(path, "wb").write(r.read())
        time.sleep(2)
    rows = json.load(open(path))["results"]["bindings"]
    return [{k: v["value"] for k, v in b.items()} for b in rows]


def build_england():
    rows = wikidata("monarchs_england_uk", SPARQL)
    by = {}
    for r in rows:
        key = urllib.parse.unquote(r.get("art", "").rsplit("/", 1)[-1])
        w = by.setdefault(key, {"name": r["mLabel"], "qid": r["m"].rsplit("/", 1)[1], "houses": set(), "years": set()})
        if r.get("famLabel"):
            w["houses"].add(r["famLabel"])
        if r.get("start"):
            w["years"].add(int(r["start"][:4]))
    out, problems = [], []
    for m in RD.MONARCHS:  # hand table after Wikipedia's lists of English and British monarchs
        key = m["url"].rsplit("/", 1)[1]
        w = by.get(key)
        if not w:
            problems.append(f"{m['name']}: not found in Wikidata positions")
        else:
            if m["from"] not in w["years"]:
                problems.append(f"{m['name']}: Wikipedia {m['from']}, Wikidata start {sorted(w['years'])}")
            pats = [RD.HOUSE_MATCH[m["house"]]] + RD.HOUSE_ALT.get(m["house"], [])
            if not any(p in h for h in w["houses"] for p in pats):
                problems.append(f"{m['name']}: house {m['house']}, Wikidata {sorted(w['houses'])}")
        out.append({**m, "qid": w["qid"] if w else None, "wikidataHouse": sorted(w["houses"]) if w else []})
    print("Wikidata vs Wikipedia:", len(problems), "differences")
    for p in problems:
        print("  ", p)
    d = {"source": "wikidata", "asOf": "2026-10-14", "retrieved": TODAY,
         "note": "Kings and queens of England (871/927-1707), Great Britain (1707-1801) and the United Kingdom (1801-), one row "
                 "per reign. Names, years and houses typed from Wikipedia's 'List of English monarchs' and 'List of British "
                 "monarchs' and checked against Wikidata (P39 position held: monarch of England Q18810062, King of Ireland "
                 "Q18810066, monarch of the UK Q111722535/Q9134365, with start qualifiers and P53 family). Alfred is counted "
                 "from 871, when he became king of Wessex (Wikidata); Wikipedia's English list starts his reign c. 886 as king "
                 "of the Anglo-Saxons. Disputed claimants (Matilda, Louis, Edgar Aetheling) are left out; Lady Jane Grey is in. "
                 "Differences found: " + ("; ".join(problems) or "none"),
         "monarchs": out}
    dump(os.path.join(HIST, "royals-england.json"), d)
    return out


# ---------------------------------------------------------------- historical-basemaps: realms of the crowns
HB = os.path.join(ROOT, ".cache", "hre", "hb")


def build_realms():
    feats = []
    snaps = [s for s, _ in RD.REALMS]
    for i, (snap, keep) in enumerate(RD.REALMS):
        nxt = snaps[i + 1] if i + 1 < len(snaps) else None
        g = json.load(open(os.path.join(HB, f"{snap}.geojson")))
        for f in g["features"]:
            nm = f["properties"].get("NAME")
            if nm in keep and f["geometry"]:
                group, label = keep[nm]
                feats.append({"type": "Feature", "geometry": f["geometry"],
                              "properties": {"name": label, "from": snap, "to": nxt, "group": group,
                                             "note": f"historical-basemaps world_{snap}: '{nm}'"}})
    src = os.path.join(CACHE, "realms.geojson")
    json.dump({"type": "FeatureCollection", "features": feats}, open(src, "w"))
    tmp = os.path.join(CACHE, "realms.topo.json")
    ms(src, "-clip", "bbox=-12,40,6,61.5", "-simplify", "weighted", "40%", "keep-shapes",
       "-filter-islands", "min-area=60km2", "-rename-layers", "shapes", "-o", tmp, "format=topojson",
       "quantization=20000", "force")
    t = json.load(open(tmp))
    d = {"source": "historical-basemaps", "asOf": "2026-09-15", "retrieved": TODAY,
         "licence": "GPL-3.0 (derived from historical-basemaps; this file stays under the GNU GPL v3)",
         "note": "Lands of the English (later British) and Scottish crowns from historical-basemaps by André Ourednik "
                 "(snapshot maps for the years shown; each shape holds until the next snapshot). Approximate: the maps "
                 "draw whole Ireland under the English crown from 1500, although royal control reached beyond Dublin only "
                 "in the 1500s-1600s, and leave out Normandy (1066-1204) and Calais (to 1558).",
         "groups": RD.REALM_GROUPS, "topology": t}
    dump(os.path.join(HIST, "royals-realms.json"), d)


# ---------------------------------------------------------------- hand-typed sets
def build_cards():
    for name, (kinds, items) in RD.CARDS.items():
        for it in items:
            assert it.get("source") and it.get("url"), it["title"]
        d = {"source": "editorial", "asOf": "2026-10-14", "retrieved": TODAY,
             "note": "Event cards typed by Orbis from the cited Wikipedia articles. Dates are Gregorian; cards marked Julian "
                     "show the Julian date their sources use (England kept the Julian calendar until 1752).",
             "kinds": kinds, "items": items}
        dump(os.path.join(HIST, f"royals-cards-{name}.json"), d)


def build_cousins():
    dump(os.path.join(HIST, "royals-cousins.json"), RD.COUSINS)


def build_today():
    dump(os.path.join(HIST, "royals-today.json"), RD.TODAY_SETS)


if __name__ == "__main__":
    units = build_geo()
    print(len(units), "areas:", " ".join(units))
    build_crowns(units)
    build_england()
    build_realms()
    build_cards()
    build_cousins()
    build_today()
