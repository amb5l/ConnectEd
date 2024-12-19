from diagram import Diagram
from . import slot_with_diagram


class SlotsEditMixin:
    @slot_with_diagram
    def editUndo(self, diagram : Diagram):
        diagram.editUndo()

    @slot_with_diagram
    def editRedo(self, diagram : Diagram):
        diagram.editRedo()

    @slot_with_diagram
    def editCut(self, diagram : Diagram):
        diagram.editCut()

    @slot_with_diagram
    def editCopy(self, diagram : Diagram):
        diagram.editCopy()

    @slot_with_diagram
    def editPaste(self, diagram : Diagram):
        diagram.editPaste()
