"""v2.1 quality repairs. Runs after all authors, before persistent user overrides.
Repairs are explicit and stable-ID based: never an automatic 'heal all meshes'.
"""
from copy import deepcopy
import math
from foundation.common import PARTS, P, C, Q, mul, choice, loft, profile, poly, box, ico

REBUILT = {}

def forms(ident):
    return PARTS[ident]['shape_params']['forms']

def mark(ident, reason):
    REBUILT.setdefault(ident, []).append(reason)
    d=PARTS[ident]
    d['source'].update(revision='2.1.0', refinement='tools/refinement/__init__.py')
    d['quality']['refinement']=REBUILT[ident].copy()
    d['quality']['review_scope']='2.1 topology / silhouette / toon isolation'

def reverse(ident, indices):
    for i in indices: forms(ident)[i]['faces']=[list(reversed(face)) for face in forms(ident)[i]['faces']]
    mark(ident,'Explicit outward winding repair; positions and sockets unchanged')

def solid(points, faces, colour, **kw):
    """Orient a newly authored numeric closed polyhedron, preserving every edge.
    Used only on this module's authored topology, not imported/user geometry.
    """
    from collections import defaultdict, deque
    faces=[list(f) for f in faces]; edges=defaultdict(list)
    for i,f in enumerate(faces):
        for a,b in zip(f, f[1:]+f[:1]): edges[tuple(sorted((a,b)))].append((i,a,b))
    if any(len(e)!=2 for e in edges.values()): raise ValueError('Authored solid is not closed')
    seen={0}; queue=deque([0])
    while queue:
        i=queue.popleft(); f=faces[i]
        for a,b in zip(f, f[1:]+f[:1]):
            for j,_,_ in edges[tuple(sorted((a,b)))]:
                if j in seen: continue
                g=faces[j]
                if any(x==a and y==b for x,y in zip(g,g[1:]+g[:1])): faces[j].reverse()
                seen.add(j);queue.append(j)
    vol=0
    for face in faces:
        a=points[face[0]]
        for k in range(1,len(face)-1):
            b=points[face[k]];c=points[face[k+1]]
            vol+=a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0])
    if vol<0:faces=[list(reversed(f)) for f in faces]
    return poly(points,faces,colour,**kw)

def author():
    REBUILT.clear()
    # A cape is intentionally an open cloth sheet. Remove the redundant
    # shoulder triangle sharing two already paired edges (third incident face).
    forms('w.wear.cape')[0]['faces'].pop()
    forms('w.wear.cape')[0]['surface_type']='cloth-sheet'
    mark('w.wear.cape','Remove overlapping third-face shoulder bridge; preserve intentional neck/hem boundary')
    # The original values were negative solids, hidden by double-sided materials.
    for ident,ix in [('core.nature.rock',[0]),('core.vehicle.body_center',[1]),('w.mech.fork_carriage',[1,2])]:reverse(ident,ix)
    for ident,i in [('w.nature.mushroom',1),('w.outpost.dish',0)]:
        forms(ident)[i]['reverse']=not forms(ident)[i].get('reverse',False)
        mark(ident,'Outward closed-profile lathe winding; dimensions unchanged')
    forms('p6.fish.tail')[0]['frame_axis']=[0,0,-1]
    mark('p6.fish.tail','Caudal peduncle uses its actual -Z sweep direction')

    # Human planes remain intentionally faceted. Never round eyelids, lips and
    # cranium together simply because two vertex positions happen to coincide.
    head=forms('core.human.head');reverse('core.human.head',[1])
    head[0]['rings'].insert(4,{'c':[0,.083,-.007],'r':[mul(.132,Q('face_width')),.112]})
    head[0].update(roundness=.34,style_overrides={'toon':{'roundness':.32,'smooth_angle':68}})
    head[1].update(style_overrides={'toon':{'smooth_angle':28}})
    # Recessed, short lips and pupil inlays; no floating teeth or giant eyeballs.
    head[2]['bevel']=.0018
    for f in head:
        if f.get('kind')=='bevelbox' and f.get('color')==C('white'):f['bevel']=.0038
    mark('core.human.head','Supported forehead/cheek profile; bounded facial crease policy')
    hair=forms('core.human.hair.short')
    hair[0]=profile([
        [0,.055,-.025,.139,.122],[0,.103,-.024,.142,.124],
        [.004,.149,-.023,.126,.115],[.016,.181,-.027,.096,.091],
        [.027,.191,-.035,.045,.052],[.029,.196,-.037,.019,.025]
    ],'hair',frame_axis=[0,1,0],roundness=.24,style_overrides={'toon':{'roundness':.30,'smooth_angle':64}})
    mark('core.human.hair.short','Continuous six-section asymmetric hair cap; avoids random overlapping chunks')

    hand=forms('core.human.hand');wrist=deepcopy(hand[0]);root=deepcopy(wrist['rings'][0])
    wrist['rings']=[root,{'c':[0,-.026,.007],'r':[.045,.030]},
        {'c':[0,-.056,.013],'r':[.045,.025]},
        {'c':[0,-.079,.017],'r':[.035,.020]}]
    wrist.update(roundness=.30,style_overrides={'toon':{'roundness':.36,'smooth_angle':66}},preserve_ends=True)
    thumb=profile([[-.032,-.023,.013,.019,.020],[-.051,-.045,.032,.020,.019],
        [-.049,-.064,.048,.017,.016],[-.038,-.079,.051,.010,.012]],'skin',bone='hand',roundness=.30)
    fingers=[]
    for i,(x,length) in enumerate([(-.027,.050),(-.009,.059),(.009,.055),(.027,.043)]):
        r=.0098 if i<3 else .009
        fingers.append(loft([
            [x,-.067,.017,r,r*1.35],
            [x,choice('grip',{'false':-.086,'true':-.086}),choice('grip',{'false':.022,'true':.036}),r*.97,r*1.13],
            [x,choice('grip',{'false':-.066-length*.80,'true':-.082}),choice('grip',{'false':.028,'true':.058}),r*.82,r],
            [x,choice('grip',{'false':-.067-length,'true':-.065}),choice('grip',{'false':.031,'true':.060}),r*.61,r*.75]
        ],'skin',8,bone='hand',roundness=.23,style_overrides={'toon':{'roundness':.26}},preserve_ends=True))
    PARTS['core.human.hand']['shape_params']['forms']=[wrist,thumb,*fingers]
    mark('core.human.hand','Palm + four tapered fingers + thumb; grip changes geometry; original wrist ring/bone preserved')

    # Feline muzzle lobes now use stable, purposeful rings rather than distorted
    # icosahedra. Ear shells are closed wedges, with inset single-sided patches.
    cat=forms('core.animal.cat.head'); body=deepcopy(cat[0]);body['roundness']=.32
    new=[body]
    for sg in [-1,1]:
        new.append(loft([[sg*.034,-.042,.047,.039,.026],[sg*.034,-.039,.079,.041,.029],
            [sg*.028,-.037,.096,.032,.020],[sg*.022,-.035,.100,.015,.013]],'cream',10,frame_axis=[0,0,1],roundness=.22))
    nose=solid([[-.019,-.021,.094],[.019,-.021,.094],[0,-.041,.103],
                [-.015,-.020,.106],[.015,-.020,.106],[0,-.039,.115]],
               [[0,1,2],[3,5,4],[0,3,4,1],[1,4,5,2],[2,5,3,0]],'skinShade',smooth_angle=24)
    new.append(nose)
    # Keep existing eyes and their original local positions.
    new.extend(deepcopy(cat[4:6]))
    for sg in [-1,1]:
        ear=solid([[sg*.033,.050,-.028],[sg*.105,.035,-.026],[sg*.087,.167,-.019],
             [sg*.034,.055,.013],[sg*.104,.038,.012],[sg*.085,.155,-.005]],
             [[0,1,2],[3,5,4],[0,3,4,1],[1,4,5,2],[2,5,3,0]],cat[0]['color'])
        new.append(ear)
        new.append(poly([[sg*.046,.065,.014],[sg*.094,.055,.012],[sg*.085,.133,-.003]],
            [[0,2,1] if sg<0 else [0,1,2]],'skinShade'))
    PARTS['core.animal.cat.head']['shape_params']['forms']=new
    mark('core.animal.cat.head','Closed ear prisms; layered continuous muzzle; correctly wound nose')

    for isfox in [False,True]:
        ident='w.fauna.'+('fox' if isfox else 'dog')+'.head';old=forms(ident);col=old[0]['color'];sn=.21 if isfox else .16
        new=[loft([[0,.048,-.04,.078,.089],[0,.058,.012,.099,.107],
             [0,.025,.076,.096,.085],[0,-.006,sn*.76,.048,.045],
             [0,-.018,sn,.028,.033]],col,10,frame_axis=[0,0,1],roundness=.25),
             loft([[0,-.048,.048,.064,.035],[0,-.047,sn*.69,.048,.032],
                 [0,-.032,sn,.027,.022]],'cream',8,frame_axis=[0,0,1],roundness=.23)]
        new.extend(deepcopy(old[2:5]))
        for sg in [-1,1]:
            new.append(solid([[sg*.032,.091,-.034],[sg*.109,.075,-.030],[sg*.085,.238,-.023],
                [sg*.034,.102,.014],[sg*.107,.084,.010],[sg*.084,.222,-.009]],
                [[0,1,2],[3,5,4],[0,3,4,1],[1,4,5,2],[2,5,3,0]],col))
            new.append(poly([[sg*.049,.112,.012],[sg*.096,.098,.009],[sg*.084,.194,-.006]],
                [[0,2,1] if sg<0 else [0,1,2]],'woodDark'))
        PARTS[ident]['shape_params']['forms']=new
        mark(ident,'Continuous brow-to-muzzle transition and finite-thickness forward ear shells')

    # Deliberate, watertight butterfly membrane. Concave front/hind lobes use
    # constrained triangulation in the shared kernel. Marks lie ON the plane,
    # offset by 0.15/0.30mm, not floating quads on unrelated heights.
    outline=[(0,.040),(.030,.080),(.079,.111),(.128,.106),(.157,.080),
        (.140,.035),(.105,.008),(.137,-.020),(.162,-.057),(.145,-.082),
        (.104,-.091),(.062,-.078),(.027,-.044),(0,-.035)]
    top=.0012;bot=-.0012;n=len(outline)
    pts=[[x,top,z] for x,z in outline]+[[x,bot,z] for x,z in outline]
    faces=[list(range(n)),list(reversed(range(n,2*n)))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]
    wing=[solid(pts,faces,'shadow',smooth_angle=0)]
    # Forewing and hindwing colour islands, each clear of the outer dark margin.
    patches=[([(.018,.038),(.043,.071),(.081,.098),(.120,.094),(.143,.077),(.127,.040),(.092,.020)],'orange'),
             ([(.022,-.028),(.052,-.008),(.109,-.019),(.145,-.057),(.130,-.070),(.099,-.078),(.064,-.065)],'orange'),
             ([(.047,.052),(.076,.085),(.098,.088),(.109,.062),(.083,.035)],'amber'),
             ([(.057,-.026),(.091,-.027),(.117,-.050),(.099,-.064),(.069,-.054)],'amber')]
    for j,(coords,color) in enumerate(patches):
        # Amber islands overlap the orange ones: they need a distinct height.
        # A single shared height caused visible z-fighting in real GLB review.
        offset=.00015 if j<2 else .00030
        up=list(range(len(coords)))
        signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(coords,coords[1:]+coords[:1]))
        if signed>0:up.reverse()  # x/z signed area has the opposite Y normal.
        wing.append(poly([[x,top+offset,z] for x,z in coords],[up],color,smooth_angle=0))
        wing.append(poly([[x,bot-offset,z] for x,z in coords],[up[::-1]],color,smooth_angle=0))
    PARTS['p6.insect.butterfly_wing']['shape_params']['forms']=wing
    mark('p6.insect.butterfly_wing','Two-lobe concave 2.4mm membrane, coherent closed winding, registered bilateral colour patches')
    mark('p6.insect.butterfly_wing_left','Mirrored source inherits rebuilt wing; independent hinge retained')

    # Beetle shell is a true swept carapace instead of four intersecting crystals.
    bs=[loft([[0,.066,-.105,.012,.018],[0,.075,-.083,.040,.032],
         [0,.081,-.035,.059,.039],[0,.080,.025,.055,.039],
         [0,.079,.053,.043,.029]],'teal',12,frame_axis=[0,0,1],roundness=.18),
        loft([[0,.080,.044,.044,.026],[0,.085,.071,.052,.029],
              [0,.081,.099,.035,.023]],'shadow',10,frame_axis=[0,0,1],roundness=.18),
        loft([[0,.075,.086,.024,.018],[0,.075,.123,.030,.022],
              [0,.072,.151,.017,.014]],'teal',10,frame_axis=[0,0,1],roundness=.18),
        loft([[0,.110,-.070,.0015,.0015],[0,.120,-.032,.0015,.0015],
              [0,.119,.020,.0015,.0015],[0,.107,.047,.0015,.0015]],'shadow',5,roundable=False)]
    for sg in [-1,1]:bs.append(ico([.009,.009,.010],'ink',[sg*.024,.086,.130],1,distort=0))
    PARTS['p6.insect.beetle_shell']['shape_params']['forms']=bs
    mark('p6.insect.beetle_shell','Swept elytra/thorax/head with supported ridgeline and leg-root coverage')
    legs=[]
    for sg in [-1,1]:
        for z in [-.055,0,.060]:
            legs.append(loft([[sg*.035,.066,z,.008,.009],[sg*.073,.061,z-.016,.007,.007],
                [sg*.092,.050,z-.024,.006,.006],[sg*.124,.010,z+.029,.0045,.0045],
                [sg*.142,.005,z+.041,.0025,.003]],'shadow',6,roundness=.13))
        legs.append(loft([[sg*.018,.086,.133,.0032,.0032],[sg*.032,.105,.158,.0032,.0032],
            [sg*.045,.101,.178,.0026,.0026],[sg*.050,.089,.194,.0018,.0018]],'shadow',6,roundness=.12))
    PARTS['p6.insect.beetle_legs']['shape_params']['forms']=legs
    mark('p6.insect.beetle_legs','Tapered five-section six legs, contained roots and four-section antennae')

    # Shell markings follow the actual faceted surface. No detached rod cage.
    shell=forms('p6.turtle.shell');base=shell[0]
    radii=[(.0,0),(.22,0),(.39,.10),(.37,.24),(.23,.40),(.07,.44)]
    pts=[];sides=10
    for r,y in radii:
        pts += [[math.cos(2*math.pi*k/sides)*r,y,math.sin(2*math.pi*k/sides)*r*1.32] for k in range(sides)]
    # Build face-coloured shell explicitly using the original lathe profile;
    # neutral vertex colours cannot accidentally determine smooth-normal islands.
    f=[];colors=[]
    for j in range(len(radii)-1):
        for k in range(sides):
            f.append([j*sides+k,(j+1)*sides+k,(j+1)*sides+(k+1)%sides,j*sides+(k+1)%sides])
            colors.append(C(['moss','lichen','leafDark'][(k//2+j)%3]) if j>=2 else C('moss'))
    f.append(list(range((len(radii)-1)*sides,len(radii)*sides))[::-1]);colors.append(C('moss'))
    # Axis ring contains coincident points; kernel strips the degenerate fan.
    shellpoly=poly(pts,f,'moss',colors=colors,style_overrides={'toon':{'smooth_angle':64}})
    PARTS['p6.turtle.shell']['shape_params']['forms']=[shellpoly,deepcopy(shell[1])]
    mark('p6.turtle.shell','Registered face-colour scutes replace floating tube cage; original shell/abdomen envelope retained')

    # Keep the head attached at its original neck socket, add controlled beak taper.
    th=forms('p5.turtle-head.module')
    th[0]=loft([[0,.13,.35,.092,.065],[0,.143,.48,.102,.074],
        [0,.154,.58,.119,.084],[0,.146,.66,.102,.072],
        [0,.13,.733,.055,.052]],'lichen',10,frame_axis=[0,0,1],roundness=.25)
    mark('p5.turtle-head.module','Neck/skull/beak support sections; assembly pivot and four-flipper spacing retained')
