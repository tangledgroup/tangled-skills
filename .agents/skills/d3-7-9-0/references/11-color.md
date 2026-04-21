# Color

> **Source:** https://d3js.org/d3-color, d3-interpolate, d3-scale-chromatic
> **Loaded from:** SKILL.md (via progressive disclosure)

## Color Spaces — d3-color

D3 provides representations for RGB, HSL, OKLCH, OKLab, CIELAB, CIELUV, and named colors.

### Creating Colors

```js
// From CSS color string
let c = d3.color("steelblue"); // {r: 70, g: 130, b: 180, opacity: 1}
c = d3.color("rgb(70, 130, 180)");
c = d3.color("#4682b4");
c = d3.color("hsl(207, 44%, 49%)");

// From components
c = d3.rgb(70, 130, 180);
c = d3.hsl(207, 0.44, 0.49);
c = d3.lab(52, -14, 26);
c = d3.lch(52, 29, 207);
c = d3.cubehelix().rotate(0).saturation(1).lightness(0.5);

// Named colors
d3.color("aliceblue"); // {r: 240, g: 248, b: 255}
```

### Color Conversion

```js
// Convert between color spaces
c = d3.hsl(c); // {h: 207.3, s: 0.44, l: 0.49, opacity: 1}
c = d3.lab(c); // {l: 52, a: -14, b: 26}
c = d3.lch(c); // {l: 52, c: 29, h: 207.3}
```

### Color Manipulation

```js
// Modify in place (returns this)
c.opacity = 0.5;
c.opacity *= 0.5;

// Brighten/darken (LAB space, returns new color)
c = d3.color("steelblue").brighter(2); // twice as bright
c = d3.color("steelblue").darker(2);   // half as bright

// Mix colors
c = d3.color("red").interpolate(d3.color("blue"))(0.5);
// or
c = d3.interpolate("red", "blue")(0.5);
```

### Color Output

```js
c.toString(); // "#4682b4"
c.formatHex(); // "#4682b4"
c.formatHex8(); // "#4682b4ff"
c.formatRgb(); // "rgb(70, 130, 180)"
c.formatHsl(); // "hsl(207.3, 44%, 49%)"
c.formatLch(); // "lch(52, 29, 207.3)"
```

## Interpolation — d3-interpolate

### Value Interpolation

```js
const i = d3.interpolate(0, 10);
i(0.5); // 5

// String interpolation
d3.interpolate("1em", "2em")(0.5); // "1.5em"

// Array interpolation
d3.interpolate([0, 0], [960, 500])(0.5); // [480, 250]

// Object interpolation
d3.interpolate({r: 0, g: 0}, {r: 255, g: 255})(0.5);
```

### Color Interpolation

```js
// Interpolate in specified color space
d3.interpolateRgb("red", "blue")(0.5); // in RGB
d3.interpolateHsl("red", "blue")(0.5); // in HSL (may go through black)
d3.interpolateLab("red", "blue")(0.5); // perceptually uniform
d3.interpolateCubehelix("red", "blue")(0.5);

// OKLCH (perceptually uniform, modern)
d3.interpolateOklch("red", "blue")(0.5);
```

### Interpolating Transforms

```js
d3.interpolateTransformSvg("translate(10, 20) scale(2)", "translate(30, 40) scale(1)")(0.5);
```

### Zoom Interpolation

```js
d3.interpolateZoom([view0, view1], [width, height])(t);
// Returns {k: scale, x: tx, y: ty} for smooth camera transitions
```

## Color Schemes — d3-scale-chromatic

### Categorical Schemes (for distinct categories)

```js
d3.schemeCategory10;       // 10 colors
d3.schemeTableau10;        // 10 colors
d3.schemeSet3;             // 12 colors (ColorBrewer)
d3.schemeSet2;             // 8 colors

// Access by count
d3.schemeCategory10[0];    // first 10 colors
```

### Cyclical Schemes (for sequential data with wraparound)

```js
d3.interpolateRainbow(t);      // 0 to 1, full spectrum
d3.interpolateSinebow(t);      // smoother variant

// Scheme arrays
d3.schemeRainbow;
d3.schemeSinebow;
```

### Diverging Schemes (for data with meaningful midpoint)

```js
d3.interpolateRdYlBu(-1);     // red-yellow-blue
d3.interpolateRdBu(-1);       // red-blue
d3.interpolatePiYG(-1);       // pink-green-yellow
d3.interpolateSpectral(-1);   // full spectral

// Scheme arrays (ColorBrewer)
d3.schemeRdYlBu[11];          // 11 stops
```

### Sequential Schemes (for ordered data)

```js
// Interpolators
d3.interpolateViridis(t);     // 0 to 1
d3.interpolatePlasma(t);
d3.interpolateInferno(t);
d3.interpolateMagma(t);
d3.interpolateCividis(t);     // colorblind-safe
d3.interpolateTurbo(t);

// Scheme arrays (ColorBrewer)
d3.schemeBlues[9];            // 9 stops, light to dark blue
d3.schemeGreens[9];
d3.schemeOrRd[9];
```

### Using Scales with Chromatic

```js
const color = d3.scaleSequential(d3.interpolateViridis)
  .domain([0, 100]);

const color = d3.scaleSequential(d3.interpolateRdYlBu)
  .domain([-1, 0, 1]); // diverging

const color = d3.scaleOrdinal(d3.schemeTableau10);
```

## Complete Color Example

```js
// Sequential color scale
const colorScale = d3.scaleSequential(d3.interpolateViridis)
  .domain([0, d3.max(data, d => d.value)]);

svg.selectAll("circle")
  .data(data)
  .join("circle")
  .attr("fill", d => colorScale(d.value));

// Diverging for deviation from mean
const mean = d3.mean(data, d => d.value);
const colorDiv = d3.scaleDiverging(d3.interpolateRdYlBu)
  .domain([d3.min(data, d => d.value - mean), 0, d3.max(data, d => d.value - mean)]);
```
