"""Anatomical profiles, not complete rigged characters. Symmetry stays editable."""
from .common import *
from .common import author as emit

def author():
    def put(key,name,fs,size,**kw):return emit('creature','creature',key,name,fs,size,collision='none',**kw)
    fs=[profile_z([[-.36,.20,.16,.15],[-.22,.24,.26,.21],[.07,.25,.29,.23],[.29,.22,.20,.18],[.39,.19,.11,.10]],C('gSteel'),12)]
    fs.append(detail(tube([[0,.45,-.25],[0,.49,0],[0,.38,.30]],.018,C('gCopper'),6)))
    put('arthropod_thorax','节肢胸甲躯段',fs,[.58,.5,.75],purpose='有前后收颈和腹面分层的节肢胸段',ports=[port('neck',[0,.19,.39],[0,0,1]),port('abdomen',[0,.20,-.36],[0,0,-1]),port('leg.left',[-.24,.18,0],[-1,0,0],[0,1,0]),port('leg.right',[.24,.18,0],[1,0,0],[0,1,0])])
    fs=[profile_z([[-.19,.16,.14,.13],[-.10,.18,.20,.16],[.15,.14,.15,.11],[.23,.10,.09,.07]],C('gSteel'),10)]
    for s in (-1,1):
        fs.append(ellipsoid([s*.17,.22,.035],[.08,.075,.13],C('gAmber'),8,5))
        fs.append(tube([[s*.09,.10,.20],[s*.17,.075,.30],[s*.065,.075,.36]],[.035,.026,.008],C('gStoneDark'),8))
        fs.append(detail(tube([[s*.115,.27,.10],[s*.21,.43,.10],[s*.31,.46,.18]],[.013,.009,.005],C('gCopper'),6)))
    put('beetle_head','甲虫头与内扣口器',fs,[.64,.49,.56],purpose='扁颅、复眼与内弯口器的虫类头部',ports=[port('neck',[0,.16,-.19],[0,0,-1])])
    fs=[tube([[0,0,0],[.05,.37,.03],[.22,.61,.02],[.34,.27,.07]],[.042,.075,.046,.016],C('gLeafDark'),8)]
    for j in range(5):
        y=.29+j*.049;fs.append(detail(tube([[.31-j*.02,y,.07],[.25-j*.022,y+.016,.07]],[.018,.004],C('gAmber'),6)))
    put('raptorial_forelimb','螳形捕捉前肢',fs,[.40,.66,.14],purpose='带内缘棘列和折返胫节的捕捉型前肢',ports=[port('shoulder',[0,0,0],[0,-1,0])])
    fs=[tube([[0,.48,0],[.33,.75,.04],[.73,.47,.09],[.91,0,.12]],[.055,.045,.024,.010],C('gSteel'),8)]
    for p in ((.33,.75,.04),(.73,.47,.09)):fs.append(detail(ellipsoid(p,[.10,.10,.10],C('gCopper'),8,4)))
    put('spider_leg','三折蜘蛛步足',fs,[.97,.81,.18],purpose='由胸段向外落地的分节步足',ports=[port('hip',[0,.48,0],[-1,0,0],[0,1,0]),port('contact',[.91,0,.12],[0,-1,0])])
    fs=[profile_z([[-.16,.17,.085,.08],[0,.18,.16,.14],[.16,.16,.12,.10]],C('gRed'),10)]
    for s in (-1,1):
        fs.append(tube([[s*.085,.16,.12],[s*.15,.15,.30],[s*.11,.16,.45],[s*.025,.16,.49]],[.065,.055,.033,.009],C('gRed'),8))
    fs.append(detail(ellipsoid([0,.20,-.16],[.11,.12,.12],C('gCopper'),8,4)))
    put('crab_pincer','蟹钳开合爪端',fs,[.44,.35,.70],purpose='保持夹口空隙的左右钳指外观',ports=[port('wrist',[0,.17,-.16],[0,0,-1])])
    fs=[tube([[0,0,0],[0,.15,-.03],[0,.36,.05],[0,.47,.22],[0,.40,.36]],[.075,.08,.057,.029,.005],C('gSteel'),10)]
    for j,p in enumerate([[0,.11,-.025],[0,.25,0],[0,.39,.09]]):fs.append(detail(ellipsoid(p,[.17-.025*j,.09,.13],C('gCopper'),10,4)))
    put('scorpion_stinger','上卷蝎尾毒针节',fs,[.19,.53,.47],purpose='尾根、腹针囊与向前下钩的针尖')
    ps=[[-.035,0,0],[.035,0,0],[.25,.22,0],[.13,.37,0],[0,.55,0],[-.13,.37,0],[-.25,.22,0],[0,.27,.07],[0,.27,-.07]]
    n=7;fs=[mesh(ps,[[7,i,(i+1)%n] for i in range(n)]+[[8,(i+1)%n,i] for i in range(n)],C('gRed'))]
    put('tail_spade','龙尾菱脊箭叶',fs,[.50,.55,.14],purpose='从窄尾根展开并汇尖的尾端骨片')
    outline=[[-.45,.03],[-.38,.25],[-.22,.57],[0,.73],[.26,.45],[.47,.10],[.43,.02]]
    fs=[plate(outline,.024,'gCloth')]
    for a,b in [([-.42,.03,0],[-.22,.56,0]),([-.12,.02,0],[0,.72,0]),([.22,.02,0],[.27,.44,0])]:fs.append(detail(tube([a,b],[.025,.010],C('gSteel'),7)))
    put('dorsal_sail','分肋背帆片',fs,[.94,.75,.065],purpose='可沿脊背装配的薄膜背帆与骨肋')
    fs=[profile_z([[-.22,.16,.20,.13],[-.09,.19,.31,.18],[.16,.16,.32,.13],[.29,.12,.23,.08],[.33,.12,.12,.055]],C('gLeaf'),12)]
    for s in (-1,1):
        fs.append(ellipsoid([s*.21,.31,.04],[.18,.19,.18],C('gLeaf'),10,6))
        fs.append(ellipsoid([s*.215,.323,.12],[.105,.102,.060],C('gAmber'),10,5))
        fs.append(ellipsoid([s*.215,.329,.149],[.055,.070,.024],C('gStoneDark'),8,4))
    fs.append(detail(tube([[-.23,.10,.265],[0,.082,.32],[.23,.10,.265]],.009,C('gLeafDark'),6)))
    put('frog_head','蛙类宽吻头',fs,[.69,.43,.57],purpose='宽扁吻、上置眼与连续下颌的两栖头部',ports=[port('neck',[0,.16,-.22],[0,0,-1])])
    fs=[profile_z([[-.30,.16,.11,.12],[-.17,.20,.24,.18],[.07,.20,.29,.19],[.25,.19,.23,.16],[.34,.16,.16,.10]],C('gLeafDark'),12)]
    fs.append(detail(profile_z([[-.19,.09,.17,.025],[.05,.055,.24,.026],[.27,.09,.16,.025]],C('gCream'),10)))
    put('amphibian_torso','两栖扁腹躯体',fs,[.58,.39,.64],purpose='背腹分层、前颈和后骨盆收束的躯段',ports=[port('neck',[0,.16,.34],[0,0,1]),port('pelvis',[0,.16,-.30],[0,0,-1])])
    fs=[tube([[0,0,0],[0,.10,.12],[0,.10,.23]],[.046,.036,.024],C('gLeaf'),8)]
    for k in range(5):
        x=(k-2)*.043;tip=[x*1.7,.09,.38-abs(k-2)*.027]
        fs.append(tube([[0,.1,.16],[x,.10,.27],tip],[.018,.014,.010],C('gLeaf'),6))
        fs.append(ellipsoid(tip,[.05,.029,.065],C('gCream'),8,4))
    put('gecko_toepad','五趾吸附掌端',fs,[.36,.15,.45],purpose='细趾与扁平末端趾垫清晰分离的壁虎足')
    outline=[[-.05,0],[.05,0],[.26,.38],[.03,.29],[-.03,.29],[-.26,.38]]
    fs=[plate(outline,.022,'gCloth')]
    for s in (-1,1):
        for t in (.35,.65,.95):fs.append(detail(tube([[0,.02,.012],[s*.25*t,.36*t,.012]],[.007,.004],C('gAmber'),5)))
    put('forked_caudal_fin','深叉鱼尾鳍',fs,[.52,.38,.036],purpose='中央叉缺和分区鳍条的独立尾鳍')
