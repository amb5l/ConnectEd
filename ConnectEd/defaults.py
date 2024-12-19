import os, platform
from PyQt6.QtCore import Qt, QSizeF
from PyQt6.QtGui import QColor


# default paths are platform dependant
if platform.system() == 'Windows':
    if 'WORK' in os.environ:
        default_path = os.environ['WORK']
    elif 'USERPROFILE' in os.environ:
        default_path = os.environ['USERPROFILE']
    elif 'HOMEPATH' in os.environ:
        default_path = os.environ['HOMEPATH']
    elif 'HOMEDRIVE' in os.environ:
        default_path = os.environ['HOMEDRIVE']
    else:
        default_path = 'C:'
else:
    if 'WORK' in os.environ:
        default_path = os.environ['WORK']
    else:
        default_path = '~'

FACTORY_SHEET_SIZES = {
    'A4' : QSizeF( 1169.0 ,  827.0 ),
    'A3' : QSizeF( 1654.0 , 1169.0 ),
    'A2' : QSizeF( 2338.0 , 1654.0 ),
    'A1' : QSizeF( 3307.0 , 2338.0 ),
    'A0' : QSizeF( 4677.0 , 3307.0 ),
    'A'  : QSizeF(  970.0 ,  720.0 ),
    'B'  : QSizeF( 1520.0 ,  970.0 ),
    'C'  : QSizeF( 2020.0 , 1520.0 ),
    'D'  : QSizeF( 3220.0 , 2020.0 ),
    'E'  : QSizeF( 4220.0 , 3220.0 )
}

DEFAULT_PREFS = {
    'file': {
        'new' : {
            'size'   : FACTORY_SHEET_SIZES['A4'],
            'margin' : 10
        },
        'open': {
            'dir' : default_path
        },
        'save': {
            'dir' : default_path
        }
    },
    'display': {
        'theme' : 'dark',
        'margin' : {
            'left'   : 0,
            'top'    : 0,
            'right'  : 0,
            'bottom' : 0
        },
        'grid' : {
            'enable' : True,
            'dots'   : False,
            'alpha'  : 32
        },
        'alpha' : {
            'transparent' : 128,
            'opaque'      : 255
        },
        'zoom' : {
            'max' : 16.0,
            'min' : 0.1
        },
        'pan_step'   : 0.125,
        'wheel_step' : 120
    },
    'draw': {
        'default' : {
            'alpha' : 192
        },
        'block' : {
            'line' : {
                'width' : 1,
                'style' : Qt.PenStyle.SolidLine
            },
            'fill' : {
                'style' : Qt.BrushStyle.SolidPattern
            },
            'property' : {
                'font'    : {
                    'family' : 'Courier',
                    'size'   : 6,
                    'bold'   : False,
                    'italic' : False
                },
                'outline' : True
            }
        }
    },
    'edit': {
        'grid' : {
            'snap' : True,
            'x'    : 10,
            'y'    : 10
        },
        'select' : {
            'enclose' : False
        },
        'drag' : {
            'min' : 5 # TODO apply this to screen pixels, not diagram pixels
        }
    },
    'print': {
        'theme' : 'print'
    }
}

DEFAULT_THEMES = {
    'dark': {
        'background'    : QColor(  8,    8,   8 ),
        'sheet'         : QColor(  16,  16,  16 ),
        'edge'          : QColor( 255,   0,   0 ),
        'grid'          : QColor(  32,  32,  32 ),
        'border'        : QColor(  64,  64,  64 ),
        'title_block'   : QColor(  64,  64,  64 ),
        'selected' : {
            'line'      : QColor( 255,   0, 255 ),
            'fill'      : QColor(  32,   0,  32 )
        },
        'highlighted' : {
            'line'      : QColor( 255, 255,   0 ),
            'fill'      : QColor(  32,  32,   0 )
        },
        'moving'      : {
            'line'      : QColor( 255, 255, 255 ),
            'fill'      : None
        },
        'block'       : {
            'line'      : QColor(   0, 128, 128 ),
            'fill'      : QColor(   0, 128, 128 ),
            'property'  : QColor( 128, 128,   0 )
        }
    },
    'light': {
        'background'    : QColor( 128, 128, 128 ),
        'sheet'         : QColor( 255, 255, 255 ),
        'grid'          : QColor( 192, 192, 192 ),
        'border'        : QColor(  64,  64,  64 ),
        'title_block'   : QColor(  64,  64,  64 ),
        'selected' : {
            'line'      : QColor( 255,   0, 255 ),
            'fill'      : QColor( 192, 192, 192 )
        },
        'highlighted' : {
            'line'      : QColor( 255, 255,   0 ),
            'fill'      : QColor( 192, 192, 192 )
        },
        'moving'      : {
            'line'      : QColor( 255, 255, 255 ),
            'fill'      : None
        },
        'block'       : {
            'line'      : QColor(   0, 128, 128 ),
            'fill'      : QColor(   0, 128, 128 ),
            'property'  : QColor( 128, 128,   0 )
        }
    },
    'mono': {
        'background'    : QColor( 128, 128, 128 ),
        'sheet'         : QColor( 255, 255, 255 ),
        'grid'          : QColor( 192, 192, 192 ),
        'border'        : QColor(  64,  64,  64 ),
        'title_block'   : QColor(  64,  64,  64 ),
        'selected' : {
            'line'      : QColor( 255,   0, 255 ),
            'fill'      : QColor( 192, 192, 192 )
        },
        'highlighted' : {
            'line'      : QColor( 255, 255,   0 ),
            'fill'      : QColor( 192, 192, 192 )
        },
        'moving'      : {
            'line'      : QColor( 255, 255, 255 ),
            'fill'      : None
        },
        'block'       : {
            'line'      : QColor(   0, 128, 128 ),
            'fill'      : QColor(   0, 128, 128 ),
            'property'  : QColor( 128, 128,   0 )
        }
    }
}
