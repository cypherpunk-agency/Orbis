"""NASA Black Marble paired 2012/2016 reprocessed global imagery, reduced for story swipe.
Run python tools/build/night_light_change.py. Pillow required. Files are display composites,
not physical radiance grids. Do not infer numeric radiance, casualties or population from pixels.
"""
import hashlib, json, urllib.request
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
CACHE=ROOT/'.cache/night-light-change'; CACHE.mkdir(parents=True,exist_ok=True)
OUT=ROOT/'data/grids'; OUT.mkdir(parents=True,exist_ok=True)
BASE='https://assets.science.nasa.gov/content/dam/science/esd/eo/images/imagerecords/144000/'
frames={}; provenance={}
for year,record in [(2012,'144875'),(2016,'144898')]:
 url=BASE+record+f'/BlackMarble_{year}_3km.jpg'
 raw=CACHE/f'{year}.jpg'
 if not raw.exists():
  with urllib.request.urlopen(url,timeout=120) as r: raw.write_bytes(r.read())
 im=Image.open(raw).convert('RGB'); assert im.size==(13500,6750),im.size
 im=im.resize((4096,2048),Image.Resampling.LANCZOS)
 file=f'night-light-change-{year}.webp'; im.save(OUT/file,'WEBP',quality=90,method=6)
 assert (OUT/file).stat().st_size<1000000
 frames[str(year)]='data/grids/'+file
 provenance[str(year)]={'url':url,'sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'nativeSize':[13500,6750],'outputSize':[4096,2048]}
 print(file,(OUT/file).stat().st_size,flush=True)
d={'source':'nasa-night-change','asOf':'2016','retrieved':'2026-10-14','note':'NASA Black Marble 2012 and 2016 paired reprocessed colour composites, released 2017. Reduced from 13500x6750 to 4096x2048 and compressed to WebP by Orbis. Colour/display brightness is not calibrated radiance; no numeric pixel readings. Clouds, compositing, surface reflectance, lighting practices and observation coverage affect appearance. Compare broad patterns, not individual buildings or household electrification.','units':'NASA display imagery','grid':{'width':4096,'height':2048,'bbox':[-180,-90,180,90]},'encoding':{'type':'image'},'frames':frames,'provenance':provenance}
(OUT/'night-light-change.json').write_text(json.dumps(d,indent=1)+'\n',encoding='utf-8')
