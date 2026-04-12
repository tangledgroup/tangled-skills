# Oat UI - Data Display Components

Tables, avatars, badges, and data presentation components.

## Tables

### Basic Table

```html
<div class="table">
  <table>
    <thead>
      <tr>
        <th>Name</th>
        <th>Email</th>
        <th>Role</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Alice Johnson</td>
        <td>alice@example.com</td>
        <td>Admin</td>
        <td><span class="badge success">Active</span></td>
      </tr>
      <tr>
        <td>Bob Smith</td>
        <td>bob@example.com</td>
        <td>Editor</td>
        <td><span class="badge">Active</span></td>
      </tr>
      <tr>
        <td>Carol White</td>
        <td>carol@example.com</td>
        <td>Viewer</td>
        <td><span class="badge secondary">Pending</span></td>
      </tr>
    </tbody>
  </table>
</div>
```

Wrap in `class="table"` for horizontal scrolling on small screens.

### Table with Actions

```html
<div class="table">
  <table>
    <thead>
      <tr>
        <th>User</th>
        <th>Email</th>
        <th>Status</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Alice Johnson</td>
        <td>alice@example.com</td>
        <td><span class="badge success">Active</span></td>
        <td>
          <div class="hstack gap-2">
            <button class="outline small">Edit</button>
            <button class="outline small" data-variant="danger">Delete</button>
          </div>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

### Table with Avatars

```html
<div class="table">
  <table>
    <thead>
      <tr>
        <th>User</th>
        <th>Email</th>
        <th>Last Login</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          <div class="hstack items-center gap-2">
            <figure data-variant="avatar" class="small">
              <img src="/alice.jpg" alt="" />
            </figure>
            <span>Alice Johnson</span>
          </div>
        </td>
        <td>alice@example.com</td>
        <td>2 hours ago</td>
      </tr>
    </tbody>
  </table>
</div>
```

### Table with Checkbox Selection

```html
<div class="table">
  <table>
    <thead>
      <tr>
        <th><input type="checkbox" id="select-all" /></th>
        <th>Name</th>
        <th>Email</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><input type="checkbox" name="selected[]" value="1" /></td>
        <td>Alice Johnson</td>
        <td>alice@example.com</td>
        <td><span class="badge success">Active</span></td>
      </tr>
      <tr>
        <td><input type="checkbox" name="selected[]" value="2" /></td>
        <td>Bob Smith</td>
        <td>bob@example.com</td>
        <td><span class="badge">Active</span></td>
      </tr>
    </tbody>
  </table>
</div>

<script>
document.getElementById('select-all').addEventListener('change', (e) => {
  document.querySelectorAll('tbody input[type="checkbox"]').forEach(cb => {
    cb.checked = e.target.checked;
  });
});
</script>
```

## Avatars

### Basic Avatar

```html
<figure data-variant="avatar" aria-label="Jane Doe">
  <img src="/avatar.jpg" alt="" />
</figure>
```

### Avatar Sizes

```html
<!-- Small -->
<figure data-variant="avatar" class="small" aria-label="User">
  <img src="/avatar.jpg" alt="" />
</figure>

<!-- Default -->
<figure data-variant="avatar" aria-label="User">
  <img src="/avatar.jpg" alt="" />
</figure>

<!-- Large -->
<figure data-variant="avatar" class="large" aria-label="User">
  <img src="/avatar.jpg" alt="" />
</figure>
```

### Avatar with Initials

```html
<figure data-variant="avatar" aria-label="John Doe">
  <abbr title="John Doe">JD</abbr>
</figure>
```

### Avatar with Icon

```html
<figure data-variant="avatar" aria-label="Guest">
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
    <circle cx="12" cy="7" r="4"/>
  </svg>
</figure>
```

### Avatar Group

```html
<figure data-variant="avatar" role="group" aria-label="Team members">
  <figure data-variant="avatar" aria-label="Alice">
    <img src="/alice.jpg" alt="" />
  </figure>
  <figure data-variant="avatar" aria-label="Bob">
    <img src="/bob.jpg" alt="" />
  </figure>
  <figure data-variant="avatar" aria-label="Carol">
    <img src="/carol.jpg" alt="" />
  </figure>
</figure>
```

### Avatar Group with Count

```html
<figure data-variant="avatar" role="group" aria-label="12 team members">
  <figure data-variant="avatar" aria-label="Alice">
    <img src="/alice.jpg" alt="" />
  </figure>
  <figure data-variant="avatar" aria-label="Bob">
    <img src="/bob.jpg" alt="" />
  </figure>
  <figure data-variant="avatar" aria-label="+10 more">
    <abbr title="+10 more">+10</abbr>
  </figure>
</figure>
```

## Badges

### Badge Variants

```html
<span class="badge">Default</span>
<span class="badge secondary">Secondary</span>
<span class="badge outline">Outline</span>
<span class="badge success">Success</span>
<span class="badge warning">Warning</span>
<span class="badge danger">Danger</span>
```

### Badge in Button

```html
<button>
  Notifications
  <span class="badge danger" style="margin-left: var(--space-2);">3</span>
</button>
```

### Badge as Counter

```html
<figure data-variant="avatar" aria-label="User">
  <img src="/avatar.jpg" alt="" />
  <span class="badge success" style="position: absolute; bottom: 0; right: 0; width: 12px; height: 12px; padding: 0; border-radius: 50%;"></span>
</figure>
```

## Meter Display

### With Label

```html
<div class="vstack gap-1">
  <div class="hstack justify-between">
    <span>Storage</span>
    <span>75%</span>
  </div>
  <meter value="0.75" min="0" max="1" low="0.5" high="0.8" optimum="0.2"></meter>
</div>
```

### Multiple Meters

```html
<div class="vstack gap-3">
  <div>
    <div class="hstack justify-between mb-1">
      <span>CPU Usage</span>
      <span>45%</span>
    </div>
    <meter value="0.45" min="0" max="1"></meter>
  </div>
  
  <div>
    <div class="hstack justify-between mb-1">
      <span>Memory</span>
      <span>68%</span>
    </div>
    <meter value="0.68" min="0" max="1"></meter>
  </div>
  
  <div>
    <div class="hstack justify-between mb-1">
      <span>Disk</span>
      <span>92%</span>
    </div>
    <meter value="0.92" min="0" max="1" low="0.5" high="0.8"></meter>
  </div>
</div>
```

## Stat Cards

### Basic Stat

```html
<article class="card">
  <header>
    <h4>Total Users</h4>
  </header>
  <h2>12,345</h2>
  <p class="text-light">+12% from last month</p>
</article>
```

### Stat with Trend

```html
<article class="card">
  <header class="hstack justify-between items-start">
    <div>
      <h4>Revenue</h4>
      <p class="text-light">This month</p>
    </div>
    <span class="badge success">+12%</span>
  </header>
  
  <h2>$42,200</h2>
  
  <progress value="72" max="100"></progress>
</article>
```

### Stat Grid

```html
<div class="container">
  <div class="row" style="gap: var(--space-4);">
    <div class="col-4">
      <article class="card">
        <header class="hstack justify-between">
          <h4>Revenue</h4>
          <span class="badge success">+12%</span>
        </header>
        <h2>$42,200</h2>
        <p class="text-light">vs last month</p>
      </article>
    </div>
    
    <div class="col-4">
      <article class="card">
        <header class="hstack justify-between">
          <h4>Users</h4>
          <span class="badge success">+8%</span>
        </header>
        <h2>1,234</h2>
        <p class="text-light">active users</p>
      </article>
    </div>
    
    <div class="col-4">
      <article class="card">
        <header class="hstack justify-between">
          <h4>Tickets</h4>
          <span class="badge warning">+3</span>
        </header>
        <h2>14</h2>
        <p class="text-light">open tickets</p>
      </article>
    </div>
  </div>
</div>
```

## Lists

### Simple List

```html
<ul>
  <li>Item 1</li>
  <li>Item 2</li>
  <li>Item 3</li>
</ul>
```

### List with Icons

```html
<ul style="list-style: none; padding: 0;">
  <li class="hstack items-center gap-2">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
    Task completed
  </li>
  <li class="hstack items-center gap-2">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
    Another task
  </li>
</ul>
```

### Divided List

```html
<ul style="list-style: none; padding: 0;">
  <li style="padding: var(--space-3); border-bottom: 1px solid var(--border);">
    <strong>Name</strong>
    <p class="text-light">john@example.com</p>
  </li>
  <li style="padding: var(--space-3); border-bottom: 1px solid var(--border);">
    <strong>Email</strong>
    <p class="text-light">Verified</p>
  </li>
</ul>
```

## Empty States

### Basic Empty State

```html
<article class="card align-center" style="padding: var(--space-8);">
  <h3>No items yet</h3>
  <p class="text-light">Get started by creating your first item.</p>
  <footer class="mt-4">
    <button>Create Item</button>
  </footer>
</article>
```

### Empty State with Icon

```html
<article class="card align-center" style="padding: var(--space-8);">
  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--muted-foreground)" stroke-width="1.5" style="margin-bottom: var(--space-3);">
    <circle cx="12" cy="12" r="10"/>
    <line x1="12" y1="8" x2="12" y2="12"/>
    <line x1="12" y1="16" x2="12.01" y2="16"/>
  </svg>
  
  <h3>No notifications</h3>
  <p class="text-light">You're all caught up!</p>
</article>
```

## Accessibility

### Table Headers

Always use `<thead>` with `<th>` elements:

```html
<table>
  <thead>
    <tr>
      <th scope="col">Name</th>
      <th scope="col">Email</th>
    </tr>
  </thead>
  <tbody>
    <!-- Data rows -->
  </tbody>
</table>
```

### Avatar Labels

Always provide `aria-label`:

```html
<figure data-variant="avatar" aria-label="John Doe">
  <img src="/avatar.jpg" alt="" />
</figure>
```

### Badge Context

Ensure badge meaning is clear from context:

```html
<td>
  <span class="badge success" aria-label="Status: Active">Active</span>
</td>
```

## Customization

### Table Border Radius

```css
table {
  border-radius: var(--radius-md);
  overflow: hidden;
}

thead {
  background: var(--muted);
}
```

### Avatar Border

```css
figure[data-variant="avatar"] img {
  border: 2px solid var(--background);
}
```

### Badge Animation

```css
.badge.danger {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
```
