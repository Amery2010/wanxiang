"""Purpose-specific furniture. Supports meet their load; fixtures have real cavities."""
from .common import *
from .landscape import solid_shape
from shapely.geometry import Point, box as rect, Polygon
from shapely.affinity import scale as affine_scale

WOOD='#A18460';DARK='#596369';METAL='#99AAA9';WHITE='#D5D9D2';CLOTH='#82988E';BLACK='#344249'

def fourlegs(w,d,h,thick=.07,color=WOOD):
    return [basebox([thick,h,thick],[x,0,z],color,bevel=.009) for x in (-w/2+thick/2,w/2-thick/2) for z in (-d/2+thick/2,d/2-thick/2)]

def cabinet(w,h,d,color=WHITE):
    t=.045
    return [basebox([w,.06,d],[0,.04,0],color),basebox([t,h-.04,d],[-w/2+t/2,.08,0],color),basebox([t,h-.04,d],[w/2-t/2,.08,0],color),basebox([w,h-.04,t],[0,.08,-d/2+t/2],color),basebox([w,.055,d],[0,h-.015,0],color)]

def ellipse(w,d,n=32):return [(w/2*math.cos(i*math.tau/n),d/2*math.sin(i*math.tau/n)) for i in range(n)]

def ring(rx,rz,y,width,color=METAL):
    outer=affine_scale(Point(0,0).buffer(1,quad_segs=12),rx,rz)
    inner=affine_scale(Point(0,0).buffer(1,quad_segs=12),rx-width,rz-width)
    return solid_shape(outer.difference(inner),y,y+.022,color)

def bowl(w,d,y,depth,color=WHITE):
    # The inner profile returns to a raised closed base, not through the floor.
    f=revolve([(.001,y-depth),(.24,y-depth),(.36,y-depth*.86),(.47,y-.05),(.5,y),(.45,y+.012),(.41,y-.06),(.28,y-depth*.62),(.001,y-depth*.65)],color,24)
    return placed([f],scale=[w,1,d])

def faucet(x,y,z):
    return [tube([[x,y,z],[x,y+.27,z],[x,y+.31,z+.08],[x,y+.29,z+.19],[x,y+.23,z+.19]],.017,METAL,10),beam([x-.06,y+.12,z],[x+.06,y+.12,z],.025,METAL)]

def finish(ident,a,b,problem,change,mat='mat.wood',bmat=None,aname='structure',bname='functional_details'):
    if not a or not b:raise ValueError('Furniture needs meaningful structural and functional groups '+ident)
    replace(ident,[node(ident,aname,a,material=mat),node(ident,bname,b,material=bmat or mat)],problem,change)

def table(key):
    ident='l3-interior-table-'+key;w=1.65;d=.85;h=.38 if key=='coffee' else .74;t=.065
    if key in ('side','hex'):w=d=.8
    if key=='conference':w=2.45;d=1.05
    if key=='seminar':w=1.5;d=.82
    if key=='corner':outline=[[-w/2,-d/2],[w/2,-d/2],[w/2,-.08],[.08,-.08],[.08,d/2],[-w/2,d/2]]
    elif key=='picnic':w=1.95;d=1.1;outline=[[-w/2,-d/2],[w/2,-d/2],[0,d/2]]
    elif key=='hex':outline=ellipse(w,d,6)
    elif key=='seminar':outline=[[-w/2,-d/2],[w/2,-d/2]]+[[w/2*math.cos(a),-d/2+d*math.sin(a)] for a in [math.pi*i/20 for i in range(1,21)]]
    elif key in ('round','side','dining','conference'):outline=ellipse(w,d)
    elif key=='coffee':outline=[[w/2*math.cos(a)*(1-.19*math.sin(a)),d/2*math.sin(a)] for a in [i*math.tau/36 for i in range(36)]]
    else:outline=[[-w/2,-d/2],[w/2,-d/2],[w/2,d/2],[-w/2,d/2]]
    top=solid_shape(Polygon(outline).buffer(0),h-t,h,WOOD);supports=[];details=[]
    if key in ('side','hex'):
        supports=[revolve([(.001,0),(.31,0),(.30,.045),(.09,.08),(.065,h-t),(.001,h-t)],DARK,16)]
    elif key=='picnic':
        supports=[beam([-w*.36,0,-d*.24],[w*.15,h-t,.12],.105,WOOD),beam([w*.36,0,-d*.24],[-w*.15,h-t,.12],.105,WOOD),beam([0,0,d*.39],[0,h-t,0],.105,WOOD),beam([-w*.48,.32,-d*.51],[w*.48,.32,-d*.51],.11,WOOD)]
        details=[basebox([w*.98,.08,.25],[0,.32,-d*.67],WOOD),basebox([1.05,.08,.24],[.45,.32,.50],WOOD),basebox([1.05,.08,.24],[-.45,.32,.50],WOOD)]
    else:
        # Supports land strictly inside the actual perimeter even on curved tops.
        positions=[[-w*.30,-d*.29],[w*.30,-d*.29],[-w*.30,d*.29],[w*.30,d*.29]]
        if key=='corner':positions=[[-w*.40,-d*.32],[w*.40,-d*.32],[-w*.40,d*.32],[0,0]]
        if key=='seminar':positions=[[-w*.37,-d*.28],[w*.37,-d*.28],[-w*.17,d*.25],[w*.17,d*.25]]
        for x,z in positions:supports.append(basebox([.07,h-t+.008,.07],[x,0,z],DARK if key in ('coffee','conference','seminar') else WOOD))
        if key in ('workbench','altar','console'):
            details += [basebox([w*.64,.09,.08],[0,.23,-d*.28],WOOD),basebox([w*.48,.16,d*.63],[0,h-.24,0],'#8D7456'),block([.30,.025,.035],[0,h-.15,d*.34],DARK)]
        if key=='drop_leaf':
            for x in (-w*.30,w*.30):details.append(basebox([.004,.002,d*.9],[x,h,0],DARK,bevel=0))
    finish(ident,supports,top+details,'桌腿、横撑和不规则桌面缩放后出现承重断接或轮廓破碎。','桌面为闭合连续轮廓，支撑按桌面实际边界内缩并接至底面；用途配件分别建模。')

def seat(key):
    if key=='sofa':return
    ident='l3-interior-seat-'+key;w=1.6 if key in ('bench','pew') else .60;d=1.4 if key in ('chaise','lounge') else .58;h=.72 if key=='stool' else .44
    padded=key in ('armchair','office','auditorium','bucket','tractor','chaise','lounge','kneeling');col=CLOTH if padded else WOOD
    supports=[];body=[];backh=.51
    if key=='office':
        supports=[tube([[0,.11,0],[0,h,0]],.035,METAL,12)]
        for i in range(5):
            a=i*math.tau/5;x=.34*math.cos(a);z=.34*math.sin(a);supports += [beam([0,.16,0],[x,.07,z],.045,DARK),ellipsoid([x,.045,z],[.072,.08,.072],DARK,10,5)]
    elif key in ('stool','tractor'):
        supports=[revolve([(.001,0),(.28,0),(.28,.04),(.055,.09),(.04,h),(.001,h)],DARK,16)]
        if key=='stool':supports+=ring(.19,.19,.30,.014,METAL)
    elif key=='rocker':
        for x in (-w*.39,w*.39):
            pts=[[x,.065+.095*((z/.48)**2),z] for z in [-.49,-.32,0,.32,.49]]
            supports.append(tube(pts,.035,WOOD,8))
            for z in (-.20,.20):supports.append(beam([x,.08,z],[x,h,z],.055,WOOD))
    elif key=='kneeling':
        for s in (-1,1):supports += [beam([s*.22,.055,-.44],[s*.22,.055,.39],.055,DARK),beam([s*.22,.055,-.37],[s*.22,h,-.15],.055,DARK),beam([s*.22,.055,.31],[s*.22,.28,.23],.055,DARK)]
        body=[block([.51,.09,.36],[0,h,-.19],col,rot=[-12,0,0]),block([.49,.09,.30],[0,.28,.25],col,rot=[12,0,0])]
    elif key in ('folding','auditorium'):
        for s in (-1,1):supports += [beam([s*w*.37,.025,-.29],[s*w*.37,h+.03,.20],.04,DARK),beam([s*w*.37,.025,.29],[s*w*.37,h+.03,-.20],.04,DARK)]
    else:supports=fourlegs(w-.12,d-.13,h+.01,.075,DARK if padded else WOOD)
    if key!='kneeling':
        body=[block([w,.095,d],[0,h,0],col,.032 if padded else .014)]
        if key=='stool':pass
        elif key in ('garden','dining','pew','bench','rocker'):
            for s in (-1,1):body.append(basebox([.045,backh,.045],[s*(w/2-.03),h,-d/2+.025],WOOD))
            if key in ('dining','pew'):
                body.append(block([w,.05,.055],[0,h+backh,-d/2+.025],WOOD))
                for i in range(7):body.append(basebox([.022,backh-.09,.027],[(i/6-.5)*w*.80,h+.07,-d/2+.025],WOOD))
            else:
                for j in range(3):body.append(basebox([w,.08,.045],[0,h+.13+j*.135,-d/2+.025],WOOD))
        else:
            body.append(block([w*.91,.50 if key!='tractor' else .32,.075],[0,h+.27,-d/2+.04],col,.04))
            if key in ('bucket','tractor'):
                for s in (-1,1):body.append(block([.095,.28,d*.90],[s*w*.45,h+.15,0],col,.035))
        if key in ('armchair','office','lounge','chaise'):
            for s in (-1,1):
                body += [basebox([.04,.23,.04],[s*(w/2-.02),h,d*.24],DARK if key=='office' else WOOD),block([.075,.06,d*.9],[s*(w/2-.02),h+.25,0],col)]
    finish(ident,supports,body,'座面、靠背与腿组的固定盒缩放导致离体或不符合座椅用途。','按使用姿态确定座高、倾角、扶手和接地支撑；办公椅五爪脚、摇椅弧轨、跪坐椅分离膝垫。',mat='mat.metal' if padded else 'mat.wood',bmat='mat.fabric' if padded else 'mat.wood')

def bed(key):
    ident='l3-interior-bed-'+key;w=1.5 if key=='canopy' else .80 if key=='crib' else .95;d=1.4 if key=='crib' else 2.05;h=.38
    frame=fourlegs(w-.06,d-.06,h,.075)+[basebox([w,.10,d],[0,h,0],WOOD)];soft=[block([w-.09,.16,d-.09],[0,h+.17,0],WHITE,.045),block([w*.70,.12,.32],[0,h+.31,-d*.34],CLOTH,.05)]
    if key=='canopy':
        for x in (-w/2,w/2):
            for z in (-d/2,d/2):frame.append(basebox([.065,2.05,.065],[x,0,z],WOOD))
        for x in (-w/2,w/2):frame.append(block([.065,.075,d],[x,2.05,0],WOOD))
        for z in (-d/2,d/2):frame.append(block([w,.075,.065],[0,2.05,z],WOOD))
        soft.append(block([w+.06,.028,d+.06],[0,2.09,0],CLOTH))
    elif key=='crib':
        for s in (-1,1):
            frame.append(block([.06,.065,d],[s*w/2,1.05,0],WOOD))
            for j in range(11):frame.append(basebox([.024,.59,.024],[s*w/2,h+.10,(j/10-.5)*d*.91],WOOD))
        for z in (-d/2,d/2):
            frame += [block([w,.065,.06],[0,1.05,z],WOOD)]+[basebox([.025,.59,.025],[(j/6-.5)*w*.90,h+.10,z],WOOD) for j in range(7)]
    else:
        frame=[]
        for x in (-w*.43,w*.43):
            for z in (-d*.39,d*.39):frame += [ellipsoid([x,.065,z],[.10,.12,.10],DARK,10,5),basebox([.055,.37,.055],[x,.08,z],METAL)]
        frame += [basebox([w,.075,d],[0,h,0],METAL)]
        for z in (-d/2,d/2):frame += [basebox([w,.45,.055],[0,h,z],WHITE),block([w*.72,.05,.06],[0,h+.43,z],METAL)]
        for x in (-w/2,w/2):
            frame.append(tube([[x,h+.1,-.7],[x,h+.40,-.7],[x,h+.40,.45],[x,h+.10,.45]],.022,METAL,10))
    finish(ident,frame,soft,'四柱床缺少顶框，婴儿床缺少侧围，护理床与普通床结构相同。','补全顶框、连续围栏或护理床侧护栏及脚轮，床垫保持独立且连接正确。',bmat='mat.fabric')

def kitchen(key):
    ident='l3-interior-kitchen-'+key;w=1.35;d=.70;h=.90;case=cabinet(w,h-.045,d,WOOD);detail=[]
    # Actual countertop cutouts: no bowl/solid-top intersection.
    area=rect(-w/2,-d/2,w/2,d/2)
    if key in ('sink','dishwash'):
        case=case[:-1]  # The closed cabinet top must not block the real sink cutout.
        area=area.difference(affine_scale(Point(0,0).buffer(1,quad_segs=12),.39,.23));detail+=bowl(.82,.50,h,.24,METAL)+faucet(0,h,-.29)
    detail+=solid_shape(area,h-.045,h,'#C3C3B3')
    if key in ('stove','hob','hood'):
        for x in (-.30,.30):
            for z in (-.17,.17):
                detail+=ring(.095,.095,h+.01,.014,DARK)
                detail[-1]=placed([detail[-1]],[x,0,z])[0]
                if key!='hob':
                    detail += [block([.23,.018,.016],[x,h+.045,z],DARK),block([.016,.018,.23],[x,h+.045,z],DARK)]
        detail.append(basebox([.86,.33,.025],[0,.23,d/2+.005],DARK));detail.append(block([.65,.025,.04],[0,.61,d/2+.04],METAL))
        for i in range(4):detail.append(ellipsoid([-.37+i*.245,.74,d/2+.03],[.052,.052,.03],METAL,10,5))
    else:
        for x in (-.32,.32):
            detail.append(basebox([.62,.71,.028],[x,.12,d/2+.008],WOOD));detail.append(block([.15,.018,.025],[x,.73,d/2+.035],DARK))
    if key=='hood':
        for x in (-w*.43,w*.43):case.append(basebox([.045,.92,.045],[x,.87,-d*.37],METAL))
        detail += [profile_z([[-.28,1.78,.53,.07],[.30,1.78,.53,.07]],METAL,8),basebox([.28,.55,.27],[0,1.82,-.06],METAL)]
    if key=='bar':detail.append(basebox([w,.085,.35],[0,1.12,-.30],WOOD));case+=[basebox([.045,.24,.045],[x,.88,-.28],DARK) for x in (-.50,.50)]
    if key=='bakery':detail.append(block([.63,.035,.47],[0,h+.018,0],WOOD));detail.append(tube([[-.34,h+.067,.04],[.34,h+.067,.04]],.035,WOOD,12))
    if key=='prep':detail.append(block([.44,.035,.38],[.24,h+.018,0],WOOD))
    finish(ident,case,detail,'台面、灶具、水槽与基柜使用错误组件，罩体与工作区关系不成立。','实际开孔水槽、灶面四火眼、独立烤箱门与连接到排烟罩的立柱；柜门和把手与外壳对齐。')

def appliance(key):
    ident='l3-interior-appliance-'+key;w=.66;d=.62;h=1.78 if key=='fridge' else 1.80 if key=='vending' else 1.64 if key=='aircon' else 1.10 if key=='water' else .43 if key=='microwave' else .52 if key=='coffee' else .85
    case=cabinet(w,h,d,WHITE);face=[];front=d/2+.01
    if key in ('washer','dryer'):
        case.append(basebox([w,h-.06,.035],[0,.07,front],WHITE))
        opening=ring(.235,.235,0,.035,METAL)
        face+=placed(opening,[0,.40,front+.017],[90,0,0])
        face.append(ellipsoid([0,.40,front+.026],[.39,.39,.035],BLACK,20,8))
        face += [block([.33,.08,.015],[-.11,.74,front+.025],DARK),ellipsoid([.21,.74,front+.04],[.063,.063,.037],METAL,12,5)]
    elif key=='fridge':
        for y,hh in ((.10,1.05),(1.17,.57)):
            face.append(basebox([w-.035,hh,.045],[0,y,front],WHITE));face.append(basebox([.025,.30,.035],[-.21,y+hh-.36,front+.045],DARK))
    elif key in ('oven','microwave','dishwasher'):
        face.append(basebox([w-.025,h-.12,.035],[0,.10,front],WHITE))
        if key!='dishwasher':face.append(basebox([w*.66,h*.57,.015],[-.055,h*.22,front+.026],BLACK))
        face.append(block([w*.66,.025,.035],[0,h-.12,front+.055],METAL))
        for y in (h-.08,h-.18):face.append(ellipsoid([w*.39,y,front+.045],[.043,.043,.025],DARK,10,5))
    elif key=='vending':
        case.append(basebox([w-.035,h-.10,.025],[0,.09,front],DARK))
        face += [basebox([.43,1.08,.02],[-.065,.52,front+.019],'#95ACA8'),basebox([.38,.14,.026],[-.06,.19,front+.025],BLACK)]
        for j in range(4):
            for i in range(3):face.append(basebox([.075,.17,.026],[-.22+i*.135,.59+j*.24,front+.037],['#B89B60','#A26950','#69877D'][i]))
        for i in range(5):face.append(ellipsoid([.26,1.39-i*.12,front+.04],[.04,.04,.022],METAL,8,4))
    elif key=='coffee':
        # Open cup recess, dispenser stems over a removable drip tray.
        face=[basebox([w,.13,.10],[0,h-.14,.19],DARK),block([w-.08,.035,d*.68],[0,.095,.10],METAL)]
        for x in (-.12,.12):face.append(tube([[x,h-.15,.20],[x,h-.24,.20]],.012,METAL,8));face.append(revolve([(.001,.11),(.055,.11),(.060,.22),(.047,.22),(.042,.13),(.001,.13)],WHITE,12,at=[x,0,.19]))
        face.append(block([.24,.055,.025],[0,h-.07,.25],BLACK))
    elif key=='aircon':
        face.append(basebox([w-.03,h-.10,.035],[0,.09,front],WHITE))
        for j in range(15):face.append(block([w*.79,.017,.014],[0,.22+j*.065,front+.026],DARK))
        face.append(block([.21,.14,.013],[.05,1.36,front+.027],BLACK))
    elif key=='water':
        case=[basebox([w,.73,d],[0,.06,0],WHITE),basebox([w,.14,d],[0,.91,0],WHITE)]+[basebox([.09,.26,d],[s*(w/2-.045),.71,0],WHITE) for s in (-1,1)]
        face=[block([.40,.025,.30],[0,.75,.12],DARK),revolve([(.001,1.04),(.18,1.04),(.21,1.17),(.21,1.42),(.14,1.47),(.001,1.47)],'#79A5B3',16)]
        for x,c in ((-.11,'#976858'),(.11,'#608DA4')):face.append(tube([[x,.96,.20],[x,.88,.20]],.016,c,8))
    finish(ident,case,face,'电器共用木柜及不匹配的器件，关键门体、开口和操作区缺失。','按家电用途重做金属机壳、分区门体、操作面板、出水/取物开口；没有复用木质柜面。',mat='mat.paint',bmat='mat.matte')

def sanitary(key):
    ident='l3-interior-sanitary-'+key;structure=[];detail=[]
    if key in ('vanity','pedestal','washstation','utility','drain'):
        w=1.5 if key in ('washstation','drain') else .82;d=.61;y=.88 if key!='utility' else .42
        if key=='pedestal':structure=[revolve([(.001,0),(.19,0),(.15,.12),(.10,.55),(.16,.65),(.001,.65)],WHITE,16)]
        else:
            structure=fourlegs(w+.08,d+.08,y-.025,.06,METAL)+[block([w+.02,.055,d+.02],[0,.12,0],WHITE)]
            counter=rect(-w/2-.05,-d/2-.05,w/2+.05,d/2+.05)
            for x in ((-.37,.37) if key=='washstation' else (0,)):
                hole=affine_scale(Point(x,0).buffer(1,quad_segs=12),.64*.43 if key=='washstation' else w*.43,.51*.43 if key=='washstation' else d*.43,origin=(x,0))
                counter=counter.difference(hole)
            structure+=solid_shape(counter,y-.03,y-.007,METAL)
        if key=='washstation':
            for x in (-.37,.37):detail+=placed(bowl(.64,.51,y,.20),[x,0,0])+faucet(x,y,-.22)
        else:detail+=bowl(w,d,y,.24 if key!='utility' else .27)+faucet(0,y,-.23)
        if key=='drain':
            for j in range(7):detail.append(block([w*.65,.012,.015],[0,y-.13,(j-3)*.05],METAL))
    elif key=='bath':
        structure=[ellipsoid([x,.10,z],[.15,.20,.14],METAL,10,5) for x in (-.35,.35) for z in (-.10,.10)];detail=bowl(1.70,.78,.65,.48)+faucet(.55,.65,-.25)
    elif key=='toilet':
        structure=[revolve([(.001,0),(.18,0),(.17,.09),(.105,.22),(.17,.29),(.001,.29)],WHITE,18),basebox([.47,.50,.19],[0,.38,-.31],WHITE),block([.51,.055,.23],[0,.895,-.31],WHITE)]
        detail=bowl(.56,.71,.46,.25)+ring(.28,.355,.47,.052,WHITE)+[ellipsoid([.15,.75,-.20],[.04,.028,.018],METAL,10,4)]
    elif key in ('shower','outdoor'):
        structure=[basebox([.90,.08,.90],[0,0,0],WHITE),tube([[.32,.07,-.34],[.32,1.93,-.34],[.32,2.02,-.13]],.021,METAL,10)]
        detail=[ellipsoid([.32,1.99,-.11],[.23,.035,.22],METAL,18,5),block([.20,.075,.075],[.32,1.05,-.32],METAL),block([.10,.012,.10],[0,.085,0],DARK)]
        if key=='shower':
            for x in (-.43,.43):structure.append(basebox([.025,1.96,.025],[x,.08,-.43],METAL))
            structure += [basebox([.90,.04,.04],[0,2.02,-.43],METAL),basebox([.90,1.93,.02],[0,.08,-.43],'#9FB9B7'),basebox([.02,1.93,.90],[-.43,.08,0],'#9FB9B7')]
            detail += [basebox([.04,1.93,.04],[.43,.08,.43],METAL),tube([[.42,1.07,.42],[.42,1.34,.42]],.017,METAL,8)]
    elif key=='towel':
        structure=[block([.80,.07,.42],[0,.04,0],METAL)]+[tube([[x,.06,0],[x,1.15,0]],.022,METAL,10) for x in (-.33,.33)]
        for yy in (.72,1.12):structure.append(tube([[-.33,yy,0],[.33,yy,0]],.022,METAL,10))
        detail=[basebox([.39,.48,.012],[0,.64,.027],CLOTH),basebox([.39,.42,.012],[0,.70,-.027],CLOTH),block([.39,.018,.066],[0,1.128,0],CLOTH)]
    finish(ident,structure,detail,'卫生洁具被套成高台、实心管件或家具，关键盆腔、便器和淋浴关系不成立。','实际闭合盆腔与口沿、落地支撑、龙头出水方向及适当的排水/操作位置；便器分离底座、坐圈和水箱。',mat='mat.ceramic',bmat='mat.matte')

def service(key):
    if key=='podium':return
    ident='l3-interior-service-'+key;a=[];b=[]
    if key=='coatstand':
        a=[revolve([(.001,0),(.33,0),(.33,.045),(.10,.10),(.04,1.73),(.001,1.73)],WOOD,16)]
        for j in range(6):
            q=j*math.tau/6;b.append(tube([[0,1.46,0],[.24*math.cos(q),1.66,.24*math.sin(q)],[.27*math.cos(q),1.75,.27*math.sin(q)]],.019,WOOD,8))
    elif key in ('easel','musicstand','lectern'):
        if key=='easel':
            a=[beam([-.34,0,.17],[-.19,1.55,-.10],.045,WOOD),beam([.34,0,.17],[.19,1.55,-.10],.045,WOOD),beam([0,0,-.51],[0,1.43,-.08],.045,WOOD),block([.65,.035,.07],[0,.63,.08],WOOD)];b=[block([.52,.68,.03],[0,1.00,-.03],WHITE,rot=[-8,0,0]),block([.65,.055,.10],[0,.66,.09],WOOD)]
        else:
            a=[revolve([(.001,0),(.27,0),(.27,.05),(.045,.10),(.035,1.02),(.001,1.02)],METAL if key=='musicstand' else WOOD,14)]
            b=[block([.66,.05,.47],[0,1.06,0],DARK if key=='musicstand' else WOOD,rot=[-20,0,0]),block([.61,.055,.025],[0,.99,.225],DARK if key=='musicstand' else WOOD)]
    elif key=='mirror':
        a=fourlegs(.69,.44,.12,.06)+[basebox([.065,1.58,.065],[x,.08,0],WOOD) for x in (-.33,.33)]+[block([.72,.065,.08],[0,1.68,0],WOOD),block([.72,.065,.08],[0,.20,0],WOOD)]
        b=[basebox([.58,1.41,.035],[0,.235,0],'#AFC8C6')]
    elif key=='screen':
        for i in range(3):
            fs=fourlegs(.56,.22,.12,.045)+[basebox([.045,1.57,.035],[x,.05,0],WOOD) for x in (-.26,.26)]+[block([.56,.045,.035],[0,1.64,0],WOOD)]
            a+=placed(fs,[(i-1)*.51,0,abs(i-1)*.10],[0,(-1 if i==0 else 1 if i==2 else 0)*22,0]);b+=placed([basebox([.46,1.39,.024],[0,.18,0],CLOTH)],[(i-1)*.51,0,abs(i-1)*.10],[0,(-1 if i==0 else 1 if i==2 else 0)*22,0])
    elif key=='trolley':
        for x in (-.36,.36):
            for z in (-.24,.24):a += [ellipsoid([x,.05,z],[.085,.10,.085],DARK,10,5),tube([[x,.11,z],[x,.97,z]],.018,METAL,8)]
        b=[block([.80,.045,.57],[0,y,0],METAL) for y in (.24,.61,.91)]
        a.append(tube([[-.36,.93,-.24],[-.36,1.08,-.24],[.36,1.08,-.24],[.36,.93,-.24]],.02,METAL,8))
    elif key=='reception':
        a=[basebox([1.4,.99,.075],[0,.04,.25],WOOD),basebox([.075,.99,.65],[-.67,.04,-.02],WOOD),basebox([.075,.99,.65],[.67,.04,-.02],WOOD)]
        b=[block([1.5,.07,.74],[0,1.06,-.02],WOOD),block([1.20,.04,.55],[0,.73,-.15],WOOD)]
    elif key=='altar':
        a=fourlegs(1.20,.53,.89,.11)+[block([1.12,.10,.10],[0,.20,0],WOOD)];b=[block([1.45,.09,.75],[0,.93,0],WOOD),block([1.05,.018,.68],[0,.986,0],CLOTH)]
    finish(ident,a,b,'服务家具共用桌架与悬浮板，衣帽架、谱架、画架等使用形象不成立。','按功能重建三脚/立柱/折屏等结构，独立面板及实际托边、挂钩和层板，保持接地和承重连续。')

def author():
    for key in 'dining workbench coffee side conference console corner drop_leaf hex seminar altar picnic'.split():table(key)
    for key in 'dining office armchair rocker stool lounge kneeling folding auditorium garden tractor bucket bench chaise pew'.split():seat(key)
    for key in 'canopy crib hospital'.split():bed(key)
    for key in 'island sink stove hob hood prep pantry bar bakery dishwash'.split():kitchen(key)
    for key in 'fridge washer dryer oven vending coffee microwave dishwasher aircon water'.split():appliance(key)
    for key in 'vanity pedestal bath shower toilet towel drain outdoor washstation utility'.split():sanitary(key)
    for key in 'reception lectern altar coatstand mirror screen trolley easel musicstand'.split():service(key)
