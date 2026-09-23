"""Advanced Lowpoly source repairs based on the 166-item v3.8 audit."""
from . import common

def author():
    import os,sys
    common.start()
    from . import architecture,characters,creatures,mechanical,interior,nature,props,terrain_robot,vehicles,parameters,integration
    for module in (architecture,characters,creatures,mechanical,interior,nature,props,terrain_robot,vehicles,parameters,integration):
        if os.environ.get('WX_REPAIR_TRACE'):print('repair39:',module.__name__,file=sys.stderr,flush=True)
        module.author()
    common.finish()
