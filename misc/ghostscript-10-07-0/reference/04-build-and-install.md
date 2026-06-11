# Build and Install

## Contents
- Source Layout
- Unix/Linux/macOS Build
- Windows Build
- Shared Library Builds
- Installation
- Fonts
- Cross-Compilation

## Source Layout

Ghostscript source is organized in the following subdirectories:

| Directory | Contents |
|-----------|----------|
| `base/` | Graphics library C source and makefiles |
| `psi/` | PostScript interpreter C source and makefiles |
| `pcl/` | PCL/PXL interpreter C source, makefiles, fonts |
| `xps/` | XPS interpreter C source and makefiles |
| `devices/` | Output device drivers maintained by Ghostscript team |
| `contrib/` | Community-contributed output devices |
| `arch/` | Pre-defined architecture header files |
| `Resource/` | PostScript initialization, resource, and font files |
| `lib/` | PostScript utility scripts (ps2pdf, pdf2ps, etc.) |
| `doc/` | Documentation |
| `man/` | Unix man pages |
| `examples/` | Sample PostScript files |
| `iccprofiles/` | Default ICC color profiles |
| `windows/` | Visual Studio project and solution files |
| `demos/` | Language binding demo code |
| `toolbin/` | Developer tools (non-PostScript) |

Third-party library sources (jpeg, freetype, etc.) are in their own subdirectories.

## Unix/Linux/macOS Build

### Standard Configure/Make Workflow

```bash
# Extract source
tar -zxf ghostscript-10.07.0.tar.gz
cd ghostscript-10.07.0

# Configure (auto-detects system and dependencies)
./configure
# or with custom prefix:
./configure --prefix=/opt/ghostscript

# Build
make

# Install (may require root)
sudo make install
```

The default prefix is `/usr/local`, installing `gs` to `/usr/local/bin/gs`.

### Configure Options

Run `./configure --help` for a complete listing. Common options:

| Option | Description |
|--------|-------------|
| `--prefix=PATH` | Installation directory (default `/usr/local`) |
| `--disable-compile-inits` | Don't compile initialization files into executable |
| `--enable-cmm` | Enable ICC color management module |

### Building from Development Source

For git checkouts (not released tarballs), run `./autogen.sh` instead of `./configure`. It accepts the same options.

### Manual Makefile Configuration

Without `configure`, edit the platform-specific makefile:

- `base/unix-gcc.mak` — Unix with GCC
- `base/unixansi.mak` — Unix with non-GCC ANSI C compilers

Key variables to adjust:
- `MAKEFILE` — Name of the makefile itself
- Install paths (prefix, etc.)
- `GS_LIB_DEFAULT` — Default search paths for init and font files
- `DEBUG` / `TDEBUG` — Debugging options
- `FEATURE_DEVS` — Which features to include
- `DEVICE_DEVS` / `DEVICE_DEVS1-15` — Which device drivers to include

### Selecting Features and Devices

```make
# In the platform-specific makefile:
FEATURE_DEVS=$(PSD)level2.dev $(PSD)pdf.dev
DEVICE_DEVS=$(DD)png16m.dev $(DD)jpeg.dev $(DD)tiff24nc.dev
```

Features use `$(PSD)` prefix, devices use `$(DD)` prefix. Default builds include a complete feature set — only remove features for resource-constrained environments.

### Precompiled Run-Time Data

By default, initialization files are compiled into the executable (`COMPILE_INITS=1`), creating a `%rom%` file system. This makes Ghostscript self-contained and improves startup speed.

To disable: `./configure --disable-compile-inits` or set `COMPILE_INITS=0` in the makefile.

## Windows Build

### Microsoft Visual Studio

Visual Studio project files are in the `windows/` directory. Open the solution file to build.

Built libraries:
- 32-bit: `gpdll32.dll`, `gsdll32.dll`
- 64-bit: `gpdll64.dll`, `gsdll64.dll`

### Command Line Build

Use `psi/msvc.mak` with NMAKE. Edit the makefile to select features and devices, then invoke NMAKE.

### Windows Executables

| File | Description |
|------|-------------|
| `GSWIN32C.EXE` / `GSWIN64C.EXE` | Console-based Ghostscript (preferred) |
| `GSWIN32.EXE` / `GSWIN64.EXE` | Windowed Ghostscript with its own display window |
| `GSDLL32.DLL` / `GSDLL64.DLL` | Dynamic link library for embedding |

### Windows Registry

Ghostscript reads environment variables from the registry if not set:
- `HKEY_CURRENT_USER\Software\GPL Ghostscript\10.07.0`
- `HKEY_LOCAL_MACHINE\SOFTWARE\GPL Ghostscript\10.07.0`

## macOS Build

Standard Unix build applies. Alternatively, install via Homebrew or MacPorts:

```bash
brew install ghostscript
# or
sudo port install ghostscript
```

## Shared Library Builds

Ghostscript can be built as a shared library for embedding in applications:

| Platform | Library Name |
|----------|-------------|
| Linux / OpenBSD | `libgs.so`, `libgpdl.so` |
| macOS | `libgs.dylib`, `libgpdl.dylib` (versioned with symlinks) |
| Windows 32-bit | `gsdll32.dll`, `gpdll32.dll` |
| Windows 64-bit | `gsdll64.dll`, `gpdll64.dll` |

After building as a shared object, use `make soinstall` instead of `make install`.

## Installation

### Unix Install Layout

With default prefix `/usr/local`:

| Path | Contents |
|------|----------|
| `/usr/local/bin/gs` | Ghostscript executable |
| `/usr/local/share/ghostscript/10.07.0/` | Initialization files, resources |
| `/usr/local/share/ghostscript/fonts/` | Fonts (installed separately) |
| `/usr/local/lib/` | Shared libraries (if built as shared object) |
| `/usr/local/libexec/ghostscript/` | Helper scripts |

### Fonts

Fonts are installed to `{prefix}/share/ghostscript/fonts/`. Ghostscript ships with 35 URW++ Type 1 fonts (Times, Helvetica, Courier families, Symbol, ZapfDingbats).

To add custom fonts, edit the `Fontmap` file or set `GS_FONTPATH`:

```bash
export GS_FONTPATH=/usr/share/fonts/truetype/:/usr/share/fonts/type1/
```

### Linux RPM/Snap

Some distributions provide pre-built RPMs. Ghostscript also provides a snap package:

```bash
gunzip gs_10.07.0_amd64_snap.tgz
tar xvf gs_10.07.0_amd64_snap.tar
sudo snap install --devmode gs_10.07.0_amd64.snap
```

The snap requires `--devmode` because Ghostscript needs access to input files, output files, and fonts outside the sandbox.

### Utility Scripts

Ghostscript ships with convenience wrapper scripts in `lib/`:

| Script | Description |
|--------|-------------|
| `ps2pdf` | PostScript → PDF |
| `pdf2ps` | PDF → PostScript |
| `ps2epsi` | PostScript → Encapsulated PostScript |
| `pdf2dsc` | PDF → Distiller Comments format |
| `ps2ascii` | PostScript → ASCII text |
| `ps2ps` / `ps2ps2` | PostScript level conversion |

These call Ghostscript with appropriate option sets. The `ps2*` scripts work with EPS files as well.

## Cross-Compilation

Configure supports standard cross-compilation flags:

```bash
./configure --host=arm-linux-gnueabihf --prefix=/opt/arm-ghostscript
make
make install
```

## Default Paper Size

Ghostscript defaults to US letter paper. To change the installed default, edit `Resource/Init/gs_init.ps`:

```postscript
% /DEFAULTPAPERSIZE (a4) def
```

Uncomment and substitute the desired size:

```postscript
/DEFAULTPAPERSIZE (a4) def
```

On Windows and some Linux builds, the default is selected based on locale.
