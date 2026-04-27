# tangled-skills

Collection of Skills for Agents by Tangled

## About

All skills in this repository are automatically generated using the `write-skill` skill. Each skill is created from public references, official documentation URLs, and other publicly available resources to ensure accuracy and completeness.

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
| 1 | a2a-1-0-0 | a2a | 1.0.0 | agent-communication, multi-agent, interoperability, protocol, json-rpc | The Agent2Agent (A2A) Protocol v1.0.0 is an open standard enabling communication and interoperability between... |
| 2 | agent-coding-mini-rasbt-0-1-0 | agent-coding-mini-rasbt | 0.1.0 | coding-agent, ollama, local-ai, autonomous-agent, python | A minimal standalone coding agent framework by Sebastian Raschka backed by Ollama that provides workspace context... |
| 3 | agent-coding-wyattdave-0-1-0 | agent-coding-wyattdave | 0.1.0 | ai-agents, prompt-engineering, vscode-extensions, coding-assistants, customization | A toolkit for creating custom AI coding agents using prompt engineering, instruction files, and skill modules. Use when... |
| 4 | agent-nirzabari-0-1-0 | agent-nirzabari | 0.1.0 | ai-agents, coding-agents, harness-engineering, llm-systems, agent-architecture | A comprehensive guide to understanding and building coding agent harnesses, covering the 7-layer architecture, context... |
| 5 | agent-ralph-loop-claude | agent-ralph-loop-claude | 1.0.0 | claude-code, plugin, iterative-development, autonomous-agents, ralph-wiggum | Implements the Ralph Wiggum technique as a Claude Code plugin for iterative, self-referential AI development loops. Use... |
| 6 | agent-ralph-loop-vercel-labs | agent-ralph-loop-vercel-labs | 0.0.3 | autonomous-agent, ai-sdk, iterative-loop, coding-agent, continuous-autonomy | Continuous autonomy framework for the Vercel AI SDK implementing the Ralph Wiggum technique — an iterative outer loop... |
| 7 | agent-ralph-wiggum-fstandhartinger-0-3-0 | agent-ralph-wiggum-fstandhartinger | 0.3.0 | autonomous-development, spec-driven, iterative-loops, ai-coding, ralph-wiggum | Autonomous AI coding with spec-driven development combining iterative bash loops and SpecKit-style specifications for... |
| 8 | agent-wiggum-cli-federiconeri | agent-wiggum-cli-federiconeri | 0.18.3 | autonomous-coding, ralph-loop, spec-driven-development, ai-agent, claude-code | Wiggum CLI is an open-source autonomous coding agent that plugs into any codebase — scans your tech stack, generates... |
| 9 | agentmemory-0-8-10 | agentmemory | 0.8.10 | ai-agent, persistent-memory, mcp-server, hybrid-search, knowledge-graph | Persistent memory engine for AI coding agents providing automatic cross-session context capture, hybrid search (BM25 +... |
| 10 | agentmemory-0-8-9 | agentmemory | 0.8.9 | ai-agents, memory, mcp-server, persistent-context, vector-search | Persistent memory engine for AI coding agents providing automatic cross-session context capture, hybrid search (BM25 +... |
| 11 | aiohttp-3-13-0 | aiohttp | 3.13.0 | http, async, client, server, websocket | Async HTTP client/server for Python asyncio. Use when building async web applications, REST APIs, or making concurrent... |
| 12 | aiohttp-cors-0-8-1 | aiohttp-cors | 0.8.1 | cors, aiohttp, web-security, http-headers, cross-origin | A skill for implementing Cross-Origin Resource Sharing (CORS) support in aiohttp web applications using aiohttp-cors... |
| 13 | aiohttp-jinja2-1-6-0 | aiohttp-jinja2 | 1.6.0 | aiohttp, jinja2, templating, web-framework, async | Jinja2 template renderer for aiohttp.web applications providing decorator-based rendering, context processors, URL... |
| 14 | aiohttp-security-0-5-0 | aiohttp-security | 0.5.0 | aiohttp, authentication, authorization, identity-policy, permission | Authentication and authorization toolkit for aiohttp.web applications providing identity policies (cookies, sessions,... |
| 15 | aiohttp-session-2-12-0 | aiohttp-session | 2.12.0 | aiohttp, sessions, web, async, storage | Server-side sessions for aiohttp.web applications using aiohttp-session 2.12, providing multiple storage backends... |
| 16 | aiohttp-sse-2-2-0 | aiohttp-sse | 2.2.0 | aiohttp, server-sent-events, sse, eventsource, streaming | Python library for Server-Sent Events (SSE) support in aiohttp applications. Use when building real-time streaming... |
| 17 | aioitertools-0-13-0 | aioitertools | 0.13.0 | asyncio, python, itertools, async-iterators, generators | Async-compatible versions of itertools, builtins, and more for Python asyncio. Use when building async Python... |
| 18 | aiorwlock-1-5-1 | aiorwlock | 1.5.1 | asyncio, concurrency, synchronization, read-write-lock | Async read-write lock for Python asyncio providing concurrent reader access and exclusive writer access. Use when... |
| 19 | aiozmq-0-7-0 | aiozmq | 0.7.0 | zeromq, asyncio, rpc, messaging, distributed | Async ZeroMQ integration for Python asyncio providing transport-level APIs, stream abstraction, and RPC frameworks for... |
| 20 | alpinejs-3-15-11 | alpinejs | 3.15.11 | javascript, frontend, reactive, html, directives | A skill for building reactive user interfaces with Alpine.js 3.15, a minimal JavaScript framework that uses HTML-first... |
| 21 | argon2-25-1-0 | argon2 | 25.1.0 | password-hashing, authentication, cryptography, argon2, security | Python toolkit for password hashing and verification using the Argon2 algorithm via argon2-cffi 25.x. Use when... |
| 22 | asyncstdlib-3-14-0 | asyncstdlib | 3.14.0 | python, async, itertools, builtins, functools | Python async standard library providing async versions of builtins, itertools, functools, contextlib, heapq, and core... |
| 23 | autoloop-0-4-0 | autoloop | 0.4.0 | autonomous-agents, multi-role-loops, event-routing, preset-workflows, agent-harness | Simpler, opinionated loop harness for inspectable long-running agent workflows. Spinoff of ralph-orchestrator that... |
| 24 | axios-1-15-0 | axios | 1.15.0 | http, rest, api, fetch, ajax | A comprehensive toolkit for making HTTP requests using Axios 1.x, a promise-based HTTP client for browser and Node.js... |
| 25 | bcrypt-5-0-0 | bcrypt | 5.0.0 | password-hashing, cryptography, security, authentication, key-derivation | A skill for password hashing and key derivation using bcrypt 5.0 in Python. Use when implementing secure password... |
| 26 | boto3-1-42-89 | boto3 | 1.42.89 | aws, boto3, cloud, python, sdk | Complete toolkit for AWS SDK for Python (Boto3) 1.42.89 providing high-level resource interface and low-level client... |
| 27 | bun-1-3-12 | bun | 1.3.12 | javascript, typescript, runtime, package-manager, bundler | Complete toolkit for Bun 1.3.12 JavaScript runtime, package manager, bundler, and test runner. Use when building... |
| 28 | caddy-2-11-2 | caddy | 2.11.2 | web server, reverse proxy, HTTPS, Caddyfile, automatic SSL | Complete Caddy 2.11.2 web server toolkit covering Caddyfile configuration, JSON API, CLI commands, automatic HTTPS with... |
| 29 | caveman-1-5-1 | caveman | 1.5.1 | communication, token-optimization, brevity, efficiency | Ultra-compressed communication mode that cuts token usage by ~75% while maintaining full technical accuracy. Supports... |
| 30 | cffi-2-0-0 | cffi | 2.0.0 | cffi, c-integration, ffi, foreign-function-interface, python-c-bindings | Python C Foreign Function Interface for calling C libraries from Python |
| 31 | changelog-1-1-0 | changelog | 1.1.0 | changelog, documentation, versioning, semver, release-notes | A skill for creating and maintaining changelogs following the Keep a Changelog specification v1.1.0, providing... |
| 32 | chart-js-4-5-1 | chart-js | 4.5.1 | charts, canvas, data-visualization, javascript, html5 | Complete toolkit for Chart.js 4.5.1, the most popular open-source JavaScript charting library using HTML5 Canvas... |
| 33 | chonkie-1-6-2 | chonkie | 1.6.2 | text-chunking, rag, nlp, embeddings, vector-databases | A skill for using Chonkie 1.6.2, a lightweight Rust-based text chunking library for RAG pipelines providing 10+... |
| 34 | chonkie-1-6-4 | chonkie | 1.6.4 | text-chunking, rag, nlp, embeddings, vector-databases | Lightweight text chunking library for fast, efficient RAG pipelines. Provides 12+ chunkers (token, sentence, recursive,... |
| 35 | coding-guidelines-0-1-0 | coding-guidelines | 0.1.0 | behavioral-guidelines, code-quality, simplicity, llm-best-practices | Behavioral guidelines to reduce common LLM coding mistakes including |
| 36 | crun-1-27-0 | crun | 1.27.0 | oci-runtime, containers, podman, checkpointing, criu | Lightweight OCI container runtime written in C for running Linux containers with low memory footprint and high... |
| 37 | cryptography-46-0-0 | cryptography | 46.0.0 | cryptography, encryption, hashing, asymmetric, symmetric | Comprehensive toolkit for Python cryptographic operations using the cryptography library. Use when implementing... |
| 38 | curl-8-19-0 | curl | 8.19.0 | HTTP client, FTP, URL transfer, libcurl, CLI tool | Complete toolkit for curl 8.19.0 CLI tool and libcurl C library covering command-line usage, URL syntax,... |
| 39 | cython-3-2-4 | cython | 3.2.4 | python, compiler, c-extension, performance, optimization | A skill for using Cython 3.2.4, an optimizing Python compiler that makes |
| 40 | d3-7-9-0 | d3 | 7.9.0 | JavaScript, visualization, SVG, Canvas, data-visualization | Complete toolkit for D3.js 7.9.0, the JavaScript library for bespoke data-driven documents providing SVG and... |
| 41 | daisyui-5-5-0 | daisyui | 5.5.0 | tailwindcss, daisyui, ui-components, theming, css-framework | A skill for using DaisyUI 5.5, a component library for Tailwind CSS 4 that provides semantic class names for common UI... |
| 42 | dayjs-1-11-0 | dayjs | 1.11.0 | date, time, parsing, formatting, manipulation | Complete toolkit for date and time manipulation using Day.js 1.11, a minimalist 2kB library with Moment.js-compatible... |
| 43 | deno-2-7-0 | deno | 2.7.0 | javascript, typescript, runtime, web-server, cli-tools | A comprehensive toolkit for the Deno 2.x JavaScript/TypeScript runtime, |
| 44 | docker-docs-2026-04-16 | docker-docs | 2026-04-16 | containers, docker-engine, docker-desktop, docker-compose, dockerfile | Comprehensive reference for Docker platform including Docker Engine, |
| 45 | duckdb-1-5-2 | duckdb | 1.5.2 | analytics, olap, embedded-database, sql, data-science | High-performance analytical SQL database with support for nested types, vectorized execution, and seamless integration... |
| 46 | esbuild-0-28-0 | esbuild | 0.28.0 | javascript, bundler, typescript, jsx, css | Complete toolkit for esbuild v0.28 JavaScript bundler providing CLI, JavaScript API, and Go API access for bundling,... |
| 47 | gh-2-91-0 | gh | 2.91.0 | github, cli, devops, automation, ci-cd | GitHub CLI v2.91.0 for managing repositories, pull requests, issues, releases, workflows, codespaces, and more from the... |
| 48 | git | git | 2.54.0 | git, version-control, conventional-commits, keep-a-changelog, semver | Complete Git 2.54.0 toolkit covering version control workflows, Conventional Commits v1.0.0, Keep a Changelog message... |
| 49 | haproxy-3-3-0 | haproxy | 3.3.0 | load balancing, reverse proxy, SSL termination, high availability, HTTP proxy | Complete HAProxy 3.3.0 toolkit for load balancing, reverse proxying, |
| 50 | htm-3-1-0 | htm | 3.1.0 | jsx-alternative, tagged-templates, preact, react, virtual-dom | A skill for using htm 3.1, a tagged template syntax library that provides JSX-like markup in plain JavaScript without... |
| 51 | htmx-2-0-0 | htmx | 2.0.0 | htmx, html, ajax, web-development, frontend | A skill for building interactive web applications with htmx 2.x, a JavaScript library that allows accessing modern... |
| 52 | htmx-4-0-0 | htmx | 4.0.0 | htmx, hypermedia, ajax, html-attributes, server-driven-ui | A skill for building interactive web applications with htmx 4.0, a JavaScript library that provides HTML attributes for... |
| 53 | jinja2-3-1-6 | jinja2 | 3.1.6 | templating, html, python, jinja, web | Complete toolkit for Jinja2 v3.1.6 templating engine covering template design, Python API integration, custom... |
| 54 | jq-1-8-1 | jq | 1.8.1 | json, cli, data-processing, transformation, shell | Complete toolkit for jq 1.8.1, the lightweight and flexible command-line JSON processor. Use when parsing,... |
| 55 | jsonpath-rfc-9535-1-0-0 | jsonpath-rfc | 1.0.0 | JSON, query-language, data-selection, extraction, IETF-standard | Complete reference for JSONPath RFC 9535, the IETF Standards Track specification defining a string syntax for selecting... |
| 56 | lingua-py-2-2-0 | lingua-py | 2.2.0 | nlp, language-detection, text-processing, multilingual, natural-language-processing | Accurate natural language detection library for Python supporting 75 languages with high accuracy on short text and... |
| 57 | llama-cpp-1-0-0 | llama-cpp | 1.0.0 | llm, inference, gguf, quantization, cuda | C/C++ LLM inference library providing GGUF model support, quantization, GPU acceleration (CUDA/Metal/HIP/Vulkan/SYCL),... |
| 58 | lodash-4-18-1 | lodash | 4.18.1 | javascript, utility-library, data-manipulation, functional-programming, browser-compatibility | Complete toolkit for Lodash 4.18 utility library providing 300+ helper functions for arrays, collections, objects,... |
| 59 | logfire-4-32-1 | logfire | 4.32.1 | observability, tracing, opentelemetry, logging, metrics | Production-grade AI observability platform built on OpenTelemetry by the Pydantic team. Native SDKs for Python,... |
| 60 | matplotlib-3-10-8 | matplotlib | 3.10.8 | plotting, visualization, charts, graphs, data-visualization | Comprehensive toolkit for Matplotlib 3.10.8, the Python plotting library for creating static, animated, and interactive... |
| 61 | mcp-2025-11-25 | mcp | 2025-11-25 | mcp, model-context-protocol, llm, ai-integration, json-rpc | Model Context Protocol (MCP) version 2025-11-25 specification covering client-host-server architecture, JSON-RPC... |
| 62 | mem0-1-0-11 | mem0 | 1.0.11 | memory, llm, ai-agents, vector-search, langchain | A skill for using Mem0 v1.0.11, a universal self-improving memory layer for LLM applications that enables persistent... |
| 63 | mempalace-3-3-0 | mempalace | 3.3.0 | ai-memory, local-rag, chromadb, knowledge-graph, mcp | Local AI memory system that mines projects and conversations into a searchable palace using ChromaDB for vector search... |
| 64 | mermaid-11-14-0 | mermaid | 11.14.0 | diagramming, visualization, charts, flowcharts, sequence-diagrams | JavaScript-based diagramming and charting tool that generates diagrams from Markdown-inspired text definitions.... |
| 65 | networkx-3-6-1 | networkx | 3.6.1 | graph-theory, network-analysis, complex-networks, centrality, community-detection | A comprehensive toolkit for NetworkX 3.6.1, the Python package for creating, manipulating, and studying complex... |
| 66 | networkxternal-0-3-0 | networkxternal | 0.3.0 | graph, database, networkx, sqlite, postgresql | NetworkX-compatible interface for external memory MultiDiGraphs persisted in databases (SQLite, PostgreSQL, MySQL,... |
| 67 | nextjs-16-2-3 | nextjs | 16.2.3 | react, nextjs, ssr, ssg, fullstack | A skill for building production-ready React applications with Next.js 16.2.3, providing App Router and Pages Router... |
| 68 | nginx-1-30-0 | nginx | 1.30.0 | HTTP server, reverse proxy, load balancer, SSL/TLS, caching | Complete toolkit for Nginx 1.30.0 high-performance HTTP server, reverse proxy, and load balancer covering configuration... |
| 69 | nltk-3-9-2 | nltk | 3.9.2 | nlp, natural-language-processing, python, text-processing, wordnet | Complete toolkit for Natural Language Processing with NLTK 3.9.2, covering tokenization, stemming, lemmatization, POS... |
| 70 | nodejs-24-14-0 | nodejs | 24.14.0 | nodejs, javascript, runtime, server-side, async | Complete Node.js 24.14 runtime toolkit covering core modules, async programming, HTTP servers, file system operations,... |
| 71 | nuitka-4-0-8 | nuitka | 4.0.8 | python, compiler, c-extension, standalone, onefile | Python compiler that translates Python code to C and native executables. Use when compiling Python applications for... |
| 72 | numba-0-65-0 | numba | 0.65.0 | jit, compiler, llvm, numba, numpy | Just-in-time compiler for Python that translates numerical and array-oriented code into optimized machine code using... |
| 73 | numeral-2-0-6 | numeral | 2.0.6 | javascript, number-formatting, currency, localization | A JavaScript library for formatting and manipulating numbers. Use when formatting currency, percentages, bytes, time... |
| 74 | numkong-7-6-0 | numkong | 7.6.0 | vector-similarity, simd, mixed-precision, dot-product, distance-metrics | Ultra-fast mixed-precision vector similarity and distance library with |
| 75 | numpy-2-4-4 | numpy | 2.4.4 | numpy, arrays, scientific-computing, linear-algebra, data-science | Complete toolkit for NumPy 2.4.4, the fundamental package for scientific computing with Python, providing powerful... |
| 76 | oat-0-6-0 | oat | 0.6.0 | ui-library, css-framework, semantic-html, zero-dependency, webcomponents | Ultra-lightweight semantic UI component library with zero dependencies (~8KB). Use when building web applications with... |
| 77 | obscura-0-1-0 | obscura | 0.1.0 | headless-browser, web-scraping, rust, cdp, puppeteer | Lightweight headless browser engine written in Rust for web scraping and AI agent automation. Runs real JavaScript via... |
| 78 | openai-2-31-0 | openai | 2.31.0 | openai, llm, ai, chat-completions, responses-api | Python SDK for OpenAI API v2.31 providing type-safe access to Responses API, Chat Completions, embeddings, audio... |
| 79 | opentelemetry-1-55-0 | opentelemetry | 1.55.0 | distributed-tracing, metrics, logging, observability, OTLP | Complete OpenTelemetry 1.55.0 specification toolkit for implementing distributed tracing, metrics collection, and... |
| 80 | opentelemetry-collector-1-56-0 | opentelemetry-collector | 1.56.0 | opentelemetry, collector, observability, telemetry, tracing | Complete toolkit for OpenTelemetry Collector v1.56.0 covering configuration, deployment patterns (agent, gateway,... |
| 81 | opentelemetry-python-1-41-0 | opentelemetry-python | 1.41.0 | opentelemetry, observability, tracing, metrics, logging | Complete OpenTelemetry Python v1.41.0 toolkit for distributed tracing, metrics collection, and log management with... |
| 82 | pacote-21-5-0 | pacote | 21.5.0 | npm, packages, npx, download, extract | Use pacote 21.5 via npx to inspect, download, and extract npm packages without installing them first. Supports registry... |
| 83 | paramiko-4-0-0 | paramiko | 4.0.0 | ssh, sshv2, sftp, remote-execution, file-transfer | Complete toolkit for Paramiko 4.0.0, a pure-Python SSHv2 protocol implementation providing both client and server... |
| 84 | payloadcms-3-82-1 | payloadcms | 3.82.1 | cms, headless-cms, content-management, nextjs, typescript | Complete toolkit for Payload CMS v3.82.1 headless CMS development including collections, fields, access control,... |
| 85 | payloadcms-blank-3-82-1 | payloadcms-blank | 3.82.1 | cms, payload, nextjs, mongodb, headless-cms | Minimal Payload CMS 3.82.1 starter template providing a clean foundation for building custom headless CMS applications... |
| 86 | payloadcms-ecommerce-3-82-1 | payloadcms-ecommerce | 3.82.1 | payloadcms, ecommerce, commerce, stripe, payments | Complete guide for Payload CMS ecommerce template v3.82.1 providing production-ready online store with products,... |
| 87 | payloadcms-website-3-82-1 | payloadcms-website | 3.82.1 | cms, headless-cms, website-template, nextjs, typescript | Complete guide for Payload CMS website template v3.82.1 providing production-ready starter for content-driven websites,... |
| 88 | pi-mono-0-66-1 | pi-mono | 0.66.1 | ai-coding-agent, terminal-harness, extensions, tui, session-management | Complete implementation guide for pi-mono monorepo architecture covering provider abstraction, agent runtime, terminal... |
| 89 | picocss-2-1-1 | picocss | 2.1.1 | css-framework, semantic-html, responsive-design, light-dark-mode, minimal-css | A skill for using Pico CSS v2.1, a minimalist CSS framework that styles semantic HTML elements elegantly by default... |
| 90 | pinecone-router-7-5-0 | pinecone-router | 7.5.0 | alpinejs, router, spa, client-side-routing, single-page-application | A comprehensive toolkit for building client-side routing in Alpine.js applications using Pinecone Router v7.5,... |
| 91 | plan | plan | 0.1.0 | planning, workflow, task-management, read-only | Read-only exploration mode for safe code analysis. Restricts tools to read-only operations, extracts numbered steps... |
| 92 | podman-5-8-1 | podman | 5.8.1 | containers, daemonless, rootless, oci, pods | Comprehensive toolkit for Podman 5.8.1, a daemonless container engine providing Docker-compatible CLI for managing... |
| 93 | podman-compose-1-5-0 | podman-compose | 1.5.0 | podman, compose, containers, orchestration, devops | Orchestrates multi-container applications using Compose specification files with Podman backend. Use when deploying... |
| 94 | podman-py-5-8-0 | podman-py | 5.8.0 | podman, containers, python, docker-alternative, container-management | Python client library for Podman container engine providing programmatic access to containers, images, pods, networks,... |
| 95 | pulp-3-3-0 | pulp | 3.3.0 | optimization, linear-programming, mixed-integer-programming, lp, mip | Complete toolkit for PuLP 3.3.0, a Python linear and mixed-integer programming (MIP) modeler that generates MPS/LP/JSON... |
| 96 | python-scrypt-0-9-4 | python-scrypt | 0.9.4 | scrypt, password-hashing, key-derivation, cryptography, pbkdf | Python toolkit for scrypt-based key derivation and password hashing. Use when implementing secure password storage,... |
| 97 | pywebview-6-2-0 | pywebview | 6.2.0 | python, gui, webview, desktop, cross-platform | Cross-platform wrapper around native webview components that lets Python applications display HTML content in a native... |
| 98 | pyzmq-27-1-0 | pyzmq | 27.1.0 | zeromq, zmq, messaging, networking, sockets | Complete toolkit for Python bindings to ZeroMQ (pyzmq 27.x) covering socket types, messaging patterns, async/await... |
| 99 | quickjs-2025-09-13 | quickjs | 2025-09-13 | javascript, engine, es2023, c-api, embedding | Small and fast JavaScript engine supporting ES2023 with C API for embedding, qjs REPL interpreter, and qjsc bytecode... |
| 100 | qwen3-embedding-1-0-0 | qwen3-embedding | 1.0.0 | embedding, semantic-search, retrieval, multilingual, reranking | Complete toolkit for Qwen3 Embedding models (0.6B, 4B, 8B) and Qwen3 |
| 101 | qwen3-reranker-1-0-0 | qwen3-reranker | 1.0.0 | reranking, text-ranking, retrieval, cross-encoder, multilingual | Comprehensive toolkit for Qwen3 Reranker models (0.6B, 4B, 8B) — state-of-the-art cross-encoder text reranking with... |
| 102 | qwen3-vl-embedding-0-1-0 | qwen3-vl-embedding | 0.1.0 | embedding, multimodal, vision-language, retrieval, semantic-search | Complete toolkit for Qwen3-VL-Embedding 0.1.0 multimodal embedding models (2B and 8B) supporting text, images,... |
| 103 | qwen3-vl-reranker-1-0-0 | qwen3-vl-reranker | 1.0.0 | reranker, multimodal, retrieval, qwen, cross-encoder | Complete toolkit for Qwen3-VL-Reranker (2B and 8B) multimodal reranking models that score relevance of text, image,... |
| 104 | ralph-orchestrator-2-9-2 | ralph-orchestrator | 2.9.2 | ai-orchestration, ralph-wiggum, autonomous-agents, hat-system, event-driven | Hat-based orchestration framework that keeps AI agents in a loop until the task is done. Supports Claude Code, Kiro,... |
| 105 | redis-om-python-1-1-0 | redis-om-python | 1.1.0 | redis, orm, object-mapping, pydantic, redi-search | A skill for using Redis OM Python v1.1, an object mapping library that |
| 106 | redis-py-7-4-0 | redis-py | 7.4.0 | redis, database, key-value-store, caching, async | Comprehensive Python client for Redis database and key-value store. Use when building Python applications requiring... |
| 107 | rqlite-9-4-0 | rqlite | 9.4.0 | database, distributed-systems, sqlite, raft, high-availability | Comprehensive toolkit for rqlite 9.4, a lightweight distributed relational database built on SQLite with Raft... |
| 108 | rsync-3-4-1 | rsync | 3.4.1 | file-transfer, backup, mirroring, sync, daemon | Complete toolkit for rsync 3.4.1, the fast and versatile file-copying tool using delta-transfer algorithm. Use when... |
| 109 | ruff-0-4-10 | ruff | 0.4.10 | python, linter, formatter, code-quality, flake8 | A skill for using Ruff 0.4.10, an extremely fast Python linter and code formatter written in Rust that replaces Flake8... |
| 110 | rustfs-1-0-0-alpha-93 | rustfs | 1.0.0-alpha.93 | object-storage, s3, swift, distributed-systems, observability | High-performance distributed object storage system with S3-compatible API, OpenStack Swift support, and comprehensive... |
| 111 | scikit-learn-1-8-0 | scikit-learn | 1.8.0 | machine-learning, classification, regression, clustering, pipelines | Complete scikit-learn 1.8 toolkit for machine learning covering supervised and unsupervised algorithms, pipelines,... |
| 112 | scipy-1-17-1 | scipy | 1.17.1 | scipy, scientific-computing, optimization, integration, statistics | Complete SciPy 1.17 toolkit for scientific computing covering optimization, integration, interpolation, eigenvalue... |
| 113 | semver-2-0-0 | semver | 2.0.0 | versioning, semver, semantic-versioning, releases, dependency-management | Implement and validate Semantic Versioning 2.0.0 to manage software version numbers, determine compatibility, compare... |
| 114 | sentence-transformers-5-4-1 | sentence-transformers | 5.4.1 | embeddings, semantic-search, reranking, nlp, sentence-embeddings | Comprehensive toolkit for computing text embeddings, semantic search, and reranking using Sentence Transformers v5.4.1.... |
| 115 | solid-meta-0-29-0 | solid-meta | 0.29.0 | solidjs, meta-tags, document-head, ssr, seo | Manages document head tags in SolidJS applications with @solidjs/meta v0.29, providing asynchronous SSR-ready Document... |
| 116 | solid-router-0-16-0 | solid-router | 0.16.0 | solidjs, router, spa, routing, ssg | The universal router for SolidJS providing fine-grained reactivity for route navigation with support for history-based,... |
| 117 | solid-start-1-3-0 | solid-start | 1.3.0 | solidjs, fullstack, ssr, ssg, csr | Fullstack framework for SolidJS providing SSR, SSG, API routes, file-based routing, and server functions. Use when... |
| 118 | solidjs-1-9-12 | solidjs | 1.9.12 | solidjs, reactivity, signals, jsx, fine-grained | A comprehensive toolkit for building reactive user interfaces with SolidJS 1.x, a declarative JavaScript framework... |
| 119 | spacy-3-8-14 | spacy | 3.8.14 | nlp, natural-language-processing, text-analysis, machine-learning, python | Industrial-strength NLP library for Python providing tokenization, named entity recognition, dependency parsing, text... |
| 120 | spec-kit-0-6-1 | spec-kit | 0.6.1 | specification-driven-development, sdd, ai-assisted-development, project-management, workflow-automation | A skill for implementing Spec-Driven Development (SDD) using GitHub's Spec Kit v0.6.1 toolkit, enabling... |
| 121 | sqlalchemy-2-0-49 | sqlalchemy | 2.0.49 | database, orm, sql, python, postgresql | Complete SQLAlchemy 2.0 toolkit for database operations, ORM mapping, and SQL expression construction. Use when... |
| 122 | sqlite-3-53-0 | sqlite | 3.53.0 | sqlite, database, sql, json, fts | Complete toolkit for SQLite 3.53 covering all official documentation topics including SQL queries, C API integration,... |
| 123 | stanza-1-11-1 | stanza | 1.11.1 | nlp, natural-language-processing, multilingual, tokenization, pos-tagging | Stanford NLP Group's official Python NLP library for 80+ languages providing tokenization, POS tagging, lemmatization,... |
| 124 | stringzilla-4-6-0 | stringzilla | 4.6.0 | simd, string-processing, search, hashing, sorting | High-performance SIMD-accelerated string library for search, hashing, sorting, and fuzzy matching in... |
| 125 | tailwindcss-4-2-4 | tailwindcss | 4.2.4 | css, tailwind, styling, frontend, utility-first | A skill for using Tailwind CSS v4.2, a utility-first CSS framework with CSS-based configuration via @theme, OKLCH color... |
| 126 | tailwindcss-browser-4-2-0 | tailwindcss-browser | 4.2.0 | css, tailwind, browser, prototyping, no-build | A skill for using Tailwind CSS v4.2 browser build (@tailwindcss/browser) that enables in-browser Tailwind compilation... |
| 127 | tea-0-14-0 | tea | 0.14.0 | gitea, cli, git, devops, ci-cd | Official CLI for Gitea servers. Manage issues, pull requests, releases, milestones, organizations, repositories,... |
| 128 | textblob-0-20-0 | textblob | 0.20.0 | nlp, text-processing, sentiment-analysis, pos-tagging, tokenization | Python library for simplified natural language processing providing part-of-speech tagging, noun phrase extraction,... |
| 129 | tinycc-0-9-27 | tinycc | 0.9.27 | c-compiler, code-generation, dynamic-compilation, x86, arm | Complete toolkit for TinyCC 0.9.27, a small hyper-fast C compiler that generates native x86/x86_64/ARM code directly... |
| 130 | tinypy-1-1-0 | tinypy | 1.1.0 | python, vm, embedding, scripting, minimal | A minimalist Python implementation in ~64k of code featuring a fully bootstrapped parser and bytecode compiler written... |
| 131 | tokenizers-0-22-3 | tokenizers | 0.22.3 | nlp, tokenization, rust, python, transformers | Fast state-of-the-art tokenizers library for NLP written in Rust with |
| 132 | transformers-5-5-4 | transformers | 5.5.4 | nlp, machine-learning, deep-learning, pytorch, huggingface | Complete toolkit for Hugging Face Transformers 5.5.4 providing state-of-the-art pretrained models for NLP, computer... |
| 133 | ty-0-0-29 | ty | 0.0.29 | python, type-checking, static-analysis, language-server, mypy-alternative | A skill for using ty 0.0.29, an extremely fast Python type checker and language server written in Rust that is 10x-100x... |
| 134 | tzip | tzip | 0.4.0 | token-prune, efficiency, guidelines | Lightweight token-pruning communication mode that drops filler and hedging while keeping full sentences and... |
| 135 | upx-5-1-1 | upx | 5.1.1 | compression, executable-packer, distribution, size-optimization, cross-platform | A skill for using UPX (Ultimate Packer for eXecutables) v5.1.1 to compress and decompress executable files across... |
| 136 | usearch-2-24-0 | usearch | 2.24.0 | vector-search, hnsw, similarity-search, approximate-nearest-neighbors, embedding-search | High-performance single-file similarity search and clustering engine for vectors supporting HNSW algorithm with... |
| 137 | usearch-2-25-1 | usearch | 2.25.1 | vector-search, ann, hnsw, similarity-search, clustering | High-performance single-file similarity search and clustering engine for vectors using HNSW algorithm with user-defined... |
| 138 | uv-0-11-6 | uv | 0.11.6 | python, package-management, dependency-resolution, virtual-environments, pip-replacement | A skill for using uv 0.11.6, an extremely fast Python package and project manager written in Rust that replaces pip,... |
| 139 | write-skill | write-skill | 0.7.2 | skill-writing, skill-generation, meta-skill, automation | Generate fine-grained agent skills from user requirements, creating complete spec-compliant markdown files that work... |
| 140 | yq-4-53-2 | yq | 4.53.2 | yaml, json, xml, ini, csv | A skill for using yq v4.x, a lightweight and portable command-line YAML, JSON, XML, INI, Properties, CSV/TSV, HCL,... |
| 141 | zeromq-wiki-3-2-0 | zeromq-wiki | 3.2.0 | zeromq, messaging, distributed-systems, networking, sockets | A comprehensive toolkit for ZeroMQ (ØMQ) messaging library covering socket patterns, protocols, architecture, and best... |
| 142 | zeromq-zguide-3-2-0 | zeromq-zguide | 3.2.0 | zeromq, zmq, messaging, sockets, distributed-systems | Complete ZeroMQ ZGuide 3.2 toolkit covering messaging patterns, socket types, reliability mechanisms, and distributed... |

## Statistics

- **Total Skills**: 142
