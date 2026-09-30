# ConnectEd scripting

Scripted tests, macros, and demos. Import as `import ConnectEd.scripting as cs`.
Methods under this package use camelCase (`processEvents`, `withModal`,
`mouseDrag`).

## Two runtime modes

| Mode | Entry | Typical use |
|------|--------|-------------|
| **CLI** | `cs.run(fn, ["--cli"])` | Model, scenes, nodes — no `Window`. Headless CI. |
| **GUI** | `cs.run(fn, ["--nosplash"])` + `cs.gui(window)` | Full window, menus, modals, QTest mouse. |

Tests: [`test_scripted_cli.py`](../../tests/integration/test_scripted_cli.py),
[`test_scripted_gui.py`](../../tests/integration/test_scripted_gui.py).

## GUI driver

```python
import ConnectEd.scripting as cs

def test(app: cs.App) -> None:
    window = app.window()
    driver = cs.gui(window)

    bar = driver.menuBar()
    about = bar.getMenus()["Help"].getAction("About")
    driver.withModal(about.trigger, onAbout)

cs.run(test, ["--nosplash"])
```

- `driver.window()` → ConnectEd `Window`.
- `driver.menuBar()` → `MenuBar` with `getMenus()`, `getAction()`.
- Navigation uses ConnectEd menu/action APIs, not raw `QMenuBar` walks.

Factory: [`gui.py`](gui.py). Qt delivery: [`qt/`](qt/) (`core`, `modal`,
`shell`, `mouse`).

## QTest mouse (`qt/mouse.py`)

| Method | Role |
|--------|------|
| `mousePress` / `mouseMove` / `mouseRelease` | Explicit steps; `processEvents()` after each |
| `mouseClick(widget, pos, …)` | Press + release at viewport coordinates |
| `mouseDrag(widget, pos1, pos2=None, …)` | Full drag; `pos2=None` leaves button held |
| `viewPos(view, scene)` / `scenePos(view, view_pt)` | Scene ↔ viewport mapping |

ConnectEd enters drag only after move distance ≥ `prefs/mouse/drag`. Example:
[`examples/scripts/gui.py`](../../examples/scripts/gui.py).

## Modals (`withModal`)

Blocking dialogs need the opener on the next event-loop tick:

```python
def onAbout() -> None:
    modal = driver.activeModal()
    assert modal is not None
    modal.accept()

driver.withModal(about.trigger, onAbout)
```

## GUI in CI

Use a real `QApplication` (not `--cli`). Linux: `QT_QPA_PLATFORM=offscreen` or
`xvfb-run`. Prefer `--nosplash`, `withModal` / `schedule`, `processEvents`.

```powershell
.venv\Scripts\python.exe -m pytest tests/integration/test_scripted_gui.py -v
```
