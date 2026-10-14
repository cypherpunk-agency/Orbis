// Validate the complete final renderer regression against the current checkout.
// Usage: node tools/check-roadmap-regression.mjs <report-dir> [report-dir ...]
import fs from 'fs';
import path from 'path';
import {createHash} from 'crypto';
const hash=file=>createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const index=JSON.parse(fs.readFileSync('stories/index.json','utf8'));
const rendererHash=hash('js/app.js'),errors=[],rows=new Map();
for(const dir of process.argv.slice(2)){
 const report=JSON.parse(fs.readFileSync(path.join(dir,'results.json'),'utf8'));
 if(report.rendererHash!==rendererHash){errors.push(dir+': renderer hash differs');continue;}
 if(report.mode!=='all-scene-captures'){errors.push(dir+': not the full scene capture pass');continue;}
 for(const row of report.results){
  const key=row.id+':'+row.viewport.width;
  if(rows.has(key))errors.push(key+': duplicate viewport result');
  rows.set(key,{dir:row.captureDir||dir,row});
 }
}
let sceneViews=0,optionViews=0,screenshots=0;
for(const entry of index){
 const story=JSON.parse(fs.readFileSync(entry.file,'utf8'));
 for(const width of [1280,390]){
  const key=entry.id+':'+width,hit=rows.get(key);
  if(!hit){errors.push(key+': missing result');continue;}
  const {dir,row}=hit;
  if(row.errors.length)errors.push(key+': '+row.errors.join(' | '));
  if(row.viewport.height!==(width===1280?800:844))errors.push(key+': wrong viewport height');
  if(row.storyHash!==hash(entry.file))errors.push(key+': story changed since review');
  if(row.scenes.length!==story.scenes.length)errors.push(key+': incomplete scenes');
  for(let i=0;i<story.scenes.length;i++){
   const actual=row.scenes[i],expected=story.scenes[i];
   if(!actual)continue;
   if(actual.scene!==i+1||actual.title!==expected.title)errors.push(key+': scene/title differs at '+(i+1));
   if(!actual.description?.trim())errors.push(key+': missing map description at '+(i+1));
   const options=expected.switch?.options?.length||0;
   if(actual.switches!==options)errors.push(key+': incomplete options at '+(i+1));
   const files=['scene-'+(i+1)+'.png',...Array.from({length:options},(_,k)=>'scene-'+(i+1)+'-option-'+k+'.png')];
   for(const name of files){
    const file=path.join(dir,entry.id,String(width),name);
    if(!fs.existsSync(file)||fs.statSync(file).size<100)errors.push(key+': missing capture '+name);
    else screenshots++;
   }
   sceneViews++;optionViews+=options;
  }
 }
}
for(const key of rows.keys())if(!index.some(e=>key.startsWith(e.id+':')))errors.push(key+': unregistered result');
console.log(JSON.stringify({rendererHash,stories:index.length,viewportResults:rows.size,sceneViews,optionViews,screenshots,errors},null,2));
if(errors.length)process.exitCode=1;
