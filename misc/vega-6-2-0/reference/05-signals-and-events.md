# Signals & Events

## Contents
- Signal Definitions
- Built-in Signals
- Nested Signals
- Event Handlers
- Event Streams
- Event Stream Selectors
- Input Element Binding

## Signal Definitions

Signals are dynamic variables that parameterize a visualization. They update reactively in response to input events, external API calls, or upstream signal changes.

| Property | Type | Description |
|----------|------|-------------|
| `name` | String | **Required.** Unique signal name (valid JS identifier, no leading digit) |
| `value` | Any | Initial value (default: `undefined`) |
| `init` | Expression | ≥4.4 One-time initialization expression (mutually exclusive with `update`) |
| `update` | Expression | Re-evaluated expression; auto-reacts to upstream signals unless `react: false` |
| `react` | Boolean | Auto-re-evaluate when upstream signals change (default: `true`) |
| `on` | Handler[] | Array of event stream handlers for updating the signal |
| `bind` | Bind | Bind signal to external HTML input element |
| `description` | String | Text description for inline documentation |

Reserved signal names: `datum`, `event`, `item`, `parent`.

### Built-in Signals

| Signal | Description |
|--------|-------------|
| `width` / `height` | View dimensions (auto-defined from spec) |
| `padding` | View padding (auto-defined, ≥5.10) |
| `autosize` | Autosize settings (auto-defined, ≥5.10) |
| `background` | Background color (auto-defined, ≥5.10) |
| `cursor` | CSS mouse cursor for the entire view when set |

The `cursor` signal overrides mark-level cursor properties. Set to `"default"` to resume mark-based cursors.

### Nested Signals

Signals can be defined within group marks, accessible only within that group's scope. To update an outer-scope signal from a nested group:

```json
{
  "name": "outerSignal",
  "push": "outer"
}
```

Nested signal updates cannot include `value` or `update` properties.

## Event Handlers

An event handler captures events and updates a signal or mark encoding.

| Property | Type | Description |
|----------|------|-------------|
| `events` | EventStream | **Required.** Events to respond to |
| `update` | Expression | New signal value when events occur (required if no `encode`) |
| `encode` | String | Encoding set name to re-evaluate on the source mark (required if no `update`) |
| `force` | Boolean | Propagate even if signal value doesn't change (default: `false`) |

### Example: Count Clicks

```json
{
  "name": "count",
  "value": 0,
  "on": [
    {"events": "rect:mouseover", "update": "count + 1"}
  ]
}
```

### Example: Encode Set Toggle

```json
{
  "name": "clickEncode",
  "on": [
    {"events": "*:mousedown", "encode": "select"},
    {"events": "*:mouseup", "encode": "release"}
  ]
}
```

## Event Streams

Event streams capture sequences of input events (click, touch, timer ticks, signal updates).

### Event Stream Objects

| Property | Type | Description |
|----------|------|-------------|
| `source` | String | Event source: `"view"` (default), `"scope"`, `"window"`, or CSS selector |
| `type` | String | **Required.** Event type (see Supported Types below) |
| `markname` | String | Only monitor events from this mark name |
| `marktype` | String | Only monitor events from this mark type (`arc`, `rect`, etc.) |
| `filter` | Expression / Expression[] | Predicate expressions (cannot reference signals, only event properties) |
| `throttle` | Number | Min milliseconds between captured events (default: 0). For timer: interval in ms |
| `debounce` | Number | Min wait time before processing; restarts on new event |
| `consume` | Boolean | Call `event.preventDefault()` (default: `false`) |
| `between` | EventStream[] | Two-element array: sentinel start and end events |

### Supported DOM Event Types

`click`, `dblclick`, `dragenter`, `dragleave`, `dragover`, `keydown`, `keypress`, `keyup`, `mousedown`, `mousemove`, `mouseout`, `mouseover`, `mouseup`, `mousewheel`, `touchend`, `touchmove`, `touchstart`, `wheel`, `timer`.

### Event Stream Selectors

CSS-inspired shorthand syntax: `(source:)?type([filter])*({throttle(,debounce)?})?`

| Selector | Meaning |
|----------|---------|
| `mousedown` | All mousedown events |
| `*:mousedown` | Mousedown on marks (not view) |
| `rect:mousedown` | Mousedown on rect marks |
| `@foo:mousedown` | Mousedown on marks named 'foo' |
| `symbol:mousedown!` | Consume mousedown on symbol marks |
| `window:mousemove` | Mousemove from browser window |
| `mousemove{100}` | Throttle mousemove to 100ms |
| `mousemove{100, 200}` | Throttle 100ms + debounce 200ms |
| `timer{1000}` | Timer tick every 1000ms |
| `click[event.shiftKey]` | Click with shift key pressed |
| `[rect:mousedown, window:mouseup] > window:mousemove` | Drag events between mousedown/mouseup |

### Signal & Scale References

```json
// Signal reference
{"events": {"signal": "foo"}, "update": "..."}

// Combined signal + event
{"events": [{"signal": "foo"}, {"type": "click", "marktype": "rect"}], "update": "..."}

// Scale reference
{"events": {"scale": "xscale"}, "update": "..."}
```

## Input Element Binding

Bind signals to HTML form elements (two-way binding).

| Property | Type | Description |
|----------|------|-------------|
| `input` | String | **Required.** Input type: `checkbox`, `radio`, `range`, `select`, or any valid HTML input type |
| `element` | String | CSS selector for parent element (default: Vega view container) |
| `name` | String | Custom label for the input element |
| `debounce` | Number | Delay event handling in milliseconds |

### Range Input Properties
| Property | Type | Description |
|----------|------|-------------|
| `min` | Number | Minimum slider value (default: min of signal or 0) |
| `max` | Number | Maximum slider value (default: max of signal or 100) |
| `step` | Number | Slider increment (auto-determined if undefined) |

### Radio/Select Properties
| Property | Type | Description |
|----------|------|-------------|
| `options` | Array[] | **Required.** Array of selectable options |
| `labels` | String[] | ≥5.9 Label strings for each option |

### External Element Binding

Bind to an existing HTML element without generating new inputs:

```json
"bind": {
  "element": "#myInput",
  "event": "input",
  "debounce": 100
}
```
