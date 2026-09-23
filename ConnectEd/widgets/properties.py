from __future__ import annotations

from .table.row import TableRow

from .graphics.properties import PropertyPending

from .graphics.items.property_text import PropertyTextPending


def populateProperty(
    row   : TableRow,
    draft : PropertyPending,
    new   : bool = False
) -> None:
    # Imported here: dialogs.properties loads this module through the bush.
    from .dialogs.properties.item import PropertiesItem, PropertiesValueItem
    if draft.state is None:
        raise ValueError("Property draft state is None")
    if draft.obj is None:
        raise ValueError("Store property source is None")
    name     = draft.state.name
    kind     = draft.state.kind
    value    = draft.state.value
    custom   = draft.obj.isCustom()
    editable = draft.obj.writeable()
    p = PropertiesItem
    v = PropertiesValueItem
    row[ "Name"   ] = p(name, draft.state, "name", new, not custom)
    row[ "Custom" ] = p(custom, None, None, new, False)
    row[ "Type"   ] = p(kind, draft.state, "kind", new, not custom)
    row[ "Value"  ] = v(kind, value, draft.state, "value", new, editable)


def populatePropertyText(
    row   : TableRow,
    draft : PropertyTextPending,
    new   : bool = False
) -> None:
    from .dialogs.properties.item import PropertiesItem
    if draft.state is None:
        raise ValueError("Property text pending state is None")
    p = PropertiesItem
    c = draft.state
    row[ "Visible"    ] = p( c.visible    , c , "visible"    , new )
    row[ "Cleat"      ] = p( c.cleat      , c , "cleat"      , new )
    row[ "X"          ] = p( c.x          , c , "x"          , new )
    row[ "Y"          ] = p( c.y          , c , "y"          , new )
    row[ "Rotation"   ] = p( c.rotation   , c , "rotation"   , new )
    row[ "Mirror H"   ] = p( c.mirror_h   , c , "mirror_h"   , new )
    row[ "Mirror V"   ] = p( c.mirror_v   , c , "mirror_v"   , new )
    row[ "Autoflip"   ] = p( c.autoflip   , c , "autoflip"   , new )
    row[ "Origin"     ] = p( c.origin     , c , "origin"     , new )
    row[ "Align H"    ] = p( c.align_h    , c , "align_h"    , new )
    row[ "Align V"    ] = p( c.align_v    , c , "align_v"    , new )
    row[ "Width"      ] = p( c.width      , c , "width"      , new )
    row[ "Height"     ] = p( c.height     , c , "height"     , new )
    row[ "Pad Left"   ] = p( c.pad_left   , c , "pad_left"   , new )
    row[ "Pad Right"  ] = p( c.pad_right  , c , "pad_right"  , new )
    row[ "Pad Top"    ] = p( c.pad_top    , c , "pad_top"    , new )
    row[ "Pad Bottom" ] = p( c.pad_bottom , c , "pad_bottom" , new )
    row[ "Color"      ] = p( c.color      , c , "color"      , new )
    row[ "Font"       ] = p( c.font       , c , "font"       , new )
    row[ "Size"       ] = p( c.size       , c , "size"       , new )
    row[ "Bold"       ] = p( c.bold       , c , "bold"       , new )
    row[ "Italic"     ] = p( c.italic     , c , "italic"     , new )
    row[ "Underline"  ] = p( c.underline  , c , "underline"  , new )
