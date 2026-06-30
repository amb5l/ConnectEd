# None typing — scope and plan

Audit of optional `None` in instance attributes and return types, and a plan to
reduce type-checker friction without fighting real optional semantics.

Related: `PROPERTIES.md`, origin refactor in `ItemTransformMixin` (`hasOrigin()`
/ `origin() -> T`).

---

## Size of the issue

Rough counts (grep for `T | None` on attrs and `-> T | None` on methods, plus
`is None` guards):

| Area | Files touched | `T \| None` annotations | `-> T \| None` | `is None` guards |
|------|--------------:|------------------------:|---------------:|-----------------:|
| `widgets/graphics/items/` | ~29 / 46 | ~214 | ~43 | ~180+ |
| `widgets/graphics/items/mixin/` | ~14 / 18 | ~72 | ~27 | (included above) |
| `widgets/graphics/` (whole tree) | ~80+ | ~350+ | ~80+ | ~400+ |
| `widgets/graphics/properties.py` | 1 | ~30 | 4 | ~14 |
| `core/types.py` | 1 | 2 | 0 | 1 |
| Dialogs / views / scenes (graphics-adjacent) | many | significant | significant | heavy in state machines |

**Verdict:** medium-large, but **clustered**. Most pain is not “None everywhere”
but ~6 recurring patterns. A focused pass on items + presentation + properties
would remove a large share of `isinstance`/`if x is None` boilerplate in call
sites without a repo-wide purge.

**Not a goal:** eliminate `None` where it is the correct domain value (Qt parent,
disconnected segment endpoint, “use scene default” override, property not found).

---

## Three meanings (your taxonomy)

Use this when deciding whether to keep `T | None` or refactor.

| Code | Meaning | Keep `\| None`? | Preferred typing pattern |
|------|---------|------------------|---------------------------|
| **(a) Meaningful value** | Absence is valid data | **Yes** | `T \| None` on return; document contract |
| **(b) Not yet initialised** | Set in `init*` after `__init__` | **No** (prefer) | `hasX()` + `x() -> T`, or init order / `@checked` |
| **(c) Not in use / unsupported** | Feature absent on this class | **No** (prefer) | Omit attribute; `hasX()`; split mixin or role |

Examples already aligned with **(b)/(c)**:

- **Origin:** `_ORIGIN` undefined ⇒ no transform origin; `hasOrigin()` +
  `origin() -> T` (not `T | None`).
- **Presentation:** attribute **missing** ⇒ unsupported; attribute **`= None`** ⇒
  supported but “use scene default” (intentional **(a)** for overrides).

Examples that should stay **`None`**:

- `SegmentItem` endpoints while wiring connectivity.
- `PropertiesManager.value()` when name unknown (sentinel + log).
- `onSceneChanged(scene: DrawingScene | None)` when item leaves scene.
- `T | None | NoChange` edit APIs (`None` = clear override).

---

## Categories (where the annotations live)

### 1. Presentation overrides (~40–50 attrs, ~22 returns)

Files: `mixin/presentation/{__init__,text,line,fill}.py`

- `_line_color: QColor | None = None` etc. — **(a)** “use theme default”.
- `hasTextColor()` / `hasattr` — **(c)** unsupported on this item.
- Getters `textColor() -> QColor | None` force guards before use.

**Plan:** keep `| None` on storage for **(a)**; tighten getters that are only
called after `has*` or from dialogs that accept optional. Consider
`defaultTextColor() -> QColor` (non-optional) vs `textColor() -> QColor | None`
(override only).

### 2. Qt / platform nullability (~30)

- `parent: QGraphicsItem | None`, `scene() -> DiagramScene | None`,
  `paint(..., widget: QWidget | None)`.

**Plan:** **leave as-is** (external API). Narrow once at boundary
(`ItemSceneMixin.scene()`), then use non-optional `DiagramScene` on items that
require a scene (`@checked` or `narrow()`).

### 3. Graph / geometry (~20)

Files: `segment.py`, `node.py`, `polyline.py`, `rubber.py`

- `_node1: NodeItem | None` — **(a)** during/after connect.
- `axis() -> Axis | None`, `sweep() -> float | None` — **(a)** geometric
  degeneracy.

**Plan:** keep returns; add `hasNode1()` / connect-state enum only if call-site
noise is high. Low priority.

### 4. Property system (~34 in `properties.py`)

- Metadata optional on descriptors; lookup returns `None` on failure.
- Tri-state queries: `inherent(name) -> bool | None`.

**Plan:** document in `PROPERTIES.md`; optional later `PropertyLookup` Result
type. Do not rush — many callers rely on `None` + log.

### 5. Bindings / handles (~15)

Files: `property_text.py`, `grip.py`, `handle.py`, `tether.py`

- `item() -> ItemHandlesMixin | None`, `handle() -> HandleItem | None`.
- Often followed by immediate `if x is None: raise TypeError`.

**Plan:** **high impact** — split protocols or use `narrow()` / non-optional
returns where caller always raises (grip on valid handle parent).

### 6. Lifecycle / init guards (~10)

- `hasattr(self, "_tether")` in `property_text.py`.
- `_origin: T` before `initTransform()` — type says always `T`, runtime uses
  `hasOrigin()`.

**Plan:** align types with init order (same as origin pattern); avoid `T | None`
on attrs that are always set before public use.

### 7. Edit/command unions (`T | None | NoChange`)

Files: `text.py`, `properties.editText()`, presentation setters.

**Plan:** **keep** — three-way semantics are intentional.

---

## Inconsistencies to fix (high value)

| Issue | Example | Action |
|-------|---------|--------|
| Return `\| None` then immediate raise | `grip.handle()`, `grip.item()` | `-> T` + `@checked` or `narrow()` |
| `origin()` without `hasOrigin()` | older call sites | finish origin sweep (dialogs, properties sync) |
| `getattr(..., False)` on always-init attrs | `mirrorH()` | direct `_mirror_h: bool` |
| Dual “unsupported” vs “default None” | presentation | document; don’t merge semantics |
| Storage `T` vs `hasattr` | `_origin: T` | **done** for origin; replicate for other init-gated attrs |
| Tri-state bool queries | `inherent() -> bool \| None` | defer; document caller rules |

---

## Recommended patterns (standard library for ConnectEd)

1. **Optional capability (no feature)**  
   Class has no `_ORIGIN` / no `_text_color` attribute ⇒ `hasOrigin()`,
   `hasTextColor()` via `hasattr` or role mixin. Accessor `-> T` only after `has*`.

2. **Optional value (feature present, value absent)**  
   Keep `T | None` on storage and returns; use **(a)** explicitly in docstring.

3. **Init-gated state**  
   Set in `initItem` / `initTransform`; public methods assume initialised or call
   `has*` first. Do **not** expose `-> T | None` if callers always treat `None`
   as bug.

4. **Boundary narrowing**  
   `ItemSceneMixin`, `narrow()`, `@checked` at Qt/mixin boundary — internal
   code uses non-optional types.

5. **Generics instead of `\| None` for IDs**  
   `ItemTransformMixin[T]`, `ItemHandlesMixin[T]` — already started; extend
   where `HandleId | None` was only used for typing weakness.

---

## Phased plan

### Phase 0 — Policy (this doc)

- [ ] Agree taxonomy **(a)/(b)/(c)** on PRs touching optional types.
- [ ] New optional features: pick pattern before adding `T | None`.

### Phase 1 — Origin / transform (mostly done)

- [x] `hasOrigin()`, `origin() -> T`, `setOrigin` uses `hasOrigin()`.
- [ ] Audit call sites still using `origin() is None` or `RectHandleId` guards
      after `origin()` (e.g. text dialog init).
- [ ] `getOriginHandle() -> HandleItem` — ensure callers don’t null-check.

**Files:** `transform.py`, `handle.py`, `grip.py`, `text.py` dialog,
`properties.py` sync, `property_text.py`.

### Phase 2 — Grip / handle bindings (~2–4 files, high ROI)

- [ ] `HandleGripItem.handle() -> HandleItem` (raise if bad parent).
- [ ] `HandleGripItem.item() -> ItemHandlesMixin` where context guarantees handle.
- [ ] Review `MoveGripItem.ctxMenuItems` — already uses `hasOrigin()`.

**Files:** `grip.py`, `handle.py`.

### Phase 3 — Presentation getters (~4 files, medium ROI)

- [ ] Split API: `hasTextColor()` vs `textColor() -> QColor | None` vs
      `defaultTextColor(scene) -> QColor` (non-optional).
- [ ] Dialog code paths: use `has*` before optional getters; use defaults where
      theme always applies.
- [ ] Same for line/fill/quill.

**Files:** `mixin/presentation/*.py`, `dialogs/appearance.py`,
`dialogs/items/text.py`.

### Phase 4 — PropertyText / tether (~2 files)

- [ ] `name() -> str` after init (not `str | None`).
- [ ] `cleat() -> HandleId | None` — **keep** if cleat optional **(a)**.
- [ ] Replace `hasattr("_tether")` with init order or `hasTether()`.

**Files:** `property_text.py`, `tether.py`.

### Phase 5 — Segment / polyline (~3 files, lower priority)

- [ ] Keep `NodeItem | None` on endpoints; optional `isConnected()` helpers.
- [ ] Document `sweep() -> float | None` etc. as **(a)**.

**Files:** `segment.py`, `polyline.py`, `node.py`.

### Phase 6 — Properties module (defer)

- [ ] Tri-state queries and descriptor metadata — design separately; large
      caller surface.

**Files:** `properties.py`, `doc/PROPERTIES.md`.

---

## What not to do

- Strip `None` from Qt signatures or protocols that mirror Qt callbacks.
- Force `origin() -> T` on classes without `_ORIGIN` — use bare
  `ItemTransformMixin` / no `origin()` on a split mixin instead.
- Repo-wide `reportOptional*` pyright disables — fix semantics instead.
- Replace meaningful **(a)** `None` with sentinel objects without domain need.

---

## Success metrics

- Fewer `isinstance(..., RectHandleId)` / `if x is None: raise TypeError("Bad …")`
  after known `has*` / init.
- Pyright standard mode: reduced `possibly None` / `not assignable` in
  `items/` and `dialogs/items/` without new `# pyright: ignore`.
- Clear doc per module: which attrs are **(a)/(b)/(c)**.

---

## Quick reference — heaviest files

| File | Priority | Main None theme |
|------|----------|-----------------|
| `properties.py` | Phase 6 | lookup / metadata |
| `mixin/presentation/text.py` | Phase 3 | theme overrides |
| `property_text.py` | Phase 4 | binding / init |
| `segment.py` | Phase 5 | connectivity **(a)** |
| `polyline.py` | Phase 5 | arc math **(a)** |
| `grip.py` / `handle.py` | Phase 2 | raise vs `\| None` |
| `mixin/transform.py` | Phase 1 | **hasOrigin** template |
| `text.py` | Phase 3 | `NoChange` unions + dialog guards |

---

## Immediate next steps (suggested)

1. Finish Phase 1 origin call-site sweep (grep `origin()` + `is None`).
2. Phase 2: tighten `grip.handle()` / `grip.item()` return types.
3. Add **(a/b/c)** comment on new `_foo: T | None` attrs in items (one line).

Estimated effort: **Phase 1–2 ~1 session**, **Phase 3 ~2 sessions**, **Phase 4–5
as touched**, **Phase 6 separate project**.
