"""Aircraft sections, vehicle shell surfacing, marine and chassis connections."""
from .common import *
from .aero import foil
from .props import curve2,seam_on
from .nature import lamina
from .terrain_robot import triangulated_cap


def reflect(f,axis):
    g=deepcopy(f)
    g['points']=[[(-v if k==axis else v) for k,v in enumerate(p)] for p in f['points']]
    g['faces']=[list(reversed(p)) if isinstance(p,list) else {**p,'v':list(reversed(p['v']))} for p in f['faces']]
    return g


def author():
    stations=[(-2.20,.90,.76,.10),(-1.80,.96,.755,.060),(-.85,1.02,.75,.027),(.30,.97,.75,.029),(1.20,.73,.76,.070),(1.95,.33,.79,.145),(2.38,.090,.80,.223),(2.50,.016,.795,.295)]
    pp=[];rings=[]
    for z,w,top,bottom in stations:
        t=min(.050,w*.23)
        sec=[[-w,top],[-w*.95,bottom+.38],[-w*.70,bottom+.075],[0,bottom],[w*.70,bottom+.075],[w*.95,bottom+.38],[w,top],
             [w-t,top],[w*.95-t,bottom+.39],[w*.70-t,bottom+.126],[0,bottom+.058],[-w*.70+t,bottom+.126],[-w*.95+t,bottom+.39],[-w+t,top]]
        rings.append(sec);pp.extend([[x,y,z] for x,y in sec])
    n=len(rings[0]);ff=[]
    for j in range(len(stations)-1):
        for k in range(n):ff.append([j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k])
    ff+=triangulated_cap(rings[0],0,True)+triangulated_cap(rings[-1],(len(stations)-1)*n)
    fs=[mesh(pp,ff,'#477B76')]
    # End walls close the interior water volume; the gunwale remains open.
    rear=[[-.855,.754],[-.812,.486],[-.596,.220],[0,.151],[.596,.220],[.812,.486],[.855,.754]]
    fs.append(plate(rear,.055,'#477B76',at=(0,0,-2.168)))
    front=[[-.014,.792],[-.012,.630],[-.007,.411],[0,.350],[.007,.411],[.012,.630],[.014,.792]]
    fs.append(plate(front,.030,'#477B76',at=(0,0,2.480)))
    for s in (-1,1):
        path=[[s*(w-.014),top+.006,z] for z,w,top,b in stations]
        fs.append(tube(path,[.022,.025,.025,.025,.023,.019,.012,.0045],'woodLight',10))
    fs.append(tube([[-.887,.766,-2.186],[.887,.766,-2.186]],[.026,.026],'woodLight',10))
    apply('exp.transport.boat_hull',fs,'船壳以连续双层U形截面重建龙骨、舷侧与船艏；增加实际艉封板和艏端闭合，保留开放甲板与舷口木护边。',dimensioned=False,contracts={'open_deck':True,'stern_transom':True,'keel_closed':True,'bow_closed':True})

    body=profile_z([(-2.70,.98,.035,.050),(-2.44,1.025,.091,.107),(-1.80,1.087,.226,.254),(-1.10,1.15,.352,.38),(-.43,1.17,.405,.434),(.40,1.18,.437,.461),(1.06,1.17,.405,.402),(1.68,1.11,.304,.301),(2.08,1.09,.184,.164),(2.28,1.085,.040,.050)],'#DFD8BF',24)
    fs=[body]
    canopy=profile_z([(-.62,1.493,.162,.037),(-.39,1.556,.273,.132),(-.09,1.593,.319,.206),(.36,1.584,.324,.230),(.70,1.531,.262,.164),(.95,1.423,.118,.037)],'#496D79',20,material='mat.vehicleGlass')
    fs.append(canopy)
    for z in (-.34,.68):
        # Upper half arch of the local canopy is sampled and projected.
        ys=[]
        for x in np.linspace(-.23,.23,15):
            try:ys.append([x,surface_coordinate(canopy,[x,z],axis=1)+.004,z])
            except ValueError:continue
        fs.append(tube(ys,[.009]*len(ys),'#768C8D',8))
    fin=plate([[-.72,0],[.44,0],[.27,.25],[-.12,1.08],[-.48,1.04],[-.63,.52]],.075,'#477B76',at=(0,1.07,-2.02),rotation=[0,90,0]);fs.append(fin)
    apply('exp.transport.fuselage',fs,'机身由鼻罩、座舱肩部、机腹和尾锥的多层截面连续塑形；座舱泡罩下缘埋入机身，弧形框条按玻璃表面投射。',dimensioned=False,detail=[1,2,3])

    top=[[-2.12,.42],[-2.12,.89],[-1.97,.963],[-1.27,1.015],[-.78,1.633],[-.65,1.685],[.85,1.685],[.98,1.62],[1.49,1.091],[2.04,.956],[2.12,.865],[2.12,.42],[1.70,.42]]
    for a in np.linspace(0,math.pi,17)[1:]:top.append([1.27+.43*math.cos(a),.42+.43*math.sin(a)])
    top.append([-.79,.42])
    for a in np.linspace(0,math.pi,17)[1:]:top.append([-1.22+.43*math.cos(a),.42+.43*math.sin(a)])
    def half_width(z,y):
        cabin=.839-.177*max(0,min(1,(y-.98)/.69))
        ends=.040*max(0,(abs(z)-1.75)/.37)
        belt=.018*math.exp(-((y-.94)/.095)**2)
        return cabin-ends+belt
    local=lamina(top,'#457D78',zfront=half_width,zback=lambda z,y:-half_width(z,y),res=(36,19))
    sidefs=[local]
    windows=[[[ -.73,1.11],[-.065,1.11],[-.065,1.595],[-.61,1.595]],[[.025,1.11],[1.326,1.11],[.887,1.584],[.025,1.595]]]
    for outline in windows:
        patch=surface_patch(local,outline,'#456774',.003);sidefs.extend([patch,reflect(patch,2)])
    for z in (-.285,.29):
        patch=surface_patch(local,rect(.145,.025,(z,1.04),.007),'#A7B2A7',.004);sidefs.extend([patch,reflect(patch,2)])
    for zc in (-1.22,1.27):
        outline=[[zc+.478*math.cos(a),.42+.478*math.sin(a)] for a in np.linspace(0,math.pi,22)]
        outline += [[zc+.435*math.cos(a),.42+.435*math.sin(a)] for a in np.linspace(math.pi,0,22)]
        patch=surface_patch(local,outline,'#365953',.0025);sidefs.extend([patch,reflect(patch,2)])
    # Local (longitudinal Z,Y,width X) rotates into the public vehicle frame.
    for f in sidefs:f['points']=[[-p[2],p[1],p[0]] for p in f['points']]
    body=sidefs[0];fs=sidefs
    windshield=[[-.715,1.115],[.715,1.115],[.625,1.567],[-.625,1.567]]
    fs.append(surface_patch(body,windshield,'#527883',.0035))
    mirrored=reflect(body,2)
    backglass=surface_patch(mirrored,[[-.71,1.097],[.71,1.097],[.605,1.558],[-.605,1.558]],'#456774',.0035)
    fs.append(reflect(backglass,2))
    for s in (-1,1):
        fs.append(block([.24,.080,.037],[s*.56,.783,2.104],'#D7CC9F',.012))
        fs.append(block([.17,.16,.033],[s*.604,.758,-2.113],'#A95541',.010))
    fs.append(block([1.48,.087,.062],[0,.543,2.092],'#3E4C4B',.014))
    apply('exp.transport.utility_body',fs,'车体重建收窄座舱、肩线和渐变侧面；轮拱、车窗及把手依实际壳面贴合，A/B柱留出明确厚度，并补车首尾的识别细节。',dimensioned=False)

    wing=foil([(0,1.22,-.030,.035,.16,0),(.34,1.13,-.046,.035,.15,-.3),(1.1,.91,-.080,.039,.14,-.6),(2.15,.65,-.121,.048,.12,-1.0),(2.85,.495,-.145,.053,.10,-1.5),(3.0,.445,-.16,.055,.095,-1.8)],'#477B76',22)
    fs=[]
    for side in ('right','left'):
        f=deepcopy(wing) if side=='right' else reflect(wing,0)
        f['enabled']=choice('side',{'right':side=='right','left':side=='left'})
        fs.append(f)
    apply('exp.transport.wing',fs,'渐缩机翼重建圆润前缘、凸上翼面、薄后缘和根尖厚度变化；保留左右安装开关，镜像同时修正面绕序。',dimensioned=False,contracts={'side_switch_retained':True,'closed_airfoil':True})

    fs=[foil([(.0,.11,0,.010,.20,17),(.14,.23,-.012,.010,.16,14),(.45,.25,-.040,.009,.13,11),(1.5,.205,-.105,.004,.10,7),(1.95,.15,-.145,.004,.08,4),(2,.081,-.153,.004,.08,3)],'#5D727E',20)]
    fs.append(spin([(.060,-.065),(.060,.088),(.053,.099),(.030,.099),(.030,-.065)],'metal',24))
    apply('l1.vehicle.aero.rotor_blade',fs,'桨叶分为夹持根、扩弦段和渐细尖端，并明确径向桨距变化；根部进入带孔夹持套，不再是光杆加薄直条。')
    fs=[foil([(0,.65,0,0,.16,0),(.22,.59,-.106,.011,.15,-.25),(.80,.435,-.38,.035,.13,-.8),(1.40,.28,-.70,.071,.11,-1.6),(1.6,.218,-.80,.094,.095,-2)],'#5D727E',22)]
    fs.append(plate([[1.51,.086],[1.63,.086],[1.646,.244],[1.605,.282],[1.553,.246]],.155,'#83999D',at=(0,0,-.80)))
    apply('l1.vehicle.aero.swept_wing',fs,'后掠翼使用连续气动截面，根部厚、翼尖薄，并形成轻微上反；翼梢小翼底部接入翼尖，不是悬挂小方块。')
    fs=[foil([(0,.65,0,0,.16,0),(.2,.62,-.018,.008,.15,-.2),(.85,.49,-.085,.018,.135,-.7),(1.45,.378,-.175,.032,.11,-1.2),(1.6,.348,-.20,.036,.10,-1.4)],'#5D727E',22)]
    apply('l1.vehicle.aero.wing',fs,'直翼段建立前缘鼻部、上翼面弧度与薄后缘，翼根到翼尖连续减薄；保持原有单侧安装范围。')

    pp=[];n=33
    # Arched sheet has a thin lip, broad crown and folded return, not a torus.
    section=[(.411,-.151),(.418,-.171),(.446,-.176),(.482,-.151),(.549,-.100),(.554,.113),(.539,.166),(.504,.173),(.491,.155),(.522,.138),(.530,.107),(.525,-.090),(.469,-.135),(.440,-.148),(.431,-.146)]
    for j,a in enumerate(np.linspace(0,math.pi,n)):
        for r,z in section:pp.append([r*math.cos(a),r*math.sin(a),z])
    m=len(section);ff=[]
    for j in range(n-1):
        for k in range(m):ff.append([j*m+k,j*m+(k+1)%m,(j+1)*m+(k+1)%m,(j+1)*m+k])
    ff+=triangulated_cap(section,0,True)+triangulated_cap(section,(n-1)*m)
    apply('l1.vehicle.body.fender',[mesh(pp,ff,'#5D727E',smooth_angle=35)],'翼子板按钣金薄壳重建：轮口有翻边、拱冠有宽度、后缘有回折，保留半圆轮拱且不再等厚管环。')

    fs=[]
    for j,L in enumerate((.75,.635,.52,.405)):
        def spring(u,v,L=L,j=j):
            x=(u*2-1)*L;return [x,.108+.092*(x/.75)**2-j*.022,(v*2-1)*.090]
        fs.append(grid_shell(spring,28,2,.014,'metal' if j%2==0 else 'metalLight'))
    for s in (-1,1):fs.append(plate(circle(.035,(s*.75,.219),24),.18,'metal',holes=[circle(.020,(s*.75,.219),20)]))
    for x in (-.26,.26):fs.append(plate(rect(.056,.130,(x,.091),.003),.204,'metalDark',holes=[rect(.030,.104,(x,.091),.002)]))
    fs.append(plate(circle(.012,(0,.103),16),.21,'metalDark'))
    apply('l1.vehicle.chassis.leafspring',fs,'钢板簧主片在上、短片逐层承托于下，各层独立有厚度；增加两端卷耳、侧抱箍及中心定位，保留弧形弹性轮廓。')

    fs=[]
    for s in (-1,1):
        path=bezier([[s*.477,.031,.010],[s*.37,.030,.170],[s*.156,.041,.43],[s*.029,.033,.541]],17)
        fs.append(sweep(path,rect(.065,.041,r=.006),'metal'))
        fs.append(spin([(.086,0),(.086,.119),(.075,.127),(.042,.127),(.042,0)],'metal',24,at=(s*.5,0,0)))
    fs.append(tube([[-.29,.031,.23],[.29,.031,.23]],[.019,.019],'metal',10))
    fs.append(spin([(0,-.014),(.085,-.014),(.085,.066),(.068,.095),(0,.095)],'metalDark',24,at=(0,0,.55)))
    fs.append(spin([(0,.071),(.035,.071),(.040,.088),(.022,.108),(.021,.167),(0,.169)],'metalLight',20,at=(0,0,.55)))
    apply('l1.vehicle.chassis.wishbone',fs,'两支叉臂向同一球铰座汇聚，内侧两衬套与外侧球头形成三点连接；增加轻量横撑，避免只见U形断开的杆件。')

    blade=foil([(0,.153,0,0,.23,49),(.12,.29,0,0,.18,42),(.26,.395,0,0,.14,34),(.41,.325,0,0,.10,27),(.50,.17,0,0,.075,22),(.53,.027,0,0,.075,20)],'copper',24,camber=.028)
    blade['points']=[[p[2]+.247*math.sin((p[0]/.53)*math.pi*.5),p[0],p[1]+.18*(p[0]/.53)**1.5] for p in blade['points']]
    apply('l1.vehicle.marine.propeller',[blade],'保留单桨叶部件语义；径向增宽再收尖，叶面有弦向弧度、递变桨距与后掠，根部截面满足后续接入轮毂。')

    from shapely.geometry import Polygon,Point,box as sb
    outer=curve2([[-.111,0],[.111,0],[.118,.251],[.266,.294],[.331,.367],[.332,.502],[.274,.565],[.172,.584],[.115,.549],[.099,.499],[.192,.472],[.213,.410],[.145,.378],[.034,.394],[-.045,.446],[-.119,.423],[-.170,.343],[-.145,.271],[-.113,.224]],3)
    # Hook body is open at the coupling mouth; hinge bore passes through its cheek.
    shape=Polygon(outer);bore=Point(.251,.358).buffer(.027,quad_segs=6)
    fs=[plate(list(shape.exterior.coords)[:-1],.220,'metal',holes=[list(bore.exterior.coords)[:-1]])]
    knuckle=curve2([[-.060,.414],[-.102,.445],[-.107,.498],[-.066,.545],[.019,.543],[.053,.505],[.01,.491],[-.024,.472],[-.023,.435]],3)
    fs.append(plate(knuckle,.19,'metalDark'))
    fs.append(plate(circle(.023,(.251,.358),20),.241,'metalLight'))
    apply('l1.vehicle.rail.coupler',fs,'车钩重建杆颈、钩喉与弧形钩舌，侧部具有独立铰销和贯穿孔；用负形表达接合口，替换错位双方块。')

    profile=[(.271,0),(.31,.008),(.365,.036),(.408,.076),(.430,.125),(.437,.19),(.430,.255),(.408,.304),(.365,.344),(.310,.372),(.271,.38),(.258,.357),(.260,.312),(.260,.068),(.258,.025)]
    fs=[spin(profile,'rubber',48)]
    for i in range(16):
        a=i*math.tau/16
        for s in (-1,1):
            pp=[];n=7
            for j in range(n):
                t=j/(n-1);y=.190+s*.135*t;angle=a+.26*t;rad=float(np.interp(y,[.055,.076,.125,.19,.255,.304,.325],[.389,.408,.430,.437,.430,.408,.389]))-.004
                for rr,da in [(rad,-.038),(rad,.038),(rad+.028,.034),(rad+.028,-.034)]:pp.append([rr*math.cos(angle+da),y,rr*math.sin(angle+da)])
            ff=[]
            for j in range(n-1):
                for k in range(4):ff.append([j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k])
            ff += [[3,2,1,0],list(range((n-1)*4,n*4))];fs.append(mesh(pp,ff,'#252C2B',material='mat.rubber'))
    apply('l1.vehicle.wheel.tractor_tire',fs,'轮胎侧壁以连续鼓面过渡，胎面重建十六组贴合圆周的V形牵引花纹；胎块由中心向肩部弯曲并嵌入胎体。',contracts={'chevron_pairs':16,'tread_root_embedded':True})
