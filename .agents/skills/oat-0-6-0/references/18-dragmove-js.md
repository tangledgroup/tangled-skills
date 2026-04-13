# DragMove.js - Draggable DOM Elements

A super tiny (~500 bytes minified+gzipped), zero-dependency JavaScript library to make DOM elements draggable and movable. Includes touch screen support for mobile devices.

[**View Demo**](https://knadh.github.io/dragmove.js/docs/) | [**GitHub**](https://github.com/knadh/dragmove.js)

## Features

- Make any DOM element draggable
- Touch screen support for mobile devices
- Zero dependencies, ~500 bytes minified+gzipped
- Optional start/end callbacks for custom behavior
- Simple API with minimal configuration

## Installation

### npm

```bash
npm install @knadh/dragmove
```

### ES Module (CDN)

```html
<script type="module">
  import { dragmove } from 'https://unpkg.com/@knadh/dragmove';
</script>
```

## Basic Usage

### Simple Draggable Element

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>DragMove Demo</title>
  <style>
    .draggable {
      position: absolute;
      top: 100px;
      left: 100px;
      width: 200px;
      height: 150px;
      background: #4a90d9;
      border-radius: 8px;
      padding: 20px;
      color: white;
      cursor: move;
      user-select: none;
    }
    
    .drag-handle {
      padding: 10px;
      background: rgba(255,255,255,0.2);
      border-radius: 4px;
      cursor: grab;
      text-align: center;
    }
    
    .drag-handle:active {
      cursor: grabbing;
    }
  </style>
</head>
<body>
  <div id="box" class="draggable">
    <div class="drag-handle">Drag me!</div>
    <p style="margin-top: 15px;">This entire box is draggable from the handle above.</p>
  </div>
  
  <script type="module">
    import { dragmove } from 'https://unpkg.com/@knadh/dragmove';
    
    // Make the box draggable using the handle
    const box = document.querySelector('#box');
    const handle = document.querySelector('#box .drag-handle');
    
    dragmove(box, handle);
  </script>
</body>
</html>
```

### Drag Entire Element (No Handle)

```html
<div id="widget" style="position: absolute; width: 200px; height: 150px; background: #4a90d9;">
  <h3>Draggable Widget</h3>
  <p>Click anywhere to drag</p>
</div>

<script type="module">
  import { dragmove } from '@knadh/dragmove';
  
  // Make entire element draggable (no separate handle)
  const widget = document.querySelector('#widget');
  dragmove(widget, widget);
</script>
```

## Advanced Usage

### Start and End Callbacks

Use callbacks to add custom behavior when dragging starts and ends:

```javascript
import { dragmove } from '@knadh/dragmove';

const box = document.querySelector('#box');
const handle = document.querySelector('#box .handle');

function onStart(element, x, y) {
  console.log('Drag started at:', x, y);
  
  // Store original position or add visual feedback
  element.classList.add('dragging');
  element.style.opacity = '0.8';
}

function onEnd(element, x, y) {
  console.log('Drag ended at:', x, y);
  
  // Remove visual feedback
  element.classList.remove('dragging');
  element.style.opacity = '1';
  
  // Save new position
  localStorage.setItem('box-position', 
    JSON.stringify({ left: element.offsetLeft, top: element.offsetTop })
  );
}

// Initialize with callbacks
dragmove(box, handle, onStart, onEnd);
```

### Snap to Edges on Drop

```javascript
const snapThreshold = 50; // Pixels from edge to trigger snap

function onStart(el, x, y) {
  // Store original positioning method
  el._originalTop = el.style.top;
  el._originalLeft = el.style.left;
  
  // Ensure we're using top/left for dragging
  el.style.top = el.offsetTop + 'px';
  el.style.left = el.offsetLeft + 'px';
  el.style.bottom = 'auto';
  el.style.right = 'auto';
}

function onEnd(el, x, y) {
  const windowWidth = window.innerWidth;
  const windowHeight = window.innerHeight;
  const elWidth = el.offsetWidth;
  const elHeight = el.offsetHeight;
  
  // Snap to top
  if (el.offsetTop < snapThreshold) {
    el.style.top = '0px';
  }
  
  // Snap to bottom
  if (windowHeight - (el.offsetTop + elHeight) < snapThreshold) {
    el.style.top = 'auto';
    el.style.bottom = '0px';
  }
  
  // Snap to left
  if (el.offsetLeft < snapThreshold) {
    el.style.left = '0px';
  }
  
  // Snap to right
  if (windowWidth - (el.offsetLeft + elWidth) < snapThreshold) {
    el.style.left = 'auto';
    el.style.right = '0px';
  }
  
  // Snap to center
  const centerX = windowWidth / 2 - elWidth / 2;
  const centerY = windowHeight / 2 - elHeight / 2;
  const distToCenter = Math.hypot(
    el.offsetLeft - centerX,
    el.offsetTop - centerY
  );
  
  if (distToCenter < snapThreshold) {
    el.style.left = centerX + 'px';
    el.style.top = centerY + 'px';
  }
}

dragmove(box, handle, onStart, onEnd);
```

### Drag Boundary Constraint

Constrain dragging within a parent container:

```javascript
function onEnd(el, x, y) {
  const parent = el.parentElement;
  const parentRect = parent.getBoundingClientRect();
  const elRect = el.getBoundingClientRect();
  
  // Constrain within parent boundaries
  if (elRect.left < parentRect.left) {
    el.style.left = (parentRect.left - elRect.left) + el.offsetLeft + 'px';
  }
  
  if (elRect.top < parentRect.top) {
    el.style.top = (parentRect.top - elRect.top) + el.offsetTop + 'px';
  }
  
  if (elRect.right > parentRect.right) {
    el.style.left = (parentRect.right - elRect.right) + el.offsetLeft + 'px';
  }
  
  if (elRect.bottom > parentRect.bottom) {
    el.style.top = (parentRect.bottom - elRect.bottom) + el.offsetTop + 'px';
  }
}

dragmove(box, handle, null, onEnd);
```

### Multiple Draggable Elements

```javascript
import { dragmove } from '@knadh/dragmove';

// Make multiple elements draggable
document.querySelectorAll('.draggable').forEach(element => {
  const handle = element.querySelector('.handle') || element;
  dragmove(element, handle);
});

// Or with specific pairs
const widgets = [
  { el: '#widget1', handle: '#widget1 .title' },
  { el: '#widget2', handle: '#widget2 .header' },
  { el: '#widget3', handle: '#widget3' } // Entire element
];

widgets.forEach(({ el, handle }) => {
  dragmove(document.querySelector(el), document.querySelector(handle));
});
```

### Restore Saved Position

```javascript
import { dragmove } from '@knadh/dragmove';

const box = document.querySelector('#box');
const handle = document.querySelector('#box .handle');

// Load saved position
const savedPos = localStorage.getItem('box-position');
if (savedPos) {
  const { left, top } = JSON.parse(savedPos);
  box.style.left = left + 'px';
  box.style.top = top + 'px';
}

// Save position on drag end
function onEnd(el, x, y) {
  localStorage.setItem('box-position', JSON.stringify({
    left: el.offsetLeft,
    top: el.offsetTop
  }));
}

dragmove(box, handle, null, onEnd);
```

## Styling

### Basic Styles for Draggable Elements

```css
/* Draggable container */
.draggable {
  position: absolute; /* Required for dragging */
  user-select: none;  /* Prevent text selection while dragging */
  touch-action: none; /* Prevent browser gestures on mobile */
}

/* Drag handle */
.drag-handle {
  cursor: grab;
  padding: 10px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  user-select: none;
}

.drag-handle:active {
  cursor: grabbing;
  background: rgba(0, 0, 0, 0.2);
}

/* Visual feedback during drag */
.draggable.dragging {
  opacity: 0.8;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  transform: scale(1.02);
  transition: none; /* Remove transitions for smooth dragging */
}

/* Reset after drag */
.draggable:not(.dragging) {
  transition: box-shadow 0.2s, transform 0.2s;
}
```

### Integration with Oat UI

```css
/* Use Oat's design system */
.draggable {
  position: absolute;
  background: var(--card-background, var(--background));
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  color: var(--text-color);
  user-select: none;
  touch-action: none;
}

.drag-handle {
  cursor: grab;
  padding: var(--space-2) var(--space-3);
  background: var(--hover-background);
  border-bottom: 1px solid var(--border-color);
  font-weight: 500;
  user-select: none;
}

.drag-handle:active {
  cursor: grabbing;
  background: var(--active-background);
}

.draggable.dragging {
  opacity: 0.9;
  box-shadow: var(--shadow-lg);
  z-index: 1000;
}
```

## Real-World Example: Dashboard Widgets

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Draggable Dashboard</title>
  <link rel="stylesheet" href="oat.min.css">
  
  <style>
    .dashboard {
      position: relative;
      width: 100vw;
      height: 100vh;
      background: var(--background);
    }
    
    .widget {
      position: absolute;
      min-width: 250px;
      background: var(--card-background);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-md);
      user-select: none;
      touch-action: none;
    }
    
    .widget-header {
      padding: var(--space-3);
      background: var(--primary);
      color: var(--primary-foreground);
      border-radius: var(--radius-md) var(--radius-md) 0 0;
      cursor: grab;
      font-weight: 600;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .widget-header:active {
      cursor: grabbing;
    }
    
    .widget-content {
      padding: var(--space-3);
    }
    
    .widget.dragging {
      opacity: 0.9;
      box-shadow: var(--shadow-xl);
      z-index: 1000;
    }
  </style>
</head>
<body>
  <div class="dashboard" id="dashboard">
    <div class="widget" id="widget1" style="top: 20px; left: 20px; width: 300px;">
      <div class="widget-header">
        <span>📊 Statistics</span>
      </div>
      <div class="widget-content">
        <p>User stats and analytics</p>
      </div>
    </div>
    
    <div class="widget" id="widget2" style="top: 20px; left: 340px; width: 280px;">
      <div class="widget-header">
        <span>📝 Recent Activity</span>
      </div>
      <div class="widget-content">
        <p>Latest user actions</p>
      </div>
    </div>
    
    <div class="widget" id="widget3" style="top: 350px; left: 20px; width: 320px;">
      <div class="widget-header">
        <span>⚙️ Settings</span>
      </div>
      <div class="widget-content">
        <p>Configuration options</p>
      </div>
    </div>
  </div>
  
  <script src="oat.min.js" defer></script>
  <script type="module">
    import { dragmove } from 'https://unpkg.com/@knadh/dragmove';
    
    // Initialize all widgets as draggable
    document.querySelectorAll('.widget').forEach(widget => {
      const header = widget.querySelector('.widget-header');
      
      function onStart(el) {
        el.classList.add('dragging');
      }
      
      function onEnd(el) {
        el.classList.remove('dragging');
        
        // Save position
        const positions = JSON.parse(localStorage.getItem('widget-positions') || '{}');
        positions[el.id] = {
          top: el.offsetTop,
          left: el.offsetLeft
        };
        localStorage.setItem('widget-positions', JSON.stringify(positions));
      }
      
      dragmove(widget, header, onStart, onEnd);
    });
    
    // Load saved positions
    const positions = JSON.parse(localStorage.getItem('widget-positions') || '{}');
    Object.keys(positions).forEach(widgetId => {
      const widget = document.querySelector(`#${widgetId}`);
      if (widget && positions[widgetId]) {
        widget.style.top = positions[widgetId].top + 'px';
        widget.style.left = positions[widgetId].left + 'px';
      }
    });
  </script>
</body>
</html>
```

## Touch Support

DragMove automatically supports touch events for mobile devices:

```javascript
// No special configuration needed - touch works out of the box!
dragmove(element, handle);
```

The library handles:
- `touchstart`, `touchmove`, `touchend` events
- Multi-touch prevention
- Smooth dragging on mobile devices

## API Reference

```javascript
dragmove(target, handler, onStart, onEnd)
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `target` | Element | Yes | The element to be dragged |
| `handler` | Element | Yes | The element that initiates dragging (can be same as target) |
| `onStart` | Function | No | Callback when dragging starts: `(element, x, y) => void` |
| `onEnd` | Function | No | Callback when dragging ends: `(element, x, y) => void` |

### Callback Parameters

Both `onStart` and `onEnd` receive:
- `element`: The target element being dragged
- `x`: X coordinate of the mouse/touch event
- `y`: Y coordinate of the mouse/touch event

## Browser Support

- All modern browsers
- Chrome, Firefox, Safari, Edge
- Mobile browsers with touch support
- IE11+ (with limitations)

## Tips and Best Practices

### DO

- Use `position: absolute` or `position: fixed` on draggable elements
- Add visual feedback during drag (opacity, shadow, scale)
- Save positions to localStorage for persistence
- Use separate handles for better UX on content-rich widgets
- Constrain dragging within parent boundaries if needed

### DON'T

- Forget to set `position: absolute` on target elements
- Use CSS transitions during drag (causes lag)
- Make entire content-area draggable (use a handle instead)
- Forget about mobile touch support (it's built-in!)

## Limitations

- No built-in collision detection
- No built-in snap-to-grid (implement in callbacks)
- No z-index management (handle manually)
- Single drag at a time (no multi-element drag)

## Related Libraries

- **tinyrouter.js**: Client-side routing
- **highlighted-input.js**: Keyword highlighting in inputs
- **floatype.js**: Floating autocomplete for textareas

Licensed under the MIT License.
