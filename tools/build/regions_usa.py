"""US states (50 + DC): population estimates and median household income. US Census Bureau (public domain).
Fetch:
  mkdir -p .cache/usa && cd .cache/usa
  curl -O https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/state/totals/NST-EST2025-ALLDATA.csv
  curl -O https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/1YRData/acsdt1y2024-b19013.dat
  (the Census data API now requires a key; these bulk files do not)
Run: python3 tools/build/regions_usa.py
Output: data/regions/usa.json, series keyed by ISO 3166-2 ids of data/geo/admin1/USA.json ("US-CA"); "world" = US total."""
import os, json, csv, datetime
root = os.path.join(os.path.dirname(__file__), "..", "..")
cache = os.path.join(root, ".cache/usa")
FIPS = {"01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE", "11": "DC",
        "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY",
        "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT",
        "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
        "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT",
        "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI", "56": "WY"}  # Puerto Rico (72) is not in USA.json
YEARS = list(range(2020, 2026))
ACS_YEAR = 2024
pop, pop_us = {}, None
for r in csv.DictReader(open(os.path.join(cache, "NST-EST2025-ALLDATA.csv"), encoding="latin-1")):
    vals = [int(r[f"POPESTIMATE{y}"]) for y in YEARS]
    if r["SUMLEV"] == "010": pop_us = vals
    elif r["SUMLEV"] == "040" and r["STATE"] in FIPS: pop["US-" + FIPS[r["STATE"]]] = vals
inc, inc_us = {}, None
for r in csv.DictReader(open(os.path.join(cache, f"acsdt1y{ACS_YEAR}-b19013.dat"), encoding="latin-1"), delimiter="|"):
    g = r["GEO_ID"]
    v = [int(r["B19013_E001"]) if y == ACS_YEAR else None for y in YEARS]
    if g == "0100000US": inc_us = v
    elif g.startswith("0400000US") and g[-2:] in FIPS: inc["US-" + FIPS[g[-2:]]] = v
out = {"source": "us-census", "asOf": "2025-12", "retrieved": datetime.date.today().isoformat(), "years": YEARS,
       "series": {
           "pop": {"label": "Resident population, 1 July estimate (Vintage 2025)", "units": "people", "values": pop},
           "income": {"label": f"Median household income, {ACS_YEAR} (ACS 1-year)", "units": f"USD ({ACS_YEAR} dollars)", "values": inc}},
       "world": {"pop": pop_us, "income": inc_us},
       "note": "Population: Census Bureau Population Estimates Program, Vintage 2025 (NST-EST2025-ALLDATA), July 1 of each year "
               "(2020 = July 1, 2020 estimate). Income: American Community Survey 1-year estimates, table B19013, "
               f"{ACS_YEAR}, in {ACS_YEAR} inflation-adjusted dollars; sample estimates with margins of error. "
               "50 states and District of Columbia; Puerto Rico excluded. 'world' holds the US total."}
for k, s in out["series"].items():
    print(k, len(s["values"]), "regions; missing", sorted(set("US-" + v for v in FIPS.values()) - set(s["values"])))
dst = os.path.join(root, "data/regions/usa.json")
os.makedirs(os.path.dirname(dst), exist_ok=True)
json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(dst, os.path.getsize(dst), "bytes")
