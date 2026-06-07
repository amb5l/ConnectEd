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

from .check   import checked
from .defs    import ORG_NAME, APP_NAME, DEFS
from .utils   import getDefaultPath, val2str, str2val
from .palette import palette_dark, palette_light_mono


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
    "ai" : {
        "profiles_data"       : "[]",
        "default_profile"     : "",
        "system_prompt_extra" : "",
        "confirm_destructive" : True,
        "max_tool_rounds"     : 10,
        "chat_mru"            : "[]",
    },
    "themes" : {
        "dark" : {
            "background" : palette_dark.Background,
            "origin" : {
                "color" : palette_dark.Origin,
                "size"  : 12
            },
            "sheet"      : palette_dark.Sheet,
            "border"     : palette_dark.Border,
            "items" : {
                "FreeNode" : {
                    "size" : 3,
                    "unconnected" : {
                        "line" : {
                            "color" : palette_dark.FreeNodeUnconnected,
                            "width" : 0,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : palette_dark.FreeNodeUnconnected,
                            "style" : Qt.BrushStyle.NoBrush
                        }
                    },
                    "connected" : {
                        "line" : {
                            "color" : palette_dark.FreeNodeConnected,
                            "width" : 0,
                            "style" : Qt.PenStyle.NoPen
                        },
                        "fill" : {
                            "color" : palette_dark.FreeNodeConnected,
                            "style" : Qt.BrushStyle.NoBrush
                        }
                    },
                    "junction" : {
                        "line" : {
                            "color" : palette_dark.FreeNodeJunction,
                            "width" : 0,
                            "style" : Qt.PenStyle.NoPen
                        },
                        "fill" : {
                            "color" : palette_dark.FreeNodeJunction,
                            "style" : Qt.BrushStyle.SolidPattern
                        }
                    }
                },
                "FixedNode" : {
                    "size" : 3,
                    "unconnected" : {
                        "line" : {
                            "color" : palette_dark.FixedNodeUnconnected,
                            "width" : 0,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : palette_dark.FixedNodeUnconnected,
                            "style" : Qt.BrushStyle.NoBrush
                        }
                    },
                    "connected" : {
                        "line" : {
                            "color" : palette_dark.FixedNodeConnected,
                            "width" : 0,
                            "style" : Qt.PenStyle.NoPen
                        },
                        "fill" : {
                            "color" : palette_dark.FixedNodeConnected,
                            "style" : Qt.BrushStyle.NoBrush
                        }
                    },
                    "junction" : {
                        "line" : {
                            "color" : palette_dark.FixedNodeJunction,
                            "width" : 0,
                            "style" : Qt.PenStyle.NoPen
                        },
                        "fill" : {
                            "color" : palette_dark.FixedNodeJunction,
                            "style" : Qt.BrushStyle.SolidPattern
                        }
                    }
                },
                "Segment" : {
                    "line" : {
                        "orthogonal" : {
                            "color" : palette_dark.SegmentOrthogonal,
                            "width" : 1,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "diagonal" : {
                            "color" : palette_dark.SegmentDiagonal,
                            "width" : 1,
                            "style" : Qt.PenStyle.DashLine
                        }
                    }
                },
                "SegmentPreview1" : {
                    "line" : {
                        "color" : palette_dark.SegmentPreview1,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "SegmentPreview2" : {
                    "line" : {
                        "color" : palette_dark.SegmentPreview2,
                        "width" : 1,
                        "style" : Qt.PenStyle.DashDotDotLine
                    }
                },
                "Tap" : {
                    "line" : {
                        "unresolved" : {
                            "color" : palette_dark.TapUnresolved,
                            "width" : 1,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "wire" : {
                            "color" : palette_dark.TapWire,
                            "width" : 1,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "bus" : {
                            "color" : palette_dark.TapBus,
                            "width" : 2,
                            "style" : Qt.PenStyle.SolidLine
                        }
                    }
                },
                "NetLabel" : {
                    "text" : {
                        "color"     : palette_dark.NetLabel,
                        "font"      : "Liberation Sans",
                        "size"      : 5,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "Port" : {
                    "pin" : {
                        "wire" : {
                            "line" : {
                                "color" : palette_dark.PortPinWire,
                                "width" : 1,
                                "style" : Qt.PenStyle.SolidLine
                            }
                        },
                        "bus" : {
                            "line" : {
                                "color" : palette_dark.PortPinBus,
                                "width" : 2,
                                "style" : Qt.PenStyle.SolidLine
                            }
                        }
                    },
                    "arrow" : {
                        "size" : 6,
                        "line" : {
                            "color" : palette_dark.PortArrowLine,
                            "width" : 1,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : palette_dark.PortArrowFill,
                            "style" : Qt.BrushStyle.SolidPattern
                        }
                    }
                },
                "PortName" : {
                    "text" : {
                        "color"     : palette_dark.PortName,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "PortComment" : {
                    "text" : {
                        "color"     : palette_dark.PortComment,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "Gate" : {
                    "line" : {
                        "color" : palette_dark.GateLine,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : palette_dark.GateFill,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "GatePin" : {
                    "pin" : {
                        "wire" : {
                            "line" : {
                                "color" : palette_dark.GatePinWire,
                                "width" : 1,
                                "style" : Qt.PenStyle.SolidLine
                            }
                        },
                        "bus" : {
                            "line" : {
                                "color" : palette_dark.GatePinBus,
                                "width" : 2,
                                "style" : Qt.PenStyle.SolidLine
                            }
                        },
                        "dot" : {
                            "size" : 2.5
                        },
                        "clock" : {
                            "size" : 2.5
                        }
                    },
                    "arrow" : {
                        "size" : 3,
                        "line" : {
                            "color" : palette_dark.GatePinArrowLine,
                            "width" : 0.5,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : palette_dark.GatePinArrowFill,
                            "style" : Qt.BrushStyle.SolidPattern
                        }
                    }
                },
                "Block" : {
                    "line" : {
                        "color" : palette_dark.BlockLine,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : palette_dark.BlockFill,
                        "style" : Qt.BrushStyle.SolidPattern
                    }
                },
                "BlockLabel" : {
                    "text" : {
                        "color"     : palette_dark.BlockLabel,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "BlockName" : {
                    "text" : {
                        "color"     : palette_dark.BlockName,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "BlockPin" : {
                    "pin" : {
                        "wire" : {
                            "line" : {
                                "color" : palette_dark.BlockPinWire,
                                "width" : 1,
                                "style" : Qt.PenStyle.SolidLine
                            }
                        },
                        "bus" : {
                            "line" : {
                                "color" : palette_dark.BlockPinBus,
                                "width" : 2,
                                "style" : Qt.PenStyle.SolidLine
                            }
                        }
                    },
                    "arrow" : {
                        "size" : 6,
                        "line" : {
                            "color" : palette_dark.BlockPinArrowLine,
                            "width" : 1,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : palette_dark.BlockPinArrowFill,
                            "style" : Qt.BrushStyle.SolidPattern
                        }
                    }
                },
                "BlockPinName" : {
                    "text" : {
                        "color"     : palette_dark.BlockPinName,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "BlockPinComment" : {
                    "text" : {
                        "color"     : palette_dark.BlockPinComment,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "SymbolPin" : {
                    "pin" : {
                        "wire" : {
                            "line" : {
                                "color" : palette_dark.SymbolPinWire,
                                "width" : 1,
                                "style" : Qt.PenStyle.SolidLine
                            }
                        },
                        "bus" : {
                            "line" : {
                                "color" : palette_dark.SymbolPinBus,
                                "width" : 2,
                                "style" : Qt.PenStyle.SolidLine
                            }
                        },
                        "dot" : {
                            "size" : 2.5
                        },
                        "clock" : {
                            "size" : 2.5
                        }
                    },
                    "arrow" : {
                        "size" : 3,
                        "line" : {
                            "color" : palette_dark.SymbolPinArrowLine,
                            "width" : 0.5,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : palette_dark.SymbolPinArrowFill,
                            "style" : Qt.BrushStyle.SolidPattern
                        }
                    }
                },
                "SymbolPinName" : {
                    "text" : {
                        "color"     : palette_dark.SymbolPinName,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "SymbolPinComment" : {
                    "text" : {
                        "color"     : palette_dark.SymbolPinComment,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "PropertyText" : {
                    "text" : {
                        "color"     : palette_dark.PropertyText,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "NetLabel" : {
                    "text" : {
                        "color"     : palette_dark.NetLabel,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "Line" : {
                    "line" : {
                        "color" : palette_dark.Line,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "Rectangle" : {
                    "line" : {
                        "color" : palette_dark.Rectangle,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : palette_dark.Rectangle,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "Ellipse" : {
                    "line" : {
                        "color" : palette_dark.Ellipse,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : palette_dark.Ellipse,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "Polyline" : {
                    "line" : {
                        "color" : palette_dark.Polyline,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : palette_dark.Polyline,
                        "style" : Qt.BrushStyle.NoBrush
                    }

                },
                "Text" : {
                    "text" : {
                        "color"     : palette_dark.Text,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                }
            },
            "selected" : {
                "line" : palette_dark.SelectedLine,
                "fill" : palette_dark.SelectedFill,
                "text" : palette_dark.SelectedText
            },
            "grip" : {
                "size"  : 12,
                "line" : {
                    "color" : palette_dark.Grip,
                    "width" : 0,
                    "style" : Qt.PenStyle.NoPen
                },
                "fill" : {
                    "color" : palette_dark.Grip,
                    "style" : Qt.BrushStyle.SolidPattern
                }
            },
            "tether" : {
                "line" : {
                    "color" : palette_dark.SelectedLine,
                    "width" : 0,
                    "style" : Qt.PenStyle.DotLine
                }
            },
            "grid" : {
                "line" : palette_dark.Grid
            },
            "properties" : {
                "deleted" : {
                    "color" : palette_dark.PropertyDeleted
                },
                "changed" : {
                    "color" : palette_dark.PropertyChanged
                },
                "added" : {
                    "color" : palette_dark.PropertyAdded
                }
            }
        },
        "light_mono" : {
            "background" : palette_light_mono.Background,
            "origin" : {
                "color" : palette_light_mono.Origin,
                "size"  : 12
            },
            "sheet"      : palette_light_mono.Sheet,
            "border"     : palette_light_mono.Border,
            "items" : {
                "FreeNode" : {
                    "size" : 3,
                    "unconnected" : {
                        "line" : {
                            "color" : palette_light_mono.FreeNodeUnconnected,
                            "width" : 0,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : palette_light_mono.FreeNodeUnconnected,
                            "style" : Qt.BrushStyle.NoBrush
                        }
                    },
                    "connected" : {
                        "line" : {
                            "color" : palette_light_mono.FreeNodeConnected,
                            "width" : 0,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : palette_light_mono.FreeNodeConnected,
                            "style" : Qt.BrushStyle.NoBrush
                        }
                    },
                    "junction" : {
                        "line" : {
                            "color" : palette_light_mono.FreeNodeJunction,
                            "width" : 0,
                            "style" : Qt.PenStyle.NoPen
                        },
                        "fill" : {
                            "color" : palette_light_mono.FreeNodeJunction,
                            "style" : Qt.BrushStyle.SolidPattern
                        }
                    }
                },
                "FixedNode" : {
                    "size" : 3,
                    "unconnected" : {
                        "line" : {
                            "color" : palette_light_mono.FixedNodeUnconnected,
                            "width" : 0,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : palette_light_mono.FixedNodeUnconnected,
                            "style" : Qt.BrushStyle.NoBrush
                        }
                    },
                    "connected" : {
                        "line" : {
                            "color" : palette_light_mono.FixedNodeConnected,
                            "width" : 0,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : palette_light_mono.FixedNodeConnected,
                            "style" : Qt.BrushStyle.NoBrush
                        }
                    },
                    "junction" : {
                        "line" : {
                            "color" : palette_light_mono.FixedNodeJunction,
                            "width" : 0,
                            "style" : Qt.PenStyle.NoPen
                        },
                        "fill" : {
                            "color" : palette_light_mono.FixedNodeJunction,
                            "style" : Qt.BrushStyle.SolidPattern
                        }
                    }
                },
                "Segment" : {
                    "line" : {
                        "orthogonal" : {
                            "color" : palette_light_mono.SegmentOrthogonal,
                            "width" : 1,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "diagonal" : {
                            "color" : palette_light_mono.SegmentDiagonal,
                            "width" : 1,
                            "style" : Qt.PenStyle.DashLine
                        }
                    }
                },
                "SegmentPreview1" : {
                    "line" : {
                        "color" : palette_light_mono.SegmentPreview1,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "SegmentPreview2" : {
                    "line" : {
                        "color" : palette_light_mono.SegmentPreview2,
                        "width" : 1,
                        "style" : Qt.PenStyle.DashDotDotLine
                    }
                },
                "Tap" : {
                    "line" : {
                        "unresolved" : {
                            "color" : palette_dark.TapUnresolved,
                            "width" : 1,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "wire" : {
                            "color" : palette_dark.TapWire,
                            "width" : 1,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "bus" : {
                            "color" : palette_dark.TapBus,
                            "width" : 2,
                            "style" : Qt.PenStyle.SolidLine
                        }
                    }
                },
                "NetLabel" : {
                    "text" : {
                        "color"     : palette_light_mono.NetLabel,
                        "font"      : "Liberation Sans",
                        "size"      : 5,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "Port" : {
                    "pin" : {
                        "wire" : {
                            "line" : {
                                "color" : palette_light_mono.PortPinWire,
                                "width" : 1,
                                "style" : Qt.PenStyle.SolidLine
                            }
                        },
                        "bus" : {
                            "line" : {
                                "color" : palette_light_mono.PortPinBus,
                                "width" : 2,
                                "style" : Qt.PenStyle.SolidLine
                            }
                        }
                    },
                    "arrow" : {
                        "size" : 6,
                        "line" : {
                            "color" : palette_light_mono.PortArrowLine,
                            "width" : 1,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : palette_light_mono.PortArrowFill,
                            "style" : Qt.BrushStyle.SolidPattern
                        }
                    }
                },
                "PortName" : {
                    "text" : {
                        "color"     : palette_light_mono.PortName,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "PortComment" : {
                    "text" : {
                        "color"     : palette_light_mono.PortComment,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "Gate" : {
                    "line" : {
                        "color" : palette_light_mono.GateLine,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : palette_light_mono.GateFill,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "GatePin" : {
                    "pin" : {
                        "wire" : {
                            "line" : {
                                "color" : palette_light_mono.GatePinWire,
                                "width" : 1,
                                "style" : Qt.PenStyle.SolidLine
                            }
                        },
                        "bus" : {
                            "line" : {
                                "color" : palette_light_mono.GatePinBus,
                                "width" : 2,
                                "style" : Qt.PenStyle.SolidLine
                            }
                        },
                        "dot" : {
                            "size" : 2.5
                        },
                        "clock" : {
                            "size" : 2.5
                        }
                    },
                    "arrow" : {
                        "size" : 3,
                        "line" : {
                            "color" : palette_light_mono.GatePinArrowFill,
                            "width" : 0.5,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : palette_light_mono.GatePinArrowFill,
                            "style" : Qt.BrushStyle.SolidPattern
                        }
                    }
                },
                "Block" : {
                    "line" : {
                        "color" : palette_light_mono.BlockLine,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : palette_light_mono.BlockFill,
                        "style" : Qt.BrushStyle.SolidPattern
                    }
                },
                "BlockLabel" : {
                    "text" : {
                        "color"     : palette_light_mono.BlockLabel,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "BlockName" : {
                    "text" : {
                        "color"     : palette_light_mono.BlockName,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "BlockPin" : {
                    "pin" : {
                        "wire" : {
                            "line" : {
                                "color" : palette_light_mono.BlockPinWire,
                                "width" : 1,
                                "style" : Qt.PenStyle.SolidLine
                            }
                        },
                        "bus" : {
                            "line" : {
                                "color" : palette_light_mono.BlockPinBus,
                                "width" : 2,
                                "style" : Qt.PenStyle.SolidLine
                            }
                        }
                    },
                    "arrow" : {
                        "size" : 6,
                        "line" : {
                            "color" : palette_light_mono.BlockPinArrowLine,
                            "width" : 1,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : palette_light_mono.BlockPinArrowFill,
                            "style" : Qt.BrushStyle.SolidPattern
                        }
                    }
                },
                "BlockPinName" : {
                    "text" : {
                        "color"     : palette_light_mono.BlockPinName,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "BlockPinComment" : {
                    "text" : {
                        "color"     : palette_light_mono.BlockPinComment,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "SymbolPin" : {
                    "pin" : {
                        "wire" : {
                            "line" : {
                                "color" : palette_light_mono.SymbolPinWire,
                                "width" : 1,
                                "style" : Qt.PenStyle.SolidLine
                            }
                        },
                        "bus" : {
                            "line" : {
                                "color" : palette_light_mono.SymbolPinBus,
                                "width" : 2,
                                "style" : Qt.PenStyle.SolidLine
                            }
                        },
                        "dot" : {
                            "size" : 2.5
                        },
                        "clock" : {
                            "size" : 2.5
                        }
                    },
                    "arrow" : {
                        "size" : 3,
                        "line" : {
                            "color" : palette_light_mono.SymbolPinArrowLine,
                            "width" : 0.5,
                            "style" : Qt.PenStyle.SolidLine
                        },
                        "fill" : {
                            "color" : palette_light_mono.SymbolPinArrowFill,
                            "style" : Qt.BrushStyle.SolidPattern
                        }
                    }
                },
                "SymbolPinName" : {
                    "text" : {
                        "color"     : palette_light_mono.SymbolPinName,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "SymbolPinComment" : {
                    "text" : {
                        "color"     : palette_light_mono.SymbolPinComment,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "PropertyText" : {
                    "text" : {
                        "color"     : palette_light_mono.PropertyText,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "NetLabel" : {
                    "text" : {
                        "color"     : palette_light_mono.NetLabel,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                },
                "Line" : {
                    "line" : {
                        "color" : palette_light_mono.Line,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    }
                },
                "Rectangle" : {
                    "line" : {
                        "color" : palette_light_mono.Rectangle,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : palette_light_mono.Rectangle,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "Ellipse" : {
                    "line" : {
                        "color" : palette_light_mono.Ellipse,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : palette_light_mono.Ellipse,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "Polyline" : {
                    "line" : {
                        "color" : palette_light_mono.Polyline,
                        "width" : 1,
                        "style" : Qt.PenStyle.SolidLine
                    },
                    "fill" : {
                        "color" : palette_light_mono.Polyline,
                        "style" : Qt.BrushStyle.NoBrush
                    }
                },
                "Text" : {
                    "text" : {
                        "color"     : palette_light_mono.Text,
                        "font"      : "Liberation Sans",
                        "size"      : 7,
                        "bold"      : False,
                        "italic"    : False,
                        "underline" : False
                    }
                }
            },
            "selected" : {
                "line" : palette_light_mono.SelectedLine,
                "fill" : palette_light_mono.SelectedFill,
                "text" : palette_light_mono.SelectedText
            },
            "grip" : {
                "size"  : 12,
                "line" : {
                    "color" : palette_light_mono.Grip,
                    "width" : 0,
                    "style" : Qt.PenStyle.NoPen
                },
                "fill" : {
                    "color" : palette_light_mono.Grip,
                    "style" : Qt.BrushStyle.SolidPattern
                }
            },
            "tether" : {
                "line" : {
                    "color" : palette_light_mono.SelectedLine,
                    "width" : 0,
                    "style" : Qt.PenStyle.DotLine
                }
            },
            "grid" : {
                "line" : palette_light_mono.Grid
            },
            "properties" : {
                "deleted" : {
                    "color" : palette_light_mono.PropertyDeleted
                },
                "changed" : {
                    "color" : palette_light_mono.PropertyChanged
                },
                "added" : {
                    "color" : palette_light_mono.PropertyAdded
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

    @checked
    def __init__(self : Self) -> None:
        super().__init__()
        self._settings = self._deepCopy(FACTORY_SETTINGS)

    @checked
    def get(self : Self, path : str) -> Any:
        theme = self._get(self._settings, "display/theme")
        path = f"/{path}".replace("/theme/", f"/themes/{theme}/").strip("/")
        value = self._get(self._settings, path)
        return self._toNamespace(value) if isinstance(value, dict) else value

    @checked
    def getMRU(self : Self) -> list[str]:
        r = []
        for i in range(1, 10):
            mru = self.get(f"mru/{i}")
            if mru:
                r.append(mru)
        return r

    @checked
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

    @checked
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

    @checked
    def reset(self : Self) -> None:
        """Clear all saved settings from QSettings."""
        logger().info("Clearing all persistent settings")
        qsettings = QSettings(ORG_NAME, APP_NAME)
        qsettings.clear()
        self._settings = self._deepCopy(FACTORY_SETTINGS)
        self.changed.emit()

    @checked
    def load(self : Self) -> None:
        """Load settings from QSettings into the settings store."""
        logger().debug("Loading settings")
        qsettings = QSettings(ORG_NAME, APP_NAME)
        for group in FACTORY_SETTINGS.keys():
            qsettings.beginGroup(group)
            self._load(self._settings[group], qsettings, group)
            qsettings.endGroup()
        self.changed.emit()

    @checked
    def save(self : Self) -> None:
        """Save settings to QSettings storage."""
        logger().debug("Saving settings")
        qsettings = QSettings(ORG_NAME, APP_NAME)
        for group, value in self._settings.items():
            qsettings.beginGroup(group)
            self._save(value, qsettings, group)
            qsettings.endGroup()

    @checked
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
