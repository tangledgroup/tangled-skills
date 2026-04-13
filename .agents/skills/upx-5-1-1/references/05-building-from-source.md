# Building UPX from Source

This guide covers building UPX v5.1.1 from source code, including prerequisites, build options, and modifying decompression stubs.

## Prerequisites

### Required Tools

**C++ Compiler** (must fully implement C++17):
- clang-5 or newer
- gcc-8 or newer
- msvc-2019-16.11 or newer
- Older compilers may work but are unsupported

**Build System:**
- GNU make
- CMake 3.13 or better (https://cmake.org/)

### Optional Tools (for stub modification)

**Preferred method:**
- Podman or Docker (see `misc/podman/rebuild-stubs`)

**Alternative method (Linux host required):**
- Perl
- Python 2
- Older compatibility libraries
- upx-stubtools (cross-assemblers and cross-compilers)
  - Precompiled binaries: https://github.com/upx/upx-stubtools/releases

## Quick Build

### Simple Make Build

```bash
# Clone repository
git clone https://github.com/upx/upx.git
cd upx

# Initialize submodules (compression algorithms, etc.)
git submodule update --init

# Build
make

# UPX binary will be in src/upx
./src/upx --version
```

### CMake Build (Recommended)

```bash
# Clone repository with submodules
git clone --recursive https://github.com/upx/upx.git
cd upx

# Create build directory
mkdir -p build/release
cd build/release

# Configure
cmake ../..

# Build
cmake --build . --verbose

# UPX binary will be in build/release/upx
./upx --version
```

## Developer Quick Start

For development and testing with full test suite:

```bash
# 1. Create working directory
mkdir my-upx
cd my-upx

# 2. Clone UPX and test suite
git clone https://github.com/upx/upx.git
git clone https://github.com/upx/upx-testsuite.git

# 3. Initialize submodules
cd upx
git submodule update --init
# DO NOT TOUCH vendor/...
# After git merge/pull, check with "git status"
# If vendor is dirty: "git submodule update"
# If stuck: "rm -rf vendor; git submodule update --init"

# 4. Optional: Setup stub rebuilding tools
cd src/stub
wget https://github.com/upx/upx-stubtools/releases/download/v20221212/bin-upx-20221212.tar.xz
# Extract to $HOME/bin/bin-upx or $HOME/local/bin/bin-upx
# See: https://github.com/upx/upx-stubtools

# Ubuntu prerequisites for stubtools:
# dpkg --add-architecture i386
# apt-get update
# apt-get install zlib1g-dev:i386 libc6-dev:i386
# apt-get install crossbuild-essential-riscv64  # for example
# ln -s /lib/x86_64-linux-gnu/libmpfr.so.6 /lib/x86_64-linux-gnu/libmpfr.so.4

# Verify stub rebuild:
make clean
make

cd ../..

# 5. Build with CMake
mkdir -p build/debug build/release
cd build/debug

# Install GNU g++ if needed (Ubuntu 24.04 workaround)
# If using clang as default c++, may get:
# c++: error: unknown argument: '-fno-lifetime-dse'
# Solution: Install g++ so it's used when invoking "c++"

cmake ../..
cmake --build . --verbose

cd ../..

# 6. Run test suite
cd src
make run-testsuite 2>&1 | tee testsuite.log
```

## Platform-Specific Notes

### Ubuntu/Debian

```bash
# Install build dependencies
sudo apt-get install build-essential cmake git

# For stub rebuilding (optional)
sudo dpkg --add-architecture i386
sudo apt-get update
sudo apt-get install zlib1g-dev:i386 libc6-dev:i386 perl python2

# Build
cd upx
make
```

### macOS

```bash
# Install dependencies with Homebrew
brew install cmake gcc git

# For coreutils (readlink -en, sha256sum -b)
brew install coreutils
# Add to PATH: <prefix>/opt/coreutils/libexec/gnubin

# Build
cd upx
make
```

**Note:** macOS support is disabled in v4.2.0+ until compatibility with macOS 13+ is fixed. Building may still work but macOS format support will be unavailable.

### Windows

```bash
# Use MSVC 2019 16.11+ or MinGW-w64
# Install CMake from https://cmake.org/

# In Developer Command Prompt or MSYS2:
cd upx
mkdir build
cd build
cmake ..
cmake --build .
```

## Build Options

### CMake Options

```bash
# Debug build
cmake -DCMAKE_BUILD_TYPE=Debug ../..

# Release build with optimizations
cmake -DCMAKE_BUILD_TYPE=Release ../..

# Specify install prefix
cmake -DCMAKE_INSTALL_PREFIX=/usr/local ../..

# Install
cmake --install .
```

### Make Options

```bash
# Clean build
make clean

# Show verbose output
make V=1

# Parallel build (use CPU cores)
make -j$(nproc)

# Cross-compile
make CROSS_COMPILE=arm-linux-gnueabihf-
```

## Understanding the Source Structure

### Directory Layout

```
upx/
├── src/
│   ├── stub/          # Decompression stubs (assembler)
│   ├── upx.cpp        # Main UPX logic
│   ├── *.cpp          # Format handlers (win32, linux, etc.)
│   └── ...
├── vendor/            # Submodules (compression algorithms)
│   ├── nrv/           # NRV compression library
│   └── lzma/          # LZMA algorithm
├── doc/               # Documentation
├── misc/              # Miscellaneous files
│   └── podman/        # Stub rebuild with Docker/Podman
├── CMakeLists.txt     # CMake build configuration
└── Makefile           # Top-level makefile
```

### Two Main Components

1. **src/stub/** - Decompression stubs
   - Written mainly in assembler
   - "Compiled" into C header files
   - Added to each compressed executable

2. **src/** - Packer sources
   - Stub headers are #included by format handlers
   - Contains compression logic and format support

### Submodules

```bash
# Initialize submodules (first time)
git submodule update --init

# Update submodules (after pull/merge)
git submodule update

# Check submodule status
git status
# Look for changes in vendor/...

# Reset if stuck
rm -rf vendor
git submodule update --init
```

**Important:** DO NOT manually modify vendor/ contents. They are managed by git submodules.

## Rebuilding Stubs

### Using Podman/Docker (Preferred)

```bash
cd src/stub

# Use provided script
../misc/podman/rebuild-stubs

# Or manually with Docker
docker run --rm -v $(pwd):/work upx/upx-stubtools make
```

### Manual Rebuild (Linux Required)

```bash
# 1. Install upx-stubtools
wget https://github.com/upx/upx-stubtools/releases/download/v20221212/bin-upx-20221212.tar.xz
tar -xf bin-upx-20221212.tar.xz
# Extract to $HOME/bin/bin-upx

# 2. Build stubs
cd src/stub
make clean
make

# 3. Verify
cd ../..
make clean
make
```

### Stub Dependencies

Some pre-built tools require:
- i386 libz (zlib1g-dev:i386 on Ubuntu)
- libmpfr.so.4 (symlink from libmpfr.so.6 if needed)
- Cross-compilers for various architectures

## Testing

### Run Test Suite

```bash
cd src
make run-testsuite
```

**With test suite repository:**
```bash
# Clone test suite (if not already done)
git clone https://github.com/upx/upx-testsuite.git

# Run tests
make run-testsuite
```

### Manual Testing

```bash
# Test compression
./src/upx --best /bin/ls
./src/upx -t /bin/ls  # Verify integrity
./src/upx -d /bin/ls  # Decompress

# Test with various files
./src/upx --brute large_file.exe
./src/upx -l compressed_file  # List info
```

## Troubleshooting Build Issues

### C++ Compiler Errors

**Problem:** Unknown arguments or C++17 feature errors

**Solution:** Ensure compiler supports C++17:
```bash
# Check compiler version
g++ --version
# Should be gcc-8+ or clang-5+

# Specify C++17 explicitly
cmake -DCMAKE_CXX_STANDARD=17 ../..
```

### Ubuntu 24.04 Clang Issue

**Problem:** `c++: error: unknown argument: '-fno-lifetime-dse'`

**Cause:** CMake's HandleLLVMOptions.cmake adds flag that system clang doesn't support

**Solution:** Install GNU g++:
```bash
sudo apt-get install g++
# Ensure g++ is used when invoking "c++"
which c++
```

### Missing Submodule Files

**Problem:** Compression algorithm files not found

**Solution:**
```bash
git submodule update --init
# Or if stuck:
rm -rf vendor
git submodule update --init
```

### Stub Build Failures

**Problem:** Cannot rebuild stubs, missing cross-compilers

**Solution:** Use Podman/Docker method or install upx-stubtools:
```bash
# Download pre-built tools
wget https://github.com/upx/upx-stubtools/releases/download/v20221212/bin-upx-20221212.tar.xz

# Or use Docker/Podman
cd misc/podman
./rebuild-stubs
```

### macOS Build Issues

**Problem:** Missing coreutils commands (readlink -en, sha256sum -b)

**Solution:**
```bash
brew install coreutils
# Add to PATH
export PATH="/opt/homebrew/opt/coreutils/libexec/gnubin:$PATH"
```

## Installation

### System-Wide Install

```bash
# With CMake
cmake -DCMAKE_INSTALL_PREFIX=/usr/local ../..
cmake --build .
sudo cmake --install .

# With Make
make
sudo make install PREFIX=/usr/local
```

### Custom Install Location

```bash
# Install to user directory
cmake -DCMAKE_INSTALL_PREFIX=$HOME/local ../..
cmake --build .
cmake --install .

# Add to PATH
export PATH=$HOME/local/bin:$PATH
```

## Verification

After building, verify the installation:

```bash
# Check version
upx --version
# Output: UPX 5.1.1

# Test basic functionality
upx --help

# Compress and test a file
upx -k /bin/ls
upx -t /bin/ls
upx -d /bin/ls
```

## Advanced Topics

### Adding New Format Support

See the source code for examples. Key points:

- Use types LE16, LE32, BE16, BE32 for file header fields
- Use [sg]et_[bl]e(16|32) for data stream values
- Use macros for compiler-specific features
- Follow coding style (4-space indent, no tabs)
- Use throwSomeException() instead of throw SomeException()

### Modifying Compression Algorithms

Compression algorithms are in vendor/ submodules:
- **NRV:** Not publicly available (used in official builds)
- **LZMA:** Available in vendor/lzma/

**Note:** NRV is intentionally not public to prevent creation of fake/trojan UPX versions.

## Resources

- **Source Code:** https://github.com/upx/upx
- **Test Suite:** https://github.com/upx/upx-testsuite
- **Stub Tools:** https://github.com/upx/upx-stubtools
- **Documentation:** https://upx.github.io/docs/upx.html
- **Issues:** https://github.com/upx/upx/issues

## Related Reference Files

- [Common Operations](01-common-operations.md) - Basic commands and workflows
- [Format-Specific Notes](03-format-notes.md) - Platform-specific considerations
