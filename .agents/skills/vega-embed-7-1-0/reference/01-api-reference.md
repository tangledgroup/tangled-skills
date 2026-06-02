# API Reference

## Contents
- embed() Function
- container() Function
- Result Type
- EmbedOptions Interface
- Actions Interface
- Hover Interface
- Patch Types
- Exported Symbols

## embed() Function

```ts
embed(el: HTMLElement | string, spec: VisualizationSpec | string, opts?: EmbedOptions): Promise<Result>
```

Embeds a Vega visualization component in a web page.

**Arguments:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `el` | `HTMLElement \| string` | DOM element or CSS selector for the container |
| `spec` | `VisualizationSpec \| string` | Vega/Vega-Lite spec object, or URL string to load from |
| `opts` | `EmbedOptions` | Optional configuration |

**Return:** `Promise<Result>` — resolves to a result object with `view`, `spec`, `vgSpec`, and `finalize`.

**Behavior:**
1. If `spec` is a string (URL), loads it via the Vega loader
2. Extracts `embedOptions` from `spec.usermeta.embedOptions` if present
3. Merges options: `opts` takes priority over `usermeta.embedOptions`
4. Auto-detects mode (`vega` or `vega-lite`) from `$schema` URL or spec structure
5. Compiles Vega-Lite to Vega if needed
6. Applies patches (JSON-Patch RFC6902, function, or loaded URL)
7. Renders via SVG (default) or Canvas
8. Adds action links and tooltip handler

**Auto-detection logic:**
- If `$schema` is present, parses it with `vega-schema-url-parser` to determine mode
- Otherwise checks for Vega-Lite keys (`mark`, `encoding`, `layer`, `hconcat`, `vconcat`, `facet`, `repeat`) → `"vega-lite"`
- Checks for Vega keys (`marks`, `signals`, `scales`, `axes`) → `"vega"`
- Falls back to `opts.mode` or `"vega"`

**Warnings:**
- Logs version mismatch between spec `$schema` and installed vega/vega-lite versions
- Warns if `mode` argument conflicts with parsed `$schema` library

## container() Function

```ts
container(spec: VisualizationSpec | string, opt?: EmbedOptions): Promise<HTMLDivElement & { value: View }>
```

Creates a promise to an HTML `<div>` element with the embedded visualization. The element has a `value` property holding the Vega View instance. Designed for Observable notebooks.

**Differences from embed():**
- Returns an HTML element, not a DOM container selector
- Default actions: `{ export: true, source: false, compiled: true, editor: true }` (vs embed's `{ export: {svg:true,png:true}, source: true, compiled: true, editor: true }`)
- Wraps the chart in a `<div class="vega-embed-wrapper">`

## Result Type

```ts
interface Result {
  view: View;           // The Vega view instance
  spec: VisualizationSpec;  // Input spec (Vega or Vega-Lite)
  vgSpec: VgSpec;       // Compiled and patched Vega spec
  embedOptions: EmbedOptions;  // Merged options used
  finalize: () => void;         // Cleanup function
}
```

## EmbedOptions Interface

```ts
interface EmbedOptions<S = string, R = Renderers> {
  bind?: HTMLElement | string;
  actions?: boolean | Actions;
  mode?: 'vega' | 'vega-lite';
  theme?: keyof Omit<typeof themes, 'version'>;
  defaultStyle?: boolean | string;
  logLevel?: number;
  logger?: Logger;
  loader?: Loader | LoaderOptions;
  renderer?: R;
  tooltip?: TooltipHandler | TooltipOptions | boolean;
  patch?: S | PatchFunc | Operation[];
  width?: number;
  height?: number;
  padding?: number | { left?: number; right?: number; top?: number; bottom?: number };
  scaleFactor?: number | { svg?: number; png?: number };
  config?: S | Config;
  sourceHeader?: string;
  sourceFooter?: string;
  editorUrl?: string;
  hover?: boolean | Hover;
  i18n?: Partial<typeof I18N>;
  downloadFileName?: string;
  formatLocale?: Record<string, unknown>;
  timeFormatLocale?: Record<string, unknown>;
  expressionFunctions?: ExpressionFunction;
  ast?: boolean;
  expr?: typeof expressionInterpreter;
  viewClass?: typeof View;
  forceActionsMenu?: boolean;
}
```

## Actions Interface

Controls the action links shown in the embed menu:

```ts
interface Actions {
  export?: boolean | { svg?: boolean; png?: boolean };
  source?: boolean;
  compiled?: boolean;
  editor?: boolean;
}
```

**Defaults:** `{ export: { svg: true, png: true }, source: true, compiled: true, editor: true }`

The `export` key can be:
- `true` — show both SVG and PNG export
- `false` — hide export
- `{ svg: boolean, png: boolean }` — control each format individually

## Hover Interface

```ts
interface Hover {
  hoverSet?: EncodeEntryName;
  updateSet?: boolean;
}
```

Controls hover event processing. Enabled for Vega by default, disabled for Vega-Lite.

## Patch Types

Specs can be modified before parsing via the `patch` option:

```ts
type PatchFunc = (spec: VgSpec) => VgSpec;
// Or: Operation[] from fast-json-patch (JSON-Patch RFC6902)
// Or: string URL to load a patch JSON file
```

When using Vega-Lite, the compiled Vega spec is patched.

## Exported Symbols

| Symbol | Type | Description |
|--------|------|-------------|
| `embed` | `Function` | Primary embed function |
| `container` | `Function` | Observable-compatible container function |
| `vega` | `Namespace` | The vega module (re-exported) |
| `vegaLite` | `Namespace` | The vega-lite module (or `window.vl` for backward compat) |
| `version` | `string` | Package version (`"7.1.0"`) |
| `DEFAULT_ACTIONS` | `Object` | Default actions configuration |
| `I18N` | `Object` | Default i18n strings |
| `guessMode` | `Function` | Auto-detect spec type from `$schema` or structure |
| `VisualizationSpec` | `type` | Union of Vega and Vega-Lite spec types |
| `Result` | `interface` | Return type of embed/container |
| `EmbedOptions` | `interface` | Configuration options |
| `Actions` | `interface` | Actions menu configuration |
| `Mode` | `type` | `'vega' \| 'vega-lite'` |
| `Config` | `type` | Vega or Vega-Lite config |
