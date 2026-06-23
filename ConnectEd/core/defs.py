from PyQt6.QtCore import QSizeF


ORG_NAME = "ConnectEd"
APP_NAME = "ConnectEd"
APP_EXT = ".ce"
MIME_TYPE = f"application/x-{APP_NAME.lower()}-xml"

LOG_FILENAME = f"{APP_NAME}.log"

Z_TEMPLATE      = -100
Z_DRAWING       = 0    # drawing layer
Z_SEGMENT       = Z_DRAWING - 1
Z_TOP           = +100 # select box / WIP

LAYERS_SHEET   = (Z_TEMPLATE,)
LAYERS_DRAWING = (Z_SEGMENT, Z_DRAWING)

WIDTH = 1  # standard line width
PITCH = 10 # standard item pitch

DEFS = {
    "sheets" : {
        "A4 (landscape)" : QSizeF( 1169.0 ,  827.0 ),
        "A3 (landscape)" : QSizeF( 1654.0 , 1169.0 ),
        "A2 (landscape)" : QSizeF( 2338.0 , 1654.0 ),
        "A1 (landscape)" : QSizeF( 3307.0 , 2338.0 ),
        "A0 (landscape)" : QSizeF( 4677.0 , 3307.0 ),
        "A (landscape)"  : QSizeF(  970.0 ,  720.0 ),
        "B (landscape)"  : QSizeF( 1520.0 ,  970.0 ),
        "C (landscape)"  : QSizeF( 2020.0 , 1520.0 ),
        "D (landscape)"  : QSizeF( 3220.0 , 2020.0 ),
        "E (landscape)"  : QSizeF( 4220.0 , 3220.0 ),
        "A4 (portrait)"  : QSizeF(  827.0 , 1169.0 ),
        "A3 (portrait)"  : QSizeF( 1169.0 , 1654.0 ),
        "A2 (portrait)"  : QSizeF( 1654.0 , 2338.0 ),
        "A1 (portrait)"  : QSizeF( 2338.0 , 3307.0 ),
        "A0 (portrait)"  : QSizeF( 3307.0 , 4677.0 ),
        "A (portrait)"   : QSizeF(  720.0 ,  970.0 ),
        "B (portrait)"   : QSizeF(  970.0 , 1520.0 ),
        "C (portrait)"   : QSizeF( 1520.0 , 2020.0 ),
        "D (portrait)"   : QSizeF( 2020.0 , 3220.0 ),
        "E (portrait)"   : QSizeF( 3220.0 , 4220.0 ),
    }
}
