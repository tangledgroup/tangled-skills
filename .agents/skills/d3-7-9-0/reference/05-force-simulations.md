# Force Simulations

## Force Simulation Basics

Force simulations use a physics engine to position nodes based on configurable forces. The simulation runs iteratively, updating node positions until reaching equilibrium or a tick limit.

```js
const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id))
    .force("charge", d3.forceManyBody().strength(-30))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide(nodeRadius + 2));

// Listen for each tick (frame)
simulation.on("tick", () => {
    link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);
});

// Control simulation lifecycle
simulation.alpha(1).restart();  // restart with full energy
simulation.stop();              // stop immediately
```

**Simulation parameters:**

```js
simulation.alpha(0.3);           // initial energy (0-1, default 0.3)
simulation.alphaDecay(0.0228);   // how quickly energy dissipates
simulation.alphaMin(0.001);      // minimum energy before stopping
simulation.velocityDecay(0.4);   // damping factor (0-1, higher = more damping)
simulation.force("name", null);  // remove a force
simulation.find(x, y, radius);   // find nearest node at position
```

## Force Types

**Link force** — attracts connected nodes toward a target distance:

```js
d3.forceLink(links)
    .id(d => d.id)           // resolve node references by id
    .distance(120)            // target distance between linked nodes
    .strength(0.7)            // force strength (0-1, default 0.4)
    .iterations(1);           // relaxation iterations per tick
```

Links can reference nodes by object reference or by id string. Use `.id()` to set up the lookup function when links use string identifiers.

**Many-body force** — simulates charge between all node pairs (attraction or repulsion):

```js
d3.forceManyBody()
    .strength(-30)            // negative = repulsion, positive = attraction
    .theta(0.618)             // Barnes-Hut approximation (0 = exact, 1 = coarsest)
    .distanceMin(1)           // minimum distance clamp
    .distanceMax(Infinity);   // maximum distance clamp
```

Negative strength creates repulsion (nodes push apart). Positive strength creates attraction (nodes cluster together). The `theta` parameter controls the Barnes-Hut approximation for performance — 0 computes exact forces O(n²), higher values use quadtree approximation O(n log n).

**Center force** — pulls all nodes toward a center point:

```js
d3.forceCenter(width / 2, height / 2);
```

Keeps the graph centered in the viewport. Does not account for node size.

**Collide force** — prevents node overlap using circle packing:

```js
d3.forceCollide()
    .radius(d => d.radius)    // radius accessor or fixed number
    .strength(0.7)            // resolution strength (0-1)
    .iterations(1);           // relaxation iterations
```

Each node is treated as a circle with the specified radius. Nodes are pushed apart when they overlap.

**Position forces** — attract nodes toward fixed positions:

```js
// x-position force
d3.forceX(d => d.targetX)
    .strength(0.1);           // weak pull toward target

// y-position force
d3.forceY(height / 2)
    .strength(0.1);

// Combined x,y position
d3.forceRadial(radius, cx, cy)
    .strength(0.5);           // pull toward circle of given radius
```

`forceX` and `forceY` are useful for constraining nodes to specific axes (e.g., layers in a Sankey diagram). `forceRadial` positions nodes along a circle.

## Complete Example: Force-Directed Graph

```js
const width = 800, height = 600;

const svg = d3.create("svg")
    .attr("width", width)
    .attr("height", height);

// Draw links
const link = svg.append("g")
    .attr("stroke", "#999")
    .attr("stroke-width", 1.5)
    .selectAll("line")
    .data(graph.links)
    .join("line");

// Draw nodes
const node = svg.append("g")
    .attr("stroke", "#fff")
    .attr("stroke-width", 1.5)
    .selectAll("circle")
    .data(graph.nodes)
    .join("circle")
    .attr("r", 5)
    .attr("fill", d => color(d.group));

// Run simulation
const simulation = d3.forceSimulation(graph.nodes)
    .force("link", d3.forceLink(graph.links).id(d => d.id).distance(100))
    .force("charge", d3.forceManyBody().strength(-200))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collide", d3.forceCollide(10));

simulation.on("tick", () => {
    link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);
});
```

## Dragging Nodes

Combine force simulation with drag behavior for interactive graphs:

```js
const drag = d3.drag()
    .on("start", (event, d) => {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;  // fix x position
        d.fy = d.y;  // fix y position
    })
    .on("drag", (event, d) => {
        d.fx = event.x;
        d.fy = event.y;
    })
    .on("end", (event, d) => {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;  // unfreeze x
        d.fy = null;  // unfreeze y
    });

node.call(drag);
```

Setting `d.fx` and `d.fy` fixes a node's position during the simulation. Setting them back to `null` releases the node so forces can move it again.
