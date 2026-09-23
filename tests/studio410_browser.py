"""Real Studio dev server, real build/export bridge; start pnpm dev before running."""
from pathlib import Path
import json,time,hashlib,tempfile,os
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];OUT=R/'generated/verification/browser';OUT.mkdir(parents=True,exist_ok=True)
results=[];errors=[];downloads=[]
def check(name,fn):
 try:
  v=fn();results.append({'name':name,'passed':True,'detail':v});print('PASS',name,flush=True)
 except Exception as e:results.append({'name':name,'passed':False,'error':str(e)});print('FAIL',name,str(e),flush=True)
def need(v,msg='Assertion failed'):
 if not v:raise AssertionError(msg)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=os.environ.get('WX_CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1600,'height':1000},accept_downloads=True);page.set_default_timeout(15000);page.on('pageerror',lambda e:errors.append(str(e)))
 studio_url=os.environ.get('WX_STUDIO_URL','http://127.0.0.1:5173')
 page.goto(studio_url,wait_until='load',timeout=90000)
 def wait():
  page.wait_for_function('window.WX_QA&&!WX_QA.building&&!WXSceneEditor.isBusy()&&(WX_QA.cpuDrawn||WX_QA.runtimeDrawn)',timeout=120000);page.wait_for_timeout(180)
 def state():return page.evaluate('({id:WX_QA.assetId,error:WX_QA.buildError,triangles:WX_QA.liveTriangleCount,glb:WX_QA.actualGLBLoaded,cpu:WX_QA.cpuDrawn,webgl:WX_QA.runtimeDrawn,renderer:WX_QA.renderer,signature:WX_QA.geometrySignature})')
 wait()
 check('3730 real catalogue entries and L1-L4 counts',lambda:need(page.evaluate('WX_DATA.assets.length===3730&&JSON.stringify(WXStudioCore.counts(WX_DATA.assets).levels)===JSON.stringify({1:1600,2:1010,3:1000,4:120})')))
 def newkit():
  page.locator('[data-collection="game410"]').click();need(page.locator('#catalogCount').inner_text().startswith('130'))
  need(page.evaluate('WXStudioShell.state.level')=='all');page.screenshot(path=str(OUT/'game-collection.png'));return {'visible_count':130}
 check('New collection resets incompatible default L3 filter',newkit)
 for kit in ('dungeon','traversal','survival','farming','scifi','automation','creature','equipment','waterland','puzzle'):
  def filterkit(kit=kit):
   page.locator('[data-game-kit="'+kit+'"]').click();need(page.locator('#catalogCount').inner_text().startswith('13'));need(page.locator('#catalog .asset-card[data-id]').count()==13)
   return {'kit':kit,'parts':12,'examples':1}
  check('Browse actual game kit '+kit,filterkit)
 def image_sizes():
  page.locator('#gridView').click();page.wait_for_function("[...document.querySelectorAll('#catalog .card-image img')].filter(x=>x.complete).length>0")
  page.wait_for_timeout(200);g=page.locator('#catalog .card-image img').first.evaluate('(im)=>[im.naturalWidth,im.naturalHeight,im.src.slice(0,23)]');need(g[:2]==[256,256],str(g))
  page.locator('#listView').click();page.wait_for_timeout(250);sm=page.locator('#catalog .card-image img').first.evaluate('(im)=>[im.naturalWidth,im.naturalHeight,im.src.slice(0,23)]');need(sm[:2]==[96,96],str(sm));page.screenshot(path=str(OUT/'small-list.png'));page.locator('#gridView').click();return {'grid':g,'list':sm}
 check('Actual grid and list image decode sizes are 256 and 96',image_sizes)
 def select(i,shot=None):
  page.evaluate('async id=>{await WX_LIVE_QA.select(id)}',i);wait();s=state();need(not s['error'],str(s));need(s['glb'] and s['triangles']>0,str(s))
  if shot:page.screenshot(path=str(OUT/(shot+'.png')))
  return s
 for i,shot in [('l1.nature.game_farming.corn_husk','corn'),('l1.character.game_equipment.climbing_harness','harness'),('l1.architecture.game_scifi.cryopod_shell','cryopod'),('l1.props.game_survival.basket_body','basket'),('l2-game410-automation','clamp'),('l2-game410-creature','creature'),('l2-game410-puzzle','puzzle'),('core.human.head','legacy-head')]:check('Real GLB load and draw '+i,lambda i=i,s=shot:select(i,s))
 def parameter():
  select('l1.architecture.game_scifi.bulkhead_frame');a=state();spec=page.evaluate('WX_LIVE_QA.getSpec()');spec.setdefault('params',{})['width']=2.50;page.evaluate('async s=>{await WX_LIVE_QA.commit(s)}',spec);wait();b=state();need(not b['error'] and b['signature']!=a['signature']);return {'before':a['signature'],'after':b['signature']}
 check('Dimension parameter rebuilds actual geometry',parameter)
 def details():
  select('l1.nature.game_farming.corn_husk');a=state();s=page.evaluate('WX_LIVE_QA.getSpec()');s.setdefault('params',{})['detail']=False;page.evaluate('async s=>{await WX_LIVE_QA.commit(s)}',s);wait();b=state();need(not b['error'] and b['triangles']<a['triangles'],str((a,b)));return {'before':a['triangles'],'after':b['triangles']}
 check('Detail-off reduces actual corn geometry',details)
 def styles():
  select('l1.architecture.game_scifi.cryopod_shell');s=page.evaluate('WX_LIVE_QA.getSpec()');s['style']='toon';page.evaluate('async s=>{await WX_LIVE_QA.commit(s)}',s);wait();v=state();need(not v['error'] and v['glb']);need(page.evaluate('WX_LIVE_QA.stats().style')=='toon');return v
 check('Toon style builds and loads a new game model',styles)
 def export():
  select('l2-game410-dungeon')
  with page.expect_download(timeout=60000) as got:page.locator('#exportBtn').click()
  d=got.value
  with tempfile.TemporaryDirectory() as folder:
   q=Path(folder)/'asset.glb';d.save_as(q);raw=q.read_bytes();need(raw[:4]==b'glTF' and len(raw)>100);downloads.append({'name':d.suggested_filename,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
  return downloads[-1]
 check('Visible export button downloads the actual new assembly GLB',export)
 def narrow():
  page.set_viewport_size({'width':430,'height':900});page.wait_for_timeout(500);need(page.locator('canvas').count()>0 and not state()['error']);page.screenshot(path=str(OUT/'narrow-430.png'));return {'width':430,'physical_device':False}
 check('430px viewport still builds and draws',narrow)
 check('No uncaught page JavaScript errors',lambda:need(not errors,str(errors)))
 renderer=state();browser.close()
report={'version':'3.10.0','studio_url':studio_url,'results':results,'passed':sum(x['passed'] for x in results),'failed':sum(not x['passed'] for x in results),'page_errors':errors,'downloads':downloads,'final_render_state':renderer,'limitations':'Real headless desktop Chromium only. CPU fallback/software WebGL is not physical-GPU, mobile-device, full-PBR, rig or physics certification.'}
(OUT/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'failed':report['failed']}),flush=True)
if report['failed']:raise SystemExit(1)
