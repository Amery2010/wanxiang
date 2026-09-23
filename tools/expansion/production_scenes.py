"""Six curated D/E validation scenes; all leaves resolve to the public catalogue."""
from .production import *

def paving(nx,nz,step=2):
    return [pi(f'ground{x}_{z}','exp.arch.floor',[(x-(nx-1)/2)*step,0,(z-(nz-1)/2)*step],scale=[step/2,1,step/2]) for x in range(nx) for z in range(nz)]
def trees(points,kind='exp-birch'):
    return [ai('tree'+str(i),kind,[x,0,z],scale=[s,s,s]) for i,(x,z,s) in enumerate(points)]
def scene(key,name,items,theme,footprint,notes):
    da('scene-'+key,name,'terrain',items,'scenes',theme,level=4,budget=250000,
       metadata={'stage':'D' if key in ('medieval','castle','dungeon','industrial') else 'E',
         'scene':{'footprint':footprint,'units':'m','camera_hint':{'azimuth':35,'elevation':38},'walkable_route':notes,'placement':'curated metres; no seeded noise or exported meshes','navigation_mesh':False}},
       description='场景搭建与比例验证配方，全部引用正式组件。导出不包含寻路、关卡逻辑或物理求解器。',tags=['场景','可编辑','比例验证'])

def author():
    village=[*paving(10,9),ai('homeL','exp-arch-timber_house',[-5.8,0,-4.8],rot=[0,12,0]),ai('homeR','exp-arch-timber_house',[5.6,0,-4.9],rot=[0,-12,0],scale=[.88,.90,.88]),ai('marketA','exp-arch-market_stall',[-5.2,0,3.1],rot=[0,22,0]),ai('marketB','exp-arch-market_stall',[5.2,0,3.1],rot=[0,-22,0]),ai('merchant','exp-character-merchant',[-3.6,0,2.2]),ai('guard','exp-character-guard',[1.7,0,-1.8]),ai('lantern','world-lantern',[1.45,.7,1.5]),pi('pedestal','exp.arch.foundation',[0,0,1.6],scale=[.56,.55,.56]),pi('basin','exp.interior.basin',[0,.2,1.6],scale=[1.4,1.4,1.4]),*[ai('supply'+str(i),'world-supply-crate',[x,0,z]) for i,(x,z) in enumerate([(-6.8,4.8),(-6.0,5.9),(6.5,5.2)])],*trees([(-8.3,-6,.75),(8.2,-6.5,.75),(8,6,.62),(-8,6,.65)])]
    village += [pi('planter'+str(i),'exp.nature.undergrowth',[x,.015,z],scale=[1.7,1,1.2]) for i,(x,z) in enumerate([(-8.7,-2),(8.7,-2),(-8.2,7),(8.2,7)])]
    scene('medieval','中世纪村庄 · 住宅、集市与水台',village,'medieval',[20,18],'central plaza and front approach remain open; houses rear, stalls sides')
    castle=[*paving(10,10),ai('gate','exp-arch-gatehouse',[0,0,-7.1],rot=[0,180,0]),ai('towerL','exp-arch-watchtower',[-7.5,0,-6.9]),ai('towerR','exp-arch-watchtower',[7.5,0,-6.9]),*[ai('wall'+str(s)+str(j),'exp-arch-fortress_wall',[s*8.5,0,-3.5+2.0*j],rot=[0,90,0]) for s in [-1,1] for j in range(6)],*[ai('rearcurtain'+str(s),'exp-arch-fortress_wall',[s*5.9,0,-7.1]) for s in [-1,1]],ai('guardL','exp-character-guard',[-1.7,0,-4.8]),ai('guardR','exp-character-guard',[1.7,0,-4.8]),ai('store','exp-arch-market_stall',[-5.7,0,5.4],rot=[0,35,0]),pi('flag','exp.game.checkpoint_flag',[5.7,0,5.0]),ai('weapons','exp-wear-melee',[-5.4,.75,5.2]),ai('repair','exp-interior-workbench_cell',[5.1,0,.3],rot=[0,-90,0]),*trees([(-6.1,6.8,.50),(6.1,6.8,.50)],'exp-spruce')]
    scene('castle','城堡庭院 · 城门、围墙与守备工坊',castle,'castle',[20,20],'central gate axis 4m clear; wall and tower colliders separate from apertures')
    dungeon=[*paving(9,9),ai('entry','exp-arch-gate_bridge',[0,0,-3.9]),pi('arch','exp.arch.cave_vault',[0,0,-5.5],scale=[1.8,1.55,1.7]),*[pi('buttress'+str(s),'exp.arch.buttress',[s*3.5,0,-4.7],scale=[1.5,1.25,1.5]) for s in [-1,1]],*[pi('wall'+str(i),'exp.arch.dungeon_wall',[x,0,-7.8]) for i,x in enumerate([-7,-5,-3,3,5,7])],ai('crystalL','exp-biome-cave',[-5.8,0,-.8],scale=[.58,.58,.58]),ai('crystalR','exp-biome-cave',[5.8,0,-.8],scale=[.58,.58,.58]),ai('lever','exp-game-lever_switch',[-3,0,-1.1]),ai('gatekeeper','exp-creature-skeleton_guard',[2.6,0,-1]),ai('portal','exp-game-teleporter',[0,0,4]),ai('mage','exp-character-wizard',[-2.8,0,3.7]),*[ai('lantern'+str(i),'world-lantern',[x,.6,z],scale=[1.2,1.2,1.2]) for i,(x,z) in enumerate([(-2,-3.4),(2,-3.4)])]]
    scene('dungeon','地下城入口 · 石拱、闸门与传送祭台',dungeon,'dungeon',[18,18],'front portal plaza feeds a clear 2m doorway; side crystals are not placed in the passage')
    industry=[*paving(12,11),ai('line','exp-industry-production_line',[0,0,-1.4]),ai('water','exp-industry-water_treatment',[-6.6,0,-6.0]),ai('power','exp-industry-substation',[6.7,0,-6.0]),ai('dock','exp-industry-loading_dock',[-6,0,4.2]),ai('robot','exp-robot-workcell',[6.0,0,3.5]),ai('operator','exp-character-miner',[3.0,0,3.1]),*[pi('light'+str(j),'exp.arch.column',[x,0,z],scale=[.30,1.1,.30]) for j,(x,z) in enumerate([(-10,-8.5),(10,-8.5)])],*[pi('cabinet'+str(j),'exp.industry.switchgear',[7.7,0,-.3+1.2*j],rot=[0,-90,0]) for j in range(2)]]
    scene('industrial','工业生产基地 · 物流、加工与公用工程',industry,'industrial',[24,22],'conveyors central; utilities rear; loading and manipulator cells separated by an operator aisle')
    # Rail top is +.338m. Bogie contact was authored to meet it, no arbitrary train scaling.
    rail=[*paving(13,17)]
    for j,x in enumerate([-4.5,1.0]):
        for k,z in enumerate(range(-12,13,4)):
            if j==1 and k==6:rail.append(mate('curved_exit','exp.transport.rail_curve','rail1_5'))
            else:rail.append(pi(f'rail{j}_{k}','exp.transport.rail_straight',[x,0,z]))
    rail += [ai('locomotive','exp-transport-shunter',[-4.5,0,7.0]),ai('freight','exp-transport-freight_wagon',[-4.5,0,-.4]),ai('freight2','exp-transport-freight_wagon',[-4.5,0,-7.5]),ai('coach','exp-transport-passenger_coach',[1,0,2]),ai('platform','exp-transport-platform',[1.32,0,-2]),ai('shed','exp-arch-residence',[9,0,-8.4],rot=[0,-90,0]),ai('racks','exp-interior-warehouse_bay',[8.5,0,.5],rot=[0,-90,0]),ai('truck','exp-transport-flatbed_trailer',[9,0,8.2]),*[ai('crate'+str(i),'world-supply-crate',[x,0,z]) for i,(x,z) in enumerate([(7.6,-3.5),(8.8,-3.5),(7.6,-2.1),(9,4.3)])],*trees([(-11.5,-11,.6),(-11.5,10.5,.6),(11.5,12,.6)])]
    scene('rail','铁路货运站 · 双线停靠与仓储装卸',rail,'rail',[26,34],'1.435m gauge; adjacent track centres 5.5m; warehouse to the right, clear central service corridor')
    airport=[*paving(18,18)]
    airport += [pi('threshold','exp.transport.runway',[0,.013,-11]),pi('apron','exp.transport.runway',[0,.013,1],rot=[0,180,0]),ai('plane','exp-transport-propeller_plane',[-6,0,2.0],rot=[0,20,0]),ai('jet','exp-transport-jet',[5.6,0,-2.2],rot=[0,-25,0]),ai('helicopter','exp-transport-helicopter',[7,0,11.7],rot=[0,-30,0]),ai('service','exp-transport-ground_service',[-10,0,10.8]),ai('terminal','exp-arch-residence',[-11,0,-10.7],rot=[0,90,0]),ai('pilot','exp-character-pilot',[-5,0,7.3]),pi('signal','exp.transport.signal_bar',[-8.0,.45,-12]),*[pi('light'+str(i),'exp.game.pickup',[x,.02,z],scale=[.12,.12,.12]) for i,(x,z) in enumerate([(x,z) for x in [-11.2,11.2] for z in [-15,-10,-5,0,5]])]]
    scene('airport','机场停机坪 · 固定翼、旋翼与地勤',airport,'airport',[36,36],'aircraft remain at authored metre scale; central apron, rear threshold, terminal and ground service to the sides')
