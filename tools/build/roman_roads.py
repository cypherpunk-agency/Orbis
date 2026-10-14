#!/usr/bin/env python3
"""Roman roads (Itiner-e 2024 static version) + major Roman cities (Pleiades) -> data/history/roman-roads*.json

Sources
- Itiner-e: de Soto, Pažout, Brughmans et al., "A High-Resolution Dataset of Roads of the Roman Empire: Itiner-e static
  version 2024", Zenodo 17122148 (v1.3, 2025-09-15), CC BY 4.0. https://doi.org/10.5281/zenodo.17122148
  Paper: Scientific Data (2025) https://doi.org/10.1038/s41597-025-06140-z
- Pleiades gazetteer of ancient places, CC BY 3.0, https://pleiades.stoa.org (coordinates of the city points below,
  read from the places dump https://atlantides.org/downloads/pleiades/dumps/pleiades-places-latest.csv.gz).

Pipeline: download itinere_roads.geojson (78 MB, EPSG:3395 World Mercator) into .cache/roman_roads/, unproject to lon/lat,
chain road sections that share endpoints (same road type and certainty) into longer polylines, simplify (Douglas-Peucker),
round to 0.01 degrees. Lengths are the dataset's own geodesic Shape_Leng (metres), summed before simplification.
Outputs (each < 300 KB):
  data/history/roman-roads.json        main roads, by certainty  (sets main_certain, main_conjectured, main_hypothetical)
  data/history/roman-roads-minor.json  secondary roads, by certainty
  data/history/roman-roads-named.json  named roads (Via Appia, ...), extremes and city points (Pleiades)
"""
import json, math, os, sys, time, urllib.request, collections

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(ROOT, ".cache", "roman_roads")
OUT = os.path.join(ROOT, "data", "history")
UA = {"User-Agent": "Orbis-data-build/1.0"}
URL = "https://zenodo.org/api/records/17122148/files/itinere_roads.geojson/content"
TODAY = time.strftime("%Y-%m-%d")
os.makedirs(CACHE, exist_ok=True)

def fetch(url, path):
    if not os.path.exists(path):
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=300) as r, open(path + ".part", "wb") as f:
            while True:
                b = r.read(1 << 20)
                if not b: break
                f.write(b)
        os.rename(path + ".part", path)
    return path

# ---- EPSG:3395 (WGS84 World Mercator) -> lon/lat
A, E = 6378137.0, 0.0818191908426215
def unproj(x, y):
    lon = math.degrees(x / A)
    t = math.exp(-y / A)
    phi = math.pi / 2 - 2 * math.atan(t)
    for _ in range(8):
        es = E * math.sin(phi)
        phi = math.pi / 2 - 2 * math.atan(t * ((1 - es) / (1 + es)) ** (E / 2))
    return lon, math.degrees(phi)

def hav(a, b):
    R = 6371.0088
    la1, la2 = math.radians(a[1]), math.radians(b[1])
    dl = math.radians(b[0] - a[0])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))

def dp(pts, tol):
    """Douglas-Peucker in degrees (longitude scaled by cos(lat))."""
    if len(pts) < 3: return pts
    keep = [False] * len(pts); keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1: continue
        ax, ay = pts[i]; bx, by = pts[j]
        k = math.cos(math.radians((ay + by) / 2))
        dx, dy = (bx - ax) * k, by - ay
        L2 = dx * dx + dy * dy
        best, bi = -1, -1
        for m in range(i + 1, j):
            px, py = (pts[m][0] - ax) * k, pts[m][1] - ay
            if L2 == 0: d = px * px + py * py
            else:
                t = max(0, min(1, (px * dx + py * dy) / L2))
                d = (px - t * dx) ** 2 + (py - t * dy) ** 2
            if d > best: best, bi = d, m
        if best > tol * tol:
            keep[bi] = True; stack += [(i, bi), (bi, j)]
    return [p for p, k in zip(pts, keep) if k]

def chain(lines):
    """Join polylines that meet end to end at nodes of degree 2."""
    key = lambda p: (round(p[0], 3), round(p[1], 3))
    ends = collections.defaultdict(list)
    for i, l in enumerate(lines):
        ends[key(l[0])].append(i); ends[key(l[-1])].append(i)
    used = [False] * len(lines); out = []
    def extend(path):
        while True:
            k = key(path[-1]); nxt = [i for i in ends[k] if not used[i]]
            if len(ends[k]) != 2 or len(nxt) != 1: return path
            i = nxt[0]; used[i] = True; l = lines[i]
            path = path + (l[1:] if key(l[0]) == k else l[::-1][1:])
    for i, l in enumerate(lines):
        if used[i]: continue
        used[i] = True
        p = extend(list(l))
        p = extend(p[::-1])
        out.append(p)
    return out

def rnd(path):
    q = []
    for x, y in path:
        p = [round(x, 2), round(y, 2)]
        if not q or q[-1] != p: q.append(p)
    return q

src = fetch(URL, os.path.join(CACHE, "itinere_roads.geojson"))
feats = json.load(open(src))["features"]

ALIAS = {"Via Popillia Capua-Rhegium": "Via Popillia", "Via Iulia Augusta": "Via Julia Augusta"}
sections = []  # (properties, lon/lat parts) of every feature, for the dated cards below
TYPE = {"Main Road": "main", "Secondary Road": "minor"}
CERT = {"Certain": "certain", "Conjectured": "conjectured", "Hypothetical": "hypothetical"}
groups = collections.defaultdict(list)
km = collections.Counter(); n = collections.Counter(); kmcheck = 0.0
named = collections.defaultdict(list); namedkm = collections.Counter()
bbox = [180, 90, -180, -90]; extreme = {}

NAMED = ["Via Appia", "Via Egnatia", "Via Domitia", "Via Hadriana", "Via Cassia", "Via Salaria", "Via Latina", "Via Valeria",
         "Via Popillia", "Via Claudia Augusta", "Via Sebaste",
         "Via Nova Traiana", "Via Flaminia", "Via Aurelia", "Via Aemilia", "Via Postumia", "Watling Street", "Ermine Street",
         "Fosse Way", "Dere Street", "Via Maris", "Strata Diocletiana", "Via Militaris", "Via Agrippae", "Via Traiana"]

for f in feats:
    p = f["properties"]
    t, c = TYPE[p["Type"]], CERT[p["Segment_s"]]
    L = p["Shape_Leng"] / 1000
    km[(t, c)] += L; n[(t, c)] += 1
    g = f["geometry"]
    parts = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
    its = [s.strip() for s in (p["Itinerary"] or "").split(",")]
    its = [ALIAS.get(s, s) for s in its]
    sections.append((p, []))
    for part in parts:
        ll = [unproj(q[0], q[1]) for q in part]
        kmcheck += sum(hav(ll[i], ll[i + 1]) for i in range(len(ll) - 1))
        for q in ll:
            for nm, better in (("north", q[1] > extreme.get("north", (0, -90))[1]), ("south", q[1] < extreme.get("south", (0, 90))[1]),
                               ("east", q[0] > extreme.get("east", (-180, 0))[0]), ("west", q[0] < extreme.get("west", (180, 0))[0])):
                if better: extreme[nm] = q
        groups[(t, c)].append(ll)
        sections[-1][1].append(ll)
        for nm in NAMED:
            if nm in its: named[nm].append(ll)
    for nm in NAMED:
        if nm in its: namedkm[nm] += L

total = sum(km.values())
print("features", len(feats), "total km (Shape_Leng)", round(total), "haversine check", round(kmcheck))
for k in sorted(km): print(k, n[k], round(km[k]))
print("extremes", {k: [round(v[0], 2), round(v[1], 2)] for k, v in extreme.items()})

TOL = {"main": 0.02, "minor": 0.055}
def build_sets(t):
    sets = {}
    for c in ("certain", "conjectured", "hypothetical"):
        ch = chain(groups[(t, c)])
        items = []
        for pth in ch:
            q = rnd(dp(pth, TOL[t]))
            if len(q) >= 2: items.append({"path": q})
        sets[f"{t}_{c}"] = items
        print(t, c, "sections", len(groups[(t, c)]), "-> chains", len(items))
    return sets

def summary():
    return {f"{t}_{c}": {"km": round(km[(t, c)]), "sections": n[(t, c)]} for t in TYPE.values() for c in CERT.values()}

note = ("Itiner-e static version 2024 (Zenodo 17122148, v1.3): 14,769 digitised road sections of the Roman Empire, c. 300 BC–AD 300. "
        "Certainty grades the spatial accuracy of the drawn course: 'certain' = well documented, within 50 m (mountains) or 200 m (plains); "
        "'conjectured' = road known, course less precisely documented; 'hypothetical' = road identified but not localised, tracks not fixed "
        "(deserts, flood plains), or speculated. Orbis joined sections end to end, simplified them (Douglas-Peucker, about 2 km for main and 5 km for secondary roads) and rounded to "
        "0.01°. Lengths ('km') are sums of the dataset's geodesic Shape_Leng before simplification.")
meta = {"source": "itinere", "asOf": "2025-09-15", "retrieved": TODAY, "note": note,
        "totals": {"km": round(total), "sections": len(feats), "byClass": summary()}}

def write(name, obj):
    path = os.path.join(OUT, name)
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    open(path, "w").write(s)
    print(name, len(s) // 1024, "KB")

write("roman-roads.json", dict(meta, lines=build_sets("main")))
write("roman-roads-minor.json", dict(meta, lines=build_sets("minor")))

# ---- named roads: each as one or more items (chained pieces), lightly simplified; one label point per road
nitems, nlabels = [], []
for nm in NAMED:
    pieces = [rnd(dp(pth, 0.01)) for pth in chain(named[nm])]
    pieces = [q for q in pieces if len(q) >= 2]
    for q in pieces: nitems.append({"name": nm, "path": q})
    if pieces:
        big = max(pieces, key=len)
        nlabels.append({"name": nm, "at": big[len(big) // 2], "r": 1.5})
print("named km", {k: round(v) for k, v in namedkm.items()})

# ---- cities from Pleiades (coordinates read from the place JSON; ids checked by title)
CITIES = [  # (Pleiades id, label); ids checked against the Pleiades title in the dump
    (423025, "Rome"), (727070, "Alexandria"), (658381, "Antioch"), (314921, "Carthage"), (520985, "Byzantium"),
    (599612, "Ephesus"), (79574, "Londinium"), (167717, "Lugdunum"), (89175, "Eboracum"), (108894, "Augusta Treverorum"),
    (383706, "Mediolanum"), (570182, "Corinth"), (579885, "Athens"), (687928, "Jerusalem"), (668331, "Palmyra"),
    (344448, "Lepcis Magna"), (256177, "Gades"), (246349, "Tarraco"), (256155, "Emerita Augusta"), (207447, "Sirmium"),
    (491741, "Thessalonica"), (893990, "Dura-Europos"), (275740, "Volubilis"), (108751, "Colonia Agrippina"),
    (785986, "Berenike"), (148127, "Massalia"), (442509, "Brundisium"), (432754, "Capua"), (857359, "Trapezus"),
    (197130, "Aquincum"), (678073, "Bostra"), (275736, "Tingi"), (511337, "Nicomedia"), (678106, "Damascus"),
    (678401, "Caesarea"), (786123, "Syene"), (305064, "Cirta"), (619103, "Ancyra"),
]
PURL = "https://atlantides.org/downloads/pleiades/dumps/pleiades-places-latest.csv.gz"
import csv, gzip
pl = {r["id"]: r for r in csv.DictReader(gzip.open(fetch(PURL, os.path.join(CACHE, "pleiades-places.csv.gz")), "rt", encoding="utf-8"))}
cities = []
for pid, label in CITIES:
    r = pl[str(pid)]
    print(pid, label, "|", r["title"], r["reprLong"], r["reprLat"])
    cities.append({"name": label, "at": [round(float(r["reprLong"]), 2), round(float(r["reprLat"]), 2)], "pleiades": pid})

# end points of the extreme sections (Itiner-e names: Crawford-Cramond, Dunqul-Qasr Ibrim Primis, Trapezous-Apsarus, Olisipo-Magnum Pr)
ext = [{"name": {"north": "Cramond", "south": "Primis (Qasr Ibrim)", "east": "Apsarus", "west": "Magnum Promontorium"}[k],
        "at": [round(v[0], 2), round(v[1], 2)]} for k, v in extreme.items()]
reach = {"northSouthKm": round(hav(extreme["north"], extreme["south"])), "westEastKm": round(hav(extreme["west"], extreme["east"]))}
print("reach", reach)

# ---- dated cards: when key roads were built. Dates come from Itiner-e's construction field (Cons_per_e: the magistrate or
# emperor under whom the road was built); each card sits on the sections that carry that value (and the road's name).
DOI = "https://doi.org/10.5281/zenodo.17122148"
CARDS = [  # (road in Itinerary or None, Cons_per_e value, date (astronomical year), kind, title, text)
    ("Via Appia", "Appius Claudius Caecus (312 BCE)", -311, "republic", "Via Appia",
     "The censor Appius Claudius Caecus builds Rome's first great road, south from Rome through Tarracina and Fundi to Capua."),
    ("Via Aurelia", "Gaius Aurelius Cotta (241 BCE)", -240, "republic", "Via Aurelia",
     "Gaius Aurelius Cotta lays out the coast road north-west from Rome into Etruria, towards Pisae."),
    ("Via Flaminia", "Gaius Flaminius Nepos (220-219 BCE)", -219, "republic", "Via Flaminia",
     "Gaius Flaminius builds the road across the Apennines from Rome to Fanum Fortunae and Ariminum on the Adriatic."),
    ("Via Aemilia", "Marcus Aemilius Lepidus (189-187 CE)", -186, "republic", "Via Aemilia",
     "Marcus Aemilius Lepidus runs a straight road from Ariminum to Placentia, along the edge of the Po plain."),
    ("Via Postumia", "Spurius Postumius Albinus Magnus (148 BCE)", -147, "republic", "Via Postumia",
     "Spurius Postumius Albinus links Genua on the Tyrrhenian coast with Aquileia at the head of the Adriatic, across northern Italy."),
    ("Via Egnatia", "Gnaeus Egnatius (146 BCE)", -145, "republic", "Via Egnatia",
     "Gnaeus Egnatius builds the road across the Balkans, through Lychnidos, Pella and Thessalonike, the land route from Italy to the East."),
    ("Via Popillia", "Publius Popillius Laenas (132 BCE)", -131, "republic", "Via Popillia",
     "Publius Popillius Laenas carries a road from Capua down to the toe of Italy, towards Rhegium."),
    (None, "Manius Aquilius (129-126 BCE)", -128, "republic", "Roads of Asia",
     "Manius Aquilius, who organised Rome's new province of Asia, builds the first Roman roads in Anatolia, reaching south to Perge and Side."),
    ("Via Domitia", "Gnaeus Domitius Ahenobarbus (118 BCE)", -117, "republic", "Via Domitia",
     "Gnaeus Domitius Ahenobarbus builds the road through southern Gaul, from the Pyrenees past Narbo to Nemausus: the land link between Italy and Spain."),
    ("Via Sebaste", "Augustus (6 BCE)", -5, "empire", "Via Sebaste",
     "Augustus has the Via Sebaste built through the mountains of Pisidia, linking his new colonies such as Antiochia in Pisidia."),
    ("Via Claudia Augusta", "Drusus-Claudius (15 BCE-46 CE)", 46, "empire", "Via Claudia Augusta",
     "The road over the Alps from the Po valley to Augusta Vindelicum (Augsburg), opened by Drusus's campaign of 15 BC, is completed under Claudius."),
    ("Via Nova Traiana", "Trajan (111 CE)", 111, "empire", "Via Nova Traiana",
     "After annexing Arabia, Trajan builds the Via Nova Traiana from Bostra to the Red Sea; these sections run through Madaba and Dibon."),
    ("Via Hadriana", "Hadrian (137 CE)", 137, "empire", "Via Hadriana",
     "Hadrian's road runs from his new city of Antinoopolis on the Nile across the Eastern Desert to the Red Sea coast."),
    ("Strata Diocletiana", "Tetrarch (293-305 CE)", 293, "empire", "Strata Diocletiana",
     "Under Diocletian's Tetrarchy a military road is built along the desert frontier of Syria, through Palmyra."),
]
items = []
for road, cons, date, kind, title, text in CARDS:
    pts, kmc, bib = [], 0, collections.Counter()
    for p, parts in sections:
        its = [ALIAS.get(x.strip(), x.strip()) for x in (p["Itinerary"] or "").split(",")]
        if p["Cons_per_e"] == cons and (road is None or road in its):
            for part in parts: pts += part
            kmc += p["Shape_Leng"] / 1000; bib[p["Bibliograp"]] += 1
    assert pts, (road, cons)
    cx, cy = sum(q[0] for q in pts) / len(pts), sum(q[1] for q in pts) / len(pts)
    at = min(pts, key=lambda q: (q[0] - cx) ** 2 + (q[1] - cy) ** 2)
    yr = (str(1 - date) + " BC") if date <= 0 else ("AD " + str(date))
    items.append({"title": title, "date": date, "at": [round(at[0], 2), round(at[1], 2)], "kind": kind, "text": text,
                  "source": "Itiner-e: %s km of sections dated '%s'%s; bibliography: %s" % (
                      round(kmc), cons, " (a slip for 189-187 BC; Livy 39.2 dates the Via Aemilia to 187 BC)" if "CE)" in cons and "BCE" not in cons and date < 0 else "",
                      bib.most_common(1)[0][0]),
                  "url": DOI})
    print("card", yr, title, round(kmc), "km", items[-1]["at"])

builtby = [p["Shape_Leng"] for p, _ in sections if p["Cons_per_e"]]
write("roman-roads-named.json", {"source": "itinere", "asOf": "2025-09-15", "retrieved": TODAY,
    "note": (note + " Named roads: sections whose Itinerary field names the road; 'km' sums their Shape_Leng. Cards: dates from the "
            "Itiner-e construction field (Cons_per_e), which names a builder for %d sections (%d%% of the length). City points: coordinates of the representative point "
            "in the Pleiades gazetteer (CC BY 3.0, pleiades.stoa.org), retrieved " + TODAY + ".") % (len(builtby), round(100 * sum(builtby) / total / 1000)),
    "namedKm": {k: round(v) for k, v in namedkm.items()},
    "reach": reach,
    "lines": {"named": nitems},
    "points": {"cities": cities, "extremes": ext, "roadLabels": nlabels},
    "kinds": {"republic": {"label": "Built under the Republic", "color": "c3"}, "empire": {"label": "Built under the emperors", "color": "c2"}},
    "items": items})
