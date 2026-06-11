"""Scratch: XOR gate jog staircase lane ordering."""
import traceback
from pathlib import Path

from PyQt6.QtCore import QPointF

log = Path(__file__).with_suffix(".log")
log.write_text("", encoding="utf-8")


def w(msg: str) -> None:
    with open(log, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg, flush=True)


def lanes_for(offset_y: float) -> list[tuple[float, float | None]]:
    from ConnectEd.core.db import DesignDbNode
    from ConnectEd.core.types import Axis
    from ConnectEd.widgets.graphics.items.gate import XorGateItem
    from ConnectEd.widgets.graphics.views.diagram import DiagramView
    from ConnectEd.widgets.graphics.views.diagram.interaction.move import DiagramMoveInteraction

    path = Path(__file__).resolve().parents[1] / "examples" / "test.dsn"
    db = DesignDbNode.load(str(path))
    view = DiagramView(db.scene())
    xor = next(i for i in db.scene().items() if isinstance(i, XorGateItem))
    pos = xor.scenePos()
    move = DiagramMoveInteraction(view, [xor], pos, slide=True)
    move.update(pos + QPointF(0, offset_y))
    rows = []
    for jog in move._rubber_jogs:
        ss = jog._static.scenePos()
        across = ss.y() if jog.axis() == Axis.H else ss.x()
        rows.append((across, jog.lane()))
    return sorted(rows)


try:
    import ConnectEd.scripting as cs

    def test(app: cs.App) -> None:
        up = lanes_for(-40)
        down = lanes_for(40)
        w(f"up   {up}")
        w(f"down {down}")
        assert up[0][1] < up[1][1], up
        assert down[0][1] > down[1][1], down
        w("ok")

    cs.run(test, ["--nosplash"])
except Exception:
    traceback.print_exc(file=open(log, "a", encoding="utf-8"))
    raise
