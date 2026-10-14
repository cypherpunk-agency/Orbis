#!/usr/bin/env python3
"""Country panel data for Explore -> data/countries.json.

For every country: a few headline facts (latest value, year and rank, from data/atlas/) and the stories
that feature it. A story features a country when one of its scenes outlines or colours it (highlight,
fills) or names it in the scene title or text. Stories are ranked by how strongly they feature it.

No downloads: it reads only files already in the repo, so it inherits their licences (atlas: CC BY 4.0,
World Bank; story text: Orbis). Re-run after adding or editing stories or rebuilding the atlas.
Run: python3 tools/build/countries.py
"""
import json, os, re
from collections import defaultdict

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
P = lambda *a: os.path.join(ROOT, *a)

# headline facts, in display order (atlas indicator codes)
FACTS = ["SP.POP.TOTL", "NY.GDP.PCAP.PP.CD", "SP.DYN.LE00.IN", "EN.GHG.CO2.PC.CE.AR5"]
RECENT = 5  # a value counts as current when it is within this many years of the dataset's last year

# extra names used in story prose; the map's own names are always matched too
ALIASES = {
 "USA": ["United States", "America", "the US", "U.S."], "GBR": ["United Kingdom", "Britain", "the UK"],
 "RUS": ["Russia", "Soviet Union", "USSR"], "TUR": ["Turkey", "Türkiye", "Anatolia"], "KOR": ["South Korea"],
 "PRK": ["North Korea"], "CHN": ["China"], "IRN": ["Iran"], "SYR": ["Syria"], "COD": ["DR Congo", "Democratic Republic of the Congo"],
 "COG": ["Republic of the Congo"], "CIV": ["Côte d'Ivoire", "Ivory Coast"], "CZE": ["Czechia", "Czech Republic"],
 "NLD": ["Netherlands", "Holland"], "ARE": ["United Arab Emirates", "UAE"], "SAU": ["Saudi Arabia"], "VNM": ["Vietnam", "Viet Nam"],
 "LAO": ["Laos"], "BOL": ["Bolivia"], "VEN": ["Venezuela"], "TZA": ["Tanzania"], "MMR": ["Myanmar", "Burma"],
 "SWZ": ["Eswatini", "Swaziland"], "MKD": ["North Macedonia"], "BIH": ["Bosnia"], "TWN": ["Taiwan"], "PSE": ["Palestine", "Gaza", "West Bank"],
}
# names that are words or parts of other names; only matched via an alias
SKIP_NAMES = {"Georgia", "Jordan", "Chad", "Niger", "Guinea", "Congo", "Dominica"}


def main():
    world = json.load(open(P("data/world50.json")))
    names = {g["id"]: g["properties"]["name"] for g in world["objects"]["countries"]["geometries"] if g.get("id")}
    pats = {}
    for iso, n in names.items():
        terms = [] if n in SKIP_NAMES else [n]
        terms += ALIASES.get(iso, [])
        if terms:
            pats[iso] = re.compile(r"(?<![\w-])(" + "|".join(re.escape(t) for t in sorted(set(terms), key=len, reverse=True)) + r")(?![\w-])")
    # ambiguous names: "Guinea" also ends other country names; "Georgia" is also a US state, so it is only matched by map use
    pats["NER"] = re.compile(r"(?<![\w-])Niger(?![\w-])")
    pats["GIN"] = re.compile(r"(?<!New )(?<!Equatorial )(?<![\w-])Guinea(?!-Bissau)(?![\w-])")
    pats["JOR"] = re.compile(r"(?<![\w-])Jordan(?! River)(?![\w-])"); pats["TCD"] = re.compile(r"(?<![\w-])Chad(?![\w-])")

    stories = defaultdict(list)  # iso -> [[story id, best scene index, score]]
    for entry in json.load(open(P("stories/index.json"))):
        try:
            st = json.load(open(P(entry["file"])))
        except (OSError, ValueError):
            continue
        score, best = defaultdict(int), {}
        for i, sc in enumerate(st.get("scenes") or []):
            hit = defaultdict(int)
            for iso in sc.get("highlight") or []:
                hit[iso] += 3
            for iso in (sc.get("fills") or {}):
                hit[iso] += 2
            title, text = sc.get("title") or "", sc.get("text") or ""
            for iso, rx in pats.items():
                if rx.search(title): hit[iso] += 3
                if rx.search(text): hit[iso] += 1
            for iso, s in hit.items():
                if iso not in names: continue
                score[iso] += s
                if s > best.get(iso, (0, 0))[0]: best[iso] = (s, i)
        for iso, s in score.items():
            stories[iso].append([entry["id"], best[iso][1], s])

    facts = defaultdict(list)  # iso -> [[indicator, value, year, rank, of]]
    for code in FACTS:
        d = json.load(open(P("data/atlas", code + ".json")))
        ys, vals = d["years"], d["series"]["v"]["values"]
        def latest(a):
            for j in range(len(a) - 1, max(-1, len(a) - 1 - RECENT), -1):
                if a[j] is not None: return a[j], ys[j]
            return None
        cur = {iso: v for iso, a in vals.items() if (v := latest(a))}
        order = sorted((v[0] for v in cur.values()), reverse=True)
        for iso, (v, y) in cur.items():
            facts[iso].append([code, v, y, order.index(v) + 1, len(order)])

    out = {}
    for iso in sorted(set(stories) | set(facts)):
        s = sorted(stories.get(iso, []), key=lambda r: (-r[2], r[0]))
        out[iso] = {"f": facts.get(iso, []), "s": [[sid, i] for sid, i, _ in s]}
    meta = {"facts": FACTS, "note": "Built by tools/build/countries.py from data/atlas and stories; see that file."}
    with open(P("data/countries.json"), "w") as fh:
        json.dump({"meta": meta, "countries": out}, fh, ensure_ascii=False, separators=(",", ":"))
    n = sum(len(v["s"]) for v in out.values())
    print(f"{len(out)} countries, {n} story links, {os.path.getsize(P('data/countries.json')) // 1024} KB")


if __name__ == "__main__":
    main()
