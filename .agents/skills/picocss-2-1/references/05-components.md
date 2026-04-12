# Components

Pico v2 includes several modular components for common UI patterns.

## Card

Cards are versatile containers for grouping related content:

```html
<article>
  <header>
    <h2>Card Title</h2>
    <p>Card subtitle or metadata</p>
  </header>
  
  <section class="content">
    <p>Card content goes here. You can include text, images, forms, and more.</p>
  </section>
  
  <footer>
    <a href="/card/1">Learn more</a>
  </footer>
</article>
```

### Card with Image

```html
<article>
  <header>
    <img src="image.jpg" alt="Card image" style="width: 100%; height: auto;">
    <h2>Image Card</h2>
  </header>
  
  <section class="content">
    <p>Content with an image header.</p>
  </section>
  
  <footer>
    <button>View Details</button>
  </footer>
</article>
```

### Cards in Grid

```html
<div class="grid">
  <article>
    <h3>Card 1</h3>
    <p>Content for card 1...</p>
    <footer><a href="#">Read more</a></footer>
  </article>
  
  <article>
    <h3>Card 2</h3>
    <p>Content for card 2...</p>
    <footer><a href="#">Read more</a></footer>
  </article>
  
  <article>
    <h3>Card 3</h3>
    <p>Content for card 3...</p>
    <footer><a href="#">Read more</a></footer>
  </article>
</div>
```

## Accordion

Create collapsible content sections:

```html
<details>
  <summary>First item</summary>
  <div class="content">
    <p>Content for the first item...</p>
  </div>
</details>

<details>
  <summary>Second item</summary>
  <div class="content">
    <p>Content for the second item...</p>
  </div>
</details>

<details open>
  <summary>Third item (open by default)</summary>
  <div class="content">
    <p>Content for the third item...</p>
  </div>
</details>
```

### Accordion with Icons

```html
<details>
  <summary>
    <span>FAQ Item 1</span>
    <svg class="icon" ...>+</svg>
  </summary>
  <div class="content">
    <p>Answer to FAQ item 1...</p>
  </div>
</details>
```

## Modal

Create modal dialogs using dialog element:

```html
<button onclick="document.getElementById('modal').showModal()">
  Open Modal
</button>

<dialog id="modal">
  <header>
    <h2>Modal Title</h2>
  </header>
  
  <section class="content">
    <p>Modal content goes here...</p>
  </section>
  
  <footer>
    <button onclick="document.getElementById('modal').close()">
      Close
    </button>
  </footer>
</dialog>
```

### Modal with Form

```html
<button onclick="document.getElementById('login-modal').showModal()">
  Log In
</button>

<dialog id="login-modal">
  <header>
    <h2>Log In</h2>
  </header>
  
  <form method="dialog">
    <label>
      Email
      <input type="email" required>
    </label>
    
    <label>
      Password
      <input type="password" required>
    </label>
    
    <button type="submit">Sign In</button>
  </form>
  
  <footer>
    <button onclick="document.getElementById('login-modal').close()">
      Cancel
    </button>
  </footer>
</dialog>
```

## Dropdown

Create dropdown menus with list elements:

```html
<div role="group">
  <button aria-haspopup="true" aria-expanded="false">
    Actions
  </button>
  
  <ul role="menu">
    <li role="menuitem"><a href="/edit">Edit</a></li>
    <li role="menuitem"><a href="/duplicate">Duplicate</a></li>
    <li role="menuitem"><a href="/delete" class="contrast">Delete</a></li>
  </ul>
</div>
```

## Group

Group related buttons or form elements:

```html
<div role="group">
  <input type="text" placeholder="Search...">
  <button type="submit">Search</button>
</div>
```

### Button Group

```html
<div role="group">
  <button>Save</button>
  <button>Cancel</button>
  <button class="contrast">Delete</button>
</div>
```

## Navigation

### Horizontal Nav

```html
<nav>
  <ul>
    <li><a href="/" aria-current="page">Home</a></li>
    <li><a href="/about">About</a></li>
    <li><a href="/services">Services</a></li>
    <li><a href="/contact">Contact</a></li>
  </ul>
</nav>
```

### Vertical Nav (Sidebar)

```html
<nav>
  <ul>
    <li><a href="/dashboard" aria-current="page">Dashboard</a></li>
    <li><a href="/projects">Projects</a></li>
    <li><a href="/tasks">Tasks</a></li>
    <li><a href="/settings">Settings</a></li>
  </ul>
</nav>
```

### Nav with Dropdown

```html
<nav>
  <ul>
    <li><a href="/">Home</a></li>
    <li>
      <div role="group">
        <button aria-haspopup="true">Services</button>
        <ul role="menu">
          <li><a href="/web-design">Web Design</a></li>
          <li><a href="/development">Development</a></li>
          <li><a href="/consulting">Consulting</a></li>
        </ul>
      </div>
    </li>
    <li><a href="/contact">Contact</a></li>
  </ul>
</nav>
```

## Progress Bar

Show loading or progress states:

```html
<progress value="70" max="100"></progress>
```

### Indeterminate Progress

```html
<progress></progress>
```

### Styled Progress

```css
progress {
  width: 100%;
}
```

```html
<div>
  <p>Loading... 70%</p>
  <progress value="70" max="100"></progress>
</div>
```

## Loading Spinner

Create loading states with CSS animations:

```html
<div class="loading">
  <div class="spinner"></div>
  <span>Loading...</span>
</div>
```

```css
.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--pico-primary);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

## Tooltip

Add tooltips using the `title` attribute or custom implementation:

```html
<button title="Click to save changes">Save</button>
```

### Custom Tooltip with CSS

```html
<div class="tooltip" role="tooltip">
  <button>Hover for tooltip</button>
  <span class="tooltip-text">This is a custom tooltip</span>
</div>
```

```css
.tooltip {
  position: relative;
  display: inline-block;
}

.tooltip-text {
  visibility: hidden;
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  padding: 0.5rem;
  background: var(--pico-contrast);
  color: var(--pico-contrast-inverse);
  border-radius: var(--pico-border-radius);
  white-space: nowrap;
  z-index: 10;
}

.tooltip:hover .tooltip-text {
  visibility: visible;
}
```

## Table

Tables are styled with basic borders and spacing:

```html
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
      <td>John Doe</td>
      <td>john@example.com</td>
      <td>Admin</td>
      <td>Active</td>
    </tr>
    <tr>
      <td>Jane Smith</td>
      <td>jane@example.com</td>
      <td>User</td>
      <td>Inactive</td>
    </tr>
  </tbody>
</table>
```

### Table with Overflow

For wide tables that need horizontal scrolling:

```html
<div class="overflow-auto">
  <table>
    <thead>
      <tr>
        <th>Column 1</th>
        <th>Column 2</th>
        <th>Column 3</th>
        <th>Column 4</th>
        <th>Column 5</th>
        <th>Column 6</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Data 1</td>
        <td>Data 2</td>
        <td>Data 3</td>
        <td>Data 4</td>
        <td>Data 5</td>
        <td>Data 6</td>
      </tr>
    </tbody>
  </table>
</div>
```

## Code Blocks

Display code with syntax highlighting:

```html
<pre><code class="language-javascript">
function greet(name) {
  console.log(`Hello, ${name}!`);
}
</code></pre>
```

### Inline Code

Use `<code>` for inline code:

```html
<p>Use the <code>.container</code> class to center content.</p>
```

### Keyboard Input

Use `<kbd>` for keyboard shortcuts:

```html
<p>Press <kbd>Ctrl</kbd> + <kbd>S</kbd> to save.</p>
```

## Complete Example: Dashboard Layout

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <link rel="stylesheet" href="css/pico.min.css">
  <title>Dashboard</title>
</head>
<body>
  <header class="container">
    <nav>
      <ul>
        <li><a href="/dashboard" aria-current="page">Dashboard</a></li>
        <li><a href="/projects">Projects</a></li>
        <li><a href="/settings">Settings</a></li>
      </ul>
    </nav>
  </header>

  <main class="container">
    <section>
      <hgroup>
        <h1>Dashboard</h1>
        <p>Welcome back, John!</p>
      </hgroup>
    </section>

    <section>
      <h2>Quick Stats</h2>
      <div class="grid">
        <article>
          <h3>Projects</h3>
          <p><strong>12</strong> active projects</p>
        </article>
        <article>
          <h3>Tasks</h3>
          <p><strong>45</strong> pending tasks</p>
        </article>
        <article>
          <h3>Progress</h3>
          <progress value="75" max="100"></progress>
          <p>75% complete</p>
        </article>
      </div>
    </section>

    <section>
      <h2>Recent Projects</h2>
      <table>
        <thead>
          <tr>
            <th>Project</th>
            <th>Status</th>
            <th>Progress</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Website Redesign</td>
            <td>In Progress</td>
            <td><progress value="60" max="100"></progress></td>
            <td>
              <div role="group">
                <button>Edit</button>
                <button class="secondary">View</button>
              </div>
            </td>
          </tr>
          <tr>
            <td>Mobile App</td>
            <td>Planning</td>
            <td><progress value="20" max="100"></progress></td>
            <td>
              <div role="group">
                <button>Edit</button>
                <button class="secondary">View</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <section>
      <h2>FAQ</h2>
      <details>
        <summary>How do I create a new project?</summary>
        <div class="content">
          <p>Click the "New Project" button in the top right corner.</p>
        </div>
      </details>
      
      <details>
        <summary>How do I invite team members?</summary>
        <div class="content">
          <p>Go to Settings > Team and click "Invite Member".</p>
        </div>
      </details>
    </section>
  </main>

  <footer class="container">
    <p>&copy; 2024 Your Company. All rights reserved.</p>
  </footer>
</body>
</html>
```
