import functools

from typing          import Any
from collections.abc import Callable


def withScene(func : Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for `QGraphicsItem` methods whose first positional argument
    (after `self`) is an optional `scene` defaulting to `None`.

    The wrapper resolves the scene as follows:
      * if the caller supplies a non-`None` scene, it is forwarded unchanged;
      * otherwise `self.scene()` is used;
      * if that is also `None` (the item is not yet attached to a scene), the
        wrapped method is skipped and `None` is returned.

    Use to eliminate the boilerplate:

        def method(self, scene=None, ...):
            if scene is None:
                if (scene := self.scene()) is None:
                    return
            ...
    """
    @functools.wraps(func)
    def wrapper(self, scene = None, *args, **kwargs):
        if scene is None:
            if (scene := self.scene()) is None:
                return None
        return func(self, scene, *args, **kwargs)
    return wrapper
