import ConnectEd.scripting as cs

from PyQt6.QtCore import QPointF, QSizeF

from ConnectEd.widgets.graphics.items.rectangle import Rectangle

from ConnectEd.core.db import DesignDbItem, DiagramItem
from ConnectEd.widgets.graphics.scenes.diagram import DiagramScene
from ConnectEd.widgets.graphics.items import DEFAULT


def test(app : cs.ConnectEdApp):

    print("test started")

    # verify we are running in CLI mode but with graphics support
    assert isinstance(app, cs.ConnectEdApp)
    assert app.cli() == True

    # create new design
    model = app.model()
    assert model is not None
    design_item = model.newDesignItem()
    assert isinstance(design_item, DesignDbItem)
    assert design_item.text() == "UntitledDesign1"
    diagram_items = design_item.diagramItems()
    assert len(diagram_items) == 1
    diagram_item = diagram_items[0]
    assert isinstance(diagram_item, DiagramItem)
    assert diagram_item.text() == "UntitledDiagram1"
    symbol_items = design_item.symbolItems()
    assert len(symbol_items) == 0

    # get diagram
    diagram = diagram_item.diagram()
    assert isinstance(diagram, DiagramScene)

    # add rectangle to diagram
    pos = QPointF(100, 100)
    size = QSizeF(100, 100)
    rect = Rectangle(pos, size)
    # verify basic properties
    assert rect.pos() == pos, \
        f"Got {rect.pos()}, expected {pos}"
    assert rect.rect().width() == size.width(), \
        f"Got {rect.rect().width()}, expected {size.width()}"
    assert rect.rect().height() == size.height(), \
        f"Got {rect.rect().height()}, expected {size.height()}"
    assert rect.line.getColor() == DEFAULT, \
        f"Got {rect.line.getColor()}, expected {DEFAULT}"
    assert rect.line.getWidth() == DEFAULT, \
        f"Got {rect.line.getWidth()}, expected {DEFAULT}"
    assert rect.line.getStyle() == DEFAULT, \
        f"Got {rect.line.getStyle()}, expected {DEFAULT}"
    assert rect.line.getStyle() == DEFAULT, \
        f"Got {rect.line.getStyle()}, expected {DEFAULT}"
    diagram.addItem(rect)

    # done
    print("test finished")

cs.run(test, ["--cli"])
