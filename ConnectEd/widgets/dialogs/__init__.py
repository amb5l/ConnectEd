from PyQt6.QtWidgets import QHBoxLayout, QPushButton

def okCancelLayoutStart(self) -> None:
    self.ok_cancel_layout = QHBoxLayout()

def okCancelLayoutFinish(self) -> None:
    self.ok_button = QPushButton("OK")
    self.ok_button.clicked.connect(self.accept)
    self.ok_cancel_layout.addWidget(self.ok_button)
    self.cancel_button = QPushButton("Cancel")
    self.cancel_button.clicked.connect(self.reject)
    self.ok_cancel_layout.addWidget(self.cancel_button)
    self.dialog_layout.addLayout(self.ok_cancel_layout)

def okCancelLayout(self) -> None:
    okCancelLayoutStart(self)
    self.ok_cancel_layout.addStretch()
    okCancelLayoutFinish(self)

def okCancelNewLayout(self) -> None:
    okCancelLayoutStart(self)
    self.new_button = QPushButton("New")
    self.new_button.clicked.connect(self.new)
    self.ok_cancel_layout.addWidget(self.new_button)
    self.ok_cancel_layout.addStretch()
    okCancelLayoutFinish(self)

__all__ = ["okCancelLayout"]

from .file          import *
from .text          import *
from .pin           import *
from .appearance    import *
from .properties    import *
from .property_text import *

__all__ += file.__all__
__all__ += text.__all__
__all__ += pin.__all__
__all__ += appearance.__all__
__all__ += properties.__all__
__all__ += property_text.__all__