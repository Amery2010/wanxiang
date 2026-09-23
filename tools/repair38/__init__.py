"""Reproducible L4 repairs derived from the v3.7.1 three-view manual ledger."""
from . import common

def author():
 common.start()
 from . import interiors,dungeons,facilities,civic,transport,landscapes,legacy
 for module in (interiors,dungeons,facilities,civic,transport,landscapes,legacy):module.author()
 from repair37.common import bound_private_instances
 from repair37.scenes import refresh_scene_membership
 bound_private_instances()
 # Explicit memberships also cover the two untouched legacy scenes, whose
 # editor previously inferred membership. Geometry stays unchanged.
 for ident in common.LEDGER:
  definition=common.ASSEMBLIES[ident];refresh_scene_membership(definition)
  scene=definition['metadata']['scene']
  for obj in scene['objects'].values():
   scene.setdefault('layers',{}).setdefault(obj['layer'],{'label':obj['layer'],'visible':True})
   scene.setdefault('regions',{}).setdefault(obj['region'],{'label':obj['region']})
 expected={i for i,note in common.LEDGER.items() if note['priority']!='PASS'}
 actual={c['id'] for c in common.CHANGES}
 if expected!=actual:raise ValueError('L4 authored repair coverage mismatch: '+str(expected^actual))
