from __future__ import annotations
from typing import TYPE_CHECKING
import time
import numpy as np

from imgui_bundle import imgui
from imgui_bundle import imgui_ctx
from imgui_bundle import implot

from PotatoUI import GUIWindow

if TYPE_CHECKING:
    from .interface import SpaceduckInterface


class SerialWindow(GUIWindow):

    def __init__(
        self,
        io: imgui._IO,
        interface: SpaceduckInterface,
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

    def draw_contents(self):

        with imgui_ctx.begin_tab_bar("SerialTabs") as tab_bar:
            with imgui_ctx.begin_tab_item("Messages") as msg:
                if msg.visible:
                    self.show_msg_stream = False
            with imgui_ctx.begin_tab_item("Stream") as strm:
                if strm.visible:
                    self.show_msg_stream = True

        with imgui_ctx.begin_child(
            "##TextDisplayArea", (0, -50), child_flags=imgui.ChildFlags_.border
        ):
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
            flags=imgui.InputTextFlags_.enter_returns_true,
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
        interface: SpaceduckInterface,
        closable: bool = False,
        flags=None,
    ) -> None:
        if flags is None:
            flags = 0

        flags |= imgui.WindowFlags_.always_auto_resize
        flags |= imgui.WindowFlags_.no_background
        flags |= imgui.WindowFlags_.no_decoration
        flags |= imgui.WindowFlags_.no_move
        flags |= imgui.WindowFlags_.no_bring_to_front_on_focus

        super().__init__("ButtonPanel", io, closable, flags)

        self.interface = interface
        self.armed = False

    def draw_contents(self):
        state = self.interface.state

        imgui.dummy((200, -1))
        with imgui_ctx.push_font(self.interface.bigger_icon_font):

            duck_color = (
                (1.0, 0.0, 0.0)
                if (self.interface.current_time - self.interface.heartbeat)
                > self.HEART_RED_TIME_S
                else (0.0, 1.0, 0.0)
            )

            # latch_color = (
            #     (1.0, 0.0, 0.0)
            #     if (self.interface.current_time - state.latch_heartbeat)
            #     > self.HEART_RED_TIME_S
            #     else (0.0, 1.0, 0.0)
            # )
            icon_text = "\ue9c5"  # "\ueae6"
            window_width = imgui.get_window_width()
            text_width = imgui.calc_text_size(icon_text).x
            imgui.set_cursor_pos_x((window_width - text_width) * 0.5)
            imgui.text_colored(imgui.ImVec4(*duck_color, 1.0), icon_text)  # \uea6d
            # imgui.text_colored("\ue915", *latch_color)

        if self.armed:
            color = (0.0, 1.0, 1.0)
        else:
            color = (1.0, 0.0, 0.0)

        # imgui.text("Latch: ")
        # imgui.same_line()
        # if state.latch_open:
        #     imgui.text_colored("OPEN", 0.7, 0, 1.0)
        # else:
        #     imgui.text_colored("CLOSED", 0.0, 1.0, 1.0)

        # imgui.separator()
        # imgui.dummy(-1, -1)

        imgui.text(f"Altitude: {state.altitude:.1f}m")
        imgui.text(f"Accel: {state.acceleration}")
        imgui.text(f"Orient: {state.orientation}")
        imgui.text(f"Temperature: {state.temperature:.1f} \u00B0C")

        # imgui.separator()
        # imgui.dummy(-1, -1)

        imgui.text("Status: ")
        imgui.same_line()

        with imgui_ctx.push_style_color(imgui.Col_.text, imgui.ImVec4(*color, 1.0)):
            if self.armed:
                imgui.text("ARMED")
            else:
                imgui.text("DISARMED")

            if self.armed:
                with imgui_ctx.push_font(self.interface.icon_font):
                    arm = imgui.button("\uea48###ArmButton", (-1, 0))
            else:
                with imgui_ctx.push_font(self.interface.icon_font):
                    arm = imgui.button("\ueaa1###ArmButton", (-1, 0))

            if arm:
                self.armed = not self.armed

            if self.armed:
                with imgui_ctx.push_font(self.interface.bigger_icon_font):
                    transmit = imgui.button("\uea83###TransmitButton", (200, 200))
                    if transmit:
                        self.interface.send_data("transmit")

                if imgui.button("Echo"):
                    self.interface.send_data("echo")
                imgui.same_line()
                if imgui.button("Transmit Now"):
                    self.interface.send_data("!transmitnow")
                if imgui.button("Switch to recover state (shutdown)"):
                    self.interface.send_data("!recover")


class PlotWindow(GUIWindow):

    MAX_PLOT_VALUES = 600

    PLOT_UPDATE_TIME_S = 0.1

    def __init__(
        self,
        io: imgui._IO,
        interface: SpaceduckInterface,
        closable: bool = False,
        flags=None,
    ) -> None:
        if flags is None:
            flags = 0

        flags |= imgui.WindowFlags_.no_background
        flags |= imgui.WindowFlags_.always_auto_resize
        flags |= imgui.WindowFlags_.no_decoration

        super().__init__("Plot Window", io, closable, flags)
        self.interface = interface

        self.time_data = np.zeros(self.MAX_PLOT_VALUES, dtype=np.float32)
        self.alt_data = np.zeros(self.MAX_PLOT_VALUES, dtype=np.float32)

        self.accel_data = np.zeros(self.MAX_PLOT_VALUES, dtype=np.float32)
        self.temp_data = np.zeros(self.MAX_PLOT_VALUES, dtype=np.float32)

        self.offset_index = 0
        self.num_values = 0

        self.last_graph_update = interface.current_time

    def update_data(self):
        if self.offset_index == self.MAX_PLOT_VALUES:
            self.offset_index = 0

        self.time_data[self.offset_index] = self.interface.current_time
        self.alt_data[self.offset_index] = self.interface.state.altitude

        self.accel_data[self.offset_index] = np.sqrt(
            np.sum(np.asarray(self.interface.state.acceleration) ** 2)
        )
        self.temp_data[self.offset_index] = self.interface.state.temperature

        self.offset_index += 1

        if self.num_values < self.MAX_PLOT_VALUES:
            self.num_values += 1

    def draw_contents(self):
        time_since_update = self.interface.current_time - self.last_graph_update

        if time_since_update > self.PLOT_UPDATE_TIME_S:
            self.update_data()
            self.last_graph_update = self.interface.current_time

        max_width = imgui.get_content_region_avail().x

        axis_flags = implot.AxisFlags_.auto_fit
        plot_flags = implot.Flags_.crosshairs

        implot.push_style_color(implot.Col_.plot_bg, (0, 0, 0, 0.1))
        implot.push_style_color(implot.Col_.frame_bg, (0, 0, 0, 0.1))
        implot.push_style_var(implot.StyleVar_.fill_alpha, 0.35)

        if implot.begin_plot("###AltitudeVeloPlot", flags=plot_flags):
            implot.setup_axes("", "", axis_flags, axis_flags)
            implot.plot_shaded(
                "Altitude",
                self.time_data,
                self.alt_data,
                offset=self.offset_index,
            )

            implot.plot_line(
                "Acceleration",
                self.time_data,
                self.accel_data,
                offset=self.offset_index,
            )

            implot.end_plot()

        if implot.begin_plot("###TempPlot", flags=plot_flags):
            implot.setup_axes("Time", "", axis_flags, axis_flags)

            implot.plot_shaded(
                "Temperature",
                self.time_data,
                self.temp_data,
                offset=self.offset_index,
            )
            implot.end_plot()

        implot.pop_style_color()
        implot.pop_style_color()
        implot.pop_style_var()
        # implot.show_demo_window()
