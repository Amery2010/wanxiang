"""Botanical silhouettes: growth habit, reproductive placement and connected stems."""
from .common import *
from l1_expansion.common import placed
GREEN='#658E48'; DARK='#426745'; LIGHT='#8FA95A'; WOOD='#786047'

def e(p,s,c):return ellipsoid(p,s,c,segments=8,rings=4)
def shift(fs,p=(0,0,0),r=(0,0,0),s=(1,1,1)):return placed(fs,p,r,s)

def flower(p,color='#EAD9AA',petals=7,r=.12,upright=False):
    x,y,z=p;out=[]
    for i in range(petals):
        a=math.tau*i/petals
        if upright:
            a0=[x+math.sin(a)*r*.28,y+math.cos(a)*r*.28,z];b=[x+math.sin(a)*r,y+math.cos(a)*r,z]
            out.append(ellipsoid([(a0[0]+b[0])/2,(a0[1]+b[1])/2,z],[r*.43,r*.43,.04],color,8,4))
        else:out.append(leaf([x,y,z],[x+math.sin(a)*r,y+.01,z+math.cos(a)*r],r*.65,color,curve=.03))
    out.append(e([x,y+.018,z] if not upright else [x,y,z+.03],[r*.65,.05 if not upright else r*.65,r*.65 if not upright else .055],'#BA9B42'))
    return out

def pinnate(root,tip,width=.4,n=9,color=GREEN):
    out=[tube([root,[(root[k]+tip[k])/2 for k in range(3)],tip],[.016,.012,.003],color,6)]
    dx=tip[0]-root[0];dz=tip[2]-root[2];ll=max(.001,math.hypot(dx,dz));sx,sz=-dz/ll,dx/ll
    for j in range(1,n+1):
        t=j/(n+1);c=[root[k]+(tip[k]-root[k])*t for k in range(3)];w=width*math.sin(math.pi*t)**.7
        for side in (-1,1):out.append(leaf(c,[c[0]+sx*w*side+dx*.09,c[1]-.025,c[2]+sz*w*side+dz*.09],w*.24,color,curve=.035,thickness=.008))
    return out

def rosette(key,h=.65):
    out=[];rings=3 if key=='succulent' else 2
    for ring in range(rings):
        n=9-ring*2
        for i in range(n):
            a=math.tau*(i+ring*.38)/n;rr=(.64-ring*.15)*h/.65;yy=(.16+ring*.15)*h/.65
            out.append(leaf([0,.02,0],[math.sin(a)*rr,yy,math.cos(a)*rr],(.27 if key=='succulent' else .19)*h/.65,'#759C83' if key=='succulent' else '#709571',curve=.18*h/.65,thickness=.045 if key=='succulent' else .026))
    out.append(leaf([0,.02,0],[.01,h,0],.16, '#8BA884',curve=0,thickness=.025));return out

def cereal(key,h=1):
    out=[];heads=[]
    for j in range(3 if key=='rice' else 2):
        x=(j-.5)*.09;z=.025*math.sin(j*3);top=h*(.9+.06*j)
        out.append(tube([[x,0,z],[x*.9,top*.5,z],[x+.025,top,z]],.012 if key!='cane' else .035,GREEN,6))
        for k in range(3):
            y=top*(.2+k*.19);side=(-1)**k
            out.append(leaf([x,y,z],[x+side*.23,y+.09,z+side*.15],.045,'#91A653',curve=.05,thickness=.006))
        if key=='rice':
            for q in range(4):
                xx=x+.07*(q+1);yy=top+.06-.028*q
                heads.append(tube([[x+.025,top,z],[xx,yy+.06,z+.02*q],[xx+.035,yy-.08,z+.02*q]],.006,'#BCAA65',5))
                for t in range(3):heads.append(e([xx+.015,yy-.03*t,z+.02*q],[.033,.048,.025],'#D1BA73'))
        else:
            stemcolor='#CFB576';heads.append(tube([[x+.025,top-.025,z],[x+.025,top+.25,z]],.009,stemcolor,5))
            for k in range(6):
                for side in (-1,1):
                    yy=top+k*.034;xx=x+.025+side*.022
                    heads.append(e([xx,yy,z],[.045,.055,.031],stemcolor))
                    if key=='barley':heads.append(tube([[xx,yy,z],[xx+side*.036,yy+.14,z]],.0025,'#DDC782',4))
    return out+heads

def crop(key):
    out=[]
    if key in ('wheat','barley','rice'):return cereal(key,.8 if key=='rice' else 1.03)
    if key in ('corn','cane','sorghum'):
        h={'corn':1.8,'cane':2.1,'sorghum':1.65}[key];out=[tube([[0,0,0],[0,h,0]],.026 if key!='cane' else .045,GREEN,8)]
        for j in range(7):
            y=.2+j*h*.09;a=j*2.42
            out.append(leaf([0,y,0],[math.sin(a)*.56,y+.08,math.cos(a)*.56],.12 if key=='corn' else .065,GREEN,curve=.18,thickness=.008))
            if key=='cane':out.append(revolve([(.045,y-.012),(.052,y-.012),(.052,y+.012),(.045,y+.012)],'#B2B36C',8))
        if key=='corn':
            for side,y in [(-1,.75),(1,1.03)]:
                out.append(e([side*.075,y,.025],[.12,.3,.115],'#D5B75F'));out.append(leaf([0,y-.2,0],[side*.12,y+.12,.10],.15,GREEN,curve=.015))
            for i in range(5):out.append(tube([[0,h-.12,0],[.09*math.sin(i),h+.13,.09*math.cos(i)]],.008,'#BCAA6C',5))
        elif key=='sorghum':
            for i in range(16):
                a=i*2.4;y=h-.04+(i%4)*.06;out.append(e([math.sin(a)*.065,y,math.cos(a)*.065],[.06,.09,.06],'#9D6145'))
        return out
    if key=='sunflower':
        out=[tube([[0,0,0],[0,1.5,0]],.026,GREEN,8)]
        for j in range(4):out.append(leaf([0,.28+j*.24,0],[(-1)**j*.37,.35+j*.24,(-1)**(j//2)*.13],.25,GREEN,curve=.12))
        out+=flower([0,1.48,.015],'#E3B741',14,.28,True);out.append(ellipsoid([0,1.48,.057],[.28,.28,.055],'#61503B',12,5));return out
    if key=='lettuce':return rosette('succulent',.34)[:-1]+[e([0,.17,0],[.23,.23,.23],'#9DB975')]
    if key in ('pumpkin','strawberry','clover'):
        for j in range(4):
            a=j*math.tau/4;r=.45 if key=='pumpkin' else .21;x=math.sin(a)*r;z=math.cos(a)*r
            out.append(tube([[0,.025,0],[x*.5,.03,z*.5],[x,.04,z]],.012,GREEN,6))
            for q in range(2):
                root=[x*(q+1)/2,.04,z*(q+1)/2];yy=.18 if key=='pumpkin' else .11
                out.append(tube([root,[root[0],yy,root[2]]],.008,GREEN,5))
                for k in range(3 if key in ('clover','strawberry') else 1):
                    aa=a+k*2.094;out.append(leaf([root[0],yy,root[2]],[root[0]+math.sin(aa)*.15,yy+.015,root[2]+math.cos(aa)*.15],.2 if key=='pumpkin' else .10,GREEN,curve=.02))
            if key=='pumpkin':
                c=[x*.75,.12,z*.75]
                for q in range(8):aa=q*math.tau/8;out.append(e([c[0]+.063*math.sin(aa),c[1],c[2]+.063*math.cos(aa)],[.15,.23,.15],'#C8863C'))
                out.append(tube([[c[0],.22,c[2]],[c[0]+.018,.28,c[2]]],.023,'#786E3F',6))
            elif key=='strawberry':out.append(profile_z([[z,.055,.035,.046,x],[z+.06,.045,.014,.018,x]],'#BC4D46',8))
            else:out+=flower([x,.13,z],'#E8D8D5',5,.04)
        return out
    if key in ('grape','beans','tomato'):
        out=[tube([[-.12,0,0],[-.08,.4,.01],[.05,.8,.03],[0,1.22,0]],.018,WOOD if key=='grape' else GREEN,7)]
        for j in range(7):
            y=.16+j*.15;side=(-1)**j;x=.24*side
            out.append(tube([[0,y,0],[x,y+.12,0]],.009,GREEN,6));out.append(leaf([x*.6,y+.07,0],[x*1.4,y+.17,.04],.23 if key=='grape' else .14,GREEN,curve=.03))
            if j%2:
                if key=='grape':
                    for q in range(9):aa=q*2.4;out.append(e([x+.03*math.sin(aa)*(1-q/13),y-.018*q,.02+.03*math.cos(aa)*(1-q/13)],[.058,.058,.058],'#786186'))
                elif key=='beans':out.append(tube([[x,y+.02,.04],[x+.02,y-.12,.06],[x+.005,y-.23,.05]],[(.018,.011),(.023,.013),(.006,.006)],'#88A15D',6))
                else:out.append(e([x,y,.06],[.13,.12,.13],'#C75442'))
        return out
    if key in ('lotus','waterlily'):
        for i in range(5):
            a=i*2.4;r=.18+i*.045;x=math.sin(a)*r;z=math.cos(a)*r;y=.38+i*.035 if key=='lotus' else .014
            if key=='lotus':out.append(tube([[0,0,0],[x,y,z]],.01,GREEN,6))
            outline=[]
            for q in range(19):ang=.15+q*(math.tau-.3)/18;outline.append([x+.19*math.sin(ang),z+.19*math.cos(ang)])
            outline.append([x,z]);out.append(slab_polygon(outline,y,.01,'#679667'))
        fy=.61 if key=='lotus' else .075
        out.append(tube([[0,0,0],[0,fy,0]],.014,GREEN,6));out+=flower([0,fy,0],'#E8B2B9',10,.18);out+=flower([0,fy+.035,0],'#F0D2CB',7,.11);return out
    if key=='cotton':
        out=[tube([[0,0,0],[0,.8,0]],.018,WOOD,6)]
        for j in range(5):
            a=j*2.4;y=.3+j*.1;x=.24*math.sin(a);z=.24*math.cos(a)
            out.append(tube([[0,y-.15,0],[x,y,z]],.012,WOOD,6));out.append(leaf([x*.5,y-.08,z*.5],[x*1.2,y+.02,z*1.2],.14,GREEN,curve=.035))
            for q in range(4):out.append(e([x+.035*math.sin(q*1.57),y+.025*(q%2),z+.035*math.cos(q*1.57)],[.095,.10,.09],'#E9E4D2'))
        return out
    # Herbaceous flowers: non-woody stalk, basal/alternating leaves and a real corolla.
    h=.48 if key=='tulip' else .42 if key=='daisy' else .62
    out=[tube([[0,0,0],[0,h,0]],.012,GREEN,6)]
    for side in (-1,1):out.append(leaf([0,.02,0],[side*.16,.38 if key=='tulip' else .18,.05],.08,GREEN,curve=.08))
    if key=='tulip':
        for i in range(6):
            a=i*math.tau/6;out.append(leaf([math.sin(a)*.018,h-.06,math.cos(a)*.018],[math.sin(a)*.085,h+.1,math.cos(a)*.085],.11,'#C86574',curve=.01))
    elif key=='orchid':
        for y in (.35,.49,.62):out+=flower([.07,y,.035],'#D5ADC7',5,.105,True);out.append(tube([[0,y-.04,0],[.07,y,.03]],.006,GREEN,5))
    else:out+=flower([0,h,0],'#EDE6CD',10,.13)
    return out

def shrub(key):
    if key in ('aloe','agave','succulent'):return rosette(key,.65 if key!='agave' else .95)
    if key in ('fern','cycad'):
        out=[revolve([(.04,0),(.15,.1),(.11,.35),(.03,.4)],WOOD,10,False)]
        for i in range(9):
            a=i*math.tau/9;out+=pinnate([0,.25,0],[math.sin(a)*.8,.30,math.cos(a)*.8],.21,9,'#5E874F')
        return out
    if key=='cactus':
        out=[tube([[0,0,0],[0,1.35,0]],[.15,.11],'#65917B',12),ellipsoid([0,1.32,0],[.22,.2,.22],'#65917B',12,5)]
        for side,y in [(-1,.62),(1,.83)]:out.append(tube([[0,y,0],[side*.27,y,0],[side*.35,y+.10,0],[side*.35,y+.38,0]],[.1,.1,.1,.075],'#65917B',10));out.append(e([side*.35,y+.38,0],[.15,.14,.15],'#65917B'))
        for i in range(10):a=i*math.tau/10;out.append(tube([[.146*math.sin(a),.08,.146*math.cos(a)],[.112*math.sin(a),1.33,.112*math.cos(a)]],.006,'#8AA791',5))
        return out
    if key=='reed':return sum([shift(cereal('rice',1.1+i*.065),[.14*math.sin(i*2.4),0,.14*math.cos(i*2.4)]) for i in range(5)],[])
    if key in ('lavender','rosemary'):
        out=[]
        for j in range(11):
            a=j*2.4;x=.25*math.sin(a);z=.25*math.cos(a);h=.5+.1*(j%3)
            out.append(tube([[x*.3,0,z*.3],[x,h,z]],.009,GREEN,6))
            for k in range(4):
                for s in (-1,1):out.append(leaf([x*k/5,h*k/5,z*k/5],[x*k/5+s*.07,h*k/5+.04,z*k/5+.025],.018,'#819D72',curve=.015,thickness=.004))
            if key=='lavender':
                for k in range(5):out.append(e([x,h-.08+k*.03,z],[.057,.044,.055],'#9C83B0'))
        return out
    out=[];linear=key in ('hedge','tea');bloom=key in ('rose','hydrangea','azalea')
    for i in range(7):
        a=i*2.4;x=(i-3)*.21 if linear else math.sin(a)*.29;z=0 if linear else math.cos(a)*.29;yy=.53+.1*(i%3)
        out.append(tube([[x*.35,0,z*.35],[x,yy,z]],[.025,.008],WOOD,7))
        out.append(ellipsoid([x,yy-.04,z],[.60,.59,.56],DARK if key in ('holly','coffee','juniper') else GREEN,10,5))
        if bloom:
            color={'rose':'#C16B78','hydrangea':'#AAA0C0','azalea':'#D28CA6'}[key]
            for q in range(3):out+=flower([x+math.sin(q*2.1)*.15,yy+.22,z+math.cos(q*2.1)*.15],color,7,.09)
        if key in ('berry','holly','coffee'):
            for q in range(4):out.append(e([x+.22*math.sin(q*2.4),yy+.07,z+.22*math.cos(q*2.4)],[.065,.065,.065],'#BC635B' if key!='berry' else '#655F88'))
    return out

def mushroom(key,h=.42,r=.22):
    cream='#D7C6A1';brown='#967348';out=[]
    if key=='puffball':return [ellipsoid([0,h*.43,0],[r*2,h*.86,r*2],'#D7D0B9',14,7)]
    if key=='morel':
        out.append(tube([[0,0,0],[0,h*.43,0]],[r*.3,r*.33],cream,10));p=[];n=24;m=13
        for j in range(m):
            t=j/(m-1);rad=r*(.70+.3*math.sin(math.pi*t))*(1-t*.86)
            for i in range(n):
                a=i*math.tau/n;d=.8 if (i%4 in (1,2) and j%3==1) else 1;p.append([rad*d*math.sin(a),h*(.33+.67*t),rad*d*math.cos(a)])
        faces=[]
        for j in range(m-1):
            for i in range(n):a=j*n+i;b=j*n+(i+1)%n;faces.append([a,b,b+n,a+n])
        faces+=[list(range(n-1,-1,-1)),list(range((m-1)*n,m*n))];out.append(mesh(p,faces,brown));return out
    if key=='oyster':
        for j in range(4):
            a=j*1.95;x=.06*math.sin(a);z=.06*math.cos(a);y=.04+j*.065
            out.append(tube([[0,0,0],[x,y,z]],.03,cream,8));out.append(ellipsoid([x+.07*math.sin(a),y+.04,z+.07*math.cos(a)],[r*1.7,.09,r*1.35],'#B3A58B',12,5))
        return out
    out.append(tube([[0,0,0],[.01,h*.67,0]],[r*.23,r*.3],cream,10))
    if key=='chanterelle':profile=[(.001,h*.64),(r*.25,h*.67),(r,h*.91),(r*.96,h),(r*.38,h*.91),(.001,h*.77)];col='#C9A054'
    elif key=='inkcap':profile=[(.001,h*.65),(r,h*.55),(r*.83,h*.83),(r*.47,h),(.001,h*1.07)];col='#C1B9A3'
    else:profile=[(.001,h*.61),(r,h*.66),(r*.94,h*.78),(r*.62,h*.96),(.001,h*1.02)];col=brown if key!='fairy_ring' else '#BC895F'
    out.append(revolve(profile,col,18));return out

def tree(key,shape):
    h=4.4 if shape not in ('column','tier') else 5.6;out=[];fol=[]
    if key=='bamboo':
        for j in range(7):
            a=j*2.4;x=.32*math.sin(a);z=.32*math.cos(a);hh=3.7+.18*j
            out.append(tube([[x,0,z],[x+.12,hh,z]],[.07,.04],'#83925F',10))
            for k in range(1,9):out.append(revolve([(.055,hh*k/9-.02),(.073,hh*k/9-.02),(.073,hh*k/9+.02),(.055,hh*k/9+.02)],'#B8B080',10,at=(x+.12*k/9,0,z)))
            for k in range(3):
                y=hh*(.63+k*.12);fol+=pinnate([x+.08,y,z],[x+.7*math.sin(a+k),y-.10,z+.7*math.cos(a+k)],.18,6,GREEN)
        return out,fol
    thick=.75 if key=='baobab' else .45 if key in ('redwood','sequoia') else .16
    trunkcolor='#D9D2BD' if key in ('birch','aspen') else WOOD
    out.append(tube([[0,0,0],[.03,h*.35,.015],[0,h*.73,0],[.025,h*.89,0]],[thick,thick*.8,thick*.46,.025],trunkcolor,12))
    if key in ('birch','aspen'):
        for j in range(9):out.append(block([.20,.045,.016],[.015,h*.075*(j+1),thick*(1-.04*j)],'#666359',bevel=.001))
    if shape=='dead':
        for j in range(7):a=j*2.4;y=h*(.27+j*.07);out.append(tube([[0,y,0],[.62*math.sin(a),y+.25,.62*math.cos(a)],[.85*math.sin(a),y+.5,.85*math.cos(a)]],[.09,.045,.007],WOOD,7))
        return out,[]
    if shape in ('palm','palmfruit','umbrella'):
        root=[0,h*.85,0];banana=key=='banana'
        for j in range(9):
            a=j*math.tau/9;tip=[math.sin(a)*1.6,h*.7+(.18 if j%2 else 0),math.cos(a)*1.6]
            if banana:fol.append(leaf(root,tip,.7,GREEN,curve=.5,thickness=.016))
            elif shape=='umbrella':
                end=[math.sin(a)*.7,h*.87,math.cos(a)*.7];out.append(tube([[0,h*.65,0],end],[.11,.065],WOOD,8));fol+=shift(rosette('agave',.62),end)
            else:fol+=pinnate(root,tip,.38,11,GREEN)
        if key=='coconut':
            for j in range(5):a=j*math.tau/5;fol.append(e([.19*math.sin(a),h*.80,.19*math.cos(a)],[.23,.3,.23],'#A89B54'))
        if banana:
            for j in range(7):a=j*2.4;fol.append(tube([[.06,h*.71,0],[.13*math.sin(a),h*.66,.13*math.cos(a)],[.11*math.sin(a),h*.62,.11*math.cos(a)]],.035,'#B9B657',6))
        return out,fol
    if shape in ('tier','column') and key not in ('poplar','aspen','birch'):
        n=6
        for j in range(n):
            y=h*(.25+j*.105);r=(1.40 if key not in ('cypress','redwood') else .80)*(1-j/(n+1))
            fol.append(revolve([(.01,y+.06),(r,y+.08),(r*.81,y+.3),(r*.37,y+.72),(.008,y+1.1)],DARK if j%2==0 else GREEN,12))
        return out,fol
    n=10 if shape not in ('column',) else 8
    for j in range(n):
        a=j*2.4;rad=.50 if shape=='column' else 1.12;yy=h*(.60+.035*(j%5));x=math.sin(a)*rad;z=math.cos(a)*rad
        if shape in ('flat','umbrella'):yy=h*.78+(j%2)*.12
        out.append(tube([[0,h*.44,0],[x*.6,yy-.25,z*.6],[x,yy,z]],[.09,.055,.02],WOOD,8))
        c='#D3B3BD' if key=='cherry' else '#E2C7C6' if key=='plum' else '#BBBC81' if key=='ginkgo' else DARK if key=='olive' else GREEN
        fol.append(ellipsoid([x,yy+.16,z],[1.20 if rad>1 else .95,.68 if shape=='flat' else 1.12,1.20 if rad>1 else .95],c,12,5))
        if shape=='droop':
            for q in range(4):
                a2=a+q*1.57;tip=[x+.22*math.sin(a2),yy-1,z+.22*math.cos(a2)];fol.append(tube([[x,yy+.15,z],tip],[.012,.004],'#79916B',5))
                for t in (.25,.55,.8):
                    root=[x+(tip[0]-x)*t,yy+.15+(tip[1]-yy-.15)*t,z+(tip[2]-z)*t];fol.append(leaf(root,[root[0]+.055,root[1]-.22,root[2]+.03],.045,'#8CA86C',curve=.015,thickness=.005))
        if shape in ('fruit','citrus','nut'):
            for q in range(3):aa=q*2.1;fol.append(e([x+.43*math.sin(aa),yy-.18,z+.43*math.cos(aa)],[.12,.13,.12],'#C2833E' if shape=='citrus' else '#AC6252' if key=='apple' else '#B6A765'))
    if shape in ('aerial','root'):
        for j in range(7):
            a=j*math.tau/7;xx=.9*math.sin(a);zz=.9*math.cos(a)
            if shape=='root':out.append(tube([[0,1.3,0],[xx*.6,.6,zz*.6],[xx,0,zz]],[.13,.10,.035],WOOD,8))
            else:out.append(tube([[xx,h*.62,zz],[xx*.95,.3,zz*.95],[xx,0,zz]],[.045,.04,.06],WOOD,6))
    return out,fol

def aquatic(key):
    out=[ellipsoid([0,.08,0],[.7,.18,.6],'#938E82',12,5)];pink='#BE8E87'
    if key=='brain':
        out.append(ellipsoid([0,.34,0],[.9,.65,.8],'#B4A678',16,7))
        for j in range(8):
            z=-.30+j*.085;pts=[]
            for q in range(13):x=-.35+q*.058;y=.32+.28*math.sqrt(max(0,1-(x/.45)**2-(z/.41)**2));pts.append([x,y+.018+.013*math.sin(q*2.5+j),z+.015*math.sin(q*2)])
            out.append(tube(pts,.018,'#D1BD8A',6))
    elif key=='tube':
        for j in range(7):
            a=j*2.4;x=.2*math.sin(a);z=.2*math.cos(a);h=.42+.08*(j%3)
            out.append(revolve([(.095,.08),(.10,h-.03),(.085,h),(.060,h),(.055,.12)],pink,12,True,at=(x,0,z)))
    elif key=='plate':
        for j in range(4):out.append(tube([[0,.05,0],[.08*j,.14+j*.13,0]],.04,pink,8));out.append(ellipsoid([.08*j,.14+j*.13,0],[.65,.06,.55],pink,16,4))
    elif key=='anemone':
        out.append(revolve([(.2,.08),(.22,.14),(.16,.26),(.19,.3),(.08,.28)],pink,16))
        for j in range(28):a=j*2.4;r=.12+.03*(j%3);out.append(tube([[r*math.sin(a),.27,r*math.cos(a)],[r*1.8*math.sin(a),.45,r*1.8*math.cos(a)],[r*2*math.sin(a+.1),.56,r*2*math.cos(a+.1)]],[.018,.015,.007],'#D0A391',6))
    else:
        out.append(tube([[0,.06,0],[0,.64,0]],[.06,.012],pink,7))
        for j in range(9):
            y=.15+j*.049;a=j*2.4;end=[math.sin(a)*.38,y+.18,0 if key=='fan' else math.cos(a)*.38];out.append(tube([[0,y,0],end],[.025,.01],pink,7))
            for s in (-1,1):out.append(tube([[end[0]*.65,y+.12,end[2]*.65],[end[0]+s*.10,end[1]+.10,end[2]+(0 if key=='fan' else s*.08)]],[.016,.006],pink,6))
    return out

def author():
    from l34_expansion.nature import TREES
    for key,name,leafkey,shape,n in TREES:
        ident='l3-nature-tree-'+key;wood,fol=tree(key,shape);items=[node(ident,'trunk_and_branches',wood,material='mat.wood')]
        if fol:items.append(node(ident,'crown',fol,material='mat.leaf'))
        replace(ident,items,'树冠、叶簇和果实装配混用，部分冠层缺少可信枝干承接。','按生长习性重建连续树干、受支撑冠层；棕榈、竹、针叶与阔叶分别生成。')
    for ident in list(ASSEMBLIES):
        if ident.startswith('l3-nature-shrub-'):
            key=ident.removeprefix('l3-nature-shrub-');replace(ident,[node(ident,'plant',shrub(key),material='mat.leaf')],'灌木、蕨类与多肉共用木质枝杈，生长形态错误。','分别实现莲座肉质叶、仙人掌肉质茎、羽状蕨叶与有冠层的灌木。')
        elif ident.startswith('l3-nature-crop-'):
            key=ident.removeprefix('l3-nature-crop-');n=3 if key in ('corn','cane','sunflower','sorghum','tomato','beans','grape') else 4;items=[]
            for i in range(n):
                p=[(i%2-.5)*(.62 if n==3 else .48),0,(i//2-.5)*.52];items.append(node(ident,'plant'+str(i),shift(crop(key),p),material='mat.leaf'))
            if key in ('tomato','beans','grape'):
                forms=[basebox([.055,1.48,.055],[x,0,0],WOOD) for x in (-.56,.56)]
                for yy in (.5,.9,1.35):forms.append(beam([-.58,yy,0],[.58,yy,0],.035,WOOD))
                items.append(node(ident,'trellis',forms,material='mat.wood'))
            replace(ident,items,'作物使用粗木枝模板、产物位置与叶形不符；地表藤本被做成立木。','按草本茎、穗、叶、果实与栽培支架独立造型；南瓜匍匐，草莓贴地，水生叶贴近水位。')
        elif ident.startswith('l3-nature-fungus-'):
            key=ident.removeprefix('l3-nature-fungus-');n=8 if key=='fairy_ring' else 4;items=[]
            for i in range(n):
                a=i*math.tau/n;rr=.43 if n==8 else .18;fs=mushroom(key,.35+.075*(i%3),.15+.025*(i%2));items.append(node(ident,'fungus'+str(i),shift(fs,[rr*math.sin(a),0,rr*math.cos(a)]),material='mat.matte'))
            replace(ident,items,'菌盖与菌柄比例和连接不正确，羊肚菌出现漂浮环。','闭合菌盖与菌柄接合；羊肚菌用连续凹坑网格，侧耳侧生层叠，马勃取消错误长柄。')
        elif ident.startswith('l3-nature-aquatic-'):
            key=ident.removeprefix('l3-nature-aquatic-');replace(ident,[node(ident,'colony',aquatic(key),material='mat.matte')],'海绵、脑珊瑚、海扇混用木质枝段，主体辨识失效。','建立空心管口、连续沟脊、扇状分枝、盘状群体及海葵触手。')
