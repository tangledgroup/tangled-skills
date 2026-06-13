# Usage and Embedding

## Embedding Vega-Lite

### Vega-Embed (Recommended)

```html
<script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-lite@6"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>

<div id="vis"></div>
<script>
  vegaEmbed('#vis', vlSpec);
</script>
```

Vega-Embed auto-adds export links (image, source, editor). Configure via options object.

### NPM

```sh
npm install vega vega-lite vega-embed
```

## Compilation to Vega

### JavaScript API

```js
var vgSpec = vegaLite.compile(vlSpec, {config: config, logger: logger, fieldTitle: fn}).spec;
```

### CLI Tools (via npx)

| Command | Output |
|---------|--------|
| `npx vl2vg spec.vl.json` | Vega JSON |
| `npx vl2png spec.vl.json` | PNG image |
| `npx vl2svg spec.vl.json` | SVG image |
| `npx vl2pdf spec.vl.json` | PDF document |

With `-p` flag for pretty-printed output.

## TypeScript

```ts
import {Config, TopLevelSpec, compile} from 'vega-lite';

const spec: TopLevelSpec = {
  $schema: 'https://vega.github.io/schema/vega-lite/v6.json',
  // ... spec
};

const config: Config = {bar: {color: 'firebrick'}};
const vegaSpec = compile(spec, {config}).spec;
```

## Debugging

1. **Validate schema** — use [Vega Editor](https://vega.github.io/editor/) for warnings
2. **Check logs** — Vega-Lite emits warnings via `console.log/warn`
3. **Step through** — use browser devtools with source maps
4. **Non-minified sources** — load from `/build/vega-lite.js` on jsDelivr for debugging

## Configuration System

```json
{
  "config": {
    "font": "Helvetica",
    "padding": 5,
    "background": "#f0f0f0",
    "axis": {"labelFontSize": 12},
    "axisX": {"grid": false},
    "axisQuantitative": {"tickCount": 10},
    "legend": {"labelFontSize": 12},
    "mark": {"tooltip": true, "invalid": "filter"},
    "bar": {"color": "#4c78a8", "cornerRadius": 3},
    "point": {"filled": true},
    "scale": {"barBandPaddingInner": 0.1},
    "range": {"category": ["#1f77b4", "#ff7f0e"]},
    "view": {"stroke": "transparent"},
    "concat": {"spacing": 20},
    "facet": {"spacing": 30},
    "title": {"fontSize": 14, "anchor": "middle"},
    "selection": {"point": {"toggle": "shiftKey"}},
    "style": {
      "label": {"align": "center", "dy": -5}
    }
  }
}
```

### Config Categories

| Category | Properties |
|----------|-----------|
| Top-level | `autosize`, `background`, `countTitle`, `fieldTitle`, `font`, `lineBreak`, `padding`, `tooltipFormat` |
| Format | `numberFormat`, `timeFormat`, `customFormatTypes` |
| Guides | `axis*`, `header`, `legend` |
| Marks | `mark`, `bar`, `circle`, `line`, etc. |
| Styles | Named style blocks invoked via `style` property |
| Scales | `scale`, `range` |
| View | `view`, `concat`, `facet`, `repeat` |

### Custom Format Types

Register expression functions and set `customFormatTypes: true` in config for custom formatters.

### Tooltip-Specific Formats

Use `tooltipFormat` in config for longer tooltip formats while keeping axis labels short.

## Invalid Data Handling

### Mark Invalid Modes

| Mode | Behavior |
|------|----------|
| `"filter"` | Exclude invalid values from marks and scales |
| `"break-paths"` | Break lines/areas at nulls, filter from scales |
| `"break-paths-show-domains"` | Break paths but include in scale domains |
| `"show"` | Include all data, render invalid at zero or minimum |

```json
{"mark": {"type": "line", "invalid": "break-paths"}}
```

### Scale Invalid Output

Override outputs for invalid values per channel:

```json
{
  "config": {
    "scale": {
      "invalid": {"color": "grey", "size": 10}
    }
  }
}
```

### Alternative Approaches

- **Conditional encoding:** `{"condition": [{"test": "isValid(datum.x)", ...}], "value": "grey"}`
- **Layering:** Separate layer for null data with different mark
- **Window transform:** Impute missing values with lag/lead

## Tooltips

### From Encoding (Default)

```json
{"mark": {"type": "bar", "tooltip": true}}
```

Shows all encoding fields.

### From Data Point

```json
{"mark": {"type": "bar", "tooltip": {"content": "data"}}}
```

Shows all underlying data fields.

### Via Tooltip Channel

Single field: `"tooltip": {"field": "b"}`

Multiple fields: `"tooltip": [{"field": "a"}, {"field": "b"}]`

Custom labels: `"tooltip": [{"field": "b", "title": "Value"}]`

### Images in Tooltips

Use `image` field name with Vega Tooltip plugin:

```json
{"tooltip": [{"field": "thumbnail", "type": "nominal", "title": "Image"}]}
```

Supports base64: `"data:image/png;base64,..."`.

### Disable Tooltips

Per view: `"tooltip": null` in mark or encoding.
Global: `{"config": {"mark": {"tooltip": null}}}`.

## Streaming Data

Use Vega's `view.change()` with named data sources:

```js
vegaEmbed('#chart', vlSpec).then(res => {
  setInterval(() => {
    const changeSet = vega
      .changeset()
      .insert(newData())
      .remove(t => t.x < minimumX);
    res.view.change('table', changeSet).run();
  }, 1000);
});
```

Specify data name in spec: `"data": {"name": "table"}`.

Configure `autosize` or call `view.resize()` to handle layout changes from new data.

## Getting Started Checklist

1. Define `$schema`: `'https://vega.github.io/schema/vega-lite/v6.json'`
2. Add `data` (inline values or URL)
3. Set `mark` type
4. Map fields to `encoding` channels
5. Customize with `config`, `title`, `width`/`height`
6. Embed with Vega-Embed

## Key Resources

- **Online Editor:** https://vega.github.io/editor/
- **Examples Gallery:** https://vega.github.io/vega-lite/examples/
- **Schema Reference:** https://vega.github.io/schema/vega-lite/v6.json
- **Vega-Lite Block Template:** https://bl.ocks.org/domoritz/455e1c7872c4b38a58b90df0c3d7b1b9
