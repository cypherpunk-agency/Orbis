"""Aviation before/during/after COVID: World Bank WDI IS.AIR.DPRT, 2019-2021.
Run python tools/build/empty_skies.py. Pins cached raw metadata and data to the release
retrieval date; refuses unclear/non-commercial metadata. Counts takeoffs by carrier
registration country, not by airport geography, and are not passenger counts.
"""
import json,hashlib,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CACHE=ROOT/'.cache/empty-skies-wdi';CACHE.mkdir(parents=True,exist_ok=True)
API='https://api.worldbank.org/v2'
urls={'metadata':API+'/sources/2/series/IS.AIR.DPRT/metadata?format=json','countries':API+'/country?format=json&per_page=400','values':API+'/country/all/indicator/IS.AIR.DPRT?date=2019:2021&format=json&per_page=2000&source=2'}
raw={}
for key,url in urls.items():
 p=CACHE/(key+'.json')
 if not p.exists():
  with urllib.request.urlopen(url,timeout=60) as r: p.write_bytes(r.read())
 raw[key]=json.loads(p.read_text(encoding='utf-8'))
mt={m['id']:m['value'] for m in raw['metadata']['source'][0]['concept'][0]['variable'][0]['metatype']}
lic=mt.get('License_Type','')
assert lic=='CC BY-4.0' or lic=='CC BY 4.0',lic
assert raw['countries'][0]['pages']==1 and raw['values'][0]['pages']==1
countries={c['id'] for c in raw['countries'][1] if c['region']['id']!='NA'}
vals={};world={};years=[2019,2020,2021]
for r in raw['values'][1]:
 c=r['countryiso3code']; y=int(r['date']); v=r['value']
 if v is not None:
  assert v>=0
  if c in countries: vals.setdefault(c,{})[y]=v
  if c=='WLD':world[y]=v
assert vals and all(y in world for y in years)
series={c:[d.get(y) for y in years] for c,d in sorted(vals.items())}
base={c:[round(100*v/a[0],2) if v is not None else None for v in a] for c,a in series.items() if a[0] is not None and a[0]>0}
d={'source':'wb-wdi','asOf':raw['values'][0].get('lastupdated','2026-10-14'),'retrieved':'2026-10-14','years':years,'note':'WDI IS.AIR.DPRT; original source ICAO. Counts domestic takeoffs and takeoffs abroad by carriers registered in each country. These are carrier-registration totals, not departures from the country, passenger numbers or a measure of airspace closures. Annual totals are fixed to 2019/2020/2021. Percentage of 2019 is derived by Orbis only for non-zero known baselines; missing observations stay null. Country aggregates are excluded from map values; the separately reported World series is retained.','licence':lic,'definition':mt.get('Longdefinition',''),'originalSource':mt.get('Source',''),'provenance':{k:{'url':u,'sha256':hashlib.sha256((CACHE/(k+'.json')).read_bytes()).hexdigest()} for k,u in urls.items()},'series':{'departures':{'label':'Registered-carrier takeoffs','units':'takeoffs','values':series},'baseline':{'label':'Takeoffs as % of 2019','units':'% of 2019','values':base}},'world':{'departures':[world[y] for y in years]}}
p=ROOT/'data/people/empty-skies.json';p.write_text(json.dumps(d,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
print('Licence',lic,'countries',len(series),'world',[world[y] for y in years],flush=True)
for c in ['USA','GBR','AUT','TUR','CHN']:print(c,series.get(c),base.get(c),flush=True)
