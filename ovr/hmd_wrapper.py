
import ctypes
from OpenGL.GL import GL_SRGB8_ALPHA8

import ovr

class HmdWrapper():
    
    def __init__(self):
        self.hmd = None
        self.pTextureSet = None
        self.frame_index = 0

    def __enter__(self):
        self.init_tracking()
        self.init_texture()     
        return self

    def __exit__(self, arg2, arg3, arg4):
        self.dispose_hmd()

    def init_tracking(self):
        """
        Create resources for Oculus Rift tracking and rendering.
        """
        # 1) Initialize
        # 1a) Initialize Oculus SDK
        ovr.initialize(None)
        self.hmd, luid = ovr.create()
        self.hmdDesc = ovr.getHmdDesc(self.hmd)
        # print "Rift screen size = ", self.hmdDesc.Resolution        
        ovr.configureTracking(self.hmd, 
            ovr.TrackingCap_Orientation | # supported capabilities
            ovr.TrackingCap_MagYawCorrection |
            ovr.TrackingCap_Position, 
            0) # required capabilities

    def init_texture(self):
        """
        NOTE: Initialize OpenGL first (elsewhere), before getting Rift textures here.
        """
        # Configure Stereo settings.
        # Use a single shared texture for simplicity
        # 1bb) Compute texture sizes
        recommenedTex0Size = ovr.getFovTextureSize(self.hmd, ovr.Eye_Left, 
                self.hmdDesc.DefaultEyeFov[0], 1.0)
        recommenedTex1Size = ovr.getFovTextureSize(self.hmd, ovr.Eye_Right,
                self.hmdDesc.DefaultEyeFov[1], 1.0)
        bufferSize = ovr.Sizei()
        bufferSize.w  = recommenedTex0Size.w + recommenedTex1Size.w
        bufferSize.h = max ( recommenedTex0Size.h, recommenedTex1Size.h )
        print "Recommended buffer size = ", bufferSize, bufferSize.w, bufferSize.h
        # NOTE: We need to have set up OpenGL context before this point...
        # 1c) Allocate SwapTextureSets
        self.pTextureSet = ovr.createSwapTextureSetGL(self.hmd,
                GL_SRGB8_ALPHA8, bufferSize.w, bufferSize.h)
        # print self.pTextureSet

        # Initialize VR structures, filling out description.
        # 1ba) Compute FOV
        eyeRenderDesc = (ovr.EyeRenderDesc * 2)()
        hmdToEyeViewOffset = (ovr.Vector3f * 2)()
        eyeRenderDesc[0] = ovr.getRenderDesc(self.hmd, ovr.Eye_Left, self.hmdDesc.DefaultEyeFov[0])
        eyeRenderDesc[1] = ovr.getRenderDesc(self.hmd, ovr.Eye_Right, self.hmdDesc.DefaultEyeFov[1])
        hmdToEyeViewOffset[0] = eyeRenderDesc[0].HmdToEyeViewOffset
        hmdToEyeViewOffset[1] = eyeRenderDesc[1].HmdToEyeViewOffset
        self.hmdToEyeViewOffset = hmdToEyeViewOffset
        # Initialize our single full screen Fov layer.
        layer = ovr.LayerEyeFov()
        layer.Header.Type      = ovr.LayerType_EyeFov
        layer.Header.Flags     = ovr.LayerFlag_TextureOriginAtBottomLeft # OpenGL convention
        layer.ColorTexture[0]  = self.pTextureSet # single texture for both eyes
        layer.ColorTexture[1]  = self.pTextureSet # single texture for both eyes
        layer.Fov[0]           = eyeRenderDesc[0].Fov
        layer.Fov[1]           = eyeRenderDesc[1].Fov
        layer.Viewport[0]      = ovr.Recti(ovr.Vector2i(0, 0),                ovr.Sizei(bufferSize.w / 2, bufferSize.h))
        layer.Viewport[1]      = ovr.Recti(ovr.Vector2i(bufferSize.w / 2, 0), ovr.Sizei(bufferSize.w / 2, bufferSize.h))
        self.layer = layer
        v = self.layer.Viewport[0]
        # print v.Pos.x, v.Pos.y, v.Size.w, v.Size.h
        # ld.RenderPose is updated later per frame.

    def dispose_hmd(self):
        "Release resources for Oculus Rift tracking and rendering"
        # 3) Shutdown
        # 3a) TODO: Call ovr_DestroySwapTextureSet to destroy swap texture buffers. Call ovr_DestroyMirrorTexture to destroy a mirror texture. To destroy the ovrHmd object, call ovr_Destroy.
        if self.hmd is not None:
            if self.pTextureSet is not None:
                ovr.destroySwapTextureSet(self.hmd, self.pTextureSet)
            ovr.destroy(self.hmd)
        ovr.shutdown()        

    def recenter_pose(self):
        ovr.recenterPose(self.hmd)

    def submit_frame(self):
        # 2c) Call ovr_SubmitFrame, passing swap texture set(s) from the previous step within a ovrLayerEyeFov structure. Although a single layer is required to submit a frame, you can use multiple layers and layer types for advanced rendering. ovr_SubmitFrame passes layer textures to the compositor which handles distortion, timewarp, and GPU synchronization before presenting it to the headset. 
        layers = self.layer.Header
        viewScale = ovr.ViewScaleDesc()
        viewScale.HmdSpaceToWorldScaleInMeters = 1.0
        viewScale.HmdToEyeViewOffset[0] = self.hmdToEyeViewOffset[0]
        viewScale.HmdToEyeViewOffset[1] = self.hmdToEyeViewOffset[1]
        result = ovr.submitFrame(self.hmd, self.frame_index, viewScale, layers, 1)
        self.frame_index += 1

    def update_gl_poses(self):
        # 2a) Use ovr_GetTrackingState and ovr_CalcEyePoses to compute eye poses needed for view rendering based on frame timing information
        ftiming  = ovr.getFrameTiming(self.hmd, 0)
        hmdState = ovr.getTrackingState(self.hmd, ftiming.DisplayMidpointSeconds)
        # print hmdState.HeadPose.ThePose
        ovr.calcEyePoses(hmdState.HeadPose.ThePose, 
                self.hmdToEyeViewOffset,
                self.layer.RenderPose)
        # Increment to use next texture, just before writing
        # 2d) Advance CurrentIndex within each used texture set to target the next consecutive texture buffer for the following frame.
        tsc = self.pTextureSet.contents
        tsc.CurrentIndex = (tsc.CurrentIndex + 1) % tsc.TextureCount
        texture = ctypes.cast(ctypes.addressof(tsc.Textures[tsc.CurrentIndex]), ctypes.POINTER(ovr.GLTexture)).contents
        return self.layer, texture.OGL.TexId
