"""UCDP Georeferenced Event Dataset (GED) aggregated to grid cells by month, for one country. CC BY 4.0.
Source: https://ucdp.uu.se/downloads/  (GED Global 26.1 covers 1989-2025; UCDP Candidate monthly releases extend it into 2026)
Fetch:
  mkdir -p .cache/ucdp && cd .cache/ucdp && \
  curl -sSfLO https://ucdp.uu.se/downloads/ged/ged261-csv.zip && unzip -o ged261-csv.zip -d ged && \
  curl -sSfLO https://ucdp.uu.se/downloads/candidateged/GEDEvent_v26_01_26_06.csv && \
  curl -sSfLO https://ucdp.uu.se/downloads/candidateged/GEDEvent_v26_0_7.csv && \
  curl -sSfLO https://ucdp.uu.se/downloads/candidateged/GEDEvent_v26_0_8.csv
Run:    python3 tools/build/events_conflict_ukraine.py   (or _syria, _sudan; all call build() below)
Output: data/events/conflict-<name>.json             v = number of UCDP events in the cell and month
        data/events/conflict-<name>-fatalities.json  v = sum of UCDP best-estimate deaths in the cell and month
        {source, asOf, retrieved, note, fields:[lon,lat,t,v], tUnit:"month", vLabel, vUnits, cell, events:[[lon, lat, yyyymm, v], ...]}
        lon/lat are cell centres. Cell is 0.25 deg unless the file would exceed MAX_BYTES, then 0.5 deg."""
import os, csv, json, math, datetime, collections
root = os.path.join(os.path.dirname(__file__), "..", "..")
CACHE = os.path.join(root, ".cache/ucdp")
OUTDIR = os.path.join(root, "data/events")
MAX_BYTES = 400 * 1024
GED = ("GED 26.1", "ged/GEDEvent_v26_1.csv")
# Candidate releases, oldest first; a later release replaces an event with the same id.
CANDIDATES = [("Candidate 26.01.26.06", "GEDEvent_v26_01_26_06.csv"),
              ("Candidate 26.0.7", "GEDEvent_v26_0_7.csv"),
              ("Candidate 26.0.8", "GEDEvent_v26_0_8.csv")]
TYPES = {"1": "state-based", "2": "non-state", "3": "one-sided"}


def read(path):
    with open(os.path.join(CACHE, path), newline="", encoding="utf-8") as fh:
        yield from csv.DictReader(fh)


def load(country, start):
    """Events for `country` with date_start month >= start (yyyymm). GED for <= 2025, candidates after."""
    ev = {}
    for label, path in [GED] + CANDIDATES:
        is_ged = label == GED[0]
        for r in read(path):
            if r["country"] != country:
                continue
            ym = int(r["date_start"][:4] + r["date_start"][5:7])
            if ym < start or (not is_ged and ym <= 202512):
                continue
            ev[r["id"]] = dict(r, ym=ym, release=label)
    return list(ev.values())


def grid(events, cell, value):
    agg = collections.defaultdict(float)
    for e in events:
        lon = (math.floor(float(e["longitude"]) / cell) + 0.5) * cell
        lat = (math.floor(float(e["latitude"]) / cell) + 0.5) * cell
        agg[(round(lon, 3), round(lat, 3), e["ym"])] += value(e)
    out = [[round(lon, 2), round(lat, 2), ym, int(v)] for (lon, lat, ym), v in agg.items() if v > 0]
    out.sort(key=lambda x: (x[2], -x[3]))
    return out


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def build(name, country, start, label):
    events = load(country, start)
    if not events:
        raise SystemExit("no events; check .cache/ucdp (see docstring)")
    nall = len(events)
    vague = [e for e in events if e["where_prec"] in ("6", "7")]  # only country known / international waters or airspace
    events = [e for e in events if e["where_prec"] not in ("6", "7")]
    last = max(e["ym"] for e in events)
    releases = collections.Counter(e["release"] for e in events)
    rel_txt = ", ".join(f"{k}: {v}" for k, v in releases.items())
    deaths = sum(int(e["best"] or 0) for e in events)
    by_type = collections.Counter(TYPES.get(e["type_of_violence"], "?") for e in events)
    cand = sum(v for k, v in releases.items() if k != GED[0])
    retrieved = datetime.date.fromtimestamp(os.path.getmtime(os.path.join(CACHE, CANDIDATES[-1][1]))).isoformat()
    s, l = f"{start // 100}-{start % 100:02d}", f"{last // 100}-{last % 100:02d}"

    common = (f"UCDP Georeferenced Event Dataset: events of organised violence (state-based conflict, non-state conflict and "
              f"one-sided violence against civilians) that caused at least one death, in {country}, {s} to {l}. "
              f"Sources: UCDP GED Global 26.1 (to December 2025) plus UCDP Candidate monthly releases for 2026 "
              f"(26.01.26.06, 26.0.7, 26.0.8; last month covered {l}). Candidate events are preliminary and may be "
              f"revised or removed in the next GED release, and are less complete than the annual GED. "
              f"{len(events)} events ({rel_txt}; {', '.join(f'{k} {v}' for k, v in by_type.most_common())}), "
              f"best-estimate deaths {deaths:,}. Events are placed at their coded location (often a town or a province "
              f"centroid when the exact place is unknown); {len(vague)} of {nall} events coded only to country level or to "
              f"international waters/airspace are left out. Only events UCDP codes to country '{country}' are included. "
              f"Month is the event's start date. Cells are grid squares; lon/lat give the cell centre.")

    for suffix, value, vlabel, vunits, extra in [
        ("", lambda e: 1, "Events", "UCDP events per cell and month", ""),
        ("-fatalities", lambda e: int(e["best"] or 0), "Deaths (best estimate)", "UCDP best-estimate deaths per cell and month",
         " Values are UCDP's best estimate of deaths (combatants and civilians), which is uncertain; UCDP also gives low and high estimates."),
    ]:
        for cell in (0.25, 0.5, 1.0):
            rows = grid(events, cell, value)
            out = {"source": "ucdp-ged", "asOf": f"UCDP GED 26.1 + Candidate 26.0.8 (to {l})", "retrieved": retrieved,
                   "note": f"{label}. " + common + f" Cell size {cell} deg." + extra,
                   "fields": ["lon", "lat", "t", "v"], "tUnit": "month", "vLabel": vlabel, "vUnits": vunits,
                   "cell": cell, "events": rows}
            txt = dump(out)
            if len(txt.encode()) <= MAX_BYTES:
                break
        path = os.path.join(OUTDIR, f"{name}{suffix}.json")
        os.makedirs(OUTDIR, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(txt)
        print(f"{os.path.relpath(path, root)}: {len(rows)} cell-months, cell {cell} deg, {len(txt.encode())/1024:.0f} KB")

    print(f"{nall} events read, {len(vague)} dropped as country-level/vague, last month {l}; {rel_txt}; deaths {deaths:,}")
    yr = collections.Counter(e["ym"] // 100 for e in events)
    yd = collections.Counter()
    for e in events:
        yd[e["ym"] // 100] += int(e["best"] or 0)
    print("per year (events / deaths):", ", ".join(f"{y} {yr[y]}/{yd[y]}" for y in sorted(yr)))
    cells, adm = collections.Counter(), collections.defaultdict(collections.Counter)
    for e in events:
        k = (math.floor(float(e["longitude"]) / 0.5) * 0.5 + 0.25, math.floor(float(e["latitude"]) / 0.5) * 0.5 + 0.25)
        cells[k] += 1
        adm[k][e["adm_1"]] += 1
    print("top 0.5-deg cells (all months):")
    for k, n in cells.most_common(8):
        print(f"  {k[0]:7.2f} {k[1]:6.2f}  {n:6}  {adm[k].most_common(1)[0][0]}")
