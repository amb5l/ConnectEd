# Rotation Compensation Design

## Summary
This document describes rotation compensation for PropertyText to keep text readable when rotated upside-down (135° to 315° scene rotation).

**Key Architectural Decision**: Introduce `onSizeChange()` method in PropertyText to orchestrate all geometry-change responses (handle positioning, origin maintenance, compensation offset updates). This replaces the overloaded `updateHandles()` method and provides cleaner separation of concerns.

## Motivation
Keep property text readable (left-to-right or top-to-bottom) when its total effective (scene) rotation is in the range 135° to 315°.

## Requirements

### 1. When to Apply
- **Scene rotation 135° < θ ≤ 315°**: Apply 180° compensation to text if not already active
- **Scene rotation outside this range**: Remove compensation if active

### 2. Visual Behavior
- Text rotated an additional 180° to remain readable
- Handles - especially the origin - don't move (requires counter rotation)
- Transform origin temporarily moves to Middle Center for the 180° rotation, then restored to origin

### 3. Transparent to External Code
Public methods (`pos()`, `setPos()`, `rotation()`, `setRotation()`) should hide the compensation:
- External code sees "logical" values (uncompensated)
- Internal compensation is applied on top

## Architecture: Geometry Change Handling

### Current Responsibilities
`ItemHandlesMixin.updateHandles()` has grown beyond its original scope:
1. Update handle positions based on bounding rect
2. Update origin offset and transform origin (via `updateOrigin()`)
3. **NEW**: Should also update `_rotcomp_offset` when compensated

### Proposed Refactoring: `onSizeChange()`
Since rotation compensation is PropertyText-specific, and geometry change handling has broadened, create:

**`PropertyText.onSizeChange()`** (or in PropertyTextMixin):
```python
def onSizeChange(self) -> None:
    """Handle geometry changes (text resize, etc.)."""
    # 1. Update handle positions (origin handle moves in item coordinates)
    self.updateHandles()

    # 2. Update origin offset and restore position
    self.updateOrigin()  # Captures position, recalculates offset, restores position

    # 3. Update rotation compensation offset if active
    if getattr(self, '_rotcomp', False):
        rect = self.boundingRect()
        self._rotcomp_offset = QPointF(rect.width(), rect.height())
```

**`ItemHandlesMixin.updateHandles()`** - simplified back to core responsibility:
```python
def updateHandles(self) -> None:
    """Update handle positions based on current bounding rect."""
    if not hasattr(self, "_handles"):
        return
    rect = self.handleRect()
    x0 = rect.topLeft().x()
    y0 = rect.topLeft().y()
    w = rect.width()
    h = rect.height()
    for name, (x, y) in self._AP_RECT.items():
        self._handles[name].setPos(QPointF(x0 + (x * w), y0 + (y * h)))
```

**`ItemOriginMixin.updateOrigin()`** - simplified, no pos parameter:
```python
def updateOrigin(self) -> None:
    """Update origin offset and transform origin, preserving visual position."""
    # Capture position before updating offset
    target_pos = self.pos()  # Uses OLD _origin_offset

    # Update origin offset from handle position
    self._origin_offset = self._handles[self._origin_name].pos()
    self.setTransformOriginPoint(self._origin_offset)

    # Restore position (uses NEW _origin_offset)
    self.setPos(target_pos)
```

**Benefits**:
- Clear separation of concerns
- `updateHandles()` is pure handle positioning
- PropertyText-specific logic (compensation) stays in PropertyText
- Easier to understand and maintain

**Design Question**: Should this be in `PropertyTextMixin` or directly in `PropertyText`?
- **Option A**: Create `PropertyTextMixin` - good if multiple property text classes need this behavior
- **Option B**: Add directly to `PropertyText` - simpler if it's the only class that needs it
- **Recommendation**: Start with Option B (directly in PropertyText) unless there's a clear need for reuse

### Internal State
- `_rotcomp`: bool flag indicating if compensation is currently active
- `_rotcomp_offset`: Stored bounding rect size when compensation is applied (updated by `onSizeChange()`)
- `_origin_offset`: Always in uncompensated item coordinates
- Transform origin: Temporarily at Middle Center during rotation, restored to origin after

### Method Overrides

#### `rotation()` - Hide compensation from outside
```python
def rotation(self) -> float:
    """Return logical rotation (uncompensated)."""
    rot = QGraphicsItem.rotation(self)
    if getattr(self, '_rotcomp', False):
        rot = (rot - 180) % 360
    return rot
```

#### `setRotation(angle)` - Apply compensation if needed
```python
def setRotation(self, angle: float) -> None:
    """Set logical rotation, applying compensation if needed."""
    compensate = getattr(self, '_rotcomp', False)
    actual_angle = (angle + 180) % 360 if compensate else angle
    QGraphicsItem.setRotation(self, actual_angle)
```

#### `sceneRotation()` - Return logical scene rotation
```python
def sceneRotation(self) -> float:
    """Return logical scene rotation (uncompensated)."""
    rot = self.rotation()  # Uses our override, already uncompensated
    parent = self.parentItem()
    while parent:
        rot += parent.rotation()
        parent = parent.parentItem()
    return rot % 360
```

#### `pos()` - Convert from physical to virtual coordinates
When compensation is active, `super().pos()` returns the physical Qt position (opposite corner).
We use `_p2v()` to convert to virtual (logical) position.

```python
def pos(self) -> QPointF:
    """Return origin position in parent coordinates (virtual/logical)."""
    physical_pos = super().pos()
    virtual_pos = self._p2v(physical_pos)
    return virtual_pos + self._origin_offset
```

#### `setPos(pos)` - Convert from virtual to physical coordinates
The input position is virtual (logical). We use `_v2p()` to convert to physical Qt position.

```python
def setPos(self, pos: QPointF) -> None:
    """Set origin position in parent coordinates (virtual/logical)."""
    virtual_pos = pos - self._origin_offset
    physical_pos = self._v2p(virtual_pos)
    super().setPos(physical_pos)
```

#### `onRotationChange()` - Apply/remove compensation
```python
def onRotationChange(self) -> None:
    """Apply or remove rotation compensation."""
    rotcomp = getattr(self, '_rotcomp', False)
    scene_rot = self.sceneRotation()
    should_compensate = (135 < scene_rot <= 315) and not rotcomp
    should_remove = rotcomp and not (135 < scene_rot <= 315)

    if should_compensate or should_remove:
        # Step 1: Save current virtual (logical) position
        target_pos = self.pos()  # Uses our pos() override, returns virtual position

        # Step 2: Save compensation offset (only when applying, not removing)
        if should_compensate:
            rect = self.boundingRect()
            self._rotcomp_offset = QPointF(rect.width(), rect.height())

        # Step 3: Toggle compensation flag
        self._rotcomp = should_compensate

        # Step 4: Clear compensation offset when removing
        if should_remove:
            self._rotcomp_offset = QPointF()

        # Step 5: Apply 180° rotation around Middle Center
        self.setTransformOriginPoint(self._handles["Middle Center"].pos())
        QGraphicsItem.setRotation(self, (QGraphicsItem.rotation(self) + 180) % 360)

        # Step 6: Restore transform origin to logical origin
        self.setTransformOriginPoint(self._origin_offset)

        # Step 7: Restore virtual position (uses our setPos() override with _v2p conversion)
        self.setPos(target_pos)

        # Step 8: Update geometry (handles, origin, compensation offset)
        self.onSizeChange()
```

## Virtual vs Physical Coordinate System

### Concept
Using virtual/physical separation cleanly solves the position complexity:
- **Physical**: Actual Qt position/rotation as seen by Qt (may be at opposite corner when compensated)
- **Virtual**: Logical position/rotation seen by external code (always consistent)
- Compensation affects physical, but virtual stays consistent

### Mapping Functions
```python
def _v2p(self, virtual_pos: QPointF) -> QPointF:
    """Convert virtual (logical) position to physical (Qt) position."""
    if not getattr(self, '_rotcomp', False):
        return virtual_pos
    # When compensated, physical position is offset by bounding rect size
    return virtual_pos - getattr(self, '_rotcomp_offset', QPointF())

def _p2v(self, physical_pos: QPointF) -> QPointF:
    """Convert physical (Qt) position to virtual (logical) position."""
    if not getattr(self, '_rotcomp', False):
        return physical_pos
    # Remove compensation offset to get virtual position
    return physical_pos + getattr(self, '_rotcomp_offset', QPointF())
```

### Benefits
- Separates concerns cleanly
- `pos()` and `setPos()` become simple wrappers
- Position preservation in `onRotationChange()` works naturally: save virtual position before, restore after
- No circular dependencies or complex calculations

## Open Questions & Decisions

### Q1: Transform Origin Management ✅ RESOLVED
When applying compensation:
1. Set transform origin to Middle Center
2. Apply 180° rotation
3. Restore transform origin to `_origin_offset`

**Decision**: After restoration, use `setPos(target_pos)` where `target_pos` is the saved virtual position. The v2p conversion in `setPos()` will handle the physical adjustment automatically.

### Q2: Position Calculation Complexity ✅ RESOLVED
**Decision**: Use virtual/physical coordinate separation with `_v2p()` and `_p2v()` helper functions. This makes `pos()` and `setPos()` simple and correct.

### Q3: Handle Counter-rotation
When text is rotated 180°, handles need to stay visually fixed. Options:
1. Counter-rotate handles explicitly by -180°
2. Use `_AP_RECT_ROTCOMP` (mirrored handle positions)

**Question**: Which approach is cleaner? Previously we used `_AP_RECT_ROTCOMP`. Does this still work with the new origin system?

### Q4: Scene Position Preservation ✅ RESOLVED
**Decision**: Save `target_pos = self.pos()` before applying compensation, then `self.setPos(target_pos)` after. The virtual/physical system handles the rest automatically.

## Implementation Plan

### Files to Modify

1. **`ConnectEd/widgets/graphics/items/mixin/handle.py`** (ItemHandlesMixin)
   - **Simplify** `updateHandles()`: Remove the `updateOrigin()` call, make it pure handle positioning
   - Optionally: Use `_AP_RECT_ROTCOMP` when `_rotcomp=True` for handle counter-rotation

2. **`ConnectEd/widgets/graphics/items/mixin/origin.py`** (ItemOriginMixin)
   - **Simplify** `updateOrigin()`: Remove the `pos` parameter, capture position internally before updating offset

3. **`ConnectEd/widgets/graphics/items/property_text.py`** (PropertyText class or PropertyTextMixin)
   - Add `onSizeChange()` method to orchestrate geometry change responses
   - Add `_v2p()` and `_p2v()` helper methods for coordinate conversion
   - Override `pos()` and `setPos()` to use virtual/physical conversion
   - Override `rotation()` and `setRotation()` to hide compensation
   - Implement `onRotationChange()` to apply/remove compensation

4. **`ConnectEd/widgets/graphics/items/base_text.py`** (BaseText class)
   - Update `setText()` to call `onSizeChange()` if it exists, otherwise fall back to `updateHandles()`

5. **`ConnectEd/widgets/graphics/items/mixin/rotate.py`** (ItemRotateMixin)
   - Override `setRotation()` to call `onRotationChange()` on property text children

### Implementation Steps

#### Step 0: Refactor updateHandles() → onSizeChange()
**Goal**: Separate handle positioning from geometry change orchestration

1. Simplify `ItemHandlesMixin.updateHandles()` - remove `updateOrigin()` call
2. Simplify `ItemOriginMixin.updateOrigin()` - remove `pos` parameter, capture position internally
3. Create `PropertyText.onSizeChange()` that:
   - Calls `updateHandles()` for handle positioning
   - Calls `updateOrigin()` to recalculate offset and restore position
   - Updates `_rotcomp_offset` if compensated
4. Update `BaseText.setText()` to call `onSizeChange()` instead of `updateHandles()`

**Benefit**: Clean separation - handles, origin, and compensation each handled explicitly. Each method is self-contained with no need to pass state between them.

#### Step 1: Add Helper Functions to PropertyText
Add `_v2p()` and `_p2v()` conversion functions to handle virtual/physical coordinate mapping.

#### Step 2: Update pos() and setPos() in PropertyText
Override to use the conversion functions. Should work correctly even when `_rotcomp=False` (conversions are no-ops).

#### Step 3: Add rotation() and setRotation() overrides to PropertyText
Hide the 180° compensation from external code.

#### Step 4: Implement onRotationChange() in PropertyText
Apply/remove compensation based on scene rotation, using the step-by-step process outlined above.

#### Step 5: Update ItemRotateMixin.setRotation()
Items that can rotate (Port, etc.) need to call `onRotationChange()` on their property text children when they rotate.

#### Step 6: Handle Counter-rotation (if needed)
If handles don't stay fixed, implement counter-rotation or use `_AP_RECT_ROTCOMP`.

## Next Steps

1. ✅ Verify basic origin system works without compensation
2. ✅ Test rotation around origin
3. Implement compensation with virtual/physical coordinate separation
4. Test all edge cases
5. Update ItemRotateMixin to call onRotationChange()

## Edge Cases & Potential Issues

### Initialization
- **Problem**: Text loaded from XML at 180° needs compensation applied on load
- **Solution**: Call `onRotationChange()` after loading/creating property text

### setText() During Compensation
- **Problem**: When text changes, bounding rect changes, so `_rotcomp_offset` becomes stale
- **Solution**: `setText()` calls `onSizeChange()` which updates `_rotcomp_offset` automatically

### Handle Counter-rotation During Compensation
- **Problem**: Handle positions might be wrong during compensation
- **Solution**: Use `_AP_RECT_ROTCOMP` (mirrored positions) when `_rotcomp=True`, or apply counter-rotation to handles

### Nested Rotations
- **Problem**: What if both parent and grandparent are rotated?
- **Solution**: Use `sceneRotation()` which accumulates all parent rotations correctly

### Compensation Toggle at Boundaries
- **Problem**: At exactly 135° or 315°, compensation might toggle repeatedly
- **Solution**: Use consistent inequality (135 < θ ≤ 315) to avoid thrashing

## Test Cases to Verify

- [ ] Place port, rotate it manually - text rotates around origin
- [ ] Place port at 180°, name should be readable (compensation applied)
- [ ] Edit name of compensated text - origin stays fixed
- [ ] Change origin of compensated text - origin moves correctly
- [ ] Load from XML with 180° rotation - compensation applied correctly
- [ ] Rotate port from 0° to 180° - compensation applies smoothly
- [ ] Rotate port from 180° to 0° - compensation removes smoothly
- [ ] Edit text while compensated - bounding rect change handled correctly
- [ ] Nested rotations (parent + grandparent) - compensation based on total scene rotation
- [ ] Rotation at boundary angles (135°, 315°) - no thrashing

