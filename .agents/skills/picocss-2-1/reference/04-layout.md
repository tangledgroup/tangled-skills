# Layout: Container, Grid, and Landmarks

Pico provides simple layout tools for building responsive structures with semantic HTML.

## Container

The `.container` class centers content with a maximum width:

```html
<body>
  <main class="container">
    <h1>Centered Content</h1>
    <p>This content is centered with a max-width.</p>
  </main>
</body>
```

### Fluid Container

For full-width layouts, omit the container class or use `.fluid`:

```html
<body>
  <main class="container fluid">
    <h1>Full Width Content</h1>
  </main>
</body>
```

### Class-Less Containers

In the class-less version, `<header>`, `<main>`, and `<footer>` inside `<body>` automatically act as centered containers:

```html
<link rel="stylesheet" href="css/pico.classless.min.css">

<body>
  <header>
    <h1>Centered Header</h1>
  </header>
  
  <main>
    <h2>Centered Main Content</h2>
  </main>
  
  <footer>
    <p>Centered Footer</p>
  </footer>
</body>
```

## Grid

The `.grid` class creates responsive layouts that automatically adjust columns based on viewport width:

```html
<div class="grid">
  <article>Card 1</article>
  <article>Card 2</article>
  <article>Card 3</article>
  <article>Card 4</article>
</div>
```

### Grid with Different Content Types

Grid works with any block-level elements:

```html
<div class="grid">
  <section>Section 1</section>
  <section>Section 2</section>
  <section>Section 3</section>
</div>
```

### Nested Grids

You can nest grids for complex layouts:

```html
<div class="grid">
  <article>
    <h3>Featured</h3>
    <div class="grid">
      <img src="image1.jpg" alt="">
      <img src="image2.jpg" alt="">
    </div>
  </article>
  
  <article>
    <h3>Latest</h3>
    <p>Content here</p>
  </article>
</div>
```

### Grid in Forms

Use grid for multi-column forms:

```html
<form>
  <fieldset class="grid">
    <input name="login" placeholder="Username">
    <input type="password" name="password" placeholder="Password">
    <button type="submit">Log In</button>
  </fieldset>
</form>
```

### Grid with Images

Images in grid automatically scale:

```html
<div class="grid">
  <figure>
    <img src="photo1.jpg" alt="Description 1">
    <figcaption>Caption 1</figcaption>
  </figure>
  
  <figure>
    <img src="photo2.jpg" alt="Description 2">
    <figcaption>Caption 2</figcaption>
  </figure>
  
  <figure>
    <img src="photo3.jpg" alt="Description 3">
    <figcaption>Caption 3</figcaption>
  </figure>
</div>
```

## Landmarks and Sections

### Header, Main, Footer

Semantic landmarks are styled by default:

```html
<body>
  <header>
    <nav>
      <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/about">About</a></li>
        <li><a href="/contact">Contact</a></li>
      </ul>
    </nav>
  </header>
  
  <main>
    <article>
      <h1>Main Article</h1>
      <p>Content goes here...</p>
    </article>
  </main>
  
  <footer>
    <p>&copy; 2024 Your Company</p>
  </footer>
</body>
```

### Section

Use `<section>` to group related content:

```html
<main class="container">
  <section>
    <h2>Features</h2>
    <p>Description of features...</p>
  </section>
  
  <section>
    <h2>Pricing</h2>
    <p>Pricing information...</p>
  </section>
  
  <section>
    <h2>Contact</h2>
    <p>Get in touch...</p>
  </section>
</main>
```

### Article

Use `<article>` for self-contained compositions:

```html
<div class="grid">
  <article>
    <h3>Blog Post 1</h3>
    <time datetime="2024-01-15">January 15, 2024</time>
    <p>Excerpt from the first post...</p>
    <a href="/post/1">Read more</a>
  </article>
  
  <article>
    <h3>Blog Post 2</h3>
    <time datetime="2024-01-10">January 10, 2024</time>
    <p>Excerpt from the second post...</p>
    <a href="/post/2">Read more</a>
  </article>
  
  <article>
    <h3>Blog Post 3</h3>
    <time datetime="2024-01-05">January 5, 2024</time>
    <p>Excerpt from the third post...</p>
    <a href="/post/3">Read more</a>
  </article>
</div>
```

## Overflow Auto

For scrollable content areas:

```html
<div class="overflow-auto">
  <table>
    <!-- Wide table that scrolls horizontally -->
  </table>
</div>
```

Or use the shorthand on elements:

```html
<table class="overflow-auto">
  <thead>
    <tr>
      <th>Column 1</th>
      <th>Column 2</th>
      <th>Column 3</th>
      <th>Column 4</th>
      <th>Column 5</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Data 1</td>
      <td>Data 2</td>
      <td>Data 3</td>
      <td>Data 4</td>
      <td>Data 5</td>
    </tr>
  </tbody>
</table>
```

## Spacing Customization

Customize spacing with CSS variables:

```css
:root {
  --pico-spacing: 1.5rem;
  --pico-block-spacing-vertical: 2rem;
  --pico-grid-column-gap: 1.5rem;
  --pico-grid-row-gap: 1.5rem;
}
```

## Responsive Behavior

Pico's layout elements are fully responsive:

- **Container**: Centers content with max-width, fluid on mobile
- **Grid**: Automatically adjusts columns (1 column on mobile, 2-4+ on larger screens)
- **Landmarks**: Stack vertically on mobile, maintain structure on desktop
- **Typography**: Scales font sizes based on viewport width

No media queries needed - everything is responsive by default.

## Complete Page Structure Example

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <link rel="stylesheet" href="css/pico.min.css">
  <title>Complete Page</title>
</head>
<body>
  <header class="container">
    <nav>
      <ul>
        <li><a href="/" aria-current="page">Home</a></li>
        <li><a href="/about">About</a></li>
        <li><a href="/services">Services</a></li>
        <li><a href="/contact">Contact</a></li>
      </ul>
    </nav>
  </header>

  <main class="container">
    <section>
      <hgroup>
        <h1>Welcome to Our Website</h1>
        <p>We build amazing products</p>
      </hgroup>
    </section>

    <section>
      <h2>Our Services</h2>
      <div class="grid">
        <article>
          <h3>Web Design</h3>
          <p>Beautiful, responsive websites</p>
        </article>
        <article>
          <h3>Development</h3>
          <p>Robust, scalable applications</p>
        </article>
        <article>
          <h3>Consulting</h3>
          <p>Expert advice and guidance</p>
        </article>
      </div>
    </section>

    <section>
      <h2>Contact Us</h2>
      <form>
        <fieldset class="grid">
          <input type="text" placeholder="Name" required>
          <input type="email" placeholder="Email" required>
          <button type="submit">Send Message</button>
        </fieldset>
      </form>
    </section>
  </main>

  <footer class="container">
    <p>&copy; 2024 Your Company. All rights reserved.</p>
  </footer>
</body>
</html>
```
