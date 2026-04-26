# Layout System

## Container

Pico provides two container classes for controlling content width.

**`.container`** — centered fixed-width container:
```html
<main class="container">
  <h1>Centered content</h1>
</main>
```

**`.container-fluid`** — full-width with horizontal padding:
```html
<main class="container-fluid">
  <h1>Fluid content</h1>
</main>
```

## Breakpoints and Viewport Widths

| Device | Breakpoint | Container Width |
|--------|-----------|-----------------|
| Extra small | &lt;576px | 100% |
| Small | ≥576px | 510px |
| Medium | ≥768px | 700px |
| Large | ≥1024px | 950px |
| Extra large | ≥1280px | 1200px |
| Extra extra large | ≥1536px | 1450px |

Breakpoints are customizable via Sass `$breakpoints`.

## Grid

The `.grid` class creates a responsive auto-fit grid using CSS Grid:

```html
<div class="grid">
  <div>Column 1</div>
  <div>Column 2</div>
  <div>Column 3</div>
  <div>Column 4</div>
</div>
```

Grid items auto-fit and wrap based on available width. No explicit column counts needed — the grid adapts to container size.

## Landmarks and Sections

Pico styles semantic landmark elements:
- `<header>` — page or section header
- `<main>` — primary content area
- `<footer>` — page or section footer
- `<section>` — thematic grouping
- `<article>` — self-contained content block

When `$enable-responsive-spacings` is enabled in Sass, these elements get responsive padding that scales with viewport width.

## Overflow Auto

The `.overflow-auto` class (new in v2) provides scrollable containers:

```html
<div class="overflow-auto">
  <table>
    <!-- wide table content -->
  </table>
</div>
```

Useful for wrapping tables or wide content that needs horizontal scrolling on small screens.

## RTL Support

Pico supports right-to-left layouts. Use the `dir="rtl"` attribute on `<html>`:

```html
<html lang="ar" dir="rtl">
```

All spacing, text alignment, and layout directions automatically adapt for RTL.
