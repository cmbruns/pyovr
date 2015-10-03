#! /usr/bin/env python
import pygame
import pygame.locals as pgl
import ovr

from RiftApp import RiftApp
from cgkit.cgtypes import mat4, vec3, quat
from OpenGL.GL import *

def ovrPoseToMat4(pose):
  # Apply the head orientation
  rot = pose.Orientation
  # Convert the OVR orientation (a quaternion structure) to a cgkit quaternion 
  # class, and from there to a mat4  Coordinates are camera coordinates
  rot = quat(rot.toList())
  rot = rot.toMat4()

  # Apply the head position
  pos = pose.Position
  # Convert the OVR position (a vector3 structure) to a cgcit vector3 class. 
  # Position is in camera / Rift coordinates
  pos = vec3(pos.toList())
  pos = mat4(1.0).translate(pos)
  
  pose = pos * rot
  return pose


def draw_color_cube(size=1.0):
  p = size / 2.0
  n = -p
  glBegin(GL_QUADS)

  # front
  glColor3f(1, 1, 0)
  glVertex3f(n, n, n)
  glVertex3f(p, n, n)
  glVertex3f(p, p, n)
  glVertex3f(n, p, n)
  # back
  glColor3f(0.2, 0.2, 1)
  glVertex3f(n, n, p)
  glVertex3f(p, n, p)
  glVertex3f(p, p, p)
  glVertex3f(n, p, p)
  # right
  glColor3f(1, 0, 0)
  glVertex3f(p, n, n)
  glVertex3f(p, n, p)
  glVertex3f(p, p, p)
  glVertex3f(p, p, n)
  # left
  glColor3f(0, 1, 1)
  glVertex3f(n, n, n)
  glVertex3f(n, n, p)
  glVertex3f(n, p, p)
  glVertex3f(n, p, n)
  # top
  glColor3f(0, 1, 0)
  glVertex3f(n, p, n)
  glVertex3f(p, p, n)
  glVertex3f(p, p, p)
  glVertex3f(n, p, p)
  # bottom
  glColor3f(1, 0, 1)
  glVertex3f(n, n, n)
  glVertex3f(p, n, n)
  glVertex3f(p, n, p)
  glVertex3f(n, n, p)
  glEnd()


class RiftDemo(RiftApp):
  def __init__(self):
    RiftApp.__init__(self)
    self.cube_size = ovr.getFloat(self.hmd, 
      ovr.KEY_IPD, ovr.DEFAULT_IPD)
    self.reset_camera()
    
  def reset_camera(self):
    self.camera = mat4(1.0)
    self.camera.translate(vec3(0, 0, 0.2))

  def recompose_camera(self):
    (tr, rot, sc) = self.camera.decompose()
    self.camera = mat4(1.0)
    self.camera.translate(tr)
    self.camera = self.camera * rot
    
  def init_gl(self):
    RiftApp.init_gl(self)
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1)

  def update(self):
    RiftApp.update(self)
    pressed = pygame.key.get_pressed()

    if pressed[pgl.K_r]:
      self.reset_camera()

    rotation = 0.0
    
    if pressed[pgl.K_q]:
      rotation = +1.0
    if pressed[pgl.K_e]:
      rotation = -1.0
    if (rotation != 0.0):
      self.camera = self.camera * \
        mat4.rotation(rotation * 0.01, vec3(0, 1, 0))
      self.recompose_camera()
       
    # Modify direction vectors for key presses
    translation = vec3()
    if pressed[pgl.K_r]:
      ovr.recenterPose(self.hmd)
    if pressed[pgl.K_w]:
      translation.z = -1.0
    elif pressed[pgl.K_s]:
      translation.z = +1.0
    if pressed[pgl.K_a]:
      translation.x = -1.0
    elif pressed[pgl.K_d]:
      translation.x = +1.0
    if (vec3.length(translation) > 0.1):
      translation = self.camera.getMat3() * (translation * 0.005)
      self.camera.translate(translation)
      self.recompose_camera()

  

  def render_scene(self):
    eye = self.currentEye;

    eyeview = ovrPoseToMat4(self.poses[eye])
  
    # apply the camera position
    cameraview = self.camera * eyeview  

    glMatrixMode(GL_PROJECTION)
    glLoadMatrixf(self.projections[eye].toList())

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity();
    glLoadMatrixf(cameraview.inverse().toList())

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    draw_color_cube(self.cube_size)


RiftDemo().run();


