#!/usr/bin/env python3
"""National elections for the elections explorer -> data/elections/world.json + data/elections/<ISO3>.json.

Sources (all CC0, so the output is free of licence conditions; credit given anyway):
  - ParlGov 2024 Release (Doering & Manow, Harvard Dataverse doi:10.7910/DVN/2VZ5ZC, CC0 1.0):
    lower-house elections in 37 EU/OECD democracies 1945-2023 with every party's vote share, seats
    and party family. Turnout = votes_cast / electorate from the `election` table.
  - Wikidata (CC0 1.0): every item that is an instance of a subclass of "election" (Q40231) with a
    country (P17) that has an ISO 3166 alpha-3 code (P298). Used fields: P585 date, P1867 eligible voters,
    P1868 ballots cast, P1697 valid votes, P726 candidate/party (+ qualifiers P1111 votes, P1410 seats,
    P210 party), P991 successful candidate (+ P1410 seats), P1342 seats, P527/P361 rounds.
    Party family comes from the party's political alignment (P1387), with green/regionalist ideology (P1142).
  - MEDSL "U.S. President 1976-2024" (MIT Election Data and Science Lab, doi:10.7910/DVN/42MVDX, CC0 1.0):
    national popular-vote totals summed from the state rows.

Merging: ParlGov parliament elections are used as published; Wikidata adds parliament elections after
ParlGov's last one in that country (2023 onwards) and everywhere ParlGov does not cover, plus all direct
presidential elections. US presidential results come from MEDSL (turnout from Wikidata where present).

Selection rules (see assemble/wd_election):
  - Country items: P298 holders plus items holding the same code at deprecated rank (NLD: Netherlands Q55 vs the Kingdom).
  - Parts (P527) of a national election that are elections themselves (the legislative/presidential halves of a general
    election) are kept; only parts labelled as rounds are folded into their parent. P1545 on P726 counts as a round only
    when it repeats across candidates; otherwise it is a ballot/list number and ignored.
  - Bare items (no results, no turnout) within 31 days of a same-type item with data are dropped as duplicates.
  - Winner, parliament: most seats, else most votes. Winner, president: the single successful candidate (P991) of the
    deciding round; without one, the leader only with an outright majority (>50% of valid votes). No winner while a
    later round has no results (run-off pending or unrecorded) -- such rows carry "decided": false. A first-round
    leader is never shown as the winner. P991 on a non-final round (candidates who advanced) is ignored.
  - world.json `last` = the newest election with a known winner; `latest` = the newest election on record when it is
    later than `last` (results not in the sources yet). OVERRIDES fills a few winners Wikidata lacks (sourced inline).
  - Names: English label, else Wikidata's multilingual label, else the English Wikipedia title, else another
    language's label; rows still without a name are folded into Others, never shown as a QID.

Raw downloads and Wikidata responses are cached in .cache/elections/ (gitignored).
Run: python3 tools/build/elections.py   (the Wikidata harvest takes ~30 min the first time)
"""
import csv, datetime, io, json, os, re, sqlite3, sys, time, urllib.error, urllib.parse, urllib.request
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE = os.path.join(ROOT, ".cache", "elections"); WD = os.path.join(CACHE, "wd")
OUT = os.path.join(ROOT, "data", "elections")
for d in (CACHE, WD, OUT): os.makedirs(d, exist_ok=True)
UA = "Orbis-data-build/1.0 (open-source map site)"
TODAY = datetime.date.today().isoformat()
ASOF = "ParlGov 2024 Release (2024-08-12); Wikidata as of %s; MEDSL U.S. President 1976-2024 V10" % TODAY

def get(url, data=None, accept=None, timeout=120):
    h = {"User-Agent": UA}
    if accept: h["Accept"] = accept
    req = urllib.request.Request(url, data=data, headers=h)
    return urllib.request.urlopen(req, timeout=timeout).read()

def fetch(url, path):
    if not os.path.exists(path):
        open(path, "wb").write(get(url))
    return path

def retry(fn, tries=30):
    for i in range(tries):
        try: return fn()
        except urllib.error.HTTPError as e:
            if e.code == 404: raise SystemExit("not found")  # deleted/merged entity: retrying will not help
            wait = int(e.headers.get("Retry-After") or 0) or 10 * (i + 1)
            print("  retry in %ss:" % wait, e, file=sys.stderr); time.sleep(min(wait + 1, 300))
        except Exception as e:
            print("  retry:", e, file=sys.stderr); time.sleep(min(10 * (i + 1), 120))
    raise SystemExit("request failed")

# ------------------------------------------------------------------ ParlGov
PG_DB = fetch("https://dataverse.harvard.edu/api/access/datafile/10437086", os.path.join(CACHE, "pg_stable.db"))
# family mapping: ParlGov top family -> explorer family
PG_FAM = {"com": "left", "soc": "centre-left", "eco": "green", "lib": "liberal", "chr": "centre-right",
          "con": "centre-right", "agr": "centre", "right": "right", "spec": "other", "none": "other", "code": None}

def parlgov():
    c = sqlite3.connect(PG_DB)
    fam = {r[0]: r[1] for r in c.execute("select party_id, family_name_short from view_party")}
    sub = defaultdict(set)  # party -> sub-families (info_id short names, e.g. reg, eth)
    for pid, short in c.execute("select pf.party_id, i.short from party_family pf join info_id i on i.id = pf.type_id"):
        sub[pid].add(short)
    pinfo = {r[0]: r for r in c.execute("select id, name_short, name_english, wikipedia from party")}
    out = defaultdict(list)
    q = """select e.id, c.name_short, e.date, e.seats_total, e.electorate, e.votes_cast, e.votes_valid
           from election e join country c on c.id = e.country_id
           where e.type_id = 13 and e.date >= '1945-01-01' order by e.date"""
    for eid, iso, date, seats_total, electorate, cast, valid in c.execute(q).fetchall():
        parties = []
        for pid, seats, share in c.execute("select party_id, seats, vote_share from election_result where election_id = ?", (eid,)):
            _, short, name, wiki = pinfo[pid]
            f = PG_FAM.get(fam.get(pid))
            if fam.get(pid) == "spec" and sub[pid] & {"reg", "eth"}: f = "regional"
            if short in ("none", "one-seat", "no-seat", "ind", "Ind"): f = "independent" if short != "no-seat" else "other"
            parties.append({"name": name, "abbr": short if short not in ("none", "one-seat", "no-seat", "other") else None,
                            "share": share, "seats": seats, "family": f, "wiki": wiki})
        turnout = round(100.0 * cast / electorate, 1) if cast and electorate and 0 < cast <= electorate else None
        out[iso].append({"date": int(date.replace("-", "")), "type": "parliament", "turnout": turnout,
                         "parties": parties, "seatsTotal": seats_total, "source": "parlgov"})
    return out

# ------------------------------------------------------------------ MEDSL (US president)
def medsl():
    p = os.path.join(ROOT, ".cache", "us_medsl", "1976-2024-president.csv")
    if not os.path.exists(p):
        p = fetch("https://dataverse.harvard.edu/api/access/datafile/13887042", os.path.join(CACHE, "1976-2024-president.csv"))
    tot = defaultdict(lambda: defaultdict(int)); allv = defaultdict(int); party = {}
    for r in csv.DictReader(open(p, encoding="utf-8")):
        y = int(r["year"]); cand = (r["candidate"] or "").strip(); v = int(r["candidatevotes"] or 0)
        allv[y] += v
        if not cand or cand.upper() in ("OTHER", "WRITEIN", "SCATTERING", ""): cand = "OTHER"
        tot[y][cand] += v
        pt = (r.get("party_simplified") or "").strip()
        if cand != "OTHER" and v > party.get((y, cand), ("", 0))[1]: party[(y, cand)] = (pt, v)
    res = {}
    for y, d in tot.items():
        res[y] = (allv[y], d, {k: v[0] for (yy, k), v in party.items() if yy == y})
    return res

# ------------------------------------------------------------------ Wikidata harvest
def sparql(q):
    return retry(lambda: json.loads(get("https://query.wikidata.org/sparql", data=urllib.parse.urlencode({"query": q}).encode(),
                                        accept="application/sparql-results+json", timeout=90)))["results"]["bindings"]

def country_items():
    """[(country QID, ISO3)]: items with a current ISO 3166 alpha-3 code (P298), plus items that hold the same code at
    deprecated/normal rank behind a preferred one (e.g. NLD: the code sits on the Kingdom, Q29999, while Dutch
    elections use P17 = Netherlands, Q55, whose P298 is deprecated; DNK: Denmark Q35 vs Kingdom of Denmark Q756617).
    Only codes that some current country carries are kept, so retired codes (BUR, TMP...) are ignored."""
    cp = os.path.join(WD, "countries.json")
    if not os.path.exists(cp):
        json.dump(sparql("SELECT ?c ?iso WHERE { ?c wdt:P298 ?iso . FILTER NOT EXISTS { ?c wdt:P576 ?end } }"), open(cp, "w"))
    xp = os.path.join(WD, "countries_extra.json")
    if not os.path.exists(xp):
        json.dump(sparql("SELECT ?c ?iso WHERE { ?c p:P298/ps:P298 ?iso . FILTER NOT EXISTS { ?c wdt:P298 ?iso } "
                         "FILTER NOT EXISTS { ?c wdt:P576 [] } }"), open(xp, "w"))
    main = [(b["c"]["value"].rsplit("/", 1)[1], b["iso"]["value"]) for b in json.load(open(cp))]
    codes = {iso for _, iso in main}
    extra = [(b["c"]["value"].rsplit("/", 1)[1], b["iso"]["value"]) for b in json.load(open(xp))]
    return main + sorted({x for x in extra if x[1] in codes and x not in main})

def wd_lists():
    kp = os.path.join(WD, "classes.json")
    if not os.path.exists(kp):
        json.dump({"results": {"bindings": sparql("SELECT ?cls WHERE { ?cls wdt:P279* wd:Q40231 }")}}, open(kp, "w"))
    classes = {b["cls"]["value"].rsplit("/", 1)[1] for b in json.load(open(kp))["results"]["bindings"]}
    lists = {}
    for q, iso in country_items():
        path = os.path.join(WD, "list_%s_%s.json" % (iso, q))
        if not os.path.exists(path):
            r = sparql("SELECT DISTINCT ?e ?cls WHERE { ?e wdt:P17 wd:%s ; wdt:P585 ?d ; wdt:P31 ?cls . FILTER(YEAR(?d) >= 1945) }" % q)
            json.dump(sorted({x["e"]["value"].rsplit("/", 1)[1] for x in r if x["cls"]["value"].rsplit("/", 1)[1] in classes}), open(path, "w"))
            print(" ", iso, file=sys.stderr); time.sleep(0.5)
        lists.setdefault(iso, set()).update(json.load(open(path)))
    return lists, classes

KEEP = {"P31", "P17", "P585", "P1001", "P1867", "P1868", "P1697", "P726", "P991", "P1342", "P527", "P361", "P541",
        "P102", "P1387", "P1142", "P1813", "P279", "P1366"}

LABEL_LANGS = ["en", "mul", "en-gb", "en-ca", "en-us", "es", "fr", "pt", "de", "it", "nl", "pl", "sv", "da", "nb", "fi", "cs",
               "sk", "sl", "hr", "ro", "hu", "tr", "id", "ms", "tl", "vi", "sq", "lt", "lv", "et", "ca", "eu", "gl"]

def pick_label(labels, enwiki=None):
    """English label, else the multilingual default ('mul', where Wikidata now keeps most personal names), else the
    English Wikipedia title (minus a disambiguator), else a label in a Latin-script language, else any label."""
    for l in LABEL_LANGS[:2]:
        if labels.get(l, {}).get("value"): return labels[l]["value"]
    if enwiki: return re.sub(r" \([^)]*\)$", "", enwiki)
    for l in LABEL_LANGS[2:]:
        if labels.get(l, {}).get("value"): return labels[l]["value"]
    return next((v["value"] for v in labels.values() if v.get("value")), None)

def fill_labels(*caches):
    """Entities cached without an English label: fetch all their labels (wbgetentities, 50 per request; cached in
    labels_any.json) and pick one with pick_label. Unresolved ones keep label None (their rows fold into Others)."""
    path = os.path.join(WD, "labels_any.json")
    have = json.load(open(path)) if os.path.exists(path) else {}
    need = sorted({q for c in caches for q, e in c.items() if e and not e.get("label")} - set(have))
    if need and not os.environ.get("ORBIS_OFFLINE"):
        for i in range(0, len(need), 50):
            chunk = need[i:i + 50]
            url = "https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode({
                "action": "wbgetentities", "ids": "|".join(chunk), "props": "labels|sitelinks", "sitefilter": "enwiki", "format": "json"})
            d = retry(lambda: json.loads(get(url)))
            for q in chunk:
                e = d.get("entities", {}).get(q) or {}
                have[q] = pick_label(e.get("labels", {}), e.get("sitelinks", {}).get("enwiki", {}).get("title")) or ""
            json.dump(have, open(path, "w")); time.sleep(1)
    for c in caches:
        for q, e in c.items():
            if e and not e.get("label") and have.get(q): e["label"] = have[q]

def trim(e):
    cl = {}
    for p, sts in e.get("claims", {}).items():
        if p not in KEEP: continue
        out = []
        for s in sts:
            if s.get("rank") == "deprecated": continue
            v = s["mainsnak"].get("datavalue", {}).get("value")
            qs = {}
            for qp, qv in s.get("qualifiers", {}).items():
                if qp in ("P1111", "P1410", "P210", "P518", "P1545", "P582", "P580", "P642", "P585", "P1114"):
                    qs[qp] = [x.get("datavalue", {}).get("value") for x in qv]
            out.append({"v": v, "q": qs, "r": s.get("rank")})
        cl[p] = out
    return {"id": e["id"], "label": pick_label(e.get("labels", {}), e.get("sitelinks", {}).get("enwiki", {}).get("title")),
            "enwiki": e.get("sitelinks", {}).get("enwiki", {}).get("title"), "claims": cl}

def wd_entities(ids, tag):
    """Fetch entities one by one from Special:EntityData (cache-friendly; the action API is rate-limited hard).
    Trimmed to the claims we use and cached in .cache/elections/wd/ents_<tag>.json."""
    from concurrent.futures import ThreadPoolExecutor
    path = os.path.join(WD, "ents_%s.json" % tag)
    have = json.load(open(path)) if os.path.exists(path) else {}
    todo = sorted(set(ids) - {k for k, v in have.items() if v is not None})  # failed fetches (None) are retried
    if os.environ.get("ORBIS_OFFLINE"):  # build from what is cached (missing entities are skipped)
        return have
    def one(q):
        try:
            d = retry(lambda: json.loads(get("https://www.wikidata.org/wiki/Special:EntityData/%s.json" % q, timeout=60)), tries=8)
        except SystemExit:
            return q, None
        e = d.get("entities", {}).get(q) or next(iter(d.get("entities", {}).values()), None)
        return q, trim(e) if e else None
    with ThreadPoolExecutor(3) as ex:
        for i, (q, e) in enumerate(ex.map(one, todo)):
            have[q] = e
            if i % 500 == 0:
                json.dump(have, open(path, "w")); print("  %s %d/%d" % (tag, i, len(todo)), file=sys.stderr)
    json.dump(have, open(path, "w"))
    return have

def wd_labels(ids):
    """English labels only (cheap), cached; used to drop local/constituency items before fetching claims."""
    from concurrent.futures import ThreadPoolExecutor
    path = os.path.join(WD, "labels_elections.json")
    have = json.load(open(path)) if os.path.exists(path) else {}
    todo = sorted(set(ids) - set(have))
    chunks = [todo[i:i + 50] for i in range(0, len(todo), 50)]
    def one(chunk):
        url = "https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode({
            "action": "wbgetentities", "ids": "|".join(chunk), "props": "labels", "languages": "en", "format": "json"})
        d = retry(lambda: json.loads(get(url)))
        return {k: e.get("labels", {}).get("en", {}).get("value", "") for k, e in d.get("entities", {}).items()}
    with ThreadPoolExecutor(1) as ex:
        for i, r in enumerate(ex.map(one, chunks)):
            have.update(r)
            if i % 100 == 0: json.dump(have, open(path, "w")); print("  labels %d/%d" % (i, len(chunks)), file=sys.stderr)
    json.dump(have, open(path, "w"))
    return have

def qid(v): return v.get("id") if isinstance(v, dict) else None
def amount(v):
    try: return float(v["amount"])
    except Exception: return None

# classes (and anything below them) that are not national popular elections
EXCLUDE_ROOTS = ["Q152450", "Q1057954", "Q1128324", "Q15261477", "Q669262", "Q6508670", "Q114775014", "Q15966540",
                 "Q24097670", "Q43109", "Q1006573", "Q11394707", "Q76853179"]
# "group of elections" (Q76853179) is excluded only when the item is not also a legislative/general/presidential election:
# Spanish and Chilean general elections are typed as both (class "Spanish general election" < group of elections).
GROUP_ROOT = "Q76853179"
PRESIDENT_ROOT = "Q858439"
BAD_WORDS = re.compile(r"\b(state election|regional|provincial|municipal|local|mayor|gubernatorial|by-election|primar|senate|"
                       r"senatorial|upper house|councillors|european parliament|leadership|referendum|county|city|prefectural|"
                       r"cantonal|district|constituency|governor|landtag|federal council|indirect|constituent|indigenous|"
                       r"recall|vice[- ]presiden|rajya sabha|council of states|united states elections|house of lords|kurdistan|autonomous|territorial|assembly of the republic of srpska|"
                       r"electoral college|speaker|caucus|primary|party congress|state duma by|"
                       # not elections themselves, or not the national lower house / popular vote
                       r"polls?|polling|opinion|nominations?|candidates?|next|s[aá]mi|seanad|results of|"
                       r"president of the (chamber|senate|national assembly|congress|parliament|house)|chairman)", re.I)
ROUND = re.compile(r"\bround\b|ballot|run-?off|\bstage\b|\btour\b", re.I)

# presidents chosen by parliament or an electoral body (not a popular vote) throughout the period
INDIRECT = {"IND", "DEU", "ITA", "GRC", "ISR", "LVA", "EST", "HUN", "ALB", "BGD", "PAK", "LBN", "IRQ", "CHE", "VNM", "CHN",
            "MLT", "TTO", "DMA", "NPL", "MUS", "VUT", "ETH", "SOM", "BWA", "ZAF", "MMR", "LAO", "CUB", "SMR", "AND", "LBY",
            "FJI", "WSM", "ESH"}
LEG_ROOTS = ["Q2618461", "Q1076105"]  # legislative election, general election

def subclasses(root):
    """All subclasses of the roots we need, fetched in one query (WDQS may be limited to 1 request a minute)."""
    path = os.path.join(WD, "sub_all.json")
    if not os.path.exists(path):
        roots = " ".join("wd:" + r for r in EXCLUDE_ROOTS + LEG_ROOTS + [PRESIDENT_ROOT])
        rows = sparql("SELECT ?c ?root WHERE { VALUES ?root { %s } ?c wdt:P279* ?root }" % roots)
        out = defaultdict(list)
        for r in rows: out[r["root"]["value"].rsplit("/", 1)[1]].append(r["c"]["value"].rsplit("/", 1)[1])
        json.dump(out, open(path, "w"))
    return set(json.load(open(path)).get(root, [root]))

def national_items(lists):
    """Candidate national elections: items whose class is (a subclass of) legislative/general/presidential election,
    or plain 'public election'/'snap election', with no electoral district (P768), dated 1945+, whose English label
    names the country (label, alias or demonym) and is not local, regional, a by-election, etc."""
    path = os.path.join(WD, "national_labels.json")
    if not os.path.exists(path):
        cl = sorted(set().union(*[subclasses(r) for r in LEG_ROOTS + [PRESIDENT_ROOT]]) | {"Q40231", "Q1333366"})
        q = ("SELECT ?e ?l ?d ?j WHERE { VALUES ?cls { %s } ?e wdt:P31 ?cls ; wdt:P585 ?d ; wdt:P17 ?c . MINUS { ?e wdt:P768 [] } "
             "FILTER(?d >= \"1945-01-01\"^^xsd:dateTime) ?e rdfs:label ?l . FILTER(LANG(?l)=\"en\") OPTIONAL { ?e wdt:P1001 ?j } }"
             % " ".join("wd:" + c for c in cl))
        json.dump({"results": {"bindings": sparql(q)}}, open(path, "w"))
    npath = os.path.join(WD, "country_names.json")
    if not os.path.exists(npath):
        time.sleep(60)
        json.dump({"results": {"bindings": sparql(
            'SELECT ?c ?iso ?n WHERE { ?c wdt:P298 ?iso . FILTER NOT EXISTS { ?c wdt:P576 ?end } '
            '{ ?c rdfs:label ?n FILTER(LANG(?n)="en") } UNION { ?c skos:altLabel ?n FILTER(LANG(?n)="en") } '
            'UNION { ?c wdt:P1549 ?n FILTER(LANG(?n)="en") } }')}}, open(npath, "w"))
    owner, cq = {}, defaultdict(set)
    for q, iso in country_items(): cq[iso].add(q)
    for iso, ids in lists.items():
        for e in ids: owner.setdefault(e, iso)
    names = defaultdict(set)
    for b in json.load(open(npath))["results"]["bindings"]:
        n = b["n"]["value"]
        if len(n) >= 4 or n in ("Iran", "Iraq", "Oman", "Chad", "Mali", "Peru", "Cuba", "Fiji", "Togo", "Laos", "Niue", "USA", "UAE"):
            names[b["iso"]["value"]].add(n.lower())
    def has(l, ns): return any(re.search(r"(?<![a-z])" + re.escape(n) + r"(?![a-z])", l) for n in ns)
    lab, jur = {}, defaultdict(set)
    for b in json.load(open(path))["results"]["bindings"]:
        e = b["e"]["value"].rsplit("/", 1)[1]; lab[e] = b["l"]["value"]
        if "j" in b: jur[e].add(b["j"]["value"].rsplit("/", 1)[1])
    keep = defaultdict(set)
    for e, l in lab.items():
        iso = owner.get(e); ll = l.lower()
        if not iso: continue
        if jur[e] and not (jur[e] & cq[iso]): continue
        if BAD_WORDS.search(l) or re.search(r"council|borough|\bward\b", ll): continue
        if not has(ll, names[iso]) and not (jur[e] & cq[iso]): continue
        m = re.search(r"\belections? in (.*)", ll)
        if m:  # "... election in X": X must be the country itself, not a region or constituency ("in Île-de-France")
            rest = re.sub(r"\b(the|of|\d{4}(–\d{2,4})?)\b|[,()]", " ", m.group(1)).strip()
            rest = " ".join(rest.split())
            if rest and rest not in names[iso]: continue
        keep[iso].add(e)
    return keep

def main():
    pg = parlgov()
    us = medsl()
    lists, all_cls = wd_lists()
    lists = national_items(lists)
    pres = subclasses(PRESIDENT_ROOT)
    excl = set().union(*[subclasses(r) for r in EXCLUDE_ROOTS if r != GROUP_ROOT])
    excl = (excl, subclasses(GROUP_ROOT))
    all_ids = set().union(*lists.values())
    ents = wd_entities(all_ids, "elections")
    # rounds: parts (P527) of elections that are themselves elections
    parts = {p for e in ents.values() if e for p in [qid(s["v"]) for s in e["claims"].get("P527", [])] if p}
    ents.update({k: v for k, v in wd_entities(parts, "rounds").items()})
    # parts of a national election that are elections in their own right (not rounds) are national items too, even when
    # their label does not name the country ("elections to the Congress of Deputies in 2023" is part of
    # "2023 Spanish general election"); wd_election still filters them (Senate, regional, ...).
    for iso in list(lists):
        for eid in list(lists[iso]):
            for s in (ents.get(eid) or {}).get("claims", {}).get("P527", []):
                p = ents.get(qid(s["v"]))
                if p and not ROUND.search(p.get("label") or "") and any(qid(x["v"]) in all_cls for x in p["claims"].get("P31", [])):
                    lists[iso].add(p["id"])
    # referenced candidates/parties
    refs = set()
    for e in ents.values():
        if not e: continue
        for p in ("P726", "P991"):
            for s in e["claims"].get(p, []):
                if qid(s["v"]): refs.add(qid(s["v"]))
                for x in s["q"].get("P210", []):
                    if qid(x): refs.add(qid(x))
    people = wd_entities(refs, "refs")
    more = set()
    for e in people.values():
        if e:
            for s in e["claims"].get("P102", []):
                if qid(s["v"]): more.add(qid(s["v"]))
    people.update(wd_entities(more - set(people), "refs2"))
    fill_labels(people)
    wd_election, family, people = build(pg, us, lists, ents, people, excl, pres)
    result, skipped = assemble(pg, us, lists, wd_election, family, people)
    write(result, skipped)

# ------------------------------------------------------------------ build
LEFT_WORDS = [("far-left", "left"), ("far left", "left"), ("radical left", "left"), ("centre-left", "centre-left"),
              ("center-left", "centre-left"), ("centre-right", "centre-right"), ("center-right", "centre-right"),
              ("far-right", "right"), ("far right", "right"), ("radical right", "right"), ("left-wing", "left"),
              ("right-wing", "right"), ("big tent", "centre"), ("syncretic", "centre"), ("syncretism", "centre"),
              ("radical centre", "centre"), ("centrism", "centre"), ("centre", "centre"), ("center", "centre")]

def align_family(label):
    """Map a political-alignment label to a family. For a span ("centre-right to right-wing") the first term wins."""
    if not label: return None
    l = label.lower()
    hits = sorted((l.find(w), -len(w), f) for w, f in LEFT_WORDS if w in l)  # at one position the longer term wins
    return hits[0][2] if hits else None

GREEN = re.compile(r"\bgreen politics\b|\bgreen\b|ecolog|environmental", re.I)
REGIONAL = re.compile(r"regionalism|separatism|autonomism|independence|minority rights|nationalism \(", re.I)
LIBERAL = re.compile(r"liberalism", re.I)
# party without a political alignment (P1387): the first ideology (P1142) that names a family
IDEOLOGY = [(re.compile(r"national conservatism|(?<!civic )nationalism|right-wing populism|far-right", re.I), "right"),
            (re.compile(r"social democra|third way", re.I), "centre-left"),
            (re.compile(r"christian democra|conservatism", re.I), "centre-right"),
            (re.compile(r"communis|marxis|trotsky|socialism", re.I), "left")]

def build(pg, us, lists, ents, people, excl, pres):
    leg = subclasses("Q2618461") | subclasses("Q1076105")
    # labels of alignment/ideology items
    vals = set()
    for e in people.values():
        if not e: continue
        for p in ("P1387", "P1142"):
            vals.update(qid(s["v"]) for s in e["claims"].get(p, []) if qid(s["v"]))
    lab = wd_entities(vals, "labels"); fill_labels(lab)
    lab = {k: (v or {}).get("label") for k, v in lab.items()}
    countries = defaultdict(set)
    for q, iso in country_items(): countries[iso].add(q)

    def best(e, p):
        sts = (e or {}).get("claims", {}).get(p, [])
        pref = [s for s in sts if s["r"] == "preferred"]
        return pref or sts

    fam_cache = {}
    def family(pid):
        if pid in fam_cache: return fam_cache[pid]
        e = people.get(pid); f = None
        if e:
            al = [lab.get(qid(s["v"])) for s in best(e, "P1387")]
            ide = " | ".join(filter(None, (lab.get(qid(s["v"])) for s in e["claims"].get("P1142", []))))
            f = next((align_family(a) for a in al if align_family(a)), None)
            ides = [lab.get(qid(s["v"])) or "" for s in e["claims"].get("P1142", [])]
            # green: a green party (name, or green politics as its first ideology), not a left party that lists it
            if f in (None, "centre-left", "centre", "left") and (GREEN.search(ides[0] if ides else "") or
                                                                 re.search(r"\bgreens?\b|ecolog", e.get("label") or "", re.I)): f = "green"
            elif f is None and REGIONAL.search(ide): f = "regional"
            elif f in (None, "centre") and LIBERAL.search(ide) and not re.search(r"conservat|social democra", ide, re.I): f = "liberal" if f or ide else f
            if f is None: f = next((fam for i in ides for rx, fam in IDEOLOGY if rx.search(i)), None)
            if f is None and re.search(r"independent politician|independent", (e.get("label") or ""), re.I): f = "independent"
        fam_cache[pid] = f
        return f

    def is_human(e): return any(qid(s["v"]) == "Q5" for s in (e or {}).get("claims", {}).get("P31", []))
    def party_of(pid, date):
        e = people.get(pid)
        sts = [s for s in best(e, "P102") if qid(s["v"])]
        if not sts: return None
        def live(s):
            st = [x for x in s["q"].get("P580", []) if x]; en = [x for x in s["q"].get("P582", []) if x]
            ok = True
            if st and st[0].get("time", "")[1:11].replace("-", "") > str(date): ok = False
            if en and en[0].get("time", "")[1:11].replace("-", "") < str(date): ok = False
            return ok
        cand = [s for s in sts if live(s)] or sts
        return qid(cand[-1]["v"])
    def short(pid):
        e = people.get(pid)
        for s in (e or {}).get("claims", {}).get("P1813", []):
            v = s["v"]
            if isinstance(v, dict) and v.get("text") and len(v["text"]) <= 12 and v.get("language") in ("en", "mul", None): return v["text"]
        for s in (e or {}).get("claims", {}).get("P1813", []):
            v = s["v"]
            if isinstance(v, dict) and v.get("text") and len(v["text"]) <= 12: return v["text"]
        return None

    def date_of(e):
        sts = best(e, "P585")
        if not sts or not isinstance(sts[0]["v"], dict): return None
        v = sts[0]["v"]
        if v.get("precision", 0) < 11: return None
        m = re.match(r"\+(\d{4})-(\d\d)-(\d\d)", v["time"])
        return int(m.group(1) + m.group(2) + m.group(3)) if m else None

    def num(e, p, rnd=None):
        xs = []
        for s in best(e, p):
            a = amount(s["v"])
            if a is None: continue
            r = [x for x in s["q"].get("P1545", []) if x]
            xs.append((a, r[0] if r else None))
        if not xs: return None
        if rnd is not None and any(r == rnd for _, r in xs): return max(a for a, r in xs if r == rnd)
        return max(a for a, _ in xs)

    def results(e, date, kind):
        """[(entity, votes, seats, party)] from P726 + P991 of one election item, and the round used."""
        sts = best(e, "P726")
        rk = lambda x: (int(x) if str(x).isdigit() else 99, str(x))
        # P1545 (series ordinal) marks the round only when it repeats across candidates or one candidate has several;
        # a value unique to each candidate is the ballot/list number (e.g. 2025 Dutch election: PVV 1, GL-PvdA 2, ...)
        ords = [(qid(s["v"]), x) for s in sts for x in s["q"].get("P1545", []) if x]
        per_val = defaultdict(set); per_cand = defaultdict(set)
        for c, x in ords: per_val[x].add(c); per_cand[c].add(x)
        is_round = any(len(v) > 1 for v in per_val.values()) or any(len(v) > 1 for v in per_cand.values())
        if not is_round: sts = [dict(s, q={k: v for k, v in s["q"].items() if k != "P1545"}) for s in sts]
        rounds = sorted({x for s in sts for x in s["q"].get("P1545", []) if x}, key=rk)
        voted = [r for r in rounds if any(r in s["q"].get("P1545", []) and s["q"].get("P1111") for s in sts)] or rounds
        rnd = (voted[-1] if kind == "president" else voted[0]) if voted else None
        later = bool(rounds and rnd is not None and kind == "president" and rk(rounds[-1]) > rk(rnd))  # a round without votes yet
        rows = {}
        for s in sts:
            pid = qid(s["v"])
            if not pid: continue
            r = [x for x in s["q"].get("P1545", []) if x]
            if rnd is not None and r and r[0] != rnd: continue
            v = [amount(x) for x in s["q"].get("P1111", []) if amount(x) is not None]
            se = [amount(x) for x in s["q"].get("P1410", []) if amount(x) is not None]
            pa = [qid(x) for x in s["q"].get("P210", []) if qid(x)]
            old = rows.get(pid, {"votes": None, "seats": None, "party": None})
            if v and (old["votes"] is None or v[0] > old["votes"]): old["votes"] = v[0]
            if se and old["seats"] is None: old["seats"] = se[0]
            if pa and not old["party"]: old["party"] = pa[0]
            rows[pid] = old
        winners = []
        for s in best(e, "P991"):
            pid = qid(s["v"])
            if not pid: continue
            winners.append(pid)
            se = [amount(x) for x in s["q"].get("P1410", []) if amount(x) is not None]
            row = rows.setdefault(pid, {"votes": None, "seats": None, "party": None})
            if se and row["seats"] is None: row["seats"] = se[0]
        return rows, winners, rnd, later

    popular_pres = {iso for iso, ids in lists.items() if iso not in INDIRECT and any(
        {qid(s["v"]) for s in (ents.get(e) or {}).get("claims", {}).get("P31", [])} & pres for e in ids)}

    def wd_election(eid, iso):
        e = ents.get(eid)
        if not e: return None
        label = e.get("label") or ""
        cls = {qid(s["v"]) for s in e["claims"].get("P31", [])}
        if cls & excl[0] or (cls & excl[1] and not cls & (leg | pres)) or BAD_WORDS.search(label): return None
        # a round of another item (handled through the parent's P527); other parts, e.g. the legislative half of a
        # general election, are elections in their own right
        if ROUND.search(label) and any(qid(s["v"]) in ents for s in e["claims"].get("P361", [])): return None
        juris = {qid(s["v"]) for s in e["claims"].get("P1001", [])}
        if juris and not (juris & countries[iso]): return None
        kind = "president" if cls & pres else "parliament" if (cls & leg or re.search(
            r"parliament|legislative|general election|federal election|national assembly|national council|house of representatives|"
            r"chamber of deputies|congress|bundestag|duma|majlis|sejm|knesset|storting|riksdag|folketing|althing|national election", label, re.I)) else None
        if kind is None and re.search(r"presiden", label, re.I): kind = "president"
        if not kind: return None
        # a "general election" item whose candidates are all people (no seats) holds the presidential half
        # (e.g. "2025 Chilean general election" lists Kast and Jara) -- only in countries with a popularly elected
        # president (UK/Indian general election items list party leaders the same way)
        cands = [qid(s["v"]) for s in best(e, "P726") if qid(s["v"])]
        if (kind == "parliament" and iso in popular_pres and re.search(r"general election", label, re.I) and 0 < len(cands) <= 15
                and all(is_human(people.get(c)) for c in cands) and not any(s["q"].get("P1410") for s in best(e, "P726"))):
            kind = "president"
        if kind == "president" and iso in INDIRECT: return {"skip": "indirect"}
        if re.search(r"presiden", label, re.I) and kind == "parliament" and not re.search(r"general|and", label, re.I): kind = "president"
        date = date_of(e)
        if not date or date > int(TODAY.replace("-", "")): return None
        # rounds stored as separate items
        # rounds stored as separate items (P527 parts labelled "first round", "run-off", ...), in order: ordinal from the
        # label, else date; an undated round (not held yet) sorts last
        subs = [ents.get(qid(s["v"])) for s in e["claims"].get("P527", [])]
        subs = [s for s in subs if s and ROUND.search(s.get("label") or "")]
        def order(s):
            l = (s.get("label") or "").lower()
            n = 1 if re.search(r"first|1st", l) else 2 if re.search(r"second|2nd|run-?off", l) else 3 if re.search(r"third|3rd", l) else 9
            return (n, date_of(s) or 99999999)
        subs.sort(key=order)
        src, pending = e, False
        if subs:
            withres = [s for s in subs if any(s2["q"].get("P1111") for s2 in s["claims"].get("P726", []))]
            if withres:
                src = withres[-1] if kind == "president" else withres[0]
                # presidential: a later round exists with no results yet (run-off pending, or not recorded)
                pending = kind == "president" and any(order(s) > order(src) and s not in withres for s in subs)
        rows, winners, rnd, later = results(src, date, kind)
        if pending or later: winners = []  # P991 on a non-final round names the candidates who advanced
        pending = pending or later
        if not rows and src is not e: rows, winners, rnd, _ = results(e, date, kind)
        if src is not e: winners = results(e, date, kind)[1] or winners
        elig = num(src, "P1867", rnd) or num(e, "P1867"); cast = num(src, "P1868", rnd) or num(e, "P1868")
        valid = num(src, "P1697", rnd) or (num(e, "P1697") if src is e else None)
        turnout = round(100 * cast / elig, 1) if cast and elig and 0 < cast <= elig * 1.0001 else None
        if turnout is not None and turnout < 5: turnout = None
        votes = [r["votes"] for r in rows.values() if r["votes"]]
        tot = sum(votes)
        pct = bool(votes) and max(votes) <= 100 and 99 <= tot <= 101  # P1111 holding percentages (e.g. Chile 2025)
        if kind == "president" and not elig and votes and max(votes) < 20000 and not pct:
            return {"skip": "indirect"}
        # share denominator: valid votes; else the sum of listed votes, but only when the list is evidently complete
        # (presidential field, or the sum reaches 90% of ballots cast)
        if pct and (valid or cast or elig or kind == "president"): denom = 100.0
        elif valid and valid >= tot * 0.98: denom = valid
        elif len(votes) >= 2 and ((cast and tot >= 0.9 * cast) or (kind == "president" and not cast)): denom = tot
        else: denom = None
        parties = []
        for pid, r in rows.items():
            ent = people.get(pid) or {}; pid0 = pid
            name = "Independents" if pid == "Q327591" else ent.get("label")  # None (no usable label): folds into Others
            party = r["party"] or (party_of(pid, date) if is_human(ent) else None)
            fam = family(party) if (party and is_human(ent)) else family(pid)
            if is_human(ent) and not party: fam = fam or "independent"
            if kind == "parliament" and is_human(ent) and party:  # a leader standing for the party list
                pent = people.get(party) or {}
                name, ent, pid = pent.get("label") or name, pent, party
                if pid == "Q327591": name = "Independents"
            row = {"name": name, "abbr": None if is_human(ent) else short(pid),
                   "share": round(100 * r["votes"] / denom, 2) if r["votes"] and denom else None,
                   "seats": int(r["seats"]) if r["seats"] is not None else None, "family": fam, "qid": pid,
                   "partyName": (people.get(party) or {}).get("label") if (party and is_human(ent) and party != "Q327591") else None,
                   "wiki": ent.get("enwiki"), "human": is_human(ent)}
            if pid0 in winners: winners = [pid if w == pid0 else w for w in winners]  # a leader's win counts for the party
            parties.append(row)
        if sum(p["share"] or 0 for p in parties) > 101:
            for p in parties: p["share"] = None
        seats_total = num(e, "P1342")
        if not seats_total:
            for s in best(e, "P541"):
                q = [amount(x) for x in s["q"].get("P1114", []) if amount(x)]
                if q: seats_total = q[0]; break
        if kind == "president": seats_total = None
        return {"date": date, "type": kind, "turnout": turnout, "parties": parties, "winners": winners, "pending": pending,
                "seatsTotal": int(seats_total) if seats_total else None, "source": "wikidata", "qid": eid, "label": label}

    return wd_election, family, people

# Winners of major elections whose Wikidata items carry no results yet (checked 2026-10-14). Applied only while the
# built row has no winner, so better Wikidata data takes over automatically. Keep this list minimal.
OVERRIDES = {
    # 2025 Polish presidential election, run-off 1 June 2025: Nawrocki 50.89% (PKW figures)
    # https://en.wikipedia.org/wiki/2025_Polish_presidential_election
    ("POL", 20250518, "president"): {"winner": "Karol Nawrocki", "family": "right", "share": 50.9},
    # 2024 South African general election: ANC 40.18%, 159 of 400 seats (IEC figures)
    # https://en.wikipedia.org/wiki/2024_South_African_general_election
    ("ZAF", 20240529, "parliament"): {"winner": "African National Congress", "family": "centre-left", "share": 40.2},
    # 2024 French legislative election (two rounds, 30 June / 7 July): Wikidata has no seats, so the most-votes rule picked
    # the first-round leader. Most seats: New Popular Front 180 of 577 (Ministry of the Interior figures). `force`: replace.
    # https://en.wikipedia.org/wiki/2024_French_legislative_election
    ("FRA", 20240630, "parliament"): {"winner": "New Popular Front", "family": "left", "share": None, "force": True},
}

US_PARTY = {"DEMOCRAT": ("Q29552", "Democratic Party", "centre-left"), "REPUBLICAN": ("Q29468", "Republican Party", "right"),
            "LIBERTARIAN": ("Q558334", "Libertarian Party", "right")}

def us_name(n):
    if "," in n:
        last, first = n.split(",", 1); n = first.strip() + " " + last.strip()
    n = n.title()
    return re.sub(r"\bJr\b\.?", "Jr.", n).replace("Mcc", "McC").replace("Mcm", "McM").replace("Mcg", "McG")

def top_parties(parties, seats_total, kind):
    """Sort, keep top 8, fold the rest (and the unknown remainder) into Others. Drop internal fields."""
    has_share = any(p["share"] for p in parties)
    key = (lambda p: (-(p["share"] or 0), -(p["seats"] or 0))) if has_share else (lambda p: (-(p["seats"] or 0), p["name"] or ""))
    ps = sorted(parties, key=key)
    ps = [p for p in ps if (p["share"] or 0) > 0 or (p["seats"] or 0) > 0 or kind == "president"]
    named = [p for p in ps if p["name"]]  # rows without a usable label go to Others, never shown as a QID
    top, rest = named[:8], named[8:] + [p for p in ps if not p["name"]]
    out = []
    for p in top:
        r = {"name": p["name"]}
        if p.get("abbr"): r["abbr"] = p["abbr"]
        if p.get("partyName"): r["party"] = p["partyName"]
        r.update({"share": p["share"], "seats": p["seats"], "family": p["family"]})
        out.append(r)
    sh = [p["share"] for p in top if p["share"] is not None]
    if has_share:
        o = round(100 - sum(sh), 1)
        o_seats = None
        if seats_total and all(p["seats"] is not None for p in top):
            o_seats = max(0, seats_total - sum(p["seats"] for p in top))
        if o >= 0.1 or (o_seats or 0) > 0:
            out.append({"name": "Others", "share": max(o, 0.0), "seats": o_seats if kind == "parliament" else None, "family": None})
    elif rest and kind == "parliament":
        s = sum(p["seats"] or 0 for p in rest)
        if s: out.append({"name": "Others", "share": None, "seats": s, "family": None})
    for p in out:
        if p["share"] is not None: p["share"] = round(p["share"], 1)
    return out

def assemble(pg, us, lists, wd_election, family, people):
    countries = defaultdict(list); skipped = defaultdict(int)
    for iso, ids in lists.items():
        for eid in ids:
            r = wd_election(eid, iso)
            if r is None: skipped["filtered"] += 1; continue
            if "skip" in r: skipped[r["skip"]] += 1; continue
            countries[iso].append(r)
    result = {}
    for iso in sorted(set(countries) | set(pg)):
        wd = countries.get(iso, [])
        # same election listed twice (e.g. main item and a duplicate): keep the one with most data
        byk = {}
        for r in wd:
            k = (r["date"], r["type"])
            score = lambda x: (len([p for p in x["parties"] if p["share"] is not None or p["seats"] is not None]), x["turnout"] is not None,
                               len(set(x.get("winners") or [])) == 1, len(x["parties"]))
            if k not in byk or score(r) > score(byk[k]): byk[k] = r
        wd = list(byk.values())
        # a bare item (no results, no turnout) within a month of a same-type item that has data is a duplicate or a
        # sub-item of it (rounds of a two-round election stored separately, a "general election" umbrella, ...)
        def bare(x): return not x["parties"] and x["turnout"] is None
        near = lambda a, b: abs((datetime.date(a // 10000, a // 100 % 100, a % 100) - datetime.date(b // 10000, b // 100 % 100, b % 100)).days) <= 31
        alld = wd + [dict(e, type="parliament") for e in pg.get(iso, [])]
        wd = [r for r in wd if not (bare(r) and any(o is not r and o["type"] == r["type"] and not bare(o) and near(o["date"], r["date"]) for o in alld))]
        els = []
        pge = pg.get(iso, [])
        last_pg = max((e["date"] for e in pge), default=0)
        for e in pge:
            # ParlGov has no turnout for a few elections: borrow Wikidata's if the date matches
            if e["turnout"] is None:
                m = [w for w in wd if w["type"] == "parliament" and abs(w["date"] - e["date"]) <= 3 and w["turnout"]]
                if m: e["turnout"] = m[0]["turnout"]; e["turnoutSource"] = "wikidata"
            els.append(e)
        # ParlGov family for the same party (matched by English Wikipedia title) keeps families consistent over time
        pgfam = {urllib.parse.unquote(p["wiki"].rsplit("/", 1)[1]).replace("_", " "): p["family"]
                 for e in pge for p in e["parties"] if p.get("wiki") and p["family"]}
        for w in wd:
            if w["type"] == "parliament" and pge and w["date"] <= last_pg + 3: continue
            for p in w["parties"]:
                if p.get("wiki") in pgfam and not p.get("partyName"): p["family"] = pgfam[p["wiki"]]
            els.append(w)
        if iso == "USA":
            for w in els:
                y = w["date"] // 10000
                if w["type"] == "president" and y in us:
                    total, d, pt = us[y]; ps = []
                    for cand, v in d.items():
                        if cand == "OTHER": continue
                        q, pname, fam = US_PARTY.get(pt.get(cand), (None, None, None))
                        ps.append({"name": us_name(cand), "partyName": pname, "share": 100.0 * v / total, "seats": None,
                                   "family": (family(q) or fam) if q else "other"})
                    w["parties"] = ps; w["source"] = "medsl-president"
                    w["winners"] = []; w["usWinner"] = True
        def richness(e): return (len(e["parties"]) > 0) + (e["turnout"] is not None)
        els.sort(key=lambda e: (-e["date"], -richness(e), e["type"] != "president"))
        out = []
        for e in els:
            kind = e["type"]
            winner = None
            ps_all = e["parties"]
            if kind == "parliament":
                if any(p["seats"] for p in ps_all):
                    winner = max(ps_all, key=lambda p: (p["seats"] or 0, p["share"] or 0))
                elif any(p["share"] for p in ps_all):
                    winner = max(ps_all, key=lambda p: p["share"] or 0)
                elif len(set(e.get("winners") or [])) == 1:  # no figures, but a single recorded winner (P991)
                    # (a party: a person here is the president or prime minister chosen, not a party result)
                    winner = next((p for p in ps_all if p.get("qid") in e["winners"] and not p.get("human")), None)
                if winner and not winner["name"]: winner = None
            else:
                # President: the single successful candidate (P991) of the deciding round; without one, the leader
                # only if they won an outright majority of valid votes. A first-round leader with a run-off pending
                # (later round item/qualifier without results, or under 50% with no P991) is not a winner.
                wq = set(e.get("winners") or [])
                ws = [p for p in ps_all if p.get("qid") in wq] if len(wq) == 1 else []
                if e.get("usWinner"):
                    # the Electoral College decides: winners per MEDSL year
                    W = {1976: "Carter", 1980: "Reagan", 1984: "Reagan", 1988: "Bush", 1992: "Clinton", 1996: "Clinton", 2000: "Bush",
                         2004: "Bush", 2008: "Obama", 2012: "Obama", 2016: "Trump", 2020: "Biden", 2024: "Trump"}[e["date"] // 10000]
                    ws = [p for p in ps_all if W in p["name"] and p["share"] > 30]
                if ws: winner = ws[0]
                elif not e.get("pending") and any(p["share"] for p in ps_all):
                    lead = max(ps_all, key=lambda p: p["share"] or 0)
                    if lead["share"] > 50: winner = lead
                if winner and not winner["name"]: winner = None
            parties = top_parties(ps_all, e.get("seatsTotal"), kind)
            if not parties and e["turnout"] is None and e["source"] == "wikidata" and not winner:
                # bare item: date only
                pass
            row = {"date": e["date"], "type": kind, "turnout": e["turnout"], "parties": parties,
                   "seatsTotal": e.get("seatsTotal"), "source": e["source"]}
            if e.get("turnoutSource"): row["turnoutSource"] = e["turnoutSource"]
            if winner:
                wn = winner["name"]
                if kind == "president" and winner.get("partyName"): wn = "%s (%s)" % (winner["name"], winner["partyName"])
                row["_winner"] = {"winner": wn, "family": winner["family"], "share": round(winner["share"], 1) if winner["share"] is not None else None}
            ov = OVERRIDES.get((iso, e["date"], kind))
            if ov and (not winner or ov.get("force")): row["_winner"] = {k: ov[k] for k in ("winner", "family", "share")}
            if kind == "president" and e.get("pending") and not row.get("_winner"): row["decided"] = False  # run-off pending / not recorded
            if e.get("qid"): row["wikidata"] = e["qid"]
            out.append(row)
        if out: result[iso] = out
    return result, skipped

def write(result, skipped):
    note_c = ("National parliamentary (lower house) and direct presidential elections since 1945, newest first. "
              "parties: top 8 by vote share (or seats) plus Others; share = % of valid votes, seats = seats won. "
              "Parliament elections up to 2023 in ParlGov countries come from ParlGov; later ones and all others from Wikidata, "
              "whose party results are incomplete for many countries (parties may be [] or shares null). "
              "Presidential results are the deciding round where Wikidata stores rounds; decided:false marks a presidential "
              "election whose deciding round is pending or not recorded (shares are then the latest round on record). "
              "US presidential popular vote from MEDSL. "
              "Turnout = ballots cast / registered voters (ParlGov: votes_cast / electorate). "
              "family is Orbis' grouping of ParlGov party families or Wikidata political alignment (P1387).")
    for f in os.listdir(OUT):
        if re.fullmatch(r"[A-Z]{3}\.json", f): os.remove(os.path.join(OUT, f))
    world = {}
    sizes = []
    for iso, els in result.items():
        srcs = sorted({e["source"] for e in els} | ({"wikidata"} if any(e.get("turnoutSource") for e in els) else set()))
        clean = []
        for e in els:
            r = {k: v for k, v in e.items() if not k.startswith("_") and k != "wikidata"}
            clean.append(r)
        doc = {"source": srcs if len(srcs) > 1 else srcs[0], "asOf": ASOF, "retrieved": TODAY, "note": note_c, "elections": clean}
        s = json.dumps(doc, ensure_ascii=False, separators=(",", ":"))
        if len(s) > 60000:  # trim: drop parties of the oldest elections until it fits
            for e in reversed(clean):
                if len(s) <= 60000: break
                e["parties"] = e["parties"][:3]
                s = json.dumps(doc, ensure_ascii=False, separators=(",", ":"))
        open(os.path.join(OUT, iso + ".json"), "w").write(s)
        sizes.append((len(s), iso))
        # last = the newest election with a known winner (else the newest); latest = the newest on record when that
        # is a different, later election (results not in the sources yet, or a run-off pending)
        last = next((e for e in els if e.get("_winner")), els[0])
        w = last.get("_winner") or {}
        world[iso] = {"last": {"date": last["date"], "type": last["type"], "turnout": last["turnout"],
                               "winner": w.get("winner"), "family": w.get("family"), "share": w.get("share")},
                      "n": len(els)}
        if els[0]["date"] > last["date"]:
            world[iso]["latest"] = {"date": els[0]["date"], "type": els[0]["type"]}
    wsrc = sorted({s for els in result.values() for e in els for s in [e["source"]]} | {"wikidata"})
    doc = {"source": wsrc, "asOf": ASOF, "retrieved": TODAY,
           "note": ("Latest national parliamentary or direct presidential election per country (date up to the build date). "
                    "last = the newest election with a known winner; latest = a newer election whose results are not in the "
                    "sources yet (or whose run-off is pending). "
                    "winner = party with most seats (parliament; most votes if seats unknown) or elected candidate (president: the "
                    "recorded successful candidate, else an outright majority; never a first-round leader); "
                    "share = winner's % of valid votes (deciding round for presidents). null where the source has no figure. "
                    "Details per country in data/elections/<ISO3>.json; " + note_c.split(". ", 1)[1]),
           "countries": world}
    open(os.path.join(OUT, "world.json"), "w").write(json.dumps(doc, ensure_ascii=False, separators=(",", ":")))
    sizes.sort(reverse=True)
    print("countries:", len(world), "largest:", sizes[:3], "skipped:", dict(skipped), file=sys.stderr)


if __name__ == "__main__":
    main()
