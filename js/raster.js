// ---------- raster underlay (WebGL2) ----------
// Draws an equirectangular image (satellite, night lights, any lon/lat grid) on a mesh that is
// projected in the vertex shader with the same maths as the D3 vector layer: rotation, a blend of
// two raw projections (globe / Equal Earth / Mercator) and the same clip circle. Raster layers
// therefore follow the globe-to-flat morph exactly.
const Raster = (function(){
  const VS = `#version 300 es
  precision highp float;
  in vec2 aRot;                       // rotated lon/lat in radians (mesh is built in rotated space)
  uniform int uA, uB;                 // raw projections: 0 globe, 1 equal earth, 2 mercator
  uniform float uT, uSa, uSb, uK;     // blend, per-projection scale, zoom
  uniform vec2 uTr, uSize;            // translate (css px), viewport (css px)
  out vec2 vRot;
  vec2 raw(int m, vec2 p){
    float l=p.x, f=p.y;
    if(m==0) return vec2(cos(f)*sin(l), sin(f));
    if(m==2){ f=clamp(f,-1.4835,1.4835); return vec2(l, log(tan(0.785398163+f*0.5))); }
    const float A1=1.340264, A2=-0.081106, A3=0.000893, A4=0.003796, M=0.8660254;
    float t=asin(M*sin(f)), t2=t*t, t6=t2*t2*t2;
    return vec2(l*cos(t)/(M*(A1+3.0*A2*t2+t6*(7.0*A3+9.0*A4*t2))), t*(A1+A2*t2+t6*(A3+A4*t2)));
  }
  void main(){
    vec2 p = raw(uA,aRot)*uSa*(1.0-uT) + raw(uB,aRot)*uSb*uT;
    vec2 s = vec2(uTr.x + uK*p.x, uTr.y - uK*p.y);
    gl_Position = vec4(s.x/uSize.x*2.0-1.0, 1.0-s.y/uSize.y*2.0, 0.0, 1.0);
    vRot = aRot;
  }`;
  const FS = `#version 300 es
  precision highp float;
  in vec2 vRot;
  uniform sampler2D uTex;
  uniform float uDl, uDp, uClip, uAlpha;   // rotation (radians), cos(clip angle) or -2 for none
  uniform vec4 uBox;                       // patch extent in degrees (lon0, lat0, lon1, lat1); lon0 > lon1 means whole world
  out vec4 o;
  void main(){
    float cl=cos(vRot.x), cp=cos(vRot.y);
    if(cl*cp < uClip) discard;
    // inverse of d3.geoRotation([dl, dp, 0])
    float x=cl*cp, y=sin(vRot.x)*cp, z=sin(vRot.y), c=cos(uDp), s=sin(uDp);
    float lam=atan(y, x*c+z*s) - uDl, phi=asin(clamp(z*c-x*s,-1.0,1.0));
    float u=lam/6.283185307+0.5, v=0.5-phi/3.141592654;
    if(uBox.x<uBox.z){ // a regional patch: map into its box, nothing outside it
      float lo=degrees(lam), la=degrees(phi);
      lo=lo-360.0*floor((lo-uBox.x)/360.0);
      if(lo>uBox.z||la<uBox.y||la>uBox.w) discard;
      vec2 uv=vec2((lo-uBox.x)/(uBox.z-uBox.x),(uBox.w-la)/(uBox.w-uBox.y));
      o=texture(uTex,uv)*uAlpha; return;
    }
    // continuous u for derivatives, so the mip level does not jump at the date line
    float u2=fract(u+0.5)-0.5;
    vec2 dx=vec2(dFdx(u),dFdx(v)), dy=vec2(dFdy(u),dFdy(v));
    vec2 dx2=vec2(dFdx(u2),dFdx(v)), dy2=vec2(dFdy(u2),dFdy(v));
    if(abs(dx2.x)+abs(dy2.x) < abs(dx.x)+abs(dy.x)){ dx=dx2; dy=dy2; }
    o = textureGrad(uTex, vec2(fract(u), v), dx, dy) * uAlpha;
  }`;
  let gl=null, prog=null, buf=null, count=0, U={}, canvas=null, ok=false;
  const tex={}, pending={}, box={};
  function init(c){
    canvas=c;
    try{ gl=c.getContext("webgl2",{premultipliedAlpha:true,antialias:false}); }catch(e){ gl=null; }
    if(!gl) return false;
    const sh=(type,src)=>{const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);
      if(!gl.getShaderParameter(s,gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s)); return s;};
    try{
      prog=gl.createProgram();
      gl.attachShader(prog,sh(gl.VERTEX_SHADER,VS)); gl.attachShader(prog,sh(gl.FRAGMENT_SHADER,FS));
      gl.linkProgram(prog); if(!gl.getProgramParameter(prog,gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
    }catch(e){ console.warn("Raster layer disabled:",e); gl=null; return false; }
    ["uA","uB","uT","uSa","uSb","uK","uTr","uSize","uTex","uDl","uDp","uClip","uAlpha","uBox"].forEach(n=>U[n]=gl.getUniformLocation(prog,n));
    // mesh: 1° cells in rotated lon/lat space
    const R=Math.PI/180, v=[];
    for(let i=-180;i<180;i++) for(let j=-90;j<90;j++){
      const a=[i*R,j*R], b=[(i+1)*R,j*R], c2=[(i+1)*R,(j+1)*R], d=[i*R,(j+1)*R];
      v.push(...a,...b,...c2,...a,...c2,...d);
    }
    buf=gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,buf); gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(v),gl.STATIC_DRAW);
    count=v.length/2; ok=true; return true;
  }
  // upload an image or canvas as a mipmapped, longitude-wrapping texture
  function upload(name,src){
      const t=tex[name]||gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D,t);
      gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,true);
      gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,src);
      gl.generateMipmap(gl.TEXTURE_2D);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR_MIPMAP_LINEAR);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.REPEAT);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
      const ext=gl.getExtension("EXT_texture_filter_anisotropic");
      if(ext) gl.texParameterf(gl.TEXTURE_2D,ext.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(8,gl.getParameter(ext.MAX_TEXTURE_MAX_ANISOTROPY_EXT)));
      tex[name]=t;
  }
  function load(name,url,onReady){
    if(!ok||tex[name]||pending[name]) return;
    pending[name]=true;
    const img=new Image(); img.crossOrigin="anonymous";
    img.onload=()=>{ upload(name,img); delete pending[name]; onReady&&onReady(); };
    img.onerror=()=>{ delete pending[name]; console.warn("Could not load raster",url); };
    img.src=url;
  }
  const MODE={globe:0,equal:1,mercator:2};
  // p: {layers:[{name, alpha, span}], a, b, t, sa, sb, k, tr:[x,y], rot:[dl,dp] (radians), clip (degrees or null), W, H, dpr}
  // layers are drawn in order (base map first, data grids on top); returns true if anything was drawn
  function draw(p){
    if(!ok) return false;
    const w=Math.round(p.W*p.dpr), h=Math.round(p.H*p.dpr);
    if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}
    gl.viewport(0,0,w,h); gl.clearColor(0,0,0,0); gl.clear(gl.COLOR_BUFFER_BIT);
    const list=(p.layers||[]).filter(l=>tex[l.name]); if(!list.length) return false;
    gl.useProgram(prog); gl.bindBuffer(gl.ARRAY_BUFFER,buf);
    const loc=gl.getAttribLocation(prog,"aRot"); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc,2,gl.FLOAT,false,0,0);
    gl.uniform1i(U.uA,MODE[p.a]); gl.uniform1i(U.uB,MODE[p.b]); gl.uniform1f(U.uT,p.t);
    gl.uniform1f(U.uSa,p.sa); gl.uniform1f(U.uSb,p.sb); gl.uniform1f(U.uK,p.k);
    gl.uniform2f(U.uTr,p.tr[0],p.tr[1]); gl.uniform2f(U.uSize,p.W,p.H);
    gl.uniform1f(U.uDl,p.rot[0]); gl.uniform1f(U.uDp,p.rot[1]);
    gl.uniform1f(U.uClip,p.clip==null?-2:Math.cos(p.clip*Math.PI/180));
    gl.enable(gl.BLEND); gl.blendFunc(gl.ONE,gl.ONE_MINUS_SRC_ALPHA);
    gl.activeTexture(gl.TEXTURE0); gl.uniform1i(U.uTex,0);
    list.forEach(l=>{ gl.uniform1f(U.uAlpha,l.alpha==null?1:l.alpha); const b=box[l.name]||[1,0,0,0];
      // l.span = [x0, x1] in css px: draw only between them (before/after swipe)
      if(l.span){ gl.enable(gl.SCISSOR_TEST); const x0=Math.round(l.span[0]*p.dpr), x1=Math.round(l.span[1]*p.dpr); gl.scissor(x0,0,Math.max(0,x1-x0),h); }
      gl.uniform4f(U.uBox,b[0],b[1],b[2],b[3]); gl.bindTexture(gl.TEXTURE_2D,tex[l.name]); gl.drawArrays(gl.TRIANGLES,0,count);
      if(l.span) gl.disable(gl.SCISSOR_TEST); });
    return true;
  }
  function clear(){ if(ok){ gl.clearColor(0,0,0,0); gl.clear(gl.COLOR_BUFFER_BIT); } }
  function put(name,canvasOrImage){ if(ok) upload(name,canvasOrImage); }
  // a texture that covers only a lon/lat box (clamped, no wrapping)
  function putPatch(name,img,bbox){ if(!ok) return; upload(name,img); box[name]=bbox;
    gl.bindTexture(gl.TEXTURE_2D,tex[name]); gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE); }
  return {init, load, put, putPatch, draw, clear, get ok(){return ok;}, has:n=>!!tex[n]};
})();
