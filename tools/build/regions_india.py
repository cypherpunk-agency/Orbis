"""India by state / union territory: Census 2011 population, and GDP per capita (PPP) 1990-2024.
Fetch:
  mkdir -p .cache/india && cd .cache/india
  # Census 2011 Table A-01 (India, states/UTs, districts, sub-districts). censusindia.gov.in sends an incomplete TLS
  # chain: add its intermediate (http://repository.emsign.com/certs/emSignSSLCAG1.crt, DER -> PEM) to a CA file.
  curl --cacert <ca-with-emsign.pem> -o A-1.xlsx \
    "https://censusindia.gov.in/nada/index.php/catalog/42526/download/46152/A-1_NO_OF_VILLAGES_TOWNS_HOUSEHOLDS_POPULATION_AND_AREA.xlsx"
  # Kummu, Kosonen & Masoumzadeh Sayyar, gridded GDP per capita PPP, Zenodo record 18429133 (CC BY 4.0)
  curl -L -o tabulated_adm1_gdp_perCapita.csv "https://zenodo.org/records/18429133/files/tabulated_adm1_gdp_perCapita.csv?download=1"
  curl -L -o tabulated_adm0_gdp_perCapita.csv "https://zenodo.org/records/18429133/files/tabulated_adm0_gdp_perCapita.csv?download=1"
Run: python3 tools/build/regions_india.py   (needs openpyxl)
Output (series keyed by ISO 3166-2 ids of data/geo/admin1/IND.json):
  data/regions/india.json      pop (Census 2011), source "editorial" (official counts typed from Table A-01; facts)
  data/regions/india_gdp.json  gdp_pc_ppp 1990-2024, source "kummu-gdp"
Census 2011 states are re-cut to today's units with 2011 district counts:
  IN-TG Telangana = the ten 2011 districts 532-541 (before the 2014 transfer of seven Khammam mandals to Andhra Pradesh);
  IN-LA Ladakh = Leh + Kargil; IN-JK = rest of Jammu & Kashmir; IN-DH = Dadra & Nagar Haveli + Daman & Diu."""
import os, json, csv, datetime
import openpyxl
root = os.path.join(os.path.dirname(__file__), "..", "..")
cache = os.path.join(root, ".cache/india")
STATE = {"01": "IN-JK", "02": "IN-HP", "03": "IN-PB", "04": "IN-CH", "05": "IN-UT", "06": "IN-HR", "07": "IN-DL",
         "08": "IN-RJ", "09": "IN-UP", "10": "IN-BR", "11": "IN-SK", "12": "IN-AR", "13": "IN-NL", "14": "IN-MN",
         "15": "IN-MZ", "16": "IN-TR", "17": "IN-ML", "18": "IN-AS", "19": "IN-WB", "20": "IN-JH", "21": "IN-OR",
         "22": "IN-CT", "23": "IN-MP", "24": "IN-GJ", "25": "IN-DH", "26": "IN-DH", "27": "IN-MH", "28": "IN-AP",
         "29": "IN-KA", "30": "IN-GA", "31": "IN-LD", "32": "IN-KL", "33": "IN-TN", "34": "IN-PY", "35": "IN-AN"}
DISTRICT = {**{f"{d:03d}": "IN-TG" for d in range(532, 542)}, "003": "IN-LA", "004": "IN-LA"}  # moved out of AP / JK
pop, india = {}, None
ws = openpyxl.load_workbook(os.path.join(cache, "A-1.xlsx"), read_only=True)["Sheet1"]
for r in ws.iter_rows(min_row=5, values_only=True):
    if r[5] != "Total": continue
    st, dist, level, persons = r[0], r[1], r[3], int(r[10])
    if level == "INDIA": india = persons
    elif level == "STATE": pop[STATE[st]] = pop.get(STATE[st], 0) + persons
    elif level == "DISTRICT" and dist in DISTRICT and st in ("01", "28"):
        pop[DISTRICT[dist]] = pop.get(DISTRICT[dist], 0) + persons
        pop[STATE[st]] -= persons
assert sum(pop.values()) == india, (sum(pop.values()), india)
print("pop:", len(pop), "regions, total", india)
pop_out = {"source": "editorial", "asOf": "2011-03-01", "retrieved": datetime.date.today().isoformat(), "years": [2011],
           "series": {"pop": {"label": "Population, Census 2011", "units": "people", "values": {k: [v] for k, v in pop.items()}}},
           "world": {"pop": [india]},
           "note": "Office of the Registrar General & Census Commissioner, India. Population Census 2011, Table A-01 "
                   "(reference date 1 March 2011), persons. Re-cut to today's states with 2011 district counts: Telangana = "
                   "ten districts of 2011 Andhra Pradesh (Adilabad … Khammam; the official post-2014 figure is 35.0 m because "
                   "seven Khammam mandals went to Andhra Pradesh), Ladakh = Leh + Kargil, Dadra & Nagar Haveli and Daman & Diu "
                   "merged. Jammu & Kashmir counts exclude areas not administered by India. 'world' holds the India total."}

# GDP per capita (PPP), admin-1 table of Kummu et al.
NAME = {"Andaman and Nicobar": "IN-AN", "Andhra Pradesh": "IN-AP", "Arunachal Pradesh": "IN-AR", "Assam": "IN-AS",
        "Bihar": "IN-BR", "Chandigarh": "IN-CH", "Chhattisgarh": "IN-CT", "Goa": "IN-GA", "Gujarat": "IN-GJ",
        "Haryana": "IN-HR", "Himachal Pradesh": "IN-HP", "Jammu and Kashmir": "IN-JK", "Jharkhand": "IN-JH",
        "Karnataka": "IN-KA", "Kerala": "IN-KL", "Madhya Pradesh": "IN-MP", "Maharashtra": "IN-MH", "Manipur": "IN-MN",
        "Meghalaya": "IN-ML", "Mizoram": "IN-MZ", "NCT of Delhi": "IN-DL", "Nagaland": "IN-NL", "Odisha": "IN-OR",
        "Puducherry": "IN-PY", "Punjab": "IN-PB", "Rajasthan": "IN-RJ", "Sikkim": "IN-SK", "Tamil Nadu": "IN-TN",
        "Telangana": "IN-TG", "Tripura": "IN-TR", "Uttar Pradesh": "IN-UP", "Uttarakhand": "IN-UT", "West Bengal": "IN-WB"}
SKIP = {"Dadra and Nagar Haveli", "Daman and Diu", "Lakshadweep"}  # source fills these with the national value
YEARS = list(range(1990, 2025))
gdp, nat = {}, None
for r in csv.DictReader(open(os.path.join(cache, "tabulated_adm1_gdp_perCapita.csv"), encoding="latin-1")):
    if r["iso3"] != "IND" or r["Subnat"] in SKIP: continue
    gdp[NAME[r["Subnat"]]] = [int(r[str(y)]) if r[str(y)] not in ("", "NA") else None for y in YEARS]
for r in csv.DictReader(open(os.path.join(cache, "tabulated_adm0_gdp_perCapita.csv"), encoding="latin-1")):
    if r["iso3"] == "IND": nat = [int(r[str(y)]) for y in YEARS]
print("gdp:", len(gdp), "regions; no value for", sorted((set(STATE.values()) | {"IN-TG", "IN-LA"}) - set(gdp)))
gdp_out = {"source": "kummu-gdp", "asOf": "2026-03-13", "retrieved": datetime.date.today().isoformat(), "years": YEARS,
           "series": {"gdp_pc_ppp": {"label": "GDP per capita, PPP", "units": "international dollars", "values": gdp}},
           "world": {"gdp_pc_ppp": nat},
           "note": "Kummu, M., Kosonen, M. & Masoumzadeh Sayyar, S. (2025), Downscaled gridded global dataset for GDP per capita "
                   "PPP, Scientific Data 12: 178, data v. 2026-03-13 (Zenodo 18429133), admin-1 table. For India the state "
                   "shares come from Reserve Bank of India state accounts (1998-2021), scaled to the World Bank national "
                   "PPP series; Telangana before 2004 and Andaman & Nicobar 2020 are scaled estimates; other years extrapolated. "
                   "The source states units as 2021 international dollars, but the national series rises in step with "
                   "current-price PPP, so compare states within a year rather than reading growth. Jammu & Kashmir includes "
                   "Ladakh (no separate value). No state value for Ladakh, Lakshadweep, Dadra & Nagar Haveli and Daman & Diu. "
                   "'world' holds the India value."}
for name, obj in (("india", pop_out), ("india_gdp", gdp_out)):
    dst = os.path.join(root, f"data/regions/{name}.json")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    json.dump(obj, open(dst, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(dst, os.path.getsize(dst), "bytes")
