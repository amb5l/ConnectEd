from typing import Callable

from .app  import ConnectEdApp, ConnectEdCliApp, ConnectEdGuiApp, app
from .main import main


def run(func : Callable[["ConnectEdCliApp | ConnectEdGuiApp"], None]) -> None:
    try:
        if app() is None:
            main(func)
        else:
            func(app())
    except Exception as e:
        print(f"Script error: {e}")
        raise
