// Verify registered campaign order, deep links, chapter boundaries and embed.
// Usage: node tools/review-campaigns.mjs <campaign-id> <report.json>
import {createRequire} from 'module';
import fs from 'fs';
const {chromium}=createRequire(import.meta.url)('playwright');
const [id,out]=process.argv.slice(2);
const cp=JSON.parse(fs.readFileSync('stories/campaigns.json','utf8')).find(x=>x.id===id);
if(!cp||!out) throw Error('Expected registered campaign ID and report path');
const base=process.env.ORBIS_BASE_URL||'http://127.0.0.1:8765/';
const b=await chromium.launch({executablePath:process.env.ORBIS_BROWSER,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const errors=[],results=[];
const story=sid=>JSON.parse(fs.readFileSync('stories/'+sid+'.json','utf8'));
try {
  for(const viewport of [{width:1280,height:800},{width:390,height:844}]) {
    const p=await b.newPage({viewport}); p.on('pageerror',e=>errors.push(e.message));
    await p.goto(base+'#c/'+id); await p.waitForSelector('#campGo');
    const order=await p.locator('.camp-list button').evaluateAll(es=>es.map(e=>e.dataset.id));
    if(JSON.stringify(order)!==JSON.stringify(cp.chapters)) throw Error('Campaign order mismatch');
    const title=async expected=>p.waitForFunction(t=>document.querySelector('#sTitle')?.textContent===t,expected,{timeout:30000});
    await p.locator('#campGo').click(); await title(story(cp.chapters[0]).scenes[0].title);
    for(let i=0;i<cp.chapters.length;i++) {
      const sid=cp.chapters[i],st=story(sid);
      await p.goto(base+'#'+sid+'/1'); await p.reload(); await title(st.scenes[0].title);
      await p.goto(base+'#'+sid+'/'+st.scenes.length); await p.reload(); await title(st.scenes.at(-1).title);
      await p.locator('#next').click();
      if(i+1<cp.chapters.length) {
        await title(story(cp.chapters[i+1]).scenes[0].title);
        await p.locator('#prev').click(); await title(st.scenes.at(-1).title);
      } else await p.waitForSelector('#campGo');
    }
    await p.goto(base+'?embed=1#'+cp.chapters[0]+'/1'); await title(story(cp.chapters[0]).scenes[0].title);
    results.push({viewport,order,deepLinks:'passed',chapterBoundaries:'passed',embed:'passed'}); await p.close();
  }
} finally {await b.close(); fs.writeFileSync(out,JSON.stringify({id,results,errors},null,2)+'\n');}
console.log(JSON.stringify({id,results,errors})); if(errors.length)process.exitCode=1;
