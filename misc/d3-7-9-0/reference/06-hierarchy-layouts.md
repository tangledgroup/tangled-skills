# Hierarchy Layouts

## Hierarchy Fundamentals

D3 hierarchy layouts operate on tree structures. The first step is always creating a root node with `d3.hierarchy()`:

```js
// Input: nested JSON object
const data = {
    name: "root",
    children: [
        { name: "child1", value: 10, children: [
            { name: "grandchild1", value: 5 },
            { name: "grandchild2", value: 3 }
        ]},
        { name: "child2", value: 8 }
    ]
};

// Create hierarchy root
const root = d3.hierarchy(data);

// Access properties
root.depth;           // 0 (root)
root.height;          // 2 (max depth below this node)
root.descendants();   // flat array of all nodes
root.links();         // flat array of {source, target} parent-child links
root.path(otherNode); // shortest path between two nodes

// Sum values bottom-up
root.sum(d => d.value);

// Collapse subtree (for collapsible trees)
root.children[0].children = null;
```

**Stratify operator** — convert tabular data to hierarchy:

```js
const root = d3.stratify()
    .id(d => d.id)
    .parentId(d => d.parentId)
    (data);

// Input: flat array with id and parentId columns
// [
//   { id: "1", parentId: null, value: 100 },
//   { id: "2", parentId: "1", value: 40 },
//   { id: "3", parentId: "1", value: 60 }
// ]
```

## Tree Layout

Position nodes in a two-dimensional tree (Reingold-Tilford algorithm):

```js
const treeLayout = d3.tree()
    .nodeSize([20, 100])   // [horizontal spacing, vertical spacing] per node
    .separation((a, b) => a.parent === b.parent ? 1 : 2);

treeLayout(root);

// After layout, each node has:
// node.x — horizontal position
// node.y — vertical position (depth-based)

// Draw links
svg.selectAll("path.link")
    .data(root.links())
    .join("path")
    .attr("d", d3.linkHorizontal()
        .x(d => d.y)
        .y(d => d.x));

// Draw nodes
svg.selectAll("circle")
    .data(root.descendants())
    .join("circle")
    .attr("cx", d => d.y)
    .attr("cy", d => d.x)
    .attr("r", 4);
```

Note: `tree()` produces a vertical layout by default. Swap x/y for horizontal trees using `linkHorizontal()`.

## Cluster Layout (Dendrogram)

Like tree but only leaf nodes are positioned, internal nodes are midpoints:

```js
const cluster = d3.cluster()
    .size([height - marginBottom, width - marginLeft]);

cluster(root);
```

Produces the same node.x/node.y properties. Links use the same `linkHorizontal()` or `linkVertical()` generators.

## Partition Layouts

Partition layouts divide space proportionally based on node values. Requires `.sum()` to be called first.

**Basic partition:**

```js
root.sum(d => d.value);

const partition = d3.partition()
    .size([width, height]);

partition(root);

// Each node has: x0, x1 (horizontal span), y0, y1 (vertical span)
```

**Treemap** — tiled rectangular layout with squarified bins:

```js
const treemap = d3.treemap()
    .size([width, height])
    .padding(4)
    .round(true);

treemap(root);

// Each node has: x0, y0 (top-left), x1, y1 (bottom-right)
svg.selectAll("rect")
    .data(root.descendants())
    .join("rect")
    .attr("x", d => d.x0)
    .attr("y", d => d.y0)
    .attr("width", d => d.x1 - d.x0)
    .attr("height", d => d.y1 - d.y0);
```

**Pack layout (circle packing)** — nested circles sized by value:

```js
const pack = d3.pack()
    .size([width, height])
    .padding(10);

pack(root);

// Each node has: x, y (center), r (radius)
svg.selectAll("circle")
    .data(root.descendants())
    .join("circle")
    .attr("cx", d => d.x)
    .attr("cy", d => d.y)
    .attr("r", d => d.r);
```

Use `d3.packEnclose(circles)` to compute the minimum enclosing circle for a set of circles.

## Complete Example: Collapsible Tree

```js
const width = 640, height = 480;
const root = d3.hierarchy(data, d => d.children);
root.x0 = height / 2;
root.y0 = 0;

// Collapse nodes beyond depth 2
root.descendants().forEach((d, i) => {
    d.id = i;
    if (d.depth > 1) {
        d.children = d.children ? d._children = d.children : null;
        d.data.name = d.data.name + " (collapsed)";
    }
});

const svg = d3.create("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", "translate(40,0)");

const g = svg.selectAll(".node")
    .data(root.descendants().slice(1))
    .join("g")
    .attr("class", "node")
    .attr("transform", d => `translate(${d.y},${d.x})`)
    .on("click", (event, d) => {
        // Toggle children on click
        if (d.children) {
            d._children = d.children;
            d.children = null;
        } else {
            d.children = d._children;
            d._children = null;
        }
        update(d);  // re-run layout and transition
    });

g.append("circle")
    .attr("r", 4.5)
    .attr("fill", d => d._children ? "steelblue" : "none");

function update(source) {
    const nodes = d3.tree().nodeSize([10, 180])(root).descendants();
    // Transition logic here...
}
```
