# Presentation defaults

Theme lookup (`pen` / `brush` / `quill`) is keyed by **name + default key**,
not by a live item. Instance `defaultTextColor(view)` (and line/fill cousins)
exist only as a handle onto `scene.resources`. State snapshots store
**overrides** (`None` = inherit). Defaults stay on the scene.

`AppearanceDialog` (multi-item) goes away; PropertiesDialog covers that.
Do not keep six instance default getters just to feed it.

---

## `settingsName` / `resourcesName`

**Yes — start here.** Class-level defaults need a name without an instance.

Lift constant names to `@classmethod`. `self.settingsName()` still works.


| Kind                                                                                                          | Action                      |
| ------------------------------------------------------------------------------------------------------------- | --------------------------- |
| Mixin default (`Item` suffix strip)                                                                           | `@classmethod`              |
| Constant overrides (`"Text"`, `"Gate"`, `"GatePin"`, `"BlockPin"`, `"Symbol"`, `"rubber"`, pin/arrow aliases) | `@classmethod`              |
| `PropertyTextItem.settingsName`                                                                               | **Keep as instance method** |


`PropertyTextItem` is the only name that depends on instance state: parent
`settingsName` + property name, if that key exists under `theme/items`, else
`"PropertyText"`. `resourcesName` follows it (`BlockName` vs `PropertyText`).
A classmethod cannot express that.

Class-level lookup for `PropertyTextItem` uses `"PropertyText"`, or an
explicit `name=` when the caller already knows the theme key (parent type +
property). Do not construct a dummy item just to resolve `BlockName`.

`resourcesName` lifts in the same step (it is what defaults actually key on).
Where it currently delegates to `settingsName`, the classmethod does the same.

---



## Steps

Work in order.

### 1. Class names

- [x] `ItemNamesMixin.settingsName` / `resourcesName` → `@classmethod`
- [x] Convert every constant override to `@classmethod`
- [x] Leave `PropertyTextItem.settingsName` as an instance method
- [ ] Existing tests: `BlockName` / `PropertyText` fallback still pass



### 2. Class-level theme lookup

- [ ] `_resourceKeyDefault` → `@classmethod` where the key is class-constant
  ```
  (`False` for text; neutral keys for node/segment stay as they are)
  ```
- [ ] Add `defaultQuill(cls, scene, name=None) -> Quill` (optional `name`
  ```
  is for `PropertyTextItem` / `BlockName`)
  ```
- [ ] Same for `defaultPen` / `defaultBrush`
- [ ] Pass `DiagramScene`, not `view`. View-to-scene is the caller’s job
- [ ] Delete `_defaultScene(view)` once nothing needs the “item not in
  ```
  scene” fallback
  ```



### 3. Drop per-field instance defaults

- [ ] Remove `defaultTextColor` / `Font` / `Size` / `Bold` / `Italic` /
  ```
  `Underline` and the line/fill equivalents
  ```
- [ ] PropertySpec `default=` reads `type(self).defaultQuill(scene)` (etc.)
- [ ] One `Quill` (or pen/brush) is the defaults bundle — do not put
  ```
  `default_*` fields on appearance state
  ```



### 4. Dialogs and place

- [ ] `TextAppearanceLayout` takes `(state, defaults: Quill, …)` — not an
  ```
  item and not `item.defaultTextColor(view)`
  ```
- [ ] Existing item: `fromItem` + `type(item).defaultQuill(scene)`
  ```
  (`name=item.resourcesName()` when the instance name can differ)
  ```
- [ ] New item: blank/desired state + `TextItem.defaultQuill(scene)`
- [ ] Place-text must not create a `TextItem` solely to read the theme



### 5. Kill `AppearanceDialog`

- [ ] Route “Appearance…” / multi-select through PropertiesDialog
- [ ] Delete `dialogs/appearance.py` and `editAppearance` view/scene/cmd
  ```
  wiring
  ```
- [ ] Menu/context actions that only opened AppearanceDialog point at
  ```
  Properties instead
  ```

