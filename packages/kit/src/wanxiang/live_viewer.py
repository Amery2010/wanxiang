"""Catalogue data for the Studio development server."""
from __future__ import annotations
from .paths import require_resources
import base64
from html import escape
from .util import ROOT,read_json,read_data,safe_id

LEAD_ASSEMBLIES=['exp-scene-medieval','exp-scene-castle','exp-scene-industrial','exp-scene-rail','exp-scene-airport','exp-scene-dungeon','exp-scene-forest','exp-scene-desert','exp-scene-snow','exp-scene-swamp','exp-scene-mountain','exp-scene-cave','world-scene-harbor','world-scene-space','world-scene-cyber','world-scene-cross-theme','world-rowboat','world-sailboat','world-habitat-docked','world-moon-rover','world-service-robot','world-astronaut','world-neon-kiosk','world-hovercar','world-treasure-chest','world-scene-camp','world-scene-farm','world-scene-city','world-scene-home','world-scene-construction','world-scene-depot','world-scene-outpost','fnd-adult','fnd-cat','fnd-horse']

def _palette_preview(record):
    name=escape(str(record['name']))
    color=escape(str(record.get('displayColor','#B6BDB7')),quote=True)
    rough=float(record.get('roughnessFactor',1))
    metal=float(record.get('metallicFactor',0))
    shine=max(0,min(1,(1-rough)*.55+metal*.1))
    emissive=record.get('emissiveFactor') or [0,0,0]
    accent='#%02x%02x%02x'%tuple(round(min(1,max(0,v))*255) for v in emissive) if any(emissive) else '#547362'
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
<rect width="256" height="256" fill="#eef1ef"/>
<path d="M0 184 256 104v152H0Z" fill="#e1e8e3"/>
<text x="18" y="28" fill="#607168" font-family="Arial,sans-serif" font-size="11" letter-spacing="1.3">MATERIAL ROLE / NO TEXTURE</text>
<ellipse cx="128" cy="181" rx="68" ry="13" fill="#718078" opacity=".18"/>
<path d="m128 58 65 35-65 36-65-36Z" fill="{color}" stroke="#899b90"/>
<path d="m63 93 65 36v68l-65-36Z" fill="{color}" stroke="#899b90"/>
<path d="m193 93-65 36v68l65-36Z" fill="{color}" stroke="#899b90"/>
<path d="m128 58 65 35-65 36-65-36Z" fill="#fff" opacity="{shine:.2f}"/>
<path d="m63 93 65 36v68l-65-36Z" fill="#27372d" opacity=".12"/>
<path d="m193 93-65 36v68l65-36Z" fill="#fff" opacity=".14"/>
<path d="m128 58 65 35-65 36" fill="none" stroke="{accent}" stroke-width="4" opacity=".85"/>
<rect x="0" y="206" width="256" height="50" fill="#fff"/>
<text x="18" y="230" fill="#263a30" font-family="Arial,sans-serif" font-size="19" font-weight="700" textLength="{min(210,max(0,len(name)*11))}" lengthAdjust="spacingAndGlyphs">{name}</text>
<text x="18" y="246" fill="#66756b" font-family="Arial,sans-serif" font-size="10">ROUGH {rough:.2f}   METAL {metal:.2f}</text>
</svg>'''
    return 'data:image/svg+xml;base64,'+base64.b64encode(svg.encode()).decode()

def _materials():
    mats=[]
    for p in sorted((ROOT/'library/materials').glob('*/material.json')):
        r=read_json(p);c=r.get('channels',{});m={'id':r['id'],'name':r['name'],'record':r,'files':{}}
        for kind,channel in c.items():
            file=channel['file'];encoded=base64.b64encode((p.parent/file).read_bytes()).decode()
            m['files'][file]=encoded
            if kind=='basecolor':m['preview']='data:image/png;base64,'+encoded
            elif kind in ('normal','orm','emissive'):m[kind]='data:image/png;base64,'+encoded
        if 'preview' not in m:
            m['preview']=_palette_preview(r)
        mats.append(m)
    return mats

def catalog_data():
    """List metadata only; geometry definitions are fetched for explicit asset actions."""
    require_resources()
    from .build_cache import build_context
    registry=read_json(ROOT/'library/registry.json')['records']
    preview={row['id']:row for row in read_data(ROOT/'library/preview-index.json',max_bytes=32_000_000)}
    expansion=read_json(ROOT/'library/game-expansion.json')
    kits={asset_id:key for key,kit in expansion['kits'].items() for asset_id in [*kit['parts'],kit['assembly']]}
    def row(r):
        ident=r['id'];part=r['kind']=='part';kit=kits.get(ident)
        return {'id':ident,'name':r['name'],'category':'part_'+r['category'] if part else 'assembly','game_category':r['category'],'family':r['kind'],'level':r['level'],'l1':ident.startswith('l1.'),'l2':ident.startswith('l2-'),'l3':r['level']==3,'l4':r['level']==4,'theme':r['theme'],'tags':r['runtime']['tags'],'runtime':r['runtime'],'game_expansion':kit is not None,'game_kit':kit,'expansion':ident.startswith(('exp.','exp-')),'hero':'/__wanxiang/thumbnails/'+ident+'.webp','report':{'triangles':preview.get(ident,{}).get('triangles',0)},'dynamic':True,'status':'definition'}
    assemblies={r['id']:r for r in registry if r['kind']=='assembly'}
    parts=sorted((r for r in registry if r['kind']=='part'),key=lambda r:r['id']+'.json')
    ordered=[assemblies[k] for k in LEAD_ASSEMBLIES if k in assemblies]+[assemblies[k] for k in sorted(assemblies,key=lambda k:k+'.json') if k not in LEAD_ASSEMBLIES]+parts
    assets=sorted((row(r) for r in ordered),key=lambda r:(0 if r['id']=='l3-architecture-building-cottage' else 1 if r['id'].startswith('l3-') else 2 if r['id'].startswith('l4-') else 3))
    return {'version':'3.10.0','title':'万象工坊 3D · LowPoly Studio','offline':True,'parts':{},'assemblies':{},'motions':{},'interfaces':read_json(ROOT/'library/interfaces.json'),'aliases':read_json(ROOT/'library/aliases.json'),'retired':read_json(ROOT/'library/retired.json'),'build_context':build_context(),'materials':_materials(),'game_expansion':expansion,'assets':assets}

def _asset_row(d,part,registry,preview_index,thumbnails):
    ident=d['id'];world=(d.get('quality',{}).get('status')=='worlds') if part else (d.get('metadata',{}).get('collection') in ('worlds-1.9','worlds-2.0'));theme=d.get('theme','shared') if part else d.get('metadata',{}).get('theme','shared');foundation=(d.get('quality',{}).get('status')=='foundation') if part else (d.get('metadata',{}).get('collection')=='foundation-1.8');level=d.get('level',1) if part else d.get('metadata',{}).get('level',3);spec={'schema':'wx.part-build/1.0','id':ident,'part':ident,'style':'lowpoly','params':{}} if part else dict(d)
    thumb=ROOT/'library/thumbnails'/(ident+'.webp');hero='data:image/webp;base64,'+base64.b64encode(thumb.read_bytes()).decode() if thumbnails and thumb.exists() else ''
    game=d.get('game_expansion') or d.get('metadata',{}).get('game_expansion',{})
    return {'game_kit':game.get('kit'),'game_expansion':bool(game),'id':ident,'l1':ident.startswith('l1.'),'l2':ident.startswith('l2-'),'l3':level==3,'l4':level==4,'runtime':registry.get(ident,{}).get('runtime',{}),'game_category':d['category'],'expansion':ident.startswith(('exp.','exp-')),'foundation':foundation,'world':world,'theme':theme,'level':level,'quality':d.get('quality') or d.get('metadata',{}).get('quality',{}),'name':d['name'],'category':'part_'+d['category'] if part else 'assembly','family':'part' if part else 'assembly','tags':d.get('tags',[]),'hero':hero,'views':[],'dynamic':True,'kit':spec,'spec':{'id':ident,'style':'lowpoly','params':{}},'recipe':{'id':ident,'version':'3.10.0'},'report':{'triangles':preview_index.get(ident,{}).get('triangles',0),'nodes':0,'mesh_stats':[],'evidence':{}},'bytes':0,'bom':[],'provenance':{},'status':'definition','cache_hits':0}

def bundle_data(thumbnails=True):
    require_resources()
    parts={p.stem:read_json(p) for p in sorted((ROOT/'library/parts').glob('*.json'))}
    if any(d.get('shape')!='faceted' for d in parts.values()):raise ValueError('Only authored faceted definitions are allowed in Worlds Studio')
    assemblies={p.stem:read_json(p) for p in sorted((ROOT/'library/assemblies').glob('*.json'))}
    motions={p.stem:read_json(p) for p in sorted((ROOT/'library/motions').glob('*.json'))}
    mats=_materials()
    preview_index={d['id']:d for d in read_data(ROOT/'library/preview-index.json',max_bytes=32_000_000)} if (ROOT/'library/preview-index.json').is_file() else {}
    items=[]
    from .build_cache import build_context
    registry={r['id']:r for r in read_json(ROOT/'library/registry.json')['records']}
    def row(d,part):return _asset_row(d,part,registry,preview_index,thumbnails)
    # Deliberately lead with the requested new domains rather than legacy final tanks.
    items=[row(assemblies[k],False) for k in LEAD_ASSEMBLIES if k in assemblies and not assemblies[k].get('internal')]+[row(d,False) for k,d in assemblies.items() if k not in LEAD_ASSEMBLIES and not d.get('internal')]+[row(d,True) for d in parts.values() if not d.get('internal')]
    items=sorted(items,key=lambda r:(0 if r['id']=='l3-architecture-building-cottage' else 1 if r['id'].startswith('l3-') else 2 if r['id'].startswith('l4-') else 3))
    return {'game_expansion':read_json(ROOT/'library/game-expansion.json'),'thumbnail_policy':read_json(ROOT/'authoring/thumbnail-policy.json'),'l3':read_json(ROOT/'library/l3.json'),'l4':read_json(ROOT/'library/l4.json'),'l2':read_json(ROOT/'library/l2.json'),'l1':read_json(ROOT/'library/l1.json'),'version':'3.10.0','title':'万象工坊 3D · LowPoly Studio','offline':True,'aliases':read_json(ROOT/'library/aliases.json'),'retired':read_json(ROOT/'library/retired.json'),'foundation':read_json(ROOT/'library/foundation.json'),'worlds':read_json(ROOT/'library/worlds.json'),'expansion':read_json(ROOT/'library/expansion.json'),'interfaces':read_json(ROOT/'library/interfaces.json'),'registry':registry,'build_context':build_context(),'parts':parts,'assemblies':assemblies,'motions':motions,'materials':mats,'assets':items,'architecture':'The browser and Node share geometry.js; compile definitions on demand, export an immutable recipe snapshot, independent of preview transforms.'}


def asset_data(ident):
    """Return one authored asset and only its transitive model dependencies."""
    require_resources()
    safe_id(ident)
    part_path=ROOT/'library/parts'/(ident+'.json')
    assembly_path=ROOT/'library/assemblies'/(ident+'.json')
    part=part_path.is_file()
    if not part and not assembly_path.is_file():raise FileNotFoundError('Unknown asset: '+ident)
    definition=read_json(part_path if part else assembly_path)
    if definition.get('id')!=ident:raise ValueError('Asset ID does not match definition')
    from .build_cache import dependency_closure
    registry={r['id']:r for r in read_json(ROOT/'library/registry.json')['records']}
    preview={r['id']:r for r in read_data(ROOT/'library/preview-index.json',max_bytes=32_000_000)}
    asset=_asset_row(definition,part,registry,preview,False)
    asset['hero']='/__wanxiang/thumbnails/'+ident+'.webp'
    closure=dependency_closure(asset['kit'])
    parts={};assemblies={} if part else {ident:definition};motions={}
    groups={'part':parts,'assembly':assemblies,'motion':motions}
    for key,value in closure.items():
        kind,dependency_id=key.split(':',1)
        if value.get('missing'):raise FileNotFoundError('Missing model dependency: '+key)
        if kind=='part' and value.get('shape')!='faceted':raise ValueError('Only authored faceted definitions are allowed')
        groups[kind][dependency_id]=value
    return {'assets':[asset],'parts':parts,'assemblies':assemblies,'motions':motions}
