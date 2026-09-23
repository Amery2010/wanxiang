"""Purpose-specific vehicles and containers. All coordinates are metres, +Z forward."""
from .common import *
from l1_expansion.common import placed
METAL='#6D7D81'; RUBBER='#3C4444'; WOOD='#A1835D'; PAINT='#7F9B9D'; GLASS='#8EBDC7'

def wheel(center,r=.33,width=.20,spokes=False):
    fs=[];profile=[(r*.55,-width*.47),(r*.88,-width*.55),(r,-width*.34),(r,width*.34),(r*.88,width*.55),(r*.55,width*.47)]
    fs.append(revolve(profile,RUBBER,20));fs.append(revolve([(0,-width*.4),(r*.63,-width*.4),(r*.63,width*.4),(0,width*.4)],'#9AABA9',16))
    if spokes:
        for j in range(12):a=j*math.tau/12;fs.append(beam([0,-width*.44,0],[r*.64*math.sin(a),-width*.44,r*.64*math.cos(a)],.018,METAL))
    fs.append(revolve([(0,-width*.58),(r*.17,-width*.58),(r*.17,width*.58),(0,width*.58)],METAL,12))
    return placed(fs,center,[0,0,90])

def chest(key='chest'):
    ident='l3-props-container-'+key;w=.9;d=.62;h=.58;t=.055;fs=[];lid=[];hardware=[];mat='mat.wood'
    col=WOOD if key in ('chest','shipping','wine','display','trunk','hamper','tote','barrel') else '#7E9290'
    if key=='pallet':
        fs=[basebox([.13,.13,.70],[x,0,0],WOOD) for x in (-.36,0,.36)]
        fs += [basebox([.96,.055,.115],[0,.13,(j-2)*.14],WOOD) for j in range(5)]
    elif key in ('barrel','oil','water','waste','recycle','grain','cylinder'):
        if key=='grain':
            fs=[revolve([(.01,0),(.25,0),(.35,.18),(.31,.6),(.17,.78),(.09,.84),(.03,.85)],'#BCA781',16)]
            hardware=[tube([[-.12,.78,0],[0,.80,.08],[.12,.79,0]],.018,WOOD,7)]
        elif key=='cylinder':
            fs=[revolve([(.001,0),(.23,0),(.25,.15),(.25,.80),(.17,.96),(.065,1.0),(.065,1.08),(.001,1.08)],PAINT,16)]
            hardware=[basebox([.18,.08,.09],[0,1.08,0],METAL),tube([[0,1.08,0],[.13,1.08,0]],.025,METAL,8)]
        else:
            r=.32;hh=.72;profile=[(.01,.06),(r-.035,.06),(r-.02,hh),(r,hh),(r+.025,hh*.6),(r,.02),(.01,.02)]
            fs=[revolve(profile,col,20)];lid=[revolve([(.01,hh),(.335,hh),(.335,hh+.035),(.01,hh+.035)],col,20)]
            for yy in (.13,.57):hardware.append(revolve([(r-.012,yy),(r+.035,yy),(r+.035,yy+.035),(r-.012,yy+.035)],METAL,20))
            if key=='water':hardware += [tube([[0,.16,.28],[0,.16,.42],[0,.10,.44]],.034,METAL,8),block([.12,.022,.035],[0,.21,.38],METAL)]
            if key=='recycle':hardware.append(arch(.20,.16,.03,.025,'#D1D7B6',[0,.40,.331],10))
    else:
        fs=[basebox([w,t,d],[0,0,0],col),basebox([t,h,d],[-w/2+t/2,0,0],col),basebox([t,h,d],[w/2-t/2,0,0],col),basebox([w-2*t,h,t],[0,0,-d/2+t/2],col),basebox([w-2*t,h,t],[0,0,d/2-t/2],col)]
        if key=='chest':
            # Barrel vault runs along X. Lower inner roof preserves cavity when opened.
            pts=[]
            for i in range(17):z=-d/2+d*i/16;y=.22*math.sin(math.pi*i/16);pts.append([z,y])
            outline=pts+[[z,y-.035] for z,y in reversed(pts)]
            lid=placed([extrude_xy(outline,w+.04,col)],[0,0,d/2],[0,90,0])
            for side in (-1,1):lid += placed([extrude_xy(pts,.04,col)],[side*(w/2-.005),0,d/2],[0,90,0])
            # Lid-local origin is on the back hinge; source remains editable.
            for xx in (-.30,.30):
                for j in range(16):
                    z0=d*j/16;z1=d*(j+1)/16;y0=.22*math.sin(math.pi*j/16)+.009;y1=.22*math.sin(math.pi*(j+1)/16)+.009
                    lid.append(beam([xx,y0,z0],[xx,y1,z1],.025,'#A59565',depth=.06))
            for xx in (-w/2+.045,w/2-.045):hardware.append(basebox([.055,h,.035],[xx,0,d/2+.018],METAL))
            # Hasp bridges the seam, lock body stays on fixed front wall.
            lid += [basebox([.055,.13,.025],[0,-.10,d+.008],METAL)]
            hardware += [basebox([.12,.115,.055],[0,h-.16,d/2+.035],'#B4A373'),ellipsoid([0,h-.115,d/2+.066],[.019,.027,.007],'#3F4D4A',8,4)]
            for xx in (-.28,.28):hardware.append(tube([[xx-.05,h,-d/2],[xx+.05,h,-d/2]],.03,METAL,10))
        elif key not in ('shipping','tote','hamper','wine','display'):lid=[basebox([w+.02,.045,d+.02],[0,0,d/2],col)]
        if key in ('shipping','wine','display'):
            for z in (-d/2-.012,d/2+.012):
                for yy in (.06,.49):hardware.append(block([w,.045,.025],[0,yy,z],WOOD))
            for x in (-w/2-.012,w/2+.012):hardware.append(basebox([.025,h,.065],[x,0,0],WOOD))
        if key=='wine':
            for j in range(6):
                x=(j%3-1)*.24;z=(j//3-.5)*.25;fs.append(revolve([(.001,.06),(.075,.06),(.076,.32),(.032,.39),(.026,.51),(.001,.51)],'#678475',12,at=[x,0,z]))
        if key in ('hamper','tote'):
            hardware.append(tube([[-.27,h,0],[-.27,h+.18,0],[0,h+.30,0],[.27,h+.18,0],[.27,h,0]],.022,WOOD,8))
        if key in ('suitcase','trunk','toolbox','medical','ammo'):
            hardware.append(tube([[-.16,h+.075,0],[-.16,h+.18,0],[.16,h+.18,0],[.16,h+.075,0]],.022,METAL,8))
            for x in (-.29,.29):hardware.append(basebox([.055,.09,.03],[x,h-.08,d/2+.02],METAL))
        if key=='suitcase':
            for x in (-.35,.35):fs+=wheel([x,.07,-d*.38],.085,.06)
        if key=='mail':
            hardware.append(basebox([.48,.026,.015],[0,.41,d/2+.015],'#3D555D'))
    items=[node(ident,'body',fs,material=mat)];controls=[]
    if lid:
        items.append(node(ident,'lid',lid,at=[0,h,-d/2] if key not in ('barrel','oil','water','waste','recycle') else [0,0,0],material=mat))
        if key not in ('barrel','oil','water','waste','recycle'):controls=[rotation_control('lid_open','lid','打开箱盖',[-1,0,0],105)]
    if hardware:items.append(node(ident,'hardware',hardware,material='mat.metal'))
    replace(ident,items,'容器主体套用不适合的盖片、管段或内部嵌件，箱身与开口结构不完整。','箱体有底、壁与内腔；宝箱拱盖独立铰接，搭扣和锁具安装在正确侧；桶罐保留口沿。',controls=controls);add_motion(ident,controls)

def wing(span,chord,y,z,color=PAINT,swept=False):
    tip=chord*.45 if swept else chord*.80
    outline=[[-span/2,z-tip*.5-(.55 if swept else 0)],[-span/2,z+tip*.5-(.55 if swept else 0)],[0,z+chord*.5],[span/2,z+tip*.5-(.55 if swept else 0)],[span/2,z-tip*.5-(.55 if swept else 0)],[0,z-chord*.5]]
    return slab_polygon(outline,y,.07,color)

def propeller(at,r=.65,n=2,axis='z'):
    fs=[]
    for i in range(n):
        a=i*math.tau/n;tip=[math.sin(a)*r,math.cos(a)*r,0]
        fs.append(leaf([math.sin(a)*.06,math.cos(a)*.06,0],tip,.13,'#817054',curve=0,thickness=.03))
    fs.append(ellipsoid([0,0,0],[.19,.19,.25],METAL,12,5))
    return placed(fs,at,[90,0,0] if axis=='y' else [0,90,0] if axis=='x' else [0,0,0])

def air(key):
    ident='l3-vehicle-air-'+key;body=[];wings=[];gear=[];extras=[];glass=[]
    if key=='airship':
        body=[profile_z([[-3.6,2.5,.045,.05],[-2.8,2.5,.75,.85],[-1.6,2.5,1.05,1.20],[1.5,2.5,1.08,1.2],[2.7,2.5,.76,.87],[3.2,2.5,.07,.07]],'#BFC3B3',20),basebox([.9,.46,1.7],[0,.78,0],PAINT)]
        glass=[basebox([.85,.22,.03],[0,1.0,.86],GLASS)]
        for z in (-.60,.60):extras.append(beam([0,1.22,z],[0,1.45,z],.07,METAL))
        wings=[wing(2.15,.85,2.50,-2.85,PAINT),extrude_xy([[-.04,2.45],[-.04,3.75],[.04,3.75],[.04,2.45]],1.0,PAINT,-2.7)]
        for s in (-1,1):extras+=propeller([s*.74,1.04,.3],.26,3)
    elif key=='quadrotor':
        body=[ellipsoid([0,.40,0],[.55,.24,.70],PAINT,12,5)]
        for x in (-.58,.58):
            for z in (-.58,.58):
                extras.append(beam([0,.42,0],[x,.42,z],.085,METAL));extras.append(tube([[x,.40,z],[x,.55,z]],.045,METAL,10));wings+=propeller([x,.57,z],.35,2,'y')
                gear.append(basebox([.04,.30,.04],[x*.70,0,z*.70],METAL))
    elif key in ('helicopter','gyrocopter'):
        cy=1.08
        body=[ellipsoid([0,cy,.35],[1.05,.82,1.9],PAINT,16,7),tube([[0,cy,-.4],[0,cy+.25,-2.5]],[.24,.06],PAINT,12)]
        glass=[ellipsoid([0,cy+.15,.84],[.90,.63,.99],GLASS,14,6)]
        extras=[tube([[0,cy+.2,0],[0,2.05,0]],.045,METAL,10)]
        wings+=propeller([0,2.1,0],2.4,4 if key=='helicopter' else 2,'y');wings+=propeller([.1,cy+.42,-2.45],.45,3,'x')
        wings.append(extrude_xy([[-.06,cy],[-.06,cy+.9],[.06,cy+.9],[.06,cy]],.58,PAINT,-2.4))
        if key=='helicopter':
            for s in (-1,1):
                gear.append(tube([[s*.7,.17,-1.0],[s*.7,.13,.9],[s*.7,.30,1.2]],.045,METAL,8))
                for z in (-.45,.6):gear.append(beam([s*.25,.9,z],[s*.7,.15,z],.055,METAL))
        else:
            for s in (-1,1):gear+=wheel([s*.55,.23,-.05],.23,.13);gear.append(beam([0,.8,0],[s*.55,.23,-.05],.07,METAL))
            gear+=wheel([0,.16,1.13],.16,.09)
    else:
        length=6.5 if key=='cargo' else 5.5 if key in ('glider','jet','shuttle') else 4.5;cy=1.38;rear=-length/2;front=length/2
        if key=='biplane':
            body=[profile_z([[rear,cy+.05,.04,.07],[-1.3,cy,.22,.25],[-.62,cy,.35,.39]],PAINT,14),profile_z([[.32,cy,.39,.41],[1.5,cy,.38,.38],[front,cy,.25,.25]],PAINT,14)]
            # Open cockpit shell: an arc open above the pilot, not a seat buried in a solid fuselage.
            pts=[];rows=(-.64,.34);arc=[math.radians(160+i*220/16) for i in range(17)]
            for z in rows:
                pts += [[.39*math.cos(a),cy+.41*math.sin(a),z] for a in arc]+[[.31*math.cos(a),cy+.33*math.sin(a),z] for a in reversed(arc)]
            n=34;faces=[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]+[list(range(n-1,-1,-1)),list(range(n,2*n))];body.append(mesh(pts,faces,PAINT))
            extras += [basebox([.34,.10,.38],[0,cy-.18,-.23],WOOD),basebox([.34,.33,.06],[0,cy-.10,-.43],WOOD)]
            glass=[extrude_xy([[-.27,cy+.12],[.27,cy+.12],[.22,cy+.43],[-.22,cy+.43]],.028,GLASS,.28)]
            wings=[wing(6.7,.95,1.05,.30,'#C3B089'),wing(6.95,.98,2.22,.31,'#C3B089')]
            for x in (-2.45,2.45):
                for z in (-.01,.58):extras.append(beam([x,1.12,z],[x,2.23,z],.055,WOOD))
                extras.append(beam([x,1.12,-.01],[x,2.23,.58],.035,METAL))
            for x in (-.27,.27):
                for z in (.12,.6):extras.append(beam([x,1.65,z],[x*.9,2.24,z],.043,METAL))
        else:
            rad=.60 if key=='cargo' else .43 if key=='shuttle' else .32
            body=[profile_z([[rear,cy,.035,.04],[rear+.6,cy,rad*.5,rad*.7],[0,cy,rad,rad],[front-.6,cy,rad*.95,rad],[front,cy,.035,.04]],'#D0CDC0' if key=='shuttle' else PAINT,16)]
            glass=[ellipsoid([0,cy+.24,front*.36],[rad*1.65,.46,.99],GLASS,14,6)]
            span=9.0 if key=='glider' else 7.2 if key=='cargo' else 5.5
            if key in ('jet','shuttle'):
                outline=[[-.32,1.5],[-2.35,-1.15],[-2.25,-1.65],[0,-1.10],[2.25,-1.65],[2.35,-1.15],[.32,1.5]];wings=[slab_polygon(outline,cy-.06,.08,PAINT)]
            else:wings=[wing(span,.62 if key=='glider' else 1.05,cy+.10,.12,PAINT)]
            if key=='cargo':
                for x in (-1.7,1.7):extras.append(profile_z([[-.5,cy,.20,.20],[.8,cy,.18,.18]],METAL,12));extras[-1]=placed([extras[-1]],[x,0,0])[0];extras+=propeller([x,cy,.86],.52,3)
            if key=='tiltrotor':
                for x in (-2.6,2.6):extras.append(ellipsoid([x,cy+.13,.05],[.40,.6,.45],PAINT,12,5));wings+=propeller([x,cy+.48,.05],1.10,3,'y')
        # Horizontal stabiliser and proper vertical tail attached to the tapered tail cone.
        wings.append(wing(2.0,.62,cy+.08,rear+.42,PAINT))
        tailoutline=[[rear,cy],[rear+.15,cy+.82],[rear+.63,cy+.83],[rear+.96,cy]]
        wings+=placed([extrude_xy(tailoutline,.055,PAINT)],[0,0,0],[0,-90,0])
        if key not in ('jet','shuttle','glider','cargo','tiltrotor'):extras+=propeller([0,cy,front+.06],.66,2)
        if key=='seaplane':
            for x in (-.7,.7):
                gear.append(profile_z([[-1.5,.20,.05,.04],[-1.2,.23,.22,.21],[.9,.23,.23,.2],[1.6,.27,.045,.05]],'#7B9295',12));gear[-1]=placed([gear[-1]],[x,0,0])[0]
                for z in (-.75,.75):gear.append(beam([x*.3,cy-.22,z],[x,.41,z],.055,METAL))
        else:
            for side in (-1,1):gear+=wheel([side*.69,.28,.53],.28,.16);gear.append(beam([side*.19,cy-.30,.2],[side*.69,.28,.53],.075,METAL))
            gear+=wheel([0,.12,rear+.38],.12,.075);gear.append(beam([0,cy-.02,rear+.33],[0,.12,rear+.38],.04,METAL))
        if key=='jet':
            for x in (-.36,.36):extras.append(tube([[x,cy-.08,-.45],[x,cy-.08,-1.85]],.18,METAL,12))
    items=[]
    for nm,fs,mat in [('fuselage',body,'mat.paint'),('wings',wings,'mat.paint'),('landing_gear',gear,'mat.rubber'),('structure',extras,'mat.metal'),('cockpit_glass',glass,'mat.vehicleGlass')]:
        if fs:items.append(node(ident,nm,fs,material=mat))
    replace(ident,items,'不同航空器共用筒状机体、杆状落地件和近似翼片；双翼机没有完整座舱与轮式起落架。','按机型重建机身、座舱、机翼、尾翼和起落装置；旋翼、浮筒与翼间撑杆按用途配置。')

def hull(w,d,color,openboat=True,double_ended=False):
    stations=[(-d/2,.001 if double_ended else w*.34),(-d*.36,w*.34 if double_ended else w*.46),(-d*.13,w*.5),(d*.18,w*.47),(d*.38,w*.30),(d*.5,.001 if double_ended else .025)];pts=[]
    for z,rx in stations:
        yy=.70 if z<d*.3 else .70+(z/d-.3)*.25
        section=[(-rx,yy),(-rx*.84,.26),(0,.03),(rx*.84,.26),(rx,yy),(rx*.86,yy-.015),(rx*.68,.31),(0,.17),(-rx*.68,.31),(-rx*.86,yy-.015)]
        pts += [[x,y,z] for x,y in section]
    n=10;fs=[]
    for j in range(len(stations)-1):
        for i in range(n):a=j*n+i;b=j*n+(i+1)%n;fs.append([a,b,b+n,a+n])
    fs += [list(range(n-1,-1,-1)),list(range((len(stations)-1)*n,len(stations)*n))]
    return mesh(pts,fs,color),stations

def boat(key):
    ident='l3-vehicle-marine-'+key;w=1.75;d=4.6;small=key in ('rowboat','canoe','kayak','dinghy');w=1.08 if key in ('canoe','kayak') else w
    hf,st=hull(w,d,WOOD if key in ('rowboat','canoe') else PAINT,double_ended=key in ('canoe','kayak'));body=[hf];deck=[];extra=[];glass=[]
    outline=[[-rx*.86,z] for z,rx in st]+[[rx*.86,z] for z,rx in reversed(st)]
    if not small:deck=[slab_polygon(outline,.59,.07,'#B9AE8B')]
    else:
        for z in (-1.,.2):deck.append(basebox([w*.73,.08,.28],[0,.44,z],WOOD))
        if key=='kayak':
            from .landscape import solid_shape
            from shapely.geometry import Polygon,Point
            shape=Polygon(outline).difference(Point(0,0).buffer(.33,quad_segs=12));deck+=solid_shape(shape,.56,.64,PAINT)
        if key in ('rowboat','canoe','kayak'):
            for x in (-.75,.75) if key=='rowboat' else (.48,):
                extra += [tube([[x,.65,-.75],[x,.65,1.15]],.023,WOOD,8),leaf([x,.65,1.05],[x,.65,1.55],.17,WOOD,curve=0,thickness=.026)]
    if key=='dinghy':
        for side in (-1,1):body.append(tube([[side*.63,.55,-1.9],[side*.83,.55,-.9],[side*.77,.57,1.0],[side*.35,.6,2.0],[0,.60,2.17]],.19,'#778C84',12))
        extra += [basebox([.26,.38,.28],[0,.42,-2.17],METAL),tube([[0,.45,-2.2],[0,.05,-2.25]],.045,METAL,8)]
    if key=='sailboat':
        extra.append(tube([[0,.65,.22],[0,3.80,.22]],[.05,.023],WOOD,10));extra.append(beam([0,1.0,.22],[0,1.0,-1.62],.045,WOOD))
        sails=[mesh([[.018,3.67,.20],[.018,1.06,.20],[.018,1.06,-1.60],[.035,3.67,.20],[.035,1.06,.20],[.035,1.06,-1.60]],[[0,1,2],[3,5,4],[0,3,4,1],[1,4,5,2],[2,5,3,0]],'#D8D1AE'),mesh([[.02,3.20,.29],[.02,.91,1.97],[.02,.91,.45],[.038,3.20,.29],[.038,.91,1.97],[.038,.91,.45]],[[0,1,2],[3,5,4],[0,3,4,1],[1,4,5,2],[2,5,3,0]],'#B78C76')];extra+=sails
        for z in (-2.,2.):extra.append(tube([[0,3.6,.22],[0,.68,z]],.01,METAL,5))
    elif key not in ('rowboat','canoe','kayak','dinghy','barge'):
        cw=w*.72;cd=1.5 if key!='ferry' else 2.35;cz=-.3
        extra += [basebox([cw,.52,cd],[0,.66,cz],PAINT),basebox([cw+.10,.07,cd+.10],[0,1.74,cz],PAINT)]
        for x in (-cw/2,cw/2):
            for z in (cz-cd/2,cz+cd/2):extra.append(basebox([.065,.56,.065],[x,1.18,z],METAL))
        glass.append(basebox([cw-.07,.52,.025],[0,1.2,cz+cd/2],GLASS))
        for x in (-cw/2,cw/2):glass.append(basebox([.025,.52,cd-.07],[x,1.2,cz],GLASS))
        if key in ('fishing','tug','research','patrol'):extra.append(tube([[0,1.8,cz],[0,2.55,cz]],.03,METAL,8))
        if key=='fishing':extra += [beam([0,2.0,-.35],[0,2.0,-1.8],.055,METAL),tube([[0,2.0,-1.8],[0,.75,-1.8]],.011,METAL,5)]
        if key=='research':extra += [beam([.52,.72,-1.5],[.52,2.1,-1.5],.09,METAL),beam([.52,2.1,-1.5],[.52,2.2,-2.55],.09,METAL),tube([[.52,2.2,-2.5],[.52,.60,-2.5]],.018,METAL,6)]
    if key=='barge':
        for x in (-w*.43,w*.43):extra.append(basebox([.07,.45,d*.68],[x,.65,-.2],PAINT))
        for j in range(3):extra.append(basebox([.8,.60,.75],[0,.66,-1.15+j*.80],WOOD))
    if not small:
        for side in (-1,1):
            for z,rx in st[1:-1]:extra.append(basebox([.024,.34,.024],[side*rx*.84,.68,z],METAL))
            extra.append(tube([[side*rx*.84,1.02,z] for z,rx in st[1:-1]],.018,METAL,6))
    items=[]
    for nm,fs,mat in [('hull',body,'mat.paint'),('deck',deck,'mat.wood'),('fittings',extra,'mat.matte'),('glazing',glass,'mat.vehicleGlass')]:
        if fs:items.append(node(ident,nm,fs,material=mat))
    replace(ident,items,'船艇使用楔形板条代替完整船壳，甲板穿出船首，桨与帆装配缺乏支撑。','双层连续船壳保留内腔；甲板跟随船舷，桨座、座板、船舱与帆索均有真实连接。')

def road(key):
    ident='l3-vehicle-road-'+key;items=[];frame=[];body=[];glass=[];extra=[]
    if key in ('motorcycle','bicycle'):
        for i,z in enumerate((-.80,.80)):items.append(node(ident,'wheel'+str(i),wheel([0,.34,z],.34,.11 if key=='motorcycle' else .047,True),material='mat.rubber'))
        pts=[([0,.34,-.8],[0,.85,-.15]),([0,.85,-.15],[0,.36,.14]),([0,.36,.14],[0,.34,-.8]),([0,.85,-.15],[0,.9,.55]),([0,.9,.55],[0,.36,.14]),([0,.9,.55],[0,.34,.8])]
        frame=[beam(a,b,.043,PAINT) for a,b in pts];extra=[basebox([.20,.07,.29],[0,.86,-.15],RUBBER),tube([[-.28,1.0,.55],[0,.97,.55],[.28,1.0,.55]],.026,METAL,8)]
        if key=='motorcycle':body=[ellipsoid([0,.80,.13],[.35,.32,.65],PAINT,12,5),basebox([.3,.32,.46],[0,.33,0],METAL)]
        else:
            for side in (-1,1):extra.append(beam([0,.37,.12],[side*.18,.37,.12],.024,METAL));extra.append(block([.16,.03,.07],[side*.19,.37,.12],RUBBER))
    else:
        small=key in ('sedan','hatch','estate','coupe','convertible','pickup');L=4.2 if small else 6.3;w=1.74 if small else 1.96;r=.34 if small else .40;n=3 if key in ('city_bus','coach','refuse','fire_engine','tanker','tractor_unit') else 2
        zs=[-L*.33,L*.32] if n==2 else [-L*.36,-L*.18,L*.33]
        for j,z in enumerate(zs):
            frame.append(beam([-w*.48,r,z],[w*.48,r,z],.09,METAL))
            for s in (-1,1):items.append(node(ident,f'wheel{j}_{s}',wheel([s*w*.50,r,z],r,.23),material='mat.rubber'))
        frame.append(basebox([w*.79,.19,L-.15],[0,.45,0],'#495B5F'))
        body.append(basebox([w,.35,L-.12],[0,.66,0],PAINT))
        for s in (-1,1):extra.append(basebox([.30,.14,.045],[s*w*.33,.86,L/2-.03],'#DBCDA2'));extra.append(basebox([.22,.12,.045],[s*w*.34,.78,-L/2-.01],'#A16C59'))
        if small:
            cz=-.05 if key!='pickup' else .56;cl=1.75 if key not in ('coupe','pickup','estate') else 1.35 if key in ('coupe','pickup') else 2.35;roofy=1.68
            body.append(basebox([w-.10,.16,.91],[0,1.01,L*.33],PAINT));glass += [basebox([w-.21,.56,.035],[0,1.08,cz+cl/2],GLASS)]
            for s in (-1,1):
                for z in (cz-cl/2,cz+cl/2):frame.append(beam([s*(w/2-.1),1.00,z],[s*(w/2-.17),roofy,z],.065,PAINT))
                if key!='convertible':glass.append(basebox([.03,.51,cl-.10],[s*(w/2-.145),1.10,cz],GLASS))
            if key!='convertible':body.append(basebox([w-.24,.09,cl+.07],[0,roofy,cz],PAINT));glass.append(basebox([w-.25,.51,.03],[0,1.10,cz-cl/2],GLASS))
            else:
                for x in (-.36,.36):extra+=[basebox([.48,.18,.53],[x,1.0,-.25],RUBBER),basebox([.48,.43,.1],[x,1.10,-.49],RUBBER)]
            if key=='pickup':
                for x in (-w/2+.07,w/2-.07):body.append(basebox([.08,.44,1.42],[x,1.01,-1.26],PAINT))
                body.append(basebox([w,.44,.09],[0,1.01,-L/2+.05],PAINT));body.append(basebox([w-.12,.06,1.4],[0,1.01,-1.23],WOOD))
        else:
            cz=L*.5-.88;body += [basebox([w,.43,1.65],[0,1.0,cz],PAINT),basebox([w+.03,.10,1.72],[0,2.13,cz],PAINT)]
            for x in (-w*.44,w*.44):
                for z in (cz-.79,cz+.79):frame.append(basebox([.08,.75,.08],[x,1.40,z],PAINT))
                glass.append(basebox([.025,.65,1.47],[x,1.45,cz],GLASS))
            glass.append(basebox([w*.83,.65,.028],[0,1.45,cz+.805],GLASS));back=-.85;bl=L-1.95
            if key=='tanker':body.append(profile_z([[-L/2,1.62,.03,.03],[-L/2+.35,1.62,w*.46,.56],[1.12,1.62,w*.46,.56],[1.36,1.62,.03,.03]],'#ACB6AC',20))
            elif key in ('flatbed','tractor_unit'):body.append(basebox([w,.15,bl],[0,1.0,back],WOOD));extra += [revolve([(.01,1.12),(.45,1.12),(.45,1.19),(.01,1.19)],METAL,16,at=[0,0,-1.2])] if key=='tractor_unit' else []
            else:
                bh=1.28;body += [basebox([w,.12,bl],[0,1.02,back],PAINT),basebox([w,.09,bl],[0,2.3,back],PAINT)]
                for x in (-w/2+.04,w/2-.04):body.append(basebox([.08,bh,bl],[x,1.07,back],PAINT))
                for z in (back-bl/2,back+bl/2):body.append(basebox([w,.98,.07],[0,1.15,z],PAINT))
                if key in ('city_bus','coach','minibus'):
                    # Side glazing on the upper body, with repeated mullions.
                    for x in (-w/2-.016,w/2+.016):
                        for j in range(5):glass.append(basebox([.03,.62,.62],[x,1.55,-2.68+j*.73],GLASS))
                if key=='fire_engine':
                    for x in (-.40,.40):extra.append(beam([x,2.48,-2.7],[x,2.48,1.9],.06,METAL))
                    for j in range(13):extra.append(beam([-.4,2.48,-2.65+j*.36],[.4,2.48,-2.65+j*.36],.05,METAL))
                if key in ('ambulance','fire_engine'):extra.append(basebox([1.1,.15,.26],[0,2.24,cz],'#9D6C60'))
                if key=='refrigerated':extra.append(basebox([.75,.5,.25],[0,1.77,1.45],'#BCC6BD'))
    for nm,fs,mat in [('frame',frame,'mat.metal'),('body',body,'mat.paint'),('glazing',glass,'mat.vehicleGlass'),('fittings',extra,'mat.matte')]:
        if fs:items.append(node(ident,nm,fs,material=mat))
    replace(ident,items,'轮组、座舱和载荷模块连接粗糙，部分车种仅由近似方盒和错误薄轮组成。','重建真实轮胎截面和轴桥；汽车座舱、载货平台、罐体、客舱与自行车三角车架独立建模。')

def author():
    for ident in list(ASSEMBLIES):
        if ident.startswith('l3-props-container-'):chest(ident.removeprefix('l3-props-container-'))
        elif ident.startswith('l3-vehicle-air-'):air(ident.removeprefix('l3-vehicle-air-'))
        elif ident.startswith('l3-vehicle-marine-'):boat(ident.removeprefix('l3-vehicle-marine-'))
        elif ident.startswith('l3-vehicle-road-'):road(ident.removeprefix('l3-vehicle-road-'))
