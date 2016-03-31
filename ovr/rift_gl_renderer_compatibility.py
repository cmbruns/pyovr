#!/bin/env python


import math
import ctypes


from OpenGL.GL import *


from ovr.rift import Rift
import ovr


class RiftGLRendererCompatibility(list):
    "Class RiftGLRenderer is a list of OpenGL actors"

    def __init__(self):
        self.layers = list()
        self.width = 100
        self.height = 100
        self.frame_index = 0
        self.textureSwapChain = None
        self.rift = Rift()
        Rift.initialize()
        self.rift.init() # TODO: Yuck initialize() init()
        # self.rift.configure_tracking()

    def display_gl(self):
        self.display_rift_gl()
        self.display_desktop_gl()

    def display_desktop_gl(self):
        # 1) desktop (non-Rift) pass
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._set_up_desktop_projection()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        for actor in self:
            actor.display_gl()

    def display_rift_gl(self):
        # 2) Rift pass
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        layer, texId = self._update_gl_poses()
        glFramebufferTexture2D(GL_FRAMEBUFFER, 
                GL_COLOR_ATTACHMENT0, 
                GL_TEXTURE_2D,
                texId,
                0)
        # print format(glCheckFramebufferStatus(GL_FRAMEBUFFER), '#X'), GL_FRAMEBUFFER_COMPLETE
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)        
        for eye in range(2):
            # Set up eye viewport
            v = layer.Viewport[eye]
            glViewport(v.Pos.x, v.Pos.y, v.Size.w, v.Size.h)                
            # Get projection matrix for the Rift camera
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            proj = self.rift.get_perspective(layer.Fov[eye], 0.2, 100.0, )
            glMultTransposeMatrixf(proj.M)
            # Get view matrix for the Rift camera
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            p = layer.RenderPose[eye].Position
            q = layer.RenderPose[eye].Orientation
            pitch, yaw, roll = q.getEulerAngles()
            glRotatef(-roll*180/math.pi, 0, 0, 1)
            glRotatef(-yaw*180/math.pi, 0, 1, 0)
            glRotatef(-pitch*180/math.pi, 1, 0, 0)
            glTranslatef(-p.x, -p.y, -p.z)
            # Render the scene for this eye.
            for actor in self:
                actor.display_gl()
        self.submit_frame()
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def dispose_gl(self):
        for actor in self:
            actor.dispose_gl()
        if self.textureSwapChain is not None:
            self.rift.destroy_swap_texture(self.textureSwapChain)       

    def init_gl(self):
        glClearColor(0, 0, 1, 0)
        self._init_rift_render_layer()
        self.fbo = glGenFramebuffers(1)
        self._set_up_desktop_projection()
        for actor in self:
            actor.init_gl()

    def resize_gl(self, width, height):
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)
        self._set_up_desktop_projection()

    def submit_frame(self):
        # 2c) Call ovr_SubmitFrame, passing swap texture set(s) from the previous step within a ovrLayerEyeFov structure. Although a single layer is required to submit a frame, you can use multiple layers and layer types for advanced rendering. ovr_SubmitFrame passes layer textures to the compositor which handles distortion, timewarp, and GPU synchronization before presenting it to the headset. 
        layers = [self.layer.Header]
        viewScale = ovr.ViewScaleDesc()
        viewScale.HmdSpaceToWorldScaleInMeters = 1.0
        viewScale.HmdToEyeOffset[0] = self.hmdToEyeOffset[0]
        viewScale.HmdToEyeOffset[1] = self.hmdToEyeOffset[1]
        self.rift.commit_texture_swap_chain(self.textureSwapChain)
        result = self.rift.submit_frame(self.frame_index, viewScale, layers, 1)
        self.frame_index += 1

    def _init_rift_render_layer(self):
        """
        NOTE: Initialize OpenGL first (elsewhere), before getting Rift textures here.
        """
        # Configure Stereo settings.
        # Use a single shared texture for simplicity
        # 1bb) Compute texture sizes
        hmdDesc = self.rift.hmdDesc
        recommenedTex0Size = self.rift.get_fov_texture_size(ovr.Eye_Left, 
                hmdDesc.DefaultEyeFov[0])
        recommenedTex1Size = self.rift.get_fov_texture_size(ovr.Eye_Right,
                hmdDesc.DefaultEyeFov[1])
        bufferSize = ovr.Sizei()
        bufferSize.w  = recommenedTex0Size.w + recommenedTex1Size.w
        bufferSize.h = max ( recommenedTex0Size.h, recommenedTex1Size.h )
        # print "Recommended buffer size = ", bufferSize, bufferSize.w, bufferSize.h
        # NOTE: We need to have set up OpenGL context before this point...
        # 1c) Allocate SwapTextureSets
        self.textureSwapChain = self.rift.create_swap_texture(bufferSize)
        # Initialize VR structures, filling out description.
        # 1ba) Compute FOV
        eyeRenderDesc = (ovr.EyeRenderDesc * 2)()
        hmdToEyeOffset = (ovr.Vector3f * 2)()
        eyeRenderDesc[0] = self.rift.get_render_desc(ovr.Eye_Left, hmdDesc.DefaultEyeFov[0])
        eyeRenderDesc[1] = self.rift.get_render_desc(ovr.Eye_Right, hmdDesc.DefaultEyeFov[1])
        hmdToEyeOffset[0] = eyeRenderDesc[0].HmdToEyeOffset
        hmdToEyeOffset[1] = eyeRenderDesc[1].HmdToEyeOffset
        self.hmdToEyeOffset = hmdToEyeOffset
        # Initialize our single full screen Fov layer.
        layer = ovr.LayerEyeFov()
        layer.Header.Type      = ovr.LayerType_EyeFov
        layer.Header.Flags     = ovr.LayerFlag_TextureOriginAtBottomLeft # OpenGL convention
        layer.ColorTexture[0]  = self.textureSwapChain # single texture for both eyes
        layer.ColorTexture[1]  = self.textureSwapChain # single texture for both eyes
        layer.Fov[0]           = eyeRenderDesc[0].Fov
        layer.Fov[1]           = eyeRenderDesc[1].Fov
        layer.Viewport[0]      = ovr.Recti(ovr.Vector2i(0, 0),                ovr.Sizei(bufferSize.w / 2, bufferSize.h))
        layer.Viewport[1]      = ovr.Recti(ovr.Vector2i(bufferSize.w / 2, 0), ovr.Sizei(bufferSize.w / 2, bufferSize.h))
        self.layer = layer

    def _set_up_desktop_projection(self):
        # TODO: non-fixed-function pathway
        # Projection matrix for desktop (i.e. non-Rift) display
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        zNear = 0.1
        zFar = 1000.0
        fovY = 3.14159 / 4.0 # radians
        aspect = float(self.width) / float(self.height)
        fH = math.tan(fovY) * zNear
        fW = fH * aspect
        glFrustum( -fW, fW, -fH, fH, zNear, zFar )
        #
        glMatrixMode(GL_MODELVIEW)

    def _update_gl_poses(self):
        # 2a) Use ovr_GetTrackingState and ovr_CalcEyePoses to compute eye poses needed for view rendering based on frame timing information
        displayMidpointSeconds = self.rift.get_predicted_display_time(self.frame_index)
        hmdState = self.rift.get_tracking_state(displayMidpointSeconds, True)
        # print hmdState.HeadPose.ThePose
        self.rift.calc_eye_poses(hmdState.HeadPose.ThePose, 
                self.hmdToEyeOffset, self.layer.RenderPose)
        # Increment to use next texture, just before writing
        # 2d) Advance CurrentIndex within each used texture set to target the next consecutive texture buffer for the following frame.
        textureId =  self.rift.get_current_texture_id_GL(self.textureSwapChain)
        # TODO: mirror texture
        # mirrorTextureId = ovr.getMirrorTextureBufferGL(self.rift.session, self.mirrorTexture)
        return self.layer, textureId

