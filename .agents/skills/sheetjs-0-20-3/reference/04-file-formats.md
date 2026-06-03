# File Formats

## Contents
- Supported Formats Overview
- Excel Worksheet/Workbook Formats
- Excel Text Formats
- Other Workbook/Worksheet Formats
- Common Output Formats
- Range Limits by Format
- Constellation Libraries

## Supported Formats Overview

SheetJS supports reading and writing 40+ spreadsheet file formats. Features not supported by a given format are silently omitted during write.

### Excel 2007+ XML Formats (XLSX/XLSM)
- **Read**: ✔ | **Write**: ✔
- ZIP container with XML files per Open Packaging Conventions (OPC)
- Standardized in ECMA-376 / ISO/IEC 29500
- XLSM includes macro containers

### Excel 2007+ Binary Format (XLSB BIFF12)
- **Read**: ✔ | **Write**: ✔
- Compact binary format, faster parse/write for large files

### Excel 2003 XML Format (XML "SpreadsheetML")
- **Read**: ✔ | **Write**: ✔
- XML-based format used by Excel 2003

### Excel 97-2004 (XLS BIFF8)
- **Read**: ✔ | **Write**: ✔
- Legacy binary format, widely supported

### Other Excel Legacy Formats
| Format | Read | Write |
| --- | --- | --- |
| Excel 5.0/95 (XLS BIFF5) | ✔ | ✔ |
| Excel 4.0 (XLS/XLW BIFF4) | ✔ | ✔ |
| Excel 3.0 (XLS BIFF3) | ✔ | ✔ |
| Excel 2.0/2.1 / Multiplan 4.x DOS (XLS BIFF2) | ✔ | ✔ |

### Excel Supported Text Formats
| Format | Read | Write |
| --- | --- | --- |
| Delimiter-Separated Values (CSV/TXT) | ✔ | ✔ |
| Data Interchange Format (DIF) | ✔ | ✔ |
| Symbolic Link (SYLK/SLK) | ✔ | ✔ |
| Lotus Formatted Text (PRN) | ✔ | ✔ |
| UTF-16 Unicode Text (TXT) | ✔ | ✔ |

### Other Workbook/Worksheet Formats
| Format | Read | Write |
| --- | --- | --- |
| Numbers 3.0+ / iWork 2013+ (NUMBERS) | ✔ | ✔ |
| WPS 电子表格 (ET) | ✔ | — |
| OpenDocument Spreadsheet (ODS) | ✔ | ✔ |
| Flat XML ODF (FODS) | ✔ | ✔ |
| Uniform Office Format (UOS1/UOS2) | ✔ | — |
| dBASE II/III/IV / Visual FoxPro (DBF) | ✔ | ✔ |
| Lotus 1-2-3 (WK1/WK3) | ✔ | ✔ |
| Lotus 1-2-3 (WKS/WK2/WK4/123) | ✔ | — |
| Quattro Pro (WQ1/WQ2/WB1/WB2/WB3) | ✔ | — |
| Works 1.x-3.x DOS / 2.x-5.x Windows (WKS) | ✔ | — |
| Works 6.x-9.x (XLR) | ✔ | — |
| Quattro Pro QPW | ✔ | — |

### Common Spreadsheet Output Formats
| Format | Read | Write |
| --- | --- | --- |
| HTML Tables | ✔ | ✔ |
| Rich Text Format (RTF) | ✔ | ✔ |
| Ethercalc Record Format (ETH) | ✔ | ✔ |

## Range Limits by Format

Formats with range limits are silently truncated beyond their maximum:

| Format | Last Cell | Max Cols | Max Rows |
| --- | --- | --- | --- |
| XLSX/XLSM | `XFD1048576` | 16,384 | 1,048,576 |
| XLSB BIFF12 | `XFD1048576` | 16,384 | 1,048,576 |
| NUMBERS | `ALL1000000` | 1,000 | 1,000,000 |
| Quattro Pro QPW | `IV1000000` | 256 | 1,000,000 |
| XLS BIFF8 | `IV65536` | 256 | 65,536 |
| XLS BIFF5/4/3/2 | `IV16384` | 256 | 16,384 |
| Lotus WK1/WK3/WK4 | `IV8192` | 256 | 8,192 |
| Lotus WKS | `IV2048` | 256 | 2,048 |

Excel 2003 SpreadsheetML range limits are governed by the Excel version and not enforced by the writer.

## Constellation Libraries

SheetJS includes related libraries for specialized formats:

| Library | Description | Package |
| --- | --- | --- |
| `ssf` | Number format library (ECMA-376 format codes) | `ssf` |
| `cfb` | Container file processing (OLE/ZIP) | `cfb` |
| `codepage` | Legacy text encodings for XLS and legacy formats | `codepage` / `cptable` |
| `xlsx-cli` | Node.js command-line tool for processing files | `xlsx` (bin/xlsx) |
| `dta` | Stata DTA file processor (separate package) | `@sheetjs/dta` |
| `frac` | Rational approximation library (separate package) | `fraction` |
| `crc32` | CRC32 checksum utility (separate package) | `crc-32` |

### CLI Tool (`xlsx`)

The `xlsx` command-line tool is included with the npm package:

```bash
npx xlsx --help
npx xlsx input.xlsx   # Convert to JSON
npx xlsx input.csv    # Convert CSV to XLSX
```

## Key Concepts for Format Handling

### Parser Behavior
- Parsers convert from underlying file format representation to the Common Spreadsheet Format (CSF)
- Most parsers generate formatted text (`w` property) at parse time
- Use `cellNF: true` option to preserve original number format strings
- Use `cellDates: true` option to get Date objects instead of date codes

### Writer Behavior
- Writers convert from CSF to the target file format
- Features not supported by a format are silently omitted
- XLSX/XLSM use ZIP compression; enable with `compression: true` in write options
- Formulae are always exported when present in the workbook
