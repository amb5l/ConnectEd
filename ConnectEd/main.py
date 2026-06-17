import sys

from collections.abc import Callable

from PyQt6.QtCore    import Qt, QTimer
from PyQt6.QtGui     import QIcon

from .app import ConnectEdApp

from .core.log      import logger
from .core.args     import known_args
from .core.settings import Settings
from .core.session  import Session

from .resources  import getIconPath, initResources

from .widgets.splash import Splash
from .widgets.window import Window


def main(func : Callable | None = None) -> int:
    def _func():
        try:
            func(app)
        finally:
            if not known_args.noexit:
                w = app.window()
                if w is not None:
                    w.close()
                QTimer.singleShot(100, app.quit)

    logger.info("started")
    app = ConnectEdApp(known_args.cli)
    app.setCli(known_args.cli)
    if not known_args.cli:
        app.setStyle("Fusion")
    if func is not None:
        if known_args.nosplash:
            app.ready.window.connect(_func)
        else:
            app.ready.splash.connect(_func)
    if not (known_args.cli or known_args.nosplash):
        scheme = app.styleHints().colorScheme()
        splash = Splash(scheme == Qt.ColorScheme.Light)
        splash.show()
    app.setLogger(logger)
    app.setSettings(Settings())
    if known_args.reset:
        app.settings().reset()
    app.settings().load()
    if known_args.dump:
        print(app.settings().dump())
    if not known_args.cli:
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
    app.setSession(Session())
    if not known_args.cli:
        Window() # create window
    app.processEvents()
    if not (known_args.cli or known_args.nosplash):
        splash.finish(app.window())
    r = 0
    if func is not None and known_args.cli:
        func(app)
    elif func is None or known_args.noexit or not known_args.cli:
        r = app.exec()
    app.settings().save()
    logger.info("finished")
    return r

if __name__ == "__main__":
    r = main()
    logger.info(f"exited with code {r}")
    sys.exit(r)
