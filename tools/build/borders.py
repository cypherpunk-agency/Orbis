"""Historical country-border snapshots from CShapes 2.0 (ETH Zurich ICR), GW system, incl. dependent territories.
Licence: CC BY-NC-SA 4.0 (https://icr.ethz.ch/data/cshapes/ "License" section). Story layer only, non-commercial;
the derived files below stay CC BY-NC-SA 4.0.
Raw: https://icr.ethz.ch/data/cshapes/cshapes_2.0.tar.gz (the R package distributed by ICR). Its
  inst/extdata/cshapes_2_gw.topojson.xz holds the same 710 country-periods as CShapes-2.0.geojson but adds
  `status` (independent / colony / protectorate / mandate / occupied) and `owner` (GW code of the ruling state),
  which the plain GeoJSON/shapefile lack. Downloaded into .cache/cshapes/ if missing.
Run: python3 tools/build/borders.py   (needs the mapshaper CLI in tools/node_modules)
Output: data/history/borders.json, either
  {source, asOf, retrieved, note, snapshots: {year: TopoJSON}}  if every snapshot <= MAX_KB and the total <= MAX_TOTAL_KB,
  or an index {source, asOf, retrieved, note, files: {year: "data/history/borders-<year>.json"}} plus one TopoJSON per year.
  TopoJSON object "states"; properties {name, id, gw, lx, ly} and, for dependencies, {status, owner}.
Snapshot date: 1 January of the year; 1 July if a CShapes period starts on 1 Jan of that year or ends on 31 Dec before it.
Ids: ISO3 of today's successor where the polity is essentially the same state/territory, else the codes in SPECIAL."""
import os, sys, json, lzma, tarfile, subprocess, datetime, urllib.request, tempfile

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
cache = os.path.join(root, ".cache/cshapes")
out_dir = os.path.join(root, "data/history")
MS = os.path.join(root, "tools/node_modules/.bin/mapshaper")
URL = "https://icr.ethz.ch/data/cshapes/cshapes_2.0.tar.gz"
YEARS = [1886, 1900, 1914, 1920, 1925, 1938, 1945, 1950, 1960, 1975, 1990, 1993, 2000, 2011, 2019]
MAX_KB = 120
MAX_TOTAL_KB = 300  # one combined file only if it stays within the ~300 KB per-file guideline (docs/STORY-FORMAT.md)
PCTS = [12, 10, 8, 6.5, 5, 4, 3, 2.4, 1.8]  # share of removable vertices kept, tried in turn

# GW code -> ISO3 of today's successor (independent states and dependencies alike)
ISO = {
    2: "USA", 20: "CAN", 31: "BHS", 40: "CUB", 41: "HTI", 42: "DOM", 51: "JAM", 52: "TTO", 53: "BRB", 6: "PRI",
    65: "GLP", 66: "MTQ", 70: "MEX", 80: "BLZ", 90: "GTM", 91: "HND", 92: "SLV", 93: "NIC", 94: "CRI", 95: "PAN",
    100: "COL", 101: "VEN", 110: "GUY", 115: "SUR", 120: "GUF", 130: "ECU", 135: "PER", 140: "BRA", 145: "BOL",
    150: "PRY", 155: "CHL", 160: "ARG", 165: "URY",
    200: "GBR", 205: "IRL", 210: "NLD", 211: "BEL", 212: "LUX", 220: "FRA", 225: "CHE", 230: "ESP", 235: "PRT",
    255: "DEU", 290: "POL", 305: "AUT", 310: "HUN", 316: "CZE", 317: "SVK", 325: "ITA", 338: "MLT", 339: "ALB",
    340: "SRB", 341: "MNE", 343: "MKD", 344: "HRV", 346: "BIH", 347: "XKX", 349: "SVN", 350: "GRC", 352: "CYP",
    355: "BGR", 359: "MDA", 360: "ROU", 365: "RUS", 366: "EST", 367: "LVA", 368: "LTU", 369: "UKR", 370: "BLR",
    371: "ARM", 372: "GEO", 373: "AZE", 375: "FIN", 380: "SWE", 385: "NOR", 390: "DNK", 395: "ISL",
    402: "CPV", 404: "GNB", 411: "GNQ", 420: "GMB", 432: "MLI", 433: "SEN", 434: "BEN", 435: "MRT", 436: "NER",
    437: "CIV", 438: "GIN", 439: "BFA", 450: "LBR", 451: "SLE", 452: "GHA", 461: "TGO", 471: "CMR", 475: "NGA",
    481: "GAB", 482: "CAF", 483: "TCD", 484: "COG", 490: "COD", 500: "UGA", 501: "KEN", 510: "TZA", 516: "BDI",
    517: "RWA", 520: "SOM", 521: "SOL", 522: "DJI", 530: "ETH", 531: "ERI", 540: "AGO", 541: "MOZ", 551: "ZMB",
    552: "ZWE", 553: "MWI", 560: "ZAF", 565: "NAM", 570: "LSO", 571: "BWA", 572: "SWZ", 580: "MDG", 581: "COM",
    585: "REU", 590: "MUS", 600: "MAR", 609: "ESH", 615: "DZA", 616: "TUN", 620: "LBY", 625: "SDN", 626: "SSD",
    630: "IRN", 640: "TUR", 645: "IRQ", 651: "EGY", 652: "SYR", 660: "LBN", 663: "JOR", 666: "ISR", 670: "SAU",
    678: "YEM", 690: "KWT", 692: "BHR", 694: "QAT", 696: "ARE", 698: "OMN", 700: "AFG", 701: "TKM", 702: "TJK",
    703: "KGZ", 704: "UZB", 705: "KAZ", 710: "CHN", 712: "MNG", 713: "TWN", 731: "PRK", 732: "KOR", 740: "JPN",
    750: "IND", 760: "BTN", 770: "PAK", 771: "BGD", 775: "MMR", 780: "LKA", 781: "MDV", 790: "NPL", 800: "THA",
    811: "KHM", 812: "LAO", 815: "VNM", 820: "MYS", 830: "SGP", 835: "BRN", 840: "PHL", 850: "IDN", 860: "TLS",
    900: "AUS", 910: "PNG", 920: "NZL", 930: "NCL", 940: "SLB", 950: "FJI", 960: "PYF",
}
# Polities with no single present-day equivalent (or sub-units of one). ISO 3166-2 codes for former colonies that
# are today a subdivision with the same extent; short mnemonic codes otherwise (checked against ISO3 codes in use).
SPECIAL = {
    3: "US-AK", 4: "US-HI", 21: "CA-NL", 901: "AU-NSW", 902: "AU-WA", 903: "AU-SA", 904: "AU-VIC", 905: "AU-QLD",
    906: "AU-TAS", 8201: "MY-08", 8202: "MY-10", 8203: "MY-06", 823: "MY-12", 824: "MY-13",
    260: "BRD", 265: "DDR", 291: "DAN", 300: "AUH", 315: "CSK", 345: "YUG", 680: "YMD", 711: "TIB", 730: "KRU",
    816: "DRV", 817: "RVN", 511: "ZAN", 563: "TVL", 564: "OFS",
    1201: "INI", 3461: "BOS", 3462: "HZG", 430: "AOF", 460: "GTO", 462: "BTO", 470: "KAM", 472: "BCM",
    4781: "LAG", 4782: "ORP", 4783: "SNG", 4784: "NNG", 515: "RUR", 5200: "ITS", 5518: "NERH", 5519: "NWRH",
    550: "FRN", 561: "CPC", 562: "NTL", 5612: "BBE", 602: "SPMO", 6021: "SPMS", 610: "SPWA", 665: "PAL",
    6511: "GAZ", 6631: "WBK", 681: "ADN", 6801: "FSA", 6812: "EAP", 7020: "BUK", 7030: "KHV", 7351: "SKH",
    750: None,  # British India (dependency) -> RAJ, independent India -> IND; see ident()
    7506: "JKI", 7708: "AJK", 821: "FMS", 822: "UMS", 827: "STS", 851: "DNG", 911: "PAP", 912: "GNG", 9401: "GSI",
}

def ident(p, date):
    gw, status = p["gwcode"], p["status"]
    if gw == 365: return "USSR" if "1922-12-30" <= date <= "1991-12-25" else "RUS"  # Russian Empire / RSFSR / Russia -> RUS
    if gw == 640: return "OTT" if date < "1923-10-14" else "TUR"  # CShapes switches to the Republic on 1923-10-14
    if gw == 260: return "DEU" if date >= "1990-10-03" else "BRD"  # CShapes continues unified Germany as GW 260
    if gw == 750 and status != "independent": return "RAJ"
    if gw in SPECIAL and SPECIAL[gw]: return SPECIAL[gw]
    if gw in ISO: return ISO[gw]
    raise SystemExit(f"no id for gw {gw} {p['country_name']}")

def ms(*args):
    r = subprocess.run([MS, *args], capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr)
    return r.stderr

def snapshot_date(year, recs):
    jan = f"{year}-01-01"
    if year > YEARS[0] and any(p["start"] == jan or p["end"] == f"{year - 1}-12-31" for p in recs):
        return f"{year}-07-01"
    return jan

def main():
    os.makedirs(cache, exist_ok=True)
    tgz = os.path.join(cache, "cshapes_2.0.tar.gz")
    if not os.path.exists(tgz):
        urllib.request.urlretrieve(URL, tgz)
    retrieved = datetime.date.fromtimestamp(os.path.getmtime(tgz)).isoformat()
    src = os.path.join(cache, "cshapes_2_gw.topojson")
    if not os.path.exists(src):
        with tarfile.open(tgz) as t:
            data = t.extractfile("cshapes/inst/extdata/cshapes_2_gw.topojson.xz").read()
        open(src, "wb").write(lzma.decompress(data))
    topo = json.load(open(src, encoding="utf-8"))
    recs = [g["properties"] for g in topo["objects"]["cshapes_2_gw"]["geometries"]]

    def owner_name(gw, date):
        if gw == 0: return "League of Nations"
        for p in recs:
            if p["gwcode"] == gw and p["status"] == "independent" and p["start"] <= date <= p["end"]: return p["country_name"]
        return next(p["country_name"] for p in recs if p["gwcode"] == gw)

    iso_in_use = set()
    w50 = os.path.join(root, "data/world50.json")
    if os.path.exists(w50):
        iso_in_use = {g["properties"]["id"] for g in json.load(open(w50))["objects"]["countries"]["geometries"]}
    clash = {c for c in SPECIAL.values() if c in iso_in_use}
    if clash: raise SystemExit(f"special codes clash with ISO3 codes in use: {clash}")

    os.makedirs(out_dir, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="borders-")
    snaps, dates, sizes = {}, {}, {}
    for year in YEARS:
        date = snapshot_date(year, recs)
        dates[str(year)] = date
        raw = os.path.join(tmp, f"raw-{year}.geojson")
        ms("-i", src, "-filter", f"start <= '{date}' && end >= '{date}'", "-o", raw, "format=geojson", "precision=0.000001")
        fc = json.load(open(raw, encoding="utf-8"))
        feats, seen = [], {}
        for f in fc["features"]:
            p = f["properties"]
            props = {"name": p["country_name"], "id": ident(p, date), "gw": p["gwcode"], "cx": p["caplong"], "cy": p["caplat"]}
            own = int(p["owner"]) if str(p["owner"]).isdigit() else None
            if p["status"] != "independent" and own != p["gwcode"]:
                props["status"] = p["status"]
                props["owner"] = owner_name(own, date)
            if props["id"] in seen: raise SystemExit(f"{year}: duplicate id {props['id']} ({seen[props['id']]} / {props['name']})")
            seen[props["id"]] = props["name"]
            feats.append({"type": "Feature", "geometry": f["geometry"], "properties": props})
        gw_seen = [f["properties"]["gw"] for f in feats]
        if len(gw_seen) != len(set(gw_seen)): raise SystemExit(f"{year}: overlapping periods for one GW code")
        prep = os.path.join(tmp, f"prep-{year}.geojson")
        json.dump({"type": "FeatureCollection", "features": feats}, open(prep, "w", encoding="utf-8"))
        out = os.path.join(tmp, f"out-{year}.json")
        for pct in PCTS:
            ms("-i", prep, "-simplify", f"{pct}%", "keep-shapes", 
               "-each", "lx=+(this.innerX == null ? cx : this.innerX).toFixed(2), ly=+(this.innerY == null ? cy : this.innerY).toFixed(2)",
               "-rename-layers", "states", "-o", out, "format=topojson", "quantization=100000")
            kb = os.path.getsize(out) / 1024
            if kb <= MAX_KB: break
        t = json.load(open(out, encoding="utf-8"))
        for g in t["objects"]["states"]["geometries"]:
            pr = g["properties"]
            g["properties"] = {k: pr[k] for k in ("name", "id", "gw", "lx", "ly", "status", "owner") if k in pr}
        snaps[str(year)] = t
        sizes[str(year)] = len(json.dumps(t, separators=(",", ":"), ensure_ascii=False).encode()) / 1024
        print(f"{year} ({date}): {len(feats)} units, simplify {pct}%, {sizes[str(year)]:.0f} KB", file=sys.stderr)

    note = ("CShapes 2.0 (Schvitz, Rüegger, Girardin, Cederman, Weidmann, Gleditsch 2022, Journal of Conflict Resolution 66(1):144–61), "
            "ETH Zurich ICR, Gleditsch–Ward system, independent states and dependent territories (from the cshapes 2.0 R package "
            "distributed by ICR, which adds status and ruling state). Licence CC BY-NC-SA 4.0 (non-commercial, share-alike); "
            "derived snapshots (date filter, Visvalingam simplification, label points, ids) are by Orbis and are likewise licensed "
            "CC BY-NC-SA 4.0. Snapshot dates: " + ", ".join(f"{y} = {d}" for y, d in dates.items()) + ". "
            "CShapes codes de jure borders and omits changes under 10,000 km²; areas not held by any state or dependency in "
            "CShapes (e.g. Antarctica, some unclaimed or undefined interiors) are absent. Dependencies carry status and owner. "
            "Ids are ISO3 of today's successor where the polity is essentially the same; otherwise short codes (AUH, USSR, OTT, "
            "YUG, CSK, BRD, DDR, RAJ, …) or ISO 3166-2 codes for former colonies that are today one subdivision (US-AK, AU-NSW).")
    head = {"source": "cshapes", "asOf": "CShapes 2.0", "retrieved": retrieved, "note": note}
    dump = lambda obj, path: open(path, "w", encoding="utf-8").write(json.dumps(obj, separators=(",", ":"), ensure_ascii=False))
    total = sum(sizes.values())
    if max(sizes.values()) <= MAX_KB and total <= MAX_TOTAL_KB:
        dump({**head, "snapshots": snaps}, os.path.join(out_dir, "borders.json"))
        print(f"single file, {total:.0f} KB", file=sys.stderr)
    else:
        files = {}
        for y, t in snaps.items():
            rel = f"data/history/borders-{y}.json"
            dump(t, os.path.join(root, rel))
            files[y] = rel
        dump({**head, "files": files}, os.path.join(out_dir, "borders.json"))
        print(f"split into {len(files)} files, {total:.0f} KB total", file=sys.stderr)

if __name__ == "__main__":
    main()
