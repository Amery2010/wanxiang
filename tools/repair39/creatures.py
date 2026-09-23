"""Species silhouettes and connected wing/foot structures, not recoloured solids."""
from .common import *


def mirror_x(f):
    g=deepcopy(f)
    g['points']=[[-p[0],p[1],p[2]] for p in f['points']]
    g['faces']=[list(reversed(p)) if isinstance(p,list) else {**p,'v':list(reversed(p['v']))} for p in f['faces']]
    return g


def eyes_side(body,y,z,r,iris='#9B742C',vertical=False):
    # UV plane of a side-facing eye is (Y,Z); ray-test every corner on the skull.
    fs=[]
    for size,col,off in [(1.18,'#3A3129',.0008),(1,iris,.0016),(.53,'ink',.0024)]:
        shape=circle(r*size,(y,z),16,scale=((.77 if not vertical else 1.0),(.99 if not vertical else .48)))
        f=surface_patch(body,shape,col,off,axis=0);fs.extend([f,mirror_x(f)])
    return fs


def nose_front(at,size,color='ink'):
    x,y,z=at;w,h,d=size
    return mesh([[x-w,y+h*.45,z],[x+w,y+h*.45,z],[x+w*.85,y-h*.15,z],[x,y-h*.60,z+d*.3],[x-w*.85,y-h*.15,z],
                 [x-w*.72,y+h*.35,z+d],[x+w*.72,y+h*.35,z+d],[x,y-h*.3,z+d]],
                [[0,1,6,5],[1,2,3,7,6],[3,4,0,5,7],[5,6,7],[0,4,3,2,1]],color)


def feather(root,tip,width,color,curve=.02,asym=.34):
    """A closed cambered feather; off-centre rachis and smooth outline taper."""
    a=np.array(root,float);b=np.array(tip,float);d=b-a;L=np.linalg.norm(d);d/=L
    # Wings lie in XZ; upright standalone feathers are transformed separately.
    side=np.cross(np.array([0.,1,0]),d);side/=np.linalg.norm(side)
    pp=[];n=12
    for j in range(n):
        t=j/(n-1);center=a+(b-a)*t+np.array([0,curve*math.sin(t*math.pi),0]);w=width*(math.sin(math.pi*t)**.64 if 0<t<1 else .015)
        for k in (-1,0,1):
            p=center+side*w*(asym if k<0 else 1-asym)*k
            p+=np.array([0,.003*math.sin(t*math.pi)*(1-abs(k)),0]);pp.append(p.tolist())
    N=len(pp);pp += [[p[0],p[1]-.003,p[2]] for p in pp];ff=[]
    for j in range(n-1):
        for k in range(2):u=j*3+k;ff += [[u,u+1,u+4,u+3],[u+N+3,u+N+4,u+N+1,u+N]]
    edge=[0,1,2]+[j*3+2 for j in range(1,n)]+[(n-1)*3+1,(n-1)*3]+[j*3 for j in range(n-2,0,-1)]
    for u,v in zip(edge,edge[1:]+edge[:1]):ff.append([u,v,v+N,u+N])
    return mesh(pp,ff,color)


def paw(w=.125,L=.18,h=.14,color='#AF8254'):
    """One connected skin shell; toe scallops share roots and a planar sole."""
    outline=[]
    # Rounded heel, then four distinct but connected toe lobes at the front.
    outline += [[-w*.67,-L*.55],[-w*.96,-L*.28],[-w,.04*L],[-w*.94,L*.55]]
    for i in range(4):
        cx=(-.75+i*.5)*w;front=L*(.83 if i in (0,3) else 1)
        outline.extend([[cx-w*.23,front-.025],[cx-w*.13,front+.007],[cx+w*.08,front+.015],[cx+w*.23,front-.025]])
    outline += [[w*.98,L*.38],[w,-L*.12],[w*.72,-L*.55]]
    # Build explicit layers, constricting toe lobes into a smaller ankle.
    pp=[]
    for y,sx,sz,cz in [(0,1,1,0),(h*.22,1.02,1.01,0),(h*.55,.90,.83,-L*.02),(h,.52,.37,-L*.10)]:
        pp.extend([[x*sx,y,z*sz+cz] for x,z in outline])
    n=len(outline);ff=[]
    for j in range(3):
        for k in range(n):ff.append([j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k])
    ff += [list(range(n-1,-1,-1)),list(range(3*n,4*n))]
    return mesh(pp,ff,color)


def hoof_half(x,w,L,h,color):
    outline=[[-.85,-.78],[-1,-.30],[-.95,.43],[-.63,1],[.48,1.04],[.85,.71],[.93,-.30],[.58,-.82]]
    pp=[]
    for y,sx,sz,cz in [(0,1,1,.02),(h*.18,1.01,1.03,.02),(h*.83,.79,.83,0),(h,.68,.71,-.006)]:
        pp.extend([[x+a*w*sx,y,b*L*sz+cz] for a,b in outline])
    ff=[];n=8
    for j in range(3):
        for k in range(n):ff.append([j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k])
    ff.extend([list(range(n-1,-1,-1)),list(range(24,32))]);return mesh(pp,ff,color)


def author():
    body=organic_profile([(-.081,.041,.036,.044,.023),(-.066,.068,.065,.055,.018),(-.044,.089,.080,.071,.010),
        (-.019,.103,.082,.084,0),(.012,.108,.072,.088,0),(.041,.096,.070,.085,-.008),(.068,.080,.054,.067,-.011),(.086,.044,.032,.043,-.013)],'#BA7A3C',20)
    fs=[body]
    for side in (-1,1):
        eye=almond(side*.048,.013,.023,.014)
        fs += [surface_patch(body,eye,'#57452B',.0008),surface_patch(body,almond(side*.048,.013,.019,.011),'#A6B46B',.0017),surface_patch(body,circle(.009,(side*.048,.013),12,scale=(.33,1)),'ink',.0026)]
        cheek=[[side*.002,-.023],[side*.026,-.020],[side*.058,-.039],[side*.052,-.060],[side*.018,-.064],[side*.002,-.050]]
        fs.append(surface_patch(body,cheek,'#E8D6B6',.001))
        e=ear_cup([[-.038,0],[.035,.006],[.025,.053],[.017,.119],[.001,.113],[-.028,.052]],color='#BA7A3C',inner='#D3A290',depth=.022)
        fs += placed([e],[side*.063,.043,-.01],[0,side*13,side*-8],[1.04,.75,1.0])
    fs.append(nose_front([0,-.032,.087],[.016,.021,.012],'#9B6B59'))
    fs.append(surface_patch(body,[[-.004,-.044],[.004,-.044],[.006,-.055],[0,-.058],[-.006,-.055]],'#73533F',.002))
    apply('core.animal.cat.head',fs,'重建猫科额头、颊弓与短吻；杏仁眼和分色口鼻贴合头壳，耳根有厚度且接入颅顶。',dimensioned=False)

    body=profile_z([(-.075,.055,.083,.125),(-.025,.080,.107,.16),(.045,.063,.118,.167),(.12,.018,.103,.144),(.23,-.068,.088,.118),(.35,-.132,.082,.090),(.418,-.141,.083,.075),(.45,-.143,.063,.061)],'#9E724E',20)
    fs=[body]+eyes_side(body,.098,.064,.021,'#483829')
    # Muzzle colour is applied to the joined shell; nostrils are inset-looking patches.
    for side in (-1,1):
        patch=surface_patch(body,[[ -.199,.34],[-.17,.421],[-.111,.443],[-.076,.407],[-.071,.343]],'#BA9474',.0008,axis=0)
        fs.append(patch if side>0 else mirror_x(patch))
        nostril=surface_patch(body,circle(.017,(-.116,.40),12,scale=(.62,1.2)),'#483829',.0018,axis=0);fs.append(nostril if side>0 else mirror_x(nostril))
        e=ear_cup([[-.028,0],[.028,0],[.025,.076],[.012,.139],[-.004,.147],[-.022,.097]],'#9E724E','#6C4E39',.025)
        fs += placed([e],[side*.067,.177,-.023],[0,side*12,side*-10])
    fs.append(tube([[0,.228,-.064],[0,.237,-.001],[0,.216,.039],[0,.163,.072]],[.025,.027,.024,.005],'#543D2E',8))
    apply('core.animal.horse.head',fs,'通过额骨、眼眶、面嵴及长吻的连续控制环塑形；鼻孔附着于吻侧，厚耳壳和鬃根接入头部。',dimensioned=False)

    body=profile_z([(-.24,.03,.19,.19),(-.12,.065,.267,.263),(.02,.058,.282,.268),(.13,.004,.24,.211),(.24,-.035,.174,.142),(.36,-.046,.135,.107),(.415,-.044,.112,.092)],'#634530',20)
    fs=[body]+eyes_side(body,.100,.13,.028,'#4C3829')
    muzzle=profile_z([(.215,-.035,.13,.105),(.27,-.034,.153,.113),(.38,-.049,.128,.095),(.43,-.047,.093,.07)],'#9B7756',16);fs.append(muzzle)
    fs.append(nose_front([0,-.012,.421],[.109,.078,.037]))
    for side in (-1,1):
        e=ear_cup(circle(.087,n=16,scale=(1,1.08)),'#634530','#473526',.025)
        fs += placed([e],[side*.209,.255,-.095],[0,side*12,side*-20])
    apply('exp.creature.bear_head',fs,'重做宽颅与短粗吻过渡；眼睛按侧面壳体投射贴合，圆耳嵌入头部并带耳腔。',dimensioned=False)

    body=profile_z([(-.28,.05,.143,.175),(-.18,.075,.207,.234),(-.04,.077,.24,.216),(.095,.06,.229,.178),(.23,.014,.181,.127),(.38,-.012,.15,.103),(.53,-.019,.109,.076),(.565,-.013,.070,.063)],'#367A76',16)
    fs=[body]+eyes_side(body,.109,.171,.035,'#D4AB43',True)
    for side in (-1,1):
        horn_path=bezier([[side*.18,.192,-.14],[side*.213,.38,-.15],[side*.25,.51,-.28],[side*.31,.59,-.38]],16)
        fs.append(tube(horn_path,[.070*(1-t)**1.25+.0015 for t in np.linspace(0,1,16)],'bone',10))
        fs.append(tube([[side*.19,.161,.035],[side*.218,.159,.15],[side*.182,.108,.28]],[.041,.034,.007],'#458D85',8))
        n=surface_patch(body,circle(.018,(.004,.492),12,scale=(.55,1)),'#204A48',.0015,axis=0);fs.append(n if side>0 else mirror_x(n))
    fs.append(profile_z([(.09,-.074,.15,.045),(.24,-.096,.157,.033),(.43,-.082,.132,.027),(.541,-.051,.082,.015)],'#71A58B',12))
    # Small ridges root into the forehead rather than terminating in mid-air.
    for z,y,h in [(-.22,.20,.105),(-.07,.233,.10),(.065,.213,.075)]:
        fs.append(plate([[-.025,0],[.025,0],[0,h]],.11,'#377A73',at=(0,y,z)))
    apply('exp.creature.dragon_head',fs,'分离眶上脊、颊部与长吻造型；角根埋入颅骨、眼和鼻孔按真实表面贴合，下颌沿吻线收束。',dimensioned=False)

    fs=[tube([[0,0,0],[.24,.035,-.065],[.48,.03,-.11],[.66,.014,-.20],[.89,-.014,-.39]],[(.076,.068),(.086,.052),(.067,.037),(.05,.031),(.020,.014)],'#6C4D36',10)]
    # Secondary flight feathers: parallel along the ulna; primary feathers fan from wrist.
    for i in range(6):
        root=[.115+i*.082,-.026,-.075-i*.022];tip=[root[0]+.07,-.042,-.40-i*.026]
        fs.append(feather(root,tip,.132,'#BC9970' if i%2 else '#CBB390',curve=.012))
    wrist=np.array([.58,-.012,-.19])
    for i in range(7):
        root=wrist+np.array([i*.033,-i*.0008,-i*.023]);tip=[.76+i*.061,-.037,-.69+i*.021]
        fs.append(feather(root,tip,.133,'#D8C7A4' if i%2 else '#CABB9B',curve=.027))
    # Fitted covert row; never gate the essential flight feathers behind detail.
    for i in range(8):
        root=[.09+i*.09,.022,-.04-i*.032];tip=[root[0]+.052,.002,root[2]-.185]
        fs.append(feather(root,tip,.105,'#8C6A4B',curve=.016))
    # Legacy left-wing mounts rotate 180 degrees around Z. Compensate Y only
    # inside the part so the final world transform mirrors X without turning
    # the dorsal covert layer upside down. Node/pivot/animation paths survive.
    fs=placed(fs)
    for f in fs:
        for col in range(4):f['matrix'][col*4+1]=mul(f['matrix'][col*4+1],choice('mount_inverted',{'false':1,'true':-1}))
    apply('exp.creature.feather_wing',fs,'按肩肘腕建立渐细翼骨，分区重建覆羽、次飞羽与扇展主飞羽；薄弧面羽片补充左翼旧安装姿态的翻面补偿，使双翼覆羽均朝上。',dimensioned=False,detail=list(range(len(fs)-8,len(fs))),parameters={'mount_inverted':{'type':'boolean','default':False,'title':'旧式180°左翼安装翻面补偿'}})

    # Tail fin is a single YZ membrane with convex leading edges and a concave fork.
    outline=[[.08,-.068],[-.16,-.105],[-.49,-.43],[-.61,-.56],[-.57,-.29],[-.41,-.06],[-.39,.02],[-.46,.22],[-.62,.65],[-.49,.54],[-.16,.12],[.08,.08]]
    fs=placed([plate(outline,.012,'#6A8790')],[0,0,0],[0,-90,0])
    fs.append(profile_z([(.10,0,.055,.078),(-.04,0,.048,.086),(-.18,0,.012,.11)],'#586D78',12))
    for y,z in [(-.44,-.49),(-.29,-.50),(-.13,-.43),(.12,-.43),(.34,-.51),(.55,-.57)]:
        fs.append(tube([[0,0,-.04],[0,y*.53,z*.57],[0,y,z]],[.007,.005,.002],'#96AFB3',6))
    apply('exp.creature.fish_tail',fs,'重建宽展分叉尾鳍薄膜与凹弧后缘，尾柄渐细接入鳍面，鳍条沿扇形受力方向展开。',dimensioned=False)

    body=profile_z([(-.15,.013,.072,.09),(-.11,.030,.122,.145),(-.025,.052,.151,.162),(.055,.054,.144,.148),(.12,.035,.102,.114),(.169,.006,.056,.080)],'#E4DEC9',20)
    fs=[body]+eyes_side(body,.084,.071,.023,'#C4A152')
    beak=profile_z([(.127,.002,.057,.042),(.184,.016,.066,.043),(.237,.013,.045,.040),(.270,-.009,.025,.038),(.279,-.042,.009,.029),(.267,-.068,.003,.004)],'#B69A52',12);fs.append(beak)
    fs.append(profile_z([(.128,-.039,.048,.016),(.194,-.043,.043,.015),(.240,-.038,.010,.006)],'#8B733C',10))
    for side in (-1,1):
        # A fitted angular brow, not an unsupported rectangular stick.
        f=surface_patch(body,[[.098,.035],[.113,.060],[.111,.102],[.099,.116],[.092,.083]],'#F2EAD6',.003,axis=0);fs.append(f if side>0 else mirror_x(f))
    apply('exp.creature.raptor_head',fs,'重建猛禽颅顶、眼眶和眶上脊；连续收尖的钩喙取代方块，分清上喙、下喙与蜡膜区域。',dimensioned=False)

    body=profile_z([(-.20,.015,.17,.105),(-.10,.049,.226,.148),(.018,.053,.257,.165),(.16,.033,.245,.151),(.32,.009,.213,.103),(.49,-.004,.188,.083),(.69,-.007,.158,.069),(.85,-.002,.133,.064),(.92,-.001,.105,.054)],'#397248',20)
    fs=[body]+eyes_side(body,.113,.124,.028,'#B4A24E',True)
    jaw=profile_z([(-.04,-.068,.18,.043),(.20,-.085,.205,.034),(.47,-.072,.175,.027),(.72,-.056,.143,.023),(.90,-.034,.10,.016)],'#899359',16);fs.append(jaw)
    for side in (-1,1):
        brow=tube([[side*.18,.143,.0],[side*.198,.153,.10],[side*.20,.12,.21]],[.045,.036,.012],'#4A8050',8);fs.append(brow)
        n=surface_patch(body,circle(.018,(side*.067,.848),12,scale=(.80,1)),'#234D36',.0018,axis=1);fs.append(n)
        # Teeth roots intersect the gum strip; discrete lower-jaw sockets stay intact.
        for i in range(6):
            z=.30+i*.088;x=side*(.195-.099*(z-.3)/.53);y=-.068+.021*(z-.3)/.53
            fs.append(tube([[x,y+.010,z],[x,y-.020,z+.002]],[.008,.0012],'bone',6))
    apply('exp.creature.reptile_head',fs,'按后颅、隆起眼眶、扁长吻和连续下颌重建；消除外贴眼球，鼻孔与齿根接入实际头壳和牙龈。',dimensioned=False)

    fs=[hoof_half(s*.071,.059,.111,.15,'#5C4838') for s in (-1,1)]
    apply('l1.creature.foot.cloven',fs,'用平底蹄壁、收束蹄冠、圆弧蹄尖和中央蹄缝重建偶蹄，保留左右足端子件尺度。')
    fs=[paw()]
    # Sole pad rests on a genuine flat sole; it is not an extra row of floating balls.
    fs.append(placed([plate([[-.047,-.037],[0,-.058],[.045,-.034],[.055,.039],[.014,.065],[-.040,.044]],.003,'#7B5C48')],[0,.001,.014],[90,0,0])[0])
    apply('l1.creature.foot.paw',fs,'通过共享顶点的掌壳和四趾波形前缘塑造肉掌；趾根连续、足底平整，肉垫仅为贴底浅层。')

    fs=[tube([[0,.15,-.019],[0,.085,0],[0,.044,.058]],[.033,.038,.036],'#A58143',10)]
    for i,x in enumerate((-.106,0,.106)):
        L=.23 if i!=1 else .275
        fs.append(tube(bezier([[x*.18,.066,.024],[x*.60,.026,.095],[x,.027,L-.038],[x,.030,L]],11),[.029*(1-.45*t) for t in np.linspace(0,1,11)],'#B19355',8))
        fs.append(tube(bezier([[x,.030,L-.008],[x,.055,L+.019],[x,.054,L+.041],[x,.006,L+.054]],8),[.016*(1-t)+.001 for t in np.linspace(0,1,8)],'#45413C',8))
    fs.append(tube(bezier([[0,.078,.008],[.010,.031,-.072],[.026,.029,-.14],[.03,.010,-.17]],10),[.025*(1-t)+.003 for t in np.linspace(0,1,10)],'#B19355',8))
    fs.append(tube([[.029,.014,-.15],[.03,.035,-.18],[.029,.007,-.192]],[.011,.006,.001],'#45413C',8))
    apply('l1.creature.foot.talon',fs,'重建三前趾与一后趾，趾根汇入踝部；各趾独立曲线、抓握指节和下钩爪尖取代厚扇板。')

    outline=[[-.02,-.12],[-.09,.024],[-.167,.174],[-.12,.177],[-.084,.160],[-.047,.184],[0,.249],[.047,.184],[.084,.16],[.12,.177],[.167,.174],[.09,.024],[.02,-.12]]
    fs=placed([plate(outline,.009,'#BC9456')],[0,.024,0],[90,0,0])
    for x,z in [(-.157,.178),(0,.246),(.157,.178)]:
        fs.append(tube([[0,.035,-.105],[x*.46,.034,z*.34],[x,.027,z]],[.014,.010,.004],'#C9A468',8))
    apply('l1.creature.foot.webbed',fs,'统一蹼膜与趾骨的水平坐标，将膜厚减至薄壳；前缘以低幅凹弧连接三趾，趾骨贴合膜面。')

    fs=[profile_z([(0,0,.112,.081),(.08,.045,.109,.082),(.18,.067,.074,.064),(.26,.049,.039,.047),(.296,.014,.017,.038),(.291,-.023,.007,.019),(.278,-.043,.002,.002)],'#B69857',12)]
    apply('l1.creature.mouth.beak_hook',fs,'用连续截面建立喙根、隆起鼻梁、收尖喙尖与下钩，消除另接直杆式钩部。')
    outline=[[-.055,0],[.032,-.008],[.091,.04],[.134,.105],[.158,.196],[.146,.287],[.102,.362],[.05,.396],[.074,.33],[.078,.28],[.037,.24],[.071,.21],[.063,.167],[.021,.158],[.046,.121],[.013,.088],[-.041,.107],[-.073,.066]]
    fs=[plate(outline,.040,'#695039')]
    apply('l1.creature.mouth.mandible',fs,'重建向内弯曲的咬合臂、基部转接和小型咬齿，轮廓由连续曲线采样而非直角块组成。')

    outline=[[0,0],[-.15,.22],[-.40,.58],[-.30,.51],[-.22,.48],[-.13,.51],[0,.72],[.13,.51],[.22,.48],[.30,.51],[.40,.58],[.15,.22]]
    fs=[plate(outline,.008,'#776054')]
    for x,y in [(-.4,.58),(0,.72),(.4,.58)]:
        fs.append(tube([[0,0,0],[x*.43,y*.53,.005],[x,y,0]],[.019,.011,.003],'#A18469',8))
    apply('l1.creature.wing.bat_membrane',fs,'将膜缘改为翼指间凹弧，增加中间翼指、薄壳厚度和指根汇合；不将局部膜片误建为整只蝙蝠。')

    f=feather([0,0,0],[.022,0,.90],.164,'#E5DCC8',curve=.018,asym=.28)
    fs=placed([f],[0,0,0],[-90,0,0])
    fs.append(tube([[0,0,0],[.005,.25,.008],[.014,.60,.018],[.021,.88,.005]],[.007,.006,.0035,.0015],'#BFA778',6))
    apply('l1.creature.wing.primary_feather',fs,'重建两侧不对称的连续羽片，偏置羽轴顺弧度贴合羽面，羽根窄、羽端渐尖。')

    apply('w.fauna.canine_paw',[paw(.046,.079,.071,'#765439')],'以单一闭合壳塑造犬掌四趾、脚背和踝根，保留足底零平面与原始装配尺寸。',dimensioned=False)

    # Species-specific canine/fox cranial stations rather than one recoloured head.
    for ident,fox in [('w.fauna.dog.head',False),('w.fauna.fox.head',True)]:
        col='#B07843' if fox else '#94704D'
        stations=([(-.052,.028,.068,.086),(-.01,.054,.10,.111),(.054,.021,.111,.088),(.101,-.013,.060,.048),(.174,-.030,.030,.026),(.193,-.030,.020,.018)] if fox else
            [(-.044,.037,.062,.082),(.004,.052,.103,.108),(.057,.019,.107,.092),(.094,-.010,.064,.055),(.145,-.020,.046,.035),(.178,-.019,.025,.024)])
        body=profile_z(stations,col,20);fs=[body]+eyes_side(body,.045,.068,.013,'#9E8B48')
        for s in (-1,1):
            e=ear_cup([[-.031,0],[.036,0],[.030,.055],[.018,.126],[-.012,.096]],col,'#B19783',.015)
            fs += placed([e],[s*.066,.095,-.016],[0,s*10,s*-12],scale=[1.12 if fox else 1,1.03 if fox else .92,1])
            f=surface_patch(body,[[-.023,.048],[-.055,.076],[-.050,.115],[-.032,.151],[-.020,.131],[-.009,.094]],'#E4D5BD',.0007,axis=0);fs.append(f if s>0 else mirror_x(f))
        fs.append(nose_front([0,-.017,.187 if fox else .169],[.023,.027,.012]))
        apply(ident,fs,'以物种专属额颊和吻长控制环重建；眼睑与口鼻分色投射贴合，厚耳根、鼻尖和下颌共同形成清晰犬科轮廓。',dimensioned=False)

    for ident,sheep in [('w.fauna.cow.head',False),('w.fauna.sheep.head',True)]:
        sx=.59 if sheep else 1.;col='#75553C' if sheep else '#AA794A'
        stations=[(-.052,.063,.179*sx,.212*sx),(.015,.071,.223*sx,.261*sx),(.082,.02,.236*sx,.246*sx),(.166,-.037,.184*sx,.17*sx),(.255,-.062,.151*sx,.115*sx),(.303,-.058,.139*sx,.106*sx)]
        body=profile_z(stations,col,20);fs=[body]+eyes_side(body,.064,.092,.028*sx,'#3F352A')
        snout=profile_z([(.237,-.058,.129*sx,.10*sx),(.271,-.058,.17*sx,.119*sx),(.318,-.055,.153*sx,.108*sx)],'#C69E92' if not sheep else '#624933',16);fs.append(snout)
        for side in (-1,1):
            fs.append(surface_patch(snout,circle(.020*sx,(side*.075*sx,-.039),12,scale=(1,.61)),'#664F48',.001,axis=2))
            earout=[[-.024,0],[.045,.005],[.092,.039],[.166,.086],[.179,.109],[.145,.122],[.067,.094],[.008,.049]]
            e=ear_cup(earout,col,'#B8937A',.025)
            fs += placed([e],[side*.182*sx,.099,-.023],[0,side*4,-(22 if sheep else 0)*side],scale=[side*sx,sx,sx])
        if not sheep:
            # A small frontal blaze follows the forehead, without detached polygon shards.
            fs.append(surface_patch(body,[[-.022,.231],[.017,.229],[.040,.151],[.023,.071],[-.019,.046],[-.036,.132]],'#DFD2BA',.0008,axis=2))
        apply(ident,fs,'依据额头、眼眶、长吻和颌部重建头型；耳片横向展开并有真实耳腔，鼻孔和眼部贴合支撑表面。',dimensioned=False)

    # Equine hoof is a single toe, not a split cattle hoof.
    fs=[hoof_half(0,.047,.067,.073,'#614A38')]
    fs.append(spin([(.030,.067),(.034,.068),(.033,.078),(.029,.080)],'#775B43',16))
    apply('w.fauna.hoof',fs,'单蹄以蹄冠收束、外展蹄壁和前圆后缓的着地轮廓重建，避免岩石块观感。',dimensioned=False)
