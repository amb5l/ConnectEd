import os

import ConnectEd.scripting as cs

from PyQt6.QtCore import QPointF, QSizeF

from ConnectEd.widgets.graphics.items.rectangle import Rectangle

from ConnectEd.core.db import DesignDbItem, DiagramItem
from ConnectEd.widgets.graphics.scenes.diagram import DiagramScene
from ConnectEd.widgets.graphics.items import DEFAULT


TEST_DESIGN = "test_scripted_cli_design"
TEST_DIAGRAM = "test_scripted_cli_diagram"
TEST_FILE = f"./{TEST_DESIGN}.xml"


def test(app : cs.ConnectEdApp):

    print("test started")

    assert isinstance(app, cs.ConnectEdApp)

    # verify we are running in CLI mode
    assert app.cli() == True

    # create new design
    model = app.model()
    assert model is not None
    design_item = model.newDesignItem(TEST_DESIGN)
    assert isinstance(design_item, DesignDbItem)
    assert design_item.text() == TEST_DESIGN
    diagram_item = model.newDiagramItem(design_item, TEST_DIAGRAM)
    assert isinstance(diagram_item, DiagramItem)
    assert diagram_item.text() == TEST_DIAGRAM
    diagram_items = design_item.diagramItems()
    assert len(diagram_items) == 1
    assert diagram_items[0] is diagram_item
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

    # save the design
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    assert not os.path.exists(TEST_FILE)
    design_item.save(TEST_FILE)
    assert os.path.exists(TEST_FILE)

    # close the design
    model.close(design_item)

    # verify the design is not in the model
    assert design_item not in model.designItems()

    # discard the design
    del design_item

    # load the design
    design_item = DesignDbItem.load(TEST_FILE)
    assert isinstance(design_item, DesignDbItem)
    assert design_item.text() == TEST_DESIGN
    diagram_items = design_item.diagramItems()
    assert len(diagram_items) == 1
    diagram_item = diagram_items[0]

    # done
    print("test finished")


class TestScriptedCLI:
    def test_scripted_cli(self):
        cs.run(test, ["--cli"])


if __name__ == "__main__":
    cs.run(test, ["--cli"])
