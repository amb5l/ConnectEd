from dataclasses import dataclass


@dataclass
class Text:
    string : str   # text string value
    block  : bool  # False = line, True = block

    def __str__(self) -> str:
        return self.string


@dataclass
class TextLine(Text):
    block : bool = False


@dataclass
class TextBlock(Text):
    block : bool = True


text_default = TextLine("")
