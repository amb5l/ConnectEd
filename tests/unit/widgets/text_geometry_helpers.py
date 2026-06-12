"""Helpers for the parented PropertyText permutation matrix."""

from __future__ import annotations

from dataclasses import dataclass
from typing      import Self

import pytest
from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsSimpleTextItem, QGraphicsTextItem

from ConnectEd.core.db import DesignDbNode
from ConnectEd.core.types import AlignH, AlignV, DataKind, RectHandleId
from ConnectEd.core.utils import val2str
from ConnectEd.widgets.graphics.items.polyline import PolylineItem
from ConnectEd.widgets.graphics.items.property_text import PropertyTextItem
from ConnectEd.widgets.graphics.items.text import TextItem, TextLineRenderer
from ConnectEd.widgets.graphics.scenes.diagram import DiagramScene

SHORT        = "short"
LONG         = "longer"
X_STEP       = 80.0
Y_STEP       = 40.0
GRID         = 144
SHEET_WIDTH  = 12000.0
SHEET_HEIGHT = 6000.0
GRID_ORIGIN  = QPointF(200.0, 200.0)
CAPTION      = "Caption"
TOL          = 0.5

ROTATIONS = (0.0, 90.0, 180.0, 270.0)
MIRRORS   = (False, True)
ALIGNS_H  = tuple(AlignH)
ALIGNS_V  = tuple(AlignV)
ORIGINS   = tuple(RectHandleId)

_CHEVRON_VERTICES = [
    QPointF( 0.0, 30.0),
    QPointF(20.0,  0.0),
    QPointF(40.0, 30.0),
]

@dataclass(frozen=True)
class TextCase:
    row     : int
    col     : int
    poly    : PolylineItem
    text    : PropertyTextItem


@dataclass(frozen=True)
class TextGeometry:
    child_scene        : QRectF
    handle_scene       : QRectF
    origin_scene       : QPointF
    handle_scene_by_id : dict[RectHandleId, QPointF]
    rotation           : float
    mirror_h           : bool
    mirror_v           : bool
    origin             : RectHandleId | None
    text               : str
    width              : float
    height             : float

    def _close(self : Self, a : float, b : float, tol : float) -> bool:
        return abs(a - b) <= tol

    def matches(self : Self, other : Self, tol : float = TOL) -> bool:
        return (
            self._close(self.child_scene.left(),   other.child_scene.left(),   tol)
            and self._close(self.child_scene.right(),  other.child_scene.right(),  tol)
            and self._close(self.child_scene.top(),    other.child_scene.top(),    tol)
            and self._close(self.child_scene.bottom(), other.child_scene.bottom(), tol)
            and self._close(self.handle_scene.left(),   other.handle_scene.left(),   tol)
            and self._close(self.handle_scene.right(),  other.handle_scene.right(),  tol)
            and self._close(self.handle_scene.top(),    other.handle_scene.top(),    tol)
            and self._close(self.handle_scene.bottom(), other.handle_scene.bottom(), tol)
            and self._close(self.origin_scene.x(),      other.origin_scene.x(),      tol)
            and self._close(self.origin_scene.y(),      other.origin_scene.y(),      tol)
            and self.rotation == other.rotation
            and self.mirror_h == other.mirror_h
            and self.mirror_v == other.mirror_v
            and self.origin   == other.origin
            and self.text     == other.text
            and self._close(self.width,  other.width,  tol)
            and self._close(self.height, other.height, tol)
        )


def decode_orientation(idx : int) -> tuple[float, bool, bool]:
    mirror_v = bool(idx % 2)
    mirror_h = bool((idx // 2) % 2)
    rotation = ROTATIONS[idx // 4]
    return rotation, mirror_h, mirror_v


def decode_align(idx : int) -> tuple[AlignH, AlignV]:
    return ALIGNS_H[idx % 3], ALIGNS_V[idx // 3]


def _apply_parent_transform(item : PolylineItem, rotation : float, mirror_h : bool, mirror_v : bool) -> None:
    item.setRotation(rotation)
    item.setMirrorH(mirror_h)
    item.setMirrorV(mirror_v)
    if mirror_h or mirror_v:
        item.updateTransform()


def _apply_text_transform(
    pt       : PropertyTextItem,
    rotation : float,
    mirror_h : bool,
    mirror_v : bool,
) -> None:
    pt.setRotation(rotation)
    pt.setMirrorH(mirror_h)
    pt.setMirrorV(mirror_v)
    if mirror_h or mirror_v:
        pt.updateTransform()


def apply_permutation(poly : PolylineItem, row : int, col : int) -> None:
    align_idx         = row // 16
    parent_orient_idx = row % 16
    orient_idx        = col // 9
    origin_idx        = col % 9

    align_h, align_v = decode_align(align_idx)
    parent_rot, parent_mh, parent_mv = decode_orientation(parent_orient_idx)
    text_rot, text_mh, text_mv = decode_orientation(orient_idx)
    origin = ORIGINS[origin_idx]

    _apply_parent_transform(poly, parent_rot, parent_mh, parent_mv)

    pt = poly.properties.text(CAPTION)
    assert pt is not None
    pt.setAlignH(align_h)
    pt.setAlignV(align_v)
    _apply_text_transform(pt, text_rot, text_mh, text_mv)
    pt.setOrigin(origin)


def make_chevron_polyline() -> PolylineItem:
    poly = PolylineItem(vertices=_CHEVRON_VERTICES)
    poly.properties.add(CAPTION, DataKind.STR, SHORT)
    poly.properties.addText(
        CAPTION,
        cleat      = RectHandleId.MIDDLE_RIGHT,
        x          = 0.0,
        y          = 0.0,
        origin     = RectHandleId.MIDDLE_LEFT,
        align_h    = AlignH.LEFT,
        align_v    = AlignV.MIDDLE,
    )
    return poly


def configure_scene_sheet(scene : DiagramScene) -> None:
    scene.setSheetWidth(SHEET_WIDTH)
    scene.setSheetHeight(SHEET_HEIGHT)


def build_parented_text_matrix(scene : DiagramScene) -> list[TextCase]:
    configure_scene_sheet(scene)
    prototype = make_chevron_polyline()
    cases : list[TextCase] = []
    for row in range(GRID):
        for col in range(GRID):
            poly = prototype.clone()
            poly.setPos(
                GRID_ORIGIN.x() + col * X_STEP,
                GRID_ORIGIN.y() + row * Y_STEP,
            )
            apply_permutation(poly, row, col)
            scene.addItem(poly)
            pt = poly.properties.text(CAPTION)
            assert pt is not None
            cases.append(TextCase(row = row, col = col, poly = poly, text = pt))
    return cases


def build_design() -> DesignDbNode:
    node = DesignDbNode()
    node.setText("TextPermutations")
    scene = node.scene()
    build_parented_text_matrix(scene)
    return node


def collect_cases_from_scene(scene : DiagramScene) -> list[TextCase]:
    polylines = [
        item for item in scene.items()
        if isinstance(item, PolylineItem) and item.parentItem() is None
    ]
    polylines.sort(key = lambda poly: (poly.pos().y(), poly.pos().x()))
    cases : list[TextCase] = []
    for poly in polylines:
        pos = poly.pos()
        col = int((pos.x() - GRID_ORIGIN.x()) / X_STEP)
        row = int((pos.y() - GRID_ORIGIN.y()) / Y_STEP)
        pt = poly.properties.text(CAPTION)
        assert pt is not None
        cases.append(TextCase(row = row, col = col, poly = poly, text = pt))
    return cases


def _glyph_scene_rect(item : TextItem) -> QRectF:
    child = item._child
    if isinstance(child, TextLineRenderer):
        glyph = QGraphicsSimpleTextItem.boundingRect(child)
    else:
        glyph = QGraphicsTextItem.boundingRect(child)
    return child.mapToScene(glyph).boundingRect()


def display_text(item : TextItem) -> str:
    if isinstance(item, PropertyTextItem):
        return val2str(item.value())
    return item.text()


def measure(item : TextItem) -> TextGeometry:
    child_scene  = _glyph_scene_rect(item)
    handle_scene = item.mapToScene(item.handleRect()).boundingRect()
    handle_scene_by_id = {
        id : item.getHandle(id).scenePos()
        for id in RectHandleId
    }
    return TextGeometry(
        child_scene        = child_scene,
        handle_scene       = handle_scene,
        origin_scene       = item.getOriginHandle().scenePos(),
        handle_scene_by_id = handle_scene_by_id,
        rotation           = item.rotation(),
        mirror_h           = item.mirrorH(),
        mirror_v           = item.mirrorV(),
        origin             = item.origin(),
        text               = display_text(item),
        width              = item.handleRect().width(),
        height             = item.handleRect().height(),
    )


def assert_handles_on_handle_rect(item : TextItem, tol : float = 0.01) -> None:
    hrect = item.handleRect()
    for id in RectHandleId:
        name = id.value
        x = 1.0 if "Right" in name else 0.5 if "Center" in name else 0.0
        y = 1.0 if "Bottom" in name else 0.5 if "Middle" in name else 0.0
        expected = QPointF(
            hrect.left() + (x * hrect.width()),
            hrect.top()  + (y * hrect.height()),
        )
        actual = item.getHandle(id).pos()
        assert actual.x() == pytest.approx(expected.x(), abs=tol)
        assert actual.y() == pytest.approx(expected.y(), abs=tol)


def assert_child_aligns_handles(geom : TextGeometry, tol : float = TOL) -> None:
    assert geom.child_scene.left()   == pytest.approx(geom.handle_scene.left(),   abs=tol)
    assert geom.child_scene.right()  == pytest.approx(geom.handle_scene.right(),  abs=tol)
    assert geom.child_scene.top()    == pytest.approx(geom.handle_scene.top(),    abs=tol)
    assert geom.child_scene.bottom() == pytest.approx(geom.handle_scene.bottom(), abs=tol)


def assert_origin_on_handle_rect(item : TextItem, geom : TextGeometry, tol : float = TOL) -> None:
    origin = item.origin()
    assert origin is not None
    expected = geom.handle_scene_by_id[origin]
    assert geom.origin_scene.x() == pytest.approx(expected.x(), abs=tol)
    assert geom.origin_scene.y() == pytest.approx(expected.y(), abs=tol)


def assert_geometry(item : TextItem, geom : TextGeometry | None = None) -> TextGeometry:
    geom = geom or measure(item)
    assert_handles_on_handle_rect(item)
    assert_child_aligns_handles(geom)
    assert_origin_on_handle_rect(item, geom)
    return geom


def case_label(case : TextCase) -> str:
    return f"row={case.row} col={case.col}"
