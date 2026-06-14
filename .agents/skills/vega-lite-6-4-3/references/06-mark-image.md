# Image Mark Reference

The `image` mark renders images at specified positions. Useful for embedding logos, thumbnails, or visual markers in a chart.

## Basic Image

Use the `url` encoding channel to set image sources:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Scatter plot with image markers.",
  "data": {
    "values": [
      {"x": 0.5, "y": 0.5, "img": "data/ffox.png"},
      {"x": 1.5, "y": 1.5, "img": "data/gimp.png"},
      {"x": 2.5, "y": 2.5, "img": "data/7zip.png"}
    ]
  },
  "mark": {"type": "image", "width": 50, "height": 50},
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "url": {"field": "img", "type": "nominal"}
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
| `width` | auto | Image width in pixels |
| `height` | auto | Image height in pixels |

## Gotchas

- Images must be served with proper CORS headers if loaded from a different origin.
- The `url` encoding channel maps data fields to image URLs; use a constant `"value"` in the `url` encoding for a single shared image.
- Image marks are rect-based, so they share sizing properties with bar and rect marks.
- Large images can slow rendering — resize before embedding or use small thumbnails.
