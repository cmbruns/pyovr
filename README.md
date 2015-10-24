# pyovr
### Python bindings for Oculus Rift SDK

![Screenshot of pygame/RiftDemo.py](https://raw.githubusercontent.com/cmbruns/pyovr/master/examples/pygame/RiftDemo.png)

## Installation
- [ ] Install Python 2.7 https://www.python.org/download/releases/2.7/ (32-bit version)
- [ ] Install Oculus Rift Runtime 0.8.0 https://developer.oculus.com/downloads/pc/0.8.0.0-beta/Oculus_Runtime_for_Windows/
- [ ] ``pip install ovr``

If the above command fails, you might need to install `pip` http://stackoverflow.com/questions/4750806/how-to-install-pip-on-windows

Alternatively, you can get the pyovr installer at github: https://github.com/cmbruns/pyovr/releases

## Use

```python
import sys
import time
import ovr

ovr.initialize(None)
hmd, luid = ovr.create()
hmdDesc = ovr.getHmdDesc(hmd)
print hmdDesc.ProductName
for t in range(100):
    # Query the HMD for the current tracking state.
    ts  = ovr.getTrackingState(hmd, ovr.getTimeInSeconds(), True)
    if ts.StatusFlags & (ovr.Status_OrientationTracked | ovr.Status_PositionTracked):
        pose = ts.HeadPose
        print pose.ThePose
        sys.stdout.flush()
    time.sleep(0.200)
ovr.destroy(hmd)
ovr.shutdown()
```

Look in the "examples" folder for more example code.

See the Oculus developer documentation for more details. https://developer.oculus.com/documentation/pcsdk/latest/concepts/book-dg/ NOTE you will need to mentally translate the example code from C++ to python.

## Details
Runs on Windows only at the moment, but so does OVR SDK 0.8.0

This python module uses the installed 32-bit OVR dll on Windows, so you must have the Oculus 0.8 Runtime installed to use this module. Get the Oculus Runtime at https://developer.oculus.com/downloads/pc/0.8.0.0-beta/Oculus_Runtime_for_Windows/

This module also assumes you are running a 32-bit version of python. In particular, it was developed and tested with 32-bit Python version 2.7 installed from https://www.python.org/downloads/release/python-2710/

## Other python bindings for libOVR:
* https://github.com/jherico/python-ovrsdk/ maybe not quite updated to SDK 0.4.4 yet
* https://github.com/wwwtyro/python-ovrsdk/ updated to SDK 0.3.2



