"""Architectural repair: functional sections before ornamental detail."""
from .common import *
from shapely.geometry import Polygon, box as polygon_box, LineString
from shapely.ops import unary_union
from shapely.affinity import rotate


def column_base():
    return [spin([(0,0),(.25,0),(.265,.04),(.265,.075),(.235,.105),(.205,.15),(.195,1.02),(.215,1.075),(.215,1.13),(0,1.13)],'l1Ivory',24)]


def author():
    # Volutes sit on a load-bearing echinus, not on detached ornamental rings.
    fs=column_base()+[block([.72,.105,.49],[0,1.335,0],'l1Ivory',.018),
        spin([(0,1.075),(.215,1.075),(.27,1.14),(.30,1.23),(0,1.23)],'l1Ivory',24)]
    for side in (-1,1):
        # Two solid volute discs joined through the capital, front and back coils.
        fs.append(placed([spin([(0,0),(.128,0),(.145,.025),(.145,.31),(.128,.335),(0,.335)],'l1Ivory',24)], [side*.245,1.23,-.168],[90,0,0])[0])
        for z in (-.179,.179):
            p=[]
            for j in range(36):
                t=j/35;ang=math.pi*.55+math.tau*1.35*t;r=.125*(1-t)+.02*t
                p.append([side*(.245+r*math.cos(ang)),1.23+r*math.sin(ang),z])
            fs.append(tube(p,.012,'#CBC0A8',sides=6))
    apply('l1.architecture.column.ionic',fs,'重建承托钟体、实体卷涡板和双面螺卷；卷涡与顶板形成承托结构。',detail=[4,5,7,8])

    fs=column_base()+[spin([(0,.88),(.19,.88),(.21,1.0),(.285,1.19),(.31,1.28),(.31,1.32),(0,1.32)],'l1Ivory',24)]
    for j in range(12):
        a=j*math.tau/12
        def petal_surface(u,v,a=a):
            y=.945+.35*v
            r=.185+.144*v+.031*math.sin(math.pi*v)
            angle=a+(u-.5)*.50*math.sin(math.pi*v)**.55
            r+=.009*(1-abs(2*u-1))*math.sin(math.pi*v)
            return [r*math.cos(angle),y,r*math.sin(angle)]
        f=grid_shell(petal_surface,4,10,.014,'#E9DECA' if j%2 else '#DACEB7',axis=(math.cos(a),0,math.sin(a)))
        fs.append(f)
    fs.append(spin([(.30,1.29),(.33,1.30),(.33,1.34),(.30,1.34)],'l1Ivory',24))
    apply('l1.architecture.column.lotus',fs,'建立外展莲瓣、瓣脊、柱颈与顶口；瓣片沿柱冠包络交叠。',detail=list(range(2,14)))

    outline=[]
    for j in range(16):
        a=j*math.tau/16;rad=1 if j%4 in (0,3) else .70;outline.append([rad*math.cos(a),rad*math.sin(a)])
    fs=[loft([[0,.08+j*1.18/24,0,.208,.208] for j in range(25)],'l1Ivory',16,
        outline=outline,phase_degrees=0,twist_degrees=Q('twist_degrees'),smooth_angle=0),
        spin([(0,0),(.255,0),(.27,.025),(.27,.07),(.22,.10),(0,.10)],'l1Ivory',24),
        spin([(0,1.25),(.22,1.25),(.27,1.28),(.27,1.33),(0,1.33)],'l1Ivory',24)]
    apply('l1.architecture.column.twisted',fs,'共轴柱身沿真实路径长度渐进扭转；新增明确的总扭转角（度）参数，保留旧弧度配方行为。',
        parameters={'twist_degrees':number(110,0,240,'柱身总扭转角',5,'deg')},contracts={'twist':'degrees-v1','coaxial':True},detail=[1,2])

    sec=[]
    for i in range(17):
        a=math.pi+i*math.pi/16;sec.append([.25*math.cos(a),.26+.25*math.sin(a)])
    for i in range(16,-1,-1):
        a=math.pi+i*math.pi/16;sec.append([.217*math.cos(a),.26+.217*math.sin(a)])
    fs=[plate(sec,1.0,'l1Metal',at=(0,0,.5))]
    fs += [block([.037,.039,1.0],[s*.236,.26,.5],'l1Metal',.008) for s in (-1,1)]
    apply('l1.architecture.drainage.half_round',fs,'用真实开口U形截面重建檐槽，连续内壁与双口沿；两端保留贯通接水通道。',contracts={'opening':'top-and-ends','wall_m':.033})

    path=[[0,.72,0],[0,.54,0],[0,.38,.018],[0,.25,.075],[0,.16,.19],[0,.145,.34],[0,.145,.48]]
    fs=[pipe(path,.105,.016,'l1Metal',16)]
    fs.append(pipe([[0,.68,0],[0,.75,0]],.116,.012,'l1Metal',16))
    apply('l1.architecture.drainage.shoe',fs,'重建有壁厚的弯曲落水管，入口与出口均为环形开口；接管套环覆盖而不封闭流道。',contracts={'hollow':True,'wall_m':.016})

    # Periodic domino herringbone. Lattice area = 2*N; intersect after board inset.
    tile=polygon_box(-.65,-.65,.65,.65);N=3;step=1.3/(6*math.sqrt(2));boards=[]
    for i in range(-5,6):
        for j in range(-12,13):
            x=(N*i-j)*step;y=(N*i+j)*step
            for vertical in (False,True):
                p=polygon_box(x+N*step,y,x+(N+1)*step,y+N*step) if vertical else polygon_box(x,y,x+N*step,y+step)
                p=rotate(p,-45,origin=(0,0)).buffer(-.0018,join_style=2).intersection(tile)
                if not p.is_empty and p.area>1e-7:boards.append((p,vertical,(i+j)%3))
    fs=[block([1.3,.025,1.3],[0,.0125,0],'woodDark',.002)]
    for p,vertical,k in boards:
        fs.append(shape_extruded(p,.025,.044,['#A77548','#BA8754','#C69462'][k] if vertical else ['#B18453','#C08C5B','#AC7A4D'][k]))
    apply('l1.architecture.floor.herringbone',fs,'数学铺装格生成无重叠人字木板，按1.3米方形边界裁切；连续底板承托，板缝为真实间隙。',contracts={'tile_m':1.3,'periodic':True,'board_gap_m':.0036,'subfloor':True})

    fs=[block([1.3,.025,1.3],[0,.0125,0],'woodDark',.002)]
    for iz in range(4):
        for ix in range(4):
            for k in range(3):
                x=-.65+(ix+.5)*.325;z=-.65+(iz+.5)*.325
                dx,dz=(.325-.004,.325/3-.004) if (ix+iz)%2==0 else (.325/3-.004,.325-.004)
                if (ix+iz)%2==0:z+=(k-1)*.325/3
                else:x+=(k-1)*.325/3
                fs.append(block([dx,.043,dz],[x,.047,z],['#BA895A','#A67849','#C79561'][(k+ix)%3],.0015))
    apply('l1.architecture.floor.parquet',fs,'重建可周期铺设的篮编拼花方块，板条同层分区且无交叠；整块底衬消除缺口。',contracts={'tile_m':1.3,'periodic':True})

    fs=[block([1.2,.065,.075],[0,y,0],'l1Slate',.01) for y in (.04,1.085)]
    fs += [block([.05,1.045,.05],[s*.56,.56,0],'l1Slate',.007) for s in (-1,1)]
    # Continuous S scrolls touch both rails through designed straight leads.
    for x in (-.36,0,.36):
        p=bezier([[x,.08,0],[x-.24,.28,0],[x+.25,.35,0],[x,.565,0]],14)
        p+=bezier([[x,.565,0],[x-.25,.79,0],[x+.24,.92,0],[x,1.05,0]],14)[1:]
        fs.append(tube(p,.022,'l1Metal',sides=8))
        for sign,y in ((1,.32),(-1,.79)):
            p=[]
            for j in range(28):
                t=j/27;a=sign*(.2+1.5*math.pi*t);r=.13*(1-t)+.023*t
                p.append([x+r*math.cos(a),y+r*math.sin(a),0])
            fs.append(tube(p,.017,'l1Metal',sides=8))
    apply('l1.architecture.railing.scroll',fs,'以连接上下横档的连续S形主栅条和收卷细枝重建涡线，不再重复环饰模板。')

    fs=[]
    for iz in range(4):
        for ix in range(4):
            # Shared periodic S profile; overlapping lips stay close to one sheet thickness.
            def fn(u,v,ix=ix,iz=iz):
                x=-.8+ix*.4+u*.412;z=-.8+iz*.4+v*.455
                return [x,.10+.24*(z+.8)/1.6+.06*math.sin((x+.8)*math.tau/.4)+iz*.012,z]
            fs.append(grid_shell(fn,12,3,.019,['#AA6049','#B96B50','#B0654D'][(ix+iz)%3]))
    apply('l1.architecture.roof.pantile',fs,'连续S形瓦壳带真实厚度，按横向波形搭接与纵向压叠铺排；保留可见口沿和排水方向。')

    # Broken voussoir: radial inner/outer faces, damaged outer skin only.
    outer=[[.82*math.cos(a),.05+.82*math.sin(a)] for a in np.linspace(.43,1.31,8)]
    inner=[[.51*math.cos(a),.05+.51*math.sin(a)] for a in np.linspace(1.31,.43,8)]
    fs=[plate(outer+inner,.45,'stone',at=(-.37,0,0))]
    apply('l1.architecture.ruin.broken_arch',fs,'以径向楔形重建断拱石，内外弧与两侧连接面明确；断裂保留在非配合表面。')
    ps=[Polygon([(-.55,-.35),(.12,-.35),(.03,-.13),(.14,.05),(.06,.35),(-.55,.35)]),
        Polygon([(.13,-.35),(.55,-.35),(.55,.35),(.073,.35),(.154,.051),(.047,-.128)])]
    fs=[shape_extruded(p,0,.115,['stone','stoneLight'][i]) for i,p in enumerate(ps)]
    apply('l1.architecture.ruin.cracked_slab',fs,'保留大面积共面石板，窄曲折主裂缝贯穿板厚；去除夸大的屋脊式V形缺口。')
    p=[];n=16
    for j,(y,r) in enumerate([(0,.24),(.045,.28),(.11,.25),(.62,.245)]):
        for k in range(n):
            a=k*math.tau/n;top=y+( .12*math.sin(a*3)+.045*math.cos(a*5) if j==3 else 0)
            p.append([r*math.cos(a),top,r*math.sin(a)])
    f=[]
    for j in range(3):
        for k in range(n):a=j*n+k;b=j*n+(k+1)%n;f.append([a,b,b+n,a+n])
    f += [list(range(n-1,-1,-1)),list(range(3*n,4*n))]
    apply('l1.architecture.ruin.fractured_column',[mesh(p,f,'stone')],'从完整圆柱截面生成不规则断口，保留主轴、基座与大段完整侧壁。')

    # Deterministic planar subdivisions, not crossing rods. Shared boundaries are united.
    from shapely import voronoi_polygons
    from shapely.geometry import MultiPoint
    region=polygon_box(-.52,0,.52,1)
    seeds=[(-.40,.12),(-.15,.17),(.20,.12),(.43,.30),(-.37,.47),(-.05,.38),(.17,.62),(-.42,.77),(-.14,.86),(.39,.87)]
    cells=voronoi_polygons(MultiPoint(seeds),extend_to=region).geoms
    lines=[]
    for cell in cells:
        p=cell.intersection(region)
        if not p.is_empty:lines.append(p.boundary)
    network=unary_union(lines).buffer(.017,join_style=2).intersection(region)
    # More than eight holes: split non-overlapping regions at x=0, still one continuous lattice.
    fs=[]
    for clip in (polygon_box(-.55,-.03,0,1.03),polygon_box(0,-.03,.55,1.03)):
        q=network.intersection(clip)
        for shape in getattr(q,'geoms',[q]):
            if shape.geom_type=='Polygon':fs.append(plate(list(shape.exterior.coords)[:-1],.045,'wood',holes=[list(h.coords)[:-1] for h in shape.interiors]))
    fs += [block([.075,1.05,.08],[s*.545,.5,0],'woodDark',.006) for s in (-1,1)]
    fs += [block([1.16,.075,.08],[0,y,0],'woodDark',.006) for y in (-.015,1.015)]
    apply('l1.architecture.traditional.lattice',fs,'以封闭不规则多边形格构造冰裂纹，交点合并为同一平面网络并与外框连接。')

    # Connected square-return fret. Buffered centreline avoids bulky crossing boxes.
    paths=[]
    for row in range(3):
        y=.07+row*.30
        pts=[(-.52,y),(-.45,y),(-.45,y+.22),(-.19,y+.22),(-.19,y+.075),(-.35,y+.075),(-.35,y+.145),(-.27,y+.145)]
        paths.append(LineString(pts))
        pts2=[(-x,y0) for x,y0 in pts];paths.append(LineString(pts2))
        paths.append(LineString([(-.52,y),( .52,y)]))
    fs=[]
    for start in range(0,len(paths),3):
        network=unary_union(paths[start:start+3]).buffer(.018,join_style=2,cap_style=2)
        for shape in getattr(network,'geoms',[network]):
            fs.append(plate(list(shape.exterior.coords)[:-1],.045,'wood',holes=[list(h.coords)[:-1] for h in shape.interiors]))
    fs += [block([.07,1.02,.08],[s*.55,.50,0],'woodDark',.006) for s in (-1,1)]
    fs += [block([1.16,.07,.08],[0,y,0],'woodDark',.006) for y in (.01,.99)]
    apply('l1.architecture.traditional.screen',fs,'重建左右对称连续回转纹和横向连接线，统一线宽，消除独立梳齿式残片。')

    outline=[[-.20,0],[.19,0],[.19,.06],[.155,.073],[.12,.10],[.10,.145],[.095,.20],[.065,.255],[.012,.289],[-.07,.31],[-.13,.33],[-.16,.37],[-.20,.38]]
    apply('l1.architecture.trim.cyma',[plate(outline,1.5,'l1Ivory')],'重做凹凸交替的S形檐口截面，大平面与折线采样清晰分工。')
    fs=[block([1.5,.09,.23],[0,.29,-.018],'l1Ivory',.008),block([1.5,.045,.22],[0,.055,-.016],'l1Ivory',.006)]
    for i in range(5):
        x=-.6+i*.30
        fs.append(organic_profile([(.07,.025,.036,.038,.035),(.11,.060,.081,.05,.035),(.18,.082,.085,.05,.035),(.235,.07,.063,.05,.035),(.26,.035,.026,.035,.035)],'l1Ivory',16,position=[x,0,0]))
        if i<4:fs.append(plate([[-.018,.08],[0,.055],[.018,.08],[.008,.24],[0,.265],[-.008,.24]],.042,'#D6CAB4',at=(x+.15,0,.04)))
    apply('l1.architecture.trim.egg',fs,'建立下收上圆的卵形单元和细长箭镖间隔，上下线脚形成连续饰带。')
