# Image Mark Reference

The `image` mark renders images at specified positions. Useful for embedding logos, thumbnails, or visual markers in a chart.

## Basic Image

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Image mark at a fixed position.",
  "data": {"values": [{"x": 50, "y": 50}]},
  "mark": {
    "type": "image",
    "from": "https://example.com/logo.png"
  },
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"}
  }
}
```

## Images as Data Points

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Scatter plot with image markers.",
  "data": {
    "values": [
      {"category": "A", "value": 10, "icon": "https://example.com/a.png"},
      {"category": "B", "value": 20, "icon": "https://example.com/b.png"},
      {"category": "C", "value": 30, "icon": "https://example.com/c.png"}
    ]
  },
  "mark": {
    "type": "image",
    "width": 24,
    "height": 24
  },
  "encoding": {
    "x": {"field": "category", "type": "nominal"},
    "y": {"field": "value", "type": "quantitative"},
    "url": {"field": "icon"}
  }
}
```

## Key Channels

| Channel | Role |
|---|---|
| `x`, `y` | Position of the image |
| `url` | Image source URL |
| `width`, `height` | Display dimensions in pixels |

## Mark Properties

| Property | Default | Description |
|---|---|---|
| `from` | — | Direct image URL (alternative to encoding `url`) |
| `width` | auto | Image width in pixels |
| `height` | auto | Image height in pixels |

## Gotchas

- Images must be served with proper CORS headers if loaded from a different origin.
- The `url` encoding channel maps data fields to image URLs; the `from` mark property sets a single URL for all marks.
- Image marks are rect-based, so they share sizing properties with bar and rect marks.
- Large images can slow rendering — resize before embedding or use small thumbnails.
