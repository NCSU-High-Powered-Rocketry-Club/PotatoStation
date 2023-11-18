from __future__ import annotations
from typing import TYPE_CHECKING

import imgui
from PotatoUI import GUIWindow

if TYPE_CHECKING:
    from .interface import KrakenInterface


class SerialWindow(GUIWindow):

    def __init__(self, io: imgui._IO, interface: KrakenInterface, closable: bool = False, flags=None) -> None:
        super().__init__("Serial Console", io, closable, flags)
        self.interface = interface
        self.serial_input_text = ""
        self.just_sent = False
        self.just_updated = False
        self.just_updated_2 = False

    def drawContents(self):
        with imgui.begin_child("##OldTextChild", height=-50, border=True):
            imgui.text("".join(self.interface.serial_text))

            if self.just_updated_2:
                imgui.set_scroll_y(imgui.get_scroll_max_y())
                self.just_updated_2 = False

        if self.just_sent:
            imgui.set_keyboard_focus_here()
            self.just_sent = False
            self.just_updated = True

        if self.just_updated:
            self.just_updated = False
            self.just_updated_2 = True

        imgui.push_item_width(-1)
        enter, self.serial_input_text = imgui.input_text_with_hint(
            "##SerialEntry", "Send something (Enter)", self.serial_input_text, flags=imgui.INPUT_TEXT_ENTER_RETURNS_TRUE)

        if enter:
            self.just_sent = True

            self.interface.send_data(self.serial_input_text)
            self.serial_input_text = ""


class ButtonPanel(GUIWindow):
    def __init__(self, io: imgui._IO, interface: KrakenInterface, closable: bool = False, flags=None) -> None:
        if flags is None:
            flags = 0

        flags |= imgui.WINDOW_ALWAYS_AUTO_RESIZE
        flags |= imgui.WINDOW_NO_BACKGROUND
        flags |= imgui.WINDOW_NO_DECORATION

        super().__init__("ButtonPanel", io, closable, flags)
        self.pushed = False
        self.interface = interface
        self.armed = False

    def drawContents(self):
        self.pushed = imgui.button("PRESSA DA BUTTON", 200, 200)

        if self.pushed:
            self.interface.send_data("a")

        if self.armed:
            color = (0.0, 1.0, 1.0)
        else:
            color = (1.0, 0.0, 0.0)

        imgui.align_text_to_frame_padding()
        imgui.text("Status: ")
        imgui.same_line()
        with imgui.colored(imgui.COLOR_TEXT, *color):
            if self.armed:
                imgui.text("ARMED")
            else:
                imgui.text("DISARMED")

            if self.armed:
                with imgui.font(self.interface.icon_font):
                    arm = imgui.button("\uea48###ArmButton", -1)
            else:
                with imgui.font(self.interface.icon_font):
                    arm = imgui.button("\ueaa1###ArmButton", -1)

            if arm:
                self.armed = not self.armed

            if self.armed:
                with imgui.font(self.interface.bigger_icon_font):
                    deploy = imgui.button("\ue9b9###DeployButton", 200, 200)
                    if deploy:
                        self.interface.send_data("deploy")
