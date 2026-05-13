# Command-Line Utilities

## Contents
- Text Extraction (pdftotext)
- Format Conversion (pdftocairo, pdftops, pdftoppm, pdftohtml)
- Metadata and Inspection (pdfinfo, pdffonts, pdfimages)
- Page Operations (pdfunite, pdfseparate)
- Embedded Files (pdfattach, pdfdetach)
- Digital Signatures (pdfsig)

---

## Text Extraction

### pdftotext

Convert PDF to plain text. Reads from stdin if input is `-`, writes to stdout if output is `-`.

```bash
pdftotext [options] input.pdf [output.txt]
```

| Option | Description |
|--------|-------------|
| `-f N` | First page to convert |
| `-l N` | Last page to convert |
| `-r DPI` | Resolution (default 72) |
| `-layout` | Preserve original physical layout |
| `-raw` | Content-stream order (column undo, not recommended for general use) |
| `-fixed W` | Fixed-pitch text with character width W (forces layout mode) |
| `-remove-hyphens mode` | `all` (default), `soft`, or `none` — controls end-of-line hyphen removal |
| `-nodiag` | Discard diagonal text (skip watermarks) |
| `-htmlmeta` | Wrap output in HTML with metadata headers |
| `-bbox` | XHTML with per-word bounding boxes |
| `-bbox-layout` | XHTML with bounding boxes in layout mode |
| `-x N -y N -W N -H N` | Crop area (top-left x,y, width, height in pixels) |

**Default behavior**: Reading order text extraction, hyphens removed. Use `-layout` when physical position matters (e.g., forms, tables).

---

## Format Conversion

### pdftocairo

Convert PDF to PNG, JPEG, TIFF, PDF, PS, EPS, SVG, or print (Windows). One format flag required.

```bash
pdftocairo [options] -<format> input.pdf [output-root]
```

| Format Flag | Output |
|-------------|--------|
| `-png` | PNG file(s) |
| `-jpeg` | JPEG file(s) |
| `-tiff` | TIFF file(s) |
| `-pdf` | PDF (re-render, useful for flattening) |
| `-ps` | PostScript |
| `-eps` | Encapsulated PostScript (single page only — use `-f` and `-l`) |
| `-svg` | SVG vector graphics |
| `-print` | Print to system printer (Windows only) |

Common options:

| Option | Description |
|--------|-------------|
| `-f N -l N` | Page range |
| `-r DPI` / `-rx W -ry H` | Resolution for raster output |
| `-scale-to W H` | Fixed output dimensions (resolution varies with page size) |
| `-singlefile` | Write only first page, no digit suffix |
| `-o` / `-e` | Odd/even pages only |
| `-x N -y N -W N -H N` | Crop area (pixels for raster, points for vector) |
| `-nocenter` | Cropped region at top-left instead of centered |
| `-jpegopt quality=Q` | JPEG quality setting |
| `-stickiness S` | EPS stickiness percentage (0-100) |
| `-sep` | Separated output for color printing |
| `-progressive` | Progressive JPEG/PNG |
| `-transparent` | Preserve transparency in raster output |
| `-antialias mode` | `none`, `force`, or `default` for antialiasing control |

For raster formats, multi-page PDFs produce `output-root-1.png`, `output-root-2.png`, etc. Vector formats produce a single file named `output-root`.

### pdftops

Convert PDF to PostScript.

```bash
pdftops [options] input.pdf [output.ps]
```

| Option | Description |
|--------|-------------|
| `-level1` / `-level1sep` | PostScript Level 1 (monochrome/separated) |
| `-level2` / `-level2sep` | PostScript Level 2 |
| `-level3` / `-level3sep` | PostScript Level 3 (default) |
| `-eps` | Encapsulated PostScript (single page, use with `-f`/`-l`) |
| `-paper size` | Paper size: `letter`, `legal`, `A3`, `A4`, `A5`, `B4`, `B5` |
| `-paperw W -paperh H` | Custom paper dimensions (inches) |
| `-origpagesizes` | Use original PDF page sizes for media box |
| `-nosplit` | Don't split pages with multiple XObjects |

### pdftoppm

Convert PDF to PPM/PGM/PNG images.

```bash
pdftoppm [options] input.pdf output-root
```

| Option | Description |
|--------|-------------|
| `-png` | Output PNG instead of PPM (default is PPM) |
| `-gray` | Grayscale output |
| `-mono` | Monochrome output |
| `-r DPI` / `-rx W -ry H` | Resolution |
| `-scale-dimension-before-rotation` | Scale before applying page rotation |
| `-f N -l N` | Page range |
| `-o` / `-e` | Odd/even pages only |

### pdftohtml

Convert PDF to HTML.

```bash
pdftohtml [options] input.pdf [output.html]
```

| Option | Description |
|--------|-------------|
| `-s` | Generate single HTML file with embedded images |
| `-c` | Generate CSS stylesheets |
| `-i` | Insert original images into HTML |
| `-dataurls` | Embed images as data: URLs |
| `-p` | Use physical layout positioning |
| `-f N -l N` | Page range |
| `-xml` | Output XML instead of HTML |

---

## Metadata and Inspection

### pdfinfo

Print PDF document information from the Info dictionary plus additional properties.

```bash
pdfinfo [options] input.pdf
```

Output includes: title, subject, keywords, author, creator, producer, creation/modification dates, page count, encryption status, print/copy permissions, page size, file size, linearization flag, PDF version, form type (AcroForm/XFA/none), and JavaScript presence.

| Option | Description |
|--------|-------------|
| `-f N -l N` | Examine specific pages (prints per-page sizes) |
| `-box` | Print page box bounding boxes (MediaBox, CropBox, BleedBox, TrimBox, ArtBox) |
| `-meta` | Print document-level metadata stream |
| `-custom` | Print custom and standard metadata |
| `-js` | Print all embedded JavaScript |
| `-struct` | Print logical structure tree |
| `-struct-text` | Print text with structure tags |
| `-url` | Print all URLs in the document |
| `-isodates` / `-rawdates` | Date output format |
| `-dests` | Print named destinations |
| `-listenc` | List available character encodings |

Only one of `-listenc`, `-meta`, `-js`, `-struct`, `-struct-text`, `-url`, `-dests` may be used at a time — they suppress the standard Info dictionary output.

### pdffonts

List fonts used in a PDF.

```bash
pdffonts [options] input.pdf
```

Output columns: name, type (Type1, TrueType, Type1C/CID, etc.), encoding, emb (embedded: yes/no), sub (subset: yes/no), uni (Unicode cmap: yes/no), object ID, and flags.

| Option | Description |
|--------|-------------|
| `-subst` | Show font substitution information |
| `-f N -l N` | Limit to page range |
| `-v` | Verbose output |

### pdfimages

List or extract images from a PDF.

```bash
pdfimages [options] input.pdf output-root
```

Without format flags, lists images in table format: page number, image number, width, height, color space, bits per component, encoding, and object ID. With a format flag, extracts images to files named `output-root-000.ext`, etc.

| Format Flag | Description |
|-------------|-------------|
| `-png` | Save as PNG |
| `-tiff` | Save as TIFF |
| `-j` | Save JPEG images in original encoding |
| `-jp2` | Save JPEG2000 images in original encoding |
| `-jbig2` | Save JBIG2 images in original encoding |
| `-ccitt` | Save CCITT images in original encoding (with ASCII 85/Hex decoding) |
| `-all` | Save all images in original encoding |
| `-opt` | Optimize output (default behavior) |

Other options:

| Option | Description |
|--------|-------------|
| `-f N -l N` | Page range |
| `-p` | Include page number in output filename |
| `-q` | Suppress status messages |
| `-csv` | Output list in CSV format |

---

## Page Operations

### pdfunite

Merge multiple PDFs into one.

```bash
pdfunite input1.pdf input2.pdf ... output.pdf
```

Pages are concatenated in the order given. Supports `-v` (verbose) and `-h`/`--help`.

### pdfseparate

Split a PDF into individual page files.

```bash
pdfseparate [options] input.pdf output-%d.pdf
```

The output pattern uses `printf`-style formatting. `%d` is replaced with the page number, `-N` pads to N digits. Example: `output-%03d.pdf` produces `output-001.pdf`, `output-002.pdf`, etc.

| Option | Description |
|--------|-------------|
| `-f N -l N` | Page range |
| `-v` | Verbose |

---

## Embedded Files

### pdfattach

Attach files to a PDF document.

```bash
pdfattach [options] input.pdf file-to-attach output.pdf
```

| Option | Description |
|--------|-------------|
| `-replace` | Replace existing attachment with same filename |

Exit codes: 0 (success), 1 (usage error), 2 (can't open PDF), 3 (can't open file to attach), 4 (can't create output file).

### pdfdetach

List or extract embedded files from a PDF.

```bash
pdfdetach [options] input.pdf
```

| Option | Description |
|--------|-------------|
| `-list` | List all embedded files |
| `-n N` | Extract file by index |
| `-u name` | Extract file by filename |
| `-o output` | Specify output filename (default: original embedded name) |

---

## Digital Signatures

### pdfsig

Verify or display information about digital signatures in PDF documents. Uses NSS for certificate validation and OCSP for revocation checking.

```bash
pdfsig [options] input.pdf
```

| Option | Description |
|--------|-------------|
| `-nssdir dir` | NSS database directory |
| `-nss-pwd password` | NSS database password |
| `-nocert` | Don't verify certificate chain |
| `-no-ocsp` | Skip OCSP revocation checking |
| `-assert-signer fpr_or_file` | Assert a specific signer fingerprint or key file |
| `-no-appearance` | Ignore signature appearance |
| `-aia` | Enable Authority Information Access |
| `-dump` | Dump raw signature data |

Exit codes: 0 (all signatures valid), 1 (invalid signature found), 2 (usage error), 3 (can't open PDF).
