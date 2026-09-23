"""Original game-kit authors. Metres, +Y up, +Z forward. No baked model input.

Reusable authored profiles, not palette/size variants. Collision fields express
adapter intent only: the library does not run gameplay or physics.
"""
from __future__ import annotations
from copy import deepcopy
import inspect, math
from foundation.common import PARTS, ASSEMBLIES, Q, P, C, number, schema, port, box, cube, loft, poly, extrude, lathe, rod, assembly, inst, mul, add
from l1_expansion.common import register, placed, dimensions, DOMAIN_NAMES
from repair39.common import (mesh, rect, circle, plate, spin, cyl, bezier, sweep,
    pipe, grid_shell, ring_tube, block, basebox, ellipsoid, profile_z, leaf, tube,
    beam, slab_polygon)
REV='3.10.0'
ADDED=[]
DEMOS=[]
KITS={
 'dungeon':('地牢与城堡','RPG / 地牢探索 / 模块化建筑'),
 'traversal':('攀爬与平台','动作冒险 / 平台跳跃 / 跑酷'),
 'survival':('生存与采集','生存 / 采集 / 工艺制作'),
 'farming':('农场与园艺','种植 / 经营 / 乡村生活'),
 'scifi':('科幻舱室','科幻探索 / 空间站 / 舰船内饰'),
 'automation':('机械与自动化','工厂 / 自动化 / 机器人'),
 'creature':('异形与小型生物','怪物 / 虫类 / 两栖 / 水生'),
 'equipment':('冒险装备','角色穿戴 / 武器外观 / 飞行装备'),
 'waterland':('水岸与洞穴','水岸 / 洞穴 / 熔岩 / 雪地'),
 'puzzle':('机关与魔法','解谜 / 光路 / 符石 / 魔法装置')}
P.update(gStone='#858B8C',gStoneLight='#ABB1AC',gStoneDark='#505D64',gStoneWarm='#AAA18A',
         gSteel='#4C6573',gMetal='#A8B8B9',gCopper='#BE8852',gCloth='#597E80',
         gGlow='#60CAD6',gRed='#BE6852',gPurple='#9A80BD',gAmber='#E7BD6B',
         gLeaf='#6C964E',gLeafDark='#3F674F',gCream='#E8DCBD',gLeather='#865D42',
         gWood='#A57A4D',gWoodDark='#604A36',gBark='#71523B',gSoil='#735B46',gKernel='#DEAD56')

def detail(form):
    f=deepcopy(form);f['enabled']=Q('detail');return f

def author(kit, domain, key, name, forms, size, *, purpose, ports=None,
           collision='authored-mesh', material='mat.matte', tags=(), max_tris=12000, anchor='base'):
    """All geometry and named datums share the same dimensional transform."""
    if kit not in KITS:raise ValueError(kit)
    fs=deepcopy(forms)
    roles={}
    for role,keys in {'mat.metal':('gSteel','gMetal','gCopper'), 'mat.wood':('gWood','gWoodDark','gBark'), 'mat.stone':('gStone','gStoneLight','gStoneDark','gStoneWarm'), 'mat.leaf':('gLeaf','gLeafDark'), 'mat.leather':('gLeather',), 'mat.fabric':('gCloth',), 'mat.emissive.cyan':('gGlow',)}.items():
        for key_ in keys:roles[C(key_)]=role
    for k,f in enumerate(fs):
        if f.get('color') in roles:
            role=roles[f['color']]
            if domain=='creature' and role=='mat.metal':role='mat.matte'
            if domain=='robot' and f.get('color')==C('gCloth'):role='mat.rubber'
            f.setdefault('material',role)
        f.setdefault('name',f'{key}_{k:02}')
        f.setdefault('roundable',False)
        f.setdefault('style_overrides',{'toon':{'smooth_angle':50}})
    if ports is None:
        ports=[port('datum.mount',[0,0,0],[0,-1,0],[1,0,0]),
               port('datum.top',[0,size[1],0],[0,1,0],[1,0,0])]
    ident=register(domain,'game_'+kit,key,name,fs,size,ports=ports,collision=collision,
       material=material,anchor=anchor,description=purpose+'；游戏用外观部件，交互和碰撞由接入引擎实现。',
       purpose=purpose,tags=('Game-Expansion-3.10',kit,KITS[kit][0],*tags))
    d=PARTS[ident]
    module=inspect.currentframe().f_back.f_code.co_filename.split('/')[-1]
    d['version']=REV
    d['source'].update(authoring='tools/game410/'+module,revision=REV,type='original_game_asset_profiles')
    d['quality'].update(review_scope='game-expansion-3.10',visual_review='see docs/game410/index.html; no automatic aesthetic rating')
    d['semantic'].update(game_kit=kit,game_use=KITS[kit][1],consumer_example='library/game-expansion.json',
        status='implemented; geometry and interface checks, not commercial certification')
    d['runtime']['triangle_budget']=max_tris
    d['game_expansion']={'version':REV,'kit':kit,'primary_role':purpose,'authoring':'procedural-profile',
       'physics_implemented':False,'rig_implemented':False,'parameter_units':'m',
       'visual_evidence':'docs/game410/index.html'}
    ADDED.append(ident)
    return ident

def ring_y(r,y,h,wall,color='gMetal',n=16):
    return spin([(r-wall,y),(r,y),(r,y+h),(r-wall,y+h)],color,n)

def annulus_xy(ro,ri,depth,color='gMetal',center=(0,0),n=24):
    return plate(circle(ro,center,n),depth,color,holes=[circle(ri,center,n)])

def wedge_xz(outline,y,h,color='gStone'):
    return slab_polygon(outline,y,h,C(color))

def arc_slab(r0,r1,a0,a1,y,h,color='gStone',n=12):
    out=[[r1*math.cos(math.radians(a0+(a1-a0)*k/n)),r1*math.sin(math.radians(a0+(a1-a0)*k/n))] for k in range(n+1)]
    out += [[r0*math.cos(math.radians(a0+(a1-a0)*k/n)),r0*math.sin(math.radians(a0+(a1-a0)*k/n))] for k in range(n,-1,-1)]
    return wedge_xz(out,y,h,color)

def capped_panel(points,thickness,color='gSteel'):
    return plate(points,thickness,color)

def teeth_disc(r,root,teeth,depth,color='gMetal',hole=.09):
    out=[]
    for k in range(teeth):
        for phase,rad in [(0,root),(.20,r),(.64,r),(.86,root)]:
            a=(k+phase)*math.tau/teeth;out.append([math.cos(a)*rad,math.sin(a)*rad])
    return plate(out,depth,color,holes=[circle(hole,n=16)] if hole else [])

def tube_curve(ps,r,color='gSteel',r_end=None,n=12,sides=8):
    pts=bezier(ps,n)
    radii=[r+(r_end-r)*k/(n-1) if r_end is not None else r for k in range(n)]
    return tube(pts,radii,C(color),sides)

def flattened_leaf(root,tip,width,color='gLeaf',curve=.06):
    return leaf(root,tip,width,C(color),curve=curve,thickness=.014)

def demo(kit,name,items,description):
    ident='l2-game410-'+kit
    if ident in ASSEMBLIES:raise ValueError(ident)
    assembly(ident,name,'gameplay',items,level=2,description=description,
       metadata={'collection':'game-3.10','level':2,'theme':'game-'+kit,'game_kit':kit,
        'quality':{'status':'l2','approval':'not-user-approved','review_scope':'game410-composition'},
        'runtime':{'schema':'wx.runtime-metadata/1.0','units':'m','up':'+Y','forward':'+Z',
          'collision':{'type':'children'},'triangle_budget':100000,
          'lod':{'levels':[],'reason':'demonstrates authored child profiles; no scene LOD claim'},
          'engine_adapter_required':True},
        'game_expansion':{'version':REV,'kit':kit,'purpose':'composition example, no gameplay logic'}})
    d=ASSEMBLIES[ident];d['version']=REV;d['tags']=['Game-Expansion-3.10',kit,KITS[kit][0],'装配样例']
    d['metadata']['source']={'type':'original_composition','license':'project-authored','authoring':'tools/game410/examples.py','revision':REV}
    DEMOS.append(ident);return ident
