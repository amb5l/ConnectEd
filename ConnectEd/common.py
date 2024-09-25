import logging


ORG_NAME = "ConnectEd"
APP_NAME = "PyConnectEd"
APP_TITLE = "ConnectEd"

DPI = 100

logger = logging.getLogger(__name__)
logging.basicConfig(filename=f'{APP_NAME}.log', level=logging.INFO)
