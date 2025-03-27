import sys

from PyQt6.QtWidgets import QApplication

from .core      import logger, known_args, unknown_args, \
                       NameCounter, Settings, DatabaseManager, Design
from .widgets   import MainWindow, DiagramView, DiagramSubWindow
from .resources import initResources

from . import hub


def main() -> int:
    logger.info("started")
    hub.name_counter = NameCounter()
    hub.settings = Settings()
    if known_args.reset:
        hub.settings.reset()
    hub.settings.load()
    #print(settings.dump())
    app = QApplication(sys.argv[:1] + unknown_args)
    initResources()
    hub.database_manager = DatabaseManager()
    hub.main_window = MainWindow()
    hub.main_window.show()

    # TODO remove this
    test_db = hub.database_manager.new(Design)
    test_diagram = test_db.new_diagram()
    test_view = DiagramView(test_diagram)
    test_sub_window = DiagramSubWindow(hub.main_window.mdi_area)
    test_sub_window.setWidget(test_view)
    test_sub_window.setWindowTitle("Test Diagram")
    hub.main_window.mdi_area.addSubWindow(test_sub_window)
    test_sub_window.showMaximized()


    r = app.exec()
    hub.settings.save()
    logger.info("finished")
    return r

if __name__ == '__main__':
    r = main()
    logger.info(f"exited with code {r}")
    sys.exit(r)
