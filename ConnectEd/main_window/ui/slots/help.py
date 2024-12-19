from . import slot_with_main_window


class SlotsHelpMixin:
    @slot_with_main_window
    def helpAbout(self, main_window : 'MainWindow'):
        main_window.helpAbout()
