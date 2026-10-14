// Shared renderer regression: every scene/switch in every registered story.
// Usage: node tools/review-all.mjs <output-dir> [story-id ...]
// Screenshots and JSON results are retained, including failed cases.
import {createRequire} from 'module';
import fs from 'fs';
import path from 'path';
import {createHash} from 'crypto';
const {chromium}=createRequire(import.meta.url)('playwright');
const [out='.cache/roadmap-review/regression',...only]=process.argv.slice(2);
const entries=JSON.parse(fs.readFileSync('stories/index.json','utf8')).filter(x=>!only.length||only.includes(x.id));
const base=process.env.ORBIS_BASE_URL||'http://127.0.0.1:8765/';
// Use alongside the separate normal-motion navigation review. Chapter visual
// acceptance still uses shoot.mjs and the retained all-scene captures.
const smoke=process.env.ORBIS_REVIEW_SMOKE==='1';
fs.mkdirSync(out,{recursive:true});
const hash=file=>createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const rendererHash=hash('js/app.js');
const report={started:new Date().toISOString(),rendererHash,mode:smoke?'reduced-motion-smoke':'all-scene-captures',ids:entries.map(x=>x.id),results:[]};
const reportPath=path.join(out,'results.json');
if(fs.existsSync(reportPath)) {
  const previous=JSON.parse(fs.readFileSync(reportPath,'utf8'));
  fs.copyFileSync(reportPath,path.join(out,'previous-results.json'));
  if(previous.rendererHash===rendererHash&&previous.mode===report.mode) report.results=previous.results.filter(r=>{
    const entry=entries.find(x=>x.id===r.id);
    return entry&&!r.errors.length&&r.storyHash===hash(entry.file)&&r.scenes.length===JSON.parse(fs.readFileSync(entry.file,'utf8')).scenes.length;
  });
  report.resumedFrom=previous.started;
}
const browser=await chromium.launch({executablePath:process.env.ORBIS_BROWSER,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try {
  for(const entry of entries) {
    const st=JSON.parse(fs.readFileSync(entry.file,'utf8'));
    for(const viewport of [{width:1280,height:800},{width:390,height:844}]) {
      if(report.results.some(r=>r.id===entry.id&&r.viewport.width===viewport.width))continue;
      const dir=path.join(out,entry.id,String(viewport.width));fs.mkdirSync(dir,{recursive:true});
      const errors=[],scenes=[],p=await browser.newPage({viewport,reducedMotion:smoke?'reduce':'no-preference'});
      p.on('pageerror',e=>errors.push('page: '+e.message));
      p.on('response',r=>{if(r.status()>=400)errors.push(r.status()+' '+r.url())});
      try {
        await p.goto(base+'#'+entry.id+'/1');
        for(let i=0;i<st.scenes.length;i++) {
          const sc=st.scenes[i];
          await p.waitForFunction(t=>document.querySelector('#sTitle')?.textContent===t,sc.title,{timeout:30000});
          await p.waitForLoadState('networkidle',{timeout:30000});await p.waitForTimeout(smoke?100:1800);
          const label=await p.locator('#srDesc').innerText();
          if(!label.trim())errors.push('Scene '+(i+1)+': no accessible map description');
          if(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2))errors.push('Scene '+(i+1)+': horizontal overflow');
          if(!smoke||i===0)await p.screenshot({path:path.join(dir,'scene-'+(i+1)+'.png')});
          const controls=p.locator('#sSwitch:not([hidden]) button');
          const switches=await controls.count();
          for(let k=0;k<switches;k++) {
            await controls.nth(k).click();await p.waitForLoadState('networkidle');await p.waitForTimeout(smoke?100:400);
            if(!smoke)await p.screenshot({path:path.join(dir,'scene-'+(i+1)+'-option-'+k+'.png')});
          }
          scenes.push({scene:i+1,title:sc.title,switches,description:label});
          if(i+1<st.scenes.length)await p.locator('#next').click();
        }
      }catch(e){errors.push(e.message)}finally{await p.close();}
      if(hash('js/app.js')!==rendererHash)errors.push('Renderer changed during review; repeat with final renderer');
      report.results.push({id:entry.id,storyHash:hash(entry.file),viewport,scenes,errors:[...new Set(errors)]});
      fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');
      console.log(entry.id+' '+viewport.width+': '+(errors.length?'FAIL '+errors.join(' | '):'passed '+scenes.length+' scenes'));
    }
  }
}finally {
  await browser.close();report.finished=new Date().toISOString();
  fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');
}
if(report.results.some(x=>x.errors.length))process.exitCode=1;
