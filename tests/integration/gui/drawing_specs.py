"""Data-driven GUI drawing integration cases."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from PyQt6.QtCore import QPointF

_TESTS_DIR = Path(__file__).resolve().parents[2]
FIXTURES_DSN_DIR = _TESTS_DIR / "fixtures" / "dsn"


@dataclass(frozen=True)
class DrawingDragStep:
    kind: Literal["drag"] = "drag"
    p1: QPointF = field(default_factory=QPointF)
    p2: QPointF = field(default_factory=QPointF)


@dataclass(frozen=True)
class DrawingPlaceModeStep:
    kind: Literal["place_mode"] = "place_mode"
    mode: str = "placeRectangle"


DrawingStep = DrawingDragStep | DrawingPlaceModeStep


@dataclass(frozen=True)
class DrawingCase:
    id: str
    fixture: Path
    steps: tuple[DrawingStep, ...]
    new_design: bool = True
    enabled: bool = True


DRAWING_CASES: tuple[DrawingCase, ...] = (
    DrawingCase(
        id="rectangle_place",
        fixture=FIXTURES_DSN_DIR / "rectangle_place.dsn",
        steps=(
            DrawingPlaceModeStep(mode="placeRectangle"),
            DrawingDragStep(
                p1=QPointF(100.0, 100.0),
                p2=QPointF(250.0, 250.0),
            ),
        ),
    ),
)
