# Modified / dirty state — Doc, Navigator, MDI

Design notes for **unsaved-change indication** in the navigator tree, tooltips, and (optionally) MDI titles.

**Related:** `[NAVIGATOR.md](NAVIGATOR.md)` (row labels, tooltips, refresh), `[REFACTOR.md](REFACTOR.md)` (close/save prompts), `[LOOKUPS.md](LOOKUPS.md)` (`docChanged` refresh).

---

## Goals


| Surface                      | Signal                                                                                                                              |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Navigator L2 (document root) | `*` suffix when the document has unsaved edits                                                                                      |
| Navigator symbol rows        | `*` when **that** symbol definition is dirty — see [Symbol definitions — three-phase model](#symbol-definitions--three-phase-model) |
| Tooltip                      | Path and/or save state; add `**(modified)`** when the row is dirty                                                                  |
| MDI title (optional)         | Same dirty rules as the bound subject — later                                                                                       |


Principles (same as tooltips):

- **Navigator stays document-agnostic** — it calls `Doc` hooks; it does not read undo stacks or append `*`.
- **Domain name ≠ display label** — inline rename must never persist decorative suffixes.
- `**docChanged` refresh** — programmatic `setText` / `setToolTip` on bound rows; no Navigator branch on `isModified()`.

---

## Ownership


| Concern                          | Owner                                                      |
| -------------------------------- | ---------------------------------------------------------- |
| “Is the document dirty?”         | `**Doc.isModified()`**                                     |
| “Is this bound row dirty?”       | `**Doc.isSubjectModified(subject)**`                       |
| Canonical row text (rename)      | `**Doc.navLabel(subject)**`                                |
| Tree display text                | `**Doc.navDisplayLabel(subject)**`                         |
| Tooltip text                     | `**Doc.navToolTip(subject)**`                              |
| Applying text to `QStandardItem` | **Navigator** (`_addDoc`, `_refreshDocNav`)                |
| When to refresh                  | `**Doc.onChanged()`** → `session().docChanged` → Navigator |


```text
edit / undo / redo / save / load
        →  dirty state changes
        →  doc.onChanged()
        →  session.docChanged.emit(doc)
        →  Navigator._refreshDocNav(doc)
        →  setText(doc.navDisplayLabel(subject))
        →  setToolTip(doc.navToolTip(subject))
```

**Do not** put `*` logic in `onDocChanged` or Navigator beyond calling the `nav*` hooks above.

---

## `Doc.isModified()`

Already on the `Doc` ABC (`ConnectEd/core/doc.py`). Document-level dirty — “needs save before close?”

Implementations derive this from their persistence model, not from navigator formatting.

### `HdlSchematicDiagramDoc`

**Decision:** diagram edits and symbol-definition edits that go through the **diagram scene `QUndoStack`** dirty the document. That matches current scene APIs (`newSymbol`, geometry edits, etc.) and is the desired behaviour.

```python
def isModified(self) -> bool:
    stack = self._scene.undo_stack
    return stack is not None and not stack.isClean()
```

**Wire-up (not yet done):**

- Connect `undo_stack.cleanChanged` → `doc.onChanged()` so `*` appears/clears on edit, undo, and redo.
- `**setClean()`** after successful **save** and **load**; fresh new doc starts clean until first edit.
- `**saveXml`** already calls `onChanged()` after save — add `setClean()` there (or in `Doc.save` override).

**Symbol editor subwindow (clone `SymbolScene`):** edits on the clone’s own undo stack do **not** automatically dirty the diagram stack until `**commitEditor`** pushes a command onto the diagram stack. Per-symbol row dirty uses the [three-phase model](#symbol-definitions--three-phase-model) below.

### `HdlSchematicLibraryDoc`

**Decision:** a session may edit **multiple symbol definitions** in one library file. Users should see **which** symbols changed, not only that the library file is dirty.


| Level         | Rule                                                                 |
| ------------- | -------------------------------------------------------------------- |
| Symbol row    | `isSubjectModified(symbol)` — that definition has unsaved edits      |
| Document root | `isModified()` — **any** symbol (or library-level metadata) is dirty |


Implementation sketch (when the doc exists beyond registration):

- Each symbol definition owns a dirty source (dedicated undo stack, or explicit dirty flag set on edit and cleared on per-symbol save / whole-doc save).
- `isModified()` = `any(isSubjectModified(s) for s in symbols)` ∨ library-level dirty.
- `cleanChanged` (or equivalent) on **each** stack → `doc.onChanged()` so one refresh updates all affected rows.
- Prefer the same **three-phase model** and **baseline** rules as diagram symbols (below); baselines are essential here because symbols are first-class and multiple editors may be open at once.

---

## Symbol definitions — three-phase model

Symbol definitions are serialised as `**SymbolItem`** objects (embedded in a diagram scene or owned by a library doc). To know if a **symbol row** is dirty, track dirty state in three phases tied to the **symbol editor** (`SymbolSubWindow` + clone `**SymbolScene`**), not the master `SymbolItem` alone.

Today, `_createSubWindow` builds a fresh `SymbolScene`, adds `subject.clone()`, and gives that scene its own `QUndoStack`. The master on the diagram is unchanged until `**commitEditor**` applies the clone.

### Phases


| Phase      | When                           | Clean?                                               | `isSubjectModified(symbol)` |
| ---------- | ------------------------------ | ---------------------------------------------------- | --------------------------- |
| **Before** | No editor open for this symbol | Default **clean**                                    | `False`                     |
| **During** | Editor open (clone scene live) | From `**editor_scene.undo_stack.isClean()`**         | `not stack.isClean()`       |
| **After**  | Editor closed                  | See [commit vs discard](#commit-vs-discard-on-close) | Depends on close path       |


**Before editing** means **no pending editor session** — not “unchanged since last save to disk”. File-level dirty stays on `**isModified()`** / the diagram (or library) undo stack.

**During editing:** on editor open, `setClean()` on the fresh clone stack so “opened but not yet edited” is clean. Connect `**cleanChanged`** on that stack → `**doc.onChanged()**` so the symbol row `*` toggles on undo/redo without closing the window.

Register open editor stacks with the doc while subwindows exist — e.g. map `SymbolItem` → clone `SymbolScene`, or resolve via `DocBinding` on `SymbolSubWindow`.

### Commit vs discard on close


| Close path                         | Master / diagram stack                                     | Symbol row after close                       | Doc root `*`                                   |
| ---------------------------------- | ---------------------------------------------------------- | -------------------------------------------- | ---------------------------------------------- |
| **Discard** (close without commit) | Unchanged                                                  | **Clean** — uncommitted clone thrown away    | Unchanged                                      |
| **Commit** (`commitEditor`)        | Clone applied to master; **undo command on diagram stack** | **Clean** in editor sense — no pending clone | **Dirty** until Save — diagram stack not clean |


Two layers after **commit**:

1. **Symbol row (editor sense):** clean once the editor is gone — nothing left pending in the clone.
2. **Document root (file sense):** dirty via diagram stack until the file is saved.

After **discard**, do not persist a “dirty at close” snapshot from the editor stack — the user rejected those edits.

### Baseline snapshot (optional layer)

**“Copy saved as the scene was closed”** — on **commit close**, store a **baseline** of the committed definition (serialised snapshot, hash, or equivalent) keyed by symbol. Use baselines when dirty must be visible **after** the editor closes.

```text
on commit close   →  baseline[symbol] = snapshot(committed definition)
on doc save       →  baseline[symbol] = snapshot for all symbols; stacks setClean()
on load           →  baseline[symbol] = loaded state
no editor open    →  dirty iff snapshot(current) != baseline[symbol]   (when baselines enabled)
```


| Doc type                          | Baselines                                                                                                                                 |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `**HdlSchematicDiagramDoc` (v1)** | **Optional.** Symbol row `*` only while an open editor stack is dirty; doc root `*` from diagram stack covers committed-but-unsaved work. |
| `**HdlSchematicLibraryDoc`**      | **Expected.** Symbols are long-lived; multiple editors; user must see which definitions differ from last save even with no editor open.   |


With baselines enabled:

```python
def isSubjectModified(self, subject):
    if subject has open editor:
        return not editor_stack.isClean()
    return snapshot(subject) != baseline[subject]
```

```python
def isModified(self):
    return not doc_stack.isClean() or any(isSubjectModified(s) for s in symbols)
```

### Diagram vs library summary


| Concern                        | Diagram doc                           | Library doc                                       |
| ------------------------------ | ------------------------------------- | ------------------------------------------------- |
| Doc-level dirty                | Diagram `QUndoStack`                  | Library stack and/or `any(isSubjectModified)`     |
| Symbol row while editing       | Clone stack                           | Clone stack (per symbol)                          |
| Symbol row, editor closed (v1) | Clean unless baselines added          | Baseline ≠ current                                |
| Commit path                    | `commitEditor` → diagram undo command | `commitEditor` → update symbol + baseline / stack |


---

## `Doc.isSubjectModified(subject)`

**Add** alongside `isModified()` — row-level dirty for navigator display.

```python
def isSubjectModified(
    self    : Self,
    subject : DocSubjectProtocol | None = None,
) -> bool:
    """True when this bound row has unsaved edits."""
```


| Doc type                 | Primary subject (L2)                   | Symbol subject                                                                                     |
| ------------------------ | -------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `HdlSchematicDiagramDoc` | same as `isModified()` (diagram stack) | **During:** clone editor stack dirty; **after close:** clean (v1) or baseline ≠ current (optional) |
| `HdlSchematicLibraryDoc` | `isModified()` (aggregate)             | three-phase model + baseline when editor closed                                                    |
| Default / stub           | `False`                                | `False`                                                                                            |


Navigator calls this only **indirectly** via `navDisplayLabel` / `navToolTip` on `Doc`.

---

## `navLabel` vs `navDisplayLabel`

**Problem:** embedding `*` in the only label string breaks inline rename — the editor would open on `"CPU Board*"` and `navSetLabel` could persist the star.

**Decision:** split canonical name from display decoration.


| Method                         | Role                                                                                               | Used by                                                                           |
| ------------------------------ | -------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `**navLabel(subject)`**        | Canonical row text — same as domain name for editable rows (`subject.name()` unless doc overrides) | `navSetLabel` validation; delegate `**setEditorData**` (text shown while editing) |
| `**navDisplayLabel(subject)**` | Presentation — `navLabel` plus dirty suffix (`*`, etc.)                                            | Navigator `**setText**` on build and refresh                                      |


Default on `Doc` (non-abstract):

```python
def navDisplayLabel(
    self    : Self,
    subject : DocSubjectProtocol | None = None,
) -> str:
    label = self.navLabel(subject)
    if self.isSubjectModified(subject):
        return label + "*"
    return label
```

Concrete docs override `isSubjectModified` (and optionally `navDisplayLabel` if suffix rules differ).

**Navigator changes:**

```python
# _addRows / _refreshDocNav — display, not canonical
item.setText(doc.navDisplayLabel(binding.subject))

# NavItemDelegate.setEditorData — canonical only
editor.setText(binding.doc.navLabel(binding.subject))
```

`**navSetLabel**` continues to compare and apply **canonical** text:

```python
if label == self.navLabel(subject):
    return False
# apply to domain; no asterisk stripping required
```

Update the `navLabel` docstring on `Doc` to say **canonical** row text; add `navDisplayLabel` with **tree display** docstring.

**Do not** rename `navLabel` to mean “display” — that would confuse every existing call site and `NAVIGATOR.md` section that already describes `navLabel` as the refresh hook (refresh should move to `navDisplayLabel`).

---

## Tooltips — show `(modified)`?

**Yes**, for bound rows whose tooltip reflects doc state. The `*` is for quick scanning; the tooltip carries explicit wording and works when the suffix is easy to miss.

### Rules


| Row state                 | Tooltip (primary / L2 schematic) |
| ------------------------- | -------------------------------- |
| Saved, clean              | full path                        |
| Unsaved path empty, clean | `(not saved)`                    |
| Saved, dirty              | `{path} (modified)`              |
| Unsaved, dirty            | `(not saved, modified)`          |


For **symbol rows** under `"Symbol Definitions"`:


| State | Tooltip                                                                             |
| ----- | ----------------------------------------------------------------------------------- |
| Clean | `None` or symbol-specific detail (future)                                           |
| Dirty | `(modified)` or `{path} — {symbol name} (modified)` when the library doc has a path |


**Implementation:** build the base string in `navToolTip` (path / `(not saved)` as today), then append  `(modified)` or `, modified` when `isSubjectModified(subject)`.

**Do not** rely on tooltip alone without `navDisplayLabel` — the star on the label remains the primary affordance.

Static container rows (`"Symbol Definitions"`, `<none loaded>`) — no `(modified)`; optional aggregate hint later (“3 modified”) is out of scope for v1.

---

## What not to do

- Navigator reads `doc.isModified()` or undo stacks directly.
- Store `*` in `subject.name()` or persist decorative suffixes via `navSetLabel`.
- Call `onChanged()` on every undo **push** — use `**QUndoStack.cleanChanged`** (fires only when clean/dirty **toggles**).
- Use `navLabel` for `setText` once `navDisplayLabel` exists — keeps rename and refresh consistent.
- Treat “unsaved” and “modified” as the same flag — unsaved means no path; modified means edits since last save (a saved file can be modified).
- Treat “clean before editing” as “no dirty editor session” — not “matches file on disk”.
- Persist editor-stack dirty state on **discard close** — discard means throw away the clone; symbol row returns to clean.

---

## MDI titles (optional, later)

`windowTitle(subject)` can follow the same split as the tree:

- canonical title stem (as today);
- append `*` when `isSubjectModified(subject)`.

Not required for the first navigator pass; document here so tree and MDI stay aligned when implemented.

---

## Implementation checklist

1. `**Doc.isSubjectModified`** + default `**navDisplayLabel**` on `Doc`.
2. `**HdlSchematicDiagramDoc.isModified**` — diagram `undo_stack.isClean()`; wire `**cleanChanged**` → `**onChanged()**`; `**setClean()**` on save/load/new.
3. **Navigator** — `navDisplayLabel` for `setText`; delegate `**setEditorData`** uses `**navLabel**`.
4. `**navToolTip**` — append `**(modified)**` / `**, modified**` when `isSubjectModified`.
5. **Symbol editors** — register clone stacks; `cleanChanged` → `onChanged()`; `commitEditor` / discard on close per [three-phase model](#symbol-definitions--three-phase-model).
6. `**HdlSchematicLibraryDoc`** — per-symbol three-phase dirty + baselines + aggregate `isModified` when the doc is implemented.
7. **Cross-ref** — update `[NAVIGATOR.md](NAVIGATOR.md)` row-label section to point here; fix stale “future asterisk in `navLabel`” wording.

---

## Related display summary


| Surface                 | Text                                  | Tooltip                            |
| ----------------------- | ------------------------------------- | ---------------------------------- |
| Navigator bound row     | `doc.navDisplayLabel(subject)`        | `doc.navToolTip(subject)`          |
| Navigator inline editor | `doc.navLabel(subject)`               | —                                  |
| Navigator container row | fixed `str` in `NavItemSpec`          | `NavItemSpec.tip` or default       |
| MDI subwindow (later)   | `windowTitle(subject)` + optional `*` | often path — optional `navToolTip` |


