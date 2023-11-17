from collections import deque
from threading import Thread
import time

import serial
from PotatoUI import MainInterface

from . import windows


# TODO: add com port parameter
class KrakenInterface(MainInterface):
    def __init__(self, name: str, width: int, height: int, serial_port: str, baudrate=9600, font_path=None, font_size=14, scaling_factor=1):
        super().__init__(name, width, height, font_path, font_size, scaling_factor)

        self.serial = serial.Serial(serial_port, baudrate, timeout=2)
        self.serial_text = deque([], maxlen=100)

        self.read_serial = True
        self.serial_thread = Thread(target=self.serial_listen)
        self.serial_thread.start()

        self.serial_window = windows.SerialWindow(self.io, self)
        self.big_button = windows.MassiveButton(self.io, self)

    def drawGUI(self):
        # Draw the background logo and version stuff
        super().drawGUI()

        self.serial_window.drawWindow()
        self.big_button.drawWindow()

    def serial_listen(self):

        while self.read_serial:
            data = self.serial.readline().decode('ascii', errors="ignore")

            # Do stuff with data
            if data != "":
                self.serial_text.append(data)
                self.serial_window.just_updated = True

            time.sleep(0.001)

    def shutdownGUI(self):
        super().shutdownGUI()
        self.read_serial = False
        self.serial_thread.join()
