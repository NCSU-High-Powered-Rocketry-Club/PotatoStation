import argparse

msg = "Very Cool Ground Station Software"

parser = argparse.ArgumentParser(description=msg)

parser.add_argument("port", type=str,
                    help="Connected XBee or Arduino COM port")

args = parser.parse_args()


def main(args):
    pass


if __name__ == "__main__":
    main(args)
