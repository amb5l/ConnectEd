ORG_NAME = "ConnectEd"
APP_NAME = "ConnectEd"
MIME_TYPE = f"application/x-{APP_NAME.lower()}-xml"
GEN_EXT = ".ce*"
DSN_EXT = ".cedsn"
LIB_EXT = ".celib"

LOG_FILENAME = f"{APP_NAME}.log"

Z_TEMPLATE      = -100
Z_DRAWING       = 0    # drawing layer
Z_TOP           = +100 # select box / WIP

LAYER_SHEET   = (Z_TEMPLATE,)
LAYER_DRAWING = (Z_DRAWING,)
