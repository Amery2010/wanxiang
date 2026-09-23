"""Load paths for robot frames and coherent geological surfaces."""
from .common import *
from .aero import foil


def triangulated_cap(points,offset=0,reverse=False):
    from shapely.geometry import Polygon
    from shapely.ops import triangulate
    p=Polygon(points);out=[]
    pts=np.asarray(points)
    for tri in triangulate(p):
        if not p.covers(tri):continue
        ids=[offset+int(np.argmin(np.linalg.norm(pts-np.array(q),axis=1))) for q in list(tri.exterior.coords)[:3]]
        out.append(ids[::-1] if reverse else ids)
    return out


def heightfield(fn,nx,nz,xrange,zrange,bottom,colorfn):
    pp=[]
    for j in range(nz+1):
        for i in range(nx+1):
            x=xrange[0]+(xrange[1]-xrange[0])*i/nx;z=zrange[0]+(zrange[1]-zrange[0])*j/nz;pp.append([x,fn(x,z),z])
    ff=[]
    for j in range(nz):
        for i in range(nx):
            a=j*(nx+1)+i;b=a+1;c=b+nx+1;d=a+nx+1
            for ids in ([a,d,b],[b,d,c]):ff.append({'v':ids,'color':colorfn(np.array([pp[k] for k in ids]).mean(0).tolist())})
    edge=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,nz+1)]+[nz*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(nz-1,0,-1)]
    N=len(pp);pp.extend([[pp[k][0],bottom,pp[k][2]] for k in edge]);n=len(edge)
    for j in range(n):ff.append({'v':[edge[j],edge[(j+1)%n],N+(j+1)%n,N+j],'color':'#665D4C'})
    ff.append({'v':list(range(N+n-1,N-1,-1)),'color':'#665D4C'})
    return mesh(pp,ff,'stone')


def shard(at,size,color,phase=0):
    x,y,z=at;w,h,d=size
    outline=[[-.50,-.33],[-.16,-.52],[.40,-.40],[.52,.18],[.19,.48],[-.35,.40]]
    pp=[]
    for j,(yy,sx,sz,dx,dz) in enumerate([(0,1,1,0,0),(.57,1.02,.87,.035,-.025),(1,.50,.61,.06,.025)]):
        for k,(a,b) in enumerate(outline):
            xx=w*(a*sx+dx);zz=d*(b*sz+dz);pp.append([x+xx*math.cos(phase)-zz*math.sin(phase),y+h*(yy+(.07*math.sin(k*2) if j>0 else 0)),z+xx*math.sin(phase)+zz*math.cos(phase)])
    ff=[];n=len(outline)
    for j in range(2):
        for k in range(n):ff.append([j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k])
    ff += [list(range(n-1,-1,-1)),list(range(2*n,3*n))]
    return mesh(pp,ff,C(color),material='mat.stone')


def tiled_cliff(ident):
    # Read the pre-repair author, not a stale generated JSON. The source edge
    # height profile is interpolated exactly, to protect adjacent scene tiles.
    from wanxiang.semantic import evaluate,parameter_values
    d=BASELINE[ident]
    old=evaluate(d['shape_params']['forms'][0],parameter_values(d.get('parameter_schema',{}),{}))
    arr=np.array(old['points'][:81],float).reshape(9,9,3);ys=arr[:,:,1]
    def old_height(x,z):
        u=(x+2)*2;v=(z+2)*2;i=min(7,max(0,int(u)));j=min(7,max(0,int(v)));a=u-i;b=v-j
        return (1-a)*(1-b)*ys[j,i]+a*(1-b)*ys[j,i+1]+a*b*ys[j+1,i+1]+(1-a)*b*ys[j+1,i]
    def fn(x,z):
        h=old_height(x,z);w=max(0,1-(x/2)**2)*max(0,1-(z/2)**2)
        slope=min(1,max(0,(2.47-h)*3))*min(1,max(0,h*4))
        terr=(round(h/.43)*.43-h)*.85
        return h+w*slope*(terr+.105*math.sin(x*3.4+z*.4)*math.sin(z*2.8+.2))
    def color(p):
        x,y,z=p;h=old_height(x,z)
        if h>=2.40:return '#789554'
        if h<=.12:return '#7E825C'
        return ['#8A8977','#96937F','#7D8076','#A09A82'][int(max(0,y)/.42)%4]
    return heightfield(fn,24,24,(-2,2),(-2,2),-.3,color)


def author():
    arc=[[.42*math.cos(a),0,.42*math.sin(a)] for a in np.linspace(math.radians(20),math.radians(160),29)]
    fs=[sweep(arc,rect(.095,.108,r=.013),'rubber',material='mat.rubber')]
    fs.append(block([.45,.045,.12],[0,.0225,0],'#60727D',.007))
    for s in (-1,1):
        fs.append(beam([s*.175,.015,.036],[s*.205,.015,.338],.035,'metalDark',depth=.031))
        fs.append(block([.071,.068,.041],[s*.205,.010,.334],'metalDark',.006))
    apply('l1.robot.housing.bumper',fs,'弧形橡胶防撞条与内侧安装横梁之间增加两条实际支撑，所有力路闭合，橡胶截面与支架材料明确区分。')

    corners=[[-.12,-.08],[.12,-.08],[.12,.08],[-.12,.08]];fs=[]
    for x,z in corners:fs.append(tube([[x,0,z],[x,.75,z]],[.019,.019],'metal',10))
    for y in (.012,.25,.50,.738):
        for i,(x,z) in enumerate(corners):xx,zz=corners[(i+1)%4];fs.append(tube([[x,y,z],[xx,y,zz]],[.011,.011],'metal',8))
    for j in range(3):
        for i,(x,z) in enumerate(corners):
            xx,zz=corners[(i+1)%4];a=[x,.016+j*.241,z];b=[xx,.016+(j+1)*.241,zz]
            if (j+i)%2:a,b=[xx,a[1],zz],[x,b[1],z]
            fs.append(tube([a,b],[.009,.009],'metalLight',8))
    apply('l1.robot.link.lattice',fs,'四根主弦杆由端框、横框和交错斜腹杆连接成空间桁架；杆端嵌入节点，避免几根独立立杆。')

    fs=[spin([(.181,-.05),(.208,-.047),(.219,-.030),(.219,.027),(.211,.047),(.181,.049),(.164,.039),(.163,-.027)],'#DEE3D8',40)]
    fs.append(spin([(0,-.041),(.030,-.041),(.039,-.027),(.039,.012),(.029,.032),(0,.038)],'#7F8D92',24))
    for i in range(3):
        a=i*120;rad=math.radians(a)
        fs.append(tube([[.025*math.cos(rad),-.026,.025*math.sin(rad)],[.182*math.cos(rad),-.026,.182*math.sin(rad)]],[.009,.009],'#79888D',8))
        blade=foil([(.027,.029,0,.013,.13,24),(.065,.052,.002,.013,.105,19),(.118,.043,.004,.013,.08,13),(.155,.021,.009,.013,.065,9)],'#536A70',14)
        fs+=placed([blade],[0,0,0],[0,a,0])
    apply('p5.drone.duct',fs,'导管增设圆润入口与下部静止支架，电机由三支杆连接外圈；三枚有厚度和桨距的叶片在支架上方留隙旋转。',dimensioned=False,contracts={'stator_plane_y':-.026,'rotor_reference_y':.013,'rotor_radius':.155,'duct_inner_min':.163})

    fs=[spin([(0,-.06),(.041,-.06),(.050,-.048),(.050,.041),(.043,.052),(.030,.061),(0,.063)],'metalDark',24)]
    blade=foil([(.032,.039,0,.044,.15,24),(.074,.059,-.003,.044,.13,20),(.188,.049,.009,.044,.095,13),(.259,.024,.019,.044,.08,9)],'rubber',18)
    fs += [blade]+placed([blade],[0,0,0],[0,180,0])
    apply('w.robot.drone_rotor',fs,'重建双叶桨：叶根进入轮毂，弦宽由根到梢变化，桨距和厚度逐渐收小；修正直条悬在电机上方。',dimensioned=False)

    outline=[[-2.18,0],[-1.31,0],[-1.30,.70],[-1.34,1.36],[-1.08,1.93],[-.66,2.20],[-.10,2.31],[.46,2.28],[1.00,1.95],[1.27,1.41],[1.24,.69],[1.27,0],[2.12,0],[2.24,.84],[2.12,1.68],[1.77,2.29],[1.15,2.85],[.56,3.15],[-.22,3.23],[-1.02,3.04],[-1.63,2.65],[-2.14,2.04],[-2.31,1.18]]
    n=len(outline);pp=[];layers=[]
    for j,z in enumerate([-.57,-.24,.22,.57]):
        ring=[]
        for k,(x,y) in enumerate(outline):
            factor=min(1,y/.6);dx=.055*math.sin(k*1.63+j*1.45)*factor;dy=.049*math.sin(k*1.1+j*.9)*factor
            ring.append([x+dx,y+dy]);pp.append([x+dx,y+dy,z])
        layers.append(ring)
    ff=[]
    for j in range(3):
        for k in range(n):ff.append({'v':[j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k],'color':['#82877C','#7B8178','#92968A'][(k//3+j)%3]})
    ff += triangulated_cap(layers[0],0,True)+triangulated_cap(layers[-1],3*n)
    apply('exp.terrain.cave_arch',[mesh(pp,ff,'#858A80',material='mat.stone')],'洞口改为不对称自然岩拱，入口、内壁和后口共享连续厚壁；岩层方向与拱顶受力形态协调，去掉外挂小石。',dimensioned=False)
    for ident in ('exp.terrain.cliff_outer','exp.terrain.cliff_straight'):
        apply(ident,[tiled_cliff(ident)],'在保留四边原有拼接高度的前提下细化内部崖面：加入断层台阶与受控起伏，草皮只留在上部，露出岩层分面。',dimensioned=False,contracts={'boundary_height':'bilinear interpolation of 3.8.0 edge samples','tile_extent':[-2,2,-2,2]})

    def flow(u,v):
        x=(u-.5)*1.03;shape=(.5+.5*math.cos(u*math.tau*5+.22*math.sin(v*4)))**1.7
        z=-.14*v+.128*shape*(.65+.35*(1-v))+.012*math.sin(v*math.tau*3+u*2)
        return [x,1.2*v,z]
    fs=[grid_shell(flow,40,28,.040,'#B1AB91',axis=(0,0,1),smooth_angle=32)]
    apply('l1.terrain.cave.flowstone',fs,'流石帘采用连成一体的薄厚变化面，竖向沉积褶脊交融且带轻微层纹；不再并排摆放独立石柱。')

    outline=rect(2.0,1.0,r=.13);n=len(outline);pp=[];levels=[0,.18,.235,.27,.52,.56,.60,.82,.858,.899,1.15,1.19,1.23,1.49]
    for j,y in enumerate(levels):
        scale=.96+.035*math.sin(j*2.1);dx=.023*math.sin(j*.7)
        for k,(x,z) in enumerate(outline):pp.append([x*scale+dx,y+(.030*math.sin(k*1.4+j*.35) if j not in(0,len(levels)-1) else 0),z*(.94+.066*math.sin(k*1.7+j*.8))])
    ff=[]
    for j in range(len(levels)-1):
        for k in range(n):ff.append({'v':[j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k],'color':['#777F79','#858B80','#9A9A87'][min(2,j%4)]})
    ff += [list(range(n-1,-1,-1)),list(range((len(levels)-1)*n,len(levels)*n))]
    apply('l1.terrain.cliff.layered',[mesh(pp,ff,'stone',material='mat.stone')],'层理岩壁以单一连续岩体重建，层厚不等、断面轻微错动、细窄层缝内收；不再堆叠整齐独立砖板。')

    def slope(x,z):return float(np.interp(x,[-1,-.5,.15,1],[.27,.47,1.19,1.66]))+.035*math.sin(x*8+z*4)*max(0,1-(z/.6)**2)
    fs=[heightfield(slope,20,14,(-1,1),(-.6,.6),0,lambda p:'#939587' if p[0]>.12 else '#858B81')]
    for j in range(13):
        x=-.91+(j%5)*.235;z=-.45+(j//5)*.38+.038*math.sin(j*2);h=slope(x,z);size=[.19+.07*math.sin(j*.9)**2,.10+.06*math.sin(j*2.1)**2,.15+.1*math.sin(j)**2]
        fs.append(shard([x,h-.025,z],size,'#777F78' if j%2 else '#A0A293',j*.63))
    apply('l1.terrain.cliff.talus',fs,'崖脚由连续坡体承接大小不同的棱角岩屑，碎屑半埋入坡面并向低处集中；取消底边之外排列的多面球。')

    from scipy.spatial import Voronoi
    from shapely.geometry import Polygon,box as sb
    rng=np.random.default_rng(390151);seeds=rng.uniform(-1,1,(22,2));allseeds=np.concatenate([seeds+[dx,dz] for dx in (-2,0,2) for dz in (-2,0,2)])
    vor=Voronoi(allseeds);region=sb(-1,-1,1,1);fs=[block([2,.171,2],[0,.0855,0],'#5C4939',.0)]
    for i,p in enumerate(allseeds):
        rr=vor.regions[vor.point_region[i]]
        if not rr or -1 in rr:continue
        cell=Polygon(vor.vertices[rr]).buffer(-.0065,join_style=2).intersection(region)
        if cell.is_empty or cell.area<.0004:continue
        if cell.geom_type!='Polygon':continue
        fs.append(shape_extruded(cell,.168,.048+ .010*math.sin(i*1.7)**2,['#94734E','#A17D53','#886B49'][i%3]))
    apply('l1.terrain.surface.dried',fs,'干泥块以周期邻域细胞分割形成真实连续龟裂，裂缝露出下层深土；泥片大小、顶高有受控差异，删除稀疏直线划痕。')

    def lava(x,z):
        phase=math.tau*(z*2.5+.16*math.sin(x*3.1)+.055*math.sin(x*8))
        return .185+.110*(.5+.5*math.sin(phase))**1.8+.029*math.sin(x*4.2+z*.8)**2
    fs=[heightfield(lava,36,36,(-1,1),(-1,1),0,lambda p:['#4E514B','#5D6055','#6F7060'][min(2,max(0,int((p[1]-.18)/.05)))])]
    apply('l1.terrain.surface.lava',fs,'凝固熔岩表面采用有流向的弧形绳状褶脊和连续深谷，层次来自网格起伏而非随机散点小山。')
