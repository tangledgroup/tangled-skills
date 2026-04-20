# D3 Shapes and Geometry

## Line Generator

```javascript
const line = d3.line()
    .x(d => xScale(d.date))
    .y(d => yScale(d.value))
    .defined(d => d.value !== null)   // Skip missing data
    .curve(d3.curveLinear)            // Interpolation
    .context(null);                   // Canvas context (optional)

const path = line(data);
// → "M0,100 L50,80 L100,40 ..."
```

### Line Curves

| Curve | Description |
|-------|-------------|
| `curveLinear` | Linear interpolation (default) |
| `curveLinearClosed` | Linear closed curve |
| `curveBasis` | Open cubic B-spline |
| `curveBasisOpen` | Open cubic B-spline |
| `curveBasisClosed` | Closed cubic B-spline |
| `curveCardinal` | Cardinal spline |
| `curveCardinalOpen` | Open cardinal spline |
| `curveCardinalClosed` | Closed cardinal spline |
| `curveCatmullRom` | Catmull-Rom spline |
| `curveCatmullRomOpen` | Open Catmull-Rom spline |
| `curveCatmullRomClosed` | Closed Catmull-Rom spline |
| `curveMonotoneX` | Monotone cubic (x-axis) |
| `curveMonotoneY` | Monotone cubic (y-axis) |
| `curveBumpX` | B-spline (x-axis) |
| `curveBumpY` | B-spline (y-axis) |
| `curveBundle` | Bundle spline |
| `curveNatural` | Natural cubic spline |
| `curveStep` | Step before |
| `curveStepBefore` | Step before |
| `curveStepAfter` | Step after |

### Curve Configuration

```javascript
d3.curveBundle.beta(0.85);
d3.curveCardinal.tension(0.8);
d3.curveCatmullRom.alpha(0.5);
```

## Area Generator

```javascript
const area = d3.area()
    .x(d => xScale(d.date))
    .y0(height - marginBottom)     // Baseline
    .y1(d => yScale(d.value))      // Top
    .defined(d => d.value !== null)
    .curve(d3.curveMonotoneY);

const path = area(data);
```

### Defined Area

```javascript
const areaDefined = d3.area()
    .defined(d => d.y0 !== null && d.y1 !== null)
    .x0(d => xScale(d.date))
    .y0(d => yScale(d.y0))
    .x1(d => xScale(d.date))
    .y1(d => yScale(d.y1));
```

## Arc Generator

```javascript
const arc = d3.arc()
    .innerRadius(0)
    .outerRadius(100)
    .startAngle(0)
    .endAngle(Math.PI)
    .padAngle(0.02)
    .padRadius(50)
    .cornerRadius(3)
    .context(null);

const path = arc({value: 1});
```

### Arc Methods

```javascript
arc.centroid();         // → [x, y] center of arc
arc.startAngle(angle);
arc.endAngle(angle);
arc.innerRadius(radius);
arc.outerRadius(radius);
arc.cornerRadius(r);    // Rounded corners
arc.padAngle(degrees);
arc.padRadius(r);       // Radius for pad angle calculation
```

## Pie Generator

```javascript
const pie = d3.pie()
    .value(d => d.value)
    .sortValues((a, b) => b - a)
    .startAngle(0)
    .endAngle(2 * Math.PI)
    .padAngle(0.02);

const arcs = pie(data);
// → [{data: ..., index: 0, startAngle: 0, endAngle: 1.57, ...}]
```

## Stack Generator

```javascript
const stack = d3.stack()
    .keys(["A", "B", "C"])
    .order(d3.stackOrderAscending)
    .offset(d3.stackOffsetNone);

const stacked = stack(data);
// → [[[y0, y1], [y0, y1]], ...] for each series

// For defined stacking:
const stackDefined = d3.stack()
    .defined((d, key) => d[key] !== null);
```

### Stack Orders

| Order | Description |
|-------|-------------|
| `stackOrderAscending` | By first point value |
| `stackOrderDescending` | By first point value descending |
| `stackOrderInsideOut` | Alternating up/down from center |
| `stackOrderNone` | Input order |
| `stackOrderReverse` | Reverse input order |

### Stack Offsets

| Offset | Description |
|--------|-------------|
| `stackOffsetNone` | No offset (default) |
| `stackOffsetExpand` | Normalize to 0-1 |
| `stackOffsetSilhouette` | Center around zero |
| `stackOffsetWiggle` | Minimize wiggle for smooth lines |
| `stackOffsetDiverging` | Positive up, negative down |

## Symbol Generator

```javascript
const symbol = d3.symbol()
    .type(d3.symbolCircle)
    .size(d => Math.PI * (d.radius || 5) ** 2)
    .context(null);

symbol();
// → "M0,-5 L0,5 M-5,0 L5,0" for circle

// Symbol types:
d3.symbolCircle;
d3.symbolCross;
d3.symbolDiamond;
d3.symbolSquare;
d3.symbolStar;
d3.symbolTriangle;
d3.symbolWye;
d3.symbolAsterisk;
d3.symbolPlus;

// Fill vs stroke symbols:
d3.symbolsFill;    // All symbols filled
d3.symbolsStroke;  // All symbols stroked
```

## Radial Shapes

### Radial Line
```javascript
const lineRadial = d3.lineRadial()
    .angle(d => xScale(d.date))
    .radius(d => yScale(d.value));
```

### Radial Area
```javascript
const areaRadial = d3.areaRadial()
    .angle(d => xScale(d.date))
    .innerRadius(d => yScale(d.min))
    .outerRadius(d => yScale(d.max));
```

### Radial Link
```javascript
const linkRadial = d3.linkRadial()
    .angle(d => xScale(d.t))
    .radius(d => yScale(d.r));
```

## Path Generator

```javascript
const pathGen = d3.path();
pathGen.moveTo(10, 10);
pathGen.lineTo(50, 50);
pathGen.arc(100, 100, 20, 0, Math.PI * 2);
pathGen.closePath();

const svgPath = pathGen.toString();

// With context for Canvas
const canvas = document.createElement("canvas");
const ctx = canvas.getContext("2d");
pathGen.context(ctx);
```

## Polygon Utilities

```javascript
d3.polygonArea(polygon);           // Signed area
d3.polygonLength(polygon);        // Perimeter
d3.polygonCentroid(polygon);      // Centroid [x, y]
d3.polygonHull(polygon);          // Convex hull
d3.polygonContains(polygon, point);  // Point-in-polygon test
```

## Quadtree

```javascript
const quadtree = d3.quadtree()
    .x(d => d.x)
    .y(d => d.y)
    .extent([[0, 0], [width, height]]);

data.forEach(d => quadtree.add(d));
// Or: quadtree.addAll(data);

quadtree.cover(100, 100, 50);     // Add point with radius
quadtree.find(50, 50, 20);        // Find nearest to (50,50) within r=20
quadtree.visit(callback);         // Visit nodes
quadtree.remove(d);
quadtree.root;                     // Access root
```

## Delaunay and Voronoi

```javascript
const delaunay = d3.Delaunay.from(data, d => d.x, d => d.y);

// Or:
const delaunay = d3.delaunay(pointsArray);  // [[x,y], ...]

delaunay.hull(0);                        // Convex hull indices
delaunay.triangles();                     // Triangle index triples
delaunay.neighbors(i);                    // Neighbor indices
delaunay.find(x, y);                      // Find cell containing point

const voronoi = delaunay.voronoi([0, 0, width, height]);
voronoi.renderCell(i, pathGen);           // Render cell to path
voronoi.cellPolygon(i);                   // Get polygon coordinates
voronoi.contains(i, x, y);                // Check if point in cell
voronoi.neighbors(i);                     // Adjacent cell indices
```
