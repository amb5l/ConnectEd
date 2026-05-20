import sys

from collections.abc import Callable

from .app import ConnectEdApp as App, app

from .widgets.window import Window


def run(
    func : Callable[["App"], None],
    argv : list[str] = []
) -> None:
    try:
        if App.instance() is None:
            sys.argv = [sys.argv[0]] + argv + sys.argv[1:]
            from .main import main
            main(func)
        else:
            func(app())
            if exit:
                app().quit()
    except Exception as e:
        print(f"Script error: {e}")
        raise


__all__ = ["run", "App", "Window"]