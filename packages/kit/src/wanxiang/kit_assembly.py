"""LLM-first hierarchical kit assembly with typed full-frame connector mating.
JSON is data; no Python/YAML expression evaluation. Repeated parts share mesh
buffers in GLB, but keep separately addressable nodes, pivots and bill of materials.
"""
from __future__ import annotations
from .paths import require_resources
from .paths import code_path, runtime_code_files, WORKSPACE_ROOT
import copy, csv, io, math, time, hashlib
from pathlib import Path
from collections import Counter
import numpy as np
from scipy.spatial.transform import Rotation
from .util import ROOT, read_json, write_json, digest, sha256, safe_id, atomic_bytes
from .errors import WXError
from .ir import AssetIR
from .kit_parts import build_part, definition, frame, connector, STYLES, canonical_style
from .glb import export_glb, read_glb
from .materials import load_material
from .validation import inspect_asset

ASSEMBLY_DIR=ROOT/'library/assemblies'


def trs(position=(0,0,0),rotation=(0,0,0),scale=(1,1,1)):
    p,r,s=(np.asarray(x,float) for x in (position,rotation,scale))
    if any(x.shape!=(3,) or not np.isfinite(x).all() for x in (p,r,s)) or np.any(s<=0) or np.any(s>100):raise WXError('RECIPE_INVALID','Transforms need finite vectors, positive scale <=100')
    m=np.eye(4);m[:3,:3]=Rotation.from_euler('xyz',r,degrees=True).as_matrix()@np.diag(s);m[:3,3]=p;return m


def get_template(id):
    require_resources()
    from .retirement import refuse
    refuse(id,'assembly')
    aliases=read_json(ROOT/'library/aliases.json') if (ROOT/'library/aliases.json').exists() else {}
    id=aliases.get(id,id)
    p=ASSEMBLY_DIR/(safe_id(id)+'.json')
    if not p.is_file():raise WXError('RECIPE_INVALID',f'Assembly not found: {id}')
    return read_json(p)


def expanded_instances(instances):
    result=[]
    for item in instances:
        it=copy.deepcopy(item);enabled=it.pop('enabled',True)
        if not isinstance(enabled,bool):raise WXError('RECIPE_INVALID','Instance enabled must resolve to a boolean')
        if not enabled:continue
        rep=it.pop('repeat',None)
        if not rep:result.append(it);continue
        base=it['id'];kind=rep.get('type','linear');coords=[]
        if kind=='linear':
            n=rep.get('count',1)
            if type(n) is not int:raise WXError('RECIPE_INVALID','Repeat count must be an integer')
            step=np.asarray(rep.get('step',[1,0,0]),float)
            if step.shape!=(3,) or not np.isfinite(step).all():raise WXError('RECIPE_INVALID','Invalid repeat step')
            if not 1<=n<=512:raise WXError('BUDGET_EXCEEDED','Linear repeat count outside 1..512')
            coords=[(step*i,[0,0,0]) for i in range(n)]
        elif kind=='grid':
            count=rep.get('count',[1,1,1]);step=rep.get('step',[1,1,1])
            if not isinstance(count,list) or not isinstance(step,list) or any(not isinstance(x,(int,float)) or not math.isfinite(x) for x in step):raise WXError('RECIPE_INVALID','Invalid grid vector')
            if len(count)!=3 or len(step)!=3 or any(type(x) is not int or not 1<=x<=128 for x in count) or math.prod(count)>2048:raise WXError('BUDGET_EXCEEDED','Invalid grid count')
            coords=[(np.array([x*step[0],y*step[1],z*step[2]]),[0,0,0]) for y in range(count[1]) for z in range(count[2]) for x in range(count[0])]
        elif kind=='radial':
            n=rep.get('count',8);radius=float(rep.get('radius',1));start=float(rep.get('start',0))
            if type(n) is not int or not math.isfinite(start):raise WXError('RECIPE_INVALID','Invalid radial repeat count/start')
            if not 1<=n<=512 or not 0<=radius<=100:raise WXError('BUDGET_EXCEEDED','Invalid radial repeat')
            coords=[(np.array([radius*math.sin(math.radians(start+i*360/n)),0,radius*math.cos(math.radians(start+i*360/n))]),[0,start+i*360/n if rep.get('orient',True) else 0,0]) for i in range(n)]
        else:raise WXError('RECIPE_INVALID','Unknown repeat type')
        if it.get('attach'):raise WXError('RECIPE_INVALID','Repeated instances cannot all mate to the same socket; expand explicit attaches instead')
        for i,(p,r) in enumerate(coords):
            c=copy.deepcopy(it);c['id']=base+f'_{i:03d}';c['position']=(np.asarray(c.get('position',[0,0,0]))+p).tolist();c['rotation']=(np.asarray(c.get('rotation',[0,0,0]))+r).tolist();result.append(c)
    if len(result)>2500:raise WXError('BUDGET_EXCEEDED','At most 2500 instances per assembly')
    return result


class Assembler:
    def __init__(self,style='lowpoly',max_nodes=10000,max_triangles=500000):
        if style not in STYLES:raise WXError('RECIPE_INVALID','Unknown kit style')
        self.style=style;self.cache={};self.max_nodes=max_nodes;self.max_triangles=max_triangles;self.cache_hits=0
    def part(self,id,style,params=None,material=None):
        d=definition(id);key=digest([d,style,params,material])
        if key in self.cache:self.cache_hits+=1;return self.cache[key],key
        a=build_part(id,style,params,material);self.cache[key]=a;return a,key
    def assemble(self,spec,stack=()):
        from .semantic import assembly as resolve_assembly
        source_spec=copy.deepcopy(spec)
        spec=resolve_assembly(spec)
        from .contracts import validate_runtime
        validate_runtime(spec.get('metadata',{}).get('runtime',{}))
        if not isinstance(spec,dict) or spec.get('schema')!='wx.assembly/1.0':raise WXError('RECIPE_INVALID','Expected wx.assembly/1.0')
        allowed={'schema','id','name','version','category','tags','description','instances','exports','style','max_triangles','metadata','internal'}
        if set(spec)-allowed:raise WXError('RECIPE_INVALID',f'Unknown assembly fields: {set(spec)-allowed}')
        if 'internal' in spec and not isinstance(spec['internal'],bool):raise WXError('RECIPE_INVALID','Assembly internal flag must be boolean')
        id=safe_id(spec['id'])
        if id in stack or len(stack)>12:raise WXError('RECIPE_INVALID','Recursive/cyclic assembly')
        style=spec.get('style',self.style)
        if style not in STYLES:raise WXError('RECIPE_INVALID','Unknown assembly style')
        items=expanded_instances(spec.get('instances',[]))
        if not items:raise WXError('RECIPE_INVALID','Assembly needs at least one instance')
        a=AssetIR();a.group('root',role='assembly_root');bom=[];attachments=[];ids=set();by={}
        for it in items:
            known={'id','part','assembly','position','rotation','scale','params','material','style','parent','attach','joint','angle','role','pivot','collision'}
            if set(it)-known:raise WXError('RECIPE_INVALID',f'Unknown instance field: {set(it)-known}')
            iid=safe_id(it['id'])
            if iid=='root' or iid in ids:raise WXError('RECIPE_INVALID','Duplicate/reserved instance id')
            ids.add(iid);by[iid]=it
            if ('part'in it)==('assembly'in it):raise WXError('RECIPE_INVALID','Each instance requires exactly one part or assembly')
        # Parent + mate constraints form a dependency DAG, not a last-write-wins list.
        ordered=[];visiting=set();done=set()
        def owner(path):return max((x for x in ids if path==x or path.startswith(x+'.')),key=len,default=None)
        def visit(iid):
            if iid in done:return
            if iid in visiting:raise WXError('RECIPE_INVALID','Parent/attachment cycle detected',node=iid)
            visiting.add(iid);it=by[iid]
            deps=[]
            if it.get('parent'):deps.append(it['parent'])
            if it.get('attach'):deps.append(it['attach'].get('target',''))
            for path in deps:
                dep=owner(path)
                if dep is None:raise WXError('RECIPE_INVALID',f'Unknown attachment or parent target: {path}')
                visit(dep)
            visiting.remove(iid);done.add(iid);ordered.append(iid)
        for iid in by:visit(iid)
        for iid in ordered:
            it=by[iid];istyle=it.get('style',style);parent=it.get('parent','root')
            if 'part'in it:
                sub,key=self.part(it['part'],istyle,{**{k:v for k,v in spec.get('metadata',{}).items() if k in ('roundness','paint_strength','texture_scale','voxel_resolution','seed')},**it.get('params',{})},it.get('material'))
                entries=[{'instance':iid,'part':it['part'],'name':definition(it['part'])['name'],'style':istyle,'params':it.get('params',{}),'material':sub.nodes[-1]['material'],'definition_sha256':sub.metadata['definition_sha256']}]
            else:
                child=get_template(it['assembly']);child['style']=istyle
                child['metadata']={**child.get('metadata',{}),**{k:v for k,v in spec.get('metadata',{}).items() if k in ('roundness','paint_strength','texture_scale','voxel_resolution','seed')}}
                
                if it.get('params'):child['metadata']={**child.get('metadata',{}),'parameters':{**child.get('metadata',{}).get('parameters',{}),**it['params']}}
                sub=self.assemble(child,stack+(id,));key=digest([child,istyle]);entries=[{**e,'instance':iid+'.'+e['instance']} for e in sub.metadata['bom']]
            pivot=it.get('pivot')
            if pivot is not None:
                pv=np.asarray(pivot,float)
                if pv.shape!=(3,) or not np.isfinite(pv).all() or np.max(np.abs(pv))>1e4:
                    raise WXError('RECIPE_INVALID','Invalid local pivot')
                if it.get('attach'):raise WXError('RECIPE_INVALID','Explicit pivot and socket attachment are mutually exclusive')
                a.group(iid,parent=parent,matrix=trs(it.get('position',[0,0,0]),it.get('rotation',[0,0,0])),role=it.get('role','pivot_instance'))
                a.nodes[-1].update(kit_instance=iid,content_node=iid+'.__content',authored_pivot=pv.tolist())
            if 'collision' in it:
                if 'part' not in it:raise WXError('RECIPE_INVALID','Collision override belongs to a part instance, not a nested assembly')
                validate_runtime({'schema':'wx.runtime-metadata/1.0','units':'m','up':'+Y','forward':'+Z','collision':it['collision']})
                entries[0]['collision_override']=copy.deepcopy(it['collision'])
            node_map={n['id']:(iid+'.__content' if pivot is not None else iid) if n['id']=='root' else iid+'.'+n['id'] for n in sub.nodes}
            for n in sub.nodes:
                nn=copy.deepcopy(n);nn['id']=node_map[n['id']];nn['parent']=node_map[n['parent']] if n.get('parent') else parent
                if n['id']=='root':
                    if pivot is not None:
                        content=trs(scale=it.get('scale',[1,1,1]));content[:3,3]=-content[:3,:3]@pv
                        nn['matrix']=content.tolist();nn['parent']=iid;nn['role']='pivot_content'
                    else:
                        nn['matrix']=trs(it.get('position',[0,0,0]),it.get('rotation',[0,0,0]),it.get('scale',[1,1,1])).tolist()
                        nn['role']=it.get('role','part_instance' if 'part'in it else 'subassembly_instance')
                    nn['kit_instance']=iid
                if n.get('content_node'):nn['content_node']=node_map[n['content_node']]
                if n.get('kit_instance') and n['id']!='root':nn['kit_instance']=iid+'.'+n['kit_instance']
                if n.get('skin'):nn['skin']={**n['skin'],'joints':[node_map[x] for x in n['skin']['joints']]}
                if n.get('mesh'):
                    meshkey=key[:20]+'.'+n['mesh'];nn['mesh']=meshkey
                    if meshkey not in a.meshes:a.meshes[meshkey]=sub.meshes[n['mesh']]
                a.nodes.append(nn)
            for s in sub.sockets:
                ns=copy.deepcopy(s);ns['id']=iid+'.'+s['id'];ns['node']=node_map[s['node']];a.sockets.append(ns)
            bom.extend(entries)
            if it.get('attach'):
                att=it['attach']
                if any(not np.allclose(it.get(k,default),default) for k,default in [('position',[0,0,0]),('rotation',[0,0,0]),('scale',[1,1,1])]):raise WXError('RECIPE_INVALID','Attached instances use socket twist/offset and part params.size; nonidentity instance TRS would be ambiguous')
                allowed_a={'target','socket','own','mode','twist','offset','allow_interface_mismatch'}
                if set(att)-allowed_a:raise WXError('RECIPE_INVALID','Unknown attachment field')
                destid=att['target']+'.'+att.get('socket','top');ownid=iid+'.'+att.get('own','mount')
                sd=self._socket(a,destid);so=self._socket(a,ownid)
                from .contracts import compatibility,world_socket
                world=a.world_matrices()
                decision=compatibility(world_socket(sd,world[sd['node']]),world_socket(so,world[so['node']]))
                compatible=decision['compatible']
                if not compatible and not att.get('allow_interface_mismatch',False):raise WXError('RECIPE_INVALID',f'Incompatible socket interfaces: {sd["interface"]} vs {so["interface"]}')
                world=a.world_matrices();target=world[sd['node']]@self._frame(sd);own_local=np.linalg.inv(world[iid])@world[so['node']]@self._frame(so)
                flip=np.eye(4);mode=att.get('mode','opposed')
                if mode=='opposed':flip[:3,:3]=Rotation.from_euler('x',180,degrees=True).as_matrix()
                elif mode!='coincident':raise WXError('RECIPE_INVALID','Mate mode must be opposed or coincident')
                twist=float(att.get('twist',0));offs=np.asarray(att.get('offset',[0,0,0]),float)
                if not math.isfinite(twist) or offs.shape!=(3,) or not np.isfinite(offs).all():raise WXError('RECIPE_INVALID','Invalid mate twist/offset')
                extra=trs(offs,[0,0,twist]);desired=target@extra@flip@np.linalg.inv(own_local)
                nn=next(n for n in a.nodes if n['id']==iid);nn['matrix']=(np.linalg.inv(world[parent])@desired).tolist()
                attachments.append({'instance':iid,'target':destid,'own':ownid,'mode':mode,'compatible':compatible,'twist':twist,'offset':offs.tolist()})
            if it.get('joint'):
                joint=it['joint'];axis=np.asarray(joint.get('axis',[0,1,0]),float);angle=float(it.get('angle',0));limits=joint.get('limits',[-180,180])
                if axis.shape!=(3,) or not np.isfinite(axis).all() or np.linalg.norm(axis)<1e-8 or not limits[0]<=angle<=limits[1]:raise WXError('RECIPE_INVALID','Invalid joint axis or angle outside limits')
                axis/=np.linalg.norm(axis);rot=np.eye(4);rot[:3,:3]=Rotation.from_rotvec(axis*math.radians(angle)).as_matrix()
                nn=next(n for n in a.nodes if n['id']==iid);nn['matrix']=(np.array(nn['matrix'])@rot).tolist();nn['joint']={**joint,'angle':angle}
            if len(a.nodes)>self.max_nodes:raise WXError('BUDGET_EXCEEDED','Scene node budget exceeded')
        from .mechanics import apply as solve_mechanics
        linkage=solve_mechanics(a,spec)
        seen_exports=set()
        for ex in spec.get('exports',[]):
            if not isinstance(ex.get('id'),str) or ex['id'] in seen_exports:
                raise WXError('RECIPE_INVALID','Duplicate or invalid exported socket')
            seen_exports.add(ex['id'])
            if 'position' in ex:
                from .contracts import validate_connector
                if 'node' in ex or 'socket' in ex:raise WXError('RECIPE_INVALID','Direct socket cannot also reference a node')
                validate_connector(ex)
                frame_node=ex.get('frame_node','root')
                if frame_node not in {n['id'] for n in a.nodes}:raise WXError('RECIPE_INVALID','Unknown exported frame node')
                a.socket(ex['id'],frame_node,ex['position'],ex['normal'],ex.get('interface','surface'))
                a.sockets[-1].update(copy.deepcopy(ex))
                continue
            s=self._socket(a,ex['node']+'.'+ex['socket']);world=a.world_matrices();mat=world[s['node']]@self._frame(s)
            from .contracts import world_socket
            ws=world_socket(s,world[s['node']]);a.socket(ex['id'],'root',ws['position'],ws['normal'],s['interface']);a.sockets[-1].update({k:v for k,v in ws.items() if k not in ('id','node')})
        if not any(s['id']=='mount' for s in a.sockets):
            a.socket('mount','root',[0,0,0],[0,-1,0],'surface');a.sockets[-1]['tangent']=[1,0,0]
        triangles=sum(len(a.meshes[n['mesh']].faces) for n in a.nodes if n.get('mesh'))
        if triangles>min(self.max_triangles,spec.get('max_triangles',400000)):raise WXError('BUDGET_EXCEEDED','Expanded triangle budget exceeded')
        # Evaluate mates after hierarchy construction. Offset/joint effects are recorded.
        worlds=a.world_matrices()
        for j in attachments:
            d=self._socket(a,j['target']);s=self._socket(a,j['own']);fd=worlds[d['node']]@self._frame(d);fs=worlds[s['node']]@self._frame(s)
            wanted=(fd@np.r_[j['offset'],1])[:3];j['position_error_m']=float(np.linalg.norm(wanted-fs[:3,3]));j['normal_dot']=float(np.dot(fd[:3,2],fs[:3,2])/(np.linalg.norm(fd[:3,2])*np.linalg.norm(fs[:3,2])));j['position_passed']=j['position_error_m']<1e-5
        a.metadata={'runtime':copy.deepcopy(spec.get('metadata',{}).get('runtime',{})),'id':id,'name':spec.get('name',id),'style':style,'level':spec.get('metadata',{}).get('level',2 if stack else 3),'assembly_schema':'wx.assembly/1.0','bom':bom,'attachments':attachments,'linkage':linkage,'source_spec':source_spec,'triangles_expanded':triangles,'mesh_buffers_unique':len(a.meshes),'part_instances':len(bom),'unique_part_definitions':len({b['part'] for b in bom}),'source':'registered_component_assembly','component_sources':{part:definition(part)['source'] for part in sorted({entry['part'] for entry in bom})},'limitations':['Assembly preserves separate intersecting components; no automatic watertight union.','Sockets use declared frames; no automatic inference of semantic joints from arbitrary meshes.']}
        return a
    @staticmethod
    def _socket(a,id):
        found=[s for s in a.sockets if s['id']==id]
        if len(found)!=1:raise WXError('RECIPE_INVALID',f'Socket not uniquely found: {id}')
        return found[0]
    @staticmethod
    def _frame(s):return frame({'position':s['position'],'normal':s['axis'],'tangent':s.get('tangent',[1,0,0])})


def materials_for(asset):
    return {name:load_material(name,style='natural') for name in sorted({n['material'] for n in asset.nodes if n.get('mesh')})}


def template_dependencies(spec,seen=None):
    out={} if seen is None else seen
    for item in spec.get('instances',[]):
        id=item.get('assembly')
        if id and id not in out:
            p=ASSEMBLY_DIR/(safe_id(id)+'.json');d=read_json(p);out[id]={'sha256':sha256(p),'definition':d};template_dependencies(d,out)
    return out


def publish(asset,spec,run,review=True):
    run=Path(run);identity=digest(spec)
    if spec.get('schema')=='wx.part-build/1.0' and 'bom' not in asset.metadata:
        asset.metadata['bom']=[{'instance':'root','part':spec['part'],'name':asset.metadata['name'],'params':spec.get('params',{}),'material':next(n['material'] for n in asset.nodes if n.get('mesh')),'style':asset.metadata['style'],'definition_sha256':asset.metadata['definition_sha256']}]
        asset.metadata.update(part_instances=1,unique_part_definitions=1,mesh_buffers_unique=len(asset.meshes))
    if (run/'source/kit-spec.json').exists() and digest(read_json(run/'source/kit-spec.json'))!=identity:raise WXError('INPUT_INVALID','Output belongs to a different specification; choose a new run directory')
    run.mkdir(parents=True,exist_ok=True);write_json(run/'source/kit-spec.json',spec)
    write_json(run/'source/toolchain.json',{'version':'3.0.0','files':{**{name:sha256(path) for name,path in runtime_code_files().items()},**{f:sha256(code_path(f)) for f in ('wanxiang/ir.py','wanxiang/skinning.py','wanxiang/render.py','wanxiang/rigid_motion.py','wanxiang/kit_cli.py','web/runtime.js','web/app.js','wanxiang/kit_parts.py','wanxiang/kit_assembly.py','wanxiang/live_geometry.py','wanxiang/geometry.py','wanxiang/glb.py','wanxiang/materials.py','wanxiang/kit_external.py','web/styles.js','web/runtime-pack.js','wanxiang/runtime_export.py','wanxiang/retirement.py','web/mechanics.js','wanxiang/semantic.py','wanxiang/mechanics.py','web/surfaces.js','web/semantic.js','web/primitives.js','web/seams.js','web/facets.js','web/geometry.js','workers/node/live_geometry.cjs','runtime/sources.cjs','runtime/source-manifest.json','vendor/three-0.186.0-with-addons.global.js')}}})
    dependencies={}
    for b in asset.metadata.get('bom',[]):
        p=ROOT/'library/parts'/(b['part']+'.json');dependencies[str(p.relative_to(ROOT))]={'sha256':sha256(p),'definition':read_json(p)}
    from .live_geometry import component_registry
    for entry in list(dependencies.values()):
        for ident,definition_data in component_registry(entry['definition']).items():
            p=ROOT/'library/parts'/(ident+'.json')
            dependencies[str(p.relative_to(ROOT))]={'sha256':sha256(p),'definition':definition_data}
    write_json(run/'source/dependency-lock.json',{'parts':dependencies,'assembly_templates':template_dependencies(spec)})
    asset.save(run/'intermediate');mats=materials_for(asset);path=run/'release/asset.glb';
    from .rigid_motion import tracks_for
    tracks=tracks_for(asset,spec.get('id',''));doc=export_glb(asset,mats,path,animations=tracks)
    from .runtime_metadata import describe
    write_json(run/'release/colliders.json',describe(asset,spec))
    write_json(run/'release/motion.json',{'schema':'wx.rigid-export/1.0','type':'skinned-bone-keyframes' if any(n.get('skin') for n in asset.nodes) else 'rigid-node-keyframes','tracks':tracks})
    report=inspect_asset(path,expected=asset,independent=True);report['kit']={k:asset.metadata.get(k) for k in ('part_instances','unique_part_definitions','mesh_buffers_unique','attachments')}
    if review:
        from .render import multi_view
        multi_view(path,run/'review',size=256);report['evidence']['cpu_preview']=True
    write_json(run/'review/inspection.json',report)
    bom=asset.metadata.get('bom',[]);write_json(run/'release/bom.json',bom);write_json(run/'release/assembly.json',spec)
    write_json(run/'release/provenance.json',asset.metadata.get('component_sources') or {spec.get('part','asset'):asset.metadata.get('source',{})})
    counter=Counter((x['part'],x['material']) for x in bom);buffer=io.StringIO();writer=csv.writer(buffer);writer.writerow(['part','material','quantity'])
    for (part,mat),n in sorted(counter.items()):writer.writerow([part,mat,n])
    atomic_bytes(run/'release/bom.csv',buffer.getvalue().encode('utf-8-sig'))
    is_part=spec.get('schema')=='wx.part-build/1.0';cat='part_'+definition(spec['part'])['category'] if is_part else 'assembly'
    recipe={'id':spec.get('part',spec.get('id')),'schema':spec['schema'],'version':'3.0.0','name':asset.metadata.get('name',spec.get('id')),'category':cat,'family':'part' if is_part else 'assembly','tags':(['零件','组件'] if is_part else ['组合','完整模型'])+[asset.metadata.get('style','lowpoly')], 'defaults':{},'parameter_schema':{'properties':{}}}
    write_json(run/'source/recipe.json',recipe)
    write_json(run/'source/material-bindings.json',{k:{kk:vv for kk,vv in v.items() if kk!='images'} for k,v in mats.items()})
    job={'id':run.name,'state':'ready' if report['passed'] else 'needs_revision','spec':{'id':run.name,'recipe':recipe['id'],'style':asset.metadata.get('style','lowpoly'),'params':{},'seed':0,'profile':'kit'},'cache_hits':0,'inspection':report,'kit_spec_hash':identity}
    write_json(run/'job.json',job);return {'id':run.name,'run':str(run),'passed':report['passed'],'triangles':report['triangles'],'nodes':report['nodes'],'part_instances':len(bom),'unique_parts':len(counter),'unique_gltf_meshes':len(doc['meshes']),'glb':str(path),'sha256':sha256(path)}


def apply_build_parameters(spec,params):
    """CLI assembly parameters are semantic shape inputs, never silently ignored."""
    spec=copy.deepcopy(spec)
    if not params:return spec
    if not isinstance(params,dict):raise WXError('RECIPE_INVALID','Parameters must be an object')
    md=spec.setdefault('metadata',{});schema=md.get('parameter_schema',{})
    declared=set(schema.get('properties',{}));style_keys={'roundness','voxel_resolution','seed'}
    if set(params)-declared-style_keys:raise WXError('RECIPE_INVALID','Unknown assembly parameter(s): '+str(sorted(set(params)-declared-style_keys)))
    if declared:md['parameters']={**md.get('parameters',{}),**{k:v for k,v in params.items() if k in declared}}
    md.update({k:v for k,v in params.items() if k in style_keys})
    return spec


def _uncached_build(id=None,spec=None,style=None,out=None,part=False,review=True,params=None):
    style=style or (spec or {}).get('style') or (get_template(id).get('style','lowpoly') if id and not part and spec is None else 'lowpoly')
    if spec is not None:
        spec=copy.deepcopy(spec)
        if spec.get('schema')=='wx.part-build/1.0':
            asset=build_part(spec['part'],spec.get('style',style),spec.get('params'),spec.get('material'))
        else:
            spec=apply_build_parameters(spec,params);spec['style']=style if style else spec.get('style','lowpoly');asset=Assembler(spec['style']).assemble(spec)
    elif part:
        spec={'schema':'wx.part-build/1.0','id':id,'part':id,'style':style,'params':params or {}};asset=build_part(id,style,params)
    else:
        spec=apply_build_parameters(get_template(id),params);spec['style']=style;asset=Assembler(style).assemble(spec)
    return publish(asset,spec,out or WORKSPACE_ROOT/'workspaces/kit/runs'/safe_id((id or spec['id'])+'-'+asset.metadata.get('style','lowpoly')),review)


def explode_asset(asset,amount=.35,level='part'):
    a=copy.deepcopy(asset);world=a.world_matrices();bounds=a.bounds();center=bounds.mean(0);diagonal=max(.01,np.linalg.norm(np.ptp(bounds,axis=0)))
    if not np.isfinite(amount) or not 0<=amount<=3:raise WXError('RECIPE_INVALID','Explosion amount outside 0..3')
    roots=[n for n in a.nodes if n.get('kit_instance') and ((n.get('role')=='part_instance') if level=='part' else n.get('parent')=='root')]
    for i,n in enumerate(roots):
        pos=world[n['id']][:3,3];d=pos-center
        if np.linalg.norm(d)<1e-6:d=np.array([0,1,0])
        shift=d*amount + d/np.linalg.norm(d)*diagonal*.035*amount
        parent=world.get(n.get('parent'),np.eye(4));m=np.array(n['matrix']);m[:3,3]+=np.linalg.inv(parent[:3,:3])@shift;n['matrix']=m.tolist()
    a.metadata={**a.metadata,'exploded':{'amount':amount,'level':level,'not_a_physical_assembly':True}}
    return a


def extract_subtree(asset,node_id):
    by={n['id']:n for n in asset.nodes}
    if node_id not in by:raise WXError('INPUT_INVALID',f'Unknown node {node_id}')
    selected={node_id};change=True
    while change:
        before=len(selected);selected.update(n['id'] for n in asset.nodes if n.get('parent') in selected);change=len(selected)!=before
    a=AssetIR();a.nodes=[copy.deepcopy(n) for n in asset.nodes if n['id'] in selected]
    for n in a.nodes:
        if n['id']==node_id:n['parent']=None;n['matrix']=np.eye(4).tolist()
        if n.get('mesh'):a.meshes[n['mesh']]=asset.meshes[n['mesh']].copy()
    if not a.meshes:raise WXError('INPUT_INVALID','Chosen subtree contains no mesh')
    for n in a.nodes:
        if n.get('skin') and not set(n['skin']['joints']).issubset(selected):raise WXError('INPUT_INVALID','Selected surface requires bones outside this subtree; select its complete part root')
    a.sockets=[copy.deepcopy(s) for s in asset.sockets if s['node'] in selected];a.metadata={'source_node':node_id,'pivot':'selected subtree local origin preserved','component_sources':{e['part']:definition(e['part'])['source'] for e in asset.metadata.get('bom',[]) if e['instance'] in selected}};return a


def split_run(run,out,unique=False):
    run=Path(run);asset=AssetIR.load(run/'intermediate');out=Path(out);out.mkdir(parents=True,exist_ok=True);seen=set();files=[]
    for entry in asset.metadata.get('bom',[]):
        key=digest([entry['part'],entry['params'],entry['material'],entry['style']])
        if unique and key in seen:continue
        seen.add(key);sub=extract_subtree(asset,entry['instance']);path=out/(entry['instance']+'.glb');export_glb(sub,materials_for(sub),path)
        files.append({'node':entry['instance'],'part':entry['part'],'path':path.name,'sha256':sha256(path)})
    write_json(out/'parts-manifest.json',{'count':len(files),'deduplicated':unique,'files':files});return {'count':len(files),'out':str(out)}


def build(id=None,spec=None,style=None,out=None,part=False,review=True,params=None,cache=True):
    """Build from definitions; cache is disposable and can never change semantics."""
    style=style or (spec or {}).get('style') or (get_template(id).get('style','lowpoly') if id and not part and spec is None else 'lowpoly')
    if spec is None:
        spec=({'schema':'wx.part-build/1.0','id':id,'part':id,'style':style,'params':params or {}} if part else apply_build_parameters(get_template(id),params))
    else:
        spec=copy.deepcopy(spec)
        if spec.get('schema')!='wx.part-build/1.0':spec=apply_build_parameters(spec,params)
    spec['style']=style
    target=out or WORKSPACE_ROOT/'workspaces/kit/runs'/safe_id((id or spec['id'])+'-'+style)
    perform=lambda: _uncached_build(spec=spec,style=style,out=target,review=review)
    if not cache:return perform()
    from .build_cache import cached_build
    return cached_build(spec,target,review,perform)
