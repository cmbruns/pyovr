#! /usr/bin/env python
import pygame
import pygame.locals as pgl
import ovr

from RiftApp import RiftApp
from cgkit.cgtypes import mat4, vec3, quat
from OpenGL.GL import *   #@UnusedWildImport
from OpenGL.GL import shaders


VERTEX_SOURCE = """#version 450 core
#line 14
layout(location = 0) uniform mat4 Projection = mat4(1);
layout(location = 4) uniform mat4 ModelView = mat4(1);
layout(location = 8) uniform float Size = 1.0;

const vec3 UNIT_CUBE[8] = vec3[8](
  vec3(-1.0, -1.0, -1.0),
  vec3(1.0, -1.0, -1.0),
  vec3(-1.0, 1.0, -1.0),
  vec3(1.0, 1.0, -1.0),
  vec3(-1.0, -1.0, 1.0),
  vec3(1.0, -1.0, 1.0),
  vec3(-1.0, 1.0, 1.0),
  vec3(1.0, 1.0, 1.0)
);

const vec3 UNIT_CUBE_NORMALS[6] = vec3[6](
  vec3(0.0, 0.0, -1.0),
  vec3(0.0, 0.0, 1.0),
  vec3(1.0, 0.0, 0.0),
  vec3(-1.0, 0.0, 0.0),
  vec3(0.0, 1.0, 0.0),
  vec3(0.0, -1.0, 0.0)
);

const int CUBE_INDICES[36] = int[36](
  0, 1, 2, 2, 1, 3, // front
  4, 6, 5, 6, 5, 7, // back
  0, 2, 4, 4, 2, 6, // left
  1, 3, 5, 5, 3, 7, // right
  2, 6, 3, 6, 3, 7, // top
  0, 1, 4, 4, 1, 5  // bottom
);

out vec3 _color;

void main() {
  _color = vec3(1.0, 0.0, 0.0);
  int vertexIndex = CUBE_INDICES[gl_VertexID];
  int normalIndex = gl_VertexID / 6;
  
  _color = UNIT_CUBE_NORMALS[normalIndex];
  if (any(lessThan(_color, vec3(0.0)))) {
      _color = vec3(1.0) + _color;
  }

  gl_Position = Projection * ModelView * vec4(UNIT_CUBE[vertexIndex] * Size, 1.0);
}
"""

FRAGMENT_SOURCE = """#version 450 core
#line 65
in vec3 _color;
out vec4 FragColor;

void main() {
  FragColor = vec4(_color, 1.0);
}
"""


class ColorCube():
  def __init__(self, size = ovr.DEFAULT_IPD):
    self.size = size
    self.vertexShader = shaders.compileShader(VERTEX_SOURCE, GL_VERTEX_SHADER)
    self.fragmentShader = shaders.compileShader(FRAGMENT_SOURCE, GL_FRAGMENT_SHADER)
    self.shader = shaders.compileProgram(self.vertexShader,self.fragmentShader)
    self.vao = glGenVertexArrays(1)
    glBindVertexArray(self.vao)
    
  def draw(self, projection, modelview):
    shaders.glUseProgram(self.shader)
    glUniformMatrix4fv(0, 1, GL_FALSE, projection)
    glUniformMatrix4fv(4, 1, GL_FALSE, modelview)
    glUniform1f(8, self.size / 2.0)
    glDrawArrays(GL_TRIANGLES, 0, 36)

  
def ovrPoseToMat4(pose):
  # Apply the head orientation
  rot = pose.Orientation
  # Convert the OVR orientation (a quaternion structure) to a cgkit quaternion 
  # class, and from there to a mat4  Coordinates are camera coordinates
  rot = quat(rot[-1:]+rot[:-1]) # reorder xyzw -> wxyz
  rot = rot.toMat4()

  # Apply the head position
  pos = pose.Position
  # Convert the OVR position (a vector3 structure) to a cgcit vector3 class. 
  # Position is in camera / Rift coordinates
  pos = vec3(pos)
  pos = mat4(1.0).translate(pos)
  
  pose = pos * rot
  return pose

class RiftDemo(RiftApp):
  def __init__(self):
    RiftApp.__init__(self)
    self.cube_size = self.rift.get_float(ovr.KEY_IPD, ovr.DEFAULT_IPD)
    self.reset_camera()
    
  def reset_camera(self):
    self.camera = mat4(1.0)
    self.camera.translate(vec3(0, 0, 0.2))

  def recompose_camera(self):
    (tr, rot, _) = self.camera.decompose()
    self.camera = mat4(1.0)
    self.camera.translate(tr)
    self.camera = self.camera * rot
    
  def init_gl(self):
    RiftApp.init_gl(self)
    glEnable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)
    glClearColor(0.1, 0.1, 0.1, 1)
    self.cube = ColorCube()

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
      self.rift.recenter_pose()
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
     
    projection = list(self.projections[eye])
    eyeview = ovrPoseToMat4(self.poses[eye])
    # apply the camera position
    cameraview = self.camera * eyeview  
    modelview = cameraview.inverse().toList()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
  
    self.cube.draw(projection, modelview);


RiftDemo().run();


