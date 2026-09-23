"""Connected construction equipment and rail vehicles in metric author space."""
from .common import *
from .objects import wheel
from .industry import disk,axis_cylinder
Y='#BE9A57';D='#4B5C60';M='#98A6A5';G='#87A9B0';P='#7A9890'

def tracks(x):
    p=[];N=32;r=.32;cy=.36
    for xx in (x-.17,x+.17):
        for rr in (r,r-.062):
            for j in range(N):
                a=math.tau*j/N;p.append([xx,cy+rr*math.sin(a),(.90 if math.cos(a)>=0 else -.90)+rr*math.cos(a)])
    faces=[]
    for j in range(N):
        n=(j+1)%N;faces += [[j,n,2*N+n,2*N+j],[N+n,N+j,3*N+j,3*N+n],[j,N+j,N+n,n],[2*N+n,3*N+n,3*N+j,2*N+j]]
    fs=[mesh(p,faces,D)]
    for z in (-.9,-.45,0,.45,.9):fs += disk([x,.35,z],.265,.28,M)
    return fs

def bucket(w,depth=.66):
    # Continuous concave bucket with side cheeks, open at upper/front face.
    yz=[[-depth/2,.48],[-depth/2,.08],[depth*.32,0],[depth*.62,.025],[depth*.35,.085],[-depth*.32,.14],[-depth*.32,.43]]
    fs=placed([extrude_xy([[z,y] for z,y in yz],w,Y)],[0,0,0],[0,90,0])
    for s in (-1,1):fs += placed([extrude_xy([[-depth/2,.47],[-depth/2,.08],[depth*.48,.02],[depth*.34,.18]],.055,Y)],[s*w/2,0,0],[0,90,0])
    return fs

def utility(key):
    ident='l3-vehicle-utility-'+key;tracked=key in ('excavator','bulldozer','paver');base=[];body=[];tool=[];glass=[]
    if tracked:
        for x in (-.73,.73):base+=tracks(x)
        base += [basebox([1.42,.25,2.30],[0,.58,0],D)]
    else:
        for z in (-.90,.90):
            for x in (-.78,.78):
                r=.52 if key=='tractor' and z<0 else .38;base+=wheel([x,r,z],r,.25)
            base.append(axis_cylinder([-.80,.38,z],[.80,.38,z],.075,D))
        base += [basebox([1.45,.22,2.40],[0,.58,0],D)]
    if key=='tractor':
        body=[basebox([.92,.61,1.16],[0,.77,.56],Y),basebox([1.03,.08,.70],[0,1.98,-.5],Y)]
        for s in (-1,1):body += [basebox([.045,1.16,.045],[s*.47,.80,-.82],D),basebox([.39,.10,1.1],[s*.63,1.01,-.72],Y)]
        body += [basebox([.42,.08,.41],[0,1.00,-.52],D),basebox([.42,.32,.065],[0,1.08,-.70],D),axis_cylinder([.34,1.33,.26],[.34,2.11,.26],.035,D)]
        tool=[basebox([.65,.10,.25],[0,.57,-1.38],D)]
        for j in range(8):tool.append(block([.72,.03,.019],[0,.91+j*.057,1.15],D))
    else:
        cabx=-.34 if key=='excavator' else 0;caby=.85;cabz=-.30
        body=[basebox([1.45,.40,1.30],[0,.80,-.68],Y),basebox([.89,.23,1.10],[cabx,caby,cabz],Y),basebox([1.05,.075,1.16],[cabx,2.04,cabz],Y)]
        for sx in (-1,1):
            for sz in (-1,1):body.append(basebox([.055,.97,.055],[cabx+sx*.44,1.06,cabz+sz*.50],Y))
        glass=[basebox([.80,.84,.018],[cabx,1.12,cabz+.50],G),basebox([.018,.83,.89],[cabx-.44,1.13,cabz],G),basebox([.018,.83,.89],[cabx+.44,1.13,cabz],G)]
        if key=='excavator':
            body.append(revolve([(.001,.76),(.57,.76),(.57,.91),(.001,.91)],D,24));start=[.38,1.14,.37];elbow=[.38,2.73,1.17];end=[.38,1.10,2.15]
            tool += [beam(start,elbow,.19,Y),beam(elbow,end,.15,Y),axis_cylinder([.38,1.30,.50],[.38,2.26,1.08],.055,M),axis_cylinder([.38,2.55,1.21],[.38,1.39,1.94],.042,M)]
            tool += placed(bucket(.69,.68),[.38,.54,2.31],[25,0,0])
        elif key in ('loader','telehandler'):
            for s in (-1,1):tool += [beam([s*.56,1.04,.05],[s*.56,1.28,1.63],.135,Y),axis_cylinder([s*.55,.83,.32],[s*.55,1.23,1.33],.037,M)]
            if key=='loader':tool+=placed(bucket(1.55,.78),[0,.24,1.84])
            else:
                tool.append(beam([0,1.25,.2],[0,2.13,2.1],.20,Y))
                for x in (-.34,.34):tool += [basebox([.075,.44,.085],[x,1.62,2.15],D),basebox([.075,.06,.74],[x,1.62,2.48],D)]
        elif key=='forklift':
            for x in (-.36,.36):tool += [basebox([.08,2.25,.10],[x,.41,1.0],D),basebox([.075,.52,.09],[x,.37,1.12],M),basebox([.075,.055,1.0],[x,.37,1.59],M)]
            tool += [block([.83,.10,.13],[0,.72,1.12],D),block([.83,.10,.13],[0,2.57,1.0],D)]
        elif key in ('bulldozer','snowplow'):
            for x in (-.58,.58):tool.append(beam([x,.75,.15],[x,.50,1.53],.13,D))
            blade=profile_z([[-.10,.46,1.05,.42],[.05,.46,1.05,.42]],Y,12)
            tool.append(placed([blade],[0,0,1.67])[0]);tool.append(block([2.14,.065,.18],[0,.06,1.75],M))
        elif key=='roller':
            # Front drum replaces (rather than overlaps) the front axle tyres.
            base=[]
            for x in (-.73,.73):base+=wheel([x,.43,-.88],.43,.26)
            base+=[basebox([1.44,.20,2.2],[0,.64,0],D)];tool += disk([0,.47,1.04],.47,1.38,M)
            for x in (-.75,.75):tool += [beam([x,.77,.15],[x,.46,1.04],.10,Y)]
        elif key=='harvester':
            body += [basebox([1.65,.82,1.31],[0,1.08,-1.01],Y),tube([[.55,1.81,-.67],[1.14,1.91,-.73],[1.7,1.91,-.53]],.09,Y,12)]
            tool += [basebox([2.57,.11,.74],[0,.20,1.52],Y),axis_cylinder([-1.18,.54,1.61],[1.18,.54,1.61],.08,D)]
            for q in range(6):
                a=q*math.tau/6;yy=.54+.25*math.sin(a);zz=1.61+.25*math.cos(a);tool.append(axis_cylinder([-1.15,yy,zz],[1.15,yy,zz],.021,D))
                for x in (-1.15,1.15):tool.append(beam([x,.54,1.61],[x,yy,zz],.02,D))
            for x in (-1.22,1.22):tool.append(beam([x,.26,1.22],[x,.54,1.61],.045,Y))
        elif key=='sweeper':
            for x in (-.66,.66):tool += [revolve([(.001,.08),(.34,.08),(.29,.19),(.001,.22)],D,20,at=[x,0,1.16]),beam([x,.72,.46],[x,.21,1.16],.075,Y)]
            body.append(basebox([1.39,.54,.79],[0,1.01,-1.12],Y))
        elif key=='crane':
            a=[0,1.18,.23];b=[0,3.45,1.91];tool += [beam(a,b,.24,Y),axis_cylinder([0,1.12,.54],[0,2.76,1.50],.055,M),tube([[0,3.45,1.91],[0,1.63,1.91]],.015,D,8),tube([[0,1.65,1.91],[0,1.49,1.91],[.09,1.44,1.91],[.15,1.53,1.91]],.029,M,10)]
            for x in (-1.28,1.28):tool += [beam([0,.55,0],[x,.55,0],.11,Y),basebox([.16,.52,.16],[x,0,0],D)]
        elif key=='paver':
            tool += placed(bucket(1.84,.98),[0,.46,1.44]);tool += [basebox([2.14,.20,.65],[0,.13,-1.38],D),beam([-.52,.85,-.83],[-.78,.29,-1.31],.09,Y),beam([.52,.85,-.83],[.78,.29,-1.31],.09,Y)]
    items=[node(ident,'running_gear',base,material='mat.rubber'),node(ident,'body',body,material='mat.paint'),node(ident,'working_attachment',tool,material='mat.metal')]
    if glass:items.append(node(ident,'cab_glass',glass,material='mat.vehicleGlass'))
    replace(ident,items,'工程车辆共用小车底盘及不相关杆件，履带、铲斗、货叉、割台或压路钢轮缺失。','按作业用途配置连接的底盘、驾驶区和工具机构；履带带体闭合，机械臂连接至工具，支腿/滚筒/割台独立。')

def rail(key):
    ident='l3-vehicle-rail-'+key;base=[basebox([2.06,.22,6.1],[0,.55,0],D)];body=[];detail=[];glass=[]
    for z0 in (-2.02,2.02):
        base.append(basebox([1.59,.20,1.04],[0,.35,z0],D))
        for z in (z0-.33,z0+.33):
            for x in (-.76,.76):base+=disk([x,.285,z],.285,.14,D)+disk([x,.285,z],.11,.17,M)
            base.append(axis_cylinder([-.76,.285,z],[.76,.285,z],.055,M))
    for s in (-1,1):detail += [basebox([.21,.17,.49],[0,.52,s*3.20],D),block([.45,.17,.12],[0,.61,s*3.41],D)]
    if key=='flat':body=[basebox([2.18,.13,6.10],[0,.77,0],'#B3A381')]
    elif key=='tank':
        body=[profile_z([[-2.6,1.51,.04,.04],[-2.40,1.51,.70,.68],[-1.9,1.51,.79,.75],[1.9,1.51,.79,.75],[2.4,1.51,.70,.68],[2.6,1.51,.04,.04]],'#BEC3B5',24)]
        for z in (-1.60,1.60):detail.append(basebox([1.54,.14,.31],[0,.80,z],M))
        detail.append(revolve([(.001,2.24),(.18,2.24),(.18,2.37),(.001,2.37)],M,16))
        for z in (-.24,.24):detail.append(axis_cylinder([.84,.75,z],[.84,2.24,z],.022,M))
        for j in range(7):detail.append(axis_cylinder([.84,.90+j*.19,-.24],[.84,.90+j*.19,.24],.02,M))
    elif key=='freight':
        body=[basebox([2.08,.12,5.85],[0,.77,0],'#A28369')]
        for x in (-1.01,1.01):body.append(basebox([.085,1.43,5.85],[x,.85,0],'#946F59'))
        for z in (-2.88,2.88):body.append(basebox([2.08,1.43,.08],[0,.85,z],'#946F59'))
        for x in (-1.06,1.06):
            for j in range(9):detail.append(basebox([.035,1.42,.046],[x,.85,(j-4)*.68],D))
    else:
        passenger=key in ('passenger','metro','tram','electric');col=P if key in ('electric','locomotive') else '#7C94A0'
        if key=='locomotive':
            body=[basebox([1.45,1.02,4.11],[0,.78,.75],col),basebox([1.91,1.52,1.55],[0,.78,-1.70],col),basebox([2.05,.12,1.65],[0,2.30,-1.70],'#C8C8B5')]
            for x in (-.965,.965):glass.append(basebox([.016,.53,1.00],[x,1.66,-1.68],G))
            detail += [axis_cylinder([0,1.81,1.35],[0,2.22,1.35],.09,D)]
        else:
            body=[basebox([2.05,.89,5.95],[0,.78,0],col),basebox([2.10,.13,6.02],[0,2.49,0],'#C8C8B5')]
            for x in (-1.005,1.005):
                for j in range(9):body.append(basebox([.066,.89,.085],[x,1.64,(j-4)*.72],col))
                for j in range(8):glass.append(basebox([.023,.76,.64],[x,1.67,(j-3.5)*.72],G))
            for z in (-2.94,2.94):body.append(basebox([2.05,.84,.055],[0,1.64,z],col));glass.append(basebox([1.66,.53,.019],[0,1.84,z+(.033 if z>0 else -.033)],G))
            if key in ('electric','tram'):
                for x in (-.39,.39):
                    detail += [beam([x,2.64,-.57],[x,3.03,0],.028,M),beam([x,3.03,0],[x,3.40,-.57],.028,M)]
                detail += [block([1.14,.035,.11],[0,3.40,-.57],M)]
            for x in (-.66,.66):detail.append(ellipsoid([x,1.13,3.002],[.12,.12,.025],'#DAD1AC',10,5))
    items=[node(ident,'bogies',base,material='mat.metal'),node(ident,'carbody',body,material='mat.paint'),node(ident,'coupling_and_equipment',detail,material='mat.metal')]
    if glass:items.append(node(ident,'windows',glass,material='mat.vehicleGlass'))
    replace(ident,items,'铁路车辆的轮组被压扁或隐藏，罐车为缩放容器，电力机车不具有完整车体。','双转向架四轴八轮、真实圆截面罐体与鞍座；客运窗带和车端、车钩按统一轨距和车架组织。')

def author():
    for k in 'tractor harvester loader excavator bulldozer roller forklift telehandler crane sweeper snowplow paver'.split():utility(k)
    for k in 'locomotive electric passenger metro freight tank flat tram'.split():rail(k)
