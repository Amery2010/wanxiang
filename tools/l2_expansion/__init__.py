"""704 functional L2 assemblies; existing IDs remain stable."""
from . import common

def author():
    common.ADDED.clear();common.VALIDATED_BOUNDS.clear()
    from . import architecture,interior,nature,terrain,props,vehicle,industry,character,creature,robot,gameplay
    for domain in (architecture,interior,nature,terrain,props,vehicle,industry,character,creature,robot,gameplay):
        domain.author()
        common.finish(domain.__name__.rsplit('.',1)[1])
