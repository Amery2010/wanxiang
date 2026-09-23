"""Buildable-looking stylised architecture with apertures and actual load paths."""
from .common import *
from l1_expansion.common import placed
from l34_expansion.architecture import BUILDINGS
STONE='#B4AA91'; WALL='#D7CDB7'; WOOD='#7D6247'; FRAME='#7C8077'; GLASS='#7DADBA'; ROOF='#647A78'

def hip(w,d,y,h,c=ROOF):
    p=[[-w/2,y,-d/2],[w/2,y,-d/2],[w/2,y,d/2],[-w/2,y,d/2],[0,y+h,-max(0,d-w)*.5],[0,y+h,max(0,d-w)*.5]]
    return [mesh(p,[[0,1,4],[1,2,5,4],[2,3,5],[3,0,4,5],[3,2,1,0]],c)]

def roundroof(r,y,h,n=12,c=ROOF):return [revolve([(.001,y),(r,y),(r*.82,y+h*.20),(r*.44,y+h*.69),(.005,y+h)],c,n)]

def dome(r,y,slot=.20):
    ps=[];na=28;nb=12;start=slot;end=math.tau-slot
    for inner in (False,True):
        rr=r-(.095 if inner else 0)
        for j in range(nb+1):
            b=.018+(math.pi/2-.018)*j/nb
            for i in range(na+1):a=start+(end-start)*i/na;ps.append([rr*math.sin(b)*math.sin(a),y+rr*math.cos(b),rr*math.sin(b)*math.cos(a)])
    N=(na+1)*(nb+1);fs=[]
    for j in range(nb):
        for i in range(na):
            k=j*(na+1)+i;fs += [[k,k+1,k+na+2,k+na+1],[N+k+na+1,N+k+na+2,N+k+1,N+k]]
    for i in range(na):fs.extend([[i,N+i,N+i+1,i+1],[nb*(na+1)+i,nb*(na+1)+i+1,N+nb*(na+1)+i+1,N+nb*(na+1)+i]])
    for j in range(nb):
        for i in (0,na):k=j*(na+1)+i;fs.append([k,k+na+1,N+k+na+1,N+k])
    return mesh(ps,fs,'#B8C8C5')

def railing(a,b,y,h=.82,c=FRAME):
    dx=b[0]-a[0];dz=b[1]-a[1];dist=math.hypot(dx,dz);n=max(1,round(dist/.45));out=[]
    for i in range(n+1):x=a[0]+dx*i/n;z=a[1]+dz*i/n;out.append(basebox([.055,h,.055],[x,y,z],c))
    for yy in (y+.14,y+h):out.append(beam([a[0],yy,a[1]],[b[0],yy,b[1]],.07,c))
    return out

def window_bay(width,h,color=WALL,window=True):
    """Local XY facade at Z=0. Wall pieces never cover the window aperture."""
    if not window:return [basebox([width,h,.18],[0,0,0],color)],[],[]
    aperture=width*.58;bottom=.72;wh=min(1.35,h-1.02);s=(width-aperture)/2
    walls=[basebox([s,h,.18],[-width/2+s/2,0,0],color),basebox([s,h,.18],[width/2-s/2,0,0],color),basebox([aperture,bottom,.18],[0,0,0],color),basebox([aperture,h-bottom-wh,.18],[0,bottom+wh,0],color)]
    frames=[basebox([.055,wh,.23],[x,bottom,0],FRAME) for x in (-aperture/2,0,aperture/2)]
    frames += [block([aperture+.12,.055,.23],[0,yy,0],FRAME) for yy in (bottom,bottom+wh)]
    frames.append(basebox([aperture+.18,.075,.31],[0,bottom-.07,.055],STONE))
    glass=[basebox([aperture-.06,wh-.07,.024],[0,bottom+.035,0],GLASS)]
    return walls,frames,glass

def facade(width,h,bays,at,rot,color,entrance=False,wide=False,all_glass=False):
    walls=[];frames=[];glass=[];door=None;bw=width/bays
    for j in range(bays):
        x=(j-(bays-1)/2)*bw
        if entrance and j==bays//2:
            dw=bw-.18 if wide else min(1.05,bw-.25);dh=h-.3 if wide else 2.12;s=(bw-dw)/2
            a=[basebox([s,h,.2],[x-bw/2+s/2,0,0],color),basebox([s,h,.2],[x+bw/2-s/2,0,0],color),basebox([dw,h-dh,.2],[x,dh,0],color)]
            walls+=a;door=[x-dw/2,dh,dw]
            frames += [basebox([.055,dh,.24],[x-dw/2,0,0],FRAME),basebox([.055,dh,.24],[x+dw/2,0,0],FRAME),basebox([dw+.06,.055,.24],[x,dh-.025,0],FRAME)]
        elif all_glass:
            frames += [basebox([.07,h,.11],[x-bw/2,0,0],FRAME),basebox([.07,h,.11],[x+bw/2,0,0],FRAME),basebox([bw,.08,.11],[x,0,0],FRAME),basebox([bw,.08,.11],[x,h-.08,0],FRAME),basebox([bw,.06,.10],[x,h*.48,0],FRAME)]
            glass += [basebox([bw-.10,h-.16,.025],[x,.08,0],GLASS)]
        else:
            a,b,c=window_bay(bw,h,color);walls+=placed(a,[x,0,0]);frames+=placed(b,[x,0,0]);glass+=placed(c,[x,0,0])
    return placed(walls,at,rot),placed(frames,at,rot),placed(glass,at,rot),door

def build_house(row):
    key,name,bx,bz,floors,rkind,programme=row;ident='l3-architecture-building-'+key
    w=bx*1.7;d=bz*1.7;fh=2.65;lift=.9 if programme=='stilt' else .12;ybase=lift+.15;top=ybase+floors*fh
    walls=[];frames=[];glass=[];rs=[];extra=[];base=[basebox([w+.22,.15,d+.22],[0,lift,0],STONE)];door_nodes=[];controls=[]
    timber=key in ('barn','stable','mountain_hut','lodge','farmhouse','boathouse','a_frame');col='#B49A77' if timber else WALL
    if lift>.2:
        for x in (-w/2+.2,w/2-.2):
            for z in (-d/2+.2,d/2-.2):base.append(basebox([.24,lift,.24],[x,0,z],WOOD))
        for i in range(5):base.append(basebox([1.15,.18*(i+1),.30],[0,0,d/2+1.36-i*.27],WOOD))
    else:base+=[basebox([1.35,.07, .50],[0,0,d/2+.34],STONE),basebox([1.28,.13,.28],[0,0,d/2+.10],STONE)]
    if key=='a_frame':
        eave=ybase+.35;ridge=ybase+3.6;rs=roof(w+.35,d+.4,eave,3.6,ROOF)
        dw=.86;dh=2.05
        for z in (-d/2,d/2):
            outer_y=eave+(ridge-eave)*(1-dw/w)
            if z>0:
                walls.extend([extrude_xy([[-w/2,eave],[-dw/2,eave],[-dw/2,outer_y]],.18,col,z),extrude_xy([[dw/2,eave],[w/2,eave],[dw/2,outer_y]],.18,col,z),extrude_xy([[-dw/2,ybase+dh],[dw/2,ybase+dh],[dw/2,outer_y],[0,ridge],[-dw/2,outer_y]],.18,col,z)])
            else:walls.append(extrude_xy([[-w/2,eave],[w/2,eave],[0,ridge]],.18,col,z))
        door_nodes=[node(ident,'entrance',[basebox([dw,dh,.08],[dw/2,0,0],WOOD),block([.03,.14,.07],[dw-.09,dh*.48,.07],'#B6AA75')],at=[-dw/2,ybase,d/2+.01])];controls=[rotation_control('open','entrance','开门',[0,1,0],100)];top=ridge
    else:
        for level in range(floors):
            yy=ybase+fh*level
            if level:base.append(basebox([w,.13,d],[0,yy-.13,0],STONE))
            for side,run,at,rot in [('front',bx,[0,yy,d/2],[0,0,0]),('back',bx,[0,yy,-d/2],[0,180,0]),('left',bz,[-w/2,yy,0],[0,90,0]),('right',bz,[w/2,yy,0],[0,90,0])]:
                ww=w if side in ('front','back') else d
                a,b,c,door=facade(ww,fh,run,at,rot,col,entrance=side=='front' and level==0,wide=programme in ('garage','loading','stable'),all_glass=rkind=='glass' or key=='cafe')
                walls+=a;frames+=b;glass+=c
                if door:
                    xx,hh,dw=door;fs=[basebox([dw,hh,.075],[dw/2,0,0],WOOD if timber else '#788783')]
                    if programme not in ('garage','loading'):
                        fs+=[block([.025,.17,.07],[dw-.09,hh*.45,.055],'#C9B882')]
                        if not timber:fs.append(basebox([dw*.60,.58,.025],[dw/2,hh*.53,.043],GLASS))
                    else:
                        for q in range(7):fs.append(block([dw-.05,.018,.022],[dw/2,hh*(q+1)/8,.045],'#68746A'))
                    door_nodes.append(node(ident,'entrance',fs,at=[xx,yy,d/2]));controls.append(rotation_control('open','entrance','开门',[0,1,0],100))
            if programme in ('balcony','terrace') and level>0:
                base.append(basebox([w+.18,.13,1.0],[0,yy-.13,d/2+.48],STONE));frames+=railing([-w/2,d/2+.95],[w/2,d/2+.95],yy)
                for x in (-w/2,w/2):frames+=railing([x,d/2],[x,d/2+.95],yy)
        rh=1.4 if rkind not in ('steep','gambrel') else 2.0
        if rkind=='dome':
            rs=[dome(w*.52,top)];extra+=[tube([[0,top-.1,0],[0,top+.8,0]],.12,FRAME,10),tube([[0,top+.68,-.3],[0,top+1.1,1.0]],[.22,.26],'#D0CFC0',14)]
        elif rkind=='hip':rs=hip(w+.5,d+.5,top,rh,'#5E7F77' if programme=='traditional' else ROOF)
        elif rkind=='glass':
            # Framed pitched glazing, not an opaque flat slab labelled greenhouse.
            rs=roof(w+.18,d+.18,top,rh,GLASS,thick=.025)
            for j in range(bz+1):zz=-d/2+d*j/bz;frames += [beam([-w/2,top,zz],[0,top+rh,zz],.085,FRAME),beam([0,top+rh,zz],[w/2,top,zz],.085,FRAME)]
            frames.append(beam([0,top+rh,-d/2],[0,top+rh,d/2],.095,FRAME))
            for x in (-w*.30,w*.30):extra.append(basebox([.7,.62,d*.70],[x,ybase,0],WOOD));extra.append(basebox([.62,.18,d*.69],[x,ybase+.62,0],'#668B53'))
        elif rkind=='sawtooth':
            for j in range(bx):
                seg=w/bx;x=-w/2+seg*j;outline=[[x,top],[x+seg*.75,top+.85],[x+seg,top+.85],[x+seg,top-.1],[x,top-.1]]
                rs.append(extrude_xy(outline,d+.25,ROOF));glass.append(extrude_xy([[x+seg,top+.01],[x+seg,top+.78],[x+seg+.025,top+.78],[x+seg+.025,top+.01]],d*.96,GLASS))
        elif rkind=='flat':
            rs=[basebox([w+.3,.18,d+.3],[0,top,0],ROOF)]
            if programme in ('parapet','terrace'):
                for x in (-w/2,w/2):rs.append(basebox([.13,.40,d],[x,top+.16,0],col))
                for z in (-d/2,d/2):rs.append(basebox([w,.4,.13],[0,top+.16,z],col))
        else:
            rs=roof(w+.4,d+.45,top,rh,ROOF,kind='gambrel' if rkind=='gambrel' else 'barrel' if rkind=='barrel' else 'gable')
            for z in (-d/2,d/2):
                outline=[[-w/2,top],[w/2,top],[0,top+rh-.07]]
                if rkind=='gambrel':outline=[[-w/2,top],[w/2,top],[w*.28,top+rh*.72],[0,top+rh],[-w*.28,top+rh*.72]]
                if rkind!='barrel':walls.append(extrude_xy(outline,.14,col,z))
    if programme=='chimney':
        cy=top+.9;extra+=[basebox([.45,1.3,.45],[w*.23,top-.18,-d*.18],'#9A7662'),basebox([.60,.10,.60],[w*.23,cy+.2,-d*.18],STONE),basebox([.31,.018,.31],[w*.23,cy+.31,-d*.18],'#485353')]
    if programme in ('porch','awning','traditional','stable','loading','garage') or key=='a_frame':
        py=ybase+2.4;pw=min(w+.2,5.5);rs.append(basebox([pw,.12,1.26],[0,py,d/2+.54],ROOF))
        for x in (-pw/2+.1,pw/2-.1):frames.append(basebox([.14,py-ybase,.14],[x,ybase,d/2+1.05],WOOD))
        if programme=='traditional':
            for x in (-w*.36,0,w*.36):frames.append(beam([x,py-.18,d/2+.8],[x,py+.1,d/2+.32],.15,'#A77754'))
    if programme=='mill':
        # Side-mounted wheel: axis X, water paddles sit radially on the rim.
        wf=[];r=1.30;cy=1.5
        for xx in (-.23,.23):
            rings=revolve([(r-.12,xx),(r,xx),(r,xx+.07),(r-.12,xx+.07)],WOOD,24)
            wf+=placed(rings if isinstance(rings,list) else [rings],[0,cy,0],[0,0,90])
        for j in range(16):
            a=j*math.tau/16;y=cy+r*math.sin(a);z=r*math.cos(a)
            wf+=placed([block([.6,.09,.34],[0,0,0],WOOD)],[-w/2-.36,y,z],[math.degrees(a),0,0])
            if j%2==0:wf.append(beam([-w/2-.36,cy,0],[-w/2-.36,y,z],.075,WOOD))
        # Move wheel rings outboard, not onto roof; axle penetrates sidewall.
        wf=placed(wf[:2],[-w/2-.36,0,0])+wf[2:]
        wf.append(beam([-w/2+.1,cy,0],[-w/2-.7,cy,0],.18,FRAME));extra+=wf
    if key=='clinic':
        extra += [block([.75,.17,.08],[w*.32,ybase+1.95,d/2+.13],'#658A87'),block([.17,.75,.08],[w*.32,ybase+1.95,d/2+.13],'#658A87')]
    if programme=='solar':
        for i in range(3):extra+=placed([basebox([1.28,.06,1.1],[0,0,0],'#526D88')],[(i-1)*1.45,top+.24,0],[15,0,0])
    if programme in ('vents','antenna'):
        for x in (-.55,.55):extra.append(basebox([.5,.35,.7],[x,top+.18,0],FRAME))
        if programme=='antenna':extra += [tube([[0,top,0],[0,top+1.7,0]],.04,FRAME,8),beam([-.7,top+1.25,0],[.7,top+1.25,0],.035,FRAME)]
    items=[node(ident,'foundation',base,material='mat.stone')]
    for nm,fs,mat in [('walls',walls,'mat.plaster'),('frames',frames,'mat.wood'),('glazing',glass,'mat.glass'),('roof',rs,'mat.glass' if rkind=='glass' else 'mat.paint'),('programme',extra,'mat.matte')]:
        if fs:items.append(node(ident,nm,fs,material=mat))
    items+=door_nodes
    replace(ident,items,'建筑外壳缺少真实窗洞，多种屋顶和用途结构被不相符部件替代。','重建墙体洞口与窗框、独立门扇和按类型生成的完整屋顶；特殊建筑配置对应结构。',controls=controls);add_motion(ident,controls)

def shelter(key):
    ident='l3-architecture-shelter-'+key;fs=[];rfs=[];items=[]
    if key in ('gazebo','bandstand'):
        n=6 if key=='gazebo' else 8;r=2.0;outline=[[r*math.sin(i*math.tau/n),r*math.cos(i*math.tau/n)] for i in range(n)];fs=[slab_polygon(outline,0,.22,STONE)]
        for x,z in outline:fs.append(basebox([.16,2.65,.16],[x*.90,.22,z*.90],WOOD))
        for i in range(1,n):fs+=railing([v*.90 for v in outline[i-1]],[v*.90 for v in outline[i]],.22,.7,WOOD)
        rfs=roundroof(2.26,2.85,1.0,n)
    elif key=='torii':
        fs=[basebox([.30,3,.30],[x,0,0],'#AE6D55') for x in (-1.5,1.5)]
        fs += [beam([-2,2.95,0],[2,2.95,0],.23,WOOD),beam([-1.8,2.42,0],[1.8,2.42,0],.20,'#AE6D55'),basebox([.12,.44,.15],[0,2.42,0],'#AE6D55')]
        rfs=[extrude_xy([[-2.12,3.0],[-1.2,3.04],[0,3.0],[1.2,3.04],[2.12,3.0],[2.1,3.18],[0,3.15],[-2.1,3.18]],.36,ROOF)]
    elif key=='moongate':
        # A circular aperture, rather than a squashed arch perched on columns.
        r=1.30;t=.25;cy=1.38;pp=[];ff=[];n=32
        for z in (-.16,.16):
            for rr in (r,r-t):
                pp += [[rr*math.sin(j*math.tau/n),cy+rr*math.cos(j*math.tau/n),z] for j in range(n)]
        for j in range(n):k=(j+1)%n;ff += [[j,k,n+k,n+j],[2*n+j,3*n+j,3*n+k,2*n+k],[j,2*n+j,2*n+k,k],[n+j,n+k,3*n+k,3*n+j]]
        fs=[mesh(pp,ff,STONE),basebox([.8,1.45,.3],[-1.57,0,0],WALL),basebox([.8,1.45,.3],[1.57,0,0],WALL)]
        rfs=[basebox([.95,.09,.44],[x,1.45,0],ROOF) for x in (-1.57,1.57)]
    elif key in ('arcade','colonnade'):
        fs=[basebox([6.5,.12,2.7],[0,0,0],STONE)]
        for x in (-2,0,2):
            for z in (-1.1,1.1):
                if key=='arcade':fs.append(arch(2,2.8,.24,.18,STONE,[x,.12,z]))
                else:fs.append(basebox([.22,2.8,.22],[x,.12,z],STONE))
        rfs=[basebox([6.5,.18,2.7],[0,2.90,0],ROOF)]
    else:
        w=6.4 if key=='bus_terminal' else 4.5 if key=='solar_carport' else 3.4;d=2.5;h=2.5
        fs=[basebox([w+.25,.12,d+.25],[0,0,0],STONE)]
        zs=(-d*.42,) if key=='bus_stop' else (-d*.42,d*.42)
        for x in (-w*.43,w*.43):
            for z in zs:fs.append(basebox([.14,h,.14],[x,.12,z],FRAME))
        if key in ('pergola','garden_gate'):
            for x in (-w*.43,w*.43):rfs.append(beam([x,h,-d/2],[x,h,d/2],.15,WOOD))
            for i in range(8):rfs.append(beam([-w/2,h+.12,-d/2+i*d/7],[w/2,h+.12,-d/2+i*d/7],.12,WOOD))
        elif key in ('bus_stop','solar_carport','bus_terminal'):rfs=roof(w+.4,d+.35,h+.12,.36,'#59748A' if key=='solar_carport' else ROOF,kind='barrel' if key=='bus_stop' else 'flat')
        else:rfs=roof(w+.4,d+.35,h+.12,.72,ROOF)
        if key in ('bus_stop','bus_terminal'):
            fs.append(basebox([w*.8,1.55,.04],[0,.35,-d*.43],GLASS));fs.append(basebox([w*.62,.10,.4],[0,.52,0],WOOD))
            for x in (-w*.23,w*.23):fs.append(basebox([.10,.52,.26],[x,0,0],FRAME))
        if key=='picnic_shelter':
            fs.append(basebox([1.9,.12,.85],[0,.75,0],WOOD))
            for z in (-.70,.70):fs.append(basebox([1.9,.10,.30],[0,.45,z],WOOD))
            for x in (-.7,.7):fs.append(basebox([.12,.75,.6],[x,0,0],WOOD))
        if key=='market_stall':fs.append(basebox([2.8,.12,.72],[0,.90,.42],WOOD))
        if key=='pump_shelter':fs += [basebox([.55,.55,.75],[0,.12,0],FRAME),tube([[0,.4,0],[0,1.0,0],[.4,1.,0]],.10,'#799181',10)]
    items=[node(ident,'structure',fs,material='mat.stone')]
    if rfs:items.append(node(ident,'roof',rfs,material='mat.wood'))
    replace(ident,items,'棚亭、门与柱廊过度共用双排柱架，名称与主要轮廓不符。','按柱数与承重关系生成亭棚；月洞门为贯通圆洞，鸟居保留双柱与两层横梁。')

def tower(key):
    ident='l3-architecture-tower-'+key;fs=[];top=[];h=5.8
    if key in ('silo','water','cooling','chimney'):
        if key=='cooling':fs=[revolve([(1.8,0),(1.6,.3),(1.05,3),(1.15,4.8),(1.3,5.4),(1.12,5.4),(.91,3),(1.43,.3),(1.6,0)],'#ADB4AB',24)]
        elif key=='water':
            for x in (-.85,.85):
                for z in (-.85,.85):fs.append(beam([x,0,z],[x*.8,3.7,z*.8],.18,FRAME))
            for z in (-.85,.85):fs+= [beam([-.85,.7,z],[.8,3.4,z*.8],.10,FRAME),beam([.85,.7,z],[-.8,3.4,z*.8],.10,FRAME)]
            top=[revolve([(0,3.5),(1.3,3.5),(1.3,5.1),(.95,5.5),(0,5.5)],'#9AA6A2',20)];fs.append(tube([[1.12,.1,0],[1.12,3.8,0]],.08,FRAME,10))
        elif key=='silo':fs=[revolve([(.01,0),(1.20,0),(1.20,4.5),(.95,4.85),(.01,5.2)],'#BDC1B5',20)];top=[]
        else:fs=[revolve([(.7,0),(.72,.3),(.43,5.7),(.50,5.7),(.50,5.9),(.32,5.9),(.32,5.4),(.46,.4)],'#A07C66',16)]
    elif key in ('radio','crane'):
        for s in (-1,1):fs.append(beam([s*.75,0,0],[s*.24,h,0],.12,FRAME))
        for j in range(8):
            y=j*.7;w=.75-.51*y/h;wn=.75-.51*(y+.7)/h;fs += [beam([-w,y,0],[wn,y+.7,0],.06,FRAME),beam([w,y,0],[-wn,y+.7,0],.06,FRAME)]
        if key=='crane':
            fs += [beam([-1.3,h,0],[4,h,0],.18,FRAME),beam([0,h+.9,0],[4,h,0],.09,FRAME),beam([0,h+.9,0],[-1.3,h,0],.09,FRAME),tube([[3.2,h,0],[3.2,2.,0]],.019,FRAME,6)]
            top.append(basebox([.8,.6,.8],[-1,h-.15,0],STONE));top.append(tube([[3.2,2.0,0],[3.2,1.8,0],[3.38,1.7,0],[3.46,1.9,0]],.05,FRAME,8))
        else:
            for yy in (3.8,4.6,5.4):fs.append(beam([-.8,yy,0],[.8,yy,0],.07,FRAME))
    else:
        width=2.2;fs=[basebox([width+.3,.18,width+.3],[0,0,0],STONE)]
        fs += [revolve([(.001,.18),(1.1,.18),(.90,4.55),(.001,4.55)],WALL,12)] if key in ('lighthouse','windmill','beacon') else [basebox([width,4.4,width],[0,.18,0],WALL)]
        # Visible entry, bands and a supported upper gallery, rather than a tiny object on a plinth.
        fs.append(basebox([.64,1.35,.08],[0,.18,1.105],WOOD))
        for yy in (1.7,3.0):fs.append(basebox([.40,.55,.09],[0,yy,1.108],GLASS))
        if key=='lighthouse':
            for yy in (1.2,2.8):fs.append(revolve([(.99,yy),(.98,yy+.45),(.92,yy+.45),(.93,yy)],'#9C6156',16))
            top=[revolve([(.01,4.4),(1.23,4.4),(1.23,4.56),(.01,4.56)],FRAME,16),revolve([(.01,4.56),(.70,4.56),(.70,5.48),(.01,5.48)],GLASS,16)]
            for j in range(8):a=j*math.tau/8;top.append(beam([.72*math.sin(a),4.56,.72*math.cos(a)],[.72*math.sin(a),5.48,.72*math.cos(a)],.06,FRAME))
            top+=roundroof(.98,5.48,.58,12)
        elif key=='windmill':
            top=roundroof(1.24,4.5,1.0,12);fs.append(tube([[0,3.75,.4],[0,3.75,1.4]],.13,WOOD,12))
            for j in range(4):
                a=math.pi/4+j*math.pi/2;end=[2.6*math.sin(a),3.75+2.6*math.cos(a),1.42];fs.append(beam([0,3.75,1.42],end,.10,WOOD))
                for q in range(5):t=.40+q*.12;cx=end[0]*t;cy=3.75+(end[1]-3.75)*t;fs.append(beam([cx-.3*math.cos(a),cy+.3*math.sin(a),1.43],[cx+.3*math.cos(a),cy-.3*math.sin(a),1.43],.13,WOOD))
        elif key=='pagoda':
            top=[]
            for j in range(4):yy=1.2+j*1.2;ww=3.1-j*.38;top+=hip(ww,ww,yy,.65,'#697D6B')
        elif key in ('bell','watch'):
            top=[basebox([2.8,.15,2.8],[0,4.5,0],WOOD)]
            for x in (-1.05,1.05):
                for z in (-1.05,1.05):top.append(basebox([.14,1.25,.14],[x,4.65,z],WOOD))
            top+=hip(2.9,2.9,5.9,.75)
            if key=='bell':top.append(revolve([(.04,5.68),(.28,5.55),(.32,5.1),(.52,4.9),(.45,4.83),(.28,5.08),(.21,5.5),(.03,5.58)],'#B39B62',16))
        elif key=='clock':
            top=hip(2.55,2.55,4.6,.9);fs.append(ellipsoid([0,3.52,1.16],[.98,.98,.065],'#E4DCC4',24,8));fs+=[beam([0,3.52,1.21],[0,3.9,1.21],.045,'#4D5D60'),beam([0,3.52,1.21],[.26,3.35,1.21],.04,'#4D5D60')]
        elif key=='gate':
            fs=[arch(3.1,4.3,1.8,.48,STONE),basebox([3.4,.20,2.05],[0,4.3,0],STONE)];top=hip(3.6,2.2,4.5,.75)
        else:top=roundroof(1.2,4.6,.75)
    items=[node(ident,'support',fs,material='mat.stone')]
    if top:items.append(node(ident,'superstructure',top,material='mat.matte'))
    replace(ident,items,'塔类主要识别结构缺失或安装位置错误。','重建水箱支架、冷却塔空腔、灯室、钟盘、磨坊叶片或起重臂等功能结构。')

def ruin(key):
    ident='l3-architecture-ruin-'+key;fs=[];stone='#9D9D8C'
    if key in ('gate','aqueduct','bridge'):
        n=3 if key=='aqueduct' else 2 if key=='bridge' else 1
        for i in range(n):fs.append(arch(1.8,2.8,.65,.27,stone,[(i-(n-1)/2)*1.8,0,0]))
        fs.append(basebox([n*1.8,.20,.75],[0,2.8,0],stone))
    elif key in ('colonnade','temple','shrine'):
        fs.append(basebox([4.8,.20,3.2],[0,0,0],stone))
        for i in range(6):
            x=(i%3-1)*1.6;z=(-1 if i<3 else 1)*1.05;h=2.35 if i not in (1,5) else .8+i*.15
            fs.append(revolve([(.25,.2),(.24,.38),(.15,.5),(.14,h),(.22,h+.08),(.22,h+.20)],stone,10,False,at=(x,0,z)))
        fs.append(beam([-1.6,2.65,-1.05],[1.6,2.65,-1.05],.25,stone))
    elif key=='stair':
        for i in range(8):fs.append(basebox([1.7,.20*(i+1),.35],[0,0,-1.2+i*.35],stone))
    else:
        fs.append(basebox([4.5,.16,3.2],[0,0,0],stone))
        for i in range(5):
            x=-2+i*.9;h=[2.4,1.8,.8,1.35,2.7][i];fs.append(basebox([.90,h,.30],[x,.16,-1.35],stone))
        fs.append(extrude_xy([[-2.15,.16],[-2.15,2.75],[-1.95,2.60],[-1.10,.85],[-.8,.16]],.28,stone,.05))
        if key in ('courtyard','bunker','factory','tower'):fs.append(arch(1.65,2.2,.35,.24,stone,[1.20,.16,.75]))
    for i in range(5):
        a=i*2.4;fs.append(ellipsoid([1.6*math.sin(a),.12,1.18*math.cos(a)],[.38,.24,.30],stone,6,3))
    replace(ident,[node(ident,'ruin',fs,material='mat.stone')],'废墟依靠随机碎块，缺乏原建筑的结构线索。','保留连续墙基、残柱、拱券和断面，碎石作为附属而非主体。')

def author():
    for row in BUILDINGS:build_house(row)
    for ident in list(ASSEMBLIES):
        if ident.startswith('l3-architecture-shelter-'):shelter(ident.removeprefix('l3-architecture-shelter-'))
        elif ident.startswith('l3-architecture-tower-'):tower(ident.removeprefix('l3-architecture-tower-'))
        elif ident.startswith('l3-architecture-ruin-'):ruin(ident.removeprefix('l3-architecture-ruin-'))
