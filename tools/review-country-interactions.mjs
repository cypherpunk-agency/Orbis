// Actual pointer acceptance checks; instrumentation exists only in the test page.
import {createRequire} from 'module';
import fs from 'fs';
import path from 'path';
import {createHash} from 'crypto';
const {chromium}=createRequire(import.meta.url)('playwright');
const out='.cache/roadmap-review/country-interaction-final.json';
const dir=path.dirname(out);fs.mkdirSync(dir,{recursive:true});
const raw=fs.readFileSync('js/app.js','utf8');
const code=raw.replace('function update(){',`function update(){
window.__project=at=>proj(at);
window.__interaction=()=>({pairFrom,focus,pairs:L.pairs&&L.pairs.from,values:L.cdata,highlight:L.highlight,flows:L.flows.map(f=>[f.a,f.b,f.v]),regions:L.regions.map(r=>({values:r.vals,year:r.year}))});`);
const report={rendererHash:createHash('sha256').update(raw).digest('hex'),views:[],errors:[]};
const sci=JSON.parse(fs.readFileSync('data/people/sci.json','utf8'));
const flows=JSON.parse(fs.readFileSync('data/people/refugees-flows.json','utf8'));
const elections=JSON.parse(fs.readFileSync('data/history/usa/us-elections.json','utf8'));
const b=await chromium.launch({executablePath:process.env.ORBIS_BROWSER,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const assert=(condition,message)=>{if(!condition)throw Error(message)};
try{
for(const viewport of [{width:1280,height:800},{width:390,height:844}]){
 const p=await b.newPage({viewport,hasTouch:viewport.width===390});
 p.on('pageerror',e=>report.errors.push(viewport.width+': '+e.message));
 await p.route('**/js/app.js',r=>r.fulfill({contentType:'application/javascript',body:code}));
 const item={viewport,checks:[]};report.views.push(item);
 const load=async(id,n)=>{const st=JSON.parse(fs.readFileSync('stories/'+id+'.json','utf8'));await p.goto((process.env.ORBIS_BASE_URL||'http://127.0.0.1:8767/')+'#'+id+'/'+n);await p.reload();await p.waitForFunction(title=>window.__project&&document.querySelector('#sTitle')?.textContent===title,st.scenes[n-1].title);await p.waitForTimeout(2200);};
 const state=()=>p.evaluate(()=>window.__interaction());
 const tap=async(at)=>{const q=await p.evaluate(at=>window.__project(at),at);assert(q&&q.every(Number.isFinite),'Invalid projected coordinate');const hit=await p.evaluate(q=>document.elementFromPoint(...q)?.id,q);assert(hit==='map','Map tap intercepted by '+hit+' at '+q);if(viewport.width===390)await p.touchscreen.tap(...q);else await p.mouse.click(...q);await p.waitForTimeout(600);return q;};
 await load('friends',1);const before=await state();assert(before.pairs==='PRT','Wrong initial SCI origin');
 await p.screenshot({path:path.join(dir,'country-'+viewport.width+'-friends-before.png')});
 const point=await tap([2,47]);const after=await state();const legend=await p.locator('#sLegend').innerText();
 assert(after.pairs==='FRA'&&after.pairFrom==='FRA','France tap did not select SCI origin');
 assert(after.highlight.includes('FRA'),'SCI origin not highlighted');
 for(const id of ['PRT','DEU','GBR'])assert(after.values[id]===sci.values.FRA[sci.countries.indexOf(id)],'SCI map values differ from FRA source row: '+id);
 assert(JSON.stringify(before.values)!==JSON.stringify(after.values),'SCI map values did not change');
 assert(legend.includes('France'),'SCI legend did not change to France');
 await p.screenshot({path:path.join(dir,'country-'+viewport.width+'-friends.png')});
 item.checks.push({story:'friends',scene:1,point,beforeOrigin:before.pairs,afterOrigin:after.pairs,legend,source:'data/people/sci.json',sourceValuesMatched:true,mapChanged:true});
 await load('refugees',4);const original=await state();assert(original.flows.length>1,'No initial refugee flows');
 await p.screenshot({path:path.join(dir,'country-'+viewport.width+'-refugees-before.png')});
 const fp=await tap([10,51]);const filtered=await state();const fl=await p.locator('#sLegend').innerText();
 const refugeeTip=await p.locator('#tip').innerText();
 assert(refugeeTip.includes('hosted here (all origins)')&&refugeeTip.includes('2,655,191')&&!/exports|imports/.test(refugeeTip),'Refugee stock terminology/scope incorrect: '+refugeeTip);
 const expected=flows.groups.ref.flows['2025'].filter(r=>r[0]==='SYR'&&(r[0]==='DEU'||r[1]==='DEU')).sort((a,b)=>b[2]-a[2]).slice(0,12).map(r=>r.slice(0,3));
 assert(filtered.focus==='DEU','Germany tap did not select refugee filter');assert(JSON.stringify(filtered.flows)===JSON.stringify(expected),'Filtered flows differ from 2025 source');assert(fl.includes('Germany')&&fl.includes('tap it again'),'Refugee filter legend missing');
 await p.screenshot({path:path.join(dir,'country-'+viewport.width+'-refugees-filtered.png')});
 await tap([10,51]);const cleared=await state();assert(cleared.focus===null&&JSON.stringify(cleared.flows)===JSON.stringify(original.flows),'Second Germany tap did not restore original flows');
 await p.screenshot({path:path.join(dir,'country-'+viewport.width+'-refugees-cleared.png')});
 item.checks.push({story:'refugees',scene:4,point:fp,initialCount:original.flows.length,filteredFlows:filtered.flows,clearedCount:cleared.flows.length,legend:fl,tooltip:refugeeTip,source:'data/people/refugees-flows.json',sourceValuesMatched:true});
 await load('ua-refugees',1);const up=await tap([10,51]);const ut=await p.locator('#tip').innerText();
 const ukraineStock=flows.groups.ref.flows['2025'].find(r=>r[0]==='UKR'&&r[1]==='DEU')[2];
 assert(ut.includes('hosted here (Ukraine origin only)')&&ut.includes(new Intl.NumberFormat('en-US').format(ukraineStock))&&!ut.includes('2,655,191')&&!/exports|imports/.test(ut),'Ukraine tooltip not scoped to source origin: '+ut);
 await p.screenshot({path:path.join(dir,'country-'+viewport.width+'-ukraine.png')});
 item.checks.push({story:'ua-refugees',scene:1,point:up,tooltip:ut,sourceStock:ukraineStock,source:'data/people/refugees-flows.json',sourceValuesMatched:true});
 await load('us-elections',1);const rp=await tap([-99,31]);const tip=await p.locator('#tip').innerText();assert(tip.includes('Texas')&&tip.includes(elections.sets.elections.byYear['1860']['US-TX'])&&tip.includes('1860'),'Texas category tap lacks correct name/allocation/date: '+tip);
 await p.screenshot({path:path.join(dir,'country-'+viewport.width+'-elections.png')});
 item.checks.push({story:'us-elections',scene:1,point:rp,tooltip:tip,source:'data/history/usa/us-elections.json',expectedCategory:'Breckinridge',expectedYear:1860});
 await p.close();
}
}catch(e){report.errors.push(e.message)}finally{await b.close();fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');}
console.log(JSON.stringify({views:report.views.length,checks:report.views.map(v=>v.checks.length),errors:report.errors}));if(report.errors.length)process.exitCode=1;
