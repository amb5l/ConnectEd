from PyQt6.QtCore import QSettings

from common import ORG_NAME, APP_NAME

settings = QSettings(ORG_NAME, APP_NAME)
settings.clear()
