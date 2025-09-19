import sys

from PyQt6.QtCore    import Qt
from PyQt6.QtGui     import QIcon

from .app import ConnectEdApp

from .core.log   import logger
from .core.nv    import Settings
from .core.db    import Model
from .core.args  import known_args, unknown_args
from .resources  import getIconPath, initResources

from .widgets.splash import Splash
from .widgets.window import Window


def main() -> int:
    logger.info("started")
    app = ConnectEdApp(sys.argv[:1] + unknown_args)
    app.setStyle("Fusion")
    scheme = app.styleHints().colorScheme()
    splash = Splash(scheme == Qt.ColorScheme.Light)
    splash.show()
    app.logger = logger
    app.settings = Settings()
    if known_args.reset:
        app.settings.reset()
    app.settings.load()
    if known_args.dump:
        print(app.settings.dump())
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
    app.model = Model()
    app.window = Window()
    app.processEvents()
    splash.finish(app.window)
    r = app.exec()
    app.settings.save()
    logger.info("finished")
    return r

if __name__ == "__main__":
    r = main()
    logger.info(f"exited with code {r}")
    sys.exit(r)
