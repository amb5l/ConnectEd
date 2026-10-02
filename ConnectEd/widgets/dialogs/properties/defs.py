from __future__ import annotations

from typing          import Self, Any
from collections.abc import Callable
from dataclasses     import dataclass

from ....core.types import DataKind

from ...graphics.properties import Property

from ...graphics.items.label import LabelItem


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
    getter : Callable[[LabelItem], Any]

    def editable(self : Self) -> bool:
        return True


_FIELD_SPECS = [

    PropertyFieldSpec ( "Name"    , DataKind.STR   , Property.name     ),
    PropertyFieldSpec ( "Custom"  , DataKind.BOOL  , Property.isCustom ),
    PropertyFieldSpec ( "Kind"    , DataKind.KIND  , Property.kind     ),
    PropertyFieldSpec ( "Value"   , DataKind.DUMMY , Property.value    ),

    DisplayFieldSpec  ( "Visible"    , DataKind.BOOL        , LabelItem.isVisible     ),
    DisplayFieldSpec  ( "Cleat"      , DataKind.DUMMY       , LabelItem.cleat         ),
    DisplayFieldSpec  ( "X"          , DataKind.FLOAT       , LabelItem.x             ),
    DisplayFieldSpec  ( "Y"          , DataKind.FLOAT       , LabelItem.y             ),
    DisplayFieldSpec  ( "Rotation"   , DataKind.FLOAT       , LabelItem.rotation      ),
    DisplayFieldSpec  ( "Mirror H"   , DataKind.BOOL        , LabelItem.mirrorH       ),
    DisplayFieldSpec  ( "Mirror V"   , DataKind.BOOL        , LabelItem.mirrorV       ),
    DisplayFieldSpec  ( "Autoflip"   , DataKind.BOOL        , LabelItem.autoflip      ),
    DisplayFieldSpec  ( "Origin"     , DataKind.RECT_HANDLE , LabelItem.origin        ),
    DisplayFieldSpec  ( "Align H"    , DataKind.ALIGN_H     , LabelItem.alignH        ),
    DisplayFieldSpec  ( "Align V"    , DataKind.ALIGN_V     , LabelItem.alignV        ),
    DisplayFieldSpec  ( "Width"      , DataKind.FLOAT       , LabelItem.width         ),
    DisplayFieldSpec  ( "Height"     , DataKind.FLOAT       , LabelItem.height        ),
    DisplayFieldSpec  ( "Pad Left"   , DataKind.FLOAT       , LabelItem.padLeft       ),
    DisplayFieldSpec  ( "Pad Right"  , DataKind.FLOAT       , LabelItem.padRight      ),
    DisplayFieldSpec  ( "Pad Top"    , DataKind.FLOAT       , LabelItem.padTop        ),
    DisplayFieldSpec  ( "Pad Bottom" , DataKind.FLOAT       , LabelItem.padBottom     ),
    DisplayFieldSpec  ( "Color"      , DataKind.COLOR       , LabelItem.textColor     ),
    DisplayFieldSpec  ( "Font"       , DataKind.FONT_FAMILY , LabelItem.textFont      ),
    DisplayFieldSpec  ( "Size"       , DataKind.FONT_SIZE   , LabelItem.textSize      ),
    DisplayFieldSpec  ( "Bold"       , DataKind.BOOL        , LabelItem.textBold      ),
    DisplayFieldSpec  ( "Italic"     , DataKind.BOOL        , LabelItem.textItalic    ),
    DisplayFieldSpec  ( "Underline"  , DataKind.BOOL        , LabelItem.textUnderline )

]
