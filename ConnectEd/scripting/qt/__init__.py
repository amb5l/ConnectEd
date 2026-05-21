"""Shared Qt interaction base for GUI scripting drivers."""

from .core import CoreMixin
from .menus import MenusMixin
from .modal import ModalMixin
from .protocol import GuiDriver
from .shell import ShellMixin


class QtScripting(CoreMixin, MenusMixin, ModalMixin, ShellMixin):
    """Qt primitives shared by GUI scripting drivers."""


__all__ = [
    "GuiDriver",
    "QtScripting",
]
