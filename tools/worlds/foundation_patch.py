"""Limited seam registration of the verified Foundation source; no global smoothing."""
from foundation.common import *
def author():
 # Ring registration is evaluated AFTER all composition/parameter transforms.
 p=PARTS['core.human.upperarm']['shape_params']['forms'][2];p.update(join_end='elbow',cap=True,frame_axis=[0,-1,0])
 p=PARTS['core.human.forearm']['shape_params']['forms'][0];p.update(join_start='elbow',join_end='hand',frame_axis=[0,-1,0])
 p=PARTS['core.human.hand']['shape_params']['forms'][0];p.update(join_start='hand',frame_axis=[0,-1,0])
 p=PARTS['core.human.thigh']['shape_params']['forms'][0];p.update(join_end='knee',frame_axis=[0,-1,0])
 p=PARTS['core.human.shin']['shape_params']['forms'][0];p.update(join_start='knee',frame_axis=[0,-1,0])
 # Eliminate an overlapping sock shell. A ring colour region is one physical surface.
 fs=PARTS['core.animal.horse.foreleg']['shape_params']['forms'];base=fs[0];base['rings'][-1]['color']=C('cream');base['rings'].append({'c':[0,-1.052,.042],'r':[.055,.060],'bone':'knee','color':C('cream')});fs.pop(1)
 # Rounded shoulders are authored rather than inflated spheres. Increase just the
 # overlap envelope of sleeve/torso, without swallowing collar or shrinking limbs.
 sleeve=PARTS['core.human.upperarm']['shape_params']['forms'][0]
 sleeve['rings']=[{'c':[0,.044,0],'r':[.036,.045],'weights':{'chest':.65,'arm':.35}},{'c':[0,.007,0],'r':[.067,.073],'weights':{'chest':.25,'arm':.75}},{'c':[0,-.064,0],'r':[.083,.082],'bone':'arm'},{'c':[0,-.18,0],'r':[.077,.078],'bone':'arm'}]
 sleeve['frame_axis']=[0,-1,0]
 # Shorter cat tail and softer terminal profile; no needle-like final triangle.
 tail=PARTS['core.animal.cat.tail']['shape_params']['forms'][0]
 tail['rings'][-1]['r']=[.015,.015]
 for ident in ['core.human.body','core.animal.horse.foreleg']:
  PARTS[ident]['source']['revision']='1.9.1';PARTS[ident]['description']+=' | 1.9.1: registered continuous interfaces.'

 # Shared support dimensions expanded only where the geometric construction remains valid.
 props=PARTS['core.interior.cushion']['parameter_schema']['properties']
 props['width']['maximum']=1.65;props['depth']['maximum']=2.20;props['thickness']['minimum']=.045
 PARTS['core.props.plank']['parameter_schema']['properties']['thickness']['maximum']=.22

 # Visible tint is carried in the glass geometry too, for consistent CPU diagnostics.
 PARTS['core.arch.glass']['shape_params']['forms'][0]['color']=C('glass')
 # A clipped rectangle, not an eight-point lozenge: retain broad furniture planes.
 pad=PARTS['core.interior.cushion']['shape_params']['forms'][0]
 pad['outline']=[[1,.90],[.90,1],[-.90,1],[-1,.90],[-1,-.90],[-.90,-1],[.90,-1],[1,-.90]]
