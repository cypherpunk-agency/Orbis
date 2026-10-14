// Structural release gate for the frozen M1–M8 scope. This does not prove
// historical accuracy or visual quality; those need the acceptance evidence.
// Usage: node tools/check-roadmap.mjs [M1 M2 ...]
import fs from 'fs';
import path from 'path';
const read=file=>JSON.parse(fs.readFileSync(file,'utf8'));
const scope=read('docs/ROADMAP-SCOPE.json'),index=read('stories/index.json'),campaigns=read('stories/campaigns.json');
const selected=process.argv.slice(2),want=m=>!selected.length||selected.includes(m);
const expected=[];
if(want('M1'))expected.push(...scope.phaseAStoryIds);
const errors=[];
for(const cp of scope.campaigns.filter(x=>/^M[2-8]$/.test(x.milestone)&&want(x.milestone))) {
  const ids=cp.chapters.map(x=>x.id);expected.push(...ids);
  const actual=campaigns.filter(x=>x.id===cp.id);
  if(actual.length!==1)errors.push(cp.id+': expected exactly one registered campaign');
  else if(JSON.stringify(actual[0].chapters)!==JSON.stringify(ids))errors.push(cp.id+': chapter order differs from frozen scope');
}
const ids=[...new Set(expected)];let scenes=0,datasets=0;
for(const id of ids) {
  const entries=index.filter(x=>x.id===id);
  if(entries.length!==1){errors.push(id+': expected exactly one index entry');continue;}
  const file=entries[0].file;
  if(!fs.existsSync(file)){errors.push(id+': missing story file');continue;}
  const st=read(file);
  if(st.id!==id)errors.push(id+': file/index ID mismatch');
  if(!st.notes?.trim())errors.push(id+': missing source notes');
  if(!scope.phaseAStoryIds.includes(id)&&(st.scenes.length<4||st.scenes.length>8))errors.push(id+': requires 4–8 substantive scenes');
  scenes+=st.scenes.length;
  for(const [i,sc] of st.scenes.entries()) {
    if(!sc.title||!sc.text||!sc.view?.center||!Number.isFinite(sc.view.zoom))errors.push(id+': scene '+(i+1)+' lacks title/text/camera');
    if(sc.timeline) {
      const years=sc.timeline.years;
      if(!Array.isArray(years)||!years.length||years.some(x=>!Number.isFinite(x))||years.some((x,j)=>j&&x<=years[j-1]))errors.push(id+': scene '+(i+1)+' malformed/unsorted timeline');
    }
    for(const ly of sc.layers||[]) {
      const options=sc.switch?.options||[{}];
      for(const option of options) {
        const alias=String(ly.data).replace(/\{(\w+)\}/g,(match,key)=>option[key]??match);
        if(!Object.hasOwn(st.data||{},alias))errors.push(id+': undeclared layer data '+alias);
      }
    }
  }
  for(const file of Object.values(st.data||{})) {
    if(typeof file!=='string'||!fs.existsSync(file)){errors.push(id+': missing dataset '+file);continue;}
    if(path.extname(file)!=='.json')continue;
    const data=read(file);datasets++;
    if(!data.source||!data.asOf)errors.push(id+': dataset lacks source/asOf '+file);
    if(fs.statSync(file).size>=1_000_000)errors.push(id+': dataset exceeds 1 MB '+file);
  }
}
console.log(JSON.stringify({milestones:selected.length?selected:['M1','M2','M3','M4','M5','M6','M7','M8'],stories:ids.length,scenes,datasetReferences:datasets,errors},null,2));
if(errors.length)process.exitCode=1;
