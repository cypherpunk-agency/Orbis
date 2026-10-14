"""Prepare small EU chapter datasets from official/cached primary data.

Commission workbook: https://commission.europa.eu/strategy-and-policy/eu-budget/long-term-eu-budget/2021-2027/spending-and-revenue_en
CC BY 4.0; Orbis subsets/derivations retain attribution and change notice.
"""
import copy,json,math,urllib.request
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'data/history/eu';CACHE=ROOT/'.cache/roadmap-review/M5/sources'
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
def meta(source,asof,note):return {'source':source,'asOf':asof,'retrieved':'2026-10-14','note':note}
EU={c:1958 for c in ['BEL','DEU','FRA','ITA','LUX','NLD']}
for y,c in [(1973,'DNK IRL'),(1981,'GRC'),(1986,'ESP PRT'),(1995,'AUT FIN SWE'),(2004,'CYP CZE EST HUN LVA LTU MLT POL SVK SVN'),(2007,'BGR ROU'),(2013,'HRV')]:EU.update({x:y for x in c.split()})
EU['GBR']=[19730101,20200201]
members={k:(v if isinstance(v,list) else v*10000+101)for k,v in EU.items()}
members.update({c:20040501 for c,y in EU.items() if y==2004});members['HRV']=20130701
euro={c:19990101 for c in 'AUT BEL DEU ESP FIN FRA IRL ITA LUX NLD PRT'.split()}
for y,c in [(2001,'GRC'),(2007,'SVN'),(2008,'CYP MLT'),(2009,'SVK'),(2011,'EST'),(2014,'LVA'),(2015,'LTU'),(2023,'HRV'),(2026,'BGR')]:euro.update({x:y*10000+101 for x in c.split()})
schengen={c:20240101 for c in members if c not in ['GBR','CYP','IRL','BGR','ROU']}
schengen.update({c:20240101 for c in ['ISL','NOR','CHE','LIE']})
schengen.update({'BGR':20250101,'ROU':20250101})
# A bounded snapshot series: 2024-01-01 is first observation, not accession.
# 2025 means completion of Bulgarian/Romanian land-border participation.
sets={'eu':{'label':'EEC / EC / EU','members':members},'euro':{'label':'Euro area','members':euro},'schengen':{'label':'Schengen (full land-border participation)','members':schengen},'founders':{'label':'Six founding states','values':{c:'member' for c in 'BEL DEU FRA ITA LUX NLD'.split()}},'candidates':{'label':'Candidate status, 14 October 2026','values':{c:'candidate' for c in 'MNE SRB ALB MKD BIH TUR UKR MDA GEO'.split()},'labels':{'candidate':'EU candidate'}}}
sets['euro_status']={'label':'EU currency status, 14 October 2026','values':{c:('euro' if c in euro else 'optout' if c=='DNK' else 'notyet')for c in members if c!='GBR'},'labels':{'euro':'Euro area','optout':'Danish treaty opt-out','notyet':'EU member, euro not yet adopted'}}
write(OUT/'memberships.json',{**meta('editorial','2026-10-14','Official EU country profiles and history; euro Bulgaria verified by ECB 2026-01-01 release; Schengen full land participation verified by Council 2024-12-12 decision. https://european-union.europa.eu/principles-countries-history/eu-countries_en ; https://www.consilium.europa.eu/policies/schengen-area/ ; https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.pr260101~c830245e42.en.html . UK end is 1 February 2020 Gregorian date, departure at midnight CET on 31 January. EU/euro dates identify entry dates. Schengen is only a bounded snapshot series from 2024-01-01: that starting date is an observation, NOT the accession date of 27 already-participating countries. BGR/ROU enter the full-land-control-removal representation on 2025-01-01; air/sea controls were already removed in March 2024. Modern country geometry is contextual, not historical sovereign boundaries.'),'sets':sets})
# Dated 2026 EU outline uses modern Natural Earth country geometry. No historic borders.
world=json.loads((ROOT/'data/world50.json').read_text(encoding='utf-8'))
obj=next(iter(world['objects'].values())); selected=[copy.deepcopy(g) for g in obj['geometries'] if g.get('id')in members and g.get('id')!='GBR']
assert len(selected)==27
arcs=[];mapping={}
def remap(x):
 if isinstance(x,list):return [remap(i)for i in x]
 i=x if x>=0 else ~x
 if i not in mapping:mapping[i]=len(arcs);arcs.append(world['arcs'][i])
 return mapping[i] if x>=0 else ~mapping[i]
for g in selected:
 g['arcs']=remap(g['arcs']);g['properties']={'name':g.get('properties',{}).get('name',g['id']),'group':'eu','from':20260101,'to':20261015}
top={'type':'Topology','objects':{'shapes':{'type':'GeometryCollection','geometries':selected}},'arcs':arcs}
if 'transform'in world:top['transform']=world['transform']
write(OUT/'union-outline.json',{**meta('naturalearth','2026-10-14','Natural Earth public domain country subset, with original Orbis 2026 membership annotations. Modern base geometry only; country status and union outline do not represent historical sovereignty or the territorial application of every treaty provision.'),'groups':{'eu':{'label':'EU27, 14 October 2026','color':'c1'}},'topology':top})

CACHE.mkdir(parents=True,exist_ok=True);raw=CACHE/'eu-budget-2000-2025.xlsx'
url='https://commission.europa.eu/document/download/9f334bee-d097-4b68-8f93-2225eabeb631_en?filename=eu_budget_spending_and_revenue_2000-2025.xlsx'
if not raw.exists():raw.write_bytes(urllib.request.urlopen(url,timeout=90).read())
w=openpyxl.load_workbook(raw,read_only=True,data_only=True)
iso=dict(zip('BE BG CZ DK DE EE IE EL ES FR HR IT CY LV LT LU HU MT NL AT PL PT RO SI SK FI SE'.split(),'BEL BGR CZE DNK DEU EST IRL GRC ESP FRA HRV ITA CYP LVA LTU LUX HUN MLT NLD AUT POL PRT ROU SVN SVK FIN SWE'.split()))
years=list(range(2021,2026));series={k:{'label':v,'units':'EUR million','values':{c:[]for c in iso.values()}}for k,v in {'financing':'VAT/GNI/plastics financing incl. adjustments, customs excluded','ordinary':'Allocated expenditure, ordinary budget','ngeu':'Allocated NextGenerationEU expenditure','receipts':'Allocated expenditure including NGEU','difference':'Allocated expenditure minus defined financing','surplus':'Positive expenditure-minus-financing difference','excess':'Positive financing-minus-expenditure difference','cohesion':'Economic, social and territorial cohesion expenditure (ordinary budget)'}.items()}
validation={}
for y in years:
 rows=list(w[str(y)].values);header=tuple(v.rstrip('*').strip() if isinstance(v,str)else v for v in rows[2]);cols={c:header.index(c)for c in iso}
 def row(label):
  found=[r for r in rows if any(isinstance(s,str)and s.strip()==label for s in r[:2])]
  assert len(found)==1,(y,label,len(found));return found[0]
 def n(r,i):
  v=r[i];assert isinstance(v,(int,float))and math.isfinite(v),(y,i,v);return v
 ordinary=row('TOTAL EXPENDITURE');ngeu=row('TOTAL NGEU');own=row('TOTAL Own resources');adj=row('TOTAL Balances and adjustments');custom=row('Customs duties')
 coh=row('Economic, Social and territorial cohesion')
 for c,i in cols.items():
  a=n(ordinary,i);b=n(ngeu,i);fin=n(own,i)+n(adj,i)-n(custom,i);rec=a+b;diff=rec-fin
  vals={'ordinary':a,'ngeu':b,'financing':fin,'receipts':rec,'difference':diff,'surplus':max(0,diff),'excess':max(0,-diff),'cohesion':n(coh,i)}
  for k,v in vals.items():series[k]['values'][iso[c]].append(round(v,4))
 # Every selected country allocation reconciles to its EU27 column.
 validation[y]={}
 for k,r in [('ordinary',ordinary),('ngeu',ngeu),('cohesion',coh)]:
  a=sum(n(r,i)for i in cols.values());b=n(r,header.index('EU-27'));assert abs(a-b)<0.02,(y,k,a,b);validation[y][k]={'countrySum':a,'reportedEU27':b}
write(OUT/'budget.json',{**meta('eu-budget','2025-12-31','European Commission EU spending and revenue 2000–2025 workbook, released 2026-09-29, selected 2021–2025 sheets. Source: '+url+' . CC BY 4.0. Orbis reduced/rounded subset and derived differences; changes are Orbis responsibility. Financing = TOTAL Own resources + TOTAL Balances and adjustments - Customs duties (sugar levies are zero in selected years). Receipts = country TOTAL EXPENDITURE + country TOTAL NGEU. Ordinary country allocations exclude externally assigned expenditure, NGEU is added explicitly. This defined cash comparison is not the Commission operating budgetary balance or a welfare measure. Geographic allocation is imperfect; administrative spending is included. Cohesion uses only Economic, Social and territorial cohesion in the ordinary country allocation, not total Cohesion/Resilience/Values heading. All units EUR million, nominal. Country observations exclude unallocated/non-EU/earmarked columns.'),'years':years,'series':series})
write(CACHE/'budget-reconciliation.json',validation)

# Frozen press-release comparison: 2023 NUTS2 GDP/head PPS, EU27=100.
regions=[('IE06','Eastern and Midland',[ -6.3,53.35],244.7),('LU00','Luxembourg',[6.13,49.61],236.8),('IE05','Southern Ireland',[-8.47,51.90],224.7),('CZ01','Praha',[14.42,50.08],192.8),('BE10','Brussels',[4.35,50.85],190.6),('BG42','Yuzhen Tsentralen',[24.75,42.14],41.3),('EL41','Voreio Aigaio',[26.56,39.11],42.3),('BG31','Severozapaden',[24.6,43.41],42.5)]
write(OUT/'regions.json',{**meta('eurostat','2023-12-31','Source: Eurostat nama_10r_2gdp, 2023 observations frozen to the 11 February 2025 release https://ec.europa.eu/eurostat/en/web/products-eurostat-news/w/ddn-20250211-2 . CC BY 4.0; Orbis selected eight-region subset and approximate regional reference locations. Eurostat is not responsible for these modifications. GDP per inhabitant in PPS as percentage of EU27 average. Reference points are not regional geometry or values at that city; labels name entire NUTS2 regions. GDP is not household income; commuting/multinational effects matter. Overseas Mayotte/Guyane intentionally outside this selected mainland/northern-Aegean comparison; not an exhaustive rank.'),'periods':['2023'],'points':[{'id':c,'name':name,'at':at,'gdp':[v]}for c,name,at,v in regions]})
print('EU datasets built; Commission allocation totals reconcile for 2021–2025.')
