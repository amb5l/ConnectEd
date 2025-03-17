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
    'connect_actions_to_slots',
    'Z_PAPER',
    'Z_TEMPLATE',
    'Z_DRAWING',
    'Z_OVERLAY',
    'Z_GRID',
    'Z_TOP',
    'LAYER_SHEET',
    'LAYER_DRAWING'
]

from .defs     import *
from .logger   import logger
from .args     import args, unknown_args
from .settings import Settings
from .types    import TypedList
from .utils    import connect_actions_to_slots

settings = Settings()
