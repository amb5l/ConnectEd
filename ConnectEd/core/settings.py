from types import SimpleNamespace

from PyQt6.QtCore import QSettings

from .logger    import logger
from .defs      import ORG_NAME, APP_NAME


class Settings:
    startup : SimpleNamespace

    def __init__(self):
        self.startup = SimpleNamespace()

    def reset(self):
        logger.debug('clearing all settings')
        qsettings = QSettings(ORG_NAME, APP_NAME)
        qsettings.clear()
