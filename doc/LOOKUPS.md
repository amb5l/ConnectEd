# Lookups — Doc, Navigator, MDI, Session

Design notes for **forward and reverse lookups** between documents, navigator rows, subwindows, and paths.

**Related:** [`NAVIGATOR.md`](NAVIGATOR.md) (tree boundary), [`REFACTOR.md`](REFACTOR.md) (checklist), [`SESSION.md`](SESSION.md) (open-doc registry).

---

## Problem

Several features need to find related objects in different layers:

- Refresh label/tooltip after `docChanged`
- Remove L2 row on `docClosed`
- Close all editors for a document
- Focus an existing subwindow for `(doc, subject)`
- Open the same path twice without duplicating session state

Today these are mostly **ad hoc linear scans** duplicated across Navigator, `Doc` implementations, and `MdiArea`.

---

## Three universes (keep separate)

| Owner | What it tracks | Lifetime |
|-------|----------------|----------|
| **Session** | Open `Doc` instances, path dedup on load | App session |
| **Navigator** | Tree rows, `DocBinding` on items | While row exists in model |
| **MdiArea** | `DocSubWindow` editors per `(doc, subject)` | While subwindow exists |

Do **not** merge these into one global registry. Each layer has its own lifecycle; a single map is easy to desync.

---

## Current mechanisms

### Forward lookup (good)

**NavItem → domain:** `DocBinding(doc, subject)` stored on `NavItem` `UserRole`.

Used by row context menus, inline rename delegate, `_openRow`, etc. This is the right pattern — read binding at the point of use, no scan.

```python
@dataclass
class DocBinding:
    doc     : Doc
    subject : DocSubjectProtocol | str   # str = static container row
```

Container rows (e.g. `"Symbol Definitions"`) use `str` subjects; bound rows use `DocSubjectProtocol`.

### Reverse lookup (scattered)

| Direction | Implementation today | Typical cost |
|-----------|----------------------|--------------|
| **Doc → L2 nav row** | `_docNavItem` — scan group children | O(open docs) |
| **Doc → all bound rows** | `_forEachNavItem` + `binding.doc is doc` | O(all nav rows) |
| **Doc → subwindows** | `_subwindowsForDoc`, `_closeSubwindowsForDoc` — scan MDI | O(subwindows) |
| **(doc, subject) → subwindow** | `HdlSchematicDiagramDoc._findSubWindow` — scan MDI again | O(subwindows) |
| **path → doc** | `Session.openDocForPath` — scan `_open_docs` | O(open docs) |
| **(doc, subject) → NavItem** | *Not implemented* — full tree walk only | O(all nav rows) |

Relevant code:

- [`navigator/private.py`](../ConnectEd/widgets/window/navigator/private.py) — `_docNavItem`, `_forEachNavItem`, `_refreshDocNav`, `_removeDocFromTree`, `_subwindowsForDoc`
- [`documents/schematic.py`](../ConnectEd/documents/schematic.py) — `_findSubWindow`
- [`core/session.py`](../ConnectEd/core/session.py) — `openDocForPath`, `_open_docs`
- [`widgets/window/mdi_area.py`](../ConnectEd/widgets/window/mdi_area.py) — builds per-doc/subject tree in `onSubWindowsChanged` (not yet exposed as lookup API)

---

## Design principles

1. **`Doc` must not hold `NavItem` / `QStandardItem` references** — domain stays free of Qt tree widgets.
2. **`Session` owns open documents, not tree shape** — do not put navigator indices in Session.
3. **`DocBinding` stays on each bound row** — forward lookup at click/edit time remains O(1).
4. **Reverse maps live on the UI owner** — Navigator for tree rows, MdiArea for subwindows.
5. **Doc may call `window().mdiArea()` helpers** — still document-agnostic at the `Doc` API; MDI owns the cache.

---

## Recommended: Navigator-owned index

Maintain a small index at **write boundaries only** (`_addDoc`, `_removeDocFromTree`, future symbol subtree rebuild).

```python
# Sketch — lives on Navigator (or NavModel helper), not on Doc

_doc_roots : dict[Doc, NavItem]
# L2 document row (direct child of group item)

_binding_items : dict[tuple[Doc, int], NavItem]
# (doc, id(subject)) → row; subject identity via id(), same as showWindow / navSetLabel
```

### Register

- In `_addRows`: for each row with a non-`str` `DocBinding`, register `(doc, id(subject)) → item`.
- On L2 root item, also `_doc_roots[doc] = item`.

### Unregister

- In `_removeDocFromTree`: drop `doc` from `_doc_roots`; remove all `_binding_items` keys whose `doc` matches (or walk removed subtree once).

### Use

| Operation | Today | With index |
|-----------|-------|------------|
| `_docNavItem` | Scan groups | `_doc_roots.get(doc)` |
| `_refreshDocNav` | Full tree walk | Iterate `_binding_items` where `key[0] is doc` |
| `_removeDocFromTree` | Find root then `removeRow` | `_doc_roots[doc]` directly |
| Symbol row update/delete (future) | — | `_binding_items[(doc, id(symbol))]` |

### Subject keys

Use **`id(subject)`** — the codebase already relies on object identity (`subject is self._scene`, `subject in self._scene.symbols()`). Do not use `subject.name()` (not unique, renames change display only).

Static container rows (`subject: str`) stay **out** of `_binding_items` unless you add an explicit convention (e.g. `(doc, hash(subject))` for containers only).

### Sanity / rebuild

Optional `_rebuildIndexFromModel()` — one tree walk to repopulate indices after a bug or refactor. Not on every `docChanged` refresh.

---

## Recommended: MdiArea lookup helpers

`onSubWindowsChanged` already builds:

```text
dict[Doc, dict[DocSubjectProtocol, list[DocSubWindow]]]
```

Expose (or cache) as:

- `subwindowsFor(doc: Doc) -> list[DocSubWindow]`
- `subwindowFor(doc: Doc, subject: DocSubjectProtocol) -> DocSubWindow | None` (first or active)

Then remove duplicate MDI scans from Navigator (`_subwindowsForDoc`, `_closeSubwindowsForDoc`) and `HdlSchematicDiagramDoc._findSubWindow`.

---

## Session path index (optional, lower priority)

`openDocForPath` as a linear scan is acceptable for small open-doc counts. If needed later:

```python
_path_by_doc : dict[str, Doc]   # cleanPath → doc
```

Updated in `load`, `close`, and `setPath` / Save As. Independent of Navigator index.

---

## What not to do

| Avoid | Why |
|-------|-----|
| One “god registry” for nav + MDI + session | Three lifecycles; hard to keep consistent |
| Reverse refs on `Doc` | Violates layering; doc may outlive tree rows |
| Index only L2, still walk tree for symbols | Symbol purge/rebuild will scan again |
| Replace `DocBinding` with index-only lookups | Menus/delegate still need binding without a second hop |
| Store `NavItem` on `Doc` | Documented anti-pattern in [`NAVIGATOR.md`](NAVIGATOR.md) |

---

## Phased delivery

### Phase 1 — doc roots only (small, low risk)

- Add `_doc_roots: dict[Doc, NavItem]`.
- Register in `_addDoc`; unregister in `_removeDocFromTree`.
- Replace `_docNavItem` implementation.
- Keep `_forEachNavItem` for `_refreshDocNav` until symbol churn needs more.

### Phase 2 — full binding index (before symbol subtree rebuild)

- Add `_binding_items`.
- `_refreshDocNav` iterates index entries for `doc`, not whole tree.
- Symbol insert/remove/rebuild updates index incrementally.

### Phase 3 — MdiArea helpers

- Cache or expose subwindow map from `onSubWindowsChanged`.
- Dedupe Navigator and schematic MDI scans.

### Phase 4 — optional Session path map

- `cleanPath → Doc` for faster `openDocForPath` and duplicate-open checks.

---

## When a full index is not worth it yet

If the tree stays **L2 + mostly static children** and open doc count stays low, full-tree walks on `docChanged` are cheap. The index pays off when you add:

- Symbol row insert/remove/rebuild
- Select navigator row from MDI / active window
- Batch refresh for many rows per doc

See symbol subtree notes in [`NAVIGATOR.md`](NAVIGATOR.md) and close/remove checklist in [`REFACTOR.md`](REFACTOR.md).

---

## Interaction with `docChanged`

Refresh policy (Navigator listens to `session().docChanged`):

```text
doc.onChanged()
  → session.docChanged.emit(doc)
  → Navigator.onDocChanged(doc)
  → update rows for doc (index or walk)
  → doc.navLabel(subject) / doc.navToolTip(subject) on each bound row
```

**Inline rename:** do not call `doc.onChanged()` during delegate commit (use `setName(..., notify=False)` on scene); delegate `setModelData` already updates the row. See rename notes in [`NAVIGATOR.md`](NAVIGATOR.md). Index does not change this rule — it only makes row lookup cheaper.

---

## Summary

| Lookup | Owner | Mechanism |
|--------|-------|-----------|
| Item → `(doc, subject)` | Row | `DocBinding` on `UserRole` |
| Doc → L2 row | Navigator | `_doc_roots` (planned) |
| `(doc, subject)` → row | Navigator | `_binding_items` (planned) |
| Doc → subwindows | MdiArea | Cached map (planned) |
| `(doc, subject)` → subwindow | MdiArea | Cached map (planned) |
| path → doc | Session | Linear scan today; optional dict later |

**Bottom line:** keep **`DocBinding` on items** for forward lookup. Add a **Navigator-owned, incrementally maintained index** for reverse tree lookups. Push **MDI reverse lookup into `MdiArea`**. Keep three small caches with three clear owners — do not unify into one global map.
