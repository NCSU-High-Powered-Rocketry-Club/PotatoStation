from collections import deque
from threading import Thread
import time

import serial
import imgui
from PotatoUI import MainInterface

from . import windows


class KrakenInterface(MainInterface):
    def __init__(self, name: str, width: int, height: int, serial_port: str, baudrate=9600, font_path=None, font_size=14, scaling_factor=1):
        super().__init__(name, width, height, font_path, font_size, scaling_factor)

        self.serial = serial.Serial(serial_port, baudrate, timeout=2)
        self.serial_text = deque([], maxlen=100)

        self.read_serial = True
        self.serial_thread = Thread(target=self.serial_listen)
        self.serial_thread.start()

        self.serial_window = windows.SerialWindow(self.io, self)
        self.button_panel = windows.ButtonPanel(self.io, self)

    def drawGUI(self):
        # Draw the background logo and version stuff
        super().drawGUI()

        display_size = self.io.display_size

        imgui.set_next_window_size(250, 400, imgui.ONCE)
        imgui.set_next_window_position(
            0 * display_size.x, 0.5 * display_size.y, imgui.ONCE, 0.0, 0.5)
        self.serial_window.drawWindow()

        imgui.set_next_window_position(
            1 * display_size.x, 0 * display_size.y, imgui.ALWAYS, 1.0, 0.0)
        self.button_panel.drawWindow()

    def serial_listen(self):
        """
        Listen thread for incoming data from the xbee/arduino

        To avoid all kinds of newline wackiness, we use semicolons to separate data.
        Since it's just a regular ascii character it's less prone to silliness from
        protocols and such

        """
        while self.read_serial:
            data = self._readline(self.serial, b";").decode(
                'ascii', errors="ignore")

            # Remove that semicolon
            data = data[:-1]

            # Do stuff with data
            if data != "":
                self.serial_text.append(f"{data}\n")
                self.serial_window.just_updated = True

            time.sleep(0.001)

    def _readline(self, serial: serial.Serial, eol: bytes) -> bytes:
        """
        Taken almost wholesale from 
        https://stackoverflow.com/questions/16470903/pyserial-2-6-specify-end-of-line-in-readline
        """

        leneol = len(eol)
        line = bytearray()
        while True:
            c = serial.read(1)
            if c:
                line += c
                if line[-leneol:] == eol:
                    break
            else:
                break
        return bytes(line)

    def send_data(self, data: str):
        """
        Function to send data to the serial port. 
        Will append a semicolon at the end, so you don't need to add one ahead of time.
        Also updates the serial monitor.

        Args:
            data (str): Input data to send
        """
        self.serial.write((data + ";").encode('ascii'))
        self.serial_window.just_updated = True
        self.serial_text.append(f"{data}\n")

    def shutdownGUI(self):
        super().shutdownGUI()
        self.read_serial = False
        self.serial_thread.join()
        self.serial.close()
