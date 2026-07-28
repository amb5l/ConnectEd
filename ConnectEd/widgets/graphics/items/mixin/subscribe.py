import weakref

from typing import Self

from .....core.check import checked


class ItemSubscribeMixin:
    """
    Opt-in per-item event registry: dependent objects register a method name
    to be invoked when the host emits a named event.
    """

    # instance attributes
    _subs : dict[str, weakref.WeakKeyDictionary]

    @checked
    def initSubscribe(self : Self) -> None:
        self._subs = {}

    @checked
    def subscribe(
        self   : Self,
        change : str,
        obj    : object,
        method : str
    ) -> None:
        """Register obj.method to be called when change occurs."""
        self._subs.setdefault(change, weakref.WeakKeyDictionary())[obj] = method

    @checked
    def unsubscribe(self : Self, change : str, obj : object) -> None:
        """Remove an object previously subscribed to a change."""
        if (change_subs := self._subs.get(change)) is not None:
            change_subs.pop(obj, None)

    @checked
    def callSubscribers(self : Self, change : str) -> None:
        """Invoke all methods registered for change."""
        if (change_subs := self._subs.get(change)) is None:
            return
        for obj, method in list(change_subs.items()):
            getattr(obj, method)()
