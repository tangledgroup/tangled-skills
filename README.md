# tangled-skills

Collection of Skills for Agents by Tangled

## About

All skills in this repository are automatically generated using the `skill` skill. Each skill is created from public references, official documentation URLs, and other publicly available resources to ensure accuracy and completeness.

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


## Skills Table

| No | Skill | Project | Version | Technologies | Description |
|----|-------|---------|---------|--------------|-------------|
| 1 | a2a-1-0-0 | a2a | 1.0.0 | agent-communication, multi-agent, interoperability, protocol, json-rpc | The Agent2Agent (A2A) Protocol v1.0.0 is an open standard enabling communication and interoperability between ... |
| 2 | acp-0-12-2 | acp | 0.12.2 | agent-protocol, json-rpc, coding-agents, editor-integration, ai-agents | The Agent Client Protocol (ACP) standardizes communication between code editors/IDEs and AI coding agents using ... |
| 3 | agent-coding-mini-rasbt-0-1-0 | agent-coding-mini-rasbt | 0.1.0 | coding-agent, ollama, local-ai, autonomous-agent, python | A minimal standalone coding agent framework by Sebastian Raschka backed by Ollama that provides workspace context ... |
| 4 | agent-coding-wyattdave-0-1-0 | agent-coding-wyattdave | 0.1.0 | ai-agents, prompt-engineering, vscode-extensions, coding-assistants, customization | A toolkit for creating custom AI coding agents using prompt engineering, instruction files, and skill modules. Use ... |
| 5 | agentmemory-0-8-10 | agentmemory | 0.8.10 | ai-agent, persistent-memory, mcp-server, hybrid-search, knowledge-graph | Persistent memory engine for AI coding agents providing automatic cross-session context capture, hybrid search (BM25 ... |
| 6 | agentmemory-0-8-9 | agentmemory | 0.8.9 | ai-agents, memory, mcp-server, persistent-context, vector-search | Persistent memory engine for AI coding agents providing automatic cross-session context capture, hybrid search (BM25 ... |
| 7 | agentmemory-0-9-4 | agentmemory | 0.9.4 | ai-agent, persistent-memory, mcp-server, hybrid-search, knowledge-graph | Persistent memory engine for AI coding agents providing automatic cross-session context capture, hybrid search (BM25 ... |
| 8 | agent-nirzabari-0-1-0 | agent-nirzabari | 0.1.0 | ai-agents, coding-agents, harness-engineering, llm-systems, agent-architecture | A comprehensive guide to understanding and building coding agent harnesses, covering the 7-layer architecture, ... |
| 9 | agent-ralph-loop-claude | agent-ralph-loop-claude | 1.0.0 | claude-code, plugin, iterative-development, autonomous-agents, ralph-wiggum | Implements the Ralph Wiggum technique as a Claude Code plugin for iterative, self-referential AI development loops. ... |
| 10 | agent-ralph-loop-vercel-labs | agent-ralph-loop-vercel-labs | 0.0.3 | autonomous-agent, ai-sdk, iterative-loop, coding-agent, continuous-autonomy | Continuous autonomy framework for the Vercel AI SDK implementing the Ralph Wiggum technique — an iterative outer ... |
| 11 | agent-ralph-wiggum-fstandhartinger-0-3-0 | agent-ralph-wiggum-fstandhartinger | 0.3.0 | autonomous-development, spec-driven, iterative-loops, ai-coding, ralph-wiggum | Autonomous AI coding with spec-driven development combining iterative bash loops and SpecKit-style specifications ... |
| 12 | agent-ralph-wiggum-ghuntley | agent-ralph-wiggum-ghuntley | 0.1.0 | ralph-wiggum, autonomous-development, iterative-loops, greenfield, prompt-tuning | Geoffrey Huntley's Ralph Wiggum technique — a monolithic iterative loop pattern for autonomous AI-driven software ... |
| 13 | agent-ralph-wiggum-loop-beuke | agent-ralph-wiggum-loop-beuke | 1.0.0 | ralph-wiggum, agentic-loops, autonomous-agents, ai-safety, feedback-systems | Principles and conceptual framework of the Ralph Wiggum Loop pattern for goal-oriented autonomous AI agent loops. ... |
| 14 | agent-ralph-wiggum-snarktank | agent-ralph-wiggum-snarktank | 0.1.0 | ralph-wiggum, autonomous-agent, coding-loop, prd-driven, claude-code | Autonomous AI coding loop that runs AI coding tools (Amp or Claude Code) repeatedly until all PRD items are ... |
| 15 | agent-wiggum-cli-federiconeri | agent-wiggum-cli-federiconeri | 0.18.3 | autonomous-coding, ralph-loop, spec-driven-development, ai-agent, claude-code | Wiggum CLI is an open-source autonomous coding agent that plugs into any codebase — scans your tech stack, generates ... |
| 16 | aiohttp-3-13-0 | aiohttp | 3.13.0 | http, async, client, server, websocket | Async HTTP client/server for Python asyncio. Use when building async web applications, REST APIs, or making ... |
| 17 | aiohttp-3-13-5 | aiohttp | 3.13.5 | http, async, client, server, websocket | Async HTTP client/server for Python asyncio. Use when building async web applications, REST APIs, or making ... |
| 18 | aiohttp-cors-0-8-1 | aiohttp-cors | 0.8.1 | cors, aiohttp, web-security, http-headers, cross-origin | A skill for implementing Cross-Origin Resource Sharing (CORS) support in aiohttp web applications using aiohttp-cors ... |
| 19 | aiohttp-jinja2-1-6-0 | aiohttp-jinja2 | 1.6.0 | aiohttp, jinja2, templating, web-framework, async | Jinja2 template renderer for aiohttp.web applications providing decorator-based rendering, context processors, URL ... |
| 20 | aiohttp-security-0-5-0 | aiohttp-security | 0.5.0 | aiohttp, authentication, authorization, identity-policy, permission | Authentication and authorization toolkit for aiohttp.web applications providing identity policies (cookies, ... |
| 21 | aiohttp-session-2-12-0 | aiohttp-session | 2.12.0 | aiohttp, sessions, web, async, storage | Server-side sessions for aiohttp.web applications using aiohttp-session 2.12, providing multiple storage backends ... |
| 22 | aiohttp-session-2-12-1 | aiohttp-session | 2.12.1 | aiohttp, sessions, web, async, storage | Server-side sessions for aiohttp.web applications using aiohttp-session 2.12, providing multiple storage backends ... |
| 23 | aiohttp-sse-2-2-0 | aiohttp-sse | 2.2.0 | aiohttp, server-sent-events, sse, eventsource, streaming | Python library for Server-Sent Events (SSE) support in aiohttp applications. Use when building real-time streaming ... |
| 24 | aioitertools-0-13-0 | aioitertools | 0.13.0 | asyncio, python, itertools, async-iterators, generators | Async-compatible versions of itertools, builtins, and more for Python asyncio. Use when building async Python ... |
| 25 | aiorwlock-1-5-1 | aiorwlock | 1.5.1 | asyncio, concurrency, synchronization, read-write-lock | Async read-write lock for Python asyncio providing concurrent reader access and exclusive writer access. Use when ... |
| 26 | aiozmq-0-7-0 | aiozmq | 0.7.0 | zeromq, asyncio, rpc, messaging, distributed | Async ZeroMQ integration for Python asyncio providing transport-level APIs, stream abstraction, and RPC frameworks ... |
| 27 | aiozmq-1-0-0 | aiozmq | 1.0.0 | zeromq, asyncio, rpc, messaging, distributed | Async ZeroMQ integration for Python asyncio providing transport-level APIs, stream abstraction, and RPC frameworks ... |
| 28 | alpinejs-3-15-11 | alpinejs | 3.15.11 | javascript, frontend, reactive, html, directives | A skill for building reactive user interfaces with Alpine.js 3.15, a minimal JavaScript framework that uses ... |
| 29 | alpinejs-3-15-12 | alpinejs | 3.15.12 | javascript, frontend, reactive, html, directives | A skill for building reactive user interfaces with Alpine.js 3.15, a minimal JavaScript framework that uses ... |
| 30 | argon2-25-1-0 | argon2 | 25.1.0 | password-hashing, authentication, cryptography, argon2, security | Python toolkit for password hashing and verification using the Argon2 algorithm via argon2-cffi 25.x. Use when ... |
| 31 | asyncstdlib-3-14-0 | asyncstdlib | 3.14.0 | python, async, itertools, builtins, functools | Python async standard library providing async versions of builtins, itertools, functools, contextlib, heapq, and ... |
| 32 | autoloop-0-4-0 | autoloop | 0.4.0 | autonomous-agents, multi-role-loops, event-routing, preset-workflows, agent-harness | Simpler, opinionated loop harness for inspectable long-running agent workflows. Spinoff of ralph-orchestrator that ... |
| 33 | automerge-3-2-6 | automerge | 3.2.6 | automerge, crdt, local-first, collaborative-editing, offline-sync | CRDT library for building collaborative, local-first applications with automatic conflict-free merging. Provides ... |
| 34 | axios-1-15-0 | axios | 1.15.0 | http, rest, api, fetch, ajax | A comprehensive toolkit for making HTTP requests using Axios 1.x, a promise-based HTTP client for browser and ... |
| 35 | axios-1-15-2 | axios | 1.15.2 | http, rest, api, fetch, ajax | A comprehensive toolkit for making HTTP requests using Axios 1.x, a promise-based HTTP client for browser and ... |
| 36 | bcrypt-5-0-0 | bcrypt | 5.0.0 | password-hashing, cryptography, security, authentication, key-derivation | A skill for password hashing and key derivation using bcrypt 5.0 in Python. Use when implementing secure password ... |
| 37 | boto3-1-42-89 | boto3 | 1.42.89 | aws, boto3, cloud, python, sdk | Complete toolkit for AWS SDK for Python (Boto3) 1.42.89 providing high-level resource interface and low-level client ... |
| 38 | boto3-1-43-1 | boto3 | 1.43.1 | aws, boto3, cloud, python, sdk | Complete toolkit for AWS SDK for Python (Boto3) 1.43.1 providing high-level resource interface and low-level client ... |
| 39 | bun-1-3-12 | bun | 1.3.12 | javascript, typescript, runtime, package-manager, bundler | Complete toolkit for Bun 1.3.12 JavaScript runtime, package manager, bundler, and test runner. Use when building ... |
| 40 | bun-1-3-13 | bun | 1.3.13 | javascript, typescript, runtime, package-manager, bundler | Complete toolkit for Bun 1.3.13 JavaScript runtime, package manager, bundler, and test runner. Use when building ... |
| 41 | caddy-2-11-2 | caddy | 2.11.2 | web server, reverse proxy, HTTPS, Caddyfile, automatic SSL | Complete Caddy 2.11.2 web server toolkit covering Caddyfile configuration, JSON API, CLI commands, automatic HTTPS ... |
| 42 | caveman-1-5-1 | caveman | 1.5.1 | communication, token-optimization, brevity, efficiency | Ultra-compressed communication mode that cuts token usage by ~75% while maintaining full technical accuracy. ... |
| 43 | cffi-2-0-0 | cffi | 2.0.0 | cffi, c-integration, ffi, foreign-function-interface, python-c-bindings | Python C Foreign Function Interface for calling C libraries from Python |
| 44 | changelog-1-1-0 | changelog | 1.1.0 | changelog, documentation, versioning, semver, release-notes | A skill for creating and maintaining changelogs following the Keep a Changelog specification v1.1.0, providing ... |
| 45 | chart-js-4-5-1 | chart-js | 4.5.1 | charts, canvas, data-visualization, javascript, html5 | Complete toolkit for Chart.js 4.5.1, the most popular open-source JavaScript charting library using HTML5 Canvas ... |
| 46 | chibi-scheme-0-12 | chibi-scheme | 0.12 | chibi-scheme, scheme, lisp, embedded-vm, c-ffi | Minimal Scheme implementation for embedding in C applications. Provides a tagged-pointer VM with precise non-moving ... |
| 47 | chonkie-1-6-2 | chonkie | 1.6.2 | text-chunking, rag, nlp, embeddings, vector-databases | A skill for using Chonkie 1.6.2, a lightweight Rust-based text chunking library for RAG pipelines providing 10+ ... |
| 48 | chonkie-1-6-4 | chonkie | 1.6.4 | text-chunking, rag, nlp, embeddings, vector-databases | Lightweight text chunking library for fast, efficient RAG pipelines. Provides 12+ chunkers (token, sentence, ... |
| 49 | coding-guidelines-0-1-0 | coding-guidelines | 0.1.0 | behavioral-guidelines, code-quality, simplicity, llm-best-practices | Behavioral guidelines to reduce common LLM coding mistakes including |
| 50 | crdt-2026-05-03 | crdt | 2026-05-03 | crdt, distributed-systems, conflict-resolution, collaborative-editing, eventual-consistency | Conflict-free replicated data types (CRDTs) replicate across distributed nodes without coordination, guaranteeing ... |
| 51 | crun-1-27-0 | crun | 1.27.0 | oci-runtime, containers, podman, checkpointing, criu | Lightweight OCI container runtime written in C for running Linux containers with low memory footprint and high ... |
| 52 | crun-1-27-1 | crun | 1.27.1 | oci-runtime, containers, podman, checkpointing, criu | Lightweight OCI container runtime written in C for running Linux containers with low memory footprint and high ... |
| 53 | cryptography-46-0-0 | cryptography | 46.0.0 | cryptography, encryption, hashing, asymmetric, symmetric | Comprehensive toolkit for Python cryptographic operations using the cryptography library. Use when implementing ... |
| 54 | cryptography-47-0-0 | cryptography | 47.0.0 | cryptography, encryption, hashing, asymmetric, symmetric | Comprehensive toolkit for Python cryptographic operations using the cryptography library v47.0.0. Use when ... |
| 55 | curl-8-19-0 | curl | 8.19.0 | HTTP client, FTP, URL transfer, libcurl, CLI tool | Complete toolkit for curl 8.19.0 CLI tool and libcurl C library covering command-line usage, URL syntax, ... |
| 56 | curl-8-20-0 | curl | 8.20.0 | HTTP client, FTP, URL transfer, libcurl, CLI tool | Complete toolkit for curl 8.20.0 CLI tool and libcurl C library covering command-line usage, URL syntax, ... |
| 57 | cython-3-2-4 | cython | 3.2.4 | python, compiler, c-extension, performance, optimization | A skill for using Cython 3.2.4, an optimizing Python compiler that makes |
| 58 | d3-7-9-0 | d3 | 7.9.0 | JavaScript, visualization, SVG, Canvas, data-visualization | Complete toolkit for D3.js 7.9.0, the JavaScript library for bespoke data-driven documents providing SVG and ... |
| 59 | daisyui-5-5-0 | daisyui | 5.5.0 | tailwindcss, daisyui, ui-components, theming, css-framework | A skill for using DaisyUI 5.5, a component library for Tailwind CSS 4 that provides semantic class names for common ... |
| 60 | daisyui-5-5-19 | daisyui | 5.5.19 | tailwindcss, daisyui, ui-components, theming, css-framework | A skill for using DaisyUI 5.5.19, a component library for Tailwind CSS 4 that provides semantic class names for ... |
| 61 | dayjs-1-11-0 | dayjs | 1.11.0 | date, time, parsing, formatting, manipulation | Complete toolkit for date and time manipulation using Day.js 1.11, a minimalist 2kB library with ... |
| 62 | dayjs-1-11-20 | dayjs | 1.11.20 | date, time, parsing, formatting, manipulation | Complete toolkit for date and time manipulation using Day.js 1.11.20, a minimalist 2kB library with ... |
| 63 | deno-2-7-0 | deno | 2.7.0 | javascript, typescript, runtime, web-server, cli-tools | A comprehensive toolkit for the Deno 2.x JavaScript/TypeScript runtime, |
| 64 | deno-2-7-14 | deno | 2.7.14 | javascript, typescript, runtime, web-server, cli-tools | A comprehensive toolkit for the Deno 2.x JavaScript/TypeScript runtime, |
| 65 | design-md-0-1-1 | design-md | 0.1.1 | design.md, design-tokens, design-system, cli-tool, google | "DESIGN.md format for describing visual identity to coding agents. Combines YAML front matter design tokens (colors, ... |
| 66 | dirac-0-2-89 | dirac | 0.2.89 | coding-agent, hash-anchored-edits, ast-manipulation, tree-sitter, multi-file-batching | Open-source coding agent that reduces API costs by 64.8% while maintaining 100% accuracy on complex refactoring ... |
| 67 | docker-docs-2026-04-16 | docker-docs | 2026-04-16 | containers, docker-engine, docker-desktop, docker-compose, dockerfile | Comprehensive reference for Docker platform including Docker Engine, |
| 68 | dspy-3-2-0 | dspy | 3.2.0 | llm-programming, prompt-optimization, ai-compilation, few-shot-learning, instruction-tuning | DSPy is the framework for programming—rather than prompting—language models. It provides modular AI system ... |
| 69 | duckdb-1-5-2 | duckdb | 1.5.2 | analytics, olap, embedded-database, sql, data-science | High-performance analytical SQL database with support for nested types, vectorized execution, and seamless ... |
| 70 | duckduckgo-2026-05-08 | duckduckgo | 0.1.2 | web-search, web search, duckduckgo | Searches DuckDuckGo using the HTML endpoint (default, html→markdown via scrapling) and JSON API (--format json), ... |
| 71 | esbuild-0-28-0 | esbuild | 0.28.0 | javascript, bundler, typescript, jsx, css | Complete toolkit for esbuild v0.28 JavaScript bundler providing CLI, JavaScript API, and Go API access for bundling, ... |
| 72 | fltk-1-4-5 | fltk | 1.4.5 | fltk, gui, c++, desktop, widgets | Cross-platform C++ GUI toolkit with ~80 widget classes, OpenGL/GLUT integration, drawing primitives, image support ... |
| 73 | gh-2-91-0 | gh | 2.91.0 | github, cli, devops, automation, ci-cd | GitHub CLI v2.91.0 for managing repositories, pull requests, issues, releases, workflows, codespaces, and more from ... |
| 74 | gh-2-92-0 | gh | 2.92.0 | github, cli, devops, automation, ci-cd | GitHub CLI v2.92.0 for managing repositories, pull requests, issues, releases, workflows, codespaces, and more from ... |
| 75 | git | git | 0.2.1 | meta, meta-skill, git, version-control, conventional-commits | Complete Git 2.54.0 toolkit covering version control workflows, Conventional Commits v1.0.0, Keep a Changelog ... |
| 76 | haproxy-3-3-0 | haproxy | 3.3.0 | load balancing, reverse proxy, SSL termination, high availability, HTTP proxy | Complete HAProxy 3.3.0 toolkit for load balancing, reverse proxying, |
| 77 | haproxy-3-3-8 | haproxy | 3.3.8 | load balancing, reverse proxy, SSL termination, high availability, HTTP proxy | Complete HAProxy 3.3.8 toolkit for load balancing, reverse proxying, |
| 78 | hnswlib-0-9-0 | hnswlib | 0.9.0 | ann, vector-search, hnsw, nearest-neighbor, simd | Header-only C++ library implementing Hierarchical Navigable Small World graphs for fast approximate nearest neighbor ... |
| 79 | htm-3-1-0 | htm | 3.1.0 | jsx-alternative, tagged-templates, preact, react, virtual-dom | A skill for using htm 3.1, a tagged template syntax library that provides JSX-like markup in plain JavaScript ... |
| 80 | htm-3-1-1 | htm | 3.1.1 | jsx-alternative, tagged-templates, preact, react, virtual-dom | A skill for using htm 3.1, a tagged template syntax library that provides JSX-like markup in plain JavaScript ... |
| 81 | htmx-2-0-0 | htmx | 2.0.0 | htmx, html, ajax, web-development, frontend | A skill for building interactive web applications with htmx 2.x, a JavaScript library that allows accessing modern ... |
| 82 | htmx-2-0-10 | htmx | 2.0.10 | htmx, html, ajax, web-development, frontend | A skill for building interactive web applications with htmx 2.0.10, a JavaScript library that allows accessing ... |
| 83 | htmx-4-0-0 | htmx | 4.0.0-beta2 | htmx, hypermedia, ajax, html-attributes, server-driven-ui | "A skill for building interactive web applications with htmx 4.0 (currently at 4.0.0-beta2), a JavaScript library ... |
| 84 | hy-1-2-0 | hy | 1.2.0 | hy, hylang, lisp, python-embedded, macros | Lisp dialect embedded in Python providing prefix S-expression syntax, compile-time macros, quasiquoting, reader ... |
| 85 | jina-ai-reader | jina-ai-reader | 0.1.0 | url-to-markdown, web-crawling, web-search, llm-context, context-engineering | Converts any URL to LLM-friendly markdown via r.jina.ai and searches the web with s.jina.ai, returning top results ... |
| 86 | jinja2-3-1-6 | jinja2 | 3.1.6 | templating, html, python, jinja, web | Complete toolkit for Jinja2 v3.1.6 templating engine covering template design, Python API integration, custom ... |
| 87 | jq-1-8-1 | jq | 1.8.1 | json, cli, data-processing, transformation, shell | Complete toolkit for jq 1.8.1, the lightweight and flexible command-line JSON processor. Use when parsing, ... |
| 88 | jsonpath-rfc-9535-1-0-0 | jsonpath-rfc | 1.0.0 | JSON, query-language, data-selection, extraction, IETF-standard | Complete reference for JSONPath RFC 9535, the IETF Standards Track specification defining a string syntax for ... |
| 89 | lingua-py-2-2-0 | lingua-py | 2.2.0 | nlp, language-detection, text-processing, multilingual, natural-language-processing | Accurate natural language detection library for Python supporting 75 languages with high accuracy on short text and ... |
| 90 | lisp-in-c-2026-05-03 | lisp-in-c | 2026-05-03 | lisp, c, interpreter, eval-apply, s-expression | "Build a Lisp interpreter in C from scratch, covering S-expression parsing, manual memory management, hash-table ... |
| 91 | lisp-in-python-2026-05-03 | lisp-in-python | 2026-05-03 | lisp, interpreter, python, eval-apply, homoiconicity | "Complete guide to building a minimal Lisp interpreter in Python, synthesized from six independent implementations ... |
| 92 | llama-cpp-1-0-0 | llama-cpp | 1.0.0 | llm, inference, gguf, quantization, cuda | C/C++ LLM inference library providing GGUF model support, quantization, GPU acceleration ... |
| 93 | lodash-4-18-1 | lodash | 4.18.1 | javascript, utility-library, data-manipulation, functional-programming, browser-compatibility | Complete toolkit for Lodash 4.18 utility library providing 300+ helper functions for arrays, collections, objects, ... |
| 94 | logfire-4-32-1 | logfire | 4.32.1 | observability, tracing, opentelemetry, logging, metrics | Production-grade AI observability platform built on OpenTelemetry by the Pydantic team. Native SDKs for Python, ... |
| 95 | lua-5-5-0 | lua | 5.5.0 | lua, scripting, embeddable, c-api, dynamic-language | Lightweight embeddable scripting language with a small C footprint, dynamic typing via tables, coroutines for ... |
| 96 | matplotlib-3-10-8 | matplotlib | 3.10.8 | plotting, visualization, charts, graphs, data-visualization | Comprehensive toolkit for Matplotlib 3.10.8, the Python plotting library for creating static, animated, and ... |
| 97 | matplotlib-3-10-9 | matplotlib | 3.10.9 | plotting, visualization, charts, graphs, data-visualization | Comprehensive toolkit for Matplotlib 3.10.9, the Python plotting library for creating static, animated, and ... |
| 98 | mcp-2025-11-25 | mcp | 2025-11-25 | mcp, model-context-protocol, llm, ai-integration, json-rpc | Model Context Protocol (MCP) version 2025-11-25 specification covering client-host-server architecture, JSON-RPC ... |
| 99 | mem0-1-0-11 | mem0 | 1.0.11 | memory, llm, ai-agents, vector-search, langchain | A skill for using Mem0 v1.0.11, a universal self-improving memory layer for LLM applications that enables persistent ... |
| 100 | mem0-2-0-1 | mem0 | 2.0.1 | memory, llm, ai-agents, vector-search, hybrid-search | A skill for using Mem0 v2.0.1, a self-improving memory layer for LLM agents that enables persistent context across ... |
| 101 | mempalace-3-3-0 | mempalace | 3.3.0 | ai-memory, local-rag, chromadb, knowledge-graph, mcp | Local AI memory system that mines projects and conversations into a searchable palace using ChromaDB for vector ... |
| 102 | mempalace-3-3-4 | mempalace | 3.3.4 | ai-memory, local-rag, chromadb, knowledge-graph, mcp | Local AI memory system that mines projects and conversations into a searchable palace using ChromaDB for vector ... |
| 103 | mermaid-11-14-0 | mermaid | 11.14.0 | diagramming, visualization, charts, flowcharts, sequence-diagrams | >- |
| 104 | nekovm-2-4-1 | nekovm | 2.4.1 | nekovm, neko, virtual-machine, scripting-language, haxe | Stack-based bytecode virtual machine and dynamically typed scripting language designed as a common runtime for ... |
| 105 | networkx-3-6-1 | networkx | 3.6.1 | graph-theory, network-analysis, complex-networks, centrality, community-detection | A comprehensive toolkit for NetworkX 3.6.1, the Python package for creating, manipulating, and studying complex ... |
| 106 | networkxternal-0-3-0 | networkxternal | 0.3.0 | graph, database, networkx, sqlite, postgresql | NetworkX-compatible interface for external memory MultiDiGraphs persisted in databases (SQLite, PostgreSQL, MySQL, ... |
| 107 | networkxternal-0-5 | networkxternal | 0.5 | graph, database, networkx, external-memory, sql | NetworkX-compatible interface for external memory MultiDiGraphs persisted in databases (SQLite, PostgreSQL, MySQL, ... |
| 108 | nextjs-16-2-3 | nextjs | 16.2.3 | react, nextjs, ssr, ssg, fullstack | A skill for building production-ready React applications with Next.js 16.2.3, providing App Router and Pages Router ... |
| 109 | nextjs-16-2-4 | nextjs | 16.2.4 | react, nextjs, ssr, ssg, fullstack | A skill for building production-ready React applications with Next.js 16.2.4, providing App Router and Pages Router ... |
| 110 | nginx-1-30-0 | nginx | 1.30.0 | HTTP server, reverse proxy, load balancer, SSL/TLS, caching | Complete toolkit for Nginx 1.30.0 high-performance HTTP server, reverse proxy, and load balancer covering ... |
| 111 | nltk-3-9-2 | nltk | 3.9.2 | nlp, natural-language-processing, python, text-processing, wordnet | Complete toolkit for Natural Language Processing with NLTK 3.9.2, covering tokenization, stemming, lemmatization, ... |
| 112 | nltk-3-9-4 | nltk | 3.9.4 | nlp, natural-language-processing, python, text-processing, wordnet | Complete toolkit for Natural Language Processing with NLTK 3.9.4, covering tokenization, stemming, lemmatization, ... |
| 113 | nodejs-24-14-0 | nodejs | 24.14.0 | nodejs, javascript, runtime, server-side, async | Complete Node.js 24.14 runtime toolkit covering core modules, async programming, HTTP servers, file system ... |
| 114 | nuitka-4-0-8 | nuitka | 4.0.8 | python, compiler, c-extension, standalone, onefile | Python compiler that translates Python code to C and native executables. Use when compiling Python applications for ... |
| 115 | numba-0-65-0 | numba | 0.65.0 | jit, compiler, llvm, numba, numpy | Just-in-time compiler for Python that translates numerical and array-oriented code into optimized machine code using ... |
| 116 | numba-0-65-1 | numba | 0.65.1 | jit, compiler, llvm, numba, numpy | Just-in-time compiler for Python that translates numerical and array-oriented code into optimized machine code using ... |
| 117 | numeral-2-0-6 | numeral | 2.0.6 | javascript, number-formatting, currency, localization | A JavaScript library for formatting and manipulating numbers. Use when formatting currency, percentages, bytes, time ... |
| 118 | numkong-7-6-0 | numkong | 7.6.0 | vector-similarity, simd, mixed-precision, dot-product, distance-metrics | Ultra-fast mixed-precision vector similarity and distance library with |
| 119 | numpy-2-4-4 | numpy | 2.4.4 | numpy, arrays, scientific-computing, linear-algebra, data-science | Complete toolkit for NumPy 2.4.4, the fundamental package for scientific computing with Python, providing powerful ... |
| 120 | oat-0-6-0 | oat | 0.6.0 | ui-library, css-framework, semantic-html, zero-dependency, webcomponents | Ultra-lightweight semantic UI component library with zero dependencies (~8KB). Use when building web applications ... |
| 121 | oat-0-6-1 | oat | 0.6.1 | ui-library, css-framework, semantic-html, zero-dependency, webcomponents | Ultra-lightweight semantic UI component library with zero dependencies (~8KB). Use when building web applications ... |
| 122 | obscura-0-1-0 | obscura | 0.1.0 | headless-browser, web-scraping, rust, cdp, puppeteer | Lightweight headless browser engine written in Rust for web scraping and AI agent automation. Runs real JavaScript ... |
| 123 | obscura-0-1-1 | obscura | 0.1.1 | headless-browser, web-scraping, rust, cdp, puppeteer | Lightweight headless browser engine written in Rust for web scraping and AI agent automation. Runs real JavaScript ... |
| 124 | openai-2-31-0 | openai | 2.31.0 | openai, llm, ai, chat-completions, responses-api | Python SDK for OpenAI API v2.31 providing type-safe access to Responses API, Chat Completions, embeddings, audio ... |
| 125 | openai-2-33-0 | openai | 2.33.0 | openai, llm, ai, chat-completions, responses-api | Python SDK for OpenAI API v2.33 providing type-safe access to Responses API, Chat Completions, embeddings, audio ... |
| 126 | opentelemetry-1-55-0 | opentelemetry | 1.55.0 | distributed-tracing, metrics, logging, observability, OTLP | Complete OpenTelemetry 1.55.0 specification toolkit for implementing distributed tracing, metrics collection, and ... |
| 127 | opentelemetry-1-56-0 | opentelemetry | 1.56.0 | distributed-tracing, metrics, logging, observability, OTLP | Complete OpenTelemetry 1.56.0 specification toolkit for implementing distributed tracing, metrics collection, and ... |
| 128 | opentelemetry-collector-1-56-0 | opentelemetry-collector | 1.56.0 | opentelemetry, collector, observability, telemetry, tracing | >- |
| 129 | opentelemetry-python-1-41-0 | opentelemetry-python | 1.41.0 | opentelemetry, observability, tracing, metrics, logging | Complete OpenTelemetry Python v1.41.0 toolkit for distributed tracing, metrics collection, and log management with ... |
| 130 | opentelemetry-python-1-41-1 | opentelemetry-python | 1.41.1 | opentelemetry, observability, tracing, metrics, logging | Complete OpenTelemetry Python v1.41.1 toolkit for distributed tracing, metrics collection, and log management with ... |
| 131 | ot-2026-05-03 | ot | 2026-05-03 | operational-transformation, ot, collaborative-editing, concurrency-control, real-time-collaboration | Operational Transformation (OT) theory and practice for consistency maintenance in real-time collaborative editing ... |
| 132 | pacote-21-5-0 | pacote | 21.5.0 | npm, packages, npx, download, extract | Use pacote 21.5 via npx to inspect, download, and extract npm packages without installing them first. Supports ... |
| 133 | paramiko-4-0-0 | paramiko | 4.0.0 | ssh, sshv2, sftp, remote-execution, file-transfer | >- |
| 134 | payloadcms-3-82-1 | payloadcms | 3.82.1 | cms, headless-cms, content-management, nextjs, typescript | Complete toolkit for Payload CMS v3.82.1 headless CMS development including collections, fields, access control, ... |
| 135 | payloadcms-3-84-1 | payloadcms | 3.84.1 | cms, headless-cms, content-management, nextjs, typescript | Complete toolkit for Payload CMS v3.84.1 headless CMS development including collections, fields, access control, ... |
| 136 | payloadcms-blank-3-82-1 | payloadcms-blank | 3.82.1 | cms, payload, nextjs, mongodb, headless-cms | Minimal Payload CMS 3.82.1 starter template providing a clean foundation for building custom headless CMS ... |
| 137 | payloadcms-blank-3-84-1 | payloadcms-blank | 3.84.1 | cms, payload, nextjs, mongodb, headless-cms | Minimal Payload CMS 3.84.1 starter template providing a clean foundation for building custom headless CMS ... |
| 138 | payloadcms-ecommerce-3-82-1 | payloadcms-ecommerce | 3.82.1 | payloadcms, ecommerce, commerce, stripe, payments | Complete guide for Payload CMS ecommerce template v3.82.1 providing production-ready online store with products, ... |
| 139 | payloadcms-ecommerce-3-84-1 | payloadcms-ecommerce | 3.84.1 | payloadcms, ecommerce, commerce, stripe, payments | Complete guide for Payload CMS ecommerce template v3.84.1 providing production-ready online store with products, ... |
| 140 | payloadcms-website-3-82-1 | payloadcms-website | 3.82.1 | cms, headless-cms, website-template, nextjs, typescript | Complete guide for Payload CMS website template v3.82.1 providing production-ready starter for content-driven ... |
| 141 | payloadcms-website-3-84-1 | payloadcms-website | 3.84.1 | cms, headless-cms, website-template, nextjs, typescript | Complete guide for Payload CMS website template v3.84.1 providing production-ready starter for content-driven ... |
| 142 | peg-2026-05-03 | peg | 2026-05-03 | peg, parsing, parser-generator, formal-grammar, compiler-construction | Parsing Expression Grammars (PEGs) — recognition-based formal grammars using ordered choice to eliminate ambiguity, ... |
| 143 | picocss-2-1-1 | picocss | 2.1.1 | css-framework, semantic-html, responsive-design, light-dark-mode, minimal-css | A skill for using Pico CSS v2.1, a minimalist CSS framework that styles semantic HTML elements elegantly by default ... |
| 144 | pi-mono-0-66-1 | pi-mono | 0.66.1 | ai-coding-agent, terminal-harness, extensions, tui, session-management | Complete implementation guide for pi-mono monorepo architecture covering provider abstraction, agent runtime, ... |
| 145 | pi-mono-0-71-0 | pi-mono | 0.71.0 | ai-coding-agent, terminal-harness, extensions, tui, session-management | Complete implementation guide for pi-mono monorepo architecture covering provider abstraction, agent runtime, ... |
| 146 | pinecone-router-7-5-0 | pinecone-router | 7.5.0 | alpinejs, router, spa, client-side-routing, single-page-application | A comprehensive toolkit for building client-side routing in Alpine.js applications using Pinecone Router v7.5, ... |
| 147 | pipe | pipe | 0.1.3 | pipe, meta, meta-skill, chaining, workflow | Unix-style pipe expression syntax for chaining multiple agent operations sequentially. Each stage's output becomes ... |
| 148 | plan | plan | 0.1.5 | meta, meta-skill, workflow, task-management | Phase/task based workflow system with PLAN.md as single source of truth. Use when tackling projects that require ... |
| 149 | podman-5-8-1 | podman | 5.8.1 | containers, daemonless, rootless, oci, pods | Comprehensive toolkit for Podman 5.8.1, a daemonless container engine providing Docker-compatible CLI for managing ... |
| 150 | podman-5-8-2 | podman | 5.8.2 | containers, daemonless, rootless, oci, pods | Comprehensive toolkit for Podman 5.8.2, a daemonless container engine providing Docker-compatible CLI for managing ... |
| 151 | podman-compose-1-5-0 | podman-compose | 1.5.0 | podman, compose, containers, orchestration, devops | Orchestrates multi-container applications using Compose specification files with Podman backend. Use when deploying ... |
| 152 | podman-py-5-8-0 | podman-py | 5.8.0 | podman, containers, python, docker-alternative, container-management | Python client library for Podman container engine providing programmatic access to containers, images, pods, ... |
| 153 | prescheme-2026-05-03 | prescheme | 2026-05-03 | prescheme, scheme, lisp, static-typing, systems-programming | Statically typed Scheme dialect that compiles to C via Hindley/Milner type inference and CPS transformations. ... |
| 154 | pulp-3-3-0 | pulp | 3.3.0 | optimization, linear-programming, mixed-integer-programming, lp, mip | Complete toolkit for PuLP 3.3.0, a Python linear and mixed-integer programming (MIP) modeler that generates ... |
| 155 | pycrdt-0-12-50 | pycrdt | 0.12.50 | pycrdt, crdt, yjs, yrs, collaborative-editing | Python bindings for Yrs, the Rust port of the Yjs CRDT framework. Provides shared data types (Text, Array, Map, XML) ... |
| 156 | python-louvain-0-16 | python-louvain | 0.16 | community-detection, louvain, graph-algorithms, networkx, modularity | Python implementation of the Louvain algorithm for community detection in graphs. Produces modularity-optimized ... |
| 157 | python-scrypt-0-9-4 | python-scrypt | 0.9.4 | scrypt, password-hashing, key-derivation, cryptography, pbkdf | Python toolkit for scrypt-based key derivation and password hashing. Use when implementing secure password storage, ... |
| 158 | pywebview-6-2-0 | pywebview | 6.2.0 | python, gui, webview, desktop, cross-platform | Cross-platform wrapper around native webview components that lets Python applications display HTML content in a ... |
| 159 | pywebview-6-2-1 | pywebview | 6.2.1 | python, gui, webview, desktop, cross-platform | Cross-platform wrapper around native webview components that lets Python applications display HTML content in a ... |
| 160 | pyzmq-27-1-0 | pyzmq | 27.1.0 | zeromq, zmq, messaging, networking, sockets | Complete toolkit for Python bindings to ZeroMQ (pyzmq 27.x) covering socket types, messaging patterns, async/await ... |
| 161 | quickjs-2025-09-13 | quickjs | 2025-09-13 | javascript, engine, es2023, c-api, embedding | Small and fast JavaScript engine supporting ES2023 with C API for embedding, qjs REPL interpreter, and qjsc bytecode ... |
| 162 | qwen3-embedding-1-0-0 | qwen3-embedding | 1.0.0 | embedding, semantic-search, retrieval, multilingual, reranking | Complete toolkit for Qwen3 Embedding models (0.6B, 4B, 8B) and Qwen3 |
| 163 | qwen3-reranker-1-0-0 | qwen3-reranker | 1.0.0 | reranking, text-ranking, retrieval, cross-encoder, multilingual | Comprehensive toolkit for Qwen3 Reranker models (0.6B, 4B, 8B) — state-of-the-art cross-encoder text reranking with ... |
| 164 | qwen3-vl-embedding-0-1-0 | qwen3-vl-embedding | 0.1.0 | embedding, multimodal, vision-language, retrieval, semantic-search | Complete toolkit for Qwen3-VL-Embedding 0.1.0 multimodal embedding models (2B and 8B) supporting text, images, ... |
| 165 | qwen3-vl-reranker-1-0-0 | qwen3-vl-reranker | 1.0.0 | reranker, multimodal, retrieval, qwen, cross-encoder | Complete toolkit for Qwen3-VL-Reranker (2B and 8B) multimodal reranking models that score relevance of text, image, ... |
| 166 | raft-2026-05-03 | raft | 2026-05-03 | raft, consensus, distributed-systems, replicated-log, leader-election | Raft consensus algorithm for managing replicated logs across a cluster of servers. Provides leader election, log ... |
| 167 | ralph-orchestrator-2-9-2 | ralph-orchestrator | 2.9.2 | ai-orchestration, ralph-wiggum, autonomous-agents, hat-system, event-driven | Hat-based orchestration framework that keeps AI agents in a loop until the task is done. Supports Claude Code, Kiro, ... |
| 168 | redis-om-python-1-1-0 | redis-om-python | 1.1.0 | redis, orm, object-mapping, pydantic, redi-search | A skill for using Redis OM Python v1.1, an object mapping library that |
| 169 | redis-py-7-4-0 | redis-py | 7.4.0 | redis, database, key-value-store, caching, async | Comprehensive Python client for Redis database and key-value store. Use when building Python applications requiring ... |
| 170 | rich-15-0-0 | rich | 15.0.0 | terminal, cli, formatting, color, tables | Python library for rich text and beautiful formatting in the terminal. Provides color, tables, progress bars, ... |
| 171 | rqlite-10-0-1 | rqlite | 10.0.1 | database, distributed-systems, sqlite, raft, high-availability | Comprehensive toolkit for rqlite 10.0.1, a lightweight distributed relational database built on SQLite with Raft ... |
| 172 | rqlite-9-4-0 | rqlite | 9.4.0 | database, distributed-systems, sqlite, raft, high-availability | Comprehensive toolkit for rqlite 9.4, a lightweight distributed relational database built on SQLite with Raft ... |
| 173 | rsync-3-4-1 | rsync | 3.4.1 | file-transfer, backup, mirroring, sync, daemon | Complete toolkit for rsync 3.4.1, the fast and versatile file-copying tool using delta-transfer algorithm. Use when ... |
| 174 | rsync-3-4-2 | rsync | 3.4.2 | file-transfer, backup, mirroring, sync, daemon | Complete toolkit for rsync 3.4.2, the fast and versatile file-copying tool using delta-transfer algorithm. Use when ... |
| 175 | ruff-0-15-12 | ruff | 0.15.12 | python, linter, formatter, code-quality, flake8 | An extremely fast Python linter and code formatter written in Rust that replaces Flake8 (plus dozens of plugins), ... |
| 176 | ruff-0-4-10 | ruff | 0.4.10 | python, linter, formatter, code-quality, flake8 | A skill for using Ruff 0.4.10, an extremely fast Python linter and code formatter written in Rust that replaces ... |
| 177 | rustfs-1-0-0-alpha-93 | rustfs | 1.0.0-alpha.93 | object-storage, s3, swift, distributed-systems, observability | High-performance distributed object storage system with S3-compatible API, OpenStack Swift support, and ... |
| 178 | rustfs-1-0-0-beta-1 | rustfs | 1.0.0-beta.1 | object-storage, s3, swift, distributed-systems, observability | High-performance distributed object storage system with S3-compatible API, OpenStack Swift support, and ... |
| 179 | scheme-in-python-2026-05-03 | scheme-in-python | 2026-05-03 | scheme, interpreter, lisp, python, eval-apply | Build a Scheme interpreter in Python covering tokenization, eval/apply loop, environment frames with lexical and ... |
| 180 | scikit-learn-1-8-0 | scikit-learn | 1.8.0 | machine-learning, classification, regression, clustering, pipelines | Complete scikit-learn 1.8 toolkit for machine learning covering supervised and unsupervised algorithms, pipelines, ... |
| 181 | scipy-1-17-1 | scipy | 1.17.1 | scipy, scientific-computing, optimization, integration, statistics | Complete SciPy 1.17 toolkit for scientific computing covering optimization, integration, interpolation, eigenvalue ... |
| 182 | scrapling-0-4-7 | scrapling | 0.1.2 | web-search, web scrape, web scraping, browser automation | Web scraping tool that converts web pages to Markdown using Scrapling v0.4.7's CLI. Use when extracting content from ... |
| 183 | semver-2-0-0 | semver | 2.0.0 | versioning, semver, semantic-versioning, releases, dependency-management | Implement and validate Semantic Versioning 2.0.0 to manage software version numbers, determine compatibility, ... |
| 184 | sentence-transformers-5-4-1 | sentence-transformers | 5.4.1 | embeddings, semantic-search, reranking, nlp, sentence-embeddings | Comprehensive toolkit for computing text embeddings, semantic search, and reranking using Sentence Transformers ... |
| 185 | skman | skman | 0.2.0 | meta, meta skill, skill manager, skill package manager, authoring | Skill Package Manager, skman, it is meta skill for skill authoring and skill package manager for AI agents. |
| 186 | solidjs-1-9-12 | solidjs | 1.9.12 | solidjs, reactivity, signals, jsx, fine-grained | >- |
| 187 | solid-meta-0-29-0 | solid-meta | 0.29.0 | solidjs, meta-tags, document-head, ssr, seo | Manages document head tags in SolidJS applications with @solidjs/meta v0.29, providing asynchronous SSR-ready ... |
| 188 | solid-meta-0-29-4 | solid-meta | 0.29.4 | solidjs, meta-tags, document-head, ssr, seo | Manages document head tags in SolidJS applications with @solidjs/meta v0.29.4, providing asynchronous SSR-ready ... |
| 189 | solid-router-0-16-0 | solid-router | 0.16.0 | solidjs, router, spa, routing, ssg | The universal router for SolidJS providing fine-grained reactivity for route navigation with support for ... |
| 190 | solid-router-0-16-1 | solid-router | 0.16.1 | solidjs, router, spa, routing, ssg | The universal router for SolidJS providing fine-grained reactivity for route navigation with support for ... |
| 191 | solid-start-1-3-0 | solid-start | 1.3.0 | solidjs, fullstack, ssr, ssg, csr | Fullstack framework for SolidJS providing SSR, SSG, API routes, file-based routing, and server functions. Use when ... |
| 192 | solid-start-1-3-2 | solid-start | 1.3.2 | solidjs, fullstack, ssr, ssg, csr | Fullstack framework for SolidJS providing SSR, SSG, API routes, file-based routing, and server functions. Use when ... |
| 193 | spacy-3-8-14 | spacy | 3.8.14 | nlp, natural-language-processing, text-analysis, machine-learning, python | Industrial-strength NLP library for Python providing tokenization, named entity recognition, dependency parsing, ... |
| 194 | spec-kit-0-6-1 | spec-kit | 0.6.1 | specification-driven-development, sdd, ai-assisted-development, project-management, workflow-automation | A skill for implementing Spec-Driven Development (SDD) using GitHub's Spec Kit v0.6.1 toolkit, enabling ... |
| 195 | spec-kit-0-8-3 | spec-kit | 0.8.3 | specification-driven-development, sdd, ai-assisted-development, project-management, workflow-automation | A skill for implementing Spec-Driven Development (SDD) using GitHub's Spec Kit v0.8.3 toolkit, enabling ... |
| 196 | sqlalchemy-2-0-49 | sqlalchemy | 2.0.49 | database, orm, sql, python, postgresql | Complete SQLAlchemy 2.0 toolkit for database operations, ORM mapping, and SQL expression construction. Use when ... |
| 197 | sqlite-3-53-0 | sqlite | 3.53.0 | sqlite, database, sql, json, fts | Complete toolkit for SQLite 3.53 covering all official documentation topics including SQL queries, C API ... |
| 198 | stanza-1-11-1 | stanza | 1.11.1 | nlp, natural-language-processing, multilingual, tokenization, pos-tagging | Stanford NLP Group's official Python NLP library for 80+ languages providing tokenization, POS tagging, ... |
| 199 | stitch-2026-05-04 | stitch | 2026-05-04 | stitch, ui-design, ai-design, mcp, google-labs | AI-powered UI design tool from Google Labs generating high-fidelity screens and frontend code from text prompts and ... |
| 200 | stringzilla-4-6-0 | stringzilla | 4.6.0 | simd, string-processing, search, hashing, sorting | High-performance SIMD-accelerated string library for search, hashing, sorting, and fuzzy matching in ... |
| 201 | tailwindcss-4-2-4 | tailwindcss | 4.2.4 | css, tailwind, styling, frontend, utility-first | A skill for using Tailwind CSS v4.2, a utility-first CSS framework with CSS-based configuration via @theme, OKLCH ... |
| 202 | tailwindcss-browser-4-2-0 | tailwindcss-browser | 4.2.0 | css, tailwind, browser, prototyping, no-build | A skill for using Tailwind CSS v4.2 browser build (@tailwindcss/browser) that enables in-browser Tailwind ... |
| 203 | tailwindcss-browser-4-2-4 | tailwindcss-browser | 4.2.4 | css, tailwind, browser, prototyping, no-build | A skill for using Tailwind CSS v4.2 browser build (@tailwindcss/browser) that enables in-browser Tailwind ... |
| 204 | tea-0-14-0 | tea | 0.14.0 | gitea, cli, git, devops, ci-cd | Official CLI for Gitea servers. Manage issues, pull requests, releases, milestones, organizations, repositories, ... |
| 205 | textblob-0-20-0 | textblob | 0.20.0 | nlp, text-processing, sentiment-analysis, pos-tagging, tokenization | Python library for simplified natural language processing providing part-of-speech tagging, noun phrase extraction, ... |
| 206 | textual-8-2-4 | textual | 8.2.4 | tui, terminal-ui, python, framework, reactive | Rapid application development framework for building sophisticated terminal and browser user interfaces in Python. ... |
| 207 | textual-8-2-5 | textual | 8.2.5 | tui, terminal-ui, python, framework, reactive | Rapid application development framework for building sophisticated terminal and browser user interfaces in Python. ... |
| 208 | tinycc-0-9-27 | tinycc | 0.9.27 | c-compiler, code-generation, dynamic-compilation, x86, arm | Complete toolkit for TinyCC 0.9.27, a small hyper-fast C compiler that generates native x86/x86_64/ARM code directly ... |
| 209 | tinypy-1-1-0 | tinypy | 1.1.0 | python, vm, embedding, scripting, minimal | A minimalist Python implementation in ~64k of code featuring a fully bootstrapped parser and bytecode compiler ... |
| 210 | tinyscheme-1-41 | tinyscheme | 1.41 | tinyscheme, scheme, lisp, interpreter, embedded | Lightweight Scheme interpreter (R5RS subset) in ~5000 lines of C, designed as an embeddable scripting engine. ... |
| 211 | tokenizers-0-22-3 | tokenizers | 0.22.3 | nlp, tokenization, rust, python, transformers | Fast state-of-the-art tokenizers library for NLP written in Rust with |
| 212 | tokenizers-0-23-1 | tokenizers | 0.23.1 | nlp, tokenization, rust, python, transformers | Fast state-of-the-art tokenizers library for NLP written in Rust with Python, Node.js, and Ruby bindings. Use when ... |
| 213 | transformers-5-5-4 | transformers | 5.5.4 | nlp, machine-learning, deep-learning, pytorch, huggingface | Complete toolkit for Hugging Face Transformers 5.5.4 providing state-of-the-art pretrained models for NLP, computer ... |
| 214 | transformers-5-7-0 | transformers | 5.7.0 | nlp, machine-learning, deep-learning, pytorch, huggingface | Complete toolkit for Hugging Face Transformers 5.7.0 providing state-of-the-art pretrained models for NLP, computer ... |
| 215 | ty-0-0-29 | ty | 0.0.29 | python, type-checking, static-analysis, language-server, mypy-alternative | A skill for using ty 0.0.29, an extremely fast Python type checker and language server written in Rust that is ... |
| 216 | ty-0-0-33 | ty | 0.0.33 | python, type-checking, static-analysis, language-server, mypy-alternative | A skill for using ty 0.0.33, an extremely fast Python type checker and language server written in Rust that is ... |
| 217 | tzip | tzip | 0.4.0 | meta, meta-skill, token-prune, efficiency, guidelines | Lightweight token-pruning communication mode that drops filler and hedging while keeping full sentences and ... |
| 218 | upx-5-1-1 | upx | 5.1.1 | compression, executable-packer, distribution, size-optimization, cross-platform | >- |
| 219 | usearch-2-24-0 | usearch | 2.24.0 | vector-search, hnsw, similarity-search, approximate-nearest-neighbors, embedding-search | High-performance single-file similarity search and clustering engine for vectors supporting HNSW algorithm with ... |
| 220 | usearch-2-25-1 | usearch | 2.25.1 | vector-search, ann, hnsw, similarity-search, clustering | High-performance single-file similarity search and clustering engine for vectors using HNSW algorithm with ... |
| 221 | uv-0-11-6 | uv | 0.11.6 | python, package-management, dependency-resolution, virtual-environments, pip-replacement | A skill for using uv 0.11.6, an extremely fast Python package and project manager written in Rust that replaces pip, ... |
| 222 | uv-0-11-8 | uv | 0.11.8 | python, package-management, dependency-resolution, virtual-environments, pip-replacement | A skill for using uv 0.11.8, an extremely fast Python package and project manager written in Rust that replaces pip, ... |
| 223 | webfetch | webfetch | 0.1.0 | meta, meta-skill, webfetch, scraping, markdown | Fetches web pages and converts them to clean Markdown. Delegates to the local scrapling-0-4-7 skill for all URL ... |
| 224 | websearch | websearch | 0.1.0 | meta, meta-skill, websearch, search, meta-skill | Meta skill that delegates web search tasks to the local duckduckgo-2026-05-08 skill. Use when performing web ... |
| 225 | yjs-13-6-30 | yjs | 13.6.30 | yjs, crdt, collaborative-editing, real-time, shared-types | CRDT framework that exposes shared types (Y.Map, Y.Array, Y.Text, Y.XmlFragment) for conflict-free collaborative ... |
| 226 | yq-4-53-2 | yq | 4.53.2 | yaml, json, xml, ini, csv | >- |
| 227 | zeromq-wiki-3-2-0 | zeromq-wiki | 3.2.0 | zeromq, messaging, distributed-systems, networking, sockets | A comprehensive toolkit for ZeroMQ (ØMQ) messaging library covering socket patterns, protocols, architecture, and ... |
| 228 | zeromq-zguide-3-2-0 | zeromq-zguide | 3.2.0 | zeromq, zmq, messaging, sockets, distributed-systems | Complete ZeroMQ ZGuide 3.2 toolkit covering messaging patterns, socket types, reliability mechanisms, and ... |


## Statistics

- **Total Skills**: 228
