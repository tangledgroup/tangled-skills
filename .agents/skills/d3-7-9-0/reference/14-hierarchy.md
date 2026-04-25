# Hierarchy Layouts

> **Source:** https://d3js.org/d3-hierarchy
> **Loaded from:** SKILL.md (via progressive disclosure)

D3 provides algorithms for visualizing hierarchical data: node-link diagrams, adjacency diagrams, and enclosure diagrams.

## Hierarchy — d3.hierarchy()

Creates a hierarchy from nested data or tabular data.

```js
const root = d3.hierarchy({
  name: "root",
  children: [
    {name: "child1", value: 100},
    {name: "child2", children: [
      {name: "grandchild", value: 50}
    ]}
  ]
});

// From tabular data (stratify)
const root = d3.hierarchy(stratifiedData);
```

### Hierarchy Methods

```js
root.sum(value)           // set node values
root.sort(compare)        // sort children
root.each(fn)             // iterate all nodes breadth-first
root.eachBefore(fn)       // pre-order (parent before children)
root.eachAfter(fn)        // post-order (children before parent)
root.eachDescendant(fn)   // all descendants
root.path(target)         // path from root to target
root.ancestors()          // array of ancestors
root.descendants()        // flat array of all nodes
root.leaves()             // leaf nodes only
root.links()              // array of {source, target} links
root.height               // max depth
root.depth                // node depth (root = 0)
```

## Stratify — d3.stratify()

Converts tabular data (parent-child rows) into a hierarchy.

```js
const stratify = d3.stratify()
  .id(d => d.id)
  .parentId(d => d.parentId);

const root = stratify([
  {id: "A", parentId: null},
  {id: "B", parentId: "A"},
  {id: "C", parentId: "A"},
  {id: "D", parentId: "B"}
]);
```

## Tree Layout — d3.tree()

"Tidy" tree diagram. Compact, places nodes at uniform depth.

```js
const tree = d3.tree()
  .size([height, width])
  .separation((a, b) => a.parent === b.parent ? 1 : 2);

tree(root);

// Get link paths
const links = root.links();
links.forEach(l => {
  // l.source → l.target
});
```

**Configuration:**
- `.size([width, height])` — layout dimensions
- `.separation(a, b)` — control spacing between siblings/cousins
- `.nodeSize([width, height])` — fixed node spacing (polar form)

## Cluster Layout — d3.cluster()

Dendrogram: places all leaves at the same depth.

```js
const cluster = d3.cluster()
  .size([height, width]);

cluster(root);
```

## Partition Layout — d3.partition()

Space-filling adjacency diagrams (icicle charts).

```js
const partition = d3.partition()
  .size([width, height]);

partition(root);
// Each node gets: x0, y0, x1, y1
```

## Pack Layout — d3.pack()

Circle-packing: tightly nests circles.

```js
const pack = d3.pack()
  .size([width, height])
  .padding(0.5);

pack(root);
// Each node gets: x, y, r
```

## Treemap Layout — d3.treemap()

Recursively subdivides rectangles by value (squarified).

```js
const treemap = d3.treemap()
  .size([width, height])
  .paddingOuter(4)       // outer padding
  .paddingInner(2)       // gap between tiles
  .paddingRadius([10, 0]) // corner radius
  .round(true);          // round coordinates

treemap(root);
// Each leaf gets: x0, y0, x1, y1
```

**Tile algorithms:**
- `d3.treemapSquarify` — squarified (default)
- `d3.treemapBinary` — binary splits
- `d3.treemapSlice` — vertical slices
- `d3.treemapDice` — horizontal slices
- `d3.treemapResquarify` — resquarify without reordering

## Complete Treemap Example

```js
const width = 960;
const height = 500;

const color = d3.scaleOrdinal(d3.schemeTableau10);

const root = d3.hierarchy(data)
  .sum(d => d.value)
  .sort((a, b) => b.value - a.value);

const treemap = d3.treemap()
  .size([width, height])
  .padding(3)
  .round(true);

treemap(root);

const svg = d3.create("svg")
  .attr("viewBox", [0, 0, width, height]);

svg.selectAll("rect")
  .data(root.leaves())
  .join("rect")
  .attr("x", d => d.x0)
  .attr("y", d => d.y0)
  .attr("width", d => d.x1 - d.x0)
  .attr("height", d => d.y1 - d.y0)
  .attr("fill", d => color(d.data.category))
  .attr("stroke", "white");

svg.selectAll("text")
  .data(root.leaves())
  .join("text")
  .attr("x", d => d.x0 + 4)
  .attr("y", d => d.y0 + 14)
  .text(d => d.data.name);
```

## Key Notes

- `hierarchy.sum()` computes values from leaves up
- `hierarchy.sort()` sorts children before layout
- Layouts modify nodes in-place (add x0, y0, x1, y1)
- Use `root.links()` to get source-target pairs for rendering
- Polar tree: use `nodeSize` with `d3.tree().polar()`
