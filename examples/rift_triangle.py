#!/bin/env python

import ovr

class RiftTriangle():
    "Example program for Oculus Rift rendering in python"

    def __init__(self):
        self.hmd = None
    
    def __enter__(self):
        ovr.initialize(None)
        self.hmd, luid = ovr.create()
        self.hmdDesc = ovr.getHmdDesc(self.hmd)
        ovr.configureTracking(self.hmd, 
            ovr.TrackingCap_Orientation | # supported
            ovr.TrackingCap_MagYawCorrection |
            ovr.TrackingCap_Position, 
            0) # required
        print "Rift screen size = ", self.hmdDesc.Resolution
        return self

    def __exit__(self, arg2, arg3, arg4):
        ovr.destroy(self.hmd)
        ovr.shutdown()

    def current_state(self):
        ts = ovr.getTrackingState(self.hmd, ovr.getTimeInSeconds())
        return ts


if __name__ == "__main__":
    with RiftTriangle() as app:
        for t in range(10):
            ts = app.current_state()
            print ts.HeadPose.ThePose

