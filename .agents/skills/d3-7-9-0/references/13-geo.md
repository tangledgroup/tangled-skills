# Geo-Projections

> **Source:** https://d3js.org/d3-geo
> **Loaded from:** SKILL.md (via progressive disclosure)

D3 provides map projections for converting spherical coordinates (longitude, latitude) to planar coordinates. Uses spherical GeoJSON natively.

## Path Generator — d3.geoPath()

Generates SVG path `d` attributes from GeoJSON features.

```js
const path = d3.geoPath()
  .projection(projection)
  .context(canvas); // use Canvas instead of SVG

svg.append("path")
  .datum(country)
  .attr("d", path);
```

**Methods:**
- `.projection([project])` — set the projection function
- `.context([context])` — set rendering context (null=SVG, canvas=Canvas)
- `.pointRadius([radius])` — radius for point geometries
- `.area(feature)` — compute projected area
- `.bounds(feature)` — compute bounding box
- `.measure(feature)` — compute spherical area
- `.centroid(feature)` — compute projected centroid

## Projections

All projections are functions: `projection([longitude, latitude]) → [x, y]`.

### Cylindrical Projections

```js
d3.geoEquirectangular();     // equal-area cylindrical
d3.geoMercator();            // spherical Mercator (Google Maps)
d3.geoTransverseMercator();  // vertical cylinder
d3.geoSinusoidal();          // false cylindrical, equal-area
d3.geoGnomonic();            // perspective from center of sphere
```

### Conic Projections

```js
d3.geoAlbers();              // Albers USA (default)
d3.geoConicConformal();      // Lambert conformal conic
d3.geoConicEqualArea();      // Albers (customizable)
d3.geoConicEquidistant();    // equidistant conic
```

### Azimuthal Projections

```js
d3.geoAzimuthalEqualArea();  // equal-area, perspective from center
d3.geoAzimuthalEquidistant();// equidistant from center point
d3.geoOrthographic();        // perspective from infinity
d3.geoGnomonic();            // perspective from sphere center
d3.geoStereographic();       // perspective from opposite point
```

### Custom Projection

```js
const projection = d3.geoNaturalEarth1()
  .scale(150)
  .translate([width / 2, height / 2]);

// Or define custom
function customProjection(lambda, phi) {
  return [lambda, Math.log(Math.tan(Math.PI / 4 + phi / 2))];
}
```

## Projection Configuration

All projections share these methods:

```js
projection
  .scale([scale])            // zoom level (default: 150)
  .translate([x, y])         // center position in pixels
  .center([lon, lat])        // center point in degrees
  .rotate([lon, lat, phi])   // rotate coordinates
  .clipExtent([[x0, y0], [x1, y1]]) // pixel clip region
  .fitSize([width, height], feature) // auto-scale and translate
  .fitExtent([[x0,y0],[x1,y1]], feature);
```

## Geo Features

### Circles

```js
const circle = d3.geoCircle()
  .center([-98, 39])
  .radius(30); // degrees
// Returns GeoJSON Feature for a circle on sphere
```

### Graticules

```js
const graticule = d3.geoGraticule()
  .step([10, 10])          // longitude, latitude step
  .extent([[−180, −90], [180, 90]]);

svg.append("path")
  .datum(graticule)
  .attr("d", path)
  .style("fill", "none")
  .style("stroke", "#ddd");
```

### Stream Transform

```js
// Transform geometry during rendering
const stream = d3.geoStream(feature, projection);
```

## Complete Map Example

```js
const width = 960;
const height = 500;

const projection = d3.geoAlbersUsa()
  .scale(1000)
  .translate([width / 2, height / 2]);

const path = d3.geoPath().projection(projection);

const svg = d3.create("svg")
  .attr("viewBox", [0, 0, width, height]);

// Load GeoJSON
const data = await d3.json("us-states.json");

svg.selectAll("path")
  .data(data.features)
  .join("path")
  .attr("d", path)
  .attr("fill", "lightgray")
  .attr("stroke", "white");

// State labels
svg.selectAll("text")
  .data(data.features)
  .join("text")
  .attr("transform", d => `translate(${path.centroid(d)})`)
  .attr("text-anchor", "middle")
  .text(d => d.properties.abbr);
```

## Key Notes

- D3 uses GeoJSON with spherical coordinates
- Projections convert lon/lat → pixel coordinates
- The path generator handles all geometry types (Point, LineString, Polygon, Multi*)
- Antimeridian cutting handled automatically
- Use `fitSize`/`fitExtent` for automatic scaling to container
