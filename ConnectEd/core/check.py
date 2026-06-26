from typing          import Any, TypeVar
from collections.abc import Callable
from functools       import partial

from typeguard import typechecked


T = TypeVar("T", bound=Callable[..., Any])


def checked(
    fn: T | None = None, /, *, always: bool = False
) -> T:
    if fn is None:
        return partial(checked, always=always)

    if always or __debug__:
        return typechecked(fn)  # type: ignore[return-value]
    return fn
