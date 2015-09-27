# pyovr
### Python bindings for Oculus Rift SDK

## Installation
- [ ] ```git clone https://github.com/cmbruns/pyovr.git```
- [ ] ```cd pyovr```
- [ ] ```python setup.py install```

## Use

```python
import sys
import time
import ovr

ovr.initialize(None)
hmd, luid = ovr.create()
hmdDesc = ovr.getHmdDesc(hmd)
print hmdDesc.ProductName
# Start the sensor which provides the Rift's pose and motion.
ovr.configureTracking(hmd, 
    ovr.TrackingCap_Orientation | # supported capabilities
    ovr.TrackingCap_MagYawCorrection |
    ovr.TrackingCap_Position, 
    0) # required capabilities
while True:
    # Query the HMD for the current tracking state.
    ts  = ovr.getTrackingState(hmd, ovr.getTimeInSeconds())
    if ts.StatusFlags & (ovr.Status_OrientationTracked | ovr.Status_PositionTracked):
        pose = ts.HeadPose
        print pose.ThePose
        sys.stdout.flush()
    time.sleep(0.200)
ovr.destroy(hmd)
ovr.shutdown()
```

## Details
Runs on Windows only at the moment, but so does OVR SDK 0.7.0

This python module uses the installed 32-bit OVR dll on Windows, so you must have the Oculus 0.7 Runtime installed to use this module. Get the Oculus Runtime at https://developer.oculus.com/downloads/pc/0.7.0.0-beta/Oculus_Runtime_for_Windows/

This module also assumes you are running a 32-bit version of python. In particular, it was developed and tested with 32-bit Python version 2.7 installed from https://www.python.org/downloads/release/python-2710/

## Other python bindings for libOVR:
* https://github.com/jherico/python-ovrsdk/ maybe not quite updated to SDK 0.4.4 yet
* https://github.com/wwwtyro/python-ovrsdk/ updated to SDK 0.3.2



