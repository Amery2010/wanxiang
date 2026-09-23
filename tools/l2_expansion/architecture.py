"""94 structural bays, genuine openings, access sections and roof/edge modules."""
from .common import *
D='architecture'

def author():
    # Window/opening cassettes: perimeter is never filled by a hidden solid slab.
    for key in ids(D,'opening'):
        w,h=1.8,2.2
        items=[p('perimeter',D,'opening',key,[w,h,.18]),
               plate('sill',[w+.16,.10,.38],[0,-.10,0]),
               p('drip',D,'trim','drip',[.28,.10,w+.16],[0,-.11,.13],rot=[0,90,0],anchor='center'),
               *fasteners('fix',[[-w*.44,.16,.11],[w*.44,.16,.11]],.055)]
        if key in ('rect','arch','point','lancet','segment'):
            items.append(post('mullion',h*.72,[0,.08,0],.045))
        elif key in ('round','octagon','diamond'):
            items.append(bar('transom',[-w*.34,h*.5,0],[w*.34,h*.5,0],.04))
        register(D,'opening',key,label(pid(D,'opening',key)).replace('基件','')+'安装窗芯',items,[w+.16,h,.38],edge=True,
                 function='含窗台滴水与紧固位的真实洞口安装单元；不包含玻璃及墙体。')
    for key in ids(D,'wall'):
        w,h,d=2.4,2.7,.22
        items=[p('infill',D,'wall',key,[w-.16,h-.20,d],[0,.10,0]),
               post('studL',h,[-(w-.08)/2,0,0],.08),post('studR',h,[(w-.08)/2,0,0],.08),
               bar('top',[-w/2,h-.04,0],[w/2,h-.04,0],.08),
               plate('track',[w,.08,.26]),
               p('drip',D,'trim','coping',[.36,.10,w],[0,h,0],[0,90,0]),
               *fasteners('anchor',[[-1.12,.04,.14],[1.12,.04,.14]])]
        register(D,'wallbay',key,label(pid(D,'wall',key))+'框架墙段',items,[w,h+.1,.36],edge=True,
                 notes=['非承重计算模型；穿孔和检修口由真实几何保持，未生成跨洞口实体碰撞盒。'])
    for key in ids(D,'roof'):
        items=[p('skin',D,'roof',key,[2.4,.65,2.4],[0,.2,0]),
               bar('eaveL',[-1.15,.13,-1.18],[-1.15,.13,1.18],.12),
               bar('eaveR',[1.15,.13,-1.18],[1.15,.13,1.18],.12),
               bar('tie',[-1.15,.13,0],[1.15,.13,0],.10),
               p('gutter',D,'drainage','box_gutter',[.18,.15,2.45],[1.22,.12,0]),
               p('rafter_end',D,'traditional','rafter',[.10,.10,.18],[-1.14,.12,1.20],optional=True)]
        if key in ('sawtooth','standing_seam','corrugated','glazed'):
            items.extend([bar('purlin'+str(i),[-1.1,.2,z],[1.1,.2,z],.075) for i,z in enumerate([-.8,.8])])
        register(D,'roofbay',key,label(pid(D,'roof',key))+'檩条排水单元',items,[2.55,.85,2.45],edge=True,
                 function='可安装到上层建筑的屋面面板、檩条、檐槽功能段。')
    for key in ids(D,'railing'):
        items=[p('infill',D,'railing',key,[1.8,.9,.075],[0,.14,0]),
               post('postL',1.13,[-.97,0,0],.085),post('postR',1.13,[.97,0,0],.085),
               bar('handrail',[-1.03,1.10,0],[1.03,1.10,0],.065,section='bulb'),
               *[p('foot'+str(i),D,'joinery','shoe',[.18,.14,.18],[x,0,0]) for i,x in enumerate([-.97,.97])]]
        register(D,'railing',key,label(pid(D,'railing',key))+'带扶手栏段',items,[2.06,1.14,.18],edge=True)
    stair_types=names('closed:实体直跑 open:开放踏板 grating:工业栅梯 bullnose:圆鼻梯段 switchback:折返平台 spiral:旋转踏步')
    for key,name in stair_types:
        items=[];w=1.1;n=5;rise=.18;run=.28
        if key=='spiral':
            items.append(post('axis',1.85,[0,0,0],.11,section='bulb'))
            extent=natural_size(pid(D,'stair','spiral_tread'));railpoints=[]
            for i in range(n):
                # Author-space sleeve centre, not the asymmetrical mesh bounds.
                items.append(p('tread'+str(i),D,'stair','spiral_tread',[extent[0]*.94,.13,extent[2]*.94],
                               [0,rise*i,0],[0,-35*i,0],pivot=[-.5,0,-.5]))
                theta=math.radians(17.5+35*i);x,z=.90*math.cos(theta),.90*math.sin(theta)
                items.append(post('railpost'+str(i),.90,[x,rise*i+.12,z],.036,section='bulb'))
                railpoints.append([x,rise*i+1.02,z])
            items.extend(bar('handrail'+str(i),railpoints[i],railpoints[i+1],.045,section='bulb') for i in range(n-1))
            items.append(p('collar',D,'joinery','shoe',[.26,.10,.26]))
            size=[2.0,1.85,2.0]
        else:
            kind={'closed':'closed_tread','open':'open_tread','grating':'grating_tread','bullnose':'bullnose','switchback':'closed_tread'}[key]
            for i in range(n):
                z=(i-(n-1)/2)*run;y=i*rise
                items.extend([p('tread'+str(i),D,'stair',kind,[w,.1,run+.012],[0,y,z]),
                              p('strip'+str(i),D,'stair','anti_slip',[w-.07,.015,.055],[0,y+.10,z-run*.36],optional=True)])
            for side in (-1,1):items.append(bar('stringer'+str(side),[side*.47,-.1,-.70],[side*.47,.82,.70],.16,depth=.07,section='c'))
            if key=='switchback':items.append(plate('landing',[1.8,.12,.8],[.35,.80,1.02]))
            items.extend([post('railBase',1.0,[-.61,0,-.62],.055),post('railTop',1.0,[-.61,.72,.62],.055),
                          bar('rail',[-.61,1.0,-.62],[-.61,1.72,.62],.05,section='bulb')])
            size=[1.8 if key=='switchback' else 1.22,1.77,2.84 if key=='switchback' else 1.52]
        register(D,'stair',key,name+'功能梯段',items,size,mount=[w,.28],function='五级可复用楼梯段；踏面、承托与扶手分件，不包含建筑楼层。')
    for key in ids(D,'column'):
        items=[p('column',D,'column',key,[.64,2.0,.64],[0,.16,0]),
               plate('base',[.82,.16,.82]),plate('cap',[.86,.16,.86],[0,2.16,0]),
               p('seat',D,'joinery','saddle',[.50,.24,.36],[0,2.32,0]),
               *fasteners('basebolt',[[x,.16,z] for x in [-.32,.32] for z in [-.32,.32]],.06)]
        register(D,'columnbay',key,label(pid(D,'column',key))+'梁托立柱段',items,[.86,2.56,.86],mount=[.82,.82])
    traditional=[('gong','dou','层叠斗栱'),('qiao','ang','挑檐翘昂'),('fang','que','额枋雀替'),('purlin','gong','檩枋承托'),
                 ('screen','lattice','双层窗屏'),('moon_gate','screen','月洞屏边'),('tile_end','drip_tile','瓦当滴水'),('hip_finial','ridge_beast','屋脊端饰')]
    for key,second,name in traditional:
        items=[p('primary',D,'traditional',key,[.95,.68,.30]),
               p('secondary',D,'traditional',second,[.60,.32,.28],[0,.68,0]),
               p('seat',D,'joinery','tenon',[.34,.13,.24],[0,-.13,0]),
               *fasteners('pin',[[.28,.2,.17],[-.28,.2,.17]],.04,'clevis_pin')]
        if key=='gong':
            # The dou supports the curved arm from below. A spanning head beam
            # meets both raised arm tips; a narrow block above the gap would float.
            items=[p('dou',D,'traditional','dou',[.38,.24,.35]),
                   p('gong',D,'traditional','gong',[.95,.40,.25],[0,.18,0]),
                   p('headBeam',D,'traditional','fang',[.96,.16,.29],[0,.57,0]),
                   p('seat',D,'joinery','tenon',[.28,.12,.24],[0,-.1,0]),
                   *fasteners('pin',[[.28,.34,.13],[-.28,.34,.13]],.035,'clevis_pin')]
        register(D,'traditional',key,name+'构件簇',items,[.96,.73,.35] if key=='gong' else [.95,1.0,.34],mount=[.34,.24],
                 notes=['传统结构的风格化游戏部件，不宣称古建营造尺度或历史复原。'])
    for key in ids(D,'joinery'):
        items=[p('joint',D,'joinery',key,[.44,.34,.40]),
               bar('beamL',[-.8,.18,0],[-.20,.18,0],.18,section='i'),
               bar('beamR',[.20,.18,0],[.8,.18,0],.18,section='i'),
               *fasteners('bolt',[[x,.35,z] for x in [-.14,.14] for z in [-.12,.12]],.045)]
        if key in ('knee','gusset','saddle','shoe'):items.append(post('shortPost',.52,[0,-.5,0],.18))
        register(D,'jointbay',key,label(pid(D,'joinery',key))+'接续节点',items,[1.6,.86,.40],edge=True,
                 function='梁段与连接件的可维护节点；接口描述设计截面，不做结构承载认证。')
