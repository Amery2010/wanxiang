"""One explicit handedness migration found in actual consumer-view inspection."""
from .common import *
def author():
    a=ASSEMBLIES['exp-creature-flight_rig']
    left=next(n for n in a['instances'] if n['id']=='wingL')
    assert left['part']=='exp.creature.feather_wing' and left['rotation']==[0,0,180]
    left.setdefault('params',{})['mount_inverted']=True
    a['version']=REV
    a['metadata']['repair39']={'source_revision':REV,'change':'保留旧左翼节点、180度基姿和控制轴，启用局部翻面补偿，修复新覆羽一侧朝下的装配回归。','public_nodes_and_controls_retained':True}
    a['metadata']['source']={'authoring':'tools/repair39/integration.py','revision':REV,'type':'authored_handedness_migration','license':'project-authored'}
