import argparse

parser = argparse.ArgumentParser(
    prog="ConnectEd",
    description="CONNECTion EDitor",
    epilog="See https://github.com/amb5l/ConnectEd"
    )
modeGroup = parser.add_mutually_exclusive_group()
parser.add_argument("-c", "--cli", action="store_true", help="run in CLI mode")
parser.add_argument("-n", "--nosplash", action="store_true", help="do not show splash screen")
parser.add_argument("-r", "--reset", action="store_true", help="clear stored preferences")
parser.add_argument("-d", "--dump", action="store_true", help="dump settings")
parser.add_argument("-x", "--exec", metavar="SCRIPT", help="execute script file")
parser.add_argument("-v", "--version", action="store_true", help="print version")
known_args, unknown_args = parser.parse_known_args()
