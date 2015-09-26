#!/bin/env python

# Simplest OpenGL example I could think of

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


def draw_scene():
    glClear(GL_COLOR_BUFFER_BIT)
    #
    glBegin(GL_TRIANGLE_STRIP)
    glColor3f(1, 1, 1)
    glVertex3f(0, 0, -20)
    glVertex3f(0, 5, -20)
    glVertex3f(5, 5, -20)
    glEnd()
    #
    glutSwapBuffers()


def init_gl(width, height):
    glClearColor(0.5, 0.5, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def resize_scene(width, height):
    if height == 0:
        height = 1
    glViewport(0, 0, int(width), int(height))
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)   


if __name__ == "__main__":
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(640, 480)
    glutInitWindowPosition(50, 50)
    win = glutCreateWindow("Just a triangle")
    glutDisplayFunc(draw_scene)
    glutIdleFunc(draw_scene)
    glutReshapeFunc(resize_scene)
    init_gl(640, 480)
    glutMainLoop()
