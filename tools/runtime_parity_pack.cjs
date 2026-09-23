const fs=require('fs'),vm=require('vm'),path=require('path'),root=path.resolve(__dirname,'..');
const runtime=require('./runtime-source.cjs')('@wanxiang/runtime/sources');
for(const f of ['vendor/three-0.186.0-with-addons.global.js','web/pipeline.js','web/runtime-pack.js'])vm.runInThisContext(fs.readFileSync(runtime.sourcePath(f.replace(/^web\//,'src/')),'utf8'));
(async()=>{const input=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));const out=[];
 for(const item of input.items){try{const bytes=fs.readFileSync(item.glb),buffer=bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength);const loaded=await WXPipeline.load(buffer);const packed=WXRuntimePack.pack(loaded,item.spec,input.data);out.push({id:item.id,report:packed.report});WXPipeline.dispose(loaded.scene);packed.cleanup()}catch(e){out.push({id:item.id,error:String(e.stack||e)})}}
 fs.writeFileSync(process.argv[3],JSON.stringify(out));})().catch(e=>{console.error(e);process.exit(1)});
