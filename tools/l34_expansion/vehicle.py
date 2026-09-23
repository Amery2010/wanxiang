"""64 complete vehicle silhouettes with grounded running gear and attachments."""
from .common import *

def wheels(w,d,r=.3,axles=2,tire='road_tire'):
    items=[]
    for j in range(axles):
        z=(j/max(1,axles-1)-.5)*d
        for i,s in enumerate((-1,1)):
            items.append(fit(f'wheel{j}_{i}',l2('vehicle','wheelhub',tire),[r*2,.23,r*2],[s*w/2,r,z],[0,0,90],anchor='center'))
        items.append(beam('axle'+str(j),[-w/2,r,z],[w/2,r,z],.08))
    return items

def chassis(key,mode,axles=2):
    w=1.75;length=4 if mode in ('small','pickup','open') else 6.4
    items=wheels(w,length*.68,.34,axles)
    items.append(block('chassis',[w-.28,.24,length],[0,.48,0],color='#43535A'))
    items.append(fit('front_bumper',l1('vehicle','body','bumper'),[w,.24,.2],[0,.5,length/2]))
    for i,s in enumerate((-1,1)):
        items.append(fit('headlamp'+str(i),l1('props','lamp','diffuser'),[.28,.18,.08],[s*.57,.84,length/2+.05],material='mat.light'))
    return items,w,length

def author():
    road=[('sedan','三厢轿车','small',2,'boot'),('hatch','掀背车','small',2,'hatch'),('estate','旅行车','small',2,'estate'),('coupe','双门跑车','small',2,'coupe'),('convertible','敞篷车','open',2,'open'),('pickup','皮卡','pickup',2,'bed'),('van','厢式货车','box',2,'van'),('minibus','小型客车','bus',2,'minibus'),('city_bus','城市公交车','bus',3,'city'),('coach','长途客车','bus',3,'coach'),('delivery','厢式配送车','box',2,'box'),('refrigerated','冷藏运输车','box',2,'refrigeration'),('refuse','压缩垃圾车','box',3,'hopper'),('fire_engine','消防车','box',3,'ladder'),('ambulance','急救车','box',2,'medical'),('tanker','罐式运输车','box',3,'tank'),('flatbed','平板货车','box',3,'flatbed'),('tractor_unit','半挂牵引车','box',3,'coupling'),('motorcycle','摩托车','cycle',2,'motor'),('bicycle','城市自行车','cycle',2,'pedal')]
    for key,name,mode,n,load in road:
        if mode=='cycle':
            items=[];r=.34;d=1.6
            for i,z in enumerate((-d/2,d/2)):items.append(fit('wheel'+str(i),l1('vehicle','wheel','spoke_hub'),[r*2,.065,r*2],[0,r,z],[0,0,90],anchor='center'))
            for i,(a,b) in enumerate([([0,.34,-.8],[0,.75,-.15]),([0,.75,-.15],[0,.38,.12]),([0,.38,.12],[0,.34,-.8]),([0,.75,-.15],[0,.86,.55]),([0,.86,.55],[0,.38,.12]),([0,.86,.55],[0,.34,.8])]):items.append(beam('frame'+str(i),a,b,.055))
            items += [fit('seat',l1('interior','seat','saddle'),[.23,.06,.32],[0,.8,-.12]),fit('handle',l1('props','handle','t_bar'),[.55,.15,.07],[0,.93,.55])]
            if load=='motor':items.append(fit('engine',l1('robot','housing','servo'),[.34,.35,.45],[0,.35,0]))
            else:items.append(fit('crank',l1('industry','drive','crank'),[.25,.2,.05],[0,.38,.12],[0,0,90]))
            register('vehicle','road',key,name,items,[.6,1.15,2.3],['轮组','三角承力车架',load]);continue
        items,w,d=chassis(key,mode,n)
        if mode in ('small','pickup','open'):
            items.append(block('lower_body',[w,.38,d-.15],[0,.66,0],color='#719095'))
            items.append(fit('hood',l1('vehicle','body','hood'),[w-.1,.23,1.15],[0,.97,d*.3]))
            cabinlen=1.15 if load in ('coupe','bed') else 2.0 if load=='estate' else 1.65
            items += [block('cabin_back',[w-.28,.68,.08],[0,1.0,-cabinlen/2],color='#789293'),block('windscreen',[w-.28,.58,.05],[0,1.08,cabinlen/2],[14,0,0],color='#ABC6CD',material='mat.vehicleGlass')]
            for i,s in enumerate((-1,1)):
                items.append(fit('door'+str(i),l1('vehicle','body','door'),[.075,.7,cabinlen],[s*(w/2-.09),.95,0]))
            if load!='open':items.append(fit('roof',l1('vehicle','body','roof'),[w-.2,.12,cabinlen+.1],[0,1.67,0]))
            else:items.append(fit('seat',l1('vehicle','body','seat_frame'),[1.2,.4,.7],[0,1.0,0]))
            if load=='bed':items.append(fit('loadbed',l1('interior','drawer','box'),[w-.05,.55,1.5],[0,.9,-1.18]))
            elif load=='boot':items.append(block('boot',[w-.1,.25,.7],[0,.95,-1.5]))
            elif load=='hatch':items.append(fit('rear',l1('vehicle','body','grille'),[w-.15,.5,.08],[0,.93,-d/2]))
        else:
            # Independent cab, windshield, upper module and its load-specific node tree.
            items += [block('cab',[w,.9,1.45],[0,.8,d/2-.73],color='#8EACA8'),block('glass',[w-.16,.5,.05],[0,1.27,d/2+.03],material='mat.vehicleGlass',color='#A9C4CE'),fit('cabroof',l1('vehicle','body','roof'),[w+.08,.12,1.55],[0,1.7,d/2-.73])]
            rearz=-.75;loadlen=d-1.7
            if mode=='bus':
                items.append(block('saloon',[w,1.35,loadlen],[0,.85,rearz],color='#A9BBAB'))
                count=5 if load=='city' else 4 if load=='coach' else 3
                for i in range(count):
                    z=-(d/2)+.4+i*(loadlen-.5)/max(1,count-1)
                    for s in (-1,1):items.append(block(f'window{i}_{s}',[.03,.7,.65],[s*(w/2+.015),1.4,z],color='#9AC1CD',material='mat.vehicleGlass'))
                items.append(fit('rear_door',l1('vehicle','body','door'),[.8,1.15,.045],[0,.88,-d/2-.04]))
            elif load=='tank':items.append(fit('tank',l1('props','vessel','carboy'),[w,loadlen,w],[0,.85,rearz],[90,0,0],anchor='center'))
            elif load=='ladder':
                items.append(block('equipment',[w,.75,loadlen],[0,.8,rearz],color='#B96553'))
                items.append(fit('ladder',l1('architecture','railing','lattice'),[loadlen,.22,.6],[0,1.65,rearz],[0,90,0]))
            elif load=='hopper':items.append(fit('compactor',l1('industry','process','hopper'),[w,1.3,loadlen],[0,.85,rearz]))
            elif load=='coupling':items.append(fit('fifth_wheel',l1('industry','drive','coupling'),[1.2,.28,1.2],[0,.85,-1.2]))
            elif load=='flatbed':items.append(block('bed',[w+.15,.12,loadlen],[0,.85,rearz]))
            else:
                items.append(fit('cargo_box',l1('interior','case','open_front'),[w,1.45,loadlen],[0,.85,rearz],[0,180,0]))
                items.append(block('cargo_door',[w-.08,1.38,.045],[0,.9,-d/2-.03],color='#BDC5C0'))
                if load=='refrigeration':items.append(fit('cooler',l1('industry','power','fan_guard'),[.7,.5,.3],[0,1.8,1.25]))
                if load=='medical':items.append(fit('beacon',l1('props','lamp','dome_shade'),[.7,.15,.25],[0,1.85,d/2-.7],material='mat.emissive.cyan'))
        register('vehicle','road',key,name,items,[w+.35,2.45,d+.3],['独立底盘','接地车轮','驾驶区',load],notes=['刚性演示轮组；未实现动力学或驾驶控制器'])
    rail=[('locomotive','内燃机车','locomotive_body',2),('electric','电力机车','locomotive_body',3),('passenger','客运车厢','passenger_body',2),('metro','地铁车厢','passenger_body',3),('freight','敞顶货车','freight_body',2),('tank','铁路罐车','freight_body',3),('flat','铁路平车','freight_body',4),('tram','有轨电车','passenger_body',4)]
    for key,name,body,n in rail:
        d=6;items=[fit('underframe',l1('vehicle','chassis','ladder_rail'),[2,.35,d],[0,.4,0])]
        for i,z in enumerate([-2,2]):items.append(fit('bogie'+str(i),l2('vehicle','railunit','bolster'),[2,.55,1.1],[0,0,z]))
        if key=='tank':items.append(fit('tank',l1('props','vessel','carboy'),[1.6,4.8,1.6],[0,1.4,0],[90,0,0],anchor='center'))
        elif key!='flat':items.append(fit('body','exp.transport.'+body,[2.2,2.5,6],[0,.7,0]))
        else:items.append(block('deck',[2.4,.18,6],[0,.8,0]))
        for i,s in enumerate((-1,1)):items.append(fit('coupler'+str(i),l1('vehicle','rail','coupler'),[.3,.22,.5],[0,.65,s*3.25],[0,180*i,0]))
        if key in ('electric','tram','metro'):items.append(fit('collector',l1('vehicle','rail','pantograph_arm'),[1.2,.65,1.3],[0,3.15,0]))
        if key=='locomotive':items.append(fit('stack',l1('industry','pipe','socket'),[.4,.4,.4],[0,3.1,1.5]))
        if key=='freight':items.append(fit('load',l1('terrain','surface','scree'),[1.8,.65,5],[0,2,0],optional=True))
        register('vehicle','rail',key,name,items,[2.5,3.9,7],['车体','双转向架','端部车钩',key])
    utility=[('tractor','农用拖拉机','rack'),('harvester','联合收割机','impeller'),('loader','轮式装载机','hopper'),('excavator','挖掘机','fork_beam'),('bulldozer','推土机','blade'),('roller','压路机','roller'),('forklift','叉车','rack'),('telehandler','伸缩臂装卸车','telescopic'),('crane','起重车','lattice'),('sweeper','道路清扫车','brush'),('snowplow','铲雪车','shovel'),('paver','摊铺机','chute')]
    for j,(key,name,tool) in enumerate(utility):
        items,w,d=chassis(key,'small',2)
        items.extend([block('cab',[1.3,1.2,1.3],[0,.75,-.35],color='#D0A156'),block('windscreen',[1.18,.7,.04],[0,1.17,.32],material='mat.vehicleGlass'),fit('counterweight',l1('vehicle','body','hood'),[1.6,.65,1.1],[0,.76,-1.4])])
        ref={'rack':l1('industry','drive','rack'),'impeller':l1('industry','process','impeller'),'hopper':l1('industry','process','hopper'),'fork_beam':l1('robot','link','fork_beam'),'blade':l1('gameplay','trap','blade'),'roller':l1('industry','conveyor','roller'),'telescopic':l1('robot','link','telescopic'),'lattice':l1('robot','link','lattice'),'brush':l1('props','toolhead','brush'),'shovel':l1('props','toolhead','shovel'),'chute':l1('industry','conveyor','chute')}[tool]
        items += [beam('boom',[0,1.25,.25],[0,1.05,2.1],.2),fit('attachment',ref,[1.5,.85,.7],[0,.45,2.15])]
        if key in ('excavator','crane','telehandler'):items.append(fit('upperboom',l1('robot','link','telescopic'),[.25,1.8,.25],[0,1.15,.65],[35,0,0]))
        if key=='harvester':items.append(fit('crophead',l1('industry','conveyor','belt_cleat'),[2.6,.5,.8],[0,.25,2.1]))
        register('vehicle','utility',key,name,items,[2.8,3.3,5],['底盘驾驶舱','工具臂','作业端',tool,key])
    boats=[('rowboat','划艇',1,'oar'),('canoe','独木舟',0,'paddle'),('kayak','皮划艇',0,'deck'),('dinghy','充气艇',0,'outboard'),('sailboat','小帆船',1,'sail'),('yacht','游艇',2,'cabin'),('fishing','渔船',2,'net'),('tug','拖船',2,'winch'),('barge','驳船',1,'cargo'),('ferry','摆渡船',3,'passenger'),('patrol','巡逻艇',2,'antenna'),('research','海洋调查船',3,'crane')]
    for key,name,n,feature in boats:
        w=1.65;d=4.2;items=[fit('hull',l1('vehicle','marine','bow'),[w,.8,d]),fit('deck',l1('vehicle','body','cargo_floor'),[w*.87,.08,d*.8],[0,.65,0])]
        for i in range(n):items.append(fit('rib'+str(i),l1('vehicle','marine','rib'),[w*.85,.45,.12],[0,.2,(i-(n-1)/2)*.7]))
        if feature in ('cabin','net','winch','passenger','antenna','crane'):items += [block('cabin',[1.1,.8,1.4],[0,.73,-.15],color='#E0D7BE'),block('window',[1,.38,.03],[0,1.05,.57],material='mat.vehicleGlass')]
        if feature in ('sail','antenna','net'):items.append(block('mast',[.07,2.8,.07],[0,.73,0]))
        if feature=='sail':items.append(fit('sail',l1('props','sign','pennant'),[1.5,2,.04],[.4,1.4,0]))
        elif feature=='crane':items.append(fit('crane',l1('robot','link','lattice'),[.3,1.8,.3],[.6,.75,-1.3],[0,0,-30]))
        elif feature=='winch':items.append(fit('winch',l2('industry','driveunit','pulley_v'),[.6,.5,.6],[0,.73,-1.3]))
        elif feature in ('paddle','oar'):items.extend([fit('oar'+str(i),l1('vehicle','marine','oar_blade'),[.18,.07,1.7],[s*.85,.65,0],[0,s*35,0]) for i,s in enumerate((-1,1))])
        elif feature in ('outboard','deck'):items.append(fit('motor',l1('vehicle','aero','nacelle'),[.4,.5,.6],[0,.5,-d/2]))
        elif feature=='cargo':items.append(fit('cargo',l1('props','container','crate_side'),[1.2,.8,2],[0,.73,0]))
        items.append(fit('rudder',l1('vehicle','marine','rudder'),[.08,.5,.3],[0,0,-d/2]))
        register('vehicle','marine',key,name,items,[2.6,3.8,d+.4],['船壳','独立甲板','舵',feature],notes=['默认为展示基准，不是自动浮力配置'])
    aircraft=[('trainer','教练螺旋桨飞机',2,'prop'),('biplane','双翼机',4,'prop'),('glider','滑翔机',2,'glide'),('jet','轻型喷气机',2,'jet'),('cargo','运输机',4,'jet'),('seaplane','水上飞机',2,'float'),('helicopter','直升机',0,'rotor'),('gyrocopter','自转旋翼机',0,'gyro'),('tiltrotor','倾转旋翼机',2,'tilt'),('quadrotor','四旋翼物流机',4,'quad'),('airship','小型飞艇',0,'balloon'),('shuttle','科考穿梭机',2,'delta')]
    for key,name,n,feature in aircraft:
        items=[fit('fuselage',l1('vehicle','aero','nacelle'),[1,1,3.5],[0,.65,0]),fit('tailfin',l1('vehicle','aero','fin'),[.7,.75,.6],[0,1,-1.4])]
        if feature in ('quad','tilt'):
            for i in range(n):
                a=math.tau*i/n;r=1.5;items.append(beam('arm'+str(i),[0,1,0],[r*math.sin(a),1,r*math.cos(a)],.1));items.append(fit('rotor'+str(i),l2('vehicle','flightmodule','rotor_blade'),[1.1,.16,1.1],[r*math.sin(a),1.08,r*math.cos(a)]))
        else:
            for i in range(n):items.append(fit('wing'+str(i),l1('vehicle','aero','delta' if feature=='delta' else 'swept_wing' if feature=='jet' else 'wing'),[1.7,.13,.8],[(-1 if i%2==0 else 1)*1.05,1+(i//2)*.55,.15],[0,180 if i%2==0 else 0,0]))
        if feature in ('rotor','gyro'):items.append(fit('mainrotor',l2('vehicle','flightmodule','rotor_blade'),[3.7,.25,3.7],[0,1.7,0]))
        if feature in ('prop','jet','float'):items.append(fit('engine',l2('vehicle','flightmodule','prop_blade' if feature!='jet' else 'inlet'),[.9,.2,.9],[0,1.08,1.8],[90,0,0]))
        if feature=='balloon':items.append(fit('envelope',l1('vehicle','aero','nacelle'),[2,1.8,4.6],[0,1.45,0]))
        for i,s in enumerate((-1,1)):
            if feature=='float':items.append(fit('float'+str(i),l1('vehicle','marine','bow'),[.38,.35,2.4],[s*.8,0,0]))
            else:items.append(fit('undercarriage'+str(i),l1('vehicle','wheel','caster_fork'),[.2,.65,.35],[s*.42,0,.45]))
        register('vehicle','air',key,name,items,[4.8,3.4,5],['机身','尾翼','支撑或浮筒',feature,str(n)+'翼或旋翼'])
