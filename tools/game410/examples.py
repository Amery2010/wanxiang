"""Ten explicit compositions. Reuse public parts, keep every instance editable."""
from .common import *

def pid(kit,key):
    choices=[i for i in ADDED if i.endswith('.'+key) and '.game_'+kit+'.' in i]
    if len(choices)!=1:raise ValueError((kit,key,choices))
    return choices[0]

def author():
    def it(kit,key,name,pos=(0,0,0),rot=None,**kw):return inst(name,part=pid(kit,key),pos=pos,rot=rot,**kw)
    demo('dungeon','地牢栅门装配样例',[
        it('dungeon','pointed_portal','portal'),it('dungeon','portcullis_leaf','gate',(0,0,0)),
        it('dungeon','torch_sconce','sconce-l',(-.775,.65,.20)),it('dungeon','torch_sconce','sconce-r',(.775,.65,.20)),
        it('dungeon','floor_grate_tile','drain',(0,-.11,.69))],
        '开放门框、独立门叶和壁托组成的静态入口；不包含开门动画与陷阱逻辑。')
    demo('traversal','攀爬训练墙模块',[
        it('traversal','wallrun_panel','wall'),it('traversal','crimp_hold','crimp-l',(-.39,.15,.10)),
        it('traversal','jug_hold','jug-r',(.32,.43,.10)),it('traversal','crimp_hold','crimp-top',(-.32,.80,.10))],
        '攀点与真实墙面附着的静态示例；碰撞和角色吸附由游戏实现。')
    demo('survival','野外制革与采集样例',[
        it('survival','hide_stretcher','frame'),it('survival','waterskin','skin',(.57,0,.05)),
        it('survival','herb_bundle','herbs',(-.55,0,.09)),it('survival','kindling_bundle','twigs',(0,.08,.40))],
        '一组制革及采集部件组合，保留独立资源边界。')
    demo('farming','葡萄架与果丛样例',[
        it('farming','fan_trellis','trellis'),it('farming','grape_cluster','grapes-l',(-.23,.48,.10)),
        it('farming','grape_cluster','grapes-r',(.25,.47,.10)),it('farming','strawberry_crown','crown',(0,0,.34))],
        '将收获物悬挂在支架上的简单园艺组合，作物生长逻辑不在本模型中。')
    demo('scifi','科幻舱门闭合装配',[
        it('scifi','bulkhead_frame','frame'),it('scifi','bulkhead_leaf','leaf'),
        it('scifi','corridor_rib','rib',(0,0,-.65))],
        '舱框与配套门叶的静态闭合状态；叶片仍为独立可平移节点。')
    items=[it('automation','gimbal_ring','ring',(0,.065,0),(90,0,0))]
    for k in range(3):
        a=k*math.tau/3
        items.append(it('automation','threejaw_finger','finger-'+str(k),(.275*math.cos(a),.05,.275*math.sin(a)),(0,180-k*120,0)))
    demo('automation','三指机械夹具静态装配',items,'环架与三只独立指体，尚未绑定驱动、接触和抓取物理。')
    items=[it('creature','arthropod_thorax','thorax',(0,.30,0)),it('creature','beetle_head','head',(0,.33,.58))]
    for z in (-.22,0,.22):
        suffix=str(round((z+.22)*100));items += [it('creature','spider_leg','leg-r-'+suffix,(.23,0,z)),it('creature','spider_leg','leg-l-'+suffix,(-.23,0,z),(0,180,0))]
    demo('creature','节肢前躯与六足装配',items,'头、胸和六条独立步足的静态骨架前躯示例，不是完整蒙皮角色。')
    demo('equipment','弩身部件对位样例',[
        it('equipment','crossbow_stock','stock'),it('equipment','crossbow_limb','limb',(0,.77,.04))],
        '手持弩的弩托和反曲臂对位示例，未装弦、未绑定发射和动画。')
    items=[it('waterland','stream_junction_bank','banks')]
    for k in range(3):items.append(it('waterland','stepping_stone','stone-'+str(k),((k-1)*.30,0,-.10),params={'width':.24,'height':.13,'depth':.24}))
    # Legal parameter minima are enforced; use scaled instances for small stones.
    for x in items[1:]:x.pop('params',None);x['scale']=[.45,.8,.45]
    demo('waterland','溪岸踏石组合',items,'保留水道开口的三块踏石与岸边；没有水面或流体模拟。')
    demo('puzzle','晶钥与祭坛组合',[
        it('puzzle','altar_basin','basin'),it('puzzle','tri_receiver','receiver',(0,.16,0)),
        it('puzzle','tri_key','key',(0,.20,.025)),it('puzzle','socketed_crystal','core',(.64,0,0))],
        '三角钥匙和贯通槽的尺寸参照，独立晶核保留为拆装部件；无解谜判定逻辑。')
