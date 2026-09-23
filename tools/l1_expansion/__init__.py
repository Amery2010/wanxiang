"""L1-only expansion. No new registered assemblies or scenes."""
from . import common

def author():
    common.ADDED.clear()
    from . import architecture, nature, interior, terrain, industry, vehicle, character, creature, robot, gameplay, props
    for domain in (architecture, nature, interior, terrain, industry, vehicle, character, creature, robot, gameplay, props):
        domain.author()

    for ident in ('l1.industry.pipe.eccentric','l1.industry.pipe.hose_end','l1.industry.drive.bevel'):
        common.PARTS[ident]['source']['repair']='L2-3.2.0: preserve open bore; rebuild hollow indexed/profile shells'
    common.PARTS['l1.architecture.stair.spiral_tread']['source']['repair']='L2-3.2.0: annular tread sector preserves the shaft-sleeve bore'

    common.PARTS['l1.industry.drive.bearing']['source']['repair']='L2-3.2.0: pedestal web terminates below the bearing bore; no solid web through the shaft'
