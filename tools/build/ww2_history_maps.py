"""Reproduce optional WWII US Army atlas overlays, sourced and credited at item level.
Run with the bundled Python (numpy/Pillow): python tools/build/ww2_history_maps.py [--download]
Ground control points were read from named city/island positions in the original scans;
rounded coordinates and polynomial warps are for overview reading, not local control lines.
"""
from pathlib import Path
import argparse,hashlib,json,urllib.request
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[2];D=R/'data/history/ww2';D.mkdir(parents=True,exist_ok=True)
ap=argparse.ArgumentParser();ap.add_argument('--download',action='store_true');a=ap.parse_args()
def scale(points,f):return [[round(x*f,1),round(y*f,1),lon,lat] for x,y,lon,lat in points]
maps=[
 {'id':'northern-europe','filename':'n-europe-1944-1945.jpg','url':'https://maps.lib.utexas.edu/maps/historical/n_europe_1944-1945.jpg','title':'US Army atlas: Northern Europe, June 1944–May 1945','asOf':'1944-06 to 1945-05','bbox':[-6,46,16,55],'order':2,
  'gcps':scale([[595,427,-0.128,51.507],[816,846,2.352,48.857],[1850,222,13.405,52.52],[1014,540,4.352,50.847],[1066,305,4.895,52.367],[1758,909,11.582,48.135],[1999,584,14.437,50.075],[354,409,-2.588,51.455],[545,780,-0.37,49.183],[132,851,-4.486,48.39],[1087,1078,5.041,47.322]],2343/2048)},
 {'id':'pacific-areas','embedOnly':True,'filename':'pacific-area-1942.jpg','url':'https://maps.lib.utexas.edu/maps/historical/pacific_area_1942.jpg','title':'US Army atlas: Pacific command areas, 1 August 1942','asOf':'1942-08-01','bbox':[95,-40,242,67],'order':2,
  'gcps':scale([[525,546,139.76,35.68],[1205,742,202.06,21.35],[591,1081,147.18,-9.44],[471,1100,130.84,-12.46],[665,1258,153.03,-27.47],[582,1364,144.96,-37.81],[133,930,103.82,1.35],[944,645,182.63,28.2],[875,283,173.19,52.84]],2100/1717)},
]
def terms(lon,lat):return np.stack([np.ones_like(lon),lon,lat,lon*lon,lon*lat,lat*lat],axis=-1)
for m in maps:
 raw=D/m['filename']
 if a.download:raw.write_bytes(urllib.request.urlopen(m['url'],timeout=60).read())
 elif not raw.exists():
  cached=R/'.cache/ww2'/m['filename']
  if not cached.exists():raise SystemExit('Missing cleared scan; use --download: '+m['url'])
  raw.write_bytes(cached.read_bytes())
 m['sha256']=hashlib.sha256(raw.read_bytes()).hexdigest();m['originalSize']=list(Image.open(raw).size)
 if m.get('embedOnly'):
  m['note']='Original scan used as panel media. Provisional georeferencing rejected (mean 21.78px, max44.5px); no geographic warp is used.'
  continue
 g=np.array(m['gcps'],float);T=terms(g[:,2],g[:,3]);cx=np.linalg.lstsq(T,g[:,0],rcond=None)[0];cy=np.linalg.lstsq(T,g[:,1],rcond=None)[0]
 residual=np.hypot(T@cx-g[:,0],T@cy-g[:,1]);m['fit']={'order':2,'gcps':len(g),'meanErrorPx':round(float(residual.mean()),2),'maxErrorPx':round(float(residual.max()),2)}
 print(m['id'],m['fit'])
 lon0,lat0,lon1,lat1=m['bbox'];W=1800;H=round(W*(lat1-lat0)/(lon1-lon0));src=np.asarray(Image.open(raw).convert('RGBA'));h,w=src.shape[:2]
 lon=np.linspace(lon0,lon1,W,endpoint=False)+(lon1-lon0)/W/2;lat=np.linspace(lat1,lat0,H,endpoint=False)-(lat1-lat0)/H/2
 lo,la=np.meshgrid(lon,lat);t=terms(lo,la);px=t@cx;py=t@cy;x=np.floor(px).astype(int);y=np.floor(py).astype(int);fx=(px-x)[...,None];fy=(py-y)[...,None]
 inside=(x>=0)&(x<w-1)&(y>=0)&(y<h-1);x=np.clip(x,0,w-2);y=np.clip(y,0,h-2);s=src.astype(float)
 out=s[y,x]*(1-fx)*(1-fy)+s[y,x+1]*fx*(1-fy)+s[y+1,x]*(1-fx)*fy+s[y+1,x+1]*fx*fy;out[~inside]=0
 image=D/(m['id']+'-overlay.webp');Image.fromarray(out.astype(np.uint8)).save(image,'WEBP',quality=82)
 note='US Army Center of Military History, American Military History (1989), scanned by University of Texas Libraries. Courtesy of the University of Texas Libraries, The University of Texas at Austin. Overview polynomial georeferencing from rounded named-place control points; not for local military-control inference. Original scan and GCPs retained alongside this descriptor. '+('The Pacific boundaries divide Allied commands; they do not denote Japanese occupation.' if m['id']=='pacific-areas' else 'Original arrows summarize campaign advances across June 1944–May 1945; they are not one simultaneous front.')
 desc={'source':'us-army-atlas','asOf':m['asOf'],'retrieved':'2026-10-14','title':m['title'],'image':image.relative_to(R).as_posix(),'bbox':m['bbox'],'note':note,'fit':m['fit'],'sourceUrl':m['url'],'original':raw.relative_to(R).as_posix()}
 (D/(m['id']+'-overlay.json')).write_text(json.dumps(desc,indent=2)+'\n',encoding='utf-8')
(D/'map-provenance.json').write_text(json.dumps({'source':'us-army-atlas','asOf':'Historical dates stated per scan','retrieved':'2026-10-14','licence':'Public domain; US federal government cartography','licenceUrl':'https://maps.lib.utexas.edu/maps/faq.html','catalogue':'https://maps.lib.utexas.edu/maps/historical/history_ww2.html','maps':maps},indent=2)+'\n',encoding='utf-8')
