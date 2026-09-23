"""118 furniture and interior modules, kept below complete-furniture level."""
from .common import *
from .architecture import contour_frame,opening_outline


def slab(outline,thickness=.065,color='wood',y=.065):
    return plate(outline,thickness,color,rotation=[90,0,0],position=[0,y-thickness/2,0])


def shell(w=1,h=1,d=.5,open_back=False):
    fs=[formbox(w,.065,d,'wood',y=y) for y in [0,h-.065]]
    fs += [formbox(.065,h-.13,d,'wood',x=x,y=.065) for x in [-(w-.065)/2,(w-.065)/2]]
    if not open_back:fs += [formbox(w-.13,h-.13,.045,'woodDark',y=.065,z=-d/2+.0225)]
    return fs


def cushion(w,h,d,shape='square'):
    if shape=='round':return [lathe([[w*.4,0],[w*.5,h*.3],[w*.5,h*.7],[w*.36,h]],'l1Ivory',12,cap=True,scale=[1,1,d/w])]
    if shape=='wedge':return [plate([[-w/2,0],[w/2,0],[w/2,h*.35],[-w/2,h]],d,'l1Ivory')]
    return [box([w,h,d],'l1Ivory',[0,h/2,0],min(h*.25,.08))]


def author():
    def put(g,k,n,fs,sz,**kw):return register('interior',g,k,n,fs,sz,**kw)
    tops=names('round:圆盘桌面芯 oval:椭圆桌面芯 stadium:长圆桌面芯 trapezoid:梯形桌面芯 triangular:三角桌面芯 hex:六角桌面芯 kidney:肾形桌面芯 corner:转角桌面芯 semicircle:半圆桌面芯 scalloped:波边桌面芯 live_edge:自然边桌面芯 drop_leaf:折叶桌面芯')
    for key,name in tops:
        if key in ('round','oval','stadium'):
            outline=[]
            for j in range(20):
                a=j*math.tau/20;x=.55*math.cos(a);z=.55*math.sin(a)
                if key=='oval':x*=1.45
                if key=='stadium':x+=.30*(1 if x>=0 else -1)
                outline.append([x,z])
        elif key in ('triangular','hex'):n=3 if key=='triangular' else 6;outline=[[.7*math.cos(j*math.tau/n),.7*math.sin(j*math.tau/n)] for j in range(n)]
        elif key=='trapezoid':outline=[[-.7,-.35],[.7,-.35],[.45,.4],[-.45,.4]]
        elif key=='corner':outline=[[-.7,-.7],[.15,-.7],[.15,-.15],[.7,-.15],[.7,.7],[-.7,.7]]
        elif key=='semicircle':outline=[[-.7,0],[.7,0]]+[[.7*math.cos(j*math.pi/12),.7*math.sin(j*math.pi/12)] for j in range(1,12)]
        elif key=='kidney':outline=[[-.75,-.12],[-.62,-.36],[-.3,-.4],[0,-.19],[.32,-.33],[.63,-.22],[.76,.06],[.61,.38],[.15,.45],[-.35,.40],[-.67,.24]]
        elif key=='scalloped':outline=[[(.62+.06*math.cos(j*math.pi/2))*math.cos(j*math.tau/24),(.5+.06*math.cos(j*math.pi/2))*math.sin(j*math.tau/24)] for j in range(24)]
        elif key=='live_edge':outline=[[-.8,-.35],[-.4,-.43],[.1,-.38],[.6,-.43],[.8,-.32],[.8,.38],[.42,.43],[0,.34],[-.5,.42],[-.8,.32]]
        else:outline=[[-.7,-.25],[.7,-.25],[.7,.12],[.58,.35],[-.58,.35],[-.7,.12]]
        fs=[slab(outline)]
        if key=='drop_leaf':fs += [round_tube(.025,.01,.2,'l1Metal',8,rotation=[0,0,90],position=[x,.05,-.24]) for x in [-.45,.45]]
        put('tabletop',key,name,fs,[1.8,.12,1.5],material='mat.wood')
    seats=names('scoop:凹弧座壳基件 tractor:鞍状座盘基件 bucket:包裹座壳基件 saddle:双翼鞍座基件 mesh_pan:网格座盘基件 slatted:条栅座面基件 upholstered:软包座芯基件 kneeling:跪坐承托垫基件 back_spindle:栅条靠背基件 back_ladder:梯档靠背基件 back_fan:扇形靠背基件 back_shell:曲面靠背基件 arm_loop:环形扶手基件 arm_pad:软包扶手基件')
    for key,name in seats:
        fs=[]
        if key in ('scoop','tractor','saddle'):
            pts=[[-.28,.13,-.25],[.28,.13,-.25],[.30,.12,.2],[.18,.04,.3],[-.18,.04,.3],[-.30,.12,.2],[0,.04,0],[-.28,.08,-.25],[.28,.08,-.25],[.30,.07,.2],[.18,0,.3],[-.18,0,.3],[-.30,.07,.2],[0,0,0]]
            faces=[]
            for j in range(6):faces += [[6,j,(j+1)%6],[13,7+(j+1)%6,7+j],[j,7+j,7+(j+1)%6,(j+1)%6]]
            fs=[poly(pts,faces,'wood')]
            if key=='tractor':fs += [ico([.2,.08,.25],'woodDark',[x,.1,-.06],detail=0) for x in [-.13,.13]]
            if key=='saddle':fs += [ico([.15,.14,.18],'l1Rubber',[0,.14,.20],detail=0)]
        elif key=='bucket':fs=cushion(.52,.10,.52)+[box([.07,.25,.42],'l1Slate',[x,.17,-.06],.025) for x in [-.28,.28]]+[box([.56,.32,.07],'l1Slate',[0,.22,-.29],.025,rotation=[-10,0,0])]
        elif key in ('mesh_pan','slatted'):
            fs=[box([.05,.08,.55],'l1Slate',[x,.04,0]) for x in [-.28,.28]]+[box([.55,.035,.05],'wood' if key=='slatted' else 'l1Slate',[0,.07,z]) for z in [-.24,-.12,0,.12,.24]]
            if key=='mesh_pan':fs += [box([.025,.025,.5],'l1Slate',[x,.075,0]) for x in [-.20,-.1,0,.1,.2]]
        elif key=='upholstered':fs=cushion(.58,.14,.53)+[box([.53,.022,.48],'woodDark',[0,-.01,0])]
        elif key=='kneeling':fs=placed(cushion(.55,.15,.35),[0,.05,0],[0,0,-12])+[box([.45,.04,.3],'wood',[0,.02,0])]
        elif key in ('back_spindle','back_ladder','back_fan'):
            fs=[rod([x,0,0],[x,.65,0],.026,'woodDark') for x in [-.28,.28]]+[box([.62,.07,.07],'wood',[0,.64,0])]
            if key=='back_ladder':fs += [box([.53,.07,.045],'wood',[0,y,0],.012) for y in [.15,.31,.47]]
            else:fs += [rod([x*(.5 if key=='back_fan' else 1),.05,0],[x,.6,0],.015,'wood') for x in [-.21,-.105,0,.105,.21]]
        elif key=='back_shell':fs=[loft([[0,0,0,.23,.04],[0,.18,-.05,.28,.04],[0,.5,.01,.3,.04],[0,.68,.06,.23,.04]],'l1Slate',8)]
        elif key=='arm_loop':fs=[loft([[-.04,0,-.25,.025,.025],[0,.22,-.25,.025,.025],[0,.28,.15,.025,.025],[0,.12,.3,.025,.025],[0,0,.3,.025,.025]],'l1Slate',8)]
        else:fs=cushion(.13,.07,.5)+[box([.07,.08,.35],'l1Slate',[0,-.03,0])]
        put('seat',key,name,fs,[.7,.8,.75],material='mat.fabric' if key in ('upholstered','arm_pad','kneeling') else 'mat.wood')
    legs=names('tapered:收分桌腿基件 cabriole:曲线兽足桌腿基件 turned:车旋桌腿基件 hairpin:发夹桌腿基件 sled:滑橇支脚基件 trestle:人字支架基件 pedestal:中柱底脚基件 crossbar:十字底脚基件 folding:折叠腿架基件 cantilever:悬臂腿架基件 star:放射椅脚基件 caster:脚轮叉架基件')
    for key,name in legs:
        if key=='tapered':fs=[loft([[0,0,0,.035,.035],[0,.75,0,.07,.07]],'wood',4)]
        elif key=='cabriole':fs=[loft([[.10,0,0,.065,.045],[.05,.08,0,.04,.04],[-.04,.35,0,.04,.04],[.03,.62,0,.065,.06],[0,.75,0,.075,.06]],'wood',8)]
        elif key=='turned':fs=[lathe([[.065,0],[.04,.08],[.055,.2],[.03,.42],[.075,.59],[.05,.69],[.07,.75]],'wood',10,cap=True)]
        elif key in ('hairpin','trestle'):
            fs=[rod([x,0,0],[0,.75,.12],.023 if key=='hairpin' else .05,'l1Slate' if key=='hairpin' else 'wood') for x in [-.20,.20]]
            fs += [rod([-.20,0,0],[.20,0,0],.023,'l1Slate')] if key=='hairpin' else [box([.6,.07,.18],'wood',[0,.76,.12])]
        elif key=='sled':fs=[rod([x,0,-.25],[x,.72,-.25],.025,'l1Slate') for x in [-.25,.25]]+[rod([-.25,0,-.25],[.25,0,-.25],.025,'l1Slate'),rod([-.25,0,.25],[.25,0,.25],.025,'l1Slate')]
        elif key in ('pedestal','crossbar','star'):
            fs=[lathe([[.1,.06],[.07,.7]],'l1Slate',12,cap=True)]
            n=5 if key=='star' else 4
            if key=='pedestal':fs += [disk(.33,.065,'l1Metal')]
            else:fs += [rod([0,.10,0],[.37*math.cos(a),.025,.37*math.sin(a)],.045,'l1Slate') for a in [i*math.tau/n for i in range(n)]]
        elif key=='folding':fs=[rod([-.26,0,0],[.26,.72,0],.028,'l1Slate'),rod([.26,0,.025],[-.26,.72,.025],.028,'l1Slate'),disk(.055,.035,'l1Metal',rotation=[90,0,0],position=[0,.36,.045])]
        elif key=='cantilever':fs=[loft([[0,0,.27,.033,.033],[0,0,-.27,.033,.033],[0,.68,-.27,.033,.033],[0,.68,.25,.033,.033]],'l1Metal',8)]
        else:fs=[formbox(.20,.035,.16,'l1Metal',y=.2)]+[formbox(.035,.20,.16,'l1Slate',x=x) for x in [-.0825,.0825]]+[rod([-.13,.08,0],[.13,.08,0],.024,'l1Metal')]
        if key=='sled':fs += [rod([x,0,-.25],[x,0,.25],.025,'l1Slate') for x in [-.25,.25]]
        put('leg',key,name,fs,[.8,.85,.8],material='mat.metal' if key not in ('turned','cabriole','tapered','trestle') else 'mat.wood')
    cases=names('open_front:前开柜壳基件 through:双面通柜壳基件 corner:转角柜壳基件 beveled:斜角柜壳基件 display:三面通透柜壳基件 tall:分仓柜壳基件 locker:通风储物柜壳基件 under_sink:下水避让柜壳基件 wall_hung:吊柜悬挂壳基件 curved:圆弧端柜壳基件 cubby:蜂格储物柜芯 apothecary:小格药柜芯')
    for key,name in cases:
        fs=shell()
        if key=='through':fs=shell(open_back=True)
        if key=='corner':fs += placed(shell(.55,1,.5),[.50,0,.5],[0,90,0])
        if key=='beveled':fs=[formbox(1,.06,.5,'wood')]+[plate([[-.5,0],[.5,0],[.3,1],[-.3,1]],.04,'wood',position=[0,0,-.23])]+[box([.065,1,.5],'wood',[x,.5,0],.01,rotation=[0,0,12 if x>0 else -12]) for x in [-.4,.4]]
        if key=='display':fs=frame(1,1,.5,.055,'l1Slate')+[box([.04,.88,.46],'glass',[x,.5,0],.005,material='mat.glass') for x in [-.46,.46]]
        if key=='tall':fs += [box([.88,.06,.47],'wood',[0,y,0]) for y in [.35,.68]]
        if key=='locker':fs += [box([.80,.05,.035],'l1Slate',[0,.25+j*.12,.23],.004) for j in range(5)]
        if key=='under_sink':fs=fs[:-1]+[box([.38,.35,.045],'woodDark',[x,.25,-.23]) for x in [-.28,.28]]
        if key=='wall_hung':fs += [plate([[-.08,0],[.08,0],[.08,.35],[-.08,.14]],.075,'l1Slate',position=[x,.48,-.29]) for x in [-.3,.3]]
        if key=='curved':fs=fs[:2]+[lathe([[.45,0],[.45,1],[.39,1],[.39,0]],'wood',12,closed_profile=True,position=[0,0,-.1],scale=[1,1,.6])]
        if key in ('cubby','apothecary'):
            nx,ny=(3,3) if key=='cubby' else (4,5)
            fs += [box([.035,.88,.45],'wood',[x,.5,0]) for x in [-.5+i/nx for i in range(1,nx)]]
            fs += [box([.88,.035,.45],'wood',[0,i/ny,0]) for i in range(1,ny)]
        put('case',key,name,fs,[1.6 if key=='corner' else 1,1,1 if key=='corner' else .6],material='mat.wood')
    drawers=names('tray:浅盘抽屉芯 box:深箱抽屉芯 divided:分格抽屉芯 file:悬挂文件抽屉芯 cutlery:餐具分槽抽屉芯 mesh:网底抽屉芯 curved_front:弧面抽屉面芯 inset_pull:内凹拉手面芯 finger_pull:指槽拉手面芯 tambour:卷片柜门芯')
    for key,name in drawers:
        w,h,d=.7,.25,.5
        fs=[box([w,.035,d],'wood',[0,.0175,0])]+[box([.03,h,d],'wood',[x,h/2,0]) for x in [-.335,.335]]+[box([w-.06,h,.03],'wood',[0,h/2,z]) for z in [-.235,.235]]
        if key=='tray':fs=placed(fs,scale=[1,.42,1])
        if key=='box':fs += [formbox(.07,.04,.22,'woodDark',x=x,y=-.02) for x in [-.26,.26]]
        if key in ('divided','cutlery'):fs += [box([.025,h-.05,d-.05],'woodLight',[x,(h-.05)/2+.035,0]) for x in [-.13,.13]]+([box([w-.05,h-.05,.025],'woodLight',[0,.135,-.05])] if key=='divided' else [])
        if key=='file':fs += [rod([x,.28,-.23],[x,.28,.23],.012,'l1Metal') for x in [-.28,.28]]
        if key=='mesh':fs=fs[1:]+[rod([-.32,.035,z],[.32,.035,z],.006,'l1Metal') for z in [-.2,-.1,0,.1,.2]]
        if key=='curved_front':fs += [loft([[-.35,.14,.18,.12,.035],[0,.14,.3,.12,.035],[.35,.14,.18,.12,.035]],'wood',8)]
        if key=='inset_pull':fs += [box([.16,.055,.025],'l1Slate',[0,.18,.26],.01),box([.20,.015,.04],'woodLight',[0,.215,.27])]
        if key=='finger_pull':fs += [box([.67,.04,.07],'woodLight',[0,.25,.25],.008)]
        if key=='tambour':fs=[box([.055,.9,.04],'wood',[x,.45,0],.008) for x in [-.33,-.27,-.21,-.15,-.09,-.03,.03,.09,.15,.21,.27,.33]]+[box([.7,.025,.05],'woodDark',[0,y,-.01]) for y in [.03,.87]]
        put('drawer',key,name,fs,[.75,.95 if key=='tambour' else .32,.65],material='mat.wood')
    shelves=names('floating:隐托层板芯 bracketed:三角托层板芯 slotted:插槽层板芯 wire:金属线层板芯 angled:倾斜展示层板芯 bookend:挡书端板芯 cantilever:悬臂托架芯 pegboard:孔板挂件芯 wine:酒格层板芯 shoe:鞋槽层板芯')
    for key,name in shelves:
        fs=[box([.9,.045,.35],'wood',[0,.025,0])]
        if key=='floating':fs += [rod([x,.02,-.25],[x,.02,.1],.017,'l1Metal') for x in [-.3,.3]]
        if key=='bracketed':fs += [plate([[-.16,0],[.16,.25],[-.16,.25]],.04,'l1Slate',rotation=[0,90,0],position=[x,-.23,0]) for x in [-.3,.3]]
        if key=='slotted':fs += [box([.035,.05,.35],'l1Slate',[x,.065,0]) for x in [-.3,0,.3]]
        if key=='wire':fs=[rod([-.45,.03,z],[.45,.03,z],.009,'l1Metal') for z in [-.15,-.075,0,.075,.15]]+[rod([x,.015,-.17],[x,.015,.17],.012,'l1Slate') for x in [-.4,0,.4]]
        if key=='angled':fs=placed(fs,[0,.10,0],[-14,0,0])+[box([.9,.07,.04],'woodDark',[0,.035,.19])]
        if key=='bookend':fs=[box([.25,.03,.32],'l1Slate',[0,.015,0]),box([.025,.32,.32],'l1Slate',[-.11,.17,0])]
        if key=='cantilever':fs=[plate([[-.2,0],[.15,.08],[.2,.16],[-.2,.18]],.07,'l1Slate'),box([.12,.36,.06],'l1Slate',[0,.18,-.22])]
        if key=='pegboard':fs=[box([.28,.45,.04],'wood',[0,.225,0])]+[rod([x,y,.03],[x,y,.14],.018,'woodDark') for x in [-.08,.08] for y in [.12,.32]]
        if key=='wine':fs=placed(frame(.9,.45,.35,.03,'wood'),[0,0,0])+[box([.025,.48,.35],'wood',[x,.22,0],.004,rotation=[0,0,45]) for x in [-.3,0,.3]]
        if key=='shoe':fs += [box([.9,.10,.035],'woodDark',[0,.08,.16]),box([.9,.065,.035],'woodDark',[0,.06,-.16])]
        put('shelf',key,name,fs,[1,.65,.65],material='mat.wood')
    beds=names('slat:床架弧形排骨条 rail:床侧锁接梁 cleat:床架角托件 head_spindle:床头栅芯 head_panel:床头嵌板芯 head_tuft:软包床头芯 foot_panel:床尾护板芯 bunk_guard:双层床护栏芯 ladder_rung:床梯踏档芯 canopy_corner:床幔转角支件')
    for key,name in beds:
        if key=='slat':fs=[loft([[-.6,.02,0,.035,.06],[0,.055,0,.035,.06],[.6,.02,0,.035,.06]],'woodLight',4)]
        elif key=='rail':fs=[formbox(.12,.22,1.8,'wood')]
        elif key=='cleat':fs=[plate([[-.2,0],[.2,0],[-.2,.3]],.12,'l1Slate')]
        elif key in ('head_panel','head_tuft','foot_panel'):
            fs=frame(1.2,.7,.09,.075,'woodDark')+[box([1.02,.51,.045],'wood',[0,.35,0])]
            if key=='head_tuft':fs += cushion(1.0,.4,.07);fs += [ico([.04,.04,.025],'l1Ochre',[x,y,.06],detail=0) for x in [-.3,0,.3] for y in [.2,.4]]
            if key=='foot_panel':fs += [box([1.25,.1,.13],'woodLight',[0,.73,0])]
        elif key in ('head_spindle','bunk_guard'):
            fs=[box([1.2,.07,.09],'wood',[0,y,0]) for y in [0,.6]]+[rod([x,0,0],[x,.6,0],.019,'woodDark') for x in [-.5,-.3,-.1,.1,.3,.5]]
            if key=='bunk_guard':fs += [formbox(.08,.35,.08,'l1Metal',x=x,y=-.3) for x in [-.5,.5]]
        elif key=='ladder_rung':fs=[rod([-.4,.05,0],[.4,.05,0],.055,'wood'),box([.72,.025,.12],'l1Rubber',[0,.09,0])]
        else:fs=[rod([0,0,0],[0,.55,0],.027,'l1Metal'),rod([0,.55,0],[.4,.55,0],.027,'l1Metal'),rod([0,.55,0],[0,.55,.4],.027,'l1Metal'),ico([.09,.09,.09],'l1Ochre',[0,.59,0],detail=0)]
        if key=='rail':fs += [box([.065,.08,.16],'l1Metal',[0,.11,z]) for z in [-.93,.93]]
        put('bed',key,name,fs,[1.3,.85,2 if key=='rail' else .6],material='mat.wood')
    softs=names('box_cushion:箱形包边软垫 bolster:圆柱靠枕基件 wedge:斜坡靠垫基件 buttoned:拉扣坐垫基件 piped:滚边枕芯 base_pleat:褶边布裙片 curtain_fold:窗帘褶片 valance:弧垂帘楣片 roman_fold:罗马帘折片 rug_fringe:地毯流苏边片')
    for key,name in softs:
        fs=[]
        if key in ('box_cushion','wedge','buttoned','piped'):
            fs=cushion(.6,.18,.45,'wedge' if key=='wedge' else 'square')
            if key=='buttoned':fs += [ico([.035,.015,.035],'l1Ochre',[x,.183,z],detail=0) for x in [-.15,.15] for z in [-.1,.1]]
            if key in ('piped','box_cushion'):fs += [rod(a,b,.009,'woodLight') for a,b in [([-.28,.09,-.20],[.28,.09,-.20]),([-.28,.09,.20],[.28,.09,.20]),([-.28,.09,-.20],[-.28,.09,.20]),([.28,.09,-.20],[.28,.09,.20])]]
        elif key=='bolster':fs=[lathe([[.14,0],[.16,.05],[.16,.54],[.14,.59]],'l1Ivory',12,cap=True,rotation=[0,0,90],position=[.295,.16,0])]
        elif key in ('curtain_fold','base_pleat','roman_fold'):
            if key=='roman_fold':fs=[box([.65,.12,.09],'l1Ivory',[0,.10+i*.16,0],.035) for i in range(5)]
            else:fs=[loft([[x,0,0,.06,.055],[x,.75,0,.06,.055]],'l1Ivory',6) for x in [-.27,-.135,0,.135,.27]]
            if key=='base_pleat':fs += [box([.65,.06,.08],'l1Ochre',[0,.74,0])]
        elif key=='valance':fs=[plate([[-.45,.4],[.45,.4],[.4,.18],[.18,.03],[0,0],[-.18,.03],[-.4,.18]],.045,'l1Ivory')]
        else:fs=[box([.7,.018,.1],'l1Ivory',[0,.012,0])]+[rod([x,.01,.03],[x+.008,.01,.18],.008,'l1Ochre',sides=5) for x in [-.32,-.24,-.16,-.08,0,.08,.16,.24,.32]]
        put('soft',key,name,fs,[.95,.85,.7],material='mat.fabric',collision='none')
    kitchens=names('sink_bowl:水槽盆芯 drainboard:沥水板芯 hob_ring:炉口承托环 cooker_grate:灶台锅架芯 hood_filter:烟罩滤芯 faucet_spout:龙头弯颈芯 cabinet_toekick:橱柜踢脚芯 worktop_cutout:台面开孔边芯 backsplash:挡水拼接条 drawer_organizer:厨柜收纳格芯')
    for key,name in kitchens:
        if key=='sink_bowl':fs=[lathe([[.16,0],[.24,.05],[.30,.24],[.34,.27],[.30,.29],[.27,.24],[.21,.07],[.13,.035]],'l1Metal',12,closed_profile=True,scale=[1.5,1,1])]
        elif key=='drainboard':fs=[box([.5,.025,.4],'l1Metal',[0,.02,0])]+[box([.022,.022,.33],'l1Slate',[x,.043,0],.004) for x in [-.20,-.12,-.04,.04,.12,.20]]
        elif key=='hob_ring':fs=[ring(.2,.038,.055,'l1Rubber'),ring(.13,.026,.048,'l1Slate',position=[0,.03,0])]
        elif key=='cooker_grate':fs=[box([.5,.045,.028],'l1Rubber',[0,.05,0],.004,rotation=[0,a,0]) for a in [0,60,120]]+[ring(.18,.018,.055,'l1Rubber')]
        elif key=='hood_filter':fs=frame(.55,.4,.06,.025,'l1Metal')+[box([.035,.35,.025],'l1Slate',[x,.20,0],.002,rotation=[0,0,12]) for x in [-.20,-.12,-.04,.04,.12,.20]]
        elif key=='faucet_spout':fs=[loft([[0,0,0,.024,.024],[0,.24,0,.024,.024],[0,.32,.1,.024,.024],[0,.32,.24,.024,.024],[0,.26,.28,.024,.024]],'l1Metal',10)]
        elif key=='cabinet_toekick':fs=[plate([[-.09,0],[.09,0],[.09,.04],[.04,.04],[.04,.2],[-.02,.2],[-.02,.07],[-.09,.07]],1.2,'l1Slate')]
        elif key=='worktop_cutout':fs=placed(frame(.95,.65,.055,.12,'l1Ivory'),[0,.055,-.325],[90,0,0])
        elif key=='backsplash':fs=[plate([[-.05,0],[.06,0],[.06,.04],[.015,.07],[.015,.3],[-.05,.3]],1.2,'l1Ivory')]
        else:fs=[box([.6,.025,.4],'wood',[0,.013,0])]+[box([.025,.10,.38],'woodLight',[x,.065,0]) for x in [-.2,0,.2]]+[box([.58,.10,.025],'woodLight',[0,.065,z]) for z in [-.185,.185]]
        put('kitchen',key,name,fs,[1.25,.7,1.25],material='mat.metal')
    baths=names('basin:洗面盆芯 pedestal:洗面盆支柱芯 bathtub_rim:浴缸围边芯 shower_tray:淋浴底盘芯 shower_head:花洒喷盘芯 towel_rail:毛巾架杆芯 toilet_seat:坐圈基件 drain_grate:地漏篦芯')
    for key,name in baths:
        if key=='basin':fs=[lathe([[.06,0],[.17,.06],[.32,.25],[.35,.27],[.31,.29],[.14,.09],[.04,.025]],'l1Ivory',16,closed_profile=True,scale=[1.4,1,1])]
        elif key=='pedestal':fs=[lathe([[.18,0],[.2,.06],[.12,.16],[.10,.55],[.18,.70]],'l1Ivory',12,cap=True)]
        elif key in ('bathtub_rim','toilet_seat'):fs=[lathe([[.45,0],[.47,.06],[.36,.07],[.35,0]],'l1Ivory',20,closed_profile=True,scale=[1,1,1.65 if key=='bathtub_rim' else 1.3])]
        elif key=='shower_tray':fs=[box([.9,.05,.9],'l1Ivory',[0,.025,0])]+[box([.9,.05,.045],'l1Ivory',[0,.075,z]) for z in [-.4275,.4275]]+[box([.045,.05,.81],'l1Ivory',[x,.075,0]) for x in [-.4275,.4275]]
        elif key=='shower_head':fs=[disk(.18,.04,'l1Metal'),disk(.15,.02,'l1Slate',y=-.015)]+[ico([.015,.008,.015],'l1Ivory',[r*math.cos(a),-.020,r*math.sin(a)],detail=0) for r,n in [(.065,6),(.12,10)] for a in [i*math.tau/n for i in range(n)]]
        elif key=='towel_rail':fs=[rod([-.32,.10,0],[.32,.10,0],.017,'l1Metal')]+[rod([x,.1,0],[x,.1,-.1],.023,'l1Metal') for x in [-.3,.3]]
        else:fs=placed(frame(.3,.3,.03,.025,'l1Metal'),[0,.03,-.15],[90,0,0])+[box([.023,.03,.25],'l1Slate',[x,.015,0]) for x in [-.09,-.045,0,.045,.09]]
        put('bath',key,name,fs,[1,.8,1.7 if key=='bathtub_rim' else 1],material='mat.ceramic')
    fixtures=names('hinge_cup:暗铰杯芯 hinge_leaf:合页单片芯 latch_plate:柜锁扣板芯 runner:抽屉导轨芯 lift_stay:上翻支撑杆芯 hook:壁挂钩芯 switch_plate:墙壁开关面芯 outlet_plate:墙壁插座面芯 vent:室内通风格栅芯 conduit:电缆护槽芯')
    for key,name in fixtures:
        if key=='hinge_cup':fs=[round_tube(.07,.048,.035,'l1Metal',12),box([.23,.018,.09],'l1Metal',[0,.034,0])]
        elif key=='hinge_leaf':fs=[box([.12,.18,.016],'l1Metal',[.06,.09,0])]+[round_tube(.024,.012,.05,'l1Metal',10,position=[0,y,0]) for y in [.005,.115]]
        elif key=='latch_plate':fs=frame(.12,.23,.025,.025,'l1Metal')+[box([.05,.06,.065],'l1Slate',[.05,.115,-.02])]
        elif key=='runner':fs=[plate([[-.035,0],[.035,0],[.035,.07],[.025,.07],[.025,.014],[-.025,.014],[-.025,.07],[-.035,.07]],.6,'l1Metal'),box([.035,.022,.48],'l1Slate',[0,.026,.10])]
        elif key=='lift_stay':fs=[rod([0,0,0],[0,.38,.1],.024,'l1Slate'),rod([0,.28,.075],[0,.6,.16],.012,'l1Metal'),ring(.04,.017,.035,'l1Metal',rotation=[90,0,0],position=[0,.62,.16])]
        elif key=='hook':fs=[box([.08,.18,.018],'l1Slate',[0,.09,0]),loft([[0,.06,.02,.018,.018],[0,.02,.1,.018,.018],[0,.06,.15,.018,.018],[0,.12,.14,.018,.018]],'l1Metal',8)]
        elif key in ('switch_plate','outlet_plate'):
            fs=[box([.14,.14,.018],'l1Ivory',[0,.07,0])]
            if key=='switch_plate':fs += [box([.08,.09,.015],'l1Slate',[0,.07,.018],.006,rotation=[-8,0,0])]
            else:fs += [box([.014,.027,.012],'l1Slate',[x,.073,.018]) for x in [-.024,.024]]+[disk(.009,.013,'l1Slate',rotation=[90,0,0],position=[0,.037,.015])]
        elif key=='vent':fs=frame(.45,.28,.06,.025,'l1Ivory')+[box([.39,.025,.07],'l1Slate',[0,y,0],.003,rotation=[20,0,0]) for y in [.065,.115,.165,.215]]
        else:fs=[plate([[-.08,0],[.08,0],[.08,.05],[.06,.05],[.06,.015],[-.06,.015],[-.06,.05],[-.08,.05]],.6,'l1Ivory')]
        put('fixture',key,name,fs,[.7,.75,.7],material='mat.metal')
    finish('interior',118)
