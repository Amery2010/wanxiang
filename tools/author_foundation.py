"""Deterministic Foundation authoring entry; returns definitions, writes nothing."""
from foundation import common, humans, animals, environment, machines
from copy import deepcopy

def generate(include_l2=True, include_l34=True):
    common.PARTS.clear();common.ASSEMBLIES.clear();common.MOTIONS.clear()
    for module in (humans,animals,environment,machines):module.author()
    from worlds import foundation_patch, shared, nature, people, fauna, interiors, buildings, vehicles, industry, amenities, scenes
    for module in (foundation_patch,shared,nature,people,fauna,interiors,buildings,vehicles,industry,amenities,scenes):module.author()
    from frontiers import harbor, space, cyber, ecology, sites
    for module in (harbor,space,cyber,ecology,sites):module.author()
    from refinement import author as refine
    refine()
    from expansion import author as expand
    expand()
    from l1_expansion import author as expand_l1
    expand_l1()
    from l2_expansion import author as expand_l2
    if include_l2:expand_l2()
    if include_l2 and include_l34:
        from l34_expansion import author as expand_l34
        expand_l34()
    # A head is a functional subassembly, never a padded full-animal catalogue entry.
    common.ASSEMBLIES['world-turtle-head']['metadata']['level']=2
    materials={}
    roles={
        'mat.ceramic':(.30,0),'mat.matte':(.82,0),'mat.skin':(.88,0),'mat.hair':(.86,0),'mat.fabric':(.96,0),
        'mat.leather':(.73,0),'mat.wood':(.86,0),'mat.rubber':(.96,0),'mat.fur':(.94,0),
        'mat.hoof':(.75,0),'mat.leaf':(.91,0),'mat.stone':(.93,0),'mat.plaster':(.96,0),
        'mat.glass':(.16,0),'mat.water':(.38,0),'mat.paint':(.49,.12),'mat.metal':(.42,.72),
        'mat.panel_solar':(.25,.2),'mat.emissive.magenta':(.36,0),'mat.display':(.36,.08),'mat.vehicleGlass':(.30,.06),'mat.light':(.31,.04),'mat.tailLight':(.37,.02),
        'mat.emissive.cyan':(.34,0),'mat.emissive.amber':(.38,0)
    }
    for ident,(rough,metal) in roles.items():
        d={'schema':'wx.material/1.0','id':ident,'name':ident.replace('mat.',''),'version':'3.0.0','kind':'palette','displayColor':'#B6BDB7','baseColorFactor':[1,1,1,1],'roughnessFactor':rough,'metallicFactor':metal,'doubleSided':True,'alphaMode':'OPAQUE','channels':{},'extras':{'wxStyle':'lowpoly','material_role':ident},'source':{'type':'original_scalar_palette','license':'project-authored'}}
        if ident=='mat.glass':d.update(alphaMode='BLEND',baseColorFactor=[1,1,1,.40],doubleSided=True)
        if ident in ('mat.emissive.cyan','mat.emissive.amber','mat.emissive.magenta','mat.light','mat.tailLight'):
            d['emissiveFactor']={'mat.emissive.magenta':[.42,.035,.24],'mat.emissive.cyan':[.07,.55,.65],'mat.emissive.amber':[.8,.32,.04],'mat.light':[.3,.24,.12],'mat.tailLight':[.26,.018,.012]}[ident]
        materials[ident]=d
    for d in [*common.PARTS.values(),*common.ASSEMBLIES.values()]:d['version']='3.4.0'
    if include_l2 and include_l34:
        from repair37 import author as repair_current
        repair_current()
        from repair38 import author as repair_l4_current
        repair_l4_current()
        from repair39 import author as repair_advanced
        repair_advanced()
        from game410 import author as expand_game410
        expand_game410()
    return {'parts':deepcopy(common.PARTS),'assemblies':deepcopy(common.ASSEMBLIES),'motions':deepcopy(common.MOTIONS),'materials':materials}
if __name__=='__main__':
    import json
    print(json.dumps({k:len(v) for k,v in generate().items()}))
