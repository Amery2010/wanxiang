"""118 complete set-dressing / usable props with purpose-specific structure."""
from .common import *

def author():
    containers=[('shipping','运输箱','crate_side',4),('chest','带锁宝箱','chest_lid',1),('barrel','箍圈木桶','barrel_stave',8),('hamper','编织提篮','basket_wall',4),('trunk','旅行箱','trunk_shell',1),('toolbox','工具箱','case_foam',3),('medical','急救箱','case_foam',6),('ammo','弹药箱','ammo_insert',8),('wine','瓶装运输箱','bottle_divider',6),('grain','谷物麻袋','sack_shell',1),('mail','投递信箱','tube_body',1),('waste','带盖垃圾箱','can_body',1),('recycle','分类回收桶','can_body',3),('water','带龙头储水桶','can_body',2),('oil','油料桶','can_body',4),('tote','开放手提筐','tote_wall',4),('pallet','码放托盘','pallet_deck',5),('suitcase','拉杆行李箱','pack_shell',1),('cylinder','气瓶推架','tube_body',2),('display','展示收纳箱','crate_end',2)]
    for key,name,body,n in containers:
        items=[block('floor',[.8,.06,.6])]
        if body in ('crate_side','basket_wall','tote_wall','crate_end'):
            for i,(x,z,rot) in enumerate(((-.4,0,90),(.4,0,90),(0,-.3,0),(0,.3,0))):items.append(fit('wall'+str(i),l1('props','container',body),[.8,.55,.055],[x,.04,z],[0,rot,0]))
        elif body=='barrel_stave':items.extend(radial(l1('props','container',body),n,.28,.05,[.19,.75,.055],prefix='stave'))
        elif body=='pallet_deck':
            for i in range(n):items.append(fit('board'+str(i),l1('props','container','pallet_deck'),[.8,.06,.1],[0,.12,(i-(n-1)/2)*.12]))
        else:items.append(fit('body',l1('props','container',body),[.8,.55,.6],[0,.05,0]))
        if key not in ('grain','pallet','tote'):items.append(fit('lid',l1('props','container','crate_lid'),[.83,.06,.63],[0,.59,0]))
        if key in ('chest','trunk','toolbox','medical','ammo'):items.append(fit('lock',l2('gameplay','lock','latch'),[.12,.15,.05],[0,.4,.34]))
        if key in ('cylinder','suitcase'):
            for i,s in enumerate((-1,1)):items.append(fit('wheel'+str(i),l1('vehicle','wheel','solid_tire'),[.14,.055,.14],[s*.32,.06,-.2],[90,0,0],anchor='center'))
            items.append(fit('handle',l1('props','handle','u_pull'),[.38,.45,.07],[0,.45,-.26]))
        if key=='water':items.append(fit('tap',l2('industry','flowjoint','nozzle'),[.12,.1,.18],[0,.15,.34]))
        if key=='wine':
            for i in range(6):items.append(fit('bottle'+str(i),l1('props','vessel','bottle'),[.16,.4,.16],[(i%3-1)*.21,.1,(i//3-.5)*.24],optional=True))
        register('props','container',key,name,items,[.9,1,.8],['完整底壁结构','用途附件',body,key])
    toolkits=[('carpenter','木工工具架',['saw','chisel','plane']),('gardener','园艺工具架',['hoe','rake','trowel']),('miner','采矿工具架',['pick','sledge','shovel']),('smith','锻造工具台',['hammer','plier','file']),('mason','泥瓦工具台',['trowel','mallet','chisel']),('mechanic','维修工具车',['wrench','socket','plier']),('electrician','电工工具盘',['snip','awl','wrench']),('woodcutter','伐木工具架',['adze','saw','claw']),('excavator','挖掘工具架',['spade','fork','pick']),('sculptor','雕刻工具台',['chisel','mallet','scraper']),('painter','油漆工具台',['brush','scraper','snip']),('leather','皮革工具台',['awl','mallet','snip']),('potter','陶艺工具台',['scraper','spade','trowel']),('metal','钣金工具台',['snip','hammer','file']),('survey','测量工具柜',['awl','drill','wrench']),('restorer','修复工具台',['brush','scraper','chisel']),('craft','精工工具柜',['file','drill','socket']),('farm','农具架',['fork','hoe','spade']),('quarry','采石工具台',['sledge','pick','chisel']),('assembly','装配工位工具架',['socket','wrench','drill'])]
    for j,(key,name,tools) in enumerate(toolkits):
        items=legs(1.1,.5,.65,.08)+[block('worktop',[1.3,.07,.65],[0,.65,0],color='#B19770'),block('backboard',[1.3,.65,.04],[0,.70,-.3],color='#677B79')]
        for i,k in enumerate(tools):items.append(fit('tool'+str(i),l2('props','tool',k),[.25,.6,.13],[(i-1)*.4,.74,-.2]))
        items.append(fit('tray',l1('interior','drawer','tray'),[.7,.1,.4],[0,.72,.05],optional=True))
        register('props','toolkit',key,name,items,[1.3,1.4,.7],['工作台','立式悬挂架',*tools])
    lamps=[('desk','台灯','conical_shade',.45,1),('floor','落地灯','drum_shade',1.55,1),('street','单臂路灯','dome_shade',3,1),('double_street','双臂路灯','dome_shade',3,2),('lanternpost','庭院灯柱','lantern_frame',2.2,1),('bollard','矮柱景观灯','diffuser',.65,1),('sconce','壁挂灯','bell_shade',.5,1),('chandelier','吊灯','candle_cup',1.2,6),('candelabra','三头烛台','candle_cup',.6,3),('oil','煤油灯','chimney',.45,1),('spot','检修射灯','reflector',.9,1),('tripod','摄影灯','spot_yoke',1.6,1),('signal','三色信号灯','cage',2.4,3),('beacon','旋转警示灯','dome_shade',.35,1),('bollard_pair','双向步道灯','diffuser',.9,2),('hanging','链吊提灯','lantern_frame',1.2,1)]
    for key,name,shade,h,n in lamps:
        items=[fit('base',l1('props','lamp','lamp_base'),[.4,.1,.4]),block('stem',[.06,h,.06],[0,.08,0],color='#64747D')]
        for i in range(n):
            x=(i-(n-1)/2)*.3 if n<4 else .4*math.sin(i*math.tau/n);z=0 if n<4 else .4*math.cos(i*math.tau/n)
            if n>1:items.append(beam('arm'+str(i),[0,h-.1,0],[x,h,z],.035))
            items.append(fit('light'+str(i),l2('props','luminaire',shade),[.3,.4,.3],[x,h,z]))
        if key=='tripod':
            for i in range(3):items.append(beam('tripod'+str(i),[0,.7,0],[.45*math.sin(i*math.tau/3),0,.45*math.cos(i*math.tau/3)],.04))
        register('props','lamp',key,name,items,[max(.5,n*.3),h+.5,.9],['基座与支架','独立发光材质',shade,key],notes=['发光材质并不自动创建引擎实时灯光'])
    instruments=[('guitar','吉他','lute_body','guitar_neck'),('lute','鲁特琴','lute_body','peg'),('violin','小提琴','violin_plate','guitar_neck'),('cello','大提琴','violin_plate','peg'),('drum','立式鼓','drum_shell','reed'),('timpani','定音鼓','drum_shell','bridge'),('flute','长笛','flute_tube','mouthpiece'),('clarinet','单簧管','flute_tube','reed'),('trumpet','小号','horn_bell','mouthpiece'),('trombone','长号','horn_bell','flute_tube'),('horn','圆号','horn_bell','peg'),('bell','架钟','bell','bridge'),('cymbal','镲架','cymbal','peg'),('gong','锣架','cymbal','bridge'),('xylophone','木琴','bridge','reed'),('harp','框架竖琴','lute_body','peg')]
    for j,(key,name,body,accessory) in enumerate(instruments):
        items=[fit('body',l1('props','musical',body),[.45,.55,.2],[0,.05,0]),fit('fitting',l1('props','musical',accessory),[.16,.55,.12],[0,.45,0])]
        if key in ('drum','timpani','bell','cymbal','gong','xylophone'):items+=legs(.5,.35,.45,.04);items[0]['position'][1]+=.4;items[1]['position'][1]+=.4
        if key in ('guitar','lute','violin','cello','harp'):
            for i in range(4 if key!='guitar' else 6):items.append(beam('string'+str(i),[(i-2)*.012,.25,.105],[(i-2)*.012,.9,.105],.003,color='#E1D4B0',optional=True))
        if key=='xylophone':items.extend([fit('bar'+str(i),l1('props','musical','bridge'),[.055,.03,.25+i*.035],[(i-3)*.07,.85,0]) for i in range(7)])
        register('props','instrument',key,name,items,[.65,1.2,.5],['完整演奏器物','构造附件',body,accessory])
    narratives=[('hourglass','沙漏','hourglass_cup'),('compass','航海罗盘','compass_case'),('telescope','观测望远镜','watch_case'),('chess','棋盘棋具','chess_knight'),('reliquary','遗物展示匣','relic_shard'),('scroll','卷轴架','scroll_rod'),('seal','印章文案','seal_stamp'),('locket','首饰展示架','locket'),('medal','奖章展示座','medallion'),('dice','骰盅游戏盘','dice'),('keys','钥匙挂架','key_blank'),('clock','座钟','watch_case'),('treasure','宝藏陈列盒','treasure_corner'),('charter','蜡封文书','wax_seal')]
    for j,(key,name,k) in enumerate(narratives):
        items=[fit('tray',l1('interior','drawer','tray'),[.65,.07,.45])]
        for i in range(2+j%4):items.append(fit('object'+str(i),l1('props','narrative',k),[.13,.2,.13],[(i-(1+j%4)/2)*.15,.06,0]))
        if key in ('hourglass','clock','compass'):items.append(fit('frame',l1('props','lamp','lantern_frame'),[.55,.55,.4],[0,.05,0]))
        if key=='chess':items.append(fit('board',l1('architecture','floor','parquet'),[.6,.02,.4],[0,.065,0]))
        register('props','narrative',key,name,items,[.7,.65,.5],['完整陈设','承载与展示结构',k])
    streets=[('bench','街边长凳','back_ladder'),('fountain','饮水喷泉','basin'),('hydrant','消防栓','tee'),('postbox','邮筒','tube_body'),('bollard','防撞柱','baluster'),('bike_rack','自行车架','u_pull'),('bin','街角废物桶','basket_wall'),('planter','带座椅花箱','planter'),('notice','公告栏','notice'),('wayfinding','多向导视牌','arrow'),('bus_sign','公交站牌','round'),('barrier','交通护栏','cross'),('meter','停车计时器','control_knob'),('ticket','自助售票机','screen_bezel'),('kiosk','公共信息终端','keyboard_plate'),('parcel','快递取件柜','locker')]
    domains={'back_ladder':('interior','seat'),'basin':('props','vessel'),'tee':('industry','pipe'),'tube_body':('props','container'),'baluster':('architecture','column'),'u_pull':('props','handle'),'basket_wall':('props','container'),'planter':('props','vessel'),'notice':('props','sign'),'arrow':('props','sign'),'round':('props','sign'),'cross':('architecture','railing'),'control_knob':('props','device'),'screen_bezel':('props','device'),'keyboard_plate':('props','device'),'locker':('interior','case')}
    for j,(key,name,k) in enumerate(streets):
        w=1.6 if key in ('bench','bike_rack','planter','notice','barrier') else .65;h=1.5 if key in ('notice','wayfinding','bus_sign','meter','ticket','kiosk','parcel') else .8
        items=[block('footing',[w,.1,.5],color='#818F91'),block('upright',[.1,h,.1],[0,.1,0],color='#586E77')]
        d,g=domains[k];items.append(fit('function',l1(d,g,k),[w,h*.6,.4],[0,h*.45,0]))
        if key=='wayfinding':items.extend([fit('arrow'+str(i),l1('props','sign','arrow'),[.8,.18,.06],[0,h-.15*i,0],[0,90*i,0]) for i in range(3)])
        if key=='bench':items += legs(w-.2,.4,.45,.1)
        register('props','street',key,name,items,[w,h+.6,.6],['稳定接地','功能构造',key,k])
    devices=[('camera','三脚照相机','camera_shell','lens_barrel'),('radio','收音机','radio_grille','control_knob'),('console','控制台','keyboard_plate','screen_bezel'),('terminal','电脑终端','screen_bezel','keyboard_plate'),('printer','打印机','phone_shell','radio_grille'),('projector','投影仪','camera_shell','lens_barrel'),('speaker','音箱','speaker_cone','radio_grille'),('phone','电话机','phone_shell','control_knob'),('microscope','显微镜','lens_barrel','control_knob'),('oscilloscope','示波器','screen_bezel','control_knob'),('analyzer','分析仪','camera_shell','screen_bezel'),('sensor','监测站','radio_grille','lens_barrel'),('scanner','扫描仪','phone_shell','lens_barrel'),('amplifier','功放','radio_grille','control_knob'),('transmitter','无线电台','keyboard_plate','radio_grille'),('recorder','记录仪','screen_bezel','speaker_cone')]
    for j,(key,name,k,a) in enumerate(devices):
        items=[fit('housing',l1('interior','case','beveled'),[.65,.45,.5]),fit('face',l1('props','device',k),[.55,.32,.06],[0,.1,.27]),fit('control',l1('props','device',a),[.14,.14,.08],[.22,.06,.3])]
        if key in ('camera','microscope','sensor'):items.append(fit('support',l1('interior','leg','star'),[.65,.5,.65],[0,-.48,0]));[it.update(position=[it.get('position',[0,0,0])[0],it.get('position',[0,0,0])[1]+.48,it.get('position',[0,0,0])[2]]) for it in items]
        if key in ('radio','transmitter','sensor'):items.append(fit('antenna',l1('robot','sensor','antenna'),[.15,.65,.15],[.22,.45,-.1]))
        if key in ('console','terminal'):items.append(fit('keyboard',l1('props','device','keyboard_plate'),[.62,.03,.25],[0,.01,.45]))
        register('props','device',key,name,items,[.7,1.15,.8],['完整机壳','操作面','用途附件',key])
