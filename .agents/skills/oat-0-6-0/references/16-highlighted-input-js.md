# Highlighted-Input.js - Keyword Highlighting in Input Fields

A super tiny (~450 bytes minified+gzipped), zero-dependency JavaScript library that highlights specific keywords and tags in an `<input>` field. Ideal for search inputs to highlight field selectors as users type.

[**View Demo**](https://knadh.github.io/highlighted-input.js) | [**GitHub**](https://github.com/knadh/highlighted-input.js)

## Features

- Highlight specific keywords and patterns in real-time
- Zero dependencies, ~450 bytes minified+gzipped
- CSS-based highlighting with custom classnames
- Works with any input field
- Perfect for search queries, command interfaces, and tagging

## How It Works

The library uses a clever overlay technique:
1. Creates a hidden layer that mirrors the input content
2. Applies CSS classes to matched keywords in the layer
3. The input text is transparent, showing the highlighted layer beneath

## Installation

### npm

```bash
npm install @knadh/highlighted-input
```

### ES Module (CDN)

```html
<script type="module">
  import { highlightedInput } from 'https://unpkg.com/@knadh/highlighted-input';
</script>
```

## Basic Usage

### Setup with Keyword Map

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Highlighted Input Demo</title>
  <!-- Include the CSS styles -->
  <link rel="stylesheet" href="highlighted-input.css">
</head>
<body>
  <input type="text" id="search-input" placeholder="Try: lang:javascript repo:oat user:knadh AND..." />
  
  <script type="module">
    import { highlightedInput } from 'https://unpkg.com/@knadh/highlighted-input';
    
    const input = document.getElementById("search-input");
    
    // Define CSS class names for different highlight levels
    const h1 = "highlighted-h1";  // Primary highlights (blue)
    const h2 = "highlighted-h2";  // Secondary highlights (orange)
    
    // Map keywords to their corresponding CSS classes
    const keywordMap = {
      "lang:": h1,   // Highlight "lang:" with primary style
      "repo:": h1,   // Highlight "repo:" with primary style
      "user:": h1,   // Highlight "user:" with primary style
      "AND": h2,     // Highlight "AND" with secondary style
      "OR": h2,      // Highlight "OR" with secondary style
      "NOT": h2      // Highlight "NOT" with secondary style
    };
    
    // Initialize the highlighter
    highlightedInput(input, keywordMap);
  </script>
</body>
</html>
```

### Required CSS Styles

Copy these styles from the library's `style.css` and customize as needed:

```css
/* Highlighted input component styles */
.highlighted-wrap {
    position: relative;
    margin: 1rem 0;
}

.highlighted-input,
.highlighted-layer {
    width: 100%;
    padding: 1rem;
    font-size: 1.3rem;
    font-family: inherit;
    color: #444;
    max-width: 100%;
    top: 0;
    left: 0;
    box-sizing: border-box;
    height: 100%;
    overflow: auto;
    white-space: pre;
    word-wrap: normal;
    overflow-wrap: normal;
}

.highlighted-input {
    background: transparent;
    color: transparent;  /* Input text is transparent */
    caret-color: #111;   /* But cursor is visible */
    border: 1px solid #ccc;
    border-radius: 4px;
    position: relative;
    z-index: 2;          /* Input on top for events */
    resize: none;
}

.highlighted-input:focus {
    outline: none;
    border-color: #0066cc;
}

.highlighted-layer {
    background-color: #fff;
    position: absolute;
    pointer-events: none;  /* Clicks pass through to input */
    z-index: 1;            /* Layer beneath input */
    border: 1px solid transparent;
    border-radius: 4px;
}

/* Primary highlight style (blue) */
.highlighted-h1 {
    color: #0066cc;
    background: #e6f2ff;
    border-radius: 2px;
    padding: 1px 3px;
}

/* Secondary highlight style (orange) */
.highlighted-h2 {
    color: #cc6600;
    background: #fff2e6;
    border-radius: 2px;
    padding: 1px 3px;
}
```

## Advanced Usage

### Custom Highlight Styles

```html
<style>
/* Custom mention style */
.mention {
    color: #0369a1;
    background: #dbeafe;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 500;
}

/* Custom tag style */
.tag {
    color: #92400e;
    background: #fef3c7;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 500;
}

/* Command keywords */
.command {
    color: #569cd6;
    background: #e8f4fd;
    padding: 1px 4px;
    border-radius: 3px;
    font-family: monospace;
}
</style>

<script type="module">
  import { highlightedInput } from '@knadh/highlighted-input';
  
  const input = document.getElementById("input");
  
  const keywordMap = {
    "@": "mention",      // Highlight anything starting with @
    "#": "tag",          // Highlight anything starting with #
    "help": "command",   // Highlight exact word "help"
    "exit": "command",   // Highlight exact word "exit"
    "quit": "command"    // Highlight exact word "quit"
  };
  
  highlightedInput(input, keywordMap);
</script>
```

### Search Query Interface

Perfect for advanced search interfaces with field selectors:

```javascript
const searchInput = document.getElementById("search");

const keywordMap = {
  // Field selectors (primary highlights)
  "author:": "highlight-field",
  "date:": "highlight-field",
  "type:": "highlight-field",
  "status:": "highlight-field",
  
  // Operators (secondary highlights)
  "AND": "highlight-op",
  "OR": "highlight-op",
  "NOT": "highlight-op",
  "(": "highlight-paren",
  ")": "highlight-paren"
};

highlightedInput(searchInput, keywordMap);
```

```css
.highlight-field {
    color: #0066cc;
    background: #e6f2ff;
    padding: 1px 3px;
    border-radius: 2px;
}

.highlight-op {
    color: #666;
    background: #f5f5f5;
    padding: 1px 3px;
    border-radius: 2px;
    font-weight: bold;
}

.highlight-paren {
    color: #999;
}
```

### Command Line Interface

```javascript
const commandInput = document.getElementById("command");

const keywordMap = {
  // Commands
  "ls": "cmd",
  "cd": "cmd",
  "mkdir": "cmd",
  "rm": "cmd",
  "cp": "cmd",
  "mv": "cmd",
  
  // Flags
  "-l": "flag",
  "-a": "flag",
  "-r": "flag",
  "--help": "flag",
  "--force": "flag"
};

highlightedInput(commandInput, keywordMap);
```

```css
.cmd {
    color: #00aa00;
    background: #e6ffe6;
    padding: 1px 4px;
    border-radius: 2px;
    font-family: monospace;
    font-weight: bold;
}

.flag {
    color: #aa00aa;
    background: #fce6fc;
    padding: 1px 4px;
    border-radius: 2px;
    font-family: monospace;
}
```

## Integration with Oat UI

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Oat + Highlighted Input</title>
  <link rel="stylesheet" href="oat.min.css">
  
  <style>
    /* Combine with Oat's design system */
    .highlighted-wrap {
      margin: var(--space-4) 0;
    }
    
    .highlighted-input,
    .highlighted-layer {
      padding: var(--space-3);
      font-size: 1rem;
      border-radius: var(--radius-md);
    }
    
    .highlighted-input {
      border-color: var(--border-color);
      caret-color: var(--text-color);
    }
    
    .highlighted-input:focus {
      border-color: var(--primary);
    }
    
    .highlighted-layer {
      background-color: var(--background);
      color: var(--text-color);
    }
    
    /* Oat-themed highlights */
    .oat-highlight-primary {
      color: var(--primary);
      background: color-mix(in srgb, var(--primary) 15%, transparent);
      padding: 1px 4px;
      border-radius: var(--radius-sm);
    }
    
    .oat-highlight-secondary {
      color: var(--secondary);
      background: color-mix(in srgb, var(--secondary) 15%, transparent);
      padding: 1px 4px;
      border-radius: var(--radius-sm);
    }
  </style>
</head>
<body>
  <div class="container" style="padding: var(--space-6); max-width: 800px;">
    <h1>Advanced Search</h1>
    
    <label data-field>
      Search Query
      <input 
        type="text" 
        id="search" 
        placeholder="Try: lang:javascript repo:oat user:knadh AND..."
        style="width: 100%;"
      />
      <small data-hint>Use field selectors like <code>lang:</code>, <code>repo:</code>, and operators <code>AND</code>, <code>OR</code>, <code>NOT</code></small>
    </label>
    
    <button type="button" class="primary">Search</button>
  </div>
  
  <script src="oat.min.js" defer></script>
  <script type="module">
    import { highlightedInput } from 'https://unpkg.com/@knadh/highlighted-input';
    
    const searchInput = document.getElementById("search");
    
    const keywordMap = {
      "lang:": "oat-highlight-primary",
      "repo:": "oat-highlight-primary",
      "user:": "oat-highlight-primary",
      "type:": "oat-highlight-primary",
      "AND": "oat-highlight-secondary",
      "OR": "oat-highlight-secondary",
      "NOT": "oat-highlight-secondary"
    };
    
    highlightedInput(searchInput, keywordMap);
  </script>
</body>
</html>
```

## Customization

### Font and Sizing

The highlighted layer must match the input's font properties exactly:

```css
.highlighted-input,
.highlighted-layer {
    /* These MUST match for proper alignment */
    font-size: 16px;
    font-family: 'Inter', sans-serif;
    font-weight: 400;
    line-height: 1.5;
    letter-spacing: normal;
    
    padding: 12px;
}
```

### Dark Mode Support

```css
@media (prefers-color-scheme: dark) {
    .highlighted-input {
        caret-color: #fff;
        border-color: #444;
    }
    
    .highlighted-layer {
        background-color: #1a1a1a;
        color: #ccc;
    }
    
    .highlighted-h1 {
        color: #66b3ff;
        background: #1a3a5c;
    }
    
    .highlighted-h2 {
        color: #ffb366;
        background: #3a2c1a;
    }
}
```

## Tips and Best Practices

### DO

- Ensure input and layer have identical font properties
- Use descriptive class names for different highlight types
- Include helpful placeholder text showing examples
- Add a hint explaining available keywords/operators
- Test with long queries to ensure scrolling works

### DON'T

- Change font properties on input without updating layer
- Use complex CSS that might break the overlay
- Forget to include the required CSS styles
- Expect it to work on `<textarea>` (use floatype.js instead)

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires CSS and JavaScript support
- Graceful degradation: input works normally without JS

## Related Libraries

- **floatype.js**: For floating autocomplete in textareas
- **autocomp.js**: For dropdown suggestions on inputs

## Limitations

- Works only with single-line `<input>` elements
- Not suitable for multi-line text areas
- Highlighting is visual only (doesn't affect submitted value)
- Requires matching font properties between input and layer

Licensed under the MIT License.
