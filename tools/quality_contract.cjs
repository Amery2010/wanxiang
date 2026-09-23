/* Executable geometry/shader contracts. Uses the production kernel, not mocks. */
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const R=path.resolve(__dirname,'..');
const runtime=require('./runtime-source.cjs')('@wanxiang/runtime/sources');
for(const f of ['vendor/three-0.186.0-with-addons.global.js','web/styles.js','web/semantic.js','web/primitives.js','web/seams.js','web/facets.js'])vm.runInThisContext(fs.readFileSync(runtime.sourcePath(f.replace(/^web\//,'src/')),'utf8'),{filename:f});
const rows=[];function check(name,pass,detail){rows.push({name,passed:!!pass,detail});if(!pass)throw Error(name+': '+JSON.stringify(detail));}
function build(forms,style='lowpoly',params={},extra={}){return WXFacets.build({forms,...extra},params,style);}
function near(a,b,e=1e-6){return a.length===b.length&&a.every((v,i)=>Math.abs(v-b[i])<e);}
function metrics(g){const p=g.attributes.position,edges=new Map(),tris=new Set();let volume=0,duplicates=0,zero=0;
 const key=v=>v.map(x=>Math.round(x*1e7)).join(',');
 for(let i=0;i<p.count;i+=3){const v=[0,1,2].map(k=>new THREE.Vector3().fromBufferAttribute(p,i+k)),ids=v.map(x=>key(x.toArray()));
  const tri=ids.slice().sort().join('|');if(tris.has(tri))duplicates++;tris.add(tri);
  if(v[1].clone().sub(v[0]).cross(v[2].clone().sub(v[0])).lengthSq()<1e-24)zero++;
  volume+=v[0].dot(v[1].clone().cross(v[2]))/6;
  for(let k=0;k<3;k++){const a=ids[k],b=ids[(k+1)%3],key=a<b?a+'|'+b:b+'|'+a;let e=edges.get(key);if(!e){e={count:0,dir:0};edges.set(key,e);}e.count++;e.dir+=a<b?1:-1;}
 }
 return {triangles:p.count/3,boundary:[...edges.values()].filter(e=>e.count===1).length,nonmanifold:[...edges.values()].filter(e=>e.count>2).length,inconsistent:[...edges.values()].filter(e=>e.count===2&&e.dir).length,volume,duplicates,zero};}
for(const style of ['lowpoly','toon'])for(const size of [[1,1,1],[2,.04,3],[.006,.009,.02]]){
 const g=build([{kind:'bevelbox',size,bevel:Math.min(...size)*.2,color:'#ffffff'}],style),m=metrics(g);
 check(`${style} chamfer closed/outward ${size}`,!m.boundary&&!m.nonmanifold&&!m.inconsistent&&!m.duplicates&&!m.zero&&m.volume>0,m);
 check(`${style} chamfer triangle budget ${size}`,m.triangles===(style==='toon'?92:44));
 g.computeBoundingBox();check(`${style} panel envelope ${size}`,near(g.boundingBox.getSize(new THREE.Vector3()).toArray(),size));
 if(style==='toon'){
  const p=g.attributes.position,n=g.attributes.normal;let ok=true;
  // First six authored panels occupy the first 36 corners, with exact plane normals.
  for(let i=0;i<36;i++){const a=[Math.abs(n.getX(i)),Math.abs(n.getY(i)),Math.abs(n.getZ(i))];ok&&=a.filter(x=>x>.999999).length===1&&a.filter(x=>x<1e-7).length===2;}
  check('analytic normals keep planar toon panels flat '+size,ok);
 }
 g.dispose();
}
// Two triangles share an edge and a colour boundary, but no crease.
const a=[[0,0,0],[1,0,0],[0,1,0],[1,1,.30]],f={kind:'poly',points:a,faces:[[0,1,2],[2,1,3]],colors:['#ffffff','#222222'],color:'#ffffff',roundable:false,style_overrides:{toon:{smooth_angle:70}}};
const g=build([f],'toon'),p=g.attributes.position,n=g.attributes.normal;
const same=[];for(let i=0;i<p.count;i++)if(near([p.getX(i),p.getY(i),p.getZ(i)],a[1]))same.push([n.getX(i),n.getY(i),n.getZ(i)]);
check('colour does not split an edge-connected normal island',same.length===2&&near(same[0],same[1]));
const split=build([{...f,faces:[[0,1,2]]},{...f,faces:[[2,1,3]]}],'toon');
check('separate authored forms do not average their contact normals',!near(Array.from(split.attributes.normal.array.slice(3,6)),Array.from(split.attributes.normal.array.slice(12,15))));
const touch=build([{kind:'poly',points:[[0,0,0],[1,0,0],[0,1,0],[-1,0,0],[0,-1,.5]],faces:[[0,1,2],[0,3,4]],color:'#ffffff',smooth_angle:80,roundable:false}],'toon');
check('vertex-only contact is not an edge-connected smoothing island',!near(Array.from(touch.attributes.normal.array.slice(0,3)),Array.from(touch.attributes.normal.array.slice(9,12))));
const sharp=build([{...f,style_overrides:{toon:{smooth_angle:10}}}],'toon');
check('authored crease threshold is preserved',!near(Array.from(sharp.attributes.normal.array.slice(3,6)),Array.from(sharp.attributes.normal.array.slice(12,15))));
// Concave L panel should have area 3, not an overlapping fan through its notch.
const L=build([{kind:'poly',points:[[0,0,0],[2,0,0],[2,1,0],[1,1,0],[1,2,0],[0,2,0]],faces:[[0,1,2,3,4,5]],color:'#ffffff'}]);
let area=0;for(let i=0;i<L.attributes.position.count;i+=3){const v=[0,1,2].map(k=>new THREE.Vector3().fromBufferAttribute(L.attributes.position,i+k));area+=v[1].sub(v[0]).cross(v[2].sub(v[0])).length()/2;}
check('concave triangulation has the correct area',Math.abs(area-3)<1e-7,area);
const tube={kind:'loft',rings:[[-1,0,0],[-.5,.1,0],[0,.12,0],[.5,.1,0],[1,0,0]].map(c=>({c,r:[.04,.03]})),sides:8,color:'#ffffff'};
const frames=WXPrimitives.loftFrames(tube).frames;
check('sweep crossing X retains frame continuity',frames.slice(1).every((f,i)=>f.u.dot(frames[i].u)>.95));
for(const style of ['lowpoly','toon']){
 const closed={...tube,rings:Array.from({length:13},(_,i)=>({c:[Math.cos(i*Math.PI/6),Math.sin(i*Math.PI/6),0],r:[.04,.04]}))};
 const m=metrics(build([closed],style));check(style+' closed sweep has no duplicate end caps or boundary',!m.boundary&&!m.nonmanifold&&!m.duplicates&&!m.zero,m);
}
const sec=(y,bone)=>({c:[0,y,0],r:[.12,.10],bone});
const A={kind:'loft',sides:8,frame_axis:[0,1,0],color:'#ffffff',join_end:'test',rings:[sec(0,'arm'),sec(.8,'arm'),sec(1,'arm')]};
const B={kind:'loft',sides:8,frame_axis:[0,1,0],color:'#222222',join_start:'test',rings:[sec(1.003,'hand'),sec(1.1,'hand'),sec(2,'hand')]};
const input={forms:[A,B]},registered=WXSeams.compile(input),points=registered.report[0].points;
for(const roundness of [0,.54,1]){
 const g=build([A,B],'toon',{roundness},{rig:[{name:'arm',position:[0,0,0]},{name:'hand',parent:'arm',position:[0,1,0]}]}),p=g.attributes.position,w=g.attributes.skinWeight;
 const ranges=g.userData.formRanges;let valid=true;
 for(const q of points)for(const r of ranges){const found=[];for(let i=r.start;i<r.start+r.count;i++)if(near([p.getX(i),p.getY(i),p.getZ(i)],q))found.push(i);valid&&=found.length>0&&found.every(i=>Math.abs(w.getX(i)-.5)<1e-7&&Math.abs(w.getY(i)-.5)<1e-7);}
 check('toon seam positions/weights pinned at roundness '+roundness,valid);
}
const material=new THREE.MeshStandardMaterial({roughness:.4,metalness:.7});WXStyles.shader(material,'toon');
const shader={fragmentShader:'#include <lights_physical_pars_fragment>\n#include <lights_fragment_end>'};material.onBeforeCompile(shader);
check('toon quantizes NdotL rather than post-albedo luminance',shader.fragmentShader.includes('wxBand * directLight.color')&&!shader.fragmentShader.includes('wxLum'));
check('toon keeps independent PBR specular response',shader.fragmentShader.includes('reflectedLight.directSpecular += irradiance *')&&material.metalness===.7);
check('toon export fallback explicitly labelled',material.userData.wxToon.exportFallback.includes('glTF'));
WXStyles.shader(material,'lowpoly');check('switching to Lowpoly clears toon metadata',!material.userData.wxToon&&material.customProgramCacheKey()==='wx-portable-2.1');
console.log(JSON.stringify({version:'2.1.0',checks:rows,passed:rows.filter(r=>r.passed).length,failed:rows.filter(r=>!r.passed).length},null,2));
