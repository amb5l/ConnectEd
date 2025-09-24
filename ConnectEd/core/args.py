import argparse

parser = argparse.ArgumentParser(
    prog="ConnectEd",
    description="CONNECTion EDitor",
    epilog="See https://github.com/amb5l/ConnectEd"
    )
modeGroup = parser.add_mutually_exclusive_group()
parser.add_argument("-c", "--cli", action="store_true", help="run in CLI mode")
parser.add_argument("--nosplash", action="store_true", help="do not show splash screen")
parser.add_argument("--reset", action="store_true", help="clear stored preferences")
parser.add_argument("--dump", action="store_true", help="dump settings")
parser.add_argument("-x", "--exec", metavar="SCRIPT", help="execute script file")
parser.add_argument("--noexit", action="store_true", help="do not exit after script execution")
parser.add_argument("-v", "--version", action="store_true", help="print version")
known_args, unknown_args = parser.parse_known_args()
