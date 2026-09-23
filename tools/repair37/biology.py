"""Species-specific body plans, attached appendages and coherent silhouettes."""
from .common import *

INK='#202D31';CREAM='#E6DDC6';BROWN='#785844';GOLD='#B7954F'

def eyes(at,spread=.13,size=.035,iris=INK):
    return [ellipsoid([s*spread,at[1],at[2]],[size,size,size],iris,8,4) for s in (-1,1)]

def feet(x,y,z,web=False,color=GOLD):
    out=[]
    if web:
        for s in (-1,1):
            outline=[(s*x-.055,z-.035),(s*x+.055,z-.035),(s*x+.10,z+.15),(s*x,z+.19),(s*x-.10,z+.15)]
            out.append(slab_polygon(outline,y,.035,color))
    else:
        for s in (-1,1):
            for k in (-1,0,1):out.append(tube([[s*x,y+.06,z],[s*x+k*.035,y+.025,z+.11],[s*x+k*.06,y+.016,z+.19]],[.02,.015,.009],color,6))
            out.append(tube([[s*x,y+.05,z],[s*x,y+.02,z-.10]],[.022,.008],color,6))
    return out

def bill(z,y,width,length,height,color,hook=False):
    st=[(z,y,width/2,height/2),(z+length*.62,y-height*.04,width*.32,height*.34),(z+length,y-(height*.43 if hook else 0),.009,.01)]
    fs=[profile_z(st,color,8)]
    if hook:fs.append(tube([[0,y+.01,z+length*.8],[0,y-height*.16,z+length],[0,y-height*.8,z+length*.95]],[.03,.025,.004],color,8))
    return fs

def birds():
    for key in ('duck','heron','swan','owl','eagle','raven','parrot','penguin'):
        ident='l3-creature-bird-'+key;items=[];forms=[];neck=[];head=[];wings=[];legs=[];tail=[]
        if key=='duck':
            bc='#8C8674';hc='#345D47';by=.34;headat=[0,.67,.31]
            forms=[ellipsoid([0,by,-.06],[.48,.43,.70],bc),ellipsoid([0,.31,.15],[.38,.32,.25],'#8B5847')]
            neck=[tube([[0,.42,.16],[0,.57,.25],[0,.65,.28]],[.13,.105,.10],hc,12)]
            head=[ellipsoid(headat,[.27,.26,.29],hc),*bill(.39,.655,.17,.25,.065,'#CBA447'),*eyes([0,.697,.369],.113,.030)]
            for s in (-1,1):
                wings.append(ellipsoid([s*.216,.38,-.11],[.13,.30,.50],'#6D766B'))
                wings.append(leaf([s*.23,.415,-.15],[s*.26,.35,-.36],.09,'#3F647C',curve=.012))
                legs.append(tube([[s*.135,.21,.03],[s*.135,.035,.10]],[.028,.022],'#B88943',8))
            legs+=feet(.135,0,.07,True,'#B88943');tail=[leaf([0,.36,-.28],[0,.42,-.61],.25,'#5B5B4B',curve=0)]
        elif key=='swan':
            forms=[ellipsoid([0,.42,-.12],[.72,.59,1.02],'#E9E9DB')]
            neck=[tube([[0,.55,.19],[0,.78,.33],[0,1.03,.30],[0,1.28,.34],[0,1.43,.47]],[(.13,.14),(.09,.10),(.075,.08),(.07,.075),(.075,.08)],'#E9E9DB',12)]
            head=[ellipsoid([0,1.45,.50],[.24,.24,.32],'#E9E9DB'),*bill(.60,1.43,.12,.21,.09,'#CA884C'),*eyes([0,1.493,.569],.106,.034)]
            for s in (-1,1):
                wings.append(ellipsoid([s*.28,.53,-.17],[.20,.35,.76],'#F1EFDF'))
                legs.append(tube([[s*.18,.23,-.03],[s*.18,.04,.0]],[.035,.025],INK,8))
            legs+=feet(.18,0,0,True,INK);tail=[leaf([0,.43,-.46],[0,.52,-.83],.34,'#E9E9DB',curve=.01)]
        elif key=='heron':
            forms=[ellipsoid([0,.98,0],[.36,.49,.65],'#93A6AD')]
            neck=[tube([[0,1.10,.17],[0,1.27,.30],[0,1.47,.13],[0,1.66,.20],[0,1.78,.34]],[(.11,.12),(.075,.085),(.065,.075),(.06,.075),(.06,.07)],'#D7DAD2',12)]
            head=[ellipsoid([0,1.83,.38],[.21,.22,.32],'#D8DDD5'),*bill(.50,1.824,.085,.39,.08,'#C7A767'),*eyes([0,1.86,.449],.093,.029,'#30362E'),
                  tube([[0,1.91,.34],[0,1.91,.18],[0,1.82,-.02]],[.036,.022,.002],'#273E4C',8)]
            for s in (-1,1):
                wings.append(ellipsoid([s*.143,1.02,-.05],[.11,.34,.58],'#667E8E'))
                legs.append(tube([[s*.1,.82,-.04],[s*.105,.43,.065],[s*.13,.055,.02]],[.027,.021,.016],'#737664',8))
            legs+=feet(.13,0,.02,False,'#666956');tail=[leaf([0,1.04,-.20],[0,.88,-.58],.17,'#465F6C',curve=0)]
        elif key=='owl':
            forms=[ellipsoid([0,.43,0],[.55,.64,.50],'#806D54')]
            head=[ellipsoid([0,.91,.035],[.54,.43,.46],'#8F7755')]
            for s in (-1,1):
                head += [ellipsoid([s*.125,.92,.24],[.252,.294,.09],'#C6B997'),ellipsoid([s*.115,.95,.286],[.117,.13,.052],'#CEA54F'),ellipsoid([s*.115,.953,.31],[.063,.079,.018],INK,8,4),
                         leaf([s*.18,1.01,.02],[s*.25,1.22,-.015],.13,'#5E4D3F',curve=0,thickness=.035)]
                wings.append(ellipsoid([s*.222,.49,-.015],[.16,.47,.42],'#635447'))
                for k in range(4):wings.append(ellipsoid([s*.256,.63-k*.095,.13],[.053,.035,.05],'#B4A585',8,4))
            head+=bill(.225,.855,.072,.11,.078,'#958464',True)
            legs=feet(.14,0,.08)+[tube([[side*.14,.18,.02],[side*.14,.035,.06]],.044,'#B6A078',8) for side in (-1,1)];tail=[leaf([0,.34,-.17],[0,.13,-.44],.22,'#71614E',curve=0)]
        elif key=='eagle':
            forms=[ellipsoid([0,.53,-.04],[.48,.64,.64],'#594B3B')]
            neck=[tube([[0,.72,.18],[0,.9,.25]],[.15,.12],'#D7D1B8',12)]
            head=[ellipsoid([0,.92,.28],[.29,.29,.34],'#E8E1C9'),*bill(.39,.898,.13,.21,.13,'#B7A45B',True),*eyes([0,.971,.352],.124,.036)]
            for s in (-1,1):
                outline=[(s*.15,.19),(s*.47,.22),(s*.91,.17),(s*1.26,-.04),(s*1.38,-.20),(s*1.20,-.30),(s*.78,-.29),(s*.45,-.32),(s*.18,-.27)]
                wings.append(slab_polygon(outline,.68,.09,'#5E5140'))
                for k in range(6):
                    root=[s*(.60+k*.105),.695,-.16];tip=[s*(.76+k*.119),.66,-.49-k*.012]
                    wings.append(leaf(root,tip,.13,'#4C4439',curve=.012,thickness=.025))
                legs.append(tube([[s*.135,.29,.06],[s*.135,.08,.12]],[.05,.026],'#AA9555',8))
            legs+=feet(.135,0,.1,color='#B4A059');tail=[leaf([0,.42,-.20],[0,.33,-.77],.42,'#DDD7BF',curve=0)]
        elif key=='raven':
            forms=[ellipsoid([0,.43,0],[.37,.49,.59],'#28353B')]
            neck=[tube([[0,.59,.18],[0,.75,.24]],[.12,.10],'#263237',12)]
            head=[ellipsoid([0,.80,.275],[.25,.26,.3],'#25343B'),*bill(.37,.792,.10,.23,.10,'#263037'),*eyes([0,.846,.345],.109,.026,'#070D11')]
            for s in (-1,1):
                wings.append(ellipsoid([s*.167,.43,-.12],[.10,.34,.58],'#344754'))
                legs.append(tube([[s*.10,.22,.04],[s*.10,.055,.07]],[.024,.018],'#3B3F3F',8))
            legs+=feet(.10,0,.04,color='#383F40')
            for k in range(5):tail.append(leaf([(k-2)*.025,.34,-.19],[(k-2)*.055,.25,-.76+abs(k-2)*.06],.095,'#25343F',curve=0,thickness=.015))
        elif key=='parrot':
            forms=[ellipsoid([0,.43,0],[.38,.58,.45],'#6B8D49')]
            neck=[tube([[0,.62,.08],[0,.75,.12]],[.13,.10],'#759850',12)]
            head=[ellipsoid([0,.83,.16],[.32,.33,.34],'#769A50'),*bill(.28,.82,.14,.20,.18,'#807057',True),*eyes([0,.884,.244],.132,.036)]
            for s in (-1,1):
                wings.append(ellipsoid([s*.15,.42,-.08],[.115,.44,.34],'#397360'))
                wings.append(leaf([s*.16,.42,-.02],[s*.13,.17,-.34],.12,'#3F6980',curve=.01))
                legs.append(tube([[s*.1,.2,0],[s*.1,.04,.06]],[.03,.02],'#6F7069',8))
            legs+=feet(.1,0,.03,color='#767769')
            for s in (-1,0,1):tail.append(leaf([s*.03,.30,-.12],[s*.06,.035,-.55],.095,'#648856' if s else '#CFBD60',curve=0))
        else:
            forms=[ellipsoid([0,.59,0],[.58,1.07,.49],'#263B46'),ellipsoid([0,.56,.18],[.40,.84,.17],'#E7E9DD')]
            head=[ellipsoid([0,1.12,.045],[.33,.36,.36],'#253842'),*bill(.17,1.105,.11,.17,.072,'#AB8853'),*eyes([0,1.174,.144],.128,.03,INK)]
            for s in (-1,1):wings.append(leaf([s*.225,.88,.005],[s*.40,.34,-.09],.16,'#243A46',curve=.015,thickness=.065))
            legs=feet(.17,0,.10,True,'#A78B5E')+[tube([[side*.17,.14,.025],[side*.17,.026,.08]],.045,'#A78B5E',8) for side in (-1,1)];tail=[leaf([0,.2,-.18],[0,.035,-.39],.19,'#263842',curve=0)]
        for name,fs,mat in [('torso',forms,'mat.fur'),('neck',neck,'mat.fur'),('head',head,'mat.fur'),('wings',wings,'mat.fur'),('feet',legs,'mat.hoof'),('tail',tail,'mat.fur')]:
            if fs:items.append(node(ident,name,fs,material=mat))
        replace(ident,items,'共用猛禽头与离体翼，鸟种的喙形、颈长、站姿和羽色关系错误','按鸟种重建连续体态、双侧贴合翼、喙、足、尾羽和眼位')

def reptile(key):
    ident='l3-creature-aquatic-'+key;items=[]
    if key=='turtle':
        shell=[ellipsoid([0,.28,0],[1.03,.55,1.38],'#70835B',16,7)]
        # Coloured shell panels follow the dome rather than floating decoration.
        for j,z in enumerate([-.38,0,.38]):
            for s in (-1,1):
                x=s*.20;yy=.28+.275*math.sqrt(max(.01,1-(x/.515)**2-(z/.69)**2))
                shell.append(ellipsoid([x,yy-.012,z],[.31,.057,.32],'#7F8F60' if j%2 else '#637653',8,4))
        torso=[ellipsoid([0,.15,0],[.84,.22,1.10],'#B7AD78')]
        head=[ellipsoid([0,.22,.75],[.27,.24,.42],'#819168'),*eyes([0,.267,.842],.12,.038)]
        limbs=[]
        for s in (-1,1):
            limbs.append(leaf([s*.35,.20,.34],[s*.95,.075,.67],.34,'#7F8D61',curve=.06,thickness=.05))
            limbs.append(leaf([s*.32,.15,-.38],[s*.64,.08,-.79],.25,'#7F8D61',curve=.025,thickness=.04))
        limbs.append(tube([[0,.17,-.46],[0,.14,-.81],[0,.10,-.90]],[.075,.037,.004],'#7B895D',8))
        items=[node(ident,'torso',torso),node(ident,'shell',shell),node(ident,'head',head),node(ident,'flippers',limbs)]
    else:
        croc=key=='crocodile';green='#687B48' if croc else '#7D8458'
        st=[(-2.0,.08,.008,.008),(-1.55,.15,.08,.055),(-1.05,.22,.16,.10),(-.64,.26,.29,.155),(-.10,.28,.36,.185),(.42,.29,.32,.16),(.69,.28,.23,.12)]
        torso=[profile_z(st,green,12)]
        head=[profile_z([(.49,.28,.22,.115),(.79,.31,.24,.13),(1.03,.27,.20,.078),(1.48 if croc else 1.20,.245,.12,.038)],green,12),
              profile_z([(.63,.20,.19,.043),(1.07,.18,.18,.035),(1.47 if croc else 1.2,.196,.116,.016)],'#9AA477',10),
              *[ellipsoid([side*.178,.366,.835],[.106,.099,.135],green,10,5) for side in (-1,1)],
              *eyes([0,.397,.832],.209,.043,'#D4BD73')]
        for s in (-1,1):
            head.append(ellipsoid([s*.225,.401,.84],[.017,.027,.029],INK,8,4))
            head.append(ellipsoid([s*.085,.28,1.41 if croc else 1.14],[.035,.025,.027],INK,8,4))
        items=[node(ident,'torso',torso),node(ident,'head',head)]
        for i,(s,z) in enumerate([(-1,-.48),(1,-.48),(-1,.39),(1,.39)]):
            leg=[tube([[s*.245,.25,z],[s*.45,.145,z-.14],[s*.59,.065,z-.09]],[.11,.085,.043],green,10)]
            for k in range(4):
                toe=[s*(.58+k*.026),.035,z-.16+k*.065]
                leg.append(tube([[s*.57,.064,z-.09],toe,[toe[0]+s*.1,.018,toe[2]+.06]],[.029,.024,.009],green,6))
            items.append(node(ident,'leg'+str(i),leg))
        if croc:
            fs=[]
            for j in range(9):
                z=-.73+j*.17
                # Scute bases follow the actual shell section analytically.
                for k in range(len(st)-1):
                    if st[k][0]<=z<=st[k+1][0]:
                        t=(z-st[k][0])/(st[k+1][0]-st[k][0]);v=[st[k][a]*(1-t)+st[k+1][a]*t for a in range(4)];break
                for x in (-.11,.11):
                    y=v[1]+v[3]*math.sqrt(max(.01,1-(x/v[2])**2))-.02
                    fs.append(extrude_xy([[x-.047,y],[x,y+.09],[x+.047,y]],.09,'#7B8955',z=z))
            items.append(node(ident,'scutes',fs))
    replace(ident,items,'四肢/背甲脱离，鳄鱼尾部与背饰错误；海龟使用灯罩壳和陆生腿','按连续躯干重做四肢接根、贴背甲片、尾部、口鼻；海龟独立背腹甲与鳍肢')

def aquatics():
    for key in ('crocodile','lizard','turtle'):reptile(key)
    for key in ('shark','ray','eel','octopus','squid'):
        ident='l3-creature-aquatic-'+key;items=[]
        if key=='shark':
            body=[profile_z([(-1.35,.4,.08,.14),(-.85,.47,.18,.23),(-.20,.54,.37,.39),(.54,.52,.33,.32),(1.03,.49,.17,.16),(1.30,.465,.012,.018)],'#6A8794',14)]
            fins=[extrude_xy([[-.025,.72],[-.025,1.21],[.28,.83]],.07,'#546F7C',z=-.18)]
            # Dorsal and caudal fins are vertical sagittal volumes.
            fins=[mesh([[-.03,.78,-.35],[.03,.78,-.35],[-.03,1.24,-.49],[.03,1.24,-.49],[-.03,.72,.17],[.03,.72,.17]],[[0,2,4],[1,5,3],[0,1,3,2],[2,3,5,4],[4,5,1,0]],'#566F7D')]
            fins.append(mesh([[s*.038,y,z] for s in (-1,1) for y,z in [(.42,-1.2),(1.0,-1.67),(.44,-1.54),(.05,-1.69)]],[[0,1,2,3],[4,7,6,5],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]],'#536E7B'))
            for s in (-1,1):fins.append(leaf([s*.21,.42,.16],[s*.95,.23,-.46],.35,'#5F7C89',curve=.02,thickness=.055))
            details=eyes([0,.59,.95],.215,.052,INK)
            for s in (-1,1):
                for j in range(4):details.append(tube([[s*(.294+j*.011),.65,.34-j*.085],[s*(.32+j*.005),.47,.32-j*.085]],[.008,.009],'#3A515E',5))
            items=[node(ident,'body',body),node(ident,'fins',fins),node(ident,'features',details)]
        elif key=='ray':
            body=[profile_z([(-.75,.20,.1,.07),(-.38,.25,.40,.10),(.20,.28,.51,.11),(.62,.26,.26,.075),(.71,.25,.08,.025)],'#778C89',12)]
            fins=[]
            for s in (-1,1):
                outline=[(s*.16,.61),(s*.65,.36),(s*1.18,-.04),(s*1.29,-.26),(s*.77,-.43),(s*.23,-.70)]
                fins.append(slab_polygon(outline,.18,.07,'#6A817D'))
            tail=[tube([[0,.21,-.55],[0,.20,-1.05],[.08,.23,-1.68],[.15,.26,-2.15]],[.10,.055,.025,.003],'#617571',8)]
            items=[node(ident,'body',body),node(ident,'pectoral_fins',fins),node(ident,'tail',tail),node(ident,'eyes',eyes([0,.369,.37],.20,.057))]
        elif key=='eel':
            pts=[[.19*math.sin(j*.57),.21+.04*math.sin(j*.6),1.3-j*.25] for j in range(13)]
            radii=[.13,.15,.14,.13,.12,.11,.10,.087,.073,.059,.045,.027,.005]
            body=[tube(pts,radii,'#77815C',12),ellipsoid([0,.22,1.31],[.25,.26,.42],'#7F8963')]
            fin=[]
            for j in range(2,11):fin.append(beam([pts[j][0],pts[j][1]+radii[j]*.9,pts[j][2]],[pts[j+1][0],pts[j+1][1]+radii[j+1]*.9,pts[j+1][2]],.075,'#657051',depth=.025))
            items=[node(ident,'spine',body),node(ident,'fin',fin),node(ident,'eyes',eyes([0,.283,1.44],.105,.033))]
        elif key=='octopus':
            body=[ellipsoid([0,.60,-.12],[.76,.87,.74],'#A77583',14,8),ellipsoid([0,.26,.1],[.52,.36,.52],'#A77583')]
            items=[node(ident,'mantle',body),node(ident,'eyes',eyes([0,.38,.295],.227,.085,'#2D2933'))]
            for j in range(8):
                a=math.tau*j/8;pts=[]
                for t in (0,.25,.5,.75,1):
                    rr=.19+.91*t;ang=a+.40*t*t;pts.append([rr*math.sin(ang),.16-.07*math.sin(t*math.pi)+.05*t,rr*math.cos(ang)])
                fs=[tube(pts,[.14,.105,.074,.041,.004],'#A77583',10)]
                for k in range(1,4):
                    p=pts[k];fs.append(ellipsoid([p[0],p[1]-.05,p[2]],[.064,.035,.064],'#DAB6A9',8,4))
                items.append(node(ident,'tentacle'+str(j),fs))
        else:
            body=[profile_z([(-1.15,.35,.01,.012),(-.72,.37,.25,.19),(.03,.38,.31,.24),(.58,.35,.20,.16)],'#AB939C',14)]
            fins=[]
            for s in (-1,1):fins.append(leaf([s*.09,.4,-.98],[s*.66,.38,-.46],.45,'#BD9EAA',curve=.01,thickness=.04))
            arms=[]
            for j in range(8):
                a=math.tau*j/8;arms.append(tube([[.15*math.sin(a),.35+.1*math.cos(a),.43],[.27*math.sin(a),.34+.16*math.cos(a),.91],[.20*math.sin(a),.28+.13*math.cos(a),1.40]],[.066,.039,.004],'#B99AA5',8))
            for s in (-1,1):arms += [tube([[s*.12,.36,.5],[s*.38,.24,1.2],[s*.46,.26,1.95]],[.032,.022,.026],'#B99AA5',8),ellipsoid([s*.46,.26,1.93],[.1,.055,.25],'#C6A8AF')]
            items=[node(ident,'mantle',body),node(ident,'fins',fins),node(ident,'arms',arms),node(ident,'eyes',eyes([0,.43,.47],.18,.073))]
        replace(ident,items,'体型/推进附肢复用不对应物种，部分附肢离体','重建相应水生体态与真实接根的鳍、尾、腕足，独立保留编辑节点')

def heavy_mammals():
    for key in ('rhino','boar','elephant','bear'):
        ident='l3-creature-mammal-'+key;ele=key=='elephant';rhino=key=='rhino';boar=key=='boar'
        col='#92968D' if ele or rhino else '#665444' if boar else '#785C42'
        cy=1.05 if ele else .84 if rhino else .53 if boar else .72;h=.59 if ele else .48 if rhino else .32 if boar else .45
        body=[profile_z([(-.93,cy,.12,h*.4),(-.65,cy,.44 if ele else .39,h),(.15,cy,.52 if ele else .43,h*1.12),(.67,cy+.05,.37,h*.9)],col,14)]
        items=[node(ident,'torso',body)]
        for j,(s,z) in enumerate([(-1,-.55),(1,-.55),(-1,.48),(1,.48)]):
            yy=cy-.10;r=.16 if ele else .145 if rhino else .105 if boar else .13
            fs=[tube([[s*.31,yy,z],[s*.34,yy*.48,z-.035],[s*.35,.13,z+.035]],[r*1.10,r*.87,r*.88],col,10),ellipsoid([s*.35,.11,z+.09],[r*2,.22,r*2.5],'#767D75' if ele or rhino else col)]
            if rhino or ele:
                for k in (-1,0,1):fs.append(ellipsoid([s*.35+k*r*.55,.074,z+r*1.08],[r*.48,.095,.058],'#C5C5B2',8,4))
            items.append(node(ident,'leg'+str(j),fs))
        if ele:
            head=[ellipsoid([0,1.30,.92],[.83,.94,.80],col),tube([[0,1.32,1.24],[0,.89,1.44],[0,.43,1.56],[.07,.26,1.72],[.17,.40,1.8]],[(.19,.16),(.15,.14),(.11,.10),(.08,.08),(.055,.055)],col,12),*eyes([0,1.43,1.20],.346,.056)]
            for s in (-1,1):
                head += [ellipsoid([s*.48,1.22,.76],[.27,.95,.67],'#878E84',12,6),tube([[s*.24,1.06,1.18],[s*.32,.88,1.55],[s*.34,.97,1.84]],[.09,.052,.003],'#E0D7B8',10)]
        elif rhino:
            head=[profile_z([(.50,.98,.30,.30),(.89,.80,.34,.27),(1.31,.60,.26,.22),(1.52,.59,.19,.16)],col,12),*eyes([0,.941,1.02],.295,.045)]
            for s in (-1,1):head.append(leaf([s*.18,1.1,.65],[s*.24,1.43,.52],.21,'#889084',curve=.015,thickness=.07))
            head += [tube([[0,.77,1.32],[0,1.10,1.33],[0,1.36,1.39]],[.13,.077,.003],'#C2BAA0',12),tube([[0,.86,1.04],[0,1.06,1.03]],[.08,.003],'#C2BAA0',10)]
        elif boar:
            head=[profile_z([(.40,.61,.26,.24),(.83,.54,.24,.23),(1.15,.43,.15,.12),(1.36,.43,.14,.11)],col,12),ellipsoid([0,.44,1.359],[.28,.19,.06],'#9A8270'),*eyes([0,.665,.863],.212,.038)]
            for s in (-1,1):
                head += [ellipsoid([s*.063,.45,1.39],[.045,.03,.023],INK,8,4),leaf([s*.15,.68,.63],[s*.28,.96,.58],.22,'#776351',curve=.01,thickness=.045),
                         tube([[s*.18,.39,1.02],[s*.29,.44,1.14],[s*.27,.66,1.11]],[.061,.035,.003],CREAM,10)]
            body.append(tube([[-.01,.84,-.73],[0,.9,-.19],[0,.96,.41]],[.07,.08,.045],'#443F35',6))
        else:
            head=[ellipsoid([0,.94,.91],[.67,.63,.61],col),ellipsoid([0,.84,1.18],[.39,.26,.34],'#AC9270'),ellipsoid([0,.874,1.346],[.15,.10,.06],INK),*eyes([0,1.015,1.151],.237,.045)]
            for s in (-1,1):head.append(ellipsoid([s*.25,1.22,.85],[.20,.22,.14],col,10,5))
        tail=[tube([[0,cy,-.80],[0,cy-.2,-1.02],[.12,cy-.35,-1.10]],[.07,.045,.009],col,8)]
        items += [node(ident,'head',head),node(ident,'tail',tail)]
        replace(ident,items,'犀牛/野猪共用熊头，腿根、鼻角或獠牙连接和比例不对应物种','按物种独立重建头吻、耳廓、角/獠牙、四肢承重与连续胸腹')
    for key in ('stag','ram','musk_ox','working_goat'):
        ident='l3-creature-mammal-'+key;d=ASSEMBLIES[ident]
        if key=='working_goat':continue  # preserve existing pack rig; horns belong to the source head.
        d['instances']=[v for v in d['instances'] if v['id']!='horns'];fs=[]
        for s in (-1,1):
            if key=='stag':
                base=[s*.105,.14,-.08];pts=[base,[s*.20,.38,-.12],[s*.33,.66,-.18],[s*.42,.89,-.21]]
                fs.append(tube(pts,[.045,.035,.024,.003],CREAM,8))
                for j,p in enumerate(pts[1:3]):fs.append(tube([p,[p[0]+s*.16,p[1]+.20,p[2]+.16]],[.026,.003],CREAM,7))
            elif key=='ram':
                pts=[[s*(.15+.15*math.sin(a)),.10+.18*math.cos(a),-.05+.15*math.sin(a)] for a in [0,.5,1,1.5,2,2.5,3,3.5,4]]
                fs.append(tube(pts,[.068,.065,.058,.054,.048,.040,.030,.02,.003],GOLD,10))
            else:fs.append(tube([[s*.12,.11,-.02],[s*.28,.08,-.02],[s*.4,.13,.02],[s*.44,.36,.05]],[.066,.056,.039,.004],CREAM,9))
        d['instances'].append(node(ident,'horns',fs,parent='skin.rig.head'));d['version']=REV
        record(ident,'鹿角/羊角以单件居中摆放，不能形成成对生长关系','保留原身体蒙皮与头骨节点，在骨骼局部框架中重建双侧角冠')

def fantastic():
    for key in ('beetle','spider','moth','crab','golem','dragon','wyvern','slime'):
        ident='l3-creature-fantastic-'+key;items=[]
        if key=='slime':
            continue  # no new visual fault established for the intentionally fantastic slime.
        if key in ('beetle','spider','moth','crab'):
            crab=key=='crab';spider=key=='spider';moth=key=='moth';col='#A9654C' if crab else '#675341' if spider else '#7F8560' if moth else '#4F6952'
            body=[ellipsoid([0,.33,-.16],[1.0,.42,.68] if crab else [.62,.52,.77],col)]
            body.append(ellipsoid([0,.31,.36],[.43,.34,.39],col))
            if key=='beetle':
                for s in (-1,1):body.append(ellipsoid([s*.155,.40,-.16],[.33,.31,.76],'#5C7650'))
            items=[node(ident,'core',body),node(ident,'eyes',eyes([0,.43,.52],.15,.045))]
            n=8 if crab or spider else 6
            for j in range(n):
                s=-1 if j%2==0 else 1;z=(j//2-(n//2-1)/2)*.22
                pts=[[s*.20,.31,z],[s*.57,.50,z+(.15 if z>0 else -.15)],[s*.87,.03,z+(.30 if z>0 else -.30)]]
                items.append(node(ident,'leg'+str(j),[tube(pts,[.057,.047,.009],col,8)]))
            extras=[]
            if crab:
                for s in (-1,1):
                    extras += [tube([[s*.3,.34,.35],[s*.64,.34,.55],[s*.64,.37,.87]],[.095,.083,.075],col,10),ellipsoid([s*.64,.38,.88],[.28,.22,.28],col)]
                    for k in (-1,1):extras.append(tube([[s*.64+k*.10,.39,.91],[s*.64+k*.11,.4,1.10],[s*.64+k*.022,.41,1.18]],[.055,.035,.003],col,7))
            else:
                for s in (-1,1):extras.append(tube([[s*.1,.43,.43],[s*.19,.58,.61],[s*.26,.62,.73]],[.016,.012,.003],col,6))
            if moth:
                for s in (-1,1):
                    extras += [leaf([s*.1,.42,.19],[s*1.0,.42,.65],.72,'#A59B7C',curve=.08,thickness=.035),leaf([s*.13,.36,-.02],[s*.76,.34,-.61],.60,'#8C7E63',curve=.05,thickness=.03),
                               ellipsoid([s*.63,.494,.40],[.17,.021,.19],'#504B45',10,4),ellipsoid([s*.63,.507,.40],[.09,.014,.095],'#C8BE98',8,4)]
            if extras:items.append(node(ident,'features',extras))
        elif key=='golem':
            torso=[basebox([.75,.85,.43],[0,.57,0],'#858E85',bevel=.13),block([.45,.42,.44],[0,1.65,.02],'#ADB2A2',bevel=.09)]
            items=[node(ident,'core',torso)]
            for j,s in enumerate((-1,1)):
                items.append(node(ident,'leg'+str(j),[basebox([.28,.64,.30],[s*.22,0,0],'#92998B',bevel=.05),block([.31,.20,.43],[s*.22,.10,.06],'#788578',bevel=.06)]))
                items.append(node(ident,'arm'+str(j),[tube([[s*.39,1.27,0],[s*.56,.94,.02],[s*.66,.68,.14]],[(.19,.19),(.16,.15),(.16,.14)],'#929B8E',6),block([.3,.27,.3],[s*.67,.59,.15],'#788578',bevel=.07)]))
            items.append(node(ident,'face',[block([.08,.04,.022],[s*.10,1.70,.247],'#88BEB0',bevel=.006) for s in (-1,1)]))
        else:
            col='#64765E';body=[profile_z([(-1.55,.23,.008,.008),(-.95,.33,.13,.10),(-.55,.45,.28,.22),(.15,.52,.37,.32),(.56,.63,.24,.28)],col,12),tube([[0,.65,.34],[0,.97,.53],[0,1.18,.80]],[.23,.19,.15],col,12)]
            head=[profile_z([(.62,1.17,.17,.19),(.91,1.17,.22,.2),(1.29,1.08,.12,.10)],col,10),*eyes([0,1.27,.98],.191,.044,'#D2B365')]
            for s in (-1,1):head.append(tube([[s*.15,1.29,.69],[s*.23,1.55,.51]],[.07,.003],CREAM,8))
            items=[node(ident,'core',body),node(ident,'head',head)]
            for j,(s,z) in enumerate([(-1,-.32),(1,-.32)]+([] if key=='wyvern' else [(-1,.4),(1,.4)])):
                items.append(node(ident,'leg'+str(j),[tube([[s*.24,.53,z],[s*.40,.30,z-.09],[s*.43,.07,z+.1]],[.13,.11,.05],col,10),ellipsoid([s*.43,.07,z+.17],[.2,.14,.31],col)]))
            for s in (-1,1):
                outline=[(s*.22,.3),(s*.57,.51),(s*1.19,.28),(s*1.66,-.23),(s*1.10,-.33),(s*.65,-.69),(s*.30,-.39)]
                fs=[slab_polygon(outline,.90,.055,'#8C9270')]
                for k in (2,3,4,5):fs.append(tube([[s*.24,.945,.29],[s*.58,1.02,.38],[outline[k][0],.93,outline[k][1]]],[.067,.045,.008],col,8))
                items.append(node(ident,'wing'+('0' if s<0 else '1'),fs))
        replace(ident,items,'幻想生物复用哺乳躯干/爬行腿，翼根和肢体脱节，节肢动物及傀儡辨识不成立','按双翼龙/六足昆虫/八足蛛/蟹钳/双臂石傀儡结构分别重建')

def author():
    birds();aquatics();heavy_mammals();fantastic()
