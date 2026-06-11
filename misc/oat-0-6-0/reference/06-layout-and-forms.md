# Layout and Forms

## Grid System

A 12-column responsive grid using CSS Grid. Uses `--grid-cols`, `--grid-gap`, and `--container-max` variables for customization.

### Structure

```html
<div class="container">
  <div class="row">
    <div class="col-4">Column 1 (4/12)</div>
    <div class="col-4">Column 2 (4/12)</div>
    <div class="col-4">Column 3 (4/12)</div>
  </div>
</div>
```

### Classes

| Class | Purpose |
|-------|---------|
| `.container` | Max-width wrapper (default 1280px), centered, padded |
| `.row` | CSS grid container with 12 columns and gap |
| `.col-{n}` | Span n columns (1-12) |
| `.offset-{n}` | Offset by n columns (1-6) |
| `.col-end` | Stretch column to end of row |

### Examples

```html
<div class="container">
  <div class="row">
    <!-- Equal thirds -->
    <div class="col-4">A</div>
    <div class="col-4">B</div>
    <div class="col-4">C</div>
  </div>

  <!-- Half and half -->
  <div class="row">
    <div class="col-6">Left</div>
    <div class="col-6">Right</div>
  </div>

  <!-- With offset -->
  <div class="row">
    <div class="col-4 offset-2">Centered block</div>
    <div class="col-4">Right block</div>
  </div>

  <!-- col-end stretches to fill remaining space -->
  <div class="row">
    <div class="col-3">Sidebar</div>
    <div class="col-4 col-end">Main content fills rest</div>
  </div>
</div>
```

### Responsive Behavior

At `max-width: 768px`, the grid collapses to 4 columns and all `.col-{n}` classes span all 4 columns (full width). Offsets are disabled on mobile.

### Customization

Override grid variables:

```css
:root {
  --grid-cols: 12;
  --grid-gap: 1.5rem;
  --container-max: 1280px;
  --container-pad: 1rem;
}
```

---

## Form Elements

All form elements are styled automatically when wrapped in `<label>` or `[data-field]`.

### Basic Inputs

```html
<form>
  <label data-field>
    Name
    <input type="text" placeholder="Enter your name" />
  </label>

  <label data-field>
    Email
    <input type="email" placeholder="you@example.com" />
  </label>

  <label data-field>
    Password
    <input type="password" placeholder="Password" aria-describedby="hint" />
    <small id="hint" data-hint>Must be at least 8 characters</small>
  </label>
</form>
```

**Styling**: Full width, `--text-7` font size, `--input` border, rounded corners. Focus ring uses `--ring` color with 2px box-shadow. Placeholder in `--muted-foreground`.

### Select

```html
<div data-field>
  <label>Select option</label>
  <select aria-label="Choose an option">
    <option value="">Select...</option>
    <option value="a">Option A</option>
    <option value="b">Option B</option>
  </select>
</div>
```

Custom chevron icon via background-image. No native appearance.

### Textarea

```html
<label data-field>
  Message
  <textarea placeholder="Your message..."></textarea>
</label>
```

Auto height with min-height 5rem, vertical resize, extra padding.

### Checkbox and Radio

```html
<label data-field>
  <input type="checkbox" /> I agree to the terms
</label>

<fieldset class="hstack">
  <legend>Preference</legend>
  <label><input type="radio" name="pref"> Option A</label>
  <label><input type="radio" name="pref"> Option B</label>
  <label><input type="radio" name="pref"> Option C</label>
</fieldset>
```

Custom styled with `appearance: none`. Checkbox has checkmark via CSS mask. Radio has filled circle via CSS mask. Labels with checkbox/radio inputs display as inline-flex with gap.

### Range Slider

```html
<label data-field>
  Volume
  <input type="range" min="0" max="100" value="50" />
</label>
```

Custom styled thumb (circle, primary color) and track (muted background). Hover scales thumb to 1.1x.

### File Input

```html
<label data-field>
  File
  <input type="file" />
</label>
```

`::file-selector-button` styled with transparent background and border.

### Date/Time Inputs

```html
<label data-field>
  Date
  <input type="date" />
</label>
<label data-field>
  DateTime
  <input type="datetime-local" />
</label>
```

Styled as standard text inputs with native date picker.

### Disabled Inputs

```html
<label data-field>
  Disabled
  <input type="text" placeholder="Cannot edit" disabled />
</label>
```

Muted background, 50% opacity (inherited from `:disabled` base style).

---

## Input Groups

Combine inputs with buttons or labels using `fieldset.group`:

```html
<fieldset class="group">
  <legend>https://</legend>
  <input type="url" placeholder="subdomain">
  <select aria-label="Domain">
    <option>.example.com</option>
    <option>.example.net</option>
  </select>
  <button>Go</button>
</fieldset>

<fieldset class="group">
  <input type="text" placeholder="Search" />
  <button>Go</button>
</fieldset>
```

Inputs stretch to fill available space. First/last child get outer border radius, middle elements have no radius. Legend floats inline with muted styling.

---

## Validation Errors

Use `data-field="error"` to reveal error messages:

```html
<div data-field="error">
  <label for="email-input">Email</label>
  <input type="email" id="email-input" aria-invalid="true"
         aria-describedby="email-error" value="invalid" />
  <div id="email-error" class="error" role="status">
    Please enter a valid email address.
  </div>
</div>
```

**Behavior**: `.error` is hidden by default inside `[data-field]`. When `data-field="error"`, the error div becomes visible with `--danger` color. Input with `aria-invalid="true"` or `:user-invalid` gets red border and red focus ring.

---

## Field Containers

The `[data-field]` attribute marks a field container:

```html
<label data-field>
  Label text
  <input type="text" />
</label>

<div data-field>
  <label>Label</label>
  <input type="text" />
  <small data-hint>Help text</small>
</div>
```

**Behavior**: Adds bottom margin (space-4). `[data-hint]` children get small muted text styling. `.error` children are hidden unless `data-field="error"`.

---

## Sidebar Layout

Responsive admin dashboard layout with sticky sidebar, optional topnav, and collapsible sections.

### Basic Sidebar

```html
<div data-sidebar-layout>
  <aside data-sidebar>
    <nav>
      <ul>
        <li><a href="#" aria-current="page">Home</a></li>
        <li><a href="#">Users</a></li>
        <li>
          <details open>
            <summary>Settings</summary>
            <ul>
              <li><a href="#">General</a></li>
              <li><a href="#">Security</a></li>
            </ul>
          </details>
        </li>
      </ul>
    </nav>
    <footer>
      <button class="outline" style="width: 100%;">Logout</button>
    </footer>
  </aside>
  <main>
    <div style="padding: var(--space-3)">Main content area.</div>
  </main>
</div>
```

### With Top Navigation

```html
<body data-sidebar-layout>
  <nav data-topnav>
    <button data-sidebar-toggle aria-label="Toggle menu" class="outline">&#9776;</button>
    <span>App Name</span>
  </nav>

  <aside data-sidebar>
    <header>Logo</header>
    <nav>...navigation...</nav>
    <footer>Actions</footer>
  </aside>

  <main>Main page content.</main>
</body>
```

### Always-Collapsible

Set `data-sidebar-layout="always"` to keep the toggle visible at all screen sizes:

```html
<body data-sidebar-layout="always">
```

### Attributes Reference

| Attribute | Element | Purpose |
|-----------|---------|---------|
| `data-sidebar-layout` | Container (e.g., `<body>`) | Enables grid layout with sidebar + main |
| `data-sidebar-layout="always"` | Container | Always-collapsible mode (toggle visible at all widths) |
| `data-topnav` | `<nav>` or `<header>` | Full-width sticky top navigation bar |
| `data-sidebar` | `<aside>` | Sticky sidebar panel |
| `data-sidebar-toggle` | `<button>` | Toggle button for sidebar |
| `data-sidebar-open` | Layout container | Applied/removed to show/hide sidebar (managed by JS) |

### Responsive Behavior

- **Desktop (>768px)**: Sidebar is always visible, sticky alongside main content
- **Mobile (&le;768px)**: Sidebar becomes a slide-out overlay. Toggle button appears. Clicking outside sidebar dismisses it
- **"always" mode on desktop**: Toggle collapses sidebar with animation (translateX + opacity). Main content fills full width

### Sidebar Structure

The sidebar supports `<header>`, `<nav>`, and `<footer>` children:
- `<header>`: Fixed at top, padded
- `<nav>`: Flex-grow, scrollable if content overflows. Contains `<ul>` with links and collapsible `<details>` sections
- `<footer>`: Pushed to bottom via `margin-block-start: auto`
