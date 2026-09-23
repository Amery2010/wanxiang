"""Space-station profiles: open cable routes, hollow docking and readable panels."""
from .common import *
from .common import author as emit

def author():
    def put(key,name,fs,size,**kw):return emit('scifi','architecture',key,name,fs,size,**kw)
    outer=[[-1,0],[-1,2.2],[-.69,2.65],[.69,2.65],[1,2.2],[1,0],[.70,0],[.70,2.12],[.48,2.36],[-.48,2.36],[-.70,2.12],[-.70,0]]
    fs=[plate(outer,.37,'gSteel')]
    for x in (-.84,.84):fs.append(detail(block([.045,1.35,.03],[x,1.16,.20],C('gGlow'),.009)))
    fs.append(detail(block([.72,.065,.04],[0,2.51,.20],C('gAmber'),.01)))
    put('bulkhead_frame','切角舱门框',fs,[2,2.65,.42],purpose='有开放通道与独立门叶基准的舱壁门框',ports=[port('datum.mount',[0,0,0],[0,-1,0]),port('leaf',[0,0,0],[0,0,1]),port('passage',[0,1.15,0],[0,0,1])])
    fs=[plate([[-.66,0],[.66,0],[.66,2.08],[.46,2.31],[-.46,2.31],[-.66,2.08]],.13,'gMetal'),
        plate([[-.55,.14],[.55,.14],[.55,1.60],[.37,1.83],[-.37,1.83],[-.55,1.60]],.021,'gSteel',at=(0,0,.077))]
    fs += [detail(block([.04,1.45,.018],[x,.93,.096],C('gGlow'),.006)) for x in (-.40,.40)]
    fs.append(detail(plate([[-.20,1.96],[.20,1.96],[.29,2.06],[-.29,2.06]],.02,'gAmber',at=(0,0,.078))))
    put('bulkhead_leaf','舱门独立闭合叶',fs,[1.32,2.31,.22],purpose='匹配切角舱框的独立滑动门叶；不开假孔',ports=[port('datum.mount',[0,0,0],[0,-1,0]),port('slide',[0,1.15,0],[1,0,0],[0,1,0])])
    path=[[-.92,0,0],[-.92,1.90,0],[-.62,2.25,0],[.62,2.25,0],[.92,1.90,0],[.92,0,0]]
    fs=[sweep(path,rect(.16,.20),C('gSteel'))]
    for sign in (-1,1):fs.append(detail(block([.07,.65,.035],[sign*.925,.9,.115],C('gGlow'),.01)))
    put('corridor_rib','六折角廊道支肋',fs,[2.08,2.40,.24],purpose='科幻走廊结构节律用开放支肋')
    fs=[plate(rect(.95,.95,(0,.475),.12),.08,'gSteel',holes=[rect(.21,.055,(0,.77),.02)]),
        detail(plate(rect(.77,.50,(0,.365),.07),.015,'gMetal',at=(0,0,.052)))]
    for x in (-.35,.35):
        for y in (.13,.82):fs.append(detail(plate(circle(.027,(x,y),8),.026,'gCopper',at=(0,0,.05))))
    put('service_hatch','带握槽检修盖板',fs,[.95,.95,.10],purpose='有实际提握槽的可拆卸地板或墙板')
    path=[[.58*math.cos(math.pi*k/24),0,.58*math.sin(math.pi*k/24)] for k in range(13)]
    section=[[-.17,0],[.17,0],[.17,.16],[.13,.16],[.13,.035],[-.13,.035],[-.13,.16],[-.17,.16]]
    fs=[sweep(path,section,C('gSteel'))]
    put('cable_tray_elbow','开放线槽九十度弯头',fs,[.8,.35,.8],purpose='有壁厚且保持上方开口的桥架弯头')
    fs=[]
    for a,b in [([-.52,.11,0],[.52,.11,0]),([0,.11,0],[0,.11,.50])]:fs.append(pipe([a,b],.105,.02,C('gMetal'),12))
    # Externally joined conduits: no assertion of a Boolean-clean fluid manifold.
    for x,z in [(-.50,0),(.50,0),(0,.48)]:
        direction=(0,0,1) if z else (1,0,0)
        fs.append(detail(pipe([[x-direction[0]*.035,.11,z-direction[2]*.035],[x+direction[0]*.035,.11,z+direction[2]*.035]],.13,.04,C('gSteel'),12)))
    put('conduit_branch','T形线缆护管节点',fs,[1.08,.25,.66],purpose='外观线缆护管分流节点，不作为内部流体布尔模型')
    # A longitudinal U-section: open TOP, not a tube with only axial openings.
    stations=[(-.94,.26,.62,.30),(-.80,.40,.64,.44),(-.58,.47,.64,.50),(.62,.47,.64,.50),(.86,.36,.64,.38),(.98,.25,.64,.26)]
    ps=[];ff=[];n=13
    for z,w,y,d in stations:
        ps += [[-w*math.cos(math.pi*k/(n-1)),y-d*math.sin(math.pi*k/(n-1)),z] for k in range(n)]
        ps += [[-(w-.045)*math.cos(math.pi*k/(n-1)),y-(d-.048)*math.sin(math.pi*k/(n-1)),z] for k in range(n-1,-1,-1)]
    for j in range(len(stations)-1):
        for k in range(2*n):ff.append([j*2*n+k,j*2*n+(k+1)%(2*n),(j+1)*2*n+(k+1)%(2*n),(j+1)*2*n+k])
    ff += [list(range(2*n-1,-1,-1)),list(range((len(stations)-1)*2*n,len(stations)*2*n))]
    fs=[mesh(ps,ff,C('gSteel'))]
    for z,w,y,d in (stations[0],stations[-1]):
        outline=[[-w*math.cos(math.pi*k/12),y-d*math.sin(math.pi*k/12)] for k in range(13)]
        fs.append(plate(outline,.04,'gSteel',at=(0,0,z)))
    fs += [basebox([.65,.15,.24],[0,0,z],C('gMetal')) for z in (-.53,.53)]
    for sign in (-1,1):fs.append(detail(block([.025,.035,1.14],[sign*.474,.618,.015],C('gGlow'),.008)))
    put('cryopod_shell','休眠舱开放壳体',fs,[1.0,.66,1.96],purpose='顶部开放、有端壁和壁厚的休眠舱壳',ports=[port('datum.mount',[0,0,0],[0,-1,0]),port('interior',[0,.20,0],[0,1,0])])
    fs=[annulus_xy(.46,.31,.16,'gSteel',center=(0,.58)),basebox([.68,.16,.40],[0,0,0],C('gMetal')),
        block([.19,.16,.24],[0,.21,0],C('gSteel'))]
    for k in range(8):
        a=k*math.tau/8;fs.append(detail(plate(rect(.09,.12,(.40*math.cos(a),.58+.40*math.sin(a)),.012),.022,'gCopper',at=(0,0,.095))))
    put('coil_carrier','反应堆线圈支架',fs,[.92,1.04,.40],purpose='保留中央通道的环形线圈载架')
    fs=[spin([(0,0),(.44,0),(.49,.06),(.40,.17),(.30,.22),(.23,.22),(.23,.18),(0,.18)],'gSteel',20),
        cyl(.22,.026,'gGlow',at=(0,.185,0),sides=24)]
    for k in range(4):
        a=k*math.tau/4
        fs.append(detail(block([.065,.08,.17],[.36*math.cos(a),.17,.36*math.sin(a)],C('gMetal'),.014,rot=(0,-k*90,0))))
    put('hologram_base','全息投影空心底座',fs,[.98,.24,.98],purpose='独立发光透镜与外框，不包含全息粒子特效')
    fs=[spin([(.15,0),(.27,0),(.32,.07),(.29,.18),(.21,.20),(.17,.13)],'gSteel',16)]
    for k in range(3):
        a=k*math.tau/3
        fs.append(block([.05,.25,.08],[.22*math.cos(a),.25,.22*math.sin(a)],C('gCopper'),.01,rot=(0,-k*120,0)))
    put('canister_socket','三爪能源罐底座',fs,[.64,.375,.64],purpose='能量罐安装底杯，中央保留放置空间')
    fs=[spin([(.64,0),(.78,0),(.80,.10),(.78,.18),(.64,.18)],'gSteel',24)]
    for y in (.035,.085,.135):fs.append(detail(ring_y(.805,y,.015,.015,'gCloth',24)))
    put('docking_seal','中空对接密封环',fs,[1.64,.18,1.64],purpose='舱段连接处具有真实孔径的软硬结合密封环')
    fs=[spin([(.13,0),(.17,0),(.19,.10),(.26,.38),(.41,.65),(.43,.70),(.39,.70),(.36,.64),(.22,.38),(.15,.10)],'gSteel',20)]
    fs.append(detail(ring_y(.21,.09,.055,.034,'gCopper',20)))
    put('thruster_bell','内凹钟形推进喷口',fs,[.86,.70,.86],purpose='内外表面连续且出口开放的推进器钟罩')
