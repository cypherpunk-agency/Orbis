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
// detailed geometry (Natural Earth 1:50m) arrives after the first paint; it adds small states to the logic set
// and replaces the 1:110m outlines when zoomed in
const HI={byId:null,borders:null,label:new Map()};
const useHi=()=>HI.byId&&V.zoom>=2;
const geom=f=>(useHi()&&HI.byId.get(f.id))||f;
function loadDetail(){
  return fetch("data/world50.json").then(r=>r.json()).then(t=>{
    const fs=topojson.feature(t,t.objects.countries).features;
    HI.byId=new Map(fs.map(f=>[f.id,f])); HI.borders=topojson.mesh(t,t.objects.countries,(a,b)=>a!==b);
    fs.forEach(f=>{ HI.label.set(f.id,[f.properties.lx,f.properties.ly]); if(LANG==="de"&&f.properties.de) NAMES.set(f.id,f.properties.de);
      if(byId.has(f.id)) return;   // a small state the 1:110m map lacks: add it everywhere
      f.properties={name:LANG==="de"&&f.properties.de||f.properties.name}; feats.push(f); byId.set(f.id,f); AREA.set(f.id,d3.geoArea(f));
      tint.push(feats.length%5); NAMES.set(f.id,f.properties.name); if(!ANCHOR.has(f.id)) ANCHOR.set(f.id,d3.geoCentroid(f)); });
    markDirty(); render();
  }).catch(e=>console.warn("Detailed map not loaded:",e));
}
// political tints: greedy colouring so neighbours differ
const nb = topojson.neighbors(WORLD.objects.countries.geometries);
const tint = new Array(feats.length).fill(0);
feats.map((f,i)=>i).sort((a,b)=>nb[b].length-nb[a].length).forEach(i=>{
  const used=new Set(nb[i].map(j=>tint[j]));let k=0;while(used.has(k))k++;tint[i]=k%5;});

// ---------- colours ----------
let C={};
function readColors(){
  const cs=getComputedStyle(document.documentElement);
  ["ocean","land","border","grat","ink","halo","accent","paper","ink-soft","c1","c2","c3","c4","c5","muted","nodata","rim","t0","t1","t2","t3","t4","s0","s1","s2","s3"].forEach(k=>C[k]=cs.getPropertyValue("--"+k).trim());
  C.tints=[C.t0,C.t1,C.t2,C.t3,C.t4]; C.ink_soft=C["ink-soft"];
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
  const L={fills:{},groups:[],choro:null,routes:[],points:[],circles:[],highlight:s.highlight||[],symbols:[],flows:[],vals:[],sizeKey:null,flowKeys:[],spikes:[],spikeKey:null,carto:null,rasters:[],regions:[],pov:null,particles:null,events:[],hist:null};
  Object.assign(L.fills,s.fills||{});
  L.groups=(s.groups||[]).slice();
  if(s.choro) L.choro=s.choro;
  L.routes=arr(s.routes).slice(); L.points=arr(s.points).slice(); L.circles=(s.circles||[]).slice();
  if(frame){ if(frame.groups)L.groups=L.groups.concat(frame.groups); if(frame.routes)L.routes=L.routes.concat(frame.routes);
    if(frame.points)L.points=L.points.concat(frame.points); if(frame.fills)Object.assign(L.fills,frame.fills); }
  if(explore.bloc){const b=BLOCS[explore.bloc];L.groups.push({label:t(b.label),color:"c2",ids:b.ids});}
  L.political = scene ? !!s.political : !explore.bloc;
  L.countryLabels = scene ? !!s.countryLabels : true;
  compileLayers(s,L);
  L.gmap=new Map(); L.groups.forEach(g=>g.ids.forEach(id=>L.gmap.set(id,g)));
  if(L.choro){const ch=L.choro,d=ch.values||DATA[ch.data],vals=Object.values(d);
    const lo=ch.vmin!=null?ch.vmin:d3.min(vals),hi=ch.vmax!=null?ch.vmax:d3.max(vals);
    if(ch.diverging){ // blue below the midpoint, red above, symmetric so equal distances look equal
      const m=ch.mid, r=Math.max(Math.abs(hi-m),Math.abs(m-lo))||1, dv=d3.interpolateRgbBasis(["#2166AC","#67A9CF","#F7F7F7","#EF8A62","#B2182B"]);
      L.color=v=>dv(clamp(0.5+(v-m)/(2*r),0,1)); L.ramp=dv;
    } else {
      const sc=ch.log?d3.scaleLog().domain([Math.max(lo,0.1),hi]):d3.scaleLinear().domain([lo,hi]);
      L.color=v=>{let t=clamp(sc(ch.log?Math.max(v,0.1):v),0,1); if(ch.reverse)t=1-t; return C.seq(t);}; L.ramp=null; }
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
// image layers drawn by WebGL under the vector canvas: a base map texture, then data grids
function drawRaster(){
  if(!Raster.ok) return false;
  const list=[];
  let m=BM.mode;
  if(m==="political"&&L&&L.rasters.length) m="plain";   // data grids need a base the vector canvas does not cover
  if(m==="plain"){ ensurePlain(); list.push({name:"plain"}); }
  else if(BASEMAPS[m].tex){ if(!Raster.has(m)) Raster.load(m,BASEMAPS[m].tex,render); list.push({name:m}); }
  if(DETAIL.name&&DETAIL.mode===m&&Raster.has(DETAIL.name)) list.push({name:DETAIL.name});
  if(L) L.rasters.forEach(r=>{ if(Raster.has(r.tex)) list.push({name:r.tex,alpha:r.alpha}); });
  if(!list.length||!list.some(l=>Raster.has(l.name))){ if(rasterOn){Raster.clear();rasterOn=false;} return false; }
  const wg=wGlobe(), c=V.center;
  rasterOn=Raster.draw({layers:list,a:V.a,b:V.b,t:V.t,sa:S[V.a],sb:S[V.b],k:V.zoom,tr:proj.translate(),
    rot:[-c[0]*rad,-c[1]*wg*rad],clip:wg>0.001?90+(1-wg)*89.4:null,W,H,dpr:DPR});
  return rasterOn;
}
// historical border snapshots, decoded once (inline TopoJSON or one file per snapshot)
const HIST={};
function histSnap(alias,d,yr){
  const key=alias+":"+yr; if(HIST[key]) return HIST[key].ready?HIST[key]:null;
  HIST[key]={ready:false};
  const done=t=>{ const o=t.objects.states||Object.values(t.objects)[0], fs=topojson.feature(t,o).features;
    const nb=topojson.neighbors(o.geometries), tn=new Array(fs.length).fill(0);
    fs.map((f,i)=>i).sort((a,b)=>nb[b].length-nb[a].length).forEach(i=>{const u=new Set(nb[i].map(j=>tn[j]));let k=0;while(u.has(k))k++;tn[i]=k%5;});
    Object.assign(HIST[key],{feats:fs,tint:tn,mesh:topojson.mesh(t,o,(a,b)=>a!==b),area:fs.map(f=>d3.geoArea(f)),ready:true}); lateData(); };
  if(d.snapshots) setTimeout(()=>done(d.snapshots[yr]),0); else loadJSON(d.files[yr]).then(done);
  return null;
}
// data that arrives after a scene opened: rebuild layers and the panel's legend
function lateData(){ markDirty(); L=layers(); Ldirty=false; if(el&&el.legend) el.legend.innerHTML=legendHTML(); render(); }
// admin-1 geometry per country, loaded on demand
const REG={};
function regionGeo(iso){
  if(REG[iso]) return REG[iso].ready?REG[iso]:null;
  REG[iso]={ready:false};
  loadJSON("data/geo/admin1/"+iso+".json").then(t=>{ const o=t.objects.regions||Object.values(t.objects)[0];
    Object.assign(REG[iso],{feats:topojson.feature(t,o).features,mesh:topojson.mesh(t,o,(a,b)=>a!==b),ready:true}); lateData(); })
    .catch(e=>console.warn("No regions for",iso,e));
  return null;
}
// u/v wind field from an RGB PNG (R=u, G=v, 128 = 0)
const VF={};
function vectorField(alias,desc){
  if(VF[alias]) return VF[alias].ready?VF[alias]:null;
  const G=VF[alias]={ready:false}, url=Object.values(desc.frames)[0], e=desc.encoding;
  const img=new Image(); img.onload=()=>{ const cv=document.createElement("canvas"); cv.width=img.width; cv.height=img.height;
    const g=cv.getContext("2d"); g.drawImage(img,0,0); const px=g.getImageData(0,0,cv.width,cv.height).data;
    G.w=cv.width; G.h=cv.height; G.u=new Float32Array(G.w*G.h); G.v=new Float32Array(G.w*G.h);
    for(let i=0;i<G.u.length;i++){ G.u[i]=(px[i*4]-128)/127*e.max; G.v[i]=(px[i*4+1]-128)/127*e.max; }
    G.ready=true; lateData(); };
  img.src=url; return null;
}
function windAt(F,lon,lat){ const x=((lon+180)/360*F.w%F.w+F.w)%F.w, y=clamp((90-lat)/180*F.h,0,F.h-1.001);
  const x0=Math.floor(x), y0=Math.floor(y), x1=(x0+1)%F.w, y1=y0+1<F.h?y0+1:y0, fx=x-x0, fy=y-y0;
  const at=(a,i,j)=>a[j*F.w+i], lerp=(a)=>(at(a,x0,y0)*(1-fx)+at(a,x1,y0)*fx)*(1-fy)+(at(a,x0,y1)*(1-fx)+at(a,x1,y1)*fx)*fy;
  return [lerp(F.u),lerp(F.v)]; }
let PARTS=null;
function drawParticles(P){
  const n=P.count, TR=12;
  function seed(i,init){ PARTS.lon[i]=Math.random()*360-180; PARTS.lat[i]=Math.asin(Math.random()*2-1)*deg*0.95; PARTS.age[i]=init?Math.floor(Math.random()*80):0;
    for(let k=0;k<TR;k++){ PARTS.tr[(i*TR+k)*2]=PARTS.lon[i]; PARTS.tr[(i*TR+k)*2+1]=PARTS.lat[i]; } }
  if(!PARTS||PARTS.n!==n){ PARTS={n,lon:new Float32Array(n),lat:new Float32Array(n),age:new Uint16Array(n),tr:new Float32Array(n*TR*2)};
    for(let i=0;i<n;i++) seed(i,true); }
  const k=reduce?0:0.008*P.speed;
  ctx.lineWidth=1.3; ctx.lineCap="round";
  const fast=[],slow=[];
  for(let i=0;i<n;i++){
    const w=windAt(P.F,PARTS.lon[i],PARTS.lat[i]), sp=Math.hypot(w[0],w[1]);
    for(let t=TR-1;t>0;t--){ PARTS.tr[(i*TR+t)*2]=PARTS.tr[(i*TR+t-1)*2]; PARTS.tr[(i*TR+t)*2+1]=PARTS.tr[(i*TR+t-1)*2+1]; }
    PARTS.lon[i]+=w[0]*k/Math.max(0.2,Math.cos(PARTS.lat[i]*rad)); PARTS.lat[i]+=w[1]*k;
    if(PARTS.lon[i]>180) PARTS.lon[i]-=360; if(PARTS.lon[i]<-180) PARTS.lon[i]+=360;
    PARTS.tr[i*TR*2]=PARTS.lon[i]; PARTS.tr[i*TR*2+1]=PARTS.lat[i];
    if(++PARTS.age[i]>90||Math.abs(PARTS.lat[i])>85||sp<3){ seed(i,false); continue; }
    (sp>35?fast:slow).push(i);
  }
  [[slow,0.35],[fast,0.85]].forEach(([ids,a])=>{ ctx.beginPath();
    ids.forEach(i=>{ let prev=null;
      for(let t=0;t<TR;t++){ const ll=[PARTS.tr[(i*TR+t)*2],PARTS.tr[(i*TR+t)*2+1]];
        if(!visible(ll)){prev=null;continue;} const p=proj(ll); if(!p){prev=null;continue;}
        if(prev&&Math.abs(prev[0]-p[0])<40){ ctx.moveTo(prev[0],prev[1]); ctx.lineTo(p[0],p[1]); } prev=p; } });
    ctx.strokeStyle=onDark?"#FFFFFF":col(P.color); ctx.globalAlpha=a; ctx.stroke(); ctx.globalAlpha=1; });
}
// deep zoom: when the camera rests zoomed in on an image basemap, fetch a sharper patch of just the visible area
// from NASA GIBS (500 m/px source) and draw it over the global texture
const GIBS={satellite:"BlueMarble_NextGeneration",night:"VIIRS_Black_Marble",terrain:"BlueMarble_ShadedRelief_Bathymetry"};
const DETAIL={name:null,mode:null,key:null,timer:null};
function scheduleDetail(){
  clearTimeout(DETAIL.timer);
  DETAIL.timer=setTimeout(()=>{
    const m=BM.mode; if(!GIBS[m]||V.zoom<2.5||anim||V.t!==0||!proj.invert) return;
    // visible box from the frame corners and edges
    const pts=[]; for(let i=0;i<=8;i++) for(let j=0;j<=8;j++){ const p=proj.invert([F.x+F.w*i/8,F.y+F.h*j/8]); if(p&&!isNaN(p[0])&&(curKind()!=="globe"||d3.geoDistance(p,V.center)<Math.PI/2)) pts.push(p); }
    if(pts.length<4) return;
    let lo0=d3.min(pts,p=>p[0]),lo1=d3.max(pts,p=>p[0]),la0=d3.min(pts,p=>p[1]),la1=d3.max(pts,p=>p[1]);
    if(lo1-lo0>180) return;  // spans the date line or too wide to gain detail
    const pad=0.08*(lo1-lo0); lo0=Math.max(-180,lo0-pad); lo1=Math.min(180,lo1+pad); la0=Math.max(-90,la0-pad); la1=Math.min(90,la1+pad);
    const key=m+[lo0,la0,lo1,la1].map(v=>v.toFixed(1)).join(","); if(key===DETAIL.key) return; DETAIL.key=key;
    const w=2048, h=Math.max(256,Math.min(2048,Math.round(w*(la1-la0)/(lo1-lo0))));
    const url="https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS="+GIBS[m]+
      "&STYLES=&CRS=EPSG:4326&BBOX="+[la0,lo0,la1,lo1].map(v=>v.toFixed(3)).join(",")+"&WIDTH="+w+"&HEIGHT="+h+"&FORMAT=image/jpeg";
    const img=new Image(); img.crossOrigin="anonymous";
    img.onload=()=>{ if(DETAIL.key!==key) return; const name="detail:"+(DETAIL.flip=!DETAIL.flip?1:0);
      Raster.putPatch(name,img,[lo0,la0,lo1,la1]); DETAIL.name=name; DETAIL.mode=m; render(); };
    img.src=url;
  },500);
}
// plain land/ocean texture in the theme colours, drawn once from the country shapes
let plainFor=null;
function ensurePlain(){
  const key=C.ocean+C.land+feats.length; if(plainFor===key) return; plainFor=key;
  const cv=document.createElement("canvas"); cv.width=4096; cv.height=2048; const g=cv.getContext("2d");
  const pr=d3.geoEquirectangular().scale(4096/(2*Math.PI)).translate([2048,1024]).precision(0.2), pa=d3.geoPath(pr,g);
  g.fillStyle=C.ocean; g.fillRect(0,0,4096,2048);
  g.beginPath(); feats.forEach(f=>pa(f)); g.fillStyle=C.land; g.fill();
  Raster.put("plain",cv);
}
// data grids: greyscale PNG frames decoded through a palette into colour textures
const GRIDS={};
function gridPalette(kind){
  const lut=new Uint8ClampedArray(256*4), dv=d3.interpolateRgbBasis(["#2166AC","#67A9CF","#F7F7F7","#EF8A62","#B2182B"]);
  for(let i=1;i<256;i++){ const t=(i-1)/254;
    const c=d3.rgb(kind==="diverging"?dv(t):C.seq(t)); lut[i*4]=c.r; lut[i*4+1]=c.g; lut[i*4+2]=c.b;
    lut[i*4+3]=kind==="diverging"?235:Math.round(255*(0.25+0.75*t)); }
  return lut;
}
function gridFrame(alias,desc,label){
  const key=alias+":"+label, url=desc.frames[label]; if(!url) return null;
  if(GRIDS[key]) return GRIDS[key];
  const G=GRIDS[key]={tex:"grid:"+key,ready:false};
  const img=new Image(); img.onload=()=>{
    const cv=document.createElement("canvas"); cv.width=img.width; cv.height=img.height; const g=cv.getContext("2d");
    g.drawImage(img,0,0); const id=g.getImageData(0,0,cv.width,cv.height), px=id.data, lut=gridPalette(desc.palette);
    G.w=cv.width; G.h=cv.height; G.bytes=new Uint8Array(cv.width*cv.height);
    for(let i=0;i<G.bytes.length;i++){ const b=px[i*4]; G.bytes[i]=b; px[i*4]=lut[b*4]; px[i*4+1]=lut[b*4+1]; px[i*4+2]=lut[b*4+2]; px[i*4+3]=b?lut[b*4+3]:0; }
    g.putImageData(id,0,0); Raster.put(G.tex,cv); G.ready=true; lateData(); };
  img.src=url; return G;
}
function gridDecode(desc,b){ if(!b) return null; const e=desc.encoding, t=(b-1)/254;
  return e.type==="log"?Math.pow(10,Math.log10(e.min)+t*(Math.log10(e.max)-Math.log10(e.min))):e.min+t*(e.max-e.min); }
let rasterOn=false;
// layers depend on the scene, timeline frame, switch and focus, not on the camera: rebuild only when marked dirty
let Ldirty=true;
const markDirty=()=>{Ldirty=true;};
function draw(){
  update(); if(Ldirty||!L){ L=layers(); Ldirty=false; }
  if(L.carto) L._cartoLabels=[];
  const ras=drawRaster(); onDark=ras&&(BM.mode==="satellite"||BM.mode==="night"||BM.mode==="terrain"); placed=[];
  ctx.setTransform(DPR,0,0,DPR,0,0); ctx.clearRect(0,0,W,H);
  if(!ras){ctx.beginPath();path(SPHERE);ctx.fillStyle=C.ocean;ctx.fill();}
  ctx.beginPath();path(GRAT);ctx.strokeStyle=onDark?"rgba(255,255,255,.10)":C.grat;ctx.lineWidth=0.6;ctx.stroke();
  if(L.hist){ const Hh=L.hist.H;
    ctx.beginPath(); feats.forEach(f=>path(f)); ctx.fillStyle=onDark?"rgba(255,255,255,.1)":C.land; ctx.fill();
    Hh.feats.forEach((f,i)=>{ ctx.beginPath(); path(f); ctx.fillStyle=C.tints[Hh.tint[i]]; ctx.globalAlpha=ras?0.75:1; ctx.fill(); ctx.globalAlpha=1; });
    ctx.beginPath(); path(Hh.mesh); ctx.strokeStyle=C.ink; ctx.lineWidth=0.9; ctx.stroke();
  }
  else if(L.carto) drawCartogram(ras);
  else{
    if(ras) ctx.globalAlpha=0.72;
    for(let i=0;i<feats.length;i++){const fc=fillFor(feats[i],i,ras); if(!fc) continue; ctx.beginPath();path(geom(feats[i]));ctx.fillStyle=fc;ctx.fill();}
    ctx.globalAlpha=1;
    ctx.beginPath();path(useHi()?HI.borders:borders);ctx.strokeStyle=onDark?"rgba(240,245,248,.42)":C.border;ctx.lineWidth=onDark?0.7:0.6;ctx.stroke();
  }
  L.regions.forEach(rg=>{ rg.R.feats.forEach(f=>{ const v=rg.vals[f.id]; ctx.beginPath(); path(f); ctx.fillStyle=v==null?C.nodata:rg.color(v); ctx.fill(); });
    ctx.beginPath(); path(rg.R.mesh); ctx.strokeStyle=C.paper; ctx.lineWidth=0.8; ctx.stroke(); });
  if(L.pov) L.pov.areas.forEach(a=>{ let o=a.properties.o[L.pov.view]; if(o&&!NAMES.has(o)) o=null; if(L.pov.only&&!L.pov.only.includes(a.properties.name)) return;
    ctx.beginPath(); path(a); const idx=feats.findIndex(f=>f.id===o);
    ctx.fillStyle=o&&idx>=0?C.tints[tint[idx]]:C.nodata; ctx.fill();
    ctx.setLineDash([3,3]); ctx.strokeStyle=C.accent; ctx.lineWidth=1.3; ctx.stroke(); ctx.setLineDash([]); });
  if(L.highlight.length){ctx.beginPath();L.highlight.forEach(id=>{const f=byId.get(id);if(f)path(geom(f));});ctx.strokeStyle=C.ink;ctx.lineWidth=1.6;ctx.stroke();}
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
      if(visible(at)){const xy=proj(at); if(xy){let t=(r.label||"")+(r.dist?(r.label?": ":"")+"≈ "+(km(p)<1000?d3.format(",")(Math.round(km(p)/10)*10):d3.format(",")(Math.round(km(p)/100)*100))+" km":""); labels.push([t,xy[0]+6,xy[1]-10,{color:col(r.color),size:13}]);}}}
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
  if(L.particles) drawParticles(L.particles);
  // events: older ones faint, the current timeline step bright
  L.events.forEach(E=>{ const c=col(E.color);
    [[false,0.28],[true,0.85]].forEach(([now,a])=>{ ctx.beginPath();
      E.pts.forEach(p=>{ if(p.now!==now||!visible(p.at)) return; const q=proj(p.at); if(!q) return; ctx.moveTo(q[0]+p.r,q[1]); ctx.arc(q[0],q[1],p.r,0,2*Math.PI); });
      ctx.fillStyle=c; ctx.globalAlpha=a; ctx.fill(); ctx.globalAlpha=1; if(now){ctx.lineWidth=0.8; ctx.strokeStyle=C.halo; ctx.stroke();} }); });
  if(L.hist&&L.hist.labels){ const Hh=L.hist.H, R=Math.min(F.w,F.h)/2*V.zoom*0.9;
    Hh.feats.map((f,i)=>[f,i]).sort((a,b)=>Hh.area[b[1]]-Hh.area[a[1]]).forEach(([f,i])=>{ const n=f.properties.name||"", size=Math.sqrt(Hh.area[i])*R;
      if(size<n.length*5.2) return; const at=f.properties.lx!=null?[f.properties.lx,f.properties.ly]:d3.geoCentroid(f); if(!visible(at)) return;
      const q=proj(at); if(q) labels.push([n,q[0],q[1],{align:"center",size:size>160?14:12}]); }); }
  L.regions.forEach(rg=>{ if(!rg.labels) return; rg.R.feats.forEach(f=>{ const v=rg.vals[f.id], at=[f.properties.lx,f.properties.ly];
    if(at[0]==null||!visible(at)) return; const p=proj(at); if(p) labels.push([f.properties.name+(v!=null?" "+rg.fmt(v):""),p[0],p[1],{align:"center",size:12}]); }); });
  if(L.pov) L.pov.areas.forEach(a=>{ let o=a.properties.o[L.pov.view]; if(o&&!NAMES.has(o)) o=null; if(L.pov.only&&!L.pov.only.includes(a.properties.name)) return;
    if(path.area(a)<400) return;  // skip slivers
    const c=d3.geoCentroid(a); if(!visible(c)) return; const p=proj(c); if(p) labels.push([o?nameOf(o):t("disputed"),p[0],p[1],{align:"center",size:12,color:C.accent}]); });
  if(L._cartoLabels) labels.unshift(...L._cartoLabels);
  if(L.countryLabels&&!L.carto&&!L.hist) countryLabels(labels);
  labels.forEach(l=>label(...l));
  // rim
  ctx.beginPath();path(SPHERE);ctx.strokeStyle=C.rim;ctx.lineWidth=1;ctx.stroke();
}

// ---------- country names ----------
// largest countries first; a name is shown when the country is big enough on screen to hold it
const BY_AREA=()=>feats.slice().sort((a,b)=>AREA.get(b.id)-AREA.get(a.id));
let byAreaCache=null, byAreaN=0;
function countryLabels(labels){
  if(!byAreaCache||byAreaN!==feats.length){ byAreaCache=BY_AREA(); byAreaN=feats.length; }
  const R=Math.min(F.w,F.h)/2*V.zoom*0.9, soft=onDark?"#D9E2E6":C.ink_soft;
  byAreaCache.forEach(f=>{ const n=nameOf(f.id), size=Math.sqrt(AREA.get(f.id))*R;
    if(size<n.length*5.2) return;
    const at=HI.label.get(f.id)||ANCHOR.get(f.id); if(!at||!visible(at)) return; const p=proj(at); if(!p) return;
    labels.push([n,p[0],p[1],{align:"center",size:size>160?14:12,color:soft}]); });
}

// ---------- cartogram ----------
let cartoStart=0;
const cartoEase=()=>reduce?1:d3.easeCubicInOut(clamp((performance.now()-cartoStart-900)/1500,0,1));
function drawCartogram(ras){
  const e=cartoEase();
  // the true map stays as a faint ghost so the distortion reads as a change
  ctx.beginPath(); feats.forEach(f=>path(geom(f))); ctx.fillStyle=ras?"rgba(255,255,255,.12)":C.nodata; ctx.globalAlpha=0.7; ctx.fill(); ctx.globalAlpha=1;
  L.carto.items.forEach(it=>{ const a=ANCHOR.get(it.f.id); if(!a||!visible(a)) return; const p=proj(a); if(!p) return;
    const k=1+(it.k-1)*e;
    ctx.save(); ctx.translate(p[0],p[1]); ctx.scale(k,k); ctx.translate(-p[0],-p[1]);
    ctx.beginPath(); path(geom(it.f)); ctx.fillStyle=it.color; ctx.globalAlpha=0.9; ctx.fill(); ctx.globalAlpha=1;
    ctx.lineWidth=0.9/k; ctx.strokeStyle=C.paper; ctx.stroke(); ctx.restore();
    if(it.label&&e>0.98) L._cartoLabels.push([it.label,p[0],p[1],{align:"center",size:13}]);
  });
}

// ---------- animation loop ----------
let anim=null, spin=false, raf=null, last=0;
function hasFlow(){return !reduce && L && (L.flows.length>0 || !!L.particles || L.routes.some(r=>r.flow));}
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
    end(){V.a=V.b=k1;V.t=0;V.center=t.center.slice();V.zoom=z1;scheduleDetail();}};
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
  if(ptrs.size===0){ if(drag&&!drag.moved) tap(e.clientX,e.clientY); drag=null; render(); scheduleDetail(); } }
canvas.addEventListener("pointerup",endPtr);canvas.addEventListener("pointercancel",endPtr);
canvas.addEventListener("wheel",e=>{e.preventDefault();settle();spin=false;V.zoom=clamp(V.zoom*Math.exp(-e.deltaY*0.0015),0.6,24);render();scheduleDetail();},{passive:false});
document.getElementById("zin").onclick=()=>{settle();V.zoom=clamp(V.zoom*1.5,0.6,24);render();scheduleDetail();};
document.getElementById("zout").onclick=()=>{settle();V.zoom=clamp(V.zoom/1.5,0.6,24);render();scheduleDetail();};

const tip=document.getElementById("tip"); let tipTimer=null;
function hideTip(){tip.hidden=true;}
function tap(x,y){
  if(V.t!==0||!proj.invert) return;
  const ll=proj.invert([x,y]); if(!ll||isNaN(ll[0])) return;
  if(curKind()==="globe"&&d3.geoDistance(ll,V.center)>Math.PI/2) return;
  for(const rg of L.regions){ const rf=rg.R.feats.find(f=>d3.geoContains(f,ll)); if(rf){ const v=rg.vals[rf.id];
    tip.innerHTML="<b>"+esc(rf.properties.name)+"</b><span>"+esc(rg.title)+": "+(v==null?t("No data"):esc(rg.fmt(v)))+"</span>";
    tip.hidden=false; tip.style.left=clamp(x,70,W-70)+"px"; tip.style.top=Math.max(70,y-14)+"px"; clearTimeout(tipTimer); tipTimer=setTimeout(hideTip,3500); return; } }
  const gridHtml=L.rasters.map(r=>{ const G=r.G; if(!G.bytes) return "";
    const x=Math.floor((ll[0]+180)/360*G.w)%G.w, y=Math.min(G.h-1,Math.floor((90-ll[1])/180*G.h)), v=gridDecode(r.desc,G.bytes[y*G.w+x]);
    return v==null?"":"<span>"+esc(r.title)+": "+esc(r.fmt(v))+"</span>"; }).join("");
  if(quiz.mode==="where"&&f0(ll)){ quizTap(f0(ll).id); return; }
  if(L.hist){ const hf=L.hist.H.feats.find(f=>d3.geoContains(f,ll));
    tip.innerHTML=hf?"<b>"+esc(hf.properties.name||"")+"</b><span>"+esc(t("Borders of {y}",{y:L.hist.year}))+"</span>":"<span>"+esc(t("Not an independent state in {y}",{y:L.hist.year}))+"</span>";
    tip.hidden=false; tip.style.left=clamp(x,70,W-70)+"px"; tip.style.top=Math.max(70,y-14)+"px"; clearTimeout(tipTimer); tipTimer=setTimeout(hideTip,3500); return; }
  const f=feats.find(f=>d3.geoContains((HI.byId&&HI.byId.get(f.id))||f,ll));
  if(!f&&gridHtml){ tip.innerHTML="<b>"+d3.format(".1f")(Math.abs(ll[1]))+"°"+(ll[1]>=0?"N":"S")+" "+d3.format(".1f")(Math.abs(ll[0]))+"°"+(ll[0]>=0?"E":"W")+"</b>"+gridHtml;
    tip.hidden=false; tip.style.left=clamp(x,70,W-70)+"px"; tip.style.top=Math.max(70,y-14)+"px"; clearTimeout(tipTimer); tipTimer=setTimeout(hideTip,3500); return; }
  if(!f){hideTip();return;}
  if(L.flows.length||focus){ focus=focus===f.id?null:f.id; L=layers(); el.legend.innerHTML=legendHTML(); render(); }
  let html="<b>"+esc(nameOf(f.id))+"</b>"+gridHtml;
  if(L.choro){const v=L.cdata[f.id]; html+="<span>"+(v==null?t("No data"):esc(String(L.choro.fmt?L.choro.fmt(v):v)))+"</span>";}
  L.vals.forEach(lv=>{const v=lv.values[f.id]; if(v!=null) html+="<span>"+esc(lv.title)+": "+esc(lv.fmt(v))+"</span>";});
  const g=L.gmap.get(f.id); if(g) html+="<span>"+esc(g.label)+"</span>";
  tip.innerHTML=html; tip.hidden=false;
  tip.style.left=clamp(x,70,W-70)+"px"; tip.style.top=Math.max(70,y-14)+"px";
  clearTimeout(tipTimer); tipTimer=setTimeout(hideTip,3500);
}
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

function f0(ll){ return feats.find(f=>d3.geoContains((HI.byId&&HI.byId.get(f.id))||f,ll)); }

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
  political:{label:t("Political")},
  satellite:{label:t("Satellite"),tex:"data/tex/satellite-4096.webp",source:"nasa-bluemarble"},
  night:{label:t("Night lights"),tex:"data/tex/night-4096.webp",source:"nasa-blackmarble"},
  terrain:{label:t("Terrain"),tex:"data/tex/terrain-4096.webp",source:"nasa-relief"}
};
const BM={mode:"political",user:null};
Raster.init(document.getElementById("raster"));
const bmBtn=document.getElementById("bmBtn"), bmMenu=document.getElementById("bmMenu");
function setBasemap(m,user){
  if(!BASEMAPS[m]||(BASEMAPS[m].tex&&!Raster.ok)) m="political";
  if(user) BM.user=m;
  BM.mode=m; bmBtn.textContent=m==="political"?t("Map"):BASEMAPS[m].label;
  [...bmMenu.children].forEach(b=>b.setAttribute("aria-checked",String(b.dataset.bm===m)));
  if(BASEMAPS[m].tex) Raster.load(m,BASEMAPS[m].tex,render);
  DETAIL.key=null; scheduleDetail();
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
  const js=meta.file==="draft"?JSON.parse(localStorage.getItem("orbis-draft")||"null"):await loadJSON(meta.file).then(j=>(LANG!=="en"&&meta.file.startsWith("stories/"+LANG+"/")&&(j._translated=true),j)).catch(e=>{ const en=meta.file.replace("stories/"+LANG+"/","stories/"); if(en!==meta.file) return loadJSON(en); throw e; }), data={};
  await Promise.all(Object.entries(js.data||{}).map(async([k,u])=>{ data[k]=await loadJSON(u); }));
  js.scenes.forEach(sc=>{ const t=sc.timeline; if(t&&!t.frame){
    const ys=!t.format&&t.years.length===2&&t.years[1]-t.years[0]>1?d3.range(t.years[0],t.years[1]+1):t.years;
    const MON=LANG==="de"?["Jan.","Feb.","März","Apr.","Mai","Juni","Juli","Aug.","Sept.","Okt.","Nov.","Dez."]:["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
    const lab0=t.format==="month"?(y=>MON[y%100-1]+" "+Math.floor(y/100)):t.format==="date"?(y=>(LANG==="de"?y%100+". ":y%100+" ")+MON[Math.floor(y/100)%100-1]+" "+Math.floor(y/10000)):(y=>y), lab=y=>(t.labels&&t.labels[y])||lab0(y);
    sc.timeline={years:ys,start:Math.max(0,t.start!=null?ys.indexOf(t.start):ys.length-1),label:lab,frame:y=>({year:y,caption:(t.captions||{})[y]})}; } });
  const st=Object.assign({},js,{file:meta.file,_data:data},meta.id.startsWith("@")?{id:meta.id}:{}); STORIES[i]=st; return st;
}
const FMT={
  kbd:v=>v>=1000?d3.format(".1f")(v/1000)+t(" m b/d"):d3.format(",.0f")(v)+t(" k b/d"),
  mbd:v=>d3.format(".1f")(v)+t(" m b/d"),
  bcm:v=>d3.format(v<10?".1f":",.0f")(v)+t(" bcm"),
  bcfd:v=>d3.format(".1f")(v)+t(" bcf/d"),
  musd:v=>v>=1000?"$"+d3.format(v>=10000?",.0f":".1f")(v/1000)+t(" bn"):"$"+d3.format(",.0f")(v)+t(" m"),
  bpp:v=>d3.format(".1f")(v)+t(" barrels"),
  m3pp:v=>d3.format(",.0f")(v)+" m³",
  mt:v=>d3.format(v<10000?".1f":",.0f")(v/1000)+" Mt",
  t:v=>v>=1e6?d3.format(".1f")(v/1e6)+" Mt":v>=1e4?d3.format(",.0f")(v/1e3)+" kt":v>=1e3?d3.format(".1f")(v/1e3)+" kt":d3.format(",.0f")(v)+" t",
  kt:v=>v>=1000?d3.format(v>=1e5?",.0f":".1f")(v/1000)+" Mt":d3.format(",.0f")(v)+" kt",  // input in thousand tonnes
  kg:v=>v>=1e6?d3.format(".1f")(v/1e6)+" kt":v>=1e3?d3.format(",.0f")(v/1e3)+" t":d3.format(",.0f")(v)+" kg",
  degc:v=>(v>0?"+":"")+d3.format(".1f")(v)+" °C",
  ppkm2:v=>d3.format(v<10?".1f":",.0f")(v)+t(" per km²"),
  int:v=>d3.format(",.0f")(v),
  num:v=>d3.format(Math.abs(v)<10?",.2~f":",.1~f")(v),
  dollar:v=>"$"+d3.format(",.2f")(v),
  tpp:v=>d3.format(v<10?".1f":",.0f")(v)+" t",
  mil:v=>d3.format(",.0f")(v)+t(" M"),
  yrs:v=>d3.format(".0f")(v)+t(" yrs"),
  pct0:v=>d3.format(".0f")(v)+"%",
  usdB:v=>"$"+d3.format(",.0f")(v)+t(" B"),
  people:v=>v>=1e6?d3.format(".1f")(v/1e6)+t(" m"):d3.format(",.0f")(v),
  usd:v=>"$"+d3.format(",.0f")(v),
  eur:v=>"€"+d3.format(",.0f")(v),
  intd:v=>"Int$ "+d3.format(",.0f")(v),
  pct:v=>d3.format(v<10?".1f":".0f")(v)+"%",
  busd:v=>v>=1000?"$"+d3.format(".1f")(v/1000)+t(" tn"):"$"+d3.format(",.0f")(v)+t(" bn")
};
const fmtOf=f=>typeof f==="function"?f:(FMT[f]||(typeof f==="string"&&f.startsWith("d3:")?d3.format(f.slice(3)):d3.format(",.3~s")));
const lastYear=d=>d.years?d.years[d.years.length-1]:null;
// values per country for a layer spec at a year: EIA-style series or BACI-style trade totals
// index of year y in a series dataset; with "step": true a value holds until the next listed date
// a year as the scene timeline shows it ("2 Apr 2025" for date timelines)
const ylab=y=>scene&&scene.timeline&&scene.timeline.years.includes(+y)?scene.timeline.label(+y):/^\d{8}$/.test(String(y))?fmtDate(y):y;
function yearIndex(d,y){ let i=d.years.indexOf(+y); if(i<0&&d.step){ i=-1; d.years.forEach((v,j)=>{ if(v<=+y) i=j; }); } return i; }
function valuesOf(ly,d,y){
  const out={};
  if(d.series){ const sr=d.series[ly.series], i=yearIndex(d,y), pop=ly.per&&d.series[ly.per].values;
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
    L.choro={title:ly.title+(ly.showYear===false?"":" · "+ylab(y)),fmt:fmtOf(ly.fmt),log:ly.log,reverse:ly.reverse,values:v,nodata:ly.nodataLabel,
      vmin:ly.vmin,vmax:ly.vmax,diverging:ly.diverging,mid:ly.mid||0}; },
  symbols(ly,d,y,L){
    const items=Array.isArray(d.points)?pointValues(ly,d,y)
      :Object.entries(valuesOf(ly,d,y)).filter(([k,v])=>v>0&&ANCHOR.has(k)).map(([k,v])=>({id:k,name:nameOf(k),at:ANCHOR.get(k),v}));
    items.sort((a,b)=>b.v-a.v);
    const vmax=ly.vmax||(items[0]&&items[0].v)||1, R=ly.maxR||40, f=fmtOf(ly.fmt), n=ly.labels==null?6:ly.labels, c=ly.color||"c3";
    items.forEach((x,i)=>{ if(x.v<=0) return; L.symbols.push({at:x.at,r:Math.max(1.5,R*Math.sqrt(x.v/vmax)),color:c,label:i<n?x.name+" "+f(x.v):null}); });
    if(!Array.isArray(d.points)) L.vals.push({title:ly.title,values:Object.fromEntries(items.map(x=>[x.id,x.v])),fmt:f});
    if(ly.key!==false) L.sizeKey={color:c,title:ly.title};
  },
  flows(ly,d,y,L){
    const g=d.groups[ly.group]; if(!g) return;
    let fl=(g.flows[y]||[]).filter(r=>ANCHOR.has(r[0])&&ANCHOR.has(r[1]));
    if(ly.from) fl=fl.filter(r=>ly.from.includes(r[0]));
    if(ly.to) fl=fl.filter(r=>ly.to.includes(r[1]));
    if(focus) fl=fl.filter(r=>r[0]===focus||r[1]===focus);
    const m=ly.metric==="qty"?3:2;  // value (million USD) or quantity (thousand tonnes)
    fl=fl.sort((p,q)=>q[m]-p[m]).slice(0,ly.top||25);
    const vmax=ly.vmax||d3.max(fl,r=>r[m])||1, f=fmtOf(ly.fmt||"musd"), c=ly.color||"c3";
    fl.forEach(r=>{ const a=ANCHOR.get(r[0]), b=ANCHOR.get(r[1]), gi=d3.geoInterpolate(a,b);
      const n=Math.max(8,Math.ceil(d3.geoDistance(a,b)*deg/3));
      L.flows.push({path:d3.range(n+1).map(i=>gi(i/n)),width:0.8+(ly.maxW||9)*r[m]/vmax,color:c,to:b,a:r[0],b:r[1],v:r[m],fmt:f,title:ly.title||g.label}); });
    const title=ly.title||g.label;
    L.flowKeys.push({color:c,title,qty:m===3});
    const fv=m===3?FMT.musd:f;  // totals are always values; quantity layers still show them in USD
    L.vals.push({title:title+", exports",values:g.exports[y]||{},fmt:fv},{title:title+", imports",values:g.imports[y]||{},fmt:fv});
  },
  lines(ly,d,y,L){ (d.lines[ly.set]||[]).filter(x=>!ly.only||ly.only.includes(x.name)).forEach(x=>L.routes.push({path:x.path,color:ly.forceColor?ly.color:(x.color||ly.color),width:x.width||ly.width||2.2,
    dash:x.dash!=null?x.dash:(ly.dash!=null?ly.dash:!!x.status&&x.status!=="operating"),flow:ly.flow&&(!x.status||x.status==="operating"),
    label:ly.labels?x.name:null,labelAt:x.labelAt,dist:x.dist||ly.dist,until:x.until!=null?x.until:ly.until})); },
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
  since(ly,d,y,L){ // countries coloured from the year they joined/adopted; values: year or [from, until]
    const set=d.sets[ly.set]; if(!set) return; const yr=+y;
    const ids=Object.entries(set.members).filter(([k,v])=>{ const a=Array.isArray(v)?v[0]:v, b=Array.isArray(v)?v[1]:null; return a<=yr&&(b==null||yr<b); }).map(([k])=>k);
    // "titles": {"1958": "EEC", "1993": "EU"} switches the label by year; "{n}" becomes the member count
    let t=ly.title||set.label; if(ly.titles){ const k=Object.keys(ly.titles).map(Number).filter(a=>a<=yr).sort((a,b)=>b-a)[0]; if(k!=null) t=ly.titles[k]; }
    L.groups.push({label:t.replace("{n}",ids.length),color:ly.color||"c2",ids});
  },
  categories(ly,d,y,L){ // one fill colour per category; values: {ISO3: category}
    const set=d.sets[ly.set]; if(!set) return;
    const nm=ly.names&&(typeof ly.names[ly.set]==="object"?ly.names[ly.set]:ly.names); // story-side labels, e.g. translations
    Object.entries(ly.colors).forEach(([cat,c])=>L.groups.push({label:(nm&&nm[cat])||(set.labels&&set.labels[cat])||cat,color:c,
      ids:Object.entries(set.values).filter(([k,v])=>v===cat).map(([k])=>k)}));
  },
  events(ly,d,y,L){ // many dated points: cumulative up to the timeline year, or a moving window
    const t=+y, w=ly.window, ev=d.events, vmax=ly.vmax||d3.max(ev,e=>e[3])||1;
    const r=v=>ly.scale==="mag"?(ly.minR||1.2)+(ly.maxR||16)*Math.sqrt(Math.pow(10,0.75*(v-(ly.base||6)))/Math.pow(10,0.75*(vmax-(ly.base||6)))):(ly.minR||1.2)+((ly.maxR||14)-(ly.minR||1.2))*Math.sqrt(v/vmax);
    const pick=ev.filter(e=>w==="all"?true:w?(e[2]<=t&&e[2]>t-w):e[2]<=t);
    L.events.push({pts:pick.map(e=>({at:[e[0],e[1]],r:r(e[3]),now:e[2]===t,v:e[3]})),color:ly.color||"c2",title:ly.title||d.vLabel,count:pick.length,fmt:fmtOf(ly.fmt)});
  },
  borders(ly,d,y,L){ // historical state borders: the latest snapshot at or before the year
    const yrs=Object.keys(d.snapshots||d.files).map(Number).sort((a,b)=>a-b), yr=+y;
    const snap=yrs.filter(v=>v<=yr).pop()||yrs[0], H=histSnap(ly.data,d,snap); if(!H) return;
    L.hist={H,year:snap,labels:ly.labels!==false};
  },
  regions(ly,d,y,L){ // sub-national areas (admin-1) of one country, coloured by a series keyed by region id
    const R=regionGeo(ly.country); if(!R) return;
    const sr=d.series[ly.series], i=yearIndex(d,y); if(!sr||i<0) return;
    const vals={}; Object.entries(sr.values).forEach(([k,a])=>{ if(a[i]!=null) vals[k]=a[i]*(ly.mult||1); });
    const v=Object.values(vals), lo=d3.min(v), hi=d3.max(v);
    const sc=ly.log?d3.scaleLog().domain([Math.max(lo,1e-9),hi]):d3.scaleLinear().domain([lo,hi]);
    L.regions.push({R,vals,color:x=>C.seq(clamp(sc(x),0,1)),lo,hi,title:ly.title+" · "+ylab(y),fmt:fmtOf(ly.fmt),labels:ly.labels});
  },
  pov(ly,d,y,L){ // disputed areas as one country sees them: filled with the owner's tint, outlined dashed
    if(!d._areas) d._areas=topojson.feature(d.areas,d.areas.objects.areas).features;
    const view=ly.view; L.pov={areas:d._areas,view,viewIso:d.views[view]||view,only:ly.areas};
  },
  particles(ly,d,y,L){ // animated particles advected by a u/v wind field
    const F=vectorField(ly.data,d); if(!F) return; L.particles={F,color:ly.color||"ink",count:ly.count||2600,speed:ly.speed||1};
  },
  raster(ly,d,y,L){ // a lon/lat grid; frames keyed by label (a year for timelines)
    const lab=String(ly.frame!=null&&ly.frame!=="t"?ly.frame:((frame&&frame.year)||Object.keys(d.frames).pop()));
    const G=gridFrame(ly.data,d,lab); if(!G) return;
    L.rasters.push({tex:G.tex,alpha:ly.opacity==null?0.9:ly.opacity,G,desc:d,title:ly.title||d.units,fmt:fmtOf(ly.fmt)});
  },
  points(ly,d,y,L){ (d.points[ly.set]||[]).filter(x=>!ly.only||ly.only.includes(x.name)).forEach(x=>L.points.push({at:x.at,label:ly.labels===false?null:x.name,color:ly.forceColor?ly.color:(x.color||ly.color),r:x.r||ly.r||4.5})); }
};
// tapping a country in a flows scene shows only that country's flows
let focus=null;
// a scene "switch" (e.g. pick a commodity) fills {placeholders} in its layers, chart and text
let switchIdx=0;
const switchOpt=()=>scene&&scene.switch?scene.switch.options[switchIdx]:null;
function subst(o){ const op=switchOpt(); if(!op||o==null) return o;
  return JSON.parse(JSON.stringify(o).replace(/\{(\w+)\}/g,(m,k)=>op[k]!=null?String(op[k]).replace(/["\\]/g,"\\$&"):m)); }
function compileLayers(s,L){
  const st=si>=0?STORIES[si]:null, D=(st&&st._data)||{};
  (subst(s.layers)||[]).forEach(ly=>{ const d=D[ly.data], fn=LAYER[ly.type]; if(!d||!fn) return;
    const y=(ly.year==null||ly.year==="t")?((frame&&frame.year)||lastYear(d)||new Date().getFullYear()):ly.year;
    fn(ly,d,y,L); });
}
function renderMedia(){
  const m=scene&&scene.media, st=si>=0?STORIES[si]:null;
  if(!m||!m.length){ el.media.hidden=true; el.media.innerHTML=""; return; }
  el.media.innerHTML=m.map(x=>{
    if(x.type==="image") return `<figure class="md-img"><img src="${esc(x.src)}" alt="${esc(x.alt||"")}" loading="lazy"><figcaption>${esc(x.caption||"")} <span class="md-credit">${x.href?`<a href="${esc(x.href)}" target="_blank" rel="noopener">${esc(x.credit||"Source")}</a>`:esc(x.credit||"")}${x.licence?" · "+esc(x.licence):""}</span></figcaption></figure>`;
    if(x.type==="quote") return `<blockquote class="md-quote"><p>${esc(x.text)}</p>${x.by?`<footer>${esc(x.by)}</footer>`:""}</blockquote>`;
    if(x.type==="line"){ const d=st&&st._data&&st._data[x.data]; if(!d||!d.series) return "";
      // x positions: plain years, or yyyymm / yyyymmdd numbers (dataset "format": "month" | "date") as fractional years
      const fm=d.format, xv=y=>fm==="month"?Math.floor(y/100)+(y%100-1)/12:fm==="date"?Math.floor(y/1e4)+(Math.floor(y/100)%100-1)/12+(y%100-1)/365:y;
      const mon=LANG==="de"?["Jan.","Feb.","März","Apr.","Mai","Juni","Juli","Aug.","Sept.","Okt.","Nov.","Dez."]:["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
      const ylb=y=>fm==="month"?mon[y%100-1]+" "+Math.floor(y/100):fm==="date"?fmtDate(y):String(y);
      const sr=d.series[x.series], ys0=d.years, ys=ys0.map(xv), w=330, h=120, pad=[8,46,18,4];
      const lines=(x.countries||[]).map((c,i)=>({c,label:x.labels&&x.labels[c],col:col(["c1","c2","c3","c4","c5"][i%5]),pts:ys.map((y,j)=>[y,sr.values[c]?sr.values[c][j]:null]).filter(p=>p[1]!=null)})).filter(l=>l.pts.length);
      const all=lines.flatMap(l=>l.pts); if(!all.length) return "";
      const sx=d3.scaleLinear().domain(d3.extent(ys)).range([pad[3],w-pad[1]]), sy=d3.scaleLinear().domain([Math.min(0,d3.min(all,p=>p[1])),d3.max(all,p=>p[1])]).nice().range([h-pad[2],pad[0]]);
      const f=fmtOf(x.fmt), ln=d3.line().x(p=>sx(p[0])).y(p=>sy(p[1]));
      return `<figure class="md-line"><figcaption>${esc(x.title||sr.label)}</figcaption><svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${esc(x.title||sr.label)}">`+
        sy.ticks(3).map(t=>`<line x1="${pad[3]}" x2="${w-pad[1]}" y1="${sy(t)}" y2="${sy(t)}" class="md-grid"/><text x="${w-pad[1]+4}" y="${sy(t)+4}" class="md-tick">${esc(f(t))}</text>`).join("")+
        `<text x="${pad[3]}" y="${h-3}" class="md-tick">${esc(ylb(ys0[0]))}</text><text x="${w-pad[1]}" y="${h-3}" class="md-tick" text-anchor="end">${esc(ylb(ys0[ys0.length-1]))}</text>`+
        lines.map(l=>`<path d="${ln(l.pts)}" fill="none" stroke="${l.col}" stroke-width="2"/>`).join("")+
        // end labels (only when there is more than one line), pushed apart so they do not overlap
        (lines.length>1?(()=>{ const lb=lines.map(l=>({l,y:sy(l.pts[l.pts.length-1][1])-5})).sort((a,b)=>a.y-b.y);
          for(let i=1;i<lb.length;i++) if(lb[i].y-lb[i-1].y<11) lb[i].y=lb[i-1].y+11;
          return lb.map(({l,y})=>`<text x="${sx(l.pts[l.pts.length-1][0])-2}" y="${Math.min(y,h-pad[2]-2)}" class="md-lab" fill="${l.col}" text-anchor="end">${esc(l.label||nameOf(l.c))}</text>`).join(""); })():"")+`</svg></figure>`; }
    return ""; }).join("");
  el.media.hidden=false;
}
function renderChart(){
  const c=subst(scene&&scene.chart), st=si>=0?STORIES[si]:null, d=c&&st&&st._data&&st._data[c.data];
  if(!d){ el.chart.hidden=true; return; }
  const y=(c.year==null||c.year==="t")?((frame&&frame.year)||lastYear(d)):c.year;
  let rows=Array.isArray(d.points)?pointValues(c,d,y).map(p=>[p.name,p.v]):Object.entries(valuesOf(c,d,y)).map(([k,v])=>[nameOf(k),v]);
  rows=rows.filter(r=>c.order==="asc"?r[1]!=null:r[1]>0).sort((a,b)=>c.order==="asc"?a[1]-b[1]:b[1]-a[1]);
  let f=fmtOf(c.fmt);
  if(c.share){ // show each country's share of the world total (dataset's own world figure when it has one)
    const w=d.world&&d.world[c.series], tot=(w&&w[yearIndex(d,y)])||d3.sum(rows,r=>r[1]);
    rows=rows.map(r=>[r[0],r[1]/tot*100]); f=FMT.pct; }
  rows=rows.slice(0,c.top||8);
  const mx=rows.length?d3.max(rows,r=>Math.abs(r[1])):1;
  el.chart.innerHTML=`<div class="ch-title">${esc(c.title)}${c.period||y?" · "+esc(String(c.period||ylab(y))):""}</div>`+
    rows.map(([n,v])=>`<div class="ch-row"><span class="nm">${esc(n)}</span><span class="bar" style="width:${(v/mx*100).toFixed(1)}%;background:${col(c.color||"c3")}"></span><span class="v">${esc(f(v))}</span></div>`).join("");
  el.chart.hidden=false;
}

function renderSwitch(){
  const sw=scene&&scene.switch, box=el.sw;
  if(!sw){ box.hidden=true; return; }
  box.innerHTML=`<span class="sw-label">${esc(sw.label||t("Show"))}</span>`+sw.options.map((o,i)=>`<button class="bloc" data-i="${i}" aria-pressed="${String(i===switchIdx)}">${esc(o.label)}</button>`).join("");
  [...box.querySelectorAll("button")].forEach(b=>b.onclick=()=>{ switchIdx=+b.dataset.i; cartoStart=performance.now()-900; renderSwitch();
    const op=switchOpt(); el.text.textContent=op.text||scene.text; L=layers(); el.legend.innerHTML=legendHTML(); renderChart(); renderData(); render(); });
  box.hidden=false;
  const op=switchOpt(); if(op&&op.text) el.text.textContent=op.text;
}

// ---------- tools: save image, record video, share, embed ----------
function composite(cv,g){ // raster + vector canvases plus a caption strip
  draw(); const w=canvas.width,h=canvas.height; if(cv.width!==w||cv.height!==h){cv.width=w;cv.height=h;}
  g.fillStyle=getComputedStyle(document.body).backgroundColor; g.fillRect(0,0,w,h);
  g.drawImage(document.getElementById("raster"),0,0,w,h); g.drawImage(canvas,0,0,w,h);
  const st=si>=0?STORIES[si]:null, title=st&&scene?st.title+" · "+scene.title:t("The world, your way");
  const credit="Orbis · "+t("Data")+": "+sourceIds().map(id=>SOURCES[id].name).join(", ");
  const fs=Math.round(15*DPR); g.font=`600 ${fs*1.25}px 'Source Serif 4', Georgia, serif`;
  g.fillStyle="rgba(250,248,243,.92)"; g.fillRect(0,h-fs*4.2,w,fs*4.2);
  g.fillStyle="#1D2A30"; g.fillText(title,fs,h-fs*2.4); g.font=`${fs*0.85}px 'Barlow Semi Condensed', sans-serif`; g.fillStyle="#4C5B61"; g.fillText(credit,fs,h-fs*0.9);
}
function download(blob,name){ const a=document.createElement("a"); a.href=URL.createObjectURL(blob); a.download=name; document.body.appendChild(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(a.href),4000); }
const fileBase=()=>"orbis-"+(si>=0?STORIES[si].id.replace(/[^a-z0-9-]/gi,"")+"-"+(ci+1):"map");
function saveImage(){ const cv=document.createElement("canvas"), g=cv.getContext("2d"); composite(cv,g); cv.toBlob(b=>download(b,fileBase()+".png"),"image/png"); }
let rec=null;
function toggleRecord(btn){
  if(rec){ rec.stop(); return; }
  const cv=document.createElement("canvas"), g=cv.getContext("2d"); composite(cv,g);
  const stream=cv.captureStream(30), mime=["video/webm;codecs=vp9","video/webm","video/mp4"].find(m=>window.MediaRecorder&&MediaRecorder.isTypeSupported(m));
  if(!mime) return;
  const chunks=[], r=new MediaRecorder(stream,{mimeType:mime,videoBitsPerSecond:6e6}); rec=r;
  r.ondataavailable=e=>e.data.size&&chunks.push(e.data);
  r.onstop=()=>{ rec=null; btn.textContent=t("Record video"); btn.classList.remove("rec"); download(new Blob(chunks,{type:mime}),fileBase()+(mime.includes("mp4")?".mp4":".webm")); };
  r.start(); btn.textContent=t("Stop recording"); btn.classList.add("rec");
  const t0=performance.now(); let tl=scene&&scene.timeline;
  if(tl){ tlIdx=0; setFrame(); if(!playing) el.play.click(); }
  (function loop(){ if(!rec) return; composite(cv,g); const done=tl?(!playing&&performance.now()-t0>1500):performance.now()-t0>8000;
    if(done||performance.now()-t0>60000) r.stop(); else requestAnimationFrame(loop); })();
}
function shareUrl(embed){ const u=new URL(location.href); u.searchParams.delete("embed"); if(embed) u.searchParams.set("embed","1"); if(LANG!=="en") u.searchParams.set("lang",LANG); return u.toString(); }
function copy(text,btn){ (navigator.clipboard?navigator.clipboard.writeText(text):Promise.reject()).then(()=>{ const o=btn.textContent; btn.textContent=t("Copied"); setTimeout(()=>btn.textContent=o,1500); }).catch(()=>prompt("",text)); }
function renderTools(){
  const box=$("sTools"); if(!box) return;
  box.innerHTML=`<button data-a="img">${t("Save image")}</button>`+(window.MediaRecorder?`<button data-a="rec">${t("Record video")}</button>`:"")+
    `<button data-a="link">${t("Copy link")}</button><button data-a="embed">${t("Copy embed code")}</button>`;
  box.querySelector('[data-a="img"]').onclick=saveImage;
  const rb=box.querySelector('[data-a="rec"]'); if(rb) rb.onclick=()=>toggleRecord(rb);
  box.querySelector('[data-a="link"]').onclick=e=>copy(shareUrl(false),e.target);
  box.querySelector('[data-a="embed"]').onclick=e=>{ const st=si>=0?STORIES[si]:null;
    copy(`<iframe src="${shareUrl(true)}" title="${esc(st?st.title:"Orbis")}" width="100%" height="620" style="border:0;border-radius:12px" loading="lazy" allow="fullscreen"></iframe>`,e.target); };
}

// ---------- screen-reader description of what the map shows ----------
function describe(){
  if(!L) return; const parts=[], top=(vals,f,n=3)=>Object.entries(vals||{}).sort((a,b)=>b[1]-a[1]).slice(0,n).map(([k,v])=>nameOf(k)+" "+f(v)).join(", ");
  const vw=(scene&&scene.view)||{mode:curKind(),center:V.center}, mode=vw.mode==="globe"?"Globe":"Flat map";
  parts.push(mode+" centred near "+Math.round(vw.center[1])+"° latitude, "+Math.round(vw.center[0])+"° longitude.");
  if(L.symbols.some(x=>x.label)) parts.push("Circles: "+L.symbols.filter(x=>x.label).slice(0,4).map(x=>x.label).join(", ")+".");
  if(L.spikes.some(x=>x.label)) parts.push("Towers: "+L.spikes.filter(x=>x.label).slice(0,4).map(x=>x.label).join(", ")+".");
  if(L.choro) parts.push("Countries coloured by "+L.choro.title+"; highest: "+top(L.cdata,L.choro.fmt)+".");
  L.vals.forEach(v=>parts.push(v.title+"; largest: "+top(v.values,v.fmt)+"."));
  if(L.flows.length){ const f=L.flows.slice().sort((a,b)=>b.v-a.v).slice(0,3); parts.push("Lines show "+f[0].title+": "+f.map(x=>nameOf(x.a)+" to "+nameOf(x.b)+" "+x.fmt(x.v)).join("; ")+"."); }
  if(L.groups.length) L.groups.forEach(g=>parts.push(g.label+": "+g.ids.length+" countries highlighted."));
  if(L.routes.length) parts.push(L.routes.length+" routes drawn"+(L.routes.some(r=>r.label)?": "+L.routes.filter(r=>r.label).slice(0,5).map(r=>r.label).join(", "):"")+".");
  if(L.points.length) parts.push("Places marked: "+L.points.filter(p=>p.label).slice(0,8).map(p=>p.label).join(", ")+".");
  if(L.rasters.length) parts.push("A colour grid shows "+L.rasters.map(r=>r.title).join(", ")+"; tap the map to read values.");
  if(L.hist) parts.push("Borders as of "+L.hist.year+".");
  const txt=parts.join(" "); $("srDesc").textContent=txt; canvas.setAttribute("aria-label",(scene&&scene.title?scene.title+". ":"")+txt);
}

// ---------- quiz ----------
const quiz={mode:null,score:0,streak:0,q:null};
async function openQuiz(){
  si=-1; scene={layers:[],fills:{},political:true,view:{mode:"equal",center:[15,20],zoom:1}}; frame=null; closeToc(); stopPlay(); sheet.classList.remove("collapsed");
  el.tl.hidden=true; el.steps.hidden=true; el.notes.hidden=true; el.blocs.hidden=true; el.sw.hidden=true; el.chart.hidden=true; el.media.hidden=true; el.camp.hidden=true; el.updated.hidden=true;
  history.replaceState(null,"","#quiz"); el.kicker.textContent=t("Quiz");
  const d=await loadJSON("data/energy/eia.json"); const i=d.years.indexOf(2024), pop=d.series.pop.values;
  quiz.pop=Object.entries(pop).filter(([k,v])=>v[i]>2000&&byId.has(k)).map(([k,v])=>[k,v[i]*1000]);
  nextQuestion();
}
function nextQuestion(){
  const P=quiz.pop, pick=()=>P[Math.floor(Math.random()*P.length)];
  quiz.mode=Math.random()<0.5?"more":"where";
  if(quiz.mode==="more"){ let a=pick(), b=pick(); while(b[0]===a[0]||Math.max(a[1],b[1])/Math.min(a[1],b[1])<1.25) b=pick();
    quiz.q={a,b}; scene.fills={[a[0]]:"c1",[b[0]]:"c2"}; scene.countryLabels=false;
    el.title.textContent=t("Which has more people?"); el.text.textContent="";
    const mid=d3.geoInterpolate(ANCHOR.get(a[0]),ANCHOR.get(b[0]))(0.5), dist=d3.geoDistance(ANCHOR.get(a[0]),ANCHOR.get(b[0]));
    flyTo({mode:"globe",center:mid,zoom:clamp(1.6/Math.max(dist,0.5),1,4)});
    quizUI([a,b].map(([k])=>`<button data-k="${k}">${esc(nameOf(k))}</button>`).join(""));
    [...el.legend.querySelectorAll("button[data-k]")].forEach(btn=>btn.onclick=()=>quizAnswer(btn.dataset.k));
  } else { const a=pick(); quiz.q={a}; scene.fills={}; scene.countryLabels=false;
    el.title.textContent=t("Where is {x}?",{x:nameOf(a[0])}); el.text.textContent=t("Tap the country on the map.");
    flyTo({mode:"equal",center:[15,20],zoom:1}); quizUI(""); }
  markDirty(); render();
}
function quizUI(buttons,feedback=""){
  el.legend.innerHTML=`<div class="qz-score">${t("Score")}: ${quiz.score} · ${t("{n} in a row",{n:quiz.streak})}</div><div class="qz">${buttons}</div>${feedback}`;
}
function quizResult(ok,extra){
  if(ok){quiz.score++;quiz.streak++;} else quiz.streak=0;
  el.text.textContent=(ok?t("Right!"):t("Not quite."))+" "+extra;
  quizUI(`<button id="qzNext">${t("Next question")}</button>`); $("qzNext").onclick=nextQuestion;
}
function quizAnswer(k){ const {a,b}=quiz.q, win=a[1]>b[1]?a[0]:b[0], f=d3.format(",.0f");
  quizResult(k===win, nameOf(a[0])+": "+f(a[1]/1e6)+" "+t(" m").trim()+", "+nameOf(b[0])+": "+f(b[1]/1e6)+" "+t(" m").trim()+"."); }
function quizTap(id){ const a=quiz.q.a[0]; scene.fills={[a]:"c4"}; if(id!==a) scene.fills[id]="c2"; markDirty();
  quizResult(id===a, id===a?"":t("That was {x}.",{x:nameOf(id)})); quiz.mode="done"; flyTo({mode:"globe",center:ANCHOR.get(a),zoom:2}); }

// ---------- your city in the world ----------
const HUBS=[["London",-0.13,51.51],["New York",-74.0,40.71],["Tokyo",139.69,35.69],["Beijing",116.4,39.9],["Delhi",77.21,28.61],["São Paulo",-46.63,-23.55],
  ["Lagos",3.38,6.52],["Sydney",151.21,-33.87],["Moscow",37.62,55.76],["Cairo",31.24,30.04],["Mexico City",-99.13,19.43],["Johannesburg",28.05,-26.2]];
async function openCity(){
  si=-1; scene={layers:[],routes:[],points:[],countryLabels:true,political:true,view:{mode:"globe",center:[15,30],zoom:1}}; frame=null; closeToc(); stopPlay(); sheet.classList.remove("collapsed");
  el.tl.hidden=true; el.steps.hidden=true; el.notes.hidden=true; el.blocs.hidden=true; el.sw.hidden=true; el.chart.hidden=true; el.media.hidden=true; el.camp.hidden=true; el.updated.hidden=true;
  history.replaceState(null,"","#city"); el.kicker.textContent=t("Your city"); el.title.textContent=t("Find your city");
  el.text.textContent=t("How far is everything from where you are? Pick a city, or use your location.");
  const d=await loadJSON("data/geo/places.json"); const P=d.places;
  el.legend.innerHTML=`<div class="city"><input id="cityIn" list="cityList" placeholder="${esc(t("Type a city"))}" autocomplete="off"><button id="cityGeo">${t("Use my location")}</button></div>
    <datalist id="cityList">${P.map(p=>`<option value="${esc(p[0]+", "+nameOf(p[1]))}">`).join("")}</datalist><ul class="city-list" id="cityOut"></ul>`;
  $("cityIn").onchange=()=>{ const v=$("cityIn").value, p=P.find(p=>p[0]+", "+nameOf(p[1])===v)||P.find(p=>p[0].toLowerCase()===v.toLowerCase()); if(p) showCity(p[0],[p[2],p[3]]); };
  $("cityGeo").onclick=()=>navigator.geolocation?navigator.geolocation.getCurrentPosition(pos=>showCity(t("your location"),[pos.coords.longitude,pos.coords.latitude]),()=>{$("cityOut").textContent=t("Location not available");}):null;
}
function showCity(name,at){
  const km=b=>Math.round(d3.geoDistance(at,b)*R_EARTH), hubs=HUBS.filter(h=>km([h[1],h[2]])>150).map(h=>({n:h[0],at:[h[1],h[2]],d:km([h[1],h[2]])}));
  const anti=[at[0]>0?at[0]-180:at[0]+180,-at[1]], af=f0(anti);
  scene.routes=hubs.map(h=>({path:[at,h.at],color:"c1",width:1.6,label:h.n,labelAt:1,dist:false}));
  scene.points=[{at,label:name,color:"c2",r:6},{at:anti,label:"↧ "+(af?nameOf(af.id):t("the open ocean")),color:"muted",r:4}];
  scene.circles=[]; markDirty(); flyTo({mode:"globe",center:at,zoom:1.05});
  el.title.textContent=t("Distances from {x}",{x:name});
  el.text.textContent=t("Directly through the Earth from {x} lies {y}.",{x:name,y:af?nameOf(af.id):t("the open ocean")});
  $("cityOut").innerHTML=hubs.sort((a,b)=>a.d-b.d).map(h=>`<li><span>${esc(h.n)}</span><span>${d3.format(",")(Math.round(h.d/10)*10)} km</span></li>`).join("");
  describe(); render();
}

// ---------- panel ----------
const $=id=>document.getElementById(id);
const el={kicker:$("sKicker"),title:$("sTitle"),text:$("sText"),legend:$("sLegend"),tl:$("sTimeline"),slider:$("tlSlider"),year:$("tlYear"),play:$("tlPlay"),cap:$("tlCaption"),
  prev:$("prev"),next:$("next"),dots:$("dots"),notes:$("sNotes"),notesBody:$("sNotesBody"),blocs:$("blocs"),steps:$("steps"),data:$("sData"),chart:$("sChart"),sw:$("sSwitch"),media:$("sMedia"),camp:$("sCamp"),updated:$("sUpdated")};
let si=-1, ci=0, tlIdx=0, playing=null;
const explore={bloc:null};

function legendHTML(){
  const s=scene; if(!s){ if(explore.bloc) return chip("c2",t(BLOCS[explore.bloc].label)); return ""; }
  let h="";
  if(s.legend) h+=s.legend.map(l=>chip(l.color,l.label)).join("");
  else if(L&&L.groups.length) h+=L.groups.map(g=>chip(g.color,g.label)).join("");
  if(L) L.flowKeys.forEach(k=>h+=chip(k.color,k.title+" · "+t(k.qty?"line width = tonnes":"line width = value")));
  if(L&&L.flowKeys.length) h+=`<span class="chip">${focus?esc(t("Showing {x} only · tap it again for all",{x:nameOf(focus)})):esc(t("Tap a country to see only its flows"))}</span>`;
  if(L&&L.spikeKey) h+=chip(L.spikeKey.color,L.spikeKey.title+" · "+t("tower height = amount"));
  if(L&&L.cartoKey) h+=chip(L.cartoKey.color,L.cartoKey.title+" · "+t("country size = amount"));
  if(L&&L.sizeKey) h+=`<span class="size-key" style="color:${col(L.sizeKey.color)}"><i style="width:16px;height:16px"></i><span style="color:var(--ink-soft)">${esc(L.sizeKey.title)} · ${t("circle area = amount")}</span></span>`;
  if(L) L.regions.forEach(rg=>{ const stops=d3.range(0,1.01,0.1).map(t=>C.seq(t)).join(",");
    h+=`<div class="ramp"><div class="ramp-title">${esc(rg.title)}</div><div class="ramp-bar" style="background:linear-gradient(90deg,${stops})"></div><div class="ramp-ends"><span>${esc(rg.fmt(rg.lo))}</span><span>${esc(rg.fmt(rg.hi))}</span></div></div>`; });
  if(L&&L.pov) h+=`<span class="chip"><i style="background:none;border:1.5px dashed ${C.accent}"></i>${esc(t("Disputed areas, drawn as seen from {x}",{x:nameOf(L.pov.viewIso)}))}</span>`;
  if(L) L.events.forEach(E=>h+=chip(E.color,E.title+" · "+t("{n} shown",{n:d3.format(",")(E.count)})));
  if(L&&L.hist) h+=`<span class="chip">${esc(t("Borders as of {y}",{y:L.hist.year}))}</span>`;
  if(L&&L.particles) h+=`<span class="chip">${esc(t("Each streak is a parcel of air; bright = faster than 35 m/s"))}</span>`;
  if(L) L.rasters.forEach(r=>{ const e=r.desc.encoding, lut=gridPalette(r.desc.palette);
    const stops=d3.range(1,256,25).map(i=>`rgb(${lut[i*4]},${lut[i*4+1]},${lut[i*4+2]})`).join(",");
    h+=`<div class="ramp"><div class="ramp-title">${esc(r.title)}</div><div class="ramp-bar" style="background:linear-gradient(90deg,${stops})"></div><div class="ramp-ends"><span>${esc(r.fmt(e.min))}</span><span>${esc(r.fmt(e.max))}</span></div></div>`; });
  const ch=L&&L.choro;
  if(ch){const stops=d3.range(0,1.01,0.1).map(t=>L.ramp?L.ramp(t):C.seq(ch.reverse?1-t:t)).join(",");
    const f=ch.fmt||(x=>x);
    h+=`<div class="ramp"><div class="ramp-title">${esc(ch.title)}</div><div class="ramp-bar" style="background:linear-gradient(90deg,${stops})"></div><div class="ramp-ends"><span>${esc(String(f(L.lo)))}</span><span>${esc(String(f(L.hi)))}</span></div><div class="ramp-na"><i style="background:${C.nodata}"></i>${esc(ch.nodata||(ch.data==="POWER"?"Near-universal access":t("No data")))}</div></div>`;}
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
  el.data.innerHTML='<span class="dl">'+t("Data")+'</span>'+sourceIds().map(id=>{const s=SOURCES[id];
    return `<button class="src ${useCls(s.use)}" data-src="${id}" title="${esc(t(USE_LABEL[s.use]))}"><b>${esc(s.name)}</b>${esc(s.licence)}</button>`;}).join("")+
    '<button id="licAll">'+t("All licences")+'</button>';
  [...el.data.querySelectorAll("[data-src]")].forEach(b=>b.onclick=()=>openLic(b.dataset.src));
  $("licAll").onclick=()=>openLic();
}
const lic=$("lic");
function openLic(focusId){
  const tiers=[["base",t("Base map and engine (commercial use required)")],["layer",t("Story layers")]];
  $("licList").innerHTML=tiers.map(([t,h])=>`<section class="lic-tier"><h2>${h}</h2>`+
    Object.entries(SOURCES).filter(([,s])=>s.tier===t).map(([id,s])=>`<div class="lic-item" id="lic-${id}"><span class="n">${esc(s.name)}</span><span class="w">${esc(s.what)}</span>
      <span class="l"><span>${s.licenceUrl?`<a href="${esc(s.licenceUrl)}" target="_blank" rel="noopener">${esc(s.licence)}</a>`:esc(s.licence)}</span>
      <span class="lic-use ${useCls(s.use)}">${esc(t(USE_LABEL[s.use]))}</span>${s.url?`<a href="${esc(s.url)}" target="_blank" rel="noopener">${t("Source")}</a>`:""}</span>
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
function stopPlay(){ if(playing){clearInterval(playing);playing=null;} el.play.textContent=t("Play"); el.play.setAttribute("aria-label",t("Play timeline")); }
el.play.onclick=()=>{ if(playing){stopPlay();return;} const t=scene.timeline; if(tlIdx>=t.years.length-1) tlIdx=0;
  el.play.textContent=t("Pause"); el.play.setAttribute("aria-label",t("Pause timeline"));
  playing=setInterval(()=>{ if(tlIdx>=t.years.length-1){stopPlay();return;} tlIdx++; setFrame(); }, t.years.length>30?(reduce?400:160):(reduce?1600:1100)); };
el.slider.oninput=()=>{stopPlay();tlIdx=+el.slider.value;setFrame();};

function showScene(i, fly=true){
  const st=STORIES[si]; ci=clamp(i,0,st.scenes.length-1); scene=st.scenes[ci]; stopPlay();
  const cp=campaignOf(st); el.camp.hidden=true;
  if(cp){ const k=cp.chapters.indexOf(st.id);
    el.kicker.innerHTML=`<button class="kick-camp" title="${esc(t("All chapters"))}">${esc(cp.title)}</button> · ${esc(t("Chapter {n} of {m}",{n:k+1,m:cp.chapters.length}))}: ${esc(st.title)}`;
    el.kicker.querySelector("button").onclick=()=>openCampaign(cp.id); }
  else el.kicker.textContent=st.title;
  el.title.textContent=scene.title; el.text.textContent=scene.text;
  el.updated.hidden=!st.updated; if(st.updated) el.updated.textContent=t("Updated {d}",{d:fmtDate(st.updated)});
  markRead(st.id,ci,st.scenes.length);
  el.blocs.hidden=true; el.steps.hidden=false; el.notes.hidden=false;
  if(scene.timeline){el.tl.hidden=false;tlIdx=scene.timeline.start||0;el.slider.max=scene.timeline.years.length-1;}
  else el.tl.hidden=true;
  markDirty(); focus=null; switchIdx=(scene.switch&&scene.switch.start)||0; cartoStart=performance.now(); renderSwitch();
  frame=null; setFrame(); L=layers(); el.legend.innerHTML=legendHTML(); renderChart(); renderMedia(); renderTools(); describe();
  el.dots.innerHTML=st.scenes.map((s,j)=>`<button class="dot" aria-label="${t("Scene")} ${j+1}: ${esc(s.title)}" ${j===ci?'aria-current="step"':""}></button>`).join("");
  [...el.dots.children].forEach((b,j)=>b.onclick=()=>showScene(j));
  el.prev.disabled=ci===0 && si===0;
  el.prev.textContent=ci===0?t("Previous story"):t("Back");
  const lastS=ci===st.scenes.length-1; el.next.textContent=lastS?(cp?(nextChapter(st,1)>=0?t("Next chapter"):t("All chapters")):si<STORIES.length-1?t("Next story"):t("All stories")):t("Next");
  if(cp&&ci===0){ el.prev.disabled=false; el.prev.textContent=nextChapter(st,-1)>=0?t("Previous chapter"):t("All chapters"); }
  el.notesBody.textContent=(st._translated&&!st.reviewed?t("Machine translation, not yet reviewed.")+" ":"")+st.notes; el.notes.open=false; renderData();
  history.replaceState(null,"","#"+st.id+"/"+(ci+1));
  setBasemap(scene.basemap||BM.user||"political",false);
  syncMode(scene.view.mode); spin=false;
  if(fly) flyTo(scene.view);
  sheet.scrollTop=0; render();
}
el.next.onclick=()=>{ const st=STORIES[si], cp=campaignOf(st); if(ci<st.scenes.length-1) return showScene(ci+1);
  if(cp){ const n=nextChapter(st,1); return n>=0?openStory(n):openCampaign(cp.id); }
  const n=STORIES.findIndex((x,i)=>i>si&&!campaignOf(x)); if(n>=0) openStory(n); else openToc(); };
el.prev.onclick=()=>{ const st=STORIES[si], cp=campaignOf(st); if(ci>0) return showScene(ci-1);
  if(cp){ const n=nextChapter(st,-1); return n>=0?openStory(n,"last"):openCampaign(cp.id); }
  const p=STORIES.map((x,i)=>i<si&&!campaignOf(x)?i:-1).filter(i=>i>=0).pop(); if(p!=null) openStory(p,"last"); };

let opening=0;
async function openStory(i, scn=0){
  quiz.mode=null; const tok=++opening; si=i; closeToc(); sheet.classList.remove("collapsed"); BM.user=null;
  if(!STORIES[i].scenes){
    el.kicker.textContent=STORIES[i].title; el.title.textContent=t("Loading…"); el.text.textContent=""; el.chart.hidden=true; sheet.classList.add("loading");
    try{ await ensureStory(i); }
    catch(e){ sheet.classList.remove("loading"); if(tok===opening){ el.title.textContent=t("This story could not load"); el.text.textContent=String(e.message||e); } return; }
    sheet.classList.remove("loading"); if(tok!==opening) return;
  }
  showScene(scn==="last"?STORIES[i].scenes.length-1:scn);
}
function openExplore(){
  quiz.mode=null; si=-1; scene=null; frame=null; markDirty(); closeToc(); stopPlay(); sheet.classList.remove("collapsed"); el.chart.hidden=true; el.sw.hidden=true; el.media.hidden=true; el.camp.hidden=true; el.updated.hidden=true;
  el.kicker.textContent=t("Explore"); el.title.textContent=t("The world, your way");
  el.text.textContent=t("Drag to turn the world, pinch or scroll to zoom, tap a country to see its name. Switch between political, satellite and night views with the map button. Show a group of countries:");
  el.tl.hidden=true; el.steps.hidden=true; el.notes.hidden=true; el.blocs.hidden=false;
  renderBlocs(); renderData(); el.legend.innerHTML=legendHTML(); history.replaceState(null,"","#explore");
  syncMode(curKind()); render();
}
function renderBlocs(){
  el.blocs.innerHTML=[["",{label:t("None")}],...Object.entries(BLOCS).map(([k,b])=>[k,{label:t(b.label)}])].map(([k,b])=>`<button class="bloc" data-k="${k}" aria-pressed="${String((explore.bloc||"")===k)}">${esc(b.label)}</button>`).join("");
  [...el.blocs.children].forEach(b=>b.onclick=()=>{explore.bloc=b.dataset.k||null;renderBlocs();L=layers();el.legend.innerHTML=legendHTML();render();});
}

// ---------- campaigns: a series of stories with a landing page, chapter order and reading progress ----------
let CAMPAIGNS=[];
const campaignOf=st=>st&&CAMPAIGNS.find(c=>c.chapters.includes(st.id.replace(/^@stories\/|\.json$/g,"")));
const storyIndex=id=>STORIES.findIndex(s=>s.id===id);
// index of the next (dir 1) or previous (dir -1) chapter that exists, or -1
function nextChapter(st,dir){ const cp=campaignOf(st); if(!cp) return -1; let k=cp.chapters.indexOf(st.id)+dir;
  while(k>=0&&k<cp.chapters.length){ const i=storyIndex(cp.chapters[k]); if(i>=0) return i; k+=dir; } return -1; }
function readState(){ try{ return JSON.parse(localStorage.getItem("orbis-read")||"{}"); }catch(e){ return {}; } }
function markRead(id,scene,n){ if(id.startsWith("@")) return; const r=readState(), p=r[id]||[0,n]; r[id]=[Math.max(p[0],scene+1),n];
  try{ localStorage.setItem("orbis-read",JSON.stringify(r)); }catch(e){} }
function fmtDate(d){ const x=new Date(String(d).length===8?String(d).replace(/(\d{4})(\d\d)(\d\d)/,"$1-$2-$3"):d);
  return isNaN(x)?String(d):x.toLocaleDateString(LANG==="de"?"de-AT":"en-GB",{day:"numeric",month:"short",year:"numeric"}); }
function openCampaign(id){
  const cp=CAMPAIGNS.find(c=>c.id===id); if(!cp) return openToc();
  quiz.mode=null; si=-1; frame=null; closeToc(); stopPlay(); sheet.classList.remove("collapsed");
  scene=Object.assign({layers:[],political:true,view:{mode:"globe",center:[0,25],zoom:1}},cp.scene||{});
  markDirty(); el.tl.hidden=true; el.steps.hidden=true; el.notes.hidden=true; el.blocs.hidden=true; el.sw.hidden=true; el.chart.hidden=true; el.media.hidden=true;
  el.kicker.textContent=(LANG==="de"?"Serie":"Series")+" · "+t("{n} chapters",{n:cp.chapters.length}); el.title.textContent=cp.title; el.text.textContent=cp.intro||cp.hook;
  el.updated.hidden=!cp.updated; if(cp.updated) el.updated.textContent=t("Updated {d}",{d:fmtDate(cp.updated)});
  const r=readState(), done=id=>r[id]&&r[id][0]>=r[id][1], seen=id=>r[id]&&r[id][0]>0;
  const ch=cp.chapters.map(id=>[id,STORIES[storyIndex(id)]]).filter(x=>x[1]);
  const nextId=(ch.find(([id])=>!done(id))||ch[0]||[])[0], started=ch.some(([id])=>seen(id));
  el.camp.innerHTML=`<button class="btn camp-go" id="campGo">${t(started?"Continue":"Start")}${nextId&&started?": "+esc(STORIES[storyIndex(nextId)].title):""}</button>
    <ol class="camp-list">${ch.map(([id,s],k)=>`<li class="${done(id)?"done":seen(id)?"seen":""}"><button data-id="${id}"><span class="camp-n">${done(id)?"✓":k+1}</span><span><b>${esc(s.title)}</b><span class="toc-hook">${esc(s.hook)}</span></span></button></li>`).join("")}</ol>
    <p class="camp-progress">${t("{n} of {m} read",{n:ch.filter(([id])=>done(id)).length,m:ch.length})}</p>`+
    (cp.dates&&cp.dates.length?`<details class="camp-dates"><summary>${t("Key dates")}</summary><ul>${cp.dates.map(x=>`<li><span>${esc(fmtDate(x.d))}</span><span>${esc(x.t)}</span></li>`).join("")}</ul></details>`:"")+
    (cp.changelog&&cp.changelog.length?`<details class="camp-dates"><summary>${t("What changed")}</summary><ul>${cp.changelog.map(x=>`<li><span>${esc(fmtDate(x.d))}</span><span>${esc(x.t)}</span></li>`).join("")}</ul></details>`:"");
  el.camp.hidden=false;
  $("campGo").onclick=()=>{ const i=storyIndex(nextId); if(i>=0) openStory(i, done(nextId)||!r[nextId]?0:Math.min(r[nextId][0],r[nextId][1])-1); };
  [...el.camp.querySelectorAll(".camp-list button")].forEach(b=>b.onclick=()=>openStory(storyIndex(b.dataset.id)));
  L=layers(); el.legend.innerHTML=legendHTML(); renderData(); renderTools(); describe();
  history.replaceState(null,"","#c/"+cp.id); syncMode(scene.view.mode); spin=false; flyTo(scene.view); sheet.scrollTop=0; render();
}

// ---------- table of contents ----------
const tocList=$("tocList");
const CATS=["Energy","Geopolitics","Economics","Planet","Statistics","Rights","People"];
function buildToc(){
  const inCamp=new Set(CAMPAIGNS.flatMap(c=>c.chapters));
  tocList.innerHTML=(CAMPAIGNS.length?`<section class="toc-cat"><h2>${esc(t("Series"))}</h2><ul>`+CAMPAIGNS.map(c=>`<li><button class="toc-story toc-camp" data-c="${c.id}"><span class="toc-title">${esc(c.title)}</span><span class="toc-hook">${esc(c.hook)}</span><span class="toc-meta">${t("{n} chapters",{n:c.chapters.length})}${c.updated?" · "+t("Updated {d}",{d:fmtDate(c.updated)}):""}</span></button></li>`).join("")+`</ul></section>`:"")+
  CATS.map(cat=>{const items=STORIES.map((s,i)=>[s,i]).filter(([s])=>s.cat===cat&&!inCamp.has(s.id)); if(!items.length) return "";
    return `<section class="toc-cat"><h2>${esc(t(cat))}</h2><ul>`+items.map(([s,i])=>`<li><button class="toc-story" data-i="${i}"><span class="toc-title">${esc(s.title)}</span><span class="toc-hook">${esc(s.hook)}</span></button></li>`).join("")+`</ul></section>`;}).join("");
  [...tocList.querySelectorAll(".toc-story")].forEach(b=>b.onclick=()=>b.dataset.c?openCampaign(b.dataset.c):openStory(+b.dataset.i));
  $("tocCount").textContent=STORIES.length;
}
$("exploreBtn").onclick=openExplore;
$("tocTools").innerHTML=`<button id="quizBtn">${t("Quiz")}</button><button id="cityBtn">${t("Your city")}</button><a href="editor.html">${t("Write a story")}</a>`+
  Object.entries(LANGS).map(([k,n])=>{ const u=new URL(location.href); u.searchParams.set("lang",k); return `<a href="${esc(u.toString())}" aria-current="${k===LANG}" lang="${k}">${n}</a>`; }).join("");
$("quizBtn").onclick=openQuiz; $("cityBtn").onclick=openCity;
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
applyStaticStrings();
if(new URLSearchParams(location.search).get("embed")){ document.body.classList.add("embed"); const of=$("openFull"); of.hidden=false;
  const u=new URL(location.href); u.searchParams.delete("embed"); of.href=u.toString(); }
readColors();
matchMedia("(prefers-color-scheme: dark)").addEventListener("change",()=>{readColors();if(scene||si<0)el.legend.innerHTML=legendHTML();render();});
new ResizeObserver(()=>layout()).observe(sheet);
addEventListener("resize",layout);
document.fonts && document.fonts.ready.then(render);
layout();
setTimeout(loadDetail,300);
(LANG==="en"?loadJSON("stories/index.json"):loadJSON("stories/"+LANG+"/index.json").catch(()=>loadJSON("stories/index.json"))).then(list=>{ STORIES.unshift(...list.map(x=>Object.assign({},x))); }).catch(e=>console.warn("Story index not loaded:",e))
.then(()=>(LANG==="en"?loadJSON("stories/campaigns.json"):loadJSON("stories/"+LANG+"/campaigns.json").catch(()=>loadJSON("stories/campaigns.json"))).then(c=>{ CAMPAIGNS=c; }).catch(()=>{}))
.then(()=>{
  buildToc();
  let h=location.hash.slice(1).split("/");
  if(h[0]==="@draft"){ STORIES.push({id:"@draft",cat:"Draft",title:"Draft",hook:"",file:"draft"}); }
  else if(h[0].startsWith("@")){ const m=location.hash.slice(2).match(/^(.+\.json)(?:\/(\d+))?$/);
    if(m){ STORIES.push({id:"@"+m[1],cat:"Draft",title:"Draft",hook:"",file:m[1]}); h=["@"+m[1],m[2]||"1"]; } }
  const idx=STORIES.findIndex(s=>s.id===h[0]);
  if(idx>=0) openStory(idx, Math.max(0,(+h[1]||1)-1));
  else if(h[0]==="c"&&h[1]) openCampaign(h[1]);
  else if(h[0]==="explore") openExplore();
  else if(h[0]==="quiz") openQuiz();
  else if(h[0]==="city") openCity();
  else { openExplore(); openToc(false); }
});
})();
