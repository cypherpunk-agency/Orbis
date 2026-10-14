"""Verify semantic EU timeline counts, required outlines and below-fold charts.

Writes local browser report/screenshots, using one browser process.
"""
import os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];os.chdir(ROOT)
os.environ['NODE_PATH']=r'C:\Users\tommi\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules'
os.environ['ORBIS_BROWSER']=r'C:\Program Files\Google\Chrome\Application\chrome.exe'
os.environ['ORBIS_BASE_URL']=os.environ.get('ORBIS_BASE_URL','http://127.0.0.1:8767/')
p=ROOT/'.cache/roadmap-review/M5/extra-review.cjs';p.parent.mkdir(parents=True,exist_ok=True)
p.write_text(r'''
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{
 const b=await chromium.launch({executablePath:process.env.ORBIS_BROWSER,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});const report={views:[],errors:[]};
 try{for(const viewport of [{width:1280,height:800},{width:390,height:844}]){
  const p=await b.newPage({viewport});p.on('pageerror',e=>report.errors.push(e.message));const results={viewport,counts:[],outlines:[],charts:[]};report.views.push(results);
  async function go(id,scene){await p.goto(process.env.ORBIS_BASE_URL+'#@stories/'+id+'.json/'+scene);await p.reload();const story=JSON.parse(fs.readFileSync('stories/'+id+'.json'));await p.waitForFunction(title=>document.querySelector('#sTitle')?.textContent===title,story.scenes[scene-1].title);await p.waitForTimeout(1000);}
  for(const [id,scene,counts]of [['eu-growth',3,[9,10,12]],['eu-growth',4,[12,15]],['eu-growth',5,[25,27,28]],['eu-clubs',2,[20,21,21]],['eu-clubs',4,[27,29,29]],['eu-brexit',3,[28,27,27]]]){
   await go(id,scene);
   for(let index=0;index<counts.length;index++){
    await p.locator('#tlSlider').evaluate((e,index)=>{e.value=index;e.dispatchEvent(new Event('input',{bubbles:true}))},index);await p.waitForTimeout(300);
    const legend=await p.locator('#sLegend').innerText();if(!legend.includes('· '+counts[index]))throw Error(id+'/'+scene+'/'+index+' expected '+counts[index]+', got '+legend);
    results.counts.push({id,scene,index,legend});
   }
  }
  for(const [id,scene]of [['eu-growth',6],['eu-candidates',5]]){
   await go(id,scene);await p.waitForFunction(()=>document.querySelector('#sLegend').textContent.includes('EU27'));await p.waitForTimeout(900);
   const legend=await p.locator('#sLegend').innerText();results.outlines.push({id,scene,legend});await p.screenshot({path:'.cache/roadmap-review/M5/'+id+'/'+viewport.width+'-outline.png'});
  }
  for(const [id,scene,expected]of [['eu-budget',1,['Germany','28,983']],['eu-budget',2,['France','16,391']],['eu-regions',1,['Eastern and Midland','244.7']],['eu-regions',4,['Poland','7,106']]]){
   await go(id,scene);await p.locator('#sChart').scrollIntoViewIfNeeded();const chart=await p.locator('#sChart').innerText();for(const x of expected)if(!chart.includes(x))throw Error('Chart missing '+x+' in '+id+'/'+scene+': '+chart);
   results.charts.push({id,scene,chart});await p.screenshot({path:'.cache/roadmap-review/M5/'+id+'/'+viewport.width+'-chart-'+scene+'.png'});
  }
  await p.close();
 }}catch(e){report.errors.push(e.message)}finally{await b.close();fs.writeFileSync('.cache/roadmap-review/M5/extra-review.json',JSON.stringify(report,null,2));}
 console.log(JSON.stringify({views:report.views.length,errors:report.errors}));if(report.errors.length)process.exitCode=1;
})();
''',encoding='utf-8')
raise SystemExit(subprocess.run(['node',str(p)]).returncode)
