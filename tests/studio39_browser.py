"""Smoke-test the Studio dev server in Chromium; start pnpm dev before running.
No mocked meshes or replacement catalogue. Software/CPU rendering is reported.
"""
from pathlib import Path
import json,time,hashlib,tempfile,os
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];OUT=R/'generated/verification/studio39-regression';OUT.mkdir(parents=True,exist_ok=True)
results=[];errors=[];downloads=[]
def check(name,fn):
 try:
  extra=fn();results.append({'name':name,'passed':True,'detail':extra});print('PASS',name,flush=True)
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
 check('3730 actual catalogue IDs and L1-L4 counts',lambda:need(page.evaluate('WX_DATA.assets.length===3730&&JSON.stringify(WXStudioCore.counts(WX_DATA.assets).levels)===JSON.stringify({1:1600,2:1010,3:1000,4:120})')))
 def select(ident,shot=None):
  page.evaluate('async id=>{await WX_LIVE_QA.select(id)}',ident);wait();s=state();need(not s['error'],str(s));need(s['glb'] and s['triangles']>0,str(s))
  if shot:page.screenshot(path=str(OUT/(shot+'.png')))
  return s
 for ident,shot in [('core.human.head','human-head'),('exp.creature.raptor_head','raptor-head'),('l1.architecture.drainage.half_round','open-gutter'),('l1.interior.fixture.outlet_plate','socket'),('l1.architecture.column.twisted','twisted-column'),('l1.nature.flower.pompom','flower'),('exp.nature.willow_curtain','willow'),('exp-transport-propeller_plane','airplane'),('fnd-adult','adult'),('exp-scene-airport','airport')]:
  check('Actual GLB load and draw '+ident,lambda i=ident,s=shot:select(i,s))
 def parameter():
  select('l1.architecture.column.twisted');before=state()['signature'];spec=page.evaluate('WX_LIVE_QA.getSpec()');spec.setdefault('params',{})['twist_degrees']=0
  page.evaluate('async s=>{await WX_LIVE_QA.commit(s)}',spec);wait();after=state();need(after['signature']!=before,'Twist did not affect buffer');need(not after['error']);page.screenshot(path=str(OUT/'twist-zero.png'));return {'before':before,'after':after['signature']}
 check('Explicit twist-degrees changes real geometry',parameter)
 def styles():
  select('l1.interior.fixture.outlet_plate');s=page.evaluate('WX_LIVE_QA.getSpec()');s['style']='toon';page.evaluate('async s=>{await WX_LIVE_QA.commit(s)}',s);wait();r=state();need(not r['error'] and r['glb']);need(page.evaluate('WX_LIVE_QA.stats().style')=='toon');page.screenshot(path=str(OUT/'socket-toon.png'));return r
 check('Toon style rebuild retains actual open socket GLB',styles)
 def export():
  select('exp.creature.raptor_head')
  with page.expect_download(timeout=60000) as got:page.locator('#exportBtn').click()
  d=got.value
  with tempfile.TemporaryDirectory() as temp:
   path=Path(temp)/'asset.glb';d.save_as(path);raw=path.read_bytes();need(raw[:4]==b'glTF');need(len(raw)>100);downloads.append({'name':d.suggested_filename,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
  return downloads[-1]
 check('Visible export button downloads real GLB',export)
 def narrow():
  page.set_viewport_size({'width':430,'height':900});page.wait_for_timeout(500);need(page.locator('canvas').count()>0);need(not state()['error']);page.screenshot(path=str(OUT/'narrow-430.png'));return {'width':430,'height':900,'physical_device':False}
 check('Narrow desktop viewport still draws without build error',narrow)
 check('No page JavaScript exceptions',lambda:need(not errors,str(errors)))
 renderer=state();browser.close()
report={'version':'3.10.0','scope':'legacy Studio interactions checked against the current Studio dev server','studio_url':studio_url,'results':results,'passed':sum(r['passed'] for r in results),'failed':sum(not r['passed'] for r in results),'page_errors':errors,'downloads':downloads,'final_render_state':renderer,'limitations':'Headless desktop Chromium only. CPU fallback or software WebGL is not physical GPU, mobile-device, full-PBR, physics or commercial-art certification.'}
(OUT/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'failed':report['failed']}),flush=True)
if report['failed']:raise SystemExit(1)
