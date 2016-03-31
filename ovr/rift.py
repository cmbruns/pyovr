import ctypes

from OpenGL.GL import GL_RGBA8

import ovr

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
    def get_perspective(fov, near, far, projectionFlags=ovr.Projection_None):
      return ovr.matrix4f_Projection(fov, near, far, projectionFlags)

    @staticmethod
    def initialize(params=None):
      return ovr.initialize(params)

    @staticmethod
    def shutdown():
      ovr.shutdown()

    def __init__(self):
      self.session = None
      self.luid = None
      self.hmdDesc = None

    def __enter__(self):
      self.init()
      return self

    def __exit__(self, exc_type, exc_val, exc_tb):
      self.destroy()

    def commit_texture_swap_chain(self, textureSwapChain):
      ovr.commitTextureSwapChain(self.session, textureSwapChain)

    def create_swap_texture(self, size, format_ = ovr.OVR_FORMAT_R8G8B8A8_UNORM_SRGB):
      textureSwapChainDesc = ovr.TextureSwapChainDesc()
      textureSwapChainDesc.Type = ovr.Texture_2D
      textureSwapChainDesc.ArraySize = ctypes.c_int(1)
      textureSwapChainDesc.Format = format_
      textureSwapChainDesc.Width = size.w
      textureSwapChainDesc.Height = size.h
      textureSwapChainDesc.MipLevels = ctypes.c_int(1)
      textureSwapChainDesc.SampleCount = ctypes.c_int(1)
      textureSwapChainDesc.StaticImage = ovr.ovrFalse
      textureSwapChainDesc.MiscFlags = ctypes.c_uint(0)
      textureSwapChainDesc.BindFlags = ctypes.c_uint(0)
      # print self.session
      # print textureSwapChainDesc
      result = ovr.createTextureSwapChainGL(self.session, textureSwapChainDesc)
      return result

    def destroy(self):
      if self.session is not None:
        ovr.destroy(self.session)
      self.session = None
      self.luid = None
      self.hmdDesc = None
      self.session = None

    def destroy_swap_texture(self, textureSwapChain):
      return ovr.destroyTextureSwapChain(self.session, textureSwapChain)

    def get_current_texture_id_GL(self, textureSwapChain):
      return ovr.getTextureSwapChainBufferGL(self.session, textureSwapChain, -1)

    def get_fov_texture_size(self, eye, fov_port, pixels_per_display_pixel=1.0):
      return ovr.getFovTextureSize(self.session, eye, fov_port, pixels_per_display_pixel);

    def get_eye_poses(self, frame_index, latencyMarker, eyeOffsets, trackingState=0):
      in_arr = (ovr.Vector3f * 2)(*eyeOffsets)
      out_arr = (ovr.Posef * 2)()
      ovr.getEyePoses(self.session, frame_index, latencyMarker, in_arr, out_arr)
      return out_arr;

    def get_float(self, name, default):
      return ovr.getFloat(self.session, name, default)

    def get_predicted_display_time(self, frameIndex):
      return ovr.getPredictedDisplayTime(self.session, frameIndex)

    def get_string(self, name, default):
      return ovr.getString(self.session, name, default)

    def get_render_desc(self, eye, fov):
      return ovr.getRenderDesc(self.session, eye, fov)

    def get_resolution(self):
      return self.hmdDesc.Resolution

    def get_tracking_state(self, absTime=0, latencyMarker=True):
      return ovr.getTrackingState(self.session, absTime, latencyMarker)

    def init(self):
      self.session, self.luid = ovr.create()
      self.hmdDesc = ovr.getHmdDesc(self.session)

    def submit_frame(self, frameIndex, viewScaleDesc, layerPtrList, layerCount):
      return ovr.submitFrame(self.session, frameIndex, viewScaleDesc, layerPtrList, layerCount)

    def recenter_pose(self):
      return ovr.recenterTrackingOrigin(self.session)


