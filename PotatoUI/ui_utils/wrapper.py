import imgui
from .widgets import GUIWindow
from imgui.integrations.glfw import GlfwRenderer
import glfw
from OpenGL import GL as gl
import sys
import math
import time


class GLFWImguiWrapper:
    def __init__(self, name: str, width: int, height: int, font_path=None, font_size=14,
                 scaling_factor=1, framerate=70, fullscreen=False):
        self.name = name

        self.glfw_window = self.impl_glfw_init(width, height, fullscreen)
        self.imgui_context = imgui.create_context()

        self.imgui_backend = GlfwRenderer(self.glfw_window)
        self.io: imgui._IO = imgui.get_io()
        self.framerate = framerate

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
        time.sleep(1.0/self.framerate)

    @property
    def should_close(self):
        return glfw.window_should_close(self.glfw_window)

    def shutdownGUI(self):
        self.imgui_backend.shutdown()
        glfw.terminate()

    def impl_glfw_init(self, width, height, fullscreen):
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

        if not fullscreen:
            # Create a windowed mode window and its OpenGL context
            window = glfw.create_window(
                int(width), int(height), window_name, None, None)

        else:
            glfw.window_hint(glfw.DECORATED, gl.GL_FALSE)

            monitor = glfw.get_primary_monitor()
            mode = glfw.get_video_mode(monitor)
            # Create a windowed mode window and its OpenGL context
            window = glfw.create_window(
                int(mode.size.width), int(mode.size.height), window_name, None, None)

        glfw.make_context_current(window)

        if not window:
            glfw.terminate()
            print("Could not initialize Window")
            sys.exit(1)

        return window

    def _imgui_scale_all_sizes(self, style, hscale: float, vscale: float) -> None:
        """pyimgui is missing ImGuiStyle::ScaleAllSizes(); this is a reimplementation of it."""

        scale = max(hscale, vscale)

        def scale_it(attrname):
            value = getattr(style, attrname)
            if isinstance(value, imgui.Vec2):
                value = imgui.Vec2(math.trunc(value.x * hscale),
                                   math.trunc(value.y * vscale))
                setattr(style, attrname, value)
            else:
                setattr(style, attrname, math.trunc(value * scale))

        scale_it("window_padding")
        scale_it("window_rounding")
        scale_it("window_min_size")
        scale_it("child_rounding")
        scale_it("popup_rounding")
        scale_it("frame_padding")
        scale_it("frame_rounding")
        scale_it("item_spacing")
        scale_it("item_inner_spacing")
        scale_it("cell_padding")
        scale_it("touch_extra_padding")
        scale_it("indent_spacing")
        scale_it("columns_min_spacing")
        scale_it("scrollbar_size")
        scale_it("scrollbar_rounding")
        scale_it("grab_min_size")
        scale_it("grab_rounding")
        scale_it("log_slider_deadzone")
        scale_it("tab_rounding")
        scale_it("tab_min_width_for_close_button")
        # scale_it("separator_text_padding")  # not present in current pyimgui
        scale_it("display_window_padding")
        scale_it("display_safe_area_padding")
        scale_it("mouse_cursor_scale")
