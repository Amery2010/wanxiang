"""Continuous terrain profiles, unioned junctions and bridges with plausible supports."""
from .common import *
from l1_expansion.common import placed
from l34_expansion.terrain import PATHS
from shapely.geometry import Polygon, LineString, Point, box as geom_box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
ROCK='#94968B'; GRASS='#8F9A6C'; EARTH='#AD9472'; WATER='#619BAE'; WOOD='#917A59'; METAL='#687D80'

def solid_shape(shape,bottom,top,color):
    """Constrained triangulation preserves holes; wall faces share boundary vertices."""
    out=[]
    if shape.is_empty:return out
    if shape.geom_type!='Polygon':
        for piece in getattr(shape,'geoms',[]):out+=solid_shape(piece,bottom,top,color)
        return out
    if shape.area<1e-8:return out
    tris=constrained_delaunay_triangles(shape);vertices=[];lookup={};faces=[]
    def v(x,y,z):
        key=(round(float(x),8),round(float(y),8),round(float(z),8))
        if key not in lookup:lookup[key]=len(vertices);vertices.append(list(key))
        return lookup[key]
    for tri in tris.geoms:
        coords=list(tri.exterior.coords)[:-1]
        faces.append([v(x,top,z) for x,z in coords]);faces.append([v(x,bottom,z) for x,z in reversed(coords)])
    for ring in [shape.exterior,*shape.interiors]:
        coords=list(ring.coords)
        for (x,z),(xx,zz) in zip(coords,coords[1:]):faces.append([v(x,bottom,z),v(xx,bottom,zz),v(xx,top,zz),v(x,top,z)])
    out.append(mesh(vertices,faces,color));return out

def courses(path):
    lines=[];cur=[]
    for p in [*path,None]:
        if p is None:
            if len(cur)>1:lines.append(LineString(cur))
            cur=[]
        else:cur.append(tuple(v*1.3 for v in p))
    return lines

def road_or_river(key,path,river=False):
    family='river' if river else 'road';ident=f'l3-terrain-{family}-{key}';lines=courses(path);width=.55 if river else .48
    region=unary_union([line.buffer(width,quad_segs=6,cap_style=2,join_style=1) for line in lines])
    if key=='culdesac':region=unary_union([region,Point(0,1.85).buffer(.92,quad_segs=12)])
    if key=='plaza':region=unary_union([region,Point(0,0).buffer(1.15,quad_segs=8)])
    tile=geom_box(-3,-3,3,3);region=region.intersection(tile)
    # Curbs/banks follow only the OUTSIDE union boundary, never individual segment edges.
    border=region.buffer(.20 if river else .105,quad_segs=6,join_style=1).difference(region)
    portals=[]
    for line in lines:
        if line.coords[0]!=line.coords[-1]:
            for endpoint in (line.coords[0],line.coords[-1]):portals.append(Point(endpoint).buffer(width+.28,quad_segs=6))
    if portals:border=border.difference(unary_union(portals))
    fs=solid_shape(tile,-.20,-.06,EARTH if river else GRASS)
    items=[node(ident,'substrate',fs,material='mat.stone')]
    # Actual lowered channel/cutout; neither banks nor curbs cross at junctions.
    land=tile.difference(region)
    items.append(node(ident,'land',solid_shape(land,-.06,.015,GRASS),material='mat.stone'))
    items.append(node(ident,'course',solid_shape(region,-.055,-.008 if river else .035,WATER if river else '#65717A'),material='mat.water' if river else 'mat.stone'))
    if not border.is_empty:items.append(node(ident,'bank' if river else 'curb',solid_shape(border,.015,.13 if river else .135,'#A4AA83' if river else '#C6C3B2'),material='mat.stone'))
    if not river and key not in ('plaza','culdesac'):
        # Discontinue centre markings at actual multi-course intersections.
        junctions=[]
        for i,line in enumerate(lines):
            for other in lines[i+1:]:
                inter=line.intersection(other)
                if not inter.is_empty:junctions.append(inter.buffer(.65))
        excluded=unary_union(junctions) if junctions else Polygon();marks=[]
        for line in lines:
            length=line.length
            for i in range(int(length/.52)):
                a=line.interpolate(i*.52+.07);b=line.interpolate(min(length,i*.52+.30));s=LineString([a,b]).buffer(.017,cap_style=2).intersection(region).difference(excluded);marks+=solid_shape(s,.036,.042,'#E3DDC1')
        if marks:items.append(node(ident,'markings',marks,material='mat.paint'))
    replace(ident,items,'分段路缘或河岸在分岔口横穿通道，拼接处重叠且水面悬于岸上。','先合并完整路径面，再生成外边界、洞口与中心标线；河床低于连续河岸。')
    ASSEMBLIES[ident]['metadata']['course_geometry']={'paths':[list(l.coords) for l in lines],'width_m':width*2,'junctions_unioned':True,'schema':'wx.authored-course/1.0'}

def heightfield(w,d,fn,c=ROCK,n=20,bottom=-.16):
    p=[]
    for j in range(n+1):
        z=(j/n-.5)*d
        for i in range(n+1):x=(i/n-.5)*w;p.append([x,max(bottom+.03,fn(x,z)),z])
    f=[]
    for j in range(n):
        for i in range(n):a=j*(n+1)+i;f.extend([[a,a+1,a+n+2],[a,a+n+2,a+n+1]])
    edge=list(range(n+1))+[j*(n+1)+n for j in range(1,n+1)]+[n*(n+1)+i for i in range(n-1,-1,-1)]+[j*(n+1) for j in range(n-1,0,-1)]
    base=[]
    for k in edge:base.append(len(p));p.append([p[k][0],bottom,p[k][2]])
    for j,k in enumerate(edge):jj=(j+1)%len(edge);f.append([k,edge[jj],base[jj],base[j]])
    f.append(list(reversed(base)));return mesh(p,f,c)

def landform(key):
    ident='l3-terrain-landform-'+key;forms=[];extra=[]
    def rnd(x,z):return .04*math.sin(x*3.7+z*.8)*math.cos(z*2.6)
    funcs={
        'mesa':lambda x,z:.10+2.05*min(1,max(0,(1.9-max(abs(x),abs(z)))*2.3)),
        'butte':lambda x,z:.08+2.8*min(1,max(0,(1.1-math.hypot(x,z))*4)),
        'escarpment':lambda x,z:.12+2.2*min(1,max(0,(x+.35)*2.5)),
        'inner_cliff':lambda x,z:.10+2.15*min(1,max(0,(math.hypot(x+1.6,z+1.6)-2.1)*3)),
        'outer_cliff':lambda x,z:.10+2.15*min(1,max(0,(2.3-math.hypot(x+1.6,z+1.6))*3)),
        'gorge':lambda x,z:.05+2.2*min(1,max(0,(abs(x+.25*math.sin(z))- .55)*2.5)),
        'canyon':lambda x,z:.06+2.5*min(1,max(0,(abs(x)-.68)*3.2)),
        'terraces':lambda x,z:.15+math.floor((x+2.5)*1.05)*.37,
        'ramp':lambda x,z:.15+(x+2.5)*.40,
        'saddle':lambda x,z:.3+1.4*(x/2.5)**2+.7*(1-(z/2.5)**2),
        'ridge':lambda x,z:.15+2.1*max(0,1-abs(x)/2.4),
        'bowl':lambda x,z:.15+1.8*min(1,(math.hypot(x,z)/2.3)**2),
        'notch':lambda x,z:.15+2.1*min(1,max(0,(x+.2)*3))*min(1,abs(z)*1.8),
        'talus':lambda x,z:.15+(x+2.5)*.42,
        'volcanic':lambda x,z:.15+2.6*max(0,1-abs(math.hypot(x,z)-1.0)/1.5),
        'icefall':lambda x,z:.10+2.5*min(1,max(0,(x+.1)*3))+.16*math.sin(z*5),
        'sinkhole':lambda x,z:.15+1.8*min(1,max(0,(math.hypot(x,z)-.6)*1.8)),
    }
    if key in funcs:
        fn=funcs[key];forms=[heightfield(5,5,lambda x,z:fn(x,z)+rnd(x,z),'#A9C6C9' if key=='icefall' else ROCK)]
        if key in ('gorge','canyon'):extra=solid_shape(LineString([(0,-2.5),(0,2.5)]).buffer(.23,cap_style=2),.065,.082,WATER)
        if key=='talus':
            for i in range(18):x=-1.9+(i%6)*.47;z=-1.9+(i//6)*1.3;extra.append(ellipsoid([x,fn(x,z)+.09,z],[.4,.24,.31],'#A7A695',6,3))
        if key=='volcanic':extra=solid_shape(Point(0,0).buffer(.24,quad_segs=10),1.02,1.08,'#B86C4E')
    elif key=='arch':
        forms=[basebox([5,.2,3],[0,-.2,0],ROCK),arch(4.2,2.75,1.15,.48,ROCK),ellipsoid([-2.0,.75,0],[1.1,1.5,1.5],ROCK,8,5),ellipsoid([2.0,.75,0],[1.1,1.5,1.5],ROCK,8,5)]
    elif key=='overhang':
        forms=[extrude_xy([[-2.5,0],[2.5,0],[2.5,2.8],[-1.3,2.8],[-1.8,2.5],[1.0,1.8],[1.2,0]],3.7,ROCK)]
    else:
        forms=[basebox([5,.16,4.5],[0,-.16,0],ROCK)]
        for j in range(5):
            for i in range(6):
                x=-2+i*.72+(j%2)*.36;z=-1.7+j*.7;h=.65+1.65*(i/5)+.22*math.sin(i+j)
                forms.append(revolve([(.001,0),(.39,0),(.38,h),(.001,h)],'#92988D' if (i+j)%2 else '#A6A899',6,at=[x,0,z]))
    items=[node(ident,'terrain',forms,material='mat.stone')]
    if extra:items.append(node(ident,'detail',extra,material='mat.water' if key in ('gorge','canyon') else 'mat.stone'))
    replace(ident,items,'地貌名称与主网格不符；峡谷、凹坑、天然石拱使用实心通用台地。','按横断面生成双壁、盆地、台阶与火山口；拱与岩檐保留真实贯通空隙。')

def polar_land(key,cx=0,cz=0,s=1):
    n=64;loops=[]
    if key in ('atoll','lagoon'):
        radii=[(.85,.0),(1.05,.10),(1.35,.22),(1.65,.14),(1.9,-.035)]
        for r,y in radii:loops.append([[cx+s*r*math.sin(i*math.tau/n),y,cz+s*r*math.cos(i*math.tau/n)] for i in range(n)])
    else:
        profile=[(.01,1.05),(.30,1.05),(.65,.6),(.88,.24),(1.0,.06),(1.13,-.05)]
        if key in ('sandbar','spit','tidal','mangrove'):profile=[(.01,.12),(.45,.18),(.83,.09),(1,-.04)]
        if key=='volcano':profile=[(.01,.50),(.17,.60),(.38,2.0),(.52,1.78),(.80,.50),(1.,.10),(1.12,-.05)]
        if key=='iceberg':profile=[(.01,1.6),(.45,1.45),(.70,1.1),(.88,.7),(1.,-.05)]
        if key=='terraced':profile=[(.01,1.3),(.30,1.3),(.38,.97),(.56,.97),(.63,.64),(.82,.64),(.89,.28),(1,.20),(1.12,-.03)]
        for rr,yy in profile:
            ring=[]
            for i in range(n):
                a=i*math.tau/n;rad=2.0*rr*(1+.06*math.sin(a*3)+.025*math.cos(a*5));x=rad*math.sin(a);z=rad*math.cos(a)
                if key in ('sandbar','spit'):x*=1.4;z*=.28;z+=.36*math.sin(x*.9)
                elif key=='headland':x*=.6;z*=1.25
                elif key=='delta':x*=1.15*(.85+.25*math.cos(a));z*=.78
                elif key=='fjord' and math.cos(a)>.5:rad*=.42;x=rad*math.sin(a);z=rad*math.cos(a)
                elif key=='crescent':x-=.95*rr*math.cos(a)**2
                ring.append([cx+x*s,yy*s,cz+z*s])
            loops.append(ring)
    return loops

def sculpted_island(shape,height=.85):
    """Constrained coastal mesh with actual bays, height falloff and sand faces."""
    points=[];faces=[];colors=[];seen={};step=.22
    def elevation(x,z):
        inland=shape.boundary.distance(Point(x,z))
        return -.035+height*min(1.,inland/.86)**.72*(.88+.08*math.sin(x*1.8)+.035*math.cos(z*3.2))
    def vertex(x,z,y=None):
        x,z=round(float(x),7),round(float(z),7);y=elevation(x,z) if y is None else y
        key=(x,round(y,7),z)
        if key not in seen:seen[key]=len(points);points.append(list(key))
        return seen[key]
    minx,minz,maxx,maxz=shape.bounds
    nx=math.ceil((maxx-minx)/step);nz=math.ceil((maxz-minz)/step)
    for ix in range(nx):
        for iz in range(nz):
            x=minx+ix*step;z=minz+iz*step;patch=shape.intersection(geom_box(x,z,x+step,z+step))
            if patch.is_empty:continue
            pieces=[patch] if patch.geom_type=='Polygon' else list(getattr(patch,'geoms',[]))
            for piece in pieces:
                if piece.geom_type!='Polygon' or piece.area<1e-8:continue
                for tri in constrained_delaunay_triangles(piece).geoms:
                    coords=list(tri.exterior.coords)[:-1];indices=[vertex(xx,zz) for xx,zz in coords]
                    faces.append(indices);level=sum(points[k][1] for k in indices)/3
                    colors.append('#C7BB91' if level<.12 else '#9AAB74' if level<.28 else '#748C66')
    pieces=[shape] if shape.geom_type=='Polygon' else list(shape.geoms)
    for piece in pieces:
        for ring in [piece.exterior,*piece.interiors]:
            coords=list(ring.coords)
            for (x,z),(xx,zz) in zip(coords,coords[1:]):
                faces.append([vertex(x,z),vertex(xx,zz),vertex(xx,zz,-.13),vertex(x,z,-.13)]);colors.append('#AD9978')
        for tri in constrained_delaunay_triangles(piece).geoms:
            faces.append([vertex(x,z,-.13) for x,z in list(tri.exterior.coords)[:-1]]);colors.append('#AD9978')
    form=mesh(points,faces,GRASS);form['colors']=colors
    return [form]

def island(key):
    ident='l3-terrain-island-'+key;items=[node(ident,'water',[basebox([7,.045,7],[0,-.095,0],WATER)],material='mat.water')];masses=[];sand=[]
    centres=[(-1.4,-.8,.55),(1.3,-.9,.54),(.2,1.4,.56)] if key=='archipelago' else [(0,0,1)]
    for cx,cz,s in centres:
        if key in ('crescent','delta','fjord'):
            shape=Point(0,0).buffer(2.1,quad_segs=20)
            if key=='crescent':shape=shape.difference(Point(.86,0).buffer(1.85,quad_segs=20))
            elif key=='fjord':shape=shape.difference(LineString([(0,2.4),(-.10,1.25),(.20,.30),(.10,-.75)]).buffer(.36,quad_segs=8))
            else:
                branches=[LineString([(0,-.4),(sign*.55,.65),(sign*1.25,2.25)]).buffer(.15,quad_segs=6) for sign in (-1,1)]
                shape=shape.difference(unary_union(branches))
            masses+=sculpted_island(shape,.48 if key=='delta' else 1.15 if key=='fjord' else .65)
            continue
        loops=polar_land('rocky' if key=='archipelago' else key,cx,cz,s);n=len(loops[0]);points=sum(loops,[]);faces=[];shore=[]
        for j in range(len(loops)-1):
            for i in range(n):a=j*n+i;b=j*n+(i+1)%n;quad=[a,b,b+n,a+n];(shore if j==len(loops)-2 else faces).append(quad)
        # Share top mesh vertices; close the base beneath water. A lagoon stays open.
        if key not in ('atoll','lagoon'):faces.append(list(range(n-1,-1,-1)))
        else:
            # Inner shore side wall reaches below waterline.
            for i in range(n):p=points[i];points.append([p[0],-.085,p[2]])
            inn=len(points)-n
            for i in range(n):faces.append([i,(i+1)%n,inn+(i+1)%n,inn+i])
        base=len(points)
        for p in loops[-1]:points.append([p[0],-.12,p[2]])
        last=(len(loops)-1)*n
        for i in range(n):faces.append([last+i,last+(i+1)%n,base+(i+1)%n,base+i])
        if key in ('atoll','lagoon'):
            for i in range(n):faces.append([base+i,base+(i+1)%n,inn+(i+1)%n,inn+i])
        else:faces.append(list(range(base+n-1,base-1,-1)))
        # Single watertight surface with per-face colours, avoiding overlapping tiles.
        allfaces=faces+shore;f=mesh(points,allfaces,'#B7CAC7' if key=='iceberg' else '#8C9970' if key not in ('rocky','volcano') else ROCK)
        # Facet colour supported as a palette-free base per surface; shoreline uses a separated face group.
        f['colors']=[f['color']]*len(faces)+['#C7BB91' if key!='iceberg' else '#CDDDDA']*len(shore)
        masses.append(f)
    items.append(node(ident,'island',masses,material='mat.stone'))
    if key=='mangrove':
        fs=[]
        for j in range(9):
            a=j*2.4;x=1.1*math.sin(a);z=1.1*math.cos(a)
            fs.append(tube([[x,.13,z],[x,.75,z]],.045,WOOD,7))
            for q in range(3):b=a+q*2.1;fs.append(tube([[x,.55,z],[x+.3*math.sin(b),.02,z+.3*math.cos(b)]],[.035,.015],WOOD,6))
            fs.append(ellipsoid([x,.77,z],[.60,.36,.58],'#638761',8,4))
        items.append(node(ident,'mangroves',fs,material='mat.leaf'))
    replace(ident,items,'岛屿由矩形岸边素材拼盘构成，环礁、火山与峡湾缺少相应主地形。','用连续环状/径向岸线构建水陆高差，环礁保留潟湖，火山有凹口，群岛保持独立。')

def bridge(key):
    ident='l3-terrain-bridge-'+key;fs=[];deck=[];rails=[];L=5.;h=.95;width=1.55
    if key=='stepping':
        for i in range(9):fs.append(ellipsoid([.10*math.sin(i*2.4),.15,-2.5+i*.625],[.80,.30,.58],ROCK,8,4))
    elif key in ('arch','culvert','viaduct'):
        n=3 if key=='viaduct' else 1;span=L/n;rise=.8 if key!='viaduct' else 1.55;h=rise+.35
        for i in range(n):fs+=placed([arch(span,rise,width,.24,ROCK)], [0,0,(i-(n-1)/2)*span],[0,90,0])
        deck=[basebox([width+.12,.20,L+.15],[0,h-.25,0],STONE if (STONE:='#B0AC98') else ROCK)]
    else:
        sag=.30 if key=='rope' else 0
        for i in range(20):
            z=-L/2+(i+.5)*L/20;yy=h-sag*(1-(2*z/L)**2);deck.append(basebox([width,.11,L/20-.012],[0,yy,z],WOOD))
        for side in (-1,1):
            xx=side*.62
            if key=='rope':
                points=[[xx,h+.90-.3*(1-(2*z/L)**2),z] for z in [-L/2+j*L/24 for j in range(25)]]
                rails.append(tube(points,.033,'#B2A07D',7))
                for j in range(11):z=-L/2+j*.5;yy=h-.3*(1-(2*z/L)**2);rails.append(tube([[xx,yy,z],[xx,yy+.9,z]],.017,'#B2A07D',6))
                for z in (-L/2,L/2):fs.append(basebox([.14,h+1.05,.14],[xx,0,z],WOOD))
            elif key=='suspension':
                # Only bank towers/end supports; no contradictory in-span ground piers.
                for z in (-2.15,2.15):fs.append(basebox([.15,h+1.9,.18],[xx,0,z],METAL))
                pts=[]
                for j in range(33):z=-2.55+j*5.1/32;y=h+.35+1.52*(z/2.15)**2;pts.append([xx,y,z])
                rails.append(tube(pts,.027,METAL,7))
                for j in range(15):z=-2.1+j*.3;y=h+.35+1.52*(z/2.15)**2;rails.append(beam([xx,h+.1,z],[xx,y,z],.02,METAL))
            elif key=='truss':
                fs.append(beam([xx,h,-2.5],[xx,h,2.5],.16,METAL));rails+= [beam([xx,h+1.0,-2.5],[xx,h+1.0,2.5],.13,METAL)]
                for j in range(5):z=-2.5+j;rails.append(beam([xx,h,z],[xx,h+1,z+.5],.1,METAL));rails.append(beam([xx,h+1,z+.5],[xx,h,z+1],.1,METAL))
            elif key not in ('pontoon','draw'):
                for z in (-2.3,0,2.3):fs.append(basebox([.14,h,.14],[xx,0,z],WOOD))
            if key not in ('rope','suspension','truss'):
                for j in range(6):z=-2.4+j*.96;rails.append(basebox([.06,.78,.06],[side*.72,h+.11,z],WOOD))
                rails.append(beam([side*.72,h+.88,-2.4],[side*.72,h+.88,2.4],.065,WOOD))
        if key in ('beam','truss','suspension','draw'):
            for z in (-2.4,2.4):fs.append(basebox([1.9,h,.35],[0,0,z],ROCK))
        if key=='pontoon':
            for z in (-1.9,-.64,.64,1.9):fs += [ellipsoid([0,.42,z],[2.15,.64,.62],'#758E91',12,5),basebox([2.0,.12,.20],[0,.74,z],WOOD)]
            # Float top and stringer meet deck underside, rather than standing on stilts.
            fs += [beam([x,.91,-2.4],[x,.91,2.4],.12,WOOD) for x in (-.55,.55)]
        if key=='draw':
            for s in (-1,1):
                fs.append(basebox([.18,h+1.8,.18],[s*.78,0,-2.38],WOOD));rails.append(tube([[s*.78,h+1.65,-2.38],[s*.72,h+.15,1.90]],.028,METAL,6))
        if key=='covered':
            for xx in (-.72,.72):
                for z in (-2.35,0,2.35):fs.append(basebox([.13,1.8,.13],[xx,h,z],WOOD))
            fs+=roof(2.15,5.5,h+1.8,.63,'#728573')
    items=[]
    for nm,geo,mat in [('supports',fs,'mat.stone'),('deck',deck,'mat.wood'),('rails',rails,'mat.metal')]:
        if geo:items.append(node(ident,nm,geo,material=mat))
    replace(ident,items,'桥型缺少各自支承结构，单侧短栏杆、悬空廊顶和浮桥落地柱不合理。','石拱、桁架、悬索、浮筒和吊桥分别建造；两侧护栏与端部支点正确连接。')

def cave(key):
    ident='l3-terrain-cave-'+key;fs=[basebox([5.2,.16,5.2],[0,-.16,0],'#7D837D')];detail=[]
    if key=='sink':
        # A vertical sinkhole is open above, not a stack of transverse arches.
        outer=Point(0,0).buffer(2.3,quad_segs=10);inner=Point(0,0).buffer(1.25,quad_segs=10);fs=solid_shape(outer.difference(inner),0,1.3,ROCK)
    elif key=='fork':
        fs.append(arch(2.8,2.5,1.8,.38,ROCK,[0,0,1.65]))
        for side in (-1,1):fs+=placed([arch(2.3,2.4,2.1,.34,ROCK)], [side*.85,0,-.55],[0,side*38,0])
        # The junction is left open; no end cap seals either fork branch.
    else:
        dep=4.3 if key in ('tunnel','lava','mine','ruin','ice') else 2.3;w=4.2 if key=='chamber' else 1.45 if key=='fissure' else 3.3
        fs.append(arch(w,2.65,dep,.36,'#AFCDD0' if key=='ice' else '#797C73' if key=='lava' else ROCK))
        if key in ('mine','ruin'):
            for z in (-1.7,0,1.7):
                for x in (-w*.39,w*.39):detail.append(basebox([.16,2.13,.16],[x,0,z],WOOD if key=='mine' else '#B1AA90'))
                detail.append(beam([-w*.40,2.1,z],[w*.40,2.1,z],.19,WOOD if key=='mine' else '#B1AA90'))
        elif key not in ('arch','fissure'):
            for j in range(6):
                x=(-1 if j%2 else 1)*w*.27;z=-dep*.36+(j//2)*dep*.36
                if j%2==0:detail.append(tube([[x,2.34,z],[x,1.64-.09*(j%3),z]],[.12,.006],'#A7B7AF' if key=='ice' else '#96998B',8))
                else:detail.append(tube([[x,0,z],[x,.48+.06*j,z]],[.15,.006],'#9AA092',8))
        if key=='sump':detail+=solid_shape(Point(0,0).buffer(1.1,quad_segs=12),.015,.035,WATER)
    items=[node(ident,'vault',fs,material='mat.stone')]
    if detail:items.append(node(ident,'formations',detail,material='mat.stone'))
    replace(ident,items,'洞室用彼此分离的拱片表达，钟乳石装在地面且洞口被附属块干扰。','连续拱顶和可通行洞口；钟乳石由顶面向下，石笋由地面向上，矿洞支护独立。')

def transition(key):
    ident='l3-terrain-transition-'+key;water=key.endswith('_watercourse');kind=key.rsplit('_',1)[0];leftcolor='#BEAE85' if kind in ('beach_dune','desert_oasis') else '#AAB9AE' if kind=='rock_snow' else '#777E74' if kind=='lava_rock' else '#969777';rightcolor=GRASS
    def fn(x,z):
        val=.12+.16*(1+math.tanh(x*1.1))/2
        if kind=='cliff_scree':val+=.6*max(0,math.tanh(-x*1.5))
        if abs(z)<.42:val=.06 if water else .17+.09*(x/5+.5)
        return val
    f=heightfield(5,5,fn,leftcolor,n=24,bottom=-.15);fs=[f]
    # Fill a real channel only up to bank level, rather than lay a floating bar across it.
    course=solid_shape(geom_box(-2.5,-.35,2.5,.35),.065 if water else .19,.082 if water else .21,WATER if water else '#B4A383')
    items=[node(ident,'transition',fs,material='mat.stone'),node(ident,'crossing',course,material='mat.water' if water else 'mat.stone')]
    replace(ident,items,'两侧地块与边界相互穿插，通道浮在两种地表之上。','统一连续高程，跨界水道低于岸面，步道与地表相接。')

def author():
    for key,label,path in PATHS:road_or_river(key,path);road_or_river(key,path,True)
    for ident in list(ASSEMBLIES):
        for family,func in [('landform',landform),('island',island),('bridge',bridge),('cave',cave),('transition',transition)]:
            prefix=f'l3-terrain-{family}-'
            if ident.startswith(prefix):func(ident.removeprefix(prefix));break
