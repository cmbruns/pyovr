
import pyglfw.pyglfw as glfw

from ovr.triangle_drawer_compatibility import TriangleDrawerCompatibility
from ovr.rift_gl_renderer_compatibility import RiftGLRendererCompatibility

def main():
    # Initialize the library
    if not glfw.init():
        return
    # Create a windowed mode window and its OpenGL context
    window = glfw.window.Window(640, 480, "Hello World", None, None)
    if not window:
        glfw.terminate()
        return

    renderer = RiftGLRendererCompatibility()
    # Paint a triangle in the center of the screen
    renderer.append(TriangleDrawerCompatibility())

    # Make the window's context current
    window.make_current()

    # Initialize Oculus Rift
    renderer.init_gl()
    renderer.rift.recenter_pose()

    # Loop until the user closes the window
    while not window.should_close:
        # Render here, e.g. using pyOpenGL
        renderer.display_rift_gl()

        # Swap front and back buffers
        window.swap_buffers()

        # Poll for and process events
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
