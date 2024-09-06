from PyQt6.QtCore import QRect
from enum import Enum

class RectAnchorPoint(Enum):
    TopLeft = 0
    TopMiddle = 1
    TopRight = 2
    LeftTop = 3
    LeftMiddle = 4
    LeftBottom = 5
    RightTop = 6
    RightMiddle = 7
    RightBottom = 8
    BottomLeft = 9
    BottomMiddle = 10
    BottomRight = 11

class AnchoredText:
    def __init__(self, text, anchor, offset):
        self.text = text
        self.anchor = anchor
        self.offset = offset

class Block:
    def __init__(self, x, y, width, height):
        self.rect = QRect(x, y, width, height)
        self.reference = "reference?"
        self.value = "value?"
