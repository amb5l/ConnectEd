import logging
from PyQt6.QtCore import QSizeF


ORG_NAME = 'ConnectEd'
APP_NAME = 'ConnectEd'
APP_EXT = 'ced'        # extension for ConnectEd files

untitled_number = 1

MSG_FMT = "%(asctime)s: %(filename)16s: %(funcName)24s(): %(message)s"
TIM_FMT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(filename=f'{APP_NAME}.log', format=MSG_FMT, datefmt=TIM_FMT)
logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.DEBUG)
