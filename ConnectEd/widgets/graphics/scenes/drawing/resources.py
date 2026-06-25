from typing import Self, Any

from PyQt6.QtCore import Qt, QPointF, QLineF, QRectF
from PyQt6.QtGui  import QPen, QBrush, QTransform, \
                         QPolygonF, QPainterPath, QColor

from .....app import settings

from ...quill import Quill

from ...items.grip import GripShape


class DrawingSceneResources:
    # class attributes
    _PEN_ITEMS   = ["Rectangle", "Ellipse", "Block", "Line", "Polyline"]
    _BRUSH_ITEMS = ["Rectangle", "Ellipse", "Block", "Polyline"]
    _QUILL_ITEMS = ["Text"]

    # instance attributes
    _pens    : dict[str, QPen | dict[tuple[bool, ...], QPen]] = {}
    _brushes : dict[str, QBrush | dict[bool, QBrush]] = {}
    _quills  : dict[str, Quill | dict[bool, Quill]] = {}
    _lines   : dict[str, QLineF] = {}
    _paths   : dict[str, dict[Any, QPainterPath]] = {}

    def __init__(self : Self) -> None:
        self.update()
        settings().changed.connect(self.update)

    def update(self : Self) -> None:
        # pens
        self._pens = {}
        for item_name in self._PEN_ITEMS:
            pen_normal, pen_selected = self._getPens(
                item_name,
                f"theme/items/{item_name}/line",
            )
            self._pens[item_name] = {
                False : pen_normal,
                True : pen_selected
            }
        # brushes
        self._brushes = {}
        for item_name in self._BRUSH_ITEMS:
            brush_normal, brush_selected = self._getBrushes(
                item_name,
                f"theme/items/{item_name}/fill",
            )
            self._brushes[item_name] = {
                False : brush_normal,
                True : brush_selected
            }
        # quills
        self._quills = {}
        for item_name in self._QUILL_ITEMS:
            self._loadQuill(item_name)
        # grip pens, brushes and paths
        self._pens["Grip"] = self._getPen("theme/grip/line")
        self._brushes["Grip"] = self._getBrush("theme/grip/fill")
        self._paths["Grip"] = {}
        size = settings().get("theme/grip/size")
        rect = QRectF(-size/2, -size/2, size, size)
        square = QPainterPath()
        square.addRect(rect)
        self._paths["Grip"][GripShape.SQUARE] = square
        circle = QPainterPath()
        circle.addEllipse(rect)
        self._paths["Grip"][GripShape.CIRCLE] = circle
        diamond = QPainterPath()
        diamond.addPolygon(QPolygonF([
            QPointF(-size/2, 0),
            QPointF(0, -size/2),
            QPointF(size/2, 0),
            QPointF(0, size/2)
        ]))
        self._paths["Grip"][GripShape.DIAMOND] = diamond
        arrow = QPainterPath()
        arrow.addPolygon(QPolygonF([
            QPointF(-size/2, -size/2),
            QPointF(size/2, 0),
            QPointF(-size/2, size/2)
        ]))
        self._paths["Grip"][GripShape.ARROW] = arrow
        star = QPainterPath()
        star.addRect(rect)
        rotated = QPainterPath()
        rotated.addRect(rect)
        rotated = QTransform().rotate(45).map(rotated)
        star = star.united(rotated)
        self._paths["Grip"][GripShape.STAR] = star

    def pen(
        self      : Self,
        item_name : str,
        key       : bool | tuple | None = None
    ) -> QPen:
        if item_name not in self._pens:
            raise ValueError(f"No pen defined for item {item_name}")
        return self._pens[item_name] if key is None \
            else self._pens[item_name][key]

    def brush(
        self      : Self,
        item_name : str,
        key       : bool | tuple | None = None
    ) -> QBrush:
        if item_name not in self._brushes:
            raise ValueError(f"No brush defined for item {item_name}")
        return self._brushes[item_name] if key is None \
            else self._brushes[item_name][key]

    def quill(
        self      : Self,
        item_name : str,
        key       : bool | tuple | None = None
    ) -> Quill:
        if item_name not in self._quills:
            self._loadQuill(item_name)
        return self._quills[item_name] if key is None \
            else self._quills[item_name][key]

    def _loadQuill(self : Self, item_name : str) -> None:
        try:
            quill_normal, quill_selected = self._getQuills(
                item_name,
                f"theme/items/{item_name}/text",
            )
        except KeyError:
            raise ValueError(f"No quill defined for item {item_name}") from None
        self._quills[item_name] = {
            False : quill_normal,
            True  : quill_selected
        }

    def line(self : Self, item_name : str) -> QLineF:
        if item_name not in self._lines:
            raise ValueError(f"No line defined for item {item_name}")
        return self._lines[item_name]

    def path(self : Self, item_name : str, key : Any) -> QPainterPath:
        if item_name not in self._paths:
            raise ValueError(f"No path defined for item {item_name}")
        return self._paths[item_name][key]

    def _getPen(
        self          : Self,
        settings_path : str,
        cap_style     : Qt.PenCapStyle = Qt.PenCapStyle.FlatCap,
        join_style    : Qt.PenJoinStyle = Qt.PenJoinStyle.MiterJoin
    ) -> QPen:
        return QPen(
            settings().get(f"{settings_path}/color"),
            settings().get(f"{settings_path}/width"),
            settings().get(f"{settings_path}/style"),
            cap_style,
            join_style
        )

    def _selectedColor(self : Self, part : str) -> QColor:
        spec = settings().get(f"theme/selected/{part}")
        if hasattr(spec, "color"):
            return spec.color
        return spec

    def _selectedItemPart(
        self      : Self,
        item_name : str,
        part      : str,
    ) -> Any | None:
        try:
            items = settings().get("theme/selected/items")
        except KeyError:
            return None
        if not hasattr(items, item_name):
            return None
        block = getattr(items, item_name)
        if not hasattr(block, part):
            return None
        return getattr(block, part)

    def _applySelectedLine(
        self      : Self,
        item_name : str,
        pen       : QPen,
    ) -> QPen:
        pen_sel = QPen(pen)
        spec = settings().get("theme/selected/line")
        if hasattr(spec, "color"):
            pen_sel.setColor(spec.color)
        else:
            pen_sel.setColor(spec)
        if hasattr(spec, "width"):
            pen_sel.setWidthF(float(spec.width))
        if hasattr(spec, "style"):
            pen_sel.setStyle(spec.style)
        override = self._selectedItemPart(item_name, "line")
        if override is not None:
            if hasattr(override, "color"):
                pen_sel.setColor(override.color)
            if hasattr(override, "width"):
                pen_sel.setWidthF(float(override.width))
            if hasattr(override, "style"):
                pen_sel.setStyle(override.style)
        return pen_sel

    def _applySelectedBrush(
        self      : Self,
        item_name : str,
        brush     : QBrush,
    ) -> QBrush:
        brush_sel = QBrush(brush)
        spec = settings().get("theme/selected/fill")
        if hasattr(spec, "color"):
            brush_sel.setColor(spec.color)
        else:
            brush_sel.setColor(spec)
        if hasattr(spec, "style"):
            brush_sel.setStyle(spec.style)
        override = self._selectedItemPart(item_name, "fill")
        if override is not None:
            if hasattr(override, "color"):
                brush_sel.setColor(override.color)
            if hasattr(override, "style"):
                brush_sel.setStyle(override.style)
        return brush_sel

    def _applySelectedQuill(
        self      : Self,
        item_name : str,
        quill     : Quill,
    ) -> Quill:
        quill_sel = Quill(quill)
        spec = settings().get("theme/selected/text")
        if hasattr(spec, "color"):
            quill_sel.setColor(spec.color)
        else:
            quill_sel.setColor(spec)
        for attr in ("font", "size", "bold", "italic", "underline"):
            if hasattr(spec, attr):
                setter = getattr(quill_sel, f"set{attr.capitalize()}")
                setter(getattr(spec, attr))
        override = self._selectedItemPart(item_name, "text")
        if override is not None:
            if hasattr(override, "color"):
                quill_sel.setColor(override.color)
            for attr in ("font", "size", "bold", "italic", "underline"):
                if hasattr(override, attr):
                    setter = getattr(quill_sel, f"set{attr.capitalize()}")
                    setter(getattr(override, attr))
        return quill_sel

    def _getPens(
        self          : Self,
        item_name     : str,
        settings_path : str,
        cap_style     : Qt.PenCapStyle = Qt.PenCapStyle.FlatCap,
        join_style    : Qt.PenJoinStyle = Qt.PenJoinStyle.MiterJoin
    ) -> tuple[QPen, QPen]:
        pen_normal = self._getPen(settings_path, cap_style, join_style)
        pen_selected = self._applySelectedLine(item_name, pen_normal)
        return pen_normal, pen_selected

    def _getBrush(self : Self, settings_path : str) -> QBrush:
        return QBrush(
            settings().get(f"{settings_path}/color"),
            settings().get(f"{settings_path}/style")
        )

    def _getBrushes(
        self          : Self,
        item_name     : str,
        settings_path : str,
    ) -> tuple[QBrush, QBrush]:
        brush_normal = self._getBrush(settings_path)
        brush_selected = self._applySelectedBrush(item_name, brush_normal)
        return brush_normal, brush_selected

    def _getQuill(self : Self, settings_path : str) -> Quill:
        return Quill(
            settings().get(f"{settings_path}/color"),
            settings().get(f"{settings_path}/font"),
            settings().get(f"{settings_path}/size"),
            settings().get(f"{settings_path}/bold"),
            settings().get(f"{settings_path}/italic"),
            settings().get(f"{settings_path}/underline")
        )

    def _getQuills(
        self          : Self,
        item_name     : str,
        settings_path : str,
    ) -> tuple[Quill, Quill]:
        quill_normal = self._getQuill(settings_path)
        quill_selected = self._applySelectedQuill(item_name, quill_normal)
        return quill_normal, quill_selected
