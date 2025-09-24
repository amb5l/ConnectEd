import sys

from typing import Callable

from PyQt6.QtCore    import Qt
from PyQt6.QtGui     import QIcon

from .app import ConnectEdCliApp, ConnectEdGuiApp

from .core.log   import logger
from .core.nv    import Settings
from .core.db    import Model
from .resources  import getIconPath, initResources

from .widgets.splash import Splash
from .widgets.window import Window


def main(func : Callable | None = None, exit : bool = False) -> int:
    from .core.args import known_args, unknown_args
    logger.info("started")
    args = sys.argv[:1] + unknown_args
    app = ConnectEdCliApp(args) if known_args.cli else ConnectEdGuiApp(args)
    if not known_args.cli:
        app.setStyle("Fusion")
    if not known_args.nosplash:
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
    app.setModel(Model())
    if not known_args.cli:
        app.setWindow(Window())
    app.processEvents()
    if not (known_args.cli or known_args.nosplash):
        splash.finish(app.window())
    elif not known_args.cli:
        app.window().show()
        app.window().raise_()
        app.window().activateWindow()
    if func is not None:
        if known_args.cli:
            func(app)
            if exit:
                return 0
        else:
            def _run():
                func(app)
                if exit:
                    app.window().close()
                    app.quit()
                    sys.exit(0)
            app.window().ready.connect(_run)
            if known_args.nosplash:
                app.window().ready.emit()
    r = app.exec()
    app.settings().save()
    logger.info("finished")
    return r

if __name__ == "__main__":
    r = main()
    logger.info(f"exited with code {r}")
    sys.exit(r)
