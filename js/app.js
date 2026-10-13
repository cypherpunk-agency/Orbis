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
// representative point per country (centroid of its largest polygon); small states the 1:110m map lacks are added by hand
const ANCHOR=new Map(), NAMES=new Map();
feats.forEach(f=>{ let g=f.geometry;
  if(g.type==="MultiPolygon"){ let best=null,ba=-1; g.coordinates.forEach(c=>{const q={type:"Polygon",coordinates:c},a=d3.geoArea(q); if(a>ba){ba=a;best=q;}}); g=best; }
  ANCHOR.set(f.id,d3.geoCentroid(g)); NAMES.set(f.id,f.properties.name); });
[["SGP","Singapore",103.82,1.35],["BHR","Bahrain",50.55,26.07],["MLT","Malta",14.4,35.9],["HKG","Hong Kong",114.17,22.32],["MAC","Macao",113.55,22.19],
 ["GIB","Gibraltar",-5.35,36.14],["MUS","Mauritius",57.55,-20.2],["MDV","Maldives",73.5,4.2],["BRB","Barbados",-59.55,13.17],["CUW","Curaçao",-68.95,12.17],
 ["ABW","Aruba",-69.97,12.52],["BMU","Bermuda",-64.75,32.3],["SYC","Seychelles",55.45,-4.6],["CPV","Cabo Verde",-23.6,15.1],["AND","Andorra",1.55,42.55],
 ["LIE","Liechtenstein",9.55,47.15],["ATG","Antigua and Barbuda",-61.8,17.1],["KNA","Saint Kitts and Nevis",-62.75,17.3],["LCA","Saint Lucia",-60.97,13.9],
 ["GRD","Grenada",-61.68,12.12],["TON","Tonga",-175.2,-21.2],["WSM","Samoa",-172.1,-13.8],["COM","Comoros",43.3,-11.7],["STP","São Tomé and Príncipe",6.6,0.3]]
 .forEach(([id,n,x,y])=>{ if(!ANCHOR.has(id)){ANCHOR.set(id,[x,y]);NAMES.set(id,n);} });
// where a centroid misleads (Russia's lies in Siberia, far from its export ports and population), anchor by hand
Object.entries({RUS:[44,56]}).forEach(([k,v])=>ANCHOR.set(k,v));
const nameOf=id=>NAMES.get(id)||id;
const AREA=new Map(feats.map(f=>[f.id,d3.geoArea(f)]));
// political tints: greedy colouring so neighbours differ
const nb = topojson.neighbors(WORLD.objects.countries.geometries);
const tint = new Array(feats.length).fill(0);
feats.map((f,i)=>i).sort((a,b)=>nb[b].length-nb[a].length).forEach(i=>{
  const used=new Set(nb[i].map(j=>tint[j]));let k=0;while(used.has(k))k++;tint[i]=k%5;});

// ---------- colours ----------
let C={};
function readColors(){
  const cs=getComputedStyle(document.documentElement);
  ["ocean","land","border","grat","ink","halo","accent","paper","c1","c2","c3","c4","c5","muted","nodata","rim","t0","t1","t2","t3","t4","s0","s1","s2","s3"].forEach(k=>C[k]=cs.getPropertyValue("--"+k).trim());
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
  const L={fills:{},groups:[],choro:null,routes:[],points:[],circles:[],highlight:s.highlight||[],symbols:[],flows:[],vals:[],sizeKey:null,flowKeys:[],spikes:[],spikeKey:null,carto:null};
  Object.assign(L.fills,s.fills||{});
  L.groups=(s.groups||[]).slice();
  if(s.choro) L.choro=s.choro;
  L.routes=arr(s.routes).slice(); L.points=arr(s.points).slice(); L.circles=(s.circles||[]).slice();
  if(frame){ if(frame.groups)L.groups=L.groups.concat(frame.groups); if(frame.routes)L.routes=L.routes.concat(frame.routes);
    if(frame.points)L.points=L.points.concat(frame.points); if(frame.fills)Object.assign(L.fills,frame.fills); }
  if(explore.bloc){const b=BLOCS[explore.bloc];L.groups.push({label:b.label,color:"c2",ids:b.ids});}
  L.political = scene ? !!s.political : !explore.bloc;
  L.gmap=new Map(); L.groups.forEach(g=>g.ids.forEach(id=>L.gmap.set(id,g)));
  compileLayers(s,L);
  if(L.choro){const d=L.choro.values||DATA[L.choro.data],vals=Object.values(d);
    const lo=d3.min(vals),hi=d3.max(vals);
    const sc=L.choro.log?d3.scaleLog().domain([Math.max(lo,0.1),hi]):d3.scaleLinear().domain([lo,hi]);
    L.color=v=>{let t=clamp(sc(Math.max(v,0.1)),0,1); if(L.choro.reverse)t=1-t; return C.seq(t);};
    L.cdata=d;L.lo=lo;L.hi=hi;}
  return L;
}
let L=null;
function fillFor(f,i,ras){
  const id=f.id;
  if(L.fills[id]) return col(L.fills[id]);
  const g=L.gmap.get(id); if(g) return col(g.color);
  if(L.choro){const v=L.cdata[id]; return v==null?(ras?null:C.nodata):L.color(v);}
  if(ras) return null;
  if(L.political) return C.tints[tint[i]];
  return C.land;
}

// ---------- drawing ----------
let tNow=0;
function visible(at){ return wGlobe()<0.5 || d3.geoDistance(at,V.center)<Math.PI/2-0.02; }
let onDark=false, placed=[];
function label(text,x,y,opts={}){
  const size=opts.size||13;
  ctx.font=size+"px 'Barlow Semi Condensed', 'Arial Narrow', sans-serif";
  ctx.textAlign=opts.align||"left";ctx.textBaseline="middle";
  // skip labels that would overlap one already drawn (earlier labels have priority)
  const w=ctx.measureText(text).width, x0=opts.align==="center"?x-w/2:x, r=[x0-2,y-size/2-2,x0+w+2,y+size/2+2];
  if(!opts.force && placed.some(q=>r[0]<q[2]&&r[2]>q[0]&&r[1]<q[3]&&r[3]>q[1])) return;
  placed.push(r);
  ctx.lineJoin="round";ctx.lineWidth=4;ctx.strokeStyle=onDark?"rgba(6,14,20,.85)":C.halo;ctx.strokeText(text,x,y);
  ctx.fillStyle=onDark&&(!opts.color||opts.color===C.ink)?"#F2F5F6":(opts.color||C.ink);ctx.fillText(text,x,y);
}
function km(p){let d=0;for(let i=1;i<p.length;i++)d+=d3.geoDistance(p[i-1],p[i]);return d*R_EARTH;}
function drawRaster(){
  const m=BM.mode, b=BASEMAPS[m];
  if(!b.tex||!Raster.ok){ if(rasterOn){Raster.clear();rasterOn=false;} return false; }
  if(!Raster.has(m)){ Raster.load(m,b.tex,render); if(rasterOn){Raster.clear();rasterOn=false;} return false; }
  const wg=wGlobe(), c=V.center;
  rasterOn=Raster.draw({name:m,a:V.a,b:V.b,t:V.t,sa:S[V.a],sb:S[V.b],k:V.zoom,tr:proj.translate(),
    rot:[-c[0]*rad,-c[1]*wg*rad],clip:wg>0.001?90+(1-wg)*89.4:null,W,H,dpr:DPR});
  return rasterOn;
}
let rasterOn=false;
function draw(){
  update(); L=layers();
  const ras=drawRaster(); onDark=ras; placed=[];
  ctx.setTransform(DPR,0,0,DPR,0,0); ctx.clearRect(0,0,W,H);
  if(!ras){ctx.beginPath();path(SPHERE);ctx.fillStyle=C.ocean;ctx.fill();}
  ctx.beginPath();path(GRAT);ctx.strokeStyle=ras?"rgba(255,255,255,.10)":C.grat;ctx.lineWidth=0.6;ctx.stroke();
  if(L.carto) drawCartogram(ras);
  else{
    if(ras) ctx.globalAlpha=0.72;
    for(let i=0;i<feats.length;i++){const fc=fillFor(feats[i],i,ras); if(!fc) continue; ctx.beginPath();path(feats[i]);ctx.fillStyle=fc;ctx.fill();}
    ctx.globalAlpha=1;
    ctx.beginPath();path(borders);ctx.strokeStyle=ras?"rgba(240,245,248,.42)":C.border;ctx.lineWidth=ras?0.7:0.6;ctx.stroke();
  }
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
  // flows: great-circle arcs, width by value, dashes moving from exporter to importer
  L.flows.forEach(fl=>{ const line={type:"LineString",coordinates:fl.path};
    ctx.beginPath();path(line);ctx.strokeStyle=col(fl.color);ctx.lineWidth=fl.width;ctx.lineCap="round";ctx.globalAlpha=ras?0.85:0.72;ctx.stroke();ctx.globalAlpha=1;
    // a thin light dash travelling along the line shows direction without hiding its width
    if(!reduce){ctx.beginPath();path(line);ctx.setLineDash([1.5,13]);ctx.lineDashOffset=-(tNow/40)%14.5;ctx.lineWidth=Math.min(1.6,fl.width*0.6);ctx.strokeStyle=C.paper;ctx.globalAlpha=0.9;ctx.stroke();ctx.setLineDash([]);ctx.globalAlpha=1;}
    if(visible(fl.to)){const q=proj(fl.to); if(q){ctx.beginPath();ctx.arc(q[0],q[1],2.6,0,2*Math.PI);ctx.fillStyle=col(fl.color);ctx.fill();}}
  });
  // proportional symbols (largest first, so small ones stay on top)
  L.symbols.forEach(sy=>{ if(!visible(sy.at)) return; const xy=proj(sy.at); if(!xy) return;
    ctx.beginPath();ctx.arc(xy[0],xy[1],sy.r,0,2*Math.PI);ctx.globalAlpha=0.5;ctx.fillStyle=col(sy.color);ctx.fill();ctx.globalAlpha=1;
    ctx.lineWidth=1.3;ctx.strokeStyle=col(sy.color);ctx.stroke();
    if(sy.label) labels.push([sy.label,xy[0]+Math.min(sy.r,14)+4,xy[1],{size:13}]);
  });
  // spikes: towers standing on the map, height proportional to value
  if(L.spikes.length){ const Rpx=Math.min(F.w,F.h)/2*V.zoom*0.9;
    L.spikes.filter(sp=>sp.h*Rpx>=2.5).map(sp=>({sp,b:visible(sp.at)&&proj(sp.at)})).filter(o=>o.b).sort((a,b)=>a.b[1]-b.b[1]).forEach(({sp,b})=>{
      const top=[b[0],b[1]-sp.h*Rpx], w=sp.w||7, c=col(sp.color);
      ctx.beginPath();ctx.ellipse(b[0],b[1],w*0.75,w*0.32,0,0,2*Math.PI);ctx.fillStyle="rgba(0,0,0,.18)";ctx.fill();
      ctx.lineCap="butt";ctx.beginPath();ctx.moveTo(b[0],b[1]);ctx.lineTo(top[0],top[1]);ctx.strokeStyle=c;ctx.lineWidth=w;ctx.stroke();
      ctx.beginPath();ctx.moveTo(b[0]-w*0.22,b[1]);ctx.lineTo(top[0]-w*0.22,top[1]);ctx.strokeStyle="rgba(255,255,255,.35)";ctx.lineWidth=w*0.3;ctx.stroke();
      ctx.beginPath();ctx.ellipse(top[0],top[1],w/2,w*0.22,0,0,2*Math.PI);ctx.fillStyle=c;ctx.fill();ctx.lineWidth=0.8;ctx.strokeStyle="rgba(255,255,255,.6)";ctx.stroke();
      ctx.lineCap="round";
      if(sp.label) labels.push([sp.label,top[0],top[1]-11,{size:13,align:"center"}]);
    }); }
  // points
  L.points.forEach(pt=>{ if(!visible(pt.at)) return; const xy=proj(pt.at); if(!xy) return;
    ctx.beginPath();ctx.arc(xy[0],xy[1],pt.r||4,0,2*Math.PI);ctx.fillStyle=col(pt.color||"c1");ctx.fill();ctx.lineWidth=1.5;ctx.strokeStyle=C.halo;ctx.stroke();
    if(pt.label) labels.push([pt.label,xy[0]+(pt.r||4)+5,xy[1],{size:13}]);
  });
  if(L._cartoLabels) labels.unshift(...L._cartoLabels);
  labels.forEach(l=>label(...l));
  // rim
  ctx.beginPath();path(SPHERE);ctx.strokeStyle=C.rim;ctx.lineWidth=1;ctx.stroke();
}

// ---------- cartogram ----------
let cartoStart=0;
const cartoEase=()=>reduce?1:d3.easeCubicInOut(clamp((performance.now()-cartoStart-900)/1500,0,1));
function drawCartogram(ras){
  const e=cartoEase();
  // the true map stays as a faint ghost so the distortion reads as a change
  ctx.beginPath(); feats.forEach(f=>path(f)); ctx.fillStyle=ras?"rgba(255,255,255,.12)":C.nodata; ctx.globalAlpha=0.7; ctx.fill(); ctx.globalAlpha=1;
  L.carto.items.forEach(it=>{ const a=ANCHOR.get(it.f.id); if(!a||!visible(a)) return; const p=proj(a); if(!p) return;
    const k=1+(it.k-1)*e;
    ctx.save(); ctx.translate(p[0],p[1]); ctx.scale(k,k); ctx.translate(-p[0],-p[1]);
    ctx.beginPath(); path(it.f); ctx.fillStyle=it.color; ctx.globalAlpha=0.9; ctx.fill(); ctx.globalAlpha=1;
    ctx.lineWidth=0.9/k; ctx.strokeStyle=C.paper; ctx.stroke(); ctx.restore();
    if(it.label&&e>0.98) L._cartoLabels.push([it.label,p[0],p[1],{align:"center",size:13}]);
  });
}

// ---------- animation loop ----------
let anim=null, spin=false, raf=null, last=0;
function hasFlow(){return !reduce && L && (L.flows.length>0 || L.routes.some(r=>r.flow));}
function render(){ if(!raf) raf=requestAnimationFrame(tick); }
function tick(now){
  raf=null; const dt=last?Math.min(50,now-last):16; last=now; tNow=now; let more=false;
  if(anim){const e=Math.min(1,(now-anim.start)/anim.dur);anim.step(d3.easeCubicInOut(e)); if(e>=1){anim.end();anim=null;}else more=true;}
  else if(spin&&!drag){V.center=[V.center[0]+dt*0.006,V.center[1]];more=true;}
  draw();
  if(L&&L.carto&&cartoEase()<1) more=true;
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
  L.vals.forEach(lv=>{const v=lv.values[f.id]; if(v!=null) html+="<span>"+esc(lv.title)+": "+esc(lv.fmt(v))+"</span>";});
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

// ---------- basemaps ----------
const BASEMAPS={
  political:{label:"Political"},
  satellite:{label:"Satellite",tex:"data/tex/satellite-4096.webp",source:"nasa-bluemarble"},
  night:{label:"Night lights",tex:"data/tex/night-4096.webp",source:"nasa-blackmarble"}
};
const BM={mode:"political",user:null};
Raster.init(document.getElementById("raster"));
const bmBtn=document.getElementById("bmBtn"), bmMenu=document.getElementById("bmMenu");
function setBasemap(m,user){
  if(!BASEMAPS[m]||(BASEMAPS[m].tex&&!Raster.ok)) m="political";
  if(user) BM.user=m;
  BM.mode=m; bmBtn.textContent=m==="political"?"Map":BASEMAPS[m].label;
  [...bmMenu.children].forEach(b=>b.setAttribute("aria-checked",String(b.dataset.bm===m)));
  if(BASEMAPS[m].tex) Raster.load(m,BASEMAPS[m].tex,render);
  if(typeof renderData==="function"&&el) renderData(); render();
}
function closeBm(){ bmMenu.hidden=true; bmBtn.setAttribute("aria-expanded","false"); }
bmBtn.onclick=e=>{ e.stopPropagation(); bmMenu.hidden=!bmMenu.hidden; bmBtn.setAttribute("aria-expanded",String(!bmMenu.hidden)); };
[...bmMenu.children].forEach(b=>{ if(BASEMAPS[b.dataset.bm].tex&&!Raster.ok) b.disabled=true;
  b.onclick=()=>{ setBasemap(b.dataset.bm,true); closeBm(); }; });
document.addEventListener("click",e=>{ if(!bmMenu.hidden&&!e.target.closest(".bm-wrap")) closeBm(); });

// ---------- data-file stories and declarative layers ----------
const JSONS={};
function loadJSON(url){ return JSONS[url]||(JSONS[url]=fetch(url).then(r=>{ if(!r.ok) throw new Error(url+": HTTP "+r.status); return r.json(); })); }
async function ensureStory(i){
  const meta=STORIES[i]; if(meta.scenes) return meta;
  const js=await loadJSON(meta.file), data={};
  await Promise.all(Object.entries(js.data||{}).map(async([k,u])=>{ data[k]=await loadJSON(u); }));
  js.scenes.forEach(sc=>{ const t=sc.timeline; if(t&&!t.frame){
    const ys=t.years.length===2&&t.years[1]-t.years[0]>1?d3.range(t.years[0],t.years[1]+1):t.years;
    sc.timeline={years:ys,start:Math.max(0,t.start!=null?ys.indexOf(t.start):ys.length-1),label:y=>y,frame:y=>({year:y,caption:(t.captions||{})[y]})}; } });
  const st=Object.assign({},js,{file:meta.file,_data:data}); STORIES[i]=st; return st;
}
const FMT={
  kbd:v=>v>=1000?d3.format(".1f")(v/1000)+" m b/d":d3.format(",.0f")(v)+" k b/d",
  mbd:v=>d3.format(".1f")(v)+" m b/d",
  bcm:v=>d3.format(v<10?".1f":",.0f")(v)+" bcm",
  bcfd:v=>d3.format(".1f")(v)+" bcf/d",
  musd:v=>v>=1000?"$"+d3.format(v>=10000?",.0f":".1f")(v/1000)+" bn":"$"+d3.format(",.0f")(v)+" m",
  bpp:v=>d3.format(".1f")(v)+" barrels",
  m3pp:v=>d3.format(",.0f")(v)+" m³",
  mt:v=>d3.format(v<10000?".1f":",.0f")(v/1000)+" Mt",
  t:v=>v>=1e6?d3.format(".1f")(v/1e6)+" Mt":v>=1e4?d3.format(",.0f")(v/1e3)+" kt":v>=1e3?d3.format(".1f")(v/1e3)+" kt":d3.format(",.0f")(v)+" t",
  kt:v=>v>=1000?d3.format(v>=1e5?",.0f":".1f")(v/1000)+" Mt":d3.format(",.0f")(v)+" kt",  // input in thousand tonnes
  kg:v=>v>=1e6?d3.format(".1f")(v/1e6)+" kt":v>=1e3?d3.format(",.0f")(v/1e3)+" t":d3.format(",.0f")(v)+" kg",
  pct:v=>d3.format(v<10?".1f":".0f")(v)+"%",
  busd:v=>v>=1000?"$"+d3.format(".1f")(v/1000)+" tn":"$"+d3.format(",.0f")(v)+" bn"
};
const fmtOf=f=>typeof f==="function"?f:(FMT[f]||d3.format(",.3~s"));
const lastYear=d=>d.years?d.years[d.years.length-1]:null;
// values per country for a layer spec at a year: EIA-style series or BACI-style trade totals
function valuesOf(ly,d,y){
  const out={};
  if(d.series){ const sr=d.series[ly.series], i=d.years.indexOf(+y), pop=ly.per&&d.series[ly.per].values;
    if(!sr||i<0) return out;
    for(const [k,arr] of Object.entries(sr.values)){ if(!NAMES.has(k)) continue; let v=arr[i]; if(v==null) continue;
      if(pop){ const q=pop[k]&&pop[k][i]; if(!q) continue; v=v/q; } out[k]=v*(ly.mult||1); }
    return out; }
  if(d.groups){ const g=d.groups[ly.group]; Object.entries((g&&g[ly.side||"exports"][y])||{}).forEach(([k,v])=>{ if(NAMES.has(k)) out[k]=v; }); }
  return out;
}
function pointValues(ly,d,y){
  const pi=d.periods.indexOf(String(ly.period||y));
  return d.points.filter(p=>p[ly.field]&&p[ly.field][pi]!=null).map(p=>({id:p.id,name:p.name,at:p.at,v:p[ly.field][pi]}));
}
const LAYER={
  choropleth(ly,d,y,L){ const v={}; Object.entries(valuesOf(ly,d,y)).forEach(([k,x])=>{ if(byId.has(k)) v[k]=x; });  // only countries the map can colour
    L.choro={title:ly.title+(ly.showYear===false?"":" · "+y),fmt:fmtOf(ly.fmt),log:ly.log,reverse:ly.reverse,values:v}; },
  symbols(ly,d,y,L){
    const items=Array.isArray(d.points)?pointValues(ly,d,y)
      :Object.entries(valuesOf(ly,d,y)).filter(([k,v])=>v>0&&ANCHOR.has(k)).map(([k,v])=>({id:k,name:nameOf(k),at:ANCHOR.get(k),v}));
    items.sort((a,b)=>b.v-a.v);
    const vmax=ly.vmax||(items[0]&&items[0].v)||1, R=ly.maxR||40, f=fmtOf(ly.fmt), n=ly.labels==null?6:ly.labels, c=ly.color||"c3";
    items.forEach((x,i)=>{ if(x.v<=0) return; L.symbols.push({at:x.at,r:Math.max(1.5,R*Math.sqrt(x.v/vmax)),color:c,label:i<n?x.name+" "+f(x.v):null}); });
    if(!Array.isArray(d.points)) L.vals.push({title:ly.title,values:Object.fromEntries(items.map(x=>[x.id,x.v])),fmt:f});
    L.sizeKey={color:c,title:ly.title};
  },
  flows(ly,d,y,L){
    const g=d.groups[ly.group]; if(!g) return;
    let fl=(g.flows[y]||[]).filter(r=>ANCHOR.has(r[0])&&ANCHOR.has(r[1]));
    if(ly.from) fl=fl.filter(r=>ly.from.includes(r[0]));
    if(ly.to) fl=fl.filter(r=>ly.to.includes(r[1]));
    const m=ly.metric==="qty"?3:2;  // value (million USD) or quantity (thousand tonnes)
    fl=fl.sort((p,q)=>q[m]-p[m]).slice(0,ly.top||25);
    const vmax=ly.vmax||d3.max(fl,r=>r[m])||1, f=fmtOf(ly.fmt||"musd"), c=ly.color||"c3";
    fl.forEach(r=>{ const a=ANCHOR.get(r[0]), b=ANCHOR.get(r[1]), gi=d3.geoInterpolate(a,b);
      const n=Math.max(8,Math.ceil(d3.geoDistance(a,b)*deg/3));
      L.flows.push({path:d3.range(n+1).map(i=>gi(i/n)),width:0.8+(ly.maxW||9)*r[m]/vmax,color:c,to:b}); });
    const title=ly.title||g.label;
    L.flowKeys.push({color:c,title,qty:m===3});
    const fv=FMT.musd; L.vals.push({title:title+", exports",values:g.exports[y]||{},fmt:fv},{title:title+", imports",values:g.imports[y]||{},fmt:fv});
  },
  lines(ly,d,y,L){ (d.lines[ly.set]||[]).forEach(x=>L.routes.push({path:x.path,color:x.color||ly.color,width:ly.width||2.2,
    dash:!!x.status&&x.status!=="operating",flow:ly.flow&&(!x.status||x.status==="operating"),label:ly.labels?x.name:null,labelAt:x.labelAt})); },
  spikes(ly,d,y,L){
    const items=Object.entries(valuesOf(ly,d,y)).filter(([k,v])=>v>0&&ANCHOR.has(k)).sort((a,b)=>b[1]-a[1]);
    const vmax=ly.vmax||(items[0]&&items[0][1])||1, f=fmtOf(ly.fmt), n=ly.labels==null?5:ly.labels, c=ly.color||"c2";
    items.forEach(([k,v],i)=>L.spikes.push({at:ANCHOR.get(k),h:(ly.maxH||0.6)*v/vmax,color:c,w:ly.width||7,label:i<n?nameOf(k)+" "+f(v):null}));
    L.vals.push({title:ly.title,values:Object.fromEntries(items),fmt:f});
    L.spikeKey={color:c,title:ly.title};
  },
  cartogram(ly,d,y,L){
    const vals=valuesOf(ly,d,y), fs=feats.filter(f=>vals[f.id]>0);
    const tv=d3.sum(fs,f=>vals[f.id]), ta=d3.sum(fs,f=>AREA.get(f.id)), f=fmtOf(ly.fmt), c=col(ly.color||"c2");
    const vmax=d3.max(fs,ft=>vals[ft.id])||1;
    // shade by value as well as size, so overlapping countries stay distinguishable
    const items=fs.map(ft=>({f:ft,v:vals[ft.id],k:clamp(Math.sqrt((vals[ft.id]/tv)/(AREA.get(ft.id)/ta)),0.12,ly.maxK||5),color:C.seq(0.3+0.7*Math.sqrt(vals[ft.id]/vmax))}))
      .sort((a,b)=>b.v-a.v);
    items.forEach((it,i)=>{ if(i<(ly.labels==null?6:ly.labels)) it.label=nameOf(it.f.id); });
    // draw big-on-screen countries first so small ones stay visible on top
    items.sort((a,b)=>b.k*b.k*AREA.get(b.f.id)-a.k*a.k*AREA.get(a.f.id));
    L.carto={items}; L._cartoLabels=[];
    L.vals.push({title:ly.title,values:vals,fmt:f});
    L.cartoKey={color:C.seq(0.8),title:ly.title};
  },
  points(ly,d,y,L){ (d.points[ly.set]||[]).forEach(x=>L.points.push({at:x.at,label:ly.labels===false?null:x.name,color:ly.color,r:ly.r||4.5})); }
};
// a scene "switch" (e.g. pick a commodity) fills {placeholders} in its layers, chart and text
let switchIdx=0;
const switchOpt=()=>scene&&scene.switch?scene.switch.options[switchIdx]:null;
function subst(o){ const op=switchOpt(); if(!op||o==null) return o;
  return JSON.parse(JSON.stringify(o).replace(/\{(\w+)\}/g,(m,k)=>op[k]!=null?String(op[k]).replace(/["\\]/g,"\\$&"):m)); }
function compileLayers(s,L){
  const st=si>=0?STORIES[si]:null, D=(st&&st._data)||{};
  (subst(s.layers)||[]).forEach(ly=>{ const d=D[ly.data], fn=LAYER[ly.type]; if(!d||!fn) return;
    const y=(ly.year==null||ly.year==="t")?((frame&&frame.year)||lastYear(d)):ly.year;
    fn(ly,d,y,L); });
}
function renderChart(){
  const c=subst(scene&&scene.chart), st=si>=0?STORIES[si]:null, d=c&&st&&st._data&&st._data[c.data];
  if(!d){ el.chart.hidden=true; return; }
  const y=(c.year==null||c.year==="t")?((frame&&frame.year)||lastYear(d)):c.year;
  let rows=Array.isArray(d.points)?pointValues(c,d,y).map(p=>[p.name,p.v]):Object.entries(valuesOf(c,d,y)).map(([k,v])=>[nameOf(k),v]);
  rows=rows.filter(r=>r[1]>0).sort((a,b)=>b[1]-a[1]);
  let f=fmtOf(c.fmt);
  if(c.share){ // show each country's share of the world total (dataset's own world figure when it has one)
    const w=d.world&&d.world[c.series], tot=(w&&w[d.years.indexOf(+y)])||d3.sum(rows,r=>r[1]);
    rows=rows.map(r=>[r[0],r[1]/tot*100]); f=FMT.pct; }
  rows=rows.slice(0,c.top||8);
  const mx=rows.length?rows[0][1]:1;
  el.chart.innerHTML=`<div class="ch-title">${esc(c.title)}${c.period||y?" · "+esc(String(c.period||y)):""}</div>`+
    rows.map(([n,v])=>`<div class="ch-row"><span class="nm">${esc(n)}</span><span class="bar" style="width:${(v/mx*100).toFixed(1)}%;background:${col(c.color||"c3")}"></span><span class="v">${esc(f(v))}</span></div>`).join("");
  el.chart.hidden=false;
}

function renderSwitch(){
  const sw=scene&&scene.switch, box=el.sw;
  if(!sw){ box.hidden=true; return; }
  box.innerHTML=`<span class="sw-label">${esc(sw.label||"Show")}</span>`+sw.options.map((o,i)=>`<button class="bloc" data-i="${i}" aria-pressed="${String(i===switchIdx)}">${esc(o.label)}</button>`).join("");
  [...box.querySelectorAll("button")].forEach(b=>b.onclick=()=>{ switchIdx=+b.dataset.i; cartoStart=performance.now()-900; renderSwitch();
    const op=switchOpt(); el.text.textContent=op.text||scene.text; L=layers(); el.legend.innerHTML=legendHTML(); renderChart(); renderData(); render(); });
  box.hidden=false;
  const op=switchOpt(); if(op&&op.text) el.text.textContent=op.text;
}

// ---------- panel ----------
const $=id=>document.getElementById(id);
const el={kicker:$("sKicker"),title:$("sTitle"),text:$("sText"),legend:$("sLegend"),tl:$("sTimeline"),slider:$("tlSlider"),year:$("tlYear"),play:$("tlPlay"),cap:$("tlCaption"),
  prev:$("prev"),next:$("next"),dots:$("dots"),notes:$("sNotes"),notesBody:$("sNotesBody"),blocs:$("blocs"),steps:$("steps"),data:$("sData"),chart:$("sChart"),sw:$("sSwitch")};
let si=-1, ci=0, tlIdx=0, playing=null;
const explore={bloc:null};

function legendHTML(){
  const s=scene; if(!s){ if(explore.bloc) return chip("c2",BLOCS[explore.bloc].label); return ""; }
  let h="";
  if(s.legend) h+=s.legend.map(l=>chip(l.color,l.label)).join("");
  else if(L&&L.groups.length) h+=L.groups.map(g=>chip(g.color,g.label)).join("");
  if(L) L.flowKeys.forEach(k=>h+=chip(k.color,k.title+" · line width = "+(k.qty?"tonnes":"value")));
  if(L&&L.spikeKey) h+=chip(L.spikeKey.color,L.spikeKey.title+" · tower height = amount");
  if(L&&L.cartoKey) h+=chip(L.cartoKey.color,L.cartoKey.title+" · country size = amount");
  if(L&&L.sizeKey) h+=`<span class="size-key" style="color:${col(L.sizeKey.color)}"><i style="width:16px;height:16px"></i><span style="color:var(--ink-soft)">${esc(L.sizeKey.title)} · circle area = amount</span></span>`;
  const ch=L&&L.choro;
  if(ch){const stops=d3.range(0,1.01,0.1).map(t=>C.seq(ch.reverse?1-t:t)).join(",");
    const f=ch.fmt||(x=>x);
    h+=`<div class="ramp"><div class="ramp-title">${esc(ch.title)}</div><div class="ramp-bar" style="background:linear-gradient(90deg,${stops})"></div><div class="ramp-ends"><span>${esc(String(f(L.lo)))}</span><span>${esc(String(f(L.hi)))}</span></div><div class="ramp-na"><i style="background:${C.nodata}"></i>${ch.data==="POWER"?"Near-universal access":"No data"}</div></div>`;}
  return h;
}
// ---------- data and licences ----------
const useCls=u=>u==="noncommercial"?"nc":u==="permission"?"perm":"";
function sourceIds(){
  // story- and scene-level sources, then the base map, which every view shows
  const ids=[];
  if(si>=0&&STORIES[si].scenes){ const st=STORIES[si], D=st._data||{};
    ids.push(...(st.sources||(st._data?[]:["editorial"])), ...((scene&&scene.sources)||[]));
    if(scene) [...(subst(scene.layers)||[]), ...(scene.chart?[subst(scene.chart)]:[])].forEach(l=>{const d=D[l.data]; if(d&&d.source) ids.push(d.source);}); }
  if(BASEMAPS[BM.mode].source) ids.push(BASEMAPS[BM.mode].source);
  ids.push("naturalearth");
  return [...new Set(ids)].filter(id=>SOURCES[id]);
}
function renderData(){
  el.data.innerHTML='<span class="dl">Data</span>'+sourceIds().map(id=>{const s=SOURCES[id];
    return `<button class="src ${useCls(s.use)}" data-src="${id}" title="${esc(USE_LABEL[s.use])}"><b>${esc(s.name)}</b>${esc(s.licence)}</button>`;}).join("")+
    '<button id="licAll">All licences</button>';
  [...el.data.querySelectorAll("[data-src]")].forEach(b=>b.onclick=()=>openLic(b.dataset.src));
  $("licAll").onclick=()=>openLic();
}
const lic=$("lic");
function openLic(focusId){
  const tiers=[["base","Base map and engine (commercial use required)"],["layer","Story layers"]];
  $("licList").innerHTML=tiers.map(([t,h])=>`<section class="lic-tier"><h2>${h}</h2>`+
    Object.entries(SOURCES).filter(([,s])=>s.tier===t).map(([id,s])=>`<div class="lic-item" id="lic-${id}"><span class="n">${esc(s.name)}</span><span class="w">${esc(s.what)}</span>
      <span class="l"><span>${s.licenceUrl?`<a href="${esc(s.licenceUrl)}" target="_blank" rel="noopener">${esc(s.licence)}</a>`:esc(s.licence)}</span>
      <span class="lic-use ${useCls(s.use)}">${esc(USE_LABEL[s.use])}</span>${s.url?`<a href="${esc(s.url)}" target="_blank" rel="noopener">Source</a>`:""}</span>
      <span class="w">${esc(s.credit)}</span></div>`).join("")+`</section>`).join("");
  lic.hidden=false; $("licClose").focus({preventScroll:true});
  if(focusId){const n=$("lic-"+focusId); if(n) n.scrollIntoView({block:"center"});}
}
function closeLic(){ lic.hidden=true; }
$("licClose").onclick=closeLic;

function chip(c,t){return `<span class="chip"><i style="background:${col(c)}"></i>${esc(t)}</span>`;}

function setFrame(){
  const t=scene&&scene.timeline; if(!t){frame=null;renderChart();return;}
  const y=t.years[tlIdx]; frame=t.frame(y,tlIdx); el.year.textContent=t.label(y); el.slider.value=tlIdx;
  el.slider.setAttribute("aria-valuetext",String(t.label(y)));
  el.cap.textContent=frame.caption||""; el.cap.hidden=!frame.caption;
  L=layers(); el.legend.innerHTML=legendHTML(); renderChart(); render();
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
  switchIdx=(scene.switch&&scene.switch.start)||0; cartoStart=performance.now(); renderSwitch();
  frame=null; setFrame(); L=layers(); el.legend.innerHTML=legendHTML(); renderChart();
  el.dots.innerHTML=st.scenes.map((s,j)=>`<button class="dot" aria-label="Scene ${j+1}: ${esc(s.title)}" ${j===ci?'aria-current="step"':""}></button>`).join("");
  [...el.dots.children].forEach((b,j)=>b.onclick=()=>showScene(j));
  el.prev.disabled=ci===0 && si===0;
  el.prev.textContent=ci===0?"Previous story":"Back";
  const lastS=ci===st.scenes.length-1; el.next.textContent=lastS?(si<STORIES.length-1?"Next story":"All stories"):"Next";
  el.notesBody.textContent=st.notes; el.notes.open=false; renderData();
  history.replaceState(null,"","#"+st.id+"/"+(ci+1));
  setBasemap(scene.basemap||BM.user||"political",false);
  syncMode(scene.view.mode); spin=false;
  if(fly) flyTo(scene.view);
  sheet.scrollTop=0; render();
}
el.next.onclick=()=>{ const st=STORIES[si]; if(ci<st.scenes.length-1) showScene(ci+1); else if(si<STORIES.length-1) openStory(si+1); else openToc(); };
el.prev.onclick=()=>{ if(ci>0) showScene(ci-1); else if(si>0) openStory(si-1,"last"); };

let opening=0;
async function openStory(i, scn=0){
  const tok=++opening; si=i; closeToc(); sheet.classList.remove("collapsed"); BM.user=null;
  if(!STORIES[i].scenes){
    el.kicker.textContent=STORIES[i].title; el.title.textContent="Loading…"; el.text.textContent=""; el.chart.hidden=true; sheet.classList.add("loading");
    try{ await ensureStory(i); }
    catch(e){ sheet.classList.remove("loading"); if(tok===opening){ el.title.textContent="This story could not load"; el.text.textContent=String(e.message||e); } return; }
    sheet.classList.remove("loading"); if(tok!==opening) return;
  }
  showScene(scn==="last"?STORIES[i].scenes.length-1:scn);
}
function openExplore(){
  si=-1; scene=null; frame=null; closeToc(); stopPlay(); sheet.classList.remove("collapsed"); el.chart.hidden=true; el.sw.hidden=true;
  el.kicker.textContent="Explore"; el.title.textContent="The world, your way";
  el.text.textContent="Drag to turn the world, pinch or scroll to zoom, tap a country to see its name. Switch between political, satellite and night views with the map button. Show a group of countries:";
  el.tl.hidden=true; el.steps.hidden=true; el.notes.hidden=true; el.blocs.hidden=false;
  renderBlocs(); renderData(); el.legend.innerHTML=legendHTML(); history.replaceState(null,"","#explore");
  syncMode(curKind()); render();
}
function renderBlocs(){
  el.blocs.innerHTML=[["",{label:"None"}],...Object.entries(BLOCS)].map(([k,b])=>`<button class="bloc" data-k="${k}" aria-pressed="${String((explore.bloc||"")===k)}">${esc(b.label)}</button>`).join("");
  [...el.blocs.children].forEach(b=>b.onclick=()=>{explore.bloc=b.dataset.k||null;renderBlocs();L=layers();el.legend.innerHTML=legendHTML();render();});
}

// ---------- table of contents ----------
const tocList=$("tocList");
const CATS=["Energy","Geopolitics","Economics","Statistics","People"];
function buildToc(){
  tocList.innerHTML=CATS.map(cat=>{const items=STORIES.map((s,i)=>[s,i]).filter(([s])=>s.cat===cat); if(!items.length) return "";
    return `<section class="toc-cat"><h2>${cat}</h2><ul>`+items.map(([s,i])=>`<li><button class="toc-story" data-i="${i}"><span class="toc-title">${esc(s.title)}</span><span class="toc-hook">${esc(s.hook)}</span></button></li>`).join("")+`</ul></section>`;}).join("");
  [...tocList.querySelectorAll(".toc-story")].forEach(b=>b.onclick=()=>openStory(+b.dataset.i));
  $("tocCount").textContent=STORIES.length+" short";
}
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
  if(!bmMenu.hidden&&e.key==="Escape"){ closeBm(); bmBtn.focus(); return; }
  if(!lic.hidden){ if(e.key==="Escape") closeLic(); return; }
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
loadJSON("stories/index.json").then(list=>{ STORIES.unshift(...list.map(x=>Object.assign({},x))); }).catch(e=>console.warn("Story index not loaded:",e))
.then(()=>{
  buildToc();
  const h=location.hash.slice(1).split("/"); const idx=STORIES.findIndex(s=>s.id===h[0]);
  if(idx>=0) openStory(idx, Math.max(0,(+h[1]||1)-1));
  else if(h[0]==="explore") openExplore();
  else { openExplore(); openToc(false); }
});
})();
