"""Species-specific profiles; source limbs are merged into one shared rig."""
from .common import *
def author():
 # Cat: broad cheek planes, short muzzle, digitigrade hind leg, lifted tail.
 part('core.animal.cat.torso','猫躯干 · 胸廓 / 腰腹 / 肩胛','animal',[
  loft([[0,.265,-.31,.105,.117],[0,.27,-.21,.143,.149],[0,.275,.035,.125,.142],[0,.296,.22,.105,.143],[0,.31,.275,.087,.106]],'#D38A43',10,bone='body'),
  loft([[0,.203,.13,.075,.075],[0,.27,.253,.075,.095],[0,.36,.277,.063,.077]],'cream',8,bone='chest')
 ],[.29,.45,.64],material='mat.fur')
 part('core.animal.cat.foreleg','猫前肢 · 肩腕连续','animal',[
  profile([{'c':[0,0,0],'r':[.046,.049],'bone':'leg'},{'c':[0,-.115,.009],'r':[.032,.035],'bone':'leg'},{'c':[0,-.19,.014],'r':[.026,.029],'weights':{'leg':.3,'knee':.7}},{'c':[0,-.268,.024],'r':[.023,.027],'bone':'knee'}],'#CC873E',preserve_ends=True)
 ],[.092,.268,.1],anchor='top',material='mat.fur')
 part('core.animal.cat.hindleg','猫后肢 · 大腿 / 跗部曲线','animal',[
  profile([{'c':[0,0,0],'r':[.072,.074],'bone':'leg'},{'c':[0,-.082,.044],'r':[.060,.062],'bone':'leg'},{'c':[0,-.138,.037],'r':[.034,.04],'weights':{'leg':.5,'knee':.5}},{'c':[0,-.21,-.02],'r':[.024,.03],'bone':'knee'},{'c':[0,-.27,.014],'r':[.023,.026],'bone':'knee'}],'#D18A43',preserve_ends=True)
 ],[.144,.27,.16],anchor='top',material='mat.fur')
 part('core.animal.cat.paw','猫爪掌 · 圆钝支撑面','animal',[
  profile([[0,.006,.018,.034,.049],[0,.029,.024,.037,.047],[0,.053,.005,.025,.029]],'cream')
 ],[.075,.053,.097],material='mat.fur',ports=[port('sole',[0,.006,0],(0,-1,0),interface='ground')])
 part('core.animal.cat.head','猫头部 · 颊面 / 短吻 / 立耳','animal',[
  profile([[0,-.081,.008,.065,.063],[0,-.046,.008,.099,.077],[0,.014,-.003,.105,.078],[0,.07,-.009,.081,.068],[0,.083,-.017,.056,.048]],'#DB944B'),
  *[ico([.080,.067,.046],'cream',[sg*.037,-.039,.071],detail=0) for sg in [-1,1]],
  poly([[-.018,-.021,.109],[.018,-.021,.109],[0,-.04,.116],[-.012,-.027,.092],[.012,-.027,.092]],[[0,1,2],[0,3,4,1],[0,2,3],[1,4,2],[2,4,3]],'#7B4E44'),
  *[box([.03,.023,.012],'ink',[sg*.057,.015,.069],bevel=.006,rotation=[0,sg*24,sg*-9]) for sg in [-1,1]],
  *[poly([[sg*.035,.055,-.04],[sg*.103,.031,-.025],[sg*.085,.167,-.013],[sg*.037,.058,.012],[sg*.105,.035,.015]],[[0,1,2],[3,2,4],[0,2,3],[1,4,2],[0,3,4,1]],'#D38A43') for sg in [-1,1]],
  *[poly([[sg*.048,.068,.015],[sg*.092,.049,.015],[sg*.083,.133,.001]],[[0,1,2]],'#D3A391') for sg in [-1,1]]
 ],[.214,.25,.20],anchor='center',material='mat.fur',ports=[port('neck',[0,-.045,-.03],(0,-1,0),interface='cat.neck.v1')])
 part('core.animal.cat.tail','猫尾巴 · 弯曲段与尾尖','animal',[
  loft([[0,0,0,.036,.035],[0,.04,-.11,.039,.038],[.018,.13,-.20,.035,.033],[.048,.245,-.245,.029,.030],[.067,.32,-.23,.02,.022],[.064,.355,-.209,.01,.012]],'#CF8740',7,bone='tail',preserve_ends=True)
 ],[.13,.39,.29],anchor='center',material='mat.fur')
 catRig=[{'name':'body','position':[0,.27,0]},{'name':'chest','parent':'body','position':[0,.31,Q('catFront')]},{'name':'head','parent':'chest','position':[0,.425,add(Q('catFront'),.065)]},{'name':'tail','parent':'body','position':[0,.31,mul(-.29,Q('body_length'))]}]
 # Values used by rig and source modules come from the same expression.
 L=Q('body_length');front=mul(.22,L);back=mul(-.22,L)
 catRig[1]['position'][2]=front;catRig[2]['position'][2]=add(front,.065)
 comps=[component('torso','core.animal.cat.torso',scale=[1,1,L]),component('tail','core.animal.cat.tail',[0,.31,mul(-.29,L)])]
 for suf,x,z,typ in [('FL',-.077,front,'foreleg'),('FR',.077,front,'foreleg'),('HL',-.10,back,'hindleg'),('HR',.10,back,'hindleg')]:
  catRig += [{'name':'leg'+suf,'parent':'body','position':[x,.305,z]},{'name':'knee'+suf,'parent':'leg'+suf,'position':[x,.16,add(z,.014)]}]
  comps += [component(suf,'core.animal.cat.'+typ,[x,.305,z],bind={'leg':'leg'+suf,'knee':'knee'+suf}),component('paw'+suf,'core.animal.cat.paw',[x,0,add(z,.016)],bone='knee'+suf)]
 part('core.animal.cat.body','猫身体总成 · 共享骨架 / 可复用四肢','animal',size=[.34,.62,.96],components=comps,rig=catRig,level=2,params=schema(body_length=number(1,.88,1.14,'躯干长度比例')),material='mat.fur')
 assembly('fnd-cat','猫母版 · 橘白短毛','animal',[inst('skin','core.animal.cat.body',params={'body_length':L}),inst('head','core.animal.cat.head',parent='skin.rig.head')],params=schema(body_length=number(1,.88,1.14,'躯干长度比例')))
 # Horse: a distinct barrel/neck and equine distal limb, never a stretched cat.
 part('core.animal.horse.torso','马躯干 · 臀 / 腹线 / 马肩隆','animal',[
  loft([[0,1.12,-.69,.215,.275],[0,1.16,-.52,.315,.335],[0,1.15,-.17,.327,.319],[0,1.20,.23,.29,.326],[0,1.26,.49,.242,.282],[0,1.29,.59,.19,.213]],'#A5754F',10,bone='body'),
  loft([[0,.99,.29,.20,.14],[0,1.17,.53,.18,.22],[0,1.37,.58,.155,.18]],'#B4865B',8,bone='chest')
 ],[.655,1.55,1.3],material='mat.fur')
 part('core.animal.horse.neck','马颈 · 倾斜颈肌与鬐甲','animal',[
  profile([{'c':[0,0,0],'r':[.217,.197],'bone':'chest'},{'c':[0,.20,.095],'r':[.18,.19],'weights':{'chest':.45,'neck':.55}},{'c':[0,.40,.21],'r':[.13,.144],'bone':'neck'},{'c':[0,.52,.23],'r':[.105,.125],'bone':'head'}],'#AD7B51')
 ],[.44,.57,.64],material='mat.fur')
 part('core.animal.horse.foreleg','马前肢 · 肩肘 / 管骨 / 球节','animal',[
  profile([{'c':[0,0,0],'r':[.116,.115],'bone':'leg'},{'c':[0,-.22,-.005],'r':[.083,.093],'bone':'leg'},{'c':[0,-.46,.01],'r':[.055,.057],'weights':{'leg':.4,'knee':.6}},{'c':[0,-.61,.027],'r':[.043,.05],'bone':'knee'},{'c':[0,-.86,.023],'r':[.038,.046],'bone':'knee'},{'c':[0,-.95,.041],'r':[.055,.06],'bone':'knee'}],'#A2734F',preserve_ends=True),
  profile([[0,-.885,.023,.041,.048],[0,-1.052,.042,.055,.060]],'cream',bone='knee')
 ],[.233,1.06,.26],anchor='top',material='mat.fur')
 part('core.animal.horse.hindleg','马后肢 · 臀腿 / 飞节 / 系部','animal',[
  profile([{'c':[0,0,0],'r':[.161,.172],'bone':'leg'},{'c':[0,-.20,.075],'r':[.12,.145],'bone':'leg'},{'c':[0,-.39,.12],'r':[.072,.089],'weights':{'leg':.5,'knee':.5}},{'c':[0,-.63,-.008],'r':[.045,.052],'bone':'knee'},{'c':[0,-.75,-.059],'r':[.042,.046],'bone':'knee'},{'c':[0,-1.03,-.023],'r':[.048,.055],'bone':'knee'}],'#A2734F',preserve_ends=True)
 ],[.322,1.06,.42],anchor='top',material='mat.fur')
 part('core.animal.horse.hoof','马蹄 · 蹄壁与着地面','animal',[
  profile([[0,.01,.019,.075,.098],[0,.057,.024,.073,.093],[0,.135,-.006,.051,.065]],'woodDark')
 ],[.15,.135,.196],material='mat.hoof',ports=[port('sole',[0,.01,0],(0,-1,0),interface='ground')])
 part('core.animal.horse.head','马头 · 额骨 / 鼻梁 / 宽钝口鼻','animal',[
  loft([[0,.075,-.075,.104,.15],[0,.085,.04,.117,.162],[0,-.026,.19,.10,.135],[0,-.136,.37,.079,.095],[0,-.14,.43,.086,.079]],'#B6875D',8),
  loft([[0,-.145,.347,.081,.067],[0,-.158,.424,.091,.07],[0,-.14,.457,.077,.055]],'cream',8),
  *[box([.03,.024,.01],'ink',[sg*.084,-.135,.419],bevel=.006,rotation=[0,sg*45,0]) for sg in [-1,1]],
  *[ico([.028,.027,.018],'ink',[sg*.108,.099,.067],detail=0) for sg in [-1,1]],
  *[profile([[sg*.076,.18,-.024,.037,.034],[sg*.092,.30,-.030,.031,.026],[sg*.089,.352,-.022,.009,.012]],'#9D704E') for sg in [-1,1]],
  poly([[-.020,.20,.062],[.020,.20,.062],[.03,.058,.183],[-.025,-.039,.25]],[[0,1,2,3]],'cream')
 ],[.24,.59,.56],anchor='center',material='mat.fur',ports=[port('neck',[0,0,-.045],(0,0,-1),interface='horse.neck.v1')])
 part('core.animal.horse.mane','马鬃 · 颈后折面带','animal',[
  poly([[-.027,.07,-.196],[.027,.07,-.196],[-.022,.53,.114],[.022,.53,.114],[-.064,.04,-.221],[.067,.035,-.216],[-.055,.47,.061],[.048,.48,.064]],[[0,1,3,2],[0,2,6,4],[1,5,7,3],[4,6,7,5],[2,3,7,6]],'hair'),
  profile([[0,.5,.106,.043,.048],[0,.60,.09,.036,.041],[0,.65,.08,.016,.022]],'hair')
 ],[.14,.70,.39],material='mat.hair')
 part('core.animal.horse.tail','马尾 · 尾根与宽束尾毛','animal',[
  loft([[0,0,0,.075,.066],[0,-.12,-.10,.078,.069],[.022,-.33,-.17,.074,.073],[.035,-.59,-.193,.068,.060],[.033,-.73,-.18,.053,.043],[.026,-.79,-.156,.015,.026]],'hair',8,bone='tail')
 ],[.18,.81,.33],anchor='top',material='mat.hair')
 horseRig=[{'name':'body','position':[0,1.18,0]},{'name':'chest','parent':'body','position':[0,1.27,mul(.49,L)]},{'name':'neck','parent':'chest','position':[0,1.58,add(mul(.49,L),.18)]},{'name':'head','parent':'neck','position':[0,1.75,add(mul(.49,L),.30)]},{'name':'tail','parent':'body','position':[0,1.35,mul(-.64,L)]}]
 comps=[component('barrel','core.animal.horse.torso',scale=[1,1,L]),component('neck','core.animal.horse.neck',[0,1.20,mul(.49,L)]),component('tail','core.animal.horse.tail',[0,1.35,mul(-.64,L)])]
 for suf,x,z,typ in [('FL',-.188,mul(.46,L),'foreleg'),('FR',.188,mul(.46,L),'foreleg'),('HL',-.205,mul(-.49,L),'hindleg'),('HR',.205,mul(-.49,L),'hindleg')]:
  horseRig.extend([{'name':'leg'+suf,'parent':'body','position':[x,1.14,z]},{'name':'knee'+suf,'parent':'leg'+suf,'position':[x,.68,add(z,.02)]}])
  comps += [component(suf,'core.animal.horse.'+typ,[x,1.14,z],bind={'leg':'leg'+suf,'knee':'knee'+suf}),component('hoof'+suf,'core.animal.horse.hoof',[x,0,add(z,.039 if typ=='foreleg' else -.014)],bone='knee'+suf)]
 part('core.animal.horse.body','马身体总成 · 四肢与颈部统一骨架','animal',size=[.74,1.85,2.25],components=comps,rig=horseRig,level=2,params=schema(body_length=number(1,.9,1.10,'马躯干长度比例')),material='mat.fur')
 # Saddle is reusable as a tack set and is not baked into the horse anatomy.
 part('core.wear.saddle','骑乘鞍具 · 鞍垫 / 鞍桥 / 挂袋','wear',[
  profile([[0,-.22,0,.33,.25],[0,-.07,0,.35,.26],[0,.027,0,.25,.23]],'navy'),
  profile([[0,.014,0,.224,.196],[0,.055,0,.20,.178]],'woodDark'),
  box([.33,.13,.054],'wood',[0,.075,.18],bevel=.022),box([.37,.10,.047],'wood',[0,.064,-.18],bevel=.017),
  *[box([.10,.24,.24],'wood',[sg*.321,-.16,-.075],bevel=.022) for sg in [-1,1]],
  *[box([.012,.32,.039],'woodDark',[sg*.353,-.18,.052],bevel=.004) for sg in [-1,1]]
 ],[.79,.49,.53],anchor='center',material='mat.leather')
 assembly('fnd-horse','马母版 · 温血乘骑马','animal',[inst('skin','core.animal.horse.body',params={'body_length':L}),inst('head','core.animal.horse.head',parent='skin.rig.head'),inst('mane','core.animal.horse.mane',pos=[0,1.20,mul(.49,L)]),inst('saddle','core.wear.saddle',pos=[0,1.48,-.12])],params=schema(body_length=number(1,.9,1.10,'躯干长度比例')))
 for ident in ['fnd-cat','fnd-horse']:
  tracks=[]
  for suf,sg in [('FL',1),('FR',-1),('HL',-1),('HR',1)]:tracks += [track('skin.rig.leg'+suf,[1,0,0],[sg*11,-sg*11,sg*11]),track('skin.rig.knee'+suf,[1,0,0],[0,17,0] if sg==1 else [17,0,17])]
  clip(ident,[{'name':'Gait inspection','duration':1.35,'tracks':tracks},{'name':'Head inspection','duration':2.5,'tracks':[track('skin.rig.head',[1,0,0],[0,16,0]),track('skin.rig.tail',[0,1,0],[-8,8,-8])]}])
