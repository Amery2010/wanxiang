"""Function-led props: attached grips, sculpted food and readable instruments."""
from .common import *
from .mechanical import thread
from .nature import lamina


def curve2(points,steps=5,closed=True):
    """Centripetal-ish bounded Catmull curve for deliberately spaced control points."""
    ps=np.array(points,float);out=[];n=len(ps)
    for i in range(n if closed else n-1):
        a,b,c,d=[ps[k%n] if closed else ps[min(n-1,max(0,k))] for k in (i-1,i,i+1,i+2)]
        for t in np.linspace(0,1,steps,endpoint=False):out.append((.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t**3)).tolist())
    if not closed:out.append(ps[-1].tolist())
    return out


def seam_on(body,points,color,width=.002,axis=2):
    path=[]
    other=[k for k in range(3) if k!=axis]
    for q in points:
        p=[0,0,0];p[other[0]],p[other[1]]=q;p[axis]=surface_coordinate(body,q,axis)+width*.20;path.append(p)
    return tube(path,[width]*len(path),color,6)


def scored_baguette():
    n=24;rows=81;pp=[];cut=[]
    for j in range(rows):
        t=j/(rows-1);x=-.40+.80*t;r=(.018+.069*math.sin(math.pi*t)**.55)
        for k in range(n):
            a=k*math.tau/n;z=r*1.08*math.cos(a);y=.026+r*math.sin(a)
            dist=min(abs(x-x0+.35*z) for x0 in (-.235,-.078,.078,.235))
            amp=math.exp(-(dist/.016)**2)*math.exp(-(z/.069)**6)*max(0,math.sin(a))**5
            y-=.014*amp
            pp.append([x,y,z]);cut.append(amp)
    ff=[]
    for j in range(rows-1):
        for k in range(n):
            ids=[j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k]
            ff.append(ids)
    ff += [list(range(n-1,-1,-1)),list(range((rows-1)*n,rows*n))]
    return mesh(pp,ff,'#BC8548',smooth_angle=34)


def loaf():
    n=48;nr=18;pp=[[0,.255-.022,0]];scores=[1.]
    for j in range(1,nr+1):
        t=j/nr
        for k in range(n):
            a=k*math.tau/n;x=.29*t*math.cos(a);z=.18*t*math.sin(a)
            y=.018+.238*max(0,1-t*t)**.53
            d=min(abs(x-x0+.19*z) for x0 in (-.128,0,.128));s=math.exp(-(d/.015)**2)*math.exp(-(z/.14)**8)*(1-t**8)
            y-=.022*s;pp.append([x,y,z]);scores.append(s)
    ff=[]
    for k in range(n):ff.append([0,1+k,1+(k+1)%n])
    for j in range(nr-1):
        for k in range(n):ff.append([1+j*n+k,1+j*n+(k+1)%n,1+(j+1)*n+(k+1)%n,1+(j+1)*n+k])
    faces=list(ff)
    edge=[1+(nr-1)*n+k for k in range(n)];N=len(pp);pp += [[pp[i][0],0,pp[i][2]] for i in edge]
    faces.append(list(range(N+n-1,N-1,-1)))
    for k in range(n):faces.append([edge[k],edge[(k+1)%n],N+(k+1)%n,N+k])
    return mesh(pp,faces,'#BC8A4F',smooth_angle=38)


def bread_details(body,centers,slope,width,length,color):
    forms=[body]
    for x in centers:
        outline=[]
        for a in np.linspace(0,math.tau,32,endpoint=False):
            z=length*math.sin(a);outline.append([x-slope*z+width*math.cos(a),z])
        forms.append(surface_patch(body,outline,color,.00035,axis=1))
    return forms


def chess_base():
    return spin([(0,0),(.105,0),(.116,.010),(.116,.026),(.104,.04),(.084,.052),(.080,.065),(.065,.073),(.049,.132),(.046,.15),(.065,.158),(.065,.17),(.045,.177),(0,.177)],'l1Ivory',24)


def author():
    # Soft shells use visible bulge and cinched closure, with deliberate seams.
    body=organic_profile([(0,.153,.071,.060,0),(.045,.205,.098,.085,0),(.16,.227,.123,.101,0),(.34,.229,.122,.104,0),(.49,.210,.104,.092,0),(.57,.170,.071,.067,0),(.595,.120,.043,.045,0)],'#71543D',20)
    fs=[body]
    out=curve2([[-.181,.527],[.181,.527],[.173,.41],[.12,.354],[-.12,.354],[-.173,.41]],4)
    fs.append(surface_patch(body,out,'#9D7046',.006))
    fs.append(seam_on(body,curve2([[-.172,.515],[-.165,.42],[-.115,.369],[.115,.369],[.165,.42],[.172,.515]],5,False),'#BE9A64',.002))
    buckle=plate(rect(.056,.050,(0,.367),.005),.009,'#AF9871',holes=[rect(.038,.030,(0,.367),.003)],at=(0,0,.130))
    # Position to the curved skin before applying the slight front offset.
    buckle['position'][2]=surface_coordinate(body,[0,.367])+.006;fs.append(buckle)
    for s in (-1,1):
        fs.append(tube(bezier([[s*.12,.53,-.062],[s*.175,.44,-.154],[s*.165,.12,-.155],[s*.12,.063,-.069]],20),[(.020,.009)]*20,'#5B4635',10))
    apply('l1.props.container.pack_shell',fs,'软包采用鼓面、收拢顶部与贴合前盖，缝边、扣框和背带有实际连接；不再使用木质硬盒和悬离盖板。')

    fs=[block([.18,.12,.22],[0,.06,0],'#A2774B',.006,material='mat.wood')]
    # Parallel end-grain lines are shallow inlays on a flat load-bearing block.
    for y in (.025,.049,.080):fs.append(block([.154,.0015,.001],[0,y,.1101],'#825E3F',.0002,material='mat.wood'))
    apply('l1.props.container.pallet_block',fs,'恢复平整承托垫块：上下接触面平行，边缘仅小倒角；删除屋顶状凸起并增加少量端面层纹。')
    body=organic_profile([(0,.080,.042,.037,0),(.025,.116,.058,.051,0),(.092,.158,.088,.075,0),(.194,.157,.083,.071,0),(.246,.129,.055,.048,0),(.286,.092,.028,.027,0),(.300,.094,.029,.028,0)],'#806046',20)
    fs=[body]
    flap=curve2([[-.071,.282],[.071,.282],[.096,.250],[.055,.206],[0,.191],[-.055,.206],[-.096,.250]],4)
    fs.append(surface_patch(body,flap,'#B08655',.004))
    fs.append(seam_on(body,curve2([[-.062,.273],[-.083,.25],[-.049,.218],[0,.202],[.049,.218],[.083,.25],[.062,.273]],4,False),'#CCAE7B',.0018))
    z=surface_coordinate(body,[0,.222]);fs.append(placed([cyl(.012,.005,'#BDA46F',sides=12)],[0,.222,z+.002],[90,0,0])[0])
    apply('l1.props.container.pouch_shell',fs,'袋腹饱满、颈部收拢、圆头封口盖与表皮逐面贴合；针脚和扣子尺寸服务于小囊尺度。')

    from shapely.geometry import Polygon,Point,box as sb,LineString
    from shapely.ops import unary_union
    flange=spin([(.079,0),(.086,.005),(.086,.011),(.078,.017),(.029,.017),(.028,0)],'metalLight',32)
    hx=Polygon(circle(.061,n=6));inside=Point(0,0).buffer(.028,quad_segs=8)
    fs=[flange,shape_extruded(hx.difference(inside),.014,.048,'metal')]
    fs.append(shape_extruded(Polygon(circle(.057,n=6)).difference(inside),.061,.006,'metalLight'))
    apply('l1.props.fastener.flange_nut',fs,'法兰保持圆形，扳手夹持面保持外六角，中心改为真实圆孔；顶沿与法兰边缘小倒角，消除内外六角混淆。')

    fs=[spin([(0,0),(.003,.003),(.022,.045),(.024,.235),(0,.235)],'metal',20)]
    helix=thread(.021,.035,.022,.218,7.7,'metalLight',width=.013,tipwidth=.0025,fade=.06)
    for p in helix['points']:
        scale=min(1,max(.05,(p[1]-.002)/.055));p[0]*=scale;p[2]*=scale
    fs.append(helix)
    fs.append(spin([(0,.208),(.024,.208),(.052,.260),(.055,.264),(0,.264)],'metal',24))
    top=Point(0,0).buffer(.055,quad_segs=8).difference(sb(-.037,-.005,.037,.005))
    for poly in getattr(top,'geoms',[top]):fs.append(shape_extruded(poly,.263,.015,'metalLight'))
    apply('l1.props.fastener.wood_screw',fs,'补足连续有导程的尖尾木螺纹，齿根与杆芯重叠；沉头具有真实凹槽，去掉外贴黑色槽条。')
    apply('l1.props.food.baguette',bread_details(scored_baguette(),(-.235,-.078,.078,.235),.35,.010,.060,'#E9C991'),'长棍面包以连续烤壳网格压出四道斜割口，割口边缘与内部浅色面同属壳体，删除外挂小方块。')
    apply('l1.props.food.bread',bread_details(loaf(),(-.128,0,.128),.19,.010,.125,'#EBD2A0'),'椭圆面包顶部连续鼓起，三道割痕直接雕入表面并露出浅色内部；不再使用悬浮细绳。')

    footprint=Polygon([[0,0],[.33,0],[.23,.20]])
    holes=[Point(.143,.037).buffer(.016,quad_segs=5),Point(.250,.038).buffer(.020,quad_segs=5),Point(.226,.122).buffer(.019,quad_segs=5)]
    cut=footprint.difference(unary_union(holes))
    fs=[shape_extruded(footprint,-.100,.175,'#E4C77D'),shape_extruded(cut,.075,.025,'#E9D492')]
    for h in holes:fs.append(shape_extruded(h.buffer(-.0002),.075,.0007,'#B99655'))
    apply('l1.props.food.cheese_wedge',fs,'保留楔形外轮廓，在顶面边界内切出三个有底凹孔；孔壁和底面真实存在，移除楔体之外的悬浮深色块。',contracts={'pits':3,'pit_floor_y':.075,'top_y':.1,'bottom_y':-.1})

    n=24;rows=33;pp=[]
    for j in range(rows):
        t=j/(rows-1);x=-.18+.36*t;h=.013+.166*math.sin(math.pi*t)**.75;w=.004+.061*math.sin(math.pi*t)**.68;cz=.046*(2*t-1)**2-.024
        for k in range(n):
            a=k*math.tau/n;sn=math.sin(a);fold=max(0,sn)**8
            z=cz+w*math.cos(a)*(1-.70*fold)+.007*math.sin(t*math.tau*7)*fold
            y=.002+h*(.5+.5*sn)+.008*(.5+.5*math.cos(t*math.tau*7))*fold
            pp.append([x,y,z])
    ff=[]
    for j in range(rows-1):
        for k in range(n):ff.append([j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k])
    ff += [list(range(n-1,-1,-1)),list(range((rows-1)*n,rows*n))]
    apply('l1.props.food.dumpling',[mesh(pp,ff,'#E8DCC0',smooth_angle=38)],'重建有饱满肚腹的月牙饺体，上缘捏合与七道褶皱直接连入同一表皮，取消屋脊和悬浮柱粒。')

    outline=curve2([[-.135,.025],[-.183,.13],[-.145,.27],[-.066,.417],[.004,.477],[.085,.385],[.137,.249],[.143,.08],[.087,.012]],4)
    body=lamina(outline,'#D99C91',ridge=.05,thickness=.054,res=(14,24));fs=[body]
    for y in np.linspace(.068,.335,7):
        # Paired bent myotome strips follow the actual fillet boundary.
        xlim=.113*(1-.52*(y/.45))
        for s in (-1,1):
            path=[[0,y-.014],[s*xlim*.50,y+.005],[s*xlim,y+.034]]
            fs.append(seam_on(body,path,'#F0C9B3',.0019))
    apply('l1.props.food.fish_fillet',fs,'鱼柳改为圆弧边缘与厚薄渐变的肉片；肌节纹顺着中轴呈弧形分叉，并投射贴合到肉面。')

    pp=[];n=32
    for j,(y,r) in enumerate([(0,.106),(.02,.156),(.052,.147),(.108,.155),(.177,.137),(.227,.097),(.256,.031)]):
        for k in range(n):
            a=k*math.tau/n;scallop=.012*math.cos(a*8+.4*j)*(1 if j<3 else .35);rr=r+scallop
            pp.append([rr*math.cos(a),y+.005*math.sin(a*5+j*.5),rr*math.sin(a)])
    ff=[]
    for j in range(6):
        for k in range(n):ff.append([j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k])
    ff += [list(range(n-1,-1,-1)),list(range(6*n,7*n))]
    apply('l1.props.food.scoop',[mesh(pp,ff,'#D7ADAE',smooth_angle=30)],'冰淇淋主球与下缘融接成同一壳体，勺挖起伏沿表面连续变化，去掉分离碎球。')

    fs=[ring_tube([0,j*.0914,0],.027,.054,.0075,'metal',plane='xy' if j%2==0 else 'yz',n=40,sides=10) for j in range(5)]
    # In YZ the helper's second radius is along Z: swap to keep all long axes Y.
    for j in (1,3):fs[j]=ring_tube([0,j*.0914,0],.054,.027,.0075,'metal',plane='yz',n=40,sides=10)
    apply('l1.props.handle.chain',fs,'五枚椭圆链环交替位于XY与YZ平面，长轴一致、中心距按线径计算，真实互锁且保留微小运动间隙。',contracts={'link_count':5,'major_radius':.054,'minor_radius':.027,'wire_radius':.0075,'center_pitch':.0914,'interlocked':True})

    outside=curve2([[-.032,0],[.032,0],[.035,.181],[.115,.22],[.156,.282],[.149,.361],[.11,.386],[-.11,.386],[-.149,.361],[-.156,.282],[-.115,.22],[-.035,.181]],3)
    inner=curve2([[-.101,.280],[-.098,.335],[.098,.335],[.101,.280],[.063,.254],[-.063,.254]],4)
    fs=[plate(outside,.057,'wood',holes=[inner],material='mat.wood')]
    fs.append(block([.202,.040,.067],[0,.354,0],'#BA8952',.012,material='mat.wood'))
    apply('l1.props.handle.spade',fs,'重建连续D形铲柄：中央柄杆分叉接入两侧握架，顶部横握与支臂相连，开孔真实贯通。')

    fs=[spin([(0,0),(.088,0),(.098,.023),(.137,.052),(.140,.06),(.129,.064),(.089,.040),(.069,.020),(0,.020)],'copper',28)]
    fs.append(spin([(0,.018),(.018,.018),(.014,.033),(.007,.085),(.001,.121),(0,.122)],'metal',16))
    apply('l1.props.lamp.candle_cup',fs,'烛盘增加连续实心底面与承蜡凹面，中心烛钉根部埋入盘底；不再把环形截面误作完整盘底。',contracts={'sealed_floor':True,'floor_min_thickness':.018})

    def mask(u,v):
        x=(u*2-1)*(.118+.018*math.sin(math.pi*v));y=.014+.176*v+.022*v**5*(1-(u*2-1)**2)
        z=.017+.052*(1-(u*2-1)**2)*math.sin(math.pi*v)+.006*math.sin(v*math.tau*3)*(1-(u*2-1)**2)
        return [x,y,z]
    fs=[grid_shell(mask,28,24,.0025,'#DBE0D8',axis=(0,0,1),smooth_angle=40)]
    for s in (-1,1):
        path=bezier([[s*.121,.043,.020],[s*.22,.005,-.038],[s*.22,.23,-.038],[s*.121,.172,.020]],26)
        fs.append(tube(path,[.0025]*26,'#C6CDBF',6))
    fs.append(tube([mask(t,1) for t in np.linspace(.23,.77,14)],[.0018]*14,'#B7C4BB',6))
    apply('l1.props.medical.mask',fs,'采用贴合鼻梁、面颊和下颌的连续薄面；三道褶皱在表皮中成形，加入两侧耳带连接，去除实心折板感。')

    outline=curve2([[0,0],[-.147,.038],[-.221,.17],[-.215,.313],[-.153,.427],[-.066,.546],[-.045,.579],[.045,.579],[.066,.546],[.153,.427],[.215,.313],[.221,.17],[.147,.038]],4)
    # Bowl is an open-front, thick-walled shell with matched inner cavity.
    n=len(outline);center=np.array([0,.253]);pp=[];layers=[(1,.022),(.86,-.071),(.54,-.128),(.13,-.151)]
    for inner in (False,True):
        for scale,z in layers:
            for p in outline:
                q=center+(np.array(p)-center)*scale*(.978 if inner else 1)
                pp.append([q[0],q[1],z+(.010 if inner else 0)])
    ff=[];N=n*len(layers)
    for b in (0,N):
        for j in range(len(layers)-1):
            for k in range(n):ff.append([b+j*n+k,b+j*n+(k+1)%n,b+(j+1)*n+(k+1)%n,b+(j+1)*n+k])
        ff.append(list(range(b+(len(layers)-1)*n,b+len(layers)*n)))
    for k in range(n):ff.append([k,(k+1)%n,N+(k+1)%n,N+k])
    fs=[mesh(pp,ff,'#8F6039',material='mat.wood')]
    hole=circle(.053,(0,.329),28);fs.append(plate(outline,.014,'#C5965A',holes=[hole],at=(0,0,.027),material='mat.wood'))
    rim=Polygon(outline).difference(Polygon(outline).buffer(-.008))
    fs.append(plate(list(rim.exterior.coords)[:-1],.002,'#79502F',holes=[list(rim.interiors[0].coords)[:-1]],at=(0,0,.035),material='mat.wood'))
    apply('l1.props.musical.lute_body',fs,'鲁特琴音箱重建梨形面板、圆鼓背壳和向琴颈收束的上肩；真实音孔连通内腔，边饰与面板共面贴合。')

    right=[[0,0],[.087,.008],[.137,.050],[.149,.117],[.121,.186],[.090,.215],[.108,.233],[.065,.265],[.062,.300],[.100,.333],[.082,.353],[.111,.382],[.115,.436],[.081,.494],[.032,.518],[0,.523]]
    outline=curve2(right+[[ -x,y] for x,y in right[-2:0:-1]],3)
    holes=[]
    for s in (-1,1):
        path=curve2([[s*.061,.177],[s*.079,.193],[s*.058,.224],[s*.047,.289],[s*.025,.319],[s*.041,.325]],4,False)
        slot=LineString(path).buffer(.006,cap_style=1,join_style=1)
        holes.append(list(slot.exterior.coords)[:-1])
    body=lamina(outline,'#AD743D',ridge=.026,thickness=.018,holes=holes,res=(18,28));fs=[body]
    apply('l1.props.musical.violin_plate',fs,'面板重建上下琴腰、肩部、C形侧腰与拱度，F形音孔真实贯通；维持面板部件定位，不擅自添加完整琴颈。')

    # The bishop's head is a rounded volume clipped in projection by a real slit.
    profile=[(.174,.014),(.184,.038),(.204,.062),(.232,.067),(.265,.055),(.296,.031),(.324,.007)]
    outer=curve2([[-r,y] for y,r in profile]+[[r,y] for y,r in profile[::-1]],4)
    slash=LineString([[-.094,.252],[.026,.293]]).buffer(.007,cap_style=2)
    shape=Polygon(outer).difference(slash)
    def bulb(x,y):
        r=float(np.interp(y,[p[0] for p in profile],[p[1] for p in profile]));return .0018+math.sqrt(max(0,r*r-x*x))*.96
    fs=[chess_base(),lamina(list(shape.exterior.coords)[:-1],'l1Ivory',holes=[list(r.coords)[:-1] for r in shape.interiors],zfront=bulb,zback=lambda x,y:-bulb(x,y),res=(20,26))]
    fs.append(ellipsoid([0,.327,0],[.017,.020,.017],'l1Ivory',12,5))
    apply('l1.props.narrative.chess_bishop',fs,'保留车削底座与收腰，主教冠改为圆润尖冠和真实斜切缺口；取消贴在冠外的短杆。')

    outline=curve2([[-.043,.156],[.049,.156],[.067,.216],[.041,.267],[.064,.297],[.119,.294],[.140,.316],[.138,.342],[.080,.371],[.044,.399],[.024,.435],[.005,.434],[-.002,.393],[-.034,.381],[-.067,.311],[-.072,.238]],3)
    fs=[chess_base()]
    fs.append(lamina(outline,'l1Ivory',zfront=lambda x,y:.027+.018*max(0,math.sin((y-.15)/.29*math.pi)),zback=lambda x,y:-.027-.018*max(0,math.sin((y-.15)/.29*math.pi)),res=(16,26)))
    for z in (-.044,.044):
        fs.append(plate(circle(.0047,(.061,.357),12),.0015,'#746A55',at=(0,0,z)))
    apply('l1.props.narrative.chess_knight',fs,'马棋子以弯颈、下颌凹口、前伸口鼻和立耳构成清楚剪影，板厚向躯干鼓起，取代L形盒块。')

    fs=[chess_base(),spin([(0,.163),(.069,.163),(.069,.227),(.086,.236),(.086,.26),(.060,.26),(.060,.248),(0,.248)],'l1Ivory',32)]
    for i in range(6):
        a=i*math.tau/6;outer=[[.086*math.cos(a+t),.086*math.sin(a+t)] for t in np.linspace(-.33,.33,5)];inner=[[.060*math.cos(a+t),.060*math.sin(a+t)] for t in np.linspace(.33,-.33,5)]
        fs.append(slab_polygon(outer+inner,.258,.043,'l1Ivory'))
    apply('l1.props.narrative.chess_rook',fs,'车棋子顶部采用六个与冠圈连接的真实城垛及内凹冠口；底座和塔身比例统一，取消顶部小球。')

    fs=[block([.18,.18,.18],[0,.09,0],'l1Ivory',.012)]
    coords={1:[(0,0)],2:[(-1,-1),(1,1)],3:[(-1,-1),(0,0),(1,1)],4:[(-1,-1),(-1,1),(1,-1),(1,1)],5:[(-1,-1),(-1,1),(1,-1),(1,1),(0,0)],6:[(x,y) for x in (-1,1) for y in (-1,0,1)]}
    # Opposite sides sum to 7; pips are very thin inlays, not raised cylinders.
    for count,axis,sign in [(1,1,1),(6,1,-1),(2,2,1),(5,2,-1),(3,0,1),(4,0,-1)]:
        for u,v in coords[count]:
            f=plate(circle(.010,(u*.045,v*.045),16),.0008,'ink')
            if axis==2:f=placed([f],[0,.09,sign*.09005],[0,0,0])[0]
            elif axis==1:f=placed([f],[0,.09+sign*.09005,0],[90,0,0])[0]
            else:f=placed([f],[sign*.09005,.09,0],[0,90,0])[0]
            fs.append(f)
    apply('l1.props.narrative.dice',fs,'六面补齐1—6点数且相对面和为7；圆点薄嵌在平面上，保留边角小倒角和正确骰子尺度。',contracts={'opposite_face_sum':7,'pips':21})

    fs=[spin([(0,0),(.155,0),(.165,.006),(.167,.015),(.165,.024),(.154,.030),(0,.030)],'copper',40)]
    # Flat XZ blank is intentional; a continuous tab now joins the suspension eye.
    tab=plate(rect(.035,.055,(0,.164),.009),.026,'copper',holes=[circle(.009,(0,.175),16)])
    fs+=placed([tab],[0,.014,0],[90,0,0])
    fs.append(ring_tube([0,.014,.194],.024,.024,.0035,'metalLight',plane='yz',n=36,sides=8))
    apply('l1.props.narrative.medallion',fs,'保留可定制空白圆牌，新增与牌身相连的穿孔耳座并使吊环穿过耳座；不是把小环摆在牌边。')

    # Book spine is a long arched U channel, with square top/bottom ends.
    sec=[]
    for a in np.linspace(0,math.pi,17):sec.append([.045*math.cos(a),.018+.021*math.sin(a)])
    for a in np.linspace(math.pi,0,17):sec.append([.039*math.cos(a),.015+.018*math.sin(a)])
    pp=[]
    for z in (-.25,.25):pp.extend([[x,y,z] for x,y in sec])
    n=len(sec);ff=[list(range(n-1,-1,-1)),list(range(n,2*n))]
    for k in range(n):ff.append([k,(k+1)%n,(k+1)%n+n,k+n])
    fs=[mesh(pp,ff,'#77543B',material='mat.wood')]
    for z in (-.19,.19):fs.append(tube([[.043*math.cos(a),.019+.022*math.sin(a),z] for a in np.linspace(0,math.pi,17)],[.0016]*17,'#B49155',6))
    apply('l1.props.office.book_spine',fs,'书脊改为两端平齐、横截面圆弧的U形连接片，前后封皮可接两条长边，增加少量压线而非两端尖菱形。')

    path=[[-.035,.027,0],[-.035,.151,0]]
    path += [[.035*math.cos(a),.151+.035*math.sin(a),0] for a in np.linspace(math.pi,0,15)[1:]]
    path.append([.035,.033,0]);path += [[.005+.030*math.cos(a),.033+.030*math.sin(a),0] for a in np.linspace(0,-math.pi,15)[1:]]
    path.append([-.025,.131,0]);path += [[-.005+.020*math.cos(a),.131+.020*math.sin(a),0] for a in np.linspace(math.pi,0,13)[1:]]
    path.append([.015,.043,0])
    apply('l1.props.office.clip',[tube(path,[.0035]*len(path),'metal',8)],'用连续绕线构造回形夹的外回环、底弯和内回环，圆弧半径与线径匹配，避免直角框架和孤立内杆。')

    outline=curve2([[-.017,0],[.017,0],[.040,.075],[.032,.108],[.010,.17],[0,.20],[-.010,.17],[-.032,.108],[-.040,.075]],3)
    region=Polygon(outline).difference(Point(0,.101).buffer(.006,quad_segs=5).union(sb(-.0013,.1,.0013,.22)))
    def front(x,y):return .005+.011*(1-min(1,(x/.041)**2))*math.sin(math.pi*min(1,y/.2))
    fs=[lamina(list(region.exterior.coords)[:-1],'copper',zfront=front,zback=lambda x,y:front(x,y)-.003,res=(14,25))]
    apply('l1.props.office.pen_nib',fs,'钢笔尖重建弧拱薄壳、呼吸孔和连至尖端的真实中心缝，两瓣尖端与肩部保持连贯。')

    # Preserve the original base's +Z longitudinal datum; move the anvil onto it.
    footprint=Polygon([[-.08,0],[.08,0],[.075,.30],[-.075,.30]])
    fs=[shape_extruded(footprint,-.02,.040,'#4F606C')]
    anvil=Polygon(rect(.073,.048,r=.007));slots=[Polygon(rect(.022,.004,(-.012,-.006),.001)),Polygon(rect(.022,.004,(.012,.006),.001))]
    fs.append(shape_extruded(anvil,.020,.005,'metal'))
    atop=shape_extruded(anvil.difference(unary_union(slots)),.024,.003,'metalLight')
    fs.append(atop)
    # Both anvil layers sit on the unshifted base at longitudinal +Z=.058.
    fs[-2:]=placed(fs[-2:],[0,0,.058])
    for s in (-1,1):fs.append(block([.018,.057,.044],[s*.061,.041,.266],'#657580',.005))
    apply('l1.props.office.stapler_base',fs,'按底座实际+Z长度方向放置砧片，砧片坐在顶面并带两条凹槽；后端补铰耳，不把局部底座误做完整订书机。',contracts={'anvil_center_z':.058,'base_z_range':[0,.30],'anvil_bottom_y':.020})

    outline=curve2([[-.036,0],[.036,0],[.038,.155],[.087,.181],[.130,.211],[.144,.273],[.126,.327],[.080,.362],[.057,.326],[.087,.278],[.066,.246],[.012,.250],[-.010,.284],[-.002,.337],[-.048,.347],[-.097,.304],[-.111,.25],[-.075,.190],[-.037,.16]],3)
    fs=[plate(outline,.048,'metal',material='mat.metal')]
    # Thin darker inset follows the neck; no text/logos baked into the part.
    fs.append(plate(rect(.025,.118,(0,.077),.007),.001,'metalDark',at=(0,0,.0241)))
    apply('l1.props.toolhead.wrench',fs,'扳手头采用偏转开口、两片夹颚和圆弧肩部，颚面有明确夹持方向；颈部厚度和内嵌面保持工具辨识。')

    fs=[spin([(0,0),(.12,0),(.148,.033),(.221,.143),(.267,.30),(.223,.43),(.155,.51),(.093,.572),(.094,.65),(.113,.669),(.113,.693),(.090,.698),(.081,.683),(.073,.655),(.073,.579),(.134,.526),(.204,.43),(.245,.30),(.202,.15),(.118,.05),(0,.045)],'#D5C7A8',32)]
    for s in (-1,1):
        path=bezier([[s*.091,.637,0],[s*.33,.697,.005],[s*.39,.389,.005],[s*.223,.403,0]],26)
        fs.append(tube(path,[(.022,.028)]*26,'#D5C7A8',12))
    apply('l1.props.vessel.amphora',fs,'罐体统一连续壁厚和实底，双耳从颈部跨出形成明显空隙，再接回肩腹，避免被壳体吞没的小把手。')

    # Pitcher's spout is the displaced vessel lip, not a separate solid wedge.
    profile=[(0,.135),(.03,.158),(.12,.198),(.35,.188),(.49,.211),(.55,.231)]
    n=40;pp=[];m=len(profile)
    for inner in (False,True):
        for j,(y,r) in enumerate(profile):
            for k in range(n):
                a=k*math.tau/n;lob=math.exp(-(math.atan2(math.sin(a),math.cos(a))/.33)**2)
                rr=r-(.018 if inner else 0)+.087*(j/(m-1))**6*lob
                yy=y+.028*(j/(m-1))**8*lob+( .024 if inner and j==0 else 0)
                pp.append([rr*math.cos(a),yy,rr*math.sin(a)])
    ff=[];N=n*m
    for b in (0,N):
        for j in range(m-1):
            for k in range(n):ff.append([b+j*n+k,b+j*n+(k+1)%n,b+(j+1)*n+(k+1)%n,b+(j+1)*n+k])
        ff.append(list(range(b,b+n)))
    for k in range(n):a=(m-1)*n+k;b=(m-1)*n+(k+1)%n;ff.append([a,b,b+N,a+N])
    fs=[mesh(pp,ff,'#D5C7A8')]
    path=bezier([[-.208,.474,0],[-.435,.518,0],[-.437,.144,0],[-.193,.16,0]],25);fs.append(tube(path,[(.026,.031)]*25,'#D5C7A8',12))
    apply('l1.props.vessel.pitcher',fs,'导流嘴直接由口沿和内外罐壁连续延伸，内腔连通并保持薄边；壶把两端接入主体，底部密闭。')

    fs=[]
    tongues=[([[0,0,0],[-.025,.17,.008],[-.036,.31,.021],[.066,.57,0]],.142,'#D76C2C'),([[.035,.012,.035],[.109,.10,.035],[.14,.258,.015],[.125,.38,.006]],.065,'#E78732'),([[-.066,.014,-.012],[-.128,.1,-.02],[-.135,.233,-.018],[-.076,.348,-.027]],.067,'#D97B2E')]
    for path,r,col in tongues:
        ps=bezier(path,16);fs.append(tube(ps,[r*(1-t)**.76+.0009 for t in np.linspace(0,1,16)],col,10))
    fs.append(tube(bezier([[0,.008,.090],[-.029,.103,.103],[-.044,.188,.075],[.012,.371,.038]],15),[.078*(1-t)**.87+.001 for t in np.linspace(0,1,15)],'#F3C45D',9))
    apply('w.camp.flame',fs,'主火舌、两侧分舌与内焰按弯曲节奏重构，基部交叠、尖端渐收，弱化方块底部和单一尖锥。',dimensioned=False)

    # Layered compressed straw body with shallow irregular side relief.
    outline=rect(.80,.48,r=.049);pp=[]
    for j,y in enumerate([0,.08,.17,.26,.36,.47]):
        for k,(x,z) in enumerate(outline):
            factor=1+.016*math.sin(j*2.8+k*1.7);pp.append([x*factor,y,z*factor])
    n=len(outline);ff=[]
    for j in range(5):
        for k in range(n):ff.append({'v':[j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k],'color':['#B89446','#C4A151','#BD984A'][j%3]})
    ff += [list(range(n-1,-1,-1)),list(range(5*n,6*n))];fs=[mesh(pp,ff,'#BE994D')]
    for x in (-.23,.23):
        path=[[x,.008,-.210],[x,.043,-.248],[x,.429,-.248],[x,.48,-.206],[x,.48,.206],[x,.429,.248],[x,.043,.248],[x,.008,.210]]
        fs.append(sweep(path,circle(.009,n=8),'#83673D',closed_path=True))
    for s in (-1,1):
        for j in range(12):
            y=.037+j*.035
            for k in range(4):
                x=-.32+k*.175+.025*math.sin(j*1.7+k)
                fs.append(tube([[x,y,s*.240],[x+.078,y+.005*math.sin(k+j),s*.241]],[.0018,.0013],'#D0B068',5))
    apply('w.farm.hay_bale',fs,'压缩草捆按浅层起伏塑形，绑绳沿圆角包覆并有轻微压入；草茎以细短端线表达，避免整齐外贴粗横杠。',dimensioned=False)

    fs=[spin([(0,0),(.098,0),(.118,.009),(.127,.026),(.126,.036),(.117,.038),(.113,.027),(.108,.014),(0,.013)],'#303B3E',32)]
    fs.append(tube([[0,.021,-.117],[0,.021,-.151]],[.015,.014],'metalDark',10))
    fs.append(tube([[0,.023,-.143],[0,.026,-.198],[0,.027,-.346]],[.016,.019,.017],'woodDark',12))
    apply('w.tool.pan',fs,'煎锅重建连续密闭平底、渐开侧壁和薄口沿；金属柄座接锅外壁，木柄从柄座后方开始，不侵入煎面。',dimensioned=False,contracts={'sealed_floor':True,'cooking_floor_y':.013,'handle_root_z':-.117})
