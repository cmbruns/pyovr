
# First try loading API 0.8.0
try:
    from _ovr080 import *
except:
    raise
    # fall through to load 0.7.0
    try:
        from _ovr070 import *
    except:
        print "Do you have the Oculus Runtime installed?"
        raise
