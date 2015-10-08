#!/bin/env python


from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


from ovr.rift_gl_renderer import RiftGLRenderer
from ovr.triangle_drawer import TriangleDrawer


renderer = RiftGLRenderer()
renderer.append(TriangleDrawer())


def display():
    renderer.display_gl()
    glutSwapBuffers()


if __name__ == "__main__":
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(400, 400)
    glutInitWindowPosition(50, 50)
    win = glutCreateWindow("Just a triangle")

    glutDisplayFunc(display)
    glutIdleFunc(renderer.display_gl)
    glutReshapeFunc(renderer.resize_gl)
    renderer.init_gl()

    glutMainLoop()
