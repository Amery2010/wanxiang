"""39 reusable edge/channel/road/cave subassemblies. Explicit non-solid water."""
from .common import *
D='terrain'

def author():
    for key in ids(D,'waterbed'):
        items=[p('bed',D,'waterbed',key,[2.4,.30,1.0]),
               p('bankA',D,'edge','straight',[2.4,.40,.50],[0,.03,-.72]),
               p('bankB',D,'edge','root',[2.4,.30,.45],[0,.03,.72],[0,180,0]),
               p('root_mass','nature','root','exposed',[.5,.12,.35],[-.75,.27,.58],optional=True)]
        register(D,'channel',key,label(pid(D,'waterbed',key))+'岸槽组件',items,[2.4,.43,1.95],edge=True,
                 function='河床、两岸与可移除岸边细节；不自动填充阻塞水道的碰撞盒。')
    for key in ids(D,'cliff'):
        items=[p('rockface',D,'cliff',key,[2.4,1.4,.85],[0,0,-.35]),
               p('foot',D,'edge','riprap',[2.4,.32,.8],[0,-.05,.26]),
               p('top',D,'surface','bedrock',[2.4,.13,.72],[0,1.32,-.45]),
               p('moss','nature','bark','moss_collar',[.46,.13,.30],[-.7,.24,.37],optional=True)]
        register(D,'cliffedge',key,label(pid(D,'cliff',key))+'崖顶崖脚组',items,[2.4,1.45,1.38],edge=True,
                 notes=['地形网格保留各块原始面，未实施跨块布尔融合或法线焊接。'])
    for key in ids(D,'road'):
        items=[p('strip',D,'road',key,[2.4,.12,.75]),
               p('foundation','architecture','floor','raised',[2.4,.08,.78],[0,-.08,0]),
               p('drain','architecture','drainage','channel_grate',[.14,.055,2.4],[0,.07,-.42],[0,90,0]),
               *fasteners('anchor',[[-.95,.14,.26],[.95,.14,.26]],.028)]
        register(D,'roadedge',key,label(pid(D,'road',key))+'路侧结构段',items,[2.4,.20,.95],edge=True)
    for key in ids(D,'cave'):
        items=[p('archL',D,'cave',key,[.72,1.7,.65],[-1.1,0,0]),
               p('archR',D,'cave',key,[.72,1.7,.65],[1.1,0,0],[0,180,0]),
               p('lintel',D,'cliff','layered',[2.5,.48,.74],[0,1.65,0]),
               p('floor','architecture','floor','plank',[2.75,.10,1.2],[0,-.10,0],material='mat.stone')]
        register(D,'caveportal',key,label(pid(D,'cave',key))+'洞口框组',items,[2.92,2.13,1.20],mount=[2.75,1.2],
                 notes=['中部净空由左右岩壁分件维持；碰撞使用逐件静态网格。'])
    transitions=[('grass_rock','surface','hummock','terrace','root','草甸接台地'),
                 ('sand_berm','surface','dune','ripple','beach','沙丘接风纹'),
                 ('mud_rut','surface','dried','rutted','marsh','干泥接车辙'),
                 ('snow_shelf','edge','snow','bedrock','snow','雪檐接裸岩'),
                 ('fractured_path','surface','fractured','scree','riprap','断层接碎石坡')]
    for key,group,a,b,edge,name in transitions:
        items=[p('sideA',D,group,a,[1.2,.18,1.6],[-.6,0,0]),p('sideB',D,'surface',b,[1.2,.18,1.6],[.6,0,0]),
               p('seam',D,'edge',edge,[.18,.12,1.6],[0,.06,0]),
               p('detail','architecture','ruin','cracked_slab',[.36,.08,.22],[.66,.17,.41],optional=True)]
        register(D,'transition',key,name+'过渡拼装块',items,[2.4,.25,1.6],edge=True,
                 function='两种真实地表剖面与对应接边组成的局部过渡段；不是换色变体。')
