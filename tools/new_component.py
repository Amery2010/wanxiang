"""Scaffold an authored component plus a pytest contract, without frozen meshes.

Write to a review directory first. Install the JSON into authoring/overrides/parts
and the test into tests only after reviewing the chosen ID and physical semantics.
"""
from pathlib import Path
import argparse,json,re

def scaffold(ident,name,out):
    if not re.fullmatch(r'[a-z][a-z0-9_.-]{2,80}',ident) or '..' in ident:raise ValueError('Use a safe lowercase semantic ID')
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    points=[[-.5,0,-.5],[.5,0,-.5],[.5,0,.5],[-.5,0,.5],[-.5,1,-.5],[.5,1,-.5],[.5,1,.5],[-.5,1,.5]]
    faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
    d={'schema':'wx.part/1.0','id':ident,'name':name,'version':'3.0.0','category':'terrain','theme':'shared','level':1,'shape':'faceted','size':[1,1,1],'anchor':'base','material':'mat.stone','parameter_schema':{'properties':{}},'shape_params':{'forms':[{'kind':'poly','points':points,'faces':faces,'color':'#9B9788'}]},'connectors':[{'id':'top','interface':'arch.floor.1m.v1','version':1,'position':[0,1,0],'normal':[0,1,0],'tangent':[1,0,0],'span':1,'gender':'neutral','allowed_scale':'none'}],'runtime':{'schema':'wx.runtime-metadata/1.0','units':'m','up':'+Y','forward':'+Z','origin':'authored-ground-contact','collision':{'type':'box','size':[1,1,1],'center':[0,.5,0]},'triangle_budget':100,'lod':{'levels':[]}},'quality':{'status':'expansion','review_scope':'custom-pending-review'},'tags':['custom','模板'],'source':{'type':'original_procedural','authoring':'authoring/overrides/parts/'+ident+'.json','revision':'3.0.0','license':'project-authored'}}
    path=out/(ident+'.json')
    if path.exists():raise FileExistsError(path)
    path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
    test='''"""Move alongside the installed author override; never inferred approval."""
import pytest
from wanxiang.kit_parts import build_part
from wanxiang.contracts import validate_connector
@pytest.mark.parametrize("style",["lowpoly","toon"])
def test_authored_component_contract(style):
    asset=build_part(%r,style)
    assert asset.meshes and asset.metadata['runtime']['collision']['type']=='box'
    for socket in asset.sockets:validate_connector(socket)
'''%ident
    (out/('test_'+ident.replace('.','_').replace('-','_')+'.py')).write_text(test)
    return {'definition':str(path),'installed':False,'next':'Review then install into authoring/overrides/parts; rebuild transactionally.'}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--id',required=True);p.add_argument('--name',required=True);p.add_argument('--out',required=True);a=p.parse_args();print(json.dumps(scaffold(a.id,a.name,a.out),ensure_ascii=False,indent=2))
