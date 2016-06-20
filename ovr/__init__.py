
from .version import __version__

try:
    from _ovr140 import *
except:
    raise
