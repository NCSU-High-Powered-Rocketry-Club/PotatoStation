from collections import deque

import imgui
from PotatoUI import MainInterface

from . import windows


# TODO: add com port parameter
class KrakenInterface(MainInterface):
    def __init__(self, name: str, width: int, height: int, font_path=None, font_size=14, scaling_factor=1):
        super().__init__(name, width, height, font_path, font_size, scaling_factor)

        self.serial_text = deque([], maxlen=100)
        self.serial_window = windows.SerialWindow(self.io, self)

    def drawGUI(self):
        # Draw the background logo and version stuff
        super().drawGUI()

        self.serial_window.drawWindow()

    def serial_listen_thread():
        pass
