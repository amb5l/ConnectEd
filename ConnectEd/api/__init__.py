import sys

from PyQt6.QtCore    import Qt
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui     import QIcon

from ..core      import NameCounter, Settings, Model, known_args, unknown_args
from ..resources import initResources
from ..widgets   import Splash, MainWindow

from .. import hub


def initCli():
    hub.name_counter = NameCounter()
    hub.settings = Settings()
    if known_args.reset:
        hub.settings.reset()
    hub.settings.load()
    hub.app = QApplication(sys.argv[:1] + unknown_args)
    hub.model = Model()

def initGui():
    hub.app = QApplication(sys.argv[:1] + unknown_args)
    hub.app.setStyle("Fusion")
    scheme = QApplication.instance().styleHints().colorScheme()
    hub.splash = Splash(scheme == Qt.ColorScheme.Light)
    hub.splash.show()
    hub.app.processEvents()
    hub.name_counter = NameCounter()
    hub.settings = Settings()
    if known_args.reset:
        hub.settings.reset()
    hub.settings.load()
    hub.model = Model()
    icon = QIcon(f"{hub.APP_ROOT}/resources/icons/ConnectEd.png")
    hub.app.setWindowIcon(icon)
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "ConnectEd.Application"
            )
        except Exception:
            pass
    initResources()
    hub.main_window = MainWindow()
    hub.splash.finish(hub.main_window)

