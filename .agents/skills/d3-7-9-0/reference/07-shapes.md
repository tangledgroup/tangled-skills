# Shapes

> **Source:** https://d3js.org/d3-shape
> **Loaded from:** SKILL.md (via progressive disclosure)

Shape generators produce SVG path `d` attributes from data. Each exposes accessors to control how input data maps to visual representation.

## Line Generator — d3.line()

Generates a line SVG path from an array of points.

```js
const line = d3.line()
  .x(d => x(d.date))
  .y(d => y(d.value))
  .defined(d => !isNaN(d.value));

path.attr("d", line(data));
```

**Accessors:**
- `.x([value])` — x-coordinate accessor (default: `d[0]`)
- `.y([value])` — y-coordinate accessor (default: `d[1]`)
- `.defined([check])` — check for valid data points
- `.curve([curve])` — set the curve interpolation (see below)
- `.basis()`, `.basisOpen()`, `.basisClosed()` — B-spline curves
- `.cardinal()`, `.cardinalOpen()` — Catmull-Rom splines
- `.monotone()` — shape-preserving cubic

## Area Generator — d3.area()

Generates an area SVG path (closed shape).

```js
const area = d3.area()
  .x(d => x(d.date))
  .y0(height)
  .y1(d => y(d.value));

path.attr("d", area(data));

// Two-y approach (stacked)
const area = d3.area()
  .x(d => x(d.date))
  .y0(d => y(d[0]))
  .y1(d => y(d[1]));
```

**Accessors:**
- `.x0()`, `.x1()` — inner and outer x-coordinates
- `.y0()`, `.y1()` — inner and outer y-coordinates (y0 defaults to 0)
- `.defined([check])` — check for valid data

## Arc Generator — d3.arc()

Generates arc/path data for pie charts, donuts, and annular sectors.

```js
const arc = d3.arc()
  .innerRadius(0)
  .outerRadius(100)
  .startAngle(0)
  .endAngle(Math.PI * 2);

path.attr("d", arc(data));

// Donut chart
const outerArc = d3.arc().innerRadius(radius).outerRadius(radius + 50);
const innerArc = d3.arc().innerRadius(radius).outerRadius(radius);
```

**Accessors:**
- `.innerRadius([radius])` — inner radius (default: 0)
- `.outerRadius([radius])` — outer radius (default: 100)
- `.startAngle([angle])` — start angle in radians
- `.endAngle([angle])` — end angle in radians
- `.padAngle([angle])` — pad angle between arcs
- `.padRadius([radius])` — pad radius for consistent padding
- `.centroid(data)` — compute arc center point

## Pie Generator — d3.pie()

Converts data to angles for pie/donut charts.

```js
const pie = d3.pie()
  .value(d => d.value)
  .sortValues(null)
  .padAngle(0.02);

const arcs = pie(data);
// [{data: {...}, startAngle: 0, endAngle: 1.2, ...}, …]
```

**Accessors:**
- `.value([value])` — value accessor (default: identity)
- `.sortValues([compare])` — sort by value descending
- `.padAngle([angle])` — pad angle between slices

## Stack Generator — d3.stack()

Stacks multiple series for stacked area/bar charts.

```js
const stack = d3.stack()
  .keys(["Apple", "Banana", "Cherry"])
  .offset(d3.stackOffsetExpand)
  .order(d3.stackOrderAscending);

const stacks = stack(data);
// [[0, 30], [30, 70], [70, 100]] per x-value
```

**Accessors:**
- `.keys([keys])` — array of key names
- `.value([value])` — value accessor
- `.offset([offset])` — stacking offset (see below)
- `.order([order])` — stacking order (see below)

**Offset modes:**
- `d3.stackOffsetNone` — default, stack from zero
- `d3.stackOffsetExpand` — normalize to [0, 1]
- `d3.stackOffsetDiverging` — stack positive/negative separately
- `d3.stackOffsetSilhouette` — center around zero

**Order modes:**
- `d3.stackOrderNone`, `d3.stackOrderAscending`, `d3.stackOrderDescending`
- `d3.stackOrderInsideNorm`, `d3.stackOrderReverse`

## Symbol Generator — d3.symbol()

Generates SVG path data for symbols (shapes).

```js
const symbol = d3.symbol()
  .type(d3.symbolCircle)
  .size(400);

path.attr("d", symbol());
```

**Symbol types:**
- `d3.symbolCircle` — circle
- `d3.symbolCross` — cross
- `d3.symbolDiamond` — diamond
- `d3.symbolSquare` — square
- `d3.symbolStar` — star
- `d3.symbolTriangle` — triangle
- `d3.symbolWye` — Y shape

**Accessors:**
- `.type([type])` — symbol type (default: circle)
- `.size([size])` — area in square pixels (default: 64)

## Curve Interpolation

Curves control how points are connected. Set via `.curve()`:

| Curve | Description |
|-------|-------------|
| `d3.curveLinear` | Linear segments (default) |
| `d3.curveLinearClosed` | Linear closed path |
| `d3.curveStep` | Step function |
| `d3.curveStepBefore` | Step before point |
| `d3.curveStepAfter` | Step after point |
| `d3.curveBasis` | Open B-spline |
| `d3.curveBasisClosed` | Closed B-spline |
| `d3.curveCardinal` | Catmull-Rom spline |
| `d3.curveMonotoneX` | Shape-preserving cubic |
| `d3.curveBundle` | Straightened B-spline |

```js
const line = d3.line().curve(d3.curveBasis);
const area = d3.area().curve(d3.curveCardinal);
```

## Link Generators

### d3.linkHorizontal() / d3.linkVertical()

Generates SVG path data for horizontal or vertical links (L-shaped paths).

```js
const link = d3.linkHorizontal()
  .x(d => d.x)
  .y(d => d.y);

path.attr("d", link({source: {x: 0, y: 0}, target: {x: 100, y: 50}}));
```

### d3.linkRadial()

Generates radial arc paths for links in polar coordinates.

```js
const radialLink = d3.linkRadial()
  .radius(d => d.r)
  .angle(d => d.theta);
```

## Complete Line Chart Example

```js
const line = d3.line()
  .x(d => x(d.date))
  .y(d => y(d.value))
  .curve(d3.curveMonotoneY);

const area = d3.area()
  .x(d => x(d.date))
  .y0(height)
  .y1(d => y(d.value))
  .curve(d3.curveMonotoneY);

svg.append("path")
  .datum(data)
  .attr("fill", "none")
  .attr("stroke", "steelblue")
  .attr("d", area);

svg.append("path")
  .datum(data)
  .attr("fill", "none")
  .attr("stroke", "steelblue")
  .attr("stroke-width", 1.5)
  .attr("d", line);
```
