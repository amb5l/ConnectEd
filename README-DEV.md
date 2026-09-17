# ConnectEd development setup

Python 3.11+ is required (`pyproject.toml`). Commands below assume the
repository root.

## Virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Linux / macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

The interpreter is `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python`
(Unix). Prefer that path over a bare `python` on PATH. See
[tests/README.md](tests/README.md) for how to run tests.

Run the app:

```powershell
.venv\Scripts\python.exe ConnectEd/main.py
```

## Cursor / VS Code

This repo’s workspace settings (`.vscode/settings.json`) point the Python
interpreter at `.venv` and configure Cursor Pyright.

On first open, install the **workspace recommended extensions** when prompted,
or install from [`.vscode/extensions.json`](.vscode/extensions.json):

| Extension | ID |
|---|---|
| Cursor Pyright | `anysphere.cursorpyright` |
| Python | `ms-python.python` |
| Python Debugger | `ms-python.debugpy` |
| Ruff | `charliermarsh.ruff` |
| Even Better TOML | `tamasfe.even-better-toml` |
| YAML | `redhat.vscode-yaml` |
| ANTLR4 | `mike-lischke.vscode-antlr4` |

Do **not** install Microsoft Pylance (`ms-python.vscode-pylance`). Cursor uses
Pyright instead; the two conflict.

After installing extensions:

1. Command Palette → **Developer: Reload Window**.
2. Open a `.py` file.
3. Command Palette → **Python: Select Interpreter** → the `.venv` interpreter.

`Python: Select Interpreter` comes from `ms-python.python`. Cursor’s built-in
Python support is syntax highlighting only; without that extension the command
does not appear.

Ruff is the in-editor linter/formatter (`[tool.ruff]` in `pyproject.toml`).
Flake8 and mypy stay available on the command line via the `dev` extra.
