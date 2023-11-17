from PotatoUI import MainInterface


class KrakenInterface(MainInterface):
    def __init__(self, name: str, width: int, height: int, font_path=None, font_size=14, scaling_factor=1):
        super().__init__(name, width, height, font_path, font_size, scaling_factor)
        pass

    def drawGUI(self):
        # Draw the background logo and version stuff
        super().drawGUI()
