# tangled-skills

Collection of Skills for Agents by Tangled

## About

All skills in this repository are automatically generated using the `skill` skill. Each skill is created from public references, official documentation URLs, and other publicly available resources to ensure accuracy and completeness.

This repository also includes meta skills that govern agent behavior and workflows: `skman`, `git`, `tzip`, `plan`, `pipe`, `webfetch`, and `websearch`.

## Install / Update
<!-- IMPORTANT: never change this section and code block -->
```bash
mkdir -p .agents/skills && \
curl -L https://github.com/tangledgroup/tangled-skills/archive/refs/heads/main.tar.gz | \
tar -xz --strip-components=3 -C .agents/skills tangled-skills-main/.agents/skills
```

### Skill Design Principles

- **Detailed yet concise**: Skills provide comprehensive coverage while staying within typical LLM context limits
- **Modular reference files**: Large topics are broken down into separate reference files that can be loaded on demand
- **Markdown only**: All skill files are plain Markdown documents - no scripts or executable code
- **Reference-driven**: Each skill links to official documentation and public resources for further exploration

<!-- IMPORTANT: never change after this point because it is automatically generated -->
## Skills Table

| No | Skill | Description |
|----|-------|-------------|
| 1 | git | Git version control. Use when the user mentions git, commits, branches, pushing, pulling, merging, rebasing, stashing, worktrees, submodules, or any version control task. Covers straightforward workflows (add/commit/push) and advanced topics. |
| 2 | matplotlib | Matplotlib plotting library (v3.11). Use this skill whenever the user mentions
plots, charts, graphs, figures, data visualization, matplotlib, pyplot, or
needs to create any kind of visual output from Python data — line plots, scatter
plots, bar charts, histograms, heatmaps, contour plots, subplots, legends,
colormaps, saving figures, styling, animations, or interactive widgets. Covers
both the pyplot (state-based) and object-oriented APIs. |
| 3 | mermaid-11-15-0 | Mermaid diagram syntax reference and validation. Use when writing, debugging,
or converting Mermaid diagrams: flowchart, sequenceDiagram, stateDiagram, classDiagram,
gantt, erDiagram, pie, gitgraph, journey, mindmap, timeline, xychart, radar-beta,
quadrantChart, sankey, block, architecture-beta, c4, packet, treemap-beta, venn-beta,
wardley-beta, ishikawa-beta, kanban, requirementDiagram. |
| 4 | networkx | Python graph library (NetworkX 3.6.1) for creating, manipulating, and analyzing complex networks.
Use this skill whenever the user works with graphs, networks, nodes, edges, shortest paths, centrality,
community detection, spanning trees, flow networks, DAGs, topological sort, graph generators,
adjacency matrices, Laplacian spectra, isomorphism, bipartite matching, or any network science task.
Triggers on: graph algorithms, network analysis, node/edge operations, Dijkstra, BFS, DFS, PageRank,
Louvain communities, connected components, minimum spanning tree, max flow, transitive closure,
and anything involving NetworkX or the `nx` module. |
| 5 | numpy-2-4-6 | "NumPy 2.4.6: array creation, manipulation, broadcasting, ufuncs, linear algebra, statistics, random sampling, structured arrays, and I/O. Use whenever working with numerical arrays, matrices, scientific computing, data analysis, or any task involving NumPy operations. Covers ndarrays, dtype system, einsum, stride tricks, masked arrays, FFT, polynomials, and the full NumPy 2.x API." |
| 6 | plan | Phase/task based workflow system with PLAN.md as single source of truth. Use when tackling projects that require structured iteration through Planning, Analysis, Design, Implementation, Testing, Deployment, Maintenance, etc phases with clear dependency graphs. |
| 7 | skman | Scaffold, validate, and inspect agent skills (SKILL.md files). Use when creating new skills, checking skill format compliance, or reviewing skill structure. |
| 8 | tzip | Lightweight token-pruning communication mode that drops filler and hedging while keeping full sentences and professional tone. Follows guidelines for code quality. Default intensity is lite. Use when user requests tzip, prune tokens, be concise, or needs efficient communication without losing clarity. |
| 9 | vega-lite-6-4-3 | Vega-Lite is a high-level grammar for interactive graphics — a concise JSON syntax for creating
data visualizations. Use this skill whenever the user mentions Vega-Lite, chart specifications,
JSON-based charts, declarative visualization, or wants to create bar charts, line charts, scatter
plots, heatmaps, pie charts, area charts, boxplots, trellis/facet charts, layered compositions,
geographic maps, or any data visualization using the Vega-Lite specification format (v6.4.3).
Also use when the user asks about encoding channels (x, y, color, size, shape, theta, radius),
mark types, transforms, aggregations, binning, time units, selections/interactions, or embedding
Vega-Lite charts in web applications. |
| 10 | webfetch | Fetches web pages as markdown or HTML for LLM consumption. Use when the user wants to fetch, scrape, download, retrieve, grab, pull, or access any URL or webpage content. Supports uvx, pipx, curl, wget, and python3 fallbacks. Always impersonates Safari to avoid blocks. Use this whenever the user asks to read a website, get page content, or fetch a URL. |
| 11 | websearch | Searches the web via DuckDuckGo and returns results as markdown, CSV, or JSON. Use this skill whenever the user wants to search the web, look up information online, find URLs, do web search, research a topic, or needs current/web-based answers. |

## Statistics

- **Total Skills**: 11
