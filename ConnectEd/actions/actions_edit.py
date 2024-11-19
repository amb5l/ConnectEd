from ._actions_private import _actions_todo

class ActionsEditMixin:
    def editCancel(self):
        _actions_todo()
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editUndo(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editRedo(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editRepeat(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editSelectAll(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editSelectWindow(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editSelectFilter(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editCut(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editCopy(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editPaste(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editDelete(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editSlide(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editMove(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editMirrorHorizonta(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editMirrorVertical(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editRotate(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editAlign(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editLock(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editUnlock(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editFix(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editUnfix(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editProperties(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editFind(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editReplace(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])

    def editSnap(self):
        QMessageBox.about(self.parent, "TODO", stack()[0][3])
