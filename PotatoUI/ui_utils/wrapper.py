import imgui
from .widgets import GUIWindow
from imgui.integrations.glfw import GlfwRenderer
import glfw
from OpenGL import GL as gl
import sys


class GLFWImguiWrapper:
    def __init__(self, name: str, width: int, height: int, font_path=None, font_size=14, scaling_factor=1):
        self.name = name

        self.glfw_window = self.impl_glfw_init(width, height)
        self.imgui_context = imgui.create_context()

        self.imgui_backend = GlfwRenderer(self.glfw_window)
        self.io: imgui._IO = imgui.get_io()

        self.setup_main_font(font_path, font_size, scaling_factor)

        self.initializeGUI()

    def setup_main_font(self, font_path: str | None, font_size: int, scaling_factor: int = 1):
        if font_path is None:
            # Just keep the default imgui font
            return

        io = self.io
        io.fonts.clear()
        self.main_font = io.fonts.add_font_from_file_ttf(
            font_path, font_size * scaling_factor
        )
        io.font_global_scale /= scaling_factor

        self.font_scaling_factor = scaling_factor
        self.imgui_backend.refresh_font_texture()

    def add_extra_font(self, path: str, font_size_in_pixels: int, *args, **kwargs):
        io = imgui.get_io()

        newFont = io.fonts.add_font_from_file_ttf(
            path, self.font_scaling_factor * font_size_in_pixels, *args, **kwargs)
        self.imgui_backend.refresh_font_texture()
        return newFont

    def initializeGUI(self):
        pass
        # For child classes to override

    def drawGUI(self):
        pass
        # For child classes to override

    def update(self):
        backend = self.imgui_backend
        glfw.poll_events()
        backend.process_inputs()

        imgui.new_frame()

        self.drawGUI()

        imgui.end_frame()

        gl.glClearColor(0.1, 0.1, 0.1, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        backend.render(imgui.get_draw_data())
        glfw.swap_buffers(self.glfw_window)

    @property
    def should_close(self):
        return glfw.window_should_close(self.glfw_window)

    def shutdownGUI(self):
        self.imgui_backend.shutdown()
        glfw.terminate()

    def impl_glfw_init(self, width, height):
        """Helper method to initialize GLFW context.
        Pretty much just copied from pyimgui example.
        """

        window_name = self.name

        if not glfw.init():
            print("Could not initialize OpenGL context")
            sys.exit(1)

        # OS X supports only forward-compatible core profiles from 3.2
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

        # Create a windowed mode window and its OpenGL context
        window = glfw.create_window(
            int(width), int(height), window_name, None, None)
        glfw.make_context_current(window)

        if not window:
            glfw.terminate()
            print("Could not initialize Window")
            sys.exit(1)

        return window
