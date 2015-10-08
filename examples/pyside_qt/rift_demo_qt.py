#!/bin/env python


import sys


from OpenGL.GL import *
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *


from ovr.triangle_drawer import TriangleDrawer
from ovr.rift_gl_renderer import RiftGLRenderer


class DemoWidget(QGLWidget):

    def __init__(self):
        super(DemoWidget, self).__init__()
        self.renderer = RiftGLRenderer()
        # Paint a triangle in the center of the screen
        self.renderer.append(TriangleDrawer())

    def initializeGL(self):
        self.renderer.init_gl()

    def paintGL(self):
        self.renderer.display_gl()

    def resizeGL(self, width, height):
        self.renderer.resize_gl(width, height)


if __name__ == "__main__":
    # Create a Qt application
    app = QApplication(sys.argv)
    # Create a Label and show it
    win = QMainWindow()
    glw = DemoWidget()
    win.setCentralWidget(glw)
    win.show()
    # Enter Qt application main loop
    retval = app.exec_()
    sys.exit(retval)
