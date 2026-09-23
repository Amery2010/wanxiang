"""Anatomical attachments, not complete creatures or skinned rigs."""
from .common import *


def author():
    def put(g,k,n,fs,sz=(.8,.9,.65),**kw):return register('creature',g,k,n,fs,sz,collision='none',**kw)
    horns=names('antler:分叉鹿角枝 ram:盘卷羊角片 ibex:后弯长角片 rhino:角质鼻角芯 pronghorn:叉尖羚角片 frill:骨质颈盾片')
    for key,name in horns:
        if key=='antler':fs=[loft([[0,0,0,.075,.065],[.08,.35,0,.06,.05],[.12,.65,.05,.03,.025],[.27,.85,.04,.009,.008]],'l1Ivory',7)]+[rod([.07,y,0],[x,y+.2,z],.035,'l1Ivory',r2=.006,sides=6) for x,y,z in [(-.18,.22,.08),(.3,.4,-.12),(-.10,.55,.02)]]
        elif key=='ram':fs=[loft([[.23*math.cos(a),.28+.23*math.sin(a),j*.007,.075*(1-j/38)+.008,.06*(1-j/38)+.006] for j,a in enumerate([i*math.tau/36 for i in range(34)])],'l1Ivory',8)]
        elif key=='ibex':fs=[loft([[0,0,0,.09,.07],[0,.4,-.08,.075,.06],[.04,.75,-.3,.045,.036],[.03,.82,-.55,.008,.01]],'l1Ivory',8)]+[ring(.07,.018,.025,'woodLight',rotation=[-20,0,0],position=[0,y,-.08]) for y in [.3,.4,.5]]
        elif key=='rhino':fs=[loft([[0,0,0,.15,.14],[0,.22,.01,.095,.09],[0,.46,.10,.01,.01]],'woodLight',8)]
        elif key=='pronghorn':fs=[loft([[0,0,0,.055,.05],[.04,.4,0,.045,.03],[-.04,.65,.04,.008,.008]],'woodDark',7),rod([.02,.33,0],[.18,.46,.02],.042,'woodDark',r2=.007)]
        else:fs=[lens([[-.45,0],[-.48,.3],[-.32,.58],[-.1,.65],[0,.58],[.1,.65],[.32,.58],[.48,.3],[.45,0]],'woodLight',.05,.10)]
        put('horn',key,name,fs)
    ears=names('feline:猫科耳廓片 canine:犬科耳廓片 lagomorph:兔形长耳片 ungulate:有蹄类耳廓片')
    for key,name in ears:
        outline={'feline':[[-.13,0],[.12,0],[.055,.28],[-.02,.36]],'canine':[[-.10,0],[.13,0],[.17,.25],[.01,.40],[-.13,.24]],'lagomorph':[[-.07,0],[.08,0],[.10,.46],[.03,.62],[-.07,.51],[-.1,.20]],'ungulate':[[0,0],[.15,.12],[.19,.29],[.12,.39],[-.03,.32],[-.1,.15]]}[key]
        fs=[lens(outline,'woodLight',.03,.03),lens([[x*.65,y*.75+.045] for x,y in outline],'skinShade',.012,.02)]
        fs[1]['position']=[0,0,.025]
        put('ear',key,name,fs,(.45,.7,.2))
    feet=names('cloven:偶蹄足端芯 paw:肉垫足端芯 talon:猛禽趾爪芯 webbed:蹼足足端芯')
    for key,name in feet:
        if key=='cloven':fs=[loft([[x,0,.04,.065,.12],[x,.15,0,.065,.09]],'woodDark',6) for x in [-.075,.075]]
        elif key=='paw':fs=[ico([.25,.12,.28],'woodLight',[0,.08,0],detail=1)]+[ico([.075,.09,.10],'woodDark',[x,.07,.14],detail=1) for x in [-.085,-.028,.028,.085]]
        elif key=='talon':fs=[loft([[0,.1,0,.05,.045],[x,.02,.2,.035,.03],[x,.08,.29,.008,.008]],'woodLight',6) for x in [-.11,0,.11]]
        else:fs=[plate([[0,-.12],[-.17,.18],[-.05,.10],[0,.26],[.06,.11],[.17,.18]],.035,'l1Ochre',rotation=[90,0,0])]+[rod([0,.035,-.1],[x,.035,.18],.014,'woodLight',r2=.008) for x in [-.15,0,.15]]
        put('foot',key,name,fs,(.5,.3,.65))
    mouths=names('beak_hook:钩喙上颚芯 beak_filter:滤食扁喙芯 tusk:弯曲獠牙芯 mandible:节肢口器芯')
    for key,name in mouths:
        if key=='beak_hook':fs=[loft([[0,0,0,.12,.09],[0,.10,.15,.09,.08],[0,.06,.3,.02,.025],[0,-.02,.28,.008,.008]],'l1Ochre',7)]
        elif key=='beak_filter':fs=[loft([[0,0,0,.095,.055],[0,.02,.18,.15,.035],[0,.01,.35,.12,.02]],'l1Ochre',8)]
        elif key=='tusk':fs=[loft([[0,0,0,.065,.055],[.02,.28,.06,.045,.035],[.04,.48,.2,.006,.007]],'l1Ivory',8)]
        else:fs=[plate([[-.06,0],[.07,0],[.16,.2],[.08,.37],[.02,.39],[.06,.24],[.02,.18],[-.08,.20]],.05,'woodDark')]
        put('mouth',key,name,fs,(.4,.6,.6))
    wings=names('primary_feather:主飞羽单片 bat_membrane:翼膜分片 insect_elytron:鞘翅单片 fin_ray:鳍条膜片')
    for key,name in wings:
        if key=='primary_feather':fs=[lens([[0,0],[.10,.3],[.09,.68],[.02,.9],[-.045,.72],[-.055,.26]],'l1Ivory',.018,.025),rod([0,0,0],[.01,.84,.018],.008,'woodLight',r2=.004,sides=5)]
        elif key=='bat_membrane':fs=[lens([[0,0],[-.4,.58],[-.15,.43],[0,.7],[.15,.43],[.4,.58]],'woodDark',.022,.02)]+[rod([0,0,0],[x,.58,0],.018,'wood',r2=.008) for x in [-.4,.4]]
        elif key=='insect_elytron':fs=[lens([[-.03,0],[.18,.15],[.24,.48],[.15,.74],[-.07,.82],[-.13,.55],[-.12,.2]],'l1LeafDark',.075,.025)]
        else:fs=[lens([[0,0],[-.32,.43],[-.16,.55],[0,.58],[.16,.55],[.32,.43]],'l1Petal',.012,.02)]+[rod([0,0,0],[x,.55-abs(x)*.35,.014],.01,'l1Ivory',r2=.004,sides=5) for x in [-.28,-.14,0,.14,.28]]
        put('wing',key,name,fs,(.9,1,.3))
    finish('creature',22)
