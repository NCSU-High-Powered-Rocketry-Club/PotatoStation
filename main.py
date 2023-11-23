import argparse
import time
from Kraken import KrakenInterface


# rough framerate, should be slightly higher due to render time
FRAMERATE = 90


msg = "Very Cool Ground Station Software"

parser = argparse.ArgumentParser(description=msg)

parser.add_argument("port_1", type=str,
                    help="Connected XBee or Arduino COM port")

parser.add_argument("port_2", type=str,
                    help="Another connected XBee or Arduino COM port")

parser.add_argument("-f", "--fullscreen", action="store_true",
                    help="Launch interface in full screen mode (borderless)")

args = parser.parse_args()


def main(args):

    ui = KrakenInterface("Kraken Control Panel", 1280, 720,
                         args.port_1, args.port_2, framerate=FRAMERATE,
                         fullscreen=args.fullscreen)

    try:
        while not ui.should_close:
            ui.update()

    except KeyboardInterrupt:
        pass

    finally:
        ui.shutdownGUI()


if __name__ == "__main__":
    main(args)
