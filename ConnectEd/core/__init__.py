from dataclasses import dataclass


@dataclass
class Text:
    value : str   # text string value
    block : bool  # False = line, True = block

    def __str__(self) -> str:
        return self.value


@dataclass
class TextLine(Text):
    block : bool = False


@dataclass
class TextBlock(Text):
    block : bool = True

