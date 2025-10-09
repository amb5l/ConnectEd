import os

from typing import Self

import ConnectEd.scripting as cs

from PyQt6.QtCore import QPointF, QSizeF

from ConnectEd.widgets.graphics.items.rectangle import Rectangle

from ConnectEd.core.db import DesignDbNode, DiagramNode
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
    design_db_node = model.newDesignDbNode(TEST_DESIGN)
    assert isinstance(design_db_node, DesignDbNode)
    assert design_db_node.text() == TEST_DESIGN
    diagram_node = model.newDiagramNode(design_db_node, TEST_DIAGRAM)
    assert isinstance(diagram_node, DiagramNode)
    assert diagram_node.text() == TEST_DIAGRAM
    diagram_nodes = design_db_node.diagramNodes()
    assert len(diagram_nodes) == 1
    assert diagram_nodes[0] is diagram_node
    symbol_nodes = design_db_node.symbolNodes()
    assert len(symbol_nodes) == 0

    # get diagram
    diagram = diagram_node.diagram()
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
    design_db_node.save(TEST_FILE)
    assert os.path.exists(TEST_FILE)

    # close the design
    model.close(design_db_node)

    # verify the design is not in the model
    assert design_db_node not in model.designDbNodes()

    # discard the design
    del design_db_node

    # load the design
    design_db_node = DesignDbNode.load(TEST_FILE)
    assert isinstance(design_db_node, DesignDbNode)
    assert design_db_node.text() == TEST_DESIGN
    diagram_nodes = design_db_node.diagramNodes()
    assert len(diagram_nodes) == 1
    diagram_node = diagram_nodes[0]

    # done
    print("test finished")


class TestScriptedCLI:
    def test_scripted_cli(self : Self) -> None:
        cs.run(test, ["--cli"])


if __name__ == "__main__":
    cs.run(test, ["--cli"])
