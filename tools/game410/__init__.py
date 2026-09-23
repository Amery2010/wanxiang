"""Additive authors; never mutate a v3.9 asset definition."""
def author():
    from . import common,dungeon,traversal,survival,farming,scifi,automation,creature,equipment,waterland,puzzle,examples
    common.ADDED.clear();common.DEMOS.clear()
    for module in (dungeon,traversal,survival,farming,scifi,automation,creature,equipment,waterland,puzzle):
        before=len(common.ADDED);module.author()
        if len(common.ADDED)-before != 12:raise ValueError(module.__name__+' must author 12 distinct profiles')
    examples.author()
    if len(common.ADDED)!=120 or len(common.DEMOS)!=10:raise ValueError('Game expansion inventory mismatch')
