from importlib import resources as impresource
import platform

from .ui_utils.imgui_wrapper import GLFWImguiWrapper
from .ui_utils.gui_style import style_gui_from_file
from .ui_utils import widgets

from imgui_bundle import imgui
from imgui_bundle import imgui_ctx

import glfw
from PIL import Image


class MainInterface(GLFWImguiWrapper):

    def __init__(
        self,
        name: str,
        width: int,
        height: int,
        font_path=None,
        font_size=14,
        scaling_factor=1,
        **kwargs,
    ):
        super().__init__(
            name, width, height, font_path, font_size, scaling_factor, **kwargs
        )

        # Enable moving around with the keyboard
        self.io.config_flags |= imgui.ConfigFlags_.nav_enable_keyboard
        self.io.set_ini_filename("")

        resources = impresource.files(__package__)

        icon = Image.open(resources.joinpath("assets", "icon.png"))

        glfw.set_window_icon(self.glfw_window, 1, icon)

        style_file = str(resources.joinpath("styles", "dark_style.toml"))

        style_gui_from_file(style_file)

        if font_path is None:
            font_path = str(resources.joinpath("fonts", "main.ttf"))

        self.setup_main_font(font_path, font_size, scaling_factor)

        icon_font_path = str(resources.joinpath("fonts", "icons.ttf"))
        icons_start = ord("\ue900")
        icons_end = ord("\uEAEE")
        icon_glyph_range = [icons_start, icons_end]

        self.icon_font = self.add_extra_font(
            icon_font_path,
            font_size * 1.3,
            glyph_ranges_as_int_list=icon_glyph_range,
        )

        self.bigger_icon_font = self.add_extra_font(
            icon_font_path,
            font_size * 6.5,
            glyph_ranges_as_int_list=icon_glyph_range,
        )

        self.io.config_docking_no_split = True
        self.io.config_windows_resize_from_edges = True

        rocket_logo_path = str(resources.joinpath("assets", "gray_rocket_logo.png"))

        self.rocket_logo = widgets.BackgroundImage(rocket_logo_path)
        rocket_scale = 0.3  # (height/self.rocket_logo.image.height) * 0.01
        self.rocket_logo.set_scale(rocket_scale, rocket_scale)

        self.python_version = platform.python_version()

    def setup_gui(self) -> None:
        # Override this method and add setup code here!
        pass

    def draw(self):
        display_size = self.io.display_size

        rocket_width = self.rocket_logo.image.width * self.rocket_logo.scale[0]
        rocket_height = self.rocket_logo.image.height * self.rocket_logo.scale[1]

        self.rocket_logo.set_image_position(
            (display_size.x / 2) - (rocket_width * 0.5),
            (display_size.y / 2) - (rocket_height * 0.5),
        )

        self.rocket_logo.draw()
        # imgui.show_test_window()

        version_flags = (
            imgui.WindowFlags_.always_auto_resize | imgui.WindowFlags_.no_decoration
        )
        version_flags |= imgui.WindowFlags_.no_background | imgui.WindowFlags_.no_move

        imgui.set_next_window_pos(
            (display_size.x, display_size.y), imgui.Cond_.always, (1.0, 1.0)
        )
        with imgui_ctx.begin("##PotatoUIFlavorText", flags=version_flags):
            imgui.push_style_color(imgui.Col_.text, (0.2, 0.2, 0.2, 1.0))
            imgui.text(f"PotatoStation by Aman on Python {self.python_version} :)")
            imgui.pop_style_color()
            if self.fullscreen:
                imgui.same_line()
                if imgui.button("Exit"):
                    glfw.set_window_should_close(self.glfw_window, True)
