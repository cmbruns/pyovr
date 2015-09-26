"""
Python module "ovr"
Python bindings for Oculus Rift SDK version 0.7.0

Windows only at the moment (just like Oculus Rift SDK...)
"""

import ctypes
from ctypes import byref
import sys

# Load Oculus runtime library
# Assumes Oculus Runtime 0.7 install on 32 bit windows
try:
    libovr = ctypes.cdll.LibOVRRT32_0_7
except:
    print "Is Oculus Runtime 0.7 installed on this Windows machine?"
    raise


### Below is translation of relevant declarations from C header file OVR_CAPI_0_7_0.h

# I remove the "ovr_" prefix from class names, because these will be in the "ovr" package.
# So, for example, "ovr_Vector2i" would become "ovr.Vector2i"

# A 2D vector with integer components.
# OVR_CAPI_0_7_0.h line 287
class Vector2i(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        # int x, y;
        ("x", ctypes.c_int), # 
        ("y", ctypes.c_int), # 
    ]
    
    def __repr__(self):
        return "Vector2i(%d, %d)" % (self.x, self.y)


# A 2D size with integer components.
# OVR_CAPI_0_7_0.h line 293
class Sizei(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        # int w, h;
        ("w", ctypes.c_int),
        ("h", ctypes.c_int),
    ]
    
    def __repr__(self):
        return "Sizei(%d, %d)" % (self.w, self.h)


# A 2D rectangle with a position and size.
# All components are integers.
# OVR_CAPI_0_7_0.h line 298
class Recti(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ("Pos", Vector2i), # ovrVector2i Pos;
        ("Size", Sizei), # ovrSizei    Size;
    ]
    
    def __repr__(self):
        return "Recti(Pos=%s, Size=%s)" % (self.Pos, self.Size)


# A quaternion rotation.
# OVR_CAPI_0_7_0.h line 306
class Quatf(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        # float x, y, z, w;
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
        ("w", ctypes.c_float),
    ]
    
    def __repr__(self):
        return "Quatf(x=%f, y=%f, z=%f, w=%f)" % (self.x, self.y, self.z, self.w)


# A 2D vector with float components.
# OVR_CAPI_0_7_0.h line 312
class Vector2f(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        # float x, y;
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
    ]
    
    def __repr__(self):
        return "Vector2f(%f, %f)" % (self.x, self.y)


# A 3D vector with float components.
# OVR_CAPI_0_7_0.h line 318
class Vector3f(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        # float x, y, z;
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
    ]
    
    def __repr__(self):
        return "Vector3f(%f, %f, %f)" % (self.x, self.y, self.z)


# A 4x4 matrix with float elements.
# OVR_CAPI_0_7_0.h line 324
class Matrix4f(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        # float M[4][4];
        ("M", (ctypes.c_float * 4) * 4),
    ]
    
    def __repr__(self):
        return "Matrix4f(%f, %f, %f)" % (self.x, self.y, self.z)


# Position and orientation together.
# OVR_CAPI_0_7_0.h line 331
class Posef(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ("Orientation", Quatf), # ovrQuatf     Orientation;
        ("Position", Vector3f), # ovrVector3f  Position;
    ]
    
    def __repr__(self):
        return "Posef(Orientation=%s, Position=%s)" % (self.Orientation, self.Position)


# A full pose (rigid body) configuration with first and second derivatives.
#
# Body refers to any object for which ovrPoseStatef is providing data.
# It can be the camera or something else; the context depends on the usage of the struct.
# OVR_CAPI_0_7_0.h line 338
class PoseStatef(ctypes.Structure):
    _pack_ = 8
    _fields_ = [
        ("ThePose", Posef), # ovrPosef     ThePose;               #< The body's position and orientation.
        ("AngularVelocity", Vector3f), # ovrVector3f  AngularVelocity;       #< The body's angular velocity in radians per second.
        ("LinearVelocity", Vector3f), # ovrVector3f  LinearVelocity;        #< The body's velocity in meters per second.
        ("AngularAcceleration", Vector3f), # ovrVector3f  AngularAcceleration;   #< The body's angular acceleration in radians per second per second.
        ("LinearAcceleration", Vector3f), # ovrVector3f  LinearAcceleration;    #< The body's acceleration in meters per second per second.
        ("pad0", ctypes.c_char * 4), # OVR_UNUSED_STRUCT_PAD(pad0, 4)      #< \internal struct pad.
        ("TimeInSeconds", ctypes.c_double), # double       TimeInSeconds;         #< Absolute time of this state sample.
    ]


# Describes the up, down, left, and right angles of the field of view.
#
# Field Of View (FOV) tangent of the angle units.
# \note For a standard 90 degree vertical FOV, we would
# have: { UpTan = tan(90 degrees / 2), DownTan = tan(90 degrees / 2) }.
# OVR_CAPI_0_7_0.h line 358
class FovPort(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ("UpTan", ctypes.c_float), # float UpTan;    #< The tangent of the angle between the viewing vector and the top edge of the field of view.
        ("DownTan", ctypes.c_float), # float DownTan;  #< The tangent of the angle between the viewing vector and the bottom edge of the field of view.
        ("LeftTan", ctypes.c_float), # float LeftTan;  #< The tangent of the angle between the viewing vector and the left edge of the field of view.
        ("RightTan", ctypes.c_float), # float RightTan; #< The tangent of the angle between the viewing vector and the right edge of the field of view.
    ]


#-----------------------------------------------------------------------------------
# ***** HMD Types

# Enumerates all HMD types that we support.
# The currently released developer kits are ovrHmd_DK1 and ovrHmd_DK2. The other enumerations are for internal use only.
# OVR_CAPI_0_7_0.h line 370
# enum ovrHmdType
Hmd_None      = 0
Hmd_DK1       = 3
Hmd_DKHD      = 4
Hmd_DK2       = 6
Hmd_CB        = 8
Hmd_Other     = 9
Hmd_E3_2015   = 10
Hmd_ES06      = 11


# HMD capability bits reported by device.
#
# Set <B>(read/write)</B> flags through ovr_SetEnabledCaps()
# OVR_CAPI_0_7_0.h line 387
# enum ovrHmdCaps
# Read-only flags.
HmdCap_DebugDevice         = 0x0010  #< <B>(read only)</B> Specifies that the HMD is a virtual debug device.
# Indicates to the developer what caps they can and cannot modify. These are processed by the client.
HmdCap_Writable_Mask       = 0x0000
HmdCap_Service_Mask        = 0x0000


# Tracking capability bits reported by the device.
# Used with ovr_ConfigureTracking.
# OVR_CAPI_0_7_0.h line 407
# enum ovrTrackingCaps
TrackingCap_Orientation      = 0x0010   #< Supports orientation tracking (IMU).
TrackingCap_MagYawCorrection = 0x0020   #< Supports yaw drift correction via a magnetometer or other means.
TrackingCap_Position         = 0x0040   #< Supports positional tracking.
# Overriding the other flags, this causes the application
# to ignore tracking settings. This is the internal
# default before ovr_ConfigureTracking is called.
TrackingCap_Idle             = 0x0100


# Specifies which eye is being used for rendering.
# This type explicitly does not include a third "NoStereo" monoscopic option, as such is
# not required for an HMD-centered API.
# OVR_CAPI_0_7_0.h line 420
# enum ovrEyeType
Eye_Left     = 0         #< The left eye, from the viewer's perspective.
Eye_Right    = 1         #< The right eye, from the viewer's perspective.
Eye_Count    = 2         #< \internal Count of enumerated elements.


# OVR_CAPI_0_7_0.h line 432
class GraphicsLuid(ctypes.Structure):
    _pack_ = 4
    # Public definition reserves space for graphics API-specific implementation
    _fields_ = [ ("Reserved", ctypes.c_char * 8), ] # char  Reserved[8];


# This is a complete descriptor of the HMD.
# OVR_CAPI_0_7_0.h line 439
class HmdDesc(ctypes.Structure):
    _fields_ = [
        ("Type", ctypes.c_uint), # ovrHmdType   Type;                         #< The type of HMD.
        # we are not on a 64-bit arch... ("",), # OVR_ON64(OVR_UNUSED_STRUCT_PAD(pad0, 4))   #< \internal struct paddding.
        ("ProductName", ctypes.c_char * 64), # char         ProductName[64];              #< UTF8-encoded product identification string (e.g. "Oculus Rift DK1").
        ("Manufacturer", ctypes.c_char * 64), # char         Manufacturer[64];             #< UTF8-encoded HMD manufacturer identification string.
        ("VendorId", ctypes.c_short), # short        VendorId;                     #< HID (USB) vendor identifier of the device.
        ("ProductId", ctypes.c_short), # short        ProductId;                    #< HID (USB) product identifier of the device.
        ("SerialNumber", ctypes.c_char * 24), # char         SerialNumber[24];             #< Sensor (and display) serial number.
        ("FirmwareMajor", ctypes.c_short), # short        FirmwareMajor;                #< Sensor firmware major version.
        ("FirmwareMinor", ctypes.c_short), # short        FirmwareMinor;                #< Sensor firmware minor version.
        ("CameraFrustumHFovInRadians", ctypes.c_float), # float        CameraFrustumHFovInRadians;   #< External tracking camera frustum horizontal field-of-view (if present).
        ("CameraFrustumVFovInRadians", ctypes.c_float), # float        CameraFrustumVFovInRadians;   #< External tracking camera frustum vertical field-of-view (if present).
        ("CameraFrustumNearZInMeters", ctypes.c_float), # float        CameraFrustumNearZInMeters;   #< External tracking camera frustum near Z (if present).
        ("CameraFrustumFarZInMeters", ctypes.c_float), # float        CameraFrustumFarZInMeters;    #< External tracking camera frustum far Z (if present).
        ("AvailableHmdCaps", ctypes.c_uint), # unsigned int AvailableHmdCaps;             #< Capability bits described by ovrHmdCaps which the HMD currently supports.
        ("DefaultHmdCaps", ctypes.c_uint), # unsigned int DefaultHmdCaps;               #< Capability bits described by ovrHmdCaps which are default for the current Hmd.
        ("AvailableTrackingCaps", ctypes.c_uint), # unsigned int AvailableTrackingCaps;        #< Capability bits described by ovrTrackingCaps which the system currently supports.
        ("DefaultTrackingCaps", ctypes.c_uint), # unsigned int DefaultTrackingCaps;          #< Capability bits described by ovrTrackingCaps which are default for the current system.
        ("DefaultEyeFov", FovPort * Eye_Count), # ovrFovPort   DefaultEyeFov[ovrEye_Count];  #< Defines the recommended FOVs for the HMD.
        ("MaxEyeFov", FovPort * Eye_Count), # ovrFovPort   MaxEyeFov[ovrEye_Count];      #< Defines the maximum FOVs for the HMD.
        ("Resolution", Sizei), # ovrSizei     Resolution;                   #< Resolution of the full HMD screen (both eyes) in pixels.
        ("DisplayRefreshRate", ctypes.c_float), # float        DisplayRefreshRate;           #< Nominal refresh rate of the display in cycles per second at the time of HMD creation.
        # we are not on a 64-bit arch... ("",), # OVR_ON64(OVR_UNUSED_STRUCT_PAD(pad1, 4))   #< \internal struct paddding.
    ]


# Used as an opaque pointer to an OVR session.
# OVR_CAPI_0_7_0.h line 467
class _HmdStruct(ctypes.Structure):
    "Used as an opaque pointer to an OVR session."
    pass
Hmd = ctypes.POINTER(_HmdStruct)


# Bit flags describing the current status of sensor tracking.
#  The values must be the same as in enum StatusBits
#
# \see ovrTrackingState
#
# OVR_CAPI_0_7_0.h line 476
# enum ovrStatusBits
Status_OrientationTracked    = 0x0001    #< Orientation is currently tracked (connected and in use).
Status_PositionTracked       = 0x0002    #< Position is currently tracked (false if out of range).
Status_CameraPoseTracked     = 0x0004    #< Camera pose is currently tracked.
Status_PositionConnected     = 0x0020    #< Position tracking hardware is connected.
Status_HmdConnected          = 0x0080    #< HMD Display is available and connected.


# Specifies a reading we can query from the sensor.
#
# \see ovrTrackingState
#
# OVR_CAPI_0_7_0.h line 487
class SensorData(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ("Accelerometer", Vector3f), # ovrVector3f    Accelerometer;    #< Acceleration reading in meters/second^2.
        ("Gyro", Vector3f), # ovrVector3f    Gyro;             #< Rotation rate in radians/second.
        ("Magnetometer", Vector3f), # ovrVector3f    Magnetometer;     #< Magnetic field in Gauss.
        ("Temperature", ctypes.c_float), # float          Temperature;      #< Temperature of the sensor in degrees Celsius.
        ("TimeInSeconds", ctypes.c_float), # float          TimeInSeconds;    #< Time when the reported IMU reading took place in seconds. \see ovr_GetTimeInSeconds
    ]


# Tracking state at a given absolute time (describes predicted HMD pose, etc.).
# Returned by ovr_GetTrackingState.
#
# \see ovr_GetTrackingState
#
# OVR_CAPI_0_7_0.h line 501
class TrackingState(ctypes.Structure):
    _pack_ = 8
    _fields_ = [
        # Predicted head pose (and derivatives) at the requested absolute time.
        # The look-ahead interval is equal to (HeadPose.TimeInSeconds - RawSensorData.TimeInSeconds).
        ("HeadPose", PoseStatef), # ovrPoseStatef  HeadPose;
        # Current pose of the external camera (if present).
        # This pose includes camera tilt (roll and pitch). For a leveled coordinate
        # system use LeveledCameraPose.
        ("CameraPose", Posef), # ovrPosef       CameraPose;
        # Camera frame aligned with gravity.
        # This value includes position and yaw of the camera, but not roll and pitch.
        # It can be used as a reference point to render real-world objects in the correct location.
        ("LeveledCameraPose", Posef), # ovrPosef       LeveledCameraPose;
        # The most recent calculated pose for each hand when hand controller tracking is present.
        # HandPoses[ovrHand_Left] refers to the left hand and HandPoses[ovrHand_Right] to the right hand.
        # These values can be combined with ovrInputState for complete hand controller information.
        ("HandPoses", PoseStatef * 2), # ovrPoseStatef  HandPoses[2];
        # The most recent sensor data received from the HMD.
        ("RawSensorData", SensorData), # ovrSensorData  RawSensorData;
        # Tracking status described by ovrStatusBits.
        ("StatusFlags", ctypes.c_uint), # unsigned int   StatusFlags;
        # Tags the vision processing results to a certain frame counter number.
        ("LastCameraFrameCounter", ctypes.c_uint32), # uint32_t       LastCameraFrameCounter;
        ("pad0", ctypes.c_char * 4), # OVR_UNUSED_STRUCT_PAD(pad0, 4) #< \internal struct padding
    ]


# Frame timing data reported by ovr_GetFrameTiming.
#
# \see ovr_GetFrameTiming
#
# OVR_CAPI_0_7_0.h line 541
class FrameTiming(ctypes.Structure):
    _pack_ = 8
    _fields_ = [
    # A point in time when the middle of the screen will be displayed. For global shutter,
    # this will be the display time. For rolling shutter this is a point at which half the image has
    # been displayed. This value can be passed as an absolute time to ovr_GetTrackingState
    # to get the best predicted pose for rendering the scene.
    ("DisplayMidpointSeconds", ctypes.c_double), # double      DisplayMidpointSeconds;
    # Display interval between the frames. This will generally be 1 / RefreshRate of the HMD;
    # however, it may vary slightly during runtime based on video cart scan-out timing.
    ("FrameIntervalSeconds", ctypes.c_double), # double      FrameIntervalSeconds;
    # Application frame index for which we requested timing.
    ("AppFrameIndex", ctypes.c_uint), # unsigned    AppFrameIndex;
    # HW display frame index that we expect this application frame will hit; this is the frame that
    # will be displayed at DisplayMidpointSeconds. This value is monotonically increasing with each v-sync.
    ("DisplayFrameIndex", ctypes.c_uint), # unsigned    DisplayFrameIndex;
    ]


# functions:

def SUCCESS(result):
    return result >= 0

def FAILURE(result):
    return not SUCCESS(result)

configureTracking = libovr.ovr_ConfigureTracking

def create():
    hmd = Hmd()
    luid = GraphicsLuid()
    result = libovr.ovr_Create(byref(hmd), byref(luid))
    if FAILURE(result):
        raise Exception("ovr.create() failed. Is the Oculus Rift On?")
    return hmd, luid    

def destroy(hmd):
    libovr.ovr_Destroy(hmd)

getHmdDesc = libovr.ovr_GetHmdDesc
getHmdDesc.restype = HmdDesc

getTimeInSeconds = libovr.ovr_GetTimeInSeconds
getTimeInSeconds.restype = ctypes.c_double

getTrackingState = libovr.ovr_GetTrackingState
getTrackingState.restype = TrackingState
getTrackingState.argtypes = [Hmd, ctypes.c_double]

def initialize(arg):
    result = libovr.ovr_Initialize(arg)
    if FAILURE(result):
        raise "ovr.initialize failed"
    
shutdown = libovr.ovr_Shutdown


# Run test program
if __name__ == "__main__":
    # Transcribed from initial example at 
    # https://developer.oculus.com/documentation/pcsdk/latest/concepts/dg-sensor/
    initialize(None)
    hmd, luid = create()
    desc = getHmdDesc(hmd)
    print desc.Resolution
    print desc.ProductName
    # Start the sensor which provides the Rift's pose and motion.
    configureTracking(hmd, 
        TrackingCap_Orientation | # requested capabilities
        TrackingCap_MagYawCorrection |
        TrackingCap_Position, 
        0) # required capabilities
    # Query the HMD for the current tracking state.
    ts  = getTrackingState(hmd, getTimeInSeconds())
    if ts.StatusFlags & (Status_OrientationTracked | Status_PositionTracked):
        pose = ts.HeadPose
        print pose.ThePose
        # TODO:

    destroy(hmd)
    shutdown()

