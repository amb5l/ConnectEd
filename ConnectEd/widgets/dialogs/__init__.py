from PyQt6.QtWidgets import QHBoxLayout, QPushButton

def okCancelLayout(self) -> None:
    self.ok_cancel_layout = QHBoxLayout()
    self.ok_cancel_layout.addStretch()
    self.ok_button = QPushButton("OK")
    self.ok_button.clicked.connect(self.accept)
    self.ok_cancel_layout.addWidget(self.ok_button)
    self.cancel_button = QPushButton("Cancel")
    self.cancel_button.clicked.connect(self.reject)
    self.ok_cancel_layout.addWidget(self.cancel_button)
    self.dialog_layout.addLayout(self.ok_cancel_layout)

__all__ = ["okCancelLayout"]

from .file       import *
from .text       import *
from .appearance import *
from .properties import *

__all__ += file.__all__
__all__ += text.__all__
__all__ += appearance.__all__
__all__ += properties.__all__