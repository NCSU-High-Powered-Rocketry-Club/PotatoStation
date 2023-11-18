from importlib import resources as impresource
import platform

from .ui_utils.wrapper import GLFWImguiWrapper
from .ui_utils.gui_style import styleGUI
from .ui_utils import widgets

import imgui


class MainInterface(GLFWImguiWrapper):

    def __init__(self, name: str, width: int, height: int, font_path=None, font_size=14, scaling_factor=1):
        super().__init__(name, width, height, font_path, font_size, scaling_factor)

        # Enable moving around with the keyboard
        self.io.config_flags |= imgui.CONFIG_NAV_ENABLE_KEYBOARD
        self.io.ini_file_name = "".encode()

        resources = impresource.files(__package__)

        style_file = str(resources.joinpath('styles', 'dark_style.toml'))

        styleGUI(style_file)

        if font_path is None:
            font_path = str(resources.joinpath('fonts', 'main.ttf'))

        self.setup_main_font(font_path, font_size, scaling_factor)

        icon_font_path = str(resources.joinpath('fonts', 'icons.ttf'))
        custom_glyph_start = ord("\ue900")
        custom_glyph_end = ord("\uEAEE")
        custom_glyph_range = imgui.GlyphRanges(
            [custom_glyph_start, custom_glyph_end, 0])

        config = imgui.core.FontConfig(merge_mode=False)

        self.icon_font = self.add_extra_font(
            icon_font_path, font_size*1.3, font_config=config, glyph_ranges=custom_glyph_range)

        self.bigger_icon_font = self.add_extra_font(
            icon_font_path, font_size*6.5, font_config=config, glyph_ranges=custom_glyph_range)

        rocket_logo_path = str(
            resources.joinpath('assets', 'gray_rocket_logo.png'))

        self.rocket_logo = widgets.BackgroundImage(rocket_logo_path)
        rocket_scale = 0.3  # (height/self.rocket_logo.image.height) * 0.01
        self.rocket_logo.setScale(rocket_scale, rocket_scale)

        self.python_version = platform.python_version()

    def drawGUI(self):
        display_size = self.io.display_size

        rocket_width = self.rocket_logo.image.width * \
            self.rocket_logo.scale[0]
        rocket_height = self.rocket_logo.image.height * \
            self.rocket_logo.scale[1]

        self.rocket_logo.setImagePosition(
            (display_size.x / 2) - (rocket_width*0.5),
            (display_size.y / 2) - (rocket_height*0.5)
        )

        self.rocket_logo.draw()
        # imgui.show_test_window()

        version_flags = imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_DECORATION | imgui.WINDOW_NO_INPUTS
        version_flags |= imgui.WINDOW_NO_BACKGROUND | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_NAV

        imgui.set_next_window_position(
            display_size.x, display_size.y, pivot_x=1.0, pivot_y=1.0)

        with imgui.begin("##PotatoUIFlavorText", flags=version_flags):
            imgui.push_style_color(imgui.COLOR_TEXT, 0.2, 0.2, 0.2, 1.0)
            imgui.text(
                f"PotatoStation by Aman on Python {self.python_version} :)")
            imgui.pop_style_color()
