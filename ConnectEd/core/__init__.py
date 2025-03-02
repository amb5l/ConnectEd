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
    'PainterContext',
    '_iround'
]

from .defs     import ORG_NAME, APP_NAME, LOG_FILENAME
from .logger   import logger
from .args     import args, unknown_args
from .settings import Settings
from .types    import TypedList, PainterContext
from .utils    import _iround

settings = Settings()
