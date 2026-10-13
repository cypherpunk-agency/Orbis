"""US customs duties and the average US tariff rate (US government works, public domain).
Sources:
  1. Monthly Treasury Statement, Table 4 (receipts), line "Customs Duties" (line_code_nbr 405), via the Treasury Fiscal Data API
     https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/mts/mts_table_4 ; also line 830 "Total -- Receipts".
  2. USITC, "U.S. imports for consumption, duties collected, and ratio of duties to value, 1891-2025" (Table 1),
     https://www.usitc.gov/documents/dataweb/ave_table.pdf (March 2026). usitc.gov refuses scripted downloads, so the script
     fetches the Internet Archive's copy of that same URL; or save the PDF by hand to .cache/tw/ave_table.pdf.
  3. US Census Bureau FT-900 country file (.cache/tw/country.xlsx, see tw_census.py): monthly total US goods imports,
     the denominator of the monthly duty rate.
Run:   python3 tools/build/tw_customs.py   (needs pdftotext from poppler-utils)
Output:
  data/tradewar/customs.json      years = yyyymm 201701..latest MTS month, values keyed "USA", billion USD:
      gross = duties deposited in the month; refunds = duties refunded; net = gross - refunds;
      rate12 = gross duties over the last 12 months / general imports over the same 12 months (%);
      share_fy = customs (net) as % of all federal receipts, fiscal year to date
  data/tradewar/tariff_long.json  years 1891..2025: rate = duties collected / value of all imports for consumption (%),
      rate_dutiable = duties / dutiable imports (%), duties (billion USD). Fiscal years 1891-1918, calendar years after."""
import os, json, re, datetime, subprocess, urllib.request
import openpyxl

root = os.path.join(os.path.dirname(__file__), "..", "..")
cache = os.path.join(root, ".cache/tw"); os.makedirs(os.path.join(cache, "mts"), exist_ok=True)
out_dir = os.path.join(root, "data/tradewar"); os.makedirs(out_dir, exist_ok=True)
UA = {"User-Agent": "Orbis-data-build/1.0"}
API = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/mts/mts_table_4"
def get(url, path, refresh=False):
    if refresh or not os.path.exists(path):
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r, open(path, "wb") as f: f.write(r.read())
    return path
FIELDS = "record_date,classification_desc,line_code_nbr,current_month_gross_rcpt_amt,current_month_refund_amt,current_month_net_rcpt_amt,current_fytd_net_rcpt_amt"
q = lambda line: f"{API}?filter=line_code_nbr:eq:{line},record_date:gte:2016-10-01&fields={FIELDS}&sort=record_date&page%5Bsize%5D=500"
cus = json.load(open(get(q(405), os.path.join(cache, "mts/customs_405.json"), refresh=True)))["data"]
tot = json.load(open(get(q(830), os.path.join(cache, "mts/receipts_830.json"), refresh=True)))["data"]
assert all(r["classification_desc"] == "Customs Duties" for r in cus), "line 405 is no longer 'Customs Duties'"
assert all(r["classification_desc"] == "Total -- Receipts" for r in tot)
ym = lambda d: int(d[:4]) * 100 + int(d[5:7])
C = {ym(r["record_date"]): r for r in cus}
T = {ym(r["record_date"]): r for r in tot}
LAST = max(C)
months = sorted(m for m in C if m >= 201701)
assert len(months) == (LAST // 100 - 2017) * 12 + LAST % 100, "gap in MTS months"
f = lambda r, k: float(r[k]) if r[k] not in (None, "null", "") else 0.0

# Census monthly total imports (World, not seasonally adjusted), million USD
wb = openpyxl.load_workbook(os.path.join(cache, "country.xlsx"), read_only=True)
imp = {}
for r in wb.worksheets[0].iter_rows(values_only=True):
    if r[0] in (None, "year"):
        if r[0] is None: break
        continue
    if str(r[1]).zfill(4) == "0015":
        for m in range(12):
            if r[3 + m]: imp[int(r[0]) * 100 + m + 1] = float(r[3 + m])
def back12(m):
    y, mm = divmod(m, 100); out = []
    for _ in range(12):
        out.append(y * 100 + mm); mm -= 1
        if mm == 0: y, mm = y - 1, 12
    return out
gross = {m: f(C[m], "current_month_gross_rcpt_amt") / 1e9 for m in C}
rate12 = []
for m in months:
    b = back12(m)
    if all(x in gross for x in b) and all(x in imp for x in b):
        rate12.append(round(sum(gross[x] for x in b) * 1000 / sum(imp[x] for x in b) * 100, 2))
    else: rate12.append(None)
share = [round(f(C[m], "current_fytd_net_rcpt_amt") / f(T[m], "current_fytd_net_rcpt_amt") * 100, 2) for m in months]
r2 = lambda v: round(v, 2)
LMON = datetime.date(LAST // 100, LAST % 100, 1).strftime("%B %Y")
doc = {"source": "us-treasury-fiscal", "asOf": f"Monthly Treasury Statement through {LMON}", "retrieved": datetime.date.today().isoformat(),
       "note": ("US customs duties by month from the Monthly Treasury Statement, Table 4, line 'Customs Duties' (billion USD; values keyed USA). "
                "gross = duties deposited; refunds = duties paid back (from May 2026 mostly refunds of the IEEPA tariffs the Supreme Court struck down "
                "on 20 Feb 2026); net = gross - refunds (negative when refunds exceed collections). rate12 = gross duties over 12 months divided by "
                "US general goods imports over the same 12 months (Census FT-900, 'World, Not Seasonally Adjusted'), %: an approximation of the "
                "average tariff rate (duties are deposited with a lag of a few weeks and general imports include goods entering bonded warehouses). "
                "rate_m = the same ratio for one month. share_fy = net customs duties as % of all federal receipts, fiscal year (Oct-Sep) to date. Built by tools/build/tw_customs.py."),
       "format": "month", "years": months,
       "series": {
           "gross": {"label": "Customs duties collected", "units": "billion USD", "values": {"USA": [r2(gross[m]) for m in months]}},
           "refunds": {"label": "Customs duties refunded", "units": "billion USD", "values": {"USA": [r2(f(C[m], "current_month_refund_amt") / 1e9) for m in months]}},
           "net": {"label": "Customs duties, net of refunds", "units": "billion USD", "values": {"USA": [r2(f(C[m], "current_month_net_rcpt_amt") / 1e9) for m in months]}},
           "rate12": {"label": "Duties as % of imports, last 12 months", "units": "%", "values": {"USA": rate12}},
           "rate_m": {"label": "Duties as % of imports, in the month", "units": "%",
                      "values": {"USA": [round(gross[m] * 1000 / imp[m] * 100, 2) if m in imp else None for m in months]}},
           "share_fy": {"label": "Customs as % of federal receipts, fiscal year to date", "units": "%", "values": {"USA": share}},
       }}
json.dump(doc, open(os.path.join(out_dir, "customs.json"), "w"), separators=(",", ":"))

# ---------- USITC long series ----------
pdf = os.path.join(cache, "ave_table.pdf")
if not os.path.exists(pdf) or open(pdf, "rb").read(4) != b"%PDF":
    get("https://web.archive.org/web/2026id_/https://www.usitc.gov/documents/dataweb/ave_table.pdf", pdf, refresh=True)
txt = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout
txt = txt[:txt.index("Table 2A")]
rows = {}
for line in txt.splitlines():
    line = re.sub(r"^(\s*\d{4})\s*\([^)]*\)", r"\1", line)  # 1918 and 1930 come in two parts (law changes): add them up
    t = line.split()
    if len(t) == 9 and re.fullmatch(r"(18|19|20)\d\d", t[0]):
        n = [float(x.replace(",", "")) for x in t[1:]]
        y = int(t[0])
        if y in rows:
            a = rows[y]; a["total"] += n[4]; a["duties"] += n[5]; a["dutiable"] += n[2]
            a["rate"] = round(a["duties"] / a["total"] * 100, 1); a["rate_dut"] = round(a["duties"] / a["dutiable"] * 100, 1)
        else: rows[y] = {"total": n[4], "duties": n[5], "dutiable": n[2], "rate_dut": n[6], "rate": n[7]}
Y = sorted(rows)
assert Y == list(range(1891, Y[-1] + 1)), f"missing years in USITC table: {set(range(1891, Y[-1] + 1)) - set(Y)}"
for y in Y:  # the printed ratio must match duties / total
    assert abs(rows[y]["duties"] / rows[y]["total"] * 100 - rows[y]["rate"]) < 0.06, (y, rows[y])
hdr = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December) \d{4}", txt).group(0)
long = {"source": "usitc", "asOf": f"USITC Table 1, 1891-{Y[-1]}, issued {hdr}", "retrieved": datetime.date.today().isoformat(),
        "note": ("Average US tariff: duties collected as % of the value of all imports for consumption (rate) and of dutiable imports only "
                 "(rate_dutiable), from USITC 'U.S. imports for consumption, duties collected, and ratio of duties to value, 1891-"
                 f"{Y[-1]}' (Table 1). Fiscal years 1891-1918, calendar years from 1919; 1918 and 1930 add up the two part-year rows of the table. Values keyed USA. USITC warns the ratio understates "
                 "how restrictive a tariff is (goods kept out by high tariffs do not count). Built by tools/build/tw_customs.py."),
        "years": Y,
        "series": {
            "rate": {"label": "Duties as % of all imports", "units": "%", "values": {"USA": [rows[y]["rate"] for y in Y]}},
            "rate_dutiable": {"label": "Duties as % of dutiable imports", "units": "%", "values": {"USA": [rows[y]["rate_dut"] for y in Y]}},
            "duties": {"label": "Duties collected", "units": "billion USD", "values": {"USA": [round(rows[y]["duties"] / 1e6, 3) for y in Y]}},
        }}
json.dump(long, open(os.path.join(out_dir, "tariff_long.json"), "w"), separators=(",", ":"))

for fn in ("customs.json", "tariff_long.json"): print(fn, os.path.getsize(os.path.join(out_dir, fn)) // 1024, "KB")
for m, g, rr, s in zip(months, doc["series"]["gross"]["values"]["USA"], rate12, share):
    if m % 100 in (3, 6, 9, 12) or m >= 202501: print(m, "gross", g, "rate12", rr, "share_fy", s)
for y in (1891, 1932, 1933, 1946, 1975, 2000, 2017, 2024, 2025): print(y, rows[y])
