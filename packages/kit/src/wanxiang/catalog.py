from .paths import require_resources
from pathlib import Path
import json,re,sqlite3
from .util import ROOT,read_json,write_json
from .errors import WXError

def records(kind=None):
    require_resources()
    result=[]
    for k,folder in [('recipe','recipes'),('component','components'),('style','styles'),('part','parts'),('assembly','assemblies')]:
        if kind and kind!=k:continue
        for p in sorted((ROOT/'library'/folder).glob('*.json')):
            d=read_json(p);result.append({**d,'kind':k,'file':str(p)})
    if not kind or kind=='material':
        for p in sorted((ROOT/'library/materials').glob('*/material.json')):result.append({**read_json(p),'kind':'material','file':str(p)})
    if not kind or kind=='pattern':
        for p in (ROOT/'library/patterns').glob('*.json'):
            for d in read_json(p):result.append({**d,'kind':'pattern','file':str(p)})
    return result

def get_recipe(id):
    p=Path(id)
    if p.suffix.lower() in ('.json','.yaml','.yml') and p.is_file():return read_json(p),p
    for item in records():
        if item['kind'] in ('recipe','component') and item['id']==id:return read_json(item['file']),Path(item['file'])
    raise WXError('RECIPE_INVALID',f'Recipe/component not found: {id}')

def search(query='',kind=None,limit=10):
    toks=re.findall(r'[a-z0-9_.-]+|[\u4e00-\u9fff]+',query.lower());scored=[]
    for r in records(kind):
        text=' '.join([r.get('id',''),r.get('name',''),*r.get('aliases',[]),*r.get('tags',[])]).lower();score=0
        for t in toks:
            if t in text:score+=10+len(t)
            elif len(t)>2 and re.search('[\u4e00-\u9fff]',t):score+=sum(2 for i in range(len(t)-1) if t[i:i+2] in text)
        if not toks or score:
            scored.append((score,r))
    scored.sort(key=lambda x:(-x[0],x[1]['id']))
    return [{'id':r['id'],'name':r.get('name',r['id']),'kind':r['kind'],'category':r.get('category'),'score':s,'status':r.get('status','implemented'),'file':r['file'],'limitations':r.get('limitations',[])[:2]} for s,r in scored[:max(1,min(limit,1000))]]

def index(workspace):
    p=Path(workspace)/'index.sqlite';p.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(p) as db:
        db.execute('CREATE TABLE IF NOT EXISTS records(id TEXT, kind TEXT, content TEXT, PRIMARY KEY(id,kind))');db.execute('DELETE FROM records')
        for r in records():db.execute('INSERT INTO records VALUES(?,?,?)',(r['id'],r['kind'],json.dumps(r,ensure_ascii=False)))
    return {'path':str(p),'count':len(records()),'source_of_truth':'versioned library files; SQLite can be rebuilt'}
