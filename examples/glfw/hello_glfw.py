import pyglfw.pyglfw as glfw

def main():
    # Initialize the library
    if not glfw.init():
        return
    # Create a windowed mode window and its OpenGL context
    window = glfw.window.Window(640, 480, "Hello World", None, None)
    if not window:
        glfw.terminate()
        return

    # Make the window's context current
    window.make_current()

    # Loop until the user closes the window
    while not window.should_close:
        # Render here, e.g. using pyOpenGL

        # Swap front and back buffers
        window.swap_buffers()

        # Poll for and process events
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
