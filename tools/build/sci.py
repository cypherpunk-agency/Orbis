"""Meta Social Connectedness Index (SCI), country to country, from the Humanitarian Data Exchange (CC0).
Dataset page: https://data.humdata.org/dataset/social-connectedness-index  (licence checked via the CKAN API:
  license_title "Public Domain / No restrictions (CC0)"; snapshot as of 25 Jan 2026)
Fetch (into .cache/sci/):
  curl -A Orbis-data-build/1.0 -L -o .cache/sci/country.csv \
    https://data.humdata.org/dataset/e9988552-74e4-4ff4-943f-c782ac8bca87/resource/652cf9c9-541f-47de-8d53-ff818062bd0c/download/country.csv
  curl -A Orbis-data-build/1.0 -o .cache/wb/countries.json "https://api.worldbank.org/v2/country?format=json&per_page=400"
Run: python3 tools/build/sci.py
Output: data/people/sci.json  ("matrix" shape for the pairs layer)
  Values are scaled_sci divided by the median scaled_sci of all country pairs (excluding a country with itself),
  so 1 = a typical pair of countries, 100 = a hundred times as many friendships per pair of users. Rounded to 3 significant digits.
  The SCI is symmetric. The value of a country with itself is left out (null)."""
import os, csv, json, datetime, statistics
root = os.path.join(os.path.dirname(__file__), "..", "..")
rows = list(csv.DictReader(open(os.path.join(root, ".cache/sci/country.csv"))))
wb = json.load(open(os.path.join(root, ".cache/wb/countries.json")))[1]
ISO3 = {c["iso2Code"]: c["id"] for c in wb}
ISO3.update({"XK": "XKX", "TW": "TWN"})
sci = {}
for r in rows:
    a, b = ISO3[r["user_country"]], ISO3[r["friend_country"]]
    sci[(a, b)] = float(r["scaled_sci"])
countries = sorted({a for a, _ in sci})
med = statistics.median(v for (a, b), v in sci.items() if a != b)
def sig(v): return float(f"{v:.3g}") if v >= 1 else float(f"{v:.2g}")
def tidy(v):
    v = sig(v)
    return int(v) if v == int(v) else v
values = {a: [None if a == b or (a, b) not in sci else tidy(sci[(a, b)] / med) for b in countries] for a in countries}
out = {
    "source": "meta-sci", "asOf": "2026-01-25", "retrieved": datetime.date.today().isoformat(),
    "note": f"Meta Social Connectedness Index, country level, HDX release (Facebook users active in the 30 days before 25 Jan 2026 with more than 20 friends). "
            f"Values are the published scaled SCI divided by the median of all {len(countries)}×{len(countries)-1} country pairs ({med:g}), "
            "so 1 = a typical pair and 1,000 = a thousand times as likely that two users are Facebook friends. "
            "No data for countries where Facebook is blocked or little used (e.g. China, Iran, North Korea, Syria, Cuba, Turkmenistan), for Palestine or for some small territories.",
    "label": "Social connectedness index", "units": "times the median country pair",
    "countries": countries, "values": values,
}
dst = os.path.join(root, "data/people/sci.json")
json.dump(out, open(dst, "w"), separators=(",", ":"))
print(len(countries), "countries, median", med, os.path.getsize(dst) // 1024, "KB")
