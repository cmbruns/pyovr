"""
Python module "ovr"
Python bindings for Oculus Rift SDK version 0.7.0

Works on Windows only at the moment (just like Oculus Rift SDK...)
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


# Selected definitions from OVR_ErrorCode.h:

Result = ctypes.c_int32 # OVR_ErrorCode.h line 23

def SUCCESS(result):
    return result >= 0

def FAILURE(result):
    return not SUCCESS(result)


ENUM_TYPE = ctypes.c_uint32


### Below is translation of relevant declarations from C header file OVR_CAPI_0_7_0.h

# I remove the "ovr_" prefix from class names, because these will be in the "ovr" package.
# So, for example, "ovr_Vector2i" would become "ovr.Vector2i"


#-----------------------------------------------------------------------------------
# ***** Word Size
#
# Specifies the size of a pointer on the given platform.
#
# OVR_CAPI_0_7_0.h line 245
OVR_PTR_SIZE = 4 # Only 32-bit python, right?


# OVR_CAPI_0_7_0.h line 287
class Vector2i(ctypes.Structure):
    "A 2D vector with integer components."
    _pack_ = 4
    _fields_ = [
        # int x, y;
        ("x", ctypes.c_int), # 
        ("y", ctypes.c_int), # 
    ]
    
    def __repr__(self):
        return "Vector2i(%d, %d)" % (self.x, self.y)


# OVR_CAPI_0_7_0.h line 293
class Sizei(ctypes.Structure):
    "A 2D size with integer components."
    _pack_ = 4
    _fields_ = [
        # int w, h;
        ("w", ctypes.c_int),
        ("h", ctypes.c_int),
    ]
    
    def __repr__(self):
        return "Sizei(%d, %d)" % (self.w, self.h)


# OVR_CAPI_0_7_0.h line 298
class Recti(ctypes.Structure):
    """
    A 2D rectangle with a position and size.
    All components are integers.
    """
    _pack_ = 4
    _fields_ = [
        ("Pos", Vector2i), # ovrVector2i Pos;
        ("Size", Sizei), # ovrSizei    Size;
    ]
    
    def __repr__(self):
        return "Recti(Pos=%s, Size=%s)" % (self.Pos, self.Size)


# OVR_CAPI_0_7_0.h line 306
class Quatf(ctypes.Structure):
    "A quaternion rotation."
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


# OVR_CAPI_0_7_0.h line 312
class Vector2f(ctypes.Structure):
    "A 2D vector with float components."
    _pack_ = 4
    _fields_ = [
        # float x, y;
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
    ]
    
    def __repr__(self):
        return "Vector2f(%f, %f)" % (self.x, self.y)


# OVR_CAPI_0_7_0.h line 318
class Vector3f(ctypes.Structure):
    "A 3D vector with float components."
    _pack_ = 4
    _fields_ = [
        # float x, y, z;
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
    ]
    
    def __repr__(self):
        return "Vector3f(%f, %f, %f)" % (self.x, self.y, self.z)


# OVR_CAPI_0_7_0.h line 324
class Matrix4f(ctypes.Structure):
    "A 4x4 matrix with float elements."
    _pack_ = 4
    _fields_ = [
        # float M[4][4];
        ("M", (ctypes.c_float * 4) * 4),
    ]
    
    def __repr__(self):
        return "Matrix4f(%f, %f, %f)" % (self.x, self.y, self.z)


# OVR_CAPI_0_7_0.h line 331
class Posef(ctypes.Structure):
    "Position and orientation together."
    _pack_ = 4
    _fields_ = [
        ("Orientation", Quatf), # ovrQuatf     Orientation;
        ("Position", Vector3f), # ovrVector3f  Position;
    ]
    
    def __repr__(self):
        return "Posef(Orientation=%s, Position=%s)" % (self.Orientation, self.Position)


# OVR_CAPI_0_7_0.h line 338
class PoseStatef(ctypes.Structure):
    """
    A full pose (rigid body) configuration with first and second derivatives.
    
    Body refers to any object for which ovrPoseStatef is providing data.
    It can be the camera or something else; the context depends on the usage of the struct.
    """
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


# OVR_CAPI_0_7_0.h line 358
class FovPort(ctypes.Structure):
    """
    Describes the up, down, left, and right angles of the field of view.
    
    Field Of View (FOV) tangent of the angle units.
    \note For a standard 90 degree vertical FOV, we would
    have: { UpTan = tan(90 degrees / 2), DownTan = tan(90 degrees / 2) }.
    """
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
HmdType = ENUM_TYPE
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
HmdCaps = ENUM_TYPE
# Read-only flags.
HmdCap_DebugDevice         = 0x0010  #< <B>(read only)</B> Specifies that the HMD is a virtual debug device.
# Indicates to the developer what caps they can and cannot modify. These are processed by the client.
HmdCap_Writable_Mask       = 0x0000
HmdCap_Service_Mask        = 0x0000


# Tracking capability bits reported by the device.
# Used with ovr_ConfigureTracking.
# OVR_CAPI_0_7_0.h line 407
# enum ovrTrackingCaps
TrackingCaps = ENUM_TYPE
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
EyeType = ENUM_TYPE
Eye_Left     = 0         #< The left eye, from the viewer's perspective.
Eye_Right    = 1         #< The right eye, from the viewer's perspective.
Eye_Count    = 2         #< \internal Count of enumerated elements.


# OVR_CAPI_0_7_0.h line 432
class GraphicsLuid(ctypes.Structure):
    _pack_ = 4
    # Public definition reserves space for graphics API-specific implementation
    _fields_ = [ ("Reserved", ctypes.c_char * 8), ] # char  Reserved[8];


# OVR_CAPI_0_7_0.h line 439
class HmdDesc(ctypes.Structure):
    "This is a complete descriptor of the HMD."
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
        ("DefaultEyeFov", FovPort * Eye_Count), # ovrFovPort   DefaultEyeFov[Eye_Count];  #< Defines the recommended FOVs for the HMD.
        ("MaxEyeFov", FovPort * Eye_Count), # ovrFovPort   MaxEyeFov[Eye_Count];      #< Defines the maximum FOVs for the HMD.
        ("Resolution", Sizei), # ovrSizei     Resolution;                   #< Resolution of the full HMD screen (both eyes) in pixels.
        ("DisplayRefreshRate", ctypes.c_float), # float        DisplayRefreshRate;           #< Nominal refresh rate of the display in cycles per second at the time of HMD creation.
        # we are not on a 64-bit arch... ("",), # OVR_ON64(OVR_UNUSED_STRUCT_PAD(pad1, 4))   #< \internal struct paddding.
    ]


# OVR_CAPI_0_7_0.h line 467
class _HmdStruct(ctypes.Structure):
    "Used as an opaque pointer to an OVR session."
    pass
Hmd = ctypes.POINTER(_HmdStruct)


# Bit flags describing the current status of sensor tracking.
#  The values must be the same as in enum StatusBits
#
# \see TrackingState
#
# OVR_CAPI_0_7_0.h line 476
# enum ovrStatusBits
StatusBits = ENUM_TYPE
Status_OrientationTracked    = 0x0001    #< Orientation is currently tracked (connected and in use).
Status_PositionTracked       = 0x0002    #< Position is currently tracked (false if out of range).
Status_CameraPoseTracked     = 0x0004    #< Camera pose is currently tracked.
Status_PositionConnected     = 0x0020    #< Position tracking hardware is connected.
Status_HmdConnected          = 0x0080    #< HMD Display is available and connected.


# OVR_CAPI_0_7_0.h line 487
class SensorData(ctypes.Structure):
    """
    Specifies a reading we can query from the sensor.
    
    \see TrackingState
    """
    _pack_ = 4
    _fields_ = [
        ("Accelerometer", Vector3f), # ovrVector3f    Accelerometer;    #< Acceleration reading in meters/second^2.
        ("Gyro", Vector3f), # ovrVector3f    Gyro;             #< Rotation rate in radians/second.
        ("Magnetometer", Vector3f), # ovrVector3f    Magnetometer;     #< Magnetic field in Gauss.
        ("Temperature", ctypes.c_float), # float          Temperature;      #< Temperature of the sensor in degrees Celsius.
        ("TimeInSeconds", ctypes.c_float), # float          TimeInSeconds;    #< Time when the reported IMU reading took place in seconds. \see ovr_GetTimeInSeconds
    ]


# OVR_CAPI_0_7_0.h line 501
class TrackingState(ctypes.Structure):
    """
    Tracking state at a given absolute time (describes predicted HMD pose, etc.).
    Returned by ovr_GetTrackingState.
    
    \see ovr_GetTrackingState
    """
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


# OVR_CAPI_0_7_0.h line 541
class FrameTiming(ctypes.Structure):
    """
    Frame timing data reported by ovr_GetFrameTiming.
    
    \see ovr_GetFrameTiming
    """
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


# Rendering information for each eye. Computed by ovr_GetRenderDesc() based on the
# specified FOV. Note that the rendering viewport is not included
# here as it can be specified separately and modified per frame by
# passing different Viewport values in the layer structure.
#
# \see ovr_GetRenderDesc
#
class EyeRenderDesc(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ("Eye", EyeType),                         #< The eye index to which this instance corresponds.
        ("Fov", FovPort),                         #< The field of view.
        ("DistortedViewport", Recti),           #< Distortion viewport.
        ("PixelsPerTanAngleAtCenter", Vector2f),   #< How many display pixels will fit in tan(angle) = 1.
        ("HmdToEyeViewOffset", Vector3f),          #< Translation of each eye.
    ]


# Projection information for ovrLayerEyeFovDepth.
#
# Use the utility function ovrTimewarpProjectionDesc_FromProjection to
# generate this structure from the application's projection matrix.
#
# \see ovrLayerEyeFovDepth, ovrTimewarpProjectionDesc_FromProjection
#
class TimewarpProjectionDesc(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ("Projection22", ctypes.c_float),      #< Projection matrix element [2][2].
        ("Projection23", ctypes.c_float),      #< Projection matrix element [2][3].
        ("Projection32", ctypes.c_float),      #< Projection matrix element [3][2].
    ]


# Contains the data necessary to properly calculate position info for various layer types.
# - HmdToEyeViewOffset is the same value pair provided in ovrEyeRenderDesc.
# - HmdSpaceToWorldScaleInMeters is used to scale player motion into in-application units.
#   In other words, it is how big an in-application unit is in the player's physical meters.
#   For example, if the application uses inches as its units then HmdSpaceToWorldScaleInMeters would be 0.0254.
#   Note that if you are scaling the player in size, this must also scale. So if your application
#   units are inches, but you're shrinking the player to half their normal size, then
#   HmdSpaceToWorldScaleInMeters would be 0.0254*2.0.
#
# \see ovrEyeRenderDesc, ovr_SubmitFrame
#
class ViewScaleDesc(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ("HmdToEyeViewOffset", Vector3f * Eye_Count),    #< Translation of each eye.
        ("HmdSpaceToWorldScaleInMeters", ctypes.c_float),        #< Ratio of viewer units to meter units.
    ]


#-----------------------------------------------------------------------------------
# ***** Platform-independent Rendering Configuration

# These types are used to hide platform-specific details when passing
# render device, OS, and texture data to the API.
#
# The benefit of having these wrappers versus platform-specific API functions is
# that they allow application glue code to be portable. A typical example is an
# engine that has multiple back ends, such as GL and D3D. Portable code that calls
# these back ends can also use LibOVR. To do this, back ends can be modified
# to return portable types such as ovrTexture and ovrRenderAPIConfig.
# enum RenderAPIType
RenderAPIType = ENUM_TYPE
RenderAPI_None         = 0          #< No API
RenderAPI_OpenGL       = 1          #< OpenGL
RenderAPI_Android_GLES = 2          #< OpenGL ES
RenderAPI_D3D11        = 5          #< DirectX 11.
RenderAPI_Count        = 4          #< \internal Count of enumerated elements.


# API-independent part of a texture descriptor.
#
# ovrTextureHeader is a common struct present in all ovrTexture struct types.
#
class TextureHeader(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ("API", RenderAPIType),            #< The API type to which this texture belongs.
        ("TextureSize", Sizei),    #< Size of this texture in pixels.
    ]


# Contains platform-specific information about a texture.
# Aliases to one of ovrD3D11Texture or ovrGLTexture.
#
# \see ovrD3D11Texture, ovrGLTexture.
#
class Texture(ctypes.Structure):
    _pack_ = OVR_PTR_SIZE
    _fields_ = [
        ("Header", TextureHeader),                     #< API-independent header.
        # (ignore on non-64 bit) OVR_ON64(OVR_UNUSED_STRUCT_PAD(pad0, 4))    #< \internal struct padding
        ("PlatformData", ctypes.POINTER(ctypes.c_uint) * 8),          #< Specialized in ovrGLTextureData, ovrD3D11TextureData etc.
    ]


# Describes a set of textures that act as a rendered flip chain.
#
# An ovrSwapTextureSet per layer is passed to ovr_SubmitFrame via one of the ovrLayer types.
# The TextureCount refers to the flip chain count and not an eye count.
# See the layer structs and functions for information about how to use ovrSwapTextureSet.
#
# ovrSwapTextureSets must be created by either the ovr_CreateSwapTextureSetD3D11 or
# ovr_CreateSwapTextureSetGL factory function, and must be destroyed by ovr_DestroySwapTextureSet.
#
# \see ovr_CreateSwapTextureSetD3D11, ovr_CreateSwapTextureSetGL, ovr_DestroySwapTextureSet.
#
class SwapTextureSet(ctypes.Structure):
    _pack_ = OVR_PTR_SIZE
    _fields_ = [
        ("Textures", ctypes.POINTER(Texture)),      #< Points to an array of ovrTextures.
        ("TextureCount", ctypes.c_int),  #< The number of textures referenced by the Textures array.
        # CurrentIndex specifies which of the Textures will be used by the ovr_SubmitFrame call.
        # This is manually incremented by the application, typically in a round-robin manner.
        #
        # Before selecting a Texture as a rendertarget, the application should increment CurrentIndex by
        # 1 and wrap it back to 0 if CurrentIndex == TextureCount, so that it gets a fresh rendertarget,
        # one that is not currently being used for display. It can then render to Textures[CurrentIndex].
        #
        # After rendering, the application calls ovr_SubmitFrame using that same CurrentIndex value
        # to display the new rendertarget.
        #
        # The application can submit multiple frames with the same ovrSwapTextureSet and CurrentIndex
        # value if the rendertarget does not need to be updated, for example when displaying an
        # information display whose text has not changed since the previous frame.
        #
        # Multiple layers can use the same ovrSwapTextureSet at the same time - there is no need to
        # create a unique ovrSwapTextureSet for each layer. However, all the layers using a particular
        # ovrSwapTextureSet will share the same value of CurrentIndex, so they cannot use different
        # textures within the ovrSwapTextureSet.
        #
        # Once a particular Textures[CurrentIndex] has been sent to ovr_SubmitFrame, that texture
        # should not be rendered to until a subsequent ovr_SubmitFrame is made (either with a
        # different CurrentIndex value, or with a different ovrSwapTextureSet, or disabling the layer).
        ("CurrentIndex", ctypes.c_int),
    ]



#-----------------------------------------------------------------------------------

# Describes button input types.
# Button inputs are combined; that is they will be reported as pressed if they are 
# pressed on either one of the two devices.
# The ovrButton_Up/Down/Left/Right map to both XBox D-Pad and directional buttons.
# The ovrButton_Enter and ovrButton_Return map to Start and Back controller buttons, respectively.
# enum Button    
Button_A         = 0x00000001
Button_B         = 0x00000002
Button_RThumb    = 0x00000004
Button_RShoulder = 0x00000008
Button_X         = 0x00000100
Button_Y         = 0x00000200
Button_LThumb    = 0x00000400  
Button_LShoulder = 0x00000800
# Navigation through DPad.
Button_Up        = 0x00010000
Button_Down      = 0x00020000
Button_Left      = 0x00040000
Button_Right     = 0x00080000
Button_Enter     = 0x00100000 # Start on XBox controller.
Button_Back      = 0x00200000 # Back on Xbox controller.     


# Describes touch input types.
# These values map to capacitive touch values reported ovrInputState::Touch.
# Some of these values are mapped to button bits for consistency.
# enum Touch
Touch = ENUM_TYPE
Touch_A              = Button_A
Touch_B              = Button_B
Touch_RThumb         = Button_RThumb
Touch_RIndexTrigger  = 0x00000010
Touch_X              = Button_X
Touch_Y              = Button_Y
Touch_LThumb         = Button_LThumb
Touch_LIndexTrigger  = 0x00001000
# Finger pose state 
# Derived internally based on distance, proximity to sensors and filtering.
Touch_RIndexPointing = 0x00000020
Touch_RThumbUp       = 0x00000040    
Touch_LIndexPointing = 0x00002000
Touch_LThumbUp       = 0x00004000


# Specifies which controller is connected; multiple can be connected at once.
# enum ControllerType
ControllerType = ENUM_TYPE
ControllerType_LTouch    = 0x01
ControllerType_RTouch    = 0x02
ControllerType_Touch     = 0x03
ControllerType_All       = 0xff


# Provides names for the left and right hand array indexes.
#
# \see ovrInputState ovrTrackingState
# 
# enum HandType
HandType = ENUM_TYPE
Hand_Left  = 0
Hand_Right = 1


# ovrInputState describes the complete controller input state including Oculus Touch,
# and XBox gamepad. If multiple inputs are connected and used at the same time,
# their inputs are combined.
class InputState(ctypes.Structure):
    _fields_ = [
        # System type when the controller state was last updated.
        ("TimeInSeconds", ctypes.c_double), 
        # Described by ovrControllerType. Indicates which ControllerTypes are present.
        ("ConnectedControllerTypes", ctypes.c_uint), 
        # Values for buttons described by ovrButton.
        ("Buttons", ctypes.c_uint), 
        # Touch values for buttons and sensors as described by ovrTouch.
        ("Touches", ctypes.c_uint), 
        # Left and right finger trigger values (ovrHand_Left and ovrHand_Right), in the range 0.0 to 1.0f.
        ("IndexTrigger", ctypes.c_float * 2),
        # Left and right hand trigger values (ovrHand_Left and ovrHand_Right), in the range 0.0 to 1.0f.
        ("HandTrigger", ctypes.c_float * 2), 
        # Horizontal and vertical thumbstick axis values (ovrHand_Left and ovrHand_Right), in the range -1.0f to 1.0f.
        ("Thumbstick", Vector2f * 2), 
    ]


#-----------------------------------------------------------------------------------
# ***** Initialize structures

# Initialization flags.
#
# \see ovrInitParams, ovr_Initialize
#
# enum InitFlags
InitFlags = ENUM_TYPE
# When a debug library is requested, a slower debugging version of the library will
# run which can be used to help solve problems in the library and debug application code.
Init_Debug          = 0x00000001
# When ServerOptional is set, the ovr_Initialize() call not will block waiting for
# the server to respond. If the server is not reachable, it might still succeed.
Init_ServerOptional = 0x00000002
# When a version is requested, the LibOVR runtime respects the RequestedMinorVersion
# field and verifies that the RequestedMinorVersion is supported.
Init_RequestVersion = 0x00000004
# These bits are writable by user code.
init_WritableBits   = 0x00ffffff


# Logging levels
#
# \see ovrInitParams ovrLogCallback
#
# enum LogLevel
LogLevel = ENUM_TYPE
LogLevel_Debug    = 0 #< Debug-level log event.
LogLevel_Info     = 1 #< Info-level log event.
LogLevel_Error    = 2 #< Error-level log event.


# Signature of the logging callback function pointer type.
#
# \param[in] userData is an arbitrary value specified by the user of ovrInitParams.
# \param[in] level is one of the ovrLogLevel constants.
# \param[in] message is a UTF8-encoded null-terminated string.
# \see ovrInitParams ovrLogLevel, ovr_Initialize
#
# typedef void (OVR_CDECL* ovrLogCallback)(ctypes.POINTER(ctypes.c_uint) userData, int level, const char* message);
LogCallback = ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_uint), ctypes.c_int, ctypes.c_char_p)


# Parameters for ovr_Initialize.
#
# \see ovr_Initialize
#
class InitParams(ctypes.Structure):
    _pack_ = 8
    _fields_ = [
        # Flags from ovrInitFlags to override default behavior.
        # Use 0 for the defaults.
        ("Flags", ctypes.c_uint32), 
        # Requests a specific minimum minor version of the LibOVR runtime.
        # Flags must include ovrInit_RequestVersion or this will be ignored
        # and OVR_MINOR_VERSION will be used.
        ("RequestedMinorVersion", ctypes.c_uint32), 
        # User-supplied log callback function, which may be called at any time
        # asynchronously from multiple threads until ovr_Shutdown completes.
        # Use NULL to specify no log callback.
        ("LogCallback", LogCallback), 
        # User-supplied data which is passed as-is to LogCallback. Typically this 
        # is used to store an application-specific pointer which is read in the 
        # callback function.
        ("UserData", ctypes.POINTER(ctypes.c_uint)), 
        # Relative number of milliseconds to wait for a connection to the server
        # before failing. Use 0 for the default timeout.
        ("ConnectionTimeoutMS", ctypes.c_uint32), 
        # (ignore on non-64 bit) OVR_ON64(OVR_UNUSED_STRUCT_PAD(pad0, 4)) #< \internal
    ]


# -----------------------------------------------------------------------------------
# ***** API Interfaces

# Overview of the API
#
# Setup:
#  - ovr_Initialize().
#  - ovr_Create(&hmd, &graphicsId).
#  - Call ovr_ConfigureTracking() to configure and initialize tracking.
#  - Use hmd members and ovr_GetFovTextureSize() to determine graphics configuration
#    and ovr_GetRenderDesc() to get per-eye rendering parameters.
#  - Allocate render target texture sets with ovr_CreateSwapTextureSetD3D11() or
#    ovr_CreateSwapTextureSetGL().
#
# Application Loop:
#  - Call ovr_GetFrameTiming() to get the current frame timing information.
#  - Call ovr_GetTrackingState() and ovr_CalcEyePoses() to obtain the predicted
#    rendering pose for each eye based on timing.
#  - Render the scene content into CurrentIndex of ovrTextureSet for each eye and layer
#    you plan to update this frame. Increment texture set CurrentIndex.
#  - Call ovr_SubmitFrame() to render the distorted layers to the back buffer
#    and present them on the HMD. If ovr_SubmitFrame returns ovrSuccess_NotVisible,
#    there is no need to render the scene for the next loop iteration. Instead,
#    just call ovr_SubmitFrame again until it returns ovrSuccess.
#
# Shutdown:
#  - ovr_Destroy().
#  - ovr_Shutdown().


# OVR_PUBLIC_FUNCTION(ovrResult) ovr_Initialize(const ovrInitParams* params);
def initialize(params):
    """
    # Initializes LibOVR
    #
    # Initialize LibOVR for application usage. This includes finding and loading the LibOVRRT
    # shared library. No LibOVR API functions, other than ovr_GetLastErrorInfo, can be called
    # unless ovr_Initialize succeeds. A successful call to ovr_Initialize must be eventually
    # followed by a call to ovr_Shutdown. ovr_Initialize calls are idempotent.
    # Calling ovr_Initialize twice does not require two matching calls to ovr_Shutdown.
    # If already initialized, the return value is ovr_Success.
    # 
    # LibOVRRT shared library search order:
    #      -# Current working directory (often the same as the application directory).
    #      -# Module directory (usually the same as the application directory,
    #         but not if the module is a separate shared library).
    #      -# Application directory
    #      -# Development directory (only if OVR_ENABLE_DEVELOPER_SEARCH is enabled,
    #         which is off by default).
    #      -# Standard OS shared library search location(s) (OS-specific).
    #
    # \param params Specifies custom initialization options. May be NULL to indicate default options.
    # \return Returns an ovrResult indicating success or failure. In the case of failure, use
    #         ovr_GetLastErrorInfo to get more information. Example failed results include:
    #     - ovrError_Initialize: Generic initialization error.
    #     - ovrError_LibLoad: Couldn't load LibOVRRT.
    #     - ovrError_LibVersion: LibOVRRT version incompatibility.
    #     - ovrError_ServiceConnection: Couldn't connect to the OVR Service.
    #     - ovrError_ServiceVersion: OVR Service version incompatibility.
    #     - ovrError_IncompatibleOS: The operating system version is incompatible.
    #     - ovrError_DisplayInit: Unable to initialize the HMD display.
    #     - ovrError_ServerStart:  Unable to start the server. Is it already running?
    #     - ovrError_Reinitialization: Attempted to re-initialize with a different version.
    #
    # \see ovr_Shutdown
    """
    result = libovr.ovr_Initialize(params)
    if FAILURE(result):
        raise "ovr.initialize failed"
    

# OVR_PUBLIC_FUNCTION(void) ovr_Shutdown();
def shutdown():
    """
    # Shuts down LibOVR
    #
    # A successful call to ovr_Initialize must be eventually matched by a call to ovr_Shutdown.
    # After calling ovr_Shutdown, no LibOVR functions can be called except ovr_GetLastErrorInfo
    # or another ovr_Initialize. ovr_Shutdown invalidates all pointers, references, and created objects
    # previously returned by LibOVR functions. The LibOVRRT shared library can be unloaded by
    # ovr_Shutdown.
    #
    # \see ovr_Initialize
    """
    libovr.ovr_shutdown()


# Provides information about the last error.
# \see ovr_GetLastErrorInfo
class ErrorInfo(ctypes.Structure):
    _fields_ = [
        ("Result", Result),                #< The result from the last API call that generated an error ovrResult.
        ("ErrorString", ctypes.c_char * 512),    #< A UTF8-encoded null-terminated English string describing the problem. The format of this string is subject to change in future versions.
    ]


# Returns information about the most recent failed return value by the
# current thread for this library.
#
# This function itself can never generate an error.
# The last error is never cleared by LibOVR, but will be overwritten by new errors.
# Do not use this call to determine if there was an error in the last API
# call as successful API calls don't clear the last ovrErrorInfo.
# To avoid any inconsistency, ovr_GetLastErrorInfo should be called immediately
# after an API function that returned a failed ovrResult, with no other API
# functions called in the interim.
#
# \param[out] errorInfo The last ovrErrorInfo for the current thread.
#
# \see ovrErrorInfo
#
# OVR_PUBLIC_FUNCTION(void) ovr_GetLastErrorInfo(ovrErrorInfo* errorInfo);
getLastErrorInfo = libovr.ovr_GetLastErrorInfo


# Returns the version string representing the LibOVRRT version.
#
# The returned string pointer is valid until the next call to ovr_Shutdown.
#
# Note that the returned version string doesn't necessarily match the current
# OVR_MAJOR_VERSION, etc., as the returned string refers to the LibOVRRT shared
# library version and not the locally compiled interface version.
#
# The format of this string is subject to change in future versions and its contents
# should not be interpreted.
#
# \return Returns a UTF8-encoded null-terminated version string.
#
# OVR_PUBLIC_FUNCTION(const char*) ovr_GetVersionString();


# Writes a message string to the LibOVR tracing mechanism (if enabled).
#
# This message will be passed back to the application via the ovrLogCallback if
# it was registered.
#
# \param[in] level One of the ovrLogLevel constants.
# \param[in] message A UTF8-encoded null-terminated string.
# \return returns the strlen of the message or a negative value if the message is too large.
#
# \see ovrLogLevel, ovrLogCallback
#
# OVR_PUBLIC_FUNCTION(int) ovr_TraceMessage(int level, const char* message);
traceMessage = libovr.ovr_TraceMessage


#-------------------------------------------------------------------------------------
# @name HMD Management
#
# Handles the enumeration, creation, destruction, and properties of an HMD (head-mounted display).
#@{


# Returns information about the given HMD.
#
# ovr_Initialize must have first been called in order for this to succeed, otherwise ovrHmdDesc::Type
# will be reported as ovrHmd_None.
# 
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create, else NULL in which
#                case this function detects whether an HMD is present and returns its info if so.
#
# \return Returns an ovrHmdDesc. If the hmd is NULL and ovrHmdDesc::Type is ovrHmd_None then 
#         no HMD is present.
#
# OVR_PUBLIC_FUNCTION(ovrHmdDesc) ovr_GetHmdDesc(ovrHmd hmd);
getHmdDesc = libovr.ovr_GetHmdDesc
getHmdDesc.restype = HmdDesc


# OVR_PUBLIC_FUNCTION(ovrResult) ovr_Create(ovrHmd* pHmd, ovrGraphicsLuid* pLuid);
def create():
    """
    # Creates a handle to an HMD.
    #
    # Upon success the returned ovrHmd must be eventually freed with ovr_Destroy when it is no longer needed.
    # A second call to ovr_Create will result in an error return value if the previous Hmd has not been destroyed.
    #
    # \param[out] pHmd Provides a pointer to an ovrHmd which will be written to upon success.
    # \param[out] luid Provides a system specific graphics adapter identifier that locates which
    # graphics adapter has the HMD attached. This must match the adapter used by the application
    # or no rendering output will be possible. This is important for stability on multi-adapter systems. An
    # application that simply chooses the default adapter will not run reliably on multi-adapter systems.
    # \return Returns an ovrResult indicating success or failure. Upon failure
    #         the returned pHmd will be NULL.
    #
    # <b>Example code</b>
    #     \code{.cpp}
    #         ovrHmd hmd;
    #         ovrGraphicsLuid luid;
    #         ovrResult result = ovr_Create(&hmd, &luid);
    #         if(OVR_FAILURE(result))
    #            ...
    #     \endcode
    #
    # \see ovr_Destroy
    """
    hmd = Hmd()
    luid = GraphicsLuid()
    result = libovr.ovr_Create(byref(hmd), byref(luid))
    if FAILURE(result):
        raise Exception("ovr.create() failed. Is the Oculus Rift On?")
    return hmd, luid


# OVR_PUBLIC_FUNCTION(void) ovr_Destroy(ovrHmd hmd);
def destroy(hmd):
    """
    # Destroys the HMD.
    #
    # \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
    # \see ovr_Create
    """
    libovr.ovr_Destroy(hmd)


# Returns ovrHmdCaps bits that are currently enabled.
#
# Note that this value is different from ovrHmdDesc::AvailableHmdCaps, which describes what
# capabilities are available for that HMD.
#
# \return Returns a combination of zero or more ovrHmdCaps.
# \see ovrHmdCaps
#
# OVR_PUBLIC_FUNCTION(unsigned int) ovr_GetEnabledCaps(ovrHmd hmd);
getEnabledCaps = libovr.ovr_GetEnabledCaps


# Modifies capability bits described by ovrHmdCaps that can be modified,
# such as ovrHmdCap_LowPersistance.
#
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
# \param[in] hmdCaps A combination of 0 or more ovrHmdCaps.
#
# \see ovrHmdCaps
#
# OVR_PUBLIC_FUNCTION(void) ovr_SetEnabledCaps(ovrHmd hmd, unsigned int hmdCaps);
setEnabledCaps = libovr.ovr_SetEnabledCaps

#@}



#-------------------------------------------------------------------------------------
# @name Tracking
#
# Tracking functions handle the position, orientation, and movement of the HMD in space.
#
# All tracking interface functions are thread-safe, allowing tracking state to be sampled
# from different threads.
#
#@{

# Starts sensor sampling, enabling specified capabilities, described by ovrTrackingCaps.
#
# Use 0 for both requestedTrackingCaps and requiredTrackingCaps to disable tracking.
# ovr_ConfigureTracking can be called multiple times with the same or different values
# for a given ovrHmd.
#
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
#
# \param[in] requestedTrackingCaps specifies support that is requested. The function will succeed
#            even if these caps are not available (i.e. sensor or camera is unplugged). Support
#            will automatically be enabled if the device is plugged in later. Software should
#            check ovrTrackingState.StatusFlags for real-time status.
#
# \param[in] requiredTrackingCaps Specifies sensor capabilities required at the time of the call.
#            If they are not available, the function will fail. Pass 0 if only specifying
#            requestedTrackingCaps.
#
# \return Returns an ovrResult indicating success or failure. In the case of failure, use
#         ovr_GetLastErrorInfo to get more information.
#
# \see ovrTrackingCaps
#
# OVR_PUBLIC_FUNCTION(ovrResult) ovr_ConfigureTracking(ovrHmd hmd, unsigned int requestedTrackingCaps,
#                                                      unsigned int requiredTrackingCaps);
configureTracking = libovr.ovr_ConfigureTracking


# Re-centers the sensor position and orientation.
#
# This resets the (x,y,z) positional components and the yaw orientation component.
# The Roll and pitch orientation components are always determined by gravity and cannot
# be redefined. All future tracking will report values relative to this new reference position.
#
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
#
# OVR_PUBLIC_FUNCTION(void) ovr_RecenterPose(ovrHmd hmd);
recenterPose = libovr.ovr_RecenterPose


# Returns tracking state reading based on the specified absolute system time.
#
# Pass an absTime value of 0.0 to request the most recent sensor reading. In this case
# both PredictedPose and SamplePose will have the same value.
#
# This may also be used for more refined timing of front buffer rendering logic, and so on.
#
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
# \param[in] absTime Specifies the absolute future time to predict the return
#            ovrTrackingState value. Use 0 to request the most recent tracking state.
# \return Returns the ovrTrackingState that is predicted for the given absTime.
#
# \see ovrTrackingState, ovr_GetEyePoses, ovr_GetTimeInSeconds
#
# OVR_PUBLIC_FUNCTION(ovrTrackingState) ovr_GetTrackingState(ovrHmd hmd, double absTime);
getTrackingState = libovr.ovr_GetTrackingState
getTrackingState.restype = TrackingState
getTrackingState.argtypes = [Hmd, ctypes.c_double]


# Returns the most recent input state for controllers, without positional tracking info.
# Developers can tell whether the same state was returned by checking the PacketNumber.
#
# \param[out] inputState Input state that will be filled in.
# \param[in] controllerTypeMask Specifies which controllers the input will be returned for.
#            Described by ovrControllerType.
# \return Returns ovrSuccess if the new state was successfully obtained.
#
# \see ovrControllerType
#
# OVR_PUBLIC_FUNCTION(ovrResult) ovr_GetInputState(ovrHmd hmd, unsigned int controllerTypeMask, ovrInputState* inputState);
getInputState = libovr.ovr_GetInputState


# Turns on vibration of the given controller.
#
# To disable vibration, call ovr_SetControllerVibration with an amplitude of 0.
# Vibration automatically stops after a nominal amount of time, so if you want vibration 
# to be continuous over multiple seconds then you need to call this function periodically.
#
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
# \param[in] controllerTypeMask Specifies controllers to apply the vibration to.
# \param[in] frequency Specifies a vibration frequency in the range of 0.0 to 1.0. 
#            Currently the only valid values are 0.0, 0.5, and 1.0 and other values will
#            be clamped to one of these.
# \param[in] amplitude Specifies a vibration amplitude in the range of 0.0 to 1.0.
#
# \return Returns ovrSuccess upon success.
#
# \see ovrControllerType
# 
# OVR_PUBLIC_FUNCTION(ovrResult) ovr_SetControllerVibration(ovrHmd hmd, unsigned int controllerTypeMask,
#                                                             float frequency, float amplitude);
setControllerVibration = libovr.ovr_SetControllerVibration

#@}


#-------------------------------------------------------------------------------------
# @name Layers
#
#@{

# Describes layer types that can be passed to ovr_SubmitFrame.
# Each layer type has an associated struct, such as ovrLayerEyeFov.
#
# \see ovrLayerHeader
#
# enum LayerType
LayerType = ENUM_TYPE
LayerType_Disabled       = 0         #< Layer is disabled.
LayerType_EyeFov         = 1         #< Described by ovrLayerEyeFov.
LayerType_EyeFovDepth    = 2         #< Described by ovrLayerEyeFovDepth.
LayerType_QuadInWorld    = 3         #< Described by ovrLayerQuad.
LayerType_QuadHeadLocked = 4         #< Described by ovrLayerQuad. Displayed in front of your face, moving with the head.
LayerType_Direct         = 6         #< Described by ovrLayerDirect. Passthrough for debugging and custom rendering.


# Identifies flags used by ovrLayerHeader and which are passed to ovr_SubmitFrame.
#
# \see ovrLayerHeader
#
# enum LayerFlags
LayerFlags = ENUM_TYPE
# ovrLayerFlag_HighQuality mode costs performance but looks better.
LayerFlag_HighQuality               = 0x01
# ovrLayerFlag_TextureOriginAtBottomLeft: the opposite is TopLeft.
# Generally this is false for D3D, true for OpenGL.
LayerFlag_TextureOriginAtBottomLeft = 0x02


# Defines properties shared by all ovrLayer structs such as ovrLayerEyeFov.
#
# ovrLayerHeader is used as a base member in these larger structs.
# This struct cannot be used by itself except for the case that Type is ovrLayerType_Disabled.
#
# \see ovrLayerType, ovrLayerFlags
#
class LayerHeader(ctypes.Structure):
    _pack_ = OVR_PTR_SIZE
    _fields_ = [
        ("Type", LayerType),    #< Described by ovrLayerType.
        ("Flags", ctypes.c_uint),   #< Described by ovrLayerFlags.
    ]


# Describes a layer that specifies a monoscopic or stereoscopic view.
# This is the kind of layer that's typically used as layer 0 to ovr_SubmitFrame,
# as it is the kind of layer used to render a 3D stereoscopic view.
#
# Three options exist with respect to mono/stereo texture usage:
#    - ColorTexture[0] and ColorTexture[1] contain the left and right stereo renderings, respectively.
#      Viewport[0] and Viewport[1] refer to ColorTexture[0] and ColorTexture[1], respectively.
#    - ColorTexture[0] contains both the left and right renderings, ColorTexture[1] is NULL,
#      and Viewport[0] and Viewport[1] refer to sub-rects with ColorTexture[0].
#    - ColorTexture[0] contains a single monoscopic rendering, and Viewport[0] and
#      Viewport[1] both refer to that rendering.
#
# \see ovrSwapTextureSet, ovr_SubmitFrame
#
class LayerEyeFov(ctypes.Structure):
    _pack_ = OVR_PTR_SIZE
    _fields_ = [
        # Header.Type must be ovrLayerType_EyeFov.
        ("Header", LayerHeader), 
        # ovrSwapTextureSets for the left and right eye respectively.
        # The second one of which can be NULL for cases described above.
        ("ColorTexture", ctypes.POINTER(SwapTextureSet) * Eye_Count), 
        # Specifies the ColorTexture sub-rect UV coordinates.
        # Both Viewport[0] and Viewport[1] must be valid.
        ("Viewport", Recti * Eye_Count), 
        # The viewport field of view.
        ("Fov", FovPort * Eye_Count), 
        # Specifies the position and orientation of each eye view, with the position specified in meters.
        # RenderPose will typically be the value returned from ovr_CalcEyePoses,
        # but can be different in special cases if a different head pose is used for rendering.
        ("RenderPose", Posef * Eye_Count), 
    ]


# Describes a layer that specifies a monoscopic or stereoscopic view,
# with depth textures in addition to color textures. This is typically used to support
# positional time warp. This struct is the same as ovrLayerEyeFov, but with the addition
# of DepthTexture and ProjectionDesc.
#
# ProjectionDesc can be created using ovrTimewarpProjectionDesc_FromProjection.
#
# Three options exist with respect to mono/stereo texture usage:
#    - ColorTexture[0] and ColorTexture[1] contain the left and right stereo renderings, respectively.
#      Viewport[0] and Viewport[1] refer to ColorTexture[0] and ColorTexture[1], respectively.
#    - ColorTexture[0] contains both the left and right renderings, ColorTexture[1] is NULL,
#      and Viewport[0] and Viewport[1] refer to sub-rects with ColorTexture[0].
#    - ColorTexture[0] contains a single monoscopic rendering, and Viewport[0] and
#      Viewport[1] both refer to that rendering.
#
# \see ovrSwapTextureSet, ovr_SubmitFrame
#
class LayerEyeFovDepth(ctypes.Structure):
    _pack_ = OVR_PTR_SIZE
    _fields_ = [
        # Header.Type must be ovrLayerType_EyeFovDepth.
        ("Header", LayerHeader), 
        # ovrSwapTextureSets for the left and right eye respectively.
        # The second one can be NULL in cases described above.
        ("ColorTexture", ctypes.POINTER(SwapTextureSet) * Eye_Count), 
        # Specifies the ColorTexture sub-rect UV coordinates.
        # Both Viewport[0] and Viewport[1] must be valid.
        ("Viewport", Recti * Eye_Count), 
        # The viewport field of view.
        ("Fov", FovPort * Eye_Count), 
        # Specifies the position and orientation of each eye view, with the position specified in meters.
        # RenderPose will typically be the value returned from ovr_CalcEyePoses,
        # but can be different in special cases if a different head pose is used for rendering.
        ("RenderPose", Posef * Eye_Count), 
        # Depth texture for positional timewarp.
        # Must map 1:1 to the ColorTexture.
        ("DepthTexture", ctypes.POINTER(SwapTextureSet) * Eye_Count), 
        # Specifies how to convert DepthTexture information into meters.
        # \see ovrTimewarpProjectionDesc_FromProjection
        ("ProjectionDesc", TimewarpProjectionDesc), 
    ]


# Describes a layer of Quad type, which is a single quad in world or viewer space.
# It is used for both ovrLayerType_QuadInWorld and ovrLayerType_QuadHeadLocked.
# This type of layer represents a single object placed in the world and not a stereo
# view of the world itself.
#
# A typical use of ovrLayerType_QuadInWorld is to draw a television screen in a room
# that for some reason is more convenient to draw as a layer than as part of the main
# view in layer 0. For example, it could implement a 3D popup GUI that is drawn at a
# higher resolution than layer 0 to improve fidelity of the GUI.
#
# A use of ovrLayerType_QuadHeadLocked might be to implement a debug HUD visible in
# the HMD.
#
# Quad layers are visible from both sides; they are not back-face culled.
#
# \see ovrSwapTextureSet, ovr_SubmitFrame
#
class LayerQuad(ctypes.Structure):
    _pack_ = OVR_PTR_SIZE
    _fields_ = [
        # Header.Type must be ovrLayerType_QuadInWorld or ovrLayerType_QuadHeadLocked.
        ("Header", LayerHeader), 
        # Contains a single image, never with any stereo view.
        ("ColorTexture", ctypes.POINTER(SwapTextureSet), ), 
        # Specifies the ColorTexture sub-rect UV coordinates.
        ("Viewport", Recti), 
        # Position and orientation of the center of the quad. Position is specified in meters.
        ("QuadPoseCenter", Posef), 
        # Width and height (respectively) of the quad in meters.
        ("QuadSize", Vector2f), 
    ]


# Describes a layer which is copied to the HMD as-is. Neither distortion, time warp,
# nor vignetting is applied to ColorTexture before it's copied to the HMD. The application
# can, however implement these kinds of effects itself before submitting the layer.
# This layer can be used for application-based distortion rendering and can also be
# used for implementing a debug HUD that's viewed on the mirror texture.
#
# \see ovrSwapTextureSet, ovr_SubmitFrame
#
class LayerDirect(ctypes.Structure):
    _pack_ = OVR_PTR_SIZE
    _fields_ = [
        # Header.Type must be ovrLayerType_EyeDirect.
        ("Header", LayerHeader), 
        # ovrSwapTextureSets for the left and right eye respectively.
        # The second one of which can be NULL for cases described above.
        ("ColorTexture", ctypes.POINTER(SwapTextureSet) * Eye_Count), 
        # Specifies the ColorTexture sub-rect UV coordinates.
        # Both Viewport[0] and Viewport[1] must be valid.
        ("Viewport", Recti * Eye_Count), 
    ]


# Union that combines ovrLayer types in a way that allows them
# to be used in a polymorphic way.
class Layer_Union(ctypes.Union):
    _fields_ = [
        ("Header", LayerHeader), 
        ("EyeFov", LayerEyeFov), 
        ("EyeFovDepth", LayerEyeFovDepth), 
        ("Quad", LayerQuad), 
        ("Direct", LayerDirect), 
    ]


# @name SDK Distortion Rendering
#
# All of rendering functions including the configure and frame functions
# are not thread safe. It is OK to use ConfigureRendering on one thread and handle
# frames on another thread, but explicit synchronization must be done since
# functions that depend on configured state are not reentrant.
#
# These functions support rendering of distortion by the SDK.
#
#@{

# TextureSet creation is rendering API-specific, so the ovr_CreateSwapTextureSetXX
# methods can be found in the rendering API-specific headers, such as OVR_CAPI_D3D.h and OVR_CAPI_GL.h


# Destroys an ovrSwapTextureSet and frees all the resources associated with it.
#
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
# \param[in] textureSet Specifies the ovrSwapTextureSet to destroy. If it is NULL then this function has no effect.
#
# \see ovr_CreateSwapTextureSetD3D11, ovr_CreateSwapTextureSetGL
#
# OVR_PUBLIC_FUNCTION(void) ovr_DestroySwapTextureSet(ovrHmd hmd, ovrSwapTextureSet* textureSet);
destroySwapTextureSet = libovr.ovr_DestroySwapTextureSet


# Destroys a mirror texture previously created by one of the mirror texture creation functions.
#
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
# \param[in] mirrorTexture Specifies the ovrTexture to destroy. If it is NULL then this function has no effect.
#
# \see ovr_CreateMirrorTextureD3D11, ovr_CreateMirrorTextureGL
#
# OVR_PUBLIC_FUNCTION(void) ovr_DestroyMirrorTexture(ovrHmd hmd, ovrTexture* mirrorTexture);
destroyMirrorTexture = libovr.ovr_DestroyMirrorTexture


# Calculates the recommended viewport size for rendering a given eye within the HMD
# with a given FOV cone.
#
# Higher FOV will generally require larger textures to maintain quality.
# Apps packing multiple eye views together on the same texture should ensure there are
# at least 8 pixels of padding between them to prevent texture filtering and chromatic
# aberration causing images to leak between the two eye views.
#
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
# \param[in] eye Specifies which eye (left or right) to calculate for.
# \param[in] fov Specifies the ovrFovPort to use.
# \param[in] pixelsPerDisplayPixel Specifies the ratio of the number of render target pixels
#            to display pixels at the center of distortion. 1.0 is the default value. Lower
#            values can improve performance, higher values give improved quality.
# \return Returns the texture width and height size.
#
# OVR_PUBLIC_FUNCTION(ovrSizei) ovr_GetFovTextureSize(ovrHmd hmd, ovrEyeType eye, ovrFovPort fov,
#                                                        float pixelsPerDisplayPixel);
getFovTextureSize = libovr.ovr_GetFovTextureSize

# Computes the distortion viewport, view adjust, and other rendering parameters for
# the specified eye.
#
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
# \param[in] eyeType Specifies which eye (left or right) for which to perform calculations.
# \param[in] fov Specifies the ovrFovPort to use.
# \return Returns the computed ovrEyeRenderDesc for the given eyeType and field of view.
#
# \see ovrEyeRenderDesc
#
# OVR_PUBLIC_FUNCTION(ovrEyeRenderDesc) ovr_GetRenderDesc(ovrHmd hmd,
#                                                            ovrEyeType eyeType, ovrFovPort fov);
getRenderDesc = libovr.ovr_GetRenderDesc

# Submits layers for distortion and display.
#
# ovr_SubmitFrame triggers distortion and processing which might happen asynchronously.
# The function will return when there is room in the submission queue and surfaces
# are available. Distortion might or might not have completed.
#
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
#
# \param[in] frameIndex Specifies the targeted application frame index, or 0 to refer to one frame
#        after the last time ovr_SubmitFrame was called.
#
# \param[in] viewScaleDesc Provides additional information needed only if layerPtrList contains
#        a ovrLayerType_QuadInWorld or ovrLayerType_QuadHeadLocked. If NULL, a default
#        version is used based on the current configuration and a 1.0 world scale.
#
# \param[in] layerPtrList Specifies a list of ovrLayer pointers, which can include NULL entries to
#        indicate that any previously shown layer at that index is to not be displayed.
#        Each layer header must be a part of a layer structure such as ovrLayerEyeFov or ovrLayerQuad,
#        with Header.Type identifying its type. A NULL layerPtrList entry in the array indicates the
#         absence of the given layer.
#
# \param[in] layerCount Indicates the number of valid elements in layerPtrList. The maximum
#        supported layerCount is not currently specified, but may be specified in a future version.
#
# - Layers are drawn in the order they are specified in the array, regardless of the layer type.
#
# - Layers are not remembered between successive calls to ovr_SubmitFrame. A layer must be
#   specified in every call to ovr_SubmitFrame or it won't be displayed.
#
# - If a layerPtrList entry that was specified in a previous call to ovr_SubmitFrame is
#   passed as NULL or is of type ovrLayerType_Disabled, that layer is no longer displayed.
#
# - A layerPtrList entry can be of any layer type and multiple entries of the same layer type
#   are allowed. No layerPtrList entry may be duplicated (i.e. the same pointer as an earlier entry).
#
# <b>Example code</b>
#     \code{.cpp}
#         ovrLayerEyeFov  layer0;
#         ovrLayerQuad    layer1;
#           ...
#         ovrLayerHeader* layers[2] = { &layer0.Header, &layer1.Header };
#         ovrResult result = ovr_SubmitFrame(hmd, frameIndex, nullptr, layers, 2);
#     \endcode
#
# \return Returns an ovrResult for which OVR_SUCCESS(result) is false upon error and true
#         upon one of the possible success values:
#     - ovrSuccess: rendering completed successfully.
#     - ovrSuccess_NotVisible: rendering completed successfully but was not displayed on the HMD,
#       usually because another application currently has ownership of the HMD. Applications receiving
#       this result should stop rendering new content, but continue to call ovr_SubmitFrame periodically
#       until it returns a value other than ovrSuccess_NotVisible.
#     - ovrError_DisplayLost: The session has become invalid (such as due to a device removal)
#       and the shared resources need to be released (ovr_DestroySwapTextureSet), the session needs to
#       destroyed (ovr_Destory) and recreated (ovr_Create), and new resources need to be created
#       (ovr_CreateSwapTextureSetXXX). The application's existing private graphics resources do not
#       need to be recreated unless the new ovr_Create call returns a different GraphicsLuid.
#
# \see ovr_GetFrameTiming, ovrViewScaleDesc, ovrLayerHeader
#
# OVR_PUBLIC_FUNCTION(ovrResult) ovr_SubmitFrame(ovrHmd hmd, unsigned int frameIndex,
#                                                   const ovrViewScaleDesc* viewScaleDesc,
#                                                   ovrLayerHeader const * const * layerPtrList, unsigned int layerCount);
submitFrame = libovr.ovr_SubmitFrame
#@}



#-------------------------------------------------------------------------------------
# @name Frame Timing
#
#@{

# Gets the ovrFrameTiming for the given frame index.
#
# The application should increment frameIndex for each successively targeted frame,
# and pass that index to any relevent OVR functions that need to apply to the frame
# identified by that index.
#
# This function is thread-safe and allows for multiple application threads to target
# their processing to the same displayed frame.
# 
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
# \param[in] frameIndex Identifies the frame the caller wishes to target.
# \return Returns the ovrFrameTiming for the given frameIndex.
# \see ovrFrameTiming
#
# OVR_PUBLIC_FUNCTION(ovrFrameTiming) ovr_GetFrameTiming(ovrHmd hmd, unsigned int frameIndex);
getFrameTiming = libovr.ovr_GetFrameTiming

# Returns global, absolute high-resolution time in seconds.
#
# The time frame of reference for this function is not specified and should not be
# depended upon.
#
# \return Returns seconds as a floating point value.
# \see ovrPoseStatef, ovrSensorData, ovrFrameTiming
#
# OVR_PUBLIC_FUNCTION(double) ovr_GetTimeInSeconds();
getTimeInSeconds = libovr.ovr_GetTimeInSeconds
getTimeInSeconds.restype = ctypes.c_double


# Performance HUD enables the HMD user to see information critical to
# the real-time operation of the VR application such as latency timing,
# and CPU & GPU performance metrics
#
#     App can toggle performance HUD modes as such:
#     \code{.cpp}
#         ovrPerfHudMode PerfHudMode = ovrPerfHud_LatencyTiming;
#         ovr_SetInt(Hmd, OVR_PERF_HUD_MODE, (int)PerfHudMode);
#     \endcode
#
# enum PerfHudMode
PerfHudMode = ENUM_TYPE
PerfHud_Off                = 0  #< Turns off the performance HUD
PerfHud_LatencyTiming      = 1  #< Shows latency related timing info
PerfHud_RenderTiming       = 2  #< Shows CPU & GPU timing info
PerfHud_PerfHeadroom       = 3  #< Shows available performance headroom in a "consumer-friendly" way
PerfHud_VersionInfo        = 4  #< Shows SDK Version Info
PerfHud_Count              = 5  #< \internal Count of enumerated elements.

#@}

# Debug HUD is provided to help developers gauge and debug the fidelity of their app's
# stereo rendering characteristics. Using the provided quad and crosshair guides 
# the developer can verify various aspects such as VR tracking units (e.g. meters),
# stereo camera-parallax properties (e.g. making sure objects at infinity are rendered
# with the proper separation), measuring VR geometry sizes and distances and more.
#
#     App can toggle the debug HUD modes as such:
#     \code{.cpp}
#         ovrDebugHudStereoMode DebugHudMode = ovrDebugHudStereo_QuadWithCrosshair;
#         ovr_SetInt(Hmd, OVR_DEBUG_HUD_STEREO_MODE, (int)DebugHudMode);
#     \endcode
#
# The app can modify the visual properties of the stereo guide (i.e. quad, crosshair)
# using the ovr_SetFloatArray function. For a list of tweakable properties,
# see the OVR_DEBUG_HUD_STEREO_GUIDE_* keys in the OVR_CAPI_Keys.h header file.
# enum DebugHudStereoMode
DebugHudStereoMode = ENUM_TYPE
DebugHudStereo_Off                 = 0  #< Turns off the Stereo Debug HUD
DebugHudStereo_Quad                = 1  #< Renders Quad in world for Stereo Debugging
DebugHudStereo_QuadWithCrosshair   = 2  #< Renders Quad+crosshair in world for Stereo Debugging
DebugHudStereo_CrosshairAtInfinity = 3  #< Renders screen-space crosshair at infinity for Stereo Debugging
DebugHudStereo_Count               = 4  #< \internal Count of enumerated elements


# Should be called when the headset is placed on a new user.
# Previously named ovrHmd_ResetOnlyBackOfHeadTrackingForConnectConf.
#
# This may be removed in a future SDK version.
#
# OVR_PUBLIC_FUNCTION(void) ovr_ResetBackOfHeadTracking(ovrHmd hmd);
resetBackOfHeadTracking = libovr.ovr_ResetBackOfHeadTracking


# Should be called when a tracking camera is moved.
#
# This may be removed in a future SDK version.
#
# OVR_PUBLIC_FUNCTION(void) ovr_ResetMulticameraTracking(ovrHmd hmd);
resetMulticameraTracking = libovr.ovr_ResetMulticameraTracking



# -----------------------------------------------------------------------------------
# @name Property Access
#
# These functions read and write OVR properties. Supported properties
# are defined in OVR_CAPI_Keys.h
#
#@{

# Reads a boolean property.
#
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
# \param[in] propertyName The name of the property, which needs to be valid for only the call.
# \param[in] defaultVal specifes the value to return if the property couldn't be read.
# \return Returns the property interpreted as a boolean value. Returns defaultVal if
#         the property doesn't exist.
# OVR_PUBLIC_FUNCTION(ovrBool) ovr_GetBool(ovrHmd hmd, const char* propertyName, ovrBool defaultVal);
getBool = libovr.ovr_GetBool

# Writes or creates a boolean property.
# If the property wasn't previously a boolean property, it is changed to a boolean property.
#
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
# \param[in] propertyName The name of the property, which needs to be valid only for the call.
# \param[in] value The value to write.
# \return Returns true if successful, otherwise false. A false result should only occur if the property
#         name is empty or if the property is read-only.
# OVR_PUBLIC_FUNCTION(ovrBool) ovr_SetBool(ovrHmd hmd, const char* propertyName, ovrBool value);
setBool = libovr.ovr_SetBool


# Reads an integer property.
#
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
# \param[in] propertyName The name of the property, which needs to be valid only for the call.
# \param[in] defaultVal Specifes the value to return if the property couldn't be read.
# \return Returns the property interpreted as an integer value. Returns defaultVal if
#         the property doesn't exist.
# OVR_PUBLIC_FUNCTION(int) ovr_GetInt(ovrHmd hmd, const char* propertyName, int defaultVal);
getInt = libovr.ovr_GetInt

# Writes or creates an integer property.
#
# If the property wasn't previously a boolean property, it is changed to an integer property.
#
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
# \param[in] propertyName The name of the property, which needs to be valid only for the call.
# \param[in] value The value to write.
# \return Returns true if successful, otherwise false. A false result should only occur if the property
#         name is empty or if the property is read-only.
# OVR_PUBLIC_FUNCTION(ovrBool) ovr_SetInt(ovrHmd hmd, const char* propertyName, int value);
setInt = libovr.ovr_SetInt


# Reads a float property.
#
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
# \param[in] propertyName The name of the property, which needs to be valid only for the call.
# \param[in] defaultVal specifes the value to return if the property couldn't be read.
# \return Returns the property interpreted as an float value. Returns defaultVal if
#         the property doesn't exist.
# OVR_PUBLIC_FUNCTION(float) ovr_GetFloat(ovrHmd hmd, const char* propertyName, float defaultVal);
getFloat = libovr.ovr_GetFloat

# Writes or creates a float property.
# If the property wasn't previously a float property, it's changed to a float property.
#
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
# \param[in] propertyName The name of the property, which needs to be valid only for the call.
# \param[in] value The value to write.
# \return Returns true if successful, otherwise false. A false result should only occur if the property
#         name is empty or if the property is read-only.
# OVR_PUBLIC_FUNCTION(ovrBool) ovr_SetFloat(ovrHmd hmd, const char* propertyName, float value);
setFloat = libovr.ovr_SetFloat


# Reads a float array property.
#
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
# \param[in] propertyName The name of the property, which needs to be valid only for the call.
# \param[in] values An array of float to write to.
# \param[in] valuesCapacity Specifies the maximum number of elements to write to the values array.
# \return Returns the number of elements read, or 0 if property doesn't exist or is empty.
# OVR_PUBLIC_FUNCTION(unsigned int) ovr_GetFloatArray(ovrHmd hmd, const char* propertyName,
#                                                        float values[], unsigned int valuesCapacity);
getFloatArray = libovr.ovr_GetFloatArray

# Writes or creates a float array property.
#
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
# \param[in] propertyName The name of the property, which needs to be valid only for the call.
# \param[in] values An array of float to write from.
# \param[in] valuesSize Specifies the number of elements to write.
# \return Returns true if successful, otherwise false. A false result should only occur if the property
#         name is empty or if the property is read-only.
# OVR_PUBLIC_FUNCTION(ovrBool) ovr_SetFloatArray(ovrHmd hmd, const char* propertyName,
#                                                   const float values[], unsigned int valuesSize);
setFloatArray = libovr.ovr_SetFloatArray


# Reads a string property.
# Strings are UTF8-encoded and null-terminated.
#
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
# \param[in] propertyName The name of the property, which needs to be valid only for the call.
# \param[in] defaultVal Specifes the value to return if the property couldn't be read.
# \return Returns the string property if it exists. Otherwise returns defaultVal, which can be specified as NULL.
#         The return memory is guaranteed to be valid until next call to ovr_GetString or
#         until the HMD is destroyed, whichever occurs first.
# OVR_PUBLIC_FUNCTION(const char*) ovr_GetString(ovrHmd hmd, const char* propertyName,
#                                                   const char* defaultVal);
getString = libovr.ovr_GetString

# Writes or creates a string property.
# Strings are UTF8-encoded and null-terminated.
#
# \param[in] hmd Specifies an ovrHmd previously returned by ovr_Create.
# \param[in] propertyName The name of the property, which needs to be valid only for the call.
# \param[in] value The string property, which only needs to be valid for the duration of the call.
# \return Returns true if successful, otherwise false. A false result should only occur if the property
#         name is empty or if the property is read-only.
# OVR_PUBLIC_FUNCTION(ovrBool) ovr_SetString(ovrHmd hmd, const char* propertyName,
#                                              const char* value);
setString = libovr.ovr_SetString


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

