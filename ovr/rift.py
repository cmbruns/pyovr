import ovr
from OpenGL.GL import GL_RGBA8

class Rift():

    @staticmethod
    def calc_eye_poses(headPose, hmdToEyeViewOffset, outEyePoses):
      ovr.calcEyePoses(headPose, hmdToEyeViewOffset, outEyePoses)

    @staticmethod
    def get_last_error(self):
      return ovr.getLastErrorInfo()

    @staticmethod
    def get_time_in_seconds():
      return ovr.getTimeInSeconds()

    @staticmethod
    def get_perspective(fov, near, far, projectionFlags = ovr.Projection_RightHanded):
      return ovr.matrix4f_Projection(fov, near, far, projectionFlags)

    @staticmethod
    def initialize(params=None):
      return ovr.initialize(params)

    @staticmethod
    def shutdown():
      ovr.shutdown()

    def __init__(self):
      self.hmd = None
      self.luid = None
      self.hmdDesc = None

    def __enter__(self):
      self.init()
      return self

    def __exit__(self, exc_type, exc_val, exc_tb):
      self.destroy()

    def configure_tracking(self,
                           supported_caps =
                              ovr.TrackingCap_Orientation |
                              ovr.TrackingCap_MagYawCorrection |
                              ovr.TrackingCap_Position, 
                           required_caps = 0):
      return ovr.configureTracking(self.hmd, supported_caps, required_caps)

    def create_swap_texture(self, size, format_ = GL_RGBA8):
      return ovr.createSwapTextureSetGL(self.hmd, format_, size.w, size.h)

    def destroy(self):
      if self.hmd is not None:
        ovr.destroy(self.hmd)
      self.hmd = None
      self.luid = None
      self.hmdDesc = None
      self.hmd = None

    def destroy_swap_texture(self, textureSet):
      return ovr.destroySwapTextureSet(self.hmd, textureSet)

    def get_fov_texture_size(self, eye, fov_port, pixels_per_display_pixel=1.0):
      return ovr.getFovTextureSize(self.hmd, eye, fov_port, pixels_per_display_pixel);

    def get_eye_poses(self, frame_index, latencyMarker, eyeOffsets, trackingState=0):
      in_arr = (ovr.Vector3f * 2)(*eyeOffsets)
      out_arr = (ovr.Posef * 2)()
      ovr.getEyePoses(self.hmd, frame_index, latencyMarker, in_arr, out_arr)
      return out_arr;

    def get_float(self, name, default):
      return ovr.getFloat(self.hmd, name, default)

    def get_predicted_display_time(self, frameIndex):
      return ovr.getPredictedDisplayTime(self.hmd, frameIndex)

    def get_string(self, name, default):
      return ovr.getString(self.hmd, name, default)

    def get_render_desc(self, eye, fov):
      return ovr.getRenderDesc(self.hmd, eye, fov)

    def get_resolution(self):
      return self.hmdDesc.Resolution

    def get_tracking_state(self, absTime=0, latencyMarker=True):
      if latencyMarker:
        lm = ovr.ovrTrue
      else:
        lm = ovr.ovrFalse
      return ovr.getTrackingState(self.hmd, absTime, lm)

    def init(self):
      self.hmd, self.luid = ovr.create()
      self.hmdDesc = ovr.getHmdDesc(self.hmd)

    def submit_frame(self, frameIndex, viewScaleDesc, layerPtrList, layerCount):
      return ovr.submitFrame(self.hmd, frameIndex, viewScaleDesc, layerPtrList, layerCount)

    def recenter_pose(self):
      return ovr.recenterPose(self.hmd)


