import ConnectEd.scripting as cs

from PyQt6.QtCore import QPointF, QSizeF

from ConnectEd.widgets.graphics.items.rectangle import Rectangle

from ConnectEd.core.db import DesignDbNode, DiagramNode
from ConnectEd.widgets.graphics.scenes.diagram import DiagramScene
from ConnectEd.widgets.graphics.items import DEFAULT


def test(app : cs.ConnectEdApp):

    print("test started")

    # get model (so we can work with designs)
    model = app.model()
    # create new design
    design_db_node = model.newDesignDbNode()
    # set the design name
    design_db_node.setText("cli")
    # get all diagram items in the design
    diagram_nodes = design_db_node.diagramNodes()
    # pick the first diagram item
    diagram_node = diagram_nodes[0]
    # get the diagram
    diagram = diagram_node.diagram()
    # create a rectangle
    pos = QPointF(100, 100)
    size = QSizeF(100, 100)
    rect = Rectangle(pos, size)
    # add rectangle to diagram
    diagram.addItem(rect)
    # save the design
    design_db_node.save("./cli.xml")

    # done
    print("test finished")

cs.run(test, ["--cli"])
