import ovr
import pygame
import pygame.locals as pgl
from ovr.rift import Rift
from OpenGL.GL import *    #@UnusedWildImport

class RiftSwapFramebuffer():
  def __init__(self, rift, size, format_ = GL_RGBA8):
    self.rift = rift
    self.depth = 0
    self.size = size
    self.format = format_
    self.fbo = 0
    self.build()

  def __getCurrentGLTexture(self):
    tsc = self.pTextureSet.contents
    curTexturePointer = ctypes.addressof(tsc.Textures[tsc.CurrentIndex])
    # Tricky casting here
    texture = ctypes.cast(curTexturePointer, ctypes.POINTER(ovr.GLTexture)).contents
    return texture
    
  def build(self, ):
    self.pTextureSet = self.rift.create_swap_texture(self.size)
    self.depth = glGenRenderbuffers(1)
    # Set up the depth attachment renderbuffer
    glBindRenderbuffer(GL_RENDERBUFFER, self.depth)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, self.size.w, self.size.h)
    glBindRenderbuffer(GL_RENDERBUFFER, 0)

    # Set up the framebuffer proper
    self.fbo = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, self.depth)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    
  def destroy(self):
    glDeleteFramebuffers(1, [self.fbo])
    glDeleteRenderbuffers(1, [self.depth])
    if self.pTextureSet is not None:
      self.rift.destroy_swap_texture(self.pTextureSet)
  
  def attachCurrentTexture(self, target = GL_DRAW_FRAMEBUFFER):
    texture = self.__getCurrentGLTexture()
    # We switch textures every frame, so we need to bind the new texture here
    glFramebufferTexture2D(target, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture.OGL.TexId, 0)

    # FIXME? validating every frame may be excessive
    fboStatus = glCheckFramebufferStatus(target)
    if (GL_FRAMEBUFFER_COMPLETE != fboStatus):
      raise Exception("Bad framebuffer setup")
    
  def bind(self, target = GL_DRAW_FRAMEBUFFER):
    glBindFramebuffer(target, self.fbo)

    
  def unbind(self, target = GL_DRAW_FRAMEBUFFER):
    glBindFramebuffer(target, 0)

  def increment(self):
    tsc = self.pTextureSet.contents
    tsc.CurrentIndex = (tsc.CurrentIndex + 1) % tsc.TextureCount
  

class RiftApp():
  def __init__(self):
    Rift.initialize()

    self.rift = Rift()
    self.rift.init()
    self.frame = 0
    self.mirror = True

    self.eyeRenderDescs = (ovr.EyeRenderDesc * 2)()
    self.eyeOffsets = (ovr.Vector3f * 2)()
    self.projections = (ovr.Matrix4f * 2)()
    self.textureSizes = (ovr.Sizei * 2)()
    self.fovPorts = (ovr.FovPort * 2)()
    self.poses = (ovr.Posef * 2)()
    self.bufferSize = ovr.Sizei()
    self.viewScale = ovr.ViewScaleDesc()
    self.viewScale.HmdSpaceToWorldScaleInMeters = 1.0

    for eye in range(0, 2):
      self.fovPorts[eye] = self.rift.hmdDesc.DefaultEyeFov[eye]
      self.eyeRenderDescs[eye] = self.rift.get_render_desc(eye, self.fovPorts[eye]);
      self.eyeOffsets[eye] = self.eyeRenderDescs[eye].HmdToEyeViewOffset
      self.projections[eye] = Rift.get_perspective(self.fovPorts[eye], 0.01, 1000)
      self.textureSizes[eye] = self.rift.get_fov_texture_size(eye, self.fovPorts[eye])
      self.viewScale.HmdToEyeViewOffset[eye] = self.eyeOffsets[eye]

    self.bufferSize.w  = self.textureSizes[0].w + self.textureSizes[1].w
    self.bufferSize.h = max ( self.textureSizes[0].h, self.textureSizes[1].h )

    # TODO make the Rift wrapper class manage the layers and provide an API for enabling and disabling them
    # Initialize our single full screen Fov layer.
    layer = ovr.LayerEyeFov()
    layer.Header.Type      = ovr.LayerType_EyeFov
    layer.Header.Flags     = ovr.LayerFlag_TextureOriginAtBottomLeft # OpenGL convention
    layer.Fov[0]           = self.fovPorts[0]
    layer.Fov[1]           = self.fovPorts[1]
    viewportSize = ovr.Sizei(self.bufferSize.w / 2, self.bufferSize.h)
    viewportPos = ovr.Vector2i(0, 0)
    layer.Viewport[0]      = ovr.Recti(viewportPos, viewportSize)
    viewportPos = ovr.Vector2i(self.bufferSize.w / 2, 0)
    layer.Viewport[1]      = ovr.Recti(viewportPos, viewportSize)
    self.layer = layer

    self.rift.configure_tracking()
        
  def close(self):
    self.framebuffer.destroy()
    self.rift.destroy()
    self.rift = None
    Rift.shutdown()

  def create_window(self):
    import os
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100, 100)
    pygame.init()
    resolution = self.rift.get_resolution()
    resolution.w /= 4
    resolution.h /= 4
    self.windowSize = resolution 
    # Note we DO NOT want double bufering here as that will trigger v-sync
    flags = pgl.HWSURFACE | pgl.OPENGL | pgl.NOFRAME
    size = (self.windowSize.w, self.windowSize.h)
    pygame.display.set_mode(size, flags)

  def init_gl(self):
    print("GL Version: " + glGetString(GL_VERSION));
    print("GL Shader Language Version: " + glGetString(GL_SHADING_LANGUAGE_VERSION));
    print("GL Vendor: " + glGetString(GL_VENDOR));
    print("GL Renderer: " + glGetString(GL_RENDERER));
    self.framebuffer = RiftSwapFramebuffer(self.rift, self.bufferSize)
    self.layer.ColorTexture[0]  = self.framebuffer.pTextureSet # single texture for both eyes
    self.layer.ColorTexture[1]  = self.framebuffer.pTextureSet # single texture for both eyes

  def submit_frame(self): 
    layers = self.layer.Header
    for eye in range(0, 2):
      self.layer.RenderPose[eye] = self.poses[eye]
    self.rift.submit_frame(self.frame, self.viewScale, layers, 1)

  def render_frame(self):
    self.frame += 1

    # Fetch the head pose
    self.poses = self.rift.get_eye_poses(self.frame, ovr.ovrTrue, self.eyeOffsets)

    # Active the offscreen framebuffer and render the scene
    self.framebuffer.bind()
    self.framebuffer.attachCurrentTexture()
    for eye in range(0, 2):
      self.currentEye = eye
      vp = self.layer.Viewport[eye]
      glViewport(vp.Pos.x, vp.Pos.y, vp.Size.w, vp.Size.h)
      glEnable(GL_SCISSOR_TEST)
      glScissor(vp.Pos.x, vp.Pos.y, vp.Size.w, vp.Size.h)
      self.render_scene()
      
    self.currentEye = -1
    self.framebuffer.unbind()
    # Optional, mirror to the screen
    if self.mirror:
      glDisable(GL_SCISSOR_TEST)
      glViewport(0, 0, self.windowSize.w, self.windowSize.h)
      glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
      self.framebuffer.bind(GL_READ_FRAMEBUFFER)
      glBlitFramebuffer(0, 0, self.framebuffer.size.w, self.framebuffer.size.h,
                        0, 0, self.windowSize.w, self.windowSize.h, 
                        GL_COLOR_BUFFER_BIT, GL_NEAREST)
      self.framebuffer.unbind(GL_READ_FRAMEBUFFER)
    self.submit_frame()
    self.framebuffer.increment()

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
