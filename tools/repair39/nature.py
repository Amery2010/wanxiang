"""Botanical silhouettes, thin laminae and continuous branching forms."""
from .common import *


def lamina(outline,color='leaf',ridge=.013,thickness=.0025,center=None,holes=None,zfront=None,zback=None,res=(6,14)):
    """XY leaf: shared triangular fan, convex/concave boundary triangulated in UV.

    Unlike the old ground-plane leaf, this part's curvature is along local Z.
    A thin closed underside is kept for glTF double-sided-independent rendering.
    """
    from shapely.geometry import Polygon
    from shapely.ops import triangulate
    shape=Polygon(outline, holes=holes or [])
    if not shape.is_valid:raise ValueError('Invalid leaf outline')
    # Insert an interior spine using clipped strips, so concave leaves never fan
    # triangles across the basal notch or the spaces between oak lobes.
    minx,miny,maxx,maxy=shape.bounds
    xs=np.linspace(minx,maxx,res[0]+1);ys=np.linspace(miny,maxy,res[1]+1)
    from shapely.geometry import box as sb
    uv=[];faces=[];lookup={}
    def vid(p):
        k=tuple(round(float(v),10) for v in p)
        if k not in lookup:lookup[k]=len(uv);uv.append(list(k))
        return lookup[k]
    for a,b in zip(xs,xs[1:]):
        for c,d in zip(ys,ys[1:]):
            geom=shape.intersection(sb(a,c,b,d))
            for part in getattr(geom,'geoms',[geom]):
                if part.geom_type!='Polygon' or part.area<1e-12:continue
                for tri in triangulate(part):
                    if part.covers(tri.representative_point()):faces.append([vid(q) for q in list(tri.exterior.coords)[:3]])
    def zfun(x,y):
        t=(y-miny)/(maxy-miny);u=(x-(minx+maxx)/2)/max((maxx-minx)/2,1e-8)
        return ridge*(1-.65*abs(u))*math.sin(math.pi*t)+ridge*.18*u*u
    pp=[[x,y,(zfront or zfun)(x,y)] for x,y in uv];N=len(pp);pp += [[x,y,zback(x,y) if zback else z-thickness] for x,y,z in pp]
    ff=faces+[list(reversed([i+N for i in f])) for f in faces]
    from collections import Counter
    ed=Counter(tuple(sorted((a,b))) for f in faces for a,b in zip(f,f[1:]+f[:1]))
    for (a,b),count in ed.items():
        if count==1:ff.append([a,b,b+N,a+N])
    return mesh(pp,ff,C(color),smooth_angle=38)


def narrow_leaf(root,tip,width,color,curve=.012,thickness=.002,up=(0,1,0)):
    """Twenty-eight triangles, closed curved blade for sub-centimetre foliage."""
    A=np.asarray(root,float);B=np.asarray(tip,float);U=np.asarray(up,float);direction=B-A
    side=np.cross(direction,U);side/=max(np.linalg.norm(side),1e-9)
    pp=[A.tolist()]
    for t,w in ((.27,.72),(.65,1.)):
        center=A+(B-A)*t+U*curve*math.sin(math.pi*t)
        for q in (-1,0,1):pp.append((center+side*width*.5*w*q+U*(thickness*.4 if q==0 else 0)).tolist())
    pp.append(B.tolist());N=len(pp);pp += [(np.array(v)-U*thickness).tolist() for v in pp]
    top=[[0,2,1],[0,3,2],[1,2,5],[1,5,4],[2,3,6],[2,6,5],[4,5,7],[5,6,7]]
    edge=[0,1,4,7,6,3];faces=top+[[i+N for i in f[::-1]] for f in top]
    faces += [[a,b,b+N,a+N] for a,b in zip(edge,edge[1:]+edge[:1])]
    return mesh(pp,faces,C(color))


def lance_xy(a,b,w,color='leaf',curve=.012):
    return narrow_leaf([*a,0],[*b,0],w,color,curve,.0015,(0,0,1))


def crown_mass(at,size,color,phase=0,lobes=5):
    """Deliberate flattened leaf-cluster tiers rather than a stack of ico spheres."""
    n=20;pp=[];rings=[(-.46,.18),(-.36,.64),(-.15,.96),(.14,1),(.33,.74),(.46,.24)]
    for j,(y,r) in enumerate(rings):
        for k in range(n):
            a=k*math.tau/n;rr=r*(1+.13*math.cos(lobes*a+phase)+.04*math.sin(3*a-j*.3))
            pp.append([at[0]+size[0]*.5*rr*math.cos(a),at[1]+size[1]*(y+.025*math.sin(a*3+phase)),at[2]+size[2]*.5*rr*math.sin(a)])
    ff=[]
    palette=[C(color),C(color),'#568A49' if color=='leaf' else C(color)]
    for j in range(len(rings)-1):
        for k in range(n):ff.append([j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k])
    ff += [list(range(n-1,-1,-1)),list(range((len(rings)-1)*n,len(rings)*n))]
    return mesh(pp,ff,C(color),smooth_angle=0)


def united_crown(positions,palette,resolution=23):
    """A shared, closed lobed crown. Smooth-min joins do not leave intersecting skins.

    Voxel sampling is an author-time operation only; the shipped recipe contains
    the actual low-poly surface and needs neither skimage nor a voxel runtime.
    """
    from skimage.measure import marching_cubes
    centers=np.array([x[0] for x in positions],float)
    radii=np.array([x[1] for x in positions],float)*.5
    lo=(centers-radii).min(0);hi=(centers+radii).max(0)
    margin=(hi-lo).max()*.12;lo-=margin;hi+=margin
    step=(hi-lo).max()/resolution
    axes=[np.arange(lo[k],hi[k]+step,step) for k in range(3)]
    grid=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1)
    field=None;blend=min(radii.max(),.25)*.6
    for c,r in zip(centers,radii):
        d=(np.linalg.norm((grid-c)/r,axis=-1)-1)*r.min()
        if field is None:field=d
        else:
            h=np.clip(.5+.5*(d-field)/blend,0,1)
            field=d*(1-h)+field*h-blend*h*(1-h)
    points,faces,_,_=marching_cubes(field.astype(np.float32),0,spacing=(step,step,step),allow_degenerate=False)
    points+=lo
    colors=[]
    for f in faces:
        q=points[f];n=np.cross(q[1]-q[0],q[2]-q[0]);n/=max(np.linalg.norm(n),1e-12)
        # Discrete broad light-facing regions, never random face colours.
        light=.38*n[0]+.85*n[1]+.35*n[2]
        shade=0 if light<-.35 else 1 if light<.25 else 2 if light<.73 else 3
        colors.append({'v':f.tolist(),'color':palette[shade]})
    return mesh(points.tolist(),colors,palette[1],smooth_angle=0)


def canopy(maple=False,small=False):
    base=['#477E40','#588D46','#699849','#7AA450'] if not maple else ['#A84B29','#BF5B2D','#D67934','#DEA046']
    positions=[([0,.50,0],[2.42,1.45,2.16]),([-.91,.43,.25],[1.47,1.10,1.43]),([.80,.65,-.27],[1.57,1.28,1.47]),([.31,1.01,.34],[1.75,1.19,1.5]),([-.29,.76,-.68],[1.62,1.21,1.36]),([.87,.37,.67],[1.29,1.03,1.11])]
    return [united_crown(positions,base,24),united_crown(positions,base,15)]


def petal(root,tip,w,color,curve=.06):
    return leaf(root,tip,w,color,curve=curve,thickness=.004)


def author():
    fs=[united_crown([([0,.18,0],[1.10,.75,1.02]),([.13,.65,.01],[.79,.67,.73]),([-.23,-.015,.13],[.69,.57,.71])],['#477D3D','#548946','#67964B','#74A053'],23)]
    apply('core.nature.crown_cluster',fs,'用共享闭合网格融合不对称主次叶团，保留分枝层级和冠缘起伏；消除叶团相交接缝及规则球堆外观。',dimensioned=False)

    fs=[]
    for j in range(5):
        y=j*.52
        fs.append(spin([(0,y),(.072,y),(.074,y+.030),(.069,y+.12),(.067,y+.36),(.071,y+.489),(.077,y+.505),(.077,y+.518),(.072,y+.523),(0,y+.523)],'#77984F',16))
        fs.append(spin([(.074,y+.5),(.081,y+.504),(.081,y+.517),(.073,y+.526)],'#ABB578',16))
    for j,side in [(1,-1),(3,1),(4,-1)]:
        y=(j+1)*.52-.015;path=bezier([[side*.052,y,0],[side*.23,y+.075,.01],[side*.40,y+.21,.03],[side*.63,y+.22,.055]],12)
        fs.append(tube(path,[.017*(1-t)+.003 for t in np.linspace(0,1,12)],'#769249',8))
        for k,t in enumerate(np.linspace(.22,.90,5)):
            p=np.array(path[min(11,int(t*11))]);sg=(-1 if k%2 else 1)
            for dz in (-.04,.035):
                tip=p+[side*.14,-.12+sg*.11,sg*.19+dz]
                fs.append(leaf(p.tolist(),tip.tolist(),.062,'#5F8742',curve=.027,thickness=.003))
    apply('exp.nature.bamboo_culm',fs,'竹节具有收腰、膨大节环和连续节间；枝条从节部萌发，并配置方向有变化的狭长叶片。',dimensioned=False)

    from scipy.spatial import ConvexHull
    pp=[]
    for j,(y,rx,rz) in enumerate([(0,.77,.58),(.12,1.05,.79),(.58,1.10,.90),(1.15,.75,.74),(1.47,.41,.36)]):
        for k in range(9):
            a=(k+.19*j)*math.tau/9;r=1+.10*math.sin(k*2.3+j*.8)
            pp.append([rx*r*math.cos(a)+.13*y,y if j in (0,4) else y+.08*math.sin(k*1.8),rz*r*math.sin(a)])
    hull=ConvexHull(np.array(pp));f=[]
    shades=['#8A918A','#92978D','#7E8884','#9CA196']
    for i,tri in enumerate(hull.simplices):f.append({'v':tri.tolist(),'color':shades[(i//5)%len(shades)]})
    apply('exp.nature.boulder',[mesh(pp,f,'#8B928A',material='mat.stone')],'重建单一闭合岩体，底面稳定落地，主断面和少量次转折决定形状；移除外挂小球和杂乱碎块。',dimensioned=False)

    pp=[];n=48;N=12
    for j in range(N):
        t=j/(N-1);y=.014+.81*t;rad=.44*math.sin(math.pi*(.12+.87*t))**.72
        for k in range(n):
            a=k*math.tau/n;r=rad*(1+.105*math.cos(a*12));pp.append([r*math.cos(a),y,r*math.sin(a)])
    ff=[]
    for j in range(N-1):
        for k in range(n):ff.append([j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k])
    ff += [list(range(n-1,-1,-1)),list(range((N-1)*n,N*n))];fs=[mesh(pp,ff,'#52855B')]
    for j in range(2,10,2):
        t=j/(N-1);y=.014+.81*t;rad=.44*math.sin(math.pi*(.12+.87*t))**.72*1.105
        for k in range(12):
            a=k*math.tau/12;p=np.array([rad*math.cos(a),y,rad*math.sin(a)])
            fs.append(ellipsoid(p.tolist(),[.023,.029,.023],'#D1BB8B',8,4))
            for delta in (-.022,.025):fs.append(tube([p.tolist(),(p+np.array([.025*math.cos(a),delta,.025*math.sin(a)])).tolist()],[.0024,.0008],'#DFD0AB',5))
    for a in np.linspace(0,math.tau,7,endpoint=False):fs.append(petal([0,.805,0],[.08*math.cos(a),.849,.08*math.sin(a)],.064,'#D9A64C',.035))
    apply('exp.nature.cactus_globe',fs,'建立十二道连续纵肋、沿肋分布的刺座和短刺，顶部花朵与生长点连接，保留球形仙人掌的饱满体积。',dimensioned=False)

    fs=[]
    for i in range(9):
        a=i*math.tau/9;reach=.54+.13*math.sin(i*2.4)**2
        path=bezier([[0,.015,0],[.13*math.cos(a),.47,.13*math.sin(a)],[.46*math.cos(a),.40,.46*math.sin(a)],[reach*math.cos(a),.19,reach*math.sin(a)]],19)
        fs.append(tube(path,[.010*(1-t)+.0016 for t in np.linspace(0,1,19)],'#527641',7))
        for k in range(3,18,2):
            t=k/18;p=np.array(path[k]);d=np.array([-math.sin(a),0,math.cos(a)]);f=np.array([math.cos(a),0,math.sin(a)])
            for s in (-1,1):
                tip=p+d*s*(.145*math.sin(math.pi*t)**.7)+f*.065+np.array([0,-.025,0])
                fs.append(leaf(p.tolist(),tip.tolist(),.043*(1-.45*t),'#5F8944' if k%4 else '#73974D',curve=.022,thickness=.002))
    apply('exp.nature.fern_rosette',fs,'重建九条自然弯曲的羽状蕨叶，叶轴从中心抽生；小羽片沿轴成对排列并向叶尖缩短，避免平面钉耙轮廓。',dimensioned=False)
    apply('exp.nature.leaf_crown',canopy(),'以一体化多叶团冠层替换相交叠片；冠顶、侧冠与低枝形成连贯轮廓，提供两档真实几何细节。',dimensioned=False)
    apply('exp.nature.maple_crown',canopy(True),'建立暖色主次叶团及较细的冠缘裂叶轮廓；叶冠不是简单给同一组球体改色，色区遵循受光面和分枝层级。',dimensioned=False)

    out=[]
    # A modest stem notch, not a quarter of the pad removed.
    for a in np.linspace(.12,math.tau-.12,48):out.append([.47*math.cos(a),.47*math.sin(a)])
    out.append([.035,0]);fs=[slab_polygon(out,.018,.012,'#4E874B')]
    for a in np.linspace(.25,math.tau-.25,9):fs.append(tube([[0,.031,0],[.36*math.cos(a),.031,.36*math.sin(a)]],[.0023,.0006],'#6C9C5B',5))
    for layer,(count,rad,y,width) in enumerate([(9,.205,.085,.115),(8,.155,.126,.086),(6,.105,.150,.063)]):
        for k in range(count):
            a=(k+.3*layer)*math.tau/count
            fs.append(petal([.015*math.cos(a),.035,.015*math.sin(a)],[rad*math.cos(a),y,rad*math.sin(a)],width,['#D9BFC7','#ECD7DA','#F4E7DE'][layer],curve=.052))
    fs.append(ellipsoid([0,.103,0],[.083,.075,.083],'#DDBD5F',12,5))
    apply('exp.nature.water_lily',fs,'荷叶保留窄V形缺口与细叶脉；花朵由三层错位花瓣包裹花心，花瓣有弧度和厚度，不再用球块围成花环。',dimensioned=False)

    crown_lobes=[([0,.59,0],[1.22,1.05,1.12])]
    for j in range(7):
        a=j*math.tau/7+.17;reach=.79+.08*math.sin(2.1*j)
        crown_lobes.append(([reach*math.cos(a),.31+.10*math.sin(1.8*j),reach*math.sin(a)],[1.02,1.16+.28*math.sin(1.9*j)**2,.94]))
    fs=[united_crown(crown_lobes,['#54823C','#619042','#709B4A','#7BA554'],24)]
    for i in range(16):
        a=i*math.tau/16;r=1.42+.16*math.sin(i*2.3);h=-1.28-.28*math.sin(i*1.7)**2
        path=bezier([[.12*math.cos(a),.40,.12*math.sin(a)],[r*math.cos(a),1.04,r*math.sin(a)],[(r+.20)*math.cos(a),-.30,(r+.20)*math.sin(a)],[(r-.1)*math.cos(a),h,(r-.1)*math.sin(a)]],27)
        fs.append(tube(path,[.024*(1-t)**1.5+.0018 for t in np.linspace(0,1,27)],'#7B7950',6))
        for k in range(7,26,2):
            p=np.array(path[k]);side=np.array([-math.sin(a),0,math.cos(a)])
            for s in (-1,1):
                tip=p+side*s*.13+np.array([.025*math.cos(a),-.25,.025*math.sin(a)])
                fs.append(narrow_leaf(p.tolist(),tip.tolist(),.052,'#719B4B' if (i+k)%3 else '#86A656',curve=.022,thickness=.002))
    apply('exp.nature.willow_curtain',fs,'重建从冠顶弧垂至低处的十六条细枝，狭长叶片逐段着生；去除倒锥状帘条，保留柳冠透空和参差下垂边缘。',dimensioned=False)

    # Slightly convex bark panel with small, surface-conforming moss patches.
    def bark(u,v):return [(u-.5)*.40,.70*v,.014+.031*(1-(u*2-1)**2)]
    body=grid_shell(bark,14,16,.034,'#796348',axis=(0,0,1));fs=[body]
    for i,(x,y,rx,ry) in enumerate([(-.06,.19,.105,.13),(.072,.34,.099,.12),(-.06,.47,.113,.108),(.044,.58,.097,.085)]):
        outline=[[x+rx*(1+.13*math.sin(5*a+i))*math.cos(a),y+ry*(1+.1*math.cos(4*a))*math.sin(a)] for a in np.linspace(0,math.tau,20,endpoint=False)]
        fs.append(surface_patch(body,outline,['#547C42','#648949'][i%2],.0015))
    apply('l1.nature.bark.moss_collar',fs,'苔层沿弧形树皮逐面贴合，用不规则连续斑块与低起伏表达，不再悬挂数个绿色球块。')

    configs=[('arch',[[-.3,0,0],[-.32,.98,.035],[.26,1.0,.06],[.30,.12,0]],.065,.014),('drooping',[[0,0,0],[-.04,.88,.01],[.48,.86,.10],[.39,.24,.08]],.065,.010)]
    for name,path,r0,r1 in configs:
        curve=bezier(path,25);fs=[tube(curve,[r0*(1-t)**1.2+r1*t for t in np.linspace(0,1,25)],'wood',12)]
        apply('l1.nature.branch.'+name,fs,'用连续曲率、多截面半径递减和自然弯曲取代折线拐角；根部保留装配直径，梢端逐渐变细。')
    path=bezier([[0,0,0],[-.018,.33,0],[.01,.57,.01],[0,.85,0]],18)
    fs=[tube(path,[.065*(1-t)+.039*t for t in np.linspace(0,1,18)],'wood',12)]
    sec=bezier([[0,.265,0],[.16,.37,.018],[.27,.62,.028],[.32,.75,0]],17);fs.append(tube(sec,[.049*(1-t)**1.25+.012 for t in np.linspace(0,1,17)],'wood',12))
    sec2=bezier([[.21,.48,.018],[.25,.66,-.01],[.33,.80,-.03],[.39,.87,-.05]],13);fs.append(tube(sec2,[.023*(1-t)+.005 for t in np.linspace(0,1,13)],'wood',9))
    apply('l1.nature.branch.braced',fs,'将机械三角撑形改为生物分枝：主枝、外侧分枝及细侧梢连续弯曲，分叉根部渐粗并埋入母枝。')
    fs=[tube(bezier([[0,0,0],[0,.36,0],[.02,.46,0],[.35,.50,0]],20),[.067*(1-t)**1.4+.012 for t in np.linspace(0,1,20)],'wood',12)]
    fs.append(tube(bezier([[.003,.33,0],[-.025,.44,.01],[-.18,.49,.018],[-.30,.50,.02]],16),[.047*(1-t)**1.3+.009 for t in np.linspace(0,1,16)],'wood',10))
    apply('l1.nature.branch.t_fork',fs,'T形分叉改为渐开、渐细的枝杈，颈部截面连续过渡并扩大根部接触，避免横杆直接焊接竖杆。')

    fs=[spin([(0,0),(.065,0),(.115,.07),(.121,.53),(.079,.68),(.014,.72),(0,.72)],'#C5A03D',16)]
    for j in range(11):
        y=.047+j*.059;rad=.118*(.74+.26*math.sin(math.pi*(j+1)/12))
        for k in range(12):
            a=(k+.48*(j%2))*math.tau/12
            f=ellipsoid([0,0,0],[.066,.068,.047],['#DDB845','#E8C04A','#D2A93A'][(k+j)%3],8,4)
            fs+=placed([f],[rad*math.cos(a),y,rad*math.sin(a)],[0,90-math.degrees(a),0])
    apply('l1.nature.crop.corn_cob',fs,'玉米粒沿穗轴十二列密排并错位贴合，顶底渐收，粒根嵌入穗芯，去掉稀疏悬浮珠串外观。')

    # Five-lobed bell: shared outer/inner surfaces, open lip and connected base.
    pp=[];n=40;rows=9
    for inner in (False,True):
        for j in range(rows):
            t=j/(rows-1)
            for k in range(n):
                a=k*math.tau/n;r=(.052+.22*t**1.4)*(1+.13*t*t*math.cos(5*a))-(.006 if inner else 0)
                y=.035+.405*t+.026*t**5*math.cos(5*a)
                pp.append([r*math.cos(a),y,r*math.sin(a)])
    ff=[];NN=n*rows
    for b in (0,NN):
        for j in range(rows-1):
            for k in range(n):ff.append([b+j*n+k,b+j*n+(k+1)%n,b+(j+1)*n+(k+1)%n,b+(j+1)*n+k])
    for j in (0,rows-1):
        for k in range(n):a=j*n+k;b=j*n+(k+1)%n;ff.append([a,b,b+NN,a+NN])
    fs=[mesh(pp,ff,'#8B76AD')]
    for k in range(5):
        a=k*math.tau/5;fs.append(tube([[0,.039,0],[.045*math.cos(a),.255,.045*math.sin(a)]],[.004,.0025],'#D8C893',6));fs.append(ellipsoid([.045*math.cos(a),.255,.045*math.sin(a)],[.014,.023,.014],'#DBC05A',8,4))
    apply('l1.nature.flower.bell',fs,'重建五裂钟形花冠、连续薄花壁和开放花口，花口起伏与五枚内部花蕊对应，不是平滑杯壳。')
    fs=[]
    for k in range(6):
        a=k*math.tau/6;fs.append(petal([.035*math.cos(a),.025,.035*math.sin(a)],[.255*math.cos(a),.397,.255*math.sin(a)],.268,'#E7AAAB',curve=.036))
    fs.append(spin([(0,0),(.056,0),(.057,.066),(.02,.086),(0,.087)],'#8D9A4B',12))
    for k in range(7):
        a=k*math.tau/7;fs.append(tube([[0,.047,0],[.073*math.cos(a),.227,.073*math.sin(a)]],[.004,.0028],'#DACDA2',6));fs.append(ellipsoid([.073*math.cos(a),.227,.073*math.sin(a)],[.018,.027,.018],'#D8AE47',8,4))
    apply('l1.nature.flower.cup',fs,'用相互搭接的六片弧形花瓣构成花杯，保留自然瓣间线和内部花蕊；花瓣根部与花托相接。')
    fs=[ellipsoid([0,.22,0],[.284,.284,.284],'#C98399',16,8)]
    # Phyllotactic distribution removes horizontal tiers. Each cupped petal
    # starts inside the core, crosses its neighbours and curls towards the tip.
    # Stable golden-angle sampling is deterministic, not random face noise.
    for k in range(94):
        theta=math.acos(1-1.88*(k+.5)/94)
        angle=k*math.pi*(3-math.sqrt(5))
        def flower_surface(u,v,a=angle,theta=theta):
            t=theta+.29-.62*v
            width=(.008+.225*math.sin(math.pi*v)**.53)/max(.30,math.sin(theta))
            ang=a+(2*u-1)*width
            radius=.133+.073*math.sin(math.pi*v*.5)+.009*(2*u-1)**2*math.sin(math.pi*v)
            return [radius*math.sin(t)*math.cos(ang),.22+radius*math.cos(t),radius*math.sin(t)*math.sin(ang)]
        normal=(math.sin(theta)*math.cos(angle),math.cos(theta),math.sin(theta)*math.sin(angle))
        shade=0 if theta>2 else 1 if theta>1.3 else 2 if theta>.7 else 3
        fs.append(grid_shell(flower_surface,3,5,.0032,['#C88499','#CE8FA2','#D89CAF','#DFAABD'][shade],axis=normal))
    apply('l1.nature.flower.pompom',fs,'以黄金角叶序分布杯状短瓣包裹球形花心，瓣根进入核心；花瓣沿球面错位弯曲搭接，消除同纬环状平台与悬空花冠。')

    fs=[tube([[0,0,0],[0,.53,.018],[0,1,.028]],[.020,.012,.003],'#627548',9)]
    for row in range(5):
        y=.14+row*.151;reach=.34*(1-.12*row)
        for s in (-1,1):
            end=[s*reach,y+.14,.025];fs.append(tube([[0,y,.01],end],[.008,.002],'#6D854A',7))
            for j in range(1,7):
                t=j/7;p=[s*reach*t,y+.14*t]
                for sy in (-1,1):fs.append(lance_xy(p,[p[0]+s*.044,p[1]+sy*.052],.027,'#699249',.003))
    apply('l1.nature.frond.bipinnate',fs,'建立叶轴—一级羽轴—二级小羽片三级结构；细叶片成对贴着羽轴生长，避免只见枝杆的梳齿状轮廓。')

    path=[[0,0,0],[-.01,.20,0],[-.025,.43,.002]]
    center=np.array([.105,.658,.012])
    for t in np.linspace(0,1,39):
        a=math.pi+t*math.tau*1.17;rad=.148*(1-t)+.012*t;path.append((center+[rad*math.cos(a),rad*math.sin(a),0]).tolist())
    fs=[tube(path,[.023*(1-t)+.005 for t in np.linspace(0,1,len(path))],'#6F884C',10)]
    for j in range(4,33,3):
        p=np.array(path[j]);d=p-center;d[2]=0;d/=max(np.linalg.norm(d),1e-8);q=p+d*(.044*(1-j/45));fs.append(lance_xy(p[:2],q[:2],.023,'#88A15C',.003))
    apply('l1.nature.frond.curled',fs,'重建连续收紧的拳卷叶尖，曲率和半径沿卷曲递减，并配置紧贴叶轴的幼小羽片，不是等径问号管。')

    fs=[]
    for j in range(6):
        y=.058+j*.067;r=.111*math.sin(math.pi*(j+.85)/7)**.7
        for k in range(9):
            a=(k+.5*(j%2))*math.tau/9
            fs.append(ellipsoid([r*math.cos(a),y,r*math.sin(a)],[.088,.084,.088],['#A73E42','#B74A4C','#C65351'][(j+k)%3],10,5))
    fs.append(tube([[0,.384,0],[.012,.46,.002]],[.012,.006],'#6F7D42',8))
    apply('l1.nature.fruit.aggregate',fs,'用错位紧排的小核果组织自然卵形聚合果；小果相互接触并沿端部收束，保留果梗连接。')

    # Continuous pocketed cap. Each cell has a rim shared with neighbours, and
    # an inward inset face. No ring meshes hover in front of a smooth cone.
    n=14;rows=8;pp=[]
    def cap(t,a,depth=0):
        r=(.023+.159*math.sin(math.pi*(.06+.94*t))**.70)-depth
        return [r*math.cos(a),.16+.58*t,r*math.sin(a)]
    for j in range(rows+1):
        for k in range(n):pp.append(cap(j/rows,(k+.45*(j%2)+.06*math.sin(2*k+j))*math.tau/n))
    ff=[]
    for j in range(rows):
        for k in range(n):
            ids=[j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k];outer=np.array([pp[v] for v in ids]);mid=outer.mean(0);inner=[]
            for v in outer:
                p=mid+(v-mid)*.60;rr=math.hypot(p[0],p[2]);p[[0,2]]*=max(.1,(rr-.016)/rr);inner.append(len(pp));pp.append(p.tolist())
            for a in range(4):ff.append([ids[a],ids[(a+1)%4],inner[(a+1)%4],inner[a]])
            ff.append({'v':inner,'color':'#695338'})
    ff += [list(range(n-1,-1,-1)),list(range(rows*n,(rows+1)*n))]
    fs=[mesh(pp,ff,'#AE9367'),spin([(0,0),(.068,0),(.073,.033),(.059,.17),(.081,.22),(0,.22)],'#D8C9A0',16)]
    apply('l1.nature.fungus.morel',fs,'帽体按连续共享边界构建内凹蜂窝坑，坑底压入主体并以深色分面表达；补足菌柄，移除悬浮圆环假纹理。')

    # Banana: shallow edge splits, central midrib in actual centimetre-scale units.
    out=[]
    for s,ts in [(1,np.linspace(0,1,24)),(-1,np.linspace(1,0,24))]:
        for t in ts:
            w=.107*math.sin(math.pi*t)**.65
            if .15<t<.9 and (int(t*23)%7==3):w*=.82
            out.append([s*max(w,.001),.048+.50*t])
    body=lamina(out,'#6A9447',.019);fs=[body,tube([[0,0,0],[0,.16,.01],[0,.44,.019],[0,.543,.002]],[.005,.004,.0024,.0006],'#AAC36E',7)]
    apply('l1.nature.leaf.banana',fs,'构建长椭圆香蕉叶、连续中肋和少量边缘裂口，叶片以薄弧面承载细节；不保留粗大外露骨架。')

    fs=[tube([[0,0,0],[.01,.135,.005],[0,.24,.015]],[.0045,.0038,.0028],'#78934F',7)]
    for a in (90,210,330):
        rad=math.radians(a);axis=np.array([math.cos(rad),math.sin(rad)]);side=np.array([-axis[1],axis[0]])
        pts=[]
        # Round paired lobes at the distal end; small terminal cleft.
        local=[(0,0),(-.035,.025),(-.066,.074),(-.057,.119),(-.029,.137),(0,.12),(.029,.137),(.057,.119),(.066,.074),(.035,.025)]
        for u,v in local:pts.append((np.array([0,.24])+axis*v+side*u).tolist())
        fs.append(lamina(pts,'#619547',.011));fs.append(tube([[0,.24,.006],*(list(p)+[.010] for p in [np.array([0,.24])+axis*.08])],[.0025,.001],'#90AF60',6))
    apply('l1.nature.leaf.clover',fs,'三片倒心形小叶在同一叶柄顶端汇合，末端有浅裂和独立中脉；修正沿杆错排的假三叶草。')

    # Base notch points towards the petiole, tip towards +Y.
    heart=[[-.004,.18],[-.062,.126],[-.112,.143],[-.145,.201],[-.142,.272],[-.105,.356],[-.052,.452],[0,.544],[.052,.452],[.105,.356],[.142,.272],[.145,.201],[.112,.143],[.062,.126],[.004,.18]]
    body=lamina(heart,'#7D9C50',.02);fs=[body,tube([[0,0,0],[0,.11,.008],[0,.19,.011]],[.004,.0035,.0025],'#9DB56B',7)]
    for t in (.31,.45,.60,.76):
        y=.18+.35*t;w=.105*(1-t*.7)
        for s in (-1,1):
            pts=[[0,y],[s*w,y-.046]]
            for a,b in zip(pts,pts[1:]):
                z1=surface_coordinate(body,a);z2=surface_coordinate(body,b)
                fs.append(tube([[*a,z1+.0005],[*b,z2+.0005]],[.0017,.0005],'#AFBF7C',5))
    apply('l1.nature.leaf.heart',fs,'重建叶柄端心形凹口、宽肩与渐尖叶端；薄曲面和细叶脉遵循叶片边界，不再让粗枝延伸到叶外。')
    out=[[.166*math.cos(a),.315+.166*math.sin(a)] for a in np.linspace(0,math.tau,40,endpoint=False)]
    body=lamina(out,'#669B6C',.018);fs=[body]
    fs.append(tube(bezier([[0,0,-.002],[0,.15,-.025],[0,.30,-.04],[0,.315,.008]],14),[.0045]*(13)+[.006],'#87AF72',8))
    for a in np.linspace(0,math.tau,10,endpoint=False):
        points=[]
        for r in np.linspace(.008,.147,8):
            q=[r*math.cos(a),.315+r*math.sin(a)];points.append(q+[surface_coordinate(body,q)+.0006])
        fs.append(tube(points,[.0019*(1-t)+.0004 for t in np.linspace(0,1,8)],'#9AB982',5))
    apply('l1.nature.leaf.lotus',fs,'盾状圆叶采用近圆薄曲面，叶柄从背面接入叶心；放射叶脉止于叶缘内，移除穿出顶部的旧主杆。')

    out=[]
    for s,ts in [(1,np.linspace(.001,.999,37)),(-1,np.linspace(.999,.001,37))]:
        for t in ts:
            w=.121*math.sin(math.pi*t)**.74*(.80+.22*math.cos(t*math.tau*4.6))
            out.append([s*w,.065+.485*t])
    body=lamina(out,'#85964B',.021);fs=[body,tube([[0,0,0],[0,.18,.012],[0,.38,.022],[0,.54,.002]],[.004,.0035,.002,.0006],'#B0B273',6)]
    for t in (.18,.36,.55,.74):
        y=.065+.485*t;te=t+.022/.485;w=.121*math.sin(math.pi*te)**.74*(.80+.22*math.cos(te*math.tau*4.6))*.76
        for s in (-1,1):
            q=[s*w,y+.022];z=surface_coordinate(body,q);fs.append(tube([[0,y,surface_coordinate(body,[0,y])+.001],[q[0],q[1],z+.001]],[.0016,.0005],'#ADB373',5))
    apply('l1.nature.leaf.oak',fs,'沿中脉组织成对圆裂叶瓣和窄叶柄，叶缘、叶面隆起及脉线共同形成橡叶轮廓；摆脱多角盾牌外形。')

    fs=[]
    for i in range(7):
        a=i*math.tau/7;length=.68+.17*math.sin(i*1.9)**2
        path=bezier([[.07*math.cos(a),.83,.07*math.sin(a)],[.13*math.cos(a),.53,.13*math.sin(a)],[.29*math.cos(a+.17),.21,.25*math.sin(a+.17)],[.24*math.cos(a+.31),.83-length,.21*math.sin(a+.31)]],22)
        fs.append(tube(path,[.033*(1-t)**1.4+.003 for t in np.linspace(0,1,22)],'#A48A62',9))
    apply('l1.nature.root.aerial',fs,'气生根从上部束状生出，长度错落、下垂柔和、尖端变细；去除相同斜直粗棍。')
    fs=[tube(bezier([[0,.80,0],[-.025,.50,.012],[.02,.24,.01],[0,.02,0]],20),[.038*(1-t)+.015 for t in np.linspace(0,1,20)],'#997650',10)]
    for j in range(7):
        y=.12+j*.09;s=(-1)**j
        path=bezier([[0,y+.04,.008],[s*.055,y+.021,.035],[s*.112,y-.012,.037],[s*.15,y-.036,.032]],14)
        fs.append(tube(path,[.010*(1-t)+.0015 for t in np.linspace(0,1,14)],'#997650',7))
        fs.append(tube(bezier([[s*.075,y+.006,.034],[s*.095,y+.025,.038],[s*.118,y+.030,.035]],8),[.004*(1-t)+.0008 for t in np.linspace(0,1,8)],'#997650',6))
    apply('l1.nature.root.clinging',fs,'攀附根向同一支撑平面铺展，短根再分支且贴面变细，避免朝空间外伸出粗桩。')
    fs=[]
    for i in range(13):
        a=i*math.tau/13;r=.25+.095*math.sin(i*2.3)**2;yend=.025+.11*math.sin(i*1.6)**2
        path=bezier([[.025*math.cos(a),.83,.025*math.sin(a)],[.055*math.cos(a),.55,.055*math.sin(a)],[r*.9*math.cos(a),.24,r*.9*math.sin(a)],[r*math.cos(a+.15),yend,r*math.sin(a+.15)]],20)
        fs.append(tube(path,[.021*(1-t)**1.3+.0018 for t in np.linspace(0,1,20)],'#A38A63',8))
        for j in (9,13,16):
            p=np.array(path[j]);q=p+np.array([.075*math.cos(a+.6),-.11,.075*math.sin(a+.6)])
            fs.append(tube(bezier([p.tolist(),(p+[.03*math.cos(a),-.07,.03*math.sin(a)]).tolist(),q.tolist()],9),[.005*(1-t)+.0006 for t in np.linspace(0,1,9)],'#AA926B',6))
    apply('l1.nature.root.fibrous',fs,'须根由多条细主根及下级根须形成密集根束，根端参差、细度递减，区别于气生根和支柱根。')
    for name,n in [('mangrove',4),('prop',3)]:
        fs=[tube([[0,.88,0],[0,.55,0]],[.084,.065],'#947149',12)]
        for i in range(n):
            a=(i+.14)*math.tau/n;r=.38 if name=='mangrove' else .32
            path=bezier([[.01*math.cos(a),.80,.01*math.sin(a)],[r*.42*math.cos(a),.66,r*.42*math.sin(a)],[r*.99*math.cos(a),.28,r*.99*math.sin(a)],[r*math.cos(a),.026,r*math.sin(a)]],22)
            fs.append(tube(path,[.060*(1-t)**1.4+.018 for t in np.linspace(0,1,22)],'#947149',11))
        apply('l1.nature.root.'+name,fs,'以多向渐变弧根支撑主根颈部，分叉根部埋入母体，弯曲到脚端连续；与细须根保持清楚的形态差异。')

    fs=[ellipsoid([0,.07,0],[.035,.103,.035],'#9B8158',10,5),tube([[0,.10,0],[0,.265,0]],[.0025,.0018],'#B7A886',6)]
    for i in range(26):
        a=i*math.tau/26;r=.242+.019*math.sin(i*2.2);tip=[r*math.cos(a),.40+.031*math.sin(i*1.7),r*math.sin(a)]
        path=bezier([[0,.264,0],[r*.45*math.cos(a),.371,r*.45*math.sin(a)],tip],11);fs.append(tube(path,[.0017*(1-t)+.0006 for t in np.linspace(0,1,11)],'#DED8C5',5))
        p=np.array(path[6]);q=np.array(tip)
        for d in (-.024,.024):
            end=q+[d*math.sin(a),.01,-d*math.cos(a)];fs.append(tube([p.tolist(),end.tolist()],[.00085,.00035],'#E8E1CF',5))
    apply('l1.nature.seed.pappus',fs,'构造瘦果、细喙及放射羽状冠毛，细丝共享冠毛基点而非一圈粗白刺；轮廓轻透且可辨识。')

    n=24;pp=[]
    for y,r in [(-.078,.012),(-.088,.028),(-.072,.052),(-.038,.073),(.005,.081),(.045,.077),(.075,.054),(.079,.025),(.059,.012)]:
        for k in range(n):
            a=k*math.tau/n;rr=r*(1+.065*math.cos(5*a));yy=y+.0025*math.cos(5*a);pp.append([rr*math.cos(a),yy,rr*math.sin(a)])
    ff=[]
    for j in range(8):
        for k in range(n):ff.append([j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k])
    ff += [list(range(n-1,-1,-1)),list(range(8*n,9*n))];fs=[mesh(pp,ff,'#BF493E')]
    fs.append(tube([[0,.057,0],[.004,.086,.001],[.008,.112,.004]],[.007,.0048,.0035],'#72593C',7));fs.append(leaf([.005,.088,.003],[.061,.108,.022],.025,'#638B46',curve=.012,thickness=.0015))
    apply('w.farm.fruit',fs,'苹果重建肩部、五瓣微起伏、凹陷果柄窝和花萼端，果梗插入凹窝并附一片薄叶，不再是带杆多面球。',dimensioned=False)
