from collections import deque
from threading import Thread
import time

import msgspec
import serial
from imgui_bundle import imgui, implot, imgui_ctx
from PotatoUI import MainInterface

from . import windows
from .state import SensorState, FlightStats, Message


# class SpaceduckState(msgspec.Struct):
#     altitude: float = 0.0
#     velo_estimate: float = 0.0
#     motor_power: float = 0.0
#     temperature: float = 0.0


class SpaceduckInterface(MainInterface):

    MESSAGE_STORE_CAP = 100

    SERIAL_TIMEOUT_S = 2

    def __init__(
        self,
        name: str,
        width: int,
        height: int,
        serial_port_1: str,
        baudrate=9600,
        font_path=None,
        font_size=14,
        scaling_factor=1,
        **kwargs,
    ):
        """
        this is all probably over-complicated tbh
        """

        # Set up data storage
        self.state = SensorState()
        self.stats = FlightStats()
        self.heartbeat: float = 0.0
        self.start_time = time.time()
        self.current_time = 0.0

        super().__init__(
            name, width, height, font_path, font_size, scaling_factor, **kwargs
        )

        self.plot_context = implot.create_context()

        # Cool deque to store previously-received data for serial monitor
        self.serial_text = deque([], maxlen=self.MESSAGE_STORE_CAP)
        self.message_text = deque([], maxlen=self.MESSAGE_STORE_CAP)
        self.read_serial = True

        # Make the serial connections
        self.serial_1 = serial.Serial(
            serial_port_1, baudrate, timeout=self.SERIAL_TIMEOUT_S, write_timeout=0
        )
        self.listen_thread_1 = Thread(target=self.serial_listen, args=(self.serial_1,))

        self.decoder = msgspec.msgpack.Decoder(SensorState | Message)

        # Start da threads
        self.listen_thread_1.start()

    def setup_gui(self) -> None:
        self.serial_window = windows.SerialWindow(self.io, self)
        self.button_panel = windows.ButtonPanel(self.io, self)
        self.plot_window = windows.PlotWindow(self.io, self)
        # self.motor_debugger = windows.MotorTesterWindow(self.io, self)
        self.first = True

    def draw(self) -> None:
        # Draw the background logo and version stuff
        super().draw()

        self.current_time = time.time() - self.start_time

        display_size = self.io.display_size

        imgui.set_next_window_size((280, 500), imgui.Cond_.once)
        imgui.set_next_window_pos(
            (0 * display_size.x, 0.5 * display_size.y),
            imgui.Cond_.once,
            (0.0, 0.5),
        )
        node_id = imgui.get_id("dashboard_dockspace")
        with imgui_ctx.begin("Dashboard", flags=imgui.WindowFlags_.no_docking):
            imgui.dock_space(node_id, (0, 0))

        if self.first:
            imgui.internal.dock_builder_remove_node(node_id)
            imgui.internal.dock_builder_add_node(
                node_id, flags=imgui.DockNodeFlags_.no_docking_split
            )

            imgui.internal.dock_builder_dock_window("Motor Tester", node_id)
            imgui.internal.dock_builder_dock_window("Serial Console", node_id)
            imgui.internal.dock_builder_finish(node_id)
            self.first = False

        self.serial_window.draw_window()
        # self.motor_debugger.draw_window()

        imgui.set_next_window_pos(
            (1 * display_size.x, 0 * display_size.y),
            imgui.Cond_.always,
            (1.0, 0.0),
        )
        self.button_panel.draw_window()

        imgui.set_next_window_size((0.55 * display_size.x, -1), imgui.Cond_.always)
        imgui.set_next_window_pos(
            (0.5 * display_size.x, 0.04 * display_size.y),
            imgui.Cond_.always,
            (0.5, 0.0),
        )
        self.plot_window.draw_window()

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

    def process_data(self, data: bytes):
        decoded_data: Message | SensorState = self.decoder.decode(data)

        if type(decoded_data) is Message:
            self.message_text.append(f"{decoded_data.message}\n")
            self.serial_window.just_updated = True

        elif type(decoded_data) is SensorState:
            self.state = decoded_data

        # Set the heartbeat since received from sail
        self.heartbeat = self.current_time

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
                line = line.strip(eol)
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
        self.serial_1.write((data + ";").encode("ascii"))

        self.serial_window.just_updated = True
        self.serial_text.append(f"{data}\n")
        self.message_text.append(f"{data}\n")

    def shutdown_gui(self):
        super().shutdown_gui()
        self.read_serial = False
        self.serial_1.close()
