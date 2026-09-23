"""33 dressed characters reuse the retained human skin/rig, not new motion claims."""
from .common import *
ROLES=[('carpenter','木匠','carpenter','hardhat','apron'),('gardener','园丁','gardener','strawhat','apron'),('miner','矿工','miner','hardhat','vest'),('scribe','抄写员','scribe','cap','cape'),('fisher','渔夫','fisher','strawhat','vest'),('signal','信号员','signal','cap','vest'),('musician','旅行乐师','musician','cap','cape'),('electrician','电工','electrician','hardhat','vest'),('archivist','档案员','archivist','cap','collar'),('explorer','探险家','explorer','helmet','backpack'),('painter','画师','painter','cap','apron'),('diver','潜水研究员','diver','helmet','belt'),('mechanic','机械师','mechanic','cap','apron'),('tailor','裁缝','tailor','cap','collar'),('surveyor','测绘员','surveyor','hardhat','vest'),('courier','信使','courier','helmet','backpack'),('botanist','植物学家','botanist','strawhat','backpack'),('medic','战地医护','medic','cap','belt'),('locksmith','锁匠','locksmith','cap','apron'),('mason','泥瓦匠','mason','hardhat','apron'),('cook','炊事员','cook','cap','apron'),('traveller','旅人','traveller','strawhat','cape'),('ranger','巡林者','explorer','cap','quiver'),('guard','城镇守卫','signal','helmet','armor'),('knight','护卫骑士','traveller','field_helmet','armor'),('scholar','学者','scribe','cap','robe'),('merchant','行商','courier','cap','belt'),('captain','船长','surveyor','cap','coat'),('welder','焊工','mechanic','weld_mask','apron'),('pilot','飞行员','signal','helmet','vest'),('farmer','农夫','gardener','strawhat','overalls'),('technician','实验室技师','electrician','cap','coat'),('porter','搬运工','courier','hardhat','backpack')]

def author():
    for j,(key,name,kit,headwear,outfit) in enumerate(ROLES):
        # Source head and clothing are bone-local; do not ground-align them.
        items=[inst('skin','core.human.body',params={'height':1.82,'build':1,'grip':False}),inst('head','core.human.head',parent='skin.rig.head'),inst('hair','core.human.hair.short',parent='skin.rig.head')]
        hat='w.wear.'+headwear
        if hat in PARTS:items.append(inst('hat',hat,parent='skin.rig.head'))
        elif 'w.wear.cap' in PARTS:items.append(inst('hat','w.wear.cap',parent='skin.rig.head'))
        if outfit=='apron':items.append(inst('apron','core.wear.apron',parent='skin.rig.chest'))
        elif outfit=='vest':items.append(inst('vest','w.wear.safety_vest',parent='skin.rig.chest'))
        elif outfit=='backpack':items.append(inst('backpack','w.wear.backpack',parent='skin.rig.chest'))
        elif outfit=='overalls':items.append(inst('overall','w.wear.overall_bib',parent='skin.rig.chest'))
        elif outfit=='armor':
            items.append(fit('breastplate',l1('character','armor','breastplate'),[.46,.45,.19],[0,-.2,.05],parent='skin.rig.chest',anchor='center'))
            for i,s in enumerate((-1,1)):items.append(fit('pauldron'+str(i),l1('character','armor','pauldron'),[.22,.16,.23],[s*.26,.0,0],parent='skin.rig.chest',anchor='center'))
        elif outfit in ('cape','robe','coat'):
            items.append(fit('cape',l1('character','clothing','cape_panel'),[.65,.9,.12],[0,-.65,-.17],parent='skin.rig.chest',anchor='center'))
            if outfit in ('robe','coat'):items.append(fit('skirt',l1('character','clothing','skirt_panel'),[.46,.5,.25],[0,-.35,0],parent='skin.rig.pelvis',anchor='center'))
        elif outfit=='quiver':items.append(fit('quiver',l1('props','container','tube_body'),[.14,.6,.14],[.18,-.2,-.2],parent='skin.rig.chest',anchor='center'))
        else:items.append(fit('belt',l1('character','clothing','belt'),[.44,.10,.25],[0,0,0],parent='skin.rig.pelvis',anchor='center'))
        # Hip-mounted service pouch keeps the hands/skin free and follows the rig.
        items.append(fit('service',l2('character','servicekit',kit),[.20,.30,.14],[.24,-.2,0],parent='skin.rig.pelvis',anchor='center'))
        if key in ('scholar','merchant','captain','ranger','porter','technician','pilot','knight','guard','welder','farmer'):
            accessory={'scholar':'book_block','merchant':'paper_stack','captain':'magnifier','ranger':'scroll_core','porter':'clipboard','technician':'pen_barrel','pilot':'folder','knight':'book_cover','guard':'clip','welder':'ruler','farmer':'binder_ring'}[key]
            items.append(fit('identifier',l1('props','office',accessory),[.12,.12,.04],[0,-.18,.14],parent='skin.rig.chest',anchor='center',optional=True))
        register('character','profession',key,name,items,[.9,1.95,.65],['完整人体与蒙皮','骨骼挂接服饰',kit,outfit],rig='retained-human-rig',clip_source='fnd-adult',notes=['继承原人体检查动作；新增服饰是刚性骨骼挂接，不是布料蒙皮或新动作认证'])
