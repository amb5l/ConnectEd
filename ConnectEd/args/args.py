# TODO change this to do things the Qt way

import argparse

from common import APP_NAME

class Args:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog=APP_NAME,
            description='ConnectEd (CONNECTion EDitor)'
        )
        self.parser.add_argument(
            '--batch',
            help='run in batch mode (no GUI)',
        )
        self.parser.add_argument(
            '--reset',
            help='reset preferences to default values',
        )
        self.args = self.parser.parse_args()
