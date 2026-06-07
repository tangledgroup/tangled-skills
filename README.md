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
| 1 | a2a-1-0-0 | Open standard for communication between independent AI agent systems. Agents discover capabilities via Agent Cards and... |
| 2 | acp-0-12-2 | Protocol standardizing communication between code editors and AI coding agents using JSON-RPC 2.0 over stdio. Decouples... |
| 3 | agent-coding-mini-rasbt-0-1-0 | Minimal standalone coding agent framework by Sebastian Raschka backed by Ollama, providing workspace context... |
| 4 | agent-coding-wyattdave-0-1-0 | A toolkit for creating custom AI coding agents using prompt engineering, instruction files, and skill modules. Use when... |
| 5 | agent-nirzabari-0-1-0 | Comprehensive guide to understanding and building coding agent harnesses, covering 7-layer architecture, context... |
| 6 | agent-ralph-loop-claude | Implements the Ralph Wiggum technique as a Claude Code plugin for iterative, self-referential AI development loops. Use... |
| 7 | agent-ralph-loop-vercel-labs | Continuous autonomy framework for the Vercel AI SDK implementing the Ralph Wiggum technique — an iterative outer loop... |
| 8 | agent-ralph-wiggum-fstandhartinger-0-3-0 | Autonomous AI coding with spec-driven development combining iterative bash loops and SpecKit-style specifications for... |
| 9 | agent-ralph-wiggum-ghuntley | Geoffrey Huntley's Ralph Wiggum technique — a monolithic iterative loop pattern for autonomous AI-driven software... |
| 10 | agent-ralph-wiggum-loop-beuke | Principles and conceptual framework of the Ralph Wiggum Loop pattern for goal-oriented autonomous AI agent loops.... |
| 11 | agent-ralph-wiggum-snarktank | Autonomous AI coding loop that runs AI coding tools (Amp or Claude Code) repeatedly until all PRD items are complete.... |
| 12 | agent-wiggum-cli-federiconeri | Autonomous coding agent that scans codebases, generates feature specs via AI interviews, and runs Ralph loops via... |
| 13 | agentmemory-0-9-4 | Persistent memory engine for AI coding agents with cross-session context capture, hybrid search (BM25 + vector +... |
| 14 | aiohttp-3-13-0 | Async HTTP client/server for Python asyncio. Use when building async web applications, REST APIs, or making concurrent... |
| 15 | aiohttp-3-13-5 | Async HTTP client/server for Python asyncio. Use when building async web applications, REST APIs, or making concurrent... |
| 16 | aiohttp-cors-0-8-1 | Implement Cross-Origin Resource Sharing (CORS) in aiohttp applications using aiohttp-cors 0.8.1, enabling secure... |
| 17 | aiohttp-jinja2-1-6-0 | Jinja2 template renderer for aiohttp.web applications providing decorator-based rendering, context processors, URL... |
| 18 | aiohttp-security-0-5-0 | Authentication and authorization toolkit for aiohttp.web applications providing identity policies (cookies, sessions,... |
| 19 | aiohttp-session-2-12-1 | Server-side sessions for aiohttp.web applications using aiohttp-session 2.12, providing multiple storage backends... |
| 20 | aiohttp-sse-2-2-0 | Python library for Server-Sent Events (SSE) support in aiohttp applications. Use when building real-time streaming... |
| 21 | aioitertools-0-13-0 | Async-compatible versions of itertools, builtins, and more for Python asyncio. Use when building async Python... |
| 22 | aiorwlock-1-5-1 | Async read-write lock for Python asyncio providing concurrent reader access and exclusive writer access. Use when... |
| 23 | aiozmq-1-0-0 | Async ZeroMQ integration for Python asyncio providing transport-level APIs, stream abstraction, and RPC frameworks... |
| 24 | alpinejs-3-15-12 | A skill for building reactive user interfaces with Alpine.js 3.15, a minimal JavaScript framework that uses HTML-first... |
| 25 | argon2-25-1-0 | Python toolkit for password hashing and verification using the Argon2 algorithm via argon2-cffi 25.x. Use when... |
| 26 | asyncstdlib-3-14-0 | Python async standard library providing async versions of builtins, itertools, functools, contextlib, and heapq for... |
| 27 | authelia-4-39-19 | Open-source authentication and authorization server providing multi-factor authentication (MFA), single sign-on (SSO),... |
| 28 | authentik-2026-5-0 | Open-source Identity Provider (IdP) for modern SSO supporting OAuth2/OIDC, SAML, LDAP, RADIUS, SCIM, and Proxy... |
| 29 | autoloop-0-4-0 | Opinionated loop harness for long-running agent workflows. Supports preset-driven multi-role loops with event-based... |
| 30 | automerge-3-2-6 | CRDT library for building collaborative, local-first applications with automatic conflict-free merging. Provides... |
| 31 | axios-1-15-2 | A comprehensive toolkit for making HTTP requests using Axios 1.x, a promise-based HTTP client for browser and Node.js... |
| 32 | bcrypt-5-0-0 | A skill for password hashing and key derivation using bcrypt 5.0 in Python. Use when implementing secure password... |
| 33 | boto3-1-43-1 | Complete toolkit for AWS SDK for Python (Boto3) 1.43.1 providing high-level resource interface and low-level client... |
| 34 | bun-1-3-13 | Complete toolkit for Bun 1.3.13 JavaScript runtime, package manager, bundler, and test runner. Use when building... |
| 35 | caddy-2-11-2 | Complete Caddy 2.11.2 web server toolkit covering Caddyfile configuration, JSON API, automatic HTTPS with Let's Encrypt... |
| 36 | category-theory | Mathematical framework for abstract structures and their relationships via categories, functors, natural... |
| 37 | caveman-1-5-1 | Ultra-compressed communication mode that cuts token usage by ~75% while maintaining full technical accuracy. Supports... |
| 38 | cffi-2-0-0 | Python C Foreign Function Interface for calling C libraries from Python with C-like declarations. Use when interfacing... |
| 39 | changelog-1-1-0 | Create and maintain changelogs following the Keep a Changelog specification v1.1.0, providing standardized format... |
| 40 | chart-js-4-5-1 | Complete toolkit for Chart.js 4.5.1, the popular JavaScript charting library using HTML5 Canvas rendering. Use when... |
| 41 | check-jsonschema-0-37-2 | CLI tool for validating JSON, YAML, TOML, and JSON5 files against JSON Schema. Use when verifying configuration files,... |
| 42 | chibi-scheme-0-12 | Minimal Scheme implementation for embedding in C applications. Provides tagged-pointer VM with precise non-moving GC,... |
| 43 | chonkie-1-6-4 | Lightweight text chunking library for RAG pipelines providing 12+ chunkers, pipeline API, refineries, vector DB... |
| 44 | coding-guidelines-0-1-0 | Behavioral guidelines to reduce common LLM coding mistakes including overcomplication, hidden assumptions, orthogonal... |
| 45 | crdt-2026-05-03 | Conflict-free replicated data types (CRDTs) replicate across distributed nodes without coordination, guaranteeing... |
| 46 | crun-1-27-1 | Lightweight OCI container runtime written in C for running Linux containers with low memory footprint and high... |
| 47 | cryptography-47-0-0 | Comprehensive toolkit for Python cryptographic operations using the cryptography library v47.0.0. Use when implementing... |
| 48 | curl-8-20-0 | CLI tool and C library for multi-protocol data transfers supporting HTTP/HTTPS, FTP, SFTP, and 30+ protocols. Covers... |
| 49 | cython-3-2-4 | A skill for using Cython 3.2.4, an optimizing Python compiler that makes writing C extensions as easy as Python itself... |
| 50 | d3-7-9-0 | JavaScript library for bespoke data-driven documents providing SVG and Canvas-based visualizations with scales, axes,... |
| 51 | daisyui-5-5-19 | A skill for using DaisyUI 5.5.19, a component library for Tailwind CSS 4 that provides semantic class names for common... |
| 52 | dayjs-1-11-20 | Complete toolkit for date and time manipulation using Day.js 1.11.20, a minimalist 2kB library with... |
| 53 | ddgs-9-14-4 | Metasearch library aggregating results from 10+ web search services (Google, Bing, DuckDuckGo, Brave, Yahoo, Yandex,... |
| 54 | deno-2-7-14 | A comprehensive toolkit for the Deno 2.x JavaScript/TypeScript runtime, covering installation, permissions, built-in... |
| 55 | design-md-0-1-1 | Format for describing visual identity to coding agents. Combines YAML front matter design tokens with markdown prose... |
| 56 | dirac-0-2-89 | 'Open-source coding agent that reduces API costs by 64.8% while maintaining 100% accuracy on complex refactoring tasks.... |
| 57 | docker-docs-2026-04-16 | Comprehensive reference for Docker platform including Docker Engine, Docker Desktop, Docker Compose, Docker... |
| 58 | docxjs-0-3-6 | Renders DOCX documents into semantic HTML in the browser using JavaScript. Use when converting Word documents to HTML... |
| 59 | dspy-3-2-0 | Framework for programming rather than prompting language models. Compiles LM calls into self-improving pipelines by... |
| 60 | duckdb-1-5-2 | High-performance analytical SQL database with support for nested types, vectorized execution, and seamless integration... |
| 61 | duckdb-1-5-3 | Complete toolkit for DuckDB 1.5.3, an in-process SQL OLAP database management system. Covers SQL queries, data... |
| 62 | duckduckgo | Searches DuckDuckGo via its HTML endpoint using scrapling. Returns results as markdown (default), raw HTML, compact... |
| 63 | esbuild-0-28-0 | Complete toolkit for esbuild v0.28 JavaScript bundler providing CLI, JavaScript API, and Go API access for bundling,... |
| 64 | fetch-api | JavaScript Fetch API for making HTTP requests from browsers and workers using promise-based fetch(). Covers... |
| 65 | fltk-1-4-5 | Cross-platform C++ GUI toolkit with ~80 widget classes, OpenGL/GLUT integration, drawing primitives, image support,... |
| 66 | gh-2-92-0 | GitHub CLI v2.92.0 for managing repositories, pull requests, issues, releases, workflows, codespaces, and more from the... |
| 67 | ghostscript-10-07-0 | Interpreter for PostScript, PDF, PCL, XPS page description languages with raster and vector output devices. Converts... |
| 68 | git | 'Complete Git 2.54.0 toolkit covering version control workflows, Conventional Commits v1.0.0, Keep a Changelog message... |
| 69 | grafana-13-0-1 | Grafana 13.0.1 observability platform for querying, visualizing, alerting on, and exploring metrics, logs, traces, and... |
| 70 | gunicorn-26-0-0 | Complete toolkit for Gunicorn 26.0.0 — Python WSGI/ASGI HTTP server with pre-fork worker model. Covers installation,... |
| 71 | haproxy-3-3-8 | Complete HAProxy 3.3.8 toolkit for load balancing, reverse proxying, SSL/TLS termination, and traffic management.... |
| 72 | hnswlib-0-9-0 | Header-only C++ library implementing HNSW graphs for fast approximate nearest neighbor search with Python bindings via... |
| 73 | htm-3-1-1 | A skill for using htm 3.1, a tagged template syntax library that provides JSX-like markup in plain JavaScript without... |
| 74 | htmx-2-0-10 | Complete reference for htmx 2.0.10 — the HTML attributes library for AJAX, WebSockets, SSE, and dynamic DOM updates... |
| 75 | htmx-4-0-0 | 'Build interactive web applications with htmx 4.0, a JavaScript library providing HTML attributes for AJAX, CSS... |
| 76 | hy-1-2-0 | Lisp dialect embedded in Python providing prefix S-expression syntax, compile-time macros, quasiquoting, reader macros,... |
| 77 | jina-ai-reader | Converts any URL to LLM-friendly markdown via r.jina.ai and searches the web with s.jina.ai, returning top results in... |
| 78 | jinja2-3-1-6 | Complete toolkit for Jinja2 v3.1.6 templating engine covering template design, Python API integration, custom... |
| 79 | jq-1-8-1 | Complete toolkit for jq 1.8.1, the lightweight and flexible command-line JSON processor. Use when parsing,... |
| 80 | jsonpath-rfc-9535-1-0-0 | Complete reference for JSONPath RFC 9535, the IETF specification defining string syntax for selecting and extracting... |
| 81 | lambda-calculus | Formal system for expressing computation via function abstraction and application. Covers untyped lambda calculus... |
| 82 | lambda-calculus-and-lisp-2026-05-12 | Covers the relationship between lambda calculus and Lisp, including McCarthy's EVAL, Church encodings in Scheme, the Y... |
| 83 | lingua-py-2-2-0 | Accurate natural language detection library for Python supporting 75 languages with high accuracy on short text and... |
| 84 | lisp-in-c-2026-05-03 | 'Build a Lisp interpreter in C from scratch, covering S-expression parsing, manual memory management, hash-table... |
| 85 | lisp-in-python-2026-05-03 | Build a minimal Lisp interpreter in Python covering the eval-apply cycle, recursive descent parsing, lexical scoping,... |
| 86 | llama-cpp-1-0-0 | C/C++ LLM inference library with GGUF support, quantization, GPU acceleration (CUDA/Metal/HIP/Vulkan/SYCL),... |
| 87 | lodash-4-18-1 | Complete toolkit for Lodash 4.18 utility library providing 300+ helper functions for arrays, collections, objects,... |
| 88 | logfire-4-32-1 | AI observability platform built on OpenTelemetry by the Pydantic team. Native SDKs for Python, JavaScript/TypeScript,... |
| 89 | logic | Comprehensive reference covering formal logic systems from propositional through higher-order logic, plus modal logic,... |
| 90 | lua-5-5-0 | Lightweight embeddable scripting language with a small C footprint, dynamic typing via tables, coroutines, and a... |
| 91 | matplotlib-3-10-9 | Comprehensive toolkit for Matplotlib 3.10.9, the Python plotting library for static, animated, and interactive... |
| 92 | mcp-2025-11-25 | Model Context Protocol (MCP) 2025-11-25 specification covering client-host-server architecture, JSON-RPC messaging,... |
| 93 | mem0-2-0-1 | Self-improving memory layer for LLM agents (Mem0 v2.0.1) enabling persistent context across sessions with single-pass... |
| 94 | mempalace-3-3-4 | Local AI memory system that mines projects and conversations into a searchable index using ChromaDB for vector search... |
| 95 | mermaid-11-15-0 | Complete toolkit for Mermaid 11.15.0 providing 29 diagram types including flowcharts, sequence diagrams, Gantt charts,... |
| 96 | mermaid-validator-0-1-0 | Lightweight Mermaid diagram syntax validator using the official mermaid parser with jsdom. Validates diagrams in... |
| 97 | nekovm-2-4-1 | Stack-based bytecode VM and dynamically typed scripting language, primarily as a compilation target for Haxe. Provides... |
| 98 | networkx-3-6-1 | Python package for creating, manipulating, and studying complex networks. Supports graph generation, algorithms... |
| 99 | networkxternal-0-5 | NetworkX-compatible interface for external memory MultiDiGraphs persisted in databases (SQLite, PostgreSQL, MySQL,... |
| 100 | nextjs-16-2-4 | Build production-ready React applications with Next.js 16.2.4, providing App Router and Pages Router, server/client... |
| 101 | nginx-1-30-0 | High-performance HTTP server, reverse proxy, and load balancer supporting HTTP/HTTPS proxying, SSL/TLS termination,... |
| 102 | nltk-3-9-4 | Complete toolkit for Natural Language Processing with NLTK 3.9.4, covering tokenization, stemming, lemmatization, POS... |
| 103 | nodejs-24-14-0 | Complete Node.js 24.14 runtime toolkit covering core modules, async programming, HTTP servers, file system operations,... |
| 104 | nuitka-4-0-8 | Python compiler that translates Python code to C and native executables. Use when compiling Python applications for... |
| 105 | numba-0-65-1 | JIT compiler for Python that translates numerical code into optimized machine code using LLVM. Supports @jit, @njit,... |
| 106 | numeral-2-0-6 | A JavaScript library for formatting and manipulating numbers. Use when formatting currency, percentages, bytes, time... |
| 107 | numkong-7-6-0 | Ultra-fast mixed-precision vector similarity and distance library with 2000+ SIMD kernels across x86, ARM, RISC-V.... |
| 108 | numpy-2-4-4 | Fundamental package for scientific computing with Python, providing n-dimensional arrays, mathematical functions,... |
| 109 | oat-0-6-0 | Ultra-lightweight semantic UI component library (~8KB CSS + JS, zero dependencies) that styles HTML elements by default... |
| 110 | obscura-0-1-1 | Lightweight headless browser engine written in Rust for web scraping and AI agent automation. Runs JavaScript via V8,... |
| 111 | openai-2-33-0 | Python SDK for OpenAI API v2.33 providing type-safe access to Responses API, Chat Completions, embeddings, audio... |
| 112 | openai-python-2-38-0 | Complete toolkit for OpenAI Python SDK 2.38.0 providing typed sync/async clients for the Responses API, Chat... |
| 113 | openpyxl-3-1-3 | Complete toolkit for openpyxl 3.1.3 providing Excel xlsx/xlsm/xltx/xltm file creation, reading, writing, styling,... |
| 114 | opentelemetry-1-56-0 | Complete OpenTelemetry 1.56.0 specification toolkit for implementing distributed tracing, metrics collection, and... |
| 115 | opentelemetry-collector-1-56-0 | Vendor-agnostic telemetry collector for OpenTelemetry providing configurable pipelines for traces, metrics, and logs.... |
| 116 | opentelemetry-python-1-41-1 | OpenTelemetry Python toolkit for distributed tracing, metrics collection, and log management with OTLP exporters,... |
| 117 | ot-2026-05-03 | Operational Transformation theory and practice for consistency in real-time collaborative editing. Covers... |
| 118 | pacote-21-5-0 | Inspect, download, and extract npm packages without installing them first using pacote 21.5 via npx. Supports registry... |
| 119 | pandas-3-0-3 | Complete toolkit for pandas 3.0.3 providing DataFrame and Series data structures, tabular data manipulation, groupby... |
| 120 | pandoc-3-9-0-2 | Universal document converter supporting 50+ input formats (Markdown, HTML, LaTeX, docx, EPUB, Org, RST, AsciiDoc) and... |
| 121 | paramiko-4-0-0 | Complete toolkit for Paramiko 4.0.0, a pure-Python SSHv2 protocol implementation providing both client and server... |
| 122 | parquet-2-2-0 | Complete toolkit for Apache Parquet 2.2.0 columnar storage format covering physical and logical types, schema... |
| 123 | payloadcms-3-84-1 | Payload CMS headless CMS toolkit including collections, fields, access control, authentication, custom components,... |
| 124 | payloadcms-blank-3-84-1 | Minimal Payload CMS 3.84.1 starter template providing a clean foundation for building custom headless CMS applications... |
| 125 | payloadcms-ecommerce-3-84-1 | Payload CMS ecommerce template providing production-ready online store with products, variants, carts, orders, Stripe... |
| 126 | payloadcms-website-3-84-1 | Payload CMS website template providing production-ready starter for content-driven websites, blogs, and portfolios with... |
| 127 | peg-2026-05-03 | Parsing Expression Grammars (PEGs) — recognition-based formal grammars using ordered choice to eliminate ambiguity,... |
| 128 | pi-mono-0-74-0 | 'Complete toolkit for the pi coding agent monorepo v0.74.0 covering five packages: pi-coding-agent (interactive CLI),... |
| 129 | picocss-2-1-1 | Minimalist CSS framework that styles semantic HTML elements by default with responsive typography, automatic light/dark... |
| 130 | pinecone-router-7-5-0 | Client-side routing toolkit for Alpine.js applications using Pinecone Router v7.5, providing route matching, template... |
| 131 | pipe | Unix-style pipe expression syntax for chaining multiple agent operations sequentially. Each stage's output becomes the... |
| 132 | plan | Phase/task based workflow system with PLAN.md as single source of truth. Use when tackling projects that require... |
| 133 | podman-5-8-1 | Daemonless container engine with Docker-compatible CLI for managing containers, pods, images, volumes, and networks.... |
| 134 | podman-5-8-2 | Daemonless container engine with Docker-compatible CLI for managing containers, pods, images, volumes, and networks.... |
| 135 | podman-compose-1-5-0 | Orchestrates multi-container applications using Compose specification files with Podman backend. Use when deploying... |
| 136 | podman-py-5-8-0 | Python client library for Podman container engine providing programmatic access to containers, images, pods, networks,... |
| 137 | polars-0-53-0 | Complete toolkit for Polars 0.53.0 providing high-performance DataFrame computing with lazy evaluation,... |
| 138 | poppler-26-05-0 | PDF rendering library providing C++, glib, Qt5, and Qt6 APIs for loading, parsing, rendering, and extracting content... |
| 139 | prescheme-2026-05-03 | Statically typed Scheme dialect that compiles to C via Hindley/Milner type inference and CPS transformations. Combines... |
| 140 | prometheus-3-11-3 | Complete toolkit for Prometheus 3.11.3 covering configuration, PromQL querying, service discovery, rules, alerting, and... |
| 141 | pulp-3-3-0 | Complete toolkit for PuLP 3.3.0, a Python linear and mixed-integer programming modeler generating MPS/LP/JSON files and... |
| 142 | pyarrow-24-0-0 | Complete toolkit for PyArrow 24.0.0 providing columnar in-memory data structures, vectorized compute functions,... |
| 143 | pycrdt-0-12-50 | Python bindings for Yrs, the Rust port of the Yjs CRDT framework. Provides shared data types (Text, Array, Map, XML)... |
| 144 | pyomo-6-10-0 | Python-based open-source optimization modeling language supporting LP, QP, NLP, MILP, MIQP, MINLP, stochastic... |
| 145 | python-docx-1-2-0 | Complete toolkit for python-docx 1.2.0, a Python library for creating, reading, and updating Microsoft Word (.docx)... |
| 146 | python-lambda-calculus-3-1-0 | Python library implementing Lambda calculus operations including term construction (Variable, Abstraction,... |
| 147 | python-louvain-0-16 | Python implementation of the Louvain algorithm for community detection in graphs. Produces modularity-optimized... |
| 148 | python-prometheus-0-25-0 | Official Prometheus Python client library v0.25.0 for instrumenting Python applications with metrics. Provides Counter,... |
| 149 | python-scrypt-0-9-4 | Python toolkit for scrypt-based key derivation and password hashing. Use when implementing secure password storage,... |
| 150 | pytorch-2-12-0 | Complete toolkit for PyTorch 2.12 providing n-dimensional tensors, automatic differentiation, neural network modules,... |
| 151 | pywebview-6-2-1 | Cross-platform wrapper around native webview components that lets Python applications display HTML content in a native... |
| 152 | pyzmq-27-1-0 | Complete toolkit for Python bindings to ZeroMQ (pyzmq 27.x) covering socket types, messaging patterns, async/await... |
| 153 | quickjs-2025-09-13 | Small and fast JavaScript engine supporting ES2023 with C API for embedding, qjs REPL interpreter, and qjsc bytecode... |
| 154 | qwen3-embedding-1-0-0 | Complete toolkit for Qwen3 Embedding models (0.6B, 4B, 8B) and Qwen3 Reranker models providing state-of-the-art text... |
| 155 | qwen3-reranker-1-0-0 | Comprehensive toolkit for Qwen3 Reranker models (0.6B, 4B, 8B) — cross-encoder text reranking with 100+ language... |
| 156 | qwen3-vl-embedding-0-1-0 | Complete toolkit for Qwen3-VL-Embedding 0.1.0 multimodal embedding models (2B and 8B) supporting text, images,... |
| 157 | qwen3-vl-reranker-1-0-0 | Complete toolkit for Qwen3-VL-Reranker (2B and 8B) multimodal reranking models that score relevance of text, image,... |
| 158 | raft-2026-05-03 | Raft consensus algorithm for replicated log management across server clusters. Covers leader election, log replication,... |
| 159 | ralph-orchestrator-2-9-2 | Orchestration framework that keeps AI agents in a loop until tasks are done. Supports Claude Code, Gemini CLI, Codex,... |
| 160 | redis-om-python-1-1-0 | A skill for using Redis OM Python v1.1, an object mapping library that provides declarative models, automatic... |
| 161 | redis-py-7-4-0 | Comprehensive Python client for Redis database and key-value store. Use when building Python applications requiring... |
| 162 | rich-15-0-0 | Python library for rich text and beautiful terminal formatting. Provides color, tables, progress bars, markdown... |
| 163 | rqlite-10-0-1 | Comprehensive toolkit for rqlite 10.0.1, a lightweight distributed relational database built on SQLite with Raft... |
| 164 | rsync-3-4-2 | Complete toolkit for rsync 3.4.2, the fast file-copying tool using delta-transfer algorithm. Use when backing up files,... |
| 165 | rtk-0-42-0 | CLI proxy that filters and compresses command outputs before they reach LLM context, reducing token consumption by... |
| 166 | ruff-0-15-12 | Extremely fast Python linter and code formatter written in Rust with 900+ rules, block-level suppressions, and Markdown... |
| 167 | rustfs-1-0-0-beta-1 | High-performance distributed object storage system with S3-compatible API, OpenStack Swift support, and comprehensive... |
| 168 | s-expression | S-expressions (symbolic expressions) are a minimal notation for nested tree-structured data using atoms and lists.... |
| 169 | s-expression-alternatives | Alternative syntaxes for Lisp-family languages that reduce or eliminate parentheses while preserving homoiconicity and... |
| 170 | s-expression-interpreter | Build and understand s-expression interpreters in Python and C. Covers lexer-free tokenization, recursive descent... |
| 171 | scheme-in-python-2026-05-03 | Build a Scheme interpreter in Python covering tokenization, eval/apply loop, environment frames with lexical and... |
| 172 | scikit-learn-1-8-0 | Complete scikit-learn 1.8 toolkit for machine learning covering supervised and unsupervised algorithms, pipelines,... |
| 173 | scipy-1-17-1 | Scientific computing library for Python covering optimization, integration, interpolation, linear algebra, signal... |
| 174 | scrapling-0-4-8 | Adaptive web scraping framework for Python providing HTML parsing with CSS/XPath/text/regex selection, HTTP and... |
| 175 | semver-2-0-0 | Implement and validate Semantic Versioning 2.0.0 to manage software version numbers, determine compatibility, compare... |
| 176 | sentence-transformers-5-4-1 | Comprehensive toolkit for computing text embeddings, semantic search, and reranking using Sentence Transformers v5.4.1.... |
| 177 | sheetjs-0-20-3 | Spreadsheet data toolkit for reading, writing, and converting 40+ file formats including XLSX, CSV, JSON, HTML, ODS.... |
| 178 | skman | Scaffold, validate, and inspect agent skills (SKILL.md files). Use when creating new skills, checking skill format... |
| 179 | solid-meta-0-29-4 | Manages document head tags in SolidJS applications with @solidjs/meta v0.29.4, providing SSR-ready Document Head... |
| 180 | solid-router-0-16-1 | The universal router for SolidJS providing fine-grained reactivity for route navigation with support for history-based,... |
| 181 | solid-start-1-3-2 | Fullstack framework for SolidJS providing SSR, SSG, API routes, file-based routing, and server functions. Use when... |
| 182 | solidjs-1-9-12 | A comprehensive toolkit for building reactive user interfaces with SolidJS 1.x, a declarative JavaScript framework... |
| 183 | spacy-3-8-14 | Industrial-strength NLP library for Python providing tokenization, named entity recognition, dependency parsing, and... |
| 184 | spec-kit-0-8-3 | Spec-Driven Development toolkit for specification-first workflows with AI agents. Generate executable specifications,... |
| 185 | sqlalchemy-2-0-49 | Complete SQLAlchemy 2.0 toolkit for database operations, ORM mapping, and SQL expression construction. Use when... |
| 186 | sqlite-3-53-0 | Embedded SQL database providing ACID transactions, full-text search (FTS5), spatial indexing (R-Tree), JSON processing,... |
| 187 | stanza-1-11-1 | Stanford NLP Group's Python NLP library for 80+ languages providing tokenization, POS tagging, lemmatization,... |
| 188 | stitch-2026-05-04 | AI-powered UI design tool generating high-fidelity screens and frontend code from text prompts and images. Provides MCP... |
| 189 | stringzilla-4-6-0 | High-performance SIMD-accelerated string library for search, hashing, sorting, and fuzzy matching in... |
| 190 | sympy-1-14-0 | Complete toolkit for SymPy 1.14.0 providing symbolic mathematics in Python including algebra, calculus, matrices,... |
| 191 | tailwindcss-4-2-4 | A skill for using Tailwind CSS v4.2, a utility-first CSS framework with CSS-based configuration via @theme, OKLCH color... |
| 192 | tailwindcss-browser-4-2-4 | In-browser Tailwind CSS v4.2 build (@tailwindcss/browser) that compiles utility classes at runtime without a build... |
| 193 | tea-0-14-0 | Official CLI for Gitea servers. Manage repositories, issues, pull requests, releases, and admin operations from the... |
| 194 | temporal-api | ECMAScript Temporal API for date/time management replacing legacy Date. Provides timezone-aware arithmetic, calendar... |
| 195 | textblob-0-20-0 | Python library for simplified natural language processing providing POS tagging, noun phrase extraction, sentiment... |
| 196 | textual-8-2-5 | Python framework for building terminal and browser UIs. Provides widget-based DOM, CSS styling (.tcss), reactive... |
| 197 | tinycc-0-9-27 | Complete toolkit for TinyCC 0.9.27, a small hyper-fast C compiler generating native x86/x86_64/ARM code without an... |
| 198 | tinypy-1-1-0 | Minimalist Python implementation in ~64k of code with a bootstrapped parser, bytecode compiler, and VM with incremental... |
| 199 | tinyscheme-1-41 | Lightweight Scheme interpreter (R5RS subset) in ~5000 lines of C, designed as an embeddable scripting engine.... |
| 200 | tokenizers-0-23-1 | Fast state-of-the-art tokenizers library for NLP written in Rust with Python, Node.js, and Ruby bindings. Use when... |
| 201 | transformers-5-7-0 | Complete toolkit for Hugging Face Transformers 5.7.0 providing pretrained models for NLP, vision, audio, video, and... |
| 202 | ty-0-0-33 | Extremely fast Python type checker and language server written in Rust, 10x-100x faster than mypy and Pyright. Provides... |
| 203 | tzip | Lightweight token-pruning communication mode that drops filler and hedging while keeping full sentences and... |
| 204 | upx-5-1-1 | A skill for using UPX (Ultimate Packer for eXecutables) v5.1.1 to compress and decompress executable files across... |
| 205 | usearch-2-25-1 | High-performance single-file similarity search engine for vectors using HNSW with user-defined metrics, quantization,... |
| 206 | uv-0-11-19 | >- |
| 207 | vega-6-2-0 | 'Vega 6.2.0 — declarative visualization grammar for creating interactive charts in JSON. Define data, scales, marks,... |
| 208 | vega-embed-7-1-0 | 'Embed interactive Vega and Vega-Lite visualizations into web pages. Load specs from URLs or JSON objects, render with... |
| 209 | vega-lite-6-4-3 | 'Vega-Lite 6.4.3 — high-level grammar of interactive graphics. Generate, author, and debug Vega-Lite specifications for... |
| 210 | vega-lite-validator-0-1-0 | Validates Vega-Lite 6.4.3 JSON specifications against the official JSON Schema using check-jsonschema. Catches... |
| 211 | voidauth-1-12-3 | Open-source SSO authentication and user management provider for self-hosted applications. Provides OIDC Provider,... |
| 212 | webfetch | Fetches any URL and converts the full page to clean AI-targeted markdown using scrapling. Use when scraping arbitrary... |
| 213 | websearch | Searches DuckDuckGo via its HTML endpoint and outputs results as raw YAML. Uses a deterministic bash script, extracts... |
| 214 | yjs-13-6-30 | CRDT framework for conflict-free collaborative editing with shared types (Y.Map, Y.Array, Y.Text). Provides... |
| 215 | yq-4-53-2 | A skill for using yq v4.x, a lightweight and portable command-line YAML, JSON, XML, INI, Properties, CSV/TSV, HCL,... |
| 216 | zeromq-wiki-3-2-0 | A comprehensive toolkit for ZeroMQ (ØMQ) messaging library covering socket patterns, protocols, architecture, and best... |
| 217 | zeromq-zguide-3-2-0 | Complete ZeroMQ ZGuide 3.2 toolkit covering messaging patterns, socket types, reliability mechanisms, and distributed... |

## Statistics

- **Total Skills**: 217
