---
name: web-fetch
description: Fetches web pages and converts them to clean Markdown. Delegates to the local scrapling-0-4-7 skill for all URL extraction, JS-rendered page scraping, and anti-bot bypass. Use when retrieving webpage content, converting URLs to readable text, or fetching live web data for AI context.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - meta
  - meta-skill
  - web-fetch
  - scraping
  - markdown
  - url-extraction
category: meta
---

# web-fetch 0.1.0

## Overview

Lightweight meta-skill for fetching web pages and converting them to clean Markdown. All work is delegated to the local `scrapling-0-4-7` skill.

## When to Use

- Fetching a URL's content as Markdown
- Extracting text from web pages, PDFs, or JS-rendered sites
- Converting live web data into LLM-readable context

## Usage

Load the `scrapling-0-4-7` skill and follow its instructions for all web-fetching operations. It provides:

- `scrapling <URL>` — CLI to fetch and convert any URL to Markdown
- Browser automation for JS-rendered pages
- Anti-bot stealth fetching
- PDF and MS Office document extraction

Refer to `scrapling-0-4-7` SKILL.md for full command syntax, options, and examples.
