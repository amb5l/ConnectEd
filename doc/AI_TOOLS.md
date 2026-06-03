
- main window

- subwindow
  - maximise/focus
- view
  - zoom full/area/item/in/out



OLD CONTENT

Tools available to LLMs.

## Read

| Tool | Description |
|------|-------------|
| `get_active_view` | Active diagram view; returns `view` ref and scene name |
| `get_sheet` | Sheet name and dimensions for a `view` |
| `get_items` | Top-level items: ref, kind, position, bounding rect (`left`/`top`/`width`/`height`) |

## Write (require edit lock)

| Tool | Description |
|------|-------------|
| `set_sheet` | Sheet `width` and `height` (scene units) for a `view` |
| `add_block` | Block with `label`, HDL `name`, `left`/`top`/`width`/`height`; returns `item` ref |
| `add_block_pin` | One pin on a block (`item` ref): `name`, `direction`, `edge`, `offset` |
| `add_block_pins` | All pins in one call: `pins` array of pin objects |
| `add_connection` | Orthogonal wire from `start` `{x,y}` or `start_ref` through `offsets` `[{axis,delta},…]` |

Pin `direction`: `in`, `out`, `bi` (VHDL `inout` → `bi`). Pin `edge`: `left`, `right`, `top`, `bottom`. Bus pins: include `:` in `name` (e.g. `data[7:0]`).

Connection `axis`: `H` (horizontal) or `V` (vertical). `delta` is signed scene units (+X for H, +Y for V). Example: `[{"axis":"H","delta":40},{"axis":"V","delta":-20}]`.

## Other

| Tool | Description |
|------|-------------|
| `ping` | Health check |
