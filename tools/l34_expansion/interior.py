"""Complete furniture with explicit supports and a usable role, not L2 relabels."""
from .common import *

def author():
    tables=[('dining','餐桌','oval','tapered'),('workbench','木工作业台','live_edge','trestle'),('coffee','低脚茶几','kidney','hairpin'),('side','边桌','round','pedestal'),('conference','会议桌','stadium','sled'),('console','玄关长案','trapezoid','turned'),('corner','转角工作台','corner','cantilever'),('drop_leaf','折页餐桌','drop_leaf','folding'),('hex','六角展台','hex','crossbar'),('seminar','扇形培训桌','semicircle','caster'),('altar','供案','scalloped','cabriole'),('picnic','三角野餐桌','triangular','trestle')]
    for key,name,top,leg in tables:
        w=1.65;d=.85;h=.72 if key!='coffee' else .36
        items=legs(w-.22,d-.18,h-.07,.1,style=leg)+[fit('top',l2('interior','worksurface',top),[w,.10,d],[0,h-.1,0])]
        if key in ('workbench','console','altar'):items += [block('stretcher',[w-.15,.12,.16],[0,.18,0]),fit('drawer',l2('interior','drawercartridge','box'),[.6,.16,.6],[0,h-.28,0])]
        if key=='picnic':items += [block('bench'+str(s),[w,.08,.28],[0,.35,s*.65]) for s in (-1,1)]
        register('interior','table',key,name,items,[w,h,d+(.6 if key=='picnic' else 0)],['完整桌面','独立承重结构',leg,top])
    seats=[('dining','餐椅','back_spindle','tapered'),('office','办公转椅','mesh_pan','star'),('armchair','扶手椅','arm_pad','turned'),('rocker','摇椅','back_ladder','sled'),('stool','吧台凳','saddle','pedestal'),('lounge','躺椅','back_shell','cantilever'),('kneeling','跪坐椅','kneeling','sled'),('folding','折叠椅','slatted','folding'),('auditorium','礼堂椅','upholstered','cantilever'),('garden','花园椅','back_fan','cabriole'),('tractor','驾驶座椅','tractor','pedestal'),('bucket','赛车座椅','bucket','sled'),('bench','公共长凳','back_ladder','trestle'),('sofa','双人沙发','arm_pad','tapered'),('chaise','贵妃榻','back_shell','cabriole'),('pew','木质教堂长椅','back_spindle','sled')]
    for key,name,seat,leg in seats:
        w=1.6 if key in ('bench','sofa','pew') else .65;d=1.35 if key=='chaise' else .62;h=.72 if key=='stool' else .43
        items=legs(w-.16,d-.16,h,.09,style=leg)+[fit('seat',l2('interior','seatpack',seat),[w,.65,d],[0,h,0])]
        if key in ('sofa','chaise'):items.append(fit('cushion',l1('interior','soft','box_cushion'),[w*.85,.16,d*.8],[0,h+.04,.04],optional=True))
        if key=='office':items.append(fit('gaslift',l1('industry','pipe','socket'),[.12,.28,.12],[0,.22,0]))
        register('interior','seat',key,name,items,[w,h+.65,d],['座面与靠背','完整接地支撑',seat,leg])
    storage=[('wardrobe','双门衣柜','tall',2),('dresser','三抽斗柜','open_front',3),('filing','文件柜','locker',4),('bookcase','开放书柜','open_front',5),('apothecary','多屉药柜','apothecary',9),('display','玻璃展示柜','display',4),('corner','转角储物柜','corner',3),('shoe','鞋柜','through',5),('sideboard','餐边柜','curved',3),('locker','更衣柜','locker',2),('media','电视矮柜','open_front',2),('wall','壁挂吊柜','wall_hung',2),('tool','工具抽屉柜','beveled',6),('wine','酒格展示柜','cubby',9),('tallboy','高斗柜','tall',5),('pantry','食品储藏柜','tall',4),('coat','衣帽组合柜','through',2),('archive','档案格柜','cubby',12)]
    for key,name,case,n in storage:
        w=1.1;h=1.8 if key not in ('media','dresser','sideboard') else .85;d=.55
        items=[fit('carcase',l2('interior','carcase',case),[w,h,d],[0,.08,0]),block('plinth',[w-.1,.08,d-.1])]
        if key in ('bookcase','shoe','wine','pantry','archive','display'):
            for i in range(n):items.append(fit('shelf'+str(i),l1('interior','shelf','wine' if key=='wine' else 'floating'),[w-.12,.04,d-.1],[0,.12+i*(h-.15)/n,0]))
        else:
            for i in range(n):items.append(fit('drawer'+str(i),l2('interior','drawercartridge','file' if key in ('filing','archive') else 'box'),[w-.12,(h-.16)/n-.02,d-.08],[0,.12+i*(h-.16)/n,.03]))
        register('interior','storage',key,name,items,[w,h+.08,d],['完整柜体','内部储存区',case,str(n)+'独立层格'])
    beds=[('single','单人床','head_spindle'),('double','双人床','head_tuft'),('bunk','双层床','bunk_guard'),('canopy','四柱床','canopy_corner'),('hospital','护理床','rail'),('crib','婴儿床','head_spindle'),('futon','低平台床','head_panel'),('daybed','靠墙榻','foot_panel')]
    for key,name,style in beds:
        w=1.65 if key in ('double','canopy') else .95;d=2;bh=.12 if key=='futon' else .4;items=legs(w-.12,d-.12,bh,.1)
        tiers=2 if key=='bunk' else 1
        for j in range(tiers):
            y=bh+j*1.3;items += [block('frame'+str(j),[w,.15,d],[0,y,0],color='#91714D'),fit('mattress'+str(j),l1('interior','soft','box_cushion'),[w-.08,.18,d-.08],[0,y+.15,0],color='#E4DFCF'),fit('pillow'+str(j),l1('interior','soft','bolster'),[w*.65,.12,.38],[0,y+.33,-d*.33],optional=True)]
        items.append(fit('headboard',l1('interior','bed',style),[w,.7,.12],[0,bh,-d/2]))
        if key in ('bunk','canopy','crib'):
            for i,(x,z) in enumerate(((-w/2,-d/2),(w/2,-d/2),(-w/2,d/2),(w/2,d/2))):items.append(block('post'+str(i),[.08,2.1,.08],[x,0,z],color='#91714D'))
        register('interior','bed',key,name,items,[w,2.1 if key in ('bunk','canopy') else bh+.8,d],['床架','床垫','枕垫',style,'双层' if tiers==2 else '单层'])
    wet=[('vanity','落地盥洗台','basin'),('pedestal','立柱洗手盆','pedestal'),('bath','独立浴缸','bathtub_rim'),('shower','淋浴间','shower_tray'),('toilet','坐便器','toilet_seat'),('towel','毛巾架','towel_rail'),('drain','公共洗涤槽','drain_grate'),('outdoor','户外花洒','shower_head'),('washstation','双盆洗手站','basin'),('utility','清洁拖布池','shower_tray')]
    for key,name,k in wet:
        w=1.5 if key in ('bath','washstation') else .8;items=[fit('fixture',l2('interior','wetfixture',k),[w,.7,.7],[0,.15,0]),block('base',[w,.15,.7],color='#C2CDD0')]
        if key in ('shower','outdoor'):items.extend([block('riser',[.04,1.9,.04],[.3,0,-.3],color='#8B9B9E'),fit('head',l1('interior','bath','shower_head'),[.25,.08,.25],[.25,1.9,-.2])])
        if key in ('vanity','pedestal','washstation'):items.append(fit('tap',l1('interior','kitchen','faucet_spout'),[.18,.35,.3],[0,.8,-.2]))
        register('interior','sanitary',key,name,items,[w,2 if key in ('shower','outdoor') else 1.15,.8],['给排水构造','独立接地体',k])
    kitchens=[('island','厨房中岛','worktop_cutout'),('sink','水槽地柜','sink_bowl'),('stove','燃气灶台','cooker_grate'),('hob','电磁炉台','hob_ring'),('hood','落地排烟工作站','hood_filter'),('prep','备餐台','drainboard'),('pantry','食品操作台','drawer_organizer'),('bar','吧台','backsplash'),('bakery','烘焙揉面台','worktop_cutout'),('dishwash','洗碗工作站','sink_bowl')]
    for key,name,k in kitchens:
        items=[fit('cabinet',l2('interior','carcase','under_sink'),[1.3,.85,.65]),fit('surface',l1('interior','kitchen',k),[1.35,.10,.7],[0,.85,0]),fit('drawer',l2('interior','drawercartridge','cutlery'),[1.1,.18,.52],[0,.58,.04])]
        if key in ('sink','dishwash'):items.append(fit('tap',l1('interior','kitchen','faucet_spout'),[.2,.38,.3],[0,.92,-.24]))
        if key=='hood':items+=[block('duct',[.32,1.2,.32],[0,.92,-.15]),fit('hood',l1('interior','kitchen','hood_filter'),[1.1,.12,.55],[0,1.7,0])]
        register('interior','kitchen',key,name,items,[1.35,2.2 if key=='hood' else 1.3,.7],['基柜','功能台面','储物抽屉',k])
    appliances=[('fridge','双门冰箱',2,'screen_bezel'),('washer','滚筒洗衣机',1,'lens_barrel'),('dryer','排风烘干机',1,'radio_grille'),('oven','烤箱',1,'screen_bezel'),('vending','自动售货机',6,'keyboard_plate'),('coffee','台式咖啡机',2,'control_knob'),('microwave','微波炉',1,'phone_shell'),('dishwasher','洗碗机',3,'radio_grille'),('aircon','独立空调机',4,'speaker_cone'),('water','饮水机',2,'control_knob')]
    for key,name,n,k in appliances:
        w=.7;h=1.65 if key in ('fridge','vending','aircon','water') else .85;items=[fit('housing',l1('interior','case','open_front'),[w,h,.65]),block('base',[w,.08,.65])]
        for i in range(n):items.append(fit('control'+str(i),l1('props','device',k),[.55,(h-.15)/n-.02,.1],[0,.1+i*(h-.15)/n,.35]))
        register('interior','appliance',key,name,items,[w,h,.75],['机壳','控制或检修面板',k,str(n)+'分区'])
    services=[('reception','接待服务台','corner'),('lectern','讲台','angled'),('altar','陈列祭台','floating'),('coatstand','衣帽架','pegboard'),('mirror','全身穿衣镜','bracketed'),('screen','折叠屏风','wire'),('trolley','医疗推车','wire'),('easel','画架','angled'),('musicstand','谱架','cantilever'),('podium','颁奖台','floating')]
    for key,name,k in services:
        w=1.4 if key in ('reception','altar','screen','podium') else .75;h=1.4
        items=legs(w-.12,.45,.35,.08,style='caster' if key=='trolley' else 'tapered')
        items+=[fit('frame',l1('interior','shelf','bracketed' if k=='corner' else k),[w,.9,.48],[0,.35,0]),block('service_top',[w,.06,.5],[0,h-.06,0])]
        if key in ('easel','mirror','screen','musicstand'):items.append(block('upright_panel',[w,.9,.05],[0,.45,-.15],rot=[-8,0,0],material='mat.glass' if key=='mirror' else 'mat.wood'))
        register('interior','service',key,name,items,[w,h,.6],['独立服务家具','接地支撑',k,key])
