#!/usr/bin/env python3
"""Regimes of the World 1900-2025 and form of government today -> data/politics/regimes.json,
data/politics/regime_counts.json, data/politics/forms.json

Sources
- V-Dem v16 "Regimes of the World" (Luehrmann, Tannenberg & Lindberg 2018), via Our World in Data's grapher
  (ourworldindata.org/grapher/political-regime.csv, indicator 1210053, "regime_row_owid"). V-Dem's own licence is
  CC BY-SA 4.0 (v-dem.net, "Do I need permission to use the V-Dem dataset?"); OWID's metadata says CC BY 4.0, which
  understates it. Files derived from it are shared under CC BY-SA 4.0. V-Dem's own download needs an e-mail form; we
  do not use it. OWID fills years before independence from the ruling or parent state for some countries
  (github.com/owid/etl .../democracy/2025-03-17/vdem/vdem.countries_impute.yml); V-Dem itself codes many colonies.
- Wikidata (CC0): sovereign states (P31 Q3624078, not dissolved), P122 basic form of government, P31 instance of,
  P1906 office held by head of state, P35 head of state, P6 head of government, and for heads of state P106 occupation.
  Fetched with the query service (list of states) and wbgetentities (claims), generic User-Agent, slow batches.
- CIA World Factbook "Government type" (public domain; archive github.com/factbook/factbook.json, CC0), cloned by
  tools/build/independence.py into .cache/factbook/repo.

Form of government: rules (in this order; the first that matches wins)
 1 Theocracy: Wikidata P122 names a theocracy or the papacy AND the Factbook says "theocratic" or "ecclesiastical".
 2 One-party state: Wikidata names a one-party state, communist state or communist dictatorship, or the Factbook
   says "communist" or "single-party". (Checked before monarchy: Wikidata calls North Korea a "hermit kingdom".)
 3 Monarchy: the head-of-state office (P1906), P31 or P122 names a monarch, king, queen, emir, sultan, prince,
   grand duke, emperor, co-prince, Yang di-Pertuan Agong or a Commonwealth realm, or the Factbook says "monarchy".
   3a Ruling monarchy: Wikidata or Factbook says "absolute monarchy", or V-Dem codes the country a closed autocracy in
      2025 (no elected chief executive).  3b Otherwise: constitutional monarchy (an elected government governs).
 4 Military government: Wikidata P122 names a military junta, or the head-of-state office names a military council,
   or the Factbook says "military"; OR V-Dem codes the country a closed autocracy in 2025 and its head of state
   (Wikidata) has the occupation military officer / military personnel and took office in 2019 or later.
 5 Transitional / other: Wikidata names a provisional government or a directorial system, or the Factbook says
   "in transition", "transitional" or "formerly".
 6 Republics: the system named by Wikidata P122 (presidential, semi-presidential, parliamentary; "super-presidential"
   counts as presidential). If Wikidata names none, several, or a different one than the Factbook, the Factbook's
   term is used. If neither names one: presidential when the head of state is also head of government, else other.
"""
import csv, glob, json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(ROOT, ".cache", "governments")
OUTDIR = os.path.join(ROOT, "data", "politics")
os.makedirs(CACHE, exist_ok=True); os.makedirs(OUTDIR, exist_ok=True)
UA = {"User-Agent": "Orbis-data-build/1.0"}
TODAY = time.strftime("%Y-%m-%d")

def get(url, path, accept=None):
    p = os.path.join(CACHE, path)
    if os.path.exists(p): return p
    h = dict(UA)
    if accept: h["Accept"] = accept
    for a in range(12):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=180) as r: data = r.read()
            if b'"maxlag"' in data[:200]: time.sleep(40); continue
            open(p, "wb").write(data); return p
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504): raise
            time.sleep(min(int(e.headers.get("Retry-After") or 30), 120) + 5)
    raise SystemExit("download failed: " + url)

# ---------------- V-Dem Regimes of the World via OWID ----------------
csvp = get("https://ourworldindata.org/grapher/political-regime.csv?v=1&csvType=full&useColumnShortNames=true", "political-regime.csv")
get("https://ourworldindata.org/grapher/political-regime.metadata.json?v=1&csvType=full&useColumnShortNames=true", "political-regime.metadata.json")
meta = json.load(open(get("https://api.ourworldindata.org/v1/indicators/1210053.metadata.json", "ind.json")))
origin = meta["origins"][0]
rows = list(csv.DictReader(open(csvp, encoding="utf-8")))
MAPCODE = {"OWID_KOS": "XKX", "OWID_SML": "SOL"}       # map ids; other OWID_ entities are historical states or Zanzibar
Y0, Y1 = 1900, 2025
byYear, counts = {}, {"dem": {}, "aut": {}, "lib": {}, "ele": {}, "ea": {}, "ca": {}}
for y in range(Y0, Y1 + 1): byYear[str(y)] = {}
cnt = {y: [0, 0, 0, 0] for y in range(Y0, Y1 + 1)}
for r in rows:
    y = int(r["year"]); c = r["code"]
    if not (Y0 <= y <= Y1) or not c or c == "OWID_ZAN": continue   # Palestine (Gaza / West Bank, no code) and Zanzibar left out
    v = int(r["regime_row_owid"]); cnt[y][v] += 1               # counts include historical states (e.g. both Germanys)
    iso = MAPCODE.get(c, c)
    if len(iso) == 3 and not iso.startswith("OWID"): byYear[str(y)][iso] = str(v)
years = list(range(Y0, Y1 + 1))
regimes = {
    "source": "vdem", "asOf": "2025-12-31", "retrieved": TODAY,
    "note": ("V-Dem v16 Regimes of the World (Luehrmann, Tannenberg & Lindberg 2018), via Our World in Data (indicator "
             "regime_row_owid, updated " + meta.get("updatedAt", "")[:10] + "). Licence CC BY-SA 4.0 (V-Dem); this file "
             "is shared under CC BY-SA 4.0. Today's borders; a country is coloured by the regime of the state that "
             "ruled it, where V-Dem or OWID gives one (OWID imputes some pre-independence years from the ruling or "
             "parent state). Divided states (Germany 1949-90, Vietnam to 1975, Yemen to 1990) have no single value "
             "and show as no data, as do Palestine and countries V-Dem does not cover (mostly small states)."),
    "sets": {"regime": {"label": "Political regime (V-Dem)", "labels": {
        "0": "Closed autocracy", "1": "Electoral autocracy", "2": "Electoral democracy", "3": "Liberal democracy"},
        "byYear": byYear}}}
json.dump(regimes, open(os.path.join(OUTDIR, "regimes.json"), "w"), separators=(",", ":"), ensure_ascii=False)
regime_counts = {
    "source": "vdem", "asOf": "2025-12-31", "retrieved": TODAY,
    "note": ("Number of countries and territories in each regime type per year, V-Dem v16 via Our World in Data. "
             "Counts include every entity in the data in that year with a code (historical states such as East and "
             "West Germany, colonies V-Dem codes, Kosovo, Somaliland), and leave out Zanzibar and Palestine. "
             "CC BY-SA 4.0."),
    "years": years,
    "series": {"count": {"label": "Countries", "units": "countries", "values": {
        "dem": [cnt[y][2] + cnt[y][3] for y in years], "aut": [cnt[y][0] + cnt[y][1] for y in years]}},
        "bytype": {"label": "Countries", "units": "countries", "values": {
        "ld": [cnt[y][3] for y in years], "ed": [cnt[y][2] for y in years],
        "ea": [cnt[y][1] for y in years], "ca": [cnt[y][0] for y in years]}}}}
json.dump(regime_counts, open(os.path.join(OUTDIR, "regime_counts.json"), "w"), separators=(",", ":"))
reg25 = {k: int(v) for k, v in byYear["2025"].items()}

# ---------------- Wikidata ----------------
SPARQL = """SELECT ?s ?iso WHERE { ?s wdt:P31 wd:Q3624078 ; wdt:P298 ?iso . FILTER NOT EXISTS { ?s wdt:P576 ?d } }"""
sp = get("https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": SPARQL}), "states_sparql.json",
         "application/sparql-results+json")
qids = sorted({b["s"]["value"].rsplit("/", 1)[1] for b in json.load(open(sp))["results"]["bindings"]})
KEEP = {"P31", "P35", "P6", "P122", "P1906", "P298"}
def entities(ids, tag, props, keep):
    out = {}
    for i in range(0, len(ids), 25):
        part = ids[i:i + 25]
        p = os.path.join(CACHE, "ent", f"{tag}_{i // 25}.json"); os.makedirs(os.path.dirname(p), exist_ok=True)
        if not os.path.exists(p):
            url = ("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&languages=en&maxlag=10&props="
                   + props + "&ids=" + "|".join(part))
            tmp = get(url, "tmp.json"); d = json.load(open(tmp)); os.remove(tmp)
            for e in d["entities"].values():
                if "claims" in e: e["claims"] = {k: v for k, v in e["claims"].items() if k in keep}
            json.dump(d, open(p, "w")); time.sleep(8)
        out.update(json.load(open(p))["entities"])
    return out
S = entities(qids, "state", "claims|labels", KEEP)
def current(e, prop):
    out = []
    for c in e.get("claims", {}).get(prop, []):
        if c["rank"] == "deprecated" or "P582" in c.get("qualifiers", {}): continue
        v = c["mainsnak"].get("datavalue", {}).get("value")
        if isinstance(v, dict) and "id" in v:
            st = c.get("qualifiers", {}).get("P580", [{}])[0].get("datavalue", {}).get("value", {}).get("time")
            out.append((v["id"], c["rank"], st))
    if any(r == "preferred" for _, r, _ in out): out = [o for o in out if o[1] == "preferred"]
    return out
refs = sorted({x[0] for e in S.values() for p in ("P31", "P122", "P1906", "P35", "P6") for x in current(e, p)})
REF = entities(refs, "ref", "claims|labels", {"P106"})
occ = sorted({o["mainsnak"]["datavalue"]["value"]["id"] for e in REF.values() for o in e.get("claims", {}).get("P106", [])
              if "datavalue" in o["mainsnak"]})
OCC = entities([o for o in occ if o not in REF], "occ", "labels", set())
def lab(q):
    e = REF.get(q) or OCC.get(q) or {}
    return ((e.get("labels") or {}).get("en") or {}).get("value") or q

# ---------------- Factbook ----------------
src = open(os.path.join(ROOT, "tools", "build", "independence.py")).read()
GEC = eval(re.search(r"GEC = (\{.*?\})\n", src, re.S).group(1)); GEC["tw"] = "TWN"
FB = {}
for f in glob.glob(os.path.join(ROOT, ".cache", "factbook", "repo", "*", "*.json")):
    c = os.path.basename(f)[:-5]
    if c in GEC:
        t = ((json.load(open(f)).get("Government") or {}).get("Government type") or {}).get("text", "")
        FB[GEC[c]] = re.sub(r"\s+", " ", t.replace("&nbsp;", " ")).strip()
fbcommit = subprocess.run(["git", "-C", os.path.join(ROOT, ".cache", "factbook", "repo"), "log", "-1", "--format=%cs"],
                          capture_output=True, text=True).stdout.strip()

MON = re.compile(r"monarch|\bking\b|queen|emir|sultan|prince|grand duke|emperor|co-prince|yang di-pertuan|commonwealth realm|kingdom|principality|grand duchy", re.I)
def system_of(text):
    t = text.lower(); out = set()
    if "semi-presidential" in t: out.add("semi")
    if re.search(r"(?<!semi-)(?<!super-)presidential", t) or "super-presidential" in t: out.add("pres")
    if "parliamentary" in t or "westminster" in t: out.add("parl")
    return out

forms, why, rows_out = {}, {}, []
for q, e in S.items():
    isos = [c["mainsnak"]["datavalue"]["value"] for c in e["claims"].get("P298", []) if c["rank"] != "deprecated" and "datavalue" in c["mainsnak"]]
    iso = {"XKS": "XKX"}.get(isos[0], isos[0])
    p122 = [lab(x[0]) for x in current(e, "P122")]; p31 = [lab(x[0]) for x in current(e, "P31")]
    office = [lab(x[0]) for x in current(e, "P1906")]
    hos = current(e, "P35"); hog = current(e, "P6")
    fb = FB.get(iso, ""); fbl = fb.lower(); wd = " | ".join(p122 + p31 + office).lower()
    v = reg25.get(iso)
    def mil_head():
        for pid, _, start in hos:
            o = [lab(x["mainsnak"]["datavalue"]["value"]["id"]) for x in (REF.get(pid) or {}).get("claims", {}).get("P106", []) if "datavalue" in x["mainsnak"]]
            if any(k in o for k in ("military officer", "military personnel")) and start and int(start[1:5]) >= 2019: return True
        return False
    if re.search(r"theocra|papacy", " ".join(p122).lower()) and re.search(r"theocratic|ecclesiastical", fbl):
        f, w = "theo", "rule 1"
    elif re.search(r"one-party state|communist state|communist dictatorship", wd) or re.search(r"communist|single-party", fbl):
        f, w = "onep", "rule 2"
    elif MON.search(" | ".join(office + p31 + p122)) or "monarchy" in fbl:
        if "absolute monarchy" in wd or "absolute monarchy" in fbl or v == 0: f, w = "amon", "rule 3a"
        else: f, w = "cmon", "rule 3b"
    elif re.search(r"military junta|military council|military leader", wd) or "military" in fbl or (v == 0 and mil_head()):
        f, w = "mil", "rule 4"
    elif re.search(r"provisional government|directorial", wd) or re.search(r"in transition|transitional|formerly", fbl):
        f, w = "other", "rule 5"
    else:
        ws, fs = system_of(" | ".join(p122)), system_of(fb)
        if len(ws) == 1 and (not fs or ws == fs): f, w = next(iter(ws)), "rule 6 (Wikidata" + (" = Factbook)" if fs else ")")
        elif len(fs) == 1: f, w = next(iter(fs)), "rule 6 (Factbook" + (", Wikidata differs)" if ws else ")")
        elif hos and hog and {x[0] for x in hos} == {x[0] for x in hog}: f, w = "pres", "rule 6 (head of state = head of government)"
        else: f, w = "other", "rule 6 (no system named)"
    forms[iso] = f; why[iso] = w
    rows_out.append([iso, lab(q) if q in REF else ((e.get("labels") or {}).get("en") or {}).get("value"), f, w, "; ".join(p122), fb])

LABELS = {"pres": "Presidential republic", "semi": "Semi-presidential republic", "parl": "Parliamentary republic",
          "cmon": "Constitutional monarchy", "amon": "Monarchy where the monarch rules", "onep": "One-party state",
          "mil": "Military government", "theo": "Theocracy", "other": "Transitional or other"}
agree = sum(1 for r in rows_out if "= Factbook" in r[3]); fbonly = sum(1 for r in rows_out if "(Factbook" in r[3])
out = {"source": "wikidata", "asOf": TODAY, "retrieved": TODAY,
       "note": ("Form of government of " + str(len(forms)) + " sovereign states (Wikidata P31 Q3624078), classified by "
                "documented rules from Wikidata (P122 basic form of government, P1906 office of head of state, P35/P6 "
                "heads, P106 occupation; CC0), the CIA World Factbook 'Government type' (public domain, archive of "
                + fbcommit + ") and V-Dem v16 Regimes of the World 2025 (CC BY-SA 4.0; used for rules 3a and 4, so this "
                "file is shared under CC BY-SA 4.0). Rules, in order: (1) theocracy if both Wikidata and the Factbook "
                "say so; (2) one-party state if a source says one-party or communist state; (3) monarchy if the head "
                "of state is a monarch, split into 'monarch rules' when a source says absolute monarchy or V-Dem finds "
                "no elected chief executive (closed autocracy), else constitutional; (4) military government if a "
                "source names a junta or military council, or V-Dem codes a closed autocracy and the head of state is "
                "a military officer who took office in 2019 or later; (5) transitional or other (provisional "
                "government, directorial system, 'in transition'); (6) republics by system: Wikidata's term, the "
                "Factbook's where Wikidata names none, several or a different one; if neither, presidential when "
                "one person is head of state and government. For republics, Wikidata and the Factbook agreed on "
                + str(agree) + " states; the Factbook decided " + str(fbonly) + ". Formal constitutions and practice "
                "differ: a 'presidential republic' may be a dictatorship (see the V-Dem regime layer)."),
       "sets": {"form": {"label": "Form of government", "labels": LABELS, "values": forms}}}
json.dump(out, open(os.path.join(OUTDIR, "forms.json"), "w"), separators=(",", ":"), ensure_ascii=False)
with open(os.path.join(CACHE, "forms_audit.tsv"), "w") as fh:
    for r in sorted(rows_out): fh.write("\t".join(str(x) for x in r) + "\n")
from collections import Counter
print("regimes 2025:", Counter(reg25.values()), "forms:", Counter(forms.values()), "agree", agree, "factbook", fbonly)
for fn in ("regimes.json", "regime_counts.json", "forms.json"):
    print(fn, os.path.getsize(os.path.join(OUTDIR, fn)), "bytes")
