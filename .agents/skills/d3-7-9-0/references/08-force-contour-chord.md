# D3 Force, Contour, Chord, and Delaunay

## Force Simulation (d3-force)

### Creating a Simulation

```javascript
const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id))
    .force("charge", d3.forceManyBody())
    .force("center", d3.forceCenter(width / 2, height / 2))
    .on("tick", ticked);

function ticked() {
  links
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

  nodes
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);
}
```

### Simulation Control

```javascript
simulation.alpha();              // Current alpha (0-1)
simulation.alpha(0.5);           // Set alpha
simulation.alphaTarget(0.1);     // Target alpha
simulation.alphaDecay(0.0228);   // Per-tick decay rate
simulation.alphaMin(0.001);      // Minimum alpha
simulation.velocityDecay(0.4);   // Velocity dampening

simulation.nodes(array);         // Set nodes
simulation.force("name", force); // Add/replace force
simulation.force("name", null);  // Remove force
simulation.find(x, y, radius);   // Find nearest node
simulation.restart();            // Restart simulation
simulation.stop();               // Stop simulation
simulation.tick();               // Run one tick

// Events
simulation.on("tick", fn);
```

### Link Force

```javascript
d3.forceLink(links)
    .id(d => d.id)              // Key function (required for objects)
    .distance(100)              // Ideal link distance
    .strength(0.5)              // Link strength (0-1)
    .iterations(1);             // Convergence iterations
```

### Many-Body Force (Charge)

```javascript
d3.forceManyBody()
    .strength(-30)              // Negative = repulsion
    .distanceMin(1)             // Minimum distance
    .distanceMax(400)           // Maximum distance
    .theta(0.8);                // Barnes-Hut accuracy
```

### Center Force

```javascript
d3.forceCenter(x, y)
    .strength(0.3);
```

### Collide Force

```javascript
d3.forceCollide()
    .radius(d => d.radius + 2)
    .strength(0.7)
    .iterations(1);
```

### Position Forces (X, Y, Radial)

```javascript
// X position force
d3.forceX(xValue).strength(0.1);

// Y position force
d3.forceY(yValue).strength(0.1);

// Radial force (attract to center)
d3.forceRadial(radius, centerX, centerY)
    .strength(0.05);
```

### Disjoint Graphs

For disconnected components, add multiple center forces:

```javascript
const components = findComponents(nodes, links);
components.forEach((component, i) => {
  simulation.force(`center-${i}`,
    d3.forceCenter(d => component.includes(d) ? width/2 : d.x,
                   d => component.includes(d) ? height/2 : d.y)
       .strength(0.3));
});
```

## Contour Plots (d3-contour)

### Density Estimation

```javascript
const density = d3.contourDensity()
    .x(d => xScale(d.longitude))
    .y(d => yScale(d.latitude))
    .size([width, height])
    .bandwidth(5)           // Kernel bandwidth
    .thresholds(10)         // Number of contour levels
    .cellSize(2);           // Grid cell size

const contours = density(data);
// → [{value: 0.05, coordinates: [[[x,y],...]]}, ...]
```

### Contour Polygons

```javascript
// From a 2D grid of values
const contours = d3.contours()
    .size([width, height])
    .thresholds([0.1, 0.3, 0.5, 0.7, 0.9])
    .smooth(true);          // Post-process with Catmull-Rom

// Render to SVG
const path = d3.geoPath();
svg.selectAll("path")
    .data(contours)
    .join("path")
    .attr("d", path)
    .attr("fill", "none")
    .attr("stroke", "steelblue");
```

### Density Configuration

```javascript
d3.contourDensity()
    .x(d => d.x)
    .y(d => d.y)
    .weight(d => d.weight)     // Optional weight
    .size([width, height])
    .bandwidth(5)              // Gaussian kernel bandwidth
    .thresholds(10)            // Auto-thresholds
    .thresholds([0.1, 0.5, 0.9]) // Manual thresholds
    .cellSize(4);              // Grid resolution
```

## Chord Diagrams (d3-chord)

### Computing Chord Layout

```javascript
const matrix = [
  [11975,  5871, 8916, 2868],
  [ 1951, 10048, 2060, 6171],
  [ 8010, 16145, 8090, 8045],
  [ 1013,   990,  940, 6907]
];

const chord = d3.chord()
    .padAngle(0.05)             // Gap between groups
    .sortGroups(d3.ascending)   // Sort group order
    .sortSubgroups(d3.ascending) // Sort within groups
    .sortChords(d3.ascending);  // Sort chord order

const chords = chord(matrix);
```

### Directed Chord

```javascript
const directed = d3.chordDirected()
    .padAngle(0.05)
    .sortGroups(d3.ascending)
    .sortSubgroups(d3.descending)
    .sortChords(d3.ascending);
```

### Transpose Matrix

```javascript
const transposed = d3.chordTranspose(matrix);
// → [[11975, 1951, 8010, 1013], [5871, 10048, ...], ...]
```

### Rendering Ribbons

```javascript
const ribbon = d3.ribbon()
    .radius(80)
    .padAngle(0.03)
    .source((d) => {
      const s = d.source;
      return {
        sourceRadius: s.source.radius,
        startAngle: s.startAngle,
        endAngle: s.endAngle
      };
    })
    .target((d) => {
      const t = d.target;
      return {
        targetRadius: t.target.radius,
        startAngle: t.startAngle,
        endAngle: t.endAngle
      };
    });

// Render group arcs (outer ring)
svg.append("g")
    .selectAll("path")
    .data(chords.groups)
    .join("path")
    .attr("d", ribbon)
    .attr("fill", d => color(d.target.key))
    .attr("stroke", d => d3.color(color(d.target.key)).darker());

// Render ribbons
svg.append("g")
    .selectAll("path")
    .data(chords)
    .join("path")
    .attr("d", ribbon)
    .attr("fill", d => color(d.source.target.key))
    .attr("stroke", d => d3.color(color(d.source.target.key)).darker());
```

## Delaunay & Voronoi (d3-delaunay)

### Creating Delaunay Triangulation

```javascript
// From array of {x, y} objects
const delaunay = d3.Delaunay.from(data, d => d.x, d => d.y);

// From flat arrays
const delaunay = d3.delaunay(
  data.map(d => d.x),
  data.map(d => d.y)
);

// From [[x,y], ...]
const delaunay = d3.delaunay(points);
```

### Delaunay Methods

```javascript
delaunay.hull(i);                    // Convex hull indices
delaunay.triangles();                // TypedArray of triangle indices [i,j,k,...]
delaunay.neighbors(i);               // Neighboring cell indices
delaunay.find(x, y);                 // Index of cell containing point
delaunay.render(path);               // Render to path context
delaunay.renderHull(path);           // Render convex hull
delaunay.renderPoints(path, radius); // Render points
delaunay.renderTriangle(path, i);    // Render triangle by index
delaunay.trianglePolygon(i);         // Get polygon for triangle
delaunay.trianglePolygons();         // All triangle polygons
delaunay.update();                   // Update after modifying points
```

### Voronoi Diagram

```javascript
const voronoi = delaunay.voronoi([x0, y0, x1, y1]);

voronoi.renderCell(i, path);           // Render cell i
voronoi.renderBounds(path);            // Render bounding box
voronoi.cellPolygon(i);                // Get polygon for cell
voronoi.cellPolygons();                // All cell polygons
voronoi.contains(i, x, y);             // Is point in cell?
voronoi.neighbors(i);                  // Adjacent cell indices
voronoi.render(path);                  // Render all cells
voronoi.circumcenters();               // All circumcenter coordinates
voronoi.vectors();                     // [x0,y0,x1,y1,...] bounding boxes
```

### Nearest Neighbor Search

```javascript
// Find nearest point to (x, y)
const index = delaunay.find(x, y);
const point = data[index];

// Voronoi cell for nearest neighbor
const cell = voronoi.cellPolygon(index);
```

### Use Cases

- **Nearest neighbor**: `delaunay.find(x, y)` — O(log n) lookup
- **Spatial partitioning**: Voronoi cells as regions
- **Mesh generation**: Delaunay triangles as mesh
- **Convex hull**: `delaunay.hull()`
- **Proximity queries**: `voronoi.contains(i, x, y)`
