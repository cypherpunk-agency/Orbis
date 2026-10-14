#!/usr/bin/env python3
"""Data for the Holy Roman Empire series (chapters hre-origins, hre-patchwork, hre-westphalia, hre-end).

Writes:
  data/geo/regions/hre-cities.json   ~2,390 city "areas of influence" (Princes & Townspeople, CC0) as a region set
  data/history/hre-rulers.json       who ruled each city, 1300-1807: ruler codes + change lists (Princes & Townspeople, CC0)
  data/history/hre-ruler-counts.json cities per ruling house, every 10 years 1300-1789 (same source; for a line chart)
  data/history/hre-outline.json      the Empire's outline 800-1715 + neighbours (historical-basemaps, GPL-3.0: file stays GPL-3.0)
  data/history/hre-circles.json      Imperial Circles 1648 and 1792 + Empire outline from them (HistoGIS / IEG-Maps; treated as BY-NC)
  data/history/hre-territories-1500s.json  16th-century territories by confession (ETH Zurich, Roller 2021, CC BY-NC-SA 4.0: stays BY-NC-SA)

Sources (licences re-read at the primary pages, 14 Oct 2026):
- Princes and Townspeople (Cantoni, Mohr, Weigand), Harvard Dataverse, all volumes "CC0 1.0" (dataset metadata, API):
  1: City Locations and Border Maps  doi:10.7910/DVN/ZGSJED   (city_borders.zip: weighted-Voronoi "areas of influence"
     that partition Germany in its 1937 borders; the authors offer them as "a sufficient approximation of the area
     controlled by a territory", explicitly "not ... actual borders")
  2: Territorial Histories           doi:10.7910/DVN/GZPPVE   (v4, 2024: cities_dynasties.tab panel 1300-1789,
     territories_all.tab rule episodes to 1918, territory_codes.tab)
- historical-basemaps by André Ourednik, github.com/aourednik/historical-basemaps, GNU GPL v3, pinned commit da7a4b73.
- HistoGIS (ACDH-CH, Austrian Academy of Sciences), "Holy Roman Empire Imperial Circles 1648" (source 220) and "... 1792"
  (source 217) by Anna Piechl, vectorised from A. Kunz, "Reichskreise 1648/1792", IEG-Maps (Mainz). ARCHE lists the
  features as CC BY 4.0; because they are traced from IEG-Maps (personal-use / CC BY-NC terms) Orbis treats them as BY-NC.
- ETH Zurich Research Collection, Ramona Roller, "Spatio-temporal data on territories of the Holy Roman Empire"
  (hdl 20.500.11850/472583, 2021), CC BY-NC-SA 4.0. Traced by hand from the maps in Schindling & Ziegler (eds.),
  "Die Territorien des Reichs im Zeitalter der Reformation und Konfessionalisierung" (1989-), attributes from Wikipedia.

Downloads go to .cache/hre/ (gitignored). Run from anywhere: python3 tools/build/hre_series.py
"""
import collections, csv, glob, json, os, re, subprocess, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(ROOT, ".cache", "hre")
OUT = os.path.join(ROOT, "data", "history")
GEO = os.path.join(ROOT, "data", "geo", "regions")
MS = os.path.join(ROOT, "tools", "node_modules", "mapshaper", "bin", "mapshaper")
for d in (CACHE, OUT, GEO, os.path.join(CACHE, "eth"), os.path.join(CACHE, "hg"), os.path.join(CACHE, "hb")):
    os.makedirs(d, exist_ok=True)
TODAY = time.strftime("%Y-%m-%d")
UA = {"User-Agent": "Orbis-data-build/1.0"}


def fetch(url, path, tries=4):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    for k in range(tries):
        try:
            print("download", url, file=sys.stderr)
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
                data = r.read()
            open(path, "wb").write(data)
            return path
        except Exception as e:  # the HistoGIS server resets connections now and then
            print("  retry", e, file=sys.stderr); time.sleep(3)
    raise SystemExit("failed: " + url)


def ms(args):
    subprocess.run(["node", MS, "-quiet"] + args, check=True)


def dump(obj, path):
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    open(path, "w", encoding="utf-8").write(s)
    print("wrote", os.path.relpath(path, ROOT), len(s.encode()) // 1024, "KB", file=sys.stderr)


def rd(path):
    return list(csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"))


# ---------------------------------------------------------------- downloads
DV = "https://dataverse.harvard.edu/api/access/datafile/%s"
PT_FILES = {"cities_dynasties.tab": 10047015, "territories_all.tab": 10047017, "territory_codes.tab": 4099956,
            "territory_documentation.pdf": 10047031, "city_locations.tab": 5588458, "city_documentation.pdf": 5588457,
            "city_borders.zip": 4099959}
for f, i in PT_FILES.items():
    fetch(DV % i, os.path.join(CACHE, f))
if not os.path.exists(os.path.join(CACHE, "city_borders", "city_borders.shp")):
    subprocess.run(["unzip", "-o", "-q", os.path.join(CACHE, "city_borders.zip"), "-d", os.path.join(CACHE, "city_borders")], check=True)

ETH = "https://www.research-collection.ethz.ch/server/api/core/bitstreams/%s/content"
ETH_FILES = {"territories_manual.shp": "3291edf3-6d4c-4b18-a8af-420da09c6355", "territories_manual.shx": "b1c670ba-a88e-4cea-9218-82ba07fec0fe",
             "territories_manual.dbf": "4a74aa26-c5f0-4829-89e6-9f64c0c5e0d6", "territories_manual.prj": "754ba5f9-e460-4ec2-b4e9-3a897194804b",
             "territories_manual.cpg": "8c6515ed-6471-4d35-85b0-3003aff34e8b", "README.md": "9f64c59e-a035-4590-9f4a-b569e7b8f0a8"}
for f, i in ETH_FILES.items():
    fetch(ETH % i, os.path.join(CACHE, "eth", f))

HG = "https://histogis.acdh.oeaw.ac.at/api/tempspatial/%d/?format=json"
HG_IDS = list(range(12044, 12055)) + list(range(11998, 12009))   # 1648 (source 220), 1792 (source 217)
for i in HG_IDS:
    fetch(HG % i, os.path.join(CACHE, "hg", "%d.json" % i))

HB = "https://raw.githubusercontent.com/aourednik/historical-basemaps/da7a4b735ecef70aebdc9c73e409d8a2500d50f3/geojson/world_%s.geojson"
HB_SNAPS = [800, 900, 1000, 1300, 1500, 1650]
for y in HB_SNAPS:
    fetch(HB % y, os.path.join(CACHE, "hb", "%d.geojson" % y))

# ---------------------------------------------------------------- Princes & Townspeople: cells
cells = os.path.join(CACHE, "cells.json")
ms(["-i", os.path.join(CACHE, "city_borders", "city_borders.shp"), "-proj", "wgs84", "-simplify", "3%", "keep-shapes",
    "-each", 'name=name_forei?name_alt+" ("+name_forei+")":name_alt', "-filter-fields", "city_id,name",
    "-rename-layers", "regions", "-o", cells, "format=topojson", "id-field=city_id", "quantization=6000"])
topo = json.load(open(cells, encoding="utf-8"))
for g in topo["objects"]["regions"]["geometries"]:
    g["properties"].pop("city_id", None)
    g["id"] = str(g["id"])
dump(topo, os.path.join(GEO, "hre-cities.json"))
CITY_IDS = {g["id"] for g in topo["objects"]["regions"]["geometries"]}

# ---------------------------------------------------------------- Princes & Townspeople: rulers
codes = {r["terr_id"]: r["terr_name"] for r in rd(os.path.join(CACHE, "territory_codes.tab"))}
rows = rd(os.path.join(CACHE, "territories_all.tab"))
# a ruler code counts as a self-governing city when most of its episodes carry a free/imperial city status
_st = collections.defaultdict(list)
for r in rows:
    if r["terr_id"]:
        _st[r["terr_id"]].append(r["city_status"] in ("1", "2", "3"))
CITYLIKE = {k for k, v in _st.items() if sum(v) > len(v) / 2}

# categories: ruling house, or kind of ruler
CATS = {"habsburg": "Habsburg", "hohenzollern": "Hohenzollern (Brandenburg-Prussia)", "wittelsbach": "Wittelsbach (Bavaria, Palatinate)",
        "wettin": "Wettin (Saxony)", "church": "Church: bishops, abbots, orders", "cities": "Free and imperial cities",
        "foreign": "Foreign crowns; Napoleon's France", "other": "Other princes, counts and lords"}
FOREIGN_IDS = {"P121", "F117", "D015", "S412", "S567", "0R0003", "0V0012", "0V0013", "0J0011", "0P0041", "0W0041",
               "1N0001", "1B0001", "1M0001", "1L0001"}
CHURCH_IDS = {"P004", "F208", "E066", "H309", "H044", "C016", "M169", "M205", "C111", "Q004", "G324", "E098", "W061", "F141",
              "L102", "S343", "F127", "V040", "D063", "J028", "0S0108", "M136", "N037", "B373", "S431", "L315", "R083", "P020",
              "K170", "A268", "W461", "S581", "S729", "S077", "H247", "W224", "E196", "W488", "M010", "B425", "K148", "M027", "T141",
              "M328", "W487", "B043", "O136", "H309"}
CITY_IDS_R = {"H061", "A002", "B426", "L316", "D105", "K149", "G178", "D147", "N198", "N236", "U018", "S362", "A270", "R331", "S421", "0R0001"}


def classify(tid):
    n = codes.get(tid, "") or ""
    if tid in FOREIGN_IDS: return "foreign"
    if tid in CITY_IDS_R or tid in CITYLIKE or re.search(r"Reichsstadt|Reichsdorf|freie Stadt|Reichsvogtei", n): return "cities"
    if tid in CHURCH_IDS or re.search(r"Erzstift|Hochstift|Stift\b|Abtei|Kloster|Orden|Bistum|Propstei|Domkapitel|Kommende|Johanniter|Deutschmeister|Reichsstift", n, re.I): return "church"
    if re.search(r"Habsburg|Österreich|Tirol|Toskana", n): return "habsburg"
    if re.search(r"Hohenzollern|^Brandenburg-|Ansbach|Bayreuth|Kulmbach|^Preußen|Nürnberg \(Burggraf|Küstrin", n) and not re.search(r"Sigmaringen|Hechingen|Haigerloch|Straßburger", n): return "hohenzollern"
    if re.search(r"Albertiner|Ernestiner|Wettin|^Sachsen-(?!Lauenburg)|Meißen \(Mark", n): return "wettin"
    if re.search(r"Bayern|Pfalz|Wittelsbach|Niederbayern|Oberbayern", n) and not re.search(r"Hochstift|Falkenstein", n): return "wittelsbach"
    if re.search(r"Vasa|Jagiellonen \(Polen\)|Poniatowski|Herzogtum Warschau|Dänemark|Schweden|Polen\b", n): return "foreign"
    if not tid or tid == "0U0001": return None
    return "other"


# readable labels for the most common rulers (the code list is German, with title lists in brackets)
LABELS = {
    "B3742": "Brandenburg-Prussia (Hohenzollern)", "A060": "Albertine Wettins (Electors of Saxony; kings of Poland 1697-1763)", "W289": "Wettin family (Saxony, Thuringia)",
    "W480": "Württemberg", "H0101": "Habsburg (Austrian line)", "H0103": "Habsburg (Austrian line of Charles VI)", "H0102": "Habsburg (Ferdinand's line)",
    "H0104": "Habsburg (Spanish line)", "H010": "Habsburg", "T0851": "Habsburg Tyrol and Further Austria", "0H0076": "Habsburg-Este",
    "0F0033": "Ferdinand of Tuscany (Habsburg-Lorraine)", "P049": "Palatinate-Birkenfeld (Wittelsbach; Bavaria from 1799)",
    "H262": "Hesse (Hesse-Kassel)", "H266": "Hesse-Darmstadt", "K148": "Archbishopric-Electorate of Cologne", "M027": "Archbishopric-Electorate of Mainz",
    "T141": "Archbishopric-Electorate of Trier", "B108": "Bavaria-Munich (Wittelsbach)", "1N0001": "Napoleon's France", "A098": "Counts of Altena (Mark)",
    "L339": "Luxembourg kings of Bohemia", "O104": "Oldenburg kings of Denmark (Schleswig-Holstein)", "M328": "Prince-Bishopric of Münster",
    "D063": "Teutonic Order", "W487": "Prince-Bishopric of Würzburg", "B019": "Baden-Durlach", "B017": "Baden", "P058": "Palatinate-Sulzbach (Wittelsbach)",
    "C0031": "Brunswick-Lüneburg, Hanover (Welf)", "1B0001": "Jérôme Bonaparte (Kingdom of Westphalia)", "1M0001": "Joachim Murat (Grand Duchy of Berg)",
    "1L0001": "Louis Bonaparte (Holland)", "P054": "Palatinate-Neuburg (Wittelsbach)", "P047": "Electoral Palatinate (Wittelsbach)",
    "M010": "Archbishopric of Magdeburg", "0J0012": "Jagiellon kings of Bohemia", "0J0011": "Jagiellon kings of Poland", "A162": "Brandenburg-Ansbach (Hohenzollern)",
    "M116": "Mecklenburg-Schwerin", "M115": "Mecklenburg-Güstrow", "M114": "Mecklenburg", "B043": "Prince-Bishopric of Bamberg", "P004": "Prince-Bishopric of Paderborn",
    "B374": "Ascanian margraves of Brandenburg", "P128": "Pomerania (Griffins)", "L0071": "Brunswick-Lüneburg (Welf)", "P057": "Palatinate-Simmern (Wittelsbach)",
    "F208": "Abbey of Fulda", "J034": "Jülich-Berg-Ravensberg", "F213": "Fürstenberg", "S037": "Saxe-Lauenburg (Ascanians)", "0V0013": "Vasa kings of Poland",
    "0V0012": "Vasa kings of Sweden", "L243": "Lippe", "B376": "Brandenburg-Ansbach (Hohenzollern)", "B377": "Brandenburg-Bayreuth (Hohenzollern)",
    "A268": "Prince-Bishopric of Augsburg", "S031": "Saxe-Gotha (Ernestine Wettins)", "N030": "Nassau-Usingen", "W400": "Counts of Wittelsbach",
    "B4081": "Brunswick-Wolfenbüttel (Welf)", "B400": "Brunswick-Wolfenbüttel (Welf)", "0N0017": "Bavaria-Landshut (Wittelsbach)", "H044": "Bishopric of Halberstadt",
    "E066": "Prince-Bishopric of Eichstätt", "H309": "Prince-Bishopric of Hildesheim", "S253": "Holstein-Gottorp", "S581": "Prince-Bishopric of Speyer",
    "P156": "Duchy of Prussia (Hohenzollern)", "O136": "Prince-Bishopric of Osnabrück", "N236": "Free imperial city of Nuremberg", "S412": "Kingdom of Sweden",
    "P121": "Kingdom of Poland", "F117": "Kingdom of France", "D015": "Kingdom of Denmark", "S567": "Kingdom of Spain", "0R0001": "Imperial domain (the Emperor directly)",
    "U018": "Free imperial city of Ulm", "L316": "Free imperial city of Lübeck", "H061": "Free imperial city of Hamburg", "B426": "Free imperial city of Bremen",
    "A270": "Free imperial city of Augsburg", "A002": "Free imperial city of Aachen", "K149": "Free imperial city of Cologne", "B425": "Archbishopric of Bremen",
    "S077": "Archbishopric of Salzburg", "P166": "Přemyslid kings of Bohemia", "N235": "Burgraves of Nuremberg (Hohenzollern)", "K2342": "Brandenburg-Kulmbach (Hohenzollern)",
    "0U0001": "Unknown",
}
MOJI = {"Ã¼": "ü", "Ã¶": "ö", "Ã¤": "ä", "ÃŸ": "ß", "KÃönig": "König", "Ã–": "Ö", "FÃ¼": "Fü"}


def label(tid):
    if tid in LABELS: return LABELS[tid]
    n = codes.get(tid) or tid
    for a, b in MOJI.items(): n = n.replace(a, b)
    n = re.sub(r"\s*\([^()]*;[^()]*\)", "", n)          # drop bracketed title lists "(Grafen; Herzogtum; ...)"
    n = re.sub(r"\s+", " ", n).strip(" .;")
    return n[:70]


# 1300-1789: the authors' city-year panel (one ruler per city-year, primary timeline)
panel = collections.defaultdict(dict)
with open(os.path.join(CACHE, "cities_dynasties.tab"), encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        panel[r["city_id"]][int(r["year"])] = r["terr_id"] or "0U0001"
# 1790-1807: derived by Orbis from the episode table (primary timeline), same rule as the panel
prim = collections.defaultdict(list)
for r in rows:
    if r["commentary_primary"]:
        prim[r["city_id"]].append(r)


def episode_ruler(cid, y):
    best = None
    for r in prim[cid]:
        try: b = int(r["beginning_reign"])
        except ValueError: continue
        e = int(r["end_reign"]) if r["end_reign"] else 9999
        if b <= y < e: best = r
    return (best["terr_id"] or best["multiple_1"] or "0U0001") if best else "0U0001"


# check: the derivation agrees with the authors' panel in 1789 for ~99% of cities
agree = sum(1 for c in prim if episode_ruler(c, 1789) == panel[c].get(1789))
print("1789 agreement with panel:", agree, "/", len(prim), file=sys.stderr)

changes, used = {}, set()
for cid in sorted(CITY_IDS, key=int):
    seq = [(y, panel[cid].get(y, "0U0001")) for y in range(1300, 1790)] + [(y, episode_ruler(cid, y)) for y in range(1790, 1808)]
    out, last = [], None
    for y, c in seq:
        if c != last:
            out.append([y, c]); last = c; used.add(c)
    changes[cid] = out
code_tab = {c: {"label": label(c), "cat": classify(c)} for c in sorted(used)}
for c, v in code_tab.items():  # say what a self-governing city is when the code name is just the town
    if v["cat"] == "cities" and not re.match(r"(Free|Imperial)", v["label"]):
        v["label"] = "Self-governing city: " + re.sub(r"\s*\((Reichsstadt|Reichsvogteistadt|freie Stadt des Reiches)[^)]*\)", "", v["label"])
for c in code_tab:
    if code_tab[c]["cat"] is None: code_tab[c].pop("cat")
dump({"source": "princes-townspeople", "asOf": "2024-04-01", "retrieved": TODAY,
      "note": ("Ruler of each city in the Deutsches Städtebuch (2,390 towns that ever held town rights, within Germany's 1937 borders), "
               "by ruling lineage, from Princes and Townspeople vol. 2 (Cantoni, Mohr, Weigand; CC0). 1300-1789: the authors' city-year panel "
               "(cities_dynasties, primary ruler; where several lords shared a city the authors picked one at random). 1790-1807: derived by Orbis "
               "from the authors' rule episodes with the same rule (agrees with their panel for %d of %d cities in 1789). Groups of lineages "
               "(Habsburg, Hohenzollern, ...) and English labels by Orbis. Areas are the authors' interpolated areas of influence, not real borders." % (agree, len(prim))),
      "sets": {"rulers": {"label": "Who ruled the city", "labels": CATS, "codes": code_tab, "changes": changes}}},
     os.path.join(OUT, "hre-rulers.json"))

# counts per category every 10 years (line chart)
YRS = list(range(1300, 1790, 10)) + [1789]
cnt = {k: [] for k in CATS}
for y in YRS:
    c = collections.Counter()
    for cid, ch in changes.items():
        code = None
        for yy, cc in ch:
            if yy <= y: code = cc
        cat = code_tab.get(code, {}).get("cat")
        if cat: c[cat] += 1
    for k in CATS: cnt[k].append(c[k])
dump({"source": "princes-townspeople", "asOf": "2024-04-01", "retrieved": TODAY, "years": YRS,
      "note": "Number of Städtebuch towns (within Germany's 1937 borders) ruled by each group, from hre-rulers.json.",
      "series": {"cities": {"label": "Towns ruled", "units": "towns", "values": cnt}}}, os.path.join(OUT, "hre-ruler-counts.json"))

# ---------------------------------------------------------------- historical-basemaps: outlines (GPL-3.0)
BOX = (-6, 36, 28, 59)
EMPIRE = {"Carolingian Empire", "Holy Roman Empire", "East Francia", "Duchy of Swabia"}
WEST = {"West Francia", "Kingdom of France", "France"}
LEFT = {"Swiss Confederation", "Dutch Republic"}
SHORT = {"Carolingian Empire": "Frankish Empire", "East Francia": "East Francia", "West Francia": "West Francia",
         "Holy Roman Empire": "Holy Roman Empire", "Duchy of Swabia": "Holy Roman Empire"}
feats = []
for k, y in enumerate(HB_SNAPS):
    to = HB_SNAPS[k + 1] if k + 1 < len(HB_SNAPS) else 1715
    if y == 1650: frm = 1648
    else: frm = y
    if k + 1 < len(HB_SNAPS) and HB_SNAPS[k + 1] == 1650: to = 1648
    d = json.load(open(os.path.join(CACHE, "hb", "%d.geojson" % y), encoding="utf-8"))
    for f in d["features"]:
        p = f["properties"]; n = p.get("NAME") or ""
        if not f["geometry"] or not n: continue
        if y == 800 and n == "Carolingian Empire": grp = "frankish"
        elif y == 900 and n == "Carolingian Empire": grp = "middle"
        elif y == 900 and n == "East Francia": grp = "frankish"
        elif n in EMPIRE or p.get("PARTOF") == "Holy Roman Empire": grp = "empire"
        elif y == 900 and n == "Carolingian Empire": grp = "middle"
        elif n in WEST: grp = "francia" if y == 900 else "france"
        elif n in LEFT: grp = "left"
        elif n == "Sweden": grp = "sweden"
        else: grp = "other"
        nm = SHORT.get(n, n)
        if y == 900 and n == "Carolingian Empire": nm = "Middle kingdoms (Lotharingia, Burgundy, Italy)"
        feats.append({"type": "Feature", "geometry": f["geometry"],
                      "properties": {"name": nm, "from": frm, "to": to, "group": grp, "snap": y}})
# process each snapshot on its own (overlapping snapshots must not be dissolved together), then join them in one topology
parts = []
for y in HB_SNAPS:
    gj = os.path.join(CACHE, "hb_sel_%d.geojson" % y)
    json.dump({"type": "FeatureCollection", "features": [f for f in feats if f["properties"]["snap"] == y]}, open(gj, "w", encoding="utf-8"), ensure_ascii=False)
    o = os.path.join(CACHE, "hb_sel_%d.out.geojson" % y)
    ms(["-i", gj, "-clip", "bbox=%d,%d,%d,%d" % BOX, "-filter", "this.area > 4e8 || group=='empire' || group=='left'",
        "-dissolve2", "name,from,to,group,snap", "-simplify", "6%", "keep-shapes", "-filter-slivers", "min-area=200km2", "-o", o, "format=geojson"])
    parts += json.load(open(o, encoding="utf-8"))["features"]
gj = os.path.join(CACHE, "hb_sel.geojson")
json.dump({"type": "FeatureCollection", "features": parts}, open(gj, "w", encoding="utf-8"), ensure_ascii=False)
tmp = os.path.join(CACHE, "hb_sel.topo.json")
ms(["-i", gj, "-rename-layers", "shapes", "-o", tmp, "format=topojson", "quantization=20000"])
t = json.load(open(tmp, encoding="utf-8"))
for g in t["objects"]["shapes"]["geometries"]:
    g["properties"].pop("snap", None)
dump({"source": "historical-basemaps", "asOf": "2026-09-15", "retrieved": TODAY,
      "licence": "GPL-3.0 (derived from historical-basemaps; this file stays under the GNU GPL v3)",
      "note": ("Borders: historical-basemaps by André Ourednik (commit da7a4b7), snapshots 800, 900, 1000, 1300, 1500 and 1650; each shown until "
               "the next snapshot (1500 until 1648, 1650 until 1714). The project marks these borders as approximate; Orbis clipped them to Europe and simplified them. "
               "Not used after 1714: the source's 1715 Empire polygon is incomplete and from 1783 it splits the Empire into its states."),
      "groups": {"frankish": {"label": "Frankish Empire; East Francia", "color": "c2"}, "empire": {"label": "Holy Roman Empire", "color": "c2"},
                 "middle": {"label": "Middle Frankish kingdoms", "color": "c5"},
                 "francia": {"label": "West Francia", "color": "c1"}, "france": {"label": "France", "color": "c1"}, "left": {"label": "Left the Empire in 1648", "color": "c4"},
                 "sweden": {"label": "Sweden", "color": "c3"}, "other": {"label": "Other states", "color": "muted"}},
      "topology": t}, os.path.join(OUT, "hre-outline.json"))

# ---------------------------------------------------------------- HistoGIS Imperial Circles (treated as BY-NC)
EN = {"Fränkischer Kreis": "Franconian", "Niederrheinisch-Westfälischer Kreis": "Lower Rhenish-Westphalian", "Obersächsischer Kreis": "Upper Saxon",
      "Niedersächsischer Kreis": "Lower Saxon", "Bayerischer Kreis": "Bavarian", "Burgundischer Kreis": "Burgundian", "Österreichischer Kreis": "Austrian",
      "Schwäbischer Kreis": "Swabian", "Kurrheinischer Kreis": "Electoral Rhenish", "Oberrheinischer Kreis": "Upper Rhenish",
      "Kreisfreies Gebiet": "Outside the circles"}
# five colours so that neighbouring circles differ
COL = {"Austrian": "c3", "Bavarian": "c1", "Swabian": "c4", "Franconian": "c5", "Upper Rhenish": "c2", "Electoral Rhenish": "c6", "Lower Rhenish-Westphalian": "c7", "Lower Saxon": "c8", "Upper Saxon": "s1", "Burgundian": "s3", "Outside the circles": "muted"}
cf = []
for i in HG_IDS:
    d = json.load(open(os.path.join(CACHE, "hg", "%d.json" % i), encoding="utf-8"))
    p = d["properties"]; en = EN[p["name"]]; y = int(p["start_date"][:4])
    cf.append({"type": "Feature", "geometry": d["geometry"],
               "properties": {"name": en + (" Circle" if en != "Outside the circles" else ""), "name_de": p["name"], "from": 1648 if y == 1648 else 1792,
                              "to": 1792 if y == 1648 else 1806, "group": "k-" + en.lower().replace(" ", "-"), "circle": en}})
parts = []
for yr in (1648, 1792):  # each year on its own: the two sets overlap and must not be dissolved together
    gj = os.path.join(CACHE, "circles_%d.geojson" % yr)
    json.dump({"type": "FeatureCollection", "features": [f for f in cf if f["properties"]["from"] == yr]}, open(gj, "w", encoding="utf-8"), ensure_ascii=False)
    o1 = os.path.join(CACHE, "circles_%d.s.geojson" % yr); o2 = os.path.join(CACHE, "circles_%d.e.geojson" % yr)
    ms(["-i", gj, "-simplify", "8%", "keep-shapes", "-filter-fields", "name,name_de,from,to,group", "-o", o1, "format=geojson"])
    ms(["-i", o1, "-dissolve2", "from,to", "-each", "name='Holy Roman Empire', group='empire'", "-filter-slivers", "min-area=30km2", "-o", o2, "format=geojson"])
    parts += json.load(open(o1, encoding="utf-8"))["features"] + json.load(open(o2, encoding="utf-8"))["features"]
gj = os.path.join(CACHE, "circles.geojson")
json.dump({"type": "FeatureCollection", "features": parts}, open(gj, "w", encoding="utf-8"), ensure_ascii=False)
tmp = os.path.join(CACHE, "circles.topo.json")
ms(["-i", gj, "-rename-layers", "shapes", "-o", tmp, "format=topojson", "quantization=20000"])
t = json.load(open(tmp, encoding="utf-8"))
groups = {"k-" + en.lower().replace(" ", "-"): {"label": en + (" Circle" if en != "Outside the circles" else " (Bohemian crown lands, parts of northern Italy)"),
                                                 "color": COL[en]} for en in EN.values()}
groups["empire"] = {"label": "Holy Roman Empire", "color": "c2"}
dump({"source": "histogis-circles", "asOf": "2021-01-01", "retrieved": TODAY,
      "licence": "Treated as CC BY-NC 4.0 (HistoGIS states CC BY 4.0, but the shapes are vectorised from IEG-Maps)",
      "note": ("Imperial Circles in 1648 (shown 1648-1791) and 1792 (shown 1792-1805): Anna Piechl, HistoGIS (ACDH-CH, Austrian Academy of Sciences), "
               "based on Andreas Kunz, 'Reichskreise 1648' and 'Reichskreise 1792', IEG-Maps, Leibniz Institute of European History, Mainz; georeferenced "
               "with OpenStreetMap. 'Outside the circles' is the source's 'Kreisfreies Gebiet' (Bohemia, Moravia, Silesia, Lusatia and parts of northern Italy). "
               "The Empire outline is the union of all shapes, computed by Orbis; the rest of Imperial Italy is not in the source."),
      "groups": groups, "topology": t}, os.path.join(OUT, "hre-circles.json"))

# ---------------------------------------------------------------- ETH Zurich 16th-century territories (CC BY-NC-SA)
eg = os.path.join(CACHE, "eth_terr.geojson")
ms(["-i", os.path.join(CACHE, "eth", "territories_manual.shp"), "-proj", "wgs84", "-o", eg, "format=geojson"])
d = json.load(open(eg, encoding="utf-8"))


def conf(r):
    r = (r or "").lower().strip()
    if not r: return "unknown"
    parts = {x.strip() for x in r.split(",")}
    parts = {"reformed" if x == "calvinist" else x for x in parts}
    if parts == {"roman-catholic"}: return "catholic"
    if parts == {"lutheran"}: return "lutheran"
    if parts == {"reformed"}: return "reformed"
    if parts <= {"roman-catholic", "lutheran", "reformed", "mixed", "free", "unclear"} and len(parts - {"unclear"}) > 1 or parts == {"mixed"}: return "mixed"
    return "unknown"


ef = []
for f in d["features"]:
    p = f["properties"]
    if not f["geometry"]: continue
    a = p.get("start_rel") or p.get("start"); b = p.get("end_rel")
    if b is None: b = p.get("end")
    if a is None: a = 1500
    a = max(int(a), 1500)
    if b is not None and int(b) <= a: continue
    kind = p.get("ecc") or p.get("secular") or ""
    ef.append({"type": "Feature", "geometry": f["geometry"],
               "properties": {"name": p["name"], "from": a, "to": int(b) if b is not None else None, "group": conf(p.get("religion")),
                              "note": (kind + "; " if kind else "") + "confession: " + (p.get("religion") or "unknown")}})
gj = os.path.join(CACHE, "eth_sel.geojson")
json.dump({"type": "FeatureCollection", "features": ef}, open(gj, "w", encoding="utf-8"), ensure_ascii=False)
tmp = os.path.join(CACHE, "eth_sel.topo.json")
ms(["-i", gj, "-simplify", "5%", "keep-shapes", "-rename-layers", "shapes", "-o", tmp, "format=topojson", "quantization=20000"])
t = json.load(open(tmp, encoding="utf-8"))
dump({"source": "eth-hre-territories", "asOf": "2021-03-02", "retrieved": TODAY,
      "licence": "CC BY-NC-SA 4.0 (derived from Roller 2021; this file stays under CC BY-NC-SA 4.0)",
      "note": ("Territories of the Holy Roman Empire in the 16th century: Ramona Roller, 'Spatio-temporal data on territories of the Holy Roman Empire', "
               "ETH Zurich Research Collection, 2021 (CC BY-NC-SA 4.0). Borders traced by the author from the maps in Schindling & Ziegler, 'Die Territorien "
               "des Reichs im Zeitalter der Reformation und Konfessionalisierung' (1989-97); confessions and dates looked up on Wikipedia by the author. "
               "Research data of uneven quality: coverage is incomplete (no Habsburg hereditary lands, Bohemia or imperial knights), and dates come from "
               "Wikipedia. One feature per territory and confession period; Orbis grouped 'calvinist' with 'reformed' and simplified the borders."),
      "groups": {"catholic": {"label": "Catholic", "color": "c3"}, "lutheran": {"label": "Lutheran", "color": "c1"},
                 "reformed": {"label": "Reformed (Calvinist)", "color": "c4"}, "mixed": {"label": "Mixed or several", "color": "c5"},
                 "unknown": {"label": "Other or unknown", "color": "muted"}},
      "topology": t}, os.path.join(OUT, "hre-territories-1500s.json"))
print("done", file=sys.stderr)
