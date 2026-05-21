"""Generate rectangle_place.dsn (run from repo root with venv Python)."""

from pathlib import Path

import ConnectEd.scripting as cs

from PyQt6.QtCore import QPointF

from ConnectEd.core.db import DesignDbNode
from ConnectEd.widgets.graphics.items.rectangle import RectangleItem

OUT = Path(__file__).resolve().parent / "rectangle_place.dsn"


def _generate(_app: cs.App) -> None:
    node = DesignDbNode()
    node.setText(node.text())
    scene = node.scene()
    rect = RectangleItem()
    scene.addItems([rect])
    rect.setPoints(QPointF(100.0, 100.0), QPointF(250.0, 250.0))
    node.save(str(OUT))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    cs.run(_generate, ["--cli"])
