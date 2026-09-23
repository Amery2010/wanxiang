"""External assets may be inspected, but are not admitted as authored components."""
from .errors import WXError

def register(*args, **kwargs):
    raise WXError('FORMAT_UNSUPPORTED', 'v1.5 contains authored faceted components only. Open external GLB in Studio for inspection/export; write an explicit control-profile recipe to create a style-switchable component.')
