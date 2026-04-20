# D3 Color and Interpolation

## Color Spaces (d3-color)

### Creating Colors

```javascript
// RGB
const rgb = d3.rgb(255, 128, 0);
rgb.formatHex();     // → "#ff8000"
rgb.formatRgb();     // → "rgb(255, 128, 0)"
rgb.formatHsl();     // → "hsl(30°, 100%, 50%)"
rgb.opacity;         // → 1 (0 to 1)

// HSL
const hsl = d3.hsl(30, 1, 0.5);

// Lab
const lab = d3.lab(50, 20, -30);

// HCL
const hcl = d3.hcl(60, 40, 50);

// Cubehelix
const cubehelix = d3.cubehelix(0.5, 0.8, 0.6);

// Gray
d3.gray(0.5);        // → gray(50%)
```

### Color Operations

```javascript
const color = d3.rgb("steelblue");

color.brighter(2);    // Make 2x brighter
color.darker(1);      // Make 1x darker
color.opacity(0.5);   // Set opacity
color.copy();         // Shallow copy

// Check if displayable
color.displayable();  // → true/false

// Parse any CSS color
d3.color("rebeccapurple");
```

### Color Conversion

```javascript
// All colors can convert to all spaces
const rgb = d3.rgb("#ff8000");
rgb.formatHsl();       // → "hsl(30°, 100%, 50%)"
rgb.formatHex();       // → "#ff8000"
rgb.formatHex8();      // → "#ff8000ff"
rgb.toString();        // → "rgb(255, 128, 0)"

// RGB clamp values to [0, 255]
d3.rgb_clamp = true;   // Default

// HSL clamp saturation and lightness
d3.hsl_clamp = true;
```

## Interpolation (d3-interpolate)

### Value Interpolation

```javascript
// Numbers
d3.interpolate(0, 100)(0.5);       // → 50
d3.interpolateNumber(a, b);        // Same as interpolate

// Dates
const d1 = new Date(2020, 0, 1);
const d2 = new Date(2024, 0, 1);
d3.interpolateDate(d1, d2)(0.5);   // → 2022-06-30

// Strings (interpolates embedded numbers)
d3.interpolateString("M0,0 L10,10", "M0,10 L10,0")(0.5);

// Arrays
d3.interpolateArray([1, 2], [3, 4])(0.5);  // → [2, 3]
d3.interpolateNumberArray(a, b);

// Objects
d3.interpolateObject({x: 0, y: 0}, {x: 100})(0.5);

// Booleans
d3.interpolate(false, true)(0.5);    // → true

// Round interpolation
d3.interpolateRound(0.4, 10.6)(0.5); // → 5 (rounded)

// Discrete
d3.interpolateDiscrete([0, 10, 20])(0.7);  // → 20

// Basis
d3.interpolateBasis([0, 10, 20, 30])(0.3);
d3.interpolateBasisClosed([0, 10, 20, 0]);
```

### Color Interpolation

```javascript
// All color spaces available
d3.interpolateRgb("steelblue", "red")(0.5);
d3.interpolateHcl("steelblue", "red")(0.5);
d3.interpolateLab("steelblue", "red")(0.5);
d3.interpolateHsl("steelblue", "red")(0.5);
d3.interpolateCubehelix("steelblue", "red")(0.5);

// Long-form (avoids gamma correction)
d3.interpolateHclLong("steelblue", "red")(0.5);
d3.interpolateHslLong("steelblue", "red")(0.5);
d3.interpolateCubehelixLong("steelblue", "red")(0.5);

// Hue interpolation (shortest path around color wheel)
d3.interpolateHue("red", "cyan")(0.5);
```

### Transform & Zoom Interpolation

```javascript
// SVG transform
d3.interpolateTransformSvg("translate(10,20)", "translate(100,200)")(0.5);
d3.interpolateTransformCss("scale(1)", "scale(2)")(0.5);

// Zoom (preserves aspect ratio)
d3.interpolateZoom([x0, y0, r0], [x1, y1, r1])(t);
```

### Piecewise & Quantized Interpolation

```javascript
// Piecewise: interpolate between multiple values
const colors = d3.piecewise(d3.interpolateRgb, ["#f00", "#0f0", "#00f"]);
colors(0.25);  // → intermediate between red and green

// Quantize: divide range into n segments
d3.quantile(interpolator, 10);
```

## Color Interpolators for Scales

### Sequential (used with d3-scale-sequential)

| Interpolator | Description |
|-------------|-------------|
| `interpolateViridis` | Perceptually uniform (default recommended) |
| `interpolatePlasma` | Perceptually uniform, high contrast |
| `interpolateInferno` | Perceptually uniform, warm tones |
| `interpolateMagma` | Perceptually uniform, dark-to-light |
| `interpolateCividis` | Colorblind-friendly |
| `interpolateTurbo` | Vibrant, perceptually ordered |

### Sequential Diverging

| Interpolator | Description |
|-------------|-------------|
| `interpolateBlues` | Blue shades |
| `interpolateGreens` | Green shades |
| `interpolateOranges` | Orange shades |
| `interpolateReds` | Red shades |
| `interpolateGreys` | Gray shades |
| `interpolatePuBu` | Purple to blue |
| `interpolateBuPu` | Blue to purple |
| `interpolateYlGn` | Yellow to green |
| `interpolateRdPu` | Red to purple |
| `interpolateYlOrRd` | Yellow to red |

### Diverging (centered)

| Interpolator | Description |
|-------------|-------------|
| `interpolateRdBu` | Red-blue (default diverging) |
| `interpolateRdYlBu` | Red-yellow-blue |
| `interpolateBrBG` | Brown-purple-green |
| `interpolatePiYG` | Pink-yellow-green |
| `interpolatePRGn` | Purple-green |
| `interpolateSpectral` | Spectral (rainbow-like) |
| `interpolateRdGy` | Red-gray |

### Cyclical

| Interpolator | Description |
|-------------|-------------|
| `interpolateRainbow` | Rainbow (avoid for data!) |
| `interpolateSinebow` | Sine-wave color wheel |

### Categorical Schemes

```javascript
// 10 colors
d3.schemeCategory10;        // ["#1f77b4", "#ff7f0e", ...]
d3.schemeTableau10;         // ["#4e79a7", "#f28e2c", ...]
d3.schemeObservable10;      // Observable's curated 10
d3.schemeAccent;             // 8 colors
d3.schemePaired;             // 12 colors (6 pairs)
d3.schemePastel1;            // 9 colors
d3.schemePastel2;            // 8 colors
d3.schemeSet1;               // 9 colors
d3.schemeSet2;               // 8 colors
d3.schemeSet3;               // 12 colors
```

## Using Interpolators with Scales

```javascript
// Sequential scale with color interpolator
const colorScale = d3.scaleSequential(d3.interpolateViridis)
    .domain([0, d3.max(data, d => d.value)]);

// Diverging scale
const diverging = d3.scaleDiverging(d3.interpolateRdBu)
    .domain([-100, 0, 100]);

// Sequential with scheme
const sequential = d3.scaleSequential(d3.schemeOranges[7])
    .domain([0, 6]);

// Custom interpolator
d3.scaleSequential(d3.piecewise(d3.interpolateRgb, ["#f00", "#ff0", "#0f0"]));
```
