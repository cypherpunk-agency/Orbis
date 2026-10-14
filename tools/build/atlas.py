"""Country atlas: download a curated set of World Development Indicators and Worldwide Governance Indicators.

Writes data/atlas/catalog.json (one entry per indicator) and data/atlas/<code>.json (series dataset, one per indicator).
Each indicator's licence is read from the World Bank metadata; only CC BY 4.0 indicators are kept, the rest are
listed as skipped (e.g. military spending, which carries SIPRI terms).

Usage: python3 tools/build/atlas.py [--only CODE,CODE]
"""
import json, os, sys, time, urllib.request, argparse, math

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
OUT = os.path.join(ROOT, "data/atlas")
CACHE = os.path.join(ROOT, ".cache/atlas")
UA = {"User-Agent": "Orbis-data-build/1.0"}
API = "https://api.worldbank.org/v2"

# topic -> [(code, short name, fmt)]; source 2 = WDI, source 3 = WGI
TOPICS = {
 "People": [("SP.POP.TOTL", "Population", "people"), ("SP.POP.GROW", "Population growth (% a year)", "pct"),
   ("SP.DYN.TFRT.IN", "Births per woman", "num"), ("SP.DYN.CBRT.IN", "Births per 1,000 people", "num"),
   ("SP.POP.65UP.TO.ZS", "Share aged 65 and over (%)", "pct"), ("SP.POP.0014.TO.ZS", "Share aged under 15 (%)", "pct"),
   ("SP.URB.TOTL.IN.ZS", "Share living in cities (%)", "pct"), ("EN.POP.DNST", "People per km²", "num"),
   ("SM.POP.NETM", "Net migration (people)", "int"), ("SM.POP.TOTL.ZS", "Born abroad (% of population)", "pct"),
   ("SP.POP.TOTL.FE.ZS", "Women (% of population)", "pct")],
 "Health": [("SP.DYN.LE00.IN", "Life expectancy (years)", "yrs"), ("SP.DYN.LE00.FE.IN", "Life expectancy, women", "yrs"),
   ("SP.DYN.LE00.MA.IN", "Life expectancy, men", "yrs"), ("SH.DYN.MORT", "Child deaths before age 5, per 1,000 births", "num"),
   ("SP.DYN.IMRT.IN", "Infant deaths per 1,000 births", "num"), ("SH.STA.MMRT", "Mothers' deaths per 100,000 births", "int"),
   ("SH.XPD.CHEX.GD.ZS", "Health spending (% of GDP)", "pct"), ("SH.XPD.CHEX.PC.CD", "Health spending per person (US$)", "usd"),
   ("SH.MED.PHYS.ZS", "Doctors per 1,000 people", "num"), ("SH.MED.BEDS.ZS", "Hospital beds per 1,000 people", "num"),
   ("SH.IMM.MEAS", "Measles vaccination (% of children)", "pct"), ("SH.IMM.IDPT", "DTP vaccination (% of children)", "pct"),
   ("SH.STA.STNT.ZS", "Stunted children under 5 (%)", "pct"), ("SN.ITK.DEFC.ZS", "Undernourished (% of population)", "pct"),
   ("SH.PRV.SMOK", "Adults who smoke (%)", "pct"), ("SH.STA.SUIC.P5", "Suicides per 100,000 people", "num"),
   ("SH.TBS.INCD", "Tuberculosis cases per 100,000 people", "int"), ("SH.DYN.AIDS.ZS", "HIV, adults 15–49 (%)", "pct"),
   ("SH.H2O.SMDW.ZS", "Safe drinking water (% of people)", "pct"), ("SH.STA.SMSS.ZS", "Safe sanitation (% of people)", "pct"),
   ("SH.ALC.PCAP.LI", "Alcohol per adult (litres a year)", "num"), ("SH.STA.TRAF.P5", "Road deaths per 100,000 people", "num"),
   ("SH.STA.BRTC.ZS", "Births attended by skilled staff (%)", "pct")],
 "Education": [("SE.ADT.LITR.ZS", "Adults who can read (%)", "pct"), ("SE.PRM.NENR", "Children in primary school (% net)", "pct"),
   ("SE.SEC.ENRR", "Secondary school enrolment (% gross)", "pct"), ("SE.TER.ENRR", "University enrolment (% gross)", "pct"),
   ("SE.XPD.TOTL.GD.ZS", "Education spending (% of GDP)", "pct"), ("SE.PRM.CMPT.ZS", "Finish primary school (%)", "pct"),
   ("SE.PRM.ENRL.TC.ZS", "Pupils per teacher, primary", "num"), ("SE.ENR.PRSC.FM.ZS", "Girls per boy in school (parity index)", "num"),
   ("SE.TER.CUAT.BA.ZS", "Adults with a bachelor's degree (%)", "pct")],
 "Economy": [("NY.GDP.MKTP.CD", "GDP (US$)", "usd"), ("NY.GDP.PCAP.CD", "GDP per person (US$)", "usd"),
   ("NY.GDP.PCAP.PP.CD", "GDP per person (PPP, int. $)", "usd"), ("NY.GDP.MKTP.KD.ZG", "Economic growth (% a year)", "pct"),
   ("FP.CPI.TOTL.ZG", "Inflation (% a year)", "pct"), ("SL.UEM.TOTL.ZS", "Unemployment (%)", "pct"),
   ("SL.TLF.CACT.FE.ZS", "Women in the labour force (%)", "pct"), ("NE.TRD.GNFS.ZS", "Trade (% of GDP)", "pct"),
   ("NE.EXP.GNFS.ZS", "Exports (% of GDP)", "pct"), ("BX.KLT.DINV.WD.GD.ZS", "Foreign investment inflows (% of GDP)", "pct"),
   ("BX.TRF.PWKR.DT.GD.ZS", "Remittances received (% of GDP)", "pct"), ("GC.DOD.TOTL.GD.ZS", "Government debt (% of GDP)", "pct"),
   ("GC.TAX.TOTL.GD.ZS", "Tax revenue (% of GDP)", "pct"), ("NV.AGR.TOTL.ZS", "Farming (% of GDP)", "pct"),
   ("NV.IND.MANF.ZS", "Manufacturing (% of GDP)", "pct"), ("NV.SRV.TOTL.ZS", "Services (% of GDP)", "pct"),
   ("SI.POV.DDAY", "Extreme poverty (% under $3 a day)", "pct"), ("SI.POV.GINI", "Inequality (Gini index)", "num"),
   ("SI.DST.10TH.10", "Income share of the richest 10% (%)", "pct"), ("IT.NET.USER.ZS", "Internet users (%)", "pct"),
   ("IT.CEL.SETS.P2", "Mobile subscriptions per 100 people", "num"), ("EG.ELC.ACCS.ZS", "Access to electricity (%)", "pct"),
   ("DT.ODA.ODAT.PC.ZS", "Aid received per person (US$)", "usd")],
 "Environment": [("EN.GHG.CO2.PC.CE.AR5", "CO₂ per person (t)", "num"), ("EN.GHG.ALL.PC.CE.AR5", "Greenhouse gases per person (t CO₂e)", "num"),
   ("EG.FEC.RNEW.ZS", "Renewable energy (% of final use)", "pct"), ("EG.ELC.RNEW.ZS", "Renewable electricity (%)", "pct"),
   ("EG.USE.PCAP.KG.OE", "Energy use per person (kg oil eq.)", "int"), ("AG.LND.FRST.ZS", "Forest (% of land)", "pct"),
   ("AG.LND.ARBL.ZS", "Arable land (% of land)", "pct"), ("AG.LND.AGRI.ZS", "Farmland (% of land)", "pct"),
   ("ER.H2O.FWST.ZS", "Water stress (% of available water used)", "pct"), ("EN.ATM.PM25.MC.M3", "Air pollution, PM2.5 (µg/m³)", "num")],
 "Governance": [("GE.EST", "Government effectiveness (−2.5 to 2.5)", "num"), ("RL.EST", "Rule of law (−2.5 to 2.5)", "num"),
   ("CC.EST", "Control of corruption (−2.5 to 2.5)", "num"), ("VA.EST", "Voice and accountability (−2.5 to 2.5)", "num"),
   ("PV.EST", "Political stability (−2.5 to 2.5)", "num"), ("RQ.EST", "Regulatory quality (−2.5 to 2.5)", "num")],
}
WGI = {"GE.EST", "RL.EST", "CC.EST", "VA.EST", "PV.EST", "RQ.EST"}

def licence_tier(lic):
    """'commercial' (CC BY / CC0), 'noncommercial' (open but NC or share-alike: allowed as a labelled layer), or None
    (redistribution restricted or terms unclear, e.g. SIPRI's limit on reproducing its data)."""
    L = (lic or "").upper().replace("-", " ")
    if "CC0" in L or "PUBLIC DOMAIN" in L: return "commercial"
    if "CC BY" in L or "CREATIVE COMMONS ATTRIBUTION" in L:
        return "noncommercial" if ("NC" in L.split() or "NONCOMMERCIAL" in L.replace(" ", "") or " SA" in L or "SHAREALIKE" in L.replace(" ", "")) else "commercial"
    return None

def get(url, tries=4):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r: return json.load(r)
        except Exception as e:
            if k == tries - 1: raise
            time.sleep(2 ** (k + 1))

def sig(v, n=4):
    if v is None or v == 0: return v
    return round(v, max(0, n - 1 - int(math.floor(math.log10(abs(v))))))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--only"); a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True); os.makedirs(CACHE, exist_ok=True)
    # real countries only (drop regional and income aggregates)
    cs = get(f"{API}/country?format=json&per_page=400")[1]
    iso = {c["id"]: c["iso2Code"] for c in cs if c["region"]["value"] != "Aggregates"}
    iso3 = set(iso)
    catalog = []; skipped = []
    only = set(a.only.split(",")) if a.only else None
    cat_path = os.path.join(OUT, "catalog.json")
    old = {c["id"]: c for c in json.load(open(cat_path))["indicators"]} if os.path.exists(cat_path) and only else {}
    for topic, items in TOPICS.items():
        for code, short, fmt in items:
            if only and code not in only:
                if code in old: catalog.append(old[code])
                continue
            src = 3 if code in WGI else 2
            try:
                meta = get(f"{API}/sources/{src}/series/{code}/metadata?format=json")
                mt = {m["id"]: m["value"] for m in meta["source"][0]["concept"][0]["variable"][0]["metatype"]}
            except Exception as e:
                skipped.append((code, f"no metadata: {e}")); continue
            lic = mt.get("License_Type", "")
            tier = licence_tier(lic)
            if not tier: skipped.append((code, f"licence: {lic or 'not stated'}")); print("skip", code, lic); continue
            rows = get(f"{API}/country/all/indicator/{code}?format=json&per_page=20000&source={src}")
            if not isinstance(rows, list) or len(rows) < 2 or not rows[1]: skipped.append((code, "no data")); continue
            vals = {}
            for r in rows[1]:
                c = r.get("countryiso3code"); v = r.get("value")
                if c in iso3 and v is not None: vals.setdefault(c, {})[int(r["date"])] = v
            if not vals: skipped.append((code, "no country values")); continue
            years = sorted({y for d in vals.values() for y in d})
            y0, y1 = years[0], years[-1]; ys = list(range(y0, y1 + 1))
            series = {c: [sig(d.get(y)) for y in ys] for c, d in sorted(vals.items())}
            name = mt.get("IndicatorName") or short
            sid = ("wb-wgi" if src == 3 else "wb-wdi") + ("-nc" if tier == "noncommercial" else "")
            ds = {"source": sid, "asOf": rows[0].get("lastupdated", ""), "retrieved": time.strftime("%Y-%m-%d"),
                  "note": f"World Bank, {'Worldwide Governance Indicators' if src == 3 else 'World Development Indicators'}, {code}: {name}. Licence {lic}. Original source: {(mt.get('Source') or '').strip()[:300]}",
                  "years": ys, "series": {"v": {"label": short, "units": mt.get("Unitofmeasure", ""), "values": series}}}
            fn = f"data/atlas/{code}.json"
            json.dump(ds, open(os.path.join(ROOT, fn), "w"), separators=(",", ":"))
            latest = max((y for d in vals.values() for y in d), default=y1)
            n_latest = sum(1 for d in vals.values() if any(y >= latest - 2 for y in d))
            catalog.append({"id": code, "name": short, "long": name, "topic": topic, "fmt": fmt, "units": mt.get("Unitofmeasure", ""),
                            "source": ds["source"], "licence": lic, "tier": tier, "years": [y0, y1], "countries": len(vals),
                            "recent": n_latest, "file": fn, "definition": (mt.get("Longdefinition") or "")[:600]})
            print(f"{code:24s} {len(vals):4d} countries {y0}-{y1} {os.path.getsize(os.path.join(ROOT, fn)) // 1024} KB")
            time.sleep(0.3)
    json.dump({"source": "wb-wdi", "asOf": time.strftime("%Y-%m-%d"), "topics": list(TOPICS), "indicators": catalog,
               "skipped": [{"id": c, "why": w} for c, w in skipped]}, open(cat_path, "w"), indent=1, ensure_ascii=False)
    print(len(catalog), "indicators,", len(skipped), "skipped:", skipped)

if __name__ == "__main__":
    main()
