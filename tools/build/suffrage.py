#!/usr/bin/env python3
"""Women's suffrage by country -> data/rights/suffrage.json (sets for `since` layers).

Facts typed from the Inter-Parliamentary Union chronology "Women's Suffrage: A World Chronology of the
Recognition of Women's Rights to Vote and to Stand for Election" (archive.ipu.org/wmn-e/suffrage.htm).
The page is downloaded to .cache/ and only the years are kept. Asterisks on the IPU page mark rights
"subject to conditions or restrictions" (*) and "restrictions or conditions lifted" (**).
A few countries the IPU page lacks or dates by local elections are added by hand (ADDITIONS, OVERRIDES).
"""
import html, json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(ROOT, ".cache", "suffrage"); os.makedirs(CACHE, exist_ok=True)
RAW = os.path.join(CACHE, "ipu.htm")
URL = "http://archive.ipu.org/wmn-e/suffrage.htm"
if not os.path.exists(RAW):
    urllib.request.urlretrieve(URL, RAW)

NAME = {
 "United States of America":"USA","New Zealand":"NZL","Australia":"AUS","Finland":"FIN","Norway":"NOR","Denmark":"DNK",
 "Iceland":"ISL","Canada":"CAN","Netherlands":"NLD","Austria":"AUT","Estonia":"EST","Georgia":"GEO","Germany":"DEU",
 "Hungary":"HUN","Ireland":"IRL","Kyrgyzstan":"KGZ","Latvia":"LVA","Lithuania":"LTU","Poland":"POL","Russian Federation":"RUS",
 "United Kingdom":"GBR","Belarus":"BLR","Belgium":"BEL","Luxembourg":"LUX","Sweden":"SWE","Ukraine":"UKR","Albania":"ALB",
 "Czech Republic":"CZE","Slovakia":"SVK","Armenia":"ARM","Azerbaijan":"AZE","Kazakhstan":"KAZ","Mongolia":"MNG",
 "Saint Lucia":"LCA","Tajikistan":"TJK","Turkmenistan":"TKM","Ecuador":"ECU","Romania":"ROU","South Africa":"ZAF",
 "Turkey":"TUR","Chile":"CHL","Portugal":"PRT","Spain":"ESP","Sri Lanka":"LKA","Brazil":"BRA","Maldives":"MDV",
 "Thailand":"THA","Uruguay":"URY","Cuba":"CUB","Myanmar":"MMR","Philippines":"PHL","Bolivia":"BOL","Uzbekistan":"UZB",
 "El Salvador":"SLV","Panama":"PAN","Dominican Republic":"DOM","Bulgaria":"BGR","France":"FRA","Jamaica":"JAM",
 "Croatia":"HRV","Guyana":"GUY","Indonesia":"IDN","Italy":"ITA","Japan":"JPN","Senegal":"SEN","Slovenia":"SVN","Togo":"TGO",
 "Cameroon":"CMR","D.P.R. of Korea":"PRK","Djibouti":"DJI","Guatemala":"GTM","Liberia":"LBR","The F.Y.R. of Macedonia":"MKD",
 "Trinidad and Tobago":"TTO","Venezuela":"VEN","Viet Nam":"VNM","Argentina":"ARG","Malta":"MLT","Mexico":"MEX",
 "Pakistan":"PAK","Singapore":"SGP","Israel":"ISR","Niger":"NER","Republic of Korea":"KOR","Seychelles":"SYC",
 "Suriname":"SUR","Bosnia and Herzegovina":"BIH","China":"CHN","Costa Rica":"CRI","Syrian Arab Republic":"SYR",
 "Barbados":"BRB","Haiti":"HTI","India":"IND","Antigua and Barbuda":"ATG","Dominica":"DMA","Grenada":"GRD","Nepal":"NPL",
 "Saint Kitts and Nevis":"KNA","Saint Vincent and the Grenadines":"VCT","Côte d'Ivoire":"CIV","Greece":"GRC",
 "Lebanon":"LBN","Bhutan":"BTN","Belize":"BLZ","Colombia":"COL","Ghana":"GHA","Cambodia":"KHM","Eritrea":"ERI",
 "Ethiopia":"ETH","Honduras":"HND","Nicaragua":"NIC","Peru":"PER","Benin":"BEN","Comoros":"COM","Egypt":"EGY",
 "Gabon":"GAB","Mali":"MLI","Mauritius":"MUS","Somalia":"SOM","Malaysia":"MYS","Zimbabwe":"ZWE","Burkina Faso":"BFA",
 "Chad":"TCD","Guinea":"GIN","Lao P.D.R.":"LAO","Madagascar":"MDG","San Marino":"SMR","Tunisia":"TUN",
 "United Republic of Tanzania":"TZA","Cyprus":"CYP","Gambia":"GMB","Tonga":"TON","Bahamas":"BHS","Burundi":"BDI",
 "Malawi":"MWI","Mauritania":"MRT","Paraguay":"PRY","Rwanda":"RWA","Sierra Leone":"SLE","Algeria":"DZA","Monaco":"MCO",
 "Uganda":"UGA","Zambia":"ZMB","Afghanistan":"AFG","Congo":"COG","Equatorial Guinea":"GNQ","Fiji":"FJI",
 "Iran (Islamic Republic of)":"IRN","Kenya":"KEN","Morocco":"MAR","Papua New Guinea":"PNG","Libyan Arab Jamahiriya":"LBY",
 "Sudan":"SDN","Bostwana":"BWA","Lesotho":"LSO","Democratic Republic of the Congo":"COD","Kiribati":"KIR","Tuvalu":"TUV",
 "Nauru":"NRU","Swaziland":"SWZ","Andorra":"AND","Switzerland":"CHE","Bangladesh":"BGD","Bahrain":"BHR","Jordan":"JOR",
 "Solomon Islands":"SLB","Angola":"AGO","Cape Verde":"CPV","Mozambique":"MOZ","Sao Tome and Principe":"STP","Vanuatu":"VUT",
 "Guinea Bissau":"GNB","Republic of Moldova":"MDA","Marshall Islands":"MHL","Micronesia (Fed. States)":"FSM","Palau":"PLW",
 "Iraq":"IRQ","Liechtenstein":"LIE","Central African Republic":"CAF","Namibia":"NAM","Samoa":"WSM","Kuwait":"KWT",
 "Yugoslavia":"YUG",
}
# entries that need a hand decision (regional or group-specific rows on the IPU page)
SPECIAL = {"South Africa (Whites)":("ZAF",1930,"*"), "South Africa (Coloureds + Indians)":("ZAF",1984,"*"),
           "South Africa (Blacks)":("ZAF",1994,"**"), "Nigeria (South)":("NGA",1958,"*"), "Nigeria (North)":("NGA",1978,"**"),
           "Yemen (D.P. R.)":("YEM",1967,"*"), "Yemen (Arab Republic)":("YEM",1970,"**")}

s = open(RAW, encoding="latin-1").read()
rows = re.findall(r"<TR><TD[^>]*><B><FONT[^>]*>(\d{4})</FONT></B>\s*</TD><TD>(.*?)</TD></TR>", s, re.S)
if len(rows) < 68: sys.exit("IPU page layout changed: only %d rows" % len(rows))
entries = []  # (iso, year, kind 'vote'|'stand'|'both', mark '', '*', '**')
unknown = []
for y, cell in rows:
    t = html.unescape(re.sub(r"<SUP>.*?</SUP>", "", cell, flags=re.S))
    t = re.sub(r"<[^>]+>", " ", t); t = re.sub(r"\s+", " ", t).strip()
    for part in re.split(r",\s*(?![^()]*\))", t):
        part = part.strip()
        if not part: continue
        m = re.match(r"^(.*?)\s*(\((to vote|to stand for election)\))?\s*(\*{0,2})\s*$", part)
        name, kind, mark = m.group(1).strip(), (m.group(3) or "both"), m.group(4)
        kind = {"to vote":"vote","to stand for election":"stand"}.get(kind, kind)
        sp = SPECIAL.get(part.rstrip("*").strip()) or SPECIAL.get(name)
        if sp: entries.append((sp[0], int(y), "both", sp[2])); continue
        if name not in NAME: unknown.append((y, part)); continue
        entries.append((NAME[name], int(y), kind, mark))
if unknown: sys.exit("unmapped IPU names: %r" % unknown)

first, full = {}, {}
by = {}
for iso, y, kind, mark in entries:
    if kind == "stand": continue
    by.setdefault(iso, []).append((y, mark))
for iso, lst in by.items():
    lst.sort()
    first[iso] = lst[0][0]
    restricted = any(m == "*" for _, m in lst)
    if restricted:
        lifted = [y for y, m in lst if m == "**"]
        if lifted: full[iso] = lifted[0]
    else:
        full[iso] = lst[0][0]
# Yugoslavia 1946 applies to today's Serbia, Montenegro and Kosovo
for iso in ("SRB", "MNE", "XKX"): first[iso] = full[iso] = first["YUG"]
del first["YUG"], full["YUG"]

# Hand additions and corrections (each cited in the dataset note)
OVERRIDES = {
  # IPU year refers to municipal elections; national vote followed later
  "MEX": (1947, 1953), "TUR": (1930, 1934),
  # IPU gives 1973 with a note that is missing from the page; women first voted in 2002 (parliamentary elections)
  "BHR": (2002, 2002),
  # Not on the IPU page
  "OMN": (1994, 2003),          # 1994: selected women in Muscat; 2003: all citizens over 21 (Majlis al-Shura)
  "QAT": (1999, 2021),          # 1999: municipal elections; 2021: first Shura Council elections
  "ARE": (2006, None),          # 2006: appointed electoral college incl. women; no universal suffrage for anyone
  "SAU": (2015, None),          # 12 Dec 2015 municipal elections; no national elections exist
  "TWN": (1947, 1947),          # Constitution of the Republic of China, in force 25 Dec 1947
  "SSD": (1964, 1964),          # part of Sudan (IPU: 1964)
  "NCY": (1960, 1960),          # Cyprus, 1960
  # IPU gives 1978 and 1993 (footnote: stages); women had voted in the Soviet Union, which annexed it in 1940
  "MDA": (1940, 1940),
}
for iso, (a, b) in OVERRIDES.items():
    first[iso] = a
    if b is None: full.pop(iso, None)
    else: full[iso] = b

partial = {k: [v, full[k]] if k in full and full[k] > v else v for k, v in first.items() if full.get(k) != v}
out = {
  "source": "ipu-suffrage", "asOf": "2026-10-13", "retrieved": "2026-10-13",
  "note": ("Years typed from the Inter-Parliamentary Union, 'Women's Suffrage: A World Chronology of the Recognition of "
           "Women's Rights to Vote and to Stand for Election' (archive.ipu.org/wmn-e/suffrage.htm, retrieved 13 Oct 2026). "
           "'vote' = first year some women could vote in national elections (IPU year for the right to vote, or to vote and stand). "
           "'equal' = year women could vote on the same terms as men: the IPU year marked 'restrictions lifted' (**), or the "
           "single IPU year where no restriction is marked. Former federations: Yugoslavia 1946 applied to Serbia, Montenegro, "
           "Kosovo; Sudan 1964 to South Sudan; Cyprus 1960 to Northern Cyprus. Hand corrections: Mexico 1947 and Turkey 1930 were "
           "local elections (national 1953 and 1934); Bahrain 2002 (IPU's 1973 entry has a missing note; women first voted in "
           "the 2002 elections); Oman 1994 limited, 2003 universal; Qatar 1999 municipal, 2021 Shura Council; UAE 2006 "
           "(electoral college only, for men and women alike); Saudi Arabia 2015 (municipal; no national elections); Taiwan 1947 "
           "(Constitution of the Republic of China); Moldova 1940, when it became part of the Soviet Union, where women already "
           "voted (IPU: 1978 and 1993). Not shown: Brunei (no elections), Palestine, Western Sahara, Somaliland, "
           "Timor-Leste, dependent territories."),
  "sets": {
    "vote": {"label": "Women can vote", "members": dict(sorted(first.items()))},
    "equal": {"label": "Women vote on equal terms with men", "members": dict(sorted(full.items()))},
    "limited": {"label": "Limited: some women, or local elections only", "members": dict(sorted(partial.items()))},
  }
}
path = os.path.join(ROOT, "data", "rights", "suffrage.json")
json.dump(out, open(path, "w"), ensure_ascii=False, separators=(",", ":"))
print("wrote", path, len(first), "countries;", len(partial), "with a limited phase")
for k in sorted(partial): print(" ", k, partial[k], "full", full.get(k))
