"""Unrigged character surface/garment modules with explicit ownership limits."""
from .common import *


def author():
    def put(g,k,n,fs,sz=(.6,.7,.5),**kw):return register('character',g,k,n,fs,sz,collision='none',**kw)
    hair=names('fringe:层叠额发片 side_lock:鬓角发束 braid:编辫发段 bun:盘发发髻芯 ponytail:马尾发束 crest:竖冠发片 curl:卷曲发束 bob:短发后片')
    for key,name in hair:
        if key=='fringe':fs=[loft([[x,.25,0,.08,.06],[x+.025,.12,.055,.075,.04],[x-.025,0,.07,.012,.016]],'hair',6) for x in [-.18,-.09,0,.09,.18]]
        elif key=='side_lock':fs=[loft([[0,.5,0,.09,.065],[.02,.25,.02,.07,.055],[-.05,0,.08,.018,.02]],'hair',7)]
        elif key=='braid':fs=[loft([[.045*math.cos(j*.75+a),j*.022,.04*math.sin(j*.75+a),.038,.035] for j in range(25)],'hair' if i%2 else 'hairLight',6) for i,a in enumerate([0,math.tau/3,math.tau*2/3])]
        elif key=='bun':fs=[ico([.30,.25,.20],'hair',[0,.14,0],detail=1),arc(.13,.028,15,330,color='hairLight',center=[0,.14,.09],n=16)]
        elif key=='ponytail':fs=[loft([[0,.6,0,.075,.075],[.07,.42,-.02,.115,.075],[.10,.15,.035,.085,.045],[.04,0,.08,.016,.012]],'hair',8),ring(.084,.015,.055,'l1Slate',position=[0,.55,0])]
        elif key=='crest':fs=[plate([[-.12,0],[.15,0],[.15,.45],[.04,.66],[-.12,.48]],.075,'hair'),plate([[-.09,0],[.10,0],[.07,.46],[-.08,.51]],.10,'hairLight',position=[0,0,-.06])]
        elif key=='curl':fs=[loft([[.1*math.cos(j*.22),j*.012,.07*math.sin(j*.22),.035,.035] for j in range(38)],'hair',7)]
        else:fs=[loft([[0,.02,0,.23,.10],[0,.2,-.01,.26,.12],[0,.4,.02,.19,.09]],'hair',8)]
        put('hair',key,name,fs,material='mat.fabric')
    face=names('brow:眉弓覆盖片 eyelid:眼睑边片 nose:鼻梁面片 ear:耳廓面片 moustache:上唇胡须片 beard:下颌胡须片 mask:半脸面罩片 jaw:下颌轮廓片')
    for key,name in face:
        if key=='brow':fs=[loft([[-.1,0,0,.016,.02],[0,.03,.018,.023,.022],[.1,.005,0,.012,.014]],'hair',6)]
        elif key=='eyelid':fs=[arc(.075,.012,10,170,color='skin',n=9),arc(.075,.008,190,350,color='skinShade',n=9)]
        elif key=='nose':fs=[topo([[-.04,0,0],[.04,0,0],[.022,.18,0],[-.022,.18,0],[0,.04,.09],[0,.15,.035]],[[0,1,2,3],[0,4,1],[0,3,5,4],[1,4,5,2],[2,5,3]],'skin')]
        elif key=='ear':fs=[lens([[0,0],[.07,.03],[.09,.15],[.04,.22],[-.03,.19],[-.04,.06]],'skin',.018,.03),ico([.065,.095,.025],'skinShade',[.02,.12,.027],detail=1)]
        elif key=='moustache':fs=[loft([[0,.07,0,.028,.027],[x*.5,.04,.02,.035,.025],[x,0,.01,.006,.008]],'hair',6) for x in [-.13,.13]]
        elif key=='beard':fs=[loft([[0,0,.04,.04,.026],[0,.1,.03,.14,.06],[0,.23,0,.16,.07]],'hair',7)]
        elif key=='mask':fs=[loft([[0,0,0,.08,.025],[0,.14,.035,.16,.05],[0,.2,0,.15,.022]],'l1Slate',8)]
        else:fs=[loft([[0,0,0,.065,.06],[0,.055,.01,.13,.075],[0,.15,-.005,.16,.065]],'skin',8)]
        put('face',key,name,fs,(.4,.35,.25))
    clothing=names('collar_stand:立领衣片 collar_lapel:翻领衣片 cuff:袖口衣片 sleeve_cap:袖山衣片 hood:兜帽后片 cape_panel:披风分片 skirt_panel:裙摆分片 belt:腰带环片 pocket:贴袋衣片 sash:斜襟绶带片')
    for key,name in clothing:
        if key=='collar_stand':fs=[round_tube(.16,.135,.12,'l1Ivory',12)]
        elif key=='collar_lapel':fs=[plate([[-.2,.25],[.05,0],[.18,.28],[.05,.2],[0,.32]],.024,'l1Slate')]
        elif key=='cuff':fs=[round_tube(.09,.07,.13,'l1Ivory',10),plate([[-.035,0],[.035,0],[.035,.10],[-.035,.10]],.018,'l1Slate',position=[.08,.01,0],rotation=[0,90,0])]
        elif key=='sleeve_cap':fs=[loft([[0,0,0,.16,.10],[0,.13,0,.18,.13],[0,.28,0,.085,.065]],'l1Slate',8)]
        elif key=='hood':fs=[loft([[0,0,0,.15,.08],[0,.18,-.04,.22,.12],[0,.38,-.04,.18,.12],[0,.48,0,.07,.06]],'l1Slate',10)]
        elif key=='cape_panel':fs=[lens([[-.38,0],[-.14,.65],[.12,.7],[.4,0],[.15,.05],[-.15,-.015]],'l1Slate',.025,.10)]
        elif key=='skirt_panel':fs=[plate([[-.35,0],[.35,0],[.18,.6],[-.18,.6]],.035,'l1Ivory')]+[rod([x,0,.022],[x*.5,.58,.022],.01,'cream') for x in [-.2,0,.2]]
        elif key=='belt':fs=[round_tube(.25,.225,.065,'woodDark',12,scale=[1,1,.65]),formbox(.08,.06,.025,'copper',y=.005,z=.168)]
        elif key=='pocket':fs=[plate([[-.10,.16],[.1,.16],[.1,.03],[.05,0],[-.05,0],[-.1,.03]],.028,'l1Slate'),formbox(.20,.025,.035,'l1Ivory',y=.145)]
        else:fs=[plate([[-.23,0],[-.10,0],[.26,.65],[.13,.65]],.03,'l1Terracotta'),formbox(.14,.10,.06,'l1Ivory',x=-.15,y=.01)]
        put('clothing',key,name,fs,material='mat.fabric')
    armor=names('pauldron:肩甲壳片 vambrace:前臂护甲片 greave:胫甲壳片 breastplate:胸甲外片 fauld:腰甲分片 helmet_visor:头盔面甲片')
    for key,name in armor:
        if key=='pauldron':fs=[loft([[0,0,0,.20,.14],[0,.14,0,.23,.17],[0,.25,0,.1,.08]],'l1Metal',8)]+[box([.22,.025,.06],'copper',[0,y,.14],.01) for y in [.03,.10]]
        elif key=='vambrace':fs=[lathe([[.10,0],[.13,.32],[.10,.32],[.075,0]],'l1Metal',8,closed_profile=True)]
        elif key=='greave':fs=[loft([[0,0,0,.08,.05],[0,.22,.02,.12,.08],[0,.47,0,.1,.07]],'l1Metal',7)]
        elif key=='breastplate':fs=[loft([[0,0,0,.18,.065],[0,.3,.02,.26,.11],[0,.5,0,.2,.06]],'l1Metal',8),rod([0,.03,.075],[0,.43,.09],.018,'copper')]
        elif key=='fauld':fs=[plate([[-.23,0],[.23,0],[.17,.2],[-.17,.2]],.045,'l1Metal')]+[disk(.015,.008,'copper',rotation=[90,0,0],position=[x,.15,.027]) for x in [-.13,.13]]
        else:fs=[loft([[0,0,0,.13,.08],[0,.14,.03,.17,.10],[0,.28,0,.17,.075]],'l1Metal',8)]+[box([.07,.014,.015],'ink',[x,.19,.112],.002) for x in [-.06,.06]]
        put('armor',key,name,fs,material='mat.metal')
    extremities=names('glove_palm:手套掌片 glove_fingers:并指手套片 boot_toe:靴头壳片 boot_sole:靴底片 sandal_strap:凉鞋带片 wrist_wrap:腕部绑带片')
    for key,name in extremities:
        if key=='glove_palm':fs=[loft([[0,0,0,.06,.035],[0,.11,.015,.085,.045],[0,.19,0,.07,.03]],'woodDark',8),loft([[-.07,.06,0,.025,.025],[-.11,.12,.01,.025,.022],[-.09,.17,.02,.012,.015]],'woodDark',6)]
        elif key=='glove_fingers':fs=[rod([x,0,0],[x,.14-abs(x)*.5,.025],.018,'woodDark',r2=.013,sides=6) for x in [-.06,-.02,.02,.06]]
        elif key=='boot_toe':fs=[loft([[0,0,0,.07,.12],[0,.075,.02,.1,.15],[0,.13,-.005,.065,.10]],'woodDark',8)]
        elif key=='boot_sole':fs=[plate([[-.08,-.18],[.08,-.18],[.10,.12],[.07,.19],[-.07,.19],[-.10,.12]],.045,'l1Rubber',rotation=[90,0,0])]+[box([.15,.025,.03],'rubber',[0,.03,z]) for z in [-.1,0,.1]]
        elif key=='sandal_strap':fs=[arc(.09,.022,0,180,color='wood',n=8),arc(.09,.022,0,180,color='wood',n=8,center=[0,0,-.12]),rod([0,.09,0],[0,.09,-.12],.02,'wood')]
        else:fs=[ring(.07,.018,.035,'l1Ivory',position=[0,y,0]) for y in [.02,.056,.092]]+[plate([[-.02,0],[.025,0],[.02,.12],[-.025,.11]],.024,'cream',position=[0,0,.076])]
        put('handfoot',key,name,fs,(.3,.3,.5),material='mat.fabric')
    finish('character',38)
