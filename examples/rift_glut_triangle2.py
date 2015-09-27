#!/bin/env python

# Refactored version of rift_glut_triangle.
# This version segregates responsibilities into separate (Glut)Renderer and Hmd classes.
# So maybe I could in the future more easily create examples using more modern Rendering methods.

from OpenGL.GL import *

from hmd import Hmd
from glut_renderer import GlutRenderer


def display():
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


with GlutRenderer() as r:
    r.set_display_func(display)
    with Hmd() as h:
        r.set_hmd(h)
        r.run_main_loop()

