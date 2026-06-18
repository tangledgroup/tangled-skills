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
| 1 | basedpyright-1-39-8 | Static type checking for Python via basedpyright — a fork of pyright with stricter defaults, new diagnostic rules, baseline support, pylance features in open-source, and improved CI integration. Use when the user mentions basedpyright, pyright, type checking, static analysis, type stubs, pyrightconfig, or wants to configure/resolve Python type errors. |
| 2 | duckdb-1-5-3 | DuckDB 1.5.3 — high-performance analytical OLAP database with embedded SQL engine. Use this skill whenever the user queries about DuckDB, needs to run SQL analytics on local files (CSV, Parquet, Excel/XLSX), wants to install or use extensions (excel, json, icu, parquet, httpfs, delta, iceberg, postgres_scanner, sqlite_scanner, fts, spatial, and others), needs data import/export workflows, or is comparing DuckDB against other analytical databases. Covers CLI usage, Python API, extension management, Excel file handling (read/write/formatting/metadata), and the full extension ecosystem available in v1.5.3. |
| 3 | duckdb-python-1-5-4 | DuckDB Python client 1.5.4 API reference and usage patterns. Use when working with the `duckdb` Python package — in-process analytical SQL database. Covers connection management, relational API (lazy evaluation), data I/O (CSV/Parquet/JSON), Python UDFs, type system, pandas/PyArrow/Polars integration, fsspec filesystems, ADBC driver, profiling, and extensions. Trigger on: duckdb, DuckDBPyConnection, DuckDBPyRelation, read_parquet, from_df, create_function, fetch_arrow_table, register_filesystem. |
| 4 | formulas-1-3-4 | Evaluate Excel formulas in Python without Excel. Use when the user needs to compute spreadsheet formulas, calculate xlsx files, convert formula-based spreadsheets to calculated values, export Excel to CSV/JSON, run batch scenarios, build JSON models from workbooks, or serve spreadsheets as a Flask API. Also triggers on mentions of formulas package, openpyxl calculation, or spreadsheet automation. |
| 5 | git | Git version control. Use when the user mentions git, commits, branches, pushing, pulling, merging, rebasing, stashing, worktrees, submodules, or any version control task. Covers straightforward workflows (add/commit/push) and advanced topics. |
| 6 | matplotlib-3-11-0 | Matplotlib plotting library (v3.11). Use this skill whenever the user mentions
plots, charts, graphs, figures, data visualization, matplotlib, pyplot, or
needs to create any kind of visual output from Python data — line plots, scatter
plots, bar charts, histograms, heatmaps, contour plots, subplots, legends,
colormaps, saving figures, styling, animations, or interactive widgets. Covers
both the pyplot (state-based) and object-oriented APIs. |
| 7 | mermaid-11-15-0 | Mermaid diagram syntax reference and validation. Use when writing, debugging,
or converting Mermaid diagrams: flowchart, sequenceDiagram, stateDiagram, classDiagram,
gantt, erDiagram, pie, gitgraph, journey, mindmap, timeline, xychart, radar-beta,
quadrantChart, sankey, block, architecture-beta, c4, packet, treemap-beta, venn-beta,
wardley-beta, ishikawa-beta, kanban, requirementDiagram. |
| 8 | networkx-3-6-1 | Python graph library (NetworkX 3.6.1) for creating, manipulating, and analyzing complex networks.
Use this skill whenever the user works with graphs, networks, nodes, edges, shortest paths, centrality,
community detection, spanning trees, flow networks, DAGs, topological sort, graph generators,
adjacency matrices, Laplacian spectra, isomorphism, bipartite matching, or any network science task.
Triggers on: graph algorithms, network analysis, node/edge operations, Dijkstra, BFS, DFS, PageRank,
Louvain communities, connected components, minimum spanning tree, max flow, transitive closure,
and anything involving NetworkX or the `nx` module. |
| 9 | numpy-2-4-6 | "NumPy 2.4.6: array creation, manipulation, broadcasting, ufuncs, linear algebra, statistics, random sampling, structured arrays, and I/O. Use whenever working with numerical arrays, matrices, scientific computing, data analysis, or any task involving NumPy operations. Covers ndarrays, dtype system, einsum, stride tricks, masked arrays, FFT, polynomials, and the full NumPy 2.x API." |
| 10 | pandas-3-0-3 | Pandas 3.0.3 data manipulation and analysis library for Python. Use when working
with DataFrames, Series, data wrangling, CSV/Excel/Parquet I/O, groupby aggregations,
merging/joining, time series, resampling, rolling windows, string operations, or any
tabular data processing in Python. Covers pandas 3.0 semantics including dedicated
string dtype by default, Copy-on-Write behavior, pd.col() expressions, Arrow PyCapsule
interface, and anti-joins. Trigger on: DataFrame, Series, read_csv, merge, groupby,
pivot_table, resample, rolling, time series analysis, ETL pipelines, data cleaning,
or any mention of pandas dataframes. |
| 11 | pandoc-3-10 | Convert documents between formats using Pandoc 3.10. Use when the user mentions pandoc, document conversion, format transformation, or needs to convert between Markdown, HTML, LaTeX, PDF, Word (docx), OpenDocument (odt), PowerPoint (pptx), Excel (xlsx), CSV, TSV, EPUB, reStructuredText, Org mode, AsciiDoc, RTF, Textile, CommonMark, GFM, or any markup/format conversion task. Also use when user asks about pandoc filters, templates, defaults files, citeproc, or Lua filters. |
| 12 | plan | Phase/task based workflow system with PLAN.md as single source of truth. Use when tackling projects that require structured iteration through Planning, Analysis, Design, Implementation, Testing, Deployment, Maintenance, etc phases with clear dependency graphs. |
| 13 | pytest-9-1-0 | Write, run, and debug Python tests with pytest 9.1.0. Use when the user mentions pytest, writing tests, test fixtures, parametrization, test discovery, conftest.py, pytest plugins, test marks, skip/xfail, monkeypatch, tmp_path, capsys, caplog, assertion rewriting, or any Python testing task. |
| 14 | pytest-asyncio-1-4-0 | Test async/await code with pytest using event loops, async fixtures, and loop scopes.
Use when writing async tests, configuring asyncio mode (auto/strict), managing event loop scopes,
using @pytest.mark.asyncio, @pytest_asyncio.fixture, custom loop factories via
pytest_asyncio_loop_factories hook, port fixtures (unused_tcp_port, unused_udp_port),
testing with uvloop or other custom event loops, integrating Hypothesis with async tests,
or migrating from older pytest-asyncio versions. Covers pytest-asyncio 1.4.0+ and Python 3.10+. |
| 15 | requests-2-34-2 | Python HTTP library (requests) version 2.34.2 — sends HTTP/1.1 requests via
the high-level API (requests.get, requests.post, etc.), Session objects for
cookie/auth persistence and connection pooling, PreparedRequest for low-level
control, streaming responses, file uploads, authentication (Basic/Digest),
proxies, TLS verification, retries, and hooks. Use this skill whenever the
user works with Python HTTP clients, needs to call REST APIs, upload files,
handle sessions or cookies, configure timeouts or retries, inspect response
headers/status codes, or debug HTTP requests in Python, even if they don't
name "requests" explicitly. |
| 16 | ruff-0-4-10 | Lint, format, and configure Python code with Ruff (v0.4+). Use when the user mentions
ruff, python linting, python formatting, code quality, replacing flake8/black/isort/pyupgrade,
pyproject.toml ruff config, ruff check, ruff format, or needs help setting up Python linting
and formatting. Also triggers for import sorting (isort replacement), docstring checks,
auto-fixing lint violations, pre-commit hooks with ruff, CI/CD linting pipelines, and
migrating from flake8 + black + isort to a single tool. |
| 17 | scikit-learn-1-9-0 | Comprehensive guide to scikit-learn 1.9.0 — the Python machine learning library.
Use when working with ML models, pipelines, preprocessing, model selection, metrics,
or any data science task using scikit-learn. Covers classification, regression,
clustering, dimensionality reduction, ensemble methods, hyperparameter tuning,
cross-validation, feature engineering, and more. Trigger on: sklearn, scikit-learn,
machine learning, ML pipeline, model training, cross-validation, GridSearchCV,
Random Forest, SVM, logistic regression, PCA, KMeans, train_test_split, metrics. |
| 18 | scipy-1-17-1 | SciPy (scientific Python) library reference for mathematics, science, and engineering. Covers optimization, integration, linear algebra, statistics, signal processing, FFT, interpolation, sparse matrices, spatial algorithms, special functions, image processing, clustering, I/O, and physical constants. Use when the user needs scientific computing in Python, numerical methods, data analysis with scipy, solving equations, statistical tests, Fourier transforms, ODE systems, matrix operations, or any math-heavy computation. Also triggers on mentions of scipy, SciPy, scientific Python, numerical Python, or packages like numpy/scipy together. |
| 19 | skman | Scaffold, validate, and inspect agent skills (SKILL.md files). Use when creating new skills, checking skill format compliance, or reviewing skill structure. |
| 20 | sqlalchemy-2-0-51 | SQLAlchemy 2.0 ORM and Core toolkit for Python database access. Use this skill whenever the user
mentions SQLAlchemy, ORM models, database queries, engine creation, session management, declarative
mappings, relationships (one-to-many, many-to-many), connection pooling, async database access,
SQL expression construction, or any Python database abstraction task. Covers both Core (expression
language) and ORM layers. Supports PostgreSQL, MySQL/MariaDB, SQLite, Oracle, Microsoft SQL Server,
and third-party dialects (CockroachDB, IBM DB2, Firebird, SAP HANA, etc.). |
| 21 | sympy-1-14-0 | Symbolic mathematics with SymPy 1.14.0 — algebra, calculus, ODE/PDE solving, matrices,
number theory, geometry, special functions, transforms, and code generation. Use when
the user needs symbolic computation, equation solving, differentiation, integration,
series expansion, matrix operations, polynomial manipulation, simplification, or any
CAS (computer algebra system) task in Python. Also use for exact arithmetic with
rationals, symbolic constants (pi, E), or converting expressions to LaTeX/C/Fortran. |
| 22 | ty-0-0-49 | Use ty, the extremely fast Python type checker and language server by Astral (creators of uv and Ruff).
Use this skill whenever the user mentions ty, Python type checking, mypy migration, pyright migration,
type diagnostics, or needs to configure a Python type checker. Also triggers for questions about
Python typing features like intersection types, gradual typing, or redeclarations.
ty is 10x–100x faster than mypy/Pyright and supports full LSP (completions, hover, navigate, etc.). |
| 23 | tzip | Lightweight token-pruning communication mode that drops filler and hedging while keeping full sentences and professional tone. Follows guidelines for code quality. Default intensity is lite. Use when user requests tzip, prune tokens, be concise, or needs efficient communication without losing clarity. |
| 24 | uv-0-11-21 | Manage Python projects, scripts, tools, environments, and packages with uv (0.11.21) — the fast Python package manager. Use when working with pyproject.toml, virtual environments, pip alternatives, venv creation, dependency locking (uv.lock), running Python scripts with inline metadata, installing/running CLI tools via uvx, managing Python versions, building wheels/sdists, publishing to PyPI, workspace management, or migrating from pip/pip-tools/virtualenv. Covers uv run, uv add, uv sync, uv lock, uv build, uv publish, uv venv, uv pip, uv tool, uv python, uv check, uv upgrade, and all related workflows. |
| 25 | vega-lite-6-4-3 | Vega-Lite is a high-level grammar for interactive graphics — a concise JSON syntax for creating
data visualizations. Use this skill whenever the user mentions Vega-Lite, chart specifications,
JSON-based charts, declarative visualization, or wants to create bar charts, line charts, scatter
plots, heatmaps, pie charts, area charts, boxplots, trellis/facet charts, layered compositions,
geographic maps, or any data visualization using the Vega-Lite specification format (v6.4.3).
Also use when the user asks about encoding channels (x, y, color, size, shape, theta, radius),
mark types, transforms, aggregations, binning, time units, selections/interactions, or embedding
Vega-Lite charts in web applications. |
| 26 | webfetch | Fetches web pages as markdown or HTML for LLM consumption. Use when the user wants to fetch, scrape, download, retrieve, grab, pull, or access any URL or webpage content. Supports uvx, pipx, curl, wget, and python3 fallbacks. Always impersonates Safari to avoid blocks. Use this whenever the user asks to read a website, get page content, or fetch a URL. |
| 27 | websearch | Searches the web via DuckDuckGo and returns results as markdown, CSV, or JSON. Use this skill whenever the user wants to search the web, look up information online, find URLs, do web search, research a topic, or needs current/web-based answers. |

## Statistics

- **Total Skills**: 27
