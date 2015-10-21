#!/bin/env python


from OpenGL.GL import *


class TriangleDrawerCompatibility():
    
    def init_gl(self):
        pass

    def display_gl(self):
        glBegin(GL_TRIANGLE_STRIP)
        size = 0.15
        x = 0.10
        y = 0.00
        z = -0.5
        glColor3f(0.3, 0.3, 0.3)
        glVertex3f(x, y, z)
        glVertex3f(x, y+size, z)
        glVertex3f(x+size, y+size, z)
        glEnd()

    def dispose_gl(self):
        pass
