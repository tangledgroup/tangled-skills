# Geographic Maps

## Geo Paths

Geo paths render GeoJSON features as SVG paths or Canvas drawings, applying a geographic projection:

```js
// Create a projection
const projection = d3.geoAlbersUsa()
    .fitSize([width, height], countries);

// Create path generator with the projection
const geoPath = d3.geoPath(projection);

// Render GeoJSON features
svg.selectAll("path")
    .data(countries.features)
    .join("path")
    .attr("d", geoPath)
    .attr("fill", "steelblue")
    .attr("stroke", "white")
    .attr("stroke-width", 0.5);
```

**Path metrics:**

```js
geoPath.area(feature);      // projected area in pixels
geoPath.bounds(feature);    // [[x0, y0], [x1, y1]] bounding box
geoPath.centroid(feature);  // [x, y] centroid in pixel space
```

**Canvas rendering:**

```js
const context = canvas.getContext("2d");
geoPath.context(context);
context.fillStyle = "steelblue";
countries.features.forEach(d => geoPath(d));
```

## Projections

D3 provides 20+ geographic projections organized into three families. All projections map spherical coordinates `[λ, φ]` (longitude, latitude in radians) to planar `[x, y]`.

**Common projections:**

```js
// Equirectangular (simple latitude-longitude mapping)
const projection = d3.geoEquirectangular();

// Mercator (preserves angles, distorts area at poles)
const projection = d3.geoMercator();

// Albers equal-area conic (standard for US maps)
const projection = d3.geoAlbers();

// Albers USA (composite: lower 48 + Alaska + Hawaii)
const projection = d3.geoAlbersUsa();

// Orthographic (globe view)
const projection = d3.geoOrthographic();

// Natural Earth (visually pleasing compromise)
const projection = d3.geoNaturalEarth1();

// Gnomonic (great circles as straight lines)
const projection = d3.geoGnomonic();
```

**Projection configuration:**

```js
projection.center([longitude, latitude]);   // center point
projection.rotate([λ, φ, γ]);               // rotation in degrees
projection.parallel(φ0);                    // standard parallel (conic)
projection.scale(150);                      // zoom level
projection.translate([width / 2, height / 2]); // position
projection.fitSize([width, height], feature);  // auto-scale to fit
projection.fitExtent([[0, 0], [w, h]], feature); // fit with padding
projection.fitPadding(padding, [[0,0],[w,h]], feature);
```

**Projection types by family:**

Azimuthal: `geoAzimuthalEqualArea`, `geoAzimuthalEquidistant`, `geoGnomonic`, `geoOrthographic`, `geoStereographic`

Conic: `geoAlbers`, `geoConicConformal`, `geoConicEquidistant`, `geoConicEqualArea`, `geoConicMaryland`, `geoConicNyquist`

Cylindrical: `geoEquirectangular`, `geoMercator`, `geoTransverseMercator`, `geoCylindricalStereographic`, `geoEqualEarth`, `geoHammer`, `geoNaturalEarth1`

**Custom projections** can be created with `d3.geoProjection(m)` where `m` is a raw projection function `[λ, φ] → [x, y]`.

## Spherical Shapes

Generate GeoJSON for geometric shapes on the sphere:

```js
// Great circle arc between two points
const arc = d3.geoGraticule();
const graticule = arc();  // returns GeoJSON LineString

// Circle at a given center with radius
const circle = d3.geoCircle()
    .center([-95, 40])
    .radius(Math.PI / 6);  // radians
const geojson = circle();  // GeoJSON Polygon

// Graticule (grid lines)
const graticule = d3.geoGraticule()
    .step([15, 15]);       // degree spacing
```

## Streams

Geo streams provide a low-level interface for processing geographic data as a sequence of operations. Useful for custom rendering or filtering:

```js
// Stream GeoJSON through a filter
const stream = feature.geojson;
stream(d3.geoStream(feature, {
    point: (λ, φ) => { /* process point */ },
    lineStart: () => { /* begin line */ },
    lineEnd: () => { /* end line */ },
    polygonStart: () => { /* begin polygon */ },
    polygonEnd: () => { /* end polygon */ }
}));
```

## Geographic Math

Utility functions for spherical geometry:

```js
// Distance between two points (in radians)
d3.geoDistance([λ1, φ1], [λ2, φ2]);

// Area of a sphere
d3.geoArea(feature);

// Centroid
d3.geoCentroid(feature);

// Bounding box
d3.geoBounds(feature);

// Length of a line
d3.geoLength(feature);
```
