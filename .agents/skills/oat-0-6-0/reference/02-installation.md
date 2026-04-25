# Oat UI - Installation and Setup

Multiple installation methods available depending on your project needs.

## Method 1: CDN (Fastest, No Build)

### Using unpkg (Recommended)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My Oat App</title>
  
  <!-- Oat CSS -->
  <link rel="stylesheet" href="https://unpkg.com/@knadh/oat/oat.min.css">
  
  <!-- Your custom CSS (after oat) -->
  <link rel="stylesheet" href="custom.css">
</head>
<body>
  <!-- Your content -->
  <h1>Hello Oat</h1>
  <button>Click me</button>
  
  <!-- Oat JS (with defer) -->
  <script src="https://unpkg.com/@knadh/oat/oat.min.js" defer></script>
</body>
</html>
```

### Using jsDelivr Alternative

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@knadh/oat@0.6.0/oat.min.css">
<script src="https://cdn.jsdelivr.net/npm/@knadh/oat@0.6.0/oat.min.js" defer></script>
```

### Version Pinning

Pin to specific version for production stability:

```html
<link rel="stylesheet" href="https://unpkg.com/@knadh/oat@0.6.0/oat.min.css">
<script src="https://unpkg.com/@knadh/oat@0.6.0/oat.min.js" defer></script>
```

**Pros:**
- Zero setup, works immediately
- No build process needed
- CDN caching for faster loads
- Easy to test and prototype

**Cons:**
- Requires internet connection
- Dependency on external CDN
- Slightly slower initial load than local files

## Method 2: npm (For Bundled Projects)

### Installation

```bash
npm install @knadh/oat
```

### ES Modules Import

```javascript
// main.js or entry point
import '@knadh/oat/oat.min.css';
import '@knadh/oat/oat.min.js';

// Or import individual files
import '@knadh/oat/css/00-base.css';
import '@knadh/oat/css/01-theme.css';
import '@knadh/oat/css/components.css';
import '@knadh/oat/js/base.js';
```

### With Vite

```javascript
// vite.config.js
export default {
  // Oat works out of the box with Vite
}
```

```html
<!-- index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>My App</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

### With Webpack

```javascript
// webpack.config.js
const path = require('path');

module.exports = {
  entry: './src/index.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist')
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      }
    ]
  }
};
```

```javascript
// src/index.js
import '@knadh/oat/oat.min.css';
import '@knadh/oat/oat.min.js';
```

**Pros:**
- Version controlled in node_modules
- Works with bundlers and build tools
- Can tree-shake individual components
- Offline development

**Cons:**
- Requires Node.js and npm
- Build step needed for production
- Larger dev dependencies

## Method 3: Direct Download (Static Sites)

### Download Files

```bash
# Download minified CSS and JS
wget https://raw.githubusercontent.com/knadh/oat/refs/heads/gh-pages/oat.min.css
wget https://raw.githubusercontent.com/knadh/oat/refs/heads/gh-pages/oat.min.js

# Or using curl
curl -o oat.min.css https://raw.githubusercontent.com/knadh/oat/refs/heads/gh-pages/oat.min.css
curl -o oat.min.js https://raw.githubusercontent.com/knadh/oat/refs/heads/gh-pages/oat.min.js
```

### Include in Project

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>My Static Site</title>
  <link rel="stylesheet" href="./oat.min.css">
</head>
<body>
  <h1>Static Site with Oat</h1>
  <script src="./oat.min.js" defer></script>
</body>
</html>
```

### Git Clone (For Development)

```bash
git clone https://github.com/knadh/oat.git
cd oat

# Build minified files
make dist

# Files will be in root directory:
# - oat.min.css
# - oat.min.js
```

**Pros:**
- Fully offline, no dependencies
- Complete control over files
- Fastest load times (local files)
- Works with any static site generator

**Cons:**
- Manual updates when new versions release
- Need to manage file versions yourself

## Method 4: Selective Component Loading

For minimal bundle size, include only needed components:

### Required Base Files

```html
<!-- MUST include these first -->
<link rel="stylesheet" href="css/00-base.css">
<link rel="stylesheet" href="css/01-theme.css">
<script src="js/base.js" defer></script>
```

### Add Only Needed Components

```html
<!-- Only components you use -->
<link rel="stylesheet" href="css/buttons.css">
<link rel="stylesheet" href="css/forms.css">
<link rel="stylesheet" href="css/dialogs.css">

<script src="js/buttons.js" defer></script>
<script src="js/dialogs.js" defer></script>
```

### Component Files Available

CSS files in `css/` directory:
- `00-base.css` - Base styles (required)
- `01-theme.css` - Theme variables (required)
- `typography.css` - Headings, paragraphs, lists
- `buttons.css` - Button styles
- `forms.css` - Form element styles
- `dialogs.css` - Dialog/modal styles
- `dropdowns.css` - Dropdown menu styles
- `tabs.css` - Tab component styles
- `tables.css` - Table styles
- `cards.css` - Card component styles
- `grid.css` - Grid system
- `alerts.css` - Alert banner styles
- `toasts.css` - Toast notification styles
- `progress.css` - Progress bars and meters
- `spinners.css` - Loading spinners
- `skeletons.css` - Skeleton loaders
- `avatars.css` - Avatar components
- `badges.css` - Badge tags
- `sidebar.css` - Sidebar layout
- `utilities.css` - Utility classes

**Pros:**
- Minimal bundle size
- Only load what you need
- Faster initial page load

**Cons:**
- More file requests
- Manual component management
- Easy to forget dependencies

## Local Development Setup

### Prerequisites

For contributing or modifying Oat itself:

```bash
# Install Zola (static site generator for docs)
# See: https://www.getzola.org/documentation/getting-started/installation/

# Install esbuild (for bundling)
npm install -g esbuild
# or
cargo install esbuild
```

### Running Docs Site

```bash
# Clone repository
git clone https://github.com/knadh/oat.git
cd oat

# Start docs server
cd docs
zola serve

# Open http://localhost:1111
```

### Building After Changes

```bash
# After modifying CSS or JS files
make dist

# This runs esbuild to bundle and minify
# Demo site auto-updates with changes
```

## Verification

### Check Installation

After any installation method, verify Oat is working:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" href="oat.min.css">
</head>
<body>
  <h1>Test</h1>
  <button>Should be styled</button>
  
  <script src="oat.min.js" defer></script>
  <script>
    // Check if Oat loaded
    console.log('Oat version:', typeof ot !== 'undefined' ? 'loaded' : 'not loaded');
  </script>
</body>
</html>
```

Open in browser - button should have Oat styling.

### Browser Console Check

```javascript
// Should show Oat namespace
console.log(ot);  // { toast: { ... } }

// Check Web Components
console.log(customElements.get('ot-tabs'));  // Should exist
console.log(customElements.get('ot-dropdown'));  // Should exist
```

## Common Installation Issues

### CSS Not Loading

**Problem**: Elements not styled

**Solutions:**
- Check browser DevTools Network tab for 404 errors
- Verify CSS path is correct (relative vs absolute)
- Ensure CSS loads in `<head>` before content renders
- Clear browser cache and hard refresh (Ctrl+Shift+R)

### JavaScript Not Working

**Problem**: Dialogs, dropdowns, tabs not functioning

**Solutions:**
- Add `defer` attribute to script tag
- Check console for JavaScript errors
- Verify JS file path is correct
- Ensure JS loads after DOM (use defer or place at end of body)

### CDN Slow or Unavailable

**Problem**: CDN links slow in your region

**Solutions:**
- Download files locally (Method 3)
- Use different CDN (jsDelivr instead of unpkg)
- Self-host files on your server

### npm Import Errors

**Problem**: Module not found errors

**Solutions:**
- Verify `@knadh/oat` in package.json
- Run `npm install` again
- Check bundler config supports CSS imports
- Try importing from `node_modules/@knadh/oat/` directly

## Upgrade Path

### From CDN

Update version numbers in URLs:

```html
<!-- Old -->
<link rel="stylesheet" href="https://unpkg.com/@knadh/oat@0.5.0/oat.min.css">

<!-- New -->
<link rel="stylesheet" href="https://unpkg.com/@knadh/oat@0.6.0/oat.min.css">
```

### From npm

```bash
npm update @knadh/oat
# or
npm install @knadh/oat@latest
```

### From Downloaded Files

Download new versions and replace files:

```bash
wget -O oat.min.css https://raw.githubusercontent.com/knadh/oat/refs/heads/gh-pages/oat.min.css
wget -O oat.min.js https://raw.githubusercontent.com/knadh/oat/refs/heads/gh-pages/oat.min.js
```

## Next Steps

After installation:

1. **Explore Components**: See references/04-typography.md through references/12-navigation.md
2. **Try the Demo**: Visit https://oat.ink/demo for interactive examples
3. **Customize Theme**: Override CSS variables (references/03-customization.md)
4. **Build Recipes**: Compose components into widgets (references/13-recipes.md)
