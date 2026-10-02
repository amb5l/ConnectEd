"""Mark a method the subclass must implement.

The wrapper raises ``NotImplementedError`` when called, so the method body
can be ``...``. ``__isabstractmethod__`` is set so ``ABCMeta`` treats the
method as abstract.

On an ``ABC``, use ``@abstractmethod``. Put ``@classmethod`` above
``@required``, the same way it goes above ``@abstractmethod``.
"""

from typing          import Any, TypeVar, cast
from collections.abc import Callable
from functools       import wraps


F = TypeVar("F", bound=Callable[..., Any])


def required(fn : F) -> F:
    @wraps(fn)
    def wrapper(*args : Any, **kwargs : Any) -> Any:
        if not args:
            name = fn.__qualname__
        elif isinstance(args[0], type):
            name = f"{args[0].__name__}.{fn.__name__}"
        else:
            name = f"{type(args[0]).__name__}.{fn.__name__}"
        raise NotImplementedError(f"{name} must be implemented by a subclass")

    setattr(wrapper, "__isabstractmethod__", True)
    return cast(F, wrapper)
