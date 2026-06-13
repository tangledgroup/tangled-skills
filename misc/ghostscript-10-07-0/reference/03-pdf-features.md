# PDF Features

## Contents
- PDF-Specific Switches
- Page Box Selection
- Page Ranges
- Password and Encryption
- Annotations and Forms
- pdfwrite Controls
- Distiller Parameters
- PDF Compression Settings
- Color Conversion

## PDF-Specific Switches

Ghostscript provides switches specific to PDF interpretation, primarily for the GhostPDF interpreter (the C-based PDF interpreter).

### `-dPDFCACHE=N`

Controls the number of recently-used indirectly-referenced objects cached by the C PDF interpreter. Default is 200. Increasing may help with oddly-constructed PDFs that reference the same objects repeatedly.

```bash
gs -dPDFCACHE=500 -dSAFER -dBATCH -dNOPAUSE -o out.png large.pdf
```

### `-dPDFINFO`

Emit detailed information about a PDF file (fonts, spot colors, structure). Descends into Forms, Images, Type 3 fonts, and Patterns. Available with GhostPDF interpreter.

```bash
gs -dPDFINFO -dSAFER input.pdf
```

## Page Box Selection

PDF pages can define multiple bounding boxes. By default, Ghostscript uses the MediaBox. Override with:

| Switch | Description |
|--------|-------------|
| `-dUseBleedBox` | Use BleedBox — region to which page contents are clipped for production output |
| `-dUseTrimBox` | Use TrimBox — intended finished dimensions after trimming |
| `-dUseArtBox` | Use ArtBox — extent of meaningful content (often smallest box) |
| `-dUseCropBox` | Use CropBox — rectangle to which page contents are clipped |

**Example — simulate finished printed page:**

```bash
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dUseTrimBox \
   -r300 -o output.png input.pdf
```

### `-dPDFFitPage`

Scale the PDF to fit the current device page size rather than using the PDF's MediaBox. Useful for creating fixed-size thumbnails from PDFs with varying page sizes.

```bash
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -dPDFFitPage \
   -r150 -o thumbnail.png input.pdf
```

## Page Ranges

### `-dFirstPage=N` / `-dLastPage=N`

Process a contiguous range of pages:

```bash
gs -dFirstPage=5 -dLastPage=10 ...
```

PDF and XPS interpreters allow `LastPage < FirstPage` to process pages in reverse order.

### `-sPageList=spec`

Process specific pages with flexible range syntax. Ranges are comma-separated:

```bash
-sPageList=1,3,5        # Pages 1, 3, and 5
-sPageList=5-10         # Pages 5 through 10
-sPageList=1,5-10,12-   # Page 1, pages 5-10, and page 12 onwards
-sPageList=odd          # All odd-numbered pages
-sPageList=even:1-20    # Even pages within range 1-20
```

Range components:
1. Single page number: `5`
2. Range with start and end: `5-10`
3. Range from start to last page: `12-`
4. Keyword `even` or `odd`, optionally with range: `odd:1-20`

## Password and Encryption

### `-sPDFPassword=password`

Set user or owner password for encrypted PDF files. For encryption method 4 and earlier, the password is an arbitrary byte string. For method 5+, it should be UTF-8 text.

```bash
gs -sPDFPassword=secret -dSAFER -dBATCH -dNOPAUSE -sDEVICE=txtwrite \
   -sOutputFile=output.txt encrypted.pdf
```

## Annotations and Forms

### `-dShowAnnots=false`

Suppress annotations. By default, annotations are rendered.

### `/ShowAnnotTypes` array

Fine-grained control over which annotation types are drawn. Set via PostScript:

```bash
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m \
   -c "/ShowAnnotTypes [/Text /Underline] def" -f input.pdf -o output.png
```

Available types: `/Stamp`, `/Squiggly`, `/Underline`, `/Link`, `/Text`, `/Highlight`, `/Ink`, `/FreeText`, `/StrikeOut`.

### `-dShowAcroForm=false`

Don't render AcroForm (interactive form) annotations. By default, AcroForm processing is enabled to match Adobe Acrobat behavior.

## pdfwrite Controls

The `pdfwrite` device creates PDF output from any supported input format. Key controls:

### `-rresolution`

Set resolution for pattern fills and bitmap font conversion. Default internal resolution for pdfwrite is 720 DPI.

```bash
gs -sDEVICE=pdfwrite -r300 -o output.pdf input.ps
```

### `-dUNROLLFORMS`

Unroll PostScript Form resources instead of preserving them as Form XObjects. Avoids incorrect output from badly-written PostScript but produces larger files.

### `-dNoOutputFonts`

Emit all text as linework/bitmaps instead of fonts. Produces larger output that renders differently at low resolution. Use with caution.

### Font Control via Distiller Parameters

```bash
# Always outline (convert to paths) specific fonts:
gs -sDEVICE=pdfwrite -o out.pdf \
   -c "<< /AlwaysOutline [/Calibri (Comic Sans) cvn] >> setdistillerparams" \
   -f input.pdf

# Never outline specific fonts even with -dNoOutputFonts:
gs -sDEVICE=pdfwrite -dNoOutputFonts -o out.pdf \
   -c "<< /NeverOutline [/Arial cvn] >> setdistillerparams" \
   -f input.pdf
```

### `-dCompressFonts` / `-dCompressStreams`

Control compression of embedded fonts and non-page streams. Default is `true` for both. Set to `false` only for debugging.

## Distiller Parameters

Distiller parameters control the pdfwrite, ps2write, and eps2write devices. They originate from Adobe Acrobat Distiller 5 specifications.

### Setting via Command Line

```bash
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.7 -dEmbedAllFonts=true \
   -o output.pdf input.ps
```

### Setting via PostScript (required for arrays and dictionaries)

Some parameters cannot be set on the command line and require PostScript:

```bash
gs -sDEVICE=pdfwrite -o out.pdf \
   -c "<< /AlwaysEmbed [/Helvetica /Times-Roman] >> setdistillerparams" \
   -f input.ps
```

Or via a parameter file:

```bash
gs -sDEVICE=pdfwrite -o out.pdf @params.in -f input.ps
```

Where `params.in` contains:
```
<</AlwaysEmbed [/Helvetica /Times-Roman]>> setdistillerparams
```

### Key Distiller Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `CompatibilityLevel` | 1.7 | Target PDF version (1.4, 1.5, 1.6, 1.7, 2.0) |
| `EmbedAllFonts` | true | Embed all fonts in output |
| `SubsetFonts` | true | Subset embedded fonts to used glyphs only |
| `MaxSubsetPct` | 100 | Minimum glyph percentage to embed full font vs subset |
| `ColorConversionStrategy` | LeaveColorUnchanged | `RGB`, `CMYK`, `Gray`, `UseDeviceIndependentColor` |
| `AutoRotatePages` | /PageByPage | Page rotation: `/None`, `/PageByPage`, `/All` |
| `CompressPages` | true | Compress page content streams |
| `DetectBlends` | true | Detect and optimize blend modes |
| `DoThumbnails` | false | Generate thumbnail images |
| `Optimize` | false | Enable output optimization (also `-dFastWebView`) |

### Image Handling Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ColorImageDownsampleType` | /Subsample | `/Average`, `/Bicubic`, `/Subsample` |
| `ColorImageResolution` | 72 | Target resolution for color images |
| `ColorImageDownsampleThreshold` | 1.5 | Downsample only if source exceeds this × target |
| `DownsampleColorImages` | false | Enable color image downscaling |
| `GrayImageDownsampleType` | /Subsample | Grayscale image downsampling method |
| `GrayImageResolution` | 72 | Target resolution for grayscale images |
| `MonoImageResolution` | 300 | Target resolution for monochrome images |
| `ColorImageFilter` | /DCTEncode | Compression: `/DCTEncode`, `/FlateDecode`, `/JBIG2Encode` |
| `AutoFilterColorImages` | true | Auto-select best compression per image |

### Preset Profiles

| Profile | Use Case | Key Settings |
|---------|----------|-------------|
| `/screen` | Web viewing | 72 dpi images, RGB, maximum compression |
| `/ebook` | E-readers | 150 dpi images, RGB, good compression |
| `/printer` | Desktop printing | 300 dpi images, preserves color spaces |
| `/prepress` | Professional printing | 300 dpi, highest quality, prepress settings |

Apply presets with `-dPDFSETTINGS`:

```bash
gs -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook -o output.pdf input.pdf
```

## PDF Compression Settings

### Image Downscaling

Reduce image resolution within PDFs:

```bash
gs -sDEVICE=pdfwrite -o compressed.pdf \
   -c "<< /DownsampleColorImages true /ColorImageResolution 150 \
        /ColorImageDownsampleType /Bicubic >> setdistillerparams" \
   -f original.pdf
```

### `-dPDFSETTINGS` Presets

The quickest way to compress PDFs:

```bash
# Lowest quality, smallest file (72 dpi images)
gs -sDEVICE=pdfwrite -dPDFSETTINGS=/screen -o out.pdf in.pdf

# Medium quality (150 dpi images)
gs -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook -o out.pdf in.pdf

# High quality (300 dpi images)
gs -sDEVICE=pdfwrite -dPDFSETTINGS=/printer -o out.pdf in.pdf

# Highest quality (300 dpi, prepress settings)
gs -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress -o out.pdf in.pdf
```

## Color Conversion

Convert PDF color spaces using distiller parameters:

```bash
# Convert to RGB
gs -sDEVICE=pdfwrite -o rgb_output.pdf \
   -c "<< /ColorConversionStrategy /RGB >> setdistillerparams" \
   -f input.pdf

# Convert to CMYK
gs -sDEVICE=pdfwrite -o cmyk_output.pdf \
   -c "<< /ColorConversionStrategy /CMYK >> setdistillerparams" \
   -f input.pdf

# Convert to Grayscale
gs -sDEVICE=pdfwrite -o gray_output.pdf \
   -c "<< /ColorConversionStrategy /Gray >> setdistillerparams" \
   -f input.pdf
```

## `-dPrinted` and `-dPrinted=false`

Control whether PDF screen or print options are used for annotations and images:

```bash
gs -dPrinted ...        # Use "printer" options (default when OutputFile is set)
gs -dPrinted=false ...  # Use "screen" options
```

## `-dNoUserUnit`

Ignore the `UserUnit` parameter in PDF. Useful for backward compatibility or processing files with large `UserUnit` values that exceed implementation limits.
