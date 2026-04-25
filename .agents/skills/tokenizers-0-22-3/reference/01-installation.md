# Installation Guide

Complete installation instructions for 🤗 Tokenizers across Python, Node.js, and Rust platforms.

## Python Installation

### Quick Install (Recommended)

```bash
pip install tokenizers
```

This installs the latest stable release with pre-built wheels for most platforms.

### Virtual Environment Setup

Always use a virtual environment for Python projects:

```bash
# Create virtual environment
python -m venv venv

# Activate on Unix/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate

# Install tokenizers
pip install tokenizers
```

### Installation from Source

Building from source requires Rust toolchain:

```bash
# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Update Rust
rustup update

# Clone repository
git clone https://github.com/huggingface/tokenizers
cd tokenizers/bindings/python

# Install in editable mode
pip install -e .
```

**Build time**: Expect 5-10 minutes for first build from source.

### System Requirements

| Platform | Python Version | Notes |
|----------|---------------|-------|
| Linux (x86_64) | 3.8+ | Wheels available |
| Linux (aarch64) | 3.8+ | Wheels available |
| macOS (Intel) | 3.8+ | Wheels available |
| macOS (Apple Silicon) | 3.8+ | Wheels available |
| Windows (x86_64) | 3.8+ | Wheels available |

### Verifying Installation

```python
import tokenizers
print(tokenizers.__version__)  # Should print version string

# Test basic functionality
from tokenizers import Tokenizer
from tokenizers.models import BPE

tokenizer = Tokenizer(BPE())
print("Tokenizer created successfully!")
```

## Node.js Installation

### Quick Install

```bash
npm install @huggingface/tokenizers
```

### TypeScript Support

Type definitions are included:

```typescript
import { Tokenizer, BPE } from '@huggingface/tokenizers';

const tokenizer = new Tokenizer(new BPE());
```

### Building from Source

```bash
# Clone repository
git clone https://github.com/huggingface/tokenizers
cd tokenizers/bindings/node

# Install dependencies
npm install

# Build
npm run build

# Test
npm test
```

## Rust Installation

### Add to Cargo.toml

```toml
[dependencies]
tokenizers = "0.22"
```

### Optional Features

```toml
[dependencies]
tokenizers = { version = "0.22", features = ["http"] }
```

Available features:
- `http`: Enable HTTP downloading for pretrained tokenizers
- `ondemand`: Load models on-demand from Hugging Face Hub

### Minimal Rust Example

```rust
use tokenizers::{Tokenizer, models::BPE};

fn main() {
    let mut tokenizer = Tokenizer::new(BPE::default());
    println!("Tokenizer created!");
}
```

## Ruby Installation (Community)

The Ruby bindings are maintained separately:

```bash
gem install tokenizers-ruby
```

**Note**: Ruby bindings may lag behind Python/Rust versions. Check compatibility at https://github.com/ankane/tokenizers-ruby

## Troubleshooting Installation

### Python: "No matching distribution found"

**Problem**: Wheel not available for your platform.

**Solution**: Install from source with Rust toolchain:
```bash
# Install Rust first
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Then install tokenizers
pip install --no-binary :all: tokenizers
```

### Python: Compilation Errors

**Problem**: Missing build dependencies during source installation.

**Solution**: Install required packages:

**Debian/Ubuntu:**
```bash
sudo apt-get install build-essential cmake
```

**Fedora:**
```bash
sudo dnf groupinstall "Development Tools"
sudo dnf install cmake
```

**macOS:**
```bash
xcode-select --install
```

### Node.js: "No prebuilt binaries found"

**Problem**: Binary not available for your Node.js version.

**Solution**: Build from source:
```bash
npm rebuild @huggingface/tokenizers
```

### Rust: Platform-Specific Features

Some features require platform-specific dependencies:

**Linux:**
```toml
[dependencies]
libc = "0.2"
```

**Windows:**
Ensure Visual C++ Build Tools are installed.

## Performance Optimization

### Use Pre-built Wheels

Wheels are significantly faster than building from source:
```bash
# Check if wheel is available
pip install tokenizers --dry-run

# Should show "Would download tokenizers-0.22.3-cp39-cp39-manylinux_2_17_x86_64.whl"
```

### Build with Optimization Flags

For Rust builds, use release mode:
```bash
RUSTFLAGS="-C target-cpu=native" cargo build --release
```

## Upgrade Guide

### Check Current Version

```python
# Python
import tokenizers
print(tokenizers.__version__)

# Node.js
npm list @huggingface/tokenizers

# Rust (check Cargo.lock)
cargo tree | grep tokenizers
```

### Upgrade to Latest

```bash
# Python
pip install --upgrade tokenizers

# Node.js
npm update @huggingface/tokenizers

# Rust
cargo update tokenizers
```

## Development Installation

For contributing to the project:

```bash
# Clone repository
git clone https://github.com/huggingface/tokenizers
cd tokenizers

# Python bindings development
cd bindings/python
pip install -e ".[dev]"

# Run tests
pytest tests/

# Node.js bindings development
cd ../node
npm install
npm run build
npm test

# Rust core development
cd ../../tokenizers
cargo test
```

## Additional Resources

- **Python Packaging Guide**: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
- **Rust Installation**: https://www.rust-lang.org/tools/install
- **Node.js ABI Compatibility**: https://github.com/nodejs/abi-stability-notes
