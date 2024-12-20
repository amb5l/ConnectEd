import sys, os

from log    import logger


def createInst(cls, *args, **kwargs):
    inst = cls(*args, **kwargs)
    if not isinstance(inst, cls):
        logger.error(f'Failed to create instance of {cls.__name__}')
        sys.exit(1)
    return inst

def getInst(obj, cls):
    if not isinstance(obj, cls):
        logger.error(f'Expected instance of {cls.__name__}, got {type(obj).__name__}')
        sys.exit(1)
    return obj

def normAbsPath(path):
    return os.path.normpath(os.path.abspath(path))
