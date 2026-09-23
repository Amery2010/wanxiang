"""Preserve existing non-dimensional author controls with explicit new geometry."""
from .common import *


def author():
    def secondary(ident,indices):
        d=PARTS[ident];prop=d['parameter_schema']['properties']['detail']
        gate=Q('detail') if prop['type']=='boolean' else choice('detail',{'0':False,'1':True})
        for k in indices:d['shape_params']['forms'][k]['enabled']=deepcopy(gate)
    for ident in ['exp.nature.leaf_crown','exp.nature.maple_crown']:
        fs=PARTS[ident]['shape_params']['forms'];fs[0]['enabled']=choice('detail',{'0':False,'1':True});fs[1]['enabled']=choice('detail',{'0':True,'1':False})
    ident='exp.nature.willow_curtain';fs=PARTS[ident]['shape_params']['forms']
    secondary(ident,[i for i in range(1,len(fs)) if (i-1)%21!=0 and i%2==0])
    for ident in ['l1.nature.bark.moss_collar','l1.nature.leaf.banana','l1.nature.leaf.heart','l1.nature.leaf.lotus','l1.nature.leaf.oak']:
        fs=PARTS[ident]['shape_params']['forms'];secondary(ident,range(1,len(fs)))
    ident='l1.nature.frond.bipinnate';fs=PARTS[ident]['shape_params']['forms'];secondary(ident,[k for k in range(1,len(fs)) if fs[k]['kind']=='poly' and k%3==0])
    ident='l1.nature.crop.corn_cob';fs=PARTS[ident]['shape_params']['forms']
    # Keep the dense kernel layout in both modes; detailed mode shades each
    # faceted kernel separately, simple mode groups its normals smoothly.
    for f in fs[1:]:f['smooth_angle']=choice('detail',{'true':0,'false':55})
    ident='exp.nature.boulder';fs=PARTS[ident]['shape_params']['forms']
    from scipy.spatial import ConvexHull
    orig=fs[0];pts=np.asarray(orig['points'],float)
    selected=np.array([0,2,4,6,9,11,13,15,18,20,22,24,36,38,40,42])
    pp=pts[selected];h=ConvexHull(pp)
    coarse=mesh(pp.tolist(),h.simplices.tolist(),'#8B928A',material='mat.stone',roundable=False,name='boulder_coarse')
    orig['enabled']=choice('detail',{'0':False,'1':True});coarse['enabled']=choice('detail',{'0':True,'1':False});fs.append(coarse)
    ident='l1.nature.fungus.morel';fs=PARTS[ident]['shape_params']['forms']
    detailed=fs[0];n=14;rows=8
    # Same outer silhouette for the inexpensive cap, no recessed cells.
    pp=deepcopy(detailed['points'][:(rows+1)*n]);ff=[]
    for j in range(rows):
        for k in range(n):ff.append([j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k])
    ff += [list(range(n-1,-1,-1)),list(range(rows*n,(rows+1)*n))]
    plain=mesh(pp,ff,'#AE9367',roundable=False,name='morel_simple')
    for key in ('matrix','position','rotation','scale'):
        if key in detailed:plain[key]=deepcopy(detailed[key])
    detailed['enabled']=Q('detail');plain['enabled']=choice('detail',{'false':True,'true':False});fs.append(plain)
    ident='l1.terrain.surface.dried';fs=PARTS[ident]['shape_params']['forms']
    # Simplified mode preserves the actual cracked relief but consolidates colour regions.
    for f in fs[1:]:
        f['color']=choice('detail',{'false':'#94734E','true':f.get('color','#94734E')})
    for ident in ['exp.terrain.cliff_outer','exp.terrain.cliff_straight']:
        f=PARTS[ident]['shape_params']['forms'][0]
        for p in f['points']:
            if abs(p[1]+.3)>1e-8:p[1]=mul(p[1],Q('relief'))
        palettes={'desert':('#B39764','#A98D68'),'snow':('#D3D8CE','#979D98'),'swamp':('#617956','#6D7461'),'mountain':('#858C80','#94998C'),'cave':('#5D6564','#7A7D78')}
        for face in f['faces']:
            if isinstance(face,dict) and 'color' in face:
                old=face['color'];green=old in ('#789554','#7E825C');face['color']=choice('surface',{'forest':old,**{k:v[0 if green else 1] for k,v in palettes.items()}})
    # Revised declared budgets: these are upper bounds, not measured FPS claims.
    budgets={'exp.nature.bamboo_culm':5000,'exp.nature.cactus_globe':6000,
             'exp.transport.utility_body':8500,'exp.nature.fern_rosette':11500,
             'exp.terrain.cliff_outer':1800,'exp.terrain.cliff_straight':1800,
             'exp.nature.willow_curtain':17000,'l1.nature.flower.pompom':12000}
    for ident,budget in budgets.items():
        PARTS[ident]['runtime']['triangle_budget']=budget
        PARTS[ident]['repair39']['triangle_budget_note']='Authored upper bound; verify_repair39 checks geometry against this bound in both styles and parameter endpoint states.'
    # Changes now reflect the complete, parameterised author output.
    for row in CHANGES:row['new_geometry_sha256']=digest(PARTS[row['id']]['shape_params'])
