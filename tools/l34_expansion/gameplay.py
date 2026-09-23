"""15 complete gameplay prefabs; signals remain explicit consumer contracts."""
from .common import *

def author():
    layouts=[('door','钥匙锁门','lock','keyway'),('vault','密码库门','lock','combination'),('lift','升降台','platform','lift_shoe'),('bridge','翻转桥','platform','hinge_plate'),('slider','横移渡板','platform','moving_bracket'),('pressure_gate','压力门','trigger','pressure'),('lever_gate','拉杆闸门','trigger','lever'),('spike_corridor','尖刺通道','trap','spike'),('pendulum','摆锤障碍','trap','pendulum'),('crusher','压砸机关','trap','crusher'),('saw','锯盘障碍','trap','saw'),('checkpoint','存档交互站','trigger','button'),('treasure','机关宝箱','lock','latch'),('barricade','可拆防护墙','cover','blast_panel'),('crystal_switch','晶体开关','lock','socket')]
    for key,name,family,partkey in layouts:
        items=[block('foundation',[2.8,.15,2],color='#8F998C')]
        if key in ('door','vault','pressure_gate','lever_gate'):
            for i,s in enumerate((-1,1)):items.append(fit('jamb'+str(i),l1('architecture','column','tuscan'),[.3,2.7,.4],[s*1.15,.15,0]))
            items.append(block('lintel',[2.6,.3,.45],[0,2.65,0]))
            items.append(fit('door',l1('architecture','wall','grid' if key.endswith('gate') else 'rebated'),[1.95,2.45,.16],[0,.15,0]))
            control_=control('open','door','门体抬升',2.45,axis=(0,1,0),mode='translation')
            items.append(fit('mechanism',l2('gameplay',family,partkey),[.45,.4,.3],[1.18,.95,.33]))
            controls=[control_]
        elif key=='treasure':
            items.extend([fit('chest',l1('props','container','trunk_shell'),[1.4,.9,.8],[0,.15,0]),fit('lid',l1('props','container','chest_lid'),[1.4,.3,.8],[0,1.03,0]),fit('mechanism',l2('gameplay',family,partkey),[.25,.3,.15],[0,.75,.46])]);controls=[control('open','lid','盖体抬升',.65,mode='translation')]
        elif family=='platform':
            items.append(fit('mechanism',l2('gameplay',family,partkey),[2.3,1.15,1.6],[0,.15,0]));controls=[]
        elif family=='trap':
            items.append(fit('mechanism',l2('gameplay',family,partkey),[1.8,1.8,1.3],[0,.15,0]));controls=[]
            for i,s in enumerate((-1,1)):items.append(fit('guard'+str(i),l1('gameplay','cover','barricade_leg'),[.3,.55,.5],[s*1.15,.15,0]))
        elif family=='cover':items.append(fit('mechanism',l2('gameplay',family,partkey),[2.3,1.7,.5],[0,.15,0]));controls=[]
        else:
            items.append(fit('pedestal',l1('architecture','column','pedestal'),[.6,.9,.6],[0,.15,0]));items.append(fit('mechanism',l2('gameplay',family,partkey),[.65,.6,.5],[0,1.03,0]));controls=[]
        ident=register('gameplay','interactive',key,name,items,[2.8,3,2],['完整安装结构','交互机构','稳定可寻址节点',key],controls=controls,rig='rigid-hierarchy')
        ASSEMBLIES[ident]['metadata']['gameplay']={'schema':'wx.gameplay-contract/1.0','events':['activate','release','reset'],'states':['idle','active'],'authority':'consumer-game','target':'door' if controls and key!='treasure' else 'lid' if key=='treasure' else 'mechanism','physics_implemented':False,'damage_implemented':False}
