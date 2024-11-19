from PyQt6.QtCore import Qt, QSizeF


DEFAULT_PREFS = {
    'file': {
        'new' : {
            'sheetSize' : QSizeF(2970, 2100)
        },
        'open': {
            'dir' : None
        },
        'save': {
            'dir' : None
        }
    },
    'draw': {
        'theme' : 'dark',
        'margin' : 10,
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
                    'family'  : 'Courier',
                    'size'    : 6,
                    'bold'    : False,
                    'italic'  : False
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
    'view': {
        'grid' : {
            'enable' : True,
            'dots'   : False,
            'alpha'  : 32
        },
        'alpha' : {
            'transparent' : 128,
            'opaque'      : 255
        },
        'zoomLimit' : {
            'max' : 16.0,
            'min' : 0.1
        },
        'canvasMargin' : {
            'left'   : 0,
            'top'    : 0,
            'right'  : 0,
            'bottom' : 0
        },
        'panStep'   : 0.125,
        'wheelStep' : 120
    },
    'print': {
        'theme' : 'print'
    }
}
