from PyQt6.QtCore import Qt
from enum import Flag


class CanvasKeyboardMixin:
    class Modifiers(Flag):
        NONE  = 0
        SHIFT = 1
        CTRL  = 2
        ALT   = 4

    def getModifiers(self, event):
        r = self.Modifiers.NONE
        r |= self.Modifiers.SHIFT if event.modifiers() & Qt.KeyboardModifier.ShiftModifier   else self.Modifiers.NONE
        r |= self.Modifiers.CTRL  if event.modifiers() & Qt.KeyboardModifier.ControlModifier else self.Modifiers.NONE
        r |= self.Modifiers.ALT   if event.modifiers() & Qt.KeyboardModifier.AltModifier     else self.Modifiers.NONE
        return r

    #def keyPressEvent(self, event):
    #    key = event.key()
    #    shift, ctrl, alt = getModifiers(event)
    #    match [key, shift, ctrl, alt]:
    #        case prefs.kbd.escape:
    #            if self.editMode != EditMode.FREE:
    #                self.editMode = EditMode.FREE
    #            else:
    #                self.diagram.selectionClear()
    #            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
    #            self.update()
    #        case prefs.kbd.addBlock:
    #            self.editMode = EditMode.ADD_BLOCK
    #            self.setCursor(QCursor(Qt.CursorShape.CrossCursor)) # mouse pointer signifies add block mode
    #            self.update()