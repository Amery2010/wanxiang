"""Rebuild the offline asset inventory from shipped sources and real renders."""
from __future__ import annotations
import base64, csv, html, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
R=Path(__file__).resolve().parents[1]
E=R/'generated/verification'
D=R/'docs/game410'
ORDER=['dungeon','traversal','survival','farming','scifi','automation','creature','equipment','waterland','puzzle']
def read(p): return json.loads(Path(p).read_text())
def data_uri(p): return 'data:image/webp;base64,'+base64.b64encode(Path(p).read_bytes()).decode()
def dump(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
    D.mkdir(parents=True,exist_ok=True)
    collection=read(R/'library/game-expansion.json')
    ids=[ident for kit in ORDER for ident in collection['kits'][kit]['parts']+[collection['kits'][kit]['assembly']]]
    needed=[E/'geometry-checks.json',E/'thumbnail-summary.json',E/'preview-verification.json',E/'browser/results.json']
    needed += [E/'game-models'/(ident+suffix) for ident in ids for suffix in ('.webp','-views.webp')]
    missing=[str(p.relative_to(R)) for p in needed if not p.exists()]
    if missing:raise SystemExit(f'Fresh validation inputs required before rebuilding the report ({len(missing)} missing): '+', '.join(missing[:8]))
    checks=read(E/'geometry-checks.json')
    bycheck={x['name']:x for x in checks['results']}
    rows=[];cards=[]
    for kit in ORDER:
        k=collection['kits'][kit]
        for ident in k['parts']+[k['assembly']]:
            level=1 if ident.startswith('l1.') else 2
            source=R/'library'/('parts' if level==1 else 'assemblies')/(ident+'.json')
            spec=read(source)
            author=spec.get('source',spec.get('metadata',{}).get('source',{})).get('authoring','')
            param=spec.get('parameter_schema',{}).get('properties',{})
            ck=bycheck[ident+(' / default lowpoly' if level==1 else ' / GLB lowpoly')]
            triangles=ck['detail']['triangles']
            size=' × '.join(f"{param[a]['default']:g}" for a in ('width','height','depth')) if level==1 else '由子装配决定'
            row={'套件':k['name'],'用途':k['use'],'层级':f'L{level}','模型ID':ident,'名称':spec['name'],'说明':spec['description'],
              '默认Lowpoly三角面':triangles,'设计尺寸W×H×D(m)':size,'尺寸参数':'width / height / depth' if level==1 else '子部件参数',
              'detail参数':str('detail' in param).lower(),'几何检查': '通过' if ck['passed'] else '失败',
              '作者源码':author,'定义文件':str(source.relative_to(R)),
              '卡片缩略图':f'library/thumbnails/{ident}.webp','列表缩略图':f'library/thumbnails/{ident}.webp',
              '视觉证据':'docs/game410/index.html',
              '边界':'静态美术；未实现游戏逻辑、蒙皮动画或物理；定位基准不等于已验证机械接口'}
            rows.append(row)
            cards.append({'id':ident,'name':spec['name'],'kit':kit,'kitName':k['name'],'level':level,'description':spec['description'],
              'triangles':triangles,'size':size,'author':author,'detail':'detail' in param,
              'image':data_uri(R/row['卡片缩略图']),'views':data_uri(E/'game-models'/(ident+'-views.webp'))})
    with (D/'new-assets.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    dump(D/'new-assets.json',rows)
    thumbs=read(E/'thumbnail-summary.json'); pv=read(E/'preview-verification.json'); browser=read(E/'browser/results.json')
    old=thumbs['baseline_grid_bytes']; old_new=thumbs['compressed_baseline_grid_bytes']; total=thumbs['grid_bytes']
    saved=(1-old_new/old)*100; allsaved=(1-total/old)*100
    # Presentation evidence always reads the current per-model render, never an older contact sheet.
    out=E/'contact-sheets';out.mkdir(exist_ok=True)
    try: font=ImageFont.truetype('DejaVuSans.ttf',14)
    except OSError: font=ImageFont.load_default()
    def sheet(ids,columns,path):
        height=((len(ids)+columns-1)//columns)*344
        canvas=Image.new('RGB',(columns*320,height),(233,237,231));draw=ImageDraw.Draw(canvas)
        for i,ident in enumerate(ids):
            with Image.open(E/'game-models'/(ident+'.webp')) as im:
                tile=im.convert('RGBA');tile.thumbnail((306,306),Image.Resampling.LANCZOS)
                x=(i%columns)*320;y=(i//columns)*344
                canvas.paste(tile,(x+(320-tile.width)//2,y),tile)
                label=ident.removeprefix('l2-game410-') if ident.startswith('l2-') else ident.rsplit('.',1)[1]
                draw.text((x+12,y+313),label,font=font,fill=(28,47,49))
        canvas.save(path,quality=92)
    for kit in ORDER: sheet(collection['kits'][kit]['parts'],4,out/(kit+'.jpg'))
    sheet([collection['kits'][k]['assembly'] for k in ORDER],5,out/'assemblies.jpg')
    # Recorded visual review is intentionally narrower than all possible views/parameters.
    visual={'version':'3.10.0','reviewed_default_L1':120,'reviewed_default_L2_examples':10,
      'supporting_render_views':390,'manual_review_scope':'All 130 default previews; selected side/rear follow-up. Not a claim that all 390 views or all parameter combinations were manually accepted.',
      'refinements':['Open-top cryopod shell','Attached corn kernels','Face-clipped charred-log and axe detail','Connected sea-fan branches','Closed climbing harness loops',
        'Open scissor pivot','Matte organic material roles','True basket floor and upper-only handle','Inward three-jaw clamp fingers','Aligned triangular key'],
      'render_evidence':'Actual GLB CPU rasterization, not generated concept art','commercial_certification':False}
    dump(E/'visual-review.json',visual)
    tri=[x['triangles'] for x in cards if x['level']==1]
    # No external JavaScript, images, fonts or server are required by this catalogue.
    opts=''.join(f'<option value="{kit}">{html.escape(collection["kits"][kit]["name"])}</option>' for kit in ORDER)
    payload=json.dumps(cards,ensure_ascii=False).replace('</','<\\/')
    page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>万象工坊 3.10 · 游戏新增模型目录</title>
<style>:root{--ink:#233a3a;--muted:#677978;--accent:#286856;--line:#d7e1dc;--bg:#f4f6f2}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 system-ui,-apple-system,"Microsoft YaHei",sans-serif}header,main,footer{max-width:1360px;margin:auto;padding:30px 28px}header{padding-top:45px}.eyebrow{letter-spacing:.16em;color:var(--accent);font-size:12px;font-weight:750}h1{font-size:clamp(28px,4vw,48px);line-height:1.2;margin:14px 0}h2{font-size:20px}p{color:var(--muted);max-width:940px}.metrics{display:flex;gap:32px;flex-wrap:wrap;margin:26px 0 10px}.metrics strong{display:block;font-size:28px;color:var(--ink)}.metrics span{color:var(--muted);font-size:13px}.bar{position:sticky;top:0;z-index:2;display:flex;gap:12px;flex-wrap:wrap;padding:14px 0;background:var(--bg)}input,select,button{font:inherit;border:1px solid var(--line);border-radius:9px;padding:10px 12px;background:white;color:var(--ink)}input{flex:1;min-width:200px}button{cursor:pointer}button:hover{border-color:var(--accent)}.count{color:var(--muted);margin:10px 0 18px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(235px,1fr));gap:18px}.card{padding:0;overflow:hidden;text-align:left;border:1px solid var(--line);background:white;border-radius:14px;cursor:pointer}.card:hover{border-color:var(--accent);transform:translateY(-2px)}.preview{height:210px;display:grid;place-items:center;background:linear-gradient(140deg,#f3f6ef,#e9efeb);position:relative}.preview img{width:210px;height:210px;object-fit:contain}.badge{position:absolute;top:12px;left:12px;border:1px solid var(--line);background:#ffffffdc;border-radius:5px;padding:1px 6px;font-size:11px}.body{padding:16px}.name{font-size:17px;font-weight:700}.meta{font-size:12px;color:var(--muted);margin-top:7px}.id{font:10px/1.6 ui-monospace,monospace;color:#7d8a86;overflow-wrap:anywhere;margin-top:8px}.note{margin-top:30px;padding:20px 24px;border:1px solid var(--line);border-radius:12px;background:white}.note p{margin:8px 0}.muted{color:var(--muted)}dialog{border:1px solid var(--line);border-radius:16px;max-width:1060px;width:calc(100vw - 28px);max-height:calc(100vh - 36px);padding:24px;color:var(--ink)}dialog::backdrop{background:#172b32af}dialog img{display:block;width:100%;object-fit:contain;background:#eef2eb;border-radius:10px}dialog .close{float:right}.wide{font:12px ui-monospace,monospace;overflow-wrap:anywhere;color:var(--muted)}.empty{padding:40px;text-align:center}.legend{font-size:12px;color:var(--muted)}footer{font-size:12px;color:var(--muted);border-top:1px solid var(--line)}@media(max-width:550px){header,main,footer{padding-left:16px;padding-right:16px}.grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.preview{height:150px}.preview img{width:145px;height:145px}.body{padding:11px}.name{font-size:14px}.id{font-size:9px}.bar select{flex:1;width:45%}.metrics{gap:22px}}</style>
<header><div class="eyebrow">WANXIANG STUDIO / 3.10.0</div><h1>为游戏世界，补齐关键构件。</h1><p>120 个新基础部件，十组可编辑装配样例。这里展示的是工程中实际 GLB 的预览，不是概念图。按领域检索，点击卡片查看多视角、参数与作者源码位置。</p>
<div class="metrics"><div><strong>120</strong><span>新 L1 基础部件</span></div><div><strong>10</strong><span>独立 L2 装配样例</span></div><div><strong>3,730</strong><span>本版公开资产总量</span></div><div><strong>1</strong><span>每项唯一缩略图</span></div></div></header>
<main><div class="bar"><input id="search" type="search" placeholder="搜索名称、用途或模型 ID…" aria-label="搜索模型"><select id="kit" aria-label="模型套件"><option value="">全部十类套件</option>__OPTIONS__</select><select id="level" aria-label="模型层级"><option value="">L1 + L2</option><option value="1">L1 基础部件</option><option value="2">L2 组合样例</option></select></div><div class="count" id="count"></div><div class="grid" id="grid"></div>
<section class="note"><h2>每项资产仅一张 WebP</h2><p>全库 3,730 项资产各保留一张 256×256 Lowpoly 缩略图；卡片、列表、搜索和素材架共用。透明背景与图片哈希保持不变，选中模型仍加载真实 3D 网格并可切换 Toon 材质。</p></section>
<section class="note"><h2>使用与验证边界</h2><p>解压完整源码并按 README 安装依赖后，运行 pnpm dev → 游戏新增 · 3.10。此离线目录只用于浏览证据，不包含 3D 编辑器或 GLB 生成器。完整工作台支持参数修改与实时导出。</p><p>这些是静态游戏美术部件。交互、动画、蒙皮、物理、具体关卡和引擎接入仍需由游戏实现；设计尺寸和定位基准不等于经过机械公差验证的插接接口。浏览器检查采用 Chromium CPU 回退渲染，窄视口测试不等于移动真机验收。</p></section></main>
<dialog id="detail"><button class="close" id="close" aria-label="关闭">关闭 ×</button><h2 id="title"></h2><p id="description"></p><img id="views" alt="模型实际 GLB 的等距、侧面和背面诊断视图"><p class="legend">从左到右：ISO 等距 / SIDE 侧面 / REAR 背面。细节仍以完整工作台实际旋转查看为准。</p><p id="spec"></p><p class="wide" id="path"></p></dialog><footer>原有 3,600 个公开 ID 保留 · 新增资产不是换色或尺寸变体计数 · 不含预构建 GLB · 2026-09-22</footer>
<script id="records" type="application/json">__DATA__</script><script>
const records=JSON.parse(document.querySelector('#records').textContent),q=document.querySelector('#search'),kit=document.querySelector('#kit'),level=document.querySelector('#level'),grid=document.querySelector('#grid'),dialog=document.querySelector('#detail');
function show(x){document.querySelector('#title').textContent=x.name;document.querySelector('#description').textContent=x.description;document.querySelector('#views').src=x.views;document.querySelector('#spec').textContent=`L${x.level} · ${x.kitName} · 默认 Lowpoly ${x.triangles.toLocaleString()} 三角面 · 设计尺寸 W×H×D: ${x.size} ${x.level===1?'m':''}${x.detail?' · 有 detail 参数':''}`;document.querySelector('#path').textContent=`ID: ${x.id}\n作者: ${x.author}`;dialog.showModal();}
function render(){let term=q.value.trim().toLowerCase();let rows=records.filter(x=>(!kit.value||x.kit===kit.value)&&(!level.value||x.level===Number(level.value))&&(!term||[x.id,x.name,x.description,x.kitName].join(' ').toLowerCase().includes(term)));grid.replaceChildren();document.querySelector('#count').textContent=`显示 ${rows.length} / 130 项 · 点击查看多视角`;for(const x of rows){const card=document.createElement('button');card.className='card';card.type='button';const preview=document.createElement('div');preview.className='preview';const im=document.createElement('img');im.src=x.image;im.alt=x.name;im.loading='lazy';im.width=256;im.height=256;preview.append(im);let badge=document.createElement('span');badge.className='badge';badge.textContent='L'+x.level;preview.append(badge);let body=document.createElement('div');body.className='body';for(const [c,t] of [['name',x.name],['meta',`${x.kitName} · ${x.triangles.toLocaleString()} 三角面`],['id',x.id]]){let el=document.createElement('div');el.className=c;el.textContent=t;body.append(el)}card.append(preview,body);card.onclick=()=>show(x);grid.append(card)}if(!rows.length){let p=document.createElement('div');p.className='empty';p.textContent='没有匹配项，请调整搜索或筛选。';grid.append(p)}}
q.addEventListener('input',render);kit.addEventListener('change',render);level.addEventListener('change',render);document.querySelector('#close').onclick=()=>dialog.close();dialog.addEventListener('click',e=>{if(e.target===dialog){const b=dialog.getBoundingClientRect();if(e.clientX<b.left||e.clientX>b.right||e.clientY<b.top||e.clientY>b.bottom)dialog.close()}});render();
</script></html>'''.replace('__OPTIONS__',opts).replace('__DATA__',payload)
    (D/'index.html').write_text(page)
    print(json.dumps({'rows':len(rows),'html_bytes':len(page.encode()),'card_saving_pct':saved,'all_image_saving_pct':allsaved,'triangle_range':(min(tri),max(tri))},ensure_ascii=False))
if __name__=='__main__':main()
