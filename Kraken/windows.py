from __future__ import annotations
from typing import TYPE_CHECKING
import time

import numpy as np
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise
import imgui
from PotatoUI import GUIWindow

if TYPE_CHECKING:
    from .interface import KrakenInterface


class SerialWindow(GUIWindow):

    def __init__(
        self,
        io: imgui._IO,
        interface: KrakenInterface,
        closable: bool = False,
        flags=None,
    ) -> None:
        super().__init__("Serial Console", io, closable, flags)
        self.interface = interface
        self.serial_input_text = ""
        self.just_sent = False
        self.just_updated = False
        self.just_updated_2 = False

        self.show_msg_stream = False

    def drawContents(self):

        with imgui.begin_tab_bar("SerialTabs") as tab_bar:
            with imgui.begin_tab_item("Messages") as msg:
                if msg.selected:
                    self.show_msg_stream = False
            with imgui.begin_tab_item("Stream") as strm:
                if strm.selected:
                    self.show_msg_stream = True

        with imgui.begin_child("##OldTextChild", height=-50, border=True):
            if self.show_msg_stream:
                imgui.text("".join(self.interface.serial_text))
            else:
                imgui.text("".join(self.interface.message_text))

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
            "##SerialEntry",
            "Send something (Enter)",
            self.serial_input_text,
            buffer_length=-1,
            flags=imgui.INPUT_TEXT_ENTER_RETURNS_TRUE,
        )

        if enter:
            self.just_sent = True

            self.interface.send_data(self.serial_input_text)
            self.serial_input_text = ""


class ButtonPanel(GUIWindow):

    HEART_RED_TIME_S = 2.0

    def __init__(
        self,
        io: imgui._IO,
        interface: KrakenInterface,
        closable: bool = False,
        flags=None,
    ) -> None:
        if flags is None:
            flags = 0

        flags |= imgui.WINDOW_ALWAYS_AUTO_RESIZE
        flags |= imgui.WINDOW_NO_BACKGROUND
        flags |= imgui.WINDOW_NO_DECORATION
        flags |= imgui.WINDOW_NO_MOVE
        flags |= imgui.WINDOW_NO_BRING_TO_FRONT_ON_FOCUS

        super().__init__("ButtonPanel", io, closable, flags)

        self.interface = interface
        self.armed = False

    def drawContents(self):
        state = self.interface.state

        imgui.dummy(200, -1)
        with imgui.font(self.interface.bigger_icon_font):

            sail_color = (
                (1.0, 0.0, 0.0)
                if (self.interface.current_time - state.sail_heartbeat)
                > self.HEART_RED_TIME_S
                else (0.0, 1.0, 0.0)
            )

            latch_color = (
                (1.0, 0.0, 0.0)
                if (self.interface.current_time - state.latch_heartbeat)
                > self.HEART_RED_TIME_S
                else (0.0, 1.0, 0.0)
            )

            imgui.text_colored("\ueae6", *sail_color)  # \uea6d
            imgui.same_line()
            imgui.text_colored("\ue915", *latch_color)

        if self.armed:
            color = (0.0, 1.0, 1.0)
        else:
            color = (1.0, 0.0, 0.0)

        imgui.text("Latch: ")
        imgui.same_line()
        if state.latch_open:
            imgui.text_colored("OPEN", 0.7, 0, 1.0)
        else:
            imgui.text_colored("CLOSED", 0.0, 1.0, 1.0)

        # imgui.separator()
        # imgui.dummy(-1, -1)

        imgui.text(f"Altitude: {state.altitude:.1f}m")
        imgui.text(f"Motor power: {state.motor_power:.1f}%")

        # imgui.separator()
        # imgui.dummy(-1, -1)

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

                with imgui.colored(imgui.COLOR_BUTTON_HOVERED, 0.9, 0.1, 0.0):
                    if imgui.button("KILL", -1):
                        imgui.open_popup("###kill-popup")
                imgui.same_line()
                with imgui.begin_popup_modal("###kill-popup") as kill_popup:
                    if kill_popup.opened:
                        imgui.text("Are you sure????")
                        if imgui.button("YESSS", -1):
                            self.interface.send_data("KILL")
                            imgui.close_current_popup()
                        if imgui.button("nah", -1):
                            imgui.close_current_popup()


class PlotWindow(GUIWindow):

    MAX_PLOT_VALUES = 700

    PLOT_UPDATE_TIME_S = 0.1

    def __init__(
        self,
        io: imgui._IO,
        interface: KrakenInterface,
        closable: bool = False,
        flags=None,
    ) -> None:
        if flags is None:
            flags = 0

        flags |= imgui.WINDOW_NO_BACKGROUND
        flags |= imgui.WINDOW_ALWAYS_AUTO_RESIZE
        flags |= imgui.WINDOW_NO_DECORATION
        # flags |= imgui.WINDOW_NO_BRING_TO_FRONT_ON_FOCUS

        super().__init__("Plot Window", io, closable, flags)
        self.interface = interface

        self.alt_data = np.zeros(self.MAX_PLOT_VALUES, dtype=np.float32)
        self.motor_data = np.zeros(self.MAX_PLOT_VALUES, dtype=np.float32)
        self.velo_estimates = np.zeros(self.MAX_PLOT_VALUES, dtype=np.float32)

        R, Q = 1.09, 0.89  # 0.09#0.08
        dt = self.PLOT_UPDATE_TIME_S

        kf = KalmanFilter(dim_x=2, dim_z=1)
        kf.x = np.zeros(2)
        kf.P *= np.array([[100, 0], [0, 1]])
        kf.R *= R
        kf.Q = Q_discrete_white_noise(2, dt, Q)
        kf.F = np.array([[1.0, dt], [0.0, 1]])
        kf.H = np.array([[1.0, 0]])
        kf.alpha = 1.215

        self.kalman_filter = kf

        self.offset_index = 0
        self.num_values = 0

        self.last_graph_update = interface.current_time

    def update_data(self):
        if self.offset_index == self.MAX_PLOT_VALUES:
            self.offset_index = 0

        self.alt_data[self.offset_index] = self.interface.state.altitude
        self.motor_data[self.offset_index] = self.interface.state.motor_power

        self.kalman_filter.predict()
        self.kalman_filter.update(self.interface.state.altitude)

        self.velo_estimates[self.offset_index] = self.kalman_filter.x[1]

        self.offset_index += 1

        if self.num_values < self.MAX_PLOT_VALUES:
            self.num_values += 1

    def drawContents(self):
        if (
            self.interface.current_time - self.last_graph_update
        ) > self.PLOT_UPDATE_TIME_S:
            self.update_data()
            self.last_graph_update = self.interface.current_time

        max_width = imgui.get_content_region_available_width()
        imgui.plot_lines(
            "##Altitude",
            self.alt_data,
            overlay_text="Altitude",
            scale_min=0,
            values_offset=self.offset_index,
            values_count=self.num_values,
            graph_size=(max_width, 150),
        )

        imgui.plot_lines(
            "##Velocity",
            self.velo_estimates,
            overlay_text="Velocity Estimate",
            values_offset=self.offset_index,
            values_count=self.num_values,
            graph_size=(max_width, 150),
        )

        imgui.plot_lines(
            "##MotorPower",
            self.motor_data,
            overlay_text="Motor Power",
            scale_min=0,
            values_offset=self.offset_index,
            values_count=self.num_values,
            graph_size=(max_width, 150),
            scale_max=100,
        )


class MotorTesterWindow(GUIWindow):
    def __init__(
        self,
        io: imgui._IO,
        interface: KrakenInterface,
        closable: bool = False,
        flags=None,
    ) -> None:
        if flags is None:
            flags = 0

        super().__init__("Motor test window", io, closable, flags)
        self.interface = interface
        self.current_motor_pwr_send = 0

    def drawContents(self):
        imgui.text("Set motor power:")
        _, self.current_motor_pwr_send = imgui.slider_int(
            "###Power", self.current_motor_pwr_send, 0, 100
        )

        if imgui.button("Set motor power", -1):
            self.interface.send_data(f"DMTR {self.current_motor_pwr_send}")
