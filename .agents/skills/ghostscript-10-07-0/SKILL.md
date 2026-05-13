---
name: ghostscript-10-07-0
description: >-
  Interpreter for PostScript, PDF, PCL, XPS page description languages with raster and vector output devices.
  Converts between document formats (PDF↔PostScript↔images), compresses PDFs, extracts text, renders pages to PNG/JPEG/TIFF,
  performs OCR on scanned documents, and manages color profiles via ICC. Use when converting PDF/PostScript/PCL/XPS
  files to images or other formats, rasterizing pages at specific DPI, compressing or optimizing PDFs, extracting
  text from documents, integrating Ghostscript via C/Python/C#/Java APIs, or building print-processing pipelines.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - ghostscript
  - ghostpdl
  - pdf
  - postscript
  - document-conversion
  - rasterization
  - pcl
  - xps
category: cli-tool
external_references:
  - https://ghostscript.com/index.html
  - https://github.com/ArtifexSoftware/ghostpdl/tree/ghostpdl-10.07.0
  - https://ghostscript.readthedocs.io/en/latest/
---

# Ghostscript 10.07.0

## Overview

Ghostscript is an interpreter for the PostScript® language and PDF files, with additional interpreters for PCL, PXL, and XPS via the GhostPDL framework. Written in C, it provides a graphics library and page description language interpreters that render to dozens of output devices — raster image formats (PNG, JPEG, TIFF, PNM), vector formats (PDF, PostScript, EPS, XPS, DOCX), printer drivers, and display devices.

Key capabilities:
- **Format conversion**: PDF↔PostScript, PS→EPS, any PDL→raster images
- **PDF optimization**: compression, image downscaling, font subsetting, color space conversion
- **Rasterization**: render pages to PNG/JPEG/TIFF at arbitrary DPI with anti-aliasing
- **Text extraction**: `txtwrite` device outputs Unicode text from PDF/PS/PCL/XPS
- **OCR**: convert scanned images to searchable PDF via OCR devices (Tesseract integration)
- **Color management**: ICC-based workflow with output intents, proof profiles, spot color handling
- **SDK/API**: embeddable via `gsapi` C API with Python, C#, and Java bindings

Ghostscript is available under AGPL-3.0 or commercial license from Artifex Software. It runs on Linux, macOS, Windows, and various Unix platforms.

## When to Use

- Converting PDF/PostScript/PCL/XPS files to raster images (PNG, JPEG, TIFF)
- Rasterizing individual pages at specific DPI for thumbnails or previews
- Compressing or optimizing PDF files (reducing image quality, downsampling, subsetting fonts)
- Extracting text from PDF/PostScript documents
- Converting between vector formats (PS→PDF, PDF→EPS, PDF→XPS, PDF→DOCX)
- Creating searchable PDFs from scanned images via OCR
- Integrating document processing into applications via the gsapi C API or language bindings
- Color-managed print workflows with ICC profiles and spot color separations
- Building print processors that handle multiple page description languages

## Core Concepts

### Interpreters

Ghostscript includes interpreters for multiple page description languages:
- **PostScript**: Level 1, 2, and 3 PostScript including EPS
- **PDF**: PDF 1.7 and PDF 2.0 via the GhostPDF interpreter (rewritten in C)
- **PCL/PXL**: PCL 5c/5e/XL via GhostPCL
- **XPS**: XML Paper Specification via GhostXPS

The GhostPDL framework unifies all interpreters under a single executable and shared graphics library.

### Output Devices

Ghostscript renders through "output devices" selected with `-sDEVICE=<name>`:
- **Raster devices**: `png16m`, `pnggray`, `jpeg`, `tiff24nc`, `tiffg4`, `pbmraw`, etc.
- **Vector (high-level) devices**: `pdfwrite`, `ps2write`, `eps2write`, `xpswrite`, `docxwrite`
- **Text extraction**: `txtwrite`
- **Display devices**: `display`, `x11alpha`
- **Printer drivers**: various PCL, HP Deskjet, IJS-based drivers

Devices are selected at invocation time. The default device is usually a display device.

### Rendering Model

Input is interpreted into low-level graphics primitives, which the selected device either renders to a bitmap (raster devices) or reassembles into high-level page description (vector devices). This means vector-to-vector conversion produces visually equivalent but structurally different output — annotations, bookmarks, and comments may not survive.

### Security Mode

`-dSAFER` restricts file system access and is recommended for processing untrusted documents. Combined with `-dBATCH -dNOPAUSE`, it enables non-interactive batch processing.

## Usage Examples

### Convert PDF page to PNG at 300 DPI

```bash
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r300 \
   -dTextAlphaBits=4 -dGraphicsAlphaBits=4 \
   -sOutputFile=output.png input.pdf
```

### Rasterize all pages to separate JPEG files

```bash
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=jpeg -dJPEGQ=90 -r150 \
   -sOutputFile='page-%03d.jpg' document.pdf
```

### Compress a PDF (reduce image quality and downsample)

```bash
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -dPDFSETTINGS=/ebook \
   -sOutputFile=compressed.pdf original.pdf
```

PDF settings presets: `/screen` (72 dpi), `/ebook` (150 dpi), `/printer` (300 dpi), `/prepress` (300 dpi, higher quality).

### Convert PostScript to PDF

```bash
ps2pdf input.ps
# or explicitly:
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sOutputFile=output.pdf input.ps
```

### Extract text from a PDF

```bash
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=txtwrite \
   -dTextFormat=3 \
   -sOutputFile=output.txt input.pdf
```

TextFormat values: `0` (XML-escaped Unicode with metadata), `1` (XML with block detection), `2` (UCS-2 layout approximation), `3` (UTF-8, default), `4` (internal format).

### Render specific pages only

```bash
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r200 \
   -dFirstPage=5 -dLastPage=10 \
   -sOutputFile='page-%03d.png' document.pdf
```

Or with page list syntax:

```bash
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r200 \
   -sPageList=1,3,5-10,odd \
   -sOutputFile='page-%03d.png' document.pdf
```

### Convert PDF to grayscale PNG

```bash
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pnggray -r150 \
   -dTextAlphaBits=4 -sOutputFile=figure.png figure.pdf
```

### Quick shorthand with `-o`

The `-o` option implies `-dBATCH -dNOPAUSE`:

```bash
gs -sDEVICE=jpeg -o out-%d.jpg somefile.ps
```

## Advanced Topics

**Command Line Reference**: Switches, parameters (`-d`, `-s`), environment variables, file searching → [Command Line Reference](reference/01-command-line-reference.md)

**Output Devices**: Raster devices (PNG/JPEG/TIFF/PNM), vector devices (pdfwrite/ps2write/eps2write), device options and resolution control → [Output Devices](reference/02-output-devices.md)

**PDF-Specific Features**: PDF switches, page box selection, password handling, annotations, distiller parameters, PDF compression → [PDF Features](reference/03-pdf-features.md)

**Building and Installing**: `./configure` workflow, platform-specific builds (Unix/Windows/macOS), shared library builds, source layout → [Build and Install](reference/04-build-and-install.md)

**API and Language Bindings**: gsapi C API lifecycle, Python/C#/Java bindings, display device callbacks, embedding Ghostscript in applications → [API and Bindings](reference/05-api-and-bindings.md)
