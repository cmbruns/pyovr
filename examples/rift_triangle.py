#!/bin/env python

import sys
import time

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import ovr

class RiftTriangle():
    "Example program for Oculus Rift rendering in python"

    def __init__(self):
        self.hmd = None
        self.pTextureSet = None
        self.isVisible = True
        self.fbo = None
        self.frame_index = 0
    
    def __enter__(self):
        "Initial set up of HMD and OpenGL"
        self.init_gl(640, 480)
        self.init_hmd()
        return self

    def __exit__(self, arg2, arg3, arg4):
        self.dispose_hmd()
        self.dispose_gl()

    def init_hmd(self):
        """
        Create resources for Oculus Rift tracking and rendering.

        NOTE: Initialize OpenGL first (elsewhere), before getting Rift textures here.
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
        layer.Header.Flags     = 0
        layer.ColorTexture[0]  = self.pTextureSet
        layer.ColorTexture[1]  = self.pTextureSet
        layer.Fov[0]           = eyeRenderDesc[0].Fov
        layer.Fov[1]           = eyeRenderDesc[1].Fov
        layer.Viewport[0]      = ovr.Recti(0, 0,                bufferSize.w / 2, bufferSize.h)
        layer.Viewport[1]      = ovr.Recti(bufferSize.w / 2, 0, bufferSize.w / 2, bufferSize.h)
        self.layer = layer
        v = self.layer.Viewport[0]
        # print v.Pos.x, v.Pos.y, v.Size.w, v.Size.h
        # ld.RenderPose is updated later per frame.

    def render_frame(self):
        "Paint one frame image during display loop"
        # A) Display something to screen
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClearColor(0, 1, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        # B) Report Head Tracking
        # if self.hmd is None:
        #     return
        # Get both eye poses simultaneously, with IPD offset already included.
        # 2) Set up frame handling
        # 2a) Use ovr_GetTrackingState and ovr_CalcEyePoses to compute eye poses needed for view rendering based on frame timing information
        ftiming  = ovr.getFrameTiming(self.hmd, 0)
        hmdState = ovr.getTrackingState(self.hmd, ftiming.DisplayMidpointSeconds)
        # print hmdState.HeadPose.ThePose
        ovr.calcEyePoses(hmdState.HeadPose.ThePose, 
                self.hmdToEyeViewOffset,
                self.layer.RenderPose)
        # print self.layer.RenderPose[0]
        if True:
            # Increment to use next texture, just before writing
            # 2d) Advance CurrentIndex within each used texture set to target the next consecutive texture buffer for the following frame.
            tsc = self.pTextureSet.contents
            tsc.CurrentIndex = (tsc.CurrentIndex + 1) % tsc.TextureCount
            # print tsc.CurrentIndex
            texture = ctypes.cast(ctypes.addressof(tsc.Textures[tsc.CurrentIndex]), ctypes.POINTER(ovr.GLTexture)).contents
            # print texture.OGL.Header
            glBindTexture(GL_TEXTURE_2D, 0)
            glEnable(GL_TEXTURE_2D)
            glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
            glFramebufferTexture2D(GL_FRAMEBUFFER, 
                    GL_COLOR_ATTACHMENT0, 
                    GL_TEXTURE_2D,
                    texture.OGL.TexId,
                    0)
            glClearColor(0.5, 0.5, 1, 1)
            glClear(GL_COLOR_BUFFER_BIT)
            # glClear(GL_COLOR_BUFFER_BIT)
            # print glCheckFramebufferStatus(GL_FRAMEBUFFER), GL_FRAMEBUFFER_COMPLETE
            # TODO: Clear and set up render-target.            
            # DIRECTX.SetAndClearRenderTarget(pTexRtv[pTextureSet.CurrentIndex], pEyeDepthBuffer)
            # Render Scene to Eye Buffers
            # 2b) TODO: Perform rendering for each eye in an engine-specific way, rendering into the current texture within the texture set. Current texture is identified by the ovrSwapTextureSet::CurrentIndex variable.
            for eye in range(2):
                pass
                # Big TODO:
                # Get view and projection matrices for the Rift camera
                # pos = originPos + originRot.Transform(layer.RenderPose[eye].Position)
                # rot = originRot * Matrix4f(layer.RenderPose[eye].Orientation)
                # finalUp      = rot.Transform(Vector3f(0, 1, 0))
                # finalForward = rot.Transform(Vector3f(0, 0, -1))
                # TODO: view         = Matrix4f::LookAtRH(pos, pos + finalForward, finalUp)
                # proj = ovr.matrix4f_Projection(layer.Fov[eye], 0.2, 1000.0,
                #                 ovr.Projection_RightHanded)
                # Render the scene for this eye.
                v = self.layer.Viewport[eye]
                glViewport(v.Pos.x, v.Pos.y, v.Size.w, v.Size.h)
                # print v.Pos.x, v.Pos.y, v.Size.w, v.Size.h
                # DIRECTX.SetViewport(layer.Viewport[eye])
                # roomScene.Render(proj * view, 1, 1, 1, 1, true)
        # Submit frame with one layer we have.
        # 2c) Call ovr_SubmitFrame, passing swap texture set(s) from the previous step within a ovrLayerEyeFov structure. Although a single layer is required to submit a frame, you can use multiple layers and layer types for advanced rendering. ovr_SubmitFrame passes layer textures to the compositor which handles distortion, timewarp, and GPU synchronization before presenting it to the headset. 
        layers = self.layer.Header
        # glBindFramebuffer(GL_FRAMEBUFFER, 0)
        viewScale = ovr.ViewScaleDesc()
        viewScale.HmdSpaceToWorldScaleInMeters = 1.0
        viewScale.HmdToEyeViewOffset[0] = self.hmdToEyeViewOffset[0]
        viewScale.HmdToEyeViewOffset[1] = self.hmdToEyeViewOffset[1]
        result = ovr.submitFrame(self.hmd, self.frame_index, viewScale, layers, 1)
        # print result
        self.frame_index += 1
        # self.isVisible = (result == ovr.Success)
        # glutSwapBuffers()


    def dispose_hmd(self):
        "Release resources for Oculus Rift tracking and rendering"
        # 3) Shutdown
        # 3a) TODO: Call ovr_DestroySwapTextureSet to destroy swap texture buffers. Call ovr_DestroyMirrorTexture to destroy a mirror texture. To destroy the ovrHmd object, call ovr_Destroy.
        if self.hmd is not None:
            if self.pTextureSet is not None:
                ovr.destroySwapTextureSet(self.hmd, self.pTextureSet)
            ovr.destroy(self.hmd)
        ovr.shutdown()        

    def init_gl(self, width, height):
        "Create resources for OpenGL rendering"
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
        glutInitWindowSize(width, height)
        glutInitWindowPosition(50, 50)
        win = glutCreateWindow("Just a triangle")  
        glViewport(0, 0, int(width), int(height))
        glutDisplayFunc(self.render_frame)
        glutIdleFunc(self.render_frame)
        glutReshapeFunc(self.resize_console)
        # 
        glClearColor(0.5, 0.5, 1, 1)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # Framebuffer
        self.fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self.fbo)
        print "framebuffer = ", self.fbo

    def resize_console(self, width, height):
        if height == 0:
            height = 1
        glViewport(0, 0, int(width), int(height))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)           

    def dispose_gl(self):
        "Release resources used for OpenGL rendering"
        if self.fbo is not None:
            glDeleteFramebuffers( [self.fbo] )

    def hmd_state(self):
        ts = ovr.getTrackingState(self.hmd, ovr.getTimeInSeconds())
        return ts

    def recenter_hmd(self):
        ovr.recenterPose(self.hmd)


if __name__ == "__main__":
    # Use "with" keyword, to get C++-like lexical scope for HMD resource
    with RiftTriangle() as app:
        glutMainLoop()

