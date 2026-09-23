"""Industrial author parts. Geometry is illustrative, not engineering certified."""
from .common import *


def elbow(radius=.32, outer=.105, inner=.075, angle=90):
    """Bent hollow tube with welded, indexed outer/inner skins and annular ends."""
    seg=10;sides=10;vs=[];fs=[]
    for radius_ in (outer,inner):
        for j in range(seg+1):
            a=math.radians(angle*j/seg)
            for i in range(sides):
                b=math.tau*i/sides;r=radius+radius_*math.cos(b)
                vs.append([r*math.cos(a)-radius,r*math.sin(a),radius_*math.sin(b)])
    stride=(seg+1)*sides
    for layer in range(2):
        for j in range(seg):
            for i in range(sides):
                a=layer*stride+j*sides+i;b=layer*stride+j*sides+(i+1)%sides
                face=[a,b,b+sides,a+sides]
                fs.append(face if layer==0 else face[::-1])
    for j in (0,seg):
        for i in range(sides):
            a=j*sides+i;b=j*sides+(i+1)%sides
            face=[a,a+stride,b+stride,b];fs.append(face if j==0 else face[::-1])
    return poly(vs,fs,'l1Metal')


def gear(teeth=12,r=.30,h=.09,hole=.10):
    # Alternating root/tip profile and a true axial aperture.
    n=teeth*4;v=[];f=[]
    for y in [0,h]:
        for inner in [False,True]:
            for i in range(n):
                a=math.tau*i/n;rad=hole if inner else r*(1 if i%4 in (1,2) else .83)
                v.append([rad*math.cos(a),y,rad*math.sin(a)])
    for i in range(n):
        j=(i+1)%n
        f += [[i,j,2*n+j,2*n+i],[n+i,3*n+i,3*n+j,n+j],
              [i,n+i,n+j,j],[2*n+i,2*n+j,3*n+j,3*n+i]]
    return poly(v,f,'l1Metal')


def flange(r=.2,hole=.1):
    return [ring(r,r-hole,.045,'l1Metal')]+[disk(.024,.035,'metal',y=.025,position=[r*.76*math.cos(i*math.tau/6),0,r*.76*math.sin(i*math.tau/6)]) for i in range(6)]


def author():
    def put(g,k,n,fs,sz=(.9,1,.9),**kw):return register('industry',g,k,n,fs,sz,material='mat.metal',**kw)
    pipes=names('socket:承插管端 threaded:外牙管端 flanged:法兰管端 reducer:同心变径管 eccentric:偏心变径管 elbow90:直角弯管 elbow45:斜角弯管 return:回形弯管 tee:三通接口体 cross:四通接口体 bellows:波纹补偿管 hose_end:软管卡嘴 cap:盲端封帽 nozzle:渐缩喷嘴芯')
    for key,name in pipes:
        if key in ('socket','threaded','flanged'):
            fs=[round_tube(.12,.085,.5,'l1Metal')]
            if key=='socket':fs += [round_tube(.16,.123,.19,'l1Metal',position=[0,.35,0])]
            elif key=='threaded':fs += [ring(.138,.018,.025,'l1Metal',position=[0,y,0]) for y in [.28,.32,.36,.40,.44]]
            else:fs += placed(flange(),[0,.48,0])
        elif key in ('reducer','eccentric'):
            fs=[lathe([[.18,0],[.18,.08],[.10,.4],[.10,.5],[.07,.5],[.07,.42],[.15,.07],[.15,0]],'l1Metal',12,closed_profile=True)]
            if key=='eccentric':
                # Indexed hollow eccentric reducer: offset inner/outer skins share annular rims.
                rings=[(0,0,.18,.15),(0,.08,.18,.15),(.08,.4,.10,.07),(.08,.5,.10,.07)]
                vs=[];faces=[];n=12
                for cx,cy,ro,ri in rings:
                    for radius in (ro,ri):
                        vs.extend([[cx+radius*math.cos(i*math.tau/n),cy,radius*math.sin(i*math.tau/n)] for i in range(n)])
                for j in range(len(rings)-1):
                    for i in range(n):
                        k=(i+1)%n;a=j*2*n
                        faces.extend([[a+i,a+k,a+2*n+k,a+2*n+i],
                                      [a+n+i,a+3*n+i,a+3*n+k,a+n+k]])
                for i in range(n):
                    k=(i+1)%n;a=(len(rings)-1)*2*n
                    faces.extend([[i,n+i,n+k,k],[a+i,a+k,a+n+k,a+n+i]])
                fs=[poly(vs,faces,'l1Metal')]
        elif key in ('elbow90','elbow45','return'):fs=[elbow(angle={'elbow90':90,'elbow45':45,'return':180}[key])]
        elif key in ('tee','cross'):
            fs=[round_tube(.12,.085,.6,'l1Metal'),round_tube(.115,.08,.32,'l1Metal',rotation=[0,0,-90],position=[0,.3,0])]
            if key=='cross':fs += [round_tube(.115,.08,.32,'l1Metal',rotation=[0,0,90],position=[0,.3,0])]
        elif key=='bellows':
            prof=[[.14+(.035 if i%2 else 0),i*.035] for i in range(15)];fs=[lathe(prof+[[.105,.49],[.105,0]],'l1Metal',14,closed_profile=True)]
        elif key=='hose_end':
            outer=[[.11,0],[.11,.10]]
            for y in [.12,.23,.34]:outer.extend([[.12,y],[.145,y+.04],[.12,y+.075]])
            outer.extend([[.11,.42],[.065,.42],[.065,0]])
            fs=[lathe(outer,'l1Metal',12,closed_profile=True)]
        elif key=='cap':fs=[lathe([[.16,0],[.16,.12],[.13,.19],[.03,.21]],'l1Metal',12,cap=True)]
        else:fs=[lathe([[.17,0],[.13,.08],[.04,.43],[.025,.43],[.10,.07],[.14,0]],'l1Metal',12,closed_profile=True)]
        put('pipe',key,name,fs)
    valves=names('gate:闸阀阀体 globe:截止阀阀体 ball:球阀阀体 butterfly:蝶阀阀板 check:止回阀瓣 needle:针阀阀针 diaphragm:膜片压盖 relief:泄压阀帽 float:浮球阀杆 spool:滑阀阀芯')
    for key,name in valves:
        if key=='gate':fs=[formbox(.45,.6,.3,'l1Slate'),round_tube(.13,.10,.68,'l1Metal',rotation=[0,0,90],position=[.34,.2,0]),round_tube(.07,.04,.35,'l1Metal',position=[0,.6,0])]
        elif key=='globe':fs=[ico([.55,.5,.45],'l1Slate',[0,.26,0],detail=1),formbox(.17,.25,.17,'l1Metal',y=.45),round_tube(.12,.08,.7,'l1Metal',rotation=[0,0,90],position=[.35,.2,0])]
        elif key=='ball':fs=[ico([.46,.46,.46],'l1Metal',[0,.23,0],detail=1),round_tube(.10,.07,.55,'metal',rotation=[90,0,0],position=[0,.23,.28])]
        elif key=='butterfly':fs=[disk(.28,.04,'l1Metal'),rod([-.32,.02,0],[.32,.02,0],.033,'metal')]
        elif key=='check':fs=[disk(.24,.04,'l1Metal'),formbox(.10,.045,.20,'metal',y=.02,z=.26),round_tube(.035,.014,.18,'l1Metal',rotation=[0,0,90],position=[.09,.05,.33])]
        elif key=='needle':fs=[lathe([[.04,0],[.065,.2],[.065,.65],[.10,.67],[.10,.72]],'l1Metal',10,cap=True)]
        elif key=='diaphragm':fs=[lathe([[.28,0],[.28,.04],[.23,.12],[.12,.22],[.06,.23]],'l1Metal',12,cap=True)]+[disk(.022,.025,'metal',position=[.245*math.cos(i*math.tau/6),.04,.245*math.sin(i*math.tau/6)]) for i in range(6)]
        elif key=='relief':fs=[lathe([[.14,0],[.14,.08],[.10,.13],[.10,.48],[.15,.52],[.15,.6]],'l1Slate',10,cap=True),rod([0,.42,0],[.25,.42,0],.06,'l1Metal')]
        elif key=='float':fs=[ico([.32,.26,.32],'copper',[.3,.34,0],detail=1),rod([-.2,0,0],[.3,.34,0],.024,'l1Metal')]
        else:fs=[rod([0,0,0],[0,.8,0],.065,'l1Metal')]+[disk(.12,.11,'metal',y=y) for y in [.06,.32,.58]]
        put('valve',key,name,fs)
    drives=names('spur:直齿齿轮坯 bevel:锥齿齿轮坯 rack:齿条坯 worm:蜗杆坯 pulley_v:V槽皮带轮坯 pulley_timing:同步带轮坯 sprocket:链轮坯 coupling:弹性联轴节半体 keyshaft:键槽轴坯 bearing:轴承座体 crank:曲柄坯 flywheel:飞轮坯')
    for key,name in drives:
        if key=='spur':fs=[gear()]
        elif key=='bevel':
            g=gear(12,.3,.14)
            # Taper only the external tooth ring; preserve the shaft bore.
            n=12*4
            for i in range(2*n,3*n):g['points'][i][0]*=.68;g['points'][i][2]*=.68
            fs=[g,lathe([[.16,.13],[.115,.28],[.10,.28],[.10,.13]],'metal',12,closed_profile=True)]
        elif key=='rack':fs=[formbox(.8,.12,.13,'l1Metal')]+[plate([[-.045,0],[.045,0],[.025,.085],[-.025,.085]],.13,'metal',position=[x,.12,0]) for x in [-.32,-.21,-.1,.01,.12,.23,.34]]
        elif key=='worm':fs=[rod([0,0,0],[0,.65,0],.085,'l1Metal')]+[loft([[.115*math.cos(j*.3*69/63),.08+j*.007*69/63,.115*math.sin(j*.3*69/63),.02,.02] for j in range(64)],'metal',6)]
        elif key=='pulley_v':fs=[lathe([[.3,0],[.3,.045],[.23,.085],[.3,.13],[.3,.17],[.09,.17],[.09,0]],'l1Metal',16,closed_profile=True)]
        elif key=='pulley_timing':fs=[gear(18,.24,.18),ring(.27,.18,.025,'metal'),ring(.27,.18,.025,'metal',position=[0,.18,0])]
        elif key=='sprocket':fs=[gear(9,.32,.045)]+placed(flange(.13,.07),[0,.04,0])
        elif key=='coupling':fs=[round_tube(.16,.07,.14,'l1Metal')]+[formbox(.07,.12,.07,'metal',x=.11*math.cos(i*math.tau/3),y=.14,z=.11*math.sin(i*math.tau/3)) for i in range(3)]
        elif key=='keyshaft':fs=[rod([0,0,0],[0,.75,0],.075,'l1Metal'),formbox(.045,.45,.02,'metal',y=.12,z=.078)]
        elif key=='bearing':fs=[formbox(.6,.10,.22,'l1Metal'),ring(.20,.065,.2,'metal',rotation=[90,0,0],position=[0,.25,0]),formbox(.20,.008,.21,'l1Metal',y=.10)]
        elif key=='crank':fs=[plate([[-.1,0],[.1,0],[.18,.45],[.07,.55],[-.05,.48]],.1,'l1Metal'),disk(.13,.12,'metal',rotation=[90,0,0],position=[0,.1,.06]),disk(.08,.18,'metal',rotation=[90,0,0],position=[.08,.46,.12])]
        else:fs=[ring(.4,.065,.10,'l1Metal'),round_tube(.09,.04,.14,'metal')]+[rod([0,.05,0],[.34*math.cos(i*math.tau/5),.05,.34*math.sin(i*math.tau/5)],.035,'l1Metal') for i in range(5)]
        put('drive',key,name,fs)
    conveyors=names('roller:输送滚筒芯 trough_roller:槽形滚筒芯 belt_cleat:挡边带齿条 chain_link:输送链节 bucket:斗提料斗壳 chute:导料溜槽壳 guide:侧导轮支座 tensioner:张紧滑座')
    for key,name in conveyors:
        if key=='roller':fs=[rod([-.4,.15,0],[.4,.15,0],.13,'l1Metal'),rod([-.5,.15,0],[.5,.15,0],.045,'metal')]
        elif key=='trough_roller':fs=[rod([-.2,.18,0],[.2,.18,0],.08,'l1Metal'),rod([-.2,.18,0],[-.5,.38,0],.08,'l1Metal'),rod([.2,.18,0],[.5,.38,0],.08,'l1Metal')]
        elif key=='belt_cleat':fs=[formbox(.8,.045,.26,'l1Rubber'),formbox(.8,.16,.045,'l1Rubber',y=.045)]
        elif key=='chain_link':fs=[round_tube(.07,.025,.28,'metal',rotation=[90,0,0],position=[x,.09,.14]) for x in [-.17,.17]]+[formbox(.4,.13,.045,'l1Metal',y=.025,z=z) for z in [-.13,.13]]
        elif key=='bucket':fs=[]
        elif key=='chute':fs=[plate([[-.4,0],[.4,0],[.4,.2],[.35,.2],[.35,.045],[-.35,.045],[-.35,.2],[-.4,.2]],.8,'l1Metal',rotation=[12,0,0])]
        elif key=='guide':fs=[formbox(.24,.07,.28,'l1Slate'),formbox(.07,.3,.07,'l1Metal',y=.07),disk(.13,.12,'l1Rubber',y=.36)]
        else:fs=[formbox(.5,.10,.25,'l1Slate'),formbox(.16,.2,.2,'l1Metal',y=.1),rod([-.35,.2,0],[.35,.2,0],.025,'metal')]
        if key=='bucket':fs=[formbox(.5,.045,.32,'l1Metal'),formbox(.5,.3,.045,'l1Metal',z=-.14)]+[formbox(.045,.3,.32,'l1Metal',x=x) for x in [-.23,.23]]
        put('conveyor',key,name,fs)
    power=names('insulator:绝缘子串芯 busbar:母排折弯片 terminal:端子底座 transformer_fin:散热翅片芯 coil:线圈骨架 fuse:熔断管壳 breaker:断路器拨杆 cable_gland:电缆密封接头 fan_guard:风机护网 plate_stack:叠片磁芯')
    for key,name in power:
        if key=='insulator':fs=[rod([0,0,0],[0,.65,0],.065,'l1Ivory')]+[lathe([[.10,y],[.17,y+.035],[.075,y+.08]],'l1Ivory',12,cap=True) for y in [.08,.21,.34,.47]]
        elif key=='busbar':fs=[plate([[-.3,0],[.3,0],[.3,.12],[.10,.12],[.10,.45],[-.02,.45],[-.02,.12],[-.3,.12]],.04,'copper')]
        elif key=='terminal':fs=[formbox(.5,.1,.24,'l1Rubber')]+[round_tube(.046,.02,.1,'copper',position=[x,.10,0]) for x in [-.16,0,.16]]
        elif key=='transformer_fin':fs=[]
        elif key=='coil':fs=[round_tube(.20,.12,.4,'l1Rubber'),ring(.25,.13,.05,'l1Rubber'),ring(.25,.13,.05,'l1Rubber',position=[0,.4,0])]
        elif key=='fuse':fs=[rod([0,0,0],[0,.5,0],.06,'l1Ivory')]+[disk(.067,.08,'l1Metal',y=y) for y in [0,.42]]
        elif key=='breaker':fs=[plate([[-.07,0],[.07,0],[.13,.22],[.12,.35],[-.03,.35]],.12,'l1Rubber')]
        elif key=='cable_gland':fs=[round_tube(.095,.044,.32,'l1Rubber',6),ring(.12,.075,.045,'l1Metal',position=[0,.08,0]),ring(.1,.05,.05,'l1Metal',position=[0,.28,0])]
        elif key=='fan_guard':fs=[ring(r,.012,.02,'l1Metal') for r in [.12,.24,.36]]+[rod([-.36,0,0],[.36,0,0],.012,'l1Metal'),rod([0,0,-.36],[0,0,.36],.012,'l1Metal')]
        else:fs=[plate([[-.25,0],[.25,0],[.25,.5],[.12,.5],[.12,.12],[-.12,.12],[-.12,.5],[-.25,.5]],.015,'metal',position=[0,0,z]) for z in [-.075,-.05,-.025,0,.025,.05,.075]]
        if key=='transformer_fin':fs=[formbox(.7,.6,.035,'l1Slate')]+[formbox(.035,.6,.16,'l1Slate',x=x) for x in [-.3,-.2,-.1,0,.1,.2,.3]]
        put('power',key,name,fs)
    process=names('impeller:泵叶轮芯 agitator:搅拌桨芯 hopper:落料斗壳 separator:旋流分离锥芯 filter:滤筒骨架 heat_tube:换热回管芯 baffle:罐内挡流板 burner:燃烧喷口芯')
    for key,name in process:
        if key=='impeller':fs=[disk(.28,.04,'l1Metal')]+[box([.22,.08,.04],'metal',[.14*math.cos(i*math.tau/6),.08,.14*math.sin(i*math.tau/6)],.006,rotation=[0,-i*60-30,0]) for i in range(6)]
        elif key=='agitator':fs=[rod([0,0,0],[0,.6,0],.035,'l1Metal')]+[box([.28,.06,.13],'metal',[x,.1,0],.01,rotation=[20,0,0]) for x in [-.15,.15]]
        elif key in ('hopper','separator'):fs=[lathe([[.13,0],[.13,.12],[.38,.65],[.38,.8],[.34,.8],[.34,.66],[.09,.13],[.09,0]],'l1Metal',8 if key=='hopper' else 16,closed_profile=True)]
        elif key=='filter':fs=[ring(.22,.025,.045,'l1Metal',position=[0,y,0]) for y in [0,.3,.6]]+[rod([.2*math.cos(i*math.tau/10),0,.2*math.sin(i*math.tau/10)],[.2*math.cos(i*math.tau/10),.6,.2*math.sin(i*math.tau/10)],.012,'metal') for i in range(10)]
        elif key=='heat_tube':fs=[elbow(.20,.045,.028,180)]+[round_tube(.045,.028,.5,'l1Metal',rotation=[0,0,180],position=[x,0,0]) for x in [0,-.4]]
        elif key=='baffle':fs=[formbox(.5,.7,.035,'l1Metal')]+[formbox(.06,.10,.13,'metal',y=y) for y in [.08,.55]]
        else:fs=[round_tube(.24,.17,.15,'metal')]+[round_tube(.034,.017,.10,'l1Metal',position=[.2*math.cos(i*math.tau/10),.15,.2*math.sin(i*math.tau/10)]) for i in range(10)]
        if key=='separator':fs += [round_tube(.09,.065,.25,'metal',rotation=[0,0,-90],position=[.25,.70,0])]
        put('process',key,name,fs)
    structural=names('gusset:三角加强板 foot:调平机脚 saddle:管道鞍座 clamp:抱箍半体 eye:起吊耳板 clevis:叉耳连接头 anchor:地脚锚钩 hinge:重载铰接耳')
    for key,name in structural:
        if key=='gusset':fs=[plate([[0,0],[.5,0],[0,.6]],.05,'l1Metal')]
        elif key=='foot':fs=[disk(.24,.08,'l1Rubber'),rod([0,.08,0],[0,.5,0],.045,'l1Metal'),disk(.08,.06,'metal',y=.3)]
        elif key=='saddle':fs=[arc(.28,.055,180,355,color='l1Metal',center=[0,.38,0]),formbox(.6,.07,.24,'l1Metal')]+[formbox(.05,.18,.18,'l1Metal',x=x,y=.07) for x in [-.24,.24]]
        elif key=='clamp':fs=[arc(.25,.035,0,180,color='l1Metal')]+[formbox(.14,.045,.12,'metal',x=x) for x in [-.29,.29]]
        elif key=='eye':fs=[ring(.17,.055,.07,'l1Metal',rotation=[90,0,0],position=[0,.32,0]),plate([[-.22,0],[.22,0],[.12,.3],[-.12,.3]],.07,'l1Metal')]
        elif key=='clevis':fs=[formbox(.4,.08,.3,'l1Metal')]+[formbox(.065,.35,.3,'l1Metal',x=x,y=.08) for x in [-.167,.167]]
        elif key=='anchor':fs=[rod([0,0,0],[0,.55,0],.035,'l1Metal'),elbow(.13,.035,.015,150)]
        else:fs=[formbox(.4,.07,.2,'l1Metal'),round_tube(.08,.038,.35,'metal',rotation=[0,0,90],position=[.175,.13,0])]
        put('structure',key,name,fs)
    finish('industry',70)
