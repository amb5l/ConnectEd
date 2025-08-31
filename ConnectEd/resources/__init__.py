from importlib.resources import files  # Python 3.9+

from .fonts import initFonts

def getIconPath(name: str) -> str:
    """Get path to icon resource that works in both dev and packaged environments."""
    try:
        # This works whether installed or in development
        resources = files('ConnectEd.resources.icons')
        return str(resources / name)
    except (ModuleNotFoundError, AttributeError):
        # Fallback for development
        import os
        app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(app_root, "resources", "icons", name)

def initResources() -> None:
    initFonts()
