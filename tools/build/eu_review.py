"""Sequential screenshot and interaction gate for six unlisted EU stories."""
import os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];os.chdir(ROOT)
os.environ['NODE_PATH']=r'C:\Users\tommi\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules'
os.environ['ORBIS_BROWSER']=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
os.environ['ORBIS_BASE_URL']=os.environ.get('ORBIS_BASE_URL','http://127.0.0.1:8767/')
fail=[]
for id in sys.argv[1:]or ['eu-growth','eu-clubs','eu-budget','eu-regions','eu-brexit','eu-candidates']:
 for view,w,h in [('desktop','1280','800'),('mobile','390','844')]:
  p=Path('.cache/roadmap-review/M5')/id/view;p.mkdir(parents=True,exist_ok=True)
  with (p/'shoot.log').open('w',encoding='utf-8')as f:r=subprocess.run(['node','tools/shoot.mjs','@stories/'+id+'.json',str(p),w,h],stdout=f,stderr=subprocess.STDOUT)
  print(id,view,r.returncode,flush=True)
  if r.returncode:fail.append(id+'/'+view)
 p=Path('.cache/roadmap-review/M5')/id
 with (p/'interactions.log').open('w',encoding='utf-8')as f:r=subprocess.run(['node','tools/review-interactions.mjs','@stories/'+id+'.json',str(p/'interactions.json')],stdout=f,stderr=subprocess.STDOUT)
 print(id,'interactions',r.returncode,flush=True)
 if r.returncode:fail.append(id+'/interactions')
print('FAILURES',fail,flush=True);raise SystemExit(bool(fail))
