import sys

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui     import QIcon

from .core.log   import logger
from .core.nv    import Settings
from .core.db    import Model
from .core.args  import known_args, unknown_args
from .resources  import getIconPath, initResources

from .widgets.splash import Splash
from .widgets.window import Window

from . import hub


def main() -> int:
    logger.info("started")
    app = QApplication(sys.argv[:1] + unknown_args)
    app.setStyle("Fusion")
    scheme = QApplication.instance().styleHints().colorScheme()
    splash = Splash(scheme == Qt.ColorScheme.Light)
    splash.show()
    app.processEvents()
    hub.settings = Settings()
    if known_args.reset:
        hub.settings.reset()
    hub.settings.load()
    if known_args.dump:
        print(hub.settings.dump())
    icon = QIcon(getIconPath("ConnectEd.png"))
    app.setWindowIcon(icon)
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "ConnectEd.Application"
            )
        except Exception:
            pass
    initResources()
    model = Model()
    window = Window(model)
    splash.finish(window)
    r = app.exec()
    hub.settings.save()
    logger.info("finished")
    return r

if __name__ == "__main__":
    r = main()
    logger.info(f"exited with code {r}")
    sys.exit(r)
