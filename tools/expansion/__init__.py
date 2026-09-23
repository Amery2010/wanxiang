"""A-F authored expansion entry; deterministic and free of file writes."""
from . import common,terrain,roads,biomes,scenes

def author():
    common.NEW_PARTS.clear();common.NEW_ASSEMBLIES.clear()
    for m in (terrain,roads,biomes,scenes):m.author()
    assert len(common.NEW_PARTS)==62, len(common.NEW_PARTS)
    assert len(common.NEW_ASSEMBLIES)==48, len(common.NEW_ASSEMBLIES)

    from . import production, architecture, interiors, industry, transport, characters, creatures, gameplay, robotics, production_scenes
    production.D_PARTS.clear();production.D_ASSEMBLIES.clear()
    for m in (architecture,interiors,industry,transport,characters,creatures,gameplay,robotics,production_scenes):m.author()
    assert len(production.D_PARTS)==168
    assert len(production.D_ASSEMBLIES)==154
    assert len(common.NEW_PARTS)==230
    assert len(common.NEW_ASSEMBLIES)==202
