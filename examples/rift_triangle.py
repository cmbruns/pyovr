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

        Initialize OpenGL first, before getting Rift textures.
        """
        # 1) Initialize
        # 1a) Initialize Oculus SDK
        ovr.initialize(None)
        self.hmd, luid = ovr.create()
        self.hmdDesc = ovr.getHmdDesc(self.hmd)
        ovr.configureTracking(self.hmd, 
            ovr.TrackingCap_Orientation | # supported capabilities
            ovr.TrackingCap_MagYawCorrection |
            ovr.TrackingCap_Position, 
            0) # required capabilities
        # 1b) TODO: Compute FOV and texture sizes 
        # Configure Stereo settings.
        # Use a single shared texture for simplicity
        recommenedTex0Size = ovr.getFovTextureSize(self.hmd, ovr.Eye_Left, 
                self.hmdDesc.DefaultEyeFov[0], 1.0)
        recommenedTex1Size = ovr.getFovTextureSize(self.hmd, ovr.Eye_Right,
                self.hmdDesc.DefaultEyeFov[1], 1.0)
        bufferSize = ovr.Sizei()
        bufferSize.w  = recommenedTex0Size.w + recommenedTex1Size.w
        bufferSize.h = max ( recommenedTex0Size.h, recommenedTex1Size.h )
        print "Recommended buffer size = ", bufferSize

        # Maybe need to set up OpenGL context first...
        # 1c) Allocate SwapTextureSets
        self.pTextureSet = ovr.createSwapTextureSetGL(self.hmd,
                GL_SRGB8_ALPHA8, bufferSize.w, bufferSize.h)
        print self.pTextureSet
        # print "Rift screen size = ", self.hmdDesc.Resolution        

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
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def dispose_gl(self):
        "Release resources used for OpenGL rendering"
        pass 

    def render_frame(self):
        "Paint one frame image during display loop"
        if self.hmd is None:
            return
        # 2) Set up frame handling
        # 2a) TODO: Use ovr_GetTrackingState and ovr_CalcEyePoses to compute eye poses needed for view rendering based on frame timing information
        # 2b) TODO: Perform rendering for each eye in an engine-specific way, rendering into the current texture within the texture set. Current texture is identified by the ovrSwapTextureSet::CurrentIndex variable.
        # 2c) TODO: Call ovr_SubmitFrame, passing swap texture set(s) from the previous step within a ovrLayerEyeFov structure. Although a single layer is required to submit a frame, you can use multiple layers and layer types for advanced rendering. ovr_SubmitFrame passes layer textures to the compositor which handles distortion, timewarp, and GPU synchronization before presenting it to the headset. 
        # 2d) TODO: Advance CurrentIndex within each used texture set to target the next consecutive texture buffer for the following frame.

    def hmd_state(self):
        ts = ovr.getTrackingState(self.hmd, ovr.getTimeInSeconds())
        return ts

    def recenter_hmd(self):
        ovr.recenterPose(self.hmd)


if __name__ == "__main__":
    # Use "with" keyword, to get C++-like lexical scope for HMD resource
    with RiftTriangle() as app:
        for t in range(3):
            ts = app.hmd_state()
            print ts.HeadPose.ThePose
            sys.stdout.flush()
            time.sleep(0.500)

