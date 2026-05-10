# Recipes, Patterns, and Extensions

## Composable UI Recipes

OAT components are designed to compose together. These recipes show common patterns.

### Split Button

Combine `menu.buttons` with `ot-dropdown` for a primary action + secondary menu:

```html
<ot-dropdown>
  <menu class="buttons">
    <li><button class="outline">Save</button></li>
    <li>
      <button class="outline" popovertarget="save-actions" aria-label="More save actions">
        More
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m6 9 6 6 6-6" />
        </svg>
      </button>
    </li>
  </menu>
  <menu popover id="save-actions">
    <button role="menuitem">Save draft</button>
    <button role="menuitem">Save and publish</button>
    <button role="menuitem">Duplicate</button>
  </menu>
</ot-dropdown>
```

**Pattern**: Button group + popover dropdown = compact multi-action control.

### Form Card

Group form fields inside a card with header, body, and footer:

```html
<article class="card">
  <header>
    <h3>Profile</h3>
    <p class="text-light">Update account information</p>
  </header>

  <div class="mt-4">
    <label data-field>
      Name
      <input type="text" value="Your name" />
    </label>

    <label data-field>
      Email
      <input type="email" value="mila@example.com" />
    </label>

    <label data-field>
      <input type="checkbox" role="switch" checked> Email notifications
    </label>
  </div>

  <footer class="hstack justify-end mt-4">
    <button class="outline">Cancel</button>
    <button>Save</button>
  </footer>
</article>
```

**Pattern**: Card container + form fields + hstack footer = self-contained form panel.

### Empty State

Card with centered text and call-to-action for empty lists/results:

```html
<article class="card align-center">
  <h3>Nothing here yet</h3>
  <p class="text-light">Why don't you create something?</p>
  <footer class="hstack justify-center mt-4">
    <button>New item</button>
  </footer>
</article>
```

**Pattern**: Card + `.align-center` + muted text + primary action = empty state placeholder.

### Stats Cards Dashboard

Compose dashboard metrics with grid, cards, badges, and progress/meter:

```html
<div class="container">
  <div class="row">
    <article class="card col-4">
      <header class="hstack justify-between items-center">
        <h4>Revenue</h4>
        <span class="badge success">+12%</span>
      </header>
      <h2>$42,200</h2>
      <p class="text-light">vs last month</p>
      <progress value="72" max="100"></progress>
    </article>

    <article class="card col-4">
      <header class="hstack justify-between items-center">
        <h4>Completion</h4>
        <span class="badge warning">-2%</span>
      </header>
      <h2>4.6%</h2>
      <p class="text-light">checkout completion</p>
      <meter value="0.46" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>
    </article>

    <article class="card col-4">
      <header class="hstack justify-between items-center">
        <h4>Tickets</h4>
        <span class="badge">14</span>
      </header>
      <h2>14</h2>
      <p class="text-light">support queue</p>
      <progress value="35" max="100"></progress>
    </article>
  </div>
</div>
```

**Pattern**: Container + row of cards + header with badge + metric + progress bar = dashboard widget.

---

## Community Extensions

Third-party extensions that work with OAT:

### oat-chips

Chip/tag component with dismissible filters, colors, and toggle selection. ~1KB gzipped.

- **Repo**: https://github.com/someshkar/oat-chips
- **Demo**: https://oat-chips.somesh.dev

### oat-animate

Lightweight animation extension with declarative `ot-animate` triggers (`on-load`, `hover`, `in-view`) and reduced-motion support. ~1KB gzipped.

- **Repo**: https://github.com/dharmeshgurnani/oat-animate
- **Demo**: https://oat-animate.dharmeshgurnani.com

---

## Companion Libraries

Zero-dependency JavaScript libraries by the same author that pair well with OAT:

| Library | Size | Purpose |
|---------|------|---------|
| [tinyrouter.js](https://github.com/knadh/tinyrouter.js) | ~950B | Frontend routing via `window.history` |
| [highlighted-input.js](https://github.com/knadh/highlighted-input.js) | ~450B | Keyword/tag highlighting in `<input>` fields |
| [floatype.js](https://github.com/knadh/floatype.js) | ~1.2KB | Floating autocomplete/suggestion for textareas |
| [dragmove.js](https://github.com/knadh/dragmove.js) | ~500B | Draggable/movable DOM elements |
| [indexed-cache.js](https://github.com/knadh/indexed-cache) | ~2.1KB | Sideload static assets to IndexedDB for offline caching |

These libraries share OAT's philosophy: tiny, zero-dependency, semantic HTML-first.
