# `@checked` runtime type checking

ConnectEd uses [`checked`](../ConnectEd/core/check.py) to validate arguments and
return values at API boundaries during development. It wraps
[typeguard](https://typeguard.readthedocs.io/) `typechecked` and raises
`TypeCheckError` when a caller passes the wrong type or a method returns a
mismatch.

```python
from ConnectEd.core.check import checked

@checked
def editMove(
    self     : Self,
    items    : ItemType | list[ItemType],
    offset   : QPointF,
    slide    : bool = False,
    undoable : bool = False,
) -> None:
    ...
```

## When checks run

By default, `@checked` is active **only when `__debug__` is true** — normal
dev runs, not `python -O` optimized builds.

| Mode | Behavior |
|------|----------|
| Default (`always=False`) | Checks run when `__debug__` is true |
| `always=True` | Checks run in all builds, including `-O` |

Use the default everywhere. Reserve `always=True` for critical paths where you
ship optimized binaries but still want runtime validation (e.g. undo command
constructors).

```python
@checked(always=True)
def __init__(self, scene: DiagramScene, item: SegmentItem) -> None:
    ...
```

## Prerequisites: annotate first

`@checked` validates against **existing type hints**. Decorating a method with
no parameter or return annotations adds almost no protection.

When touching a module for rollout:

1. Add or fix hints on boundary methods (`__init__`, public API, `fromXml`,
   setters).
2. Apply `@checked` on those same methods in the same change.

Do not block rollout on annotating every private helper, Qt override, or
`_PROPERTIES` lambda unless you are about to decorate that method.

## When to decorate

Apply `@checked` on **annotated** boundary methods:

1. **`__init__`** on widgets, items, interactions, commands, and dialogs.
2. **Scene and command boundaries** — `scenes/diagram/api/`, `scenes/drawing/api/`,
   and `cmd/*` `__init__`, `redo`, and `undo` where types are known.
3. **Item and property accessors** — `setX` / `getX`, property getters and
   setters, `fromXml` / `toXml` where signatures are stable.
4. **Netlist and connectivity** — follow the pattern in
   [`netlist.py`](../ConnectEd/widgets/graphics/scenes/diagram/netlist.py).

## When to skip

Leave methods undecorated when type checking is impractical or misleading:

- **Qt framework overrides** fed by the framework (`paint`, `boundingRect`,
  `itemChange`) unless option types are standardized project-wide.
- **Untyped passthrough** — methods with `*args: Any, **kwargs: Any` that forward
  to dynamic targets (e.g. base `Interaction.commit`); decorate concrete
  `_commit` overrides instead.
- **Unannotated private helpers** — annotate and decorate together, or leave
  plain until the API stabilizes.
- **Inner hot loops** — avoid decorating per-iteration helpers; keep checks at
  entry points (netlist already uses many checks at method boundaries).

## Fix hints before decorating

If a method accepts more shapes than the hint suggests, **widen the hint** — do
not rely on runtime `isinstance` alone and do not remove `@checked` to silence
errors.

Example: a method that accepts a single item or a list should be annotated as
`ItemType | list[ItemType]`, not `list[ItemType]`.

When `TypeCheckError` appears during testing, correct the types or hints; only
remove `@checked` if the API is genuinely dynamic.

## Scope

| In scope | Out of scope (for now) |
|----------|------------------------|
| `ConnectEd/**` except `hdl/**` | `ConnectEd/hdl/**` |
| Methods with complete parameter and return annotations | Generated or parser visitors under `hdl` |
| Public and boundary APIs | Methods that intentionally use untyped `*args` / `**kwargs` without narrowing |

## Verification

After adding `@checked` to a surface:

1. Run the app in a normal debug build (`__debug__` true).
2. Exercise the touched surface (place, move, delete, properties, netlist
   refresh, etc.).
3. Fix `TypeCheckError` by correcting types or hints.
4. Optionally run `mypy` or `pyright` on the touched modules — static analysis
   complements `@checked`; it does not replace it.

## Why this helps

Runtime checks catch caller mistakes at boundaries instead of silent coercion
or late failures deep in call chains. Real bugs have already surfaced only under
`@checked` (e.g. interactions annotated as `list[ItemType]` but called with a
single item). The rollout is incremental: decorate boundaries as modules are
touched, not via a blind codemod over every `def`.
