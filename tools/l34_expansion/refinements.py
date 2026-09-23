"""Purpose-specific corrections from colour/scale-independent geometry review.

These corrections run after domain authors and before scene composition. They
are source, not edits to generated library files. No artificial seed variants.
"""
from .common import *

def change(id,extra=(),remove=(),replace=None,note=''):
    d=ASSEMBLIES['l3-'+id]
    d['instances']=list(replace) if replace is not None else [i for i in d['instances'] if i['id'] not in remove]
    d['instances']+=list(extra)
    if len({i['id'] for i in d['instances']})!=len(d['instances']):raise ValueError('Duplicate refined node '+id)
    d['metadata']['source']['refinements']='tools/l34_expansion/refinements.py'
    d['metadata']['production']['features'].append(note)
    d['metadata']['production']['notes'].append('Colour/scale independent mesh-identity review: '+note)
    DESIGNS[d['id']]['features']=d['metadata']['production']['features']
    has_detail=any('enabled' in i or i.get('params',{}).get('detail')==Q('detail') for i in d['instances'])
    if not has_detail:
        d['metadata'].get('parameter_schema',{}).get('properties',{}).pop('detail',None)
        d['metadata'].get('parameters',{}).pop('detail',None)
        d['metadata']['runtime']['lod']={'levels':[]}



def author():
    change('architecture-shelter-garden_gate',[
        fit('garden_leaf0',l1('architecture','railing','picket'),[1.1,1.35,.09],[-.57,0,0]),
        fit('garden_leaf1',l1('architecture','railing','lattice'),[1.1,1.35,.09],[.57,0,0]),
        fit('gate_latch',l1('props','handle','ring_pull'),[.15,.15,.06],[.1,.8,.09])],note='Double gate leaves and physical latch; torii remains an open ceremonial frame')
    change('interior-kitchen-bakery',[
        block('kneading_board',[.8,.035,.55],[0,.96,.02],color='#B99A6E'),
        fit('mixing_bowl',l1('props','vessel','bowl'),[.32,.22,.32],[.39,.97,.03]),
        fit('flour_bin',l1('props','container','can_body'),[.28,.4,.3],[-.8,0,0]),
        fit('rolling_pin',l1('industry','drive','keyshaft'),[.06,.55,.06],[-.1,1.04,0],[0,0,90],anchor='center',color='#BB9767')],note='Kneading board, rolling pin, mixing bowl and floor flour bin')
    change('interior-kitchen-dishwash',[
        fit('dish_rack',l1('interior','shelf','wire'),[.45,.25,.5],[.42,.97,0]),
        block('splash_guard',[1.35,.4,.045],[0,.98,-.36]),
        *[fit('plate'+str(i),l1('props','vessel','tea_bowl'),[.22,.035,.22],[.4,1.03+i*.05,0]) for i in range(4)]],note='Drain rack, splash guard and independently stacked dishes')
    change('interior-service-podium',replace=[block('centre',[.8,.6,.65]),block('second',[.7,.4,.65],[-.75,0,0]),block('third',[.7,.25,.65],[.75,0,0]),block('backstep',[2.2,.1,.35],[0,0,-.5])],note='Three-height awards podium with access step, not a service altar')
    olive=[]
    for i in range(7):
        a=i*math.tau/7;olive.append(fit('olive'+str(i),l1('nature','fruit','drupe'),[.16,.22,.16],[1.2*math.sin(a),2.2+(i%2)*.35,1.2*math.cos(a)]))
    change('nature-tree-olive',olive,note='Distinct drupes and a branched fruiting silhouette')
    lily=[]
    for i in range(5):
        x=(i%3-1)*.35;z=(i//3-.5)*.45
        lily += [fit('pad'+str(i),l1('nature','leaf','lotus'),[.48,.48,.018],[x,.02,z],[-90,i*47,0],anchor='center'),fit('bloom'+str(i),l2('nature','inflorescence','cup'),[.22,.15,.22],[x,.025,z])]
    change('nature-crop-waterlily',replace=lily,note='Waterline pads and low flowers replace tall lotus-stem arrangement')
    change('terrain-cave-mine',[
        *[block('pitprop'+str(i),[.22,2.5,.22],[x,0,z],color='#977B59') for i,(x,z) in enumerate([(-1.35,-.8),(1.35,-.8),(-1.35,.8),(1.35,.8)])],
        block('lintel0',[3,.22,.22],[0,2.4,-.8],color='#977B59'),block('lintel1',[3,.22,.22],[0,2.4,.8],color='#977B59')],note='Paired timber mine supports and crossbeams')
    change('props-container-medical',[
        block('medical_cross_h',[.3,.065,.02],[0,.49,.358],color='#E3DCCA'),block('medical_cross_v',[.065,.3,.02],[0,.375,.361],color='#E3DCCA'),
        fit('carry_grip',l1('props','handle','u_pull'),[.3,.15,.05],[0,.65,0]),
        fit('bandage',l1('props','medical','bandage_roll'),[.2,.13,.2],[.2,.07,.1])],note='Physical rescue insignia, carrying grip and bandage compartment')
    change('props-container-recycle',replace=[block('base',[.9,.06,.6]),*[fit('bin'+str(i),l1('props','container','can_body'),[.4,.62,.55],[(i-.5)*.45,.06,0]) for i in range(2)],block('divider',[.025,.8,.58],[0,.05,0]),block('signpost',[.55,.18,.035],[0,.8,-.26])],note='Two open sorting receptacles with divider and identification stand')
    change('props-container-oil',extra=[fit('filler',l1('industry','pipe','socket'),[.13,.15,.13],[.22,.65,-.12]),fit('drain',l1('industry','valve','ball'),[.17,.12,.22],[0,.15,.35])],note='Filler neck and low drain valve')
    harp=[block('foot',[.75,.08,.35]),beam('pillar',[-.32,.08,0],[-.23,1.4,0],.075,color='#B59159'),beam('soundbox',[.25,.1,0],[.32,1.12,0],.13,color='#9E7A4E'),beam('neck',[-.23,1.4,0],[.32,1.12,0],.08,color='#B59159')]
    for i in range(9):
        x=-.18+i*.055;harp.append(beam('string'+str(i),[x,.16,0],[x,1.4-(x+.23)*.28/.55,0],.006,color='#D7CAA9'))
    change('props-instrument-harp',replace=harp,note='Triangular frame, tapered soundbox and nine spanning strings; no lute body')
    change('vehicle-road-delivery',extra=[block('loading_step',[1.5,.15,.55],[0,.35,-2.9]),fit('roller_shutter',l1('architecture','railing','picket'),[1.45,1.15,.04],[0,.94,-2.85],[0,0,90]),block('parcel_shelf',[1.2,.07,1.2],[0,1.05,-.85])],note='Rear loading step, shutter and internal parcel shelf')
    change('vehicle-rail-tram',extra=[block('boarding_step',[.35,.18,1.25],[1.23,.2,.7]),fit('cab_nose',l1('vehicle','body','hood'),[2.2,.9,.7],[0,.72,3.05]),block('route_display',[1.2,.28,.055],[0,2.65,3.05])],note='Street-running cab nose, low boarding step and destination box')
    change('vehicle-utility-forklift',remove=('boom','attachment'),extra=[
        *[block('mast'+str(i),[.14,2.6,.15],[s*.57,0,1.7],color='#5E6D70') for i,s in enumerate((-1,1))],block('carriage',[1.3,.38,.16],[0,.45,1.78]),
        *[block('fork'+str(i),[.16,.10,1.55],[s*.44,.15,2.4]) for i,s in enumerate((-1,1))],block('overhead_guard',[1.6,.1,1.6],[0,2.1,-.3])],note='Upright lift mast, low horizontal fork tines, carriage and overhead guard')
    change('vehicle-marine-kayak',remove=('motor',),extra=[fit('cockpit_rim',l1('vehicle','marine','rib'),[.68,.16,.8],[0,.66,-.25],[90,0,0]),fit('paddle',l1('vehicle','marine','oar_blade'),[.16,.045,2.7],[0,.78,.45],[0,90,0])],note='Unpowered deck kayak with cockpit rim and transverse paddle')
    change('vehicle-marine-patrol',extra=[fit('radar','w.outpost.dish',[.65,.4,.2],[0,2.7,0]),fit('beacon',l1('props','lamp','dome_shade'),[.25,.18,.25],[.3,1.53,0]),block('aft_bench',[1,.12,.38],[0,.87,-1.2])],note='Navigation radar, roof beacon and aft observation bench')
    change('vehicle-air-gyrocopter',extra=[fit('pusher_prop',l2('vehicle','flightmodule','prop_blade'),[1.25,.16,1.25],[0,1,-1.75],[90,0,0]),beam('mast_brace0',[-.4,.75,0],[0,1.8,0],.04),beam('mast_brace1',[.4,.75,0],[0,1.8,0],.04),fit('open_seat',l1('interior','seat','bucket'),[.42,.4,.5],[0,1,.6])],note='Pusher propeller and braced rotor mast separate gyroplane from powered-helicopter layout')
    change('industry-machine-bender',extra=[block('bed_die',[1.35,.2,.18],[0,1.08,.33]),block('bending_ram',[1.4,.35,.12],[0,1.5,.33]),*[block('guide'+str(i),[.12,.9,.18],[s*.7,.9,.33]) for i,s in enumerate((-1,1))]],note='Full-width bending die, ram and guide columns')
    change('industry-machine-punch',extra=[fit('punch_tool',l1('props','toolhead','awl'),[.12,.35,.12],[.2,1.18,.35]),fit('die_socket',l1('industry','pipe','socket'),[.25,.1,.25],[.2,1.08,.35]),block('ejection_chute',[.5,.07,.65],[.8,.85,.4],rot=[0,0,18])],note='Concentrated punch tool and die with ejection chute')
    change('industry-machine-saw',extra=[fit('cutting_blade',l1('industry','drive','spur'),[.45,.035,.45],[.25,1.12,.18],[90,0,0],anchor='center'),block('rip_fence',[.08,.2,.7],[-.25,1.1,.1]),fit('guard',l1('interior','case','display'),[.14,.25,.5],[.25,1.17,.18])],note='Toothed cutting disc above table, fence and transparent blade guard')
    # Working-dog equipment remains bone-local and moves with the retained rig.
    change('creature-mammal-sled_dog',remove=('bag0','bag1'),extra=[beam('towbar',[-.3,-.05,-.4],[.3,-.05,-.4],.04,parent='skin.rig.body'),fit('tow_ring',l1('props','handle','ring_pull'),[.15,.15,.055],[0,-.07,-.47],parent='skin.rig.body',anchor='center')],note='Towing harness and rear ring instead of cargo panniers')
    change('creature-mammal-messenger_dog',remove=('bag1',),extra=[fit('message_tube',l1('props','container','tube_body'),[.13,.35,.13],[-.3,.02,-.05],[0,0,90],parent='skin.rig.body',anchor='center')],note='Single dispatch pannier and rigid message tube')
    change('creature-bird-raven',extra=[fit('tail_feather'+str(i),l1('creature','wing','primary_feather'),[.14,.035,.6],[(i-2)*.07,.53,-.62],[0,(i-2)*8,0]) for i in range(5)],note='Five-feather extended tail fan')
    change('creature-bird-penguin',replace=[fit('torso','exp.creature.avian_torso',[.5,.95,.45],[0,.08,0]),fit('head','exp.creature.raptor_head',[.27,.29,.3],[0,.94,.05]),*[fit('foot'+str(i),l1('creature','foot','webbed'),[.19,.08,.25],[s*.16,0,.12]) for i,s in enumerate((-1,1))],*[fit('flipper'+str(i),'exp.creature.feather_wing',[.13,.52,.22],[s*.3,.4,0],[0,0,s*18]) for i,s in enumerate((-1,1))]],note='Upright body, short webbed feet and narrow hanging flippers')
    # Visual review: complete sitting support, recognisable bird anatomy, and
    # a mechanically connected airframe rather than floating placeholder forks.
    sofa=[*legs(1.46,.65,.13,.09,style='tapered'),block('seat_frame',[1.72,.22,.81],[0,.13,0],color='#708879'),
        fit('back',l1('interior','soft','box_cushion'),[1.62,.57,.22],[0,.32,-.32],color='#899C87')]
    for i,x in enumerate((-.42,.42)):
        sofa.append(fit('seat_cushion'+str(i),l1('interior','soft','piped'),[.79,.20,.63],[x,.35,.04],color='#A8B8A1'))
    for i,x in enumerate((-.86,.86)):
        sofa.append(fit('armrest'+str(i),l1('interior','soft','box_cushion'),[.18,.48,.81],[x,.22,0],color='#899C87'))
    change('interior-seat-sofa',replace=sofa,note='Low support frame, two seat cushions, full back and padded side arms')
    penguin=[fit('torso','exp.creature.avian_torso',[.50,.93,.45],[0,.08,0],color='#25323B'),
        fit('white_bib','exp.creature.avian_torso',[.34,.70,.24],[0,.17,.155],color='#E6E6D7'),
        fit('head','exp.creature.raptor_head',[.28,.29,.30],[0,.93,.035],color='#25323B'),
        fit('short_bill',l1('creature','mouth','beak_filter'),[.095,.055,.14],[0,1.005,.20],color='#C9A053')]
    for i,side in enumerate((-1,1)):
        penguin.append(fit('foot'+str(i),l1('creature','foot','webbed'),[.19,.08,.25],[side*.16,0,.12],color='#B89557'))
        penguin.append(fit('flipper'+str(i),'exp.creature.feather_wing',[.13,.49,.20],[side*.29,.35,0],[0,0,side*18],color='#25323B'))
    change('creature-bird-penguin',replace=penguin,note='Dark upright torso, distinct pale belly, short bill and grounded webbed feet')
    lighthouse=[fit('shaft',l1('architecture','column','tapered'),[2.1,7.2,2.1],color='#D7D8C9'),
        block('foundation',[2.65,.22,2.65],color='#929B91'),block('gallery',[3.0,.18,3.0],[0,7.2,0],color='#6C7D82'),
        fit('lantern_lens',l1('props','lamp','bulb'),[.55,.74,.55],[0,7.47,0],material='mat.light'),
        fit('lantern_cap',l1('architecture','roof','conical'),[2.4,.7,2.4],[0,8.32,0],color='#7F5E48')]
    for i,(x,z) in enumerate([(-.8,-.8),(.8,-.8),(-.8,.8),(.8,.8)]):
        lighthouse.append(block('lantern_post'+str(i),[.08,.97,.08],[x,7.38,z],color='#647781'))
    for i in range(4):
        a=i*math.pi/2;x,z=.80*math.sin(a),.80*math.cos(a)
        lighthouse.append(block('lantern_glass'+str(i),[1.6,.86,.025],[x,7.44,z],rot=[0,i*90,0],material='mat.glass',color='#AEC8CF'))
        a1=i*math.pi/2+math.pi/4;a2=(i+1)*math.pi/2+math.pi/4
        x1,z1=1.82*math.sin(a1),1.82*math.cos(a1);x2,z2=1.82*math.sin(a2),1.82*math.cos(a2)
        lighthouse.append(block('rail_post'+str(i),[.05,.60,.05],[x1,7.38,z1],color='#647781'))
        lighthouse.append(beam('gallery_rail'+str(i),[x1,7.96,z1],[x2,7.96,z2],.045))
    change('architecture-tower-lighthouse',replace=lighthouse,note='Illuminant lens, glass lantern, conical roof, gallery rails and a ground footing')
    gyro=[block('keel',[.14,.14,2.6],[0,.41,0],color='#536773'),
        fit('cockpit',l1('vehicle','aero','nacelle'),[.86,.66,1.55],[0,.52,.4],color='#B7BBAE'),
        fit('open_seat',l1('interior','seat','bucket'),[.40,.41,.47],[0,.79,.1]),
        beam('mast',[0,.46,-.36],[0,2.0,-.36],.10),
        beam('brace0',[-.42,.48,0],[0,1.75,-.36],.06),beam('brace1',[.42,.48,0],[0,1.75,-.36],.06),
        fit('mainrotor',l2('vehicle','flightmodule','rotor_blade'),[3.8,.14,3.8],[0,1.98,-.36]),
        fit('pusher_prop',l2('vehicle','flightmodule','prop_blade'),[1.2,.12,1.2],[0,1.06,-1.02],[90,0,0],anchor='center'),
        beam('tail_boom',[0,.48,-.8],[0,.55,-2.0],.095),
        fit('tailfin',l1('vehicle','aero','fin'),[.055,.71,.65],[0,.55,-1.98]),
        block('tailplane',[1.1,.045,.33],[0,.61,-1.84],color='#7B9298')]
    for i,side in enumerate((-1,1)):
        gyro.append(beam('gear_strut'+str(i),[0,.45,-.1],[side*.63,.19,-.1],.075))
        gyro.append(fit('wheel'+str(i),l1('vehicle','wheel','road_tire'),[.38,.12,.38],[side*.63,.19,-.1],[0,0,90],anchor='center'))
    gyro.append(beam('nose_strut',[0,.45,.75],[0,.15,1.03],.055))
    gyro.append(fit('nose_wheel',l1('vehicle','wheel','road_tire'),[.30,.10,.30],[0,.15,1.03],[0,0,90],anchor='center'))
    change('vehicle-air-gyrocopter',replace=gyro,note='Continuous keel, mast, pusher drive, tail boom and attached tricycle landing gear')
    # Added nested rigid propeller controls are discovered like all other modules.
    for id in ['l3-vehicle-air-gyrocopter','l3-interior-seat-sofa','l3-architecture-tower-lighthouse','l3-creature-bird-penguin']:
        d=ASSEMBLIES[id];d['metadata']['state_controls']=inherited_controls(d['instances'])

    for ident,size in {'l3-interior-seat-sofa':[1.98,.95,.81],'l3-architecture-tower-lighthouse':[3.0,9.02,3.0],'l3-creature-bird-penguin':[.76,1.23,.60],'l3-vehicle-air-gyrocopter':[3.8,2.3,4.0]}.items():
        p=ASSEMBLIES[ident]['metadata']['production'];p['dimensions_design_m']=size;p['footprint_m']=[size[0],size[2]];DESIGNS[ident]['size']=size

    # Retain the raven's distinct tail topology; correct the inherited eagle
    # palette without counting a new colour variant as another asset.
    raven=ASSEMBLIES['l3-creature-bird-raven']
    for node in raven['instances']:
        ref=node.get('part')
        if ref in PARTS:
            node.setdefault('params',{}).setdefault('palette',{}).update(colormap(ref,'#2E3A43' if node['id'].startswith(('head','wing','torso','tail')) else '#41494A'))
