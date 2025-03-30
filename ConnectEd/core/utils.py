__all__ = [
    'NameCounter',
    'check',
    'getDefaultPath'
]

import os
import platform


class NameCounter:
    counts : dict[str, int]

    def __init__(self):
        self.counts = {}

    def get(self, name : str) -> str:
        if name not in self.counts:
            self.counts[name] = 0
        self.counts[name] += 1
        return f'{name}{self.counts[name]}'

def check(b : bool, s : str) -> bool:
    if not b:
        print(s)
    return b

def getDefaultPath() -> str:
    if platform.system() == 'Windows':
        if 'WORK' in os.environ:
            r = os.environ['WORK']
        elif 'USERPROFILE' in os.environ:
            r = os.environ['USERPROFILE']
        elif 'HOMEPATH' in os.environ:
            r = os.environ['HOMEPATH']
        elif 'HOMEDRIVE' in os.environ:
            r = os.environ['HOMEDRIVE']
        else:
            r = 'C:/'
    else:
        if 'WORK' in os.environ:
            r = os.environ['WORK']
        else:
            r = '~'
    return r
