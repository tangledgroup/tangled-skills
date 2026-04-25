# Installation and Building

## Package Installation

### Debian/Ubuntu
```bash
sudo apt install rsync
# For maximum features, also install:
sudo apt install libxxhash-dev libzstd-dev liblz4-dev libssl-dev \
                 libacl1-dev libattr1-dev
```

### RHEL/CentOS/Fedora
```bash
# CentOS (requires EPEL for python3-pip)
sudo yum -y install epel-release
sudo yum -y install gcc g++ gawk autoconf automake python3-pip \
                    acl libacl-devel attr libattr-devel \
                    xxhash-devel libzstd-devel lz4-devel openssl-devel
python3 -mpip install --user commonmark

# Fedora 33+
sudo dnf -y install gcc g++ gawk autoconf automake python3-pip \
                    acl libacl-devel attr libattr-devel \
                    xxhash-devel libzstd-devel lz4-devel openssl-devel
```

### macOS
```bash
brew install rsync
# Optional build dependencies:
brew install xxhash zstd lz4 openssl automake
```

### FreeBSD
```bash
sudo pkg install -y autotools python3 py37-CommonMark xxhash zstd liblz4
```

## Build from Source

### Prerequisites
- C compiler (gcc or clang)
- Optional: C++ compiler for hardware-accelerated checksums
- Modern awk (gawk or nawk)
- If building from git: autoconf, automake, python3 with cmarkgfm or commonmark

### Build Steps
```bash
git clone https://github.com/rsyncproject/rsync.git
cd rsync

# From release tarball:
./configure
make
sudo make install

# From git repo (need to generate manpages first):
./prepare-source fetchgen   # or install python3-cmarkgfm
./configure
make
sudo make install
```

### Configure Options
```bash
./configure --help    # See all available options
./configure --prefix=/usr/local   # Install location
./configure --disable-ipv6        # Disable IPv6 support
./configure --enable-maintainer-mode  # Enable xterm crash debugger
```

### Default Install Path
Default: `/usr/local/bin`

To change, use `--prefix=DIR` in configure.

## Platform-Specific Notes

### macOS (Apple Silicon)
```bash
CFLAGS="-I /opt/homebrew/include" LDFLAGS="-L /opt/homebrew/lib" ./configure
```

### HP-UX
If the bundled C compiler fails with ANSI C errors, install gcc or HP's "ANSI/C Compiler".

### IBM AIX
Append to config.h if mkstemp has largefile problems:
```c
#ifdef _LARGE_FILES
#undef HAVE_SECURE_MKSTEMP
#endif
```

### Cygwin
```bash
setup-x86_64 --quiet-mode -P make,gawk,autoconf,automake,gcc-core,python38,python38-pip
setup-x86_64 --quiet-mode -P attr,libattr-devel
setup-x86_64 --quiet-mode -P libzstd-devel
setup-x86_64 --quiet-mode -P liblz4-devel
setup-x86_64 --quiet-mode -P libssl-devel
```

## Verify Installation
```bash
rsync --version
# Should output something like:
# rsync  version 3.4.1  protocol version 32
# Copyright (C) 1996-2025 by Andrew Tridgell, Wayne Davison, and others.
```
