# Additional Modules

> **Source:** https://d3js.org
> **Loaded from:** SKILL.md (via progressive disclosure)

## d3-dispatch — Event Dispatching

Low-level event system for registering named callbacks.

```js
const dispatch = d3.dispatch("start", "drag", "end");

dispatch.on("start", callback1);
dispatch.on("start.foo", callback2); // namespaced
dispatch.on("drag", callback3);

dispatch.call("start", context, arg1, arg2);
```

## d3-timer — Animation Timer

High-precision timer for animation loops. More efficient than `requestAnimationFrame` for multiple concurrent animations.

```js
import {timer, timerFlush} from "d3-timer";

// Create a timer
const t = timer(frame, 0); // start immediately, call frame() every frame

function frame(time) {
  // update state
  t.restart(frame); // reschedule
}

// Stop
t.stop();
```

**Functions:**
- `timer(fn, delay, time)` — create timer
- `timerFlush()` — flush all ready timers
- `timeout(fn, delay, time)` — one-shot timer
- `interval(fn, delay, time)` — recurring timer

## d3-path — Path Serialization

Serialize SVG path commands to strings. More efficient than creating DOM elements.

```js
const p = new d3.Path();
p.moveTo(100, 200);
p.lineTo(300, 100);
p.arc(200, 200, 50, 0, Math.PI * 2);
p.closePath();

const pathString = p.toString(); // "M100,200L300,100A50,50,0,1,1,...Z"
```

## d3-polygon — Polygon Utilities

```js
d3.polygonArea(polygon);           // signed area
d3.polygonCentroid(polygon);       // center point
d3.polygonHull(polygon);          // convex hull
d3.polygonConvex(polygon);        // check if convex
d3.polygonContains(polygon, point); // point-in-polygon
```

## d3-quadtree — Quadtree

Spatial index for 2D points. Efficient nearest-neighbor search.

```js
const quadtree = d3.quadtree()
  .x(d => d.x)
  .y(d => d.y)
  .extent([[0, 0], [width, height]]);

quadtree.addAll(data);

// Search
quadtree.find();                    // nearest to center
quadtree.find(d.x, d.y);           // nearest to point
quadtree.visit((node, x0, y0, x1, y1) => { /* visit nodes */ });
```

## d3-delaunay — Delaunay Triangulation

Computes Delaunay triangulation and Voronoi diagram from points.

```js
const delaunay = d3.Delaunay.from(data.map(d => [d.x, d.y]));

// Nearest neighbor
delaunay.find(100, 200);  // index of nearest point

// Voronoi cell
delaunay.voronoi([[0, 0], [width, height]]).cellPolygon(i);

// Triangle
delaunay.triangle(i);     // indices of triangle vertices
```

## d3-contour — Density Contours

Compute contour polygons from a 2D grid or point cloud.

```js
const contours = d3.contours()
  .size([width, height])
  .thresholds(d3.range(0, 1, 0.1))(data);
// GeoJSON FeatureCollection
```

## d3-chord — Chord Diagrams

Draw chord diagrams for matrix/flow data.

```js
const chord = d3.chord()
  .padAngle(0.05)
  .sortSubgroups(d3.descending);

const chords = chord(matrix);
// [{source: {...}, target: {...}}, …]

const ribbon = d3.ribbon();
path.attr("d", ribbon(chord));
```

## d3-ease — Easing Functions

Available easings for transitions:

| Function | Description |
|----------|-------------|
| `d3.easeLinear` | Constant speed |
| `d3.easePoly` | Polynomial (`.exponent(n)`) |
| `d3.easeQuad` | Quadratic |
| `d3.easeCubic` | Cubic (default) |
| `d3.easeSin` | Sinusoidal |
| `d3.easeExp` | Exponential |
| `d3.easeCircle` | Circular |
| `d3.easeElastic` | Elastic oscillation |
| `d3.easeBack` | Overshoot |
| `d3.easeBounce` | Bounce |

```js
// Create custom easing
const ease = d3.easeElastic.amplitude(1).period(4);
transition.ease(ease);
```

## d3-quickselect — In-Place Selection

Finds the k-th smallest element in-place. O(n) average case.

```js
d3.quickselect(array, k);
d3.quickselectBy(array, k, accessor);
```

## d3-geo-projection (Community)

Extended projections not in core D3:
- `d3.geoAitoff()`
- `d3.geoAugmentedGnomonic()`
- `d3.geoGuyou()`
- And many more at https://github.com/d3/d3-geo-projection
