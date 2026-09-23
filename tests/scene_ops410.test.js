'use strict';
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),cp=require('node:child_process'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),tmp=fs.mkdtempSync(path.join(os.tmpdir(),'wx-scene410-test-'));let passed=0,failed=0;
function test(name,fn){try{fn();passed++;console.log('PASS '+name)}catch(e){failed++;console.error('FAIL '+name+': '+e.message)}}
function run(args){return cp.spawnSync(process.execPath,['tools/scene_ops.js',...args],{cwd:root,encoding:'utf8',timeout:60000})}
try{
 test('Real legacy scene validates with authored definitions above 1 MB',()=>{assert.ok(fs.statSync(path.join(root,'library/parts/exp.nature.willow_curtain.json')).size>1_000_000);const r=run(['library/assemblies/l4-interior-living.json','--validate']);assert.equal(r.status,0,r.stderr);assert.equal(JSON.parse(r.stdout).ok,true)});
 test('Real legacy scene command retains correct transform',()=>{const out=path.join(tmp,'edited.json'),r=run(['library/assemblies/l4-interior-living.json','--command','examples/l34/move-sofa.command.json','--out',out]);assert.equal(r.status,0,r.stderr);const d=JSON.parse(fs.readFileSync(out));assert.deepEqual(d.instances.find(x=>x.id==='primary').position,[-1.05,0,-1])});
 test('Real region extraction resolves the expanded catalogue',()=>{const out=path.join(tmp,'east.json'),r=run(['library/assemblies/l4-harbor-fishing.json','--subset','examples/l34/east-region.selection.json','--out',out]);assert.equal(r.status,0,r.stderr);const d=JSON.parse(fs.readFileSync(out));assert.ok(d.instances.length>0&&d.metadata.scene.export_selection.ancestors_included)});
 test('Oversized user scene stays rejected without output',()=>{const big=path.join(tmp,'big.json'),out=path.join(tmp,'rejected.json');fs.writeFileSync(big,'{}'+' '.repeat(1_000_000));const r=run([big,'--out',out]);assert.notEqual(r.status,0);assert.match(r.stderr,/1 MB user-document/);assert.equal(fs.existsSync(out),false)});
 test('Oversized user command stays rejected without output',()=>{const big=path.join(tmp,'command.json'),out=path.join(tmp,'rejected-command.json');fs.writeFileSync(big,'{"type":"rename-scene","title":"ok"}'+' '.repeat(1_000_000));const r=run(['library/assemblies/l4-interior-living.json','--command',big,'--out',out]);assert.notEqual(r.status,0);assert.match(r.stderr,/1 MB user-document/);assert.equal(fs.existsSync(out),false)});
}finally{fs.rmSync(tmp,{recursive:true,force:true})}
console.log(JSON.stringify({suite:'scene_ops410',passed,failed}));process.exitCode=failed?1:0;
