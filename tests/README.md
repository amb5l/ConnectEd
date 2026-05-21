# ConnectEd Tests

## Prerequisites

Activate virtual environment first:
```bash
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

## Running From Repository Root

**All tests:**
```bash
python tests/run_tests.py
```

**Specific test file:**
```bash
python -m pytest tests/integration/test_scripted_gui.py
python -m pytest tests/unit/test_vhdl.py
```

**Specific test method:**
```bash
python -m pytest tests/integration/test_scripted_gui.py::TestScriptedGUI::test_method_name
```

**Integration tests only:**
```bash
python -m pytest tests/integration/
```

**Unit tests only:**
```bash
python -m pytest tests/unit/
```

### Direct Script Execution

**GUI integration test:**
```bash
python tests/integration/test_scripted_gui.py
```

## Drawing integration fixtures

Golden designs live under `tests/fixtures/dsn/`. GUI drawing cases are declared in `tests/integration/gui/drawing_specs.py` (`DRAWING_CASES`).

To regenerate `rectangle_place.dsn` after intentional serializer changes:

```bash
.venv\Scripts\python.exe -c "import runpy; runpy.run_path('tests/fixtures/dsn/gen_rectangle_place.py', run_name='__main__')"
```

Add a new case: create the `.dsn` (script or app save), add a `DrawingCase` row with matching `steps`, set `enabled=True`.
