/* Deterministic contract tests for the explicit seam compiler; no screenshots. */
'use strict';
const fs=require('fs'),vm=require('vm'),path=require('path');
const R=path.resolve(__dirname,'..');
const runtime=require('./runtime-source.cjs')('@wanxiang/runtime/sources');
for(const f of ['vendor/three-0.186.0-with-addons.global.js','web/semantic.js','web/primitives.js','web/seams.js'])vm.runInThisContext(fs.readFileSync(runtime.sourcePath(f.replace(/^web\//,'src/')),'utf8'),{filename:f});
const checks=[];
function check(name,pass){checks.push({name,passed:!!pass});if(!pass)throw Error(name)}
function section(y,bone,x=0){return {c:[x,y,0],r:[.12,.10],bone}}
const A={kind:'loft',sides:8,frame_axis:[0,1,0],cap:true,join_end:'elbow',rings:[section(0,'arm'),section(1,'arm')]};
const B={kind:'loft',sides:8,frame_axis:[0,1,0],cap:true,join_start:'elbow',rings:[section(1.003,'forearm',.002),section(2,'forearm')]};
const original={forms:[A,B]},before=JSON.stringify(original),result=WXSeams.compile(original);
check('source input is immutable',JSON.stringify(original)===before);
check('exactly one explicit pair',result.report.length===1);
const a=result.shape.forms[0],b=result.shape.forms[1];
check('only the internal end caps removed',a.cap_end===false&&b.cap_start===false&&a.cap_start===undefined&&b.cap_end===undefined);
check('all eight coordinates match',a.rings[1].seam_points.every(p=>b.rings[0].seam_points.some(q=>Math.hypot(...p.map((v,i)=>v-q[i]))<1e-12)));
check('matching weights assigned on both sides',JSON.stringify(a.rings[1].weights)===JSON.stringify(b.rings[0].weights)&&a.rings[1].weights.arm===.5&&a.rings[1].weights.forearm===.5);
const isolated=WXSeams.compile({forms:[A]});
check('standalone source retains its end cap',!isolated.report.length&&isolated.shape.forms[0].cap_end===undefined);
const mirrored=structuredClone(B);mirrored.matrix=new THREE.Matrix4().makeScale(-1,1,1).toArray();
check('cyclic and reversed ring registration',WXSeams.compile({forms:[A,mirrored]}).report[0].max_output_gap===0);
function rejected(f){try{f();return false}catch(e){return e.message.startsWith('SEAM_INVALID:')}}
const far=structuredClone(B);far.rings[0].c[0]=.4;
check('distant ports rejected, not dragged together',rejected(()=>WXSeams.compile({forms:[A,far]})));
const unequal=structuredClone(B);unequal.sides=7;
check('unequal tessellation rejected',rejected(()=>WXSeams.compile({forms:[A,unequal]})));
check('ambiguous three-way join rejected',rejected(()=>WXSeams.compile({forms:[A,B,structuredClone(B)]})));
console.log(JSON.stringify({checks,passed:checks.filter(c=>c.passed).length,failed:checks.filter(c=>!c.passed).length},null,2));
