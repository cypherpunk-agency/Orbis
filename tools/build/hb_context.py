#!/usr/bin/env python3
"""Period context for historical scenes: states (hard borders) and peoples/cultures (soft "influence" areas).

Writes, under data/history/:
  hb-context-ancient.json   shapes over time, 2000 BC – AD 600      (historical-basemaps, GPL-3.0: this derived file stays GPL-3.0)
  hb-context-late.json      shapes over time, AD 800 – 1866        (historical-basemaps, GPL-3.0: this derived file stays GPL-3.0)

Used by the scenes of rome-carthage, rome-expansion, rome-frontier, rome-split, rome-fall, rome-legacy, roman-roads,
hre-charlemagne, hre-after, tr-anatolia and tr-ottoman-world that hide today's borders ("modernBorders": false). Other HRE chapters
reuse data/history/hre-outline.json (tools/build/hre_series.py).

Source and licence (re-read at the primary page, 14 Oct 2026):
- historical-basemaps by André Ourednik, https://github.com/aourednik/historical-basemaps, LICENSE = GNU GPL v3.
  Pinned commit da7a4b73 (15 Sep 2026), the same commit as tools/build/rome_series.py, hre_series.py and colonial_series.py.
  Already registered as `historical-basemaps` (story-layer tier). Every border is BORDERPRECISION 1 ("approximate").

Method
- Only the snapshots the scenes need are used, each clipped to the region those scenes show (BOX), simplified like the
  Rome series (mapshaper, weighted 25%, slivers under 50 km² dropped) and dissolved by name.
- Every named polygon is assigned a group by its NAME (and SUBJECTO for vassals), from the explicit lists below; an unknown
  name stops the build. Groups are either STATES (drawn with hard borders) or PEOPLES / NOMADS (cultures, tribes,
  confederations and collective areas such as "minor states" or "city-states", drawn as soft "influence" areas in the
  stories). Unnamed polygons are left out.
- Validity: a snapshot holds from its year until the next historical-basemaps snapshot, except where a major documented
  change falls between two maps (WINDOWS: e.g. the 100 BC map is not shown after 58 BC, when Caesar's conquest of Gaul
  began). Years in such gaps show no period map. Astronomical years (0 = 1 BC).
- Corrections (FIX): relabels of names the source gets wrong for its date, and two anachronistic polygons left out;
  each is explained next to the entry and in the file's "note".

Run: python3 tools/build/hb_context.py   (needs shapely and the mapshaper CLI: npm install in tools/)
Downloads are cached in .cache/hb/ (gitignored).
"""
import json, os, subprocess, sys, time, urllib.request
from shapely.geometry import shape, mapping, MultiPolygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely import make_valid

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(ROOT, ".cache", "hb")
OUT = os.path.join(ROOT, "data", "history")
MS = os.path.join(ROOT, "tools", "node_modules", "mapshaper", "bin", "mapshaper")
os.makedirs(CACHE, exist_ok=True)
TODAY = time.strftime("%Y-%m-%d")
UA = {"User-Agent": "Orbis-data-build/1.0"}
HB = "https://raw.githubusercontent.com/aourednik/historical-basemaps/da7a4b735ecef70aebdc9c73e409d8a2500d50f3/geojson/world_%s.geojson"


def fetch(snap):
    path = os.path.join(CACHE, "world_%s.geojson" % snap)
    if not os.path.exists(path):
        print("download", HB % snap, file=sys.stderr)
        with urllib.request.urlopen(urllib.request.Request(HB % snap, headers=UA), timeout=300) as r:
            data = r.read()
        open(path, "wb").write(data)
    return path


def ms(args):
    subprocess.run(["node", MS, "-quiet"] + args, check=True)


MED = (-12, 22, 52, 60)       # Europe, North Africa, the Near East (as in rome_series.py)
ANA = (24, 28, 50, 44)        # Anatolia and its neighbours
EUR = (-12, 34, 40, 60)       # Europe (Carolingian scenes)
CAU = (24, 30, 52, 46)        # Anatolia, the Caucasus, Mesopotamia
EAST = (10, 22, 52, 50)       # eastern Mediterranean, Balkans, Near East
CEN = (0, 40, 35, 56)         # central Europe (1815: only the Austrian Empire is kept, see KEEP)

# snapshot key -> (from, to, clip box). `to` is exclusive. Reasons for windows that differ from "until the next snapshot":
ANCIENT = {
    "bc2000": (-1999, -1499, ANA),
    "bc200": (-199, -144, MED),   # until 146 BC (destruction of Carthage and Corinth; new provinces Africa and Macedonia)
    "bc100": (-99, -57, MED),     # until 58 BC (Caesar's conquest of Gaul begins)
    "bc1": (-29, 44, MED),        # from 30 BC (Egypt annexed; Augustus) to AD 43 (conquest of Britain begins)
    "100": (44, 106, MED),        # AD 43 to 106 (Trajan's conquest of Dacia; the AD 100 map has Dacia independent)
    "200": (106, 293, MED),       # AD 106 to 293 (the Tetrarchy, drawn in the AD 300 map)
    "300": (293, 395, MED),       # Tetrarchy 293-324 as drawn; 324-395 the same area as one Roman Empire (see TETRARCHY)
    "400": (395, 476, MED),       # from the division of 395 (as rome_series.py) to the end of the western court, 476
    "500": (476, 600, MED),       # from 476: the AD 500 map shows the kingdoms that followed the western empire
}
LATE = {
    "800": (800, 843, EUR),       # until the Treaty of Verdun (843) divided the Carolingian Empire
    "1000": (1000, 1045, CAU),    # until Byzantium annexed Bagratid Armenia (1045)
    "1279": (1279, 1300, EAST),
    "1400": (1400, 1453, EAST),   # until the Ottoman conquest of Constantinople
    "1492": (1453, 1516, EAST),   # from 1453; the source's 1500 map is the same in this region; until Selim I's conquests (1516)
    "1530": (1516, 1600, EAST),   # from 1516-17 (Mamluk Syria and Egypt become Ottoman)
    "1815": (1815, 1866, CEN),    # Congress of Vienna until the Austro-Prussian War
}
TETRARCHY_END = 324
OVERLORDS = {"Roman Empire", "Ottoman Empire", "Mongol Empire", "Hunnic Empire", "Khazars", "Nogai Horde", "Austrian Empire"}  # Constantine sole emperor

GROUPS_ANCIENT = {
    "rome": {"label": "Rome", "color": "c2"},
    "east": {"label": "Eastern Roman Empire", "color": "c1"},
    "client": {"label": "Client kingdoms of Rome", "color": "c5"},
    "carthage": {"label": "Carthage", "color": "c3"},
    "hellenistic": {"label": "Hellenistic kingdoms", "color": "c1"},
    "persia": {"label": "Parthian and Sasanian Persia", "color": "c4"},
    "germanic": {"label": "Germanic kingdoms", "color": "c3"},
    "states": {"label": "Other states", "color": "muted"},
    "peoples": {"label": "Peoples and cultures", "color": "c8"},
    "nomads": {"label": "Nomadic peoples", "color": "c6"},
}
GROUPS_LATE = {
    "frankish": {"label": "Carolingian Empire", "color": "c2"},
    "empire": {"label": "Holy Roman Empire", "color": "c2"},
    "byzantine": {"label": "Byzantine Empire", "color": "c1"},
    "ottoman": {"label": "Ottoman Empire", "color": "c7"},
    "turkic": {"label": "Seljuk and other Turkic states", "color": "c3"},
    "muslim": {"label": "Caliphates and other Muslim states", "color": "c4"},
    "mongol": {"label": "Mongol and Tatar khanates", "color": "c5"},
    "austria": {"label": "Austrian Empire", "color": "c1"},
    "states": {"label": "Other states", "color": "muted"},
    "peoples": {"label": "Peoples and cultures", "color": "c8"},
    "nomads": {"label": "Nomadic peoples", "color": "c6"},
}
STATES = {"rome", "east", "client", "carthage", "hellenistic", "persia", "germanic", "states",
          "frankish", "empire", "byzantine", "ottoman", "turkic", "muslim", "mongol", "austria"}

# names in historical-basemaps' own spelling -> group
NAMES = {
    # --- ancient states
    "Rome": "rome", "Roman Republic": "rome", "Roman Empire": "rome", "Western Roman Empire": "rome",
    "Rome (Maximian)": "rome", "Rome (Diocletianus)": "rome", "Rome (Constantinus)": "rome", "Rome (Galerius)": "rome",
    "Eastern Roman Empire": "east", "Carthage": "carthage",
    "Seleucid Kingdom": "hellenistic", "Ptolemaic Kingdom": "hellenistic", "Macedon and Hellenic League": "hellenistic",
    "Pergamon": "hellenistic", "Bosporan Kingdom": "hellenistic",
    "Parthian Empire": "persia", "Persia": "persia", "Sasanian Empire": "persia",
    "Ostrogoths@500": "germanic", "Visigoths@500": "germanic", "Franks@500": "germanic", "Vandals": "germanic",
    "Burgundians@500": "germanic", "Suebi": "germanic",
    "Numidia": "states", "Mauretania": "states", "Kingdom of Syphax": "states", "Kingdom of Gala": "states",
    "Nabatean Kingdom": "states", "Armenia": "states", "Dacia": "states", "Meroe": "states", "Makkura": "states",
    "Himyarite Kingdom": "states", "Dardania": "states", "Maan": "states", "Ur": "states", "Egypt": "states", "Elam": "states",
    # --- ancient peoples and cultures (soft areas)
    "Celts": "peoples", "Dacians": "peoples", "Plain-Pottery culture": "peoples", "Brushed Pottery culture": "peoples",
    "Bell-shaped burials culture": "peoples", "Milograd culture": "peoples", "Eastern Masurian culture": "peoples",
    "Western Masurian culture": "peoples", "Pomeranian culture": "peoples", "Curonians": "peoples",
    "Sambian-Nothangian culture": "peoples", "Norsemen": "peoples", "Boihaenum": "peoples", "Dumonii": "peoples",
    "Heruli": "peoples", "Geats": "peoples", "Swedes": "peoples", "Alamans": "peoples", "Franks@400": "peoples",
    "Burgundians@400": "peoples", "Visigoths@400": "peoples", "Ostrogoths@400": "peoples", "Gepids": "peoples",
    "Skirii": "peoples", "Akatziri": "peoples", "Saxons": "peoples", "Anglo-Saxons": "peoples", "Turingians": "peoples",
    "Basques": "peoples", "Armorica": "peoples", "Blemmyes": "peoples", "Finno-Ugric taiga hunter-gatherers": "peoples",
    "minor states": "peoples", "Semites": "peoples", "Anatolian tribes": "peoples", "Hittites": "peoples",
    "city-states": "peoples", "Hurrian Kingdoms": "peoples", "Canaan": "peoples", "Catacomb culture": "peoples",
    "Minoan": "peoples", "Cycladic": "peoples",
    "Coastal and Woodland Mesolithic Hunter-Foragers": "peoples", "Steppe Mesolithic Hunter-Foragers": "peoples",
    "Alluvial Lowland Mesolithic Hunter-Foragers": "peoples", "Highland Mesolithic Hunter-Foragers": "peoples",
    "Levantine Corridor (Neolithic Farmers)": "peoples", "Neolithic Farmers": "peoples",
    "Saharan pastoral nomads": "nomads", "Scythians": "nomads", "Sarmates": "nomads", "Alans": "nomads",
    "Caucasian Alans": "nomads", "Arabs": "nomads", "Hunnic Empire": "nomads",
    # --- medieval states
    "Carolingian Empire": "frankish", "Holy Roman Empire": "empire", "Byzantine Empire": "byzantine",
    "Ottoman Empire": "ottoman",
    "Seljuk Caliphate": "turkic", "Beylik of Aydin": "turkic", "Emirate of the White Sheep Turks": "turkic",
    "Emirate of Córdoba": "muslim", "Aghlabid Emirate": "muslim", "Abbasid Caliphate": "muslim", "Idrisid Caliphate": "muslim",
    "Fatimid Caliphate": "muslim", "Buwayhid Emirates": "muslim", "Mamluke Sultanate": "muslim", "Hafsid Caliphate": "muslim",
    "Safavid Empire": "muslim", "Muscat": "muslim",
    "Ilkhanate": "mongol", "Khanate of the Golden Horde": "mongol", "Golden Horde": "mongol", "Blue Horde": "mongol",
    "White Horde": "mongol", "Timurid Empire": "mongol", "Crimean Khanate": "mongol", "Nogai Horde": "mongol",
    "Astrakhan Khanate": "mongol", "Khiva Khanate": "mongol",
    "Papal States": "states", "Lombard duchies": "states", "Asturias": "states", "Mercia": "states", "Northumbria": "states",
    "Wessex": "states", "Essex": "states", "Kent": "states", "Britany": "states", "Bulgars": "states", "Cyprus": "states",
    "Bulgar Khanate": "states", "Kingdom of Georgia": "states", "Georgia": "states", "Shirvan": "states", "Arran": "states",
    "Kyivan Rus": "states", "Hungary": "states", "Kingdom of Hungary": "states", "Imperial Hungary": "states",
    "Serbia": "states", "Bosnia": "states", "Principality of Wallachia": "states", "Moldova": "states", "Trebizond": "states",
    "Venice": "states", "Sicily": "states", "Poland": "states", "Poland-Lithuania": "states", "Ryazan": "states",
    "Aragón": "states", "Naples": "states", "Florence": "states", "Swiss Confederation": "states", "Milan": "states",
    "Austrian Empire": "austria", "Venetia": "austria", "Lombardy": "austria", "Bavaria": "states", "Saxony": "states",
    "Prussia": "states", "Russian Empire": "states", "Republic of Kraków": "states", "Modena": "states", "Parma": "states",
    "Tuscany": "states", "Kingdom of Sardinia": "states", "Switzerland": "states",
    # --- medieval peoples
    "Slavonic tribes": "peoples", "Baltic tribes": "peoples", "Danes": "peoples", "Swedes and Goths": "peoples",
    "Northmen": "peoples", "Ests": "peoples", "Veps": "peoples", "Sámi": "peoples", "Finns": "peoples", "Czechs": "peoples",
    "Picts": "peoples", "Scots": "peoples", "Welsh": "peoples", "Celtic kingdoms": "peoples", "Irlanda": "peoples",
    "Rus' Khaganate": "peoples",
    "Avars": "nomads", "Khazars": "nomads", "Magyars": "nomads", "Peshemegs": "nomads", "Touareg": "nomads",
}
# corrections: (snapshot, NAME) -> properties to set; "drop" leaves the polygon out
FIX = {
    # the AD 300 map labels Persia "Parthian Empire"; the Sasanians had replaced the Parthians in 224
    ("300", "Parthian Empire"): {"name": "Sasanian Empire", "note": "labelled 'Parthian Empire' in the source"},
    # as in rome_series.py: the AD 500 'Western Roman Empire' is the rump state of Aegidius and Syagrius (457-486)
    ("500", "Western Roman Empire"): {"group": "states", "name": "Domain of Soissons (Roman rump state in northern Gaul, to 486)",
                                      "label": "Domain of Soissons"},
    # the Seljuks of Rum were sultans, not caliphs; in 1279 they ruled under Mongol (Ilkhanid) overlordship
    ("1279", "Seljuk Caliphate"): {"name": "Seljuk Sultanate of Rum", "note": "under Mongol (Ilkhanid) overlordship; 'Seljuk Caliphate' in the source"},
    # the Sultanate of Rum had ended by 1308; the 1400 map still draws it in eastern Anatolia: left out
    ("1400", "Seljuk Caliphate"): {"drop": True},
    # the 1400 map names Ottoman-ruled Bulgaria (conquered 1393-96) 'Bulgar Khanate'
    ("1400", "Bulgar Khanate"): {"name": "Bulgaria", "note": "under the Ottoman Empire since 1393-96"},
    ("1000", "Bulgar Khanate"): {"name": "Bulgarian Empire", "note": "'Bulgar Khanate' in the source"},
    ("1279", "Bulgar Khanate"): {"name": "Bulgarian Empire", "note": "'Bulgar Khanate' in the source"},
}
# snapshots of which only these polities are kept, whole (the source's 1815 map draws Frankfurt, Hamburg, Bremen and
# Lübeck inside neighbouring states and Thuringia as one state; its Austrian Empire is sound)
KEEP = {"1815": {"Austrian Empire", "Venetia", "Lombardy"}}
# label positions moved off a scene's own site marker, so both labels stay readable
LABEL_AT = {("bc2000", "Hittites"): [35.4, 41.1], ("1815", "Austrian Empire"): [19.6, 47.2]}
SHORT = {"Rome (Diocletianus)": "Diocletian", "Rome (Maximian)": "Maximian", "Rome (Galerius)": "Galerius",
         "Rome (Constantinus)": "Constantius", "Roman Republic": "Rome", "Roman Empire": "Rome",
         "Macedon and Hellenic League": "Macedon", "Eastern Roman Empire": "Eastern Empire", "Western Roman Empire": "Western Empire",
         "Emirate of the White Sheep Turks": "Aq Qoyunlu (White Sheep Turks)", "Mamluke Sultanate": "Mamluk Sultanate",
         "Khanate of the Golden Horde": "Golden Horde", "Levantine Corridor (Neolithic Farmers)": "Neolithic farmers"}


def group_of(snap, name, subj):
    if name + "@" + snap in NAMES: return NAMES[name + "@" + snap]
    if name in NAMES:
        g = NAMES[name]
        if g == "states" and subj == "Roman Empire": return "client"
        if g == "states" and subj == "Ottoman Empire": return "ottoman"
        return g
    if subj == "Roman Empire": return "client"
    raise SystemExit("unclassified polygon in %s: %r (SUBJECTO %r): add it to NAMES" % (snap, name, subj))


def build(snaps, out, groups, note):
    feats = []
    for s, (fr, to, box) in snaps.items():
        raw = fetch(s)
        tmp = os.path.join(CACHE, "ctx_%s.geojson" % s)
        ms(["-i", raw, "-clip", "bbox=%s" % ",".join(map(str, box)), "-filter-slivers", "min-area=50km2",
            "-simplify", "weighted", "25%", "keep-shapes", "-filter", "!!NAME", "-o", tmp, "format=geojson", "precision=0.01", "force"])
        snapf = []
        for f in json.load(open(tmp, encoding="utf-8"))["features"]:
            p = f["properties"]; n = (p.get("NAME") or "").strip(); subj = (p.get("SUBJECTO") or "").strip()
            if not n or n in ("?", "None") or not f["geometry"]: continue
            if s in KEEP and n not in KEEP[s]: continue
            q = {"name": n, "from": fr, "to": to, "group": group_of(s, n, subj), "label": "", "note": ""}  # empty keys dropped at the end
            if n in SHORT: q["label"] = SHORT[n]
            if subj in OVERLORDS and subj != n:
                q["note"] = "under " + subj
            q.update(FIX.get((s, n), {}))
            if q.pop("drop", False): continue
            snapf.append({"type": "Feature", "properties": q, "geometry": f["geometry"]})
        # one feature per name; each snapshot on its own (overlapping snapshots must not be dissolved together)
        sel = os.path.join(CACHE, "ctx_%s_sel.geojson" % s); dis = os.path.join(CACHE, "ctx_%s_dis.geojson" % s)
        json.dump({"type": "FeatureCollection", "features": snapf}, open(sel, "w", encoding="utf-8"), ensure_ascii=False)
        ms(["-i", sel, "-dissolve2", "name,from,to,group,label,note", "-o", dis, "format=geojson", "precision=0.01", "force"])
        snapf = [f for f in json.load(open(dis, encoding="utf-8"))["features"] if f["geometry"]]
        for f in snapf:
            if (s, f["properties"]["name"]) in LABEL_AT: f["properties"]["at"] = LABEL_AT[(s, f["properties"]["name"])]
        if s == "300":  # the Tetrarchy as drawn until 324, then the same area as one empire until 395
            tet = [f for f in snapf if f["properties"]["group"] == "rome"]
            for f in tet: f["properties"]["to"] = TETRARCHY_END
            u = unary_union([make_valid(shape(f["geometry"])) for f in tet]).buffer(0)
            u = MultiPolygon([orient(g, -1.0) for g in getattr(u, "geoms", [u]) if g.area > 0.01])  # clockwise outer rings
            snapf.append({"type": "Feature", "geometry": mapping(u), "properties": {
                "name": "Roman Empire", "label": "Rome", "from": TETRARCHY_END, "to": to, "group": "rome",
                "note": "the four Tetrarchy shares of the AD 300 map, merged"}})
        feats += snapf
    gj = os.path.join(CACHE, os.path.basename(out) + ".geojson")
    json.dump({"type": "FeatureCollection", "features": feats}, open(gj, "w", encoding="utf-8"), ensure_ascii=False)
    topo = os.path.join(CACHE, os.path.basename(out) + ".topo.json")
    # one shared topology for all snapshots
    ms(["-i", gj, "-rename-layers", "shapes", "-o", topo, "format=topojson", "quantization=20000", "force"])
    t = json.load(open(topo, encoding="utf-8"))
    for g in t["objects"]["shapes"]["geometries"]:
        p = g.get("properties") or {}
        for k in [k for k, v in p.items() if v in (None, "")]: p.pop(k)
    used = {g["properties"]["group"] for g in t["objects"]["shapes"]["geometries"]}
    d = {"source": "historical-basemaps", "asOf": "2026-09-15", "retrieved": TODAY,
         "licence": "GPL-3.0 (derived from historical-basemaps; this file stays under the GNU GPL v3)",
         "note": note, "kinds": {"states": sorted(g for g in groups if g in STATES and g in used),
                                 "influence": sorted(g for g in groups if g not in STATES and g in used)},
         "groups": {k: v for k, v in groups.items() if k in used}, "topology": t}
    json.dump(d, open(out, "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    print(out, os.path.getsize(out) // 1024, "KB", len(t["objects"]["shapes"]["geometries"]), "features", file=sys.stderr)


BASE = ("Borders: historical-basemaps by André Ourednik (GitHub aourednik/historical-basemaps, commit da7a4b7 of 15 Sep 2026, "
        "GPL-3.0). The project marks every border as approximate (BORDERPRECISION 1) and asks users to check it against other "
        "sources. Orbis clipped the maps to the regions its stories show, simplified them and grouped the polygons into states "
        "(drawn with borders) and peoples, cultures and nomadic groups (drawn as soft areas: their extent is an estimate). ")
NOTE_ANCIENT = BASE + (
    "Maps used: 2000 BC (Anatolia and its neighbours only), 200 BC, 100 BC, AD 1, 100, 200, 300, 400 and 500. "
    "Each is shown from its year until the next, except: 200 BC until 146 BC (Carthage destroyed); 100 BC until 58 BC "
    "(Caesar's Gallic War); AD 1 from 30 BC (Egypt annexed) to AD 43 (Britain invaded); AD 100 from AD 43 to 106 (Dacia "
    "conquered; this map still has Dacia independent); AD 200 from 106 to 293; AD 300 from 293 (its four Tetrarchy shares "
    "until 324, then merged as one empire until 395); AD 400 from 395 to 476; AD 500 from 476. In the gaps (300-146 BC, "
    "146-100 BC, 58-30 BC) no map is shown: the century maps would draw Rome's extent wrongly there. Corrections: the AD 300 "
    "map's 'Parthian Empire' is labelled Sasanian (from 224); the AD 500 map's 'Western Roman Empire' is the Domain of Soissons. "
    "Most 2000 BC areas are peoples and culture zones, not states. "
    "This derived file is distributed under the GNU GPL v3, like its source.")
NOTE_LATE = BASE + (
    "Maps used: AD 800 (Europe), 1000 (Anatolia and the Caucasus), 1279, 1400, 1492 and 1530 (eastern Mediterranean and Near "
    "East), 1815 (only the Austrian Empire: the source's 1815 map draws Frankfurt, Hamburg, Bremen and Lübeck inside "
    "neighbouring states and Thuringia as one state). Shown: 800 until 843 (Treaty of Verdun); 1000 until 1045 (Byzantium annexes Bagratid Armenia); 1279 until 1300; "
    "1400 until 1453; 1492 from 1453 (Constantinople Ottoman; the source's 1500 map is the same here) until 1516; 1530 from "
    "1516 (Mamluk Syria and Egypt conquered); 1815 until 1866. Corrections: 'Seljuk Caliphate' (1279) is shown as the Seljuk Sultanate of Rum; "
    "the 1400 map's Seljuk state in eastern Anatolia is left out (the sultanate had ended by 1308); 'Bulgar Khanate' is shown "
    "as the Bulgarian Empire (1000, 1279) and Ottoman Bulgaria (1400). Not used: the source's 1100 and 1200 maps, which still draw "
    "Byzantium across all of Anatolia (the Seljuks held its centre from the 1070s). "
    "This derived file is distributed under the GNU GPL v3, like its source.")

build(ANCIENT, os.path.join(OUT, "hb-context-ancient.json"), GROUPS_ANCIENT, NOTE_ANCIENT)
build(LATE, os.path.join(OUT, "hb-context-late.json"), GROUPS_LATE, NOTE_LATE)
