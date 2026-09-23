"""95 botanically inspired reusable growth modules; no whole-tree duplicates."""
from .common import *
D='nature'
NONE={'type':'none','reason':'vegetation decoration; root owner supplies physics if needed'}

def stem(node,height=1,at=(0,0,0),key='twig',rot=(0,0,0)):
    return p(node,D,'branch',key,[.12,height,.12],at,rot,collision=NONE)

def author():
    for index,key in enumerate(ids(D,'leaf')):
        stemtype='cane' if key in ('heart','clover','trifoliate') else 'whorl' if key in ('needle','pine_pair','conifer_spray') else 'y_fork'
        items=[stem('branch',1.12,key=stemtype)]
        for j in range(6):
            y=.35+(j//2)*.26;side=-1 if j%2==0 else 1
            items.append(p('leaf'+str(j),D,'leaf',key,[.35,.46,.12],[side*.04,y,0],[18,40*j,side*48],collision=NONE))
        items.append(p('bud',D,'flower','bud',[.075,.13,.075],[0,1.06,0],optional=True,collision=NONE))
        register(D,'leafybranch',key,label(pid(D,'leaf',key))+'着叶枝组',items,[.95,1.28,.75],collision=NONE,mount=[.08,.08],
                 function='可插入树冠或灌木的独立着叶枝组；不含整株树木。')
    for key in ids(D,'flower'):
        items=[stem('peduncle',.75,key='segment'),p('head',D,'flower',key,[.42,.30,.42],[0,.67,0],collision=NONE),
               p('leafA',D,'leaf','lance',[.12,.36,.06],[0,.2,0],[0,0,-45],collision=NONE),
               p('leafB',D,'leaf','lance',[.12,.36,.06],[0,.38,0],[0,180,-45],collision=NONE),
               p('bract',D,'flower','sepal',[.25,.07,.25],[0,.66,0],optional=True,collision=NONE)]
        if key in ('spike','catkin','umbrella','pompom'):items.append(p('sidebud',D,'flower','bud',[.12,.20,.12],[.16,.55,.04],[0,0,-25],collision=NONE))
        register(D,'inflorescence',key,label(pid(D,'flower',key))+'花梗模块',items,[.55,1.03,.46],collision=NONE,mount=[.035,.035])
    for key in ids(D,'fruit'):
        items=[stem('branch',1.0,key='y_fork')]
        for i,(x,y,z) in enumerate([(-.22,.73,0),(.22,.82,.025),(0,.98,-.04)]):
            items.extend([p('fruit'+str(i),D,'fruit',key,[.23,.28,.23],[x,y,z],collision=NONE),
                          stem('pedicel'+str(i),.17,[x*.55,y-.10,z],key='cane',rot=[0,0,-30 if x>0 else 30])])
        items.extend([p('leaf'+str(i),D,'leaf','ovate',[.23,.37,.05],[side*.04,.52,0],[0,90*i,side*55],collision=NONE) for i,side in enumerate([-1,1])])
        register(D,'fruiting',key,label(pid(D,'fruit',key))+'结果枝组',items,[.75,1.30,.55],collision=NONE,mount=[.08,.08])
    for key in ids(D,'frond'):
        items=[p('crown',D,'root','fibrous',[.28,.20,.28],collision=NONE)]
        for i in range(5):
            a=i*72
            items.append(p('frond'+str(i),D,'frond',key,[.34,.85,.12],[0,.16,0],[24,a,0],collision=NONE))
        items.append(p('shoot',D,'frond','curled',[.12,.45,.08],[0,.2,0],optional=True,collision=NONE))
        register(D,'frondcrown',key,label(pid(D,'frond',key))+'叶冠簇',items,[1.08,1.0,1.08],collision=NONE,mount=[.25,.25])
    for key in ids(D,'root'):
        items=[stem('collar',.45,key='hollow' if key=='exposed' else 'segment')]
        for j in range(4):
            a=j*90;items.append(p('root'+str(j),D,'root',key,[.52,.35,.38],[0,-.15,0],[0,a,0],collision=NONE))
        items.append(p('bark',D,'bark','moss_collar',[.24,.25,.24],[0,.12,0],optional=True,collision=NONE))
        register(D,'rootcollar',key,label(pid(D,'root',key))+'根颈模块',items,[.92,.48,.92],collision=NONE,mount=[.14,.14],
                 notes=['允许局部根段在地下；不使用包围盒底面强行落地。'])
    capkeys={'umbrella_cap','bell_cap','bracket_cap','funnel_cap','puffball','morel'}
    for key in ids(D,'fungus'):
        cap=key if key in capkeys else 'umbrella_cap'
        items=[p('substrate',D,'bark','peeling',[.8,.11,.58],collision=NONE)]
        for j,(x,z,h) in enumerate([(-.22,0,.30),(.12,-.1,.43),(.24,.18,.23)]):
            items.extend([p('stipe'+str(j),D,'fungus','stipe',[.07,h,.07],[x,.07,z],collision=NONE),
                          p('cap'+str(j),D,'fungus',cap,[h*.85,h*.35,h*.85],[x,h+.035,z],collision=NONE)])
        if key not in capkeys:
            items.append(p('feature',D,'fungus',key,[.33,.13,.32],[.12,.37,-.1],optional=key in ('gills','pores'),collision=NONE))
        register(D,'fungalpatch',key,label(pid(D,'fungus',key))+'腐木着生组',items,[.85,.63,.66],collision=NONE,mount=[.8,.58])
    for key in ids(D,'crop'):
        leaf='strap' if key in ('wheat_ear','rice_panicle','barley_awn','sorghum_head') else 'ovate'
        items=[p('root_mass',D,'root','fibrous',[.18,.12,.18],collision=NONE),stem('stalk',.88,key='cane')]
        for i in range(4):items.append(p('leaf'+str(i),D,'leaf',leaf,[.19,.4,.05],[0,.20+i*.15,0],[30,i*137,0],collision=NONE))
        items.append(p('yield',D,'crop',key,[.30,.32,.25],[0,.77,0],collision=NONE))
        register(D,'cropstem',key,label(pid(D,'crop',key))+'收获部位枝组',items,[.8,1.10,.75],collision=NONE,mount=[.08,.08],
                 function='茎叶和产出部位分节点，便于上层农作物换阶段或隐藏收获件；不内置农业数值。')
