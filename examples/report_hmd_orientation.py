#!/bin/env python

import time
import sys

import ovr

# Option 1: Straight wrapper around OVR C API
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
    time.sleep(0.500)
ovr.destroy(hmd)
ovr.shutdown()

