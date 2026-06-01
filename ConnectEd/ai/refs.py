"""Opaque object reference registry for AI tool arguments."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Self

from PyQt6.QtCore import QObject

from ..core.check import checked


def refKind(ref : str) -> str | None:
    if ":" not in ref:
        return None
    return ref.split(":", 1)[0]


@dataclass
class RefRegistry:
    _next_id : int = 0
    _by_ref  : dict[str, Any] = field(default_factory=dict)

    @checked
    def issue(self : Self, kind : str, obj : Any) -> str:
        if not kind or ":" in kind:
            raise ValueError(f"Invalid ref kind: {kind!r}")
        self._next_id += 1
        ref = f"{kind}:{self._next_id}"
        self._by_ref[ref] = obj
        if isinstance(obj, QObject):
            obj.destroyed.connect(lambda *, r=ref : self._drop(r))
        return ref

    @checked
    def resolve(
        self    : Self,
        ref     : str,
        kind    : str | None = None,
    ) -> Any | None:
        ref_kind = refKind(ref)
        if ref_kind is None:
            return None
        if kind is not None and ref_kind != kind:
            return None
        return self._by_ref.get(ref)

    @checked
    def drop(self : Self, ref : str) -> None:
        self._drop(ref)

    def _drop(self : Self, ref : str) -> None:
        self._by_ref.pop(ref, None)
