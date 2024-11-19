from PyQt6.QtGui import QColor

DEFAULT_THEMES = {
    'dark': {
        'background'    : QColor(  8,    8,   8 ),
        'sheet'         : QColor(  16,  16,  16 ),
        'edge'          : QColor( 255,   0,   0 ),
        'grid'          : QColor(  32,  32,  32 ),
        'border'        : QColor(  64,  64,  64 ),
        'titleBlock'    : QColor(  64,  64,  64 ),
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
        'titleBlock'    : QColor(  64,  64,  64 ),
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
    'print': {
        'background'    : QColor( 128, 128, 128 ),
        'sheet'         : QColor( 255, 255, 255 ),
        'grid'          : QColor( 192, 192, 192 ),
        'border'        : QColor(  64,  64,  64 ),
        'titleBlock'    : QColor(  64,  64,  64 ),
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
