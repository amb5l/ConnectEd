from log      import logger
from settings import settings


class MainWindowEventsMixin:
    def closeEvent(self, event):
        # save window geometry
        settings.startup['geometry'] = self.saveGeometry()
        super().closeEvent(event)
        logger.info('main_windowdow: closing')
