__all__ = [
    'ORG_NAME',
    'APP_NAME',
    'DSN_EXT',
    'LIB_EXT',
    'LOG_FILENAME',
    'Z_EXTENTS',
    'Z_PAPER',
    'Z_TEMPLATE',
    'Z_DRAWING',
    'Z_OVERLAY',
    'Z_GRID',
    'Z_TOP',
    'LAYER_SHEET',
    'LAYER_DRAWING'
]

ORG_NAME = 'ConnectEd'
APP_NAME = 'ConnectEd'
DSN_EXT = '.cedsn'
LIB_EXT = '.celib'

LOG_FILENAME = f'{APP_NAME}.log'

Z_EXTENTS       = 0 # extents layer
Z_PAPER         = 100 # } sheet layer
Z_TEMPLATE      = 200 # }
Z_DRAWING       = 300 # drawing layer
Z_DRAWING_GRIPS = 301 # drawing grips layer
Z_OVERLAY       = 400 # overlay layer (e.g watermark)
Z_GRID          = 500 # grid layer
Z_TOP           = 600 # select box / WIP

LAYER_SHEET   = (Z_PAPER, Z_TEMPLATE)
LAYER_DRAWING = (Z_DRAWING, Z_DRAWING_GRIPS)
