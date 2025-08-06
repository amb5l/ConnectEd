import argparse

parser = argparse.ArgumentParser(
    prog="ConnectEd",
    description="CONNECTion EDitor",
    epilog="See https://github.com/amb5l/ConnectEd"
    )
modeGroup = parser.add_mutually_exclusive_group()
parser.add_argument("-r", "--reset", action="store_true", help="clear stored preferences")
known_args, unknown_args = parser.parse_known_args()
