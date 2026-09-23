"""Furniture bearing structures, open cavities, upholstery and continuous cloth."""
from .common import *


def padded(w,d,height=.18,color='l1Ivory',tufts=(),nu=24,nv=20):
    """Continuous cushion top with authored depressions; closed flat underside."""
    pp=[]
    def top(u,v):
        x=w*.5*u*math.sqrt(1-.105*v*v);z=d*.5*v*math.sqrt(1-.105*u*u)
        y=height*(.55+.45*(1-u**8)*(1-v**8))
        for tx,tz in tufts:
            rr=((x-tx)/.045)**2+((z-tz)/.045)**2;y-=.043*math.exp(-rr)
        return [x,y,z]
    for j in range(nv+1):
        for i in range(nu+1):pp.append(top(i/nu*2-1,j/nv*2-1))
    N=len(pp);pp += [[x,0,z] for x,y,z in pp];ff=[]
    for j in range(nv):
        for i in range(nu):
            a=j*(nu+1)+i;b=a+1;c=b+nu+1;d0=a+nu+1;ff += [[a,b,c,d0],[a+N,d0+N,c+N,b+N]]
    edge=list(range(nu+1))+[j*(nu+1)+nu for j in range(1,nv+1)]+[nv*(nu+1)+i for i in range(nu-1,-1,-1)]+[j*(nu+1) for j in range(nv-1,0,-1)]
    for a,b in zip(edge,edge[1:]+edge[:1]):ff.append([a,N+a,N+b,b])
    return mesh(pp,ff,color,smooth_angle=35),top


def author():
    fs=[block([1.30,.28,.56],[0,.207,0],'#765337',.012),block([1.13,.067,.49],[0,.0335,0],'metalDark',.010)]
    seat,_=padded(1.39,.64,.146,'#B95343',nu=28,nv=12);fs+=placed([seat],[0,.35,.02])
    # Back foam is split into vertical stitched channels but rests on one backing.
    fs.append(block([1.37,.65,.075],[0,.716,-.30],'#8D3C34',.025,rotation=[-6,0,0]))
    for i in range(7):
        pad,_=padded(.190,.602,.062,'#B95343',nu=6,nv=12)
        fs+=placed([pad],[-.581+i*.194,.731,-.271],[84,0,0])
    # Fine welt runs continuously around the front seat edge and into the backing.
    fs.append(tube([[-.643,.418,-.258],[-.682,.418,.244],[-.64,.418,.322],[.64,.418,.322],[.682,.418,.244],[.643,.418,-.258]],[.006]*6,'#CB6E5A',8))
    apply('exp.interior.booth',fs,'重建坐垫鼓面、前缘压缩、连续包边与七道竖向靠背软包，靠背统一承托于底壳而非独立平板。',dimensioned=False)

    bowl=spin([(0,0),(.18,0),(.185,.026),(.147,.092),(.146,.158),(.198,.276),(.265,.364),(.29,.404),(.285,.438),(.248,.447),(.23,.423),(.173,.317),(.097,.260),(0,.247)],'#F8F3E7',32)
    fs=placed([bowl],scale=[.82,1,1.22])
    seat=spin([(.277,.451),(.284,.459),(.279,.478),(.266,.484),(.225,.484),(.216,.475),(.216,.461),(.224,.451)],'#E9E4D6',32)
    fs+=placed([seat],scale=[.84,1,1.23])
    fs += [block([.43,.412,.172],[0,.554,-.38],'#F8F3E7',.026),block([.453,.029,.196],[0,.777,-.38],'#E9E4D6',.013)]
    fs.append(cyl(.024,.009,'metalLight',at=(.1,.79,-.38),sides=16))
    for x in (-.13,.13):fs.append(block([.047,.025,.077],[x,.466,-.279],'#E9E4D6',.01))
    apply('exp.interior.toilet',fs,'区分陶瓷盆体、内腔转折与独立圆润座圈；盆底封闭，座圈留孔，后铰座和水箱支撑相接。',dimensioned=False)

    from shapely.geometry import Polygon,box as sb,LineString
    outline=[[-.47,-.25],[.47,-.25],[.47,-.038]]+[[.47*math.cos(a),-.038+.281*math.sin(a)] for a in np.linspace(0,math.pi,19)[1:]]
    footprint=Polygon(outline);inside=footprint.buffer(-.037,join_style=2)
    fs=[shape_extruded(footprint,0,.065,'wood'),shape_extruded(footprint,.935,.065,'wood')]
    fs.append(shape_extruded(footprint.difference(inside),.063,.874,'woodLight'))
    # A front panel seam is a deliberate narrow attached strip, not random facets.
    for x in (-.012,.012):
        z=-.038+.281*math.sqrt(1-(x/.47)**2)
        fs.append(block([.004,.856,.005],[x,.5,z+.001],'#8F613B',.001))
    apply('l1.interior.case.curved',fs,'统一顶底板与D形圆弧柜壳的轮廓；增加圆弧采样和受控板厚，移除顶板外露的旧整圈筒体。')

    footprint=sb(-.5,-.25,.5,.25);cut=sb(-.16,-.26,.16,.045)
    fs=[shape_extruded(footprint,0,.065,'wood'),shape_extruded(footprint.difference(cut),.935,.065,'wood')]
    for x in (-.4675,.4675):fs.append(block([.065,.87,.50],[x,.5,0],'wood',.007))
    # Rear service panel with open-topped pipe cutout, not isolated back fragments.
    rear=sb(-.44,.066,.44,.936).difference(sb(-.15,.23,.15,.95))
    fs.append(plate(list(rear.exterior.coords)[:-1],.027,'woodDark',at=(0,0,-.232)))
    fs.append(block([.867,.045,.050],[0,.875,.218],'woodDark',.006))
    apply('l1.interior.case.under_sink',fs,'建立与顶部缺口同轴的U形后背管路避让槽，背板连续接入两侧和底板，保留前方可装门的开放柜壳。')

    fs=[]
    for x in (-.335,.335):fs.append(block([.030,.25,.50],[x,.125,0],'wood',.008))
    for z in (-.235,.235):fs.append(block([.64,.25,.030],[0,.125,z],'wood',.008))
    for x in np.linspace(-.303,.303,15):fs.append(tube([[x,.033,-.225],[x,.033,.225]],[.0042,.0042],'metal',6))
    for z in np.linspace(-.205,.205,11):fs.append(tube([[-.325,.039,z],[.325,.039,z]],[.0042,.0042],'metalLight',6))
    apply('l1.interior.drawer.mesh',fs,'保留抽屉外框，重建双向交织金属底网；横纵杆交接并嵌入四边槽口，不再只有单向横条。')

    holes=[rect(.012,.027,(-.024,.076),.002),rect(.012,.027,(.024,.076),.002),circle(.009,(0,.036),16)]
    fs=[plate(rect(.14,.14,(0,.07),.009),.018,'l1Ivory',holes=holes)]
    from shapely.geometry import Polygon
    for hole in holes:
        liner=Polygon(hole);inside=liner.buffer(-.0004,join_style=2)
        fs.append(plate(hole,.0179,'#4B575B',holes=[list(inside.exterior.coords)[:-1]],at=(0,0,-.00005)))
    # Recess backing is behind the panel; a positive-Z ray enters real cavities.
    fs.append(block([.092,.084,.004],[0,.060,-.012],'#35444B',.001))
    apply('l1.interior.fixture.outlet_plate',fs,'用真实凹孔和后置暗色底层替换悬浮凸块；插槽、接地孔与面板共用准确边界，保持表面平整。',contracts={'front_plane_z':.009,'recess_back_z':-.010,'hole_count':3})

    path=[[0,0,0],[0,.10,0]]+bezier([[0,.18,0],[0,.414,0],[0,.40,.28],[0,.260,.28]],22)
    fs=[pipe(path,.024,.0065,'metal',20)]
    fs.append(spin([(.033,0),(.033,.015),(.027,.030),(.019,.030),(.019,0)],'metalLight',20))
    fs.append(spin([(.026,.248),(.027,.251),(.027,.266),(.016,.266),(.016,.248)],'metalLight',20,at=(0,0,.28)))
    for x in (-.006,0,.006):fs.append(block([.0015,.002,.026],[x,.259,.28],'#65757C',.0002))
    apply('l1.interior.kitchen.faucet_spout',fs,'重建连续鹅颈空心弯管，入水和出水端保持通道；末端增加内凹起泡器边圈，消除封死的实心端面。')

    stations=[(0,.10,.074,.050),(.027,.117,.071,.053),(.067,.103,.053,.043),(.145,.045,.038,.034),(.25,-.020,.032,.031),(.36,-.044,.034,.035),(.465,-.027,.050,.048),(.565,.031,.070,.062),(.637,.061,.075,.061),(.70,.028,.070,.058),(.75,0,.067,.056)]
    pp=[];n=12
    for y,x,rx,rz in stations:
        for k in range(n):a=k*math.tau/n;pp.append([x+rx*math.cos(a),y,rz*math.sin(a)])
    ff=[]
    for j in range(len(stations)-1):
        for k in range(n):ff.append([j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k])
    ff += [list(range(n-1,-1,-1)),list(range((len(stations)-1)*n,len(stations)*n))]
    apply('l1.interior.leg.cabriole',[mesh(pp,ff,'wood',material='mat.wood')],'重做膝部外展、内收腿肚和卷足轮廓，曲率沿多层截面连续改变；脚底和上榫面保持平面。')

    fs=[block([.59,.064,.069],[0,.047,0],'woodDark',.011)]
    for s in (-1,1):fs.append(tube([[s*.28,0,0],[s*.278,.25,-.004],[s*.286,.62,-.011]],[.029,.026,.028],'woodDark',12))
    crest=bezier([[-.303,.625,-.010],[-.14,.674,-.025],[.14,.674,-.025],[.303,.625,-.010]],17)
    fs.append(sweep(crest,rect(.055,.069,r=.007),'wood'))
    for x in np.linspace(-.21,.21,5):fs.append(tube([[x*.48,.048,0],[x*.71,.31,-.006],[x,.628,-.018]],[.017,.014,.018],'wood',10))
    apply('l1.interior.seat.back_fan',fs,'增设实承下横档，所有扇形杆两端嵌入横档和弧形顶冠，立柱和杆条弯曲一致。')

    def saddle(u,v):
        x=(u*2-1);z=v*2-1;w=.20+.08*(1-z)*.5
        y=.082+.060*x*x+.028*max(-z,0)**2-.029*math.exp(-(x/.23)**2)*(1-z*z)
        return [x*w,y,z*.25]
    apply('l1.interior.seat.saddle',[grid_shell(saddle,24,18,.025,'wood',material='mat.wood')],'用两侧坐骨承托翼和中央卸压凹槽构造连续鞍形座壳，前段收窄，不再用黑色球块伪装孔洞。')
    def scoop(u,v):
        x=u*2-1;z=v*2-1
        xx=.282*x*math.sqrt(1-.16*z*z);zz=.26*z*math.sqrt(1-.08*x*x)
        y=.069+.048*x*x+.065*max(-z,0)**2+.014*max(z,0)**2-.025*max((z-.76)/.24,0)
        return [xx,y,zz]
    apply('l1.interior.seat.scoop',[grid_shell(scoop,20,18,.024,'wood',material='mat.wood')],'加强中央凹座、后缘上托及前沿下翻，弯曲连续且边厚统一；去除与鞍座相同的平板母形。')

    fs=[]
    for x in (-.435,.435):fs.append(block([.03,.45,.35],[x,.225,0],'wood',.005))
    for y in (.015,.435):fs.append(block([.84,.03,.35],[0,y,0],'wood',.005))
    region=sb(-.421,.029,.421,.421)
    # Half-lap intersections are represented as one in-plane lattice network.
    from shapely.ops import unary_union
    lines=[]
    for slope in (-1,1):
        for b in np.arange(-.7,1.1,.28):lines.append(LineString([[-.9,b-slope*.9],[.9,b+slope*.9]]))
    net=unary_union(lines).buffer(.0105,join_style=2,cap_style=2).intersection(region)
    for slab in [net.intersection(sb(-.43,.028,0,.423)),net.intersection(sb(0,.028,.43,.423))]:
        for p in getattr(slab,'geoms',[slab]):
            if p.geom_type=='Polygon':fs.append(plate(list(p.exterior.coords)[:-1],.33,'woodLight',holes=[list(h.coords)[:-1] for h in p.interiors]))
    apply('l1.interior.shelf.wine',fs,'移除阻挡瓶格的封闭面，建立与边框相接的双向斜插格栅，菱形空间真实贯通且保持可放置深度。')

    def pleat(u,v):
        x=(u-.5)*.68;wave=math.sin(math.tau*5*u)
        return [x*(1+.026*(1-v)),.75*v+.009*(1-v)*(1-wave)*.5,(.030+.022*(1-v))*wave]
    fs=[grid_shell(pleat,40,12,.004,'l1Ivory',axis=(0,0,1),smooth_angle=42)]
    fs.append(block([.724,.024,.048],[0,.75,0],'woodLight',.005))
    apply('l1.interior.soft.base_pleat',fs,'以连续薄布重建箱褶、轻微外展下摆与统一顶边，褶谷共享网格，不再由独立实心柱排列。')

    tufts=[(x,z) for x in (-.15,.15) for z in (-.10,.10)]
    cushion,fn=padded(.6,.45,.18,'l1Ivory',tufts=tufts)
    fs=[cushion]
    for x,z in tufts:
        # Explicit projection prevents buttons floating above depressed foam.
        y=surface_coordinate(cushion,[x,z],axis=1)
        fs.append(cyl(.012,.005,'#BAA57D',at=(x,y-.001,z),sides=12))
    apply('l1.interior.soft.buttoned',fs,'在同一坐垫网格中压出四处拉扣凹窝，扣子投射到凹底；周围面片形成受拉走势而非外挂四个凸点。')

    def curtain(u,v):
        x=(u-.5)*.67*(1+.055*(1-v));phase=math.tau*5*u+.14*(1-v)*math.sin(u*math.pi)
        return [x,.75*v+.008*(1-v)*math.cos(math.tau*5*u),(.021+.027*(1-v))*math.sin(phase)]
    fs=[grid_shell(curtain,40,18,.0035,'#DFD5BF',axis=(0,0,1),smooth_angle=45)]
    apply('l1.interior.soft.curtain_fold',fs,'将分离柱体替换为连续柔软帘面；上部收褶、下部略展开，褶线和底边有轻微自然变化。')

    def roman(u,v):
        x=(u-.5)*.65;y=.018+.79*v
        band=(v*5)%1;z=.009+.059*(math.sin(math.pi*band)**1.1)
        y-=.008*math.sin(math.pi*u)*math.sin(math.pi*band)
        return [x,y,z]
    fs=[grid_shell(roman,16,60,.004,'l1Ivory',axis=(0,0,1),smooth_angle=40)]
    apply('l1.interior.soft.roman_fold',fs,'以连续布面建立五层横向垂弧和收折边，层与层之间不断裂，轻微中心下垂替代分离软包横条。')
