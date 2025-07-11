import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui     import QIcon

from ..core      import NameCounter, Settings, Model, known_args, unknown_args
from ..resources import initResources
from ..widgets   import MainWindow

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
    initCli()
    hub.app.setStyle("Fusion")
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
    hub.main_window.show()
