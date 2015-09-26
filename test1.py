import time
import sys

import ovr

# Option 1: Straight wrapper around OVR C API
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
    time.sleep(0.500)
ovr.destroy(hmd)
ovr.shutdown()
