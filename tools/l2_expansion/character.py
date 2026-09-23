"""60 rigid character accessory and garment modules (not skinned characters)."""
from .common import *
D='character'

def author():
    for key in ids(D,'hair'):
        items=[p('hair',D,'hair',key,[.26,.32,.18],[0,.12,0]),
               p('band',D,'clothing','belt',[.28,.025,.20],[0,.26,0]),
               p('pin','props','fastener','rivet',[.018,.035,.018],[0,.31,.096],optional=True)]
        if key in ('ponytail','braid','bun'):
            items.append(p('tie',D,'clothing','sash',[.035,.12,.035],[0,.22,.04]))
        elif key in ('bob','fringe'):
            items.extend(p('lock'+str(i),D,'hair','side_lock',[.048,.21,.07],[x,.17,.045]) for i,x in enumerate([-.10,.10]))
        elif key=='crest':items.append(p('rear',D,'hair','side_lock',[.1,.14,.09],[0,.1,-.07]))
        register(D,'hairmount',key,label(pid(D,'hair',key))+'发饰安装组',items,[.3,.48,.24],mount=[.20,.12],collision={'type':'none'},
                 notes=['刚性饰件，安装框位于颅顶局部；不含头骨、发丝物理或蒙皮。'])
    for key in ids(D,'face'):
        items=[p('feature',D,'face',key,[.18,.16,.07],[0,.04,.045]),
               p('backing',D,'face','mask' if key!='mask' else 'jaw',[.20,.16,.045],[0,.03,0]),
               p('mountL',D,'clothing','sash',[.018,.025,.13],[-.1,.10,-.04]),
               p('mountR',D,'clothing','sash',[.018,.025,.13],[.1,.10,-.04])]
        if key=='mask':items.append(p('vent','industry','power','fan_guard',[.09,.06,.016],[0,.09,.081],[90,0,0],optional=True))
        register(D,'facialpiece',key,label(pid(D,'face',key))+'脸部覆盖组',items,[.22,.23,.22],mount=[.16,.10],collision={'type':'none'},
                 notes=['无表情 blendshape；需按消费者角色脸型调整挂点，不宣称全角色通用。'])
    for key in ids(D,'clothing'):
        items=[p('cloth',D,'clothing',key,[.40,.42,.12],[0,.05,0]),
               p('binding',D,'clothing','belt' if key!='belt' else 'sash',[.42,.035,.13],[0,.38,0]),
               p('clasp','props','fastener','rivet',[.025,.028,.025],[0,.39,.072],optional=True)]
        if key=='pocket':items.append(p('flap',D,'clothing','collar_lapel',[.38,.10,.025],[0,.34,.06]))
        elif key in ('cape_panel','hood','sleeve_cap'):items.append(p('seam',D,'clothing','sash',[.025,.38,.026],[-.18,.08,.052]))
        elif key in ('collar_lapel','collar_stand'):items.append(p('tie',D,'clothing','sash',[.055,.20,.035],[0,.08,.07]))
        elif key in ('skirt_panel','sash'):items.append(p('edge',D,'clothing','cuff',[.38,.03,.12],[0,.05,0]))
        register(D,'garment',key,label(pid(D,'clothing',key))+'缝合饰边模块',items,[.45,.50,.16],mount=[.36,.10],collision={'type':'none'},
                 notes=['刚性服装分片与饰边；非布料模拟、非可直接套用任意骨架的服装。'])
    for key in ids(D,'armor'):
        items=[p('shell',D,'armor',key,[.38,.42,.18],[0,.08,0],moving=key=='helmet_visor',collision={'type':'none'}),
               p('lining',D,'clothing','cuff',[.34,.06,.16],[0,.075,0]),
               p('strap',D,'clothing','belt',[.40,.045,.20],[0,.18,0]),
               *fasteners('rivet',[[-.14,.31,.082],[.14,.31,.082]],.026,part='rivet')]
        if key in ('greave','vambrace'):items.append(p('strap2',D,'clothing','belt',[.38,.035,.19],[0,.38,0]))
        register(D,'armor',key,label(pid(D,'armor',key))+'衬里束带组',items,[.42,.52,.23],mount=[.30,.14],collision={'type':'none'},
                 controls=[control('visor','shell','面甲抬起',95,axis=(1,0,0))] if key=='helmet_visor' else [],notes=['刚性装备，消费者负责骨骼挂接和角色碰撞。'])
    for key in ids(D,'handfoot'):
        if key.startswith('glove') or key=='wrist_wrap':
            items=[p('palm',D,'handfoot','glove_palm',[.11,.16,.045],[0,.03,0]),
                   p('fingers',D,'handfoot','glove_fingers',[.105,.10,.04],[0,.17,0]),
                   p('wrap',D,'handfoot','wrist_wrap',[.115,.055,.06]),
                   p('feature',D,'handfoot',key,[.09,.07,.04],[0,.10,.025])]
        else:
            items=[p('sole',D,'handfoot','boot_sole',[.15,.04,.28]),p('toe',D,'handfoot','boot_toe',[.145,.12,.17],[0,.025,.065]),
                   p('strap',D,'handfoot','sandal_strap',[.15,.09,.19],[0,.04,-.015])]
            if key=='boot_sole':items.append(p('heel',D,'handfoot','boot_sole',[.14,.035,.09],[0,-.025,-.085]))
            elif key=='boot_toe':items.append(p('ankle',D,'clothing','cuff',[.14,.12,.13],[0,.065,-.06]))
            else:items.append(p('rearstrap',D,'handfoot','sandal_strap',[.15,.075,.12],[0,.04,-.075]))
        register(D,'extremity',key,label(pid(D,'handfoot',key))+'穿戴组合',items,[.17,.3,.3],mount=[.11,.08],collision={'type':'none'},notes=['单侧模块，不计镜像副本；不是可弯曲手指或脚掌。'])
    # Each service kit has different functional contents, not merely colours or titles.
    kits=[('carpenter','木工腰挂', [('toolhead','hammer'),('toolhead','chisel'),('handle','tool_grip')]),
          ('gardener','园艺工具挂组',[('toolhead','trowel'),('toolhead','pruner'),('container','pouch')]),
          ('miner','采矿工具背挂',[('toolhead','pickaxe'),('lamp','lantern'),('handle','tool_grip')]),
          ('medic','医护腰挂',[('medical','bandage'),('medical','vial'),('medical','scissors')]),
          ('surveyor','勘测胸挂',[('office','compass'),('office','clipboard'),('office','pencil')]),
          ('mechanic','维修腰挂',[('toolhead','wrench'),('toolhead','pliers'),('fastener','hex_bolt')]),
          ('electrician','电工工具挂组',[('toolhead','screwdriver'),('toolhead','snips'),('device','multimeter')]),
          ('courier','递送腰挂',[('container','satchel'),('office','scroll'),('office','stamp')]),
          ('cook','厨具围腰组',[('toolhead','cleaver'),('vessel','ladle'),('vessel','cup')]),
          ('scribe','文书胸挂',[('office','pen'),('office','scroll'),('office','book')]),
          ('musician','乐器附件挂组',[('musical','flute'),('musical','bell'),('musical','drumstick')]),
          ('archivist','档案腰挂',[('office','book'),('office','binder'),('office','magnifier')]),
          ('diver','潜水仪具背挂',[('device','gauge'),('lamp','torch'),('container','canister')]),
          ('explorer','探险背挂',[('office','compass'),('lamp','torch'),('vessel','bottle')]),
          ('fisher','垂钓腰挂',[('toolhead','hook'),('container','creel'),('handle','crank')]),
          ('mason','砌筑工具挂组',[('toolhead','trowel'),('toolhead','mallet'),('office','ruler')]),
          ('tailor','缝纫工具挂组',[('office','scissors'),('office','ruler'),('fastener','pin')]),
          ('painter','绘画围腰组',[('toolhead','brush'),('vessel','jar'),('office','clipboard')]),
          ('locksmith','锁匠腰挂',[('toolhead','file'),('toolhead','pliers'),('fastener','split_pin')]),
          ('signal','通信肩挂',[('device','radio'),('device','antenna'),('lamp','beacon')]),
          ('botanist','植物采样腰挂',[('medical','vial'),('office','magnifier'),('container','pouch')]),
          ('traveller','旅行挂组',[('container','satchel'),('vessel','flask'),('office','scroll')])]
    # Explicit substitutions map vocabulary to the library's authored semantic IDs.
    aliases={('toolhead','pruner'):('toolhead','snip'),('toolhead','pickaxe'):('toolhead','pick'),
             ('toolhead','screwdriver'):('toolhead','awl'),('toolhead','snips'):('toolhead','snip'),
             ('toolhead','pliers'):('toolhead','plier'),('toolhead','cleaver'):('toolhead','scraper'),
             ('toolhead','hook'):('fastener','hook'),('handle','tool_grip'):('handle','wrapped'),
             ('container','pouch'):('container','pouch_shell'),('container','satchel'):('container','pack_shell'),
             ('container','creel'):('container','basket_wall'),('container','canister'):('container','can_body'),
             ('medical','bandage'):('medical','bandage_roll'),('medical','scissors'):('medical','forceps'),
             ('office','compass'):('narrative','compass_case'),('office','pencil'):('office','pencil_core'),
             ('office','scroll'):('office','scroll_core'),('office','book'):('office','book_block'),
             ('office','binder'):('office','binder_ring'),('office','pen'):('office','pen_barrel'),
             ('office','scissors'):('office','scissors_loop'),('device','multimeter'):('device','screen_bezel'),
             ('device','gauge'):('device','control_knob'),('device','radio'):('device','radio_grille'),
             ('device','antenna'):('musical','flute_tube'),('musical','flute'):('musical','flute_tube'),
             ('musical','drumstick'):('musical','peg'),('vessel','ladle'):('vessel','mortar'),
             ('vessel','jar'):('vessel','urn'),('lamp','lantern'):('lamp','lantern_frame'),
             ('lamp','torch'):('lamp','cage'),('lamp','beacon'):('lamp','diffuser'),
             ('fastener','pin'):('fastener','clevis_pin'),('fastener','split_pin'):('fastener','cotter')}
    for key,title,contents in kits:
        items=[p('belt',D,'clothing','belt',[.44,.055,.23],[0,.26,0]),
               p('backing',D,'clothing','pocket',[.35,.28,.08],[0,.03,.095]),
               p('clasp','gameplay','lock','keeper',[.055,.065,.035],[0,.255,.13])]
        for j,(group,itemkey) in enumerate(contents):
            group,itemkey=aliases.get((group,itemkey),(group,itemkey))
            items.append(p('content'+str(j),'robot' if (key=='signal' and j==1) else 'props','sensor' if (key=='signal' and j==1) else group,'antenna' if (key=='signal' and j==1) else itemkey,[.08,.20,.06],[(j-1)*.115,.075,.155],rot=[0,0,(j-1)*-9]))
            items.append(p('loop'+str(j),D,'clothing','cuff',[.095,.045,.06],[(j-1)*.115,.17,.155]))
        register(D,'servicekit',key,title,items,[.48,.36,.26],mount=[.36,.14],collision={'type':'none'},
                 function=title+'：腰带、承托口袋、独立工具和固定环，不包含完整角色或工具行为。')
