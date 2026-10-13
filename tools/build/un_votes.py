#!/usr/bin/env python3
"""UN General Assembly votes on Ukraine (11th emergency special session) -> data/geopolitics/un_votes.json

Primary source: UN Digital Library voting records (one record per resolution, Y/N/A per Member State, blank = did not vote).
digitallibrary.un.org sits behind a bot challenge, so the records are read from Internet Archive copies of the same pages.
The 2022 votes are cross-checked against the official meeting records (A/ES-11/PV.5, A/ES-11/PV.14) from documents.un.org.
Votes are facts; the dataset is registered under the "editorial" source with citations in its note.

Raw files go to .cache/un_votes/ (gitignored). Usage: python3 tools/build/un_votes.py
"""
import json, os, re, html, subprocess, time, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(ROOT, ".cache", "un_votes")
OUT = os.path.join(ROOT, "data", "geopolitics", "un_votes.json")

# resolution key -> (UN Digital Library voting record id, expected Y, N, A, non-voting, meeting record to cross-check)
VOTES = {
    "es11_1": ("3959039", "A/RES/ES-11/1", "2 March 2022", "Aggression against Ukraine", (141, 5, 35, 12), "A/ES-11/PV.5"),
    "es11_4": ("3990400", "A/RES/ES-11/4", "12 October 2022", "Territorial integrity of Ukraine: defending the principles of the Charter", (143, 5, 35, 10), "A/ES-11/PV.14"),
    "es11_7": ("4076672", "A/RES/ES-11/7", "24 February 2025", "Advancing a comprehensive, just and lasting peace in Ukraine", (93, 18, 65, 17), None),
    "es11_10": ("4103179", "A/RES/ES-11/10", "24 February 2026", "Support for lasting peace in Ukraine", (107, 12, 51, 23), None),
}

# the 193 UN Member States, as named in UN records (plus variants used in meeting records)
M = {
 "AFGHANISTAN":"AFG","ALBANIA":"ALB","ALGERIA":"DZA","ANDORRA":"AND","ANGOLA":"AGO","ANTIGUA AND BARBUDA":"ATG","ARGENTINA":"ARG",
 "ARMENIA":"ARM","AUSTRALIA":"AUS","AUSTRIA":"AUT","AZERBAIJAN":"AZE","BAHAMAS":"BHS","BAHRAIN":"BHR","BANGLADESH":"BGD",
 "BARBADOS":"BRB","BELARUS":"BLR","BELGIUM":"BEL","BELIZE":"BLZ","BENIN":"BEN","BHUTAN":"BTN","BOLIVIA PLURINATIONAL STATE OF":"BOL",
 "BOSNIA AND HERZEGOVINA":"BIH","BOTSWANA":"BWA","BRAZIL":"BRA","BRUNEI DARUSSALAM":"BRN","BULGARIA":"BGR","BURKINA FASO":"BFA",
 "BURUNDI":"BDI","CABO VERDE":"CPV","CAMBODIA":"KHM","CAMEROON":"CMR","CANADA":"CAN","CENTRAL AFRICAN REPUBLIC":"CAF","CHAD":"TCD",
 "CHILE":"CHL","CHINA":"CHN","COLOMBIA":"COL","COMOROS":"COM","CONGO":"COG","COSTA RICA":"CRI","COTE DIVOIRE":"CIV","CROATIA":"HRV",
 "CUBA":"CUB","CYPRUS":"CYP","CZECHIA":"CZE","CZECH REPUBLIC":"CZE","DEMOCRATIC PEOPLES REPUBLIC OF KOREA":"PRK",
 "DEMOCRATIC REPUBLIC OF THE CONGO":"COD","DENMARK":"DNK","DJIBOUTI":"DJI","DOMINICA":"DMA","DOMINICAN REPUBLIC":"DOM",
 "ECUADOR":"ECU","EGYPT":"EGY","EL SALVADOR":"SLV","EQUATORIAL GUINEA":"GNQ","ERITREA":"ERI","ESTONIA":"EST","ESWATINI":"SWZ",
 "ETHIOPIA":"ETH","FIJI":"FJI","FINLAND":"FIN","FRANCE":"FRA","GABON":"GAB","GAMBIA":"GMB","GEORGIA":"GEO","GERMANY":"DEU",
 "GHANA":"GHA","GREECE":"GRC","GRENADA":"GRD","GUATEMALA":"GTM","GUINEA":"GIN","GUINEABISSAU":"GNB","GUYANA":"GUY","HAITI":"HTI",
 "HONDURAS":"HND","HUNGARY":"HUN","ICELAND":"ISL","INDIA":"IND","INDONESIA":"IDN","IRAN ISLAMIC REPUBLIC OF":"IRN","IRAQ":"IRQ",
 "IRELAND":"IRL","ISRAEL":"ISR","ITALY":"ITA","JAMAICA":"JAM","JAPAN":"JPN","JORDAN":"JOR","KAZAKHSTAN":"KAZ","KENYA":"KEN",
 "KIRIBATI":"KIR","KUWAIT":"KWT","KYRGYZSTAN":"KGZ","LAO PEOPLES DEMOCRATIC REPUBLIC":"LAO","LATVIA":"LVA","LEBANON":"LBN",
 "LESOTHO":"LSO","LIBERIA":"LBR","LIBYA":"LBY","LIECHTENSTEIN":"LIE","LITHUANIA":"LTU","LUXEMBOURG":"LUX","MADAGASCAR":"MDG",
 "MALAWI":"MWI","MALAYSIA":"MYS","MALDIVES":"MDV","MALI":"MLI","MALTA":"MLT","MARSHALL ISLANDS":"MHL","MAURITANIA":"MRT",
 "MAURITIUS":"MUS","MEXICO":"MEX","MICRONESIA FEDERATED STATES OF":"FSM","MONACO":"MCO","MONGOLIA":"MNG","MONTENEGRO":"MNE",
 "MOROCCO":"MAR","MOZAMBIQUE":"MOZ","MYANMAR":"MMR","NAMIBIA":"NAM","NAURU":"NRU","NEPAL":"NPL","NETHERLANDS":"NLD",
 "NETHERLANDS KINGDOM OF THE":"NLD","NEW ZEALAND":"NZL","NICARAGUA":"NIC","NIGER":"NER","NIGERIA":"NGA","NORTH MACEDONIA":"MKD",
 "NORWAY":"NOR","OMAN":"OMN","PAKISTAN":"PAK","PALAU":"PLW","PANAMA":"PAN","PAPUA NEW GUINEA":"PNG","PARAGUAY":"PRY","PERU":"PER",
 "PHILIPPINES":"PHL","POLAND":"POL","PORTUGAL":"PRT","QATAR":"QAT","REPUBLIC OF KOREA":"KOR","REPUBLIC OF MOLDOVA":"MDA",
 "ROMANIA":"ROU","RUSSIAN FEDERATION":"RUS","RWANDA":"RWA","SAINT KITTS AND NEVIS":"KNA","SAINT LUCIA":"LCA",
 "SAINT VINCENT AND THE GRENADINES":"VCT","SAINT VINCENT AND GRENADINES":"VCT","SAMOA":"WSM","SAN MARINO":"SMR",
 "SAO TOME AND PRINCIPE":"STP","SAUDI ARABIA":"SAU","SENEGAL":"SEN","SERBIA":"SRB","SEYCHELLES":"SYC","SIERRA LEONE":"SLE",
 "SINGAPORE":"SGP","SLOVAKIA":"SVK","SLOVENIA":"SVN","SOLOMON ISLANDS":"SLB","SOMALIA":"SOM","SOUTH AFRICA":"ZAF",
 "SOUTH SUDAN":"SSD","SPAIN":"ESP","SRI LANKA":"LKA","SUDAN":"SDN","SURINAME":"SUR","SWEDEN":"SWE","SWITZERLAND":"CHE",
 "SYRIAN ARAB REPUBLIC":"SYR","TAJIKISTAN":"TJK","THAILAND":"THA","TIMORLESTE":"TLS","TOGO":"TGO","TONGA":"TON",
 "TRINIDAD AND TOBAGO":"TTO","TUNISIA":"TUN","TURKIYE":"TUR","TURKYYE":"TUR","TURKEY":"TUR","TURKMENISTAN":"TKM","TUVALU":"TUV","UGANDA":"UGA",
 "UKRAINE":"UKR","UNITED ARAB EMIRATES":"ARE","UNITED KINGDOM":"GBR","UNITED KINGDOM OF GREAT BRITAIN AND NORTHERN IRELAND":"GBR",
 "UNITED REPUBLIC OF TANZANIA":"TZA","UNITED STATES":"USA","UNITED STATES OF AMERICA":"USA","URUGUAY":"URY","UZBEKISTAN":"UZB",
 "VANUATU":"VUT","VENEZUELA BOLIVARIAN REPUBLIC OF":"VEN","VIET NAM":"VNM","VIETNAM":"VNM","YEMEN":"YEM","ZAMBIA":"ZMB","ZIMBABWE":"ZWE",
}
MEMBERS = sorted(set(M.values()))
assert len(MEMBERS) == 193, len(MEMBERS)

def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper()
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z ]", "", s.replace("-", ""))).strip()

def iso(name):
    k = norm(name)
    if k not in M: raise SystemExit(f"unknown member name: {name!r}")
    return M[k]

def curl(url, out, tries=5):
    for i in range(tries):
        r = subprocess.run(["curl", "-sSL", "--fail", "-o", out, url])
        if r.returncode == 0 and os.path.getsize(out) > 1000: return out
        time.sleep(3 * (i + 1))
    raise SystemExit(f"download failed: {url}")

def text_of(page):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", page, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", "\n", t))
    return [l.strip() for l in t.splitlines() if l.strip()]

def library_record(rec):
    """Latest Internet Archive copy (HTTP 200) of a UN Digital Library voting record -> (summary, {ISO3: Y/N/A/''}, snapshot url)."""
    f = os.path.join(CACHE, f"undl_{rec}.html")
    snap = os.path.join(CACHE, f"undl_{rec}.snapshot")
    if not os.path.exists(f):
        for i in range(6):
            r = subprocess.run(["curl", "-sS", f"https://web.archive.org/cdx/search/cdx?url=digitallibrary.un.org/record/{rec}&filter=statuscode:200&fl=timestamp&output=json"], capture_output=True, text=True)
            try: ts = [row[0] for row in json.loads(r.stdout)[1:]]; break
            except Exception: time.sleep(5)
        else: raise SystemExit(f"no archive index for record {rec}")
        for t in reversed(ts):  # newest copy that actually contains the vote list
            url = f"https://web.archive.org/web/{t}id_/https://digitallibrary.un.org/record/{rec}"
            try: curl(url, f)
            except SystemExit: continue
            if "Voting Summary" in open(f, encoding="utf-8", errors="replace").read():
                open(snap, "w").write(url.replace("id_/", "/")); break
        else: raise SystemExit(f"no usable copy of record {rec}")
    lines = text_of(open(f, encoding="utf-8", errors="replace").read())
    summ = next(l for l in lines if l.startswith("Yes:"))
    i = lines.index("Vote", lines.index("Vote date")) + 1
    votes = {}
    for l in lines[i:]:
        m = re.match(r"^([YNA]) (.+)$", l)
        v, name = (m.group(1), m.group(2)) if m else ("", l)
        k = norm(name)
        if k not in M: break  # end of the vote list
        votes[M[k]] = v
    return summ, votes, open(snap).read().strip()

def meeting_record(symbol):
    """Recorded vote in an official meeting record PDF -> {ISO3: Y/N/A}."""
    pdf = os.path.join(CACHE, symbol.replace("/", "_") + ".pdf")
    if not os.path.exists(pdf): curl(f"https://documents.un.org/api/symbol/access?s={symbol}&l=en&t=pdf", pdf)
    t = subprocess.run(["pdftotext", pdf, "-"], capture_output=True, text=True).stdout
    t = t[t.index("A recorded vote was taken."):]
    t = re.sub(r"Draft resolution\s+\S+\s*$", "", t[:t.index("was adopted by")])
    # drop page furniture: form feeds, job numbers (22-62623), page numbers (11/20), dates, the document symbol
    t = re.sub(r"\x0c|\b\d{2}-\d{5}\b|\b\d{1,2}/\d{1,2}(/\d{4})?\b|A/ES-11/PV\.\d+", " ", t)
    out = {}
    for key, lab in (("Y", "In favour:"), ("N", "Against:"), ("A", "Abstaining:")):
        seg = t[t.index(lab) + len(lab):]
        ends = [seg.index(x) for x in ("In favour:", "Against:", "Abstaining:") if x in seg]
        seg = seg[:min(ends)] if ends else seg
        seg = seg.replace("’", "'")
        # names containing commas are written "Bolivia (Plurinational State of)"; split on commas outside parentheses.
        # The record is two-column, so a list can run into a speech: a name followed by a paragraph break ends the list.
        for tok in re.split(r",(?![^()]*\))", seg):
            paras = [re.sub(r"\s+", " ", x).strip() for x in re.split(r"\n\s*\n", tok) if x.strip()]
            if not paras: continue
            whole = " ".join(paras).rstrip(".")
            if norm(whole) in M: out[M[norm(whole)]] = key; continue
            first = paras[0].rstrip(".")
            out[iso(first)] = key
            break
    return out

os.makedirs(CACHE, exist_ok=True)
LAB = {"yes": "In favour", "no": "Against", "abstain": "Abstained", "absent": "Did not vote"}
CODE = {"Y": "yes", "N": "no", "A": "abstain", "": "absent"}
sets, notes = {}, []
for key, (rec, sym, date, title, exp, pv) in VOTES.items():
    summ, votes, snap = library_record(rec)
    assert sorted(votes) == MEMBERS, (key, set(MEMBERS) ^ set(votes))
    got = tuple(sum(1 for v in votes.values() if v == c) for c in ("Y", "N", "A", ""))
    assert got == exp, (key, got, exp, summ)
    if pv:  # cross-check against the meeting record
        rec_pv = meeting_record(pv)
        diff = {k: (votes[k], rec_pv.get(k, "")) for k in MEMBERS if votes[k] != rec_pv.get(k, "")}
        assert not diff, (key, diff)
    sets[key] = {"label": f"{sym}, {date}", "values": {k: CODE[v] for k, v in sorted(votes.items())}, "labels": LAB}
    notes.append(f"{sym} ({date}, '{title}'): {exp[0]} in favour, {exp[1]} against, {exp[2]} abstentions, {exp[3]} did not vote; "
                 f"UN Digital Library record {rec} (https://digitallibrary.un.org/record/{rec}, read via {snap})"
                 + (f", identical to meeting record {pv}" if pv else ""))
    print(key, got)

# derived: who stayed in favour between the first (2022) and the latest (2026) vote
a, b = sets["es11_1"]["values"], sets["es11_10"]["values"]
shift = {k: ("kept" if a[k] == "yes" and b[k] == "yes" else "left" if a[k] == "yes" else "joined" if b[k] == "yes" else None) for k in MEMBERS}
sets["shift"] = {"label": "In favour in March 2022 and in February 2026", "values": {k: v for k, v in shift.items() if v},
                 "labels": {"kept": "In favour both times", "left": "In favour in 2022, not in 2026", "joined": "In favour in 2026, not in 2022"}}

data = {"source": "editorial", "asOf": "2026-02-24", "retrieved": time.strftime("%Y-%m-%d"),
        "note": "Recorded votes of the 193 UN Member States in the General Assembly's eleventh emergency special session. "
                "'Did not vote' means the delegation was absent or did not take part (blank in UN records). "
                + "; ".join(notes) + ". Votes are facts typed from UN records; UN Digital Library content is (c) United Nations.",
        "sets": sets}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(data, open(OUT, "w"), ensure_ascii=False, separators=(",", ":"))
print("wrote", OUT, os.path.getsize(OUT), "bytes")
