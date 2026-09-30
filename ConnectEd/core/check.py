"""Runtime type checks at API boundaries.

``@checked`` wraps typeguard ``typechecked``. It runs only when ``__debug__``
is true (normal dev builds), unless ``always=True``.

Decorate annotated boundary methods (``__init__``, scene and command APIs,
getters/setters, ``fromXml`` / ``toXml``, netlist). Skip Qt overrides, untyped
passthroughs, and inner hot loops. Widen hints to match real call shapes
instead of removing the decorator.
"""

from typing          import Any, TypeVar, overload
from collections.abc import Callable

from typeguard import typechecked


T = TypeVar("T", bound=Callable[..., Any])


@overload
def checked(fn : T, /, *, always : bool = False) -> T: ...


@overload
def checked(fn : None = None, /, *, always : bool = False) -> Callable[[T], T]: ...


def checked(
    fn     : T | None = None,
    /,
    *,
    always : bool = False,
) -> T | Callable[[T], T]:
    if fn is None:
        def decorator(f : T) -> T:
            return checked(f, always=always)
        return decorator

    if always or __debug__:
        return typechecked(fn)  # type: ignore[return-value]
    return fn
