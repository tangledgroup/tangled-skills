# TUI Rendering - Deep Dive

This reference document explains how pi-tui implements flicker-free terminal UI rendering with differential updates and component management.

## The Flicker Problem

Traditional terminal UIs flicker because they:
1. Clear the entire screen
2. Redraw all content
3. User sees the blank screen briefly before new content appears

This is especially noticeable with frequent updates (like streaming LLM responses) and on slower terminals or remote connections.

Pi's solution uses **differential rendering** combined with **synchronized output** to eliminate flicker entirely.

## Differential Rendering Strategies

Pi uses three rendering strategies based on what changed:

### Strategy 1: First Render

When the UI starts:
- Output all lines without clearing scrollback
- Cursor ends up at the bottom
- No flicker because we're just writing, not erasing

**Why not clear first?** Clearing would erase scrollback history. By just writing, users can still scroll up to see earlier output (like application startup messages).

### Strategy 2: Width Changed

When terminal resizes:
- Clear screen and fully re-render
- All layouts need recalculation for new width
- Text wrapping changes, component positions shift

**Why full re-render?** Cached renders are invalid after resize. Components need to recalculate line breaks, truncation, and positioning. There's no efficient way to patch an old render to a new width.

### Strategy 3: Normal Update (Differential)

When content changes but width stays the same:
1. Render new content to memory (not screen)
2. Compare with previous render to find first changed line
3. Move cursor to that line
4. Clear from cursor to end of screen
5. Write only changed lines

**Example**: If a 100-line UI changes on line 45:
- Old approach: Clear all 100 lines, redraw all 100 lines (100 clear + 100 write operations)
- Pi's approach: Move to line 45, clear 56 lines, write 56 lines (1 move + 56 clear + 56 write operations)

For small changes at the bottom, this might be just a few lines. For large changes at the top, it approaches a full re-render, but that's unavoidable.

**How difference detection works**:
```
Find first line where newLines[i] !== oldLines[i]
If new content is shorter, also clear the extra old lines
```

This is O(n) where n is the number of changed lines, not total lines.

## Synchronized Output (CSI 2026)

Even with differential rendering, users might see intermediate states if the terminal renders incrementally. Pi wraps all updates in synchronized output mode:

```
\x1b[?2026h  ; Enable synchronized output
... all render data ...
\x1b[?2026l  ; Disable and display
```

**What this does**: The terminal buffers all output between enable/disable and displays it atomically. Users see either the old state or the new state, never a partially-updated state.

**Supported terminals**: Kitty, Ghostty, WezTerm, iTerm2, and other modern terminals that support the Synchronized Output DEC private mode.

**Fallback**: On unsupported terminals, pi still uses differential rendering (just without atomic display). Better than clearing everything, even if not perfectly flicker-free.

## Component Architecture

Pi's UI is built from composable components:

### Component Interface

Every component implements:
- `render(width: number): string[]` - Returns lines for given width
- `handleInput?(data: string): void` - Optional input handler
- `invalidate?(): void` - Optional cache invalidator

**Key constraint**: Each line returned by render() must not exceed the width parameter. The TUI will error if a component returns an over-width line.

**Why this interface?**
- Simple: Just a render function, no complex lifecycle
- Width-aware: Components receive available width for proper wrapping/truncation
- Optional input: Only interactive components need handleInput
- Optional invalidation: Only cached components need invalidate

### Container Components

Containers hold child components and manage layout:

**Vertical stacking**: Children render top-to-bottom, each getting full width

**Padding**: Box components add horizontal/vertical padding around children

**Background**: Box components can apply background colors to the padded area

**Example structure**:
```
Container (full width)
  ├─ Text component (header)
  ├─ Spacer (1 line)
  ├─ Box (with padding and background)
  │   ├─ Markdown component
  │   └─ Markdown component
  ├─ Spacer (1 line)
  └─ Editor component (input)
```

Each child renders independently; the container concatenates their output.

### Render Caching

Components cache rendered output to avoid unnecessary re-renders:

**Cache key**: Width + content state

**When cached**:
- If width unchanged and content unchanged, return cached lines
- No string manipulation, no wrapping, no truncation

**When invalidated**:
- Content changes (setText, pushMessage, etc.)
- Theme changes (colors, styles)
- Explicit invalidate() call

**Example**: An Editor component caches its render. When streaming text arrives:
1. Update internal text state
2. Call invalidate() to clear cache
3. TUI requests render
4. Editor re-renders from scratch, caches new output

Without caching, every TUI update would force all components to re-render, even unchanged ones. With caching, only modified components re-render.

## Focus System and IME Support

### The IME Problem

Input Method Editors (for Chinese, Japanese, Korean, etc.) show a candidate window near the text cursor. If the cursor is in the wrong position, the candidate window appears somewhere useless.

Terminal emulators position the hardware cursor based on the last written character. But pi uses **fake cursors** (rendered as part of the UI) for most components, hiding the real hardware cursor. This breaks IME positioning.

### Pi's Solution: Cursor Marker

Pi uses a zero-width APC (Application Program Command) sequence as a cursor marker:

```
\x1b]1337;CursorPos=1;\x1b\\
```

**How it works**:
1. Focusable components emit the marker right before the fake cursor position
2. TUI scans rendered output for the marker
3. TUI calculates the marker's screen position (row, column)
4. TUI moves the hardware cursor to that position
5. TUI shows the hardware cursor
6. IME candidate window appears at the correct position

**Component implementation**:
```typescript
class Input implements Component, Focusable {
    focused = false; // Set by TUI when this component has focus
    
    render(width: number): string[] {
        const marker = this.focused ? CURSOR_MARKER : "";
        return [`| ${this.text}${marker}_`]; // '_' is fake cursor
    }
}
```

**Container components**: If a container (like a dialog) contains an input, it must propagate focus to the child:
```typescript
set focused(value: boolean) {
    this._focused = value;
    this.searchInput.focused = value; // Propagate to child
}
```

Without propagation, the marker would be in the child's render output, but the parent wouldn't know to position the hardware cursor.

## Overlay System

Overlays render components on top of existing content without replacing it. Used for dialogs, menus, selectors, and modals.

### Positioning Strategies

Overlays support multiple positioning approaches:

**Anchor-based**: Position relative to anchor points
- 'center', 'top-left', 'bottom-right', etc.
- Overlay is centered or aligned to the anchor

**Percentage-based**: Position as percentage of terminal size
- row: "25%" places overlay at 25% from top
- col: "50%" places overlay at 50% from left
- Responsive to terminal resizing

**Absolute**: Exact row/column position
- row: 5, col: 10 places at specific coordinates
- Overrides anchor/percentage if specified

**Sizing**:
- Fixed width/height in cells
- Percentage width/height
- Min/max constraints
- Automatic content-based sizing

### Rendering Overlays

Overlays render **on top of** the main UI:
1. Render main UI to a buffer
2. Render overlay at its position, overwriting the buffer
3. Display the combined buffer

**Key insight**: Overlays don't modify the main UI's component tree. They're a separate rendering layer that composites on top.

### Focus Management

Overlays can capture focus:
- **Capturing overlays**: Steal focus when shown, return it when hidden
- **Non-capturing overlays**: Don't affect focus, useful for tooltips/status

**Focus stack**: Multiple overlays maintain a focus stack:
- Topmost capturing overlay has focus
- Hiding an overlay restores focus to the previous one
- No capturing overlays? Focus returns to main UI

### Visibility Control

Overlays can be conditionally visible:
```typescript
tui.showOverlay(component, {
    visible: (termWidth, termHeight) => termWidth >= 100
});
```

The visible callback is called every frame. If it returns false, the overlay doesn't render (but stays in the overlay stack).

**Use case**: Hide complex UI on narrow terminals, show simplified versions.

## Text Handling Utilities

Pi provides utilities for working with text in terminal contexts:

### Visible Width Calculation

ANSI escape codes (colors, styles) don't take up screen space:
```typescript
visibleWidth("\x1b[31mHello\x1b[0m") // Returns 5, not 16
```

**Implementation**: Strip ANSI codes, then count characters. Handles:
- Single-width characters (ASCII, most Latin)
- Double-width characters (CJK, some symbols)
- Zero-width characters (combining marks, directional controls)

### Truncation

Truncate text to fit available width:
```typescript
truncateToWidth("Hello World", 8) // "Hello..."
truncateToWidth("Hello World", 8, "") // "Hello Wo" (no ellipsis)
```

**Preserves ANSI codes**: If input is styled, output maintains styling on the visible portion.

**Handles double-width**: Correctly truncates at character boundaries, not byte boundaries.

### Word Wrapping

Wrap long lines to fit width:
```typescript
wrapTextWithAnsi("This is a long line", 10)
// ["This is a", "long line"]
```

**Preserves ANSI codes**: Styles continue across line breaks.

**Word boundaries**: Wraps at spaces when possible, hard-wraps mid-word only if necessary.

**Why important?** Components use this to ensure lines don't exceed width.

## Input Handling

### Keyboard Protocol

Pi uses the Kitty keyboard protocol when available:
- Disambiguates similar key combinations (Ctrl+Space vs Escape sequence)
- Supports more keys (Media keys, Function keys beyond F12)
- More reliable than traditional escape sequences

**Fallback**: Traditional escape sequences for older terminals.

### Key Matching

Utility function for detecting keyboard input:
```typescript
if (matchesKey(data, Key.ctrl("c"))) {
    // Handle Ctrl+C
} else if (matchesKey(data, Key.enter)) {
    // Handle Enter
}
```

**Supports**:
- Basic keys: enter, escape, tab, backspace, delete, arrows
- Modifiers: ctrl, shift, alt
- Combined: ctrl+shift+p, alt+left, etc.

**Why not just check strings?** Escape sequences vary by terminal. matchesKey normalizes across terminals and protocols.

### Paste Handling

Pi detects bracketed paste mode:
- Paste start marker: `\x1b[200~`
- Paste end marker: `\x1b[201~`

**Large pastes**: Pastes >10 lines create a compressed marker in the editor:
```
[paste #1 +50 lines]
```

User can expand the paste to view/edit contents. This prevents the editor from becoming unwieldy with huge pastes.

## Performance Optimizations

### Minimal Re-renders

Only modified components re-render:
- TUI tracks which components called invalidate()
- Only those components are re-rendered on next frame
- Unchanged components return cached output

### Efficient Difference Detection

Finding first changed line is O(n) where n is changed lines, not total lines:
```typescript
for (let i = 0; i < max(new.length, old.length); i++) {
    if (new[i] !== old[i]) return i;
}
return new.length; // All old lines match, or new is shorter
```

### Batched Updates

Multiple invalidations within a frame are batched:
- Component A invalidates
- Component B invalidates
- TUI renders once, not twice

**How**: invalidate() marks component as dirty; render() checks dirty flag and re-renders all dirty components in one pass.

### String Interning

Frequently-used strings (border characters, common UI elements) are interned:
- Same string literal = same object reference
- Faster comparison (reference equality vs character-by-character)
- Lower memory usage

## Component Examples

### Text Component

Simplest component - renders wrapped text:
- Caches render until text changes or width changes
- Uses wrapTextWithAnsi for word wrapping
- Supports optional background color

### Editor Component

Most complex component - multi-line editing:
- Maintains cursor position, scroll offset, undo stack
- Handles input (typing, navigation, deletion)
- Supports autocomplete (file paths, slash commands)
- Implements Focusable for IME support
- Caches render but invalidates on every character change

### SelectList Component

Interactive selection list:
- Renders visible subset of items (with scrolling)
- Tracks selected index
- Handles arrow key navigation, Enter to select, Escape to cancel
- Supports filtering (type to narrow options)
- Caches render except when selection/filter changes

### Markdown Component

Renders markdown with syntax highlighting:
- Parses markdown to AST
- Renders each element with appropriate styling
- Code blocks get syntax highlighting via highlight.js or similar
- Caches render until content/theme changes
- Supports custom theme for all markdown elements

## Debugging Rendering

Pi includes debugging tools:

**Render logging**: Set PI_TUI_WRITE_LOG to capture raw ANSI output

**Debug key**: Shift+Ctrl+D triggers debug callback (can log state, dump render tree)

**Component borders**: Development mode can add colored borders to components to visualize layout

**Performance metrics**: Track render times, cache hit rates, invalidation frequency

These help identify:
- Components that re-render too frequently
- Layout issues (over-width lines, misaligned elements)
- Input handling problems (keys not captured, focus issues)
