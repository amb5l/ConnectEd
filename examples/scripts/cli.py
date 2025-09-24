import ConnectEd.scripting as cs

from PyQt6.QtCore import QPointF, QSizeF

from ConnectEd.widgets.graphics.items.rectangle import Rectangle

from ConnectEd.core.db import DesignDbItem, DiagramItem
from ConnectEd.widgets.graphics.scenes.diagram import DiagramScene
from ConnectEd.widgets.graphics.items import DEFAULT


def test(app : cs.ConnectEdApp):

    print("test started")

    # get model (so we can work with designs)
    model = app.model()
    # create new design
    design_item = model.newDesignItem()
    # set the design name
    design_item.setText("cli")
    # get all diagram items in the design
    diagram_items = design_item.diagramItems()
    # pick the first diagram item
    diagram_item = diagram_items[0]
    # get the diagram
    diagram = diagram_item.diagram()
    # create a rectangle
    pos = QPointF(100, 100)
    size = QSizeF(100, 100)
    rect = Rectangle(pos, size)
    # add rectangle to diagram
    diagram.addItem(rect)
    # save the design
    design_item.save("./cli.xml")

    # done
    print("test finished")

cs.run(test, ["--cli"])
