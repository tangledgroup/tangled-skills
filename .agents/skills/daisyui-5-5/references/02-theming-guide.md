# DaisyUI Theming Guide

This guide covers built-in themes, custom theme creation, and theme switching in DaisyUI 5.5.

## Built-in Themes

DaisyUI includes 27+ pre-designed themes:

| Theme | Description |
|-------|-------------|
| `light` | Clean light theme (default) |
| `dark` | Dark theme for low-light environments |
| `cupcake` | Pastel pink and purple theme |
| `bumblebee` | Yellow and black theme |
| `emerald` | Green-themed professional look |
| `corporate` | Blue business theme |
| `synthwave` | Neon retro-futuristic theme |
| `retro` | 80s inspired warm colors |
| `cyberpunk` | High contrast neon theme |
| `valentine` | Pink and red romantic theme |
| `halloween` | Orange and purple spooky theme |
| `garden` | Natural green theme |
| `forest` | Deep forest greens |
| `aqua` | Blue and cyan aquatic theme |
| `lofi` | Muted pastel colors |
| `pastel` | Soft pastel palette |
| `fantasy` | Magical purple and pink |
| `wireframe` | Grayscale wireframe style |
| `black` | Pure black theme |
| `luxury` | Gold and black elegant theme |
| `dracula` | Popular dark developer theme |
| `cmyk` | Print color model theme |
| `autumn` | Fall colors orange and brown |
| `business` | Professional blue theme |
| `acid` | High saturation neon theme |
| `lemonade` | Yellow and green fresh theme |
| `night` | Deep blue night theme |
| `coffee` | Brown coffee-inspired theme |
| `winter` | Cool blue and white theme |
| `dim` | Low contrast muted theme |
| `nord` | Arctic blue-gray theme |
| `sunset` | Orange and pink sunset theme |
| `caramellatte` | Warm brown caramel theme |
| `abyss` | Deep dark theme |
| `silk` | Smooth gradient theme |

## Enabling Themes

### Enable Specific Themes

```css
@plugin "daisyui" {
  themes: light --default, dark --prefersdark, cupcake, bumblebee;
}
```

### Enable All Built-in Themes

```css
@plugin "daisyui" {
  themes: light, dark, cupcake, bumblebee, emerald, corporate, synthwave,
    retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi,
    pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn,
    business, acid, lemonade, night, coffee, winter, dim, nord, sunset,
    caramellatte, abyss, silk;
}
```

### Setting Default Themes

```css
@plugin "daisyui" {
  /* bumblebee is default, synthwave is dark mode */
  themes: light, dark, cupcake, bumblebee --default, emerald, 
    corporate, synthwave --prefersdark;
}
```

## Applying Themes

### HTML Level (Global)

```html
<!DOCTYPE html>
<html data-theme="cupcake">
<head>
  <title>Cupcake Theme</title>
</head>
<body>
  <!-- All components use cupcake theme -->
</body>
</html>
```

### Element Level (Local)

```html
<html>
<body>
  <div data-theme="dark">
    <button class="btn btn-primary">Dark themed button</button>
  </div>
  
  <div data-theme="cupcake">
    <button class="btn btn-primary">Cupcake themed button</button>
  </div>
</body>
</html>
```

## Theme Switching

### JavaScript Theme Switcher

```html
<select class="select select-bordered" id="theme-select">
  <option value="light">Light</option>
  <option value="dark">Dark</option>
  <option value="cupcake">Cupcake</option>
  <option value="bumblebee">Bumblebee</option>
  <option value="emerald">Emerald</option>
</select>

<script>
  const themeSelect = document.getElementById('theme-select');
  
  // Set saved theme or default
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  themeSelect.value = savedTheme;
  
  // Update theme on selection
  themeSelect.addEventListener('change', (e) => {
    const theme = e.target.value;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  });
</script>
```

### Toggle Light/Dark Mode

```html
<button id="theme-toggle" class="btn btn-sm">
  🌙 Dark Mode
</button>

<script>
  const toggle = document.getElementById('theme-toggle');
  const html = document.documentElement;
  
  // Check system preference
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const currentTheme = localStorage.getItem('theme') || (prefersDark ? 'dark' : 'light');
  html.setAttribute('data-theme', currentTheme);
  
  toggle.addEventListener('click', () => {
    const isDark = html.getAttribute('data-theme') === 'dark';
    const newTheme = isDark ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    toggle.textContent = isDark ? '🌙 Dark Mode' : '☀️ Light Mode';
  });
</script>
```

### System Preference Detection

```javascript
// Detect system dark mode preference
const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

function applySystemTheme() {
  const isDark = mediaQuery.matches;
  document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
}

// Apply on load
applySystemTheme();

// Listen for changes
mediaQuery.addEventListener('change', applySystemTheme);
```

## Custom Themes

### Creating a Custom Theme

Custom themes are defined using CSS variables in the plugin configuration:

```css
@plugin "daisyui" {
  @plugin "daisyui/theme" {
    name: "mytheme";
    default: true;
    prefersdark: false;
    color-scheme: light;
    
    /* Base colors */
    --color-base-100: oklch(98% 0.02 240);
    --color-base-200: oklch(95% 0.03 240);
    --color-base-300: oklch(92% 0.04 240);
    --color-base-content: oklch(20% 0.05 240);
    
    /* Brand colors */
    --color-primary: oklch(55% 0.3 240);
    --color-primary-content: oklch(98% 0.01 240);
    --color-secondary: oklch(70% 0.25 200);
    --color-secondary-content: oklch(98% 0.01 200);
    --color-accent: oklch(65% 0.25 160);
    --color-accent-content: oklch(98% 0.01 160);
    
    /* Neutral colors */
    --color-neutral: oklch(50% 0.05 240);
    --color-neutral-content: oklch(98% 0.01 240);
    
    /* Semantic colors */
    --color-info: oklch(70% 0.2 220);
    --color-info-content: oklch(98% 0.01 220);
    --color-success: oklch(65% 0.25 140);
    --color-success-content: oklch(98% 0.01 140);
    --color-warning: oklch(80% 0.25 80);
    --color-warning-content: oklch(20% 0.05 80);
    --color-error: oklch(65% 0.3 30);
    --color-error-content: oklch(98% 0.01 30);
    
    /* Border radius */
    --radius-selector: 1rem;
    --radius-field: 0.25rem;
    --radius-box: 0.5rem;
    
    /* Base sizes */
    --size-selector: 0.25rem;
    --size-field: 0.25rem;
    
    /* Other settings */
    --border: 1px;
    --depth: 1;
    --noise: 0;
  }
}
```

### Custom Theme with Hex Colors

Colors can use hex, rgb, or oklch formats:

```css
@plugin "daisyui/theme" {
  name: "mybrand";
  default: true;
  
  --color-base-100: #ffffff;
  --color-base-200: #f3f4f6;
  --color-base-300: #e5e7eb;
  --color-base-content: #1f2937;
  
  --color-primary: #3b82f6;
  --color-primary-content: #ffffff;
  
  --color-secondary: #8b5cf6;
  --color-secondary-content: #ffffff;
  
  --color-accent: #ec4899;
  --color-accent-content: #ffffff;
  
  --color-neutral: #6b7280;
  --color-neutral-content: #ffffff;
  
  --color-info: #06b6d4;
  --color-info-content: #ffffff;
  
  --color-success: #10b981;
  --color-success-content: #ffffff;
  
  --color-warning: #f59e0b;
  --color-warning-content: #1f2937;
  
  --color-error: #ef4444;
  --color-error-content: #ffffff;
}
```

### Custom Theme Options

| Option | Description | Values |
|--------|-------------|--------|
| `name` | Theme identifier (required) | Any string |
| `default` | Set as default theme | `true` or `false` |
| `prefersdark` | Set as dark mode theme | `true` or `false` |
| `color-scheme` | Browser UI color scheme | `light`, `dark`, or `light dark` |

### Required CSS Variables

All custom themes must include these variables:

**Base colors:**
- `--color-base-100` - Main background
- `--color-base-200` - Elevated surface
- `--color-base-300` - Higher elevation
- `--color-base-content` - Text on base

**Brand colors:**
- `--color-primary` and `--color-primary-content`
- `--color-secondary` and `--color-secondary-content`
- `--color-accent` and `--color-accent-content`

**Neutral:**
- `--color-neutral` and `--color-neutral-content`

**Semantic:**
- `--color-info` and `--color-info-content`
- `--color-success` and `--color-success-content`
- `--color-warning` and `--color-warning-content`
- `--color-error` and `--color-error-content`

### Border Radius Variables

```css
--radius-selector: 1rem;    /* Checkbox, toggle, badge */
--radius-field: 0.25rem;    /* Button, input, select, tab */
--radius-box: 0.5rem;       /* Card, modal, alert */
```

Recommended values: `0rem`, `0.25rem`, `0.5rem`, `1rem`, `2rem`

### Size Variables

```css
--size-selector: 0.25rem;   /* Base size of selectors */
--size-field: 0.25rem;      /* Base size of fields */
--border: 1px;              /* Border thickness */
--depth: 1;                 /* 0 or 1 - adds shadow and 3D effect */
--noise: 0;                 /* 0 or 1 - adds grain effect */
```

## Theme Generator

Use the [DaisyUI Theme Generator](https://daisyui.com/theme-generator/) visual tool to create custom themes interactively.

## Multi-Theme Configuration Example

Complete configuration with multiple themes:

```css
@import "tailwindcss";

@plugin "daisyui" {
  /* Enable all themes */
  themes: light, dark, cupcake, bumblebee --default, emerald, 
    corporate, synthwave --prefersdark, retro, cyberpunk, 
    valentine, halloween, garden, forest, aqua, lofi, pastel, 
    fantasy, wireframe, black, luxury, dracula, cmyk, autumn, 
    business, acid, lemonade, night, coffee, winter, dim, nord, 
    sunset, caramellatte, abyss, silk;
  
  /* Theme root selector */
  root: ":root";
  
  /* Include all components (default) */
  include: ;
  
  /* Exclude specific components */
  exclude: rootscrollgutter, checkbox;
  
  /* Add prefix to all classes */
  prefix: daisy-;
  
  /* Disable console logs */
  logs: false;
}

/* Custom theme */
@plugin "daisyui/theme" {
  name: "mybrand";
  default: true;
  
  --color-base-100: #ffffff;
  --color-base-200: #f9fafb;
  --color-base-300: #e5e7eb;
  --color-base-content: #111827;
  
  --color-primary: #2563eb;
  --color-primary-content: #ffffff;
  
  --color-secondary: #7c3aed;
  --color-secondary-content: #ffffff;
  
  --color-accent: #db2777;
  --color-accent-content: #ffffff;
  
  --color-neutral: #4b5563;
  --color-neutral-content: #ffffff;
  
  --color-info: #0891b2;
  --color-info-content: #ffffff;
  
  --color-success: #059669;
  --color-success-content: #ffffff;
  
  --color-warning: #d97706;
  --color-warning-content: #ffffff;
  
  --color-error: #dc2626;
  --color-error-content: #ffffff;
}
```

## Theme Best Practices

1. **Use built-in themes first** - They're well-tested and accessible
2. **Ensure contrast ratios** - Content colors should have sufficient contrast
3. **Test in both light and dark** - Verify readability in all modes
4. **Save user preference** - Use localStorage to remember theme choice
5. **Respect system preference** - Default to `prefers-color-scheme` if no saved preference
6. **Provide theme switcher** - Let users choose their preferred theme
7. **Keep custom themes minimal** - Override only necessary variables

## Debugging Themes

### Check Active Theme

```javascript
console.log(document.documentElement.getAttribute('data-theme'));
```

### Inspect CSS Variables

```javascript
const styles = getComputedStyle(document.documentElement);
console.log(styles.getPropertyValue('--color-primary'));
console.log(styles.getPropertyValue('--color-base-100'));
```

### Verify Theme is Loaded

Check browser dev tools for CSS variables under the `:root` or `html[data-theme="..."]` selector.
