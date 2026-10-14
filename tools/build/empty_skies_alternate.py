# Merge preservation: origin/main tools/build/empty_skies.py; standalone alternate-data builder.
# Writes only the original remote dataset paths documented below; no story JSON is written.
# Finite-roadmap data are generated separately by empty_skies.py and remain in distinct paths.
"""The sky went quiet, 2020: monthly flights per country from the OpenSky Network COVID-19 flight list.
Source: Zenodo record 5815448 (version v21.12, "Crowdsourced air traffic data from The OpenSky Network 2020 [CC-BY]",
  Olive, Strohmeier, Lübbe), licence CC BY 4.0 (checked via the Zenodo API: metadata.rights = cc-by-4.0).
  A later continuation of the dataset uses different (non-commercial) terms and is NOT used.
Airport -> country: OurAirports airports.csv (public domain, https://ourairports.com/data/).
ISO2 -> ISO3: World Bank country list (.cache/wb/countries.json, see sci.py) plus a few manual codes.
Run: python3 tools/build/empty_skies_alternate.py
  Downloads each month (~70-260 MB) into .cache/empty-skies/, aggregates it into agg-<yyyymm>.json, then deletes the raw file.
  To download several months in parallel, fetch them yourself (curl -C - into .cache/empty-skies/) and run with PREFETCH=1:
  the script then waits for each file to reach its full size instead of downloading it.
Output:
  data/statistics/flights.json        series keyed by yyyymm ("format": "month"): departures per country and change vs 2019
  data/statistics/flights-flows.json  groups: international country-to-country flights for selected months
  data/statistics/flights-totals.json all flights, international, domestic and five airlines vs 2019 (line charts)
Counting: one row = one flight seen by OpenSky's receivers. A departure counts for the country of its origin airport;
flights with no detected origin airport are left out of the country counts (but kept in the 'seen' total).
Coverage is uneven: ADS-B receivers are volunteer-run and dense in Europe and North America, sparse over Africa,
much of Asia and the oceans, so counts are relative within a country, not comparable between countries."""
import os, sys, csv, gzip, json, re, time, datetime, subprocess, collections

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CACHE = os.path.join(root, ".cache/empty-skies")
REC = "5815448"
# every month of 2019 (the baseline) and 2020, then two months of 2021 to show the recovery (Zenodo downloads are slow)
MONTHS = [y * 100 + m for y in (2019, 2020) for m in range(1, 13)] + [202104, 202108]
LAST = {2: 28, 4: 30, 6: 30, 9: 30, 11: 30}
FLOW_MONTHS = [201904, 202004, 202104, 201908, 202008, 202108]
TODAY = datetime.date.today().isoformat()
OPERATORS = {"UPS": "UPS Airlines", "FDX": "FedEx Express", "RYR": "Ryanair", "DLH": "Lufthansa", "SWA": "Southwest Airlines"}
UA = "Orbis-data-build/1.0"


def fname(ym):
    y, m = divmod(ym, 100)
    last = 29 if (m == 2 and y == 2020) else LAST.get(m, 31)
    if ym == 202105:
        last = 30  # the record names this file ..._20210530
    return f"flightlist_{y}{m:02d}01_{y}{m:02d}{last:02d}.csv.gz"


def files_in_record():
    p = os.path.join(CACHE, "record.json")
    if not os.path.exists(p):
        subprocess.run(["curl", "-sS", "-f", "-A", UA, "-H", "Accept: application/vnd.inveniordm.v1+json",
                        "-o", p, f"https://zenodo.org/api/records/{REC}"], check=True)
    rec = json.load(open(p))
    assert [r["id"] for r in rec["metadata"]["rights"]] == ["cc-by-4.0"], "licence changed"
    return {k: v["size"] for k, v in rec["files"]["entries"].items()}


def iso_maps():
    wb = json.load(open(os.path.join(root, ".cache/wb/countries.json")))[1]
    iso3 = {c["iso2Code"]: c["id"] for c in wb}
    iso3.update({"XK": "XKX", "TW": "TWN", "GP": "FRA", "MQ": "FRA", "RE": "FRA", "GF": "FRA", "YT": "FRA",
                 "PM": "SPM", "BL": "BLM", "MF": "MAF", "SX": "SXM", "CW": "CUW", "AI": "AIA", "MS": "MSR",
                 "VG": "VGB", "TC": "TCA", "CK": "COK", "NU": "NIU", "WF": "WLF", "FK": "FLK", "SH": "SHN",
                 "NF": "NFK", "PS": "PSE", "EH": "ESH", "AX": "ALA", "GG": "GGY", "JE": "JEY", "IM": "IMN",
                 "BQ": "NLD", "IO": "IOT", "CX": "AUS", "CC": "AUS", "AQ": "ATA", "SJ": "NOR", "UM": "USA"})
    ap, kw, pre = {}, {}, collections.defaultdict(collections.Counter)
    with open(os.path.join(CACHE, "airports.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            c = iso3.get(r["iso_country"])
            if not c:
                continue
            for k in (r["ident"], r["gps_code"], r["icao_code"]):
                if k and len(k) == 4 and k not in ap:
                    ap[k] = c
            if re.fullmatch("[A-Z]{4}", r["icao_code"]):
                pre[r["icao_code"][:2]][c] += 1
            for k in re.findall(r"\b[A-Z]{4}\b", r["keywords"]):  # old codes of closed airports, e.g. Berlin Tegel EDDT
                kw.setdefault(k, c)
    # fallback for origins OurAirports no longer lists under their code: old code in keywords, else the ICAO prefix
    # (when >= 95% of airports with that prefix are in one country)
    fb = dict(kw)
    for p_, cnt in pre.items():
        (c, n), = cnt.most_common(1)
        if n / sum(cnt.values()) >= 0.95:
            fb.setdefault(p_, c)
    return ap, fb


def aggregate(ym, ap, sizes):
    out = os.path.join(CACHE, f"agg-{ym}.json")
    if os.path.exists(out):
        return json.load(open(out))
    fn = fname(ym)
    raw = os.path.join(CACHE, fn)
    if os.environ.get("PREFETCH"):  # another process is downloading (see the docstring): wait for the full file
        while not os.path.exists(raw) or os.path.getsize(raw) != sizes[fn]:
            time.sleep(10)
    if not os.path.exists(raw) or os.path.getsize(raw) != sizes[fn]:
        print("download", fn, flush=True)
        subprocess.run(["curl", "-sS", "-f", "-A", UA, "-L", "-C", "-", "-o", raw,
                        f"https://zenodo.org/records/{REC}/files/{fn}?download=1"], check=True)
        assert os.path.getsize(raw) == sizes[fn], "incomplete download " + fn
    dep, arr, dom = collections.Counter(), collections.Counter(), collections.Counter()
    pairs, ops, ops_cargo = collections.Counter(), collections.Counter(), collections.Counter()
    seen = with_origin = 0
    unknown = collections.Counter()
    cs_re = re.compile(r"^([A-Z]{3})\d")
    with gzip.open(raw, "rt", newline="") as f:
        rd = csv.reader(f)
        h = next(rd)
        io, idd, ic = h.index("origin"), h.index("destination"), h.index("callsign")
        for r in rd:
            seen += 1
            o, d = r[io], r[idd]
            co = ap.get(o) if o else None
            cd = ap.get(d) if d else None
            if o and not co:
                unknown[o] += 1
            m = cs_re.match(r[ic])
            if m:
                ops[m.group(1)] += 1
            if co:
                with_origin += 1
                dep[co] += 1
            if cd:
                arr[cd] += 1
            if co and cd:
                if co == cd:
                    dom[co] += 1
                else:
                    pairs[co + ">" + cd] += 1
    agg = {"seen": seen, "with_origin": with_origin, "dep": dep, "arr": arr, "dom": dom,
           "pairs": dict(pairs.most_common(3000)), "ops": dict(ops.most_common(400)),
           "unknown_top": dict(unknown.most_common(20))}
    json.dump(agg, open(out, "w"))
    os.remove(raw)
    print(ym, "seen", seen, "with origin", with_origin, flush=True)
    return json.loads(json.dumps(agg))


def main():
    sizes = files_in_record()
    ap, fb = iso_maps()
    A = {ym: aggregate(ym, ap, sizes) for ym in MONTHS}
    # departures from airports missing from the main lookup (e.g. Berlin Tegel, closed 2020): the aggregates keep the
    # 20 most frequent unknown origins per month; add them back to departures where the fallback finds a country
    for ym in MONTHS:
        for code, n in A[ym]["unknown_top"].items():
            c = fb.get(code) or fb.get(code[:2])
            if c:
                A[ym]["dep"][c] = A[ym]["dep"].get(c, 0) + n
    # ---- series: departures per country per month, and change vs the same month of 2019
    countries = sorted({c for a in A.values() for c in a["dep"]})
    dep = {}
    chg = {}
    for c in countries:
        v = [A[ym]["dep"].get(c, 0) for ym in MONTHS]
        if max(v) < 30:   # too few flights seen to say anything
            continue
        dep[c] = v
        base = (v[MONTHS.index(202001)] + v[MONTHS.index(202002)]) / 2
        if base >= 100:  # enough flights before the pandemic for a % change
            chg[c] = [round((x / base - 1) * 100, 1) for x in v]
    intl = {c: [sum(n for k, n in A[ym]["pairs"].items() if k.startswith(c + ">")) for ym in MONTHS] for c in dep}
    world_dep = [sum(A[ym]["dep"].values()) for ym in MONTHS]
    world_seen = [A[ym]["seen"] for ym in MONTHS]
    world_intl = [sum(A[ym]["pairs"].values()) for ym in MONTHS]
    note = ("OpenSky Network COVID-19 flight list (Zenodo 5815448, v21.12, CC BY 4.0): every flight seen by OpenSky's "
            "volunteer ADS-B receivers. A departure counts for the country of the origin airport detected by OpenSky "
            "(airports matched to countries with OurAirports); flights with no detected origin are left out. "
            "Receiver coverage is dense in Europe and North America and thin over Africa, much of Asia and the oceans, and it "
            "grew over 2019–2021 (flights seen in Jan 2020 were 28% above Jan 2019): compare a country with itself over short "
            "spans, not countries with each other. dep_chg = % change against the average of January and February 2020 "
            "(countries with at least 100 departures a month then); it ignores seasons. Origins missing from OurAirports "
            "(e.g. Berlin Tegel) are added back from each month's 20 most frequent unknown codes. "
            "intl = departures to a detected airport in another country (top 3,000 country pairs per month). "
            "Built by tools/build/empty_skies_alternate.py.")
    ds = {"source": "opensky-covid", "asOf": "2021-12", "retrieved": TODAY, "format": "month", "years": MONTHS,
          "note": note,
          "series": {
              "dep": {"label": "Flights departing (seen by OpenSky)", "units": "flights", "values": dep},
              "dep_chg": {"label": "Departures vs Jan–Feb 2020", "units": "%", "values": chg},
              "intl": {"label": "International departures (seen by OpenSky)", "units": "flights", "values": intl},
          },
          "world": {"dep": world_dep, "seen": world_seen, "intl": world_intl}}
    os.makedirs(os.path.join(root, "data/statistics"), exist_ok=True)
    json.dump(ds, open(os.path.join(root, "data/statistics/flights.json"), "w"), separators=(",", ":"))
    # ---- groups: international flows for selected months
    fl, ex, im = {}, {}, {}
    for ym in FLOW_MONTHS:
        rows = sorted(((k.split(">")[0], k.split(">")[1], n) for k, n in A[ym]["pairs"].items()), key=lambda r: -r[2])
        fl[str(ym)] = [[a, b, n, None] for a, b, n in rows[:400]]
        e, i = collections.Counter(), collections.Counter()
        for a, b, n in rows:
            e[a] += n; i[b] += n
        ex[str(ym)] = dict(e.most_common()); im[str(ym)] = dict(i.most_common())
    gs = {"source": "opensky-covid", "asOf": "2021-12", "retrieved": TODAY, "years": FLOW_MONTHS, "format": "month",
          "units": {"value": "flights"},
          "note": "International flights seen by OpenSky between airports in two different countries, per month "
                  "(top 400 country pairs per month). Same coverage caveats as flights.json. Built by tools/build/empty_skies_alternate.py.",
          "groups": {"intl": {"label": "International flights", "flows": fl, "exports": ex, "imports": im}}}
    json.dump(gs, open(os.path.join(root, "data/statistics/flights-flows.json"), "w"), separators=(",", ":"))
    # ---- totals and a few airlines, % change vs the same month of 2019 (for line charts; keys are not countries)
    def vs2019(v):  # name kept short: % change against the Jan-Feb 2020 average (same receiver network, pre-pandemic)
        b = (v[MONTHS.index(202001)] + v[MONTHS.index(202002)]) / 2
        return [round((x / b - 1) * 100, 1) for x in v]
    tot = {"ALL": world_seen, "INTL": world_intl, "DOM": [sum(A[ym]["dom"].values()) for ym in MONTHS]}
    for op in OPERATORS:
        tot[op] = [A[ym]["ops"].get(op, 0) for ym in MONTHS]
    os_ = {"source": "opensky-covid", "asOf": "2021-12", "retrieved": TODAY, "format": "month", "years": MONTHS,
           "note": "Flights seen by OpenSky, % change against the average of January and February 2020 (before the pandemic hit air travel; comparing with 2019 would mix in the growth of the receiver network, +30% from Jan 2019 to Jan 2020). ALL = every flight seen; INTL = flights "
                   "between detected airports in two countries; DOM = within one country. Airlines by the ICAO prefix of the "
                   "callsign: " + ", ".join(f"{k} {v}" for k, v in OPERATORS.items()) + ". Not countries: for line charts only. "
                   "Built by tools/build/empty_skies_alternate.py.",
           "series": {"chg": {"label": "Flights vs Jan–Feb 2020", "units": "%", "values": {k: vs2019(v) for k, v in tot.items()}},
                      "n": {"label": "Flights seen", "units": "flights", "values": tot}}}
    json.dump(os_, open(os.path.join(root, "data/statistics/flights-totals.json"), "w"), separators=(",", ":"))
    for p in ("data/statistics/flights.json", "data/statistics/flights-flows.json", "data/statistics/flights-totals.json"):
        print(p, os.path.getsize(os.path.join(root, p)))


if __name__ == "__main__":
    main()
