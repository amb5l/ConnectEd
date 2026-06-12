"""
TextItem geometry: handles, growth, transforms, origin, parent, and XML round-trip.

Uses a bare ``DrawingScene`` and scene-space measurements of the rendered glyph
bounds, handle rectangle, and every grip.

By default 100 parametrized cases are chosen by a seeded PRNG; baseline
cases always run. Pass ``--full`` for the complete matrix::

    pytest tests/unit/widgets/test_text_item_geometry.py --full
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Self

import pytest
from PyQt6.QtCore    import QByteArray, QPointF, QRectF, QXmlStreamReader, QXmlStreamWriter
from PyQt6.QtWidgets import QApplication, QGraphicsRectItem, QGraphicsSimpleTextItem, \
                            QGraphicsTextItem

from ConnectEd.app import ConnectEdApp
from ConnectEd.core.settings import Settings
from ConnectEd.core.types import AlignH, AlignV, RectHandleId
from ConnectEd.core.xml import fromXmlItems, toXmlBegin, toXmlEnd
from ConnectEd.widgets.graphics.items.mixin.transform import ItemTransformMixin
from ConnectEd.widgets.graphics.items.text import TextItem, TextLineRenderer
from ConnectEd.widgets.graphics.scenes.drawing import DrawingScene

SHORT        = "A"
LONG         = "ABCDEFGH"
POS          = QPointF(50.0, 50.0)
PARENTED_POS = QPointF(20.0, 30.0)
TOL          = 0.5

ROTATIONS = (0.0, 90.0, 180.0, 270.0)
MIRRORS   = (False, True)
TEXTS     = (SHORT, LONG)
ALIGNS_H  = tuple(AlignH)
ALIGNS_V  = tuple(AlignV)
ORIGINS   = tuple(RectHandleId)


class _DummyParent(QGraphicsRectItem, ItemTransformMixin):
    """Minimal rotated/mirrored parent for parented text tests."""

    def __init__(
        self,
        rotation : float = 0.0,
        mirror_h : bool  = False,
        mirror_v : bool  = False,
    ) -> None:
        super().__init__(QRectF(0.0, 0.0, 200.0, 200.0))
        self._mirror_h = mirror_h
        self._mirror_v = mirror_v
        self.setPos(QPointF(100.0, 100.0))
        self.setRotation(rotation)
        if mirror_h or mirror_v:
            self.updateTransform()


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

    def child_matches(self : Self, other : Self, tol : float = TOL) -> bool:
        return (
            self._close(self.child_scene.left(),   other.child_scene.left(),   tol)
            and self._close(self.child_scene.right(),  other.child_scene.right(),  tol)
            and self._close(self.child_scene.top(),    other.child_scene.top(),    tol)
            and self._close(self.child_scene.bottom(), other.child_scene.bottom(), tol)
        )

    def matches(self : Self, other : Self, tol : float = TOL) -> bool:
        return (
            self.child_matches(other, tol)
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


@pytest.fixture
def connect_ed_app() -> ConnectEdApp:
    app = QApplication.instance()
    if not isinstance(app, ConnectEdApp):
        app = ConnectEdApp()
    app.setSettings(Settings())
    app.setLogger(logging.getLogger("test"))
    return app


@pytest.fixture
def drawing_scene(connect_ed_app : ConnectEdApp) -> DrawingScene:
    return DrawingScene()


def _glyph_scene_rect(item : TextItem) -> QRectF:
    child = item._child
    if isinstance(child, TextLineRenderer):
        glyph = QGraphicsSimpleTextItem.boundingRect(child)
    else:
        glyph = QGraphicsTextItem.boundingRect(child)
    return child.mapToScene(glyph).boundingRect()


def _measure(item : TextItem) -> TextGeometry:
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
        text               = item.text(),
        width              = item.handleRect().width(),
        height             = item.handleRect().height(),
    )


def _make_text(
    scene    : DrawingScene,
    text     : str           = SHORT,
    rotation : float         = 0.0,
    mirror_h : bool          = False,
    mirror_v : bool          = False,
    origin   : RectHandleId  = RectHandleId.TOP_LEFT,
    align_h  : AlignH        = AlignH.LEFT,
    align_v  : AlignV        = AlignV.TOP,
    pos      : QPointF       = POS,
    parent   : QGraphicsRectItem | None = None,
) -> TextItem:
    item = TextItem(
        text     = text,
        pos      = pos,
        rotation = rotation,
        mirror_h = mirror_h,
        mirror_v = mirror_v,
        origin   = origin,
        align_h  = align_h,
        align_v  = align_v,
        parent   = parent,
    )
    if parent is None:
        scene.addItem(item)
    else:
        scene.addItem(parent)
    return item


def _assert_handles_on_handle_rect(item : TextItem, tol : float = 0.01) -> None:
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


def _assert_child_aligns_handles(geom : TextGeometry, tol : float = TOL) -> None:
    assert geom.child_scene.left()   == pytest.approx(geom.handle_scene.left(),   abs=tol)
    assert geom.child_scene.right()  == pytest.approx(geom.handle_scene.right(),  abs=tol)
    assert geom.child_scene.top()    == pytest.approx(geom.handle_scene.top(),    abs=tol)
    assert geom.child_scene.bottom() == pytest.approx(geom.handle_scene.bottom(), abs=tol)


def _assert_origin_on_handle_rect(item : TextItem, geom : TextGeometry, tol : float = TOL) -> None:
    origin = item.origin()
    assert origin is not None
    expected = geom.handle_scene_by_id[origin]
    assert geom.origin_scene.x() == pytest.approx(expected.x(), abs=tol)
    assert geom.origin_scene.y() == pytest.approx(expected.y(), abs=tol)


def _assert_geometry(item : TextItem, geom : TextGeometry | None = None) -> TextGeometry:
    geom = geom or _measure(item)
    _assert_handles_on_handle_rect(item)
    _assert_child_aligns_handles(geom)
    _assert_origin_on_handle_rect(item, geom)
    return geom


def _roundtrip(item : TextItem) -> TextItem:
    buffer = QByteArray()
    xw = QXmlStreamWriter(buffer)
    toXmlBegin(xw)
    item.toXml(xw)
    xw.writeEndElement()
    toXmlEnd(xw)
    xr = QXmlStreamReader(buffer)
    items, _pos = fromXmlItems(xr)
    assert len(items) == 1
    assert isinstance(items[0], TextItem)
    return items[0]


def _make_parented_text(
    scene            : DrawingScene,
    parent_rotation  : float,
    parent_mirror_h  : bool,
    parent_mirror_v  : bool,
    text             : str           = SHORT,
    rotation         : float         = 0.0,
    mirror_h         : bool          = False,
    mirror_v         : bool          = False,
    origin           : RectHandleId  = RectHandleId.TOP_LEFT,
    align_h          : AlignH        = AlignH.LEFT,
    align_v          : AlignV        = AlignV.TOP,
    pos              : QPointF       = PARENTED_POS,
) -> TextItem:
    parent = _DummyParent(
        rotation = parent_rotation,
        mirror_h = parent_mirror_h,
        mirror_v = parent_mirror_v,
    )
    return _make_text(
        scene,
        text     = text,
        rotation = rotation,
        mirror_h = mirror_h,
        mirror_v = mirror_v,
        origin   = origin,
        align_h  = align_h,
        align_v  = align_v,
        pos      = pos,
        parent   = parent,
    )


class TestTextItemBaseline:
    def test_short_string_zero_transform(
        self,
        drawing_scene : DrawingScene,
    ) -> None:
        item = _make_text(drawing_scene, SHORT)
        geom = _assert_geometry(item)

        assert geom.text == SHORT
        assert geom.rotation == pytest.approx(0.0)
        assert not geom.mirror_h
        assert not geom.mirror_v
        assert geom.origin == RectHandleId.TOP_LEFT
        assert geom.width  > 0.0
        assert geom.height > 0.0

    def test_long_string_grows_from_short_baseline(
        self,
        drawing_scene : DrawingScene,
    ) -> None:
        item = _make_text(drawing_scene, SHORT)
        short_geom = _assert_geometry(item)

        item.setText(LONG)
        long_geom = _assert_geometry(item)

        assert long_geom.text == LONG
        assert long_geom.width > short_geom.width
        assert long_geom.origin_scene.x() == pytest.approx(short_geom.origin_scene.x(), abs=TOL)
        assert long_geom.origin_scene.y() == pytest.approx(short_geom.origin_scene.y(), abs=TOL)


@pytest.mark.parametrize("rotation", ROTATIONS)
@pytest.mark.parametrize("mirror_h", MIRRORS)
@pytest.mark.parametrize("mirror_v", MIRRORS)
@pytest.mark.parametrize("align_h", ALIGNS_H)
@pytest.mark.parametrize("align_v", ALIGNS_V)
@pytest.mark.parametrize("text", TEXTS)
class TestTextItemTransforms:
    def test_handle_placement_and_growth(
        self,
        drawing_scene : DrawingScene,
        rotation      : float,
        mirror_h      : bool,
        mirror_v      : bool,
        align_h       : AlignH,
        align_v       : AlignV,
        text          : str,
    ) -> None:
        item = _make_text(
            drawing_scene,
            SHORT,
            rotation = rotation,
            mirror_h = mirror_h,
            mirror_v = mirror_v,
            align_h  = align_h,
            align_v  = align_v,
        )
        short_geom = _assert_geometry(item)

        item.setText(LONG)
        long_geom = _assert_geometry(item)

        assert long_geom.text == LONG
        assert long_geom.width >= short_geom.width
        assert long_geom.origin_scene.x() == pytest.approx(
            short_geom.origin_scene.x(), abs=TOL
        )
        assert long_geom.origin_scene.y() == pytest.approx(
            short_geom.origin_scene.y(), abs=TOL
        )

        if text == LONG:
            item.setText(LONG)
            assert _measure(item).matches(long_geom)


@pytest.mark.parametrize("rotation", ROTATIONS)
@pytest.mark.parametrize("mirror_h", MIRRORS)
@pytest.mark.parametrize("mirror_v", MIRRORS)
@pytest.mark.parametrize("text", TEXTS)
@pytest.mark.parametrize("origin", ORIGINS)
class TestTextItemOrigin:
    def test_origin_change_preserves_rendered_text_and_handles(
        self,
        drawing_scene : DrawingScene,
        rotation      : float,
        mirror_h      : bool,
        mirror_v      : bool,
        text          : str,
        origin        : RectHandleId,
    ) -> None:
        item = _make_text(
            drawing_scene,
            text,
            rotation = rotation,
            mirror_h = mirror_h,
            mirror_v = mirror_v,
            origin   = RectHandleId.TOP_LEFT,
        )
        before = _assert_geometry(item)

        item.setOrigin(origin)
        after = _assert_geometry(item)

        assert after.origin == origin
        assert before.child_matches(after), (
            f"origin {origin.value}: child moved in scene\n"
            f"  before {before.child_scene}\n"
            f"  after  {after.child_scene}"
        )


@pytest.mark.parametrize("rotation", ROTATIONS)
@pytest.mark.parametrize("mirror_h", MIRRORS)
@pytest.mark.parametrize("mirror_v", MIRRORS)
@pytest.mark.parametrize("text", TEXTS)
class TestTextItemSerialization:
    def test_xml_roundtrip_preserves_geometry(
        self,
        drawing_scene : DrawingScene,
        rotation      : float,
        mirror_h      : bool,
        mirror_v      : bool,
        text          : str,
    ) -> None:
        item = _make_text(
            drawing_scene,
            text,
            rotation = rotation,
            mirror_h = mirror_h,
            mirror_v = mirror_v,
            align_h  = AlignH.CENTER,
            align_v  = AlignV.MIDDLE,
            origin   = RectHandleId.MIDDLE_LEFT,
        )
        before = _assert_geometry(item)

        loaded = _roundtrip(item)
        drawing_scene.addItem(loaded)
        after = _assert_geometry(loaded)

        assert after.matches(before), "XML round-trip changed measured geometry"


@pytest.mark.parametrize("rotation", (0.0, 180.0))
@pytest.mark.parametrize("align_h", ALIGNS_H)
@pytest.mark.parametrize("align_v", ALIGNS_V)
@pytest.mark.parametrize("origin", ORIGINS)
class TestTextItemOriginAlign:
    def test_origin_change_with_alignment(
        self,
        drawing_scene : DrawingScene,
        rotation      : float,
        align_h       : AlignH,
        align_v       : AlignV,
        origin        : RectHandleId,
    ) -> None:
        item = _make_text(
            drawing_scene,
            LONG,
            rotation = rotation,
            align_h  = align_h,
            align_v  = align_v,
        )
        before = _assert_geometry(item)
        item.setOrigin(origin)
        after = _assert_geometry(item)
        assert after.origin == origin
        assert before.child_matches(after)


@pytest.mark.parametrize("parent_rotation", ROTATIONS)
@pytest.mark.parametrize("parent_mirror_h", MIRRORS)
@pytest.mark.parametrize("parent_mirror_v", MIRRORS)
@pytest.mark.parametrize("rotation", ROTATIONS)
@pytest.mark.parametrize("mirror_h", MIRRORS)
@pytest.mark.parametrize("mirror_v", MIRRORS)
@pytest.mark.parametrize("align_h", ALIGNS_H)
@pytest.mark.parametrize("align_v", ALIGNS_V)
@pytest.mark.parametrize("text", TEXTS)
class TestTextItemParentedTransforms:
    def test_handle_placement_and_growth(
        self,
        drawing_scene     : DrawingScene,
        parent_rotation   : float,
        parent_mirror_h   : bool,
        parent_mirror_v   : bool,
        rotation          : float,
        mirror_h          : bool,
        mirror_v          : bool,
        align_h           : AlignH,
        align_v           : AlignV,
        text              : str,
    ) -> None:
        item = _make_parented_text(
            drawing_scene,
            parent_rotation = parent_rotation,
            parent_mirror_h = parent_mirror_h,
            parent_mirror_v = parent_mirror_v,
            rotation        = rotation,
            mirror_h        = mirror_h,
            mirror_v        = mirror_v,
            align_h         = align_h,
            align_v         = align_v,
        )
        short_geom = _assert_geometry(item)

        item.setText(LONG)
        long_geom = _assert_geometry(item)

        assert long_geom.text == LONG
        assert long_geom.width >= short_geom.width
        assert long_geom.origin_scene.x() == pytest.approx(
            short_geom.origin_scene.x(), abs=TOL
        )
        assert long_geom.origin_scene.y() == pytest.approx(
            short_geom.origin_scene.y(), abs=TOL
        )

        if text == LONG:
            item.setText(LONG)
            assert _measure(item).matches(long_geom)


@pytest.mark.parametrize("parent_rotation", ROTATIONS)
@pytest.mark.parametrize("parent_mirror_h", MIRRORS)
@pytest.mark.parametrize("parent_mirror_v", MIRRORS)
@pytest.mark.parametrize("rotation", ROTATIONS)
@pytest.mark.parametrize("mirror_h", MIRRORS)
@pytest.mark.parametrize("mirror_v", MIRRORS)
@pytest.mark.parametrize("text", TEXTS)
@pytest.mark.parametrize("origin", ORIGINS)
class TestTextItemParentedOrigin:
    def test_origin_change_preserves_rendered_text_and_handles(
        self,
        drawing_scene     : DrawingScene,
        parent_rotation   : float,
        parent_mirror_h   : bool,
        parent_mirror_v   : bool,
        rotation          : float,
        mirror_h          : bool,
        mirror_v          : bool,
        text              : str,
        origin            : RectHandleId,
    ) -> None:
        item = _make_parented_text(
            drawing_scene,
            parent_rotation = parent_rotation,
            parent_mirror_h = parent_mirror_h,
            parent_mirror_v = parent_mirror_v,
            text            = text,
            rotation        = rotation,
            mirror_h        = mirror_h,
            mirror_v        = mirror_v,
            origin          = RectHandleId.TOP_LEFT,
        )
        before = _assert_geometry(item)

        item.setOrigin(origin)
        after = _assert_geometry(item)

        assert after.origin == origin
        assert before.child_matches(after), (
            f"parent {parent_rotation}° mh={parent_mirror_h} mv={parent_mirror_v} "
            f"child {rotation}° mh={mirror_h} mv={mirror_v} "
            f"origin {origin.value}: child moved in scene\n"
            f"  before {before.child_scene}\n"
            f"  after  {after.child_scene}"
        )


@pytest.mark.parametrize("parent_rotation", ROTATIONS)
@pytest.mark.parametrize("parent_mirror_h", MIRRORS)
@pytest.mark.parametrize("parent_mirror_v", MIRRORS)
@pytest.mark.parametrize("rotation", ROTATIONS)
@pytest.mark.parametrize("align_h", ALIGNS_H)
@pytest.mark.parametrize("align_v", ALIGNS_V)
@pytest.mark.parametrize("origin", ORIGINS)
class TestTextItemParentedOriginAlign:
    def test_origin_change_with_alignment(
        self,
        drawing_scene     : DrawingScene,
        parent_rotation   : float,
        parent_mirror_h   : bool,
        parent_mirror_v   : bool,
        rotation          : float,
        align_h           : AlignH,
        align_v           : AlignV,
        origin            : RectHandleId,
    ) -> None:
        item = _make_parented_text(
            drawing_scene,
            parent_rotation = parent_rotation,
            parent_mirror_h = parent_mirror_h,
            parent_mirror_v = parent_mirror_v,
            text            = LONG,
            rotation        = rotation,
            align_h         = align_h,
            align_v         = align_v,
        )
        before = _assert_geometry(item)
        item.setOrigin(origin)
        after = _assert_geometry(item)
        assert after.origin == origin
        assert before.child_matches(after)
