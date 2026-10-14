"""The launch explosion: orbital launches and satellites from GCAT (J. McDowell, planet4589.org/space/gcat, CC BY 4.0).
Downloads into .cache/launches/ (≈40 MB):
  tsv/derived/launchlog.tsv  orbital launch log (one row per payload; Launch_Site, LVState)
  tsv/launch/launch.tsv      all launches (LaunchCode: O… = orbital attempt; D… = deep space)
  tsv/tables/sites.tsv       launch sites with coordinates
  tsv/cat/satcat.tsv, satcat100k.tsv, tmpcat.tsv  object catalogs (Type P… = payload)
Run: python3 tools/build/launches.py
Output: data/statistics/launches.json
"""
import os, json, datetime, collections, urllib.request

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CACHE = os.path.join(root, ".cache/launches")
BASE = "https://planet4589.org/space/gcat/tsv/"
FILES = {"launchlog.tsv": "derived/launchlog.tsv", "launch.tsv": "launch/launch.tsv", "sites.tsv": "tables/sites.tsv",
         "satcat.tsv": "cat/satcat.tsv", "satcat100k.tsv": "cat/satcat100k.tsv", "tmpcat.tsv": "cat/tmpcat.tsv"}
UA = {"User-Agent": "Orbis-data-build/1.0"}
TODAY = datetime.date.today().isoformat()
Y0, Y1 = 1957, 2025   # complete years


def rd(name):
    p = os.path.join(CACHE, name)
    if not os.path.exists(p):
        os.makedirs(CACHE, exist_ok=True)
        with urllib.request.urlopen(urllib.request.Request(BASE + FILES[name], headers=UA)) as r, open(p, "wb") as f:
            f.write(r.read())
    L = [l.rstrip("\n").split("\t") for l in open(p, encoding="utf-8")]
    h = [x.strip("#").strip() for x in L[0]]
    upd = next((l[0] for l in L[1:3] if l[0].startswith("# Updated")), "")
    return [dict(zip(h, [c.strip() for c in r])) for r in L[1:] if not r[0].startswith("#")], upd


ll, upd = rd("launchlog.tsv")
la, _ = rd("launch.tsv")
sites = {r["Site"]: r for r in rd("sites.tsv")[0]}
import re
hp = os.path.join(CACHE, "gcat.html")   # front page: release number and licence ("released under the Creative Commons CC-BY licence")
if not os.path.exists(hp):
    with urllib.request.urlopen(urllib.request.Request("https://planet4589.org/space/gcat/", headers=UA)) as r, open(hp, "wb") as f:
        f.write(r.read())
rel = re.search(r"GCAT Release [0-9.]+", open(hp, encoding="utf-8", errors="replace").read())
rel = rel.group(0).replace("GCAT ", "").lower() if rel else "release"
print("GCAT", upd, rel)

# orbital launch attempts: every launch in the orbital launch log, plus any orbital success/failure missing from it
# (pad explosions 'OE' and aborts 'OA' are not launches)
L = {}
for r in la:
    if r["LaunchCode"][:2] in ("OS", "OF"): L[r["Launch_Tag"]] = {"date": r["Launch_Date"], "site": r["Launch_Site"], "state": None, "agency": r["Agency"]}
for r in ll:
    x = L.setdefault(r["Launch_Tag"], {"date": r["Launch_Date"], "site": r["Launch_Site"], "agency": r["Agency"], "state": None})
    x["state"] = x["state"] or r["LVState"]
# lunar ascents (Apollo LM, Luna and Chang'e sample returns) are in the launch lists too: keep launches from Earth only
offearth = [t for t, x in L.items() if x["site"] in sites and sites[x["site"]]["StateCode"] in ("LUNA", "MARS")]
for t in offearth: del L[t]
print("orbital launches from Earth", len(L), "dropped off-Earth", len(offearth), "no state", sum(1 for x in L.values() if not x["state"]))
year = lambda s: int(s[:4])

# who launches (state of the launch vehicle, as GCAT assigns it)
GROUP = {"US": "USA", "SU": "RUS", "RU": "RUS", "CN": "CHN", "F": "EUR", "I-ESA": "EUR", "I-ELDO": "EUR", "I": "EUR", "D": "EUR",
         "UK": "EUR", "J": "JPN", "IN": "IND", "NZ": "NZL"}
years = list(range(Y0, Y1 + 1))
cnt = collections.defaultdict(collections.Counter); tot = collections.Counter(); spx = collections.Counter(); cnt26 = collections.Counter()
for t, x in L.items():
    y = year(x["date"]); g = GROUP.get(x["state"], "OTH")
    if y == 2026: cnt26[g] += 1
    if y > Y1: continue
    tot[y] += 1; cnt[g][y] += 1
    if x["agency"] == "SPX": spx[y] += 1
print("launches per year (last 6)", [(y, tot[y]) for y in years[-6:]], "2026 so far", sum(cnt26.values()))
print("2025 by group", {g: cnt[g][2025] for g in cnt}, "SpaceX 2025", spx[2025])
print("all-time by group", {g: sum(c.values()) for g, c in cnt.items()})
print("peak cold war", max(((y, tot[y]) for y in range(1957, 2000)), key=lambda a: a[1]))

# sites: launches per year, merged where pads of one spaceport have separate codes
MERGE = {"Kennedy": "Canaveral", "Pt Arguello": "Vandenberg", "Hainan CLS": "Wenchang", "Kagoshima": "Uchinoura",
         "Wallops I": "Wallops", "Wallops MARS": "Wallops", "Spaceport Florida": "Canaveral"}
NAMES = {"Canaveral": "Cape Canaveral", "Baykonur": "Baikonur", "Vostochniy": "Vostochny", "Kirimati": "Sea Launch (Pacific)",
         "Mahia": "Mahia (Rocket Lab)", "Huang Hai": "Yellow Sea (sea launches)", "Starbase": "Starbase (SpaceX)", "Sriharikota": "Sriharikota", "Svobodniy": "Svobodny"}
sy = collections.defaultdict(collections.Counter); at = {}; nosite = 0
for t, x in L.items():
    s = sites.get(x["site"])
    try: lon, lat = float(s["Longitude"]), float(s["Latitude"])
    except (TypeError, ValueError): nosite += 1; continue
    y = year(x["date"])
    if y > Y1: continue
    k = MERGE.get(s["ShortName"], s["ShortName"])
    sy[k][y] += 1
    at.setdefault(k, [round(lon, 2), round(lat, 2)])
print("launches without site coordinates", nosite)
pts = []
for k, c in sorted(sy.items(), key=lambda a: -sum(a[1].values())):
    run = 0; n = []; cum = []
    for y in years: run += c[y]; n.append(c[y] or None); cum.append(run)
    pts.append({"id": k.lower().replace(" ", "-"), "name": NAMES.get(k, k), "at": at[k], "n": n, "cum": cum})
print("top sites all time", [(p["name"], p["cum"][-1]) for p in pts[:8]])
print("top sites 2025", sorted(((p["name"], p["n"][-1]) for p in pts if p["n"][-1]), key=lambda a: -a[1])[:8])

# satellites (payloads reaching orbit) per launch year
pay = collections.Counter(); sl = collections.Counter(); catupd = ""
# five bands for the stacked chart: SpaceX, other US rockets, USSR/Russia, China, everyone else
who = collections.defaultdict(collections.Counter)
for t, x in L.items():
    y = year(x["date"])
    if y > Y1: continue
    g = GROUP.get(x["state"], "OTH")
    who["SPX" if x["agency"] == "SPX" else g if g in ("USA", "RUS", "CHN") else "OTH"][y] += 1
for f in ("satcat.tsv", "satcat100k.tsv", "tmpcat.tsv"):
    rows, u = rd(f); catupd = catupd or u
    for r in rows:
        if r["Type"][:1] != "P" or not r["LDate"][:4].isdigit(): continue
        y = year(r["LDate"]); pay[y] += 1
        if "Starlink" in r["Name"] or "Starlink" in r["PLName"]: sl[y] += 1
allp = sum(pay[y] for y in pay if y <= Y1)
for N in (3, 4, 5, 6):
    recent = sum(pay[y] for y in range(Y1 - N + 1, Y1 + 1))
    print(f"payloads {Y1-N+1}-{Y1}: {recent}  before: {allp - recent}")
print("payloads 2025", pay[2025], "starlink 2025", sl[2025], "2026 so far", pay[2026], "starlink all", sum(sl.values()),
      "total to 2025", allp, "total incl 2026", sum(pay.values()))
print("payloads 2010-2019 avg", sum(pay[y] for y in range(2010, 2020)) / 10)

out = {
    "source": "gcat", "asOf": upd.replace("# Updated ", "").strip(), "retrieved": TODAY,
    "note": f"GCAT {rel} (J. McDowell). Orbital launch attempts from Earth (successful or not, including deep-space launches; lunar ascents excluded) per UTC year, {Y0}–{Y1}: "
            f"{sum(tot.values()):,}; 2026 so far ({upd.replace('# Updated ', '').strip()[:11]}): {sum(cnt26.values())}. 'Who launches' uses the state GCAT "
            "assigns to the launch vehicle: USSR and Russia together; Europe = Arianespace/ESA/ELDO plus Italian and other European rockets; "
            "Rocket Lab's Electron launches from New Zealand count as New Zealand. Series 'who': SpaceX (agency SPX), other US, USSR/Russia, China, all others. Satellites = payloads catalogued in orbit (satcat, satcat100k, tmpcat; "
            "failed launches excluded) by launch year; Starlink = payloads named Starlink. Site points: launches per year at each spaceport "
            f"(pads of one spaceport merged; {nosite} air/sea launches without fixed coordinates omitted).",
    "years": years,
    "series": {
        "launches": {"label": "Orbital launch attempts per year", "units": "launches",
                     "values": {g: [cnt[g][y] for y in years] for g in ["USA", "RUS", "CHN", "EUR", "JPN", "IND", "NZL", "OTH"]},
                     },
        "who": {"label": "Orbital launch attempts per year, by launcher", "units": "launches",
                "values": {g: [who[g][y] for y in years] for g in ["SPX", "USA", "RUS", "CHN", "OTH"]}},
        "total": {"label": "Orbital launch attempts per year, world", "units": "launches", "values": {"ALL": [tot[y] for y in years],
                  "SPX": [spx[y] for y in years]}},
        "sats": {"label": "Satellites launched per year", "units": "satellites",
                 "values": {"ALL": [pay[y] for y in years], "SL": [sl[y] for y in years], "NSL": [pay[y] - sl[y] for y in years]}},
    },
    "periods": [str(y) for y in years],
    "points": pts,
}
p = os.path.join(root, "data/statistics/launches.json")
json.dump(out, open(p, "w"), ensure_ascii=False, separators=(",", ":"))
print(p, os.path.getsize(p))
