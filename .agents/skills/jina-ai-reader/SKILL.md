---
name: jina-ai-reader
description: Converts any URL to LLM-friendly markdown via r.jina.ai and searches the web with s.jina.ai, returning top results in readable format. Use when extracting clean text from web pages, PDFs, or MS Office documents for LLM context, or when grounding LLM responses with live web search results.
license: Apache-2.0
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - url-to-markdown
  - web-crawling
  - web-search
  - llm-context
  - context-engineering
category: tooling
external_references:
  - https://github.com/jina-ai/reader
---

# Jina Reader

## Overview

Jina Reader is an API-first SaaS that converts URLs of web pages, PDFs, and MS Office documents into LLM-friendly markdown. It also provides a search endpoint that returns the top 5 results with full page content already extracted. The service runs at `r.jina.ai` (read) and `s.jina.ai` (search).

## When to Use

- Converting any URL to clean markdown for LLM context or RAG pipelines
- Searching the web and getting full article content in one call
- Extracting text from PDFs hosted at arbitrary URLs
- Reading Single Page Applications (SPAs) that require JavaScript rendering
- Building agent/RAG systems that need live, readable web content

## Quick Start

Read a single URL with `curl`:

```bash
curl -sL "https://r.jina.ai/https://en.wikipedia.org/wiki/Artificial_intelligence"
```

Search the web (returns top 5 results with full content):

```bash
curl -sL "https://s.jina.ai/What%20is%20context%20engineering%3F"
```

## Advanced Topics

**Core Concepts**: Endpoints, output formats, and key terminology → [Core Concepts](reference/01-core-concepts.md)

**API Reference**: Request headers, streaming mode, JSON mode, SPA handling, and in-site search → [API Reference](reference/02-api-reference.md)

**Implementation Details**: Architecture, rendering engines, HTML-to-markdown profiles, deployment, and caching tiers → [Implementation Details](reference/03-implementation-details.md)
