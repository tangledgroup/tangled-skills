# Force Simulation

> **Source:** https://d3js.org/d3-force
> **Loaded from:** SKILL.md (via progressive disclosure)

Force simulation implements a velocity Verlet numerical integrator for simulating physical forces on particles. Used for network visualization, hierarchical layouts, and collision resolution.

## Creating a Simulation

```js
const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links).id(d => d.id))
  .force("charge", d3.forceManyBody())
  .force("center", d3.forceCenter(width / 2, height / 2))
  .on("tick", ticked);

simulation.on("tick", () => {
  link.attr("x2", d => d.target.x).attr("y2", d => d.target.y);
  node.attr("cx", d => d.x).attr("cy", d => d.y);
});
```

## Simulation Methods

### simulation.nodes([nodes])

Set or get the array of nodes. Each node needs `x`, `y` properties (set by simulation).

```js
simulation.nodes(nodes);
```

### simulation.force(name[, force])

Get or set a named force. Forces are applied each tick.

```js
simulation.force("charge", d3.forceManyBody().strength(-30));
simulation.force("link", null); // remove force
```

### simulation.alpha([alpha]) / alphaMin() / alphaMax() / alphaDecay() / velocityDecay()

Control simulation energy and cooling.

```js
simulation.alpha(1);       // reset energy
simulation.alphaTarget(0); // stop cooling
simulation.restart();      // reheat and restart
simulation.tick();         // advance one step
simulation.stop();         // stop simulation
```

## Force Types

### Link Force — d3.forceLink()

Attracts connected nodes. Requires an `id` accessor for node matching.

```js
const linkForce = d3.forceLink(links)
  .id(d => d.id)       // required: match by id
  .distance(100)       // ideal link distance
  .strength(1)         // 0 to 1, default 1
  .links(nodes);       // set links array
```

### Many-Body Force — d3.forceManyBody()

Repulsive force between all nodes (Coulomb's law).

```js
d3.forceManyBody()
  .strength(-30)       // negative = repulsion, positive = attraction
  .distanceMin(1)      // closest distance for force calculation
  .distanceMax(400)    // furthest distance considered
  .theta(0.8);         // Barnes-Hut accuracy (0–1)
```

### Center Force — d3.forceCenter()

Pulls the simulation center to a point.

```js
d3.forceCenter(width / 2, height / 2);
```

### Position Forces — d3.forceX() / d3.forceY() / d3.forceZ()

Attract nodes toward a target coordinate.

```js
d3.forceX(d => d.xTarget).strength(0.1);
d3.forceY(d => d.yTarget).strength(0.1);
```

### Collide Force — d3.forceCollide()

Prevents node overlap (radius-based collision).

```js
d3.forceCollide()
  .radius(d => d.radius)  // per-node radius
  .strength(0.7)          // 0 to 1
  .iterations(1);         // collision iterations per tick
```

### Radial Force — d3.forceRadial()

Attracts nodes toward (or away from) a center point radially.

```js
d3.forceRadial(radius, centerX, centerY)
  .strength(strength);
```

## Complete Graph Example

```js
const nodes = data.nodes.map(d => ({...d}));
const links = data.links.map(d => ({...d}));

const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links).id(d => d.id).distance(80))
  .force("charge", d3.forceManyBody().strength(-120))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collide", d3.forceCollide().radius(20))
  .alphaDecay(0.02);

// Render
const svg = d3.select("svg");
const link = svg.append("g")
  .selectAll("line")
  .data(links)
  .join("line")
  .attr("stroke", "#999")
  .attr("stroke-opacity", 0.6);

const node = svg.append("g")
  .selectAll("circle")
  .data(nodes)
  .join("circle")
  .attr("r", 8)
  .call(d3.drag()
    .on("start", dragstarted)
    .on("drag", dragged)
    .on("end", dragended));

simulation.on("tick", () => {
  link
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x)
    .attr("y2", d => d.target.y);
  node.attr("cx", d => d.x).attr("cy", d => d.y);
});

function dragstarted(event, d) {
  if (!event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(event, d) {
  d.fx = event.x;
  d.fy = event.y;
}

function dragended(event, d) {
  if (!event.active) simulation.alphaTarget(0);
  d.fx = null;
  d.fy = null;
}
```
