import sys

from typing import Callable

from .app  import ConnectEdCliApp, ConnectEdGuiApp, app


def run(
    func : Callable[["ConnectEdCliApp | ConnectEdGuiApp"], None],
    argv : list[str] = []
) -> None:
    try:
        if app() is None:
            sys.argv = [sys.argv[0]] + argv + sys.argv[1:]
            from .core import args
            from .main import main
            main(func)
        else:
            func(app())
    except Exception as e:
        print(f"Script error: {e}")
        raise
