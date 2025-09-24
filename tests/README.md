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
