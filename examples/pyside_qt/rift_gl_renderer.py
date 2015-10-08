#!/bin/env python


import math


from OpenGL.GL import *


from ovr.rift import Rift


class RiftGLRenderer(list):
    "Class RiftGLRenderer is a list of OpenGL actors"

    def __init__(self):
        self.rift = Rift()
        self.layers = list()
        self.width = 100
        self.height = 100

    def display_gl(self):
        # TODO - Rift pass and screen pass
        for actor in self:
            actor.display_gl()

    def dispose_gl(self):
        for actor in self:
            actor.dispose_gl()

    def init_gl(self):
        # TODO: layers and framebuffers
        self._set_up_desktop_projection()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        #
        for actor in self:
            actor.init_gl()

    def resize_gl(self, width, height):
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)
        self._set_up_desktop_projection()

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

