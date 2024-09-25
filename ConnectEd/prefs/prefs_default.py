from PyQt6.QtCore import Qt


PREFS_DEFAULT = {
    "general" : {
        "untitled" : "Untitled"
    },
    "draw": {
        "theme" : "dark",
        "margin" : 10,
        "block" : {
            "line" : {
                "width" : 1
            },
            "fill" : {
                "style" : Qt.BrushStyle.SolidPattern
            },
            "property" : {
                "font"    : {
                    "family"  : "Courier",
                    "size"    : 6,
                    "bold"    : False,
                    "italic"  : False
                },
                "outline" : False
            }
        }
    },
    "edit": {
        "grid" : {
            "enable" : True,
            "x"      : 10,
            "y"      : 10
        },
        "select" : {
            "enclose" : False,
            "filter"  : {
                "functional" : {
                    "title"     : True,
                    "block"     : True,
                    "pin"       : True,
                    "wire"      : True,
                    "tap"       : True,
                    "junction"  : True,
                    "port"      : True,
                    "code"      : True
                },
                "decorative" : {
                    "line"      : True,
                    "rectangle" : True,
                    "polygon"   : True,
                    "arc"       : True,
                    "ellipse"   : True,
                    "textline"  : True,
                    "textbox"   : True,
                    "image"     : True
                }
            }
        },
        "drag" : {
            "min" : {
                "x" : 10,
                "y" : 10
            }
        }
    },
    "view": {
        "alpha" : {
            "transparent" : 128,
            "opaque"      : 255
        }
        "zoomLimits" : {
            "max" : 16.0,
            "min" : 0.1
        },
        "zoomFullPadding" : {
            "left"   : 0,
            "top"    : 0,
            "right"  : 0,
            "bottom" : 0
        },
        "panStep"   : 0.125,
        "wheelStep" : 120
    },
    "print": {
        "theme" : "print"
    },
    "sheet": {
        "orientation" : "landscape",
        "size" : {
            "A4": ( 11.69 ,  8.27 ),
            "A3": ( 16.54 , 11.69 ),
            "A2": ( 23.38 , 16.54 ),
            "A1": ( 33.07 , 23.38 ),
            "A0": ( 46.77 , 33.07 ),
            "A":  (  9.70 ,  7.20 ),
            "B":  ( 15.20 ,  9.70 ),
            "C":  ( 20.20 , 15.20 ),
            "D":  ( 32.20 , 20.20 ),
            "E":  ( 42.20 , 32.20 )
        }
    }
}