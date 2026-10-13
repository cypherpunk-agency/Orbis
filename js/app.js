(function(){
"use strict";
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const rad = Math.PI/180, deg = 180/Math.PI, R_EARTH = 6371;
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));

// ---------- geometry ----------
const feats = topojson.feature(WORLD, WORLD.objects.countries).features;
const byId = new Map(feats.map(f=>[f.id,f]));
const borders = topojson.mesh(WORLD, WORLD.objects.countries,(a,b)=>a!==b);
const SPHERE={type:"Sphere"}, GRAT=d3.geoGraticule10();
// political tints: greedy colouring so neighbours differ
const nb = topojson.neighbors(WORLD.objects.countries.geometries);
const tint = new Array(feats.length).fill(0);
feats.map((f,i)=>i).sort((a,b)=>nb[b].length-nb[a].length).forEach(i=>{
  const used=new Set(nb[i].map(j=>tint[j]));let k=0;while(used.has(k))k++;tint[i]=k%5;});

// ---------- colours ----------
let C={};
function readColors(){
  const cs=getComputedStyle(document.documentElement);
  ["ocean","land","border","grat","ink","halo","accent","c1","c2","c3","c4","c5","muted","nodata","rim","t0","t1","t2","t3","t4","s0","s1","s2","s3"].forEach(k=>C[k]=cs.getPropertyValue("--"+k).trim());
  C.tints=[C.t0,C.t1,C.t2,C.t3,C.t4];
  C.seq=d3.interpolateRgbBasis([C.s0,C.s1,C.s2,C.s3]);
}
const col = c => !c ? C.accent : (C[c] || c);

// ---------- projections ----------
const RAW = {
  globe: d3.geoOrthographicRaw,
  equal: d3.geoEqualEarthRaw,
  mercator: Object.assign((l,p)=>d3.geoMercatorRaw(l,clamp(p,-1.4835,1.4835)),{invert:d3.geoMercatorRaw.invert})
};
const BOUNDS={};
["equal","mercator"].forEach(k=>{let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9;
  for(let l=-180;l<=180;l+=4)for(let p=-90;p<=90;p+=2){const v=RAW[k](l*rad,p*rad);x0=Math.min(x0,v[0]);x1=Math.max(x1,v[0]);y0=Math.min(y0,v[1]);y1=Math.max(y1,v[1]);}
  BOUNDS[k]=[x1-x0,y1-y0];});
const S={globe:1,equal:1,mercator:1};
const F={x:0,y:0,w:100,h:100};

const mutator = d3.geoProjectionMutator((a,b,t)=>{
  const A=RAW[a],B=RAW[b],sa=S[a],sb=S[b];
  const f=(l,p)=>{const u=A(l,p),v=B(l,p);return [u[0]*sa*(1-t)+v[0]*sb*t, u[1]*sa*(1-t)+v[1]*sb*t];};
  const k=t<=0?a:(t>=1?b:null);
  if(k&&RAW[k].invert){const s=S[k];f.invert=(x,y)=>RAW[k].invert(x/s,y/s);}
  return f;
});
const proj = mutator("globe","globe",0);
const V={a:"globe",b:"globe",t:0,center:[10,30],zoom:1};
const wGlobe=()=>(V.a==="globe"?1-V.t:0)+(V.b==="globe"?V.t:0);
const curKind=()=>V.t<0.5?V.a:V.b;

function update(){
  mutator(V.a,V.b,V.t);
  const wg=wGlobe(), c=V.center;
  proj.scale(V.zoom).rotate([-c[0],-c[1]*wg,0]).translate([0,0]).precision(0.35);
  if(wg>0.001) proj.clipAngle(90+(1-wg)*89.4); else proj.clipAngle(null);
  const p=proj(c)||[0,0];
  proj.translate([F.x+F.w/2-p[0],F.y+F.h/2-p[1]]);
}

// ---------- canvas ----------
const canvas=document.getElementById("map"), ctx=canvas.getContext("2d");
const path=d3.geoPath(proj,ctx);
let W=0,H=0,DPR=1;
const sheet=document.getElementById("sheet"), topbar=document.getElementById("topbar"), toc=document.getElementById("toc");
function layout(){
  W=innerWidth;H=innerHeight;DPR=Math.min(2,devicePixelRatio||1);
  canvas.width=W*DPR;canvas.height=H*DPR;canvas.style.width=W+"px";canvas.style.height=H+"px";
  const tb=topbar.getBoundingClientRect(), sh=sheet.getBoundingClientRect();
  const desktop=W>=820;
  if(desktop){F.x=sh.right+8;F.y=tb.bottom;F.w=W-F.x-8;F.h=H-F.y-8;}
  else{const tc=toc.hidden?null:toc.getBoundingClientRect(); F.x=0;F.y=tb.bottom;F.w=W;F.h=Math.max(160,(tc?tc.top:sh.top)-F.y);}
  S.globe=Math.min(F.w,F.h)/2*0.9;
  ["equal","mercator"].forEach(k=>S[k]=Math.min(F.w/BOUNDS[k][0],F.h/BOUNDS[k][1])*0.96);
  render();
}

// ---------- active scene ----------
let scene=null, frame=null; // frame = timeline overlay
function arr(v,kind){ if(!v) return []; if(typeof v==="string") return resolveRef(v); return v; }
function routePath(r){ let p=typeof r.path==="string"?resolveRef(r.path):r.path; if(r.until!=null) p=p.slice(0,r.until+1); return p; }
function layers(){
  const s=scene||{};
  const L={fills:{},groups:[],choro:null,routes:[],points:[],circles:[],highlight:s.highlight||[]};
  Object.assign(L.fills,s.fills||{});
  L.groups=(s.groups||[]).slice();
  if(s.choro) L.choro=s.choro;
  L.routes=arr(s.routes).slice(); L.points=arr(s.points).slice(); L.circles=(s.circles||[]).slice();
  if(frame){ if(frame.groups)L.groups=L.groups.concat(frame.groups); if(frame.routes)L.routes=L.routes.concat(frame.routes);
    if(frame.points)L.points=L.points.concat(frame.points); if(frame.fills)Object.assign(L.fills,frame.fills); }
  if(explore.bloc){const b=BLOCS[explore.bloc];L.groups.push({label:b.label,color:"c2",ids:b.ids});}
  L.political = scene ? !!s.political : !explore.bloc;
  L.gmap=new Map(); L.groups.forEach(g=>g.ids.forEach(id=>L.gmap.set(id,g)));
  if(L.choro){const d=DATA[L.choro.data],vals=Object.values(d);
    const lo=d3.min(vals),hi=d3.max(vals);
    const sc=L.choro.log?d3.scaleLog().domain([Math.max(lo,0.1),hi]):d3.scaleLinear().domain([lo,hi]);
    L.color=v=>{let t=clamp(sc(Math.max(v,0.1)),0,1); if(L.choro.reverse)t=1-t; return C.seq(t);};
    L.cdata=d;L.lo=lo;L.hi=hi;}
  return L;
}
let L=null;
function fillFor(f,i){
  const id=f.id;
  if(L.fills[id]) return col(L.fills[id]);
  const g=L.gmap.get(id); if(g) return col(g.color);
  if(L.choro){const v=L.cdata[id]; return v==null?C.nodata:L.color(v);}
  if(L.political) return C.tints[tint[i]];
  return C.land;
}

// ---------- drawing ----------
let tNow=0;
function visible(at){ return wGlobe()<0.5 || d3.geoDistance(at,V.center)<Math.PI/2-0.02; }
function label(text,x,y,opts={}){
  ctx.font=(opts.size||13)+"px 'Barlow Semi Condensed', 'Arial Narrow', sans-serif";
  ctx.textAlign=opts.align||"left";ctx.textBaseline="middle";
  ctx.lineJoin="round";ctx.lineWidth=4;ctx.strokeStyle=C.halo;ctx.strokeText(text,x,y);
  ctx.fillStyle=opts.color||C.ink;ctx.fillText(text,x,y);
}
function km(p){let d=0;for(let i=1;i<p.length;i++)d+=d3.geoDistance(p[i-1],p[i]);return d*R_EARTH;}
function draw(){
  update(); L=layers();
  ctx.setTransform(DPR,0,0,DPR,0,0); ctx.clearRect(0,0,W,H);
  ctx.beginPath();path(SPHERE);ctx.fillStyle=C.ocean;ctx.fill();
  ctx.beginPath();path(GRAT);ctx.strokeStyle=C.grat;ctx.lineWidth=0.6;ctx.stroke();
  for(let i=0;i<feats.length;i++){ctx.beginPath();path(feats[i]);ctx.fillStyle=fillFor(feats[i],i);ctx.fill();}
  ctx.beginPath();path(borders);ctx.strokeStyle=C.border;ctx.lineWidth=0.6;ctx.stroke();
  if(L.highlight.length){ctx.beginPath();L.highlight.forEach(id=>{const f=byId.get(id);if(f)path(f);});ctx.strokeStyle=C.ink;ctx.lineWidth=1.6;ctx.stroke();}
  // circles
  L.circles.forEach(c=>{const g=d3.geoCircle().center(c.center).radius(c.km/R_EARTH*deg).precision(1)();
    ctx.beginPath();path(g);ctx.globalAlpha=0.22;ctx.fillStyle=col(c.color);ctx.fill();ctx.globalAlpha=1;
    ctx.setLineDash([5,4]);ctx.lineWidth=2;ctx.strokeStyle=col(c.color);ctx.stroke();ctx.setLineDash([]);
    if(c.label){const la=c.labelAt||[c.center[0],c.center[1]-c.km/R_EARTH*deg*0.55]; const p=proj(la); if(p&&visible(la))label(c.label,p[0],p[1],{align:"center",color:col(c.color),size:14});}
  });
  // routes
  const labels=[];
  L.routes.forEach(r=>{const p=routePath(r); if(!p||p.length<2) return;
    const line={type:"LineString",coordinates:p};
    ctx.beginPath();path(line);ctx.strokeStyle=col(r.color);ctx.lineWidth=r.width||2;ctx.lineCap="round";
    if(r.dash)ctx.setLineDash([3,5]);
    ctx.globalAlpha=r.flow?0.45:0.9;ctx.stroke();ctx.globalAlpha=1;ctx.setLineDash([]);
    if(r.flow&&!reduce){ctx.beginPath();path(line);ctx.setLineDash([3,11]);ctx.lineDashOffset=-(tNow/45)%14;ctx.lineWidth=(r.width||2)+0.6;ctx.stroke();ctx.setLineDash([]);}
    if(r.label||r.dist){
      const at=r.labelAt!=null?p[r.labelAt]:p.length>2?p[Math.floor(p.length/2)]:d3.geoInterpolate(p[0],p[1])(0.5);
      if(visible(at)){const xy=proj(at); if(xy){let t=(r.label||"")+(r.dist?(r.label?": ":"")+"≈ "+d3.format(",")(Math.round(km(p)/100)*100)+" km":""); labels.push([t,xy[0]+6,xy[1]-10,{color:col(r.color),size:13}]);}}}
  });
  // points
  L.points.forEach(pt=>{ if(!visible(pt.at)) return; const xy=proj(pt.at); if(!xy) return;
    ctx.beginPath();ctx.arc(xy[0],xy[1],pt.r||4,0,2*Math.PI);ctx.fillStyle=col(pt.color||"c1");ctx.fill();ctx.lineWidth=1.5;ctx.strokeStyle=C.halo;ctx.stroke();
    if(pt.label) labels.push([pt.label,xy[0]+(pt.r||4)+5,xy[1],{size:13}]);
  });
  labels.forEach(l=>label(...l));
  // rim
  ctx.beginPath();path(SPHERE);ctx.strokeStyle=C.rim;ctx.lineWidth=1;ctx.stroke();
}

// ---------- animation loop ----------
let anim=null, spin=false, raf=null, last=0;
function hasFlow(){return !reduce && L && L.routes.some(r=>r.flow);}
function render(){ if(!raf) raf=requestAnimationFrame(tick); }
function tick(now){
  raf=null; const dt=last?Math.min(50,now-last):16; last=now; tNow=now; let more=false;
  if(anim){const e=Math.min(1,(now-anim.start)/anim.dur);anim.step(d3.easeCubicInOut(e)); if(e>=1){anim.end();anim=null;}else more=true;}
  else if(spin&&!drag){V.center=[V.center[0]+dt*0.006,V.center[1]];more=true;}
  draw();
  if(more||hasFlow()) render(); else last=0;
}
function flyTo(t,dur=1600){
  const k0=curKind(), k1=t.mode, c0=V.center.slice(), z0=V.zoom, z1=t.zoom||1;
  V.a=k0;V.b=k1;V.t=0;
  const gi=d3.geoInterpolate(c0,t.center), dist=d3.geoDistance(c0,t.center);
  if(reduce) dur=1;
  const dip=Math.min(1,dist/1.2)*(Math.max(z0,z1)>1.5?0.45:0.2);
  anim={start:performance.now(),dur,
    step(e){V.center=gi(e);V.zoom=Math.exp(Math.log(z0)*(1-e)+Math.log(z1)*e)*(1-dip*Math.sin(Math.PI*e));V.t=k0===k1?0:e;},
    end(){V.a=V.b=k1;V.t=0;V.center=t.center.slice();V.zoom=z1;}};
  render();
}
function settle(){ if(anim){anim=null;} const k=curKind(); V.a=V.b=k;V.t=0; }

// ---------- interaction ----------
const ptrs=new Map(); let drag=null;
canvas.addEventListener("pointerdown",e=>{canvas.setPointerCapture(e.pointerId);ptrs.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(ptrs.size===1)drag={x0:e.clientX,y0:e.clientY,moved:false};
  else if(ptrs.size===2&&drag){const [p,q]=[...ptrs.values()];drag.pinch={d:Math.hypot(p.x-q.x,p.y-q.y),z:V.zoom};drag.moved=true;}
  spin=false;hideTip();});
canvas.addEventListener("pointermove",e=>{const pr=ptrs.get(e.pointerId); if(!pr||!drag) return;
  const dx=e.clientX-pr.x, dy=e.clientY-pr.y; ptrs.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(ptrs.size===1){ if(Math.hypot(e.clientX-drag.x0,e.clientY-drag.y0)>5) drag.moved=true;
    if(drag.moved){settle();const s=S[curKind()]*V.zoom;const k=deg/s*(curKind()==="equal"?1.15:1);
      V.center=[V.center[0]-dx*k, clamp(V.center[1]+dy*k,-85,85)];render();}}
  else if(ptrs.size===2&&drag.pinch){const [p,q]=[...ptrs.values()];settle();V.zoom=clamp(drag.pinch.z*Math.hypot(p.x-q.x,p.y-q.y)/drag.pinch.d,0.6,24);render();}
});
function endPtr(e){ if(!ptrs.has(e.pointerId)) return; ptrs.delete(e.pointerId);
  if(ptrs.size===0){ if(drag&&!drag.moved) tap(e.clientX,e.clientY); drag=null; render(); } }
canvas.addEventListener("pointerup",endPtr);canvas.addEventListener("pointercancel",endPtr);
canvas.addEventListener("wheel",e=>{e.preventDefault();settle();spin=false;V.zoom=clamp(V.zoom*Math.exp(-e.deltaY*0.0015),0.6,24);render();},{passive:false});
document.getElementById("zin").onclick=()=>{settle();V.zoom=clamp(V.zoom*1.5,0.6,24);render();};
document.getElementById("zout").onclick=()=>{settle();V.zoom=clamp(V.zoom/1.5,0.6,24);render();};

const tip=document.getElementById("tip"); let tipTimer=null;
function hideTip(){tip.hidden=true;}
function tap(x,y){
  if(V.t!==0||!proj.invert) return;
  const ll=proj.invert([x,y]); if(!ll||isNaN(ll[0])) return;
  if(curKind()==="globe"&&d3.geoDistance(ll,V.center)>Math.PI/2) return;
  const f=feats.find(f=>d3.geoContains(f,ll)); if(!f){hideTip();return;}
  let html="<b>"+esc(f.properties.name)+"</b>";
  if(L.choro){const v=L.cdata[f.id]; html+="<span>"+(v==null?"No data":esc(String(L.choro.fmt?L.choro.fmt(v):v)))+"</span>";}
  const g=L.gmap.get(f.id); if(g) html+="<span>"+esc(g.label)+"</span>";
  tip.innerHTML=html; tip.hidden=false;
  tip.style.left=clamp(x,70,W-70)+"px"; tip.style.top=Math.max(70,y-14)+"px";
  clearTimeout(tipTimer); tipTimer=setTimeout(hideTip,3500);
}
const esc=s=>s.replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

// ---------- mode toggle ----------
const modeBtns=[...document.querySelectorAll("[data-mode]")];
function syncMode(k){modeBtns.forEach(b=>b.setAttribute("aria-pressed",String((b.dataset.mode==="globe")===(k==="globe"))));}
modeBtns.forEach(b=>b.onclick=()=>{const want=b.dataset.mode; const k=curKind();
  if((want==="globe")===(k==="globe")) return;
  const flat=(scene&&scene.view.mode!=="globe"?scene.view.mode:(scene&&scene.flat)||"equal");
  const target={mode:want==="globe"?"globe":flat,center:[V.center[0],want==="globe"?V.center[1]:clamp(V.center[1],-30,50)],zoom:V.zoom};
  syncMode(target.mode);flyTo(target,1400);});

// ---------- panel ----------
const $=id=>document.getElementById(id);
const el={kicker:$("sKicker"),title:$("sTitle"),text:$("sText"),legend:$("sLegend"),tl:$("sTimeline"),slider:$("tlSlider"),year:$("tlYear"),play:$("tlPlay"),cap:$("tlCaption"),
  prev:$("prev"),next:$("next"),dots:$("dots"),notes:$("sNotes"),notesBody:$("sNotesBody"),blocs:$("blocs"),steps:$("steps")};
let si=-1, ci=0, tlIdx=0, playing=null;
const explore={bloc:null};

function legendHTML(){
  const s=scene; if(!s){ if(explore.bloc) return chip("c2",BLOCS[explore.bloc].label); return ""; }
  let h="";
  if(s.legend) h+=s.legend.map(l=>chip(l.color,l.label)).join("");
  else if(L&&L.groups.length) h+=L.groups.map(g=>chip(g.color,g.label)).join("");
  if(s.choro){const stops=d3.range(0,1.01,0.1).map(t=>C.seq(s.choro.reverse?1-t:t)).join(",");
    const d=DATA[s.choro.data],v=Object.values(d),f=s.choro.fmt||(x=>x);
    h+=`<div class="ramp"><div class="ramp-title">${esc(s.choro.title)}</div><div class="ramp-bar" style="background:linear-gradient(90deg,${stops})"></div><div class="ramp-ends"><span>${esc(String(f(d3.min(v))))}</span><span>${esc(String(f(d3.max(v))))}</span></div><div class="ramp-na"><i style="background:${C.nodata}"></i>${s.choro.data==="POWER"?"Near-universal access":"No data"}</div></div>`;}
  return h;
}
function chip(c,t){return `<span class="chip"><i style="background:${col(c)}"></i>${esc(t)}</span>`;}

function setFrame(){
  const t=scene&&scene.timeline; if(!t){frame=null;return;}
  const y=t.years[tlIdx]; frame=t.frame(y,tlIdx); el.year.textContent=t.label(y); el.slider.value=tlIdx;
  el.slider.setAttribute("aria-valuetext",String(t.label(y)));
  el.cap.textContent=frame.caption||""; el.cap.hidden=!frame.caption;
  L=layers(); el.legend.innerHTML=legendHTML(); render();
}
function stopPlay(){ if(playing){clearInterval(playing);playing=null;} el.play.textContent="Play"; el.play.setAttribute("aria-label","Play timeline"); }
el.play.onclick=()=>{ if(playing){stopPlay();return;} const t=scene.timeline; if(tlIdx>=t.years.length-1) tlIdx=0;
  el.play.textContent="Pause"; el.play.setAttribute("aria-label","Pause timeline");
  playing=setInterval(()=>{ if(tlIdx>=t.years.length-1){stopPlay();return;} tlIdx++; setFrame(); }, t.years.length>30?(reduce?400:160):(reduce?1600:1100)); };
el.slider.oninput=()=>{stopPlay();tlIdx=+el.slider.value;setFrame();};

function showScene(i, fly=true){
  const st=STORIES[si]; ci=clamp(i,0,st.scenes.length-1); scene=st.scenes[ci]; stopPlay();
  el.kicker.textContent=st.title; el.title.textContent=scene.title; el.text.textContent=scene.text;
  el.blocs.hidden=true; el.steps.hidden=false; el.notes.hidden=false;
  if(scene.timeline){el.tl.hidden=false;tlIdx=scene.timeline.start||0;el.slider.max=scene.timeline.years.length-1;}
  else el.tl.hidden=true;
  frame=null; setFrame(); L=layers(); el.legend.innerHTML=legendHTML();
  el.dots.innerHTML=st.scenes.map((s,j)=>`<button class="dot" aria-label="Scene ${j+1}: ${esc(s.title)}" ${j===ci?'aria-current="step"':""}></button>`).join("");
  [...el.dots.children].forEach((b,j)=>b.onclick=()=>showScene(j));
  el.prev.disabled=ci===0 && si===0;
  el.prev.textContent=ci===0?"Previous story":"Back";
  const lastS=ci===st.scenes.length-1; el.next.textContent=lastS?(si<STORIES.length-1?"Next story":"All stories"):"Next";
  el.notesBody.textContent=st.notes; el.notes.open=false;
  history.replaceState(null,"","#"+st.id+"/"+(ci+1));
  syncMode(scene.view.mode); spin=false;
  if(fly) flyTo(scene.view);
  sheet.scrollTop=0; render();
}
el.next.onclick=()=>{ const st=STORIES[si]; if(ci<st.scenes.length-1) showScene(ci+1); else if(si<STORIES.length-1) openStory(si+1); else openToc(); };
el.prev.onclick=()=>{ if(ci>0) showScene(ci-1); else if(si>0){ openStory(si-1); showScene(STORIES[si].scenes.length-1);} };

function openStory(i, scn=0){ si=i; closeToc(); sheet.classList.remove("collapsed"); showScene(scn); }
function openExplore(){
  si=-1; scene=null; frame=null; closeToc(); stopPlay(); sheet.classList.remove("collapsed");
  el.kicker.textContent="Explore"; el.title.textContent="The political map";
  el.text.textContent="Drag to turn the world, pinch or scroll to zoom, tap a country to see its name. Show a group of countries:";
  el.tl.hidden=true; el.steps.hidden=true; el.notes.hidden=true; el.blocs.hidden=false;
  renderBlocs(); el.legend.innerHTML=legendHTML(); history.replaceState(null,"","#explore");
  syncMode(curKind()); render();
}
function renderBlocs(){
  el.blocs.innerHTML=[["",{label:"None"}],...Object.entries(BLOCS)].map(([k,b])=>`<button class="bloc" data-k="${k}" aria-pressed="${String((explore.bloc||"")===k)}">${esc(b.label)}</button>`).join("");
  [...el.blocs.children].forEach(b=>b.onclick=()=>{explore.bloc=b.dataset.k||null;renderBlocs();L=layers();el.legend.innerHTML=legendHTML();render();});
}

// ---------- table of contents ----------
const tocList=$("tocList");
const CATS=["Geopolitics","Economics","Statistics","People"];
tocList.innerHTML=CATS.map(cat=>`<section class="toc-cat"><h2>${cat}</h2><ul>`+
  STORIES.map((s,i)=>[s,i]).filter(([s])=>s.cat===cat).map(([s,i])=>`<li><button class="toc-story" data-i="${i}"><span class="toc-title">${esc(s.title)}</span><span class="toc-hook">${esc(s.hook)}</span></button></li>`).join("")+`</ul></section>`).join("");
[...tocList.querySelectorAll(".toc-story")].forEach(b=>b.onclick=()=>openStory(+b.dataset.i));
$("exploreBtn").onclick=openExplore;
$("tocBtn").onclick=()=>toc.hidden?openToc():closeToc();
$("tocClose").onclick=closeToc;
function openToc(focus=true){ toc.hidden=false; layout(); $("tocBtn").setAttribute("aria-expanded","true"); stopPlay();
  if(!reduce){ spin=true; if(curKind()!=="globe"||V.zoom>1.4) flyTo({mode:"globe",center:[V.center[0],20],zoom:1}); } render(); if(focus) $("exploreBtn").focus({preventScroll:true}); }
function closeToc(){ toc.hidden=true; $("tocBtn").setAttribute("aria-expanded","false"); spin=false; layout(); }

// collapse sheet
$("collapse").onclick=()=>{ sheet.classList.toggle("collapsed"); $("collapse").setAttribute("aria-expanded",String(!sheet.classList.contains("collapsed"))); requestAnimationFrame(layout); };

document.addEventListener("keydown",e=>{
  if(e.target.tagName==="INPUT") return;
  if(!toc.hidden){ if(e.key==="Escape") closeToc(); return; }
  if(si<0) return;
  if(e.key==="ArrowRight") el.next.click(); else if(e.key==="ArrowLeft"&&!el.prev.disabled) el.prev.click();
});

// ---------- boot ----------
readColors();
matchMedia("(prefers-color-scheme: dark)").addEventListener("change",()=>{readColors();if(scene||si<0)el.legend.innerHTML=legendHTML();render();});
new ResizeObserver(()=>layout()).observe(sheet);
addEventListener("resize",layout);
document.fonts && document.fonts.ready.then(render);
layout();
const h=location.hash.slice(1).split("/"); const idx=STORIES.findIndex(s=>s.id===h[0]);
if(idx>=0) openStory(idx, clamp((+h[1]||1)-1,0,STORIES[idx].scenes.length-1));
else if(h[0]==="explore") openExplore();
else { openExplore(); openToc(false); }
})();
