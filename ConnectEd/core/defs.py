__all__ = [
    "ORG_NAME",
    "APP_NAME",
    "MIME_TYPE",
    "GEN_EXT",
    "DSN_EXT",
    "DGM_EXT",
    "LIB_EXT",
    "LOG_FILENAME",
    "Z_TEMPLATE",
    "Z_DRAWING",
    "Z_TOP",
    "LAYER_SHEET",
    "LAYER_DRAWING"
]

ORG_NAME = "ConnectEd"
APP_NAME = "ConnectEd"
MIME_TYPE = f"application/x-{APP_NAME.lower()}-xml"
GEN_EXT = ".ce*"
DGM_EXT = ".cedgm"
DSN_EXT = ".cedsn"
LIB_EXT = ".celib"

LOG_FILENAME = f"{APP_NAME}.log"

Z_TEMPLATE      = 200 # }
Z_DRAWING       = 300 # drawing layer
Z_DRAWING_GRIPS = 301 # drawing grips layer
Z_TOP           = 600 # select box / WIP

LAYER_SHEET   = (Z_TEMPLATE)
LAYER_DRAWING = (Z_DRAWING, Z_DRAWING_GRIPS)
