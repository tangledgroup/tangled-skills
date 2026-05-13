# Output Devices

## Contents
- Selecting a Device
- Raster Image Devices
  - PNG Devices
  - JPEG Devices
  - TIFF Devices
  - PNM Devices
- Vector (High-Level) Devices
  - pdfwrite
  - ps2write / eps2write
  - txtwrite
  - docxwrite
  - xpswrite
- Per-Page Output Files
- Resolution and Anti-Aliasing
- Common Raster Options

## Selecting a Device

Use `-sDEVICE=name` to select an output device. List available devices with `gs -h`. At the interactive prompt, type `devicenames ==`.

Default device is usually a display device. For batch processing, always specify a device explicitly.

```bash
gs -sDEVICE=png16m -o output.png input.pdf
```

## Raster Image Devices

Raster devices render pages to bitmap images. All raster devices share common options for resolution and anti-aliasing.

### PNG Devices

PNG is the recommended format for high-quality raster output — lossless compression, full color, and transparency support.

| Device | Description |
|--------|-------------|
| `png16m` | 24-bit RGB color (recommended for color) |
| `pnggray` | 8-bit grayscale |
| `png256` | 8-bit indexed color |
| `png16` | 4-bit indexed color |
| `pngmono` | 1-bit black and white |
| `pngmonod` | 1-bit B&W with error diffusion from 8-bit grayscale |
| `png16malpha` | 32-bit RGBA with transparency |
| `pngalpha` | 32-bit RGBA with transparency, anti-aliasing enabled by default |

**PNG options:**

| Option | Description |
|--------|-------------|
| `-dDownScaleFactor=N` | Render at higher internal resolution, downscale by integer N (≤8) |
| `-dMinFeatureSize=N` | Expand isolated pixels (0-4, default 1), for `pngmonod` only |
| `-dBackgroundColor=16#RRGGBB` | Set background color in alpha devices (default `16#ffffff`) |

**Example — high-quality downscaling:**

```bash
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r600 -dDownScaleFactor=3 \
   -o tiger.png examples/tiger.eps
```

This renders internally at 600 DPI then downscale to 200 DPI output.

### JPEG Devices

JPEG is suitable for continuous-tone photographic images, not line art or text-heavy pages.

| Device | Description |
|--------|-------------|
| `jpeg` | Full-color JPEG (RGB) |
| `jpeggray` | Grayscale JPEG |

**JPEG options:**

| Option | Description |
|--------|-------------|
| `-dJPEGQ=N` | Quality 0-100 (default 75) — IJG quality scale |
| `-dQFactor=F` | Adobe QFactor 0.0-1.0 (alternative to JPEGQ) |

### TIFF Devices

TIFF supports multiple color depths and compression modes.

**Color TIFF devices:**

| Device | Description |
|--------|-------------|
| `tiff24nc` | 24-bit RGB, uncompressed |
| `tiff32nc` | 32-bit CMYK, uncompressed |
| `tiffgray` | 8-bit grayscale, uncompressed |
| `tiffsep` | CMYK + spot color separations (multiple output files) |

**Black-and-white TIFF devices (with compression):**

| Device | Compression |
|--------|-------------|
| `tiffg3` | G3 fax encoding with EOLs |
| `tiffg32d` | 2-D G3 fax encoding |
| `tiffg4` | G4 fax encoding |
| `tifflzw` | LZW compression |
| `tiffpack` | PackBits compression |

**Scaled TIFF devices (render at high resolution, downscale):**

| Device | Description |
|--------|-------------|
| `tiffscaled` | 1-bit B&W with error diffusion downscaling |
| `tiffscaled4` | 4-bit CMYK with error diffusion downscaling |
| `tiffscaled8` | 8-bit grayscale, no error diffusion |
| `tiffscaled24` | 24-bit RGB, no error diffusion |
| `tiffscaled32` | 32-bit CMYK, no error diffusion |

**TIFF options:**

| Option | Description |
|--------|-------------|
| `-dDownScaleFactor=N` | Downscale factor for tiffscaled devices |
| `-sCompression=name` | `none`, `crle`, `g3`, `g4`, `lzw`, `pack` |
| `-dMaxStripSize=N` | Max strip size in bytes (default 8192) |
| `-dUseBigTIFF=true` | Enable BigTIFF format for large files |
| `-sPostRenderProfile=path` | ICC profile for post-rendering color transform |

### PNM Devices

Simple uncompressed formats useful for testing or piping to external converters.

| Device | Description |
|--------|-------------|
| `ppm` / `ppmraw` | Portable pixmap (RGB) |
| `pgm` / `pgmraw` | Portable graymap (grayscale) |
| `pbm` / `pbmraw` | Portable bitmap (1-bit B&W) |
| `pnm` / `pnmraw` | Portable anymap |

## Vector (High-Level) Devices

Vector devices reassemble graphics primitives into high-level page description rather than rendering to bitmap. Output is visually equivalent but structurally different from input.

### pdfwrite

Converts any supported input format to PDF. This creates a new PDF — it does not modify the original. Annotations, bookmarks, and comments may not survive conversion.

```bash
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -dPDFSETTINGS=/printer \
   -sOutputFile=output.pdf input.ps
```

Key controls: `-dPDFSETTINGS` presets, distiller parameters, color conversion strategy, font embedding. See [PDF Features](reference/03-pdf-features.md) for details.

### ps2write / eps2write

Convert to PostScript Level 2 (`ps2write`) or Encapsulated PostScript (`eps2write`).

```bash
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=ps2write \
   -sOutputFile=output.ps input.pdf
```

### txtwrite

Extract text as Unicode. Does not preserve layout precisely — use for content extraction, not formatting.

```bash
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=txtwrite \
   -dTextFormat=3 \
   -sOutputFile=output.txt input.pdf
```

| TextFormat | Description |
|------------|-------------|
| `0` | XML-escaped Unicode with position/font metadata (developer use) |
| `1` | XML with block detection (approximate MuPDF-style layout) |
| `2` | UCS-2 text approximating page layout |
| `3` | UTF-8 text approximating page layout (default) |
| `4` | Internal format with extra information |

### docxwrite

Create DOCX files containing the text from the original document. Rotated text is placed into textboxes. Heuristics group glyphs into words, lines, and paragraphs.

```bash
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=docxwrite \
   -sOutputFile=output.docx input.pdf
```

### xpswrite

Output in Microsoft XML Paper Specification (Open XML Paper / ECMA-388) format.

```bash
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=xpswrite \
   -sOutputFile=output.xps input.pdf
```

## Per-Page Output Files

Use `%d` template in the output filename to produce one file per page. The format follows C `printf` conventions:

```bash
-sOutputFile='page-%03d.png'    # page-001.png, page-002.png, ...
-sOutputFile='doc_%04d.jpg'     # doc_0001.jpg, doc_0002.jpg, ...
```

On Windows command line, double the `%`: `-sOutputFile=page%%03d.png`.

## Resolution and Anti-Aliasing

### Resolution

Set output DPI with `-r`:

```bash
-r300          # 300×300 DPI
-r300x200      # 300 horizontal, 200 vertical DPI
```

Default is typically 72 DPI. Higher values produce larger files but sharper text and graphics.

### Anti-Aliasing

Enable subsample anti-aliasing separately for text and graphics:

```bash
-dTextAlphaBits=4 -dGraphicsAlphaBits=4
```

Values: `1` (off), `2`, or `4`. Value `4` gives optimum quality but slower rendering. These options are incompatible with vector output devices.

## Common Raster Options

The standard trio for batch rasterization:

```bash
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=<device> -o output.<ext> input.<pdl>
```

- `-dSAFER` — Security restrictions (recommended for untrusted input)
- `-dBATCH` — Exit after processing files
- `-dNOPAUSE` — No pause between pages
- `-sDEVICE=` — Select output device
- `-o` — Shorthand for OutputFile + BATCH + NOPAUSE
