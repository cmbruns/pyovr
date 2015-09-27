
import ctypes
import math

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.raw.GL.EXT.framebuffer_sRGB import glInitFramebufferSrgbEXT
from OpenGL.GL.EXT.framebuffer_sRGB import *

import ovr

class GlutRenderer():
    
    def __init__(self):
        self.fbo = None
        self.display_func = None
        self.hmd = None

    def __enter__(self):
        self.init_gl(640, 480)
        return self

    def __exit__(self, arg2, arg3, arg4):
        self.dispose_gl()

    def init_gl(self, width, height):
        "Create resources for OpenGL rendering"
        self.glut_window_width = width
        self.glut_window_height = height
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
        glutInitWindowSize(self.glut_window_width, self.glut_window_height)
        glutInitWindowPosition(50, 50)
        win = glutCreateWindow("Just a triangle")
        if glInitFramebufferSrgbEXT():
            pass
            glEnable(GL_FRAMEBUFFER_SRGB_EXT)
        glViewport(0, 0, int(self.glut_window_width), int(self.glut_window_height))
        glutDisplayFunc(self.draw_scene)
        glutIdleFunc(self.draw_scene)
        glutReshapeFunc(self.resize_console)
        glutKeyboardFunc(self.key_press)
        # 
        glClearColor(0.2, 0.2, 0.5, 1)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(self.glut_window_width)/float(self.glut_window_height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # Framebuffer
        self.fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self.fbo)
        # glEnable(GL_FRAMEBUFFER_SRGB_EXT) # redundant?
        print "framebuffer = ", self.fbo

    def draw_scene(self):
        "Paint one frame image during display loop"
        # A) Display something to screen, for comparison to Rift
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(self.glut_window_width)/float(self.glut_window_height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClearColor(0.2, 0.5, 0.2, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if self.display_func is not None:
            self.display_func()
        # B) Display to Rift
        # Clear and set up render-target.            
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        layer, texId = self.hmd.update_gl_poses()
        # texture = ctypes.cast(ctypes.addressof(tsc.Textures[tsc.CurrentIndex]), ctypes.POINTER(ovr.GLTexture)).contents
        glFramebufferTexture2D(GL_FRAMEBUFFER, 
                GL_COLOR_ATTACHMENT0, 
                GL_TEXTURE_2D,
                texId,
                0)
        # print format(glCheckFramebufferStatus(GL_FRAMEBUFFER), '#X'), GL_FRAMEBUFFER_COMPLETE
        glClearColor(0.5, 0.5, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        for eye in range(2):
            # Set up eye viewport
            v = layer.Viewport[eye]
            glViewport(v.Pos.x, v.Pos.y, v.Size.w, v.Size.h)                
            # Get projection matrix for the Rift camera
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            proj = ovr.matrix4f_Projection(layer.Fov[eye], 0.2, 100.0,
                            ovr.Projection_RightHanded)
            glMultTransposeMatrixf(proj.M)
            # Get view matrix for the Rift camera
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            p = layer.RenderPose[eye].Position
            q = layer.RenderPose[eye].Orientation
            pitch, yaw, roll = q.getPitchYawRoll()
            glRotatef(-pitch*180/math.pi, 1, 0, 0)
            glRotatef(-yaw*180/math.pi, 0, 1, 0)
            glRotatef(-roll*180/math.pi, 0, 0, 1)
            glTranslatef(-p.x, -p.y, -p.z)
            # Render the scene for this eye.
            if self.display_func is not None:
                self.display_func()
        self.hmd.submit_frame()
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glutSwapBuffers()

    def dispose_gl(self):
        "Release resources used for OpenGL rendering"
        if self.fbo is not None:
            glDeleteFramebuffers( [self.fbo] )

    def key_press(self, key, x, y):
        if ord(key) == 27:
            # print "Escape!"
            if bool(glutLeaveMainLoop):
                glutLeaveMainLoop()
            else:
                raise Exception("Application quit")
        if key == "r":
            self.hmd.recenter_hmd()

    def resize_console(self, width, height):
        if height == 0:
            height = 1
        self.glut_window_width = width
        self.glut_window_height = height
        glViewport(0, 0, int(self.glut_window_width), int(self.glut_window_height))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(self.glut_window_width)/float(self.glut_window_height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def run_main_loop(self):
        glutMainLoop()

    def set_display_func(self, fn):
        self.display_func = fn

    def set_hmd(self, hmd):
        self.hmd = hmd

