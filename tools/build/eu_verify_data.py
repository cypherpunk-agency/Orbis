"""EU contract data/reproducibility checks; stores local acceptance evidence."""
import hashlib,json,math,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'.cache/roadmap-review/M5';OUT.mkdir(parents=True,exist_ok=True)
paths=list((ROOT/'data/history/eu').glob('*.json'))+list((ROOT/'stories').glob('eu-*.json'))
before={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}
runpy.run_path(str(ROOT/'tools/build/eu_data.py'));runpy.run_path(str(ROOT/'tools/build/eu_stories.py'))
after={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}
assert before==after,'Cached rebuild changed a delivered file'
report={'cachedRebuildIdentical':True,'files':{},'memberships':{},'budget':{},'regions':{}}
for p in (ROOT/'data/history/eu').glob('*.json'):
 d=json.loads(p.read_text(encoding='utf-8'));assert all(k in d for k in ['source','asOf','retrieved','note']);assert p.stat().st_size<1000000
 report['files'][str(p.relative_to(ROOT))]={'bytes':p.stat().st_size,'source':d['source'],'asOf':d['asOf']}
d=json.loads((ROOT/'data/history/eu/memberships.json').read_text(encoding='utf-8'))
def count(k,y):return sum((v[0]if isinstance(v,list)else v)<=y and (not isinstance(v,list)or y<v[1])for v in d['sets'][k]['members'].values())
checks={'eu':{19580101:6,19730101:9,19810101:10,19860101:12,19950101:15,20040501:25,20070101:27,20130701:28,20200131:28,20200201:27,20261014:27},'euro':{20251231:20,20260101:21,20261014:21},'schengen':{20240101:27,20250101:29,20261014:29}}
for k,obs in checks.items():
 report['memberships'][k]={}
 for y,n in obs.items():assert count(k,y)==n,(k,y,count(k,y));report['memberships'][k][y]=n
assert len(d['sets']['candidates']['values'])==9
d=json.loads((ROOT/'data/history/eu/budget.json').read_text(encoding='utf-8'))
assert d['years']==[2021,2022,2023,2024,2025]
for k,s in d['series'].items():
 assert len(s['values'])==27
 for c,arr in s['values'].items():assert len(arr)==5 and all(isinstance(v,(int,float))and math.isfinite(v)for v in arr)
for c in d['series']['receipts']['values']:
 for i in range(5):
  def v(k):return d['series'][k]['values'][c][i]
  assert abs(v('ordinary')+v('ngeu')-v('receipts'))<0.0002
  assert abs(v('receipts')-v('financing')-v('difference'))<0.0002
report['budget']={'years':d['years'],'countryCount':27,'roundedArithmeticPassed':True,'reconciliation':'sources/budget-reconciliation.json','2025':{k:{c:d['series'][k]['values'][c][-1]for c in ['DEU','FRA','ITA','POL','BEL','LUX']}for k in ['financing','ordinary','ngeu','receipts','difference','cohesion']}}
d=json.loads((ROOT/'data/history/eu/regions.json').read_text(encoding='utf-8'))
assert d['periods']==['2023']and len(d['points'])==8
for x in d['points']:assert len(x['gdp'])==1 and x['gdp'][0]>0 and -180<=x['at'][0]<=180 and -90<=x['at'][1]<=90
report['regions']={p['id']:p['gdp'][0]for p in d['points']}
for id in ['eu-growth','eu-clubs','eu-budget','eu-regions','eu-brexit','eu-candidates']:
 s=json.loads((ROOT/'stories'/(id+'.json')).read_text(encoding='utf-8'));assert s['id']==id and 4<=len(s['scenes'])<=8
(OUT/'data-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('EU data gates passed; cached rebuild byte-identical.')
