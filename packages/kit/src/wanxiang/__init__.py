"""Wanxiang 3D: local-first, agent-native procedural asset production."""
__version__ = "3.10.0"

# CPU rendering caches are writable state, never package installation resources.
import os
from pathlib import Path
from .paths import WORKSPACE_ROOT
os.environ.setdefault('NUMBA_CACHE_DIR', str(Path(os.environ.get('WX_CACHE_DIR', str(WORKSPACE_ROOT / '.wx-cache'))).expanduser() / 'numba'))
