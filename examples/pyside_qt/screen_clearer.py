#!/bin/env python


from OpenGL.GL import *


class ScreenClearer():

    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue
    
    def init_gl(self):
        glClearColor(self.red, self.green, self.blue, 0)

    def display_gl(self):
        glClear(GL_COLOR_BUFFER_BIT)

    def dispose_gl(self):
        pass
