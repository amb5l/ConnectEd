"""
Core functionality for the ConnectEd application.

This module provides fundamental components used throughout the application,
including settings, logging, argument parsing, and common types.
"""

__all__ = [
    'ORG_NAME',
    'APP_NAME',
    'LOG_FILENAME',
    'logger',
    'args',
    'unknown_args',
    'settings',
    'TypedList',
    'Rect2',
    'PainterContext',
    '_iround'
]

from .defs     import *
from .logger   import logger
from .args     import args, unknown_args
from .settings import Settings
from .types    import TypedList, Rect2
from .utils    import _iround

settings = Settings()
