# Axes

> **Source:** https://d3js.org/d3-axis
> **Loaded from:** SKILL.md (via progressive disclosure)

Axes document position encodings. They are appended as `<g>` elements and positioned with transforms.

## Axis Generators

### d3.axisBottom(scale) / d3.axisTop(scale) / d3.axisLeft(scale) / d3.axisRight(scale)

Creates an axis generator for the specified side. The scale determines tick positions and labels.

```js
const xAxis = d3.axisBottom(xScale);
const yAxis = d3.axisLeft(yScale);
```

## Axis Generator Configuration

### axis.tickValues(values)

Set specific tick values explicitly. Overrides automatic tick generation.

```js
d3.axisBottom(x).tickValues([0, 25, 50, 75, 100]);
```

### axis.ticks(count[, argument…])

Request a specific number of ticks. Additional arguments control formatting for time scales.

```js
d3.axisBottom(x).ticks(5);
d3.axisLeft(y).ticks(10, ".0f");
d3.axisBottom(timeScale).ticks(d3.timeMonth.every(2));
```

### axis.tickFormat([format])

Set a format function for tick labels. Use d3-format specifiers.

```js
d3.axisLeft(y).tickFormat(d => `$${d}`);
d3.axisLeft(y).tickFormat(".1%"); // percentage
d3.axisLeft(y).tickFormat(d3.format(",.0f")); // with comma
```

### axis.tickSize([size])

Set the tick size (length of tick marks). For end tick size, pass two values: `[outerSize, innerSize]`.

```js
d3.axisBottom(x).tickSize(10);
d3.axisBottom(x).tickSize(10, 5, 2); // outer, inner, end
```

### axis.tickPadding([padding])

Set padding between ticks and labels in pixels (default: 6).

```js
d3.axisBottom(x).tickPadding(8);
```

### axis.orient([orientation])

Set the axis orientation ("top", "bottom", "left", "right"). Default is inherited from generator type.

```js
d3.axisBottom(x).orient("bottom");
```

## Rendering Axes

Append as a `<g>` element and call the axis generator with `.call()`.

```js
svg.append("g")
  .attr("transform", `translate(0,${height})`)
  .call(d3.axisBottom(x));

svg.append("g")
  .attr("transform", `translate(${marginLeft},0)`)
  .call(d3.axisLeft(y));
```

## Axis Structure

The rendered axis produces this DOM structure:

```html
<g class="axis" transform="...">
  <line class="tick" .../>
  <line class="tick" .../>
  <text class="tick" ...>label</text>
  <text class="tick" ...>label</text>
  <line class="domain" .../>
</g>
```

- `.axis` — the root group
- `.tick` — tick marks and labels
- `.domain` — the axis baseline line

## Styling Axes

```css
.axis path,
.axis line {
  fill: none;
  stroke: #000;
  shape-rendering: crispEdges;
}

.axis text {
  font-family: sans-serif;
  font-size: 11px;
}
```

## Complete Example

```js
const margin = {top: 20, right: 20, bottom: 30, left: 40};

const x = d3.scaleLinear()
  .domain([0, d3.max(data, d => d.x)])
  .range([margin.left, width - margin.right]);

const y = d3.scaleLinear()
  .domain([0, d3.max(data, d => d.y)])
  .range([height - margin.bottom, margin.top]);

svg.append("g")
  .attr("transform", `translate(0,${height - margin.bottom})`)
  .call(d3.axisBottom(x).ticks(10))
  .selectAll("text")
  .style("font-size", "12px");

svg.append("g")
  .attr("transform", `translate(${margin.left},0)`)
  .call(d3.axisLeft(y).ticks(10).tickFormat(d => `${d}%`));
```
