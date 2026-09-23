#!/usr/bin/env node
/* Headless editor command runner; same pure document operations as Studio.
 * node tools/scene_ops.js scene.json --validate
 * node tools/scene_ops.js scene.json --command command.json --out edited.json
 * node tools/scene_ops.js scene.json --subset selection.json --out region.json
 * GLB export: python wx kit build --spec edited.json --out workspaces/edited
 * Authored catalogue meshes are not user scene documents: they have a separate,
 * bounded allowance. User scenes/commands retain the 1 MB input limit.
 */
'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const runtimeRequire=require('./runtime-source.cjs');
runtimeRequire('@wanxiang/runtime/semantic');
const S=runtimeRequire('@wanxiang/runtime/scene-document');
const USER_INPUT_BYTES=1_000_000, AUTHORED_DEFINITION_BYTES=8*1024*1024;
function readJson(file,maxBytes=USER_INPUT_BYTES){
 const stat=fs.statSync(file);
 if(!stat.isFile()||stat.size>maxBytes)throw Error(`Input exceeds ${maxBytes===USER_INPUT_BYTES?'1 MB user-document': '8 MiB authored-definition'} limit: ${path.basename(file)}`);
 const bytes=fs.readFileSync(file);
 // Check again after reading in case another process changed the file.
 if(bytes.length>maxBytes)throw Error('Input changed beyond size limit during read');
 return JSON.parse(bytes.toString('utf8'));
}
try{
 const args=process.argv.slice(2);
 if(!args[0])throw Error('Usage: node tools/scene_ops.js scene.json [--validate | --command action.json | --subset query.json] [--out file.json]');
 const value=flag=>{const i=args.indexOf(flag);if(i<0)return null;if(!args[i+1]||args[i+1].startsWith('--'))throw Error('Missing value for '+flag);return args[i+1]};
 // Reject excessive user inputs before walking the model library.
 const source=readJson(args[0]);
 const command=value('--command')?readJson(value('--command')):null;
 const subset=value('--subset')?readJson(value('--subset')):null;
 const catalog=Object.create(null);
 for(const dir of ['parts','assemblies'])for(const file of fs.readdirSync(path.join(root,'library',dir))){
  if(!file.endsWith('.json'))continue;
  const d=readJson(path.join(root,'library',dir,file),AUTHORED_DEFINITION_BYTES);
  if(!d||typeof d.id!=='string'||!d.id||Object.hasOwn(catalog,d.id))throw Error('Invalid or duplicate catalogue definition: '+file);
  catalog[d.id]=d;
 }
 let d=S.normalize(source,catalog);
 if(command)d=S.apply(d,command,catalog);
 if(subset)d=S.subset(d,subset,catalog);
 const dest=value('--out');
 if(dest){fs.mkdirSync(path.dirname(path.resolve(dest)),{recursive:true});const tmp=dest+'.partial';fs.writeFileSync(tmp,JSON.stringify(d,null,2)+'\n');fs.renameSync(tmp,dest)}
 console.log(JSON.stringify({ok:true,id:d.id,objects:d.instances.length,layers:Object.keys(d.metadata.scene.layers).length,out:dest},null,2));
}catch(e){console.error(e.message);process.exitCode=1}
