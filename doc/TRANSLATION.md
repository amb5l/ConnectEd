# Origin Offset via Translation Transform

## Current Problem
The origin system currently overrides `pos()`, `setPos()`, and `scenePos()` to adjust for `_origin_offset`. This works but adds complexity and potential bugs.

## Proposed Solution
Use Qt's `QTransform` translation to shift the item so the origin point appears at `pos()`, without overriding position methods.

## Current Approach (Method Overrides)

### How It Works
```python
class ItemOriginMixin:
    _origin_offset = QPointF(10, 5)  # Origin in item coordinates

    def pos(self) -> QPointF:
        """Return origin position in parent coordinates."""
        return super().pos() + self._origin_offset

    def setPos(self, pos: QPointF) -> None:
        """Set origin position in parent coordinates."""
        super().setPos(pos - self._origin_offset)

    def scenePos(self) -> QPointF:
        """Return origin position in scene coordinates."""
        return self.mapToScene(self._origin_offset)
```

### Example
- Origin at (10, 5) in item coordinates
- Call `setPos(QPointF(0, 0))` to place origin at parent (0, 0)
- Internally: `super().setPos(0 - 10, 0 - 5)` = `(-10, -5)`
- Item's top-left is at (-10, -5), so origin is at (0, 0) ✓

### Issues
1. **Complexity**: Three method overrides, all carefully coordinated
2. **Fragility**: Easy to get coordinate math wrong
3. **Interaction with transforms**: Overrides don't compose cleanly with other transforms
4. **Not Qt-idiomatic**: Fighting against Qt's design instead of using it

## Proposed Approach (Translation Transform)

### How It Would Work
```python
class ItemOriginMixin:
    _origin_offset = QPointF(10, 5)  # Origin in item coordinates

    def _updateOriginTransform(self) -> None:
        """Update transform to shift item by origin offset."""
        transform = QTransform().translate(-self._origin_offset.x(), -self._origin_offset.y())
        self.setTransform(transform)

    def setOrigin(self, name: str) -> None:
        """Set origin handle."""
        self._origin_name = name
        self._origin_offset = self._handles[name].pos()
        self.setTransformOriginPoint(self._origin_offset)
        self._updateOriginTransform()  # Apply translation

    # No pos/setPos/scenePos overrides needed!
```

### Example
- Origin at (10, 5) in item coordinates
- Transform: `translate(-10, -5)`
- Call `setPos(QPointF(0, 0))` (regular Qt method, no override)
- Item's reference point is shifted by (-10, -5) due to transform
- Origin ends up at parent (0, 0) ✓

### Benefits
1. **Simpler**: No method overrides, just set a transform
2. **Qt-idiomatic**: Using transforms as designed
3. **Cleaner composition**: Can combine with other transforms naturally
4. **Less error-prone**: Qt handles the math

## Key Questions

### Q1: Does this actually work?
**Test needed**: Create a simple item with origin offset via translation and verify:
- `pos()` returns what we expect
- `scenePos()` is correct
- Handles appear at correct positions
- Item rotates around the correct point

### Q2: What about existing transform usage?
Items might already use transforms for other purposes. How do we compose transforms?

**Answer**: Use `QTransform` composition:
```python
def _updateOriginTransform(self) -> None:
    # Get existing transform (if any)
    current = self.transform()

    # Apply origin translation first, then existing transform
    origin_transform = QTransform().translate(-self._origin_offset.x(), -self._origin_offset.y())
    combined = origin_transform * current  # Order matters!

    self.setTransform(combined)
```

**Issue**: This gets complex if other code also calls `setTransform()`. Need a strategy.

### Q3: How to separate origin transform from other transforms?
**Option A**: Always reconstruct the full transform when anything changes
```python
def _rebuildTransform(self) -> None:
    transform = QTransform()
    transform.translate(-self._origin_offset.x(), -self._origin_offset.y())
    # Add other transforms (rotation, scale, etc.)
    self.setTransform(transform)
```

**Option B**: Use `itemTransform()` carefully to preserve non-origin parts

**Option C**: Store non-origin transform separately
```python
class ItemOriginMixin:
    _origin_offset = QPointF()
    _other_transform = QTransform()  # Non-origin transforms

    def _rebuildTransform(self) -> None:
        origin_xform = QTransform().translate(-self._origin_offset.x(), -self._origin_offset.y())
        self.setTransform(origin_xform * self._other_transform)
```

### Q4: What about setTransformOriginPoint?
We're already calling `setTransformOriginPoint(self._origin_offset)` for rotation. With translation, this becomes:
- **Transform origin**: Point around which rotation/scale happen (in item coordinates)
- **Translation**: Shifts the item so origin appears at pos()

These are complementary! Both needed:
- `setTransformOriginPoint(_origin_offset)` → rotation happens around origin
- `translate(-_origin_offset)` → origin appears at pos()

### Q5: Impact on rotation compensation?
If using translation for origin offset, rotation compensation becomes:
```python
transform = QTransform()
transform.translate(-self._origin_offset.x(), -self._origin_offset.y())  # Origin
if self._rotcomp:
    transform.rotate(180)  # Compensation (happens around transformOriginPoint!)
self.setTransform(transform)
```

**Benefit**: No need to move transform origin to Middle Center and back! The 180° rotation already happens around `transformOriginPoint` which we've set to `_origin_offset`.

**Simplification**: The rotation compensation might become much simpler!

## Implementation Challenges

### Challenge 1: Transform Management
Current code doesn't use `setTransform()` much. Introducing it for origin offset means we need a clear strategy:
- Who owns the transform?
- How do we compose multiple transform sources?
- What if user code calls `setTransform()`?

**Proposed Strategy**: Make ItemOriginMixin responsible for the entire transform
```python
class ItemOriginMixin:
    def setTransform(self, transform: QTransform) -> None:
        """Set transform, preserving origin translation."""
        # Store the non-origin transform
        self._user_transform = transform
        # Rebuild with origin included
        self._rebuildTransform()

    def _rebuildTransform(self) -> None:
        """Rebuild transform from origin offset and user transform."""
        full_transform = QTransform()
        full_transform.translate(-self._origin_offset.x(), -self._origin_offset.y())
        full_transform = full_transform * self._user_transform
        super().setTransform(full_transform)
```

### Challenge 2: Rotation Method
Current code uses `setRotation()` (simple angle). With transforms, rotation is part of the transform matrix.

**Options**:
1. Keep using `setRotation()` - it's separate from `transform()` in Qt
2. Move rotation into the transform as well

**Recommendation**: Keep `setRotation()` separate. Qt supports both:
- `setRotation(angle)` - simple rotation
- `setTransform()` - full transform matrix
- They compose automatically!

### Challenge 3: Migration Path
Can't change everything at once. Need a gradual migration:

**Phase 1**: Add translation-based origin to ItemOriginMixin
- Keep existing `pos()`/`setPos()` overrides as fallback
- Add flag `_use_translation = True` to opt in

**Phase 2**: Test thoroughly with PropertyText

**Phase 3**: Remove old overrides once confident

## Proof of Concept Needed

Before committing to this approach, create a minimal test:

```python
class TestItem(QGraphicsRectItem, ItemOriginMixin, ItemHandlesMixin):
    def __init__(self):
        super().__init__(0, 0, 50, 30)
        self.createHandles()
        self.setOrigin("Middle Center")  # Uses translation approach
        self.setPos(100, 100)  # Should work without override

# Test:
# 1. Does origin appear at (100, 100)?
# 2. Does item rotate around Middle Center?
# 3. Are handles positioned correctly?
# 4. Does scene position work correctly?
```

## Comparison Table

| Aspect | Current (Override) | Proposed (Translation) |
|--------|-------------------|------------------------|
| pos() override | Yes | No |
| setPos() override | Yes | No |
| scenePos() override | Yes | No |
| Transform management | Simple (none) | Complex (need strategy) |
| Composition with rotation | Manual math | Automatic |
| Composition with compensation | Complex | Simpler |
| Qt idioms | Against | With |
| Code complexity | Medium | Lower (after setup) |
| Risk | Known working | Needs testing |

## Decision Point

**Before proceeding**: Answer these questions:
1. Does the basic translation approach work as expected? → Need POC
2. Can we manage transform composition cleanly? → Need design
3. Does this simplify rotation compensation? → Analyze ROTATION_COMPENSATION.md
4. Is migration path feasible? → Need plan

**If all "yes"**: Proceed with implementation
**If any "no"**: Stick with current override approach

## Recommendation

This approach is **promising but needs validation**. The potential benefits are significant:
- Simpler code (no position overrides)
- More Qt-idiomatic
- Could simplify rotation compensation substantially

**Next steps**:
1. Create proof-of-concept test
2. Verify basic functionality works
3. Design transform management strategy
4. Create detailed implementation plan
5. Consider impact on rotation compensation

Only after POC succeeds should we commit to changing the codebase.


