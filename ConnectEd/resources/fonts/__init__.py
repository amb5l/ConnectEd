from pathlib import Path
from os      import walk

from PyQt6.QtCore import QDir
from PyQt6.QtGui  import QFontDatabase

from ...core import logger

def initFonts() -> None:
    module_dir = Path(__file__).parent
    for root, dirs, files in walk(module_dir):
        for file in files:
            if file.endswith(".ttf"):
                font_path = QDir.fromNativeSeparators(str(Path(root) / file))
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id < 0:
                    logger.error(f"Error loading font: {font_path}")
