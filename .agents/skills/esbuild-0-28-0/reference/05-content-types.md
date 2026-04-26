# Content Types and Loaders

Each content type has an associated loader that tells esbuild how to interpret file contents. Default loaders are configured by file extension but can be overridden with the `loader` option.

## JavaScript (loader: `js`)

Default extensions: `.js`, `.cjs`, `.mjs`.

Supports all modern JavaScript syntax. Use `target` to control which features are transformed for older browsers.

**Always transformed:**
- Trailing commas in function parameter lists and calls (es2017)
- Numeric separators (esnext): `1_000_000`

**Conditionally transformed (based on target):**
- Exponentiation operator (`a ** b`) — below es2016
- Async functions — below es2017
- Async iteration/generators — below es2018
- Spread/rest properties — below es2018
- Optional catch binding — below es2019
- BigInt, optional chaining, nullish coalescing, import.meta — below es2020
- Logical assignment operators — below es2021
- Class fields, private methods/fields, static blocks, ergonomic brand checks — below es2022

**Always passed through (not transformed):**
- Top-level await, hashbang grammar, RegExp features (dotAll, lookbehind, named capture groups, unicode property escapes, match indices, set notation)

RegExp literals that are unsupported are transformed to `new RegExp()` constructor calls so you can bring your own polyfill.

### JavaScript Caveats

**ES5 is not well supported** — Transforming ES6+ to ES5 is not fully supported. Set `target` to `es5` to prevent esbuild from introducing ES6 syntax into ES5 code (e.g., `{x: x}` becoming `{x}`).

**Private member performance** — The `#name` transform uses `WeakMap`/`WeakSet`. Creating many instances of classes with private fields may cause GC overhead on V8, JavaScriptCore, and SpiderMonkey.

**Imports follow ESM behavior** — `import` statements are hoisted to the top of the file. You cannot modify global state before an import that needs it:

```js
// This does NOT work:
window.foo = {}
import './something-that-needs-foo'

// Do this instead:
import './assign-to-foo-on-window'
import './something-that-needs-foo'
```

**Avoid direct `eval` when bundling** — Direct `eval(x)` prevents scope hoisting, tree shaking, and minification. Use indirect eval `(0, eval)('x')` or `new Function('x')` instead.

**`toString()` on functions is not preserved** — esbuild inserts helper functions that break if you extract function source via `.toString()`.

## TypeScript (loader: `ts` or `tsx`)

Default extensions: `.ts`, `.tsx`, `.mts`, `.cts`.

esbuild parses and strips type annotations but does **not** perform type checking. Run `tsc --noEmit` separately for type checking.

**Type declarations parsed and ignored:** interfaces, type aliases, function signatures, ambient declarations, type-only imports/exports.

**TypeScript extensions converted to JavaScript:** namespaces, enums, const enums, generic type parameters, JSX with types, type casts, experimental decorators (requires `experimentalDecorators`), instantiation expressions, the `satisfies` operator, `const` type parameters.

### TypeScript Caveats

**Enable `isolatedModules` in tsconfig.json** — esbuild compiles each file independently without tracing type references across files.

**Enable `esModuleInterop` in tsconfig.json** — Disables legacy behavior where `import * as foo from 'foo'` is compiled to `const foo = require('foo')`.

**`emitDecoratorMetadata` is not supported** — esbuild does not replicate TypeScript's type system.

**.d.ts generation is not supported** — Use the TypeScript compiler for declaration files.

**The `tsx` loader is NOT a superset of `ts`** — They are partially incompatible. `<T>() => {}` parses differently with each loader. With `tsx`, write `<T,>(...) => {}` (note the trailing comma).

## JSX (loader: `jsx` or `tsx`)

Default extensions: `.jsx`, `.tsx`.

JSX is converted to function calls. Default factory is `React.createElement`:

```jsx
let button = <Button>Click me</Button>
// Becomes:
let button = React.createElement(Button, null, "Click me")
```

**Automatic JSX transform (React 17+):**

```bash
esbuild app.jsx --jsx=automatic
```

This generates import statements automatically. No manual `import React` needed.

**Using JSX with non-React libraries (e.g., Preact):**

```bash
esbuild app.jsx --jsx-factory=h --jsx-fragment=Fragment
```

Or configure in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "jsxFactory": "h",
    "jsxFragmentFactory": "Fragment"
  }
}
```

## JSON (loader: `json`)

Default extension: `.json`.

Parses JSON into a JavaScript object at build time. Exports as default export, with named exports for each top-level property:

```js
import object from './example.json'
import { version } from './package.json'  // Named export, tree-shakeable
```

**Import attribute:**

```js
import object from './example.data' with { type: 'json' }
```

## CSS (loader: `css`)

Default extensions: `.css`, `.module.css` (uses `local-css` loader for CSS modules).

CSS is a first-class content type — esbuild can bundle CSS directly without importing from JavaScript:

```bash
esbuild --bundle app.css --outfile=out.css
```

Supports `@import` resolution and `url()` references. Configure loaders for image/font files referenced in `url()`.

**CSS modules** — Files with `.module.css` extension use CSS modules by default, generating scoped class names and a JavaScript map of original-to-scoped names.

**Conditionally transformed CSS features:** nested declarations, modern RGB/HSL syntax, `inset` shorthand, `hwb()`, `lab()`/`lch()`, `oklab()`/`oklch()`, `color()`.

## Text (loader: `text`)

Loads file contents as a JavaScript string. Useful for loading templates or other text files.

**Import attribute:**

```js
import html from './template.html' with { type: 'text' }
```

## Binary (loader: `binary`)

Embeds binary file contents as a `Uint8Array`.

**Import attribute:**

```js
import data from './model.bin' with { type: 'base64array' }
```

## Base64 (loader: `base64`)

Encodes file contents as a base64 string.

## Data URL (loader: `dataurl`)

Embeds the file as a data URL string. Useful for inlining small images or fonts.

## External File (loader: `copy`)

Copies the file to the output directory and returns the output path. The file is not bundled into JavaScript.

## Empty File (loader: `empty`)

Replaces the file with an empty module. Useful for stubbing out platform-specific code.
