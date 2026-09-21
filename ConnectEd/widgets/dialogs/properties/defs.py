from __future__ import annotations

from typing          import Self, Any
from dataclasses     import dataclass
from collections.abc import Callable

from ....core.types import DataKind

from ...graphics.properties import Property

from ...graphics.items.property_text import PropertyTextItem


@dataclass
class FieldSpec:
    label : str


@dataclass
class PropertyFieldSpec(FieldSpec):
    kind   : DataKind
    getter : Callable[[Property], Any]

    def editable(self : Self, custom : bool) -> bool:
        return self.label != "Custom" and \
            ((self.label != "Name" and self.label != "Kind") or custom)


@dataclass
class DisplayFieldSpec(FieldSpec):
    kind   : DataKind
    getter : Callable[[PropertyTextItem], Any]

    def editable(self : Self) -> bool:
        return True


_FIELD_SPECS = [

    PropertyFieldSpec ( "Name"    , DataKind.STR   , Property.name     ),
    PropertyFieldSpec ( "Custom"  , DataKind.BOOL  , Property.isCustom ),
    PropertyFieldSpec ( "Kind"    , DataKind.KIND  , Property.kind     ),
    PropertyFieldSpec ( "Value"   , DataKind.DUMMY , Property.value    ),
    PropertyFieldSpec ( "Display" , DataKind.BOOL  , Property.display  ),

    DisplayFieldSpec  ( "Visible"    , DataKind.BOOL        , PropertyTextItem.isVisible     ),
    DisplayFieldSpec  ( "Cleat"      , DataKind.DUMMY       , PropertyTextItem.cleat         ),
    DisplayFieldSpec  ( "X"          , DataKind.FLOAT       , PropertyTextItem.x             ),
    DisplayFieldSpec  ( "Y"          , DataKind.FLOAT       , PropertyTextItem.y             ),
    DisplayFieldSpec  ( "Rotation"   , DataKind.FLOAT       , PropertyTextItem.rotation      ),
    DisplayFieldSpec  ( "Mirror H"   , DataKind.BOOL        , PropertyTextItem.mirrorH       ),
    DisplayFieldSpec  ( "Mirror V"   , DataKind.BOOL        , PropertyTextItem.mirrorV       ),
    DisplayFieldSpec  ( "Autoflip"   , DataKind.BOOL        , PropertyTextItem.autoflip      ),
    DisplayFieldSpec  ( "Origin"     , DataKind.RECT_HANDLE , PropertyTextItem.origin        ),
    DisplayFieldSpec  ( "Align H"    , DataKind.ALIGN_H     , PropertyTextItem.alignH        ),
    DisplayFieldSpec  ( "Align V"    , DataKind.ALIGN_V     , PropertyTextItem.alignV        ),
    DisplayFieldSpec  ( "Width"      , DataKind.FLOAT       , PropertyTextItem.width         ),
    DisplayFieldSpec  ( "Height"     , DataKind.FLOAT       , PropertyTextItem.height        ),
    DisplayFieldSpec  ( "Pad Left"   , DataKind.FLOAT       , PropertyTextItem.padLeft       ),
    DisplayFieldSpec  ( "Pad Right"  , DataKind.FLOAT       , PropertyTextItem.padRight      ),
    DisplayFieldSpec  ( "Pad Top"    , DataKind.FLOAT       , PropertyTextItem.padTop        ),
    DisplayFieldSpec  ( "Pad Bottom" , DataKind.FLOAT       , PropertyTextItem.padBottom     ),
    DisplayFieldSpec  ( "Color"      , DataKind.COLOR       , PropertyTextItem.textColor     ),
    DisplayFieldSpec  ( "Font"       , DataKind.FONT_FAMILY , PropertyTextItem.textFont      ),
    DisplayFieldSpec  ( "Size"       , DataKind.FONT_SIZE   , PropertyTextItem.textSize      ),
    DisplayFieldSpec  ( "Bold"       , DataKind.BOOL        , PropertyTextItem.textBold      ),
    DisplayFieldSpec  ( "Italic"     , DataKind.BOOL        , PropertyTextItem.textItalic    ),
    DisplayFieldSpec  ( "Underline"  , DataKind.BOOL        , PropertyTextItem.textUnderline )

]
