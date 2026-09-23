/* Node and browser share the exact same data-only runtime and geometry source. */
const fs=require('fs'),vm=require('vm'),path=require('path');const R=path.resolve(__dirname,'..');
const runtime=require('./runtime-source.cjs')('@wanxiang/runtime/sources');
for(const f of [runtime.manifest.vendor,...runtime.manifest.kernel])vm.runInThisContext(fs.readFileSync(runtime.sourcePath(f.replace(/^web\//,'src/')),'utf8'),{filename:f});
const input=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),lib=new WXRuntime.Library(input.data),records=[];
for(const [si,s] of input.specs.entries()){try{const b=lib.buildSync(s,{noTextures:true});if(input.states?.[si])WXMechanics.apply(b.root,s,input.states[si]);b.root.updateMatrixWorld(true);records.push({id:s.id,triangles:b.report.triangles,bom:b.bom.map(e=>({instance:e.instance,part:e.part,material:e.material})),nodes:Object.fromEntries([...b.nodes].map(([id,o])=>[id,o.matrixWorld.toArray()]))});const gs=new Set();b.root.traverse(o=>{if(o.geometry)gs.add(o.geometry)});gs.forEach(g=>g.dispose())}catch(e){records.push({id:s.id,error:e.message})}}
fs.writeFileSync(process.argv[3],JSON.stringify(records));
