// Real browser checks for drag momentum and projection fades.
// Instrumentation is supplied only to the test page, never to the shipped app.
import {createRequire} from 'module';import fs from 'fs';import path from 'path';
const {chromium}=createRequire(import.meta.url)('playwright');
const out=process.argv[2]||'.cache/roadmap-review/navigation';fs.mkdirSync(out,{recursive:true});
const embed=process.env.ORBIS_NAV_EMBED==='1';
const target=new URL(process.env.ORBIS_BASE_URL||'http://127.0.0.1:8765/');
if(embed)target.searchParams.set('embed','1');target.hash='explore';
const code=fs.readFileSync('js/app.js','utf8').replace('function update(){',`function update(){
  window.__project=at=>proj(at);
  window.__camera={a:V.a,b:V.b,t:V.t,center:V.center.slice(),inertia:!!inertia};
  (window.__projectionFrames||(window.__projectionFrames=[])).push([V.a,V.b,V.t]);`)
 .replace('canvas.addEventListener("pointerup",endPtr);',`canvas.addEventListener("pointerup",endPtr);
 canvas.addEventListener("pointerup",()=>{window.__release={center:V.center.slice(),inertia:!!inertia};});`);
const b=await chromium.launch({executablePath:process.env.ORBIS_BROWSER,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const report={embed,results:[],errors:[]};
try {
for(const config of [{width:1280,height:800,colorScheme:'dark'},{width:390,height:844,colorScheme:'light'},{width:1280,height:800,colorScheme:'light',reducedMotion:'reduce'}]) {
 const capturePrefix=config.width+'-'+config.colorScheme+'-'+(config.reducedMotion||'normal');
 const p=await b.newPage({viewport:{width:config.width,height:config.height},colorScheme:config.colorScheme,reducedMotion:config.reducedMotion||'no-preference'});
 p.on('pageerror',e=>report.errors.push(e.message));
 await p.route('**/js/app.js',r=>r.fulfill({contentType:'application/javascript',body:code}));
 await p.goto(target.href);
 await p.waitForFunction(()=>window.__project&&document.querySelector('#sTitle')?.textContent==='The world, your way');
 await p.waitForTimeout(600);
 if(embed&&!await p.locator('body').evaluate(e=>e.classList.contains('embed')))throw Error('Embed mode absent');
 if(!config.reducedMotion){
  await p.locator('[data-mode="flat"]').click();await p.waitForTimeout(50);
  await p.evaluate(()=>document.querySelector('#map').addEventListener('pointerdown',()=>{
   const snapshot=document.querySelector('.projection-snapshot');
   window.__visibleAtPress=snapshot&&Number(snapshot.style.opacity||1)>=0.5?snapshot.camera.mode:window.__camera.a;
  },{capture:true,once:true}));
  // Interrupt over the ocean so Explore's country sheet does not change this motion test.
  const at=await p.evaluate(()=>window.__project([-30,15]));
  await p.mouse.move(at[0],at[1]);await p.mouse.down();await p.mouse.up();await p.waitForTimeout(100);
  const interrupted=await p.evaluate(()=>window.__camera);
  const visible=await p.evaluate(()=>window.__visibleAtPress);
  if(interrupted.a!==visible)throw Error('Pointer interruption did not restore the visible projection');
  if(await p.locator('.projection-snapshot').count())throw Error('Pointer interruption retained a projection snapshot');
  if(interrupted.a!=='globe'){await p.locator('[data-mode="globe"]').click();await p.waitForTimeout(1700);}
 }
 const center=await p.evaluate(()=>window.__project([10,30]));await p.mouse.move(center[0]-60,center[1]);await p.mouse.down();
 for(let j=0;j<6;j++){await p.mouse.move(center[0]-60+(j+1)*20,center[1]+j);await p.waitForTimeout(20)}
 await p.mouse.up();const release=await p.evaluate(()=>window.__release.center);
 await p.waitForTimeout(450);const coast=await p.evaluate(()=>window.__camera.center);
 const delta=Math.abs(coast[0]-release[0]);
 if(config.reducedMotion?delta>0.01:delta<0.5)throw Error('Drag momentum/reduced-motion result incorrect: '+delta);
 await p.waitForTimeout(2600);const rested=await p.evaluate(()=>window.__camera);
 if(rested.inertia)throw Error('Drag momentum did not settle');
 await p.waitForTimeout(200);const later=await p.evaluate(()=>window.__camera.center);
 if(Math.abs(rested.center[0]-later[0])>0.01)throw Error('Resting globe keeps moving');
 if(!config.reducedMotion){
  await p.locator('[data-mode="flat"]').click();await p.waitForTimeout(50);
  await p.setViewportSize({width:config.width===1280?390:1280,height:config.width===1280?844:800});
  await p.waitForFunction(()=>document.querySelector('#map').style.width===innerWidth+'px');
  if(await p.locator('.projection-snapshot').count())throw Error('Resize retained a stretched projection snapshot');
  if(await p.locator('#map').evaluate(e=>getComputedStyle(e).opacity)!=='1')throw Error('Resize left map faded');
  await p.setViewportSize({width:config.width,height:config.height});await p.waitForTimeout(200);
  await p.locator('[data-mode="globe"]').click();await p.waitForTimeout(1700);
 }
 for(const basemap of ['political','satellite']) {
  if(basemap==='satellite'){await p.locator('#bmBtn').click();await p.locator('[data-bm="satellite"]').click();await p.waitForLoadState('networkidle');await p.waitForTimeout(500);}
  for(const mode of ['flat','globe']) {
   await p.locator('[data-mode="'+mode+'"]').click();
   if(!config.reducedMotion){
    await p.waitForTimeout(250);await p.screenshot({path:path.join(out,capturePrefix+'-'+basemap+'-'+mode+'-early.png')});
    await p.waitForTimeout(450);await p.screenshot({path:path.join(out,capturePrefix+'-'+basemap+'-'+mode+'-middle.png')});
   }
   await p.waitForTimeout(1500);
   if(await p.locator('.projection-snapshot').count())throw Error('Projection snapshot remains after transition');
   if(await p.locator('#map').evaluate(e=>getComputedStyle(e).opacity)!=='1')throw Error('Map remains faded');
   await p.screenshot({path:path.join(out,capturePrefix+'-'+basemap+'-'+mode+'-end.png')});
  }
 }
 const frames=await p.evaluate(()=>window.__projectionFrames);
 if(frames.some(([a,b,t])=>a!==b||t!==0))throw Error('Transition used a folded intermediate projection');
 report.results.push({config,coastLongitudeDelta:delta,momentumSettled:true,validProjectionFrames:frames.length});await p.close();
}
}catch(e){report.errors.push(e.message)}finally{await b.close();fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');}
console.log(JSON.stringify(report));if(report.errors.length)process.exitCode=1;
