#!/usr/bin/python

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtOpenGL import *
from OpenGL.GL import *
 

class DesktopFrame(QGLWidget):

    def initializeGL(self):
        glClearColor(0, 0, 1, 1)
        QGLWidget.initializeGL(self)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        QGLWidget.paintGL(self)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        QGLWidget.resizeGL(self, width, height)


if __name__ == "__main__":
    # Create a Qt application
    app = QApplication(sys.argv)
    # Create a Label and show it
    win = QMainWindow()
    glw = DesktopFrame()
    win.setCentralWidget(glw)
    win.show()
    # Enter Qt application main loop
    retval = app.exec_()
    sys.exit(1)
