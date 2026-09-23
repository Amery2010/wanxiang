"""Species-specific silhouettes. Coat markings colour the existing surface, never shells."""
from .common import *
def author():
 h=Q('length');r=Q('thickness');b=Q('bend')
 wp('w.fauna.hoofleg','有蹄动物腿 · 肌肉、跗部与蹄部接口','animal',[
  profile([{'c':[0,0,0],'r':[mul(r,1.35),mul(r,1.45)],'weights':{'body':.75,'leg':.25}}, {'c':[0,mul(-.25,h),mul(.55,b)],'r':[mul(r,1.30),mul(r,1.35)],'weights':{'body':.20,'leg':.80}}, {'c':[0,mul(-.52,h),b],'r':[r,mul(r,1.10)],'weights':{'leg':.5,'knee':.5}}, {'c':[0,mul(-.73,h),neg(b)],'r':[mul(r,.76),r],'bone':'knee'}, {'c':[0,neg(h),0],'r':[mul(r,.90),r],'bone':'knee'}],'wood',preserve_ends=True)
 ],[.21,.9,.22],anchor='top',params=schema(length=number(.83,.27,1.30,'腿长',.01,'m'),thickness=number(.05,.025,.10,'管骨半径',.005,'m'),bend=number(.045,0,.10,'跗部后折',.005,'m')),material='mat.fur')
 wp('w.fauna.hoof','偶蹄支撑部 · 裂缝与蹄壁','animal',[profile([[0,.006,.012,.065,.075],[0,.036,.02,.069,.075],[0,.104,0,.047,.053]],'woodDark'),box([.007,.039,.057],'ink',[0,.026,.06],bevel=.002)],[.14,.105,.16],material='mat.hoof')
 wp('w.fauna.canine_leg','犬科肢体 · 趾行曲线','animal',[profile([{'c':[0,0,0],'r':[.073,.078],'bone':'leg'},{'c':[0,-.14,.022],'r':[.052,.05],'bone':'leg'},{'c':[0,-.22,0],'r':[.032,.036],'weights':{'leg':.35,'knee':.65}},{'c':[0,-.4,.018],'r':[.025,.03],'bone':'knee'}],'orange',preserve_ends=True)],[.15,.41,.17],anchor='top',material='mat.fur')
 wp('w.fauna.canine_paw','犬科足掌 · 趾端支撑','animal',[profile([[0,.003,.026,.041,.065],[0,.032,.035,.044,.060],[0,.071,.005,.028,.031]],'woodDark')],[.095,.073,.14],material='mat.fur')
 wp('w.fauna.antlers','鹿角 · 主枝与分叉','animal',[*[rod([sg*.07,.04,0],[sg*.16,.37,-.055],.023,'woodDark',.013,6) for sg in [-1,1]],*[rod([sg*.16,.31,-.05],[sg*.33,.60,-.05],.014,'woodDark',.004,5) for sg in [-1,1]],*[rod([sg*.19,.37,-.05],[sg*.11,.56,.015],.013,'woodDark',.004,5) for sg in [-1,1]],*[rod([sg*.24,.47,-.05],[sg*.39,.54,-.08],.01,'woodDark',.003,5) for sg in [-1,1]]],[.8,.63,.15],anchor='center',material='mat.hoof')
 wp('w.fauna.horns','短角 · 弯曲双角','animal',[loft([[sg*.085,0,0,.033,.033],[sg*.16,.09,-.035,.026,.025],[sg*.14,.18,-.06,.010,.009]],'cream',7) for sg in [-1,1]],[.36,.2,.14],anchor='center',material='mat.hoof')
 def hoofed(id,name,height,length,width,color,head_type,theme='farm'):
  front=length*.28;back=-length*.28;shoulder=height+.15;leg=shoulder-.08;L=Q('body_length')
  # Continuous barrel->chest->neck control surface; never a row of overlapping spheres.
  rings=[{'c':[0,height+.14,-length*.49],'r':[width*.62,height*.22],'bone':'body'}, {'c':[0,height+.17,-length*.31],'r':[width,height*.31],'bone':'body'}, {'c':[0,height+.15,0],'r':[width*1.04,height*.30],'bone':'body'}, {'c':[0,height+.21,length*.28],'r':[width*.86,height*.29],'weights':{'body':.4,'chest':.6}}, {'c':[0,height+.33,length*.42],'r':[width*.65,height*.26],'bone':'chest'}, {'c':[0,height+.53,length*.50],'r':[width*.39,height*.19],'weights':{'chest':.6,'head':.4}}]
  torso=[loft(rings,color,10)]
  if id=='cow':torso[0]['color_regions']=[{'center':[width*.8,height+.20,-length*.24],'radii':[width*.9,height*.45,length*.2],'color':C('cream')},{'center':[-width*.8,height+.10,length*.10],'radii':[width*.8,height*.4,length*.25],'color':C('cream')}]
  if id=='sheep':
   # Low-frequency crown variation on one mesh, not detached wool balls.
   torso=[ico([width*2.3,height*1.02,length*1.09],'cream',[0,height+.15,0],detail=1,distort=.065,bone='body'),loft([[0,height+.19,length*.30,width*.64,height*.20],[0,height+.50,length*.5,width*.3,height*.17]],'woodDark',8,bone='chest')]
  if id=='cow':torso.append(ico([.21,.15,.25],'#DEA69A',[0,height-.20,-length*.16],detail=1,bone='body'))
  wp('w.fauna.'+id+'.torso',name+'躯干 · 物种比例与颈部','animal',torso,[width*2.3,height*1.8,length*1.2],material='mat.fur',theme=theme)
  ht=height+.54;hz=length*.56
  headcol='woodDark' if id=='sheep' else color;snout='cream' if id in ['donkey','deer'] else '#D8998D' if id=='cow' else headcol
  wide=width*(.61 if id=='cow' else .49);sn=width*.66 if id=='cow' else width*.92
  head=[loft([[0,.08,-.04,wide*.90,wide*1.1],[0,.04,.09,wide,wide*1.12],[0,-.055,sn,wide*.63,wide*.55],[0,-.054,sn+.045,wide*.70,wide*.54]],headcol,8),loft([[0,-.056,sn-.02,wide*.64,wide*.56],[0,-.056,sn+.051,wide*.72,wide*.55]],snout,8),*[ico([.032,.029,.030],'ink',[sg*wide*.95,.065,.085],0) for sg in [-1,1]]]
  head[0]['frame_axis']=[0,0,1]
  if id=='cow':head += [ico([.024,.016,.013],'woodDark',[sg*wide*.33,-.046,sn+.063],0) for sg in [-1,1]]
  earh=.28 if id=='donkey' else .13
  for sg in [-1,1]:
   head.append(loft([[sg*wide*.8,.10,-.01,.033,.052],[sg*wide*1.25,.13+earh*.65,-.027,.048,.032],[sg*wide*1.55,.12+earh,-.013,.009,.013]],headcol,6))
  if id=='goat':head.append(loft([[0,-.07,.11,.039,.022],[0,-.22,.13,.020,.018],[0,-.25,.145,.005,.006]],'cream',6))
  wp('w.fauna.'+id+'.head',name+'头部 · 吻、耳与特征','animal',head,[width*1.65,.5,sn+.2],anchor='center',material='mat.fur',theme=theme)
  wp('w.fauna.'+id+'.tail',name+'尾部','animal',[loft([[0,0,0,.033,.032],[.035,-.15,-.06,.026,.025],[.04,-.32,-.075,.025,.023],[.028,-.43,-.06,.015,.013]],'woodDark' if id=='cow' else color,7,bone='tail')],[.10,.46,.15],anchor='center',material='mat.fur',theme=theme)
  rig=[{'name':'body','position':[0,height+.15,0]},{'name':'chest','parent':'body','position':[0,height+.3,mul(front,L)]},{'name':'head','parent':'chest','position':[0,ht,mul(hz,L)]},{'name':'tail','parent':'body','position':[0,height+.23,mul(-length*.48,L)]}]
  comps=[component('torso','w.fauna.'+id+'.torso',scale=[1,1,L]),component('tail','w.fauna.'+id+'.tail',[0,height+.23,mul(-length*.48,L)])]
  for suffix,x,z in [('FL',-width*.55,front),('FR',width*.55,front),('HL',-width*.58,back),('HR',width*.58,back)]:
   rig += [{'name':'leg'+suffix,'parent':'body','position':[x,shoulder,mul(z,L)]},{'name':'knee'+suffix,'parent':'leg'+suffix,'position':[x,shoulder-leg*.53,mul(z,L)]}]
   comps += [component(suffix,'w.fauna.hoofleg',[x,shoulder,mul(z,L)],params={'length':leg,'thickness':max(.029,min(.09,width*.18)),'bend':.069 if suffix.startswith('H') else .01,'palette':{P['wood']:C('woodDark' if id=='sheep' else color)}},bind={'leg':'leg'+suffix,'knee':'knee'+suffix}),component('hoof'+suffix,'w.fauna.hoof',[x,0,mul(z,L)],bone='knee'+suffix)]
  wp('w.fauna.'+id+'.body',name+'身体 · 共享骨架与腿组件','animal',size=[width*2.3,height*2,length*1.5],components=comps,rig=rig,level=2,params=schema(body_length=number(1,.93,1.07,'躯干长度比例')),material='mat.fur',theme=theme)
  items=[pi('skin','w.fauna.'+id+'.body',params={'body_length':L}),pi('head','w.fauna.'+id+'.head',parent='skin.rig.head')]
  if id in ['cow','goat']:items.append(pi('horns','w.fauna.horns',[0,.14,-.04],parent='skin.rig.head',scale=[1 if id=='cow' else .75]*3))
  if id=='deer':items.append(pi('antlers','w.fauna.antlers',[0,.15,-.03],parent='skin.rig.head'))
  if id=='donkey':items.append(pi('saddle','core.wear.saddle',[0,height+.43,-.09],scale=[.79,.79,.79]))
  wa('world-'+id,name,'animal',items,theme=theme,params=schema(body_length=number(1,.93,1.07,'躯干长度比例')))
  walk('world-'+id)
 def walk(id):
  tracks=[]
  for i,s in enumerate(['FL','FR','HL','HR']):
   sg=1 if i in [0,3] else -1
   tracks += [track('skin.rig.leg'+s,[1,0,0],[sg*12,-sg*12,sg*12]),track('skin.rig.knee'+s,[1,0,0],[0,15,0])]
  clip(id,[{'name':'Walk inspection','duration':1.4,'tracks':tracks}])
 for cfg in [('cow','奶牛',.86,1.85,.39,'#A96F43','cow'),('sheep','绵羊',.50,1.03,.28,'cream','sheep'),('goat','山羊',.62,1.00,.20,'wood','goat'),('donkey','驴',.99,1.45,.28,'#82766A','donkey'),('deer','鹿',1.08,1.27,.235,'#B0804D','deer','camp')]:hoofed(*cfg)
 for fox in [False,True]:
  id='fox' if fox else 'dog';name='狐狸' if fox else '牧羊犬';col='orange' if fox else '#9B7854';L=Q('body_length');front=mul(.31,L);back=mul(-.31,L)
  wp('w.fauna.'+id+'.torso',name+'躯干 · 胸腰起伏','animal',[loft([[0,.49,-.43,.10,.16],[0,.50,-.29,.17,.20],[0,.5,.16,.14,.19],[0,.59,.36,.13,.15],[0,.68,.43,.085,.105]],col,10,bone='body')],[.37,.87,.97],material='mat.fur',theme='camp')
  tail=[loft([[0,0,0,.06,.06],[0,-.02,-.15,.11 if fox else .045,.09 if fox else .045],[0,.01,-.39,.10 if fox else .035,.08 if fox else .035],[.02,-.04,-.56,.032,.03]],col,8,bone='tail',frame_axis=[0,0,-1])]
  tail[0]['rings'][-2]['color']=C('cream') if fox else C(col)
  wp('w.fauna.'+id+'.tail',name+'尾巴','animal',tail,[.23,.20,.72],anchor='center',material='mat.fur',theme='camp')
  muzzle=.21 if fox else .16
  head=[loft([[0,.05,-.03,.095,.103],[0,.02,.07,.102,.088],[0,-.018,muzzle,.032,.037]],col,8),loft([[0,-.055,.055,.066,.042],[0,-.031,muzzle,.03,.025]],'cream',7),ico([.037,.028,.031],'ink',[0,-.015,muzzle+.009],0),*[ico([.022,.021,.021],'ink',[sg*.081,.057,.066],0) for sg in [-1,1]],*[poly([[sg*.036,.09,-.027],[sg*.11,.07,-.02],[sg*.09,.24,-.03],[sg*.04,.1,.02]],[[0,1,2],[3,2,1],[0,2,3],[0,3,1]],col) for sg in [-1,1]]]
  wp('w.fauna.'+id+'.head',name+'头部 · 立耳与吻部','animal',head,[.24,.31,.34],anchor='center',material='mat.fur',theme='camp')
  rig=[{'name':'body','position':[0,.49,0]},{'name':'head','parent':'body','position':[0,.73,add(front,.19)]},{'name':'tail','parent':'body','position':[0,.53,mul(-.41,L)]}]
  comps=[component('torso','w.fauna.'+id+'.torso',scale=[1,1,L]),component('tail','w.fauna.'+id+'.tail',[0,.53,mul(-.41,L)])]
  for s,x,z in [('FL',-.10,front),('FR',.10,front),('HL',-.115,back),('HR',.115,back)]:
   rig += [{'name':'leg'+s,'parent':'body','position':[x,.46,z]},{'name':'knee'+s,'parent':'leg'+s,'position':[x,.23,z]}]
   comps += [component(s,'w.fauna.canine_leg',[x,.46,z],params={'palette':{P['orange']:C(col)}},bind={'leg':'leg'+s,'knee':'knee'+s}),component('paw'+s,'w.fauna.canine_paw',[x,0,add(z,.03)],bone='knee'+s)]
  wp('w.fauna.'+id+'.body',name+'身体 · 可复用犬科肢体','animal',size=[.4,.9,1.6],components=comps,rig=rig,level=2,params=schema(body_length=number(1,.9,1.1,'体长')),material='mat.fur',theme='camp')
  wa('world-'+id,name,'animal',[pi('skin','w.fauna.'+id+'.body',params={'body_length':L}),pi('head','w.fauna.'+id+'.head',parent='skin.rig.head')],theme='camp',params=schema(body_length=number(1,.9,1.1,'体长')));walk('world-'+id)
 # Pig: very short limbs and a broad, blunt snout, not a reskinned horse.
 pig=[loft([[0,.36,-.50,.13,.19],[0,.36,-.27,.24,.24],[0,.37,.22,.24,.23],[0,.36,.43,.15,.17]],'#E8A595',10),profile([[0,.24,.47,.13,.12],[0,.40,.47,.14,.12],[0,.50,.42,.09,.085]],'#E3A08F'),disk(.094,.067,'#D88983',[0,.35,.603],10,rotation=[90,0,0]),*[ico([.025,.027,.012],'woodDark',[sg*.037,.36,.641],0) for sg in [-1,1]],*[ico([.017,.019,.015],'ink',[sg*.104,.425,.532],0) for sg in [-1,1]],*[poly([[sg*.06,.49,.40],[sg*.18,.47,.40],[sg*.17,.55,.59],[sg*.05,.54,.48]],[[0,1,2,3]],'#D88E87') for sg in [-1,1]],*[profile([[x,.01,z,.046,.052],[x,.18,z,.054,.054],[x,.31,z,.067,.061]],'#D7998D') for x in [-.15,.15] for z in [-.30,.3]],loft([[0,.39,-.50,.018,.018],[.04,.44,-.58,.017,.017],[.05,.49,-.58,.015,.015],[0,.51,-.57,.012,.012]],'#D78E89',6)]
 simple('pig','家猪','animal',pig,[.53,.62,1.18],theme='farm',material='mat.fur')
 chicken=[ico([.34,.38,.46],'cream',[0,.29,0],1,distort=.03),loft([[0,.36,.13,.074,.07],[0,.55,.19,.065,.066],[0,.61,.2,.05,.05]],'white',8),ico([.15,.16,.16],'white',[0,.59,.21],1),loft([[0,.59,.275,.026,.025],[0,.58,.365,.004,.004]],'yellow',6),*[ico([.052,.072,.024],'red',[0,.68+i*.012,.19-i*.033],0) for i in range(3)],*[ico([.011,.012,.009],'ink',[sg*.064,.616,.248],0) for sg in [-1,1]],*[rod([x,.02,.02],[x,.19,.03],.012,'orange',sides=5) for x in [-.058,.058]],*[rod([x,.023,.02],[x+dx,.014,.13],.009,'orange',sides=4) for x in [-.058,.058] for dx in [-.028,.028]],*[loft([[sg*.10,.24,-.05,.029,.085],[sg*.177,.32,-.015,.020,.126],[sg*.14,.42,.035,.014,.018]],'white',7) for sg in [-1,1]],*[poly([[-.04,.30,-.18],[.04,.30,-.18],[.03,.59,-.39],[-.028,.51,-.40]],[[0,1,2,3]],'cream',rotation=[0,i*13,0]) for i in [-1,0,1]]]
 simple('chicken','母鸡','bird',chicken,[.40,.79,.78],theme='farm',material='mat.fur')
