# Implementation Details

## Application Architecture

Jina Reader is a multi-threaded Node.js application (Node >= 22) built on Koa. It renders web pages using headless Chrome and extracts text content using numerous techniques. PDF parsing uses PDF.js, and MS Office documents are processed through LibreOffice.

The single codebase behind `r.jina.ai` deploys directly to production on every commit to the main branch.

## URL-to-Markdown Pipeline

Given a URL, Reader determines the content type and selects the appropriate processing path:

- **Web pages (HTML/xHTML)** — Fetched and rendered using headless Chrome via Puppeteer. Advanced options allow CSS-selector-based filtering, custom JavaScript execution, and proxy configuration.
- **PDFs** — Parsed using PDF.js to extract text content as markdown and optionally render each page as an image.
- **MS Office documents** — Converted to PDF/HTML using LibreOffice first, then processed through the PDF or HTML pipeline.
- **Images** — Captioned using a vision language model (VLM) for text descriptions. Not exactly OCR — provides semantic understanding rather than character-level transcription.

## URL-to-HTML Engines

Reader supports multiple engines for rendering web pages to HTML:

- **Browser** — The most used engine. Uses headless Chrome through Puppeteer, providing the most accurate rendering with full JavaScript execution. Essential for modern web pages and SPAs.
- **CURL** — Lightweight engine using `curl-impersonate` to fetch raw HTML without JavaScript execution. Includes a simulated cookie layer for basic cookie-based redirection handling.
- **CF-Browser-Rendering** — Uses Cloudflare's Browser Rendering REST API. Strict rate limits apply; meant for testing and fallback purposes only.
- **Auto** — The default mode. Reader intelligently combines Curl and Browser engines depending on content type and requirements.

## HTML-to-Markdown Profiles

Multiple profiles exist for converting HTML to markdown:

- **@mozilla/readability** — Automatically applied to clean HTML before markdown conversion. Provides a clean, readable version of the HTML content.
- **Rule-based engine** — Custom implementation inspired by the `turndown` library with custom rules and plugins for HTML-to-markdown conversion.
- **ReaderLM v2** — Experimental engine using a specifically trained small language model to convert HTML to markdown.
- **ReaderLM v3 / VLM** — Future/WIP engine that uses a vision language model to convert webpage screenshots to markdown.

## Key Dependencies

The project relies on several key libraries:

- **Puppeteer** — Headless Chrome browser automation for rendering web pages with JavaScript execution.
- **PDF.js** — Mozilla's PDF parsing and rendering library for extracting text from PDF documents.
- **@mozilla/readability** — Content extraction library that cleans HTML to its most readable form.
- **linkedom** — Fast DOM implementation for HTML parsing and manipulation in Node.js.
- **puppeteer + LibreOffice** — MS Office document conversion pipeline.
- **tiktoken** — Token counting for LLM-compatible content sizing.
- **mathml-to-latex** — MathML to LaTeX conversion for preserving mathematical notation.
- **svg2png-wasm** — SVG to PNG conversion via WebAssembly.
- **franc** — Language detection for processed content.
- **robots-parser** — robots.txt compliance checking.

## Abuse Alleviation (SaaS)

Several mechanisms protect the service:

- **Request filtering** — Block requests targeting suspicious addresses.
- **Request throttling** — Capped concurrent requests per page.
- **Anonymous user protection** — Temporarily block websites for anonymous users when excessive requests are detected from a single page.
- **Excessive HTML nodes/depth** — Fallback to HTML-to-text instead of markdown conversion to prevent resource exhaustion.

## Progressive Clustering Tiers

The service architecture scales across three tiers:

- **Stage 0** — Fully stateless: no caching, no rate limiting, no persistence.
- **Stage 1** — S3-like object storage for caching, no rate limiting.
- **Stage 2** — MongoDB storage plus S3-like object storage. MongoDB indexes the cached objects, enabling rate limiting. This is the production SaaS version.

## Deployment Architecture

The SaaS version deploys as a Docker image on GCP Cloud Run with the following infrastructure:

- **MongoDB Atlas** — Metadata indexing and rate limiting.
- **Google Cloud Storage** — Cache data storage (MinIO-compatible).
- **Private VPC peering** — Internal services including billing, `jina-vlm`, and `readerlm-v2`.
- **Multi-region deployment** — US cluster across 3 regions (us-central1, us-east1, us-west1) and EU cluster in europe-west1.

Due to high resource requirements of headless Chrome and LibreOffice, serverless platforms with auto-scaling are recommended for deployment.

## Dockerfile Overview

The Docker image is built on Node 24 base and installs:

- Google Chrome Stable (amd64) or Chromium (arm64)
- LibreOffice for MS Office document conversion
- CJK and emoji font packages for proper text rendering
- The application runs as a non-root `jina` user

Local development requires Docker Compose with MongoDB and MinIO services, plus Node.js for the application.

## Vendor-Provided Features

Some capabilities rely on external vendors:

- **Proxy** — Built-in proxy provider for fetching content using alternative IPs (ThorData, BrightData).
- **SERP** — External search engine results providers (Serper, ThorData) power `s.jina.ai`.
- **VLM** — Vision language model for image captioning. Currently uses Gemini-2.5-flash-lite but can be switched to any model with similar capabilities.
