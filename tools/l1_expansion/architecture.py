"""174 architectural semantic profiles, not complete building assemblies."""
from .common import *

SECTIONS={
'i':[(-.5,0),(.5,0),(.5,.15),(.1,.15),(.1,.85),(.5,.85),(.5,1),(-.5,1),(-.5,.85),(-.1,.85),(-.1,.15),(-.5,.15)],
't':[(-.12,0),(.12,0),(.12,.78),(.5,.78),(.5,1),(-.5,1),(-.5,.78),(-.12,.78)],
'l':[(-.5,0),(.5,0),(.5,.18),(-.3,.18),(-.3,1),(-.5,1)],
'u':[(-.5,0),(.5,0),(.5,1),(.3,1),(.3,.18),(-.3,.18),(-.3,1),(-.5,1)],
'c':[(-.5,0),(.5,0),(.5,.18),(-.3,.18),(-.3,.82),(.5,.82),(.5,1),(-.5,1)],
'z':[(-.5,0),(.35,0),(.35,.18),(.1,.18),(.1,.82),(.5,.82),(.5,1),(-.35,1),(-.35,.82),(-.1,.82),(-.1,.18),(-.5,.18)],
'hat':[(-.5,0),(-.22,0),(-.22,.78),(.22,.78),(.22,0),(.5,0),(.5,.15),(.36,.15),(.36,1),(-.36,1),(-.36,.15),(-.5,.15)],
'omega':[(-.5,0),(-.22,0),(-.22,.3),(-.36,.55),(-.36,.86),(-.22,1),(.22,1),(.36,.86),(.36,.55),(.22,.3),(.22,0),(.5,0),(.5,.13),(.34,.13),(.5,.5),(.5,.92),(.3,1.18),(-.3,1.18),(-.5,.92),(-.5,.5),(-.34,.13),(-.5,.13)],
'lip':[(-.5,0),(.5,0),(.5,.3),(.34,.3),(.34,.14),(-.34,.14),(-.34,1),(-.5,1)],
'double_t':[(-.5,0),(.5,0),(.5,.13),(.1,.13),(.1,.42),(.42,.42),(.42,.58),(.1,.58),(.1,.86),(.5,.86),(.5,1),(-.5,1),(-.5,.86),(-.1,.86),(-.1,.58),(-.42,.58),(-.42,.42),(-.1,.42),(-.1,.13),(-.5,.13)],
'dovetail':[(-.5,0),(.5,0),(.35,.25),(.15,.25),(.33,1),(-.33,1),(-.15,.25),(-.35,.25)],
'groove':[(-.5,0),(.5,0),(.5,1),(.2,1),(.2,.35),(-.2,.35),(-.2,1),(-.5,1)],
'step':[(-.5,0),(.5,0),(.5,.3),(.18,.3),(.18,.65),(-.12,.65),(-.12,1),(-.5,1)],
'sill':[(-.5,0),(.5,0),(.5,.22),(.36,.36),(-.28,.65),(-.28,1),(-.5,1)],
'nosing':[(-.5,0),(.26,0),(.5,.18),(.5,.38),(.26,.58),(-.25,.58),(-.25,1),(-.5,1)],
'bulb':[(-.12,0),(.12,0),(.12,.65),(.35,.73),(.42,.89),(.28,1),(-.28,1),(-.42,.89),(-.35,.73),(-.12,.65)],
'rail':[(-.5,0),(.5,0),(.4,.18),(.12,.24),(.12,.73),(.35,.83),(.35,1),(-.35,1),(-.35,.83),(-.12,.73),(-.12,.24),(-.4,.18)],
'gutter':[(-.5,.5),(-.36,0),(.36,0),(.5,.5),(.33,.5),(.24,.15),(-.24,.15),(-.33,.5)],
'double_channel':[(-.5,0),(.5,0),(.5,1),(.34,1),(.34,.15),(.08,.15),(.08,.85),(-.08,.85),(-.08,.15),(-.34,.15),(-.34,1),(-.5,1)],
'cross':[(-.14,0),(.14,0),(.14,.35),(.5,.35),(.5,.65),(.14,.65),(.14,1),(-.14,1),(-.14,.65),(-.5,.65),(-.5,.35),(-.14,.35)],
'v':[(-.5,1),(-.33,1),(0,.28),(.33,1),(.5,1),(0,0)],
'keel':[(-.5,0),(.5,0),(.35,.2),(.15,.3),(0,1),(-.15,.3),(-.35,.2)],
'fork':[(-.12,0),(.12,0),(.12,.4),(.5,.85),(.35,1),(0,.65),(-.35,1),(-.5,.85),(-.12,.4)],
'tongue':[(-.5,0),(.5,0),(.5,.66),(.12,.66),(.12,1),(-.12,1),(-.12,.66),(-.5,.66)]}
SECTION_NAMES=names('i:工字承重截面 t:丁字托梁截面 l:直角护边截面 u:开口槽钢截面 c:横口导轨截面 z:错层连接截面 hat:帽形檩条截面 omega:弧折卡槽截面 lip:折边角钢截面 double_t:双腹翼梁截面 dovetail:燕尾导向截面 groove:深口嵌槽截面 step:三级阶肩截面 sill:排水窗台截面 nosing:圆肩踏鼻截面 bulb:球头立筋截面 rail:轨形承托截面 gutter:梯形檐槽截面 double_channel:双腔开槽截面 cross:十字节点截面 v:V形支撑截面 keel:龙骨支撑截面 fork:分叉托架截面 tongue:凸舌拼接截面')


def opening_outline(key):
    if key=='rect':return [(-.5,0),(.5,0),(.5,1),(-.5,1)]
    if key=='round':return [(.5*math.cos(i*math.tau/16),.5+.5*math.sin(i*math.tau/16)) for i in range(16)]
    if key=='octagon':return [(.5*math.cos(math.pi/8+i*math.tau/8),.5+.5*math.sin(math.pi/8+i*math.tau/8)) for i in range(8)]
    if key=='point':return [(-.5,0),(.5,0),(.5,.57),(.30,.83),(0,1),(-.30,.83),(-.5,.57)]
    if key=='lancet':return [(-.32,0),(.32,0),(.32,.62),(.18,.88),(0,1),(-.18,.88),(-.32,.62)]
    if key=='keyhole':return [(-.33,0),(.33,0),(.16,.52),(.4,.68),(.42,.84),(.24,1),(-.24,1),(-.42,.84),(-.4,.68),(-.16,.52)]
    if key=='horseshoe':return [(-.32,0),(.32,0),(.32,.4),(.5,.62),(.46,.82),(.25,1),(-.25,1),(-.46,.82),(-.5,.62),(-.32,.4)]
    if key=='ogee':return [(-.5,0),(.5,0),(.5,.55),(.26,.68),(.23,.85),(0,1),(-.23,.85),(-.26,.68),(-.5,.55)]
    if key=='trapezoid':return [(-.5,0),(.5,0),(.34,1),(-.34,1)]
    if key=='diamond':return [(0,0),(.5,.5),(0,1),(-.5,.5)]
    if key=='trefoil':return [(-.5,0),(.5,0),(.5,.66),(.34,.81),(.18,.79),(.18,.94),(0,1),(-.18,.94),(-.18,.79),(-.34,.81),(-.5,.66)]
    if key=='segment':return [(-.5,0),(.5,0),(.5,.7),(.3,.9),(0,1),(-.3,.9),(-.5,.7)]
    if key=='splayed':return [(-.5,0),(.5,0),(.5,.8),(.3,1),(-.3,1),(-.5,.8)]
    return [(-.5,0),(.5,0),(.5,.5),*[(.5*math.cos(a),.5+.5*math.sin(a)) for a in [i*math.pi/8 for i in range(1,9)]]]


def contour_frame(outline,w=1,h=1,d=.16,t=.09,color='l1Ivory'):
    outer=[[x*w,y*h] for x,y in outline];cy=h/2
    inner=[[x*(1-2*t/w),cy+(y-cy)*(1-2*t/h)] for x,y in outer]
    forms=[]
    for i in range(len(outer)):
        j=(i+1)%len(outer)
        forms.append(plate([outer[i],outer[j],inner[j],inner[i]],d,color))
    return forms


def author():
    def put(group,key,name,fs,sz,**kw):return register('architecture',group,key,name,fs,sz,**kw)
    for key,name in SECTION_NAMES:
        outline=SECTIONS[key];h=max(p[1] for p in outline)
        fs=[plate([[x*.5,y*.5] for x,y in outline],1.6,'l1Slate')]
        put('section',key,name,fs,[.5,h*.5,1.6],material='mat.metal',
            description=name+'；截面由可读多边形定义，沿纵向挤出，可供梁柱与边框复用。')
    wall=names('rebated:企口围护板 cavity:中空双壁板 ribbed:竖肋加劲板 corrugated:折波围护板 castellated:顶齿女儿墙板 honeycomb:六角通风墙芯 louvers:斜叶通风板 grid:方格镂空墙芯 perforated:孔洞砌块板 buttress:带斜撑基础墙片 pilaster:壁柱立面板 splitface:错缝劈面砌块 wattle:编条填充墙芯 braced:交叉撑墙芯 service:检修槽墙片 firewall:防火折返隔板')
    for key,name in wall:
        w,h,d=1.8,2.4,.28;fs=[]
        if key in ('rebated','cavity','ribbed','buttress','pilaster','splitface','service','firewall'):
            if key=='cavity':fs=[formbox(w,h,.06,'l1Ivory',z=z) for z in [-.11,.11]]+[formbox(.1,h,d,'l1Slate',x=x) for x in [-.65,0,.65]]
            elif key=='service':fs=frame(w,h,d,.22,'l1Ivory')+[formbox(.1,h-.44,.08,'l1Metal',x=x,y=.22) for x in [-.4,.4]]
            else:
                fs=[formbox(w,h,.18,'l1Ivory',z=-.05)]
                if key=='rebated':fs += [formbox(.12,h,.32,'l1Slate',x=-.84),formbox(.12,h,.12,'l1Slate',x=.84,z=.03)]
                if key=='ribbed':fs += [formbox(.1,h,.12,'l1Slate',x=x,z=.1) for x in [-.7,-.35,0,.35,.7]]
                if key=='buttress':fs += [plate([[-.15,0],[.45,0],[.08,1.8],[-.15,1.8]],.24,'l1Slate',rotation=[0,90,0],position=[x,0,.08]) for x in [-.6,.6]]
                if key=='pilaster':fs += [formbox(.28,h,.18,'l1Slate',x=x,z=.08) for x in [-.67,.67]]
                if key=='splitface':fs += [formbox(.39,.34,.08,'stone',x=-.65+j*.43+(.12 if i%2 else 0),y=.05+i*.39,z=.09,bevel=.025) for i in range(6) for j in range(4)]
                if key=='firewall':fs += [formbox(.28,h,.9,'l1Slate',x=.76,z=.3)]
        elif key=='corrugated':
            for i in range(9):fs += [formbox(.24,h,.055,'l1Metal',x=-.82+i*.205,z=.05*(1 if i%2 else -1),bevel=0,rotation=[0,25 if i%2 else -25,0])]
        elif key=='castellated':
            fs=[formbox(w,1.55,d,'stone')]+[formbox(.28,.6,d,'stone',x=x,y=1.55) for x in [-.7,-.23,.23,.7]]
        elif key=='honeycomb':
            fs=frame(w,h,.18,.08,'l1Slate')
            for y in [.4,.96,1.52,2.08]:
                for x in [-.56,0,.56]:fs += placed(contour_frame(opening_outline('round')[::2],.53,.51,.12,.035,'l1Ivory'),[x,y-.255,0])
        elif key=='louvers':fs=frame(w,h,d,.1,'l1Slate')+[box([w-.2,.055,.34],'l1Ivory',[0,.22+i*.24,0],.007,rotation=[25,0,0]) for i in range(9)]
        elif key in ('grid','perforated'):
            fs=frame(w,h,d,.10,'l1Ivory')
            fs += [formbox(.10,h-.2,d,'l1Slate',x=x,y=.10) for x in [-.42,0,.42]]
            fs += [formbox(w-.2,.12,d,'l1Slate',y=y) for y in ([.55,1.1,1.65] if key=='grid' else [.4,.8,1.2,1.6,2.0])]
        elif key=='wattle':
            fs=frame(w,h,.13,.1,'woodDark')+[formbox(.065,h-.2,.05,'wood',x=x,y=.1,z=.04) for x in [-.6,-.3,0,.3,.6]]
            fs += [formbox(w-.2,.05,.04,'woodLight',y=.25+i*.2,z=-.04) for i in range(10)]
        elif key=='braced':
            fs=frame(w,h,d,.13,'woodDark')+[rod([-.7,.2,0],[.7,2.2,0],.07,'wood'),rod([.7,.2,.05],[-.7,2.2,.05],.07,'wood')]
        put('wall',key,name,fs,[w,h,max(d,.9 if key=='firewall' else .5 if key=='buttress' else d)],material='mat.plaster')
    for key,name in names('rect:矩形洞口边框 round:圆形洞口边框 octagon:八角窗芯边框 point:尖拱洞口边框 lancet:细高尖拱窗框 keyhole:钥匙形窗芯 horseshoe:马蹄拱窗芯 ogee:双曲尖拱窗芯 trapezoid:梯形斜窗边框 diamond:菱形窗芯 trefoil:三叶拱窗芯 segment:扁拱门楣边框 splayed:斜角检修口框 arch:半圆拱洞口框'):
        put('opening',key,name,contour_frame(opening_outline(key),1.5,2,.18,.14),[1.5,2,.18],material='mat.stone')
    roof=names('standing_seam:直立锁边屋面板 corrugated:连续折波屋面板 barrel:筒拱屋面片 sawtooth:锯齿采光屋面片 butterfly:蝶形汇水屋面片 gambrel:折坡屋面片 mansard:折檐屋面片 hip_corner:斜脊三角屋面片 valley:屋谷连接片 saddle:鞍形屋面片 hyperbolic:双曲屋面片 conical:锥面扇形屋面片 scale:鱼鳞瓦排片 pantile:S形瓦排片 flat_tile:错缝平瓦排片 glazed:采光格栅屋面片')
    for key,name in roof:
        fs=[];w,d=1.6,1.6
        if key in ('scale','pantile','flat_tile'):
            for row in range(4):
                for col in range(4):
                    if key=='scale':fs.append(plate([[-.18,0],[.18,0],[.18,.25],[-.02,.37],[-.18,.25]],.055,'l1Terracotta',rotation=[-76,0,0],position=[-.6+col*.4,.12+row*.11,-.55+row*.38]))
                    elif key=='pantile':fs += placed([arc(.14,.045,0,180,'xy','l1Terracotta',6)],[-.6+col*.4,.12+row*.10,-.6+row*.4],rotation=[90,0,0],scale=[1,1,1.25])
                    else:fs.append(box([.38,.055,.46],'l1Terracotta',[-.6+col*.4,.10+row*.1,-.6+row*.38],.016,rotation=[-14,0,0]))
        elif key=='glazed':
            fs=[box([1.6,.06,1.6],'glass',[0,.18,0],.01,material='mat.glass')]
            fs += [box([.05,.07,1.6],'l1Metal',[x,.22,0],.005) for x in [-.78,-.4,0,.4,.78]]+[box([1.6,.07,.05],'l1Metal',[0,.22,z],.005) for z in [-.78,0,.78]]
        else:
            nx,nz=(8,4);pts=[];faces=[]
            def height(x,z):
                if key=='standing_seam':return .10+.05*z
                if key=='corrugated':return .14+(.07 if round((x+.8)/.2)%2 else 0)
                if key=='barrel':return .12+.4*math.sqrt(max(0,1-(x/.81)**2))
                if key=='sawtooth':return .1+((x+.8)% .8)*.5
                if key=='butterfly':return .10+.45*abs(x)
                if key=='gambrel':return .12+(.48-.6*abs(x) if abs(x)<.45 else .21-(abs(x)-.45)*.3)
                if key=='mansard':return .12+.36*min(1,(.8-abs(x))/.25)
                if key=='hip_corner':return .12+.5*max(0,.8-max(x,z))
                if key=='valley':return .12+.4*abs(x-z)
                if key=='saddle':return .30+.22*(x*x-z*z)
                if key=='hyperbolic':return .34+.32*x*z
                if key=='conical':return .12+.42*(1-math.hypot(x,z)/1.14)
                return .2
            for z in range(nz+1):
                for x in range(nx+1):
                    u,v=-.8+1.6*x/nx,-.8+1.6*z/nz;pts.append([u,height(u,v),v])
            # Closed thin shell with separate bottom topology.
            n=len(pts);pts += [[x,y-.045,z] for x,y,z in pts]
            for z in range(nz):
                for x in range(nx):
                    a=z*(nx+1)+x;b=a+1;c=a+nx+1;e=c+1
                    faces += [[a,c,e,b],[n+a,n+b,n+e,n+c]]
            rim=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,nz+1)]+[nz*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(nz-1,0,-1)]
            for i,a in enumerate(rim):b=rim[(i+1)%len(rim)];faces.append([a,b,n+b,n+a])
            fs=[poly(pts,faces,'l1Slate')]
            if key=='standing_seam':fs += [box([.035,.12,1.6],'l1Metal',[x,.21,0],.004) for x in [-.6,-.2,.2,.6]]
        put('roof',key,name,fs,[w,.8,d],material='mat.paint')
    trims=names('cyma:双曲檐口线脚 cavetto:凹弧檐口线脚 ovolo:凸弧檐口线脚 dentil:齿饰檐口段 egg:卵形檐口段 drip:滴水边线脚 fascia:层叠封檐板 soffit:通风檐底板 ridge_cap:折面脊盖件 hip_cap:斜脊锁盖件 coping:双坡压顶件 corbel:曲线托檐件 frieze:回折腰线件 snow_guard:挡雪压条件')
    for idx,(key,name) in enumerate(trims):
        if key in ('cyma','cavetto','ovolo'):
            xs=[-.2+.4*i/8 for i in range(9)]
            path=[[x,.06+.24*((math.sin((x+.2)/.4*math.pi)*.65+(x+.2)/.4*.35) if key=='cyma' else (1-math.cos((x+.2)/.4*math.pi/2) if key=='cavetto' else math.sin((x+.2)/.4*math.pi/2)))] for x in xs]
            fs=[plate([[-.2,0],[.2,0],*reversed(path)],1.5,'l1Ivory')]
        elif key in ('dentil','egg','frieze'):
            fs=[formbox(1.5,.1,.26,'l1Ivory',y=.23)]
            for x in [-.6,-.3,0,.3,.6]:
                fs += [ico([.17,.22,.19],'l1Ivory',[x,.16,0],detail=0)] if key=='egg' else [formbox(.14,.22,.2,'l1Ivory',x=x),*([] if key!='frieze' else [formbox(.22,.06,.2,'l1Ivory',x=x+.07,y=.14)])]
        elif key=='soffit':fs=[box([1.5,.045,.4],'l1Ivory',[0,.03,0])]+[box([.05,.03,.3],'l1Slate',[x,.064,0],.003) for x in [-.65,-.45,-.25,-.05,.15,.35,.55]]
        elif key=='corbel':fs=[plate([[-.2,0],[0,0],[.04,.12],[.2,.3],[.2,.4],[-.2,.4]],.30,'l1Ivory')]
        else:
            profiles={'drip':[[-.2,0],[.2,0],[.2,.08],[.08,.08],[.08,.18],[-.2,.18]],'fascia':[[-.2,0],[.2,0],[.2,.18],[.08,.18],[.08,.28],[-.2,.28]],'ridge_cap':[[-.3,0],[0,.22],[.3,0],[.3,.08],[0,.31],[-.3,.08]],'hip_cap':[[-.3,0],[0,.20],[.3,0],[.25,.14],[0,.34],[-.25,.14]],'coping':[[-.3,0],[.3,0],[.3,.13],[0,.26],[-.3,.13]],'snow_guard':[[-.2,0],[.2,0],[.2,.06],[.05,.06],[.05,.32],[-.05,.32],[-.05,.06],[-.2,.06]]}
            fs=[plate(profiles[key],1.5,'l1Ivory')]
        put('trim',key,name,fs,[1.5,.45,1.5],material='mat.stone')
    columns=names('doric:素线柱身基件 ionic:卷草柱冠基件 tuscan:简柱柱脚基件 fluted:凹槽柱身基件 twisted:螺旋柱身基件 lotus:莲瓣柱冠基件 mushroom:蘑菇柱冠基件 tapered:收分墩柱基件 baluster:束腰栏柱基件 pedestal:多台阶柱础基件')
    for key,name in columns:
        profiles={'doric':[[.3,0],[.3,.1],[.21,.18],[.18,1.2],[.31,1.26],[.31,1.35]],'ionic':[[.29,0],[.21,.1],[.19,1.15],[.26,1.28]],'tuscan':[[.35,0],[.35,.15],[.25,.24],[.2,1.3]],'lotus':[[.23,0],[.18,.3],[.23,.7],[.4,1],[.34,1.22]],'mushroom':[[.17,0],[.16,.75],[.35,1],[.45,1.2],[.43,1.3]],'tapered':[[.42,0],[.34,.22],[.19,1.3]],'baluster':[[.25,0],[.25,.1],[.14,.2],[.24,.5],[.17,.8],[.09,1.06],[.23,1.22],[.23,1.3]],'pedestal':[[.44,0],[.44,.15],[.36,.15],[.36,.3],[.28,.3],[.28,.85],[.37,.9],[.37,1.04],[.43,1.1],[.43,1.3]]}
        if key=='fluted':
            fs=[lathe([[.27,0],[.27,.13],[.2,.2],[.18,1.18],[.28,1.25],[.28,1.3]],'l1Ivory',12,cap=True)]
            fs += [rod([.2*math.cos(a),.2,.2*math.sin(a)],[.18*math.cos(a),1.17,.18*math.sin(a)],.024,'stoneLight',sides=6) for a in [i*math.tau/12 for i in range(12)]]
        elif key=='twisted':
            fs=[loft([[.035*math.sin(i*.75),i*1.3/9,.035*math.cos(i*.75),.20,.20] for i in range(10)],'l1Ivory',8,twist=65)]
            fs += [disk(.26,.09,'l1Ivory',y=y) for y in [0,1.24]]
        else:fs=[lathe(profiles[key],'l1Ivory',12,cap=True)]
        if key=='ionic':fs += [arc(.14,.055,0,280,'xy','l1Ivory',12,[x,1.22,0]) for x in [-.24,.24]]
        if key=='lotus':fs += [ico([.14,.34,.14],'stoneLight',[.28*math.cos(a),.96,.28*math.sin(a)],detail=0) for a in [i*math.tau/8 for i in range(8)]]
        put('column',key,name,fs,[.9,1.4,.9],material='mat.stone',detail=list(range(1,len(fs))) or None)
    # Treads and stringers are L1 parts, not whole staircase assemblies.
    for i,(key,name) in enumerate(names('closed_tread:封闭踏步块 open_tread:开放踏板段 grating_tread:栅格踏板段 winder:扇形转角踏板 spiral_tread:螺旋梯扇形踏板 bullnose:圆鼻踏板段 riser:踢面防滑板 stringer:锯齿梯侧梁 carriage:斜撑梯底梁 landing_edge:休息平台收边 kickplate:梯侧挡脚片 anti_slip:防滑嵌条段')):
        if key in ('winder','spiral_tread'):
            angle=90 if key=='winder' else 35;outline=[[0,0]]+[[math.cos(math.radians(a)),math.sin(math.radians(a))] for a in [j*angle/8 for j in range(9)]]
            if key=='spiral_tread':
                # The tread must not cap its own shaft sleeve. Annular sector
                # joins the collar outside its open bore; no hidden centre fan.
                outline=outline[1:]+[[.14*math.cos(math.radians(a)),.14*math.sin(math.radians(a))] for a in [j*angle/8 for j in range(8,-1,-1)]]
            fs=[plate(outline,.12,'l1Slate',rotation=[90,0,0],position=[-.5,.12,-.5])]
            if key=='spiral_tread':fs += [round_tube(.15,.09,.16,'l1Metal',12,position=[-.5,0,-.5])]
        elif key in ('stringer','carriage'):
            outline=[[-.6,0],[.6,.8],[.6,1.0]]
            if key=='stringer':outline += [[.3,1.0],[.3,.78],[0,.78],[0,.56],[-.3,.56],[-.3,.34],[-.6,.34]]
            else:outline += [[-.6,.2]]
            fs=[plate(outline,.12,'l1Slate')]
        elif key=='grating_tread':fs=[box([1,.08,.04],'l1Metal',[0,.05,z],.003) for z in [-.18,-.12,-.06,0,.06,.12,.18]]+[box([.06,.1,.43],'l1Slate',[x,.05,0]) for x in [-.46,.46]]
        elif key=='anti_slip':fs=[box([1,.03,.1],'l1Rubber',[0,.015,0],.004)]+[box([1,.01,.008],'l1Slate',[0,.035,z],.001) for z in [-.035,-.017,0,.017,.035]]
        else:
            h=.22 if key=='closed_tread' else .06;d=.42 if key not in ('riser','kickplate') else .055
            fs=[formbox(1,h,d,'l1Ivory')]
            if key in ('bullnose','landing_edge'):fs += [rod([-.5,.055,.21],[.5,.055,.21],.06,'l1Ivory')]
            if key in ('riser','kickplate'):fs += [formbox(1,.27,.03,'l1Slate',y=.04,z=-.025)]
            if key=='open_tread':fs += [formbox(.07,.15,.38,'l1Slate',x=x,y=-.13) for x in [-.32,.32]]
        put('stair',key,name,fs,[1.25,1.05 if key in ('carriage','stringer') else .35,1.05 if key in ('winder','spiral_tread') else .5],material='mat.metal')
    for i,(key,name) in enumerate(names('plank:榫接木地板芯 herringbone:人字拼地板芯 parquet:回字拼地板芯 raised:架空地板托片 perforated:散热孔地板芯 grate:直格排水地板芯 radial:放射镂空地板芯 hex:六角铺地基块 triangular:三角拼地基块 octagonal:八角铺地基块 edge_rebate:边缘嵌槽地板芯 hatch:检修孔周边板')):
        if key in ('hex','triangular','octagonal'):
            n={'hex':6,'triangular':3,'octagonal':8}[key];outline=[[.6*math.cos(a),.6*math.sin(a)] for a in [j*math.tau/n for j in range(n)]];fs=[plate(outline,.12,'l1Ivory',rotation=[90,0,0],position=[0,.12,0])]
        elif key in ('hatch','perforated','radial','grate'):
            fs=placed(frame(1.2,1.2,.10,.10,'l1Slate'),[0,.10,-.6],[90,0,0])
            if key=='grate':fs += [box([.045,.10,1.05],'l1Metal',[x,.05,0]) for x in [-.45,-.3,-.15,0,.15,.3,.45]]
            if key=='radial':fs += [box([1.1,.08,.035],'l1Metal',[0,.05,0],.002,rotation=[0,j*30,0]) for j in range(6)]
            if key=='perforated':fs += [box([1.0,.08,.055],'l1Metal',[0,.05,z],.002) for z in [-.35,0,.35]]+[box([.055,.08,1.0],'l1Metal',[x,.05,0],.002) for x in [-.35,0,.35]]
        elif key=='raised':fs=[box([1.2,.10,1.2],'l1Ivory',[0,.29,0])]+[formbox(.09,.24,.09,'l1Metal',x=x,z=z) for x in [-.48,.48] for z in [-.48,.48]]
        elif key=='edge_rebate':fs=[box([1.2,.1,1.1],'l1Ivory',[0,.05,-.05]),box([1.2,.05,.12],'l1Slate',[0,.025,.52])]
        elif key=='plank':fs=[box([.28,.10,1.2],'wood',[x,.05,0],.008) for x in [-.45,-.15,.15,.45]]+[box([1.2,.025,.06],'woodDark',[0,.07,-.57])]
        elif key=='parquet':fs=[box([1.2-.27*j,.10,.12],'woodLight' if j%2 else 'wood',[0,.05,.53-.13*j],.005,rotation=[0,j*90,0]) for j in range(4)]+[box([.38,.1,.38],'woodDark',[0,.05,0])]
        else:fs=[box([.21,.10,.64],'woodLight' if i%2 else 'wood',[x,.05,z],.005,rotation=[0,45 if i%2 else -45,0]) for i,(x,z) in enumerate([(-.36,-.24),(0,-.24),(.36,-.24),(-.36,.27),(0,.27),(.36,.27)])]
        put('floor',key,name,fs,[1.3,.4,1.3],material='mat.wood')
    rail=names('picket:尖顶栅条芯 spear:矛形栅条芯 loop:环饰栅条芯 scroll:涡线栅条芯 diamond:菱格栅条芯 cross:交叉栅条芯 mesh:网格护栏芯 glass:玻璃夹持栏芯 cable:水平索栏芯 baluster:束腰栏芯 lattice:斜格木栏芯 trellis:攀援格栅芯')
    for key,name in rail:
        fs=[formbox(1.2,.06,.08,'l1Slate',y=y) for y in [.05,.92]]
        if key in ('picket','spear','baluster'):
            for x in [-.45,-.15,.15,.45]:
                if key=='baluster':fs.append(lathe([[.035,.11],[.06,.3],[.03,.65],[.045,.92]],'l1Ivory',8,cap=True,position=[x,0,0]))
                else:
                    fs.append(rod([x,.1,0],[x,.99,0],.025,'l1Slate'))
                    fs.append(plate([[-.06,.0],[0,.17],[.06,0],[0,.04]],.035,'l1Metal',position=[x,.96,0]))
                    if key=='spear':fs.append(ring(.07,.025,.025,'l1Metal',rotation=[90,0,0],position=[x,.48,0]))
        elif key in ('loop','scroll'):
            fs += [arc(.18,.022,0,340 if key=='scroll' else 355,'xy','l1Metal',14,[x,.5,0]) for x in [-.36,0,.36]]
            fs += [rod([x,.1,0],[x,.92,0],.018,'l1Slate') for x in [-.54,.54]]
        elif key in ('cross','diamond','lattice'):
            for x in [-.38,0,.38]:
                fs += [rod([x-.18,.15,0],[x+.18,.86,0],.022,'wood' if key=='lattice' else 'l1Metal'),rod([x+.18,.15,.01],[x-.18,.86,.01],.022,'wood' if key=='lattice' else 'l1Metal')]
            if key=='diamond':fs += [box([.12,.12,.05],'l1Metal',[x,.5,0],.005,rotation=[0,0,45]) for x in [-.38,0,.38]]
        elif key=='glass':fs += [box([1.1,.76,.035],'glass',[0,.51,0],.005,material='mat.glass')]+[box([.075,.075,.08],'l1Metal',[x,y,0]) for x in [-.53,.53] for y in [.18,.84]]
        elif key=='cable':fs += [rod([-.6,y,0],[.6,y,0],.012,'l1Metal') for y in [.25,.43,.61,.79]]
        else:
            fs += [formbox(.035,.8,.035,'wood' if key=='trellis' else 'l1Slate',x=x,y=.12) for x in [-.5,-.3,-.1,.1,.3,.5]]
            fs += [formbox(1.1,.035,.035,'wood' if key=='trellis' else 'l1Slate',y=y,z=.025) for y in ([.22,.48,.73] if key=='trellis' else [.25,.4,.55,.7,.85])]
        put('railing',key,name,fs,[1.2,1.15,.12],material='mat.metal')
    joints=names('mortise:方榫承口块 tenon:透榫锁肩块 lap:半搭接连接块 scarf:斜接续梁块 dovetail:燕尾锁接块 tusk:楔销锁接块 knee:弧肘斜撑块 gusset:三角角撑片 saddle:鞍形梁托块 clevis:叉耳连接块 shoe:柱脚杯托块 splice:双夹拼接块')
    for key,name in joints:
        fs=[]
        if key in ('mortise','shoe','saddle','clevis'):
            fs=[formbox(.6,.1,.5,'l1Slate')]+[formbox(.09,.5,.5,'l1Slate',x=x,y=.1) for x in [-.255,.255]]
            if key=='mortise':fs += [formbox(.42,.1,.5,'l1Slate',y=.5)]
            if key=='shoe':fs += [formbox(.42,.45,.08,'l1Slate',y=.1,z=-.21)]
            if key=='saddle':fs += [formbox(.42,.08,.5,'l1Slate',y=.22)]
            if key=='clevis':fs += [rod([-.35,.4,0],[.35,.4,0],.06,'l1Metal')]
        elif key in ('tenon','tusk'):fs=[formbox(.6,.36,.4,'wood'),formbox(.24,.3,.22,'wood',y=.36)]+([plate([[-.3,0],[.3,.08],[.3,.15],[-.3,.1]],.1,'woodDark',position=[0,.52,0])] if key=='tusk' else [])
        elif key=='lap':fs=[formbox(.6,.2,.5,'wood'),formbox(.3,.2,.5,'wood',x=-.15,y=.2)]
        elif key=='scarf':fs=[plate([[-.5,0],[.5,0],[.5,.18],[-.5,.5]],.4,'wood')]
        elif key=='dovetail':fs=[plate([[-.3,0],[.3,0],[.15,.3],[.27,.6],[-.27,.6],[-.15,.3]],.4,'wood')]
        elif key=='gusset':fs=[plate([[-.3,0],[.3,0],[-.3,.6]],.06,'l1Slate')]+[disk(.028,.03,'l1Metal',rotation=[90,0,0],position=[x,y,.04]) for x,y in [(-.22,.1),(.15,.1),(-.22,.46)]]
        elif key=='knee':fs=[plate([[-.3,0],[-.16,0],[-.05,.25],[.3,.5],[.3,.6],[-.3,.6]],.20,'wood')]
        else:fs=[formbox(.6,.42,.05,'l1Slate',z=z) for z in [-.23,.23]]+[rod([x,.21,-.27],[x,.21,.27],.03,'l1Metal') for x in [-.2,.2]]
        put('joinery',key,name,fs,[1,.7,.6],material='mat.wood')
    trad=names('dou:斗口承托块 gong:弧形栱臂件 ang:昂尾斜撑件 qiao:翘头挑檐件 fang:额枋锁肩件 que:雀替挑角件 sparrow:镂空雀替芯 purlin:抱檩承托件 rafter:椽头收口件 hip_finial:脊端翘尾件 drip_tile:滴水瓦端件 tile_end:圆瓦当端件 ridge_beast:抽象脊饰座 moon_gate:月洞弧边件 screen:回纹屏芯件 lattice:冰裂纹窗芯')
    for i,(key,name) in enumerate(trad):
        if key=='dou':fs=[formbox(.58,.14,.58,'woodDark'),formbox(.42,.2,.42,'wood',y=.14)]+[formbox(.14,.12,.58,'wood',x=x,y=.34) for x in [-.22,.22]]
        elif key in ('gong','ang','qiao','que','sparrow','fang'):
            outlines={'gong':[[-.6,.22],[-.6,.38],[-.4,.27],[0,.16],[.4,.27],[.6,.38],[.6,.22],[.3,.04],[-.3,.04]],'ang':[[-.6,0],[.6,.4],[.6,.6],[-.6,.22]],'qiao':[[-.6,.05],[-.6,.2],[.15,.23],[.5,.5],[.6,.45],[.2,.05]],'que':[[-.5,0],[-.35,.08],[-.08,.2],[.15,.5],[.5,.6],[-.5,.6]],'sparrow':[[-.5,0],[-.4,0],[.15,.48],[.5,.48],[.5,.6],[-.5,.6]],'fang':[[-.6,0],[.6,0],[.6,.38],[.43,.38],[.43,.5],[-.43,.5],[-.43,.38],[-.6,.38]]}
            fs=[plate(outlines[key],.24,'wood')]
        elif key in ('drip_tile','tile_end'):
            fs=[plate([[-.3,.3],[0,0],[.3,.3],[.3,.5],[-.3,.5]],.08,'l1Terracotta')] if key=='drip_tile' else [disk(.27,.08,'l1Terracotta',rotation=[90,0,0],position=[0,.3,.03])]
            fs += [arc(.14,.03,0,300,'xy','l1Ochre',10,[0,.30,.085])]
        elif key in ('purlin','rafter'):fs=[round_tube(.26,.19,.5,'wood',12)] if key=='purlin' else [lathe([[.17,0],[.17,.45],[.23,.50],[.23,.58]],'wood',8,cap=True)]
        elif key in ('hip_finial','ridge_beast'):fs=[plate([[-.5,0],[.5,0],[.47,.16],[.22,.3],[.2,.5],[.04,.57],[-.08,.35],[-.26,.23],[-.5,.18]],.18,'l1Terracotta')]+([ico([.28,.16,.24],'l1Ochre',[.12,.5,0],detail=0)] if key=='ridge_beast' else [])
        elif key=='moon_gate':fs=contour_frame(opening_outline('round'),1.2,1.2,.2,.12,'l1Ivory')
        elif key=='screen':
            fs=frame(1.1,1,.08,.06,'woodDark')
            for x in [-.35,0,.35]:fs += placed([plate(SECTIONS['step'],.035,'wood')],[x,.15,.025],scale=[.25,.65,1])
        else:fs=frame(1.1,1,.08,.06,'woodDark')+[rod(a,b,.018,'wood') for a,b in [([-.5,.2,0],[.42,.77,0]),([-.3,.95,0],[.18,.04,0]),([-.5,.65,0],[.5,.4,0]),([.15,.95,0],[.45,.1,0])]]
        put('traditional',key,name,fs,[1.3,1.25,.65],material='mat.wood',description=name+'；游戏风格化结构轮廓，不作为历史建筑复原或工程施工依据。')
    for i,(key,name) in enumerate(names('broken_arch:断拱石楔件 cracked_slab:开裂铺地角片 fractured_column:断柱榫口件 exposed_rebar:外露钢筋混凝土芯 rubble_wedge:碎墙楔角件 eroded_cornice:侵蚀檐口残件 chipped_brick:缺角砖石件 collapsed_lintel:折断过梁件')):
        outlines=[[-.5,0],[.5,0],[.5,.35],[.32,.42],[.24,.67],[.03,.54],[-.13,.86],[-.33,.62],[-.5,.72]]
        if key=='broken_arch':outlines=[[-.4,0],[.32,.1],[.5,.5],[.28,.62],[.15,.8],[-.18,.68],[-.35,.5]]
        elif key=='cracked_slab':outlines=[[-.5,0],[.5,0],[.5,.27],[.12,.26],[.02,.12],[-.06,.29],[-.5,.26]]
        elif key=='chipped_brick':outlines=[[-.5,0],[.5,0],[.5,.35],[.23,.5],[-.42,.5],[-.5,.35]]
        elif key=='collapsed_lintel':outlines=[[-.7,0],[.36,.05],[.42,.22],[.7,.29],[.3,.4],[-.7,.4]]
        fs=[plate(outlines,.5 if i%2 else .32,'stone')]
        if key=='fractured_column':fs += [lathe([[.24,0],[.21,.55]],'stoneLight',8,cap=True)]
        if key=='exposed_rebar':fs += [rod([x,.5,0],[x+.05,1.2,.1],.025,'l1Metal') for x in [-.3,0,.3]]
        if key=='eroded_cornice':fs += [formbox(1,.1,.6,'stoneLight',y=.25)]
        if key=='rubble_wedge':fs += [plate([[-.4,0],[.4,0],[.1,.5]],.4,'stoneDark',rotation=[0,38,0],position=[.2,0,0])]
        put('ruin',key,name,fs,[1.4,1.25,.7],material='mat.stone')
    drain=names('box_gutter:箱形檐槽段 half_round:半圆檐槽段 scupper:女儿墙泄水口 shoe:落水管弯鞋件 hopper:汇水斗口件 leaf_guard:檐槽落叶筛芯 channel_grate:线性排水篦芯 rain_chain:雨链杯节')
    for key,name in drain:
        if key=='box_gutter':fs=[plate([[-.25,.3],[-.25,0],[.25,0],[.25,.3],[.2,.3],[.2,.05],[-.2,.05],[-.2,.3]],1,'l1Metal')]
        elif key=='half_round':fs=[lathe([[.25,0],[.25,1],[.20,1],[.20,0]],'l1Metal',12,closed_profile=True,rotation=[90,0,0],position=[0,.26,0])]+[formbox(.05,.1,1,'l1Slate',x=-.24,y=.45)]
        elif key=='scupper':fs=frame(.65,.35,.6,.06,'l1Slate')+[formbox(.7,.06,.8,'l1Metal',y=-.02,z=.1)]
        elif key=='shoe':fs=[loft([[0,.65,0,.13,.13],[0,.28,0,.13,.13],[0,.13,.16,.13,.13],[0,.13,.45,.13,.13]],'l1Metal',12)]
        elif key=='hopper':fs=[lathe([[.11,0],[.11,.16],[.32,.45],[.32,.51],[.27,.51],[.27,.46],[.065,.16],[.065,0]],'l1Metal',12,closed_profile=True)]
        elif key in ('leaf_guard','channel_grate'):
            fs=[box([.5,.04,1],'l1Slate',[0,.02,0])]+[box([.52,.06,.045],'l1Metal',[0,.06,z],.004) for z in [-.45,-.3,-.15,0,.15,.3,.45]]
            if key=='leaf_guard':fs=fs[1:]+[rod([x,.03,-.5],[x,.03,.5],.018,'l1Metal') for x in [-.2,0,.2]]
        else:fs=[lathe([[.06,0],[.22,.25],[.2,.28],[.04,.03]],'l1Metal',12,closed_profile=True),arc(.08,.014,0,355,'xy','l1Metal',12,[0,.32,0])]
        put('drainage',key,name,fs,[.8,.8,1.1],material='mat.metal')
    finish('architecture',174)
