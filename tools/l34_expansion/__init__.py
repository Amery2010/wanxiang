"""L3 complete assets and L4 editable scenes: retained original author source."""
from . import common

def author():
    common.reset()
    from . import architecture, interior, nature, terrain, props, vehicle, industry, character, creature, robot, gameplay
    for module in (architecture, interior, nature, terrain, props, vehicle, industry, character, creature, robot, gameplay):
        module.author();common.finish(module.__name__.rsplit('.',1)[1])
    from . import refinements,scenes
    refinements.author()
    scenes.author()
