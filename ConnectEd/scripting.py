import sys

from typing import Callable

from .app  import ConnectEdApp, app


def run(
    func : Callable[["ConnectEdApp"], None],
    argv : list[str] = [],
    exit : bool = True
) -> None:
    try:
        if app() is None:
            sys.argv = [sys.argv[0]] + argv + sys.argv[1:]
            from .core import args
            from .main import main
            main(func, exit)
        else:
            func(app())
            if exit:
                app().quit()
    except Exception as e:
        print(f"Script error: {e}")
        raise
