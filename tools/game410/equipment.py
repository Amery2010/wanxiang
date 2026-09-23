"""Character attachment pieces and stylized game weapon profiles, not CAD plans."""
from .common import *
from .common import author as emit

def author():
    def put(key,name,fs,size,**kw):return emit('equipment','character',key,name,fs,size,collision='none',**kw)
    fs=[]
    for j,(y,w,h) in enumerate([(.07,.22,.10),(.17,.29,.14),(.29,.26,.12)]):
        fs.append(profile_z([[-.015,y,w*.5,h*.5],[.045,y,w*.54,h*.62],[.09,y,w*.42,h*.48]],C('gMetal' if j==1 else 'gSteel'),8))
    fs.append(detail(block([.055,.10,.022],[0,.19,.102],C('gCopper'),.007)))
    put('knee_guard','三段叠片护膝',fs,[.32,.38,.13],purpose='膝盖正面叠片护甲，保留后方绑带安装面',ports=[port('knee',[0,.18,-.015],[0,0,-1])])
    fs=[spin([(.075,0),(.105,0),(.13,.21),(.11,.27),(.085,.27),(.10,.21)],'gLeather',12)]
    fs.append(profile_z([[-.03,.29,.12,.09],[.035,.29,.14,.095],[.09,.27,.10,.07]],C('gSteel'),8))
    for x in (-.066,-.022,.022,.066):fs.append(detail(block([.025,.07,.02],[x,.33,.105],C('gMetal'),.004)))
    put('fingerless_gauntlet','露指护手套壳',fs,[.28,.39,.27],purpose='开放腕孔与掌背装甲，不包含可动画手指')
    fs=[spin([(.10,0),(.145,0),(.15,.09),(.13,.24),(.095,.24),(.11,.08)],'gSteel',12)]
    fs.append(detail(plate([[-.075,.07],[.075,.07],[.07,.21],[-.07,.21]],.024,'gCopper',at=(0,0,.145))))
    put('boot_cuff','开放装甲靴护踝',fs,[.30,.24,.34],purpose='有贯通腿孔的靴口护甲圈')
    fs=[spin([(0,0),(.115,0),(.14,.52),(.17,.70),(.142,.71),(.12,.53),(.09,.04),(0,.04)],'gLeather',14)]
    for y in (.13,.50):fs.append(detail(ring_y(.13+(y-.13)*.05,y,.026,.018,'gCopper',14)))
    fs.append(tube_curve([[-.08,.08,0],[-.25,.18,0],[-.24,.47,0],[-.12,.58,0]],.023,'gLeather'))
    put('open_quiver','开放箭袋壳',fs,[.45,.71,.35],purpose='箭袋空腔、袋底与背带；箭由外部部件提供')
    fs=[spin([(.06,0),(.23,0),(.245,.035),(.17,.055),(.14,.15),(.07,.21),(0,.21),(0,.19),(.12,.13),(.13,.04),(.06,.035)],'gMetal',16)]
    for k in range(6):
        a=k*math.tau/6;fs.append(detail(cyl(.018,.035,'gCopper',at=(.205*math.cos(a),.035,.205*math.sin(a)),sides=8)))
    put('shield_boss','铆边圆盾中央护脐',fs,[.49,.24,.49],purpose='空心拱形盾脐和可识别铆边')
    stations=[(0,0,.04),(.18,.015,.046),(.45,.07,.05),(.75,.17,.038),(.97,.31,.006)]
    ps=[]
    for y,x,w in stations:ps += [[x-w,y,0],[x,y,.016],[x+w,y,0],[x,y,-.016]]
    ff=[]
    for j in range(len(stations)-1):
        for k in range(4):ff.append([j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k])
    ff += [[3,2,1,0],[16,17,18,19]]
    put('curved_sabre_blade','弧刃单脊刀身', [mesh(ps,ff,C('gMetal'))],[.39,.97,.032],purpose='有可读弯曲轮廓与菱形截面的游戏武器刀身')
    fs=[plate([[-.075,0],[.10,.035],[.08,.25],[.05,.35],[.14,.78],[.05,.92],[-.08,.86],[-.035,.34],[-.12,.19]],.085,'gWoodDark')]
    fs += [detail(block([.044,.43,.025],[.015,.59,.056],C('gMetal'),.005)),detail(block([.16,.055,.10],[.018,.36,0],C('gSteel'),.01))]
    put('crossbow_stock','手持弩托木坯',fs,[.26,.92,.125],purpose='角色手持弩的独立枪托式木坯，不含弦或发射逻辑')
    fs=[sweep([[-.58,.10,0],[-.38,.03,.02],[0,0,.06],[.38,.03,.02],[.58,.10,0]],rect(.052,.032),C('gWood'))]
    for x in (-.55,.55):fs.append(detail(block([.048,.07,.044],[x,.093,0],C('gSteel'),.008)))
    put('crossbow_limb','反曲弩臂横片',fs,[1.22,.15,.10],purpose='有反曲端部和中央安装面的横向弩臂',ports=[port('mount',[0,0,.06],[0,-1,0]),port('string.left',[-.58,.10,0],[-1,0,0],[0,1,0]),port('string.right',[.58,.10,0],[1,0,0],[0,1,0])])
    fs=[spin([(0,0),(.10,0),(.13,.10),(.075,.17),(0,.17)],'gCopper',12)]
    for k in range(3):
        a=k*math.tau/3
        fs.append(tube([[.075*math.cos(a),.10,.075*math.sin(a)],[.20*math.cos(a),.30,.20*math.sin(a)],[.12*math.cos(a),.44,.12*math.sin(a)]],[.027,.023,.009],C('gCopper'),8))
    put('orb_claw','三爪法球承托',fs,[.45,.46,.45],purpose='法杖和祭坛通用的中空三爪球体承托')
    fs=[spin([(.15,0),(.18,0),(.18,.10),(.15,.10)],'gLeather',16)]
    fs.append(detail(plate(rect(.075,.10,(0,.055),.012),.023,'gCopper',holes=[rect(.044,.063,(0,.055),.006)],at=(0,0,.19))))
    for sign in (-1,1):
        # Closed thigh loop, suspended at front and rear from the waist belt.
        fs += placed([ring_y(.096,-.20,.035,.020,'gLeather',14)],position=(sign*.12,0,.02))
        for z in (-.074,.114):
            fs.append(tube([[sign*.13,.02,z*.72],[sign*.17,-.11,z],[sign*.16,-.166,z]],.015,C('gLeather'),6))
    put('climbing_harness','腰腿分离攀爬束带',fs,[.4,.32,.42],purpose='角色腰带与两侧腿带外观；需按角色体型适配',anchor='center',ports=[port('waist',[0,.05,0],[0,1,0],[1,0,0])])
    fs=[spin([(.062,0),(.093,0),(.097,.25),(.063,.25)],'gLeather',12)]
    fs += [basebox([.035,.32,.028],[x,0,-.10],C('gLeather'),bevel=.006) for x in (-.045,.045)]
    fs.append(detail(block([.14,.03,.022],[0,.22,.103],C('gCopper'),.006)))
    put('flask_holster','腰挂水壶皮套',fs,[.2,.32,.235],purpose='可插入独立水壶的开放底筒与双挂耳')
    outline=[[-.1,0],[.10,0],[.72,.82],[.38,.72],[.15,1.02],[.06,.61],[-.17,.73]]
    fs=[plate(outline,.02,'gCloth')]
    for a,b in [([0,0,.022],[.72,.82,.022]),([0,0,.022],[.15,1.02,.022]),([0,0,.022],[-.17,.73,.022])]:fs.append(tube([a,b],[.022,.010],C('gWoodDark'),6))
    put('folded_glider_wing','折叠滑翔翼单侧片',fs,[.92,1.05,.06],purpose='骨条与有厚度翼布组成的单侧滑翔装备')
