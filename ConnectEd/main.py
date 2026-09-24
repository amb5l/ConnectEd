import gc
import sys

from collections.abc import Callable

from PyQt6.QtCore    import Qt, QTimer
from PyQt6.QtGui     import QIcon, QUndoStack

from .app import ConnectEdApp

from .core.log      import logger
from .core.args     import known_args
from .core.settings import Settings
from .core.session  import Session

from .resources  import getIconPath, initResources

from .widgets.splash import Splash, progress


def main(func : Callable | None = None) -> int:
    def _func():
        if func is None:
            raise RuntimeError("No function")
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
    splash = None
    if not (known_args.cli or known_args.nosplash):
        if (style_hints := app.styleHints()) is None:
            raise RuntimeError("No style hints")
        if (scheme := style_hints.colorScheme()) is None:
            raise RuntimeError("No color scheme")
        splash = Splash(scheme == Qt.ColorScheme.Light)
        splash.show()
    # The window import pulls in most of the UI. Load the slow pieces
    # first so the splash can move between them.
    window_cls = None
    if not known_args.cli:
        progress("Loading interface...", 0.05)
        import ConnectEd.ai.providers  # noqa: F401
        progress("Loading graphics...", 0.08)
        import ConnectEd.widgets.graphics.items.block  # noqa: F401
        progress("Loading diagram...", 0.11)
        import ConnectEd.widgets.graphics.scenes.diagram.netlist  # noqa: F401
        progress("Loading window...", 0.14)
        from .widgets.window import Window
        window_cls = Window
    app.setLogger(logger)
    progress("Loading settings...", 0.15)
    app.setSettings(Settings())
    if known_args.reset:
        app.settings().reset()
    app.settings().load()
    if known_args.dump:
        print(app.settings().dump())
    progress("Loading resources...", 0.35)
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
    progress("Starting session...", 0.5)
    app.setSession(Session())

    # side effect imports to register document types
    progress("Registering documents...", 0.65)
    import ConnectEd.domains.hdl.schematic.diagram_doc  # noqa: F401
    import ConnectEd.domains.hdl.schematic.library_doc  # noqa: F401
    import ConnectEd.domains.hdl.schematic.design_doc   # noqa: F401
    import ConnectEd.domains.hdl.fsm.diagram_doc        # noqa: F401

    if window_cls is not None:
        progress("Creating window...", 0.8)
        window_cls()
    progress("Ready", 1.0)
    app.processEvents()
    if not (known_args.cli or known_args.nosplash) and splash is not None:
        splash.finish(app.window())
    r = 0
    if func is not None and known_args.cli:
        func(app)
    elif func is None or known_args.noexit or not known_args.cli:
        r = app.exec()
    # Undo commands keep item pointers. Clear those stacks while the items
    # still exist, or destroying a scene later aborts the process.
    def _clearUndoStack(scene : object) -> None:
        stack = getattr(scene, "undo_stack", None)
        if isinstance(stack, QUndoStack):
            stack.clear()

    for doc in list(app.session()._open_docs):
        _clearUndoStack(getattr(doc, "_object", None))
        for scene in getattr(doc, "_scenes", {}).values():
            _clearUndoStack(scene)
    app.session().releaseDocs()
    gc.collect()
    app.processEvents()
    app.settings().save()
    logger.info("finished")
    return r

if __name__ == "__main__":
    r = main()
    logger.info(f"exited with code {r}")
    sys.exit(r)
