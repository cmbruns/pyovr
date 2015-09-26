import ovr

# Run test program
if __name__ == "__main__":
    # Transcribed from initial example at 
    # https://developer.oculus.com/documentation/pcsdk/latest/concepts/dg-sensor/
    ovr.initialize(None)
    hmd, luid = ovr.create()
    desc = ovr.getHmdDesc(hmd)
    print desc.Resolution
    print desc.ProductName
    # Start the sensor which provides the Rift's pose and motion.
    ovr.configureTracking(hmd, 
        ovr.TrackingCap_Orientation | # requested capabilities
        ovr.TrackingCap_MagYawCorrection |
        ovr.TrackingCap_Position, 
        0) # required capabilities
    # Query the HMD for the current tracking state.
    ts  = ovr.getTrackingState(hmd, ovr.getTimeInSeconds())
    if ts.StatusFlags & (ovr.Status_OrientationTracked | ovr.Status_PositionTracked):
        pose = ts.HeadPose
        print pose.ThePose
        # TODO:

    ovr.destroy(hmd)
    ovr.shutdown()

