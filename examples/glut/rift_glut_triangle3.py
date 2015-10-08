#!/bin/env python


from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


from ovr.rift_gl_renderer import RiftGLRenderer
from ovr.triangle_drawer import TriangleDrawer




class GlutDemoApp():

    def __init__(self):
        self.renderer = RiftGLRenderer()
        self.renderer.append(TriangleDrawer())
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
        glutInitWindowSize(400, 400)
        glutInitWindowPosition(50, 50)
        win = glutCreateWindow("Just a triangle")
        glutDisplayFunc(self.display)
        glutIdleFunc(self.renderer.display_gl)
        glutReshapeFunc(self.renderer.resize_gl)
        glutKeyboardFunc(self.key_press)
        self.renderer.init_gl()
        glutMainLoop()        

    def display(self):
        self.renderer.display_gl()
        glutSwapBuffers()

    def key_press(self, key, x, y):
        if ord(key) == 27:
            # print "Escape!"
            if bool(glutLeaveMainLoop):
                glutLeaveMainLoop()
            else:
                raise Exception("Application quit")
        if key == "r":
            self.renderer.rift.recenter_pose()


if __name__ == "__main__":
    GlutDemoApp()
