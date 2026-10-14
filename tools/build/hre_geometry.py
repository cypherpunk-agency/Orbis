"""Extract source-defined circa-1789 HRE membership and two named territory sets.
Requires svgpathtools, shapely and numpy; no new territorial borders are drawn.
The projection inversion is approximate and explicitly reported.
"""
import sys,pathlib,json,hashlib,re,math,urllib.request,xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[2];CACHE=ROOT/'.cache/roadmap-review/M8';OUT=ROOT/'data/history/hre'
sys.path.insert(0,str(CACHE/'python'))
import numpy as np
from svgpathtools import parse_path
from shapely.geometry import Polygon,MultiPolygon,mapping
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
URL='https://upload.wikimedia.org/wikipedia/commons/2/2d/Map_Holy_Roman_Empire_1789.svg'
PAGE='https://commons.wikimedia.org/wiki/File:Map_Holy_Roman_Empire_1789.svg'
p=CACHE/'hre1789.svg'
if not p.exists():
 CACHE.mkdir(parents=True,exist_ok=True);p.write_bytes(urllib.request.urlopen(urllib.request.Request(URL,headers={'User-Agent':'Orbis research/1.0'})).read())
root=ET.parse(p).getroot()
if hashlib.sha256(p.read_bytes()).hexdigest()!='b227139b3117be2373a6eb5c671afe4de428ae723ddea3ef3be5c9385fbb9916':raise ValueError('SVG source changed; re-audit required')
# Preview is 1400 x 1418; named coastal controls avoid assuming a modern state boundary.
gcps=[('Skagen',622,586,10.58,57.72),('Ruegen',702,682,13.38,54.43),('Elbe mouth',602,724,8.73,53.89),('Rhine mouth',510,782,4.13,51.99),('Brest',247,934,-4.49,48.39),('Cotentin tip',379,859,-1.95,49.72),('Trieste',734,1038,13.77,45.65),('Istria tip',746,1079,13.91,44.77),('Genoa',572,1074,8.93,44.41),('Danzig',852,666,18.65,54.35),('Ancona',778,1140,13.52,43.62),('Venice',700,1048,12.34,45.44)]
g=np.array([[x,y,lon,lat] for n,x,y,lon,lat in gcps])
def terms(x,y):return np.stack([np.ones_like(x),x,y,x*x,x*y,y*y],axis=-1)
a=terms(g[:,0],g[:,1]);clon=np.linalg.lstsq(a,g[:,2],rcond=None)[0];clat=np.linalg.lstsq(a,g[:,3],rcond=None)[0]
err=np.hypot((a@clon-g[:,2])*np.cos(np.radians(g[:,3])),a@clat-g[:,3])*111.2
def affine(e):
 tr=e.get('transform','')
 if tr.startswith('matrix'):
  v=[float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?',tr)];return v
 if tr.startswith('translate'):
  v=[float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?',tr)];return [1,0,0,1,v[0],v[1] if len(v)>1 else 0]
 return [1,0,0,1,0,0]
def shape(e):
 rings=[];a,b,c,d,tx,ty=affine(e)
 for sub in parse_path(e.get('d')).continuous_subpaths():
  pts=[]
  for seg in sub:
   # Source coordinates may be in a small transformed coordinate system.
   n=max(1,min(100,math.ceil(seg.length()*max(abs(a),abs(d))/16)))
   for i in range(n):
    z=seg.point(i/n);x=a*z.real+c*z.imag+tx;y=b*z.real+d*z.imag+ty
    pts.append(((x-1754)*1400/6576.6176,(y-161)*1418/6967.1539))
  if len(pts)>2:
   poly=Polygon(pts).buffer(0)
   if not poly.is_empty:rings.append(poly)
 # Filled compound paths follow source containment: inner rings subtract as holes.
 rings.sort(key=lambda x:x.area,reverse=True);result=Polygon()
 for poly in rings:
  result=result.difference(poly) if result.contains(poly.representative_point()) else result.union(poly)
 return result
elements=[e for e in root if e.tag.endswith('path') and 'fill:#008000;' in e.get('style','')]
selected={e.get('id'):shape(e) for e in elements}
outline=unary_union(list(selected.values())).buffer(1).buffer(-1)
def invert(ring):
 v=np.array(ring.coords);t=terms(v[:,0],v[:,1]);return [[round(float(x),5),round(float(y),5)] for x,y in zip(t@clon,t@clat)]
def polygons(s):
 ps=list(s.geoms) if hasattr(s,'geoms') else [s]
 return [[invert(orient(poly,sign=1).exterior)]+[invert(r) for r in orient(poly,sign=1).interiors] for poly in ps if poly.geom_type=='Polygon']
arcs=[];features=[]
for id,name,group,s,at in [('empire','Holy Roman Empire — circa 1789 reconstruction','empire',outline,[10.5,51]),('habsburg','Habsburg possessions within the Empire','habsburg',selected['Habsburg Holy Roman Empire'],[14.5,49]),('brandenburg','Brandenburg possessions within the Empire','brandenburg',selected['Brandenburg'],[13,52.5])]:
 pp=[]
 for poly in polygons(s.simplify(.7,preserve_topology=True)):
  rr=[]
  for ring in poly:rr.append([len(arcs)]);arcs.append(ring)
  pp.append(rr)
 features.append(dict(type='MultiPolygon',arcs=pp,properties=dict(id=id,name=name,label={'empire':'Empire, c.1789','habsburg':'Habsburg lands','brandenburg':'Brandenburg'}[id],group=group,**{'from':1789,'to':1790},at=at,uncertain=True,note='Single circa-1789 source-map reconstruction; approximate projection inversion. Validity range is a display year, not continuous legal border validity. Extra-imperial possessions are excluded according to source dark-green classification.')))
meta=dict(source='hre-alphathon1789',asOf='Circa 1789 reconstruction; source SVG revision 2021-10-17',retrieved='2026-10-14',units='Approximate cartographic geometry, longitude/latitude degrees; no area statistic',url=PAGE,download=URL,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),licence='CC BY-SA 3.0',credit='Alphathon; Fenn-O-maniC; base map contributors named in attribution.txt',note='Source-defined dark-green membership paths unioned into an outline with one-preview-pixel close/open repair to remove sampled shared-edge slivers; Habsburg Holy Roman Empire and Brandenburg are exact named SVG path selections. Pale-green extra-imperial holdings excluded. Historical reconstruction, not surveyed legal geometry. Current Commons summary mistakenly says 1279; embedded title/description and original 2013 upload comment explicitly say 1789. No modern national border proxies used.',groups={'empire':dict(label='Empire outline, c.1789 (reconstruction)',color='c2'),'habsburg':dict(label='Habsburg imperial possessions',color='c3'),'brandenburg':dict(label='Brandenburg imperial possessions',color='c4')},fit=dict(order=2,controls=len(gcps),meanControlResidualKm=round(float(err.mean()),1),maxControlResidualKm=round(float(err.max()),1)),gcps=[dict(name=n,previewPixel=[x,y],at=[lon,lat],residualKm=round(float(e),1)) for (n,x,y,lon,lat),e in zip(gcps,err)],sourceMembershipPaths=[e.get('id') for e in elements],topology=dict(type='Topology',objects={'shapes':dict(type='GeometryCollection',geometries=features)},arcs=arcs))
OUT.mkdir(parents=True,exist_ok=True);(OUT/'territories1789.json').write_text(json.dumps(meta,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf8')
desc=next(e for e in root if e.tag.endswith('desc')).text
(OUT/'attribution.txt').write_text('Source: '+PAGE+'\nAdaptation: sampled source paths, compound-ring handling, union, approximate georeferencing and simplification by Orbis, 2026-10-14. CC BY-SA 3.0 https://creativecommons.org/licenses/by-sa/3.0/\nHistorical-map author Alphathon; 2021 revision Fenn-O-maniC. Full embedded source attribution follows:\n\n'+desc+'\n',encoding='utf8')
print(len(elements),'membership paths',meta['fit'],'bytes',(OUT/'territories1789.json').stat().st_size)
