# Navigator — WIP notes

Work-in-progress design notes for the new Navigator (`ConnectEd/widgets/window/navigator/`) and its boundary with **`Doc`**.

**Related:** [`REFACTOR.md`](REFACTOR.md) (active checklist), [`SESSION.md`](SESSION.md) (background), [`NEXT.md`](NEXT.md) (immediate todos).

---

## Current state (2025-06)

| Area | Status |
|------|--------|
| L1 group rows | Done — from `session().docTypes()` |
| L2 + children | Done — `_addDoc` / `navItemSpec()` / `DocBinding` on rows |
| Double-click / Enter | Done — `_openRow` → `openWindow` (rename → `winShow` planned) |
| File New/Open/Save/Close | Partial — `navigator/api.py`; close policy incomplete |
| `docChanged` listener | **Not wired** — labels/tooltips go stale |
| Context menus | **Not started** — row menus via `navContextMenu`; viewport (free-space) menu in [`navigator/menus.py`](../ConnectEd/widgets/window/navigator/menus.py) |
| Startup sync | **Not wired** — tree not rebuilt from `session().openDocs()` |
| Doc type registration | Done — side-effect imports in [`documents/__init__.py`](../ConnectEd/documents/__init__.py) |

Reference implementation: [`HdlSchematicDiagramDoc`](../ConnectEd/documents/schematic.py) (`SchematicDoc` in older notes).

---

## Architecture (target)

Three layers — **Session** (registry), **Doc** (domain + UI policy), **Navigator** (tree + file-dialog shell). **`win*`** on **`Doc`** is deliberately **not** Navigator-only; any UI or script may call it.

```text
Session                         Doc                              MDI / other UI
  new / load / save / close  →   path, toXml, onChanged           (no Qt)
                                 nav*  — tree labels, menus
                                 win*  — subwindow show/new/title
                                 commitEditor, isPrimarySubject

Navigator (TreeView)         listens docChanged; never scans mdi for reuse
  docLoad / fileNew     →      Session + _addDoc (tree row)
  dbl-click / Enter     →      doc.winShow(binding.subject)
  row context menu      →      doc.navContextMenu(subject)
  viewport context menu →      New ▶ (docTypes) + Open … ; no Doc
  fileClose             →      close policy + Session.close

Other entry points (same Doc surface, no Navigator required):
  File → New/Open/MRU   →      navigator().docLoad (orchestration today)
  Window menu           →      MdiArea.activateSubWindow (existing windows only)
  Diagram / library UI  →      doc.winShow(subject)  (planned)
  Scripting / tests     →      session().load + doc.winShow  (planned)
  AI tools              →      session + doc.win*  (planned)
```

**Principles**

- Navigator is **document-agnostic** at the tree boundary — only `Doc`, `DocBinding`, `NavItemSpec`.
- **Do not** query `mdi_area` from Navigator for open/reuse — call **`Doc.winShow`** / **`Doc.winNew`**.
- **Do not** register Navigator callbacks on **`Doc`** — Session broadcasts; Navigator listens.
- **`nav*`** = Navigator tree presentation; **`win*`** = MDI editors; **unprefixed** = persistence and shared lifecycle (`path`, `onChanged`, `commitEditor`, `isPrimarySubject`).
- Navigator is **not** the gatekeeper for documents — **`Session`** owns open docs; **`Doc`** owns editors. Navigator adds the tree and wires file dialogs.
- **Viewport context menu** (free space) is **Navigator-only** — New/Open from **`session().docTypes()`**; not **`Doc.navContextMenu`**.

---

## Entry points

Who calls what — today and target. Navigator is one **orchestrator**, not the only path to **`Doc`**.

| Entry point | Layer | Typical flow | `winShow` / `winNew`? |
|-------------|-------|--------------|------------------------|
| Navigator dbl-click / Enter | Navigator → Doc | `_openRow` → `winShow(subject)` | Yes |
| Navigator `_addDoc` after New/Open | Navigator → Doc | build tree → `_openRow(L2)` | Yes (today, on load) |
| File → New / Open / MRU | Menu → Navigator API | `fileNew` / `docLoad` → `_addDoc` | Yes (indirect) |
| Navigator row context menu | Navigator → Doc | `navContextMenu` → handlers / `winShow` / `winNew` | Yes (planned) |
| Navigator viewport menu (free space) | Navigator only | **New ▶** per `DocType.name`; **Open …** | No |
| Navigator L1 group menu | Navigator only | **New** for types in that `DocType.group` | No |
| Window menu | MdiArea | activate existing subwindow | No |
| Diagram / canvas (future) | View → Doc | e.g. “Edit symbol” → `winShow(symbol)` | Yes |
| AI tools (future) | Tool → Session + Doc | `load` / `openDocs` + `winShow` | Optional |
| Scripting / tests | Script → Session + Doc | see below | Optional |

### Scripting and headless work

[`ConnectEd.scripting`](../ConnectEd/scripting/__init__.py) exposes **`Window`**, **`MdiArea`**, docks — not a Session facade yet. Target split:

```python
# Domain only — no Qt editors required
doc = session().load(path)
session().save(doc)

# Open an editor — Doc.win*, no Navigator click required
doc.winShow(primary_subject)

# Full GUI path — tree row + auto-open (today via _addDoc)
navigator().docLoad(path)   # Session.load + _addDoc + _openRow
```

**Batch / headless** (export netlist, validate XML): **`Session` + `Doc` persistence** only — never **`win*`**.

When **startup sync from `session().openDocs()`** lands, rebuilding Navigator rows and calling **`winShow`** should be **separate steps** — e.g. listener adds L2 row on `docOpened`; caller decides whether to open an editor. Today **`_addDoc`** always calls **`_openRow(doc_item)`**, which is why File→Open feels Navigator-owned even though the editor is assembled on **`Doc`**.

### Method prefixes on `Doc`

| Prefix | Methods | Caller(s) | Role |
|--------|---------|-----------|------|
| **`nav*`** | `navItemSpec`, `navLabel`, `navSetLabel`, `navToolTip`, `navContextMenu` | Navigator (tree) | Row shape, labels, tooltips, menu **policy** |
| **`win*`** | `winShow`, `winNew`, `winTitle` | Navigator, menus, views, scripting, AI | MDI assembly / titles — **not** Navigator-exclusive |
| *(none)* | `path`, `save`, `onChanged`, `commitEditor`, `isPrimarySubject` | Session, File menu, close path | Persistence and shared lifecycle |

**Not `nav*`** on purpose: **`winShow`** creates MDI views; **`winTitle`** is consumed by **`MdiArea`** / Window menu, not the tree. **`commitEditor`** / **`isPrimarySubject`** are domain/close policy, not tree or window verbs.

Optional later rename: **`isPrimarySubject`** → **`winIsPrimary(subject)`** if it feels orphaned next to **`win*`**; keep **`commitEditor`** unprefixed.

---

## MDI window verbs (agreed)

Two distinct operations on a **`DocBinding`** subject:

| Method | Semantics | Typical callers |
|--------|-----------|-----------------|
| **`winShow(subject)`** | If a subwindow already exists for `(doc, subject)`, **activate** it; otherwise **create** one, then show it | Navigator dbl-click; `_addDoc` auto-open; context “Edit …”; diagram “edit symbol”; scripting |
| **`winNew(subject)`** | **Always** create another subwindow for the same subject (when the doc type allows multiple views) | Navigator context menu; Window menu (future) |

**Naming:** **`win*`** prefix on MDI hooks — pairs with **`nav*`** on Navigator hooks. **`winShow`** (not `openWindow`) covers bring-to-front and first-time open; **`winNew`** always adds another view.

```text
winShow(subject):
  scan mdi for DocSubWindow with DocBinding(doc, subject)
  if found → activateSubWindow; return True
  else     → create view + subwindow; return True/False

winNew(subject):
  always create view + subwindow (same subject, new binding instance)
  return True/False; doc type may reject (NotImplementedError / False)
```

**No `showDefault()`** — the L2 doc row carries the primary edit subject in **`DocBinding(doc, subject)`** (e.g. diagram scene), same as today’s `navItemSpec()`. Navigator always calls **`winShow(binding.subject)`** for bound rows; container rows (no binding) only expand/collapse. Do not use **`DocBinding(doc, None)`** on navigable rows.

Not every doc type must support **`winNew`** for every subject (library container may not). Default to **`False`** or **`NotImplementedError`** where inappropriate.

### Close — no **`winClose`**

**Not on `Doc`.** Open is subject-keyed (`winShow` / `winNew`); close is **two tiers** that span MDI, Session, and Navigator:

| Tier | What happens |
|------|----------------|
| **Close editor** | One **`DocSubWindow`** goes away; doc stays in Session and Navigator |
| **Close document** | All subwindows for the doc, **`session().close(doc)`**, remove L2 row |

Policy (from [`REFACTOR.md`](REFACTOR.md)): full document close when **`isPrimarySubject(subject)`** *or* this was the **last** subwindow for the doc; otherwise close the subwindow only (e.g. discard symbol clone).

**Navigator orchestrates** (e.g. **`fileClose(subwindow)`** → prompts → **`subwindow.close()`** or **`closeDocument(doc)`**). **`Doc`** supplies hooks only:

| Method | Role |
|--------|------|
| **`isPrimarySubject(subject)`** | Is closing this binding a document-level close? |
| **`commitEditor(subwindow)`** | Save / apply in-editor clone before close (symbol editor) |

**Why not `winClose`?**

- **`winClose(subject)`** is ambiguous after **`winNew`** (multiple windows per subject).
- **`winClose(subwindow)`** would duplicate Navigator + Session orchestration unless it also calls **`session().close`** and tree removal — wrong layer mix.
- Symmetry with **`winShow`** is weaker: show/create is doc assembly; close adds save/discard prompts and registry/tree teardown.

Revisit **`winClose(subwindow)`** only if close policy per doc type outgrows **`isPrimarySubject`** + **`commitEditor`** and Navigator **`fileClose`** becomes a mess. Until then, keep close out of the **`win*`** set.

---

## Doc ABC review — method name mess

The [`Doc`](../ConnectEd/core/doc.py) ABC accumulated overlapping names from the legacy `DesignDbNode` tree and the new Session model. **`HdlSchematicDiagramDoc`** implements only a subset; the rest are stubs or `NotImplementedError`.

### Inventory (today)

| Method | ABC | SchematicDoc | Navigator uses | Notes |
|--------|-----|--------------|----------------|-------|
| `navItemSpec()` | abstract | implemented | `_addDoc` | Tree shape under L2 |
| `navOpen(widget)` | abstract | stub | **nothing** | Overlaps `openWindow` |
| `navRename(widget, name)` | abstract | stub | `onItemChanged` | Overlaps proposed `navSetLabel` |
| `open(widget)` | abstract (+ legacy body in ABC) | stub | **nothing** | Broken paste in ABC; overlaps open family |
| `openDefault()` | abstract | stub / dead branch | `_openRow` if `subject is None` | **Remove** — L2 binding should carry primary subject |
| `openWindow(subject)` | abstract | **implemented** | `_openRow` | **Rename → `winShow`** |
| `newWindow(widget)` | abstract | stub | **nothing** | **Rename → `winNew`** |
| `openChild(child_id)` | default NIE | — | **nothing** | String-id era; use `winShow(subject)` |
| `windowTitle(subject)` | abstract | implemented | MDI `onSubWindowsChanged` | **Rename → `winTitle`** |
| `navigatorItem(child_id)` | concrete | — | **nothing** | References `item.id` — **not on `NavItemSpec`** |
| `renameNavigatorChild(id, label)` | concrete NIE | — | **nothing** | Remove with id-based API |

Also missing from ABC but in REFACTOR target: `navLabel()`, `navSetLabel()`, `navToolTip()`, `navContextMenu()`, `commitEditor()`, `isPrimarySubject()`.

### Problems

1. **Overlapping “open” names** — `navOpen`, `open`, `openWindow`, `openDefault` (+ `openChild`).
2. **Two rename names** — `navRename` vs `navSetLabel` / `renameNavigatorChild`.
3. **`nav*` prefix inconsistent** — legacy mix of `navOpen` / bare `open*`; target: **`nav*`** on Navigator tree hooks, **`win*`** on MDI hooks (see Entry points).
4. **Return types inconsistent** — `openWindow` → `bool`; ABC `openDefault` → `None`; stubs → `NotImplementedError`.
5. **`NavItemSpec.tip`** — snapshot at tree build; stale after Save As (see Tooltips below).
6. **`DocBinding`** — code uses `subject`; REFACTOR text sometimes says `widget`. Pick one (`subject` matches `DocSubjectProtocol`).

---

## Proposed streamlined `Doc` Navigator / MDI surface

Agreed MDI pair: **`winShow`** + **`winNew`**. Drop other open-family names. **`nav*`** on Navigator hooks; **`win*`** on MDI hooks (`winShow`, `winNew`, `winTitle`).

### Keep / add

| Method | Returns | Role |
|--------|---------|------|
| **`navItemSpec()`** | `NavItemSpec` | Tree under L2 (children only, or full subtree — pick one and document) |
| **`navLabel(subject)`** | `str` | Navigator row label — see Row labels below |
| **`navSetLabel(subject, label)`** | `bool` | Inline tree edit; calls `onChanged()` on success |
| **`navToolTip(subject)`** | `str \| None` | Row tooltip — see below |
| **`winShow(subject)`** | `bool` | Activate existing subwindow or create one if none |
| **`winNew(subject)`** | `bool` | Always open an additional subwindow (when supported) |
| **`winTitle(subject)`** | `str` | MDI window / Window menu title |
| **`navContextMenu(subject)`** | `list[NavMenuAction \| NavMenuSep]` | Menu **policy** only — Navigator builds `QMenu` |
| **`commitEditor(subwindow)`** | `bool` | Symbol editor Save — clone → master (future) |
| **`isPrimarySubject(subject)`** | `bool` | Close-doc policy — last primary editor (future) |

### Remove / fold

| Remove | Fold into |
|--------|-----------|
| `navOpen` | `winShow` |
| `openWindow` | `winShow` |
| `open(widget: QWidget)` | delete (legacy paste in ABC) |
| `openDefault()` | delete |
| `openChild(child_id)` | `winShow(subject)` via `DocBinding` |
| `newWindow` | `winNew` |
| `windowTitle` | `winTitle` |
| `navRename` | `navSetLabel` |
| `displayName` / `setDisplayName` | `navLabel` / `navSetLabel` |
| `navigatorItem` / `renameNavigatorChild` | Delete |
| `NavItemSpec.tip` (dynamic rows) | `navToolTip(subject)` |

### Summary — target `Doc` ABC

After cleanup, **`Doc`** exposes one surface per caller. Persistence unchanged; Navigator / MDI use the keep/add list only.

**Session** (persistence)

| Method | Returns | Role |
|--------|---------|------|
| `path()` | `str` | Filesystem path, or `""` if unsaved |
| `setPath(path)` | `None` | Update path after Save As |
| `toXml(xw)` | `None` | Serialize document |
| `fromXml(xr)` | `Doc` | Deserialize (classmethod) |
| `save(path?)` | `bool` | Write file (concrete; uses `toXml`) |
| `load(path)` | `bool` | Read file (classmethod; uses `fromXml`) |
| `onChanged()` | `None` | Notify Session (`docChanged`); call after mutating state |

**Navigator** (tree shape and row presentation)

| Method | Returns | Role |
|--------|---------|------|
| `navItemSpec()` | `NavItemSpec` | Child rows under L2 (containers, symbols, …) |
| `navLabel(subject)` | `str` | Row label (`subject` optional — primary when omitted) |
| `navSetLabel(subject, label)` | `bool` | Inline tree edit |
| `navToolTip(subject)` | `str \| None` | Row tooltip (dynamic; not `NavItemSpec.tip`) |
| `navContextMenu(subject)` | `list[…]` | Context-menu action ids; Navigator builds `QMenu` |

**MDI** (subwindows)

| Method | Returns | Role |
|--------|---------|------|
| `winShow(subject)` | `bool` | Activate existing `(doc, subject)` window or create one |
| `winNew(subject)` | `bool` | Always open another window for the same subject |
| `winTitle(subject)` | `str` | Subwindow / Window-menu title |

**Future** (close / editor commit)

| Method | Returns | Role |
|--------|---------|------|
| `commitEditor(subwindow)` | `bool` | Persist in-editor clone (e.g. symbol Save) |
| `isPrimarySubject(subject)` | `bool` | Whether closing this editor should close the doc |

**Removed** — `navOpen`, `open`, `openWindow`, `openDefault`, `openChild`, `navRename`, `navigatorItem`, `renameNavigatorChild`.

**Related types** — `DocBinding(doc, subject)` on navigable rows; static container labels stay as `str` in `NavItemSpec`; static container tips on `NavItemSpec.tip` or Navigator defaults.

### Row labels — `navLabel` not `displayName()`

**No separate `displayName()` / `setDisplayName()`.** Use **`navLabel`** / **`navSetLabel`** — consistent with other Navigator hooks and distinct from **`DocSubjectProtocol.name()`**. REFACTOR assumed the L2 row was built outside `navItemSpec()` from a doc-only label. Current code already binds the **primary subject** on L2 (`NavItemSpec(subject=self._scene)`), so one API covers every bound row:

```python
def navLabel(self, subject: DocSubjectProtocol | None = None) -> str:
    """Navigator row text. subject=None → primary subject (L2 default label)."""

def navSetLabel(self, subject: DocSubjectProtocol | None, label: str) -> bool:
    """Apply inline edit; validate, update domain, onChanged()."""
```

**Navigator** (document-agnostic):

```text
_addRows      →  setText(doc.navLabel(spec.subject))   # not spec.subject.name()
onItemChanged →  doc.navSetLabel(binding.subject, item.text())
_onDocChanged →  setText(doc.navLabel(binding.subject)) on each bound row for doc
```

**Doc** decides label policy:

| Case | Typical `navLabel(subject)` |
|------|-----------------------------|
| Child subject | `subject.name()` (default) |
| Primary subject (L2 binding) | same underlying name, plus doc formatting if needed (e.g. dirty `*`, unsaved placeholder) |
| `subject is None` | same as primary — for refresh when only `doc` is known |

Schematic: L2 and diagram scene share one subject; `navLabel(scene)` may return `scene.name()` today and `scene.name() + "*"` when dirty later — without a second method or Navigator branch.

**Do not** call `subject.name()` directly in Navigator for bound rows — that bypasses doc formatting and couples Navigator to `DocSubjectProtocol` instead of `Doc`.

### Navigator call sites (after streamlining)

```text
_openRow(binding)     →  winShow(binding.subject)   # subject always set on bound rows
onItemChanged         →  navSetLabel(binding.subject, item.text())
_onDocChanged(doc)    →  refresh navLabel + navToolTip per bound row; rebuild symbol subtree if needed
row context menu      →  navContextMenu(subject) → Navigator builds QMenu
viewport context menu →  _viewportMenu(): New ▶ all docTypes + Open …
L1 group context menu →  _groupNewMenu(group): New for types in group
```

### Migration note

Until the ABC is cleaned up, **`openWindow`** in `HdlSchematicDiagramDoc` is the de-facto **`winShow`** implementation. Rename is mechanical: ABC + schematic + `_openRow` + `mdi_area`.

---

## Tooltips

### Problem

Tooltips are set once when the tree is built:

```python
if spec.tip is not None:
    item.setToolTip(spec.tip)
```

`navItemSpec()` currently sets `tip=self._path or "(not saved)"` on the doc row. That value is **frozen at load** — Save As, first save, and path changes do not update the row.

### Recommendation

| Concern | Owner |
|---------|--------|
| Tooltip **text** | **`Doc.navToolTip(subject)`** |
| **`setToolTip` on `QStandardItem`** | **Navigator** (on build + refresh) |
| Static container rows (`"Symbols"`, `<none loaded>`) | **`NavItemSpec.tip`**, fixed string, or Navigator default |

**Do not** pass tooltips only via `NavItemSpec` for rows whose text depends on doc state (path, dirty flag, etc.).

### `navToolTip(subject)` sketch (schematic)

```python
def navToolTip(self, subject: DocSubjectProtocol | None) -> str | None:
    if subject is None or subject is self._scene:
        return self._path or "(not saved)"
    if subject in self._scene.symbols():
        return self._path or "(not saved)"   # or symbol-specific detail later
    return None
```

### When to apply

1. **Initial build** — in `_addRows`, for rows with `DocBinding`:

   ```python
   tip = doc.navToolTip(subject_from_binding_or_spec)
   if tip is None and spec.tip is not None:
       tip = spec.tip
   if tip is not None:
       item.setToolTip(tip)
   ```

2. **Updates** — Navigator subscribes to **`session().docChanged`**:

   ```text
   doc.onChanged()  →  session.docChanged.emit(doc)
                     →  Navigator._onDocChanged(doc)
                     →  walk items where binding.doc is doc
                     →  setToolTip(doc.navToolTip(binding.subject))
                     →  setText(doc.navLabel(binding.subject))
   ```

3. **Suppress edit echo** — use a `_refreshing` flag while applying programmatic `setText` / `setToolTip` so `onItemChanged` does not call `navSetLabel`.

### What not to do

- Doc holding `QStandardItem` references or calling `setToolTip` on Navigator rows.
- Navigator reading `doc.path()` directly (breaks document-agnostic rule; library doc may differ).
- Relying on `NavItemSpec.tip` alone for the L2 doc row.

### Related display rules (from REFACTOR)

| Surface | Text | Tooltip |
|---------|------|---------|
| Navigator bound row | `doc.navLabel(subject)` | `doc.navToolTip(subject)` |
| Navigator container row | fixed `str` in spec | `NavItemSpec.tip` or default |
| MDI subwindow | `winTitle(subject)` | often path — optional `navToolTip` |

**Future:** modified asterisk on L2 label (`CPU Board*`) — in `navLabel(primary_subject)` when dirty; full path stays in tooltip ([`NEXT.md`](NEXT.md)).

---

## Context menus

Two menus — **row** (Doc policy) and **viewport / free space** (Navigator only).

### Row context menu (bound item)

Doc drives **menu policy**, not `QMenu` instances — same layering as tooltips.

- Hit-test row → read **`DocBinding`** from `UserRole`.
- **`Doc.navContextMenu(subject)`** → `list[NavMenuItem | NavMenuSep]` (or action ids — see type notes in [`doc.py`](../ConnectEd/core/doc.py)).
- **Navigator** builds `QMenu`, connects handlers (label + callable on item, or dispatch table).
- **No binding** (L1 group label, `"Symbols"` container, dummy row) → not **`navContextMenu`**; L1 group gets **New** filtered by **`DocType.group`** (see viewport section); containers/dummy TBD.

Port row specs from [`navigator_old/menus.py`](../ConnectEd/widgets/window/navigator_old/menus.py) into **`Doc.navContextMenu`** + [`navigator/menus.py`](../ConnectEd/widgets/window/navigator/menus.py) wiring.

### Viewport context menu (free space — not on any row)

**Required.** Right-click on empty tree area (invalid index / viewport background) must still show a menu — same role as legacy **`menus[None]`** in [`navigator_old/overrides.py`](../ConnectEd/widgets/window/navigator_old/overrides.py) (`showContextMenu`: invalid index → `menus[None]`).

| | Row menu | Viewport menu |
|--|----------|---------------|
| **Trigger** | `indexAt(pos).isValid()` and row has policy | `not indexAt(pos).isValid()` |
| **Owner** | **`Doc.navContextMenu(subject)`** | **Navigator** (`menus.py` / mixin) |
| **Needs** | `Doc`, `DocBinding`, subject | **`session().docTypes()`**, file API only |
| **Typical actions** | Edit, New Window, Save, Close (per doc/subject) | **New ▶** submenu, **Open …** (see below) |

**Not** `Doc.navContextMenu` — there is no row, doc, or subject.

#### **New** submenu (viewport)

Top-level **New** is a **`QMenu` submenu**, not a flat list of “New Design / New Library” strings.

- **Source:** `session().docTypes()` — every registered **`DocType`** (`Session.registerDocType`).
- **One menu action per doc type**, label = **`DocType.name`** (friendly type name, e.g. `"HDL Schematic Diagram"`).
- **Handler:** create without type picker when unambiguous — e.g. `session().new(doc_type.tag)` then `_addDoc` under **`_groups[doc_type.group]`** (add **`fileNewForTag(tag)`** or equivalent on [`navigator/api.py`](../ConnectEd/widgets/window/navigator/api.py); today **`fileNew()`** opens **`FileNewDialog`** — viewport **New** should skip the dialog when the user picked a specific type).

Example structure (two registered types):

```text
New  ▶
       HDL Schematic Diagram
       VHDL Symbol Library
---
Open …
```

If several types share the same **`DocType.group`**, the viewport **New** submenu still lists **each type by `name`**; **`_addDoc`** parent remains the matching L1 **`_groups[group]`** row.

#### L1 group row — **New** for that group

Right-click on an **L1 group row** (bold group label from **`DocType.group`**, no **`DocBinding`**) gets a **group-scoped New** entry — not the full viewport menu.

- **Filter:** doc types where **`doc_type.group ==`** that row’s group name.
- **One type in group:** single action, e.g. **New HDL Schematic Diagram** → `session().new(tag)` + `_addDoc`.
- **Several types in group:** **New** submenu (same labels **`DocType.name`**, same handlers), only types in that group.

Legacy had separate **`DesignDbContainer`** vs **`LibraryDbContainer`** menus with duplicate New/Open lines; target is **one mechanism**: filter **`docTypes()`** by group (L1 row) or show all types (viewport).

#### **Open** (viewport)

**Open …** stays a top-level viewport action (file dialog → **`fileOpen`** / **`docLoad`**), unless grouped under an **Open** submenu later. Not doc-type-specific on first implementation.

Sketch:

```text
contextMenuEvent / customContextMenuRequested(pos):
  index = indexAt(pos)
  if not index.isValid():
      buildViewportMenu().exec(...)     # New ▶ (all docTypes) + Open …
      return
  item = model.itemFromIndex(index)
  binding = item.data(UserRole)
  if binding is not None:
      entries = binding.doc.navContextMenu(binding.subject)
      buildQMenu(entries).exec(...)
  elif item in _groups.values():          # L1 group row
      buildGroupNewMenu(item.text()).exec(...)
  else:
      # container / dummy — TBD
      ...
```

Legacy free-space spec (reference only — replace with **New ▶** + **`docTypes()`**):

```text
New Design / Open Design
---
New Library / Open Library
```

### Implementation notes

- [`navigator/menus.py`](../ConnectEd/widgets/window/navigator/menus.py) — **`NavigatorMenusMixin`**: `showContextMenu(pos)`, `_viewportMenu()` (**New ▶** from **`docTypes()`** + **Open …**), `_groupNewMenu(group)`, `_rowMenu(binding)`, Qt `QMenu` assembly.
- [`navigator/events.py`](../ConnectEd/widgets/window/navigator/events.py) — enable `Qt.ContextMenuPolicy.CustomContextMenu` and connect signal if not already wired.
- Contract types (`NavMenuItem`, `NavMenuSep`, …) stay in **`core/doc.py`** (Doc API); viewport menu uses Navigator-local actions only.

---

## Open WIP checklist

- [ ] Streamline `Doc` ABC per table above; fix legacy `open()` body in [`doc.py`](../ConnectEd/core/doc.py)
- [ ] Rename `openWindow` → **`winShow`**, `newWindow` → **`winNew`**, `windowTitle` → **`winTitle`**; remove **`openDefault`**
- [ ] Add `navLabel`, `navToolTip`, `navSetLabel`; wire `docChanged`
- [ ] Remove `navigatorItem` / id-based rename API
- [ ] Align `DocBinding` field name in docs (`subject`)
- [ ] Implement `navigator/menus.py`: viewport **New ▶** (`docTypes()`), L1 **group New**, row menu from `navContextMenu`; **`fileNewForTag(tag)`** (no dialog)
- [ ] Decouple **`_addDoc`** auto-open from tree build (optional `winShow` — caller decides)
- [ ] Scripting: document **`session()` + `doc.winShow`** path (see Entry points)
- [ ] Sync tree from `session().openDocs()` on startup; handle `docClosed`
- [ ] Inline edit suppress flag on refresh
- [ ] File modified asterisk on L2 label

---

## Key files

| File | Role |
|------|------|
| [`core/doc.py`](../ConnectEd/core/doc.py) | `Doc`, `NavItemSpec`, `DocBinding` |
| [`documents/schematic.py`](../ConnectEd/documents/schematic.py) | Reference doc type |
| [`navigator/__init__.py`](../ConnectEd/widgets/window/navigator/__init__.py) | Widget + `onItemChanged` |
| [`navigator/private.py`](../ConnectEd/widgets/window/navigator/private.py) | `_addDoc`, `_openRow` |
| [`navigator/events.py`](../ConnectEd/widgets/window/navigator/events.py) | Double-click / Enter |
| [`navigator/api.py`](../ConnectEd/widgets/window/navigator/api.py) | File operations |
| [`navigator/types.py`](../ConnectEd/widgets/window/navigator/types.py) | `NavItem`, `NavDummyItem` |
| [`navigator/menus.py`](../ConnectEd/widgets/window/navigator/menus.py) | Context menus (stub) |
| [`core/session.py`](../ConnectEd/core/session.py) | `docChanged`, registry, `openDocs` |
| [`scripting/`](../ConnectEd/scripting/) | GUI tests; target: `session()` + `doc.winShow` |
| [`widgets/window/mdi_area.py`](../ConnectEd/widgets/window/mdi_area.py) | Titles from `winTitle` |
