from PotatoUI import MainInterface
import imgui


# TODO: add com port parameter
class KrakenInterface(MainInterface):
    def __init__(self, name: str, width: int, height: int, font_path=None, font_size=14, scaling_factor=1):
        super().__init__(name, width, height, font_path, font_size, scaling_factor)

        self.serial_input_text = ""

    def drawGUI(self):
        # Draw the background logo and version stuff
        super().drawGUI()

        with imgui.begin("Serial Interface"):
            _, self.serial_input_text = imgui.input_text_with_hint(
                "##SerialEntry", "Send something", self.serial_input_text, flags=imgui.INPUT_TEXT_ENTER_RETURNS_TRUE)
            pass
            # TODO: Add enter button and send to pyserial

    def serial_listen_thread():
        pass
