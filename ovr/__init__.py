
from .version import __version__

# First try loading API 0.8.0
try:
    from _ovr080 import *
except:
    raise
