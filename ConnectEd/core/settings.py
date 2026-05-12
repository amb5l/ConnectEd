"""
Settings management for the ConnectEd application.

This module provides classes for managing application settings,
including loading, saving, and accessing configuration values.
"""

# TODO:
# persistant settings for application
# session settings for diagram and library

from types  import SimpleNamespace
from typing import Self, Any

from PyQt6.QtCore import Qt, QObject, pyqtSignal, QSettings, QPointF, QSizeF

from ..app import logger

from .defs    import ORG_NAME, APP_NAME, DEFS
from .utils   import getDefaultPath, val2str, str2val
from .palette import PaletteDark, PaletteLightMono


FACTORY_SETTINGS = {
    "startup" : {
        "geometry" : b''
    },
    "mru" : {
        "1" : "",
        "2" : "",
        "3" : "",
        "4" : "",
        "5" : "",
        "6" : "",
        "7" : "",
        "8" : "",
        "9" : ""
    },
    "display" : {
        "theme" : "dark",
        "font_size" : 10,
        "alpha" : 240,
        "select" : {
            "tolerance" : 2.0,
            "outline" : {
                "width" : 0,
                "style" : Qt.PenStyle.DotLine
            }
        },
        "zoom" : {
            "padding" : 0.1,
            "step"    : 0.25,
            "min"     : 0.01,
            "max"     : 100.0
        },
        "pan" : {
            "step" : 0.1
        }
    },
    "defaults" : {
        "extents" : QSizeF(800.0, 600.0),
        "sheet" : {
            "name" : "A4 (landscape)",
            "size" : DEFS["sheets"]["A4 (landscape)"]
        },
        "margin" : 10.0,
        "border" : 1.0,
        "grid" : {
            "display"    : True,
            "snap"       : True,
            "pitch"      : QPointF(10.0, 10.0),
            "dots"       : False,
            "alpha"      : 128,
            "min_pixels" : 10
        }
    },
    "prefs" : {
        "file" : {
            "new" : {
                "sheet"  : "A4",
                "margin" : 10
            },
            "open" : {
                "dir" : getDefaultPath()
            },
            "save" : {
                "dir" : getDefaultPath()
            }
        },
        "mouse" : {
            "drag"  : 5,
            "wheel" : 120
        }
    },
    "themes" : {
        "dark" : {
            "background" : PaletteDark.Background,
            "origin" : {
                "color" : PaletteDark.Origin,
                "size"  : 12
            },
            "sheet"      : PaletteDark.Sheet,
            "border"     : PaletteDark.Border,
            "items" : {
                "FreeNode" : {
                    "size" : 3,
                    "unconnected" : {
                        "line" : {
                            "color" : PaletteDark.FreeNodeUnconnected,
                            "width" : 0,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : PaletteDark.FreeNodeUnconnected,
                            "style" : Qt.BrushStyle.NoBrush
                        }
                    },
                    "connected" : {
                        "line" : {
                            "color" : PaletteDark.FreeNodeConnected,
                            "width" : 0,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : PaletteDark.FreeNodeConnected,
                            "style" : Qt.BrushStyle.NoBrush
                        }
                    },
                    "junction" : {
                        "line" : {
                            "color" : PaletteDark.FreeNodeJunction,
                            "width" : 0,
                            "style" : Qt.PenStyle.NoPen
                        },
                        "fill" : {
                            "color" : PaletteDark.FreeNodeJunction,
                            "style" : Qt.BrushStyle.SolidPattern
                        }
                    }
                },
                "FixedNode" : {
                    "size" : 3,
                    "unconnected" : {
                        "line" : {
                            "color" : PaletteDark.FixedNodeUnconnected,
                            "width" : 0,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : PaletteDark.FixedNodeUnconnected,
                            "style" : Qt.BrushStyle.NoBrush
                        }
                    },
                    "connected" : {
                        "line" : {
                            "color" : PaletteDark.FixedNodeConnected,
                            "width" : 0,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : PaletteDark.FixedNodeConnected,
                            "style" : Qt.BrushStyle.NoBrush
                        }
                    },
                    "junction" : {
                        "line" : {
                            "color" : PaletteDark.FixedNodeJunction,
                            "width" : 0,
                            "style" : Qt.PenStyle.NoPen
                        },
                        "fill" : {
                            "color" : PaletteDark.FixedNodeJunction,
                            "style" : Qt.BrushStyle.SolidPattern
                        }
                    }
                },
                "Segment" : {
                    "line" : {
                        "color" : PaletteDark.Segment,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "SegmentPreview1" : {
                    "line" : {
                        "color" : PaletteDark.SegmentPreview1,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "SegmentPreview2" : {
                    "line" : {
                        "color" : PaletteDark.SegmentPreview2,
                        "width" : 1,
                        "style" : Qt.PenStyle.DashDotDotLine
                    }
                },
                "Tap" : {
                    "unresolved" : {
                        "line" : {
                            "color" : PaletteDark.TapUnresolved,
                            "width" : 1,
                            "style" : Qt.PenStyle.SolidLine
                        }
                    },
                    "scalar" : {
                        "line" : {
                            "color" : PaletteDark.TapScalar,
                            "width" : 1,
                            "style" : Qt.PenStyle.SolidLine
                        }
                    },
                    "vector" : {
                        "line" : {
                            "color" : PaletteDark.TapVector,
                            "width" : 3,
                            "style" : Qt.PenStyle.SolidLine
                        }
                    }
                },
                "Port" : {
                    "size" : 6,
                    "line" : {
                        "color" : PaletteDark.PortLine,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteDark.PortFill,
                        "style" : Qt.BrushStyle.SolidPattern
                    }
                },
                "PortName" : {
                    "text" : {
                        "color"     : PaletteDark.PortName,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "PortComment" : {
                    "text" : {
                        "color"     : PaletteDark.PortComment,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "Gate" : {
                    "line" : {
                        "color" : PaletteDark.GateLine,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteDark.GateFill,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "GatePin" : {
                    "line" : {
                        "color" : PaletteDark.GatePin,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteDark.GatePin,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "Block" : {
                    "line" : {
                        "color" : PaletteDark.BlockLine,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteDark.BlockFill,
                        "style" : Qt.BrushStyle.SolidPattern
                    }
                },
                "BlockLabel" : {
                    "text" : {
                        "color"     : PaletteDark.BlockLabel,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "BlockName" : {
                    "text" : {
                        "color"     : PaletteDark.BlockName,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "BlockPin" : {
                    "line" : {
                        "color" : PaletteDark.BlockPin,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "BlockPinArrow" : {
                    "size" : 6,
                    "line" : {
                        "color" : PaletteDark.BlockPinArrow,
                        "width" : 0,
                        "style" : Qt.PenStyle.NoPen
                    },
                    "fill" : {
                        "color" : PaletteDark.BlockPinArrow,
                        "style" : Qt.BrushStyle.SolidPattern
                    }
                },
                "BlockPinName" : {
                    "text" : {
                        "color"     : PaletteDark.BlockPinName,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "BlockPinComment" : {
                    "text" : {
                        "color"     : PaletteDark.BlockPinComment,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "SymbolPin" : {
                    "line" : {
                        "color" : PaletteDark.SymbolPin,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteDark.SymbolPin,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "SymbolPinDot" : {
                    "size" : 3
                },
                "SymbolPinClk" : {
                    "size" : 3
                },
                "SymbolPinArrow" : {
                    "size" : 3,
                    "line" : {
                        "color" : PaletteDark.SymbolPinArrow,
                        "width" : 0,
                        "style" : Qt.PenStyle.NoPen
                    },
                    "fill" : {
                        "color" : PaletteDark.SymbolPinArrow,
                        "style" : Qt.BrushStyle.SolidPattern
                    }
                },
                "SymbolPinName" : {
                    "text" : {
                        "color"     : PaletteDark.SymbolPinName,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "SymbolPinComment" : {
                    "text" : {
                        "color"     : PaletteDark.SymbolPinComment,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "PropertyText" : {
                    "text" : {
                        "color"     : PaletteDark.PropertyText,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "Line" : {
                    "line" : {
                        "color" : PaletteDark.Line,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "Rectangle" : {
                    "line" : {
                        "color" : PaletteDark.Rectangle,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteDark.Rectangle,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "Ellipse" : {
                    "line" : {
                        "color" : PaletteDark.Ellipse,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteDark.Ellipse,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "Polyline" : {
                    "line" : {
                        "color" : PaletteDark.Polyline,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "Text" : {
                    "text" : {
                        "color"     : PaletteDark.Text,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                }
            },
            "selected" : {
                "line" : PaletteDark.SelectedLine,
                "fill" : PaletteDark.SelectedFill,
                "text" : PaletteDark.SelectedText
            },
            "grip" : {
                "size"  : 12,
                "color" : PaletteDark.Grip
            },
            "grid" : {
                "line" : PaletteDark.Grid
            },
            "properties" : {
                "deleted" : {
                    "color" : PaletteDark.PropertyDeleted
                },
                "changed" : {
                    "color" : PaletteDark.PropertyChanged
                },
                "added" : {
                    "color" : PaletteDark.PropertyAdded
                }
            }
        },
        "light_mono" : {
            "background" : PaletteLightMono.Background,
            "origin" : {
                "color" : PaletteLightMono.Origin,
                "size"  : 12
            },
            "sheet"      : PaletteLightMono.Sheet,
            "border"     : PaletteLightMono.Border,
            "items" : {
                "FreeNode" : {
                    "size" : 3,
                    "unconnected" : {
                        "line" : {
                            "color" : PaletteLightMono.FreeNodeUnconnected,
                            "width" : 0,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : PaletteLightMono.FreeNodeUnconnected,
                            "style" : Qt.BrushStyle.NoBrush
                        }
                    },
                    "connected" : {
                        "line" : {
                            "color" : PaletteLightMono.FreeNodeConnected,
                            "width" : 0,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : PaletteLightMono.FreeNodeConnected,
                            "style" : Qt.BrushStyle.NoBrush
                        }
                    },
                    "junction" : {
                        "line" : {
                            "color" : PaletteLightMono.FreeNodeJunction,
                            "width" : 0,
                            "style" : Qt.PenStyle.NoPen
                        },
                        "fill" : {
                            "color" : PaletteLightMono.FreeNodeJunction,
                            "style" : Qt.BrushStyle.SolidPattern
                        }
                    }
                },
                "FixedNode" : {
                    "size" : 3,
                    "unconnected" : {
                        "line" : {
                            "color" : PaletteLightMono.FixedNodeUnconnected,
                            "width" : 0,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : PaletteLightMono.FixedNodeUnconnected,
                            "style" : Qt.BrushStyle.NoBrush
                        }
                    },
                    "connected" : {
                        "line" : {
                            "color" : PaletteLightMono.FixedNodeConnected,
                            "width" : 0,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : PaletteLightMono.FixedNodeConnected,
                            "style" : Qt.BrushStyle.NoBrush
                        }
                    },
                    "junction" : {
                        "line" : {
                            "color" : PaletteLightMono.FixedNodeJunction,
                            "width" : 0,
                            "style" : Qt.PenStyle.NoPen
                        },
                        "fill" : {
                            "color" : PaletteLightMono.FixedNodeJunction,
                            "style" : Qt.BrushStyle.SolidPattern
                        }
                    }
                },
                "Segment" : {
                    "line" : {
                        "color" : PaletteLightMono.Segment,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "SegmentPreview1" : {
                    "line" : {
                        "color" : PaletteLightMono.SegmentPreview1,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "SegmentPreview2" : {
                    "line" : {
                        "color" : PaletteLightMono.SegmentPreview2,
                        "width" : 1,
                        "style" : Qt.PenStyle.DashDotDotLine
                    }
                },
                "Tap" : {
                    "unresolved" : {
                        "line" : {
                            "color" : PaletteLightMono.TapUnresolved,
                            "width" : 1,
                            "style" : Qt.PenStyle.DotLine
                        }
                    },
                    "scalar" : {
                        "line" : {
                            "color" : PaletteLightMono.TapScalar,
                            "width" : 1,
                            "style" : Qt.PenStyle.SolidLine
                        }
                    },
                    "vector" : {
                        "line" : {
                            "color" : PaletteLightMono.TapVector,
                            "width" : 3,
                            "style" : Qt.PenStyle.SolidLine
                        }
                    }
                },
                "Port" : {
                    "size" : 6,
                    "line" : {
                        "color" : PaletteLightMono.PortLine,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteLightMono.PortFill,
                        "style" : Qt.BrushStyle.SolidPattern
                    }
                },
                "PortName" : {
                    "text" : {
                        "color"     : PaletteLightMono.PortName,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "PortComment" : {
                    "text" : {
                        "color"     : PaletteLightMono.PortComment,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "Gate" : {
                    "line" : {
                        "color" : PaletteLightMono.GateLine,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteLightMono.GateFill,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "GatePin" : {
                    "line" : {
                        "color" : PaletteLightMono.GatePin,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteLightMono.GatePin,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "Block" : {
                    "line" : {
                        "color" : PaletteLightMono.BlockLine,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteLightMono.BlockFill,
                        "style" : Qt.BrushStyle.SolidPattern
                    }
                },
                "BlockLabel" : {
                    "text" : {
                        "color"     : PaletteLightMono.BlockLabel,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "BlockName" : {
                    "text" : {
                        "color"     : PaletteLightMono.BlockName,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "BlockPin" : {
                    "line" : {
                        "color" : PaletteLightMono.BlockPin,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "BlockPinArrow" : {
                    "size" : 6,
                    "line" : {
                        "color" : PaletteLightMono.BlockPinArrow,
                        "width" : 0,
                        "style" : Qt.PenStyle.NoPen
                    },
                    "fill" : {
                        "color" : PaletteLightMono.BlockPinArrow,
                        "style" : Qt.BrushStyle.SolidPattern
                    }
                },
                "BlockPinName" : {
                    "text" : {
                        "color"     : PaletteLightMono.BlockPinName,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "BlockPinComment" : {
                    "text" : {
                        "color"     : PaletteLightMono.BlockPinComment,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "SymbolPin" : {
                    "line" : {
                        "color" : PaletteLightMono.SymbolPin,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteLightMono.SymbolPin,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "SymbolPinDot" : {
                    "size" : 3
                },
                "SymbolPinClk" : {
                    "size" : 3
                },
                "SymbolPinArrow" : {
                    "size" : 3,
                    "line" : {
                        "color" : PaletteLightMono.SymbolPinArrow,
                        "width" : 0,
                        "style" : Qt.PenStyle.NoPen
                    },
                    "fill" : {
                        "color" : PaletteLightMono.SymbolPinArrow,
                        "style" : Qt.BrushStyle.SolidPattern
                    }
                },
                "SymbolPinName" : {
                    "text" : {
                        "color"     : PaletteLightMono.SymbolPinName,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "SymbolPinComment" : {
                    "text" : {
                        "color"     : PaletteLightMono.SymbolPinComment,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "PropertyText" : {
                    "text" : {
                        "color"     : PaletteLightMono.PropertyText,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "Line" : {
                    "line" : {
                        "color" : PaletteLightMono.Line,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "Rectangle" : {
                    "line" : {
                        "color" : PaletteLightMono.Rectangle,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteLightMono.Rectangle,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "Ellipse" : {
                    "line" : {
                        "color" : PaletteLightMono.Ellipse,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : PaletteLightMono.Ellipse,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "Polyline" : {
                    "line" : {
                        "color" : PaletteLightMono.Polyline,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "Text" : {
                    "text" : {
                        "color"     : PaletteLightMono.Text,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                }
            },
            "selected" : {
                "line" : PaletteLightMono.SelectedLine,
                "fill" : PaletteLightMono.SelectedFill,
                "text" : PaletteLightMono.SelectedText
            },
            "grip" : {
                "size"  : 12,
                "color" : PaletteLightMono.Grip
            },
            "grid" : {
                "line" : PaletteLightMono.Grid
            },
            "properties" : {
                "deleted" : {
                    "color" : PaletteLightMono.PropertyDeleted
                },
                "changed" : {
                    "color" : PaletteLightMono.PropertyChanged
                },
                "added" : {
                    "color" : PaletteLightMono.PropertyAdded
                }
            }
        }
    }
}

class Settings(QObject):
    # instance attributes
    _settings : dict[str, Any]

    # signals
    changed = pyqtSignal()
    mruChanged = pyqtSignal()

    def __init__(self : Self) -> None:
        super().__init__()
        self._settings = self._deepCopy(FACTORY_SETTINGS)

    def get(self : Self, path : str) -> Any:
        theme = self._get(self._settings, "display/theme")
        path = f"/{path}".replace("/theme/", f"/themes/{theme}/").strip("/")
        value = self._get(self._settings, path)
        return self._toNamespace(value) if isinstance(value, dict) else value

    def getMRU(self : Self) -> list[str]:
        r = []
        for i in range(1, 10):
            mru = self.get(f"mru/{i}")
            if mru:
                r.append(mru)
        return r

    def addMRU(self : Self, file_name : str) -> None:
        old_mru = self.getMRU()  # existing list
        new_mru = [file_name]
        for entry in old_mru:
            if entry != file_name:
                new_mru.append(entry)
        for i in range(1, 10):
            if i - 1 < len(new_mru):
                self.set(f"mru/{i}", new_mru[i - 1], emit=False)
            else:
                self.set(f"mru/{i}", "", emit=False)
        self.mruChanged.emit()

    def set(self : Self, path : str, value : Any, emit : bool = True) -> None:
        tn = type(value).__name__
        tnx = self._getSettingKind(path) # type name expected
        if tn != tnx:
            logger().warning(
                f"Bad type for setting {path} - expected {tnx} but got {tn}"
            )
            return
        self._set(self._settings, path, value)
        if emit:
            self.changed.emit()

    def reset(self : Self) -> None:
        """Clear all saved settings from QSettings."""
        logger().info("Clearing all persistent settings")
        qsettings = QSettings(ORG_NAME, APP_NAME)
        qsettings.clear()
        self._settings = self._deepCopy(FACTORY_SETTINGS)
        self.changed.emit()

    def load(self : Self) -> None:
        """Load settings from QSettings into the settings store."""
        logger().debug("Loading settings")
        qsettings = QSettings(ORG_NAME, APP_NAME)
        for group in FACTORY_SETTINGS.keys():
            qsettings.beginGroup(group)
            self._load(self._settings[group], qsettings, group)
            qsettings.endGroup()
        self.changed.emit()

    def save(self : Self) -> None:
        """Save settings to QSettings storage."""
        logger().debug("Saving settings")
        qsettings = QSettings(ORG_NAME, APP_NAME)
        for group, value in self._settings.items():
            qsettings.beginGroup(group)
            self._save(value, qsettings, group)
            qsettings.endGroup()

    def dump(self : Self) -> str:
        """Return a formatted string representation of all settings."""
        lines: list[str] = []
        self._dump("settings", self._settings, lines)
        return "\n".join(lines)

    def _deepCopy(self : Self, d : dict) -> dict:
        """Create a deep copy of a settings dictionary."""
        result = {}
        for k, v in d.items():
            if isinstance(v, dict):
                result[k] = self._deepCopy(v)
            else:
                result[k] = v
        return result

    def _get(self : Self, d : dict, path : str) -> Any:
        """Retrieve a nested value from a dictionary by path."""
        path_parts = path.strip("/").split("/")
        current = d
        for part in path_parts:
            if not isinstance(current, dict) or part not in current:
                raise KeyError(f"Invalid settings path: {'/'.join(path_parts)}")
            current = current[part]
        return current

    def _set(self : Self, d : dict, path : str, value : Any) -> None:
        """Set a nested value in a dictionary by path."""
        path_parts = path.strip("/").split("/")
        current = d
        for part in path_parts[:-1]:
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        current[path_parts[-1]] = value

    def _getSettingKind(self : Self, path : str) -> str | None:
        """Determine the expected type of a setting based on FACTORY_SETTINGS."""
        value = self._get(FACTORY_SETTINGS, path)
        return None if isinstance(value, dict) else type(value).__name__

    def _load(
        self      : Self,
        settings  : dict,
        qsettings : QSettings,
        path      : str
    ) -> None:
        """Recursively load settings from QSettings."""
        for group in qsettings.childGroups():
            settings[group] = {}
            qsettings.beginGroup(group)
            self._load(settings[group], qsettings, f"{path}/{group}")
            qsettings.endGroup()
        for key in qsettings.childKeys():
            value = qsettings.value(key)
            if value is not None:
                full_path = f"{path}/{key}"
                kind = self._getSettingKind(full_path)
                if kind is not None:
                    logger().debug(f"Loading setting: {full_path} = {value} ({kind})")
                    settings[key] = str2val(value, kind)
                else:
                    logger().warning(f"Unknown setting: {full_path}")

    def _save(
        self      : Self,
        settings  : dict,
        qsettings : QSettings,
        path      : str
    ) -> None:
        """Recursively save settings to QSettings."""
        for key, value in settings.items():
            if isinstance(value, dict):
                qsettings.beginGroup(key)
                self._save(value, qsettings, f"{path}/{key}")
                qsettings.endGroup()
            else:
                full_path = f"{path}/{key}"
                logger().debug(f"Saving setting: {full_path} = {value}")
                qsettings.setValue(key, val2str(value))

    def _toNamespace(self : Self, d : dict) -> SimpleNamespace:
        """Convert a dictionary to a SimpleNamespace."""
        ns = SimpleNamespace()
        for key, value in d.items():
            if isinstance(value, dict):
                setattr(ns, key, self._toNamespace(value))
            else:
                setattr(ns, key, value)
        return ns

    def _dump(
        self   : Self,
        name   : str,
        x      : Any,
        lines  : list[str],
        indent : str = "  "
    ) -> None:
        """Recursively dump settings to a list of strings."""
        if isinstance(x, dict):
            for k, v in x.items():
                if isinstance(v, dict):
                    lines.append(f"{indent}{name}/{k}:")
                    self._dump(f"{name}/{k}", v, lines, indent + "  ")
                else:
                    lines.append(f"{indent}{name}/{k} = {val2str(v)}")
        else:
            lines.append(f"{indent}{name} = {val2str(x)}")
