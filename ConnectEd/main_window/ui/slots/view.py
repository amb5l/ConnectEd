from canvas import Canvas
from . import slot_with_canvas


class SlotsViewMixin:
    @slot_with_canvas
    def viewZoomAll(self, canvas : Canvas):
        canvas.viewZoomAll()

    @slot_with_canvas
    def viewZoomSheet(self, canvas : Canvas):
        canvas.viewZoomAll()

    @slot_with_canvas
    def viewZoomSelection(self, canvas : Canvas):
        canvas.viewZoomSelection()

    @slot_with_canvas
    def viewZoomIn(self, canvas : Canvas):
        canvas.viewZoomIn()

    @slot_with_canvas
    def viewZoomOut(self, canvas : Canvas):
        canvas.viewZoomOut()

    @slot_with_canvas
    def viewPanLeft(self, canvas : Canvas):
        canvas.viewPanLeft()

    @slot_with_canvas
    def viewPanRight(self, canvas : Canvas):
        canvas.viewPanRight()

    @slot_with_canvas
    def viewPanUp(self, canvas : Canvas):
        canvas.viewPanUp()

    @slot_with_canvas
    def viewPanDown(self, canvas : Canvas):
        canvas.viewPanDown()

    @slot_with_canvas
    def viewPrev(self, canvas : Canvas):
        canvas.viewPrev()

    @slot_with_canvas
    def viewNext(self, canvas : Canvas):
        canvas.viewNext()
