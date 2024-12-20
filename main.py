import argparse
import time
from Spaceducks import SpaceduckInterface


# rough framerate, should be slightly higher due to render time
FRAMERATE = 90


msg = "Very Cool Ground Station Software"

parser = argparse.ArgumentParser(description=msg)

parser.add_argument(
    "port_1",
    type=str,
    help="Connected XBee or Arduino COM port",
)

parser.add_argument(
    "-f",
    "--fullscreen",
    action="store_true",
    help="Launch interface in full screen mode (borderless)",
)

args = parser.parse_args()


def main(args):

    ui = SpaceduckInterface(
        "Spaceduck Control Panel",
        1280,
        720,
        args.port_1,
        framerate=FRAMERATE,
        fullscreen=args.fullscreen,
    )

    try:
        while not ui.should_close:
            ui.update_gui()

    except KeyboardInterrupt:
        pass

    finally:
        ui.shutdown_gui()


if __name__ == "__main__":
    main(args)
