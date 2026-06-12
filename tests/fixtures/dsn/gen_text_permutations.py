"""Save text_permutations.dsn for viewing (run from repo root with venv Python).

Equivalent to::

    pytest tests/unit/widgets/test_text_item_geometry.py --save-dsn tests/fixtures/dsn/text_permutations.dsn -q
"""

import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent / "text_permutations.dsn"
_REPO = Path(__file__).resolve().parents[2]
_PYTHON = _REPO / ".venv" / "Scripts" / "python.exe"


def main() -> None:
    python = _PYTHON if _PYTHON.is_file() else sys.executable
    subprocess.run(
        [
            str(python),
            "-m",
            "pytest",
            "tests/unit/widgets/test_text_item_geometry.py",
            "--save-dsn",
            str(OUT),
            "-q",
        ],
        cwd = _REPO,
        check = True,
    )


if __name__ == "__main__":
    main()
