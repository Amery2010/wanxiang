"""37 complete stylised creature prefabs, with honest static/rigged contracts."""
from .common import *

def author():
    # Thirteen morphology-driven mammals. Four skin families are retained for
    # companion working animals; heavy forms use explicit anatomy composition.
    mammals=[('pack_donkey','驮运毛驴','donkey','pack'),('saddled_horse','鞍具旅行马','horse','saddle'),('rescue_dog','救援犬','dog','rescue'),('sled_dog','雪橇犬','dog','harness'),('messenger_dog','信使犬','dog','pouch'),('working_goat','驮包山羊','goat','pack'),('stag','角冠雄鹿','deer','antler'),('musk_ox','长角麝牛','cow','horn'),('bear','山地熊','heavy','bear'),('elephant','长牙象','heavy','elephant'),('rhino','犀角兽','heavy','rhino'),('boar','獠牙野猪','heavy','tusk'),('ram','盘角羊','sheep','ram')]
    for key,name,base,feature in mammals:
        if base in ('dog','donkey','goat','deer','cow','sheep'):
            body='w.fauna.'+base+'.body';head='w.fauna.'+base+'.head';items=[inst('skin',body),inst('head',head,parent='skin.rig.head')];rig='retained-'+base
            if feature in ('pack','rescue','harness','pouch'):
                # Attach to body rig: no static saddle floating while the animal walks.
                items.append(fit('harness',l1('character','clothing','belt'),[.5,.16,.7],[0,.14,0],parent='skin.rig.body',anchor='center'))
                for i,s in enumerate((-1,1)):items.append(fit('bag'+str(i),l1('props','container','pouch_shell'),[.18,.3,.3],[s*.28,-.05,-.08],parent='skin.rig.body',anchor='center'))
            else:items.append(fit('horns',l1('creature','horn','antler' if feature=='antler' else 'ram' if feature=='ram' else 'ibex'),[.75,.7,.4],[0,.13,-.03],parent='skin.rig.head'))
            source='world-'+base
        elif base=='horse':
            # Preserve exactly the original horse rig/head local convention.
            src=ASSEMBLIES['fnd-horse'];items=deepcopy(src['instances']);source='fnd-horse';rig='retained-horse'
            items.append(fit('saddlebags',l1('props','container','pack_shell'),[.5,.5,.45],[.45,1.2,-.15]))
            # Existing recipe params are resolved to defaults before new registration.
            from wanxiang.semantic import assembly as resolve_assembly
            items=resolve_assembly(src)['instances']+[items[-1]]
            for attachment in items:
                if attachment['id'] in ('mane','saddle','saddlebags'):
                    attachment['parent']='skin.rig.body'
                    attachment['position']=[v-(1.18 if i==1 else 0) for i,v in enumerate(attachment.get('position',[0,0,0]))]

        else:
            h=1.25 if feature=='elephant' else .7;w=1 if feature=='elephant' else .75;d=1.9
            items=[fit('torso','exp.creature.mammal_torso',[w,.8,d],[0,h*.65,0])]
            for i,(x,z) in enumerate(((-w*.35,-.6),(w*.35,-.6),(-w*.35,.6),(w*.35,.6))):items.append(fit('leg'+str(i),'exp.creature.elephant_leg' if feature=='elephant' else 'exp.creature.plantigrade_leg',[.25,h,.3],[x,0,z]))
            items.append(fit('head','exp.creature.elephant_head' if feature=='elephant' else 'exp.creature.bear_head',[w*.8,.8,.9],[0,h*.65,d*.42]))
            if feature in ('rhino','tusk'):items.append(fit('feature',l1('creature','horn','rhino') if feature=='rhino' else l1('creature','mouth','tusk'),[.35,.45,.4],[0,h+.3,1.1]))
            source=None;rig='none-static'
        register('creature','mammal',key,name,items,[1.3,2.4,3],['完整身体','四肢与识别特征',base,feature],rig=rig,clip_source=source if source in MOTIONS else None,notes=['工作动物装备是独立刚性附件；不是新的完整动作库'])
    birds=[('eagle','山鹰','hook','spread'),('owl','猫头鹰','hook','folded'),('heron','苍鹭','filter','longleg'),('duck','野鸭','filter','webbed'),('swan','天鹅','filter','longneck'),('raven','渡鸦','hook','fan'),('parrot','鹦鹉','hook','crest'),('penguin','企鹅','filter','upright')]
    for j,(key,name,beak,form) in enumerate(birds):
        h=.9 if form=='longleg' else .35;items=[fit('torso','exp.creature.avian_torso',[.45,.55,.75],[0,h,0]),fit('head','exp.creature.raptor_head',[.27,.3,.3],[0,h+.45,.28])]
        for i,s in enumerate((-1,1)):
            items.append(fit('foot'+str(i),l1('creature','foot','webbed' if form=='webbed' else 'talon'),[.16,.12,.25],[s*.13,0,.1]))
            items.append(beam('leg'+str(i),[s*.13,.10,.07],[s*.13,h+.1,0],.035,color='#AFA18A'))
            items.append(fit('wing'+str(i),'exp.creature.feather_wing',[.8 if form=='spread' else .25,.12,.65],[s*.37,h+.30,0],[0,s*30,s*15]))
        if form=='crest':items.append(fit('crest',l1('creature','wing','primary_feather'),[.2,.35,.08],[0,h+.7,.22]))
        if form=='longneck':items.append(fit('neck',l1('nature','branch','cane'),[.12,.5,.12],[0,h+.38,.25]));items[1]['position'][1]+=.38
        register('creature','bird',key,name,items,[2,.8+h,1.3],['完整禽体','双翼与足',beak,form],rig='none-static')
    aquatic=[('shark','礁鲨','shark'),('ray','鳐鱼','ray'),('eel','海鳗','eel'),('turtle','海龟','turtle'),('crocodile','鳄鱼','crocodile'),('lizard','巨蜥','lizard'),('octopus','章鱼','octopus'),('squid','乌贼','squid')]
    for key,name,form in aquatic:
        items=[]
        if form=='shark':items=[fit('body','exp.creature.shark_body',[.8,1,2.5]),fit('tail','exp.creature.fish_tail',[.1,.9,.6],[0,.08,-1.3])]
        elif form in ('octopus','squid'):
            items=[fit('mantle','exp.creature.slime',[.65,.65,1 if form=='squid' else .65])]
            for i in range(8):items.append(fit('tentacle'+str(i),'exp.creature.tentacle',[.7,.25,.25],[.23*math.sin(i*math.tau/8),.05,.23*math.cos(i*math.tau/8)],[0,360*i/8,0]))
            if form=='squid':items.append(fit('fin','exp.creature.fish_tail',[.1,.6,.6],[0,.25,-.55],[0,0,90]))
        elif form=='eel':items=[fit('spine','exp.creature.serpent',[.5,.3,2.8]),fit('fin','exp.creature.fish_tail',[.05,.3,.4],[0,.05,-1.2])]
        elif form=='ray':
            items=[fit('body','exp.creature.reptile_torso',[.6,.25,1.5]),fit('tail','exp.creature.serpent',[.15,.15,1.7],[0,0,-1.1])]
            for i,s in enumerate((-1,1)):items.append(fit('pectoral'+str(i),'exp.creature.membrane_wing',[1,.12,.9],[s*.55,.1,0],[0,180*i,0]))
        else:
            items=[fit('torso','exp.creature.reptile_torso',[.75,.4,2.3]),fit('head','exp.creature.reptile_head',[.45,.3,.7],[0,.12,1.1])]
            for i,(x,z) in enumerate(((-.4,-.55),(.4,-.55),(-.4,.5),(.4,.5))):items.append(fit('leg'+str(i),'exp.creature.reptile_leg',[.45,.22,.35],[x,0,z],[0,180 if x<0 else 0,0]))
            if form=='turtle':items.append(fit('shell',l1('props','lamp','dome_shade'),[1,.45,1.4],[0,.15,0]))
            if form=='crocodile':items.extend([fit('scute'+str(i),l1('creature','horn','frill'),[.2,.2,.2],[0,.35,-.7+i*.3],optional=True) for i in range(5)])
        register('creature','aquatic',key,name,items,[2.5,1.3,3.5],['完整躯体','推进或行走附肢',form],rig='none-static',notes=['水生对象的展示原点不等于自动浮力或游泳控制器'])
    fantastic=[('dragon','幼龙','dragon',4),('wyvern','双足翼龙','wyvern',2),('beetle','甲壳巨虫','beetle',6),('spider','洞穴蛛','spider',8),('moth','夜蛾','moth',6),('crab','岩蟹','crab',8),('slime','晶簇软泥','slime',0),('golem','石质傀儡','golem',2)]
    for key,name,shape,n in fantastic:
        items=[fit('core','exp.creature.slime' if shape=='slime' else 'exp.creature.mammal_torso',[.7,.65,1.1],[0,.3,0])]
        if shape in ('dragon','wyvern'):items.append(fit('head','exp.creature.dragon_head',[.55,.6,.6],[0,.6,.55]))
        for i in range(n):
            s=-1 if i%2==0 else 1;z=(i//2-(n//2-1)/2)*.32
            if shape=='golem':items.append(fit('leg'+str(i),l1('terrain','cliff','columnar'),[.27,.55,.3],[s*.22,0,0]))
            else:items.append(fit('leg'+str(i),'exp.creature.reptile_leg',[.6,.35,.3],[s*.44,0,z],[0,180 if s<0 else 0,0]))
        if shape in ('dragon','wyvern','moth'):
            for i,s in enumerate((-1,1)):items.append(fit('wing'+str(i),'exp.creature.membrane_wing',[1.4,.4,1],[s*.7,.65,0],[0,180*i,0]))
        elif shape=='beetle':
            for i,s in enumerate((-1,1)):items.append(fit('elytron'+str(i),l1('creature','wing','insect_elytron'),[.4,.45,1.05],[s*.2,.35,0]))
        elif shape=='crab':items.extend([fit('claw'+str(i),l1('creature','mouth','mandible'),[.3,.3,.4],[s*.75,.2,.6]) for i,s in enumerate((-1,1))])
        elif shape=='slime':items.append(fit('crystal',l1('creature','horn','rhino'),[.25,.4,.25],[0,.85,0]))
        elif shape=='golem':items.append(fit('head',l1('terrain','cliff','pinnacle'),[.45,.5,.45],[0,.88,0]))
        register('creature','fantastic',key,name,items,[3,1.6,2],['独立附肢','完整奇幻生物',shape,str(n)+'足'],rig='none-static')
