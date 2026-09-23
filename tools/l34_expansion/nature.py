"""Botanical prefabs: structural morphologies, not random seed duplicates."""
from .common import *
TREES=[('oak','橡树','oak','round',5),('maple','枫树','maple','round',5),('ginkgo','银杏','ginkgo','fan',5),('birch','白桦','ovate','column',4),('willow','垂柳','lance','droop',5),('pine','松树','pine_pair','tier',5),('spruce','云杉','needle','tier',7),('fir','冷杉','conifer_spray','tier',6),('cypress','柏树','scale','column',5),('palm','棕榈','palmlet','palm',7),('coconut','椰子树','palmlet','palmfruit',8),('banana','香蕉树','banana','palmfruit',6),('baobab','猴面包树','compound','round',4),('acacia','金合欢','compound','flat',6),('mangrove','红树林树','ovate','root',5),('cherry','樱花树','ovate','bloom',5),('apple','苹果树','ovate','fruit',5),('pear','梨树','ovate','fruit',4),('citrus','柑橘树','lance','citrus',5),('peach','桃树','lance','fruit',6),('plum','梅树','ovate','bloom',4),('magnolia','玉兰','ovate','bloom',6),('dogwood','山茱萸','ovate','bloom',7),('poplar','杨树','heart','column',6),('aspen','山杨','ovate','column',7),('eucalyptus','桉树','lance','sparse',4),('olive','橄榄树','lance','split',5),('fig','无花果','maple','split',4),('chestnut','栗树','lance','nut',5),('walnut','胡桃树','compound','nut',6),('cedar','雪松','needle','flat',7),('redwood','红杉','conifer_spray','column',8),('sequoia','巨杉','scale','tier',8),('banyan','榕树','ovate','aerial',7),('rubber','橡胶树','ovate','aerial',4),('dragon','龙血树','strap','umbrella',6),('yucca','丝兰树','spear','umbrella',5),('treefern','桫椤','fern','palm',9),('bamboo','竹丛','bamboo','clump',7),('dead_snag','枯立木','none','dead',5)]

def author():
    for key,name,leaf,form,n in TREES:
        h=3.7 if form not in ('column','tier') else 5.2;w=3.5 if form not in ('column','tier') else 2.0
        trunk='exp.nature.birch_trunk' if key in ('birch','aspen') else 'exp.nature.baobab_trunk' if key=='baobab' else 'exp.nature.deadwood_trunk' if form=='dead' else 'core.nature.trunk'
        items=[fit('trunk',trunk,[.42 if key!='baobab' else 1.1,h*.68,.42 if key!='baobab' else 1.1])]
        if form=='clump':
            items=[]
            for i in range(n):
                a=i*math.tau/n;r=.36;items.append(fit('culm'+str(i),l1('nature','branch','bamboo_node'),[.13,h*(.72+.04*i),.13],[r*math.sin(a),0,r*math.cos(a)]))
                items.append(fit('leaves'+str(i),l2('nature','leafybranch','lance'),[.9,1.0,.7],[r*math.sin(a),h*.67,r*math.cos(a)],[0,360*i/n,0]))
        elif form!='dead':
            for i in range(n):
                a=i*math.tau/n;r=w*.23;yy=h*(.52+(i%3)*.1)
                if form in ('tier','column'):r=w*.2*(1-i/n*.65);yy=h*(.3+.62*i/n)
                if form in ('palm','palmfruit','umbrella'):r=w*.20;yy=h*.7
                end=[r*math.sin(a),yy,r*math.cos(a)]
                items.append(beam('branch'+str(i),[0,h*.48,0],end,.10,color='#817153'))
                if form in ('palm','palmfruit','umbrella'):
                    ref=l2('nature','frondcrown','pinnate' if form!='umbrella' else 'grass_blade');sz=[1.4,.65,1.5]
                elif form in ('tier','column'):
                    ref='exp.nature.cypress_crown' if form=='column' else 'core.nature.crown_cluster';sz=[w*(.9-i/n*.6),.9,w*(.9-i/n*.6)]
                else:ref='exp.nature.maple_crown' if leaf=='maple' else 'exp.nature.leaf_crown';sz=[w*.55,1.1,w*.55]
                items.append(fit('crown'+str(i),ref,sz,end,[0,360*i/n,0]))
                # Recognisable leaf/flower/fruit is a removable close-view feature.
                lk=leaf if leaf in keys('nature','leaf') else 'ovate'
                if form not in ('tier','column'):
                    items.append(fit('leafdetail'+str(i),l2('nature','leafybranch',lk),[.7,.55,.55],[end[0],yy+.25,end[2]],optional=True))
                if form in ('fruit','palmfruit','citrus','nut','bloom'):
                    group='inflorescence' if form=='bloom' else 'fruiting';fk='daisy' if form=='bloom' else 'citrus' if form=='citrus' else 'nut' if form=='nut' else 'pome'
                    items.append(fit('reproductive'+str(i),l2('nature',group,fk),[.3,.35,.3],[end[0],yy-.1,end[2]],optional=True))
        if form=='dead':
            items.append(fit('exposed_root',l1('nature','root','exposed'),[1,.45,1]))
            items.append(fit('broken_bough',l1('nature','branch','broken'),[.28,1.1,.28],[.25,h*.4,0],[0,0,-45]))
        if form in ('aerial','root'):
            items.extend(radial(l1('nature','root','aerial' if form=='aerial' else 'mangrove'),5,.7,0,[.25,h*.5,.28],prefix='root'))
        register('nature','tree',key,name,items,[w,h+1,w],['完整树干分枝','独立冠层',form,leaf],notes=['植物为静态环境资产；未宣称物种学精确模型'])
    shrubs=[('boxwood','黄杨','ovate','round',7),('hedge','树篱','ovate','linear',8),('holly','冬青','holly','round',5),('rose','玫瑰灌丛','trifoliate','bloom',5),('hydrangea','绣球','ovate','bloom',6),('azalea','杜鹃','lance','bloom',7),('lavender','薰衣草','lance','spike',9),('rosemary','迷迭香','needle','spike',6),('juniper','杜松','scale','flat',5),('berry','浆果灌丛','ovate','fruit',6),('fern','蕨丛','fern','fan',8),('cycad','苏铁','cycad','fan',9),('aloe','芦荟','aloe','fan',5),('agave','龙舌兰','spear','fan',7),('cactus','枝状仙人掌','succulent','column',4),('succulent','莲座多肉','succulent','rosette',6),('bushwillow','矮生柳','lance','droop',4),('tea','茶树','ovate','linear',5),('coffee','咖啡灌木','ovate','fruit',7),('reed','芦苇丛','strap','column',8)]
    for key,name,leaf,shape,n in shrubs:
        items=[]
        for i in range(n):
            a=math.tau*i/n;r=.38;x=(i/(n-1)-.5)*1.7 if shape=='linear' else r*math.sin(a);z=0 if shape=='linear' else r*math.cos(a)
            items.append(fit('stem'+str(i),l1('nature','branch','cane' if shape=='column' else 'twig'),[.12,.6,.12],[x,0,z]))
            ref=l2('nature','frondcrown','cycad') if leaf=='cycad' else l2('nature','leafybranch',leaf)
            items.append(fit('foliage'+str(i),ref,[.6,.8,.6],[x,.15,z],[0,360*i/n,0]))
            if shape in ('bloom','spike','fruit'):items.append(fit('flower'+str(i),l2('nature','inflorescence','pompom' if shape=='bloom' else 'spike') if shape!='fruit' else l2('nature','fruiting','berry'),[.3,.35,.3],[x,.75,z],optional=True))
        register('nature','shrub',key,name,items,[2,1.2,1.4],['根茎接地','枝叶簇',leaf,shape])
    crops=[('wheat','小麦','wheat_ear'),('barley','大麦','barley_awn'),('rice','水稻','rice_panicle'),('corn','玉米','corn_cob'),('cotton','棉花','cotton_boll'),('sorghum','高粱','sorghum_head'),('cane','甘蔗','cane_joint'),('sunflower','向日葵','sunflower_disk'),('beans','豆架','bean_vine'),('lettuce','生菜','lettuce_heart'),('pumpkin','南瓜藤','pepo'),('tomato','番茄架','berry'),('grape','葡萄架','aggregate'),('strawberry','草莓畦','aggregate'),('lotus','荷花丛','lotus'),('waterlily','睡莲丛','lotus'),('clover','三叶草丛','clover'),('tulip','郁金香丛','cup'),('daisy','雏菊丛','daisy'),('orchid','兰花丛','orchid')]
    for key,name,k in crops:
        items=[];n=4 if key in ('corn','cane','sunflower') else 6
        for i in range(n):
            x=(i%3-1)*.32;z=(i//3-.5)*.45
            if k in keys('nature','crop'):ref=l2('nature','cropstem',k)
            elif k in keys('nature','fruit'):ref=l2('nature','fruiting',k)
            elif k in keys('nature','leaf'):ref=l2('nature','leafybranch',k)
            else:ref=l2('nature','inflorescence',k)
            items.append(fit('plant'+str(i),ref,[.42,1 if key in ('corn','cane','sunflower') else .65,.42],[x,0,z]))
        if key in ('beans','grape','tomato'):
            items += [block('trellis'+str(i),[.06,1.5,.06],[(i-.5)*1,0,0],color='#977653') for i in range(2)]
            items.append(block('trellis_cross',[1.1,.06,.06],[0,1.2,0],color='#977653'))
        register('nature','crop',key,name,items,[1.5,1.6,1.1],['完整种植簇','接地根茎',k,key])
    for j,(key,name,cap) in enumerate([('porcini','牛肝菌群','umbrella_cap'),('morel','羊肚菌群','morel'),('oyster','侧耳菌簇','bracket_cap'),('chanterelle','鸡油菌群','funnel_cap'),('inkcap','墨汁伞群','bell_cap'),('puffball','马勃群','puffball'),('fairy_ring','蘑菇环','umbrella_cap')]):
        items=[];n=8 if key=='fairy_ring' else 3+j%3
        for i in range(n):
            a=math.tau*i/n;x=.35*math.sin(a);z=.35*math.cos(a)
            items.append(fit('stipe'+str(i),l1('nature','fungus','stipe'),[.1,.35,.1],[x,0,z]))
            items.append(fit('cap'+str(i),l1('nature','fungus',cap),[.32,.24,.32],[x,.3,z]))
        register('nature','fungus',key,name,items,[1,.65,1],['菌柄','菌盖',cap,key])
    for j,(key,name,shape) in enumerate([('staghorn','鹿角珊瑚','y_fork'),('fan','海扇','whorl'),('tube','管状海绵','hollow'),('brain','脑珊瑚','segment'),('plate','盘状珊瑚','arch'),('anemone','海葵','tendril')]):
        items=[fit('holdfast',l1('nature','root','clinging'),[.7,.15,.7])]
        for i in range(5+j):items.append(fit('branch'+str(i),l1('nature','branch',shape),[.22,.55+(i%2)*.2,.22],[.25*math.sin(i),.1,.25*math.cos(i)],[0,i*57,0],color='#C49283'))
        register('nature','aquatic',key,name,items,[1,.9,1],['附着基底','可分支群体',shape])
