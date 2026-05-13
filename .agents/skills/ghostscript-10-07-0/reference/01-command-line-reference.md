# Command Line Reference

## Contents
- Invocation Syntax
- General Switches
- Parameter Switches (-d and -s)
- Key Parameters by Category
- Environment Variables
- File Searching
- Pipes and Standard I/O

## Invocation Syntax

```bash
gs [options] {filename 1} ... [options] {filename N} ...
```

Options may appear anywhere on the command line and apply to all files named after them. The executable name varies by platform:

| System | Executable |
|--------|-----------|
| Linux/Unix/macOS | `gs` |
| Windows 32-bit | `gswin32.exe`, `gswin32c.exe` (console) |
| Windows 64-bit | `gswin64.exe`, `gswin64c.exe` (console) |

The `c` suffix on Windows indicates a console-based binary.

### Help

```bash
gs -h    # or gs -?
```

Shows version, available devices, search path, and supported formats.

## General Switches

### Input Control

| Switch | Description |
|--------|-------------|
| `-c "string"` | Execute a PostScript command string before processing files |
| `-f` | End of options; treat following arguments as files only |
| `-q` | Quiet mode — suppress banner and informational messages |
| `-dBATCH` | Exit after processing all files (no interactive prompt) |
| `-dNOPAUSE` | Suppress pause between pages |
| `-dSAFER` | Restrict file system and language operations for security |

### File Searching

| Switch | Description |
|--------|-------------|
| `-Ipath` | Add directory to search path (may be repeated) |
| `-sGS_LIB=path` | Set Ghostscript library search path |

### Setting Parameters

| Switch | Description |
|--------|-------------|
| `-dname=value` | Set boolean/integer parameter (`-dNOPAUSE`, `-r300`) |
| `-sname=string` | Set string parameter (`-sDEVICE=png16m`, `-sOutputFile=out.png`) |
| `-pname=PScode` | Push PostScript code onto operand stack |

### Suppress Messages

| Switch | Description |
|--------|-------------|
| `-q` | Quiet — suppress banner, file loading messages |
| `-dQUIET` | Same as `-q` |
| `-dNODISPLAY` | Don't use display device even if selected |

## Parameter Switches (-d and -s)

### `-d` Parameters (boolean/integer/float)

Boolean parameters are set with `-dName` (true) or `-dName=false` (false). Integer parameters use `-dName=N`.

### `-s` Parameters (string)

String parameters use `-sName=value`. The two most important:

- `-sDEVICE=name` — Select output device
- `-sOutputFile=filename` — Set output file path

## Key Parameters by Category

### Rendering Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `-rres` or `-rx×y` | float | Output resolution in DPI (default 72) |
| `-dTextAlphaBits=N` | int | Text anti-aliasing subsample size (1, 2, 4; default 1) |
| `-dGraphicsAlphaBits=N` | int | Graphics anti-aliasing subsample size (1, 2, 4; default 1) |
| `-dDownScaleFactor=N` | int | Downscale rendered image by integer factor (≤8) |

### Page Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `-dFirstPage=N` | int | Start rendering from page N |
| `-dLastPage=N` | int | Stop after page N |
| `-sPageList=spec` | string | Page ranges: `1,3,5-10,odd,even` |
| `-sPAPERSIZE=name` | string | Paper size: `a4`, `letter`, `legal`, etc. |
| `-dDEVICEWIDTHPOINTS=W` | float | Custom page width in points (1/72 inch) |
| `-dDEVICEHEIGHTPOINTS=H` | float | Custom page height in points |
| `-dFIXEDMEDIA` | bool | Force paper size, ignore document-specified size |

### Device and Output Selection Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `-sDEVICE=name` | string | Output device name (e.g. `png16m`, `pdfwrite`) |
| `-sOutputFile=path` | string | Output file path; use `%d` template for per-page files |
| `-o path` | string | Shorthand: sets OutputFile + BATCH + NOPAUSE |

### Interaction Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `-dBATCH` | bool | Exit after processing files |
| `-dNOPAUSE` | bool | Don't pause between pages |
| `-dNODISPLAY` | bool | Suppress display device |
| `-dNOINTERPOLATE` | bool | Disable image interpolation |

### ICC Color Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `-sDefaultGrayProfile=path` | string | ICC profile for undefined DeviceGray colors |
| `-sDefaultRGBProfile=path` | string | ICC profile for undefined DeviceRGB colors |
| `-sDefaultCMYKProfile=path` | string | ICC profile for undefined DeviceCMYK colors |
| `-sOutputICCProfile=path` | string | ICC profile for output device |
| `-dOverrideICC=true` | bool | Override embedded ICC profiles with defaults |
| `-sICCProfilesDir=path` | string | Directory to search for ICC profiles |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GS_DEVICE` | Default output device name |
| `GS_FONTPATH` | Colon-separated font search paths |
| `GS_LIB` | Colon-separated library search paths |
| `GS_OPTIONS` | Default command-line options appended to every invocation |
| `TMPDIR` / `TEMP` | Directory for temporary files |

## File Searching

Ghostscript searches for files (PostScript programs, fonts, resources) in this order:

1. Paths specified with `-I` or `-sGS_LIB`
2. `GS_LIB` environment variable
3. Compiled-in default search paths (ROM file system if `COMPILE_INITS=1`)
4. Current directory

The `%rom%` file system contains files compiled into the executable (initialization files, fonts, ICC profiles). The `%os%` prefix accesses the normal operating system file system.

## Pipes and Standard I/O

### Reading from stdin

Use `-` as a filename to read from standard input:

```bash
cat document.ps | gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -o out.png -
zcat paper.ps.gz | gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -o out.png -
```

### Writing to stdout

```bash
gs -q -sOutputFile=- -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m input.pdf > output.png
# or:
gs -sOutputFile=%stdout -q -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m input.pdf
```

When piping output, use `-q` to prevent Ghostscript's status messages from mixing with the data stream. Alternatively, redirect status to stderr:

```bash
gs -sstdout=%stderr -sOutputFile=- ...
```

### Piping to external commands

```bash
gs -sOutputFile=%pipe%lpr -dSAFER -dBATCH -dNOPAUSE -sDEVICE=epson input.ps
```
