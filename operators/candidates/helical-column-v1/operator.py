"""Explicitly trusted SDK candidate: helical metal brace around a stone column."""
import numpy as np
from wanxiang.ir import AssetIR
from wanxiang.geometry import cylinder,sweep
from wanxiang.errors import WXError

def build(params,seed):
    height=float(params.get('height',2));turns=int(params.get('turns',3))
    if not .5<=height<=5 or not 1<=turns<=8:raise WXError('RECIPE_INVALID','height .5..5 and turns 1..8 are required')
    ir=AssetIR();ir.add('column',cylinder(.22,height,24),'stone')
    a=np.linspace(0,turns*2*np.pi,turns*32+1);points=np.column_stack([.31*np.cos(a),np.linspace(.08,height-.08,len(a)),.31*np.sin(a)])
    ir.add('helical_brace',sweep(points,.035,8),'copper');ir.socket('base','column');ir.socket('top','column',[0,height,0]);return ir
