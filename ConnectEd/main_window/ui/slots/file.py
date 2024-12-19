from . import slot_with_main_window


class SlotsFileMixin:
    @slot_with_main_window
    def fileNew(self : 'Slots', main_window : 'MainWindow'):
        print('slot fileNew')
        main_window.fileNew()

    @slot_with_main_window
    def fileOpen(self : 'Slots', main_window : 'MainWindow'):
        main_window.fileOpen()

    @slot_with_main_window
    def fileSave(self : 'Slots', main_window : 'MainWindow'):
        main_window.fileSave()

    @slot_with_main_window
    def fileSaveAs(self : 'Slots', main_window : 'MainWindow'):
        main_window.fileSave()

    @slot_with_main_window
    def fileClose(self : 'Slots', main_window : 'MainWindow'):
        main_window.fileClose()
