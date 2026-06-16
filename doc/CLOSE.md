# Document and editor closure

Plan for **File → Close**, subwindow **X**, and Navigator-driven document removal under the Session + **`Doc`** + **`DocSubWindow`** architecture.

**Related:** [`SESSION.md`](SESSION.md), [`SYMBOLS.md`](SYMBOLS.md).

---

## Two kinds of “close”

| Kind | What happens | Session | Navigator L2 row | MDI |
|------|----------------|---------|------------------|-----|
| **Close editor** | End one edit session (e.g. symbol clone discarded) | Doc stays open | Stays | One subwindow closes |
| **Close document** | Remove doc from the session | `session().close(doc)` | Row removed | **All** subwindows for that doc close |

Do not conflate them. Today [`NavigatorApiMixin.fileClose`](../ConnectEd/widgets/window/navigator/api.py) always calls `docClose` + `subwindow.close()` — that removes the doc from Session even when closing a symbol editor only.

---

## Agreed close policy

**Full document close** when **either**:

1. **Primary / L2 editor** — the subwindow’s **`DocBinding.widget`** is the doc’s primary subject (for **`SchematicDoc`**: the **`DiagramScene`**, i.e. the L2 diagram row), **or**
2. **Last subwindow** — no other **`DocSubWindow`** with the same **`DocBinding.doc`** would remain after closing this one.

**Otherwise:** close **this subwindow only** (symbol editor → discard transient clone; schematic stays in Session and Navigator).

```text
Close symbol editor, diagram still open     → editor only
Close diagram editor (L2)                   → close document (+ all symbol editors)
Close symbol editor, only window left       → close document
```

```python
def fileClose(self, subwindow: DocSubWindow) -> None:
    binding = subwindow.docBinding()
    if binding is None:
        subwindow.close()
        return
    if binding.doc.isPrimarySubject(binding.widget) \
    or not self._otherSubwindows(binding.doc, subwindow):
        self.closeDocument(binding.doc)
    else:
        subwindow.close()
```

Add **`Doc.isPrimarySubject(widget)`** on each concrete doc ( **`SchematicDoc`**: `widget is self._scene` ).

---

## Symbol editor vs save

Symbol definitions are edited as a **clone** in a transient **`SymbolScene`**; the cache master is unchanged until **Save** commits clone → master (see [`SYMBOLS.md`](SYMBOLS.md)).

- **Save** (menu): `doc.commitEditor(subwindow)` then `session().save(doc)`.
- **Close editor** (non-document path): discard clone — no commit.
- **Close document**: optional save/discard prompt for the schematic; symbol clones in other windows are closed without commit unless saved first.

No doc-level registry of transient scenes — **`DocSubWindow.docBinding()`** + view → scene → clone is enough.

---

## Eight steps to sort out closure

Ordered for delivery. Check boxes track progress.

### 1. Fix `DocBinding` on subwindow creation

Every **`DocSubWindow`** must store **`DocBinding(doc, subject)`**, not a bare **`Doc`**.

- **`DocBinding.doc`** — owning document.
- **`DocBinding.widget`** — edit subject: **`DiagramScene`** (primary) or cache **`SymbolItem`** (symbol editor).
- Update [`SchematicDoc.openWindow`](../ConnectEd/documents/schematic.py) and [`DrawingSubWindow`](../ConnectEd/widgets/graphics/views/drawing/__init__.py) accordingly.

Until this is fixed, **`_docFromSubwindow`** and all file menu paths are unreliable.

- [ ] `DocBinding(self, widget)` at MDI creation
- [ ] `DrawingSubWindow(parent, doc_binding=...)`
- [ ] `Doc.isPrimarySubject(widget)` on ABC + `SchematicDoc`

### 2. Implement the close policy (editor vs document)

Replace unconditional `docClose` in **`fileClose`** with the **primary OR last window** rule above.

- [ ] `_otherSubwindows(doc, except_sw) -> bool`
- [ ] `fileClose` branches: `closeDocument(doc)` vs `subwindow.close()`
- [ ] Navigator context-menu Close uses the same helper where appropriate

### 3. Add `closeDocument(doc)` — tear down MDI first

Single entry point for full document close:

```text
closeDocument(doc)
  → close every DocSubWindow where docBinding.doc is doc
  → session().close(doc)
  → remove L2 row from Navigator model
```

**Order matters:** do not call **`session().close`** while other editors for that doc are still open.

- [ ] `_closeSubwindowsForDoc(doc)` (scan `mdiArea().subWindowList()`)
- [ ] `NavigatorApiMixin.closeDocument(doc)` orchestrates MDI + Session + tree
- [ ] Remove redundant `docClose` + `subwindow.close()` double-call on menu path

### 4. Remove doc from Navigator tree

**`session().close(doc)`** alone does not update the tree.

- [ ] `_removeDocFromTree(doc)` — find L2 row by **`DocBinding`** / stored doc ref, remove from **`NavModel`**
- [ ] Or: **`Session.docClosed = pyqtSignal(Doc)`** emitted from **`Session.close`**, Navigator subscribes and removes row

### 5. Save / discard prompts

Port the old **`navigator_old`** “offer to save if modified” behaviour.

| Case | Prompt |
|------|--------|
| Close **document** | Unsaved schematic / no path → Save, Discard, Cancel |
| Close **symbol editor** (editor-only path) | Dirty clone → Save (commit + optional file save), Discard, Cancel |
| Close **document** when last window is symbol editor | Same as document close; user may not expect doc removal — prompt helps |

- [ ] Dirty detection on symbol editor (undo stack or explicit flag)
- [ ] Dirty detection on schematic doc
- [ ] Shared confirm dialog helper; Cancel vetoes close

### 6. One code path for menu Close and window X

Route **File → Close** ([`menu_bar/slots.py`](../ConnectEd/widgets/window/menu_bar/slots.py) via **`@withCurrentSubWindow`**) and **`DocSubWindow.closeEvent`** through the same Navigator API (e.g. **`fileClose(subwindow)`**), so policy is identical.

- [ ] `closeEvent` calls Navigator (or doc) before accepting; Cancel sets `event.ignore()`
- [ ] Avoid `session().close` in `closeEvent` without going through `closeDocument`

### 7. Menu / actions polish

- [ ] **`fileClose`** enabled when `mdiArea().activeSubWindow()` is non-None (and ideally when it is a **`DocSubWindow`**)
- [ ] Update action tooltip from “Close database” to something accurate (e.g. “Close window” / “Close document” depending on policy)
- [ ] Non-**`DocSubWindow`** active subwindow: `subwindow.close()` only ([`Slots.fileClose`](../ConnectEd/widgets/window/menu_bar/slots.py) empty `pass` branch)
- [ ] Fix **`withCurrentWidget`** to use **`activeSubWindow()`** (not nonexistent **`currentSubWindow()`**)

### 8. Session signal (optional but clean)

- [ ] **`Session.docClosed = pyqtSignal(Doc)`** — emit from **`Session.close`**
- [ ] Navigator (and future listeners) react without duplicating Session internals
- [ ] Keep **`docChanged`** for rename/structural refresh separate from **`docClosed`**

---

## Target API summary

| Entry | Handler |
|-------|---------|
| File → Close | `Slots.fileClose` → `Navigator.fileClose(subwindow)` |
| Subwindow X | `DocSubWindow.closeEvent` → same `Navigator.fileClose` |
| Navigator Close doc | `Navigator.closeDocument(doc)` |
| File → Save (symbol) | `Navigator.fileSave` → `doc.commitEditor(subwindow)` → `session().save(doc)` |

```text
Slots.fileClose(subwindow)
    → Navigator.fileClose(subwindow)
         → if primary OR last window: closeDocument(doc)
         → else: subwindow.close()

closeDocument(doc)
    → _closeSubwindowsForDoc(doc)
    → session().close(doc)          # emits docClosed
    → _removeDocFromTree(doc)
```

---

## Subsequent refinements

| Refinement | Notes |
|------------|--------|
| **Commit on Save only** | Symbol master updated in **`doc.commitEditor(subwindow)`** before XML serialisation — not on editor close. |
| **No doc registry for symbol edits** | Transient **`SymbolScene`** + clone live under subwindow; reuse/focus by **`DocBinding.widget is master`**. |
| **Spreadsheet / other editors** | Any **`DocSubWindow`** with same **`doc`** counts in **`_otherSubwindows`**. |
| **Library doc** | Same binding and close policy; primary subject TBD on **`LibraryDoc`**. |
| **Close last symbol editor closes doc** | By design; mitigate with save/discard prompt (step 5). |
| **MDI `update()`** | Call after bulk subwindow close so window menu titles refresh. |

---

## Current gaps (state of play)

| Area | Status |
|------|--------|
| [`NavigatorApiMixin.fileClose`](../ConnectEd/widgets/window/navigator/api.py) | Always **`docClose` + subwindow.close()`** — wrong for symbol editors |
| [`docClose`](../ConnectEd/widgets/window/navigator/api.py) | Session only — no MDI sweep, no Navigator tree |
| [`SchematicDoc.openWindow`](../ConnectEd/documents/schematic.py) | Must pass **`DocBinding`**, not bare **`SchematicDoc`** |
| Navigator tree removal | Not implemented |
| Save/discard prompts | Not implemented |
| **`Session.docClosed`** | Not implemented |
| Symbol **commit on Save** | Not implemented |

---

## Legacy reference

Old path: **`navigator.close(scene)`** → db node → **`model().close(node)`** (whole database). File → Close passed **`view.scene()`**, which failed or behaved oddly for **`SymbolScene`**. New path: subwindow + **`DocBinding`**, explicit editor vs document close.
