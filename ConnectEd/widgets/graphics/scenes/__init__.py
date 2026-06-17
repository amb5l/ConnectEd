import functools

from typing          import Any
from collections.abc import Callable


def withScene(func : Callable[..., Any]) -> Callable[..., Any]:
    """
    Gets scene, skips decorated method if it is None.
    """
    @functools.wraps(func)
    def wrapper(self, scene = None, *args, **kwargs):
        if scene is None:
            if (scene := self.scene()) is None:
                return None
        return func(self, scene, *args, **kwargs)
    return wrapper
