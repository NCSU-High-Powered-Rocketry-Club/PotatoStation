import glfw
from OpenGL import GL as gl
from imgui_bundle import imgui
from imgui_bundle.python_backends.glfw_backend import GlfwRenderer
import sys
import time


class GLFWImguiWrapper:
    def __init__(
        self,
        name: str,
        width: int,
        height: int,
        font_path=None,
        font_size=14,
        scaling_factor=1,
        framerate=70,
        fullscreen=False,
    ):
        self.name = name
        self.fullscreen = fullscreen
        self.create_backend(width, height, fullscreen)

        self.io = self.imgui_backend.io
        self.io.config_flags |= imgui.ConfigFlags_.docking_enable
        self.framerate = framerate

        self.setup_main_font(font_path, font_size, scaling_factor)

        self.setup_gui()

    def create_backend(self, width, height, fullscreen):
        self.context = imgui.create_context()
        imgui.set_current_context(self.context)
        self.glfw_window = self.impl_glfw_init(width, height, fullscreen)
        self.imgui_backend = GlfwRenderer(self.glfw_window)

    def setup_main_font(
        self, font_path: str | None, font_size: int, scaling_factor: int = 1
    ):
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
            path, self.font_scaling_factor * font_size_in_pixels, *args, **kwargs
        )
        self.imgui_backend.refresh_font_texture()
        return newFont

    def setup_gui(self) -> None:
        # For child classes to override
        raise NotImplementedError

    def draw(self) -> None:
        # For child classes to override
        raise NotImplementedError

    def update_gui(self):
        backend = self.imgui_backend
        imgui.set_current_context(self.context)

        # Update inputs like mouse/keyboard
        glfw.poll_events()
        backend.process_inputs()

        smooth_scroll_speed = 8.0
        scroll_amount = 1.0
        scroll_energy = 0.0
        self.io.mouse_wheel *= scroll_amount  # Scroll multiplier / amount

        # Smooth scrolling
        scroll_energy += self.io.mouse_wheel
        if abs(scroll_energy) > 0.1:  # Scrolling threshold
            scroll_now = scroll_energy * self.io.delta_time * smooth_scroll_speed
            scroll_energy -= scroll_now
        else:
            scroll_now = 0.0
            scroll_energy = 0.0
        self.io.mouse_wheel = scroll_now

        imgui.new_frame()

        self.draw()

        imgui.end_frame()

        gl.glClearColor(0.1, 0.1, 0.1, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        backend.render(imgui.get_draw_data())
        glfw.swap_buffers(self.glfw_window)
        time.sleep(1.0 / self.framerate)

    @property
    def should_close(self):
        return glfw.window_should_close(self.glfw_window)

    def shutdown_gui(self):
        self.imgui_backend.shutdown()
        glfw.terminate()

    def impl_glfw_init(self, width: int, height: int, fullscreen: bool):
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
        if not fullscreen:
            # Create a windowed mode window and its OpenGL context
            window = glfw.create_window(
                int(width), int(height), window_name, None, None
            )

        else:
            glfw.window_hint(glfw.DECORATED, gl.GL_FALSE)

            monitor = glfw.get_primary_monitor()
            mode = glfw.get_video_mode(monitor)
            # Create a windowed mode window and its OpenGL context
            window = glfw.create_window(
                int(mode.size.width), int(mode.size.height), window_name, None, None
            )

        glfw.make_context_current(window)

        if not window:
            glfw.terminate()
            print("Could not initialize Window")
            sys.exit(1)

        return window

    def set_scale(self, scale: float) -> None:
        imgui.get_style().scale_all_sizes(scale)
