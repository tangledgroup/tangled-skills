---
name: web-search
description: Meta skill that delegates web search tasks to the local duckduckgo-2026-05-08 skill. Use when performing web searches, fetching Wikipedia summaries, or gathering search results into LLM context.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - meta
  - meta-skill
  - web-search
  - search
  - meta-skill
category: meta
---

# web-search

## Overview

This is a meta skill that delegates all web search operations to the `duckduckgo-2026-05-08` skill. Always load that skill first to access DuckDuckGo's HTML and JSON search endpoints.

## When to Use

- Performing web searches from the terminal
- Fetching Wikipedia-style summaries
- Gathering search results into clean LLM context

## Usage

Load the `duckduckgo-2026-05-08` skill and follow its instructions for:

- **HTML endpoint** — full search results converted to markdown (default)
- **JSON API** — structured data with abstracts, infoboxes, and definitions (`--format json`)
