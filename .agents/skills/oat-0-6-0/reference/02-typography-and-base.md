# Typography and Base Styles

## CSS Cascade Layers

OAT uses CSS `@layer` to organize styles into a predictable cascade order. The layer declaration at the top of `00-base.css`:

```css
@layer theme, base, components, animations, utilities;
```

This defines 5 layers in specificity order (earlier = lower priority):

| Layer | Purpose | Source Files |
|-------|---------|-------------|
| `theme` | CSS variable definitions (`:root`) | `01-theme.css` |
| `base` | Reset, typography, form elements, progress/meter | `00-base.css`, `button.css`, `form.css`, `progress.css`, `table.css` |
| `components` | Component-specific styles (cards, dialogs, etc.) | All component CSS files |
| `animations` | Keyframe animations, transitions, `@starting-style` | `animations.css` |
| `utilities` | Helper classes (flexbox, margins, alignment) | `utilities.css` |

User custom CSS without `@layer` always wins over all OAT layers. To override within a layer, use the same `@layer` declaration.

## Base Reset and Defaults

OAT's base layer (`00-base.css`) provides:

- **Box-sizing**: `border-box` on all elements including pseudo-elements
- **Margin reset**: All margins zeroed (re-applied selectively per element)
- **Tap highlight**: `-webkit-tap-highlight-color: transparent`
- **Font smoothing**: `-webkit-font-smoothing: antialiased`
- **Media max-width**: `img, picture, video, canvas, svg` constrained to `max-width: 100%`
- **Text overflow**: `overflow-wrap: break-word` on headings and paragraphs
- **Focus visible**: 2px solid outline using `--ring` color with 2px offset
- **Disabled state**: `opacity: 0.5` and `cursor: not-allowed`
- **Hidden elements**: `[hidden] { display: none }`

## Typography

All headings (h1-h6) are styled automatically with responsive font sizes using `clamp()`:

| Element | CSS Variable | Size Range | Margin Top/Bottom |
|---------|-------------|------------|-------------------|
| `<h1>` | `--text-1` | 1.75rem → 2.25rem (fluid) | space-10 / space-6 |
| `<h2>` | `--text-2` | 1.5rem → 1.875rem (fluid) | space-8 / space-5 |
| `<h3>` | `--text-3` | 1.25rem → 1.5rem (fluid) | space-6 / space-4 |
| `<h4>` | `--text-4` | 1.125rem → 1.25rem (fluid) | space-5 / space-3 |
| `<h5>` | `--text-5` | 1.125rem (fixed) | space-4 / space-2 |
| `<h6>` | `--text-regular` (= --text-6) | 1rem (fixed) | space-4 / space-2 |

All headings share: `font-weight: var(--font-semibold)` (600), `line-height: 1.25`. First child heading has zero top margin.

### Paragraphs

```html
<p>This paragraph has bottom margin of --space-4.</p>
```

Last-child paragraphs have zero bottom margin.

### Inline Text Elements

| Element | Styling |
|---------|---------|
| `<a>` | `--primary` color, underlined with 2px offset, hover dims to 80% opacity |
| `<strong>`, `<b>` | `font-weight: var(--font-semibold)` (600) |
| `<em>`, `<i>` | `font-style: italic` |
| `<small>` | `font-size: var(--text-7)` (0.875rem) |
| `<mark>` | Semi-transparent `--warning` background, rounded padding |

### Code

```html
<code>Inline code</code>
```

Styled with `--font-mono`, reduced font size (0.875em), `--faint` background, small rounded padding.

```html
<pre><code>Code block with syntax</code></pre>
```

Block code: padded container with `--faint` background, medium border radius, horizontal scroll overflow. Inner `<code>` loses its own padding/background.

### Blockquote

```html
<blockquote>This is a styled quote.</blockquote>
```

Left border (4px solid `--border`), left padding, muted foreground color, italic font style.

### Horizontal Rule

```html
<hr>
```

Top border only (1px solid `--border`), generous vertical margin (space-8).

### Lists

```html
<ul>
  <li>Unordered list item</li>
</ul>
<ol>
  <li>Ordered list item</li>
</ol>
```

- `<ul>`: disc list style, left padding space-6
- `<ol>`: decimal list style, left padding space-6
- `<li>`: bottom margin space-1

### Main element

```html
<main>Content starts here</main>
```

Has top padding of `--space-8` (2rem) by default.
