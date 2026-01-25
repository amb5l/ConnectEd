from dataclasses import dataclass


@dataclass
class Text:
    value : str   # text string value
    block : bool  # False = line, True = block

@dataclass
class TextLine(Text):
    block : bool = False

@dataclass
class TextBlock(Text):
    block : bool = True

