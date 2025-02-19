import logging

from .defs import APP_NAME


logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(f'{APP_NAME}.log')
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s: %(pathname)64s: %(funcName)24s(): %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
