from __future__ import annotations

from typing import Self
from types  import SimpleNamespace

from PyQt6.QtCore    import Qt, QRect, QSize, QAbstractItemModel
from PyQt6.QtWidgets import QWidget, QHeaderView, QTableView, \
                            QTreeView, QAbstractItemView, \
                            QStyle, QStyleOptionHeader
from PyQt6.QtGui     import QAction, QWheelEvent, QFont, QPainter, QMouseEvent

from ...app        import settings

from ...core.check import checked

from .model        import TableModel


class TableHeaderView(QHeaderView):
    """Table header view with group labels support."""

    def __init__(
        self        : Self,
        orientation : Qt.Orientation,
        parent      : QWidget | None = None
    ) -> None:
        super().__init__(orientation, parent)
        self.setSectionsMovable(False)

    def setModel(self : Self, model : QAbstractItemModel | None) -> None:
        old = self.model()
        if old is not None:
            old.headerDataChanged.disconnect(self._onHeaderMetaChanged)
            old.modelReset.disconnect(self._onHeaderMetaChanged)
        super().setModel(model)
        if model is not None:
            model.headerDataChanged.connect(self._onHeaderMetaChanged)
            model.modelReset.connect(self._onHeaderMetaChanged)
        self.updateGeometries()

    def _onHeaderMetaChanged(self : Self, *_args : object) -> None:
        self.updateGeometries()
        if (viewport := self.viewport()) is not None:
            viewport.update()

    def _groupLabels(self : Self) -> list[str] | None:
        model = self.model()
        if not isinstance(model, TableModel):
            return None
        labels = model.horizontalHeaderGroupLabels()
        if labels is None or not any(labels):
            return None
        return labels

    def _groupBandHeight(self : Self) -> int:
        if self._groupLabels() is None:
            return 0
        return max(1, super().sizeHint().height())

    def _spanAt(
        self          : Self,
        logical_index : int
    ) -> tuple[int, int, str] | None:
        labels = self._groupLabels()
        if labels is None or not (0 <= logical_index < len(labels)):
            return None
        name  = labels[logical_index]
        start = logical_index
        while start > 0 and labels[start - 1] == name:
            start -= 1
        end = logical_index + 1
        while end < len(labels) and labels[end] == name:
            end += 1
        return start, end - start, name

    def sizeHint(self : Self) -> QSize:
        hint = super().sizeHint()
        extra = self._groupBandHeight()
        if extra:
            return QSize(hint.width(), hint.height() + extra)
        return hint

    def paintSection(
        self         : Self,
        painter      : QPainter | None,
        rect         : QRect,
        logicalIndex : int
    ) -> None:
        if painter is None:
            return
        group_h = self._groupBandHeight()
        if group_h == 0:
            super().paintSection(painter, rect, logicalIndex)
            return
        leaf_rect = QRect(
            rect.left(),
            rect.top() + group_h,
            rect.width(),
            max(0, rect.height() - group_h)
        )
        group_rect = QRect(rect.left(), rect.top(), rect.width(), group_h)
        painter.save()
        super().paintSection(painter, leaf_rect, logicalIndex)
        painter.restore()
        self._paintGroupBand(painter, rect, group_rect, logicalIndex)

    def _paintGroupBand(
        self          : Self,
        painter       : QPainter,
        section_rect  : QRect,
        group_rect    : QRect,
        logical_index : int
    ) -> None:
        span = self._spanAt(logical_index)
        start = logical_index if span is None else span[0]
        count = 1 if span is None else span[1]
        name  = "" if span is None else span[2]
        x0 = self.sectionViewportPosition(start)
        width = sum(self.sectionSize(start + i) for i in range(count))
        span_rect = QRect(x0, group_rect.top(), width, group_rect.height())
        painter.save()
        painter.setClipRect(group_rect)
        opt = QStyleOptionHeader()
        self.initStyleOptionForIndex(opt, logical_index)
        opt.rect = span_rect
        opt.text = name
        opt.section = start
        opt.position = QStyleOptionHeader.SectionPosition.OnlyOneSection
        opt.textAlignment = Qt.AlignmentFlag.AlignCenter
        style = self.style()
        if style is not None:
            style.drawControl(
                QStyle.ControlElement.CE_Header, opt, painter, self
            )
        painter.restore()
        painter.save()
        pen = painter.pen()
        pen.setColor(self.palette().mid().color())
        painter.setPen(pen)
        y = group_rect.bottom()
        painter.drawLine(section_rect.left(), y, section_rect.right(), y)
        if logical_index == start + count - 1:
            x = section_rect.right()
            painter.drawLine(x, section_rect.top(), x, section_rect.bottom())
        painter.restore()

    def mousePressEvent(self : Self, e : QMouseEvent | None) -> None:
        if e is not None \
        and self._groupBandHeight() > 0 \
        and e.position().y() < self._groupBandHeight() \
        and self.cursor().shape() != Qt.CursorShape.SplitHCursor:
            e.accept()
            return
        super().mousePressEvent(e)


class TableViewMixin:
    _actions   : SimpleNamespace
    _font_size : int

    def _initTableViewMixin(self : Self) -> None:
        if not isinstance(self, QAbstractItemView):
            raise TypeError("Bad view")
        self._actions = SimpleNamespace()
        a = self._actions
        a.increaseTextSize = QAction("Increase Text Size", self)
        a.increaseTextSize.triggered.connect(self.increaseFontSize)
        a.decreaseTextSize = QAction("Decrease Text Size", self)
        a.decreaseTextSize.triggered.connect(self.decreaseFontSize)
        self.setFontSize(settings().get("display/font_size"))

    def _header(self : Self) -> QHeaderView | None:
        if isinstance(self, QTableView):
            return self.horizontalHeader()
        if isinstance(self, QTreeView):
            return self.header()
        return None

    def wheelEvent(self : Self, a0 : QWheelEvent | None) -> None:
        """Handle mouse wheel events to adjust font size when Ctrl is pressed."""
        if a0 is None:
            return
        modifiers = a0.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            delta = a0.angleDelta().y()
            if delta > 0:
                self.increaseFontSize()
            elif delta < 0:
                self.decreaseFontSize()
            a0.accept()
            return
        if isinstance(self, QTableView):
            QTableView.wheelEvent(self, a0)
        elif isinstance(self, QTreeView):
            QTreeView.wheelEvent(self, a0)

    @checked
    def setFontSize(self : Self, size : int) -> None:
        """Set the font size for all items in the table."""
        if not isinstance(self, QAbstractItemView):
            raise TypeError("Bad view")
        font = QFont()
        font.setPointSizeF(size)
        self.setFont(font)
        header = self._header()
        if header is not None:
            header.setFont(font)
            header.updateGeometries()
        self._font_size = size

    def increaseFontSize(self : Self) -> None:
        """Increase the font size."""
        self.setFontSize(min(self._font_size + 1, 20)) # TODO: max from settings

    def decreaseFontSize(self : Self) -> None:
        """Decrease the font size."""
        self.setFontSize(max(self._font_size - 1, 6)) # TODO: min from settings


class TableView(TableViewMixin, QTableView):
    @checked
    def __init__(
        self   : Self,
        model  : TableModel,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setHorizontalHeader(
            TableHeaderView(Qt.Orientation.Horizontal, self)
        )
        self.setModel(model)
        self.resizeColumnsToContents()
        self._initTableViewMixin()


class TreeTableView(TableViewMixin, QTreeView):
    @checked
    def __init__(
        self   : Self,
        model  : TableModel,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setHeader(
            TableHeaderView(Qt.Orientation.Horizontal, self)
        )
        self.setUniformRowHeights(True)
        self.setAllColumnsShowFocus(True)
        self.setRootIsDecorated(True)
        self.setModel(model)
        self.expandAll()
        self.resizeColumnsToContents()
        self._initTableViewMixin()

    def resizeColumnsToContents(self : Self) -> None:
        model = self.model()
        if model is None:
            return
        for col in range(model.columnCount()):
            self.resizeColumnToContents(col)
