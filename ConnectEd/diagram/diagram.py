import xml.etree.ElementTree as ET
from PyQt6.QtCore import QPointF

from common import EXTENSION
from diagram.diagram_select import DiagramSelectMixin
from diagram.diagram_common import DiagramCommonMixin

'''
The Diagram class encapsulates the data and methods for a diagram.
Diagram data comprises attributes, essentials and items.
Attributes include the name of the diagram, its filename, path etc.
Essentials are the sheet, the border, and the title block.
There are 2 categories of element: *functional* and *decorative*.
Function items include blocks and wires. These usually have associated
properties, for example the name of a block, or the type of a wire.
Decorative items include graphics and text.
'''
class Diagram(
    DiagramSelectMixin,
    DiagramCommonMixin
):
    class DiagramAttributes:
        def __init__(self, name):
            self.name = name

        def getName(self):
            return self.name
        def setName(self, name):
            self.name = name
        def getFileName(self):
            return self.name + '.' + EXTENSION

    def __init__(self, title, sheetSize):
        self.title        = title
        self.sheetSize    = sheetSize
        self.content      = []
        self.selectFilter = self.SelectFilter()

    def paint(self, painter, alpha):
        self.sheet.paint(painter, alpha)
        self.border.paint(painter, alpha)
        self.titleBlock.paint(painter, alpha)
        for item in self.content:
            item.paint(painter, alpha)
        for item in self.wip:
            item.paint(painter, alpha)
        self.selectionDraw(painter)

    def load(self, filename):
        # create an ElementTree object from the XML file
        tree = ET.parse(filename)

        # get the root element
        root = tree.getroot()

        # get sub elements
        self.title = root.find("title").text
        self.sheetExtents = root.find("sheetExtents").text

    def save(self, filename):
        # create root element
        root = ET.Element("ConnectEd Diagram")

        # create sub elements
        ET.SubElement(root, "title").text = self.title
        ET.SubElement(root, "sheetExtents").text = self.sheetExtents

        # create an ElementTree object from the root element
        tree = ET.ElementTree(root)

        # write the XML tree to a file
        tree.write(filename, encoding="utf-8", xml_declaration=True)
