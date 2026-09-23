"""Verify the standalone evidence catalogue with the actual embedded images."""
from pathlib import Path
import json, os
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];E=R/'generated/verification';results=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('WX_CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1440,'height':1050});errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    def check(name,ok):
        results.append({'name':name,'passed':bool(ok)})
        if not ok:raise AssertionError(name)
    page.set_content((R/'docs/game410/index.html').read_text(),wait_until='load');page.wait_for_selector('.card')
    check('All 130 entries visible',page.locator('.card').count()==130)
    page.locator('#kit').select_option('dungeon');check('Kit has 12 parts and 1 example',page.locator('.card').count()==13)
    page.locator('#level').select_option('1');check('L1 filter separates examples',page.locator('.card').count()==12)
    page.locator('#kit').select_option('');page.locator('#level').select_option('2');check('Ten L2 examples',page.locator('.card').count()==10)
    page.locator('#level').select_option('');page.locator('#search').fill('climbing_harness');check('ID search returns exact part',page.locator('.card').count()==1)
    page.locator('.card').click();page.wait_for_function("document.querySelector('#views').naturalWidth===960")
    check('Modal decodes actual multi-view image',page.locator('dialog').is_visible() and page.locator('#views').evaluate('(i)=>i.naturalHeight')==348)
    page.locator('#close').click();page.locator('#search').fill('');page.locator('#kit').select_option('dungeon');page.wait_for_timeout(250)
    page.screenshot(path=str(E/'browser/catalogue.png'))
    page.set_viewport_size({'width':430,'height':900});page.wait_for_timeout(150)
    check('Narrow catalogue has no horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
    page.screenshot(path=str(E/'browser/catalogue-narrow.png'))
    check('No uncaught JavaScript errors',not errors)
    browser.close()
report={'version':'3.10.0','source':'actual standalone HTML through set_content; file URI navigation is restricted by this runner','results':results,'passed':sum(x['passed'] for x in results),'failed':sum(not x['passed'] for x in results)}
(E/'browser/catalogue-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report))
