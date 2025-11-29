# Rotation Compensation: Container + Child Architecture

## Quick Reference

**Key Idea**: Separate positioning (container) from rendering (child text)

**Structure**:
```
Port (parent, can rotate)
└── PropertyTextLineContainer (stable, handles + origin, never rotates)
    └── PropertyTextLineRenderer (child text, rotates 180° if parent is 135-315°)
```

**Why Better**:
- Container coordinates never change → no coordinate system confusion
- Only child rotates → rotation compensation is trivial (10 lines of code)
- Handles stay stable → no counter-rotation needed
- Origin system unchanged → existing logic works as-is

**Performance**: Use `QGraphicsSimpleTextItem` for lines (much faster)

**See**: [Summary section](#summary-why-container--child-architecture-wins) for detailed comparison

---

## The Problem with Current Approach

Currently, PropertyText items try to do everything in one object:
- Manage position and origin offset
- Render text
- Apply rotation compensation
- Manage handles
- Track coordinate transformations between "virtual" and "physical" states

This creates enormous complexity with coordinate system management, especially when rotation compensation flips the bounding rect.

## Proposed Architecture: Container + Child

### Core Concept

**Separate concerns into two objects:**

1. **Container** (`PropertyTextContainer`):
   - Has handles and origin system
   - Manages position (via origin offset or translation)
   - Has a bounding rect that matches the text size
   - Never rotates for compensation (stays aligned with parent)
   - Owns all the positioning logic

2. **Child Text** (`PropertyTextRenderer`):
   - Simple QGraphicsTextItem
   - Renders the actual text
   - Can be rotated 180° for readability compensation
   - Positioned relative to container (always at 0,0 or centered)
   - No complex logic, just rendering

### Visual Structure

```
Port (parent)
└── PropertyTextContainer (origin at Middle Left, handles visible)
    └── PropertyTextRenderer (text, possibly rotated 180°)
```

### How It Works

#### Normal Case (No Compensation)
```
Container:
  - pos: (0, 0) relative to Port
  - rotation: 0°
  - boundingRect: (0, 0, 50, 11)  # Matches text size
  - origin: Middle Left handle

Child Text:
  - pos: (0, 0) relative to Container
  - rotation: 0°
  - text: "clk"
```

#### With Compensation (Parent rotated 180°)
```
Container:
  - pos: (0, 0) relative to Port
  - rotation: 0°  # Container NEVER rotates
  - boundingRect: (0, 0, 50, 11)  # Still matches text size
  - origin: Middle Left handle (still in same place!)

Child Text:
  - pos: (0, 0) relative to Container (or centered)
  - rotation: 180°  # Text rotated to remain readable
  - transformOriginPoint: Middle Center
  - text: "clk" (now readable)
```

## Key Benefits

### 1. No Coordinate System Confusion
The container's coordinate system **never changes**:
- `pos()` always means the same thing
- `boundingRect()` never flips
- Handles stay in the same logical positions
- Origin offset is constant

### 2. No Virtual/Physical Conversion
No need for `_v2p()` or `_p2v()` helpers. The container lives in one coordinate system, period.

### 3. Simple Rotation Compensation
```python
class PropertyTextContainer:
    def onRotationChange(self):
        """Parent rotation changed, update text compensation."""
        total_rotation = self.sceneRotation()

        # Determine if compensation needed
        need_compensation = 135 <= (total_rotation % 360) <= 315

        if need_compensation:
            self._text_item.setRotation(180)
            self._text_item.setTransformOriginPoint(
                self._text_item.boundingRect().center()
            )
        else:
            self._text_item.setRotation(0)
```

That's it! No position adjustments, no offset recalculations, no handle repositioning.

### 4. Origin System Works Naturally
The container uses existing origin system without modification:
- Origin offset in container coordinates
- Handles positioned normally
- No special cases for compensation

### 5. Handles Never Move
Since the container doesn't rotate, handles stay put:
- Origin handle remains at the origin
- No counter-rotation needed
- Handle positions calculated normally

## Implementation Details

### Class Structure

#### Separate Renderers for Performance and Features

```python
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtWidgets import QGraphicsSimpleTextItem, QGraphicsTextItem
from . import Default, DEFAULT

class PropertyTextLineRenderer(QGraphicsSimpleTextItem):
    """Lightweight renderer for single-line text.
    
    Uses QGraphicsSimpleTextItem for better performance.
    For editing, temporarily switch to QGraphicsTextItem.
    """
    
    def __init__(self, text: str = ""):
        super().__init__(text)
    
    def setText(self, text: str):
        """Update text content."""
        QGraphicsSimpleTextItem.setText(self, text)
        # Notify parent container of size change
        if self.parentItem():
            self.parentItem().onTextSizeChange()
    
    def text(self) -> str:
        """Get current text."""
        return QGraphicsSimpleTextItem.text(self)


class TextBlockMixin:
    """Mixin for text block alignment and constraint logic.
    
    Shared between BaseTextBlock and PropertyTextBlockRenderer.
    Implements width/height constraints and alignment as per BaseTextBlock.
    """
    
    # Default to no constraints
    _width: float | Default = DEFAULT
    _height: float | Default = DEFAULT
    _align_v: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignTop
    
    def _applyTextBlockGeometry(self):
        """Apply width/height constraints and alignment.
        
        This is the core logic from BaseTextBlock.onGeometryChange().
        """
        # Apply width constraint to enable text wrapping
        self.setTextWidth(self._width if self._width != DEFAULT else -1)
        
        # Calculate unconstrained rect (without margins)
        doc = self.document()
        root_frame = doc.rootFrame()
        fmt = root_frame.frameFormat()
        fmt.setMargin(0)  # Temporarily remove margins
        root_frame.setFrameFormat(fmt)
        
        # Get unconstrained size
        urect = QGraphicsTextItem.boundingRect(self)
        
        # Apply constraints
        w = urect.width() if self._width is DEFAULT else self._width
        h = urect.height() if self._height is DEFAULT else self._height
        self._brect = QRectF(0, 0, w, h)
        
        # Apply vertical alignment via document top margin
        if self._height != DEFAULT:
            uh = urect.height()  # Unconstrained height
            ch = self._brect.height()  # Constrained height
            if self._align_v == Qt.AlignmentFlag.AlignBottom:
                top_margin = ch - uh
            elif self._align_v == Qt.AlignmentFlag.AlignVCenter:
                top_margin = (ch - uh) / 2
            else:  # Top
                top_margin = 0
            fmt.setTopMargin(top_margin)
            root_frame.setFrameFormat(fmt)
    
    def _setTextBlockAlignment(self, origin_name: str):
        """Set text alignment based on origin handle name.
        
        Horizontal alignment via QTextOption.
        Vertical alignment stored for use in _applyTextBlockGeometry().
        """
        # Set horizontal alignment via QTextOption
        doc = self.document()
        opt = doc.defaultTextOption()
        if "Right" in origin_name:
            h_align = Qt.AlignmentFlag.AlignRight
        elif "Center" in origin_name:
            h_align = Qt.AlignmentFlag.AlignHCenter
        else:
            h_align = Qt.AlignmentFlag.AlignLeft
        opt.setAlignment(h_align)
        doc.setDefaultTextOption(opt)
        
        # Save vertical alignment for use in _applyTextBlockGeometry()
        if "Bottom" in origin_name:
            self._align_v = Qt.AlignmentFlag.AlignBottom
        elif "Middle" in origin_name:
            self._align_v = Qt.AlignmentFlag.AlignVCenter
        else:
            self._align_v = Qt.AlignmentFlag.AlignTop


class PropertyTextBlockRenderer(TextBlockMixin, QGraphicsTextItem):
    """Renderer for multi-line text with alignment and constraints.
    
    Uses QGraphicsTextItem to support wrapping and editing.
    TextBlockMixin provides alignment/constraint logic.
    """
    
    def __init__(self, text: str = ""):
        QGraphicsTextItem.__init__(self)
        self.document().setDocumentMargin(0)  # Minimize margin
        self.setPlainText(text)
        
        # Initialize from mixin
        self._width = DEFAULT
        self._height = DEFAULT
        self._align_v = Qt.AlignmentFlag.AlignTop
        self._brect = self.boundingRect()
    
    def setText(self, text: str):
        """Update text content."""
        self.setPlainText(text)
        # Notify parent container of size change
        if self.parentItem():
            self.parentItem().onTextSizeChange()
    
    def text(self) -> str:
        """Get current text."""
        return self.toPlainText()
    
    def setWidth(self, width: float | Default):
        """Set width constraint."""
        self._width = width
        self._applyTextBlockGeometry()
    
    def setHeight(self, height: float | Default):
        """Set height constraint."""
        self._height = height
        self._applyTextBlockGeometry()
    
    def setAlignment(self, origin_name: str):
        """Set alignment based on origin handle name."""
        self._setTextBlockAlignment(origin_name)
        self._applyTextBlockGeometry()
    
    def boundingRect(self) -> QRectF:
        """Return constrained bounding rect."""
        if hasattr(self, '_brect'):
            return self._brect
        return QGraphicsTextItem.boundingRect(self)
```

#### Base Container with Shared Logic

```python
from PyQt6.QtCore import QRectF
from PyQt6.QtWidgets import QGraphicsObject

from .mixin.origin import ItemOriginMixin
from .mixin.handle import ItemRectHandlesMixin

class PropertyTextContainerBase(QGraphicsObject, ItemOriginMixin, ItemRectHandlesMixin):
    """Base container with shared logic for both line and block."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._text_item = None  # Set by subclass
    
    def boundingRect(self) -> QRectF:
        """Return bounding rect matching text size."""
        return self._text_item.boundingRect()
    
    def paint(self, painter, option, widget):
        """No painting needed, child renders text."""
        pass
    
    def setText(self, text: str):
        """Update text and adjust container size."""
        self._text_item.setText(text)
    
    def text(self) -> str:
        """Get current text."""
        return self._text_item.text()
    
    def onTextSizeChange(self):
        """Called when child text size changes.
        
        Similar to current updateOrigin() - maintains visual origin position
        when text size changes (e.g., during editing).
        """
        # Capture current origin scene position
        old_origin_scene_pos = self.scenePos()
        
        # Update geometry and handles
        self.prepareGeometryChange()
        self.updateHandles()
        
        # Restore origin scene position (keeps visual position stable)
        self.setPos(old_origin_scene_pos)
    
    def onRotationChange(self):
        """Parent rotation changed - apply/remove compensation.
        
        This is called when parent (e.g., Port) rotates.
        Container stays aligned with parent, only child text rotates.
        """
        total_rotation = self.sceneRotation()
        need_compensation = 135 <= (total_rotation % 360) <= 315
        
        if need_compensation:
            # Rotate text 180° around its center for readability
            self._text_item.setRotation(180)
            self._text_item.setTransformOriginPoint(
                self._text_item.boundingRect().center()
            )
        else:
            # No compensation needed
            self._text_item.setRotation(0)


class PropertyTextLineContainer(PropertyTextContainerBase):
    """Container for single-line text (e.g., Port names).
    
    Uses QGraphicsSimpleTextItem for performance.
    """
    
    # No resize handles for single-line text
    _AP_RESIZE = []
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(parent)
        
        # Create lightweight line renderer
        self._text_item = PropertyTextLineRenderer(text)
        self._text_item.setParentItem(self)
        
        # Initialize handles and origin
        self.createHandles()
        self.setOrigin("Middle Left")  # Default for port names


class PropertyTextBlockContainer(PropertyTextContainerBase):
    """Container for multi-line text with alignment and constraints.
    
    Uses QGraphicsTextItem with TextBlockMixin for advanced features.
    Supports width/height constraints and alignment like BaseTextBlock.
    """
    
    def __init__(self, text: str = "", parent=None):
        super().__init__(parent)
        
        # Create block renderer with alignment/constraint support
        self._text_item = PropertyTextBlockRenderer(text)
        self._text_item.setParentItem(self)
        
        # Initialize handles and origin
        self.createHandles()
        self.setOrigin("Top Left")  # Default for blocks
    
    def setOrigin(self, name: str):
        """Override to apply text alignment based on origin."""
        # Tell renderer to set text alignment
        self._text_item.setAlignment(name)
        # Call base implementation
        super().setOrigin(name)
    
    def setWidth(self, width: float | Default):
        """Set width constraint."""
        self._text_item.setWidth(width)
        self.onTextSizeChange()
    
    def setHeight(self, height: float | Default):
        """Set height constraint."""
        self._text_item.setHeight(height)
        self.onTextSizeChange()
    
    def setAutoWidth(self, auto: bool):
        """Set whether width should auto-adjust."""
        self._text_item._width = DEFAULT if auto else self._text_item.boundingRect().width()
        self._text_item._applyTextBlockGeometry()
        self.onTextSizeChange()
    
    def setAutoHeight(self, auto: bool):
        """Set whether height should auto-adjust."""
        self._text_item._height = DEFAULT if auto else self._text_item.boundingRect().height()
        self._text_item._applyTextBlockGeometry()
        self.onTextSizeChange()
```

### Size Synchronization

**Challenge**: Container's `boundingRect()` must match text size.

**Solution**: Text notifies container when size changes:

```python
class PropertyTextRenderer:
    def setText(self, text: str):
        old_rect = self.boundingRect()
        self.setPlainText(text)
        new_rect = self.boundingRect()

        if old_rect != new_rect:
            if self.parentItem():
                self.parentItem().onTextSizeChange()

class PropertyTextContainer:
    def onTextSizeChange(self):
        """Text size changed, update geometry."""
        self.prepareGeometryChange()  # Notify Qt
        self.updateHandles()  # Reposition handles
        # Origin offset may change if origin is size-dependent
```

### Text Positioning Within Container

**Option A**: Text always at (0, 0)
```python
# Simple, text top-left at container top-left
self._text_item.setPos(0, 0)
```

**Option B**: Text centered in container
```python
# Text centered (useful if we add padding later)
text_rect = self._text_item.boundingRect()
container_rect = self.boundingRect()
x = (container_rect.width() - text_rect.width()) / 2
y = (container_rect.height() - text_rect.height()) / 2
self._text_item.setPos(x, y)
```

**Recommendation**: Start with Option A (0, 0), simpler.

### Handle Management

Handles belong to the container and work exactly as they do now:

```python
class PropertyTextContainer:
    def handleRect(self) -> QRectF:
        """Return rect for handle positioning."""
        return self._text_item.boundingRect()  # Delegate to text

    def createHandles(self):
        """Create handles as usual."""
        # Existing handle creation logic works unchanged
```

## Migration Strategy

### Phase 0: Extract TextBlockMixin (Optional, for BaseTextBlock reuse)

Extract alignment/constraint logic from `BaseTextBlock` into `TextBlockMixin`:

```python
# Before: BaseTextBlock has all logic inline
class BaseTextBlock(BaseTextMixin, ItemBoundMixin, ItemShapeMixin, QGraphicsTextItem):
    # All alignment/constraint logic here
    def onGeometryChange(self):
        # Complex logic
        ...

# After: Logic moved to mixin
class TextBlockMixin:
    def _applyTextBlockGeometry(self): ...
    def _setTextBlockAlignment(self, origin_name: str): ...

class BaseTextBlock(BaseTextMixin, TextBlockMixin, ItemBoundMixin, ...):
    def onGeometryChange(self):
        self._applyTextBlockGeometry()  # Call mixin method
        ...
```

**Note**: This phase is optional. Can skip if we're okay duplicating the logic in `PropertyTextBlockRenderer`.

### Phase 1: Create Renderer Classes
- Implement `PropertyTextLineRenderer` (QGraphicsSimpleTextItem wrapper)
- Implement `TextBlockMixin` (extracted or new)
- Implement `PropertyTextBlockRenderer` (QGraphicsTextItem + TextBlockMixin)
- Test renderers in isolation (no containers yet)

### Phase 2: Create Container Base
- Implement `PropertyTextContainerBase` with:
  - `onRotationChange()` - rotation compensation logic
  - `onTextSizeChange()` - maintain visual origin position
  - Shared methods: `boundingRect()`, `paint()`, `setText()`, `text()`
- Test without actual rotation

### Phase 3: Create Specific Containers
- Implement `PropertyTextLineContainer`
  - Uses `PropertyTextLineRenderer`
  - Default origin "Middle Left"
  - No resize handles
- Implement `PropertyTextBlockContainer`
  - Uses `PropertyTextBlockRenderer`
  - Default origin "Top Left"
  - Forwards width/height/alignment methods to renderer
- Test each container independently

### Phase 4: Test Rotation Compensation
- Create test scene with rotatable parent
- Add containers as children
- Rotate parent through full range (0-360°)
- Verify text compensates at 135-315°
- Verify handles stay correct
- Verify origin position stable

### Phase 5: Integration with Port/SymbolPin
- Update `Port` to create `PropertyTextLineContainer` instead of `PropertyTextLine`
- Update `SymbolPin` similarly
- Update any other property text users
- Test port placement, rotation, editing

### Phase 6: Serialization
- Add serialization methods to containers
- Update deserialization to create containers
- Test save/load of documents with property text

### Phase 7: Cleanup
- Remove old `PropertyTextLine`/`PropertyTextBlock` if no longer used
- Remove rotation compensation code from old classes
- Remove virtual/physical coordinate helpers (`_v2p`, `_p2v`)
- Remove `_rotcomp`, `_rotcomp_offset` flags from old code
- Simplify `ItemOriginMixin` (no compensation special cases)

## Design Rationale: Separate Renderers and Containers

### Performance: QGraphicsSimpleTextItem vs QGraphicsTextItem

**QGraphicsSimpleTextItem** (used for single-line):
- ✓ Much faster rendering
- ✓ Lower memory footprint
- ✓ Sufficient for simple port names
- ✗ No text wrapping, formatting, or built-in editing

**QGraphicsTextItem** (used for multi-line):
- ✓ Full text document support
- ✓ Word wrapping, alignment
- ✓ Built-in editing
- ✗ Heavier, slower for simple text

**Decision**: Use separate renderers to optimize for each use case.

### Code Reuse: TextBlockMixin

The alignment and constraint logic in `BaseTextBlock` is substantial and well-tested. Rather than duplicate it, extract into **TextBlockMixin**:

```
TextBlockMixin  (alignment, width/height constraints)
  ├── Used by BaseTextBlock (existing class, unchanged)
  └── Used by PropertyTextBlockRenderer (new renderer)
```

This ensures:
- `BaseTextBlock` continues to work as-is
- `PropertyTextBlockRenderer` gets same alignment/constraint logic
- Single source of truth for complex layout code
- Easy to maintain and test

### Container Hierarchy

```
PropertyTextContainerBase (shared: rotation compensation, size change handling)
  ├── PropertyTextLineContainer
  │     └── PropertyTextLineRenderer (QGraphicsSimpleTextItem)
  └── PropertyTextBlockContainer
        └── PropertyTextBlockRenderer (TextBlockMixin + QGraphicsTextItem)
```

### Comparison with Current Structure

**Current (without containers):**
```
BaseTextLine (QGraphicsSimpleTextItem + all mixins)
└── PropertyTextLine (adds rotation compensation - complex!)

BaseTextBlock (QGraphicsTextItem + all mixins + alignment)
└── PropertyTextBlock (adds rotation compensation - complex!)
```

**Proposed (with containers):**
```
PropertyTextLineContainer (container + mixins, no rotation)
└── PropertyTextLineRenderer (just rendering, rotates 180° if needed)

PropertyTextBlockContainer (container + mixins, no rotation)
└── PropertyTextBlockRenderer (TextBlockMixin + rendering, rotates 180° if needed)
```

### Key Difference

**Current**: Monolithic items trying to handle positioning AND rotation compensation
**Proposed**: Separation - container handles position/origin, child handles text/rotation

## Potential Issues and Solutions

### Issue 1: Editing Text

**Problem**: How does user edit text if it's a child item? Also, `QGraphicsSimpleTextItem` doesn't support editing.

**Solution A (for Line)**: Use dialog-based editing (current approach for PropertyTextLine):
```python
class PropertyTextLineContainer:
    def mouseDoubleClickEvent(self, event):
        """Open edit dialog."""
        # Current approach - dialog opens
        # This is what PropertyTextLine does now
        pass
```

**Solution B (for Line)**: Temporarily replace with editable item:
```python
class PropertyTextLineContainer:
    def enableEditing(self):
        """Switch to editable text item temporarily."""
        # Save current text
        text = self._text_item.text()
        # Remove simple text item
        self._text_item.setParentItem(None)
        # Create editable item
        edit_item = QGraphicsTextItem(text)
        edit_item.setParentItem(self)
        edit_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        edit_item.setFocus()
        # On finish, swap back to simple item
```

**Solution C (for Block)**: Block renderer already uses `QGraphicsTextItem`, so editing works natively:
```python
class PropertyTextBlockContainer:
    def mouseDoubleClickEvent(self, event):
        """Enable editing on child text item."""
        self._text_item.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextEditorInteraction
        )
        self._text_item.setFocus()
```

**Recommendation**: Use Solution A for lines (dialog editing, simpler), Solution C for blocks (inline editing).

### Issue 2: Text Selection

**Problem**: Text might be rotated, selection feels weird.

**Solution**: This is actually fine! QGraphicsTextItem handles it correctly. The text is rotated visually, but selection still works.

### Issue 3: Bounding Rect During Editing

**Problem**: When editing, text might overflow.

**Solution**: Text item can expand, notify container:
```python
class PropertyTextRenderer(QGraphicsTextItem):
    def focusOutEvent(self, event):
        """Editing finished."""
        super().focusOutEvent(event)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        if self.parentItem():
            self.parentItem().onTextSizeChange()
```

### Issue 4: Origin Position During Text Growth

**Problem**: When text grows, origin handle should stay visually fixed.

**Solution**: Container handles this in `onTextSizeChange()`, same as current `updateOrigin()` logic. Since container never rotates for compensation, the logic is simpler:

```python
def onTextSizeChange(self):
    """Text size changed, maintain origin position."""
    # Capture current origin scene position
    old_origin_scene_pos = self.scenePos()  # Using ItemOriginMixin

    # Update handles (this may change _origin_offset)
    self.prepareGeometryChange()
    self.updateHandles()

    # Restore origin scene position
    self.setPos(old_origin_scene_pos)  # Using ItemOriginMixin
```

No special cases for rotation compensation!

### Issue 5: Serialization

**Problem**: Need to save/load container + child state.

**Solution**: Serialize container properties, text is just a child:
```python
class PropertyTextContainer:
    def serialize(self) -> dict:
        return {
            'text': self._text_item.toPlainText(),
            'origin': self._origin_name,
            'pos': (self.pos().x(), self.pos().y()),
            # Container never stores rotation compensation state!
        }

    def deserialize(self, data: dict):
        self.setText(data['text'])
        self.setOrigin(data['origin'])
        self.setPos(QPointF(data['pos'][0], data['pos'][1]))
        # Compensation will be applied by onRotationChange when needed
```

## Comparison with Current Approach

| Aspect | Current (Monolithic) | Proposed (Container+Child) |
|--------|---------------------|----------------------------|
| Coordinate systems | 2 (virtual/physical) | 1 (container only) |
| `pos()` meaning | Changes with compensation | Always consistent |
| `boundingRect()` | Flips with compensation | Never flips |
| Handle positioning | Complex (compensation aware) | Simple (no special cases) |
| Rotation logic | Complex (adjust everything) | Simple (rotate child only) |
| Origin system | Special cases for compensation | Works normally |
| Code complexity | High | Low |
| Testability | Hard (coupled concerns) | Easy (separated concerns) |
| Maintainability | Low | High |

## Decision Criteria

**This approach is better if:**
- ✓ Container + child is conceptually cleaner
- ✓ Eliminates coordinate system complexity
- ✓ Makes rotation compensation trivial
- ✓ Simplifies origin system
- ✓ More maintainable long-term

**Stick with current approach if:**
- ✗ Container + child feels over-engineered
- ✗ Performance concerns (extra object per text)
- ✗ Migration is too risky

## Recommendation

**Strongly recommend container + child approach** because:

1. **Massive simplification**: Eliminates entire categories of bugs (coordinate confusion, offset flipping, handle positioning errors)

2. **Separation of concerns**: Container handles positioning/origin, child handles rendering/rotation. Each simple.

3. **Future-proof**: Easy to extend (add borders, padding, background, multiple text lines, etc.)

4. **Lower risk**: Each component simpler to test and understand

5. **Aligns with Qt**: Parent-child relationship is natural, using Qt's coordinate system as designed

## Next Steps

1. **Create POC**: Build minimal `PropertyTextContainer` + `PropertyTextRenderer`
2. **Test basic case**: No rotation, verify positioning works
3. **Test compensation**: Rotate parent, verify text compensates
4. **Test editing**: Verify text editing works correctly
5. **Test origin**: Verify origin system works without modification
6. **If successful**: Proceed with migration plan

This is an **architectural simplification**, not just a technical change. It could eliminate weeks of debugging coordinate system issues.

## Summary: Why Container + Child Architecture Wins

### Problems It Solves

1. **Coordinate System Complexity** → Container has stable coordinates, only child rotates
2. **Bounding Rect Flipping** → Container rect never flips, child rotation is visual only
3. **Handle Positioning Errors** → Handles belong to stable container, no counter-rotation needed
4. **Origin Offset Confusion** → Origin system works normally, no compensation special cases
5. **Virtual/Physical Conversion** → Eliminated entirely, one coordinate system
6. **Code Fragility** → Separation of concerns makes each component simple and testable

### What Gets Simpler

| Component | Before (Monolithic) | After (Container+Child) |
|-----------|---------------------|-------------------------|
| Rotation compensation | 100+ lines, offset math, handle counter-rotation | 10 lines, rotate child 180° |
| Origin system | Special cases for `_rotcomp` | Works normally, no changes |
| Handle positioning | Check `_rotcomp`, use `_AP_RECT_ROTCOMP` | Always use `_AP_RECT` |
| Position methods | Override `pos()`, `setPos()`, `scenePos()` | Use defaults or translate transform |
| Text size changes | Complex pivot calculations | Simple: prepareGeometryChange + updateHandles |
| Testing | Hard (everything coupled) | Easy (test container and child separately) |

### Performance Benefits

- **Lines**: Use `QGraphicsSimpleTextItem` (much faster than `QGraphicsTextItem`)
- **Blocks**: Use `QGraphicsTextItem` only where needed
- **Handles**: No per-frame handle counter-rotation calculations
- **Rendering**: Child rotation handled by Qt's optimized transform pipeline

### Maintenance Benefits

- **Separation of concerns**: Container = positioning, Child = rendering
- **Reusable logic**: `TextBlockMixin` shared between `BaseTextBlock` and `PropertyTextBlockRenderer`
- **Type safety**: Clear distinction between line and block containers
- **Easier debugging**: Each component testable in isolation
- **Future extensibility**: Easy to add borders, backgrounds, multi-line port names, etc.

### Risk Assessment

**Low Risk** because:
1. New code doesn't affect existing `BaseTextLine`/`BaseTextBlock`
2. Can develop and test containers in parallel
3. Migration can be gradual (phase by phase)
4. Easy to fall back if issues arise (old code still works)
5. Each phase independently testable

**High Reward** because:
1. Eliminates entire class of coordinate system bugs
2. Makes rotation compensation trivial (currently major pain point)
3. Cleaner codebase easier to extend
4. Performance improvements for single-line text
5. Aligns with Qt's design philosophy

## Final Recommendation

**Proceed with Container + Child architecture** using:
- Separate renderers (`PropertyTextLineRenderer`, `PropertyTextBlockRenderer`)
- Shared mixin (`TextBlockMixin`) for alignment/constraint logic
- Separate containers (`PropertyTextLineContainer`, `PropertyTextBlockContainer`)
- Base class (`PropertyTextContainerBase`) for shared rotation compensation

This is not just a refactoring - it's a fundamental simplification that makes rotation compensation almost trivial while improving performance and maintainability.

