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
        self.just_updated_2 = False

    def drawWindow(self):
        imgui.set_next_window_size(250, 400, imgui.ONCE)
        super().drawWindow()

    def drawContents(self):
        with imgui.begin_child("##OldTextChild", height=-50, border=True):
            imgui.text("".join(self.gui.serial_text))

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
            data = self.serial_input_text+"\n"
            self.gui.serial_text.append(data)
            self.gui.serial.write(self.serial_input_text.encode('ascii'))

            self.serial_input_text = ""


class MassiveButton(GUIWindow):
    def __init__(self, io: imgui._IO, gui: KrakenInterface, closable: bool = True, flags=None) -> None:
        super().__init__("BUTTON", io, closable, flags)
        self.pushed = False
        self.gui = gui

    def drawContents(self):
        self.pushed = imgui.button("PRESSA DA BUTTON", 200, 200)

        if self.pushed:
            self.gui.serial.write("a".encode('ascii'))
            self.gui.serial_window.just_sent = True
            self.gui.serial_text.append("a\n")
