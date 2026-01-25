from typing import Self

from PyQt6.QtCore import QPointF

from .......app import logger

from .....property import PropertyTextState, PropertyTextEdit

from .....items import NO_CHANGE

from .. import CmdBase

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .....property            import PropertyState, PropertyEdit
    from .....properties          import PropertiesMixin
    from .....items               import ItemMixin
    from .....items.property_text import PropertyTextItem
    from ......dialogs.properties import DisplayChoice

class CmdEditProperties(CmdBase):
    _object  : "PropertiesMixin"
    _before  : list["PropertyState"]
    _changes : dict[str, "PropertyEdit | PropertyState"]

    def __init__(
        self    : Self,
        object  : "PropertiesMixin",
        changes : dict[str, "PropertyEdit"]
    ):
        self._object  = object
        self._before = {
            name: prop.getState() for prop, name in object.properties.items()
        }
        self._changes = changes
        super().__init__()

    def redo(self : Self) -> None:
        for name, change in self._changes.items():
            if name not in self._before:
                # add property
                if not isinstance(change, PropertyState):
                    logger().error(f"Cannot edit new property '{name}'")
                    continue
                if name != change.name:
                    logger.error(f"Cannot change name of new property '{name}'")
                    continue
            elif change is None:
                # delete property
                self._object.delProperty(name)
            else:
                # modify property
                if not isinstance(change, PropertyEdit):
                    logger().error(f"Bad change to existing property '{name}'")
                    continue
                if name != change.name:
                    # rename property
                    self._object.renProperty(name, change.name)
                property = self._object.properties[name]
                if change.value is not NO_CHANGE:
                    property.set(change.value)
                if change.display is NO_CHANGE:
                    continue
                if property.getText() is None:
                    # add new property text
                    logger().warning(f"Need to add PropertyText to property '{name}'")
                elif change.display is DisplayChoice.NONE:
                    # remove property text
                    property.setText(None)
                else:
                    logger().warning(f"Need to edit PropertyText for property '{name}'")

    def undo(self : Self) -> None:
        self._do(self._changes, self._before)

    def _do(self : Self, before_attr : str, after_attr : str) -> None:
        for _name, change in self._changes.items():
            before : "PropertyState | None" = getattr(change, before_attr)
            after  : "PropertyState | None" = getattr(change, after_attr)
            if before is None:
                # add property
                self._object.initProperty(after.name, after.value)
                if after.display != DisplayChoice.NONE:
                    self._addPropertyText(after)
            elif after is None:
                # delete property
                del self._object.properties[before.name]
            else:
                # existing property
                self._object.renProperty(before.name, after.name)
                self._object.properties[after.name].set(after.value)
                pt = self._object.properties[after.name].getText()
                if pt is None:
                    if after.display != DisplayChoice.NONE:
                        self._addPropertyText(after)
                else:
                    if after.display == DisplayChoice.NONE:
                        self._object.properties[after.name].setText(None)
                    else:
                        self._modifyPropertyText(pt, after)

    def _addPropertyText(self : Self, vars : "PropertyState") -> None:
        pt = PropertyTextItem()
        self._modifyPropertyText(pt, vars)
        parent = self._object.getHandle(vars.cleat) if vars.cleat != "" else \
            self._object if isinstance(self._object, ItemMixin) else \
            None
        pt.setParentItem(parent)
        if parent is None:
            self._object.addItem(pt)  # add to scene
        self._object.properties[vars.name].setText(pt)
        pt.onPropertyChange()  # Refresh text after parenting

    def _modifyPropertyText(
        self : Self,
        pt   : "PropertyTextItem",
        vars : "PropertyState"
    ) -> None:
        pt.setName(vars.name)
        pt.setVisible(vars.display is not DisplayChoice.HIDE)
        pt.setAnchor(vars.cleat)
        pt.setPos(QPointF(vars.offset_x, vars.offset_y))
        pt.setOrigin(vars.origin)
        pt.a.quill.setFamily(vars.family)
        pt.a.quill.setSize(vars.size)
        pt.a.quill.setBold(vars.bold)
        pt.a.quill.setItalic(vars.italic)
        pt.a.quill.setUnderline(vars.underline)
        pt.a.quill.setColor(vars.color)
