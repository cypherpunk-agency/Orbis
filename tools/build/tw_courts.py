"""Legal basis of the country-wide US tariffs on each economy, before and after the Supreme Court's IEEPA ruling.
Hand-compiled from the Federal Register (cited below); no download needed.
Run: python3 tools/build/tw_courts.py
Output: data/tradewar/legal.json  (sets "before" and "after" for a categories layer; both use the keys a-e so one
legend colour map serves both)."""
import os, json, datetime
root = os.path.join(os.path.dirname(__file__), "..", "..")
geo = json.load(open(os.path.join(root, "data/world50.json")))
ALL = sorted(g["id"] for g in geo["objects"]["countries"]["geometries"])
SKIP = {"USA", "PRI", "GUM", "ASM", "MNP", "VIR", "ATA", "ATC", "ATF", "HMD", "SGS", "IOT", "IOA",
        "ESH", "KAS", "NCY", "SOL", "PCN",
        # dependent territories: tariff treatment differs from the sovereign and is not shown
        "GRL", "FRO", "NCL", "PYF", "ABW", "CUW", "SXM", "MAF", "BLM", "SPM", "AIA", "BMU", "CYM", "VGB", "TCA", "MSR",
        "FLK", "SHN", "WLF", "COK", "NIU", "NFK", "GGY", "JEY", "IMN", "ALA"}
EU = ["AUT", "BEL", "BGR", "HRV", "CYP", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HUN", "IRL", "ITA", "LVA",
      "LTU", "LUX", "MLT", "NLD", "POL", "PRT", "ROU", "SVK", "SVN", "ESP", "SWE"]

# --- Before: 19 February 2026, the day before Learning Resources v. Trump ---
# Reciprocal tariff, EO 14257 (90 FR 15041) as amended: all trading partners except Canada and Mexico; Russia, Belarus,
# Cuba and North Korea were not listed. Canada/Mexico: EO 14193 / 14194 (USMCA goods exempt). China: EO 14195 + 14257 on top of
# Section 301 (2018). Brazil: EO 14323 (40%) on top of the reciprocal 10%.
before = {}
for c in ALL:
    if c in SKIP: continue
    before[c] = "a"
before.update({"CAN": "b", "MEX": "b", "CHN": "c", "HKG": "c", "MAC": "c", "BRA": "e",
               "RUS": "d", "BLR": "d", "CUB": "d", "PRK": "d"})

# --- After: 13 October 2026 ---
# USTR, Notice of Actions in Section 301 Investigations ... Forced Labor, 91 FR 47318 (FR Doc. 2026-15181, 28 July 2026),
# effective 24 July 2026: 10% or 12.5% on all products of 60 economies (EU counted once), Section 232 goods exempt.
R10 = ["ARG", "BGD", "KHM", "CAN", "ECU", "SLV", "GTM", "HND", "IND", "IDN", "JOR", "MYS", "MEX", "PAK", "LKA", "TWN",
       "TTO", "GBR"] + EU  # EU and Taiwan: 10% net of MFN
R125 = ["DZA", "AGO", "AUS", "BHS", "BHR", "BRA", "CHL", "CHN", "COL", "CRI", "DOM", "EGY", "GUY", "HKG", "IRQ", "ISR",
        "JPN", "KAZ", "KWT", "LBY", "MAR", "NZL", "NIC", "NGA", "NOR", "OMN", "PER", "PHL", "QAT", "RUS", "SAU", "SGP",
        "ZAF", "KOR", "CHE", "THA", "TUR", "ARE", "URY", "VEN", "VNM"]  # Japan, South Korea, Switzerland: 12.5% net of MFN
assert len(R10) - len(EU) + 1 + len(R125) == 60, (len(R10), len(R125))
after = {}
for c in ALL:
    if c in SKIP: continue
    after[c] = "d"
for c in R10: after[c] = "b"
for c in R125: after[c] = "a"
after.update({"CHN": "c", "BRA": "c", "CAN": "e"})

# --- Bridge: Section 122 surcharge, Proclamation 11012 (91 FR 9339): 10% on all imports, 24 Feb - 24 Jul 2026,
# except Section 232 goods, USMCA-qualifying goods of Canada and Mexico and the products in its Annexes.
bridge = {c: "b" for c in ALL if c not in SKIP}

doc = {
    "source": "us-fedreg", "asOf": "2026-10-13", "retrieved": datetime.date.today().isoformat(),
    "note": "Legal basis of the main country-wide additional US tariff on each economy, compiled by Orbis from the Federal Register. "
            "Sector tariffs under Section 232 (steel, aluminium, copper, cars, trucks, lumber, pharmaceuticals and others) apply on top "
            "and are not shown. BEFORE (19 Feb 2026): IEEPA 'reciprocal' tariff, Executive Order 14257 of 2 Apr 2025 (90 FR 15041), "
            "as amended (EO 14326, 90 FR 37963); Canada and Mexico were excluded and instead paid IEEPA 'border' tariffs, EO 14193 and "
            "14194 (90 FR 9113, 9117; Canada 35% from 1 Aug 2025 per EO 14325; USMCA-qualifying goods exempt); China: IEEPA (EO 14195 "
            "and EO 14257, as modified by EO 14357/14358 of 4 Nov 2025) on top of Section 301 tariffs from 2018; Brazil: IEEPA, EO 14323 "
            "of 30 Jul 2025 (40%, scope narrowed by EO 14361) plus the reciprocal tariff. Russia, Belarus, Cuba and North Korea were not "
            "listed under EO 14257. All IEEPA tariffs ended under EO 14389 of 20 Feb 2026 (91 FR 9437); CBP stopped collecting "
            "them on 24 Feb 2026 (CSMS #67834313). BRIDGE: Section 122 surcharge of 10% on all countries, Proclamation 11012 "
            "(91 FR 9339), 24 Feb to 24 Jul 2026. AFTER (13 Oct 2026): USTR Section 301 forced-labour actions, 91 FR 47318 "
            "(FR Doc. 2026-15181, 28 Jul 2026), effective 24 Jul 2026: 12.5% or 10% on all products of 60 economies (the EU counted "
            "as one), with exemptions including all Section 232 goods and, for Canada and Mexico, USMCA duty-free goods; EU, Taiwan "
            "(10%) and Japan, South Korea, Switzerland (12.5%) are charged 'net of MFN'. China also pays the 2018 Section 301 "
            "tariffs (continued, FR Doc. 2026-20510); Brazil also pays 25% under Section 301 from 22 Jul 2026 (FR Doc. 2026-14542); "
            "Canada also pays 50% under Section 338 of the Tariff Act of 1930 on some motor vehicles, dairy and alcoholic beverages from "
            "19 Aug 2026 (Proclamations 11046-11048, 91 FR 46639-46663; scope changed by Proclamations 11056, 11061-11065). "
            "Hong Kong is listed separately by USTR (12.5%); Macau is not listed. Dependent territories (Greenland, Bermuda, New Caledonia and others) and disputed areas are not coded.",
    "sets": {
        "before": {"label": "Legal basis of country-wide tariffs, 19 February 2026", "values": before,
                   "labels": {"a": "IEEPA 'reciprocal' tariff",
                              "b": "IEEPA 'border' tariff (Canada, Mexico)",
                              "c": "IEEPA plus Section 301 (China)",
                              "e": "IEEPA plus a 40% IEEPA penalty (Brazil)",
                              "d": "No IEEPA tariff (already under sanctions)"}},
        "bridge": {"label": "Section 122 surcharge, 24 February to 24 July 2026", "values": bridge,
                   "labels": {"b": "Section 122 surcharge, 10%"}},
        "after": {"label": "Legal basis of country-wide tariffs, 13 October 2026", "values": after,
                  "labels": {"a": "Section 301 forced-labour tariff, 12.5%",
                             "b": "Section 301 forced-labour tariff, 10%",
                             "c": "Two Section 301 tariffs (China, Brazil)",
                             "e": "Section 301 plus Section 338 (Canada)",
                             "d": "No country-wide tariff"}},
    },
}
p = os.path.join(root, "data/tradewar/legal.json")
os.makedirs(os.path.dirname(p), exist_ok=True)
json.dump(doc, open(p, "w"), separators=(",", ":"), ensure_ascii=False)
from collections import Counter
print(p, os.path.getsize(p) // 1024, "KB", Counter(before.values()), Counter(after.values()))
