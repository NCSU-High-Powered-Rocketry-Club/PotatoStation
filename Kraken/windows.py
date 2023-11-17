from __future__ import annotations
from typing import TYPE_CHECKING

import imgui
from PotatoUI import GUIWindow

if TYPE_CHECKING:
    from .interface import KrakenInterface


class SerialWindow(GUIWindow):

    def __init__(self, io: imgui._IO, gui: KrakenInterface, closable: bool = False, flags=None) -> None:
        super().__init__("Serial Console", io, closable, flags)
        self.gui = gui
        self.serial_input_text = ""
        self.just_sent = False
        self.just_updated = False

    def drawWindow(self):
        imgui.set_next_window_size(250, 400, imgui.ONCE)
        super().drawWindow()

    def drawContents(self):
        with imgui.begin_child("##OldTextChild", height=-50, border=True):
            imgui.text("".join(self.gui.serial_text))

            if self.just_updated:
                imgui.set_scroll_y(imgui.get_scroll_max_y())
                self.just_updated = False

        if self.just_sent:
            imgui.set_keyboard_focus_here()
            self.just_sent = False
            self.just_updated = True

        imgui.push_item_width(-1)
        enter, self.serial_input_text = imgui.input_text_with_hint(
            "##SerialEntry", "Send something (Enter)", self.serial_input_text, flags=imgui.INPUT_TEXT_ENTER_RETURNS_TRUE)

        if enter:
            self.just_sent = True
            self.gui.serial_text.append(self.serial_input_text+"\n")
            self.serial_input_text = ""

        pass
        # TODO: Add enter button and send to pyserial
