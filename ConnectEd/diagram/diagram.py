import xml.etree.ElementTree as ET
from PyQt6.QtCore import QPointF

from diagram_extents import DiagramExtents
from diagram_select import DiagramSelectMixin
from diagram_common import DiagramCommonMixin


class Diagram(
    DiagramSelectMixin,
    DiagramCommonMixin
):
    startPos = QPointF()
    def __init__(self,title):
        self.title         = title
        self.extents       = DiagramExtents("A4_LANDSCAPE")
        self.content       = []

    def draw(self, painter, alpha):
        for item in self.content:
            item.draw(painter, alpha)
        for item in self.wip:
            item.draw(painter, alpha)
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
