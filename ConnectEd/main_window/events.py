from common   import logger
from settings import startup


class MainWindowEventsMixin:
    def closeEvent(self, event):
        # save window geometry
        startup['geometry'] = self.saveGeometry()
        super().closeEvent(event)
        logger.info('main_windowdow: closing')
