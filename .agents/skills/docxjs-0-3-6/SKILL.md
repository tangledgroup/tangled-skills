---
name: docxjs-0-3-6
description: Renders DOCX documents into semantic HTML in the browser using JavaScript. Use when converting Word documents to HTML preview, building document viewers, or rendering .docx files client-side with jszip dependency.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - docxjs
  - docx-preview
  - docx
  - word
  - browser
  - html-renderer
  - javascript
category: web-framework
external_references:
  - https://github.com/VolodymyrBaydalka/docxjs/tree/0.3.6
---

# docxjs 0.3.6

## Overview

docxjs (published on npm as `docx-preview`) is a JavaScript library that renders Microsoft Word `.docx` documents into HTML in the browser. It preserves HTML semantic structure rather than rasterizing to canvas (unlike Google Docs approach). The library uses [JSZip](https://stuk.github.io/jszip/) to unpack the DOCX package and renders each component as HTML elements.

Architecture: `renderAsync()` internally calls `parseAsync()` to load the DOCX into a `WordDocument` object, then `renderDocument()` to render it into a DOM container. The stable public API is `renderAsync`; internal parsing/rendering may change between versions.

## When to Use

- Rendering `.docx` documents as HTML previews in web applications
- Building document viewer components that need semantic HTML output
- Client-side DOCX-to-HTML conversion without server processing
- Embedding Word document previews in dashboards, CMS, or collaboration tools
- Generating HTML from DOCX for email templates or rich text editors

## Installation

```bash
npm install docx-preview
```

**Dependency:** `jszip` (>= 3.0.0) is required and must be loaded separately.

### CDN Usage

```html
<!-- Load JSZip first, then docxjs -->
<script src="https://unpkg.com/jszip/dist/jszip.min.js"></script>
<script src="https://unpkg.com/docx-preview/dist/docx-preview.min.js"></script>
```

### Module Usage

```javascript
import * as DocxPreview from 'docx-preview';
// or
import { renderAsync } from 'docx-preview';
```

## Quick Start

```html
<div id="container"></div>

<script src="https://unpkg.com/jszip/dist/jszip.min.js"></script>
<script src="https://unpkg.com/docx-preview/dist/docx-preview.min.js"></script>
<script>
  const docData = new Blob([/* DOCX binary data */]);

  DocxPreview.renderAsync(docData, document.getElementById("container"))
    .then(() => console.log("DOCX rendered successfully"));
</script>
```

## Options

The `Options` interface controls rendering behavior. All options have defaults listed below.

```typescript
interface Options {
  className?: string;        // Default: "docx" — CSS class prefix for generated elements
  inWrapper?: boolean;       // Default: true — wrap document content in a wrapper div
  hideWrapperOnPrint?: boolean; // Default: false — hide wrapper styles when printing
  ignoreWidth?: boolean;     // Default: false — disable page width rendering
  ignoreHeight?: boolean;    // Default: false — disable page height rendering
  ignoreFonts?: boolean;     // Default: false — skip font-face CSS rules
  breakPages?: boolean;      // Default: true — enable page breaks at <w:br w:type="page"/>
  debug?: boolean;           // Default: false — enable verbose console logging
  experimental?: boolean;    // Default: false — enable experimental features (tab stops)
  trimXmlDeclaration?: boolean; // Default: true — strip XML declarations before parsing
  renderHeaders?: boolean;   // Default: true — render header parts
  renderFooters?: boolean;   // Default: true — render footer parts
  renderFootnotes?: boolean; // Default: true — render footnotes
  renderEndnotes?: boolean;  // Default: true — render endnotes
  ignoreLastRenderedPageBreak?: boolean; // Default: true — skip <w:lastRenderedPageBreak/> elements
  useBase64URL?: boolean;    // Default: false — use base64 URLs instead of URL.createObjectURL for images/fonts
  renderChanges?: boolean;   // Default: false — [experimental] render tracked changes (insertions/deletions)
  renderComments?: boolean;  // Default: false — [experimental] render document comments
  renderAltChunks?: boolean; // Default: true — render alternate HTML chunks embedded in DOCX
}
```

### Options Notes

- **`ignoreLastRenderedPageBreak`**: By default `true`. Set to `false` if the source DOCX uses MS Word's `<w:lastRenderedPageBreak/>` elements for page breaks.
- **`useBase64URL`**: Required when rendering in contexts where `URL.createObjectURL` is unavailable (e.g., Web Workers). Increases memory usage.
- **`experimental`**: Enables tab stops calculation. Other experimental features are controlled by their own flags (`renderChanges`, `renderComments`).
- **`renderHeaders` / `renderFooters`**: Each section can have different headers/footers; they render at the appropriate position within each page group.

## Core API

### renderAsync

Renders a DOCX document directly into a DOM container.

```typescript
function renderAsync(
  data: Blob | ArrayBuffer | Uint8Array,
  bodyContainer: HTMLElement,
  styleContainer?: HTMLElement | null,
  options?: Partial<Options>
): Promise<WordDocument>;
```

**Parameters:**
- `data` — The DOCX file as `Blob`, `ArrayBuffer`, or `Uint8Array`. Any type supported by `JSZip.loadAsync`.
- `bodyContainer` — DOM element where document content is rendered.
- `styleContainer` — Optional DOM element for styles, numbering definitions, and fonts. Defaults to `bodyContainer`.
- `options` — Rendering options (see Options section above).

**Returns:** `Promise<WordDocument>` — the parsed document object for further inspection or modification.

### parseAsync

Parses a DOCX file into an internal `WordDocument` object without rendering.

```typescript
function parseAsync(
  data: Blob | ArrayBuffer | Uint8Array,
  options?: Partial<Options>
): Promise<WordDocument>;
```

Use this when you need to inspect or modify the document before rendering.

### renderDocument

Renders a pre-parsed `WordDocument` into a DOM container.

```typescript
function renderDocument(
  wordDocument: WordDocument,
  bodyContainer: HTMLElement,
  styleContainer?: HTMLElement | null,
  options?: Partial<Options>
): Promise<void>;
```

Combining `parseAsync` + `renderDocument` gives the same result as `renderAsync`, but allows intermediate processing of the `WordDocument` object.

## WordDocument API

The `WordDocument` type represents the parsed DOCX structure. Key members:

```typescript
class WordDocument {
  rels: Relationship[];           // Top-level relationships
  parts: Part[];                  // All document parts
  partsMap: Record<string, Part>; // Parts indexed by path
  documentPart: DocumentPart;     // Main document content
  fontTablePart: FontTablePart;   // Font definitions
  numberingPart: NumberingPart;   // List numbering definitions
  stylesPart: StylesPart;         // Document styles
  footnotesPart: FootnotesPart;   // Footnotes
  endnotesPart: EndnotesPart;     // Endnotes
  themePart: ThemePart;           // Theme data
  corePropsPart: CorePropsPart;   // Core properties (title, author, etc.)
  extendedPropsPart: ExtendedPropsPart;
  settingsPart: SettingsPart;     // Document settings
  commentsPart: CommentsPart;     // Tracked changes / comments
  commentsExtendedPart: CommentsExtendedPart;
}
```

### WordDocument Methods

```typescript
// Save the document back to a new DOCX file
save(type?: "blob" | "arraybuffer" | "uint8array"): Promise<Blob | ArrayBuffer | Uint8Array>;

// Load a document-embedded image by relationship ID
loadDocumentImage(id: string, part?: Part): Promise<string>; // returns data URL

// Load a numbering (bullet) image by ID
loadNumberingImage(id: string): Promise<string>;

// Load a font by ID and obfuscation key
loadFont(id: string, key: string): Promise<string | null>;

// Load an embedded HTML altChunk
loadAltChunk(id: string, part?: Part): Promise<string>;

// Find a part by relationship ID
findPartByRelId(id: string, basePart?: Part): Part | null;

// Resolve a path from a relationship ID within a part
getPathById(part: Part, id: string): string | null;
```

## Supported Features

| Feature | Status | Notes |
|---------|--------|-------|
| Text (paragraphs, runs, styles) | Full | Including bold, italic, underline, font size/color |
| Tables | Full | With borders and cell styling |
| Images | Full | Inline and embedded; supports PNG, JPEG, GIF, SVG, TIFF |
| Headers / Footers | Full | Per-section headers and footers |
| Footnotes / Endnotes | Full | Rendered inline at position |
| Page Breaks | Partial | Manual (`<w:br w:type="page"/>`) and `<w:lastRenderedPageBreak/>` |
| Numbering (lists) | Partial | Bulleted and numbered lists |
| Bookmarks | Partial | Anchors within document |
| Comments | Experimental | Requires `renderComments: true` |
| Tracked Changes | Experimental | Requires `renderChanges: true` |
| AltChunks (embedded HTML) | Full | Requires `renderAltChunks: true` (default) |
| Line spacing / Indentation | Partial | Basic support |
| Borders | Partial | Paragraph and cell borders |
| Themes | Partial | Color/font scheme |
| Custom/Core Properties | Read-only | Accessible via `corePropsPart` / `extendedPropsPart` |

## Limitations

- **No Table of Contents**: TOC fields (`{TOC}`) are not supported. There is no efficient way to extract a table of contents from the DOCX structure.
- **No Thumbnails**: The library renders to HTML, not images. Thumbnail generation must be done externally (see `demo/thumbnail.example.js` for a workaround).
- **No TOC Field Rendering**: Per [OOXML spec](http://officeopenxml.com/WPtableOfContents.php), TOC fields are not parsed.
- **Stability Warning**: Only `renderAsync` is guaranteed stable. Internal parsing and rendering implementations may change between minor versions.
- **Realtime Page Breaking**: Not implemented — requires expensive size recalculation on each insertion. Use manual page breaks or MS Word's `<w:lastRenderedPageBreak/>` for best results.

## Page Breaking

The library supports three types of page breaks:

1. **Manual page breaks** (`<w:br w:type="page"/>`) — rendered when `breakPages: true` (default)
2. **Last-rendered page breaks** (`<w:lastRenderedPageBreak/>`) — inserted by MS Word; requires `ignoreLastRenderedPageBreak: false`
3. **Section/page setting changes** — e.g., portrait to landscape transition within a document

For reliable page breaks, prefer inserting manual breaks in the source DOCX. If using documents from MS Word, set `ignoreLastRenderedPageBreak: false` and ensure the document was saved with last-rendered break points.

## TypeScript Support

Type definitions are included:

```typescript
import type { Options, WordDocument } from 'docx-preview';
```

The `WordDocument` type is currently typed as `any` (stub). For full type safety, inspect the `WordDocument` members listed in the API section above.

## Development & Building

From source:

```bash
git clone https://github.com/VolodymyrBaydalka/docxjs.git
cd docxjs && git checkout 0.3.6
npm install
npm run build       # development build
npm run build-prod  # minified production build
```

Output files are in `dist/`:
- `docx-preview.js` — development bundle
- `docx-preview.min.js` — minified UMD bundle
- `docx-preview.mjs` — ES module
- `docx-preview.min.mjs` — minified ES module
- `docx-preview.d.ts` — TypeScript declarations

When submitting PRs, **do not** include `dist/` contents.
