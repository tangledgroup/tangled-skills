# Data Display Components

## Accordion

Shows and hides content with only one item open at a time. Uses radio inputs internally.

### Class Names

- **component**: `collapse`
- **part**: `collapse-title`, `collapse-content`
- **modifier**: `collapse-arrow`, `collapse-plus`, `collapse-open`, `collapse-close`

### Syntax

```html
<details class="collapse collapse-arrow">
  <summary class="collapse-title">Section 1</summary>
  <div class="collapse-content">Content for section 1.</div>
</details>
<details class="collapse collapse-arrow">
  <summary class="collapse-title">Section 2</summary>
  <div class="collapse-content">Content for section 2.</div>
</details>
```

### Rules

- All items in the same accordion group share behavior through `<details>` elements
- Use different radio `name` attributes for separate accordion groups on the same page
- `collapse-arrow` shows an arrow indicator, `collapse-plus` shows a plus icon

## Avatar

Displays a thumbnail image, typically for user profiles.

### Class Names

- **component**: `avatar`, `avatar-group`
- **modifier**: `avatar-online`, `avatar-offline`, `avatar-placeholder`

### Syntax

```html
<div class="avatar">
  <div class="w-12 rounded-full">
    <img src="/profile.jpg" alt="Profile" />
  </div>
</div>

<!-- Avatar group -->
<div class="avatar-group -space-x-4">
  <div class="avatar"><div class="w-12"><img src="/a.jpg" /></div></div>
  <div class="avatar"><div class="w-12"><img src="/b.jpg" /></div></div>
</div>
```

### Rules

- Set custom sizes with `w-*` and `h-*` utility classes
- Use mask classes like `mask-squircle`, `mask-hexagon` for shaped avatars

## Badge

Small status indicators for data points.

### Class Names

- **component**: `badge`
- **style**: `badge-outline`, `badge-dash`, `badge-soft`, `badge-ghost`
- **color**: `badge-neutral`, `badge-primary`, `badge-secondary`, `badge-accent`, `badge-info`, `badge-success`, `badge-warning`, `badge-error`
- **size**: `badge-xs`, `badge-sm`, `badge-md`, `badge-lg`, `badge-xl`

### Syntax

```html
<span class="badge badge-primary">New</span>
<span class="badge badge-outline badge-secondary">Beta</span>
<span class="badge badge-ghost badge-success badge-sm">Active</span>
```

### Rules

- Can be used inline within text or inside buttons
- Empty badges: `<span class="badge"></span>` (no text content)

## Card

Groups and displays content with optional images, titles, and actions.

### Class Names

- **component**: `card`
- **part**: `card-title`, `card-body`, `card-actions`
- **style**: `card-border`, `card-dash`
- **modifier**: `card-side`, `image-full`
- **size**: `card-xs`, `card-sm`, `card-md`, `card-lg`, `card-xl`

### Syntax

```html
<div class="card w-96 bg-base-100 shadow-xl">
  <figure><img src="/image.jpg" alt="Description" /></figure>
  <div class="card-body">
    <h2 class="card-title">Card Title</h2>
    <p>Card content goes here.</p>
    <div class="card-actions justify-end">
      <button class="btn btn-primary">Action</button>
    </div>
  </div>
</div>
```

### Rules

- `<figure>` and `<div class="card-body">` are optional
- Use `sm:card-horizontal` for responsive horizontal layout
- Place image after `card-body` to position it at the bottom

## Carousel

Scrollable container for images or content items.

### Class Names

- **component**: `carousel`
- **part**: `carousel-item`
- **modifier**: `carousel-start`, `carousel-center`, `carousel-end`
- **direction**: `carousel-horizontal`, `carousel-vertical`

### Syntax

```html
<div class="carousel carousel-center rounded-box">
  <div class="carousel-item"><img src="/1.jpg" alt="" /></div>
  <div class="carousel-item"><img src="/2.jpg" alt="" /></div>
  <div class="carousel-item"><img src="/3.jpg" alt="" /></div>
</div>
```

### Rules

- Each item is a `<div class="carousel-item">`
- Add `w-full` to items for full-width carousel

## Chat Bubble

Displays conversation messages with optional avatar, header, and footer.

### Class Names

- **component**: `chat`
- **part**: `chat-image`, `chat-header`, `chat-footer`, `chat-bubble`
- **placement**: `chat-start`, `chat-end`
- **color**: `chat-bubble-neutral`, `chat-bubble-primary`, etc.

### Syntax

```html
<div class="chat chat-start">
  <div class="chat-image avatar"><div class="w-10 rounded-full"><img src="/avatar.jpg" /></div></div>
  <div class="chat-header">John <time>12:45</time></div>
  <div class="chat-bubble chat-bubble-primary">Hello!</div>
  <div class="chat-footer">Delivered</div>
</div>

<div class="chat chat-end">
  <div class="chat-image avatar"><div class="w-10 rounded-full"><img src="/me.jpg" /></div></div>
  <div class="chat-header">Me <time>12:46</time></div>
  <div class="chat-bubble">Hi there!</div>
  <div class="chat-footer">Read</div>
</div>
```

### Rules

- `chat-start` or `chat-end` is required (placement)
- Color classes on `chat-bubble` are optional

## Collapse

Shows and hides content independently (unlike Accordion which groups items).

### Class Names

- **component**: `collapse`
- **part**: `collapse-title`, `collapse-content`
- **modifier**: `collapse-arrow`, `collapse-plus`, `collapse-open`, `collapse-close`

### Syntax

```html
<div tabindex="0" class="collapse collapse-arrow bg-base-200">
  <div class="collapse-title text-lg font-medium">Click to expand</div>
  <div class="collapse-content">Hidden content revealed.</div>
</div>
```

### Rules

- Use `tabindex="0"` for keyboard interaction, or `<input type="checkbox">` as first child
- Can also use native `<details>`/`<summary>` tags

## Countdown

Animated number transitions between 0 and 999.

### Class Names

- **component**: `countdown`

### Syntax

```html
<span class="countdown" aria-live="polite">
  <span style="--value:42;">42</span>
</span>
```

### Rules

- Both `--value` CSS variable and text content must match (0–999)
- Update both via JavaScript for animation
- Add `aria-live="polite"` and `aria-label` for accessibility

## Diff

Side-by-side comparison of two items with a draggable divider.

### Class Names

- **component**: `diff`
- **part**: `diff-item-1`, `diff-item-2`, `diff-resizer`

### Syntax

```html
<figure class="diff aspect-16/9">
  <div class="diff-item-1"><img src="/before.jpg" /></div>
  <div class="diff-item-2"><img src="/after.jpg" /></div>
  <div class="diff-resizer"></div>
</figure>
```

### Rules

- Add `aspect-16/9` or similar to maintain aspect ratio

## Hover 3D Card

Adds a 3D tilt effect based on mouse position.

### Class Names

- **component**: `hover-3d`

### Syntax

```html
<div class="hover-3d my-12 mx-2">
  <figure class="max-w-96 rounded-2xl">
    <img src="/card.jpg" alt="3D card" />
  </figure>
  <div></div><div></div><div></div><div></div>
  <div></div><div></div><div></div><div></div>
</div>
```

### Rules

- Must have exactly 9 direct children: first is content, remaining 8 are empty `<div>` hover zones
- Content inside should be non-interactive (no buttons or links)

## Hover Gallery

Image container that reveals additional images on horizontal hover.

### Class Names

- **component**: `hover-gallery`

### Syntax

```html
<figure class="hover-gallery max-w-60">
  <img src="/1.jpg" alt="Front" />
  <img src="/2.jpg" alt="Side" />
  <img src="/3.jpg" alt="Back" />
</figure>
```

### Rules

- Supports up to 10 images
- Needs a max-width constraint
- All images should have the same dimensions

## Kbd

Displays keyboard shortcuts.

### Class Names

- **component**: `kbd`
- **size**: `kbd-xs`, `kbd-sm`, `kbd-md`, `kbd-lg`, `kbd-xl`

### Syntax

```html
<kbd class="kbd kbd-sm">Ctrl</kbd> + <kbd class="kbd kbd-sm">K</kbd>
```

## List

Vertical layout for displaying information in rows.

### Class Names

- **component**: `list`, `list-row`
- **modifier**: `list-col-wrap`, `list-col-grow`

### Syntax

```html
<ul class="list bg-base-100 rounded-box w-96">
  <li class="list-row">
    <span class="font-bold">Title</span>
    <span>Description fills remaining space</span>
  </li>
</ul>
```

### Rules

- Second child of `list-row` fills remaining space by default
- Use `list-col-grow` on another child to redirect the growth
- Use `list-col-wrap` to force an item to wrap

## Stat

Displays numbers and data in blocks.

### Class Names

- **component**: `stats`
- **part**: `stat`, `stat-title`, `stat-value`, `stat-desc`, `stat-figure`, `stat-actions`
- **direction**: `stats-horizontal`, `stats-vertical`

### Syntax

```html
<div class="stats shadow w-96">
  <div class="stat">
    <div class="stat-figure"><img src="/icon.svg" alt="" /></div>
    <div class="stat-title">Total Views</div>
    <div class="stat-value">89,400</div>
    <div class="stat-desc">Jan 1st - Feb 1st</div>
  </div>
</div>
```

### Rules

- Horizontal by default; use `stats-vertical` for vertical layout

## Status

Small visual indicator dots for element status.

### Class Names

- **component**: `status`
- **color**: `status-neutral`, `status-primary`, `status-secondary`, `status-accent`, `status-info`, `status-success`, `status-warning`, `status-error`
- **size**: `status-xs`, `status-sm`, `status-md`, `status-lg`, `status-xl`

### Syntax

```html
<span class="status status-success"></span>
<span class="status status-error status-lg"></span>
```

## Table

Data tables with optional zebra striping and pinned rows/columns.

### Class Names

- **component**: `table`
- **modifier**: `table-zebra`, `table-pin-rows`, `table-pin-cols`
- **size**: `table-xs`, `table-sm`, `table-md`, `table-lg`, `table-xl`

### Syntax

```html
<div class="overflow-x-auto">
  <table class="table table-zebra">
    <thead>
      <tr><th>Name</th><th>Role</th><th>Status</th></tr>
    </thead>
    <tbody>
      <tr><td>Alice</td><td>Admin</td><td>Active</td></tr>
      <tr><td>Bob</td><td>User</td><td>Pending</td></tr>
    </tbody>
  </table>
</div>
```

### Rules

- Wrap in `<div class="overflow-x-auto">` for horizontal scrolling on small screens

## Text Rotate

Infinite looping text rotation animation (up to 6 lines, 10s default duration).

### Class Names

- **component**: `text-rotate`

### Syntax

```html
<span class="text-rotate text-5xl font-bold">
  <span class="justify-items-center">
    <span>DESIGN</span>
    <span>DEVELOP</span>
    <span>DEPLOY</span>
  </span>
</span>
```

### Rules

- Inner wrapper must contain 2–6 `<span>` or `<div>` children
- Animation pauses on hover
- Set custom duration with Tailwind `duration-{ms}` (e.g., `duration-12000`)

## Timeline

Chronological event display.

### Class Names

- **component**: `timeline`
- **part**: `timeline-start`, `timeline-middle`, `timeline-end`
- **modifier**: `timeline-snap-icon`, `timeline-box`, `timeline-compact`
- **direction**: `timeline-vertical`, `timeline-horizontal`

### Syntax

```html
<ul class="timeline">
  <li>
    <div class="timeline-start"><span>2024</span></div>
    <div class="timeline-middle"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="currentColor"/></svg></div>
    <div class="timeline-end timeline-box">Event description</div>
    <hr />
  </li>
  <li>
    <hr />
    <div class="timeline-start"><span>2025</span></div>
    <div class="timeline-middle"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="currentColor"/></svg></div>
    <div class="timeline-end timeline-box">Another event</div>
    <hr />
  </li>
</ul>
```

### Rules

- Vertical is the default direction
- `<hr>` elements connect timeline items
- `timeline-compact` forces all content to one side
