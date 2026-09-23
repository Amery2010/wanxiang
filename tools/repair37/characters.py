"""Keep the existing skinned human; repair the bone-local equipment contract."""
from .common import *
from l34_expansion.character import ROLES

def author():
    for key,name,kit,headwear,outfit in ROLES:
        ident='l3-character-profession-'+key;d=ASSEMBLIES[ident];items=deepcopy(d['instances']);clips=deepcopy(MOTIONS.get(ident))
        for it in items:
            nid=it['id']
            if nid=='apron':it['position']=[0,-.28,0]
            elif nid=='backpack':it['position']=[0,-.02,-.19]
            elif nid=='breastplate':it['position']=[0,.02,.057]
            elif nid.startswith('pauldron'):
                side='L' if nid.endswith('0') else 'R';it['parent']='skin.rig.arm'+side;it['position']=[0,.012,0]
            elif nid=='cape':it['position']=[0,-.27,-.17]
            elif nid=='skirt':it['position']=[0,-.16,0]
            elif nid=='hat' and key=='cook':it['part']='w.wear.toque'
            elif nid=='hat' and key=='knight':it['part']='w.wear.field_helmet'
            elif nid=='skin':
                palette={}
                if key in ('cook','medic','technician'):palette={'#EFE3CB':'#ECEDE5','#707952':'#607077'}
                elif key in ('guard','knight'):palette={'#EFE3CB':'#6B7F89','#707952':'#566367'}
                elif key in ('captain','pilot'):palette={'#EFE3CB':'#6A7D8A','#707952':'#425965'}
                elif key=='diver':palette={'#EFE3CB':'#384E59','#F8F3E7':'#597786','#707952':'#354F5B','#DDAA85':'#425D69','#634530':'#42545A'}
                if palette:it['params']['palette']=palette
        # Hair visible only at the nape/temples: crown hair must not penetrate fitted headwear.
        for i,it in enumerate(items):
            if it['id']=='hair':
                hair=[block([.019,.070,.047],[s*.126,.018,-.041],'#57402E',bevel=.005) for s in (-1,1)]+[profile_z([[-.112,-.01,.090,.071],[-.088,-.01,.097,.075]],'#57402E',10)]
                items[i]=node(ident,'hair',hair,material='mat.hair',parent='skin.rig.head')
        if key=='diver':
            # Closed compressed-gas silhouette and a connected hose, not a parcel backpack.
            tank=[revolve([(.001,-.26),(.070,-.24),(.075,.21),(.055,.26),(.001,.27)],'#ADC0BC',16)]
            for x in (-.10,.10):items.append(node(ident,'cylinder'+('L' if x<0 else 'R'),tank,at=[x,-.04,-.25],material='mat.metal',parent='skin.rig.chest'))
            items.append(node(ident,'breathing_hose',[tube([[.12,.05,-.20],[.25,.25,-.03],[.16,.37,.13],[0,.29,.17]],.012,'#384B50',8)],parent='skin.rig.chest'))
        if key in ('medic','technician'):
            items.append(node(ident,'medical_case',[basebox([.18,.18,.09],[.20,-.24,.01],'#B0BEA8'),block([.065,.025,.012],[.20,-.14,.062],'#5D836D'),block([.025,.065,.012],[.20,-.14,.062],'#5D836D')],parent='skin.rig.pelvis'))
        replace(ident,items,'骨骼局部坐标混用：围裙遮住面部、背包埋入躯干，长服饰和肩甲挂点错误，头发穿帽。','围裙按腰部原点偏置、背包退至背后、肩甲跟随上臂，帽下头发截短；保留原人体蒙皮与检查动作。')
        if clips:MOTIONS[ident]=clips
