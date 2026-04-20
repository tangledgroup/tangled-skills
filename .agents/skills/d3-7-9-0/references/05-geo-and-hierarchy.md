# D3 Geography and Hierarchy

## Geographic Projections

### Cylindrical Projections

```javascript
// Mercator (most common web map projection)
const mercator = d3.geoMercator()
    .fitSize([width, height], geojson)
    .rotate([10, 0]);  // Custom rotation

// Equirectangular (Plate Carrée)
const equirectangular = d3.geoEquirectangular();

// Transverse Mercator
const transverseMercator = d3.geoTransverseMercator();

// Equal Earth
const equalEarth = d3.geoEqualEarth();

// Natural Earth 1
const naturalEarth1 = d3.geoNaturalEarth1();
```

### Conic Projections

```javascript
// Albers (standard for US maps)
const albers = d3.geoAlbers()
    .fitSize([width, height], geojson);

// Albers USA (contiguous + Alaska + Hawaii)
const albersUsa = d3.geoAlbersUsa();

// Conic Conformal (Lambert)
const lambert = d3.geoConicConformal();

// Conic Equal Area (Albers variant)
const conicEqualArea = d3.geoConicEqualArea();

// Conic Equidistant
const conicEquidistant = d3.geoConicEquidistant();

// Parallel parameter
conic.parallels([20, 60]);
```

### Azimuthal Projections

```javascript
// Azimuthal Equal Area
const equalArea = d3.geoAzimuthalEqualArea();

// Azimuthal Equidistant
const equidistant = d3.geoAzimuthalEquidistant();

// Gnomonic
const gnomonic = d3.geoGnomonic();

// Orthographic (3D globe view)
const orthographic = d3.geoOrthographic()
    .rotate([90, 0]);

// Stereographic
const stereographic = d3.geoStereographic();
```

### Projection Configuration

```javascript
projection.center([lon, lat]);      // Center point
projection.rotate([lon, lat]);      // Rotation angles
projection.precision(0.1);          // Rendering precision
projection.scale(scale);            // Scale factor
projection.translate([x, y]);       // Translation
projection.clipAngle(degrees);      // Clip angle for sphere
projection.clipExtent([[x0,y0],[x1,y1]]);  // Viewport clipping

// Fit methods
projection.fitSize([width, height], geojson);
projection.fitWidth(width, geojson);
projection.fitHeight(height, geojson);

// Inversion
projection.invert([x, y]);          // → [lon, lat]

// Custom raw projection
d3.geoProjection(rawFn);
d3.geoProjectionMutator(mutatorFn);
d3.geoTransform(transformObject);
```

### Projection Types Registry

```javascript
// All available projections:
const projections = {
  // Azimuthal
  "geoAzimuthalEqualArea", "geoAzimuthalEquidistant",
  "geoGnomonic", "geoOrthographic", "geoStereographic",

  // Conic
  "geoAlbers", "geoAlbersUsa", "geoConicConformal",
  "geoConicEqualArea", "geoConicEquidistant",

  // Cylindrical
  "geoEqualEarth", "geoEquirectangular", "geoMercator",
  "geoNaturalEarth1", "geoTransverseMercator"
};
```

## Geo Path

```javascript
const path = d3.geoPath(projection);

// Render GeoJSON
svg.selectAll("path")
    .data(geojson.features)
    .join("path")
    .attr("d", path);

// Path methods
path.area(geojson);                   // → area in pixels
path.bounds(geojson);                 // → [[x0, y0], [x1, y1]]
path.centroid(geojson);               // → [x, y] center
path.measure(geojson);                // → length in pixels
path.pointRadius(5);                  // For point geometries
```

## Geo Shape Generators

```javascript
// Graticule (grid lines)
const graticule = d3.geoGraticule()
    .step([10, 10])
    .extent([[-180, -60], [180, 80]]);

const pathString = path(graticule());

// Graticule 10° (default)
const graticule10 = d3.geoGraticule10();

// Circle on sphere
const circle = d3.geoCircle()
    .center([lon, lat])
    .radius(10)   // degrees
    .precision(0.5);

// Pre-clipped geometries
d3.geoClipAntimeridian();
d3.geoClipCircle(radius);
d3.geoClipRectangle(minX, minY, maxX, maxY);
```

## Geo Math

```javascript
d3.geoArea(geojson);                    // Sphere area
d3.geoBounds(geojson);                  // [[lonMin, latMin], [lonMax, latMax]]
d3.geoCentroid(geojson);                // [lon, lat] center
d3.geoContains(feature, [lon, lat]);    // Point-in-polygon
d3.geoDistance(a, b);                   // Great-circle distance (radians)
d3.geoInterpolate(a, b);                // Interpolation function
d3.geoLength(geojson);                  // Length in radians

// Rotation
const rotate = d3.geoRotation([lon, lat]);
rotate([x, y]);
```

## Geo Stream

```javascript
// Convert GeoJSON to streaming format
d3.geoStream(geojson, handler);

// Custom stream handler
const handler = {
  point(lon, lat),
  lineStart(),
  lineEnd(),
  polygonStart(),
  polygonEnd(),
  sphere()
};
```

## Hierarchy

### Creating Hierarchies

```javascript
// From nested data
const hierarchy = d3.hierarchy(data);

// From flat table (stratify)
const stratified = d3.stratify()
    .id(d => d.id)
    .parentId(d => d.parentId)(flatData);

// From path string
d3.stratify().path(d => d.path)(data);
```

### Node Methods

```javascript
node.count();                     // Number of leaf descendants
node.height;                      // Distance from root
node.depth;                       // Distance from root
node.ancestors();                 // Array: [root, parent, ..., node]
node.descendants();               // All descendants
node.leaves();                    // Leaf nodes
node.links();                     // Parent-child links
node.path(target);                // Path to target node
node.sort(comparator);            // Sort children
node.sum(valueFn);                // Sum numeric value
node.count();                     // Count leaves (after sort/sum)
node.copy();                      // Deep copy
```

### Iteration

```javascript
// Pre-order
node.each(d => console.log(d.data));

// Post-order
node.eachAfter(d => console.log(d.data));

// Pre-order (reverse)
node.eachBefore(d => console.log(d.data));

// Find node
node.find(d => d.data.id === "target");

// Iterator
for (const node of hierarchy) { ... }
```

### Tree Layout

```javascript
const tree = d3.tree()
    .size([height, width])
    .separation((a, b) => a.parent === b.parent ? 1 : 2);

tree(hierarchy);

// Node positioning
node.x;   // y-coordinate (depth)
node.y;   // x-coordinate (position)
```

### Cluster Layout

```javascript
const cluster = d3.cluster()
    .size([height, width]);

cluster(hierarchy);
```

### Partition Layout

```javascript
const partition = d3.partition()
    .size([width, height])
    .padding(2);

partition(hierarchy);
// → node.x0, node.y0, node.x1, node.y1
```

### Pack Layout

```javascript
const pack = d3.pack()
    .size([width, height])
    .padding(5);

pack(hierarchy);
// → node.x, node.y, node.r

// Siblings packing
d3.packSiblings(nodes);  // [{x, y, r}, ...]

// Enclose minimum circle
d3.packEnclose(nodes);
```

### Treemap Layout

```javascript
const treemap = d3.treemap()
    .size([width, height])
    .padding(4)
    .round(true)
    .ratio(0.618)       // Golden ratio
    .tile(d3.treemapSquarify);  // Layout algorithm

treemap(hierarchy);
// → node.x0, node.y0, node.x1, node.y1
```

### Treemap Layouts

| Layout | Description |
|--------|-------------|
| `treemapSquarify` | Squares (default) |
| `treemapBinary` | Binary splits |
| `treemapDice` | Horizontal strips |
| `treemapSlice` | Vertical strips |
| `treemapSliceDice` | Alternate slice/dice |

### Treemap Offsets

```javascript
treemap.offset(0);      // No offset (default)
treemap.offset(2);      // Pad inside (for nested)
```
