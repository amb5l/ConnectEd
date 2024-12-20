from log      import logger
from settings import settings


class MainWindowEventsMixin:
    def closeEvent(self, event):
        # save window geometry
        settings.startup['geometry'] = self.saveGeometry()
        logger.info('closing')
