# DragMove.js - Draggable Elements

A super tiny (~500 bytes) JavaScript library to make DOM elements draggable and movable.

## Overview

Add drag-and-drop functionality to any DOM element with minimal code and zero dependencies.

## Installation

### CDN
```html
<script src="https://unpkg.com/dragmove.js"></script>
```

### Download
```bash
wget https://raw.githubusercontent.com/knadh/dragmove.js/master/dist/dragmove.min.js
```

## Basic Usage

### Make Element Draggable

```html
<div id="draggable" style="width: 200px; height: 150px; background: #3b82f6; color: white; display: flex; align-items: center; justify-content: center;">
  Drag me!
</div>

<script src="dragmove.min.js"></script>
<script>
const dm = new DragMove('#draggable');
</script>
```

### Multiple Elements

```javascript
document.querySelectorAll('.draggable').forEach(el => {
  new DragMove(el);
});
```

## Options

```javascript
new DragMove(element, {
  // Element to use as drag handle (defaults to entire element)
  handle: '.drag-handle',
  
  // Container to constrain dragging (optional)
  container: '#container',
  
  // Callback when dragging starts
  onDragStart: (e) => {
    console.log('Drag started');
  },
  
  // Callback during drag (called continuously)
  onDrag: (e, x, y) => {
    console.log('Dragging to:', x, y);
  },
  
  // Callback when dragging ends
  onDragEnd: (e, x, y) => {
    console.log('Drag ended at:', x, y);
  },
  
  // Snap to grid size in pixels (0 = no snap)
  snap: 10,
  
  // Inertia effect after release (pixels)
  inertia: 0
});
```

## Drag Handle Example

```html
<div id="window" style="width: 400px; height: 300px; border: 1px solid #ccc; background: white;">
  <div class="drag-handle" style="padding: 8px; background: #f0f0f0; cursor: move; border-bottom: 1px solid #ddd;">
    ☰ Drag Handle
  </div>
  <div style="padding: 16px;">
    Window content here...
  </div>
</div>

<script>
const dm = new DragMove('#window', {
  handle: '.drag-handle'
});
</script>
```

## Constrained Dragging

### Within Container

```html
<div id="container" style="width: 600px; height: 400px; border: 2px dashed #ccc; position: relative;">
  <div id="box" style="width: 100px; height: 100px; background: #3b82f6; position: absolute;">
    Drag within container
  </div>
</div>

<script>
new DragMove('#box', {
  container: '#container'
});
</script>
```

### With Boundaries

```javascript
new DragMove('#draggable', {
  onDrag: (e, x, y) => {
    // Keep within viewport
    const maxX = window.innerWidth - e.target.offsetWidth;
    const maxY = window.innerHeight - e.target.offsetHeight;
    
    return {
      x: Math.max(0, Math.min(x, maxX)),
      y: Math.max(0, Math.min(y, maxY))
    };
  }
});
```

## Snap to Grid

```javascript
new DragMove('#grid-item', {
  snap: 20 // Snap to 20px grid
});
```

## Real-world Example: Draggable Cards

```html
<div style="display: flex; gap: 16px; padding: 20px;">
  <article class="card draggable-card" style="width: 300px; cursor: move;">
    <header>
      <h3>Task 1</h3>
      <p class="text-light">Drag me anywhere</p>
    </header>
    <p>This card is draggable.</p>
  </article>
  
  <article class="card draggable-card" style="width: 300px; cursor: move;">
    <header>
      <h3>Task 2</h3>
      <p class="text-light">Drag me too</p>
    </header>
    <p>Another draggable card.</p>
  </article>
</div>

<script src="oat.min.js" defer></script>
<script src="dragmove.min.js" defer></script>
<script>
document.querySelectorAll('.draggable-card').forEach(card => {
  new DragMove(card, {
    onDragStart: () => {
      card.style.boxShadow = '0 10px 40px rgba(0,0,0,0.2)';
      card.style.transform = 'scale(1.02)';
    },
    
    onDragEnd: () => {
      card.style.boxShadow = '';
      card.style.transform = '';
    }
  });
});
</script>

<style>
.draggable-card {
  transition: box-shadow 0.2s, transform 0.2s;
}
</style>
```

## Draggable Dialog/Modal

```html
<dialog id="draggable-dialog" style="width: 500px;">
  <div class="drag-handle" style="padding: 12px; cursor: move; user-select: none;">
    <h3 style="margin: 0;">Draggable Dialog</h3>
  </div>
  
  <div style="padding: 16px;">
    <p>You can drag this dialog by its header!</p>
  </div>
  
  <footer style="padding: 12px; text-align: right; border-top: 1px solid #eee;">
    <button onclick="this.closest('dialog').close()">Close</button>
  </footer>
</dialog>

<button onclick="document.getElementById('draggable-dialog').showModal()">
  Open Draggable Dialog
</button>

<script>
const dialog = document.getElementById('draggable-dialog');

// Make draggable after opening
dialog.addEventListener('showmodal', () => {
  new DragMove(dialog, {
    handle: '.drag-handle'
  });
});
</script>
```

## Draggable Sidebar Widget

```html
<aside data-sidebar>
  <div class="widget" style="margin-bottom: 16px; cursor: move;">
    <div class="widget-header" style="padding: 8px; background: #f5f5f5; cursor: grab;">
      ⚙️ Widget Settings
    </div>
    <div style="padding: 12px;">
      Widget content...
    </div>
  </div>
  
  <div class="widget" style="margin-bottom: 16px; cursor: move;">
    <div class="widget-header" style="padding: 8px; background: #f5f5f5; cursor: grab;">
      📊 Statistics
    </div>
    <div style="padding: 12px;">
      Stats content...
    </div>
  </div>
</aside>

<script>
document.querySelectorAll('.widget').forEach(widget => {
  new DragMove(widget, {
    handle: '.widget-header',
    container: widget.closest('aside')
  });
});
</script>
```

## Position Persistence

```javascript
const dm = new DragMove('#draggable', {
  onDragEnd: (e, x, y) => {
    // Save position
    localStorage.setItem('draggable-position', JSON.stringify({ x, y }));
  }
});

// Restore position on load
const saved = localStorage.getItem('draggable-position');
if (saved) {
  const { x, y } = JSON.parse(saved);
  const el = document.getElementById('draggable');
  el.style.left = x + 'px';
  el.style.top = y + 'px';
}
```

## Multiple Drag Modes

```javascript
// Free drag
const freeDrag = new DragMove('#free');

// Constrained to container
const constrained = new DragMove('#constrained', {
  container: '#container'
});

// Snap to grid
const snapDrag = new DragMove('#snapped', {
  snap: 50
});

// With handle only
const handleDrag = new DragMove('#handle-only', {
  handle: '.handle'
});
```

## Styling Tips

```css
/* Visual feedback during drag */
.dragging {
  opacity: 0.8;
  cursor: grabbing;
}

/* Handle styling */
.drag-handle {
  cursor: grab;
  user-select: none;
  -webkit-user-select: none;
}

.drag-handle:active {
  cursor: grabbing;
}

/* Drop zone indication */
.drop-zone {
  border: 2px dashed var(--primary);
  background: var(--primary)10;
}
```

## Browser Support

- All modern browsers
- Touch support built-in
- No polyfills needed

## Tips

1. Use `cursor: move` or `cursor: grab` for visual feedback
2. Add visual indicators during drag (shadow, scale)
3. Constrain dragging to prevent losing elements
4. Save positions if layout persistence is needed
5. Consider touch devices for mobile support

Perfect for draggable widgets, customizable layouts, sortable items, or any UI where users need to reposition elements!
