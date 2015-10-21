#!/bin/env python


import sys


from OpenGL.GL import *
from PySide import QtCore
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
        # Update Rift outside of normal paintGL() sequence,
        # so we don't have to worry about vsync or monitor frame rate.
        self.riftTimer = QTimer(self)
        self.riftTimer.setSingleShot(True)
        self.riftTimer.setInterval(0)
        self.riftTimer.timeout.connect(self.renderRift)
        # For display to screen (i.e. not Rift)
        # self.screenTimer = QTimer(self)
        # self.screenTimer.setSingleShot(True)
        # self.screenTimer.setInterval(20)
        # self.screenTimer.timeout.connect(self.updateGL)
        # self.setAutoBufferSwap(True)

    def initializeGL(self):
        self.renderer.init_gl()
        # Begin rendering to Rift as screen rendering begins
        self.renderer.rift.recenter_pose()
        self.riftTimer.start() 

    def paintGL(self):
        # self.renderer.display_desktop_gl()
        # self.screenTimer.start() # perpetually rerender
        pass

    def renderRift(self):
        "Rift rendering is asynchronous wrt paintGL"
        self.makeCurrent()
        self.renderer.display_rift_gl()
        self.doneCurrent()
        self.riftTimer.start() # trigger another call to renderRift

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
