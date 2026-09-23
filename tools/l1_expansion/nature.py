"""133 botanical building blocks. No whole-tree assets or colour-only species."""
from .common import *


def leaf(key,sz=(.32,.56,.035)):
    forms=[]
    base={'lance':'lanceolate','heart':'cordate','maple':'lobed','oak':'lobed','ginkgo':'fan',
          'needle':'needle','strap':'strap','arrow':'triangular','spear':'spade','holly':'serrate',
          'lotus':'ovate','banana':'lanceolate','palmlet':'strap','succulent':'ovate','aloe':'triangular'}.get(key,key)
    if key in ('clover','trifoliate','compound'):
        for i in range(3 if key!='compound' else 7):
            a=(i*120-20 if key!='compound' else (-55 if i%2 else 55))
            fs=[lens(leaf_outline('cordate' if key=='clover' else 'ovate'),'l1Leaf',.035)]
            forms+=placed(fs,[0,.34 if key!='compound' else .12+i*.115,0],[0,0,a],scale=[.4,.4,.7])
        forms += [rod([0,0,0],[0,.85,0],.018,'l1LeafDark')]
    elif key in ('pine_pair','conifer_spray','fern','scale'):
        for i in range(8 if key in ('fern','conifer_spray') else 4 if key=='scale' else 2):
            y=.12+i*.10 if key!='pine_pair' else .05
            for s in [-1,1]:
                end=[s*(.30-.02*i),y+.2,0]
                forms.append(rod([0,y,0],end,.018 if key!='scale' else .05,'l1Leaf',r2=.007,sides=5))
        forms.append(rod([0,0,0],[0,.98,0],.02,'l1LeafDark'))
    elif key=='fan':
        for a in range(-70,71,20):forms+=placed([lens(leaf_outline('strap'),'l1Leaf',.025)],[0,0,0],[0,0,a],scale=[.8,1,1])
    else:
        outline=leaf_outline(base,24 if key=='holly' else 16)
        if key=='oak':outline=[[x*(.85+.18*math.sin(y*math.pi*6)),y] for x,y in outline]
        if key=='maple':
            # Five readable palmate lobes, not an oval with a wavy perimeter.
            right=[[0,.05],[.10,.22],[.38,.16],[.32,.35],[.55,.38],[.40,.53],[.56,.75],[.31,.67],[.29,.92],[.14,.77],[0,1.08]]
            outline=right+[[-x,y] for x,y in reversed(right[1:-1])]
        if key=='ginkgo':
            # Basal fan with a central apical notch and radial venation.
            outline=[[0,.03],[.16,.28]]
            for a in range(60,-61,-10):
                theta=math.radians(a)
                outline.append([.88*math.sin(theta),.13+.88*math.cos(theta)-(.13 if a==0 else 0)])
            outline.append([-.16,.28])
        if key=='lotus':outline=[[x*1.3,.5+(y-.5)*.75] for x,y in outline]
        forms=[lens(outline,'l1Leaf',.12 if key=='succulent' else .055 if key=='aloe' else .028)]
        if key=='ginkgo':
            forms.append(rod([0,-.10,.025],[0,.17,.026],.015,'l1LeafDark',r2=.01,sides=5))
            for a in [-54,-36,-18,18,36,54]:
                t=math.radians(a)
                forms.append(rod([0,.15,.041],[.79*math.sin(t),.13+.79*math.cos(t),.049],.006,'l1LeafDark',r2=.003,sides=4))
            sz=(.42,.45,sz[2])
        elif key=='maple':
            forms.append(rod([0,-.12,.025],[0,1.00,.045],.013,'l1LeafDark',r2=.004,sides=5))
            for s in [-1,1]:
                for end in [[s*.49,.69,.04],[s*.46,.37,.04]]:
                    forms.append(rod([0,.32,.035],end,.008,'l1LeafDark',r2=.003,sides=4))
            sz=(.43,.48,sz[2])
        else:
            forms.append(rod([0,.02,.04],[0,.88,.04],.012,'l1LeafDark',r2=.004,sides=5))
            for y in [.24,.42,.6,.76]:
                for s in [-1,1]:forms.append(rod([0,y,.045],[s*.22*(1-abs(y-.5)),y+.1,.047],.004,'l1LeafDark',sides=4))
    return placed(forms,scale=sz)


def author():
    def put(group,key,name,fs,size,**kw):return register('nature',group,key,name,fs,size,
        collision='none',material='mat.leaf',**kw)
    leaves=names('ovate:卵形叶片 lance:披针叶片 heart:心形叶片 maple:掌状裂叶片 oak:羽裂波缘叶片 ginkgo:缺刻扇形叶片 needle:针状叶片 scale:覆鳞叶片 strap:带状叶片 fan:折扇叶片 arrow:箭形叶片 spear:匙形叶片 clover:三瓣心形复叶 fern:羽状小叶轴 holly:刺齿叶片 lotus:盾状圆叶片 banana:展宽长叶片 palmlet:狭长羽片 succulent:肉质厚叶片 aloe:肉质剑叶片 pine_pair:束生针叶基件 conifer_spray:鳞针侧枝叶组 compound:羽状复叶基件 trifoliate:三出复叶基件')
    for key,name in leaves:
        fs=leaf(key);put('leaf',key,name,fs,[.45,.60,.10],detail=list(range(3,len(fs))) if len(fs)>6 else None,
            description=name+'；保留厚度与主脉，作为树冠或作物配方中的叶形基件。')
    branches=names('y_fork:Y形枝杈 t_fork:T形枝杈 whorl:轮生枝杈 elbow:转折树枝 arch:拱垂枝段 drooping:下垂侧枝 thorn:带刺枝段 twig:短节芽枝 bamboo_node:竹节杆段 cane:弯曲藤杆 segment:环节木质杆 hollow:空心枯枝段 broken:断口侧枝 braced:支撑分枝 spiral:螺旋攀藤扭段 tendril:卷须末梢')
    for key,name in branches:
        fs=[]
        if key in ('hollow','bamboo_node'):
            fs=[round_tube(.09,.058,.75,'wood',10)]
            if key=='bamboo_node':fs += [disk(.107,.05,'l1LeafDark',y=.3),disk(.103,.025,'l1LeafDark',y=.65)]
        elif key in ('spiral','tendril'):
            n=18;pts=[]
            for j in range(n+1):
                a=j*math.tau/(9 if key=='spiral' else 18);r=.14 if key=='spiral' else .19*(1-j/(n+2))
                pts.append([r*math.cos(a),j*.7/n,r*math.sin(a),.025,.025])
            fs=[loft(pts,'wood' if key=='spiral' else 'l1LeafDark',6)]
        else:
            paths={'y_fork':[[0,0,0],[0,.45,0],[.3,.8,.02]],'t_fork':[[0,0,0],[0,.45,0],[.35,.5,0]],'elbow':[[0,0,0],[0,.38,0],[.35,.65,.03]],'arch':[[-.3,0,0],[-.28,.5,0],[0,.75,0],[.28,.5,0],[.3,.12,0]],'drooping':[[0,0,0],[.05,.55,0],[.26,.65,.05],[.39,.24,.08]],'cane':[[0,0,0],[.06,.25,0],[-.06,.55,.04],[.1,.9,.03]],'segment':[[0,0,0],[.02,.85,0]],'broken':[[0,0,0],[.06,.58,0]],'braced':[[0,0,0],[0,.85,0]],'thorn':[[0,0,0],[.03,.85,0]],'twig':[[0,0,0],[.05,.85,0]],'whorl':[[0,0,0],[0,.9,0]]}
            path=paths[key];fs=[loft([p+[.065*(1-i/(len(path)+1)),.060*(1-i/(len(path)+1))] for i,p in enumerate(path)],'wood',8)]
            if key in ('y_fork','t_fork'):fs += [rod([0,.4,0],[-.3,.8 if key=='y_fork' else .5,.02],.047,'wood',r2=.018)]
            if key=='whorl':fs += [rod([0,.55,0],[.33*math.cos(a),.79,.33*math.sin(a)],.035,'wood',r2=.012) for a in [i*math.tau/5 for i in range(5)]]
            if key=='braced':fs += [rod([0,.27,0],[.32,.75,0],.035,'wood'),rod([0,.72,0],[.32,.75,0],.025,'wood')]
            if key=='thorn':fs += [rod([0,y,0],[s*.12,y+.1,.02],.032,'woodDark',r2=.006,sides=5) for y,s in [(.18,1),(.37,-1),(.58,1),(.76,-1)]]
            if key=='twig':fs += [ico([.08,.13,.08],'l1Leaf',[s*.06,y,0],detail=0) for y,s in [(.22,1),(.46,-1),(.71,1)]]
            if key=='broken':fs += [rod([.06,.52,0],[x,.72,z],.021,'woodLight',r2=.006) for x,z in [(.03,.025),(.07,-.02),(.09,.01)]]
            if key=='segment':fs += [disk(.079,.025,'woodDark',y=y) for y in [.18,.4,.65]]
        put('branch',key,name,fs,[.8,1,.8],detail=list(range(2,len(fs))) if len(fs)>3 else None)
    bark=names('furrow:纵沟树皮片 plate:鳞片树皮片 peeling:卷边薄树皮 knot:瘤结树皮片 fissure:裂缝树皮片 diamond:菱裂树皮片 cork:软木块树皮片 lenticel:横纹树皮片 scar:伤痕树皮片 moss_collar:苔藓抱干片 burn:炭化裂皮片 scale_ring:环纹茎皮片')
    for key,name in bark:
        fs=[box([.4,.7,.065],'woodDark',[0,.35,0],.015)]
        if key in ('furrow','fissure','burn'):
            paths=3 if key=='furrow' else 4 if key=='fissure' else 5
            fs += [rod([-.15+i*.3/(paths-1),.03,.045],[(-.15+i*.3/(paths-1))+(0 if key=='furrow' else .035),.67,.045],.028 if key!='burn' else .018,'wood' if key!='burn' else 'coal',sides=5) for i in range(paths)]
        elif key in ('plate','diamond','cork'):
            for j in range(3):
                for i in range(2):fs.append(box([.17,.18,.07],'wood',[(-.10 if i==0 else .10)+(.015 if j%2 else 0),.13+j*.23,.044],.025,rotation=[0,0,45 if key=='diamond' else 0]))
            if key=='cork':fs += [ico([.16,.17,.10],'woodLight',[0,.39,.085],detail=0)]
        elif key=='peeling':fs += [plate([[-.18,0],[.18,0],[.18,.58],[.06,.68],[-.10,.62]],.025,'woodLight',rotation=[-18,0,0],position=[0,.06,.065])]
        elif key in ('knot','scar'):
            fs += [arc(.11,.026,0,350,'xy','wood',12,[0,.38,.06])]
            fs += [ico([.16,.19,.13],'woodLight',[0,.38,.09],detail=0)] if key=='knot' else [rod([-.035,.27,.075],[.04,.5,.075],.018,'woodDark')]
        elif key=='moss_collar':fs += [ico([.18,.17,.09],'l1Leaf',[x,y,.07],detail=0) for x,y in [(-.1,.17),(.1,.21),(-.06,.4),(.07,.57)]]
        else:fs += [box([.16 if key=='lenticel' else .4,.016,.035],'woodLight',[.05*(-1 if i%2 else 1),.10+i*.09,.05],.002) for i in range(6)]
        put('bark',key,name,fs,[.45,.75,.2],detail=list(range(2,len(fs))) if len(fs)>4 else None)
    roots=names('buttress:板状根基件 prop:支柱根基件 aerial:气生根束基件 tap:主根基件 fibrous:须根冠基件 exposed:露地盘根基件 pneumatophore:呼吸根基件 mangrove:拱根基件 tuber:块根基件 clinging:攀附根基件')
    for key,name in roots:
        if key=='buttress':fs=[plate([[-.4,0],[.4,0],[.08,.82],[-.08,.85]],.13,'wood',rotation=[0,24,0])]
        elif key=='tuber':fs=[loft([[0,0,0,.05,.05],[.02,.15,0,.24,.19],[0,.4,.02,.22,.2],[0,.64,0,.08,.07]],'wood',9)]
        else:
            paths=[]
            if key=='tap':paths=[[[0,.85,0],[0,.4,0],[.04,.03,0]],[[0,.5,0],[.27,.1,.08]],[[0,.4,0],[-.23,.12,-.1]]]
            elif key=='exposed':paths=[[[0,.5,0],[.18,.12,.08],[.55,.05,.1]],[[0,.4,0],[-.28,.07,-.08],[-.55,.03,-.12]]]
            elif key in ('prop','mangrove'):paths=[[[0,.85,0],[s*.18,.55,0],[s*.35,.03,s*.12]] for s in [-1,1]]
            elif key=='pneumatophore':paths=[[[x,0,0],[x+.025,.35+(i%2)*.2,0]] for i,x in enumerate([-.3,-.15,0,.15,.3])]
            elif key=='clinging':paths=[[[0,.8,0],[0,.06,0]]]+[[[0,y,0],[s*.2,y-.05,.10]] for y,s in [(.18,1),(.33,-1),(.52,1),(.71,-1)]]
            else:paths=[[[.1*math.cos(a),.82,.1*math.sin(a)],[.2*math.cos(a),.4,.2*math.sin(a)],[.28*math.cos(a),.02,.28*math.sin(a)]] for a in [i*math.tau/(7 if key=='fibrous' else 5) for i in range(7 if key=='fibrous' else 5)]]
            fs=[loft([p+[max(.011,.07*(1-i/(len(path)+.4))),max(.011,.07*(1-i/(len(path)+.4)))] for i,p in enumerate(path)],'wood',7) for path in paths]
        put('root',key,name,fs,[1.15,.95,.8])
    fronds=names('pinnate:羽状蕨叶枝 bipinnate:二回羽状蕨叶枝 tripinnate:多回细裂蕨叶枝 palmate:掌状棕榈叶枝 fishtail:鱼尾棕榈羽枝 comb:梳齿叶枝 cycad:硬质羽叶枝 droop:下垂羽叶枝 curled:卷曲幼叶枝 fan_rib:扇叶骨架枝 grass_blade:折面草叶枝 reed_leaf:芦苇长叶枝')
    for key,name in fronds:
        if key=='curled':fs=[arc(.19,.018,-100,210,'xy','l1Leaf',16,[0,.65,0]),rod([-.03,0,0],[-.03,.48,0],.024,'l1LeafDark')]
        elif key in ('grass_blade','reed_leaf'):
            fs=[loft([[0,0,0,.035,.018],[.05,.35,.02,.05,.018],[.12,.7,.04,.028,.013],[.20,.95,.12,.005,.004]],'l1Leaf',5)]
            if key=='reed_leaf':fs += [lens([[-.05,0],[.14,.33],[.32,.6],[.19,.55],[0,.12]],'l1Leaf',.025)]
        elif key in ('palmate','fan_rib'):
            fs=[]
            for a in range(-75,76,25):fs += placed([lens(leaf_outline('strap'),'l1Leaf',.03) if key=='palmate' else rod([0,0,0],[0,1,0],.02,'l1LeafDark',r2=.006)],[0,.05,0],[0,0,a],scale=[1,.85,1])
        else:
            fs=[rod([0,0,0],[0,1,0],.024,'l1LeafDark',r2=.008)]
            n={'pinnate':7,'bipinnate':6,'tripinnate':5,'fishtail':5,'comb':9,'cycad':8,'droop':6}[key]
            for j in range(n):
                y=.14+j*.8/n;length=.34*(1-j/(n+1))
                for s in [-1,1]:
                    end=[s*length,y+(.12 if key!='droop' else -.14),0]
                    fs.append(rod([0,y,0],end,.016,'l1Leaf',r2=.004,sides=5))
                    if key in ('bipinnate','tripinnate'):
                        for t in [.35,.7]:fs.append(rod([end[0]*t,y+.10*t,0],[end[0]*t+s*.06,y+.16*t,.012],.007,'l1Leaf',r2=.003,sides=4))
                        if key=='tripinnate':fs.append(ico([.04,.04,.026],'l1Leaf',[end[0],end[1],0],detail=0))
                    elif key=='fishtail':fs.append(lens([[0,y],[s*length,y+.06],[s*length,y+.2],[s*length*.45,y+.18]],'l1Leaf',.02))
                    elif key in ('pinnate','cycad','droop'):fs += placed([lens(leaf_outline('lanceolate'),'l1Leaf',.02)],[s*.01,y,0],[0,0,-s*65],scale=[.35,length,1])
        put('frond',key,name,fs,[1,1.1,.16],detail=list(range(5,len(fs),3)) if len(fs)>14 else None)
    flowers=names('daisy:放射舌瓣花冠 bell:钟形花冠 trumpet:喇叭形花冠 cup:杯形花冠 rosette:重瓣莲座花冠 star:星状花冠 orchid:唇瓣花冠 pea:蝶形花冠 umbrella:伞形花序基件 spike:穗状花序基件 cone:锥状花序基件 pompom:球状花序基件 catkin:下垂柔荑花序 bud:闭合花芽基件 sepal:萼片托基件 stamen:雄蕊簇基件')
    for key,name in flowers:
        fs=[]
        if key in ('bell','trumpet','cup'):
            prof={'bell':[[.055,0],[.12,.15],[.20,.38],[.28,.48],[.25,.48],[.17,.38],[.09,.15],[.035,0]],'trumpet':[[.045,0],[.06,.25],[.13,.45],[.32,.58],[.29,.58],[.1,.46],[.035,.25],[.023,0]],'cup':[[.065,0],[.17,.12],[.26,.35],[.26,.46],[.23,.46],[.22,.35],[.14,.12],[.04,0]]}[key]
            fs=[lathe(prof,'l1Petal',12,closed_profile=True)]
        elif key in ('spike','cone','catkin'):
            fs=[rod([0,0,0],[0,.8,0],.024,'l1LeafDark')]
            for j in range(7):
                for k in range(3):
                    a=k*math.tau/3+j*.6;r=.055 if key=='catkin' else .16*(1-j/9) if key=='cone' else .07
                    fs.append(ico([.12,.10,.10],'l1Petal',[r*math.cos(a),.12+j*.09,r*math.sin(a)],detail=0))
        elif key in ('bud','pompom'):
            fs=[ico([.28,.40,.28],'l1Petal',[0,.24,0],detail=1)]
            if key=='bud':fs += [placed([lens(leaf_outline('lanceolate'),'l1Leaf',.025)],[.08*math.sin(a),0,.08*math.cos(a)],[0,math.degrees(a),-20],scale=[.24,.4,.5])[0] for a in [i*math.tau/5 for i in range(5)]]
            else:fs += [ico([.13,.14,.13],'l1Petal',[.15*math.cos(a),.28+.05*math.sin(a*3),.15*math.sin(a)],detail=0) for a in [i*math.tau/9 for i in range(9)]]
        elif key=='stamen':
            for a in [i*math.tau/8 for i in range(8)]:
                p=[.15*math.cos(a),.4,.15*math.sin(a)];fs += [rod([0,0,0],p,.01,'l1Ochre'),ico([.06,.055,.06],'yellow',p,detail=0)]
        elif key=='umbrella':
            for a in [i*math.tau/7 for i in range(7)]:
                p=[.27*math.cos(a),.4,.27*math.sin(a)];fs += [rod([0,0,0],p,.013,'l1LeafDark'),ico([.13,.06,.13],'l1Petal',p,detail=0)]
        else:
            counts={'daisy':10,'rosette':8,'star':5,'orchid':5,'pea':3,'sepal':5};n=counts[key]
            fs=[disk(.08,.05,'yellow')]
            layers=2 if key=='rosette' else 1
            for layer in range(layers):
                for j in range(n):
                    a=j*360/n+layer*22
                    fs += placed([lens(leaf_outline('triangular' if key=='star' else 'ovate'),'l1Leaf' if key=='sepal' else 'l1Petal',.035)],[0,.06+layer*.06,0],[65 if key not in ('pea','orchid') else 20+j*18,a,0],scale=[.37 if key!='daisy' else .20,.4-layer*.12,.6])
            if key in ('pea','orchid'):fs += [ico([.25,.15,.24],'l1Ochre',[0,.13,.15],detail=0)]
        put('flower',key,name,fs,[.9,.9,.9],detail=list(range(9,len(fs))) if key=='rosette' else None)
    fruits=names('pome:梨果果体基件 drupe:核果果体基件 berry:浆果果体基件 citrus:柑橘瓣壳基件 pepo:瓜类棱果基件 nut:坚果果壳基件 pod:豆荚壳基件 capsule:蒴果壳基件 cone:球果鳞轴基件 hip:壶形果托基件 aggregate:聚合果基件 samara:翅果基件')
    for key,name in fruits:
        fs=[]
        if key=='pod':fs=[loft([[0,0,0,.025,.025],[.04,.2,0,.12,.07],[.06,.55,0,.13,.07],[0,.8,0,.02,.02]],'l1Leaf',8)]
        elif key=='samara':fs=[lens([[0,0],[.15,.12],[.35,.72],[.2,.8],[.05,.32]],'l1Ochre',.03),ico([.16,.16,.11],'wood',[0,.08,0],detail=0)]
        elif key in ('pepo','citrus','capsule'):
            n=8 if key=='pepo' else 6 if key=='citrus' else 4
            for j in range(n):
                a=j*math.tau/n;fs.append(ico([.19,.38,.19],'orange' if key!='capsule' else 'woodLight',[.14*math.cos(a),.23,.14*math.sin(a)],detail=1))
        elif key in ('cone','aggregate'):
            for y in range(4):
                for j in range(6):
                    a=j*math.tau/6+y*.4;r=.13*(1-y/6);fs.append(ico([.15,.12,.15],'wood' if key=='cone' else 'red',[r*math.cos(a),.08+y*.11,r*math.sin(a)],detail=0))
        else:
            profiles={'pome':[[.07,0],[.22,.10],[.24,.27],[.14,.42],[.06,.57],[.045,.61]],'drupe':[[.04,0],[.18,.10],[.24,.25],[.17,.43],[.04,.48]],'berry':[[.03,0],[.17,.12],[.18,.29],[.06,.37]],'nut':[[.08,0],[.19,.13],[.18,.31],[.04,.46]],'hip':[[.035,0],[.19,.14],[.17,.37],[.08,.48],[.06,.55]]}
            fs=[lathe(profiles[key],'l1Terracotta' if key!='nut' else 'wood',10,cap=True)]
        fs += [rod([0,.36,0],[.025,.57,.02],.018,'woodDark')]
        put('fruit',key,name,fs,[.65,.85,.65])
    for key,name in names('acorn_cup:橡果杯托基件 wing:单翼种翅基件 pappus:冠毛冠基件 burr:钩刺果壳基件 husk:谷壳基件 scale:球果种鳞基件 split_pod:开裂种荚片 seed_disk:种盘基件 caryopsis:颖果基件 spiny_shell:刺球壳基件'):
        if key=='acorn_cup':fs=[lathe([[.12,0],[.21,.08],[.23,.18],[.2,.18],[.18,.08],[.09,.03]],'wood',10,closed_profile=True)]
        elif key in ('wing','scale','husk','split_pod'):
            kind={'wing':'lanceolate','scale':'fan','husk':'strap','split_pod':'spade'}[key];fs=[lens(leaf_outline(kind),'l1Ochre',.07 if key=='split_pod' else .025)]
            if key=='husk':fs += [rod([0,.2,.02],[0,1.2,.02],.009,'woodLight',r2=.003)]
            if key=='split_pod':fs += [ico([.08,.09,.07],'woodLight',[0,y,.08],detail=0) for y in [.25,.45,.65]]
        elif key=='caryopsis':fs=[loft([[0,0,0,.02,.02],[0,.1,0,.11,.07],[0,.3,0,.09,.065],[0,.42,0,.015,.012]],'l1Ochre',8)]
        elif key=='seed_disk':fs=[disk(.3,.05,'woodDark')]+[ico([.045,.035,.045],'l1Ochre',[r*math.cos(a),.068,r*math.sin(a)],detail=0) for r,n in [(.12,8),(.23,12)] for a in [i*math.tau/n for i in range(n)]]
        else:
            fs=[ico([.25,.25,.25],'woodLight',[0,.2,0],detail=1)]
            for j in range(12):
                a=j*math.tau/12;p=[.09*math.cos(a),.22,.09*math.sin(a)];q=[.27*math.cos(a),.39 if key=='pappus' else .27,.27*math.sin(a)]
                fs.append(rod(p,q,.006 if key=='pappus' else .018,'l1Ivory' if key=='pappus' else 'wood',r2=.004,sides=5))
                if key=='burr':fs.append(rod(q,[q[0]*.93,q[1]-.04,q[2]*.93],.008,'wood',r2=.003))
        put('seed',key,name,fs,[.65,1.25,.65],detail=list(range(8,len(fs))) if len(fs)>15 else None)
    crops=names('wheat_ear:麦穗轴基件 barley_awn:长芒穗基件 rice_panicle:下垂圆锥穗基件 corn_cob:玉米穗芯基件 cotton_boll:棉铃基件 sunflower_disk:向日花盘基件 sorghum_head:密集穗冠基件 bean_vine:豆藤攀枝基件 cane_joint:蔗杆节基件 lettuce_heart:叶菜心基件')
    for key,name in crops:
        fs=[]
        if key in ('wheat_ear','barley_awn','rice_panicle','sorghum_head'):
            fs=[rod([0,0,0],[0,.85,0],.018,'l1Ochre')]
            for j in range(7):
                for s in [-1,1]:
                    x=s*.065;y=.19+j*.085
                    fs.append(ico([.10,.13,.07],'l1Ochre',[x,y,0],detail=0))
                    if key=='barley_awn':fs.append(rod([x,y,0],[s*.12,y+.24,0],.004,'l1Ochre',r2=.002,sides=4))
                    if key=='rice_panicle':fs += [rod([0,y,0],[s*.25,y-.1,0],.008,'l1Ochre'),ico([.07,.13,.04],'woodLight',[s*.25,y-.1,0],detail=0)]
                    if key=='sorghum_head':fs.append(ico([.1,.1,.1],'red',[s*.11,y,.07],detail=0))
        elif key=='corn_cob':
            fs=[lathe([[.09,0],[.14,.1],[.14,.55],[.055,.7]],'l1Ochre',10,cap=True)]
            fs += [ico([.045,.055,.045],'yellow',[.14*math.cos(a),.13+j*.07,.14*math.sin(a)],detail=0) for j in range(7) for a in [i*math.tau/8 for i in range(8)]]
        elif key=='cotton_boll':fs=[ico([.22,.23,.22],'l1Ivory',[.1*math.cos(a),.24,.1*math.sin(a)],detail=1) for a in [i*math.tau/5 for i in range(5)]]+[rod([0,0,0],[0,.17,0],.04,'wood')]
        elif key=='sunflower_disk':
            fs=[disk(.30,.06,'woodDark')]
            for a in range(0,360,30):fs += placed([lens(leaf_outline('lanceolate'),'yellow',.018)],[0,.08,0],[75,a,0],scale=[.2,.5,.7])
        elif key=='cane_joint':fs=[lathe([[.08,0],[.09,.25],[.10,.29],[.10,.34],[.085,.38],[.085,.78]],'l1Leaf',9,cap=True),ico([.08,.13,.055],'l1LeafDark',[.08,.33,0],detail=0)]
        elif key=='bean_vine':fs=[loft([[.08*math.cos(j*.8),j*.08,.08*math.sin(j*.8),.015,.015] for j in range(11)],'l1LeafDark',6)]+placed(leaf('heart'),[0,.4,0],[0,35,-40],scale=[.6,.6,.6])
        else:
            fs=[]
            for i,a in enumerate(range(0,360,60)):fs += placed([lens(leaf_outline('serrate'),'l1Leaf',.035)],[0,.03,0],[25+(i%2)*15,a,0],scale=[.4,.55,.7])
        put('crop',key,name,fs,[.9,1.05,.9],detail=list(range(1,len(fs),3)) if key=='corn_cob' else None)
    fungi=names('umbrella_cap:伞形菌盖基件 bell_cap:钟形菌盖基件 funnel_cap:漏斗菌盖基件 bracket_cap:层架菌盖基件 puffball:腹菌球壳基件 morel:网孔菌盖基件 gills:放射菌褶基件 pores:菌孔海绵基件 stipe:菌柄基件 ring_skirt:菌环裙边基件 mycelium:菌丝连接基件')
    for key,name in fungi:
        if key in ('umbrella_cap','bell_cap','funnel_cap'):
            profiles={'umbrella_cap':[[.03,.27],[.15,.25],[.34,.12],[.42,.05],[.39,.01],[.15,.15],[.03,.18]],'bell_cap':[[.025,.50],[.13,.43],[.25,.18],[.28,0],[.24,0],[.21,.17],[.095,.39],[.025,.43]],'funnel_cap':[[.05,0],[.10,.14],[.35,.3],[.4,.32],[.37,.27],[.08,.1],[.03,0]]};fs=[lathe(profiles[key],'l1Terracotta',14,closed_profile=True)]
        elif key=='bracket_cap':fs=[ico([.8,.13,.48],'wood',[0,.1,0],detail=1),ico([.63,.11,.38],'l1Ivory',[0,.2,-.04],detail=1)]
        elif key=='puffball':fs=[ico([.5,.55,.5],'l1Ivory',[0,.28,0],detail=1),round_tube(.065,.035,.07,'woodLight',8,position=[0,.5,0])]
        elif key=='morel':
            fs=[loft([[0,0,0,.12,.12],[0,.45,0,.21,.18],[0,.72,0,.04,.04]],'wood',10)]
            fs += [ring(.055,.014,.025,'l1Ivory',rotation=[90,0,0],position=[x,y,.16]) for x,y in [(-.08,.2),(.06,.2),(-.09,.36),(.07,.37),(-.04,.54)]]
        elif key=='gills':fs=[plate([[0,0],[.4,0],[.28,.12],[.03,.18]],.014,'l1Ivory',rotation=[0,a,0]) for a in range(0,360,24)]
        elif key=='pores':fs=[round_tube(.047,.028,.15,'l1Ivory',6,position=[x,0,z]) for x in [-.12,0,.12] for z in [-.12,0,.12]]
        elif key=='stipe':fs=[loft([[0,0,0,.12,.1],[.03,.18,0,.075,.07],[.03,.6,.02,.065,.06],[0,.75,0,.11,.09]],'l1Ivory',8)]
        elif key=='ring_skirt':fs=[lathe([[.10,.15],[.28,0],[.28,.035],[.10,.21]],'l1Ivory',12,closed_profile=True)]
        else:fs=[rod([0,.1,0],[x,0,z],.012,'l1Ivory',r2=.004,sides=5) for x,z in [(-.3,-.2),(.35,-.15),(-.25,.25),(.2,.33),(0,-.4),(.1,.45)]]
        put('fungus',key,name,fs,[.9,.85,.9],detail=list(range(1,len(fs),2)) if key=='morel' else None)
    finish('nature',133)
