---
name: poppler-26-05-0
description: PDF rendering library providing C++, glib, Qt5, and Qt6 APIs for loading, parsing, rendering, and extracting content from PDF documents. Use when building applications that need to render PDF pages to images, extract text/images/fonts, convert PDFs to PS/SVG/PNG/JPEG/TIFF, inspect metadata, or manipulate embedded files and digital signatures.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - poppler
  - pdf
  - rendering
  - c++
  - glib
  - qt
category: library
external_references:
  - https://poppler.freedesktop.org/
  - https://gitlab.freedesktop.org/poppler/poppler/-/tree/poppler-26.05.0?ref_type=tags
---

# Poppler 26.05.0

## Overview

Poppler is a PDF rendering library based on the xpdf-3.0 code base, maintained by freedesktop.org. It provides multiple frontends (C++, glib, Qt5, Qt6) for loading, parsing, rendering, and extracting content from PDF documents. The library also ships command-line utilities for common PDF operations: text extraction, image extraction, format conversion, font inspection, metadata viewing, page splitting/merging, file attachment, and signature verification.

Written in C++23 with a C17 core, Poppler uses CMake (3.28+) as its build system. Rendering relies on cairo for raster output and splash (optional boost) for alternative backends. Required dependencies include freetype, fontconfig (Linux), libjpeg, libpng, openjpeg2, nss3, gpgme, lcms2, tiff, and zlib.

## When to Use

- Rendering PDF pages to raster images (PNG, JPEG, TIFF) or vector formats (SVG, PS, EPS)
- Extracting text from PDFs with layout preservation or raw content-stream order
- Inspecting PDF metadata, fonts, embedded files, or digital signatures
- Converting PDFs between formats (PDF↔PS, PDF→HTML, PDF→PPM)
- Splitting or merging PDF documents
- Building applications that embed PDF rendering via C++, glib, Qt5, or Qt6 APIs
- Extracting images from PDFs in their original encoded format

## Core Concepts

**Architecture**: Poppler separates the core PDF parsing/rendering engine (written in C++) from language-specific frontends. The core handles PDF object parsing, content stream interpretation, font handling, and page rendering. Frontends provide idiomatic APIs for C++, GObject/glib, Qt5, and Qt6.

**Document Loading**: All frontends follow the same pattern — load a document from file or memory data, optionally providing owner/user passwords for encrypted files. The returned document object owns pages and provides metadata access.

**Page Rendering**: Pages are rendered to images at specified resolution (DPI). The C++ `page_renderer` class configures render hints (antialiasing, text hinting), paper color, and image format before calling `render_page()`. Qt uses `Page::renderToImage()` with similar parameters.

**Text Extraction**: Text can be extracted in reading order (default), raw content-stream order (`-raw`), or physical layout mode (`-layout`). Bounding box information per word is available via `-bbox` for position-aware processing.

**Resource Management**: In the C++ API, `document::create_page()` and similar factory methods return pointers owned by the caller — delete after use. The document object itself is created via static factory methods (`load_from_file`, `load_from_data`) and deleted with `delete`.

## Quick Start Examples

### CLI: Extract text from a PDF

```bash
pdftotext input.pdf output.txt
```

### CLI: Render pages to PNG at 150 DPI

```bash
pdftocairo -png -r 150 input.pdf page
```

### CLI: Inspect PDF metadata and properties

```bash
pdfinfo input.pdf
```

### C++ API: Load and render a page

```cpp
#include <poppler-document.h>
#include <poppler-page.h>
#include <poppler-page-renderer.h>

auto *doc = poppler::document::load_from_file("input.pdf");
if (!doc) { /* handle error */ }

auto *page = doc->create_page(0);
poppler::page_renderer renderer;
renderer.set_render_hint(poppler::page_renderer::antialiasing, true);
auto img = renderer.render_page(page, 150.0, 150.0);
// img.save_to_file("output.png");

delete page;
delete doc;
```

### glib API: Load and extract text

```c
#include <poppler.h>

PopplerDocument *doc = poppler_document_new_from_file("input.pdf", NULL, NULL, &error);
if (error) { /* handle error */ }

PopplerPage *page = poppler_document_get_page(doc, 0);
const gchar *text = poppler_page_get_text(page);
g_free((gchar *)text);
poppler_page_unref(page);
g_object_unref(doc);
```

## Advanced Topics

**Command-Line Utilities**: All 13 CLI tools with usage patterns and key options → [CLI Utilities](reference/01-cli-utils.md)

**C++ API Reference**: Classes, rendering workflow, document/page operations → [C++ API](reference/02-cpp-api.md)

**glib and Qt Frontends**: GObject (glib) and Qt5/Qt6 wrapper APIs → [glib and Qt Frontends](reference/03-glib-qt-frontends.md)

**Build and Dependencies**: CMake options, required libraries, optional backends → [Build and Dependencies](reference/04-build-dependencies.md)
