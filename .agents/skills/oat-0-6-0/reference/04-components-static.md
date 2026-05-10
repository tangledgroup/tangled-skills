# Static Components (CSS-Only)

These components require only the OAT CSS — no JavaScript needed.

## Accordion

Uses native `<details>` and `<summary>`. No JS required.

```html
<details>
  <summary>Section title</summary>
  <p>Collapsible content here.</p>
</details>
```

**Grouped accordions** (only one open at a time): Add `name` attribute to group:

```html
<details name="faq">
  <summary>Question 1</summary>
  <p>Answer 1</p>
</details>
<details name="faq">
  <summary>Question 2</summary>
  <p>Answer 2</p>
</details>
```

**Styling**: Border with rounded corners, chevron indicator via `::after`, hover background on summary. Adjacent details share borders (no double border).

## Alert

Uses `role="alert"` with optional `data-variant`.

```html
<div role="alert">Default info alert</div>
<div role="alert" data-variant="success">Success message</div>
<div role="alert" data-variant="warning">Warning message</div>
<div role="alert" data-variant="error">Error message</div>
<div role="alert" data-variant="danger">Danger message</div>
```

**Variants**: `success`, `warning`, `error`/`danger`. Each applies themed color + tinted background. Default (no variant) has bordered neutral style.

## Avatar

Uses `<figure data-variant="avatar">` with image, text initials, or icons.

```html
<!-- Image avatar -->
<figure data-variant="avatar" aria-label="Jane Doe">
  <img src="photo.jpg" alt="" />
</figure>

<!-- Text initials -->
<figure data-variant="avatar" aria-label="Jane Doe">
  <abbr title="Jane Doe">JD</abbr>
</figure>

<!-- Sizes -->
<figure data-variant="avatar" class="small" aria-label="User">
  <img src="photo.jpg" alt="" />
</figure>
<figure data-variant="avatar" class="large" aria-label="User">
  <img src="photo.jpg" alt="" />
</figure>
```

**Sizes**: `.small` (2rem), default (2.5rem), `.large` (3.25rem).

### Avatar Group

```html
<figure data-variant="avatar" role="group" aria-label="Team">
  <figure data-variant="avatar" aria-label="User 1"><img src="a.jpg" alt="" /></figure>
  <figure data-variant="avatar" aria-label="User 2"><img src="b.jpg" alt="" /></figure>
  <figure data-variant="avatar" aria-label="User 3"><img src="c.jpg" alt="" /></figure>
</figure>
```

Group inherits `.small`/`.large` size classes. Avatars overlap with negative margin and background-colored border.

## Badge

Uses `.badge` class with optional variant classes.

```html
<span class="badge">Default</span>
<span class="badge secondary">Secondary</span>
<span class="badge outline">Outline</span>
<span class="badge success">Success</span>
<span class="badge warning">Warning</span>
<span class="badge danger">Danger</span>
```

**Variants**: `secondary`, `outline`, `success`, `warning`, `danger`. Pill-shaped (full border radius), medium font weight, small text size.

## Breadcrumb

Uses semantic `<nav>` with ordered list.

```html
<nav aria-label="Breadcrumb">
  <ol class="unstyled hstack" style="font-size: var(--text-7)">
    <li><a href="/" class="unstyled">Home</a></li>
    <li aria-hidden="true">/</li>
    <li><a href="/projects" class="unstyled">Projects</a></li>
    <li aria-hidden="true">/</li>
    <li><a href="#" class="unstyled" aria-current="page"><strong>Current</strong></a></li>
  </ol>
</nav>
```

Uses `.unstyled` (removes list styles/decoration) and `.hstack` (flex row with gap). Active item marked with `aria-current="page"`.

## Button

Styled by default for `<button>`, `<a class="button">`, and `::file-selector-button`.

```html
<button>Primary</button>
<button data-variant="secondary">Secondary</button>
<button data-variant="danger">Danger</button>
<button class="outline">Outline</button>
<button class="ghost">Ghost</button>
<button disabled>Disabled</button>
```

**Semantic variants**: `data-variant="secondary"`, `data-variant="danger"`

**Visual styles**: `.outline` (bordered, transparent bg), `.ghost` (no border)

**Sizes**: `.small`, default, `.large`, `.icon` (square, no padding)

```html
<button class="small">Small</button>
<button>Default</button>
<button class="large">Large</button>
<button class="icon small" aria-label="Settings">&#9881;</button>
```

**Button groups**: Wrap in `<menu class="buttons">`:

```html
<menu class="buttons">
  <li><button class="outline">Left</button></li>
  <li><button class="outline">Center</button></li>
  <li><button class="outline">Right</button></li>
</menu>
```

Buttons in groups have connected corners (first/last get outer radius).

## Card

Uses `.card` class on any element (typically `<article>`).

```html
<article class="card">
  <header>
    <h3>Card Title</h3>
    <p>Card description.</p>
  </header>
  <p>Card content here.</p>
  <footer class="hstack">
    <button class="outline">Cancel</button>
    <button>Save</button>
  </footer>
</article>
```

**Styling**: Card background, border, small shadow, medium border radius, padding space-6.

## Meter

Uses native `<meter>` element for values within a known range.

```html
<meter value="0.8" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>
<meter value="0.5" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>
<meter value="0.2" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>
```

Colors automatically based on `low`/`high`/`optimum` attributes: optimum = `--success`, suboptimum = `--warning`, below = `--danger`. Full width, `--bar-height` tall, rounded.

## Pagination

Reuses `<menu class="buttons">` for page navigation.

```html
<nav aria-label="Pagination">
  <menu class="buttons">
    <li><a href="#prev" class="button outline small">&larr; Previous</a></li>
    <li><a href="#1" class="button outline small">1</a></li>
    <li><a href="#3" class="button small" aria-current="page">3</a></li>
    <li><a href="#5" class="button outline small">5</a></li>
    <li><a href="#next" class="button outline small">Next &rarr;</a></li>
  </menu>
</nav>
```

Active page uses solid button (no `.outline`), others use `.outline`. All use `.small` size. `aria-current="page"` marks active.

## Progress

Uses native `<progress>` element.

```html
<progress value="60" max="100"></progress>
<progress value="30" max="100"></progress>
```

Full width, `--bar-height` tall, rounded. Fill color is `--primary`, track is `--muted`. Smooth transition on value changes.

## Skeleton

Loading placeholders with shimmer animation.

```html
<div role="status" class="skeleton line"></div>
<div role="status" class="skeleton box"></div>
```

**Variants**: `.line` (full width, 1rem height), `.box` (4rem x 4rem square). Uses `role="status"` for accessibility. Shimmer animation via gradient background movement.

### Skeleton Card

```html
<article style="display: flex; gap: var(--space-3); padding: var(--space-6);">
  <div role="status" class="skeleton box"></div>
  <div style="flex: 1; display: flex; flex-direction: column; gap: var(--space-1);">
    <div role="status" class="skeleton line"></div>
    <div role="status" class="skeleton line" style="width: 60%"></div>
  </div>
</article>
```

## Spinner

Uses `aria-busy="true"` on any element.

```html
<div aria-busy="true"></div>
<div aria-busy="true" data-spinner="small"></div>
<div aria-busy="true" data-spinner="large"></div>
<button aria-busy="true" data-spinner="small" disabled>Loading</button>
```

**Sizes**: default (1.5rem), `data-spinner="small"` (1rem), `data-spinner="large"` (2rem, 3px border).

### Spinner Overlay

`data-spinner="overlay"` dims child content and overlays spinner:

```html
<article class="card" aria-busy="true" data-spinner="large overlay">
  <p>Content is dimmed while loading.</p>
</article>
```

Overlay mode sets `pointer-events: none` on children and positions spinner absolutely centered.

## Switch

Toggle switch using checkbox with `role="switch"`.

```html
<label>
  <input type="checkbox" role="switch"> Notifications
</label>
<label>
  <input type="checkbox" role="switch" checked> Enabled
</label>
<label>
  <input type="checkbox" role="switch" disabled> Disabled off
</label>
```

Styled as a pill toggle with animated thumb. Uses `--bar-height * 3` for height, primary color when checked.

## Table

Tables styled by default. Wrap in `.table` for horizontal scroll on small screens.

```html
<div class="table">
  <table>
    <thead>
      <tr>
        <th>Name</th>
        <th>Email</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Alice</td>
        <td>alice@example.com</td>
        <td><span class="badge success">Active</span></td>
      </tr>
    </tbody>
  </table>
</div>
```

**Styling**: Collapsed borders, muted headers with medium weight, row hover with muted background, bottom border on rows (none on last), small text size. `.table` wrapper has `overflow-x: auto` and min-width 320px.
