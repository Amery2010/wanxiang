"""Visual industrial prefabs, not pressure-vessel or machinery engineering designs."""
from .common import *
from .interiors import fourlegs, ring, cabinet
from .objects import wheel, propeller
WHITE='#D7D9CF'
P='#78978E';M='#A1ADAC';D='#485960';O='#B69A65';K='#35444A'

def finish(ident,structure,work,problem,change):
    replace(ident,[node(ident,'frame',structure,material='mat.paint'),node(ident,'working_parts',work,material='mat.metal')],problem,change)
    ASSEMBLIES[ident]['metadata'].setdefault('production',{})['use_limitations']=['Original visual game/scene model. Not a functional machine, safety, electrical or pressure-vessel engineering design.']

def axis_cylinder(a,b,r,c=M,sides=16):return tube([a,b],r,c,sides)

def disk(center,r,width,c=M,axis='x',hole=0):
    fs=[revolve([(max(hole,.001),-width/2),(r,-width/2),(r,width/2),(max(hole,.001),width/2)],c,24)]
    return placed(fs,center,[0,0,90] if axis=='x' else [90,0,0] if axis=='z' else [0,0,0])

def machine(key):
    ident='l3-industry-machine-'+key;a=[basebox([1.6,.13,.94],[0,0,0],D)];b=[]
    if key=='lathe':
        a += [basebox([.34,.69,.75],[x,.13,0],P) for x in (-.58,.58)]+[basebox([1.48,.12,.44],[0,.77,0],M)]
        a += [basebox([.33,.51,.62],[-.59,.86,0],P),basebox([.25,.24,.45],[.56,.89,0],P)]
        b += disk([-.39,1.13,0],.20,.13,M)+[axis_cylinder([-.31,1.13,0],[.46,1.13,0],.065,O),axis_cylinder([.48,1.13,0],[.63,1.13,0],.045,M),basebox([.30,.09,.53],[0,.91,.09],D),basebox([.10,.18,.09],[0,.99,.11],M)]
        for q in range(3):b.append(block([.055,.063,.050],[-.31,1.13+.125*math.cos(q*math.tau/3),.125*math.sin(q*math.tau/3)],D))
        b+=disk([0,.81,.37],.105,.035,D,'z')
    elif key in ('drill','mill'):
        a += [basebox([.86,.10,.74],[0,.13,0],P),axis_cylinder([-.22,.23,-.19],[-.22,1.70,-.19],.075,M),basebox([.39,.28,.49],[-.10,1.40,.04],P)]
        b += [basebox([.76,.065,.53],[0,.87,.12],M),beam([-.22,.84,-.19],[0,.84,.12],.11,D),axis_cylinder([.05,1.38,.14],[.05,1.10,.14],.033,M),axis_cylinder([.05,1.10,.14],[.05,1.01,.14],.010,D)]
        if key=='mill':a += [basebox([.38,.63,.38],[-.22,.23,-.19],P)];b += [basebox([.58,.065,.40],[0,.81,.12],D),axis_cylinder([-.4,.82,.20],[.4,.82,.20],.02,M)]
        for s in (-1,1):b.append(beam([.15,1.46,.20],[.15+s*.19,1.48,.20],.018,M))
    elif key in ('press','punch','bender'):
        h=1.73;a += [basebox([.14,h,.41],[x,.13,-.12],P) for x in (-.62,.62)]+[basebox([1.38,.20,.45],[0,h-.04,-.12],P),basebox([1.1,.10,.59],[0,.72,.03],M)]
        if key=='bender':b += [basebox([1.12,.25,.095],[0,1.12,.01],M),basebox([1.13,.05,.14],[0,.83,.03],D)]
        else:b += [axis_cylinder([0,1.24,-.08],[0,1.66,-.08],.12,M),basebox([.37,.075,.33],[0,1.17,-.03],M)]
        for x in (-.43,.43):b.append(axis_cylinder([x,.87,-.10],[x,1.62,-.10],.023,M))
    elif key in ('grinder','polisher'):
        a += [basebox([.50,.82,.42],[0,.13,0],P),basebox([.79,.075,.53],[0,.92,0],M)]
        b += [axis_cylinder([-.19,1.13,0],[.19,1.13,0],.145,P),axis_cylinder([-.52,1.13,0],[.52,1.13,0],.04,M)]
        for x in (-.42,.42):
            b+=disk([x,1.13,0],.21,.09,'#CAC3A4' if key=='polisher' else '#737B7A');b.append(block([.16,.035,.21],[x,.99,.15],M))
    elif key=='bandsaw':
        a += [basebox([.62,.48,.61],[0,.13,0],P),basebox([.12,1.08,.34],[-.29,.60,-.15],P),basebox([.65,.26,.36],[0,1.54,-.15],P),basebox([.79,.055,.70],[0,.87,0],M)]
        b += disk([0,1.57,-.10],.20,.14,P,'z')+disk([0,.45,-.10],.20,.14,P,'z')+[basebox([.007,1.07,.025],[.18,.49,.015],M),basebox([.14,.09,.10],[.18,1.28,.014],D)]
    elif key=='saw':
        a += [basebox([1.20,.68,.72],[0,.13,0],P),basebox([1.52,.065,.87],[0,.80,0],M)]
        b += disk([0,.75,0],.255,.018,M)+[basebox([.065,.10,.79],[.32,.865,0],D)]
        for i in range(24):
            q=math.tau*i/24;b.append(extrude_xy([[-.012,0],[.012,0],[0,.035]],.025,M))
            b[-1]=placed([b[-1]],[0,.75+.25*math.cos(q),.25*math.sin(q)],[0,90,-q*180/math.pi])[0]
    elif key in ('cnc','laser','printer'):
        ww=1.28;hh=1.90;a += [basebox([ww,.67,.78],[0,.13,0],P),basebox([ww,.06,.80],[0,.81,0],M)]
        for x in (-.60,.60):
            for z in (-.36,.36):a.append(basebox([.055,.98,.055],[x,.84,z],D))
        for z in (-.36,.36):a.append(block([ww,.055,.055],[0,1.82,z],D))
        for x in (-.60,.60):a.append(block([.055,.055,.77],[x,1.82,0],D))
        b += [axis_cylinder([-.56,1.57,.08],[.56,1.57,.08],.018,M),basebox([.18,.22,.14],[.12,1.40,.08],P),axis_cylinder([.12,1.37,.08],[.12,1.13,.08],.015,M)]
        for x in (-.46,.46):b.append(axis_cylinder([x,.91,-.29],[x,1.75,-.29],.018,M))
        b += [block([.90,.045,.60],[0,1.06,0],D),block([.22,.16,.035],[.42,.53,.415],K)]
        if key=='printer':b += disk([.52,1.95,-.18],.18,.13,O,'z',.075)+[basebox([.12,.12,.12],[.1,1.085,.08],O)]
        if key=='cnc':
            a.append(basebox([ww,.97,.045],[0,.85,-.375],P));a+=[basebox([.20,.97,.77],[s*.54,.85,0],P) for s in (-1,1)]
    elif key=='roll':
        a += [basebox([.19,1.12,.71],[x,.13,0],P) for x in (-.60,.60)]
        for yy,z in ((.95,-.15),(.95,.15),(1.16,0)):b.append(axis_cylinder([-.54,yy,z],[.54,yy,z],.125,M))
        b+=disk([.75,.95,.15],.20,.035,D)
    elif key=='welder':
        a += fourlegs(1.42,.78,.86,.065,D)+[basebox([1.50,.065,.88],[0,.86,0],M),basebox([.38,.42,.47],[-.43,.13,0],P)]
        b += [tube([[-.22,.39,.17],[-.15,.20,.52],[.42,.12,.51],[.49,.89,.30],[.28,.97,.15]],.018,D,8),beam([.28,.97,.15],[.40,1.03,.20],.05,D),basebox([.39,.04,.26],[0,.93,0],O)]
    finish(ident,a,b,'不同机床共用同一台面和小型传动件，工作轴、刀具、机架与设备类型不符。','独立重建车床主轴/尾座、铣钻垂直刀轴、压力机门架、实体砂轮、带锯连续刀带及打印/加工门架。')

def logistics(key):
    ident='l3-industry-logistics-'+key;a=[];b=[];length=3.0;width=.95;y=.77
    if key=='elevator':
        a=[basebox([1.05,.14,.80],[0,0,0],D)]
        a += [basebox([.13,3.02,.44],[s*.35,.14,0],P) for s in (-1,1)]
        b += [axis_cylinder([-.30,.39,0],[.30,.39,0],.22,D),axis_cylinder([-.30,2.87,0],[.30,2.87,0],.22,D)]
        for z in (-.21,.21):b.append(basebox([.48,2.48,.018],[0,.39,z],D))
        for j in range(9):
            yy=.48+j*.26;b += [basebox([.39,.08,.20],[0,yy,.27],O),basebox([.39,.12,.025],[0,yy,.36],O)]
        b += [basebox([.66,.09,.51],[0,.26,.38],P),block([.65,.08,.79],[0,3.07,.32],P,rot=[-15,0,0])]
    elif key in ('gantry','hoist','stacker','palletizer'):
        a=[basebox([.39,.10,1.65],[s*.88,0,0],D) for s in (-1,1)]+[basebox([.13,2.44,.13],[s*.88,.10,0],O) for s in (-1,1)]+[basebox([1.94,.18,.19],[0,2.48,0],O)]
        if key in ('gantry','hoist'):
            b=[basebox([.38,.29,.32],[0,2.16,0],P),tube([[0,2.19,0],[0,1.32,0]],.013,D,8),tube([[0,1.33,0],[0,1.14,0],[.07,1.09,0],[.13,1.17,0]],.026,M,10)]
        else:
            for s in (-1,1):b.append(axis_cylinder([s*.70,.21,.05],[s*.70,2.31,.05],.026,M))
            b += [basebox([1.41,.10,.27],[0,.71,.02],P)]
            for x in (-.38,.38):b.append(basebox([.08,.055,.90],[x,.73,.41],M))
    elif key=='turntable':
        a=[basebox([1.25,.14,1.25],[0,0,0],D),axis_cylinder([0,.14,0],[0,.64,0],.25,P)]
        b=[revolve([(.001,.64),(.64,.64),(.64,.71),(.001,.71)],P,32)]
        for j in range(9):
            z=(j-4)*.115;span=math.sqrt(max(0,.56*.56-z*z));b.append(axis_cylinder([-span,.75,z],[span,.75,z],.038,M))
    else:
        incline=key in ('ramp','chute');length=3.5 if key=='packing' else 2.8
        def elev(z):return y+.60*(z/length+.5) if incline else y
        for z in (-length*.39,length*.39):
            for x in (-.41,.41):a.append(basebox([.075,elev(z)-.06,.075],[x,0,z],D))
        for x in (-.47,.47):a.append(beam([x,elev(-length/2),-length/2],[x,elev(length/2),length/2],.085,P))
        for j in range(16):
            z=(j/15-.5)*length
            if key in ('roller','sorter','packing'):b.append(axis_cylinder([-.425,elev(z),z],[.425,elev(z),z],.044,M))
            else:b.append(block([.88,.048,length/16+.01],[0,elev(z),z],D if key!='chute' else M,rot=[-math.degrees(math.atan(.60/length)) if incline else 0,0,0]))
            if key in ('belt','ramp') and j%2==0:b.append(block([.83,.055,.035],[0,elev(z)+.045,z],P))
        if key=='trough':
            for s in (-1,1):b.append(block([.25,.04,length],[s*.40,y+.07,0],M,rot=[0,0,s*33]))
        if key=='sorter':
            for j in range(9):x=.4+j*.105;b.append(axis_cylinder([x,y,-.37],[x,y,.37],.037,M))
            for z in (-.4,.4):a.append(beam([.42,y-.04,z],[1.29,y-.04,z],.06,P))
        if key=='packing':
            a += [basebox([.065,1.43,.065],[s*.50,0,.30],P) for s in (-1,1)]+[block([1.08,.075,.10],[0,1.47,.30],P)]
            b += [basebox([.53,.40,.47],[0,y+.06,.28],'#A7916C'),block([.55,.025,.09],[0,y+.47,.28],O)]
    finish(ident,a,b,'升降、分流、转台与吊运设备被同一水平输送桌替代；支架与运输面脱接。','斗式提升机采用垂直循环带及料斗；转台是回转圆台；坡道有真实坡度；吊机有吊索/钩，滚筒在连续机架内。')

def process(key):
    ident='l3-industry-process-'+key;a=[basebox([1.8,.12,1.1],[0,0,0],D)];b=[]
    def vessel(x,z,r=.33,h=1.2,y=.28,c=P):
        for s in (-1,1):a.append(basebox([.065,.20,.065],[x+s*r*.65,.12,z],M))
        b.append(revolve([(.001,y),(.22,y), (r,y+.13),(r,y+h-.12),(.22,y+h),(.001,y+h)],c,20,at=[x,0,z]))
    if key in ('hopper','cyclone','separator'):
        b=[revolve([(.10,.39),(.10,.62),(.43,1.05),(.43,1.65),(.37,1.65),(.37,1.11),(.055,.66),(.055,.39)],M,20)]
        a += [basebox([.065,.98,.065],[x,.12,z],D) for x in (-.32,.32) for z in (-.25,.25)]
        if key!='hopper':b += [axis_cylinder([0,1.56,0],[0,1.89,0],.12,M),tube([[-.63,1.47,.29],[-.31,1.47,.29]],.105,P,12)]
    elif key=='pump':
        b=[axis_cylinder([-.65,.43,0],[.04,.43,0],.21,P),revolve([(.001,.13),(.24,.13),(.24,.59),(.001,.59)],P,18,at=[.30,0,0]),axis_cylinder([.28,.43,.08],[.28,.43,.50],.09,M),axis_cylinder([.28,.54,0],[.28,.92,0],.075,M)]
        a += [basebox([.85,.10,.43],[-.25,.16,0],M)]
    elif key in ('compressor','dryer','boiler'):
        b=[axis_cylinder([-.62,.52,0],[.62,.52,0],.34,P,24),ellipsoid([-.62,.52,0],[.16,.67,.67],P,16,8),ellipsoid([.62,.52,0],[.16,.67,.67],P,16,8)]
        for x in (-.42,.42):a.append(basebox([.13,.20,.48],[x,.12,0],D))
        if key=='compressor':b += [basebox([.47,.27,.31],[-.24,.87,0],M),axis_cylinder([.08,1.0,0],[.42,1.0,0],.15,D),tube([[0,1.11,0],[0,1.27,0],[.38,1.27,0],[.38,.86,0]],.025,M,8)]
        elif key=='boiler':b += [axis_cylinder([-.39,.81,0],[-.39,1.61,0],.09,D),axis_cylinder([.49,.52,0],[.86,.52,0],.17,D)]
        else:b += [tube([[.45,.70,0],[.45,1.06,0],[.75,1.12,0]],.12,M,14)]
    elif key in ('filter','water'):
        for x in (-.42,.42):vessel(x,0,.27,1.12)
        b += [tube([[-.77,.49,0],[-.42,.49,0],[-.42,1.64,0],[.42,1.64,0],[.42,.49,0],[.78,.49,0]],.048,M,12)]
        if key=='water':b.append(basebox([.17,.38,.16],[.72,.18,.19],P))
    elif key in ('mixer','reactor','distiller'):
        vessel(0,0,.42,1.12);b += [axis_cylinder([0,1.52,0],[0,1.76,0],.12,D),tube([[.31,.56,0],[.72,.56,0],[.72,.31,0]],.063,M,12)]
        if key=='distiller':b += [tube([[-.15,1.49,0],[-.15,1.81,0],[.65,1.81,0],[.65,.67,0]],.055,M,12),axis_cylinder([.65,.79,0],[.65,1.45,0],.13,M)]
    elif key in ('heater','chiller'):
        a += [basebox([.07,1.0,.68],[x,.12,0],D) for x in (-.59,.59)]
        for j in range(13):b.append(basebox([.047,.84,.64],[(j-6)*.085,.20,0],M))
        b += [axis_cylinder([-.73,.35,.14],[-.55,.35,.14],.074,P),axis_cylinder([.55,.90,-.14],[.75,.90,-.14],.074,P)]
    elif key=='burner':
        a += [basebox([1.25,1.05,.77],[0,.12,0],P)];b += [basebox([.58,.53,.035],[0,.37,.406],D),tube([[0,1.17,-.1],[0,1.77,-.1]],.12,D,14),axis_cylinder([-.72,.38,0],[-.45,.38,0],.19,M)]
    # Short, connected service line and recognisable valve; no free-standing mock fittings.
    b += [tube([[-.77,.13,.37],[-.77,.31,.37],[-.55,.31,.37]],.035,M,10),axis_cylinder([-.68,.31,.37],[-.68,.48,.37],.017,M)]
    b += ring(.07,.07,.48,.017,O);b[-1]=placed([b[-1]],[-.68,0,.37])[0]
    finish(ident,a,b,'处理设备缺少外壳或筒体、管路悬空，锅炉/干燥机等被不相关的部件替代。','以机座、连续筒体/封头、工作口和支承腿重新组织；泵、过滤、料斗、滚筒与换热机形成不同轮廓。')

def power(key):
    ident='l3-industry-power-'+key;a=[basebox([1.25,.12,.85],[0,0,0],D)];b=[]
    if key=='solar':
        a=[basebox([2.80,.10,1.80],[0,0,0],D)]
        for z in (-.66,.66):
            h=.72+(z+.66)*.36
            for x in (-1.12,1.12):a.append(basebox([.065,h,.065],[x,.10,z],M))
        for x in (-.68,.68):
            fs=[block([1.27,.055,1.72],[0,0,0],M),block([1.20,.012,1.65],[0,.034,0],'#385B6C')]
            for i in range(6):fs.append(block([.007,.014,1.63],[(i/5-.5)*1.18,.041,0],M,bevel=0))
            for j in range(9):fs.append(block([1.19,.014,.007],[0,.041,(j/8-.5)*1.61],M,bevel=0))
            b += placed(fs,[x,1.06,0],[-20,0,0])
    elif key=='wind':
        a += [tube([[0,.12,0],[0,3.3,0]],[.105,.04],WHITE,14)];b += [profile_z([[-.32,3.29,.10,.11],[.25,3.29,.10,.11]],P,12)]
        b += propeller([0,3.29,.27],1.22,3,'z')
    elif key=='generator':
        b=[basebox([.51,.51,.58],[-.28,.17,0],P),axis_cylinder([0,.40,0],[.48,.40,0],.235,M),basebox([.58,.16,.63],[-.28,.69,0],D),tube([[-.4,.78,-.13],[-.4,1.13,-.13]],.041,D,10)]
        for j in range(6):b.append(block([.025,.32,.60],[-.53+j*.092,.46,0],M))
    elif key in ('transformer','substation'):
        b=[basebox([.78,.75,.60],[0,.14,0],P)]
        for s in (-1,1):
            for j in range(7):b.append(basebox([.20,.52,.027],[s*.45,.25,(j-3)*.075],M))
        for x in (-.25,0,.25):
            b.append(axis_cylinder([x,.88,0],[x,1.18,0],.04,'#B9AC94'))
            for j in range(4):b.append(revolve([(.028,1.0+j*.04),(.075,1.0+j*.04),(.028,1.025+j*.04)],'#B9AC94',12,at=[x,0,0]))
    else:
        a += cabinet(.85,1.63,.58,P);b += [basebox([.79,1.45,.035],[0,.20,.307],P),block([.37,.19,.018],[0,1.28,.336],K),block([.025,.24,.029],[.30,.79,.34],M)]
        if key=='battery':
            for j in range(5):b.append(block([.69,.005,.012],[0,.41+j*.19,.34],D))
        else:
            for j in range(6):b.append(block([.38,.012,.016],[0,.37+j*.041,.34],D))
        for x,c in ((-.12,'#92AA87'),(0,O),(.12,'#AD7C68')):b.append(ellipsoid([x,1.06,.343],[.04,.04,.017],c,8,4))
        if key=='charger':b += [tube([[.42,1.32,.06],[.71,1.07,.05],[.73,.40,.05],[.59,.25,.05],[.49,.46,.05],[.48,1.04,.05]],.018,D,10),block([.065,.15,.07],[.47,1.09,.07],D,rot=[0,0,-18])]
    finish(ident,a,b,'电力设备沿用木柜或展示内部零件，缺少机壳、功能外形和承重结构。','发电机、变压器、充电桩、太阳能支架和风机分别重建；电柜采用封闭金属门及操作面。')

def author():
    for k in 'lathe mill drill press grinder bandsaw saw cnc laser printer bender punch roll welder polisher'.split():machine(k)
    for k in 'roller belt trough chute sorter elevator turntable stacker palletizer ramp gantry hoist packing'.split():logistics(k)
    for k in 'pump compressor filter mixer separator heater burner hopper dryer reactor water distiller cyclone boiler chiller'.split():process(k)
    for k in 'generator transformer switchgear battery charger solar wind substation ups control'.split():power(k)
