"""Terrain surfaces and seam modules; not whole terrains or registered scenes."""
from .common import *


def tile(height, n=6, width=2, depth=2, color='stone'):
    """Closed height patch with a regular XY-grid projected onto XZ."""
    vertices=[]
    for iy in range(n+1):
        for ix in range(n+1):
            x=(ix/n-.5)*width;z=(iy/n-.5)*depth
            vertices.append([x,.15+height(x,z),z])
    faces=[]
    for j in range(n):
        for i in range(n):
            a=j*(n+1)+i;faces.extend([[a,a+n+1,a+1],[a+1,a+n+1,a+n+2]])
    rim=list(range(n+1))+[j*(n+1)+n for j in range(1,n+1)]+[n*(n+1)+i for i in range(n-1,-1,-1)]+[j*(n+1) for j in range(n-1,0,-1)]
    base=len(vertices)
    vertices += [[vertices[k][0],0,vertices[k][2]] for k in rim]
    for i in range(len(rim)):
        j=(i+1)%len(rim);faces.append([rim[i],base+i,base+j,rim[j]])
    vertices.append([0,0,0]);center=len(vertices)-1
    for i in range(len(rim)):faces.append([center,base+(i+1)%len(rim),base+i])
    return poly(vertices,faces,color)


def bank(profile,color='stone',length=2):
    # Profile walks top edge, the return closes against a base datum.
    outline=[[-1,0]]+profile+[[1,0]]
    return plate(outline,length,color)


def author():
    def put(g,k,n,fs,sz,**kw):return register('terrain',g,k,n,fs,sz,**kw)
    surfaces=names('ridge:脊线地表块 basin:盆地地表块 saddle:鞍部地表块 terrace:阶地地表块 dune:沙丘脊线块 ripple:波纹沙地块 furrow:农田垄沟块 rutted:双车辙地表块 fractured:断层地表块 hummock:草甸丘包块 scree:碎石坡面块 bedrock:裸岩脊片块 dried:干裂泥地块 lava:熔岩皱褶地表块')
    for key,name in surfaces:
        height={
            'ridge':lambda x,z:.55*max(0,1-abs(x))*(.75+.2*z),
            'basin':lambda x,z:.36*min(1,x*x+z*z),
            'saddle':lambda x,z:.22+.17*x*x-.15*z*z,
            'terrace':lambda x,z:.12*(0 if x<-.35 else 1 if x<.35 else 2),
            'dune':lambda x,z:.45*max(0,1-abs(x+.25*z)/1.1)**2,
            'ripple':lambda x,z:.07*(1+math.cos(9*x+z)),
            'furrow':lambda x,z:.13*(1+math.cos(3*math.pi*x)),
            'rutted':lambda x,z:.15-.11*(math.exp(-50*(x-.48)**2)+math.exp(-50*(x+.48)**2)),
            'fractured':lambda x,z:.07+.27*(x>z*.3)+.09*abs(z),
            'hummock':lambda x,z:.38*math.exp(-3*(x*x+z*z))+.07*math.cos(4*z),
            'scree':lambda x,z:.22+.13*x+.04*math.cos(x*13+z*9),
            'bedrock':lambda x,z:.18+.15*abs(math.sin(x*3+z)),
            'dried':lambda x,z:.07+.025*math.cos(8*x)*math.cos(8*z),
            'lava':lambda x,z:.20+.1*math.sin(x*5+math.sin(z*4))}[key]
        fs=[tile(height,color='l1Ochre' if key in ('dune','ripple') else 'soil' if key in ('furrow','rutted','dried') else 'stone')]
        if key=='dried':fs += [rod([-.8,.26,z],[.8,.26,z+.16],.009,'woodDark',sides=5) for z in [-.6,-.1,.4]]
        if key=='scree':fs += [ico([.16,.12,.22],'stoneDark',[x,.45+x*.1,z],detail=0) for x,z in [(-.7,-.5),(.3,-.6),(.7,.3),(-.3,.4)]]
        put('surface',key,name,fs,[2,.8,2],detail=list(range(1,len(fs))) or None)
    cliffs=names('columnar:柱状岩壁剖面 layered:层理岩壁剖面 overhang:悬挑岩檐剖面 buttress:岩壁扶壁剖面 notch:凹槽岩壁剖面 ramp:倾斜岩壁剖面 talus:崖脚堆积剖面 pinnacle:孤岩尖脊剖面 arch_foot:天然拱脚剖面 ice:冰崖断面块')
    for key,name in cliffs:
        if key=='columnar':fs=[loft([[x,0,0,.19,.24],[x,1.1+(i%3)*.17,0,.16,.20]],'stone',6) for i,x in enumerate([-.8,-.4,0,.4,.8])]
        elif key=='layered':fs=[formbox(2-.09*i,.24,1-.07*(i%2),'stone' if i%2 else 'stoneDark',y=i*.25,x=.07*(i%2)) for i in range(6)]
        elif key=='overhang':fs=[bank([[-1,.4],[-.2,.7],[.1,1.35],[1,1.6]],length=1.0)]
        elif key=='buttress':fs=[bank([[-1,.2],[-.55,.8],[-.25,1.6],[.12,1.6],[.55,.6],[1,.3]],length=1.2)]
        elif key=='notch':fs=[bank([[-1,1.5],[-.45,1.55],[-.2,.4],[.2,.4],[.45,1.45],[1,1.5]],length=1.0)]
        elif key=='ramp':fs=[bank([[-1,.15],[1,1.6]],length=1.2)]
        elif key=='talus':fs=[bank([[-1,.4],[-.5,.5],[.15,1.3],[1,1.7]],length=1.2)]+[ico([.45,.38,.36],'stoneDark',[x,.18,.7],detail=0) for x in [-.65,.05,.72]]
        elif key=='pinnacle':fs=[loft([[0,0,0,.7,.45],[.12,.7,.04,.36,.28],[-.03,1.7,.05,.06,.08]],'stone',7)]
        elif key=='arch_foot':fs=[bank([[-1,1.5],[-.35,1.35],[-.22,.78],[.3,.3],[1,.14]],length=1)]
        else:fs=[loft([[x,0,0,.3,.4],[x+.07,1.2+i*.06,.1,.25,.35]],'l1Ivory',5) for i,x in enumerate([-.65,0,.65])]
        put('cliff',key,name,fs,[2,1.8,1.8])
    edges=names('straight:直线岸坡接边 concave:内弯岸坡接边 convex:外弯岸坡接边 split:分汊岸坡接边 stair:梯阶驳岸接边 riprap:块石护岸接边 beach:沙滩坡脚接边 marsh:湿地草岸接边 snow:雪檐接边 root:根系护岸接边')
    for key,name in edges:
        if key in ('concave','convex'):
            fs=[arc(.8,.19,0,90,axis='xz',color='soil',n=8,center=[-.6,.25,-.6])]
            if key=='convex':fs=placed(fs,rotation=[0,180,0])+[tile(lambda x,z:.20*max(0,1-(x*x+z*z)),width=1.4,depth=1.4,color='soil')]
        elif key=='split':fs=[rod([0,.25,-1],[-.8,.25,1],.22,'soil',sides=6),rod([0,.25,-1],[.8,.25,1],.22,'soil',sides=6)]
        elif key=='stair':fs=[formbox(2,.13,1-.27*i,'stone',y=i*.13,z=-.135*i) for i in range(3)]
        else:
            fs=[bank([[-1,.08],[-.45,.11],[0,.25],[.35,.42],[1,.42]],length=2,color='soil' if key!='snow' else 'l1Ivory')]
            if key=='riprap':fs += [ico([.34,.22,.38],'stone',[x,.44,z],detail=0) for x,z in [(.2,-.6),(.4,0),(.24,.65)]]
            if key=='marsh':fs += [rod([.4,.42,z],[.45,.7,z],.018,'l1Leaf') for z in [-.7,-.35,0,.35,.7]]
            if key=='root':fs += [rod([.8,.44,z],[-.4,.14,z+.15],.055,'wood',r2=.014) for z in [-.6,0,.6]]
            if key=='snow':fs += [loft([[.28,.42,z,.1,.09],[.18,.1,z,.012,.015]],'l1Ivory',6) for z in [-.6,.05,.5]]
            if key=='beach':fs=[tile(lambda x,z:.10+.1*(x+1),width=2,depth=2,color='l1Ochre')]
        put('edge',key,name,fs,[2,.8,2],detail=list(range(1,len(fs))) or None)
    waters=names('rill:浅溪河床剖面 river:宽河河床剖面 fork:分汊河床剖面 pool:潭底剖面 cascade:跌水台阶剖面 sluice:泄水渠剖面 culvert:涵洞河床剖面 spring:泉眼凹床剖面')
    for key,name in waters:
        if key=='pool':fs=[tile(lambda x,z:.4*min(1,(x*x+z*z)*.7),color='stone')]
        elif key=='spring':fs=[ring(.65,.16,.2,'stone',position=[0,.18,0]),disk(.48,.08,'stoneDark')]
        elif key=='cascade':fs=[formbox(1.4,.12,1.7-.4*i,'stone',y=i*.15,z=-i*.2) for i in range(4)]
        elif key=='culvert':fs=[round_tube(.58,.45,1.8,'stone',12,rotation=[90,0,0],position=[0,.57,.9])]
        elif key=='fork':fs=[tile(lambda x,z:.25*min(1,abs(abs(x)-max(0,z)*.5)*3),color='soil')]
        else:
            w=.3 if key=='rill' else .6 if key=='river' else .42
            fs=[tile(lambda x,z:.30*min(1,max(0,abs(x)-w)*3),color='stone' if key=='sluice' else 'soil')]
            if key=='sluice':fs += [formbox(.10,.46,2,'stone',x=x) for x in [-.9,.9]]
        put('waterbed',key,name,fs,[2,.8,2])
    roads=names('crown:拱冠路面截块 camber:单向横坡路面截块 curb:侧石路面接块 median:分隔带基块 shoulder:硬路肩接块 gutter:排水路肩接块 ramp:路缘坡道块 tactile:盲道凸点基块 railbed:轨道道床基块 boardwalk:栈道铺板基块')
    for key,name in roads:
        if key=='crown':fs=[tile(lambda x,z:.1*(1-abs(x)),color='stoneDark')]
        elif key=='camber':fs=[tile(lambda x,z:.1*(1+x),color='stoneDark')]
        elif key=='curb':fs=[formbox(1.8,.12,1,'stoneDark'),formbox(.16,.3,1,'stone',x=.84)]
        elif key=='median':fs=[plate([[-.45,0],[.45,0],[.27,.45],[-.27,.45]],1.8,'stone')]
        elif key=='shoulder':fs=[formbox(1,.12,1.8,'stone'),formbox(.14,.18,1.8,'stoneDark',x=.47)]
        elif key=='gutter':fs=[tile(lambda x,z:.16*abs(x),width=1,depth=2,color='stone')]
        elif key=='ramp':fs=[tile(lambda x,z:.23*(z+1)/2,color='stone')]
        elif key=='tactile':fs=[formbox(1,.08,1,'l1Ochre')]+[disk(.037,.027,'l1Ochre',y=.08,position=[x,0,z]) for x in [-.3,-.15,0,.15,.3] for z in [-.3,-.15,0,.15,.3]]
        elif key=='railbed':fs=[plate([[-1,0],[1,0],[.72,.3],[-.72,.3]],2,'stoneDark')]+[formbox(1.6,.09,.14,'wood',y=.3,z=z) for z in [-.75,-.25,.25,.75]]
        else:fs=[formbox(.23,.12,1.8,'wood',x=x) for x in [-.78,-.52,-.26,0,.26,.52,.78]]
        put('road',key,name,fs,[2,.6,2],detail=list(range(1,len(fs))) if key=='tactile' else None)
    caves=names('stalactite:钟乳垂体岩芯 stalagmite:石笋上生岩芯 flowstone:流石壁片岩芯 rib:溶洞岩肋芯 ledge:洞壁岩台芯 fissure:洞壁裂隙芯')
    for key,name in caves:
        if key in ('stalactite','stalagmite'):
            fs=[loft([[0,0,0,.28,.24],[.02,.4,.01,.20,.18],[.06,1.1,0,.025,.025]],'l1Ivory',7)]
            if key=='stalactite':fs=placed(fs,[0,1.1,0],[180,0,0])+[loft([[.16,.4,.04,.009,.009],[.16,.9,.04,.08,.06],[.15,1.1,.04,.13,.1]],'l1Ivory',6)]
        elif key=='flowstone':fs=[loft([[x,0,0,.12,.14],[x+.02,.6,-.1,.11,.10],[x,1.2,-.14,.08,.07]],'stone',7) for x in [-.4,-.2,0,.2,.4]]
        elif key=='rib':fs=[arc(.7,.13,0,180,color='stone',n=10)]
        elif key=='ledge':fs=[bank([[-1,.45],[-.5,.52],[.4,.45],[1,.3]],length=.8)]
        else:fs=[bank([[-1,.8],[-.15,.85],[-.03,.12],[.1,.7],[1,.75]],length=.75)]
        put('cave',key,name,fs,[2,1.4,1.2])
    finish('terrain',58)
