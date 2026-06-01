# Square and Image Marks

## Square Marks

Square marks are like point marks but with shape fixed to `square` and filled by default.

### Basic Syntax

```json
{
  "data": {"url": "data/cars.json"},
  "mark": "square",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"}
  }
}
```

### Square Mark Properties

| Property | Type | Description |
|----------|------|-------------|
| `size` | number | Default mark size (area in pixels) |

### Scatterplot with Squares

```json
{
  "data": {"url": "data/cars.json"},
  "mark": "square",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"},
    "color": {"field": "Origin", "type": "nominal"}
  }
}
```

### Square Config

```json
{
  "config": {
    "square": {"size": 50, "opacity": 0.7}
  }
}
```

---

## Image Marks

Image marks embed external images (PNG, JPG, etc.) in visualizations, loaded from URLs.

### Basic Syntax

```json
{
  "data": {"values": [
    {"x": 10, "y": 20, "img": "https://example.com/photo.png"}
  ]},
  "mark": "image",
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "url": {"field": "img"}
  }
}
```

### Image Mark Properties

| Property | Type | Description |
|----------|------|-------------|
| `url` | string | Image URL (constant) |
| `aspect` | boolean | Maintain aspect ratio (default `true`) |
| `align` | number | Alignment within cell (0-1) |
| `baseline` | string | Vertical baseline alignment |

### Scatterplot with Images

Embed images at data positions:

```json
{
  "data": {"url": "data/data.json"},
  "mark": "image",
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "url": {"field": "image_url"}
  }
}
```

### Image Config

```json
{
  "config": {
    "image": {"aspect": false, "align": 0.5}
  }
}
```
