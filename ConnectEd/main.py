import sys

from .api  import initGui
from .core import logger

from . import hub


def main() -> int:
    logger.info("started")
    initGui()
    r = hub.app.exec()
    hub.settings.save()
    logger.info("finished")
    return r

if __name__ == "__main__":
    r = main()
    logger.info(f"exited with code {r}")
    sys.exit(r)
