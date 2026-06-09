from dataclasses import dataclass

from PyQt6.QtGui import QColor, QColorConstants


@dataclass
class ThemePalette:
    Background           : QColor
    Origin               : QColor
    Sheet                : QColor
    Border               : QColor
    Grid                 : QColor
    FreeNodeUnconnected  : QColor
    FreeNodeConnected    : QColor
    FreeNodeJunction     : QColor
    FixedNodeUnconnected : QColor
    FixedNodeConnected   : QColor
    FixedNodeJunction    : QColor
    SegmentOrthogonal    : QColor
    SegmentDiagonal      : QColor
    SegmentPreview1      : QColor
    SegmentPreview2      : QColor
    TapUnresolved        : QColor
    TapWire              : QColor
    TapBus               : QColor
    NetLabel             : QColor
    PortPinWire          : QColor
    PortPinBus           : QColor
    PortArrowLine        : QColor
    PortArrowFill        : QColor
    PortName             : QColor
    PortComment          : QColor
    GateLine             : QColor
    GateFill             : QColor
    GatePinWire          : QColor
    GatePinBus           : QColor
    GatePinArrowLine     : QColor
    GatePinArrowFill     : QColor
    BlockLine            : QColor
    BlockFill            : QColor
    BlockLabel           : QColor
    BlockName            : QColor
    BlockPinWire         : QColor
    BlockPinBus          : QColor
    BlockPinArrowLine    : QColor
    BlockPinArrowFill    : QColor
    BlockPinName         : QColor
    BlockPinComment      : QColor
    SymbolPinWire        : QColor
    SymbolPinBus         : QColor
    SymbolPinArrowLine   : QColor
    SymbolPinArrowFill   : QColor
    SymbolPinName        : QColor
    SymbolPinComment     : QColor
    PropertyText         : QColor
    NetLabel             : QColor
    Junction             : QColor
    Line                 : QColor
    Rectangle            : QColor
    Ellipse              : QColor
    PolyVtx              : QColor
    Polyline             : QColor
    Text                 : QColor
    SelectedLine         : QColor
    SelectedFill         : QColor
    SelectedText         : QColor
    Grip                 : QColor
    Rubber               : QColor
    PropertyDeleted      : QColor
    PropertyChanged      : QColor
    PropertyAdded        : QColor


black          = QColor("#000000")

very_dark_gray = QColor("#202020")

dark_red       = QColor("#400000")
dark_yellow    = QColor("#404000")
dark_green     = QColor("#004000")
dark_cyan      = QColor("#004040")
dark_blue      = QColor("#000040")
dark_magenta   = QColor("#400040")
dark_gray      = QColor("#404040")

mid_red        = QColor("#800000")
mid_yellow     = QColor("#808000")
mid_green      = QColor("#008000")
mid_cyan       = QColor("#008080")
mid_blue       = QColor("#000080")
mid_magenta    = QColor("#800080")
mid_gray       = QColor("#808080")

light_red      = QColor("#C00000")
light_yellow   = QColor("#C0C000")
light_green    = QColor("#00C000")
light_cyan     = QColor("#00C0C0")
light_blue     = QColor("#0000C0")
light_magenta  = QColor("#C000C0")
light_gray     = QColor("#C0C0C0")

bright_red     = QColor("#FF0000")
bright_yellow  = QColor("#FFFF00")
bright_green   = QColor("#00FF00")
bright_cyan    = QColor("#00FFFF")
bright_blue    = QColor("#0000FF")
bright_magenta = QColor("#FF00FF")
bright_white   = QColor("#FFFFFF")


palette_dark = ThemePalette(
    Background           = black,
    Origin               = bright_white,
    Sheet                = very_dark_gray,
    Border               = mid_gray,
    Grid                 = dark_gray,
    FreeNodeUnconnected  = bright_yellow,
    FreeNodeConnected    = bright_yellow,
    FreeNodeJunction     = bright_red,
    FixedNodeUnconnected = bright_yellow,
    FixedNodeConnected   = bright_yellow,
    FixedNodeJunction    = bright_red,
    SegmentOrthogonal    = dark_green,
    SegmentDiagonal      = bright_yellow,
    SegmentPreview1      = light_magenta,
    SegmentPreview2      = mid_magenta,
    TapUnresolved        = dark_yellow,
    TapWire              = dark_green,
    TapBus               = dark_green,
    NetLabel             = dark_cyan,
    PortPinWire          = mid_gray,
    PortPinBus           = mid_gray,
    PortArrowLine        = mid_gray,
    PortArrowFill        = mid_yellow,
    PortName             = mid_yellow,
    PortComment          = mid_yellow,
    GateLine             = mid_gray,
    GateFill             = dark_gray,
    GatePinWire          = mid_gray,
    GatePinBus           = mid_gray,
    GatePinArrowLine     = mid_yellow,
    GatePinArrowFill     = mid_yellow,
    BlockLine            = mid_gray,
    BlockFill            = dark_gray,
    BlockLabel           = mid_cyan,
    BlockName            = mid_cyan,
    BlockPinWire         = mid_gray,
    BlockPinBus          = mid_gray,
    BlockPinArrowLine    = mid_yellow,
    BlockPinArrowFill    = mid_yellow,
    BlockPinName         = mid_yellow,
    BlockPinComment      = mid_yellow,
    SymbolPinWire        = mid_gray,
    SymbolPinBus         = mid_gray,
    SymbolPinArrowLine   = mid_yellow,
    SymbolPinArrowFill   = mid_yellow,
    SymbolPinName        = mid_yellow,
    SymbolPinComment     = mid_yellow,
    PropertyText         = mid_red,
    Junction             = light_red,
    Line                 = light_gray,
    Rectangle            = light_gray,
    Ellipse              = light_gray,
    PolyVtx              = light_gray,
    Polyline             = light_gray,
    Text                 = light_gray,
    SelectedLine         = bright_magenta,
    SelectedFill         = bright_magenta,
    SelectedText         = bright_magenta,
    Grip                 = bright_magenta,
    Rubber               = bright_yellow,
    PropertyDeleted      = dark_red,
    PropertyChanged      = dark_yellow,
    PropertyAdded        = dark_green,
)


palette_light_mono = ThemePalette(
    Background           = very_dark_gray,
    Origin               = black,
    Sheet                = bright_white,
    Border               = black,
    Grid                 = light_gray,
    FreeNodeUnconnected  = black,
    FreeNodeConnected    = black,
    FreeNodeJunction     = black,
    FixedNodeUnconnected = black,
    FixedNodeConnected   = black,
    FixedNodeJunction    = black,
    SegmentOrthogonal    = black,
    SegmentDiagonal      = bright_yellow,
    SegmentPreview1      = very_dark_gray,
    SegmentPreview2      = dark_gray,
    TapUnresolved        = black,
    TapWire              = black,
    TapBus               = black,
    PortPinWire          = black,
    PortPinBus           = black,
    PortArrowLine        = black,
    PortArrowFill        = bright_white,
    PortName             = black,
    PortComment          = black,
    GateLine             = black,
    GateFill             = bright_white,
    GatePinWire          = black,
    GatePinBus           = black,
    GatePinArrowLine     = black,
    GatePinArrowFill     = bright_white,
    BlockLine            = black,
    BlockFill            = bright_white,
    BlockLabel           = black,
    BlockName            = black,
    BlockPinWire         = black,
    BlockPinBus          = black,
    BlockPinArrowLine    = black,
    BlockPinArrowFill    = bright_white,
    BlockPinName         = black,
    BlockPinComment      = black,
    SymbolPinWire        = black,
    SymbolPinBus         = black,
    SymbolPinArrowLine   = black,
    SymbolPinArrowFill   = bright_white,
    SymbolPinName        = black,
    SymbolPinComment     = black,
    PropertyText         = black,
    NetLabel             = black,
    Junction             = black,
    Line                 = black,
    Rectangle            = black,
    Ellipse              = black,
    PolyVtx              = black,
    Polyline             = black,
    Text                 = black,
    SelectedLine         = bright_magenta,
    SelectedFill         = bright_magenta,
    SelectedText         = bright_magenta,
    Grip                 = bright_magenta,
    Rubber               = bright_yellow,
    PropertyDeleted      = bright_red,
    PropertyChanged      = bright_yellow,
    PropertyAdded        = bright_green,
)


__all__ = [
    "palette_dark",
    "palette_light_mono",
]
