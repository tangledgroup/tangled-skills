# Options Reference

## Contents
- Spec Type
- Styling and Actions
- View Configuration
- Data Loading
- Spec Modification
- Dimensions
- Tooltips
- Interactivity
- Localization
- Extensibility

All options are passed as the third argument to `embed()` or `container()`, or embedded in the spec as `usermeta.embedOptions`.

## Spec Type

### mode
- **Type:** `"vega" | "vega-lite"`
- **Default:** Auto-detected from `$schema` URL, spec structure, or `"vega"`

Forces Vega-Embed to parse the spec as a specific type. If omitted, auto-detection parses the `$schema` URL via `vega-schema-url-parser`, or inspects keys (`mark`/`encoding` → vega-lite; `marks`/`signals` → vega).

## Styling and Actions

### theme
- **Type:** `keyof typeof themes` (from vega-themes)
- **Default:** none

Uses a theme from [Vega Themes](https://github.com/vega/vega-themes). Merges the theme config with any `config` option.

**Experimental:** themes may change in minor version updates.

### defaultStyle
- **Type:** `boolean | string`
- **Default:** `true`

If `true`, embed actions are shown in a styled menu. If `false`, uses simple links. If a string, sets a custom stylesheet (not supported via usermeta for security reasons).

### forceActionsMenu
- **Type:** `boolean`
- **Default:** `false`

Forces the actions to display as a `<details>` menu even when `defaultStyle` is `false`. Useful when defining custom menu styles in the parent application.

### actions
- **Type:** `boolean | Actions`

Controls action links: Export PNG/SVG, View Source, View Compiled Vega (Vega-Lite only), Open in Vega Editor.

| Sub-option | Type | Default | Description |
|------------|------|---------|-------------|
| `export` | `boolean \| { svg?: boolean; png?: boolean }` | `{ svg: true, png: true }` | Export actions |
| `source` | `boolean` | `true` | "View Source" link |
| `compiled` | `boolean` | `true` | "View Compiled Vega" (Vega-Lite only) |
| `editor` | `boolean` | `true` | "Open in Vega Editor" link |

Set to `false` to hide all actions. Set to `true` to show all with defaults.

### scaleFactor
- **Type:** `number \| { svg?: number; png?: number }`
- **Default:** `1`

Multiplier for exported image dimensions. Pass an object to set per-format scales: `{ svg: 2, png: 1 }`.

### downloadFileName
- **Type:** `string`
- **Default:** `"visualization"`

Filename for downloaded PNG/SVG exports.

### sourceHeader
- **Type:** `string`

HTML injected into the `<head>` of the "View Source" and "View Vega" pages. Use for syntax highlighting scripts (e.g., highlight.js).

### sourceFooter
- **Type:** `string`

HTML injected before the closing `</body>` tag of the "View Source" and "View Vega" pages.

### editorUrl
- **Type:** `string`
- **Default:** `"https://vega.github.io/editor/"`

URL for the "Open in Vega Editor" action. Uses HTML5 postMessage to pass spec data.

## View Configuration

### renderer
- **Type:** `"canvas" | "svg"`
- **Default:** `"svg"`

Rendering backend. See [Vega View docs](https://vega.github.io/vega/docs/api/view/#view_renderer).

### width
- **Type:** `number`
- **Default:** inherited from spec or container

View width in pixels. Note: Vega-Lite may override this option.

### height
- **Type:** `number`
- **Default:** inherited from spec or container

View height in pixels. Note: Vega-Lite may override this option.

### padding
- **Type:** `number \| { left?: number; right?: number; top?: number; bottom?: number }`

View padding in pixels.

### logLevel
- **Type:** `number`
- **Default:** `vega.Warn`

Log level from [Vega Logger](https://vega.github.io/vega/docs/api/view/#view_logLevel).

### logger
- **Type:** `LoggerInterface` (from vega-util)

Custom logger instance. Must support the full API of vega-util's `logger()` method.

### viewClass
- **Type:** `typeof View`

Custom class extending Vega `View` for custom rendering behavior.

## Data Loading

### loader
- **Type:** `Loader \| LoaderOptions`

Custom Vega loader or loader options. For passing credentials with data requests:

```ts
{ loader: { http: { credentials: 'same-origin' } } }
```

See [Vega View docs](https://vega.github.io/vega/docs/api/view/#view) for full loader options.

## Spec Modification

### config
- **Type:** `string \| Config`

Vega or Vega-Lite configuration to override defaults. Can be a URL string (loaded via loader) or a parsed config object.

When `theme` is also specified, the theme is merged with `config` (config takes priority).

### patch
- **Type:** `string \| PatchFunc \| Operation[]`

Modifies the Vega spec before parsing:
- **Function:** `(spec: VgSpec) => VgSpec` — transforms the spec
- **Operation[]:** JSON-Patch array per [RFC6902](https://tools.ietf.org/html/rfc6902)
- **String URL:** loads a patch file from a URL

When using Vega-Lite, the compiled Vega spec is patched.

## Dimensions

### width
See above under View Configuration.

### height
See above under View Configuration.

### padding
See above under View Configuration.

## Tooltips

### tooltip
- **Type:** `TooltipHandler \| TooltipOptions \| boolean`

Controls tooltip behavior:
- `false` — disable tooltips
- `true` or `{}` — use default vega-tooltip handler with defaults or custom options
- `Function` — custom tooltip handler per [Vega View API](https://vega.github.io/vega/docs/api/view/#view_tooltip)

## Interactivity

### hover
- **Type:** `boolean | Hover`

Enable/disable hover event processing. Enabled for Vega by default, disabled for Vega-Lite.

When an object:
| Property | Type | Description |
|----------|------|-------------|
| `hoverSet` | `EncodeEntryName` | Named encoding set to invoke on mouseover |
| `updateSet` | `EncodeEntryName` | Named encoding set to invoke on mouseout |

### bind
- **Type:** `string \| HTMLElement`

Element that should contain input elements bound to signals.

## Localization

### formatLocale
- **Type:** `Record<string, unknown>`

Number formatting locale definition. See [d3-format locale collection](https://github.com/d3/d3-format/tree/master/locale). Global setting.

### timeFormatLocale
- **Type:** `Record<string, unknown>`

Date/time formatting locale definition. See [d3-time-format locale collection](https://github.com/d3/d3-time-format/tree/master/locale). Global setting.

### i18n
- **Type:** `Partial<typeof I18N>`

Translations for action link text:

| Key | Default (English) |
|-----|-------------------|
| `COMPILED_ACTION` | `"View Compiled Vega"` |
| `EDITOR_ACTION` | `"Open in Vega Editor"` |
| `PNG_ACTION` | `"Save as PNG"` |
| `SOURCE_ACTION` | `"View Source"` |
| `SVG_ACTION` | `"Save as SVG"` |

## Extensibility

### expressionFunctions
- **Type:** `Record<string, Function \| { fn: Function; visitor?: any }>`

Custom Vega expression functions. Maps function names to implementations:
- Plain function: `vega.expressionFunction(name, fn)`
- With visitor: `vega.expressionFunction(name, fn, visitor)`

See [Vega Expression Functions](https://vega.github.io/vega/docs/api/extensibility/#expressionFunction).

### ast
- **Type:** `boolean`
- **Default:** `false`

Generate an Abstract Syntax Tree instead of native expressions. Slower but CSP-compliant (no `eval`).

### expr
- **Type:** `typeof expressionInterpreter`

Custom Vega expression interpreter, used when `ast: true`. Defaults to `vega-interpreter`'s `expressionInterpreter`.
