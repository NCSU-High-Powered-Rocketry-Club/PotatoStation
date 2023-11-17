import argparse
from Kraken import KrakenInterface

msg = "Very Cool Ground Station Software"

parser = argparse.ArgumentParser(description=msg)

parser.add_argument("port", type=str,
                    help="Connected XBee or Arduino COM port")

args = parser.parse_args()


def main(args):
    ui = KrakenInterface("Cool UI window", 1280, 720)

    while not ui.should_close:
        ui.update()

    ui.shutdownGUI()


if __name__ == "__main__":
    main(args)
