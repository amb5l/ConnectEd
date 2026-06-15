class DocumentItem:
    pass


def _bases_excluding(marker : type, cls : type) -> tuple[type, ...]:
    return tuple(
        base for base in cls.__bases__
        if base is not marker
    )


class DecorativeItem(DocumentItem):
    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if cls is DecorativeItem:
            return
        for base in _bases_excluding(DecorativeItem, cls):
            if issubclass(base, FunctionalItem):
                raise TypeError(
                    f"{cls.__qualname__} cannot inherit both "
                    f"DecorativeItem and FunctionalItem"
                )


class FunctionalItem(DocumentItem):
    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if cls is FunctionalItem:
            return
        for base in _bases_excluding(FunctionalItem, cls):
            if issubclass(base, DecorativeItem):
                raise TypeError(
                    f"{cls.__qualname__} cannot inherit both "
                    f"DecorativeItem and FunctionalItem"
                )


class ChromeItem:
    pass
