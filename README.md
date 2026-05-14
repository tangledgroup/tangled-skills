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

## Skills Table

| No | Skill | Project | Version | Technologies | Description |
|----|-------|---------|---------|--------------|-------------|
| 1 | a2a-1-0-0 | a2a | 0.1.0 | agent-communication, multi-agent, interoperability, protocol, json-rpc | Open standard for communication between independent AI agent systems. Agents discover capabilities via Agent Cards ... |
| 2 | acp-0-12-2 | acp | 0.1.0 | agent-protocol, json-rpc, coding-agents, editor-integration, ai-agents | Protocol standardizing communication between code editors and AI coding agents using JSON-RPC 2.0 over stdio. ... |
| 3 | agent-coding-mini-rasbt-0-1-0 | agent-coding-mini-rasbt | 0.1.0 | coding-agent, ollama, local-ai, autonomous-agent, python | Minimal standalone coding agent framework by Sebastian Raschka backed by Ollama, providing workspace context ... |
| 4 | agent-coding-wyattdave-0-1-0 | agent-coding-wyattdave | 0.1.0 | ai-agents, prompt-engineering, vscode-extensions, coding-assistants, customization | A toolkit for creating custom AI coding agents using prompt engineering, instruction files, and skill modules. Use ... |
| 5 | agentmemory-0-8-10 | agentmemory | 0.1.0 | ai-agent, persistent-memory, mcp-server, hybrid-search, knowledge-graph | Persistent memory engine for AI coding agents with cross-session context capture, hybrid search (BM25 + vector + ... |
| 6 | agentmemory-0-8-9 | agentmemory | 0.1.0 | ai-agents, memory, mcp-server, persistent-context, vector-search | Persistent memory engine for AI coding agents providing automatic cross-session context capture, hybrid search (BM25 ... |
| 7 | agentmemory-0-9-4 | agentmemory | 0.1.0 | ai-agent, persistent-memory, mcp-server, hybrid-search, knowledge-graph | Persistent memory engine for AI coding agents with cross-session context capture, hybrid search (BM25 + vector + ... |
| 8 | agent-nirzabari-0-1-0 | agent-nirzabari | 0.1.0 | ai-agents, coding-agents, harness-engineering, llm-systems, agent-architecture | Comprehensive guide to understanding and building coding agent harnesses, covering 7-layer architecture, context ... |
| 9 | agent-ralph-loop-claude | agent-ralph-loop-claude | 0.1.0 | claude-code, plugin, iterative-development, autonomous-agents, ralph-wiggum | Implements the Ralph Wiggum technique as a Claude Code plugin for iterative, self-referential AI development loops. ... |
| 10 | agent-ralph-loop-vercel-labs | agent-ralph-loop-vercel-labs | 0.1.0 | autonomous-agent, ai-sdk, iterative-loop, coding-agent, continuous-autonomy | Continuous autonomy framework for the Vercel AI SDK implementing the Ralph Wiggum technique — an iterative outer ... |
| 11 | agent-ralph-wiggum-fstandhartinger-0-3-0 | agent-ralph-wiggum-fstandhartinger | 0.1.0 | autonomous-development, spec-driven, iterative-loops, ai-coding, ralph-wiggum | Autonomous AI coding with spec-driven development combining iterative bash loops and SpecKit-style specifications ... |
| 12 | agent-ralph-wiggum-ghuntley | agent-ralph-wiggum-ghuntley | 0.1.0 | ralph-wiggum, autonomous-development, iterative-loops, greenfield, prompt-tuning | Geoffrey Huntley's Ralph Wiggum technique — a monolithic iterative loop pattern for autonomous AI-driven software ... |
| 13 | agent-ralph-wiggum-loop-beuke | agent-ralph-wiggum-loop-beuke | 0.1.0 | ralph-wiggum, agentic-loops, autonomous-agents, ai-safety, feedback-systems | Principles and conceptual framework of the Ralph Wiggum Loop pattern for goal-oriented autonomous AI agent loops. ... |
| 14 | agent-ralph-wiggum-snarktank | agent-ralph-wiggum-snarktank | 0.1.0 | ralph-wiggum, autonomous-agent, coding-loop, prd-driven, claude-code | Autonomous AI coding loop that runs AI coding tools (Amp or Claude Code) repeatedly until all PRD items are ... |
| 15 | agent-wiggum-cli-federiconeri | agent-wiggum-cli-federiconeri | 0.1.0 | autonomous-coding, ralph-loop, spec-driven-development, ai-agent, claude-code | Autonomous coding agent that scans codebases, generates feature specs via AI interviews, and runs Ralph loops via ... |
| 16 | aiohttp-3-13-0 | aiohttp | 0.1.0 | http, async, client, server, websocket | Async HTTP client/server for Python asyncio. Use when building async web applications, REST APIs, or making ... |
| 17 | aiohttp-3-13-5 | aiohttp | 0.1.0 | http, async, client, server, websocket | Async HTTP client/server for Python asyncio. Use when building async web applications, REST APIs, or making ... |
| 18 | aiohttp-cors-0-8-1 | aiohttp-cors | 0.1.0 | cors, aiohttp, web-security, http-headers, cross-origin | Implement Cross-Origin Resource Sharing (CORS) in aiohttp applications using aiohttp-cors 0.8.1, enabling secure ... |
| 19 | aiohttp-jinja2-1-6-0 | aiohttp-jinja2 | 0.1.0 | aiohttp, jinja2, templating, web-framework, async | Jinja2 template renderer for aiohttp.web applications providing decorator-based rendering, context processors, URL ... |
| 20 | aiohttp-security-0-5-0 | aiohttp-security | 0.1.0 | aiohttp, authentication, authorization, identity-policy, permission | Authentication and authorization toolkit for aiohttp.web applications providing identity policies (cookies, ... |
| 21 | aiohttp-session-2-12-0 | aiohttp-session | 0.1.0 | aiohttp, sessions, web, async, storage | Server-side sessions for aiohttp.web applications using aiohttp-session 2.12, providing multiple storage backends ... |
| 22 | aiohttp-session-2-12-1 | aiohttp-session | 0.1.0 | aiohttp, sessions, web, async, storage | Server-side sessions for aiohttp.web applications using aiohttp-session 2.12, providing multiple storage backends ... |
| 23 | aiohttp-sse-2-2-0 | aiohttp-sse | 0.1.0 | aiohttp, server-sent-events, sse, eventsource, streaming | Python library for Server-Sent Events (SSE) support in aiohttp applications. Use when building real-time streaming ... |
| 24 | aioitertools-0-13-0 | aioitertools | 0.1.0 | asyncio, python, itertools, async-iterators, generators | Async-compatible versions of itertools, builtins, and more for Python asyncio. Use when building async Python ... |
| 25 | aiorwlock-1-5-1 | aiorwlock | 0.1.0 | asyncio, concurrency, synchronization, read-write-lock | Async read-write lock for Python asyncio providing concurrent reader access and exclusive writer access. Use when ... |
| 26 | aiozmq-0-7-0 | aiozmq | 0.1.0 | zeromq, asyncio, rpc, messaging, distributed | Async ZeroMQ integration for Python asyncio providing transport-level APIs, stream abstraction, and RPC frameworks ... |
| 27 | aiozmq-1-0-0 | aiozmq | 0.1.0 | zeromq, asyncio, rpc, messaging, distributed | Async ZeroMQ integration for Python asyncio providing transport-level APIs, stream abstraction, and RPC frameworks ... |
| 28 | alpinejs-3-15-11 | alpinejs | 0.1.0 | javascript, frontend, reactive, html, directives | A skill for building reactive user interfaces with Alpine.js 3.15, a minimal JavaScript framework that uses ... |
| 29 | alpinejs-3-15-12 | alpinejs | 0.1.0 | javascript, frontend, reactive, html, directives | A skill for building reactive user interfaces with Alpine.js 3.15, a minimal JavaScript framework that uses ... |
| 30 | argon2-25-1-0 | argon2 | 0.1.0 | password-hashing, authentication, cryptography, argon2, security | Python toolkit for password hashing and verification using the Argon2 algorithm via argon2-cffi 25.x. Use when ... |
| 31 | asyncstdlib-3-14-0 | asyncstdlib | 0.1.0 | python, async, itertools, builtins, functools | Python async standard library providing async versions of builtins, itertools, functools, contextlib, and heapq for ... |
| 32 | authelia-4-39-19 | authelia | 0.1.0 | authelia, authentication, mfa, sso, openid-connect | Open-source authentication and authorization server providing multi-factor authentication (MFA), single sign-on ... |
| 33 | authentik-2026-5-0 | authentik | 0.1.0 | authentik, identity-provider, sso, oauth2, oidc | Open-source Identity Provider (IdP) for modern SSO supporting OAuth2/OIDC, SAML, LDAP, RADIUS, SCIM, and Proxy ... |
| 34 | autoloop-0-4-0 | autoloop | 0.1.0 | autonomous-agents, multi-role-loops, event-routing, preset-workflows, agent-harness | Opinionated loop harness for long-running agent workflows. Supports preset-driven multi-role loops with event-based ... |
| 35 | automerge-3-2-6 | automerge | 0.1.0 | automerge, crdt, local-first, collaborative-editing, offline-sync | CRDT library for building collaborative, local-first applications with automatic conflict-free merging. Provides ... |
| 36 | axios-1-15-0 | axios | 0.1.0 | http, rest, api, fetch, ajax | A comprehensive toolkit for making HTTP requests using Axios 1.x, a promise-based HTTP client for browser and ... |
| 37 | axios-1-15-2 | axios | 0.1.0 | http, rest, api, fetch, ajax | A comprehensive toolkit for making HTTP requests using Axios 1.x, a promise-based HTTP client for browser and ... |
| 38 | bcrypt-5-0-0 | bcrypt | 0.1.0 | password-hashing, cryptography, security, authentication, key-derivation | A skill for password hashing and key derivation using bcrypt 5.0 in Python. Use when implementing secure password ... |
| 39 | boto3-1-42-89 | boto3 | 0.1.0 | aws, boto3, cloud, python, sdk | Complete toolkit for AWS SDK for Python (Boto3) 1.42.89 providing high-level resource interface and low-level client ... |
| 40 | boto3-1-43-1 | boto3 | 0.1.0 | aws, boto3, cloud, python, sdk | Complete toolkit for AWS SDK for Python (Boto3) 1.43.1 providing high-level resource interface and low-level client ... |
| 41 | bun-1-3-12 | bun | 0.1.0 | javascript, typescript, runtime, package-manager, bundler | Complete toolkit for Bun 1.3.12 JavaScript runtime, package manager, bundler, and test runner. Use when building ... |
| 42 | bun-1-3-13 | bun | 0.1.0 | javascript, typescript, runtime, package-manager, bundler | Complete toolkit for Bun 1.3.13 JavaScript runtime, package manager, bundler, and test runner. Use when building ... |
| 43 | caddy-2-11-2 | caddy | 0.1.0 | web server, reverse proxy, HTTPS, Caddyfile, automatic SSL | Complete Caddy 2.11.2 web server toolkit covering Caddyfile configuration, JSON API, automatic HTTPS with Let's ... |
| 44 | category-theory | category-theory | 0.2.0 | category-theory, functional-programming, type-theory, monads, functors | Mathematical framework for abstract structures and their relationships via categories, functors, natural ... |
| 45 | caveman-1-5-1 | caveman | 0.1.0 | communication, token-optimization, brevity, efficiency | Ultra-compressed communication mode that cuts token usage by ~75% while maintaining full technical accuracy. ... |
| 46 | cffi-2-0-0 | cffi | 0.1.0 | cffi, c-integration, ffi, foreign-function-interface, python-c-bindings | Python C Foreign Function Interface for calling C libraries from Python |
| 47 | changelog-1-1-0 | changelog | 0.1.0 | changelog, documentation, versioning, semver, release-notes | Create and maintain changelogs following the Keep a Changelog specification v1.1.0, providing standardized format ... |
| 48 | chart-js-4-5-1 | chart-js | 0.1.0 | charts, canvas, data-visualization, javascript, html5 | Complete toolkit for Chart.js 4.5.1, the popular JavaScript charting library using HTML5 Canvas rendering. Use when ... |
| 49 | chibi-scheme-0-12 | chibi-scheme | 0.1.0 | chibi-scheme, scheme, lisp, embedded-vm, c-ffi | Minimal Scheme implementation for embedding in C applications. Provides tagged-pointer VM with precise non-moving ... |
| 50 | chonkie-1-6-2 | chonkie | 0.1.0 | text-chunking, rag, nlp, embeddings, vector-databases | Lightweight Rust-based text chunking library for RAG pipelines providing 10+ chunking strategies, pipeline ... |
| 51 | chonkie-1-6-4 | chonkie | 0.1.0 | text-chunking, rag, nlp, embeddings, vector-databases | Lightweight text chunking library for RAG pipelines providing 12+ chunkers, pipeline API, refineries, vector DB ... |
| 52 | coding-guidelines-0-1-0 | coding-guidelines | 0.1.0 | behavioral-guidelines, code-quality, simplicity, llm-best-practices | Behavioral guidelines to reduce common LLM coding mistakes including |
| 53 | crdt-2026-05-03 | crdt | 0.1.0 | crdt, distributed-systems, conflict-resolution, collaborative-editing, eventual-consistency | Conflict-free replicated data types (CRDTs) replicate across distributed nodes without coordination, guaranteeing ... |
| 54 | crun-1-27-0 | crun | 0.1.0 | oci-runtime, containers, podman, checkpointing, criu | Lightweight OCI container runtime written in C for running Linux containers with low memory footprint and high ... |
| 55 | crun-1-27-1 | crun | 0.1.0 | oci-runtime, containers, podman, checkpointing, criu | Lightweight OCI container runtime written in C for running Linux containers with low memory footprint and high ... |
| 56 | cryptography-46-0-0 | cryptography | 0.1.0 | cryptography, encryption, hashing, asymmetric, symmetric | Comprehensive toolkit for Python cryptographic operations using the cryptography library. Use when implementing ... |
| 57 | cryptography-47-0-0 | cryptography | 0.1.0 | cryptography, encryption, hashing, asymmetric, symmetric | Comprehensive toolkit for Python cryptographic operations using the cryptography library v47.0.0. Use when ... |
| 58 | curl-8-19-0 | curl | 0.1.0 | HTTP client, FTP, URL transfer, libcurl, CLI tool | CLI tool and C library for multi-protocol data transfers supporting HTTP/HTTPS, FTP, SFTP, and 30+ protocols. Covers ... |
| 59 | curl-8-20-0 | curl | 0.1.0 | HTTP client, FTP, URL transfer, libcurl, CLI tool | CLI tool and C library for multi-protocol data transfers supporting HTTP/HTTPS, FTP, SFTP, and 30+ protocols. Covers ... |
| 60 | cython-3-2-4 | cython | 0.1.0 | python, compiler, c-extension, performance, optimization | A skill for using Cython 3.2.4, an optimizing Python compiler that makes |
| 61 | d3-7-9-0 | d3 | 0.1.0 | JavaScript, visualization, SVG, Canvas, data-visualization | JavaScript library for bespoke data-driven documents providing SVG and Canvas-based visualizations with scales, ... |
| 62 | daisyui-5-5-0 | daisyui | 0.1.0 | tailwindcss, daisyui, ui-components, theming, css-framework | A skill for using DaisyUI 5.5, a component library for Tailwind CSS 4 that provides semantic class names for common ... |
| 63 | daisyui-5-5-19 | daisyui | 0.1.0 | tailwindcss, daisyui, ui-components, theming, css-framework | A skill for using DaisyUI 5.5.19, a component library for Tailwind CSS 4 that provides semantic class names for ... |
| 64 | dayjs-1-11-0 | dayjs | 0.1.0 | date, time, parsing, formatting, manipulation | Complete toolkit for date and time manipulation using Day.js 1.11, a minimalist 2kB library with ... |
| 65 | dayjs-1-11-20 | dayjs | 0.1.0 | date, time, parsing, formatting, manipulation | Complete toolkit for date and time manipulation using Day.js 1.11.20, a minimalist 2kB library with ... |
| 66 | deno-2-7-0 | deno | 0.1.0 | javascript, typescript, runtime, web-server, cli-tools | A comprehensive toolkit for the Deno 2.x JavaScript/TypeScript runtime, |
| 67 | deno-2-7-14 | deno | 0.1.0 | javascript, typescript, runtime, web-server, cli-tools | A comprehensive toolkit for the Deno 2.x JavaScript/TypeScript runtime, |
| 68 | design-md-0-1-1 | design-md | 0.1.0 | design.md, design-tokens, design-system, cli-tool, google | Format for describing visual identity to coding agents. Combines YAML front matter design tokens with markdown prose ... |
| 69 | dirac-0-2-89 | dirac | 0.1.0 | coding-agent, hash-anchored-edits, ast-manipulation, tree-sitter, multi-file-batching | Open-source coding agent that reduces API costs by 64.8% while maintaining 100% accuracy on complex refactoring ... |
| 70 | docker-docs-2026-04-16 | docker-docs | 0.1.0 | containers, docker-engine, docker-desktop, docker-compose, dockerfile | Comprehensive reference for Docker platform including Docker Engine, |
| 71 | dspy-2-4-12 | dspy | 0.2.0 | llm-programming, prompt-optimization, ai-compilation, few-shot-learning, instruction-tuning | Framework for programming rather than prompting language models. Compiles LM calls into self-improving pipelines by ... |
| 72 | dspy-3-2-0 | dspy | 0.1.0 | llm-programming, prompt-optimization, ai-compilation, few-shot-learning, instruction-tuning | Framework for programming rather than prompting language models. Compiles LM calls into self-improving pipelines by ... |
| 73 | duckdb-1-5-2 | duckdb | 0.1.0 | analytics, olap, embedded-database, sql, data-science | High-performance analytical SQL database with support for nested types, vectorized execution, and seamless ... |
| 74 | duckduckgo | duckduckgo | 0.2.0 | duckduckgo, search, web-search, scrapling, scraping | Searches DuckDuckGo via its HTML endpoint using scrapling. Returns results as markdown (default), raw HTML, compact ... |
| 75 | esbuild-0-28-0 | esbuild | 0.1.0 | javascript, bundler, typescript, jsx, css | Complete toolkit for esbuild v0.28 JavaScript bundler providing CLI, JavaScript API, and Go API access for bundling, ... |
| 76 | fetch-api | fetch-api | 0.1.0 | fetch, http, javascript, web-api, browser | JavaScript Fetch API for making HTTP requests from browsers and workers using promise-based fetch(). Covers ... |
| 77 | fltk-1-4-5 | fltk | 0.1.0 | fltk, gui, c++, desktop, widgets | Cross-platform C++ GUI toolkit with ~80 widget classes, OpenGL/GLUT integration, drawing primitives, image support, ... |
| 78 | gh-2-91-0 | gh | 0.1.0 | github, cli, devops, automation, ci-cd | GitHub CLI v2.91.0 for managing repositories, pull requests, issues, releases, workflows, codespaces, and more from ... |
| 79 | gh-2-92-0 | gh | 0.1.0 | github, cli, devops, automation, ci-cd | GitHub CLI v2.92.0 for managing repositories, pull requests, issues, releases, workflows, codespaces, and more from ... |
| 80 | ghostscript-10-07-0 | ghostscript | 0.1.0 | ghostscript, ghostpdl, pdf, postscript, document-conversion | >- |
| 81 | git | git | 0.2.1 | meta, meta-skill, git, version-control, conventional-commits | Complete Git 2.54.0 toolkit covering version control workflows, Conventional Commits v1.0.0, Keep a Changelog ... |
| 82 | grafana-13-0-1 | grafana | 0.1.0 | grafana, observability, dashboards, alerting, metrics | Grafana 13.0.1 observability platform for querying, visualizing, alerting on, and exploring metrics, logs, traces, ... |
| 83 | haproxy-3-3-0 | haproxy | 0.1.0 | load balancing, reverse proxy, SSL termination, high availability, HTTP proxy | Complete HAProxy 3.3.0 toolkit for load balancing, reverse proxying, |
| 84 | haproxy-3-3-8 | haproxy | 0.1.0 | load balancing, reverse proxy, SSL termination, high availability, HTTP proxy | Complete HAProxy 3.3.8 toolkit for load balancing, reverse proxying, |
| 85 | hnswlib-0-9-0 | hnswlib | 0.1.0 | ann, vector-search, hnsw, nearest-neighbor, simd | Header-only C++ library implementing HNSW graphs for fast approximate nearest neighbor search with Python bindings ... |
| 86 | htm-3-1-0 | htm | 0.1.0 | jsx-alternative, tagged-templates, preact, react, virtual-dom | A skill for using htm 3.1, a tagged template syntax library that provides JSX-like markup in plain JavaScript ... |
| 87 | htm-3-1-1 | htm | 0.1.0 | jsx-alternative, tagged-templates, preact, react, virtual-dom | A skill for using htm 3.1, a tagged template syntax library that provides JSX-like markup in plain JavaScript ... |
| 88 | htmx-2-0-0 | htmx | 0.1.0 | htmx, html, ajax, web-development, frontend | Build interactive web applications with htmx 2.x, a JavaScript library allowing access to modern browser features ... |
| 89 | htmx-2-0-10 | htmx | 0.1.0 | htmx, html, ajax, web-development, frontend | Build interactive web applications with htmx 2.0.10, a JavaScript library allowing access to modern browser features ... |
| 90 | htmx-4-0-0 | htmx | 0.1.0 | htmx, hypermedia, ajax, html-attributes, server-driven-ui | "Build interactive web applications with htmx 4.0, a JavaScript library providing HTML attributes for AJAX, CSS ... |
| 91 | hy-1-2-0 | hy | 0.1.0 | hy, hylang, lisp, python-embedded, macros | Lisp dialect embedded in Python providing prefix S-expression syntax, compile-time macros, quasiquoting, reader ... |
| 92 | jina-ai-reader | jina-ai-reader | 0.1.0 | url-to-markdown, web-crawling, web-search, llm-context, context-engineering | Converts any URL to LLM-friendly markdown via r.jina.ai and searches the web with s.jina.ai, returning top results ... |
| 93 | jinja2-3-1-6 | jinja2 | 0.1.0 | templating, html, python, jinja, web | Complete toolkit for Jinja2 v3.1.6 templating engine covering template design, Python API integration, custom ... |
| 94 | jq-1-8-1 | jq | 0.1.0 | json, cli, data-processing, transformation, shell | Complete toolkit for jq 1.8.1, the lightweight and flexible command-line JSON processor. Use when parsing, ... |
| 95 | jsonpath-rfc-9535-1-0-0 | jsonpath-rfc | 0.1.0 | JSON, query-language, data-selection, extraction, IETF-standard | Complete reference for JSONPath RFC 9535, the IETF specification defining string syntax for selecting and extracting ... |
| 96 | lambda-calculus | lambda-calculus | 0.1.0 | lambda-calculus, functional-programming, type-theory, church-encoding, currying | Formal system for expressing computation via function abstraction and application. Covers untyped lambda calculus ... |
| 97 | lambda-calculus-and-lisp-2026-05-12 | lambda-calculus-and-lisp | 0.1.0 | lambda-calculus, lisp, scheme, y-combinator, church-encoding | Covers the relationship between lambda calculus and Lisp, including McCarthy's EVAL, Church encodings in Scheme, the ... |
| 98 | lingua-py-2-2-0 | lingua-py | 0.1.0 | nlp, language-detection, text-processing, multilingual, natural-language-processing | Accurate natural language detection library for Python supporting 75 languages with high accuracy on short text and ... |
| 99 | lisp-in-c-2026-05-03 | lisp-in-c | 0.1.0 | lisp, c, interpreter, eval-apply, s-expression | "Build a Lisp interpreter in C from scratch, covering S-expression parsing, manual memory management, hash-table ... |
| 100 | lisp-in-python-2026-05-03 | lisp-in-python | 0.1.0 | lisp, interpreter, python, eval-apply, homoiconicity | "Build a minimal Lisp interpreter in Python covering the eval-apply cycle, recursive descent parsing, lexical ... |
| 101 | llama-cpp-1-0-0 | llama-cpp | 0.1.0 | llm, inference, gguf, quantization, cuda | C/C++ LLM inference library with GGUF support, quantization, GPU acceleration (CUDA/Metal/HIP/Vulkan/SYCL), ... |
| 102 | lodash-4-18-1 | lodash | 0.1.0 | javascript, utility-library, data-manipulation, functional-programming, browser-compatibility | Complete toolkit for Lodash 4.18 utility library providing 300+ helper functions for arrays, collections, objects, ... |
| 103 | logfire-4-32-1 | logfire | 0.1.0 | observability, tracing, opentelemetry, logging, metrics | AI observability platform built on OpenTelemetry by the Pydantic team. Native SDKs for Python, ... |
| 104 | logic | logic | 0.1.0 | logic, propositional-logic, first-order-logic, higher-order-logic, modal-logic | Comprehensive reference covering formal logic systems from propositional through higher-order logic, plus modal ... |
| 105 | lua-5-5-0 | lua | 0.1.0 | lua, scripting, embeddable, c-api, dynamic-language | Lightweight embeddable scripting language with a small C footprint, dynamic typing via tables, coroutines, and a ... |
| 106 | matplotlib-3-10-8 | matplotlib | 0.1.0 | plotting, visualization, charts, graphs, data-visualization | Comprehensive toolkit for Matplotlib 3.10.8, the Python plotting library for static, animated, and interactive ... |
| 107 | matplotlib-3-10-9 | matplotlib | 0.1.0 | plotting, visualization, charts, graphs, data-visualization | Comprehensive toolkit for Matplotlib 3.10.9, the Python plotting library for static, animated, and interactive ... |
| 108 | mcp-2025-11-25 | mcp | 0.1.0 | mcp, model-context-protocol, llm, ai-integration, json-rpc | Model Context Protocol (MCP) 2025-11-25 specification covering client-host-server architecture, JSON-RPC messaging, ... |
| 109 | mem0-1-0-11 | mem0 | 0.1.0 | memory, llm, ai-agents, vector-search, langchain | Universal self-improving memory layer for LLM applications (Mem0 v1.0.11) enabling persistent context across ... |
| 110 | mem0-2-0-1 | mem0 | 0.1.0 | memory, llm, ai-agents, vector-search, hybrid-search | Self-improving memory layer for LLM agents (Mem0 v2.0.1) enabling persistent context across sessions with ... |
| 111 | mempalace-3-3-0 | mempalace | 0.1.0 | ai-memory, local-rag, chromadb, knowledge-graph, mcp | Local AI memory system that mines projects and conversations into a searchable index using ChromaDB for vector ... |
| 112 | mempalace-3-3-4 | mempalace | 0.1.0 | ai-memory, local-rag, chromadb, knowledge-graph, mcp | Local AI memory system that mines projects and conversations into a searchable index using ChromaDB for vector ... |
| 113 | mermaid-11-14-0 | mermaid | 0.1.0 | diagramming, visualization, charts, flowcharts, sequence-diagrams | JavaScript-based diagramming tool that generates diagrams from Markdown-inspired text definitions. Supports 30+ ... |
| 114 | nekovm-2-4-1 | nekovm | 0.1.0 | nekovm, neko, virtual-machine, scripting-language, haxe | Stack-based bytecode VM and dynamically typed scripting language, primarily as a compilation target for Haxe. ... |
| 115 | networkx-3-6-1 | networkx | 0.1.0 | graph-theory, network-analysis, complex-networks, centrality, community-detection | Python package for creating, manipulating, and studying complex networks. Supports graph generation, algorithms ... |
| 116 | networkxternal-0-3-0 | networkxternal | 0.1.0 | graph, database, networkx, sqlite, postgresql | NetworkX-compatible interface for external memory MultiDiGraphs persisted in databases (SQLite, PostgreSQL, MySQL, ... |
| 117 | networkxternal-0-5 | networkxternal | 0.1.0 | graph, database, networkx, external-memory, sql | NetworkX-compatible interface for external memory MultiDiGraphs persisted in databases (SQLite, PostgreSQL, MySQL, ... |
| 118 | nextjs-16-2-3 | nextjs | 0.1.0 | react, nextjs, ssr, ssg, fullstack | Build production-ready React applications with Next.js 16.2.3, providing App Router and Pages Router, server/client ... |
| 119 | nextjs-16-2-4 | nextjs | 0.1.0 | react, nextjs, ssr, ssg, fullstack | Build production-ready React applications with Next.js 16.2.4, providing App Router and Pages Router, server/client ... |
| 120 | nginx-1-30-0 | nginx | 0.1.0 | HTTP server, reverse proxy, load balancer, SSL/TLS, caching | High-performance HTTP server, reverse proxy, and load balancer supporting HTTP/HTTPS proxying, SSL/TLS termination, ... |
| 121 | nltk-3-9-2 | nltk | 0.1.0 | nlp, natural-language-processing, python, text-processing, wordnet | Complete toolkit for Natural Language Processing with NLTK 3.9.2, covering tokenization, stemming, lemmatization, ... |
| 122 | nltk-3-9-4 | nltk | 0.1.0 | nlp, natural-language-processing, python, text-processing, wordnet | Complete toolkit for Natural Language Processing with NLTK 3.9.4, covering tokenization, stemming, lemmatization, ... |
| 123 | nodejs-24-14-0 | nodejs | 0.1.0 | nodejs, javascript, runtime, server-side, async | Complete Node.js 24.14 runtime toolkit covering core modules, async programming, HTTP servers, file system ... |
| 124 | nuitka-4-0-8 | nuitka | 0.1.0 | python, compiler, c-extension, standalone, onefile | Python compiler that translates Python code to C and native executables. Use when compiling Python applications for ... |
| 125 | numba-0-65-0 | numba | 0.1.0 | jit, compiler, llvm, numba, numpy | JIT compiler for Python that translates numerical code into optimized machine code using LLVM. Supports @jit, @njit, ... |
| 126 | numba-0-65-1 | numba | 0.1.0 | jit, compiler, llvm, numba, numpy | JIT compiler for Python that translates numerical code into optimized machine code using LLVM. Supports @jit, @njit, ... |
| 127 | numeral-2-0-6 | numeral | 0.1.0 | javascript, number-formatting, currency, localization | A JavaScript library for formatting and manipulating numbers. Use when formatting currency, percentages, bytes, time ... |
| 128 | numkong-7-6-0 | numkong | 0.1.0 | vector-similarity, simd, mixed-precision, dot-product, distance-metrics | Ultra-fast mixed-precision vector similarity and distance library with 2000+ SIMD kernels across x86, ARM, RISC-V. ... |
| 129 | numpy-2-4-4 | numpy | 0.1.0 | numpy, arrays, scientific-computing, linear-algebra, data-science | Fundamental package for scientific computing with Python, providing n-dimensional arrays, mathematical functions, ... |
| 130 | oat-0-6-0 | oat | 0.1.0 | javascript, css, frontend, ui-components, semantic-html | Ultra-lightweight semantic UI component library (~8KB CSS + JS, zero dependencies) that styles HTML elements by ... |
| 131 | obscura-0-1-0 | obscura | 0.1.0 | headless-browser, web-scraping, rust, cdp, puppeteer | Lightweight headless browser engine written in Rust for web scraping and AI agent automation. Runs JavaScript via ... |
| 132 | obscura-0-1-1 | obscura | 0.1.0 | headless-browser, web-scraping, rust, cdp, puppeteer | Lightweight headless browser engine written in Rust for web scraping and AI agent automation. Runs JavaScript via ... |
| 133 | openai-2-31-0 | openai | 0.1.0 | openai, llm, ai, chat-completions, responses-api | Python SDK for OpenAI API v2.31 providing type-safe access to Responses API, Chat Completions, embeddings, audio ... |
| 134 | openai-2-33-0 | openai | 0.1.0 | openai, llm, ai, chat-completions, responses-api | Python SDK for OpenAI API v2.33 providing type-safe access to Responses API, Chat Completions, embeddings, audio ... |
| 135 | opentelemetry-1-55-0 | opentelemetry | 0.1.0 | distributed-tracing, metrics, logging, observability, OTLP | Complete OpenTelemetry 1.55.0 specification toolkit for implementing distributed tracing, metrics collection, and ... |
| 136 | opentelemetry-1-56-0 | opentelemetry | 0.1.0 | distributed-tracing, metrics, logging, observability, OTLP | Complete OpenTelemetry 1.56.0 specification toolkit for implementing distributed tracing, metrics collection, and ... |
| 137 | opentelemetry-collector-1-56-0 | opentelemetry-collector | 0.1.0 | opentelemetry, collector, observability, telemetry, tracing | Vendor-agnostic telemetry collector for OpenTelemetry providing configurable pipelines for traces, metrics, and ... |
| 138 | opentelemetry-python-1-41-0 | opentelemetry-python | 0.1.0 | opentelemetry, observability, tracing, metrics, logging | OpenTelemetry Python toolkit for distributed tracing, metrics collection, and log management with OTLP exporters, ... |
| 139 | opentelemetry-python-1-41-1 | opentelemetry-python | 0.1.0 | opentelemetry, observability, tracing, metrics, logging | OpenTelemetry Python toolkit for distributed tracing, metrics collection, and log management with OTLP exporters, ... |
| 140 | ot-2026-05-03 | ot | 0.1.0 | operational-transformation, ot, collaborative-editing, concurrency-control, real-time-collaboration | Operational Transformation theory and practice for consistency in real-time collaborative editing. Covers ... |
| 141 | pacote-21-5-0 | pacote | 0.1.0 | npm, packages, npx, download, extract | Inspect, download, and extract npm packages without installing them first using pacote 21.5 via npx. Supports ... |
| 142 | pandoc-3-9-0-2 | pandoc | 0.1.0 | pandoc, document-converter, markdown, latex, pdf | Universal document converter supporting 50+ input formats (Markdown, HTML, LaTeX, docx, EPUB, Org, RST, AsciiDoc) ... |
| 143 | paramiko-4-0-0 | paramiko | 0.1.0 | ssh, sshv2, sftp, remote-execution, file-transfer | >- |
| 144 | payloadcms-3-82-1 | payloadcms | 0.1.0 | cms, headless-cms, content-management, nextjs, typescript | Payload CMS headless CMS toolkit including collections, fields, access control, authentication, custom components, ... |
| 145 | payloadcms-3-84-1 | payloadcms | 0.1.0 | cms, headless-cms, content-management, nextjs, typescript | Payload CMS headless CMS toolkit including collections, fields, access control, authentication, custom components, ... |
| 146 | payloadcms-blank-3-82-1 | payloadcms-blank | 0.1.0 | cms, payload, nextjs, mongodb, headless-cms | Minimal Payload CMS 3.82.1 starter template providing a clean foundation for building custom headless CMS ... |
| 147 | payloadcms-blank-3-84-1 | payloadcms-blank | 0.1.0 | cms, payload, nextjs, mongodb, headless-cms | Minimal Payload CMS 3.84.1 starter template providing a clean foundation for building custom headless CMS ... |
| 148 | payloadcms-ecommerce-3-82-1 | payloadcms-ecommerce | 0.1.0 | payloadcms, ecommerce, commerce, stripe, payments | Payload CMS ecommerce template providing production-ready online store with products, variants, carts, orders, ... |
| 149 | payloadcms-ecommerce-3-84-1 | payloadcms-ecommerce | 0.1.0 | payloadcms, ecommerce, commerce, stripe, payments | Payload CMS ecommerce template providing production-ready online store with products, variants, carts, orders, ... |
| 150 | payloadcms-website-3-82-1 | payloadcms-website | 0.1.0 | cms, headless-cms, website-template, nextjs, typescript | Payload CMS website template providing production-ready starter for content-driven websites, blogs, and portfolios ... |
| 151 | payloadcms-website-3-84-1 | payloadcms-website | 0.1.0 | cms, headless-cms, website-template, nextjs, typescript | Payload CMS website template providing production-ready starter for content-driven websites, blogs, and portfolios ... |
| 152 | peg-2026-05-03 | peg | 0.1.0 | peg, parsing, parser-generator, formal-grammar, compiler-construction | Parsing Expression Grammars (PEGs) — recognition-based formal grammars using ordered choice to eliminate ambiguity, ... |
| 153 | picocss-2-1-1 | picocss | 0.1.0 | css-framework, semantic-html, responsive-design, light-dark-mode, minimal-css | Minimalist CSS framework that styles semantic HTML elements by default with responsive typography, automatic ... |
| 154 | pi-mono-0-66-1 | pi-mono | 0.1.0 | ai-coding-agent, terminal-harness, extensions, tui, session-management | Complete implementation guide for pi-mono monorepo architecture covering provider abstraction, agent runtime, ... |
| 155 | pi-mono-0-71-0 | pi-mono | 0.1.0 | ai-coding-agent, terminal-harness, extensions, tui, session-management | Complete implementation guide for pi-mono monorepo architecture covering provider abstraction, agent runtime, ... |
| 156 | pi-mono-0-74-0 | pi-mono | 0.1.0 | pi, pi-mono, coding-agent, ai-agent, terminal-ai | >- |
| 157 | pinecone-router-7-5-0 | pinecone-router | 0.1.0 | alpinejs, router, spa, client-side-routing, single-page-application | Client-side routing toolkit for Alpine.js applications using Pinecone Router v7.5, providing route matching, ... |
| 158 | pipe | pipe | 0.1.4 | pipe, meta, meta-skill, chaining, workflow | Unix-style pipe expression syntax for chaining multiple agent operations sequentially. Each stage's output becomes ... |
| 159 | plan | plan | 0.1.9 | meta, meta-skill, plan, workflow, task-management | Phase/task based workflow system with PLAN.md as single source of truth. Use when tackling projects that require ... |
| 160 | podman-5-8-1 | podman | 0.1.0 | containers, daemonless, rootless, oci, pods | Daemonless container engine with Docker-compatible CLI for managing containers, pods, images, volumes, and networks. ... |
| 161 | podman-5-8-2 | podman | 0.1.0 | containers, daemonless, rootless, oci, pods | Daemonless container engine with Docker-compatible CLI for managing containers, pods, images, volumes, and networks. ... |
| 162 | podman-compose-1-5-0 | podman-compose | 0.1.0 | podman, compose, containers, orchestration, devops | Orchestrates multi-container applications using Compose specification files with Podman backend. Use when deploying ... |
| 163 | podman-py-5-8-0 | podman-py | 0.2.0 | podman, containers, python, docker-alternative, container-management | Python client library for Podman container engine providing programmatic access to containers, images, pods, ... |
| 164 | poppler-26-05-0 | poppler | 0.1.0 | poppler, pdf, rendering, c++, glib | PDF rendering library providing C++, glib, Qt5, and Qt6 APIs for loading, parsing, rendering, and extracting content ... |
| 165 | prescheme-2026-05-03 | prescheme | 0.1.0 | prescheme, scheme, lisp, static-typing, systems-programming | Statically typed Scheme dialect that compiles to C via Hindley/Milner type inference and CPS transformations. ... |
| 166 | pulp-3-3-0 | pulp | 0.1.0 | optimization, linear-programming, mixed-integer-programming, lp, mip | Complete toolkit for PuLP 3.3.0, a Python linear and mixed-integer programming modeler generating MPS/LP/JSON files ... |
| 167 | pycrdt-0-12-50 | pycrdt | 0.1.0 | pycrdt, crdt, yjs, yrs, collaborative-editing | Python bindings for Yrs, the Rust port of the Yjs CRDT framework. Provides shared data types (Text, Array, Map, XML) ... |
| 168 | python-lambda-calculus-3-1-0 | python-lambda-calculus | 0.1.0 | lambda-calculus, lambda-calculus-3-1-0, functional-programming, symbolic-computation, church-encoding | Python library implementing Lambda calculus operations including term construction (Variable, Abstraction, ... |
| 169 | python-louvain-0-16 | python-louvain | 0.1.0 | community-detection, louvain, graph-algorithms, networkx, modularity | Python implementation of the Louvain algorithm for community detection in graphs. Produces modularity-optimized ... |
| 170 | python-scrypt-0-9-4 | python-scrypt | 0.1.0 | scrypt, password-hashing, key-derivation, cryptography, pbkdf | Python toolkit for scrypt-based key derivation and password hashing. Use when implementing secure password storage, ... |
| 171 | pytorch-2-12-0 | pytorch | 0.1.0 | pytorch, deep-learning, tensors, autograd, torch-compile | >- |
| 172 | pywebview-6-2-0 | pywebview | 0.1.0 | python, gui, webview, desktop, cross-platform | Cross-platform wrapper around native webview components that lets Python applications display HTML content in a ... |
| 173 | pywebview-6-2-1 | pywebview | 0.1.0 | python, gui, webview, desktop, cross-platform | Cross-platform wrapper around native webview components that lets Python applications display HTML content in a ... |
| 174 | pyzmq-27-1-0 | pyzmq | 0.1.0 | zeromq, zmq, messaging, networking, sockets | Complete toolkit for Python bindings to ZeroMQ (pyzmq 27.x) covering socket types, messaging patterns, async/await ... |
| 175 | quickjs-2025-09-13 | quickjs | 0.1.0 | javascript, engine, es2023, c-api, embedding | Small and fast JavaScript engine supporting ES2023 with C API for embedding, qjs REPL interpreter, and qjsc bytecode ... |
| 176 | qwen3-embedding-1-0-0 | qwen3-embedding | 0.1.0 | embedding, semantic-search, retrieval, multilingual, reranking | Complete toolkit for Qwen3 Embedding models (0.6B, 4B, 8B) and Qwen3 |
| 177 | qwen3-reranker-1-0-0 | qwen3-reranker | 0.1.0 | reranking, text-ranking, retrieval, cross-encoder, multilingual | Comprehensive toolkit for Qwen3 Reranker models (0.6B, 4B, 8B) — cross-encoder text reranking with 100+ language ... |
| 178 | qwen3-vl-embedding-0-1-0 | qwen3-vl-embedding | 0.1.0 | embedding, multimodal, vision-language, retrieval, semantic-search | Complete toolkit for Qwen3-VL-Embedding 0.1.0 multimodal embedding models (2B and 8B) supporting text, images, ... |
| 179 | qwen3-vl-reranker-1-0-0 | qwen3-vl-reranker | 0.1.0 | reranker, multimodal, retrieval, qwen, cross-encoder | Complete toolkit for Qwen3-VL-Reranker (2B and 8B) multimodal reranking models that score relevance of text, image, ... |
| 180 | raft-2026-05-03 | raft | 0.1.0 | raft, consensus, distributed-systems, replicated-log, leader-election | Raft consensus algorithm for replicated log management across server clusters. Covers leader election, log ... |
| 181 | ralph-orchestrator-2-9-2 | ralph-orchestrator | 0.1.0 | ai-orchestration, ralph-wiggum, autonomous-agents, hat-system, event-driven | Orchestration framework that keeps AI agents in a loop until tasks are done. Supports Claude Code, Gemini CLI, ... |
| 182 | redis-om-python-1-1-0 | redis-om-python | 0.1.0 | redis, orm, object-mapping, pydantic, redi-search | A skill for using Redis OM Python v1.1, an object mapping library that |
| 183 | redis-py-7-4-0 | redis-py | 0.1.0 | redis, database, key-value-store, caching, async | Comprehensive Python client for Redis database and key-value store. Use when building Python applications requiring ... |
| 184 | rich-15-0-0 | rich | 0.1.0 | terminal, cli, formatting, color, tables | Python library for rich text and beautiful terminal formatting. Provides color, tables, progress bars, markdown ... |
| 185 | rqlite-10-0-1 | rqlite | 0.1.0 | database, distributed-systems, sqlite, raft, high-availability | Comprehensive toolkit for rqlite 10.0.1, a lightweight distributed relational database built on SQLite with Raft ... |
| 186 | rqlite-9-4-0 | rqlite | 0.1.0 | database, distributed-systems, sqlite, raft, high-availability | Comprehensive toolkit for rqlite 9.4, a lightweight distributed relational database built on SQLite with Raft ... |
| 187 | rsync-3-4-1 | rsync | 0.1.0 | file-transfer, backup, mirroring, sync, daemon | Complete toolkit for rsync 3.4.1, the fast file-copying tool using delta-transfer algorithm. Use when backing up ... |
| 188 | rsync-3-4-2 | rsync | 0.1.0 | file-transfer, backup, mirroring, sync, daemon | Complete toolkit for rsync 3.4.2, the fast file-copying tool using delta-transfer algorithm. Use when backing up ... |
| 189 | ruff-0-15-12 | ruff | 0.1.0 | python, linter, formatter, code-quality, flake8 | Extremely fast Python linter and code formatter written in Rust with 900+ rules, block-level suppressions, and ... |
| 190 | ruff-0-4-10 | ruff | 0.1.0 | python, linter, formatter, code-quality, flake8 | Extremely fast Python linter and formatter written in Rust, replacing Flake8, Black, isort, and more with 10x-100x ... |
| 191 | rustfs-1-0-0-alpha-93 | rustfs | 0.1.0 | object-storage, s3, swift, distributed-systems, observability | High-performance distributed object storage system with S3-compatible API, OpenStack Swift support, and ... |
| 192 | rustfs-1-0-0-beta-1 | rustfs | 0.1.0 | object-storage, s3, swift, distributed-systems, observability | High-performance distributed object storage system with S3-compatible API, OpenStack Swift support, and ... |
| 193 | scheme-in-python-2026-05-03 | scheme-in-python | 0.1.0 | scheme, interpreter, lisp, python, eval-apply | Build a Scheme interpreter in Python covering tokenization, eval/apply loop, environment frames with lexical and ... |
| 194 | scikit-learn-1-8-0 | scikit-learn | 0.1.0 | machine-learning, classification, regression, clustering, pipelines | Complete scikit-learn 1.8 toolkit for machine learning covering supervised and unsupervised algorithms, pipelines, ... |
| 195 | scipy-1-17-1 | scipy | 0.1.0 | scipy, scientific-computing, optimization, integration, statistics | Scientific computing library for Python covering optimization, integration, interpolation, linear algebra, signal ... |
| 196 | scrapling-0-4-8 | scrapling | 0.1.0 | scrapling, web-scraping, html-parsing, crawler, anti-bot | Adaptive web scraping framework for Python providing HTML parsing with CSS/XPath/text/regex selection, HTTP and ... |
| 197 | semver-2-0-0 | semver | 0.1.0 | versioning, semver, semantic-versioning, releases, dependency-management | Implement and validate Semantic Versioning 2.0.0 to manage software version numbers, determine compatibility, ... |
| 198 | sentence-transformers-5-4-1 | sentence-transformers | 0.1.0 | embeddings, semantic-search, reranking, nlp, sentence-embeddings | Comprehensive toolkit for computing text embeddings, semantic search, and reranking using Sentence Transformers ... |
| 199 | s-expression | s-expression | 0.1.0 | s-expression, sexp, lisp, data-format, tree | S-expressions (symbolic expressions) are a minimal notation for nested tree-structured data using atoms and lists. ... |
| 200 | s-expression-alternatives | s-expression-alternatives | 0.1.0 | s-expression, sweet-expressions, i-expressions, o-expressions, liso | Alternative syntaxes for Lisp-family languages that reduce or eliminate parentheses while preserving homoiconicity ... |
| 201 | s-expression-interpreter | s-expression-interpreter | 0.1.0 | s-expression, lisp, interpreter, eval-apply, scheme | Build and understand s-expression interpreters in Python and C. Covers lexer-free tokenization, recursive descent ... |
| 202 | skman | skman | 0.3.1 | meta, meta skill, skill manager, skill package manager, authoring | Skill Package Manager, skman, it is meta skill for skill authoring and skill package manager for AI agents. |
| 203 | solidjs-1-9-12 | solidjs | 0.1.0 | solidjs, reactivity, signals, jsx, fine-grained | >- |
| 204 | solid-meta-0-29-0 | solid-meta | 0.1.0 | solidjs, meta-tags, document-head, ssr, seo | Manages document head tags in SolidJS applications with @solidjs/meta v0.29, providing SSR-ready Document Head ... |
| 205 | solid-meta-0-29-4 | solid-meta | 0.1.0 | solidjs, meta-tags, document-head, ssr, seo | Manages document head tags in SolidJS applications with @solidjs/meta v0.29.4, providing SSR-ready Document Head ... |
| 206 | solid-router-0-16-0 | solid-router | 0.1.0 | solidjs, router, spa, routing, ssg | The universal router for SolidJS providing fine-grained reactivity for route navigation with support for ... |
| 207 | solid-router-0-16-1 | solid-router | 0.1.0 | solidjs, router, spa, routing, ssg | The universal router for SolidJS providing fine-grained reactivity for route navigation with support for ... |
| 208 | solid-start-1-3-0 | solid-start | 0.1.0 | solidjs, fullstack, ssr, ssg, csr | Fullstack framework for SolidJS providing SSR, SSG, API routes, file-based routing, and server functions. Use when ... |
| 209 | solid-start-1-3-2 | solid-start | 0.1.0 | solidjs, fullstack, ssr, ssg, csr | Fullstack framework for SolidJS providing SSR, SSG, API routes, file-based routing, and server functions. Use when ... |
| 210 | spacy-3-8-14 | spacy | 0.1.0 | nlp, natural-language-processing, text-analysis, machine-learning, python | Industrial-strength NLP library for Python providing tokenization, named entity recognition, dependency parsing, and ... |
| 211 | spec-kit-0-6-1 | spec-kit | 0.1.0 | specification-driven-development, sdd, ai-assisted-development, project-management, workflow-automation | Spec-Driven Development toolkit for specification-first workflows with AI agents. Generate executable ... |
| 212 | spec-kit-0-8-3 | spec-kit | 0.1.0 | specification-driven-development, sdd, ai-assisted-development, project-management, workflow-automation | Spec-Driven Development toolkit for specification-first workflows with AI agents. Generate executable ... |
| 213 | sqlalchemy-2-0-49 | sqlalchemy | 0.1.0 | database, orm, sql, python, postgresql | Complete SQLAlchemy 2.0 toolkit for database operations, ORM mapping, and SQL expression construction. Use when ... |
| 214 | sqlite-3-53-0 | sqlite | 0.1.0 | sqlite, database, sql, json, fts | Embedded SQL database providing ACID transactions, full-text search (FTS5), spatial indexing (R-Tree), JSON ... |
| 215 | stanza-1-11-1 | stanza | 0.1.0 | nlp, natural-language-processing, multilingual, tokenization, pos-tagging | Stanford NLP Group's Python NLP library for 80+ languages providing tokenization, POS tagging, lemmatization, ... |
| 216 | stitch-2026-05-04 | stitch | 0.1.0 | stitch, ui-design, ai-design, mcp, google-labs | AI-powered UI design tool generating high-fidelity screens and frontend code from text prompts and images. Provides ... |
| 217 | stringzilla-4-6-0 | stringzilla | 0.1.0 | simd, string-processing, search, hashing, sorting | High-performance SIMD-accelerated string library for search, hashing, sorting, and fuzzy matching in ... |
| 218 | sympy-1-14-0 | sympy | 0.1.0 | sympy, symbolic-math, computer-algebra, python, mathematics | Complete toolkit for SymPy 1.14.0 providing symbolic mathematics in Python including algebra, calculus, matrices, ... |
| 219 | tailwindcss-4-2-4 | tailwindcss | 0.1.0 | css, tailwind, styling, frontend, utility-first | A skill for using Tailwind CSS v4.2, a utility-first CSS framework with CSS-based configuration via @theme, OKLCH ... |
| 220 | tailwindcss-browser-4-2-0 | tailwindcss-browser | 0.1.0 | css, tailwind, browser, prototyping, no-build | In-browser Tailwind CSS v4.2 build (@tailwindcss/browser) that compiles utility classes at runtime without a build ... |
| 221 | tailwindcss-browser-4-2-4 | tailwindcss-browser | 0.1.0 | css, tailwind, browser, prototyping, no-build | In-browser Tailwind CSS v4.2 build (@tailwindcss/browser) that compiles utility classes at runtime without a build ... |
| 222 | tea-0-14-0 | tea | 0.1.0 | gitea, cli, git, devops, ci-cd | Official CLI for Gitea servers. Manage repositories, issues, pull requests, releases, and admin operations from the ... |
| 223 | temporal-api | temporal-api | 0.1.0 | temporal, date-time, timezone, calendar, javascript | ECMAScript Temporal API for date/time management replacing legacy Date. Provides timezone-aware arithmetic, calendar ... |
| 224 | textblob-0-20-0 | textblob | 0.1.0 | nlp, text-processing, sentiment-analysis, pos-tagging, tokenization | Python library for simplified natural language processing providing POS tagging, noun phrase extraction, sentiment ... |
| 225 | textual-8-2-4 | textual | 0.1.0 | tui, terminal-ui, python, framework, reactive | Python framework for building terminal and browser UIs. Provides widget-based DOM, CSS styling (.tcss), reactive ... |
| 226 | textual-8-2-5 | textual | 0.1.0 | tui, terminal-ui, python, framework, reactive | Python framework for building terminal and browser UIs. Provides widget-based DOM, CSS styling (.tcss), reactive ... |
| 227 | tinycc-0-9-27 | tinycc | 0.1.0 | c-compiler, code-generation, dynamic-compilation, x86, arm | Complete toolkit for TinyCC 0.9.27, a small hyper-fast C compiler generating native x86/x86_64/ARM code without an ... |
| 228 | tinypy-1-1-0 | tinypy | 0.1.0 | python, vm, embedding, scripting, minimal | Minimalist Python implementation in ~64k of code with a bootstrapped parser, bytecode compiler, and VM with ... |
| 229 | tinyscheme-1-41 | tinyscheme | 0.1.0 | tinyscheme, scheme, lisp, interpreter, embedded | Lightweight Scheme interpreter (R5RS subset) in ~5000 lines of C, designed as an embeddable scripting engine. ... |
| 230 | tokenizers-0-22-3 | tokenizers | 0.1.0 | nlp, tokenization, rust, python, transformers | Fast state-of-the-art tokenizers library for NLP written in Rust with |
| 231 | tokenizers-0-23-1 | tokenizers | 0.1.0 | nlp, tokenization, rust, python, transformers | Fast state-of-the-art tokenizers library for NLP written in Rust with Python, Node.js, and Ruby bindings. Use when ... |
| 232 | transformers-5-5-4 | transformers | 0.1.0 | nlp, machine-learning, deep-learning, pytorch, huggingface | Complete toolkit for Hugging Face Transformers 5.5.4 providing pretrained models for NLP, vision, audio, video, and ... |
| 233 | transformers-5-7-0 | transformers | 0.1.0 | nlp, machine-learning, deep-learning, pytorch, huggingface | Complete toolkit for Hugging Face Transformers 5.7.0 providing pretrained models for NLP, vision, audio, video, and ... |
| 234 | ty-0-0-29 | ty | 0.1.0 | python, type-checking, static-analysis, language-server, mypy-alternative | Extremely fast Python type checker and language server written in Rust, 10x-100x faster than mypy and Pyright. ... |
| 235 | ty-0-0-33 | ty | 0.1.0 | python, type-checking, static-analysis, language-server, mypy-alternative | Extremely fast Python type checker and language server written in Rust, 10x-100x faster than mypy and Pyright. ... |
| 236 | tzip | tzip | 0.4.0 | meta, meta-skill, token-prune, efficiency, guidelines | Lightweight token-pruning communication mode that drops filler and hedging while keeping full sentences and ... |
| 237 | upx-5-1-1 | upx | 0.1.0 | compression, executable-packer, distribution, size-optimization, cross-platform | >- |
| 238 | usearch-2-24-0 | usearch | 0.1.0 | vector-search, hnsw, similarity-search, approximate-nearest-neighbors, embedding-search | High-performance single-file similarity search engine for vectors using HNSW with user-defined metrics, ... |
| 239 | usearch-2-25-1 | usearch | 0.1.0 | vector-search, ann, hnsw, similarity-search, clustering | High-performance single-file similarity search engine for vectors using HNSW with user-defined metrics, ... |
| 240 | uv-0-11-6 | uv | 0.1.0 | python, package-management, dependency-resolution, virtual-environments, pip-replacement | Extremely fast Python package and project manager written in Rust, replacing pip, pip-tools, pipx, poetry, pyenv, ... |
| 241 | uv-0-11-8 | uv | 0.1.0 | python, package-management, dependency-resolution, virtual-environments, pip-replacement | Extremely fast Python package and project manager written in Rust, replacing pip, pip-tools, pipx, poetry, pyenv, ... |
| 242 | webfetch | webfetch | 0.2.1 | webfetch, web-scraping, url-fetch, markdown, scrapling | Fetches any URL and converts the full page to clean AI-targeted markdown using scrapling. Use when scraping ... |
| 243 | websearch | websearch | 0.2.1 | websearch, web-search, duckduckgo, yaml-output, scrapling | Searches DuckDuckGo via its HTML endpoint and outputs results as raw YAML. Uses a deterministic bash script, ... |
| 244 | yjs-13-6-30 | yjs | 0.1.0 | yjs, crdt, collaborative-editing, real-time, shared-types | CRDT framework for conflict-free collaborative editing with shared types (Y.Map, Y.Array, Y.Text). Provides ... |
| 245 | yq-4-53-2 | yq | 0.1.0 | yaml, json, xml, ini, csv | >- |
| 246 | zeromq-wiki-3-2-0 | zeromq-wiki | 0.1.0 | zeromq, messaging, distributed-systems, networking, sockets | A comprehensive toolkit for ZeroMQ (ØMQ) messaging library covering socket patterns, protocols, architecture, and ... |
| 247 | zeromq-zguide-3-2-0 | zeromq-zguide | 0.1.0 | zeromq, zmq, messaging, sockets, distributed-systems | Complete ZeroMQ ZGuide 3.2 toolkit covering messaging patterns, socket types, reliability mechanisms, and ... |

## Statistics

- **Total Skills**: 247
