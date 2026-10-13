"""COVID-19 spread for the "covid-spread" story.
Run from the repo root: python3 tools/build/covid.py
Downloads (into .cache/covid-spread/, gitignored):
  ECDC, daily new reported COVID-19 cases worldwide, archived 14 Dec 2020 (CC BY 4.0, ecdc.europa.eu/en/copyright)
    https://opendata.ecdc.europa.eu/covid19/casedistribution/csv
  Our World in Data COVID-19 compact dataset (CC BY 4.0; cases/deaths from the WHO COVID-19 dashboard)
    https://catalog.ourworldindata.org/garden/covid/latest/compact/compact.csv
Writes:
  data/people/covid-first.json   sets.first_case: month (yyyymm) of the first case reported per country (ECDC)
  data/people/covid-deaths.json  series.deaths_pm: confirmed COVID-19 deaths per million by 31 Dec 2022 (OWID/WHO)
Why ECDC for first cases: WHO's own daily file has stray early reports (Germany, Finland, Monaco on 4-8 Jan 2020)
and starts late for some countries (Uzbekistan Oct 2020, Montenegro May 2020); ECDC's daily 2020 file matches
national announcements better. One known ECDC error is corrected below (Mexico).
"""
import csv, json, os, urllib.request, datetime
root = os.path.join(os.path.dirname(__file__), "..", "..")
cache = os.path.join(root, ".cache/covid-spread")
os.makedirs(cache, exist_ok=True)
ECDC = "https://opendata.ecdc.europa.eu/covid19/casedistribution/csv"
OWID = "https://catalog.ourworldindata.org/garden/covid/latest/compact/compact.csv"
def get(url, name):
    p = os.path.join(cache, name)
    if not os.path.exists(p):
        print("downloading", url); urllib.request.urlretrieve(url, p)
    return p
ecdc, owid = get(ECDC, "ecdc.csv"), get(OWID, "compact.csv")
today = datetime.date.today().isoformat()
# ECDC rows without a usable ISO3 code: Taiwan is coded "CNG1925", Wallis and Futuna has none
FIXCODE = {"CNG1925": "TWN"}
FIXGEO = {"WF": "WLF"}

# First reported case per country (ECDC dateRep = date reported)
first = {}
for r in csv.DictReader(open(ecdc, encoding="utf-8-sig")):
    if not r["cases"] or float(r["cases"]) <= 0: continue
    c = FIXCODE.get(r["countryterritoryCode"]) or FIXGEO.get(r["geoId"]) or r["countryterritoryCode"]
    if len(c) != 3: continue  # cases on an international conveyance (Diamond Princess)
    d = int(r["year"] + r["month"].zfill(2))
    if c not in first or d < first[c]: first[c] = d
# ECDC lists single Mexican cases on 14 and 30 Jan 2020 that Mexico never reported; Mexico's health ministry
# confirmed the country's first case on 28 Feb 2020 (WHO's daily file also has none in January).
first["MEX"] = 202002
json.dump({"source": "ecdc-covid", "asOf": "2020-12-14", "retrieved": today,
           "note": "Month of the first COVID-19 case reported per country, from ECDC's daily worldwide data (31 Dec 2019 to 14 Dec 2020), by reporting date. Correction: Mexico set to Feb 2020 (ECDC lists stray January cases; first case confirmed 28 Feb 2020). Countries without a reported case by 14 Dec 2020 are absent; Hong Kong and Macao are not reported separately by ECDC.",
           "sets": {"first_case": {"label": "First case reported", "members": dict(sorted(first.items()))}}},
          open(os.path.join(root, "data/people/covid-first.json"), "w"), separators=(",", ":"))

# Deaths per million by end of 2022 (last weekly value on or before 31 Dec 2022)
dpm = {}
for r in csv.DictReader(open(owid, encoding="utf-8")):
    code, d, v = r["code"], r["date"], r["total_deaths_per_million"]
    if not code or (code.startswith("OWID_") and code != "OWID_KOS") or d > "2022-12-31" or not v: continue
    if code not in dpm or d >= dpm[code][0]: dpm[code] = (d, float(v))
vals = {("XKX" if k == "OWID_KOS" else k): [round(v[1])] for k, v in sorted(dpm.items())}
json.dump({"source": "owid-covid", "asOf": "2022-12-31", "retrieved": today,
           "note": "Confirmed COVID-19 deaths per million people, cumulative to 31 Dec 2022. Our World in Data, based on WHO COVID-19 dashboard data. Confirmed deaths undercount true deaths, by different amounts in different countries.",
           "years": [2022], "series": {"deaths_pm": {"label": "Confirmed COVID-19 deaths per million", "units": "deaths per million", "values": vals}}},
          open(os.path.join(root, "data/people/covid-deaths.json"), "w"), separators=(",", ":"))
print(len(first), "countries with a first case;", len(vals), "with deaths per million")
