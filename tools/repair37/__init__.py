"""Recoverable source corrections; never consumes a previous temporary snapshot."""
from . import common

def author():
    common.reset()
    from . import biology, vegetation, architecture, landscape, objects, interiors, industry, characters, heavy_vehicles, scenes
    for module in (biology,vegetation,architecture,landscape,objects,interiors,industry,characters,heavy_vehicles,scenes):module.author()
    common.retain_editable_groups()
    common.bound_private_instances()
    for ident,definition in common.ASSEMBLIES.items():
        if ident.startswith('l4-'):scenes.refresh_scene_membership(definition)
