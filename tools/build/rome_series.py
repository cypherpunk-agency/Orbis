#!/usr/bin/env python3
"""Data for the Roman Empire series (chapters rome-rise, rome-frontier, rome-fall).

Writes, under data/history/:
  rome-hb-ancient.json  shapes over time, 500 BC – AD 500   (historical-basemaps, GPL-3.0: this derived file stays GPL-3.0)
  rome-hb-late.json     shapes over time, AD 400 – 1500     (historical-basemaps, GPL-3.0: this derived file stays GPL-3.0)
  rome-awmc.json        Roman state extent 60 BC, AD 117, AD 200 + frontier walls (AWMC geodata, ODbL 1.0: stays ODbL)
  rome-places.json      cities with their names by period + Roman forts (Pleiades, CC BY 3.0)

Sources (licences re-read at the primary pages, 14 Oct 2026):
- historical-basemaps by André Ourednik, https://github.com/aourednik/historical-basemaps, LICENSE = GNU GPL v3.
  Pinned commit da7a4b73 (15 Sep 2026). One snapshot per century; every border is BORDERPRECISION 1 ("approximate").
- AWMC geodata, Ancient World Mapping Center (UNC), https://github.com/AWMC/geodata, README: "The GeoJson files are offered
  under the ODC Open Database License"; derived from the Barrington Atlas of the Greek and Roman World. Pinned commit 7ecf8bcc.
- Pleiades gazetteer, https://pleiades.stoa.org (CC BY 3.0), places dump pleiades-places-latest.csv.gz (shared cache with
  tools/build/roman_roads.py).

The two share-alike sources are kept in separate files (GPL and ODbL are not compatible with each other); a scene may show both
as separate layers. Event cards are hand-entered in stories/rome-*.json datasets data/history/rome-events.json (editorial).
"""
import csv, gzip, json, os, subprocess, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(ROOT, ".cache", "rome")
OUT = os.path.join(ROOT, "data", "history")
MS = os.path.join(ROOT, "tools", "node_modules", "mapshaper", "bin", "mapshaper")
os.makedirs(CACHE, exist_ok=True)
TODAY = time.strftime("%Y-%m-%d")
UA = {"User-Agent": "Orbis-data-build/1.0"}
HB = "https://raw.githubusercontent.com/aourednik/historical-basemaps/da7a4b735ecef70aebdc9c73e409d8a2500d50f3/geojson/world_%s.geojson"
AW = "https://raw.githubusercontent.com/AWMC/geodata/7ecf8bccea2efe1e1e9df2daf6001942de73fb87/Cultural-Data/"
PURL = "https://atlantides.org/downloads/pleiades/dumps/pleiades-places-latest.csv.gz"


def fetch(url, path):
    if not os.path.exists(path):
        print("download", url, file=sys.stderr)
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
            data = r.read()
        open(path, "wb").write(data)
    return path


def ms(args):
    subprocess.run(["node", MS, "-quiet"] + args, check=True)


# ---------- historical-basemaps: groups ----------
ROME = {"Rome", "Roman Republic", "Roman Empire"}
CARTHAGE = {"Carthaginian Empire", "Carthage"}
GREEK = {"Greek city-states", "Greek colonies", "Empire of Alexander", "Kingdom of Antigonus", "Kingdom of Kassander",
         "Kingdom of Lysimachus", "Ptolemaic Kingdom", "Seleucid Kingdom", "Macedon and Hellenic League", "Pergamon"}
PERSIA = {"Achaemenid Empire", "Parthia", "Parthian Empire", "Persia", "Sasanian Empire"}
GERMANIC = {"Visigoths", "Visigothic Kingdom", "Vandals", "Ostrogoths", "Franks", "Frankish Kingdom", "Neustria", "Burgundians",
            "Suebi", "Lombard principalities", "Lombard duchies", "Alamans", "Gepids", "Turingians"}
MUSLIM = {"Umayyad Caliphate", "Abbasid Caliphate", "Aghlabid Emirate", "Idrisid Caliphate", "Emirate of Córdoba",
          "Caliphate of Córdoba", "Emirate of Sicily", "Fatimid Caliphate", "Buwayhid Emirates", "Seljuk Empire",
          "Seljuk Caliphate", "Almoravid dynasty", "Almohad Caliphate", "Mamluke Sultanate", "Hafsid Caliphate", "Granada",
          "Merinides", "Abdelouadides", "Zayyanid Caliphate", "Wattasid Caliphate", "Saffarids"}
SHORT = {"Rome (Diocletianus)": "Diocletian", "Rome (Maximian)": "Maximian", "Rome (Galerius)": "Galerius",
         "Rome (Constantinus)": "Constantius", "Carthaginian Empire": "Carthage", "Roman Republic": "Rome", "Roman Empire": "Rome",
         "Macedon and Hellenic League": "Macedon", "Eastern Roman Empire": "Eastern Empire", "Western Roman Empire": "Western Empire"}


def group_of(name, subj):
    if name in ROME or name.startswith("Rome ("):
        return "rome"
    if subj == "Roman Empire":
        return "client"
    if name in CARTHAGE: return "carthage"
    if name in ("Etrurians", "Sabini", "Sabines", "Samnites"): return "italic"
    if name in GREEK or subj == "Greek city-states": return "greek"
    if name in PERSIA: return "persia"
    if name == "Western Roman Empire": return "west"
    if name in ("Eastern Roman Empire", "Byzantine Empire"): return "east"
    if name in GERMANIC or subj in ("Frankish Kingdom",) or name == "Hunnic Empire" or subj == "Hunnic Empire": return "germanic"
    if name in MUSLIM or subj == "Umayyad Caliphate": return "muslim"
    if name == "Ottoman Empire" or subj == "Ottoman Empire": return "ottoman"
    return "other"


def snap_label(s):  # 'bc500' -> -499 (astronomical), '100' -> 100
    return -(int(s[2:]) - 1) if s.startswith("bc") else int(s)


def hb_file(snaps, windows, out, groups, note, fixes=None):
    """snaps: list of snapshot keys; windows: {key: (from, to)}; fixes: {(key, NAME): {props}} renames for known errors"""
    feats = []
    for s in snaps:
        raw = fetch(HB % s, os.path.join(CACHE, "hb_%s.geojson" % s))
        tmp = os.path.join(CACHE, "hb_%s_s.geojson" % s)
        # clip to Europe, North Africa and the Near East; simplify; drop slivers
        ms(["-i", raw, "-clip", "bbox=-14,14,66,61", "-filter-slivers", "min-area=50km2", "-simplify", "weighted", "25%",
            "keep-shapes", "-filter", "!!NAME", "-o", tmp, "format=geojson", "precision=0.01", "force"])
        fr, to = windows[s]
        for f in json.load(open(tmp))["features"]:
            p = f["properties"]; n = (p.get("NAME") or "").strip(); subj = (p.get("SUBJECTO") or "").strip()
            if not n or "hunter" in n or n == "None": continue
            g = group_of(n, subj)
            q = {"name": n, "from": fr, "to": to, "group": g}
            if n in SHORT: q["label"] = SHORT[n]
            if subj and subj != n and g in ("client", "other"): q["note"] = "under " + subj
            if fixes and (s, n) in fixes: q.update(fixes[(s, n)])
            if q.get("drop"): continue
            feats.append({"type": "Feature", "properties": q, "geometry": f["geometry"]})
    tmp = os.path.join(CACHE, os.path.basename(out) + ".geojson")
    json.dump({"type": "FeatureCollection", "features": feats}, open(tmp, "w"))
    topo = os.path.join(CACHE, os.path.basename(out) + ".topo.json")
    ms(["-i", tmp, "-rename-layers", "shapes", "-o", topo, "format=topojson", "quantization=20000", "force"])
    t = json.load(open(topo))
    d = {"source": "historical-basemaps", "asOf": "2026-09-15", "retrieved": TODAY,
         "licence": "GPL-3.0 (derived from historical-basemaps; this file stays under the GNU GPL v3)",
         "note": note, "groups": groups, "topology": t}
    json.dump(d, open(out, "w"), separators=(",", ":"), ensure_ascii=False)
    print(out, os.path.getsize(out) // 1024, "KB", len(feats), "features", file=sys.stderr)


ANC = ["bc500", "bc400", "bc300", "bc200", "bc100", "bc1", "100", "200", "300", "400"]
LATE = ["400", "500", "600", "700", "800", "900", "1000", "1100", "1200", "1279", "1300", "1400", "1492"]
def windows(keys, first, last):
    w = {}
    for i, k in enumerate(keys):
        a = snap_label(k) if i else first
        b = snap_label(keys[i + 1]) if i + 1 < len(keys) else last
        w[k] = (a, b)
    return w

HBNOTE = ("Borders: historical-basemaps by André Ourednik (GitHub aourednik/historical-basemaps, commit da7a4b7 of 15 Sep 2026, "
          "GPL-3.0). One map per century (500 BC, 400 BC … AD 1500); each is shown from its year until the next one. The project "
          "marks every border here as approximate (BORDERPRECISION 1) and asks users to check it against other sources. Orbis "
          "clipped the maps to Europe, North Africa and the Near East, simplified them (about 3% of points kept) and grouped "
          "polities by colour. This derived file is distributed under the GNU GPL v3, like its source.")

hb_file(ANC, windows(ANC, -800, 500), os.path.join(OUT, "rome-hb-ancient.json"), {
    "rome": {"label": "Rome", "color": "c2"},
    "client": {"label": "Client kingdoms of Rome", "color": "c5"},
    "carthage": {"label": "Carthage", "color": "c3"},
    "italic": {"label": "Other peoples of Italy", "color": "muted"},
    "greek": {"label": "Greek and Hellenistic states", "color": "c1"},
    "persia": {"label": "Persian empires", "color": "c4"},
    "west": {"label": "Western Roman Empire", "color": "c2"},
    "east": {"label": "Eastern Roman Empire", "color": "c1"},
    "germanic": {"label": "Goths, Franks, Huns and other peoples", "color": "c3"},
    "muslim": {"label": "Muslim states", "color": "c4"},
    "ottoman": {"label": "Ottoman Empire", "color": "c5"},
    "other": {"label": "Other peoples and states", "color": "muted"}}, HBNOTE,
    # for AD 200 the stories use the more precise AWMC outline (rome-awmc.json) instead of this map's Roman Empire
    {("200", "Roman Empire"): {"drop": True}})

# the AD 500 map still has a 'Western Roman Empire' in northern Gaul: the rump Roman state of Aegidius and Syagrius
# (Domain of Soissons, 457-486; Wikipedia 'Domain of Soissons'). It is relabelled so the map does not suggest the empire lived on.
# the AD 700 map still draws a Sasanian Empire, which fell to the Arabs in 651 (Wikipedia 'Sasanian Empire'): removed
FIX = {("700", "Sasanian Empire"): {"drop": True}, ("500", "Western Roman Empire"): {"group": "other", "label": "Domain of Soissons", "name": "Domain of Soissons (Roman rump state in northern Gaul, to 486)"}}
hb_file(LATE, windows(LATE, 395, 1600), os.path.join(OUT, "rome-hb-late.json"), {
    "west": {"label": "Western Roman Empire", "color": "c2"},
    "east": {"label": "Eastern Roman (Byzantine) Empire", "color": "c1"},
    "germanic": {"label": "Germanic kingdoms and the Huns", "color": "c3"},
    "muslim": {"label": "Muslim states", "color": "c4"},
    "persia": {"label": "Sasanian Persia", "color": "c5"},
    "ottoman": {"label": "Ottoman Empire", "color": "c5"},
    "rome": {"label": "Rome", "color": "c2"}, "client": {"label": "Client kingdoms", "color": "c5"},
    "carthage": {"label": "Carthage", "color": "c3"}, "greek": {"label": "Greek states", "color": "c1"},
    "other": {"label": "Other peoples and states", "color": "muted"}}, HBNOTE, FIX)

# ---------- AWMC: Roman extent 60 BC, AD 117, AD 200 and frontier walls ----------
EXT = [("roman_empire_bce_60/roman_empire_bce_60.geojson", "Roman Republic, 60 BC", -59, 0),
       ("roman_empire_ce_117_extent/roman_empire_ce_117_extent.geojson", "Roman Empire, AD 117", 117, 200),
       ("roman_empire_ce_200_extent/roman_empire_ce_200_extent.geojson", "Roman Empire, AD 200", 200, 300)]
feats, areas = [], {}
for rel, name, fr, to in EXT:
    raw = fetch(AW + "political_shading/" + rel, os.path.join(CACHE, "awmc_" + os.path.basename(rel)))
    tmp = raw.replace(".geojson", "_d.geojson")
    ms(["-i", raw, "-dissolve", "-filter-slivers", "min-area=300km2", "-simplify", "weighted", "8%", "keep-shapes",
        "-each", "area=this.area", "-o", tmp, "format=geojson", "precision=0.01", "force"])
    f = json.load(open(tmp))["features"][0]
    km2 = round(f["properties"]["area"] / 1e6, -4)
    areas[name] = km2
    lab = {-59: [16, 41], 117: [24, 41], 200: [24, 41]}[fr]
    feats.append({"type": "Feature", "geometry": f["geometry"],
                  "properties": {"name": name, "label": name.split(",")[0], "from": fr, "to": to, "group": "rome", "at": lab,
                                 "note": "about %s million km²" % format(km2 / 1e6, ".1f")}})
tmp = os.path.join(CACHE, "awmc_ext.geojson"); json.dump({"type": "FeatureCollection", "features": feats}, open(tmp, "w"))
topo = os.path.join(CACHE, "awmc_ext.topo.json")
ms(["-i", tmp, "-rename-layers", "shapes", "-o", topo, "format=topojson", "quantization=20000", "force"])

# walls: unnamed in AWMC; named here by location (Wikipedia articles cited in the stories' notes)
WALLS = [("Hadrian's Wall", (-3.3, -1.4, 54.8, 55.1), 122), ("Antonine Wall", (-4.6, -3.5, 55.8, 56.1), 142),
         ("Upper German-Raetian Limes", (6.4, 12.0, 48.7, 50.6), 100), ("Fossatum Africae", (4.9, 13.0, 31.7, 36.0), 100)]
raw = fetch(AW + "walls/walls.geojson", os.path.join(CACHE, "awmc_walls.geojson"))
walls = {}
for f in json.load(open(raw))["features"]:
    for line in f["geometry"]["coordinates"]:
        xs = [p[0] for p in line]; ys = [p[1] for p in line]
        nm = next((n for n, (x0, x1, y0, y1), _ in WALLS if x0 <= min(xs) and max(xs) <= x1 and y0 <= min(ys) and max(ys) <= y1), None)
        if not nm: continue
        walls.setdefault(nm, []).append([[round(p[0], 3), round(p[1], 3)] for p in line])
lines = []
for nm, parts in walls.items():
    for i, path in enumerate(parts):
        if len(path) < 2: continue
        lines.append({"name": nm, "path": path})
print("walls", {k: len(v) for k, v in walls.items()}, file=sys.stderr)
aw = {"source": "awmc", "asOf": "2024-04-22", "retrieved": TODAY,
      "licence": "ODbL 1.0 (derived from AWMC geodata; this file stays under the ODbL)",
      "note": ("Ancient World Mapping Center geodata (GitHub AWMC/geodata, commit 7ecf8bc of 22 Apr 2024, ODbL 1.0), derived from "
               "the Barrington Atlas of the Greek and Roman World. Extent layers 'roman_empire_bce_60', 'roman_empire_ce_117_extent' "
               "and 'roman_empire_ce_200_extent', dissolved and simplified by Orbis (about 8% of points kept). Areas computed by Orbis "
               "on the sphere from the simplified outline, rounded to 10,000 km²: " +
               "; ".join("%s %s km²" % (k, format(int(v), ",")) for k, v in areas.items()) +
               ". Walls: AWMC 'walls' layer, which carries no names; Orbis named four by location (Hadrian's Wall, Antonine Wall, "
               "Upper German-Raetian Limes, Fossatum Africae) and left the rest out."),
      "areas": areas,
      "groups": {"rome": {"label": "Roman state (AWMC, after the Barrington Atlas)", "color": "c2"}},
      "topology": json.load(open(topo)), "lines": {"walls": lines}}
p = os.path.join(OUT, "rome-awmc.json"); json.dump(aw, open(p, "w"), separators=(",", ":"), ensure_ascii=False)
print(p, os.path.getsize(p) // 1024, "KB", areas, file=sys.stderr)

# ---------- Pleiades: cities with names by period, and Roman forts ----------
pl = {r["id"]: r for r in csv.DictReader(gzip.open(fetch(PURL, os.path.join(ROOT, ".cache", "roman_roads", "pleiades-places.csv.gz")), "rt", encoding="utf-8"))}
# (Pleiades id, [(name, from, to)]) — astronomical years; sources for each change in stories' notes and below
CITIES = [
    ("423025", [("Roma", None, None)]),
    ("314921", [("Carthago", None, -145), ("Carthago", -44, 698)]),            # destroyed 146 BC, colony refounded 44 BC; Arab conquest 698
    ("520985", [("Byzantium", None, 330)]), ("520998", [("Constantinople", 330, 1453), ("Istanbul", 1453, None)]),  # Wikipedia 'Constantinople'
    ("79574", [("Londinium", 47, 410)]),                                         # founded c. AD 47-50 (Wikipedia 'Londinium')
    ("109126", [("Lutetia", -52, 360), ("Parisius", 360, None)]),               # renamed c. AD 360 (Wikipedia 'Lutetia')
    ("383706", [("Mediolanum", None, None)]),
    ("393480", [("Ravenna", None, None)]),
    ("108894", [("Augusta Treverorum", -15, None)]),
    ("108751", [("Colonia Agrippina", 50, None)]),
    ("128537", [("Vindobona", 50, None)]),
    ("197130", [("Aquincum", 89, None)]),
    ("207447", [("Sirmium", None, None)]),
    ("511337", [("Nicomedia", None, None)]),
    ("658381", [("Antiochia", -299, None)]),
    ("727070", [("Alexandria", -330, None)]),
    ("687928", [("Hierosolyma", None, 130), ("Aelia Capitolina", 130, 325), ("Hierosolyma", 325, None)]),  # Wikipedia 'Aelia Capitolina'
    ("148127", [("Massilia", -599, None)]),
    ("246349", [("Tarraco", -217, None)]),
    ("256177", [("Gades", None, None)]),
    ("265849", [("Carthago Nova", -226, None)]),
    ("89175", [("Eboracum", 71, None)]),
    ("167717", [("Lugdunum", -42, None)]),
    ("579885", [("Athenae", None, None)]),
    ("491741", [("Thessalonica", -314, None)]),
    ("893976", [("Ctesiphon", -119, 637)]),
    ("462503", [("Syracusae", None, None)]),
    ("432754", [("Capua", None, None)]),
    ("442509", [("Brundisium", None, None)]),
    ("246347", [("Narbo Martius", -117, None)]),
    ("256128", [("Corduba", -168, None)]),
    ("256155", [("Emerita Augusta", -24, None)]),
    ("344448", [("Lepcis Magna", None, None)]),
    ("599612", [("Ephesus", None, None)]),
    ("668331", [("Palmyra", None, None)]),
    ("678106", [("Damascus", None, None)]),
    ("207439", [("Serdica", None, None)]),
    ("187290", [("Aquileia", -180, None)]),
    ("207425", [("Sarmizegetusa", None, 106)]),
]
places = []
for pid, names in CITIES:
    r = pl[pid]
    places.append({"at": [round(float(r["reprLong"]), 2), round(float(r["reprLat"]), 2)], "pleiades": int(pid),
                   "names": [dict({"name": n}, **({"from": a} if a is not None else {}), **({"to": b} if b is not None else {})) for n, a, b in names]})
FORT = {"fort", "fort-2", "fortlet", "fortress", "fort-group"}
forts = []
for r in pl.values():
    ft = {t.strip() for t in r["featureTypes"].split(",")}
    per = r["timePeriodsKeys"]
    if not (ft & FORT) or not r["reprLat"]: continue
    if "roman" not in per and "late-antique" not in per: continue
    forts.append({"name": r["title"], "at": [round(float(r["reprLong"]), 2), round(float(r["reprLat"]), 2)]})
forts.sort(key=lambda x: (x["at"][0], x["at"][1]))
pd = {"source": "pleiades", "asOf": "2026-10-13", "retrieved": TODAY,
      "note": ("Pleiades gazetteer of ancient places (pleiades.stoa.org, CC BY 3.0), daily dump of 13 Oct 2026. Cities: the Pleiades "
               "representative point; names and the years they changed are Orbis's, from the Wikipedia article on each city "
               "(Constantinople 330, Aelia Capitolina 130, Lutetia renamed Parisius c. 360). Forts: every Pleiades place typed "
               "fort, fortlet or fortress with a Roman or Late Antique period (%d places); dating within the period is not used." % len(forts)),
      "places": places, "points": {"forts": forts}, "count": {"forts": len(forts)}}
p = os.path.join(OUT, "rome-places.json"); json.dump(pd, open(p, "w"), separators=(",", ":"), ensure_ascii=False)
print(p, os.path.getsize(p) // 1024, "KB", len(forts), "forts", file=sys.stderr)
