# Shapes and Paths

## Line Generators

Create SVG path data from a sequence of points:

```js
const line = d3.line()
    .x(d => x(d.date))
    .y(d => y(d.value))
    .defined(d => !isNaN(d.value))  // handle missing data
    .curve(d3.curveMonotoneX);      // smooth interpolation

// Generate path string
const pathData = line(data);

// Use with SVG
svg.append("path")
    .datum(data)
    .attr("fill", "none")
    .attr("stroke", "steelblue")
    .attr("stroke-width", 1.5)
    .attr("d", line);
```

**Curves** control interpolation between points:

- `curveLinear` — straight lines (default)
- `curveBasis` — smooth cubic basis spline
- `curveCardinal` — smooth cardinal spline with tension
- `curveCatmullRom` — Catmull-Rom spline
- `curveMonotoneX` / `curveMonotoneY` — monotone cubic, preserves trends
- `curveStep`, `curveStepBefore`, `curveStepAfter` — step interpolation
- `curveBumpX`, `curveBumpY` — bump (step with rounded corners)
- `curveNatural` — natural cubic spline

**Radial line** — same API but with angles and radii:

```js
const line = d3.radialLine()
    .angle(d => aScale(d.angle))
    .radius(d => rScale(d.value));
```

## Area Generators

Areas are like lines with a top and bottom boundary, producing filled regions:

```js
const area = d3.area()
    .x(d => x(d.date))
    .y0(height)           // baseline
    .y1(d => y(d.value))  // top edge
    .curve(d3.curveMonotoneX);

svg.append("path")
    .datum(data)
    .attr("fill", "steelblue")
    .attr("opacity", 0.2)
    .attr("d", area);
```

For stacked areas, combine with `d3.stack()` (see Stacks below).

**Radial area:**

```js
const area = d3.radialArea()
    .angle(d => aScale(d.angle))
    .innerRadius(d => rScale(d.inner))
    .outerRadius(d => rScale(d.outer));
```

## Arc Generators

For pie charts, donut charts, and radial visualizations:

```js
const arc = d3.arc()
    .innerRadius(30)
    .outerRadius(80);

// Generate path for a single arc
const pathData = arc({
    startAngle: 0,
    endAngle: Math.PI / 2,
    innerRadius: 30,
    outerRadius: 80
});

// With data binding (after pie layout)
svg.selectAll("path")
    .data(pie(data))
    .join("path")
    .attr("d", arc)
    .attr("fill", (d, i) => color(i));
```

**Arc transitions:**

```js
// Hover effect — expand arc outward
arc.outerRadius(d => d.data.value > threshold ? 100 : 80);

// Donut with varying inner radius
const arc = d3.arc()
    .innerRadius(d => Math.sqrt(d.data.value) * 2)
    .outerRadius(d => Math.sqrt(d.data.value) * 3);
```

## Pie and Stack Layouts

**Pie layout** — converts values to angles for arc rendering:

```js
const pie = d3.pie()
    .value(d => d.value)
    .sort(null)              // preserve data order
    .startAngle(0)
    .endAngle(Math.PI * 2);

const arcs = pie(data);
// Each arc has: data, index, value, startAngle, endAngle, padAngle
```

**Stack layout** — layers multiple series for stacked area/bar charts:

```js
const stack = d3.stack()
    .keys(["categoryA", "categoryB", "categoryC"])
    .order(d3.stackOrderNone)
    .offset(d3.stackOffsetNone);

// Input: array of objects with named properties
// Output: array of layers, each with stacked [y0, y1] values
const layers = stack(data);

// Render stacked areas
svg.selectAll("path")
    .data(layers)
    .join("path")
    .attr("fill", d => color(d.key))
    .attr("d", d3.area()
        .x(d => x(d.data.date))
        .y0(d => y(d[0]))
        .y1(d => y(d[1]))
        .curve(d3.curveMonotoneX));
```

Stack offsets: `stackOffsetNone` (baseline at 0), `stackOffsetExpand` (normalized to 1, 100%), `stackOffsetSilhouette` (centered), `stackOffsetWiggle` (minimize wobble).

Stack orders: `stackOrderNone`, `stackOrderAscending`, `stackOrderDescending`, `stackInsideOut`.

## Link Generators

For network diagrams and tree layouts:

```js
const link = d3.linkHorizontal()
    .x(d => d.y)
    .y(d => d.x);

// Or with source/target objects
const link = d3.linkHorizontal()
    .x(d => x(d.target.depth))
    .y(d => y(d.target.y));

svg.append("path")
    .datum(links)
    .attr("fill", "none")
    .attr("stroke", "#999")
    .attr("d", link);
```

**Radial links** for circular layouts:

```js
const link = d3.radialLink()
    .angle(d => d.angle)
    .radius(d => d.radius);
```

## Symbol Generators

Plot individual markers with various shapes:

```js
const symbol = d3.symbol()
    .type(d => d.shape)  // or a fixed type
    .size(100);

svg.selectAll("path")
    .data(data)
    .join("path")
    .attr("d", symbol)
    .attr("transform", d => `translate(${x(d.x)},${y(d.y)})`);
```

**Symbol types:** `symbolCircle`, `symbolCross`, `symbolDiamond`, `symbolSquare`, `symbolStar`, `symbolTriangle`, `symbolWye` (and their "Up" variants for triangle/wye).

Also available: `d3.symbols` (array of all types), `d3.symbolTypes` (cycle through types by index).

## Path API

The `d3.path` class generates SVG path strings programmatically, useful for Canvas rendering or custom shape generation:

```js
const path = new d3.Path();
path.moveTo(0, 0);
path.lineTo(100, 50);
path.arc(50, 50, 30, 0, Math.PI, false);
path.closePath();

const d = path.toString();  // SVG path data string

// For Canvas rendering
path.replay(context);  // replays commands to Canvas 2D context
```

The Path class supports: `moveTo`, `lineTo`, `quadraticCurveTo`, `bezierCurveTo`, `arcTo`, `arc`, `closePath`. It can be used as the `.context()` target for any shape generator.
