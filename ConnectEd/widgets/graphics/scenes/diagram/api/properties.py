from __future__ import annotations

from typing      import Self, Any
from dataclasses import fields

from PyQt6.QtGui import QColor

from ......app import logger

from ......core.check import checked
from ......core.types import NoChange, NO_CHANGE, AlignH, AlignV, \
                             HandleId, RectHandleId, DataKind

from ....properties import PropertyState, \
                           PropertyAdd, PropertyDelete, PropertyChange, \
                           PropertyAndTextsEdit

from ....items.property_text import PropertyTextState, PropertyTextChange, \
                                    PropertyTextAdd, PropertyTextDelete

from ..cmd import cmdExec

from ..cmd.edit.properties import (
    CmdAddProperty, CmdEditProperty, CmdDelProperty,
    CmdAddPropertyText, CmdEditPropertyText, CmdDelPropertyText
)

from ..host import asDiagramScene

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....items.property_text import PropertyTextItem
    from ....properties import PropertiesMixin, Property


def _textKwargs(
    source : PropertyTextState | PropertyTextChange
) -> dict[str, Any]:
    return {
        state_field.name : getattr(source, state_field.name)
        for state_field in fields(source)
        if state_field.name != "item"
    }


class DiagramSceneApiPropertiesMixin:
    @checked
    def addProperty(
        self     : Self,
        owner    : PropertiesMixin,
        name     : str,
        kind     : DataKind,
        value    : Any,
        undoable : bool = False
    ) -> Property | None:
        host = asDiagramScene(self)
        cmd = CmdAddProperty(owner, PropertyState(
            name  = name,
            value = value,
            kind  = kind
        ))
        if not hasattr(cmd, "_property"):
            return None
        cmdExec(host, cmd, undoable)
        return cmd.property()

    @checked
    def editProperty(
        self     : Self,
        owner    : PropertiesMixin,
        property : Property,
        name     : str      | NoChange = NO_CHANGE,
        kind     : DataKind | NoChange = NO_CHANGE,
        value    : Any      | NoChange = NO_CHANGE,
        undoable : bool = False
    ) -> None:
        host = asDiagramScene(self)
        if owner.propertyName(property) is None:
            logger().error("Property does not belong to owner")
            return
        cmd = CmdEditProperty(owner, property, PropertyChange(
            name  = name,
            value = value,
            kind  = kind
        ))
        cmdExec(host, cmd, undoable)

    @checked
    def delProperty(
        self     : Self,
        owner    : PropertiesMixin,
        property : Property,
        undoable : bool = False
    ) -> None:
        host = asDiagramScene(self)
        if owner.propertyName(property) is None:
            logger().error("Property does not belong to owner")
            return
        cmd = CmdDelProperty(owner, property)
        cmdExec(host, cmd, undoable)

    @checked
    def addPropertyText(
        self       : Self,
        owner      : PropertiesMixin,
        property   : Property,
        visible    : bool            = True,
        cleat      : HandleId | None = None,
        x          : float           = 0.0,
        y          : float           = 0.0,
        rotation   : float           = 0.0,
        mirror_h   : bool            = False,
        mirror_v   : bool            = False,
        autoflip   : bool            = True,
        origin     : RectHandleId    = RectHandleId.TOP_LEFT,
        align_h    : AlignH          = AlignH.LEFT,
        align_v    : AlignV          = AlignV.TOP,
        width      : float           = -1.0,
        height     : float           = -1.0,
        pad_left   : float           = 0.0,
        pad_right  : float           = 0.0,
        pad_top    : float           = 0.0,
        pad_bottom : float           = 0.0,
        color      : QColor   | None = None,
        font       : str      | None = None,
        size       : float    | None = None,
        bold       : bool     | None = None,
        italic     : bool     | None = None,
        underline  : bool     | None = None,
        undoable   : bool            = False
    ) -> None:
        host = asDiagramScene(self)
        if owner.propertyName(property) is None:
            logger().error("Property does not belong to owner")
            return
        cmd = CmdAddPropertyText(owner, property, PropertyTextState(
            visible    = visible,
            cleat      = cleat,
            x          = x,
            y          = y,
            rotation   = rotation,
            mirror_h   = mirror_h,
            mirror_v   = mirror_v,
            autoflip   = autoflip,
            origin     = origin,
            align_h    = align_h,
            align_v    = align_v,
            width      = width,
            height     = height,
            pad_left   = pad_left,
            pad_right  = pad_right,
            pad_top    = pad_top,
            pad_bottom = pad_bottom,
            color      = color,
            font       = font,
            size       = size,
            bold       = bold,
            italic     = italic,
            underline  = underline
        ))
        cmdExec(host, cmd, undoable)

    @checked
    def editPropertyText(
        self       : Self,
        item       : PropertyTextItem,
        visible    : bool            | NoChange = NO_CHANGE,
        cleat      : HandleId | None | NoChange = NO_CHANGE,
        x          : float           | NoChange = NO_CHANGE,
        y          : float           | NoChange = NO_CHANGE,
        rotation   : float           | NoChange = NO_CHANGE,
        mirror_h   : bool            | NoChange = NO_CHANGE,
        mirror_v   : bool            | NoChange = NO_CHANGE,
        autoflip   : bool            | NoChange = NO_CHANGE,
        origin     : RectHandleId    | NoChange = NO_CHANGE,
        align_h    : AlignH          | NoChange = NO_CHANGE,
        align_v    : AlignV          | NoChange = NO_CHANGE,
        width      : float           | NoChange = NO_CHANGE,
        height     : float           | NoChange = NO_CHANGE,
        pad_left   : float           | NoChange = NO_CHANGE,
        pad_right  : float           | NoChange = NO_CHANGE,
        pad_top    : float           | NoChange = NO_CHANGE,
        pad_bottom : float           | NoChange = NO_CHANGE,
        color      : QColor   | None | NoChange = NO_CHANGE,
        font       : str      | None | NoChange = NO_CHANGE,
        size       : float    | None | NoChange = NO_CHANGE,
        bold       : bool     | None | NoChange = NO_CHANGE,
        italic     : bool     | None | NoChange = NO_CHANGE,
        underline  : bool     | None | NoChange = NO_CHANGE,
        undoable   : bool                       = False
    ) -> None:
        host = asDiagramScene(self)
        owner = item.property().owner()
        if not any(
            text is item
            for text in owner.propertyTextItems(item.property())
        ):
            logger().error("Property text is not on owner")
            return
        cmd = CmdEditPropertyText(item, PropertyTextChange(
            item       = item,
            visible    = visible,
            cleat      = cleat,
            x          = x,
            y          = y,
            rotation   = rotation,
            mirror_h   = mirror_h,
            mirror_v   = mirror_v,
            autoflip   = autoflip,
            origin     = origin,
            align_h    = align_h,
            align_v    = align_v,
            width      = width,
            height     = height,
            pad_left   = pad_left,
            pad_right  = pad_right,
            pad_top    = pad_top,
            pad_bottom = pad_bottom,
            color      = color,
            font       = font,
            size       = size,
            bold       = bold,
            italic     = italic,
            underline  = underline
        ))
        cmdExec(host, cmd, undoable)

    @checked
    def delPropertyText(
        self     : Self,
        owner    : PropertiesMixin,
        item     : PropertyTextItem,
        undoable : bool = False
    ) -> None:
        host = asDiagramScene(self)
        cmd = CmdDelPropertyText(owner, item)
        cmdExec(host, cmd, undoable)

    @checked
    def editProperties(
        self     : Self,
        edits    : list[PropertyAndTextsEdit],
        undoable : bool = False
    ) -> None:
        host = asDiagramScene(self)
        if len(edits) == 0:
            return
        if undoable:
            host.undo_stack.beginMacro("editProperties")
        for group in edits:
            edit = group.edit
            if isinstance(edit, PropertyAdd):
                property = self.addProperty(
                    group.owner,
                    edit.state.name,
                    edit.state.kind,
                    edit.state.value,
                    undoable
                )
                if property is not None:
                    for text_state in edit.texts:
                        self.addPropertyText(
                            group.owner,
                            property,
                            **_textKwargs(text_state),
                            undoable = undoable
                        )
            elif isinstance(edit, PropertyDelete):
                if group.property is None:
                    logger().error("Property delete has no property")
                else:
                    self.delProperty(group.owner, group.property, undoable)
            elif isinstance(edit, PropertyChange):
                if group.property is None:
                    logger().error("Property change has no property")
                else:
                    self.editProperty(
                        group.owner,
                        group.property,
                        name     = edit.name,
                        kind     = edit.kind,
                        value    = edit.value,
                        undoable = undoable
                    )
            for text in group.texts:
                if isinstance(text, PropertyTextAdd):
                    self.addPropertyText(
                        text.owner,
                        text.property,
                        **_textKwargs(text.state),
                        undoable = undoable
                    )
                elif isinstance(text, PropertyTextDelete):
                    self.delPropertyText(group.owner, text.item, undoable)
                elif isinstance(text, PropertyTextChange):
                    self.editPropertyText(
                        text.item,
                        **_textKwargs(text),
                        undoable = undoable
                    )
        if undoable:
            host.undo_stack.endMacro()
