
import glfw

from ovr.triangle_drawer_compatibility import TriangleDrawerCompatibility
from ovr.rift_gl_renderer_compatibility import RiftGLRendererCompatibility


class GlfwApp(object):

    def key_callback(self, window, key, scancode, action, mods):
        "press ESCAPE to quit the application"
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, True)

    def run(self):
        # Initialize the library
        if not glfw.init():
            return
        # Create a windowed mode window and its OpenGL context
        self.window = glfw.create_window(640, 480, "Hello World", None, None)
        if not self.window:
            glfw.terminate()
            return
    
        renderer = RiftGLRendererCompatibility()
        # Paint a triangle in the center of the screen
        renderer.append(TriangleDrawerCompatibility())
    
        # Make the window's context current
        glfw.make_context_current(self.window)
    
        # Initialize Oculus Rift
        renderer.init_gl()
        renderer.rift.recenter_pose()
        
        glfw.set_key_callback(self.window, self.key_callback)
    
        # Loop until the user closes the window
        while not glfw.window_should_close(self.window):
            # Render here, e.g. using pyOpenGL
            renderer.display_rift_gl()
    
            # Swap front and back buffers
            glfw.swap_buffers(self.window)
    
            # Poll for and process events
            glfw.poll_events()
    
        glfw.terminate()

if __name__ == "__main__":
    GlfwApp().run()
