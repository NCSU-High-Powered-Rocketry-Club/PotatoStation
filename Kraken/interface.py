from collections import deque
from threading import Thread
import time

import msgspec
import serial
import imgui
from PotatoUI import MainInterface

from . import windows


class KrakenState(msgspec.Struct):
    altitude: float = 0.0
    motor_power: float = 0.0
    latch_open: bool = False
    latch_heartbeat: float = 0.0
    sail_heartbeat: float = 0.0


class KrakenInterface(MainInterface):

    MESSAGE_STORE_CAP = 100

    SERIAL_TIMEOUT_S = 2

    def __init__(self, name: str, width: int, height: int, serial_port_1, serial_port_2=None,
                 baudrate=9600, font_path=None, font_size=14, scaling_factor=1, **kwargs):
        """
        this is all probably over-complicated tbh
        """

        super().__init__(name, width, height, font_path, font_size, scaling_factor, **kwargs)

        # Cool deque to store previously-received data for serial monitor
        self.serial_text = deque([], maxlen=self.MESSAGE_STORE_CAP)
        self.message_text = deque([], maxlen=self.MESSAGE_STORE_CAP)
        self.read_serial = True

        # Make the serial connections
        self.serial_1 = serial.Serial(
            serial_port_1, baudrate, timeout=self.SERIAL_TIMEOUT_S, write_timeout=0)

        self.has_serial_2 = serial_port_2 is not None

        if self.has_serial_2:
            self.serial_2 = serial.Serial(
                serial_port_2, baudrate, timeout=self.SERIAL_TIMEOUT_S, write_timeout=0)

        # Make two threads to listen to incoming data
        self.listen_thread_1 = Thread(
            target=self.serial_listen,
            args=(self.serial_1,)
        )

        if self.has_serial_2:
            self.listen_thread_2 = Thread(
                target=self.serial_listen,
                args=(self.serial_2,)
            )

        # Set up data storage
        self.state = KrakenState()
        self.current_time = time.time()

        # Start da threados
        self.listen_thread_1.start()

        if serial_port_2:
            self.listen_thread_2.start()

        self.serial_window = windows.SerialWindow(self.io, self)
        self.button_panel = windows.ButtonPanel(self.io, self)
        self.plot_window = windows.PlotWindow(self.io, self)

    def drawGUI(self):
        # Draw the background logo and version stuff
        super().drawGUI()

        self.current_time = time.time()

        display_size = self.io.display_size

        imgui.set_next_window_size(250, 400, imgui.ONCE)
        imgui.set_next_window_position(
            0 * display_size.x, 0.5 * display_size.y, imgui.ONCE, 0.0, 0.5)
        self.serial_window.drawWindow()

        imgui.set_next_window_position(
            1 * display_size.x, 0 * display_size.y, imgui.ALWAYS, 1.0, 0.0)
        self.button_panel.drawWindow()

        imgui.set_next_window_size(0.55 * display_size.x, -1, imgui.ALWAYS)
        imgui.set_next_window_position(
            0.5 * display_size.x, 0.04 * display_size.y, imgui.ALWAYS, 0.5, 0.0)
        self.plot_window.drawWindow()

    def serial_listen(self, serial_conn: serial.Serial):
        """
        Listen thread for incoming data from the xbee/arduino

        To avoid all kinds of newline wackiness, we use semicolons to separate data.
        Since it's just a regular ascii character it's less prone to silliness from
        protocols and such

        """
        while self.read_serial:
            data = self._readline(serial_conn, b";")

            if data == b"":
                continue

            if data == b";":
                continue

            # Echoing disabled as this is not needed atm
            # # Echo to the other serial (so the latch and SAIL both receive stuff the other sent)
            # if serial_conn is self.serial_1:
            #     self.serial_2.write(data)
            # else:
            #     self.serial_1.write(data)

            data = data.decode('ascii', errors="ignore")

            # Remove the semicolon
            data = data[:-1]

            # Do stuff with data
            self.serial_text.append(f"{data}\n")
            self.serial_window.just_updated = True
            try:
                self.process_data(data)
            except Exception as e:
                print(e)
                print(f"Error on processing data {data}")

            # Avoid hogging thread time
            time.sleep(0.0001)

    def process_data(self, data: str):
        if data.startswith("ALT "):
            alt = float(data.split()[1])
            self.state.altitude = alt
            # Set the heartbeat since received from sail
            self.state.sail_heartbeat = self.current_time

        elif data.startswith("MOTOR "):
            power = float(data.split()[1])
            self.state.motor_power = power
            # Set the heartbeat since received from sail
            self.state.sail_heartbeat = self.current_time

        elif data.startswith("LATCH "):
            latch_state = int(data.split()[1])
            self.state.latch_open = (latch_state == 1)
            self.state.latch_heartbeat = self.current_time

        elif data.startswith("MSG "):
            self.message_text.append(f"{data[4:]}\n")
            self.serial_window.just_updated = True

    def _readline(self, serial: serial.Serial, eol: bytes) -> bytes:
        """
        Taken almost wholesale from 
        https://stackoverflow.com/questions/16470903/pyserial-2-6-specify-end-of-line-in-readline

        Modified so it actually blocks until fully read incoming data rather than receiving a
        half-finished string because the incoming stream paused
        """

        leneol = len(eol)
        line = bytearray()
        while self.read_serial:
            c = serial.read(1)
            line += c
            if line[-leneol:] == eol:
                break

        return bytes(line)

    def send_data(self, data: str):
        """
        Function to send data to both of the serial ports. 
        Will append a semicolon at the end, so you don't need to add one ahead of time.
        Also updates the serial monitor.

        Args:
            data (str): Input data to send
        """
        self.serial_1.write((data + ";").encode('ascii'))
        if self.has_serial_2:
            self.serial_2.write((data + ";").encode('ascii'))

        self.serial_window.just_updated = True
        self.serial_text.append(f"{data}\n")
        self.message_text.append(f"{data}\n")

    def shutdownGUI(self):
        super().shutdownGUI()
        self.read_serial = False
        self.serial_1.close()
        if self.has_serial_2:
            self.serial_2.close()
