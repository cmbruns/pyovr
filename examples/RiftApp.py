import ovr
import pygame
import pygame.locals as pgl

from OpenGL.GL import *

class RiftApp():
  def __init__(self):
    ovr.initialize(None)
    self.hmd, self.luid = ovr.create()
    self.hmdDesc = ovr.getHmdDesc(self.hmd)
    self.frame = 0

    ovr.configureTracking(self.hmd, 
        ovr.TrackingCap_Orientation | # supported capabilities
        ovr.TrackingCap_MagYawCorrection |
        ovr.TrackingCap_Position, 
        0) # required capabilities

    self.fovPorts = (
      self.hmdDesc.DefaultEyeFov[0],
      self.hmdDesc.DefaultEyeFov[1]
    )

    self.projections = map(
      lambda fovPort:
        (ovr.matrix4f_Projection(
           fovPort, 0.01, 1000, True)),
      self.fovPorts
    )

  def close(self):
    glDeleteFramebuffers(1, self.fbo)
    glDeleteTextures(self.color)
    glDeleteRenderbuffers(1, self.depth)

    self.hmd.destroy()
    self.hmd = None
    ovr.Hmd.shutdown()

  def create_window(self):
    import os
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100, 100)
    pygame.init()
    pygame.display.set_mode(
      (
        self.hmdDesc.Resolution.w / 4,
        self.hmdDesc.Resolution.h / 4
      ),
      pgl.HWSURFACE | pgl.OPENGL | pgl.NOFRAME)

  def init_gl(self):

    recommenedTex0Size = ovr.getFovTextureSize(self.hmd, ovr.Eye_Left, 
            self.hmdDesc.DefaultEyeFov[0], 1.0)
    
    recommenedTex1Size = ovr.getFovTextureSize(self.hmd, ovr.Eye_Right,
            self.hmdDesc.DefaultEyeFov[1], 1.0)
    self.bufferSize = ovr.Sizei()
    self.bufferSize.w  = recommenedTex0Size.w + recommenedTex1Size.w
    self.bufferSize.h = max ( recommenedTex0Size.h, recommenedTex1Size.h )
    print "Recommended buffer size = ", self.bufferSize, self.bufferSize.w, self.bufferSize.h
    # NOTE: We need to have set up OpenGL context before this point...
    # 1c) Allocate SwapTextureSets
    self.pTextureSet = ovr.createSwapTextureSetGL(self.hmd,
            GL_RGBA8, self.bufferSize.w, self.bufferSize.h)

    # Initialize our single full screen Fov layer.
    layer = ovr.LayerEyeFov()
    layer.Header.Type      = ovr.LayerType_EyeFov
    layer.Header.Flags     = ovr.LayerFlag_TextureOriginAtBottomLeft # OpenGL convention
    layer.ColorTexture[0]  = self.pTextureSet # single texture for both eyes
    layer.ColorTexture[1]  = self.pTextureSet # single texture for both eyes
    layer.Fov[0]           = self.fovPorts[0]
    layer.Fov[1]           = self.fovPorts[1]
    layer.Viewport[0]      = ovr.Recti(ovr.Vector2i(0, 0), ovr.Sizei(self.bufferSize.w / 2, self.bufferSize.h))
    layer.Viewport[1]      = ovr.Recti(ovr.Vector2i(self.bufferSize.w / 2, 0), ovr.Sizei(self.bufferSize.w / 2, self.bufferSize.h))
    self.layer = layer

    self.build_framebuffer();

    self.eyeRenderDescs = [ ovr.EyeRenderDesc(), ovr.EyeRenderDesc() ];
    self.eyeOffsets = (ovr.Vector3f * 2)();
    for eye in range(0, 2):
      self.eyeRenderDescs[eye] = ovr.getRenderDesc(self.hmd, eye, self.fovPorts[eye]);
      self.eyeOffsets[eye] = self.eyeRenderDescs[eye].HmdToEyeViewOffset
      
  def build_framebuffer(self):
    self.fbo = glGenFramebuffers(1)
    self.depth = glGenRenderbuffers(1)
    # Set up the depth attachment renderbuffer
    glBindRenderbuffer(GL_RENDERBUFFER, self.depth)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, 
                          self.bufferSize.w, self.bufferSize.h)
    glBindRenderbuffer(GL_RENDERBUFFER, 0)

    # Set up the framebuffer proper
    glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, self.depth)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

  def bind_framebuffer(self):
      glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
      tsc = self.pTextureSet.contents
      texture = ctypes.cast(ctypes.addressof(tsc.Textures[tsc.CurrentIndex]), ctypes.POINTER(ovr.GLTexture)).contents
      glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture.OGL.TexId, 0)
      fboStatus = glCheckFramebufferStatus(GL_FRAMEBUFFER)
      if (GL_FRAMEBUFFER_COMPLETE != fboStatus):
        raise Exception("Bad framebuffer setup")
  
  def increment_framebuffer(self): 
    tsc = self.pTextureSet.contents
    tsc.CurrentIndex = (tsc.CurrentIndex + 1) % tsc.TextureCount

  def submit_frame(self): 
    layers = self.layer.Header
    viewScale = ovr.ViewScaleDesc()
    viewScale.HmdSpaceToWorldScaleInMeters = 1.0
    for eye in range(0, 2):
      self.layer.RenderPose[eye] = self.poses[eye]
      viewScale.HmdToEyeViewOffset[eye] = self.eyeOffsets[eye]
    result = ovr.submitFrame(self.hmd, self.frame, viewScale, layers, 1)

  def render_frame(self):
    self.frame += 1

    # Fetch the head pose
    self.poses = (ovr.Posef * 2)()
    ovr.getEyePoses(self.hmd, self.frame, self.eyeOffsets, self.poses)

    # Active the offscreen framebuffer and render the scene
    self.bind_framebuffer()

    for eye in range(0, 2):
      self.currentEye = eye;
      vp = self.layer.Viewport[eye]
      glViewport(vp.Pos.x, vp.Pos.y, vp.Size.w, vp.Size.h)
      glEnable(GL_SCISSOR_TEST)
      glScissor(vp.Pos.x, vp.Pos.y, vp.Size.w, vp.Size.h)
      self.render_scene()

    self.currentEye = -1;
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    self.submit_frame();
    self.increment_framebuffer();
    glGetError()

  def update(self):
    for event in pygame.event.get():
      self.on_event(event)

  def on_event(self, event):
    if event.type == pgl.QUIT:
      self.running = False
      return True
    if event.type == pgl.KEYUP and event.key == pgl.K_ESCAPE:
      self.running = False
      return True
    return False

  def run(self):
    self.create_window()
    self.init_gl()
    self.running = True
    while self.running:
      self.update()
      self.render_frame()
      #pygame.display.flip()
    self.close()
    pygame.quit()
