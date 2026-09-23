"""Facial landmarks, continuous clothing and articulated finger control rings."""
from .common import *
from l1_expansion.common import transform_matrix


def facial_nose():
    # Bridge, tip, alae, nostril rims: continuous shell, not a tetrahedron.
    p=[[-.017,.068,0],[.017,.068,0],[-.030,.020,0],[.030,.020,0],[-.042,0,0],[.042,0,0],[-.030,-.018,.01],[.030,-.018,.01],[0,-.023,.020],
       [-.012,.060,.020],[.012,.060,.020],[-.019,.018,.044],[.019,.018,.044],[-.015,-.003,.056],[.015,-.003,.056],
       [-.036,-.003,.027],[.036,-.003,.027],[0,-.017,.039]]
    f=[[0,1,10,9],[0,9,11,2],[1,3,12,10],[9,10,12,11],[11,12,14,13],[2,11,13,15,4],[3,5,16,14,12],
       [13,14,17],[15,13,17,8,6],[14,16,7,8,17],[4,15,6],[5,7,16],[0,2,4,6,8,7,5,3,1]]
    return mesh(p,f,'skin')


def author():
    body=organic_profile([(-.141,.058,.055,.065,.013),(-.121,.083,.073,.073,.004),(-.088,.104,.088,.088,0),
        (-.050,.120,.100,.103,-.005),(-.018,.130,.103,.113,-.004),(.022,.130,.102,.119,-.005),
        (.067,.130,.112,.112,-.010),(.108,.121,.108,.098,-.015),(.145,.088,.075,.073,-.020),(.164,.035,.028,.024,-.019)],'skin',20)
    fs=[body]
    for side in (-1,1):
        cx=side*.056;cy=.017
        fs.append(surface_patch(body,almond(cx,cy,.027,.0125),'skinShade',.001))
        fs.append(surface_patch(body,almond(cx,cy,.021,.0085),'#F4E9D6',.002))
        fs.append(surface_patch(body,circle(.0072,(cx,cy),12,scale=(.78,1)),'#52656A',.003))
        fs.append(surface_patch(body,circle(.0048,(cx,cy),10,scale=(.77,1)),'ink',.004))
        brow=[[cx-side*.027,.045],[cx+side*.022,.047],[cx+side*.023,.053],[cx-side*.018,.053]]
        fs.append(surface_patch(body,brow,'hair',.002))
        out=[(-.023,-.046),(.010,-.047),(.027,-.019),(.030,.022),(.013,.050),(-.012,.052),(-.021,.027)]
        ear=ear_cup(out,depth=.013)
        fs += placed([ear],[side*.133,-.004,-.014],[0,side*62,side*-4], [.73,.90,.8])
    nose=facial_nose()
    for p in nose['points']:
        p[0]*=.60;p[1]=p[1]*.84-.034;p[2]=p[2]*.80+.087
    fs.append(nose)
    fs.append(surface_patch(body,[[-.028,-.076],[-.01,-.074],[0,-.077],[.011,-.074],[.028,-.076],[.01,-.081],[0,-.083],[-.012,-.081]],'#B47C65',.002))
    fs.append(surface_patch(body,[[-.027,-.079],[.027,-.079],[.01,-.082],[-.012,-.082]],'#8F6357',.0025))
    # Bake local attachment transforms before the same lower-jaw deformation is
    # applied to skull AND projected eyes/lips/ears. This prevents parameter drift.
    for f in fs:
        m=np.asarray(transform_matrix(f),float)
        f['points']=[(m@np.array([*p,1.]))[:3].tolist() for p in f['points']]
        for key in ('position','rotation','scale','matrix'):f.pop(key,None)
        for p in f['points']:
            weight=max(0,min(1,(-p[1]-.035)/.09))
            p[0]=mul(p[0],Q('face_width'),add(1,mul(weight,O('sub',Q('jaw_width'),1))))
    # The nasal root stays on the face; only the forward relief changes.
    for p in nose['points']:p[2]=add(.087,mul(p[2]-.087,Q('nose_length')))
    apply('core.human.head',fs,'以额头、颧部、眼眶、口颏与下颌控制环重建头颅；五官按真实头壳投射贴合，保留脸宽、下颌和鼻长参数。',dimensioned=False,
          contracts={'eye_attachment':'ray-projected-to-author-shell','face_parameters_preserved':True})

    # Palm stays on the original wrist datum, fingers retain the grip switch.
    fs=[organic_profile([(-.078,.030,.015,.013,.012),(-.061,.042,.022,.018,.011),(-.035,.044,.026,.022,.008),(-.010,.035,.026,.023,.002),(0,.032,.025,.024,0)],'skin',12)]
    for i,(x,L) in enumerate([(-.028,.053),(-.009,.063),(.010,.058),(.028,.044)]):
        rr=[]
        for t,rad in [(0,.0103),(.27,.0106),(.52,.009),(.76,.0081),(1,.0048)]:
            straight_y=-.068-L*t;straight_z=.011+.018*t*t
            theta=t*math.pi*.95;grip_y=-.068-.027*math.sin(theta);grip_z=.013+.036*(1-math.cos(theta))*.68
            rr.append([x+(i-1.5)*.0015*t,choice('grip',{'false':straight_y,'true':grip_y}),choice('grip',{'false':straight_z,'true':grip_z}),rad,rad*.92])
        fs.append(loft(rr,'skin',10,smooth_angle=0))
    fs.append(loft([[-.030,-.019,.006,.017,.019],[-.044,-.029,.021,.017,.017],[-.050,-.045,.038,.014,.014],[-.039,-.063,.055,.010,.010],[-.030,-.070,.053,.006,.007]],'skin',10))
    apply('core.human.hand',fs,'重建掌弓、拇指根与多节渐细手指；保留握持开关和工具抓握接口，去除平行柱式指形。',dimensioned=False,contracts={'grip_switch_retained':True})

    fs=[organic_profile([(.025,.158,.13,.15,0),(.08,.165,.132,.145,-.005),(.14,.145,.110,.129,-.012),(.19,.088,.06,.075,-.020)],'hair',16)]
    for side in (-1,1):
        for strand in range(3):
            path=[];rads=[]
            for j in range(42):
                t=j/41;a=t*math.tau*3.8+strand*math.tau/3;r=.020*(1-.62*t)
                path.append([side*(.135+.028*t)+r*math.cos(a),.035-.49*t,.028+r*math.sin(a)])
                rads.append(.015*(1-.65*t))
            fs.append(tube(path,rads,'hair' if strand!=1 else 'hairLight',sides=7))
        fs.append(ellipsoid([side*.160,-.45,.028],[.031,.046,.034],'hair',10,5))
        fs.append(ring_tube([side*.16,-.405,.028],.021,.016,.006,'navy',plane='xz',n=16,sides=6))
    apply('exp.wear.braids',fs,'用三股连续交织发束替代串珠；逐段收尖并以发圈收束，保留头部覆盖与左右辫布局。',dimensioned=False)

    # An open front coat shell. Form follows the torso and flares toward hem.
    rows=[(-.64,.27,.165),(-.53,.258,.165),(-.30,.229,.167),(-.08,.221,.17),(.11,.249,.165),(.20,.22,.13)]
    pp=[];n=20
    angles=np.linspace(.28,math.tau-.28,n)
    for inset in (0,.018):
        for y,rx,rz in rows:
            for a in angles:pp.append([(rx-inset)*math.sin(a),y,(rz-inset)*math.cos(a)])
    M=len(rows)*n;ff=[]
    for layer in (0,M):
        for j in range(len(rows)-1):
            for k in range(n-1):a=layer+j*n+k;ff.append([a,a+1,a+n+1,a+n])
    edge=list(range(n))+[j*n+n-1 for j in range(1,len(rows))]+list(range(M-2,M-n-1,-1))+[j*n for j in range(len(rows)-2,0,-1)]
    for a,b in zip(edge,edge[1:]+edge[:1]):ff.append([a,b,M+b,M+a])
    fs=[mesh(pp,ff,'#52647A')]
    # Lapels are fitted to the upper shell, not pale floating sticks.
    for side in (-1,1):
        outline=[[side*.19,.185],[side*.072,.193],[side*.068,.04],[side*.13,.084]]
        support=deepcopy(fs[0]);support['faces']=[f for f in support['faces'] if all(i<M for i in (f if isinstance(f,list) else f['v']))]
        fs.append(surface_patch(support,outline,'#E1D4BD',.007))
        fs.append(block([.105,.073,.023],[side*.145,-.31,.137],'#697A8D',.012,rotation=[0,side*22,0]))
    for y in (-.13,-.27,-.41):
        fs.append(placed([cyl(.012,.010,'#C2B6A0',sides=12)],[.064,y,.158],[90,0,0])[0])
    apply('exp.wear.winter_coat',fs,'重建绕躯干连续薄衣壳、收腰与外展下摆；前襟开口、翻领和袋口贴合衣身，保留穿戴坐标。',dimensioned=False)

    ear=ear_cup([[-.024,.017],[.008,0],[.043,.023],[.063,.083],[.062,.156],[.039,.201],[.002,.213],[-.031,.184],[-.044,.117],[-.039,.054]],depth=.022)
    # Antihelix follows the bowl and joins at both ends.
    fs=[ear,tube([[-.017,.046,.006],[.002,.069,.010],[.011,.105,.009],[-.004,.153,.011],[.015,.177,.011]],[.007,.008,.007,.005,.004],'skin',sides=7)]
    apply('l1.character.face.ear',fs,'以单一连续壳构造耳轮、耳甲腔和耳垂，内腔下陷；细耳轮接入主体而非外挂块。')

    outer=almond(0,0,.081,.045);inner=almond(0,0,.064,.028)
    fs=[plate(outer,.009,'skin',holes=[inner])]
    fs.append(tube([[-.073,-.001,.004],[-.044,.035,.006],[0,.044,.004],[.043,.033,.005],[.073,.001,.004]],[.003,.006,.006,.005,.003],'skin',8))
    apply('l1.character.face.eyelid',fs,'将圆管环改为完整杏仁形眼睑薄壳，上睑更厚、下睑更缓，眼角连续闭合。')
    fs=placed([facial_nose()],[0,.045,0],scale=[1.15,1.95,1.45])
    apply('l1.character.face.nose',fs,'由鼻梁、鼻尖、鼻翼和鼻底多层控制面重建立体鼻部，保持背面贴合基准。')

    fs=[]
    for i,(x,L,lean) in enumerate([(-.19,.255,.035),(-.105,.205,.052),(-.018,.28,.063),(.073,.24,.057),(.164,.30,.015)]):
        p=bezier([[x,.27,0],[x-.018,.24,.066],[x+lean,.13,.093],[x+lean*.82,.27-L,.071]],12)
        rr=[(.055*(1-t)+.007*t,.032*(1-t)+.003*t) for t in np.linspace(0,1,12)]
        fs.append(tube(p,rr,['hair','hairLight','hair','hair','hairLight'][i],sides=8))
    apply('l1.character.hair.fringe',fs,'按不等长主发束和侧发束重建弧形刘海，发根相接、发尾渐细，避免等距梳齿。')

    fs=[]
    for i,(x,L) in enumerate([(-.06,.12),(-.02,.145),(.02,.135),(.06,.104)]):
        p=bezier([[x,0,0],[x,.055,-.004],[x+.004,L,.025],[x+.006,L*.91,.050]],10)
        fs.append(tube(p,[.018*(1-.40*t)+.0015*math.sin(t*math.pi*3) for t in np.linspace(0,1,10)],'#74513B',sides=10,material='mat.leather'))
    apply('l1.character.handfoot.glove_fingers',fs,'保留四指子件语义，增加指节弧度、长短差和渐细截面；修正手套误用木材材质。')

    outline=[[-.025,.17],[.025,.17],[.021,.128],[.010,.116],[.028,-.12],[0,-.16],[-.028,-.12],[-.010,.116],[-.021,.128]]
    fs=[plate(outline,.007,'navy',at=(0,0,.173))]
    fs.append(plate([[-.022,.166],[.022,.166],[.014,.126],[-.014,.126]],.008,'#445C6E',at=(0,0,.178)))
    apply('w.wear.tie',fs,'将领结和领带主体连接为有厚度的连续剪影，补结部折面并消除交界间隙。',dimensioned=False)
