from collections import deque
from threading import Thread
import time

import msgspec
import serial
from imgui_bundle import imgui, implot, imgui_ctx
from PotatoUI import MainInterface

from . import windows
from .shared.state import MESSAGE_TYPES, SensorState, FlightStats, Message
from .shared.xbee_interface import XbeeInterface


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
        self.xbee = XbeeInterface(serial_port_1, self.process_data)

        self.decoder = msgspec.msgpack.Decoder(MESSAGE_TYPES)
        self.encoder = msgspec.msgpack.Encoder()

        self.xbee.start()

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

    def process_data(self, data: MESSAGE_TYPES):
        if type(data) is Message:
            self.message_text.append(f"{data.message}\n")
            self.serial_window.just_updated = True

        elif type(data) is SensorState:
            self.state = data

        # Set the heartbeat since received from sail
        self.heartbeat = self.current_time

    def send_data(self, data: str):
        """
        Function to send data to both of the serial ports.
        Will append a semicolon at the end, so you don't need to add one ahead of time.
        Also updates the serial monitor.

        Args:
            data (str): Input data to send
        """
        self.xbee.send_data(Message(data))

        self.serial_window.just_updated = True
        self.serial_text.append(f"{data}\n")
        self.message_text.append(f"{data}\n")

    def shutdown_gui(self):
        self.xbee.stop()
        super().shutdown_gui()
        self.read_serial = False
