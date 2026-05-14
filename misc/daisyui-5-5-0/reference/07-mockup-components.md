# Mockup Components

## Browser

Renders a box that looks like a browser window with title bar and URL field.

### Class Names

- **component**: `mockup-browser`
- **part**: `mockup-browser-toolbar`

### Syntax

```html
<div class="mockup-browser bg-base-300">
  <div class="mockup-browser-toolbar">
    <div class="input">https://example.com</div>
  </div>
  <div class="flex items-center justify-center bg-base-100" style="height: 14rem;">
    Page content here
  </div>
</div>
```

## Code

Renders a box that looks like a code editor with line numbers and prefixes.

### Class Names

- **component**: `mockup-code`

### Syntax

```html
<div class="mockup-code">
  <pre data-prefix="$"><code>npm i daisyui</code></pre>
  <pre data-prefix=">"><code>open index.html</code></pre>
  <pre data-prefix=""><code class="text-success">Server started → http://localhost:3000</code></pre>
</div>
```

### Rules

- Use `<pre data-prefix="{char}">` to show a prefix before each line
- Add `<code>` for syntax highlighting (requires external library)
- Apply background/text color classes to highlight specific lines

## Phone

Renders an iPhone-style phone mockup.

### Class Names

- **component**: `mockup-phone`
- **part**: `mockup-phone-camera`, `mockup-phone-display`

### Syntax

```html
<div class="mockup-phone">
  <div class="mockup-phone-camera"></div>
  <div class="mockup-phone-display">
    <div class="flex items-center justify-center" style="height: 100%;">
      App content here
    </div>
  </div>
</div>
```

### Rules

- Anything can be placed inside `mockup-phone-display`

## Window

Renders a box that looks like an operating system window with title bar and close button.

### Class Names

- **component**: `mockup-window`

### Syntax

```html
<div class="mockup-window bg-base-300">
  <div class="flex items-center justify-center" style="height: 14rem;">
    Window content here
  </div>
</div>
```
