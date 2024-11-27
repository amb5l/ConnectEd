import argparse

parser = argparse.ArgumentParser(
    prog='ConnectEd',
    description='CONNECTion EDitor - a tool for working with connection diagrams',
    epilog='See https://github.com/amb5l/ConnectEd'
    )

modeGroup = parser.add_mutually_exclusive_group()
modeGroup.add_argument('-g', '--gui', action='store_const', dest='mode', const='gui', help='start GUI (default)')
modeGroup.add_argument('-c', '--cmd', action='store_const', dest='mode', const='cmd', help='start command line processing')
parser.add_argument('-r', '--reset', action='store_true', help='clear stored preferences')
parser.add_argument('-i', '--input', type=str, dest='ifile', help='input file', default='')
parser.add_argument('-o', '--output', type=str, dest = 'ofile', help='output file', default='')
parser.add_argument('--dump_settings', action='store_true', help='dump settings')
parser.set_defaults(mode='gui')
args = parser.parse_args()
