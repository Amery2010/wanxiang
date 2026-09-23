"""Functional open passages, true thread helices and readable bearing relationships."""
from .common import *


def thread(root,crest,start,length,turns,color='metalLight',width=.025,tipwidth=.008,fade=.06,segments_per_turn=32):
    """Radial/axial tooth section. The root deliberately penetrates the shaft.

    Unlike a spring sweep, its flanks stay in radial planes. Lead-ins fade into
    the root surface, preserving a closed tooth solid at both ends.
    """
    n=max(24,math.ceil(turns*segments_per_turn));pp=[]
    for j in range(n+1):
        t=j/n;a=t*turns*math.tau;y=start+length*t
        ramp=min(1,t/fade,(1-t)/fade) if fade else 1
        top=root+(crest-root)*max(.01,ramp)
        for r,dy in [(root,-width),(top,-tipwidth),(top,tipwidth),(root,width)]:
            pp.append([r*math.cos(a),y+dy,r*math.sin(a)])
    ff=[]
    for j in range(n):
        for k in range(4):ff.append([j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k])
    ff += [[3,2,1,0],list(range(n*4,n*4+4))]
    return mesh(pp,ff,color,material='mat.metal')


def author():
    outer=rect(.6,.22,(0,.11),.012);inner=rect(.449,.070,(0,.11),.003)
    n=len(outer);pp=[]
    # Aperture flares slightly at its visible entrance; no mesh covers the hole.
    for z,loop in [(-.125,outer),(.125,outer),(-.125,inner),(.125,rect(.473,.088,(0,.11),.003))]:
        pp.extend([[x,y,z] for x,y in loop])
    ff=[]
    for k in range(n):
        j=(k+1)%n
        ff += [[k,j,n+j,n+k],[2*n+k,3*n+k,3*n+j,2*n+j],[k,2*n+k,2*n+j,j],[n+k,n+j,3*n+j,3*n+k]]
    apply('l1.gameplay.cover.bullet_slot',[mesh(pp,ff,'#777E7E',material='mat.stone')],'保留原来已贯通的射击孔，改为一体化带孔墙体；孔口增加小幅外张侧壁，不再以四根盒体拼框。',contracts={'aperture_center_ray':'open +Z/-Z'})

    from shapely.geometry import Point,Polygon
    key=Point(0,.32).buffer(.085,quad_segs=6).union(Polygon([[-.041,.274],[.041,.274],[.07,.08],[-.07,.08]]))
    fs=[plate(rect(.38,.46,(0,.245),.044),.036,'copper',holes=[list(key.exterior.coords)[:-1]],material='mat.metal')]
    for x,y in [(-.145,.08),(.145,.08),(-.145,.407),(.145,.407)]:
        fs.append(placed([cyl(.014,.006,'metalLight',sides=12)],[x,y,.020],[90,0,0])[0])
    apply('l1.gameplay.lock.keyway',fs,'将钥匙孔框重建为完整圆角锁面板，圆孔与梯形槽连为真实开口，固定孔位明确但不遮挡钥匙通道。',contracts={'keyhole':'single connected through-hole'})

    fs=[spin([(0,0),(.105,0),(.109,.025),(.086,.041),(.073,.07),(.073,.505),(.087,.524),(.087,.55),(0,.55)],'l1Ivory',24)]
    path=[]
    for t in np.linspace(0,1,193):
        a=math.tau*5*t;path.append([.087*math.cos(a),.075+.41*t,.087*math.sin(a)])
    fs.append(sweep(path,circle(.014,n=8),'copper',material='mat.metal'))
    fs.append(tube([[.087,.075,0],[.101,.056,0],[.103,.028,0]],[.014,.014,.014],'copper',8))
    fs.append(tube([[.087,.485,0],[.09,.522,0],[.068,.540,0]],[.014,.014,.014],'copper',8))
    apply('l1.gameplay.trap.coil',fs,'用一条连续五圈绕线和明确引线取代独立圆环，绕线贴近绝缘芯，两端接入上下端子区域。')

    outline=[];teeth=24
    for i in range(teeth):
        for t,r in [(0,.272),(.55,.289),(.72,.329),(.87,.326)]:
            a=(i+t)*math.tau/teeth;outline.append([r*math.cos(a),r*math.sin(a)])
    fs=placed([plate(outline,.021,'metal',holes=[circle(.036,n=24)],material='mat.metal')],[0,.021,0],[90,0,0])
    fs.append(spin([(.076,.009),(.076,.041),(.063,.049),(.036,.049),(.036,.009)],'metalLight',24))
    apply('l1.gameplay.trap.saw',fs,'重建有同向前角和齿谷的薄锯片，盘体与轴套相接；轴心保留真实安装孔。')

    # Three helical cutting lands are part of the core surface, not loose cubes.
    pp=[];N=36;RINGS=25
    for j in range(RINGS):
        t=j/(RINGS-1);y=.70*t;radius=.252*(1-t)**.7+.009;phase=1.9*t
        for k in range(N):
            theta=k*math.tau/N;a=theta+phase;flute=max(0,math.sin(3*theta))**2
            r=radius*(1-.23*flute);pp.append([r*math.cos(a),y,r*math.sin(a)])
    ff=[]
    for j in range(RINGS-1):
        for k in range(N):
            a=(k+.5)*math.tau/N;phase=1.9*(j+.5)/(RINGS-1)
            col='#63717A' if math.sin(3*a)>.70 else '#A3ACAA'
            ff.append({'v':[j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k],'color':col})
    ff += [list(range(N-1,-1,-1)),list(range((RINGS-1)*N,RINGS*N))]
    fs=[mesh(pp,ff,'metalLight'),spin([(0,-.015),(.241,-.015),(.252,.025),(.216,.054),(0,.054)],'metalDark',24)]
    apply('exp.industry.drill_head',fs,'将块状刀齿改为与锥芯同一连续网格的三条螺旋切削刃和排屑槽，沿高度逐步收尖。',dimensioned=False)

    from shapely.geometry import LineString
    side=LineString([(-.17,.09),(.17,.09)]).buffer(.067,quad_segs=5)
    fs=[]
    for z in (-.135,.135):
        fs.append(plate(list(side.exterior.coords)[:-1],.030,'metal',holes=[circle(.033,(-.17,.09),16),circle(.033,(.17,.09),16)],at=(0,0,z),material='mat.metal'))
    for x in (-.17,.17):
        fs += placed([spin([(.059,-.115),(.067,-.096),(.067,.096),(.059,.115),(.028,.115),(.028,-.115)],'metalLight',20)],[x,.09,0],[90,0,0])
        fs += placed([spin([(.042,-.156),(.042,-.145),(.032,-.145),(.032,.145),(.042,.145),(.042,.156),(.023,.156),(.023,-.156)],'metalDark',16)],[x,.09,0],[90,0,0])
    apply('l1.industry.conveyor.chain_link',fs,'以两片带孔圆端耳板、滚子和贯穿轴套重建链节，销轴孔同轴，滚子位于耳板之间。')

    fs=[block([1.07,.045,.17],[0,.017,0],'metalDark',.007)]
    for a,b in [([-.19,.18,0],[.19,.18,0]),([-.235,.198,0],[-.49,.373,0]),([.235,.198,0],[.49,.373,0])]:
        A=np.array(a);B=np.array(b);d=B-A
        fs.append(tube([A.tolist(),(A+d*.08).tolist(),(A+d*.92).tolist(),B.tolist()],[.061,.076,.076,.061],'metal',16))
        aa=(A-d*.07).tolist();bb=(B+d*.07).tolist();fs.append(tube([aa,bb],[.020,.020],'metalLight',10))
        for p in (aa,bb):
            fs.append(beam([p[0],.038,0],p,.028,'metalDark',depth=.028))
    apply('l1.industry.conveyor.trough_roller',fs,'分开中间水平辊与左右斜辊，各自独立直轴；端部轴颈、间隙和下方托架明确，避免一根折杆的观感。')

    fs=[spin([(0,0),(.070,0),(.070,.052),(.089,.072),(.089,.586),(.071,.608),(.071,.65),(0,.65)],'metal',24)]
    fs.append(thread(.085,.135,.089,.46,4.6,'metalLight',width=.029,tipwidth=.009,fade=.05))
    apply('l1.industry.drive.worm',fs,'保留连续螺旋但改成径向梯形齿截面，齿根进入轴体；两端渐隐收尾，避免弹簧悬套于轴外。',contracts={'root_radius':.085,'shaft_radius':.089,'connected_root_overlap':.004})

    fs=[spin([(.117,0),(.12,.013),(.12,.484),(.113,.50),(.085,.50),(.085,0)],'metal',28)]
    fs.append(thread(.117,.136,.272,.191,4.8,'metalLight',width=.015,tipwidth=.0028,fade=.04))
    apply('l1.industry.pipe.threaded',fs,'以连续外螺纹、可辨齿侧和端部导入重建管牙，螺纹根与管壁相交，内部水道始终贯通。',contracts={'pipe_bore_radius':.085})

    fs=[spin([(.034,0),(.278,0),(.28,.020),(.265,.034),(.075,.036),(.069,.10),(.057,.115),(.034,.115)],'metal',28)]
    for k in range(7):
        a=k*math.tau/7
        path=[]
        for t in np.linspace(0,1,16):
            r=.069+.19*t;ang=a-.65*t*t;path.append([r*math.cos(ang),.069-.012*t,r*math.sin(ang)])
        # A upright thin blade, curved in XZ; a four-sided section keeps plate edges crisp.
        fs.append(sweep(path,[[-.010,-.036],[.010,-.036],[.010,.036],[-.010,.036]],'metalLight'))
    apply('l1.industry.process.impeller',fs,'建立轮毂、开口轴孔及七片后弯导流叶片；叶根接入底盘，径向流道连续可读。')

    profile=[(.112,-.32),(.124,-.29),(.124,-.20),(.171,-.168),(.212,-.096),(.226,0),(.212,.096),(.171,.168),(.124,.20),(.124,.29),(.112,.32),(.074,.32),(.074,-.32)]
    fs=placed([spin(profile,'metal',28)],[0,.23,0],[90,0,0])
    for s in (-1,1):
        fs += placed([spin([(.141,-.039),(.141,.039),(.075,.039),(.075,-.039)],'metalLight',6)],[0,.23,s*.265],[90,0,0])
    fs.append(spin([(.059,.378),(.078,.419),(.078,.45),(.045,.472),(.035,.472),(.035,.378)],'metalLight',12))
    fs.append(block([.045,.067,.045],[0,.484,0],'metalDark',.004))
    apply('l1.industry.valve.ball',fs,'以两端同轴贯通的鼓形阀体重建球阀外壳，双端六角接头及上方阀杆接口清晰，取消穿入实心球的假管道。',contracts={'flow_axis':'+Z/-Z','through_bore_radius':.074})
