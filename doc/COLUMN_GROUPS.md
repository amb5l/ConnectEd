---
name: Table column groups
overview: Two-band horizontal headers on TableView — group labels from TableModel, painted and clickable in TableHeaderView. Empty groups keep today’s single header.
todos:
  - id: model-api
    content: Finish TableModel group API — store per-column group names; derive TableColumnGroup spans; clear groups on setHorizontalHeaderLabels
    status: pending
  - id: header-paint
    content: TableHeaderView — extra height, paint group band + leaf labels, hit-test group vs leaf
    status: pending
  - id: header-click
    content: Click group band selects that span’s columns without changing default cell selection mode
    status: pending
  - id: view-wire
    content: TableView installs TableHeaderView; reads groups from TableModel; no-op when groups is None/empty
    status: pending
  - id: properties-dialog
    content: PropertiesDialog uses TableModel + group labels (Property / Text)
    status: pending
isProject: false
---

# Table column groups

Optional second header band: **group** titles over contiguous leaf columns. Model owns names; header paints and handles clicks. No extra model rows or columns.

## Current code

[`table.py`](../ConnectEd/widgets/dialogs/components/table.py):

| Piece | State |
|--------|--------|
| `TableColumnGroup` | `NamedTuple(name, column_count)` — unused |
| `TableModel` | `_hgroups: list[str] \| None`; `setHorizontalHeaderGroupLabels` takes `(group, leaf)` **per column**; `setHorizontalHeaderLabels` clears groups |
| `TableHeaderView` | stub |
| `TableView` | still a plain `QTableView` + font-size wheel; takes `QStandardItemModel` |

[`PropertiesDialog`](../ConnectEd/widgets/dialogs/properties/__init__.py) still builds a `QStandardItemModel` and `setHorizontalHeaderLabels(_COLS)` — one flat header.

## Design

```text
TableModel          metadata: leaf labels + optional per-column group names
       │
TableView           installs TableHeaderView; does not store groups
       │
TableHeaderView     paints two bands when groups present; click group → select span
```

- **No groups** (`_hgroups is None` or all blank): one header row, current look.
- **Groups**: taller header. Top band = group name over a run of equal names; bottom = leaf (`Name`, `Type`, …).
- Data `rowCount()` / `column()` unchanged.

### Model API

Keep the per-column setter (easy for callers). Derive spans for the view.

```text
setHorizontalHeaderLabels(labels)
  → leaf headers; _hgroups = None

setHorizontalHeaderGroupLabels([(group, leaf), ...])
  → one pair per column; length must match columnCount()
  → consecutive equal group names form a TableColumnGroup

horizontalHeaderGroupLabels() -> list[str] | None
horizontalHeaderGroups()      -> list[TableColumnGroup] | None
```

Rules:

- `None` / omitted groups → no group band.
- Empty string group name → ungrouped leaf (blank span, no click target).
- Adjacent same name → one span (`("Property", 3)` not three “Property” cells conceptually).
- Do not put group titles in `headerData(DisplayRole)` for leaf columns.

Validate in debug/log if `len(pairs) != columnCount()`.

### Header (`TableHeaderView`)

`QHeaderView` has one section per **leaf** column. Extra height = group band + leaf band.

| Concern | Approach |
|---------|----------|
| Height | `sizeHint` / `sectionSizeFromContents` include group-band height when model has groups |
| Paint | `paintSection`: leaf text in lower half; group text once per span (clip to span’s x-range, or paint only on the first section of the run) |
| Resize | Group underline / vertical ticks at span boundaries |
| Click | `mousePressEvent`: y in group band → select columns `[start, start+count)`; y in leaf band → default section behaviour |
| Selection | Select those **columns’ cells** via the view’s `selectionModel`. Do **not** switch the view to `SelectColumns` permanently — properties dialog stays row-oriented for editing |
| Sections movable | Leave **off** while spans are name-run based |

Theme: reuse table/header palette; optional later `theme/properties/header/group`.

### View (`TableView`)

- Require `TableModel` (same module).
- `setHorizontalHeader(TableHeaderView(Qt.Horizontal, self))`.
- Header reads groups from `model()` on paint / model-reset (`headerDataChanged`, `modelReset`).

### First consumer — PropertiesDialog

Switch `_table_model` to `TableModel`. After columns exist:

```text
Property × 3   Name, Type, Value
Text     × n   Display + _PT_COLS
```

via `setHorizontalHeaderGroupLabels` (repeat `"Property"` / `"Text"` per column).

Click **Property** → select Name/Type/Value; click **Text** → select display + PT columns. Does not change Delete/New row logic.

## Out of scope

- Nested groups (only one group band).
- Vertical (row) groups.
- Spreadsheet / library `QTableView` (not `TableView`).
- Putting group names in data rows.

## Implementation order

1. **Model** — `horizontalHeaderGroups()` from `_hgroups` runs; keep `TableColumnGroup`.
2. **Header paint** — two bands, no click yet; PropertiesDialog wired so you can see it.
3. **Header click** — group band selects span; leaf band unchanged.
4. **Polish** — height vs font-size wheel, min dialog size includes extra header, adjacent-span separators.

## Tests (later)

- No groups → header height ≈ current.
- Groups → span list matches runs; click selects expected columns.
- `setHorizontalHeaderLabels` after groups → group band gone.
