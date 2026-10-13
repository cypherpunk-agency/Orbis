#!/usr/bin/env python3
"""Year of independence (or founding) of today's countries -> data/rights/independence.json (sets for `since`).

Source: CIA World Factbook, field "Independence", from the public-domain JSON mirror github.com/factbook/factbook.json
(CC0; the CIA stopped publishing the Factbook in February 2026). Clone into .cache/factbook/repo first:
  git clone --depth 1 https://github.com/factbook/factbook.json .cache/factbook/repo
Rule: the first year named in the field (a declaration counts, even when recognition came later).
Exceptions are listed in OLD and OVERRIDE and in the dataset note.
"""
import glob, json, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPO = os.path.join(ROOT, ".cache", "factbook", "repo")
if not os.path.isdir(REPO):
    subprocess.run(["git", "clone", "-q", "--depth", "1", "https://github.com/factbook/factbook.json", REPO], check=True)
commit = subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%h %cs"], capture_output=True, text=True).stdout.strip()

# Factbook GEC code -> ISO3 (sovereign states and Kosovo; dependencies left out)
GEC = {"ag":"DZA","ao":"AGO","bc":"BWA","bn":"BEN","by":"BDI","cd":"TCD","cf":"COG","cg":"COD","cm":"CMR","cn":"COM","ct":"CAF",
 "cv":"CPV","dj":"DJI","eg":"EGY","ek":"GNQ","er":"ERI","et":"ETH","ga":"GMB","gb":"GAB","gh":"GHA","gv":"GIN","iv":"CIV",
 "ke":"KEN","li":"LBR","lt":"LSO","ly":"LBY","ma":"MDG","mi":"MWI","ml":"MLI","mo":"MAR","mp":"MUS","mr":"MRT","mz":"MOZ",
 "ng":"NER","ni":"NGA","od":"SSD","pu":"GNB","rw":"RWA","se":"SYC","sf":"ZAF","sg":"SEN","sl":"SLE","so":"SOM","su":"SDN",
 "to":"TGO","tp":"STP","ts":"TUN","tz":"TZA","ug":"UGA","uv":"BFA","wa":"NAM","wz":"SWZ","za":"ZMB","zi":"ZWE",
 "as":"AUS","bp":"SLB","fj":"FJI","fm":"FSM","kr":"KIR","nh":"VUT","nr":"NRU","nz":"NZL","ps":"PLW","rm":"MHL","tn":"TON",
 "tv":"TUV","ws":"WSM","pp":"PNG",
 "ac":"ATG","bb":"BRB","bf":"BHS","bh":"BLZ","cs":"CRI","cu":"CUB","do":"DMA","dr":"DOM","es":"SLV","gj":"GRD","gt":"GTM",
 "ha":"HTI","ho":"HND","jm":"JAM","nu":"NIC","pm":"PAN","sc":"KNA","st":"LCA","td":"TTO","vc":"VCT",
 "aj":"AZE","am":"ARM","gg":"GEO","kg":"KGZ","kz":"KAZ","rs":"RUS","ti":"TJK","tx":"TKM","uz":"UZB",
 "bm":"MMR","bx":"BRN","cb":"KHM","ch":"CHN","id":"IDN","ja":"JPN","kn":"PRK","ks":"KOR","la":"LAO","mg":"MNG","my":"MYS",
 "rp":"PHL","sn":"SGP","th":"THA","tt":"TLS","vm":"VNM",
 "al":"ALB","an":"AND","au":"AUT","be":"BEL","bk":"BIH","bo":"BLR","bu":"BGR","cy":"CYP","da":"DNK","ei":"IRL","en":"EST",
 "ez":"CZE","fi":"FIN","fr":"FRA","gm":"DEU","gr":"GRC","hr":"HRV","hu":"HUN","ic":"ISL","it":"ITA","kv":"XKX","lg":"LVA",
 "lh":"LTU","lo":"SVK","ls":"LIE","lu":"LUX","md":"MDA","mj":"MNE","mk":"MKD","mn":"MCO","mt":"MLT","nl":"NLD","no":"NOR",
 "pl":"POL","po":"PRT","ri":"SRB","ro":"ROU","si":"SVN","sm":"SMR","sp":"ESP","sw":"SWE","sz":"CHE","uk":"GBR","up":"UKR",
 "vt":"VAT","ae":"ARE","ba":"BHR","ir":"IRN","is":"ISR","iz":"IRQ","jo":"JOR","ku":"KWT","le":"LBN","mu":"OMN","qa":"QAT",
 "sa":"SAU","sy":"SYR","tu":"TUR","ym":"YEM","ca":"CAN","mx":"MEX","us":"USA",
 "ar":"ARG","bl":"BOL","br":"BRA","ci":"CHL","co":"COL","ec":"ECU","gy":"GUY","ns":"SUR","pa":"PRY","pe":"PER","uy":"URY",
 "ve":"VEN","af":"AFG","bg":"BGD","bt":"BTN","ce":"LKA","in":"IND","mv":"MDV","np":"NPL","pk":"PAK"}

# States the Factbook dates before 1776, or by a change of regime rather than independence: shown as long-established
OLD = {"AND","AUT","DNK","ESP","FRA","GBR","LIE","MCO","NLD","PRT","SMR","SWE","CHE",   # Factbook founding dates before 1776
       "THA","NPL","OMN","ETH",                                                      # never colonised / founded before 1776
       "CHN","IRN","JPN","TUR","RUS","BTN"}  # Factbook dates a new regime (1949, 1979, 1947, 1923, 1991) or unification (1907)
OVERRIDE = {
  "BGR": 1908,   # Factbook first date (1878) is autonomy within the Ottoman Empire; full independence 22 Sep 1908
  "TZA": 1961,   # Factbook gives the 1964 union; Tanganyika became independent on 9 Dec 1961 (Zanzibar 1963)
  "TLS": 2002,   # Factbook first date is the 1975 declaration, ended by Indonesia's invasion; independence restored 2002
  "EST": 1991, "LVA": 1991, "LTU": 1991,   # restored 1991; their 1918-1940 independence is in the "interwar" set
}
INTERWAR = {"EST": [1918, 1940], "LVA": [1918, 1940], "LTU": [1918, 1940]}  # independent, then annexed by the USSR in 1940

year_re = re.compile(r"\b(1[0-9]{3}|20[0-2][0-9])\b")
members, raw = {}, {}
for f in glob.glob(os.path.join(REPO, "*", "*.json")):
    code = os.path.basename(f)[:-5]
    if code not in GEC: continue
    iso = GEC[code]
    txt = ((json.load(open(f)).get("Government") or {}).get("Independence") or {}).get("text", "")
    raw[iso] = txt
    if iso in OLD: continue
    m = year_re.search(txt)
    if not m: sys.exit("no year for %s: %r" % (iso, txt))
    members[iso] = int(m.group(1))
missing = set(GEC.values()) - set(raw)
if missing: sys.exit("missing Factbook files: %s" % missing)
members.update(OVERRIDE)

out = {
  "source": "cia-factbook", "asOf": "2026-02-04", "retrieved": "2026-10-13",
  "note": ("CIA World Factbook, field 'Independence' (public domain), via the factbook.json mirror (commit %s); the CIA stopped "
           "publishing the Factbook on 4 February 2026. Rule: the first year the field names, so declarations count even where "
           "recognition came later (USA 1776, Mexico 1810, Guinea-Bissau 1973). Dominions use the Factbook's date of union or "
           "federation (Canada 1867, Australia 1901, New Zealand 1907, South Africa 1910). Exceptions: Bulgaria 1908 (1878 was autonomy within the Ottoman Empire); Tanzania 1961 (Tanganyika; "
           "the Factbook gives the 1964 union with Zanzibar); Timor-Leste 2002 (the 1975 declaration ended with Indonesia's invasion); "
           "Estonia, Latvia and Lithuania independent 1918-1940, annexed by the USSR, independent again 1991. Shown as long-established "
           "states: those the Factbook dates before 1776 (e.g. France, the UK, Spain, Portugal, the Netherlands, Sweden, Switzerland, "
           "Thailand, Nepal, Oman), Ethiopia, Bhutan, and China, Iran, Japan, Russia and Turkey, whose Factbook dates mark a new "
           "regime or the end of the USSR rather than independence. Not dated: Taiwan, Palestine, Western Sahara, Somaliland, "
           "Northern Cyprus (no Factbook entry or date). Borders were often different at independence; the map shows today's.") % commit,
  "sets": {
    "old": {"label": "Long-established states", "members": {k: 1000 for k in sorted(OLD)}},
    "independent": {"label": "Independent", "members": dict(sorted(members.items()))},
    "interwar": {"label": "Independent 1918-1940", "members": INTERWAR},
  }
}
path = os.path.join(ROOT, "data", "rights", "independence.json")
json.dump(out, open(path, "w"), ensure_ascii=False, separators=(",", ":"))
print("wrote", path, len(members), "dated,", len(OLD), "old; factbook", commit)
from collections import Counter
dec = Counter((v // 10) * 10 for v in members.values()); print(sorted(dec.items()))
for y in (1960, 1991, 1992): print(y, sorted(k for k, v in members.items() if v == y))
