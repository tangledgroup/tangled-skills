# Build and Dependencies

## Contents
- Build System
- Required Dependencies
- Optional Dependencies
- CMake Configuration Options
- Font Backends
- Platform Notes

---

## Build System

Poppler uses CMake 3.28+ with C++23 (C17 for core). The build produces:
- `libpoppler` — Core PDF library
- `libpoppler-cpp` — C++ frontend wrapper
- `libpoppler-glib` — glib/GObject frontend (optional)
- `libpoppler-qt5` — Qt5 frontend (optional)
- `libpoppler-qt6` — Qt6 frontend (optional)
- CLI utilities (optional, in `utils/`)

### Basic Build

```bash
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
sudo make install
```

---

## Required Dependencies

| Library | Minimum Version | Purpose |
|---------|----------------|---------|
| freetype | 2.13 | Font rendering |
| fontconfig | 2.15 | Font discovery (Linux) |
| zlib | — | Flate stream decompression |

---

## Optional Dependencies

| Library | Minimum Version | CMake Flag | Purpose |
|---------|----------------|------------|---------|
| cairo | 1.18.0 | built-in | Raster rendering backend |
| libjpeg | — | `ENABLE_DCTDECODER=libjpeg` (default) | JPEG/DCT stream decoding |
| libopenjpeg2 | — | `ENABLE_LIBOPENJPEG=openjpeg2` (default) | JPEG2000/JPX stream decoding |
| libpng | — | built-in | PNG image support |
| libtiff | 4.5 | `ENABLE_LIBTIFF=ON` (default) | TIFF output for pdfimages/pdftocairo |
| nss3 | 3.98 | `ENABLE_NSS3=ON` (default) | Cryptographic signature verification |
| gpgme | 1.19 | `ENABLE_GPGME=ON` (default) | GPG-based cryptographic support |
| lcms2 | 2.14 | `ENABLE_LCMS=ON` (default) | ICC color management |
| libcurl | 8.5 | `ENABLE_LIBCURL=ON` (default) | HTTP/HTTPS resource loading |
| boost | 1.83 | `ENABLE_BOOST=ON` (default) | Splash backend performance optimization |
| glib | 2.80 | `ENABLE_GLIB=ON` (default) | glib/GObject frontend |
| gtk+3 | 3.24 | built-in | GTK test programs |
| Qt5 | 5.15 | `ENABLE_QT5=ON` (default) | Qt5 frontend |
| Qt6 | 6.4 | `ENABLE_QT6=ON` (default) | Qt6 frontend |
| gobject-introspection | 1.80 | `ENABLE_GOBJECT_INTROSPECTION=ON` (default) | GI typelib generation |
| gtk-doc | — | `ENABLE_GTK_DOC=OFF` (default) | glib API documentation generation |

### DCT Decoder Options

```bash
# Use libjpeg (recommended, default)
-DENABLE_DCTDECODER=libjpeg

# Use internal unmaintained decoder (removed July 2026)
-DENABLE_DCTDECODER=UnmaintainedWillBeRemovedInJuly2026

# No DCT decoder
-DENABLE_DCTDECODER=none
```

### JPX Decoder Options

```bash
# Use libopenjpeg2 (recommended, default)
-DENABLE_LIBOPENJPEG=openjpeg2

# Use internal unmaintained decoder (removed July 2026)
-DENABLE_LIBOPENJPEG=UnmaintainedWillBeRemovedInJuly2026

# No JPX decoder
-DENABLE_LIBOPENJPEG=none
```

---

## CMake Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `ENABLE_UTILS` | ON | Build command-line utilities |
| `ENABLE_CPP` | ON | Build C++ wrapper |
| `ENABLE_GLIB` | ON | Build glib wrapper |
| `ENABLE_QT5` | ON | Build Qt5 wrapper |
| `ENABLE_QT6` | ON | Build Qt6 wrapper |
| `ENABLE_GOBJECT_INTROSPECTION` | ON | Generate GObject introspection data |
| `ENABLE_GTK_DOC` | OFF | Generate glib API documentation |
| `ENABLE_LCMS` | ON | LCMS color management |
| `ENABLE_LIBCURL` | ON | libcurl HTTP support |
| `ENABLE_NSS3` | ON | NSS cryptographic backend |
| `ENABLE_GPGME` | ON | GPG cryptographic backend |
| `ENABLE_PGP_SIGNATURES` | OFF | Enable PGP signatures in GPG backend |
| `ENABLE_LIBTIFF` | ON | TIFF output support |
| `ENABLE_BOOST` | ON | Boost for Splash performance |
| `ENABLE_ZLIB_UNCOMPRESS` | OFF | Use zlib for flate (not fully safe) |
| `BUILD_SHARED_LIBS` | ON | Build as shared library (OFF = static) |
| `INSTALL_GLIB_DEMO` | OFF | Install glib demo program |
| `EXTRA_WARN` | OFF | Enable extra compiler warnings |
| `BUILD_GTK_TESTS` | ON | Build GTK test programs |
| `BUILD_QT5_TESTS` | ON | Build Qt5 test programs |
| `BUILD_QT6_TESTS` | ON | Build Qt6 test programs |
| `BUILD_CPP_TESTS` | ON | Build C++ test programs |
| `BUILD_MANUAL_TESTS` | ON | Build manual test programs |
| `ENABLE_UNSTABLE_API_ABI_HEADERS` | OFF | Install unstable xpdf headers |
| `TESTDATADIR` | `../test` | Path to poppler test data repository |

### Minimal Build (C++ only, no frontends)

```bash
cmake .. \
  -DENABLE_GLIB=OFF \
  -DENABLE_QT5=OFF \
  -DENABLE_QT6=OFF \
  -DENABLE_UTILS=OFF \
  -DENABLE_BOOST=OFF \
  -DENABLE_NSS3=OFF \
  -DENABLE_GPGME=OFF
```

### Full Build with All Features

```bash
cmake .. \
  -DENABLE_UTILS=ON \
  -DENABLE_CPP=ON \
  -DENABLE_GLIB=ON \
  -DENABLE_QT5=ON \
  -DENABLE_QT6=ON \
  -DENABLE_LCMS=ON \
  -DENABLE_LIBCURL=ON \
  -DENABLE_NSS3=ON \
  -DENABLE_GPGME=ON \
  -DENABLE_LIBTIFF=ON \
  -DENABLE_BOOST=ON
```

---

## Font Backends

The `FONT_CONFIGURATION` option selects the font discovery backend:

| Value | Platform | Description |
|-------|----------|-------------|
| `fontconfig` | Linux (default) | Use fontconfig for font discovery |
| `win32` | Windows (default) | Use Windows GDI font enumeration |
| `android` | Android (default) | Use Android asset manager |
| `generic` | Any | No platform-specific font code |

---

## Platform Notes

### Linux
- Default font backend: fontconfig
- Install development packages for dependencies (libfreetype-dev, libfontconfig1-dev, libjpeg-dev, libpng-dev, libopenjp2-7-dev, libtiff-dev, libnss3-dev, libgpgmepp-dev, liblcms2-dev, libcurl4-openssl-dev, libboost-dev)

### macOS
- CI tested on macOS 14, 15, and 26
- Homebrew provides most dependencies
- fontconfig backend works with homebrew's fontconfig

### Windows
- MSVC build supported
- Default font backend: win32
- `ENABLE_RELOCATABLE=ON` by default (don't hardcode library path)
- CI tested via Appveyor

### Android
- Default font backend: android
- Built via KDE Android docker images in CI

### Embedded / Minimal
- Disable all optional frontends and backends for minimal footprint
- Core library with freetype + zlib is the minimum viable build
