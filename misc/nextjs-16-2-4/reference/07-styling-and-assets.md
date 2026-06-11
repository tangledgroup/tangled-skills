# Styling and Assets

## CSS

Next.js provides several ways to style applications:

### Tailwind CSS

Tailwind CSS is the default in `create-next-app`. Configure via PostCSS:

```js
// postcss.config.mjs
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}
```

Import in global CSS:

```css
/* app/globals.css */
@import 'tailwindcss';
```

Import the CSS file in your root layout:

```tsx
// app/layout.tsx
import './globals.css'

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

### CSS Modules

Use `.module.css` files for scoped styles:

```css
/* app/components/button.module.css */
.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  background: blue;
  color: white;
}
```

```tsx
import styles from './button.module.css'

export default function Button() {
  return <button className={styles.btn}>Click</button>
}
```

### Global CSS

Import global CSS files in the root layout:

```tsx
// app/layout.tsx
import '../styles/global.css'

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

### External Stylesheets

Use the `<link>` tag in the root layout or the `next/font` helper.

### Sass

Next.js supports Sass/SCSS out of the box. Import `.scss` or `.sass` files like regular CSS:

```tsx
import '../styles/global.scss'
```

## Image Optimization

The `<Image>` component from `next/image` provides automatic optimization:

- Size optimization with modern formats (WebP, AVIF)
- Visual stability (prevents layout shift)
- Lazy loading with optional blur-up placeholders
- On-demand resizing for remote images

```tsx
import Image from 'next/image'

export default function Page() {
  return (
    <Image
      src="/profile.png"
      alt="Picture of the author"
      width={500}
      height={500}
    />
  )
}
```

### Local images

Store static files in the `public/` directory and reference from base URL:

```tsx
<Image src="/profile.png" alt="Author" width={500} height={500} />
```

### Statically imported images

Import directly for automatic width/height detection:

```tsx
import Image from 'next/image'
import ProfileImage from './profile.png'

export default function Page() {
  return <Image src={ProfileImage} alt="Author" />
}
```

### Remote images

Configure allowed domains in `next.config.js`:

```js
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.example.com',
      },
    ],
  },
}

module.exports = nextConfig
```

```tsx
<Image
  src="https://images.example.com/photo.jpg"
  alt="Remote photo"
  width={300}
  height={200}
/>
```

## Font Optimization

The `next/font` module automatically self-hosts fonts with zero layout shift:

### Google Fonts

```tsx
import { Inter } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
})

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
```

### Local fonts

```tsx
import { Geist, Geist_Mono } from 'next/font/google'

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
})

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
})

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body>{children}</body>
    </html>
  )
}
```

## Public Folder

The `public/` directory stores static assets served at the base URL:

```
my-app/
  public/
    images/
      logo.png     → /images/logo.png
    fonts/
      custom.woff2 → /fonts/custom.woff2
    data.json      → /data.json
```

Files in `public/` are not processed by Next.js build — they are served as-is.
