from PotatoUI import MainInterface


ui = MainInterface("Cool UI window", 1280, 720)

while not ui.should_close:
    ui.update()

ui.shutdownGUI()
