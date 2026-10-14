// Review real story controls and navigation; requires a local server and Playwright.
// Usage: node tools/review-interactions.mjs <id|@stories/file.json> <output.json>
// Optional ORBIS_BASE_URL, ORBIS_BROWSER and NODE_PATH for an installed runtime.
import {createRequire} from 'module';import fs from 'fs';import path from 'path';
const {chromium}=createRequire(import.meta.url)('playwright');
const [id,out='.cache/roadmap-review/interactions.json']=process.argv.slice(2);
if(!id)throw Error('Provide a story ID');
const file=id.startsWith('@stories/')?id.slice(1):'stories/'+id+'.json';
const st=JSON.parse(fs.readFileSync(file,'utf8'));
const b=await chromium.launch({executablePath:process.env.ORBIS_BROWSER,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const report={id,views:[],errors:[]};
try{
for(const viewport of [{width:1280,height:800},{width:390,height:844}]){
 const p=await b.newPage({viewport});const events=[];
 p.on('pageerror',e=>events.push(e.message));p.on('response',r=>{if(r.status()>=400)events.push(r.status()+' '+r.url())});
 const view={viewport,scenes:[],embed:false};report.views.push(view);
 for(let i=0;i<st.scenes.length;i++){
  const sc=st.scenes[i];await p.goto((process.env.ORBIS_BASE_URL||'http://127.0.0.1:8765/')+'#'+id+'/'+(i+1));await p.reload();
  await p.waitForFunction(title=>document.querySelector('#sTitle')?.textContent===title,sc.title);await p.waitForTimeout(700);
  const item={scene:i+1,title:sc.title,timeline:[],cards:0,switches:0};view.scenes.push(item);
  if(sc.timeline){
   const max=Number(await p.locator('#tlSlider').getAttribute('max'));
   for(const v of [...new Set([0,Math.floor(max/2),max])]){
    await p.locator('#tlSlider').evaluate((e,v)=>{e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}))},v);
    const label=await p.locator('#tlYear').innerText();if(!label||label.includes('undefined'))throw Error('Missing timeline label');item.timeline.push({index:v,label});
   }
   if(max>0){await p.locator('#tlPlay').click();await p.waitForTimeout(1800);item.playValue=Number(await p.locator('#tlSlider').inputValue());
    if(item.playValue<1)throw Error('Timeline Play did not advance');if((await p.locator('#tlPlay').innerText())==='Pause')await p.locator('#tlPlay').click();}
  }
  const card=p.locator('#sLegend button[data-ci]');item.cards=await card.count();
  if(item.cards){await card.first().focus();await p.keyboard.press('Enter');await p.locator('#sCard').waitFor({state:'visible'});
   if(!await p.locator('#sCard a').count())throw Error('Event card has no source link');await p.locator('#sCard .card-x').click();}
  const sw=p.locator('#sSwitch button');item.switches=await sw.count();
  for(let k=0;k<item.switches;k++){await sw.nth(k).focus();await p.keyboard.press('Enter');if(await sw.nth(k).getAttribute('aria-pressed')!=='true')throw Error('Switch not selected');}
  if((sc.layers||[]).some(l=>l.compare!=null)){
   const handle=p.locator('.sw-h');const before=await handle.boundingBox();await handle.focus();await p.keyboard.press('ArrowRight');const after=await handle.boundingBox();
   if(!before||!after||after.x<=before.x)throw Error('Swipe keyboard control did not move');item.swipeKeyboard=true;
  }
  await p.locator('#sNotes summary').click();if(!(await p.locator('#sNotesBody').innerText()).trim())throw Error('Missing notes');
  if(i+1<st.scenes.length){await p.locator('#next').click();await p.waitForFunction(title=>document.querySelector('#sTitle')?.textContent===title,st.scenes[i+1].title);await p.locator('#prev').click();await p.waitForFunction(title=>document.querySelector('#sTitle')?.textContent===title,sc.title);}
  const horizontal=await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2);if(horizontal)throw Error('Page overflows horizontally');
 }
 await p.goto((process.env.ORBIS_BASE_URL||'http://127.0.0.1:8765/')+'?embed=1#'+id+'/1');await p.waitForFunction(title=>document.querySelector('#sTitle')?.textContent===title,st.scenes[0].title);
 view.embed=await p.locator('body').evaluate(e=>e.classList.contains('embed'));if(!view.embed)throw Error('Embed mode absent');
 report.errors.push(...events.map(e=>viewport.width+': '+e));await p.close();
}
}catch(e){report.errors.push(e.message)}finally{await b.close();fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');}
console.log(JSON.stringify({id,views:report.views.length,errors:report.errors}));if(report.errors.length)process.exitCode=1;
