# UPX Common Operations

This reference covers the most frequently used UPX commands with practical examples.

## Basic Commands

### Compress Executables

```bash
# Simple compression (uses default level)
upx program.exe

# Compress multiple files
upx file1.exe file2.dll library.so

# Compress all executables in a directory
upx build/release/*.exe
```

**Output:**
```
         UPX 5.1.1      Markus Oberhumer, Laszlo Molnar & John Reiser http://upx.github.io

        Copyright (C) 1996 - 2026 UPX Team.  UPX comes with ABSOLUTELY NO WARRANTY.

    file        packed    ratio   unpacked  compressed
    program.exe  125.4 KB  38.2%   328.1 KB      125.4 KB
```

### Decompress Executables

```bash
# Decompress a single file
upx -d program.exe

# Decompress multiple files
upx -d file1.exe file2.dll

# Decompress and overwrite in place
upx -d *.exe
```

**Note:** UPX keeps the original file untouched. After decompression, you get a byte-identical copy of the original.

### Test Integrity

```bash
# Test compressed file integrity
upx -t program.exe

# Test multiple files
upx -t *.exe
```

**Output:**
```
    file        ok?     compression
    program.exe  OK      38.2%
```

**Important:** The `-t` command only checks the part that will be uncompressed during execution, not the whole file. Do not use this instead of a virus checker.

### List Compression Info

```bash
# Show compression statistics
upx -l program.exe

# List multiple files
upx -l *.exe
```

**Output:**
```
    file        packed   ratio   unpacked  compressed
    program.exe   yes    38.2%   328.1 KB      125.4 KB
```

## Output Control

### Quiet Modes

```bash
# Suppress warnings
upx -q program.exe

# Suppress errors (very quiet)
upx -qq program.exe

# No output at all
upx -qqq program.exe
```

Useful for scripts and CI/CD pipelines where you only care about exit codes.

### Backup Files

```bash
# Keep backup of original before compression
upx -k program.exe
# Creates: program.exe (compressed), program.exe.bak (original)

# Decompress with backup
upx -d -k program.exe
# Creates: program.exe (decompressed), program.exe.bak (compressed version)
```

### Custom Output File

```bash
# Write compressed output to specific file
upx -o compressed.exe program.exe

# Useful for preserving original filename
upx -o release.bin original_program
```

## Help and Version

```bash
# Show help message
upx --help

# Show version information
upx --version
# Output: UPX 5.1.1
```

## Practical Workflows

### Development Workflow

```bash
# Quick compression for testing (fast, lower ratio)
upx -5 myapp.exe

# Test the compressed version
./myapp.exe --version

# Decompress if needed for debugging
upx -d myapp.exe
```

### Release Build Workflow

```bash
# 1. Strip symbols first (recommended for best compression)
strip myprogram

# 2. Compress with maximum effort
upx --best -k myprogram

# 3. Verify integrity
upx -t myprogram

# 4. Check size reduction
ls -lh myprogram myprogram.bak
```

### Safe Distribution Workflow

```bash
# Create compressed version with backup
upx -k --best release.exe

# Test the compressed file
upx -t release.exe

# Verify round-trip (compress then decompress)
upx -d release.exe
diff release.exe release.exe.bak  # Should be identical

# If diff shows no differences, safe to distribute release.exe.bak
```

### CI/CD Integration

```bash
#!/bin/bash
set -e  # Exit on error

# Compress all release artifacts
for file in build/release/*.exe; do
    echo "Compressing $file..."
    upx -qq --best "$file" || {
        echo "Failed to compress $file"
        exit 1
    }
done

# Verify all compressed files
upx -t build/release/*.exe

echo "All files compressed successfully"
```

### Batch Processing

```bash
# Compress all executables in directory tree
find . -name "*.exe" -type f -exec upx --best {} \;

# Compress with progress output
for file in *.bin; do
    echo "Processing $file..."
    upx -l "$file"  # Show before
    upx --best "$file"
    upx -l "$file"  # Show after
done
```

## Command Options Summary

| Option | Description |
|--------|-------------|
| `-d` | Decompress files |
| `-t` | Test file integrity |
| `-l` | List compression info |
| `-q` | Be quiet (suppress warnings) |
| `-qq` | Very quiet (suppress errors) |
| `-qqq` | No output at all |
| `-k` | Keep backup files |
| `-o file` | Write output to specified file |
| `--help` | Print help message |
| `--version` | Print version number |
| `--exact` | Require byte-identical after decompress (work in progress) |
| `--no-env` | Ignore UPX environment variable |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error (invalid options, file not found) |
| 2 | File format not supported |
| 3 | Internal error during compression/decompression |

## Tips and Best Practices

### Always Test Before Distribution

```bash
# Compress
upx --best program.exe

# Test integrity
upx -t program.exe

# Run the program to verify it works
./program.exe --help
```

### Strip Before Compressing

```bash
# Remove debug symbols for better compression
strip myprogram
upx --best myprogram
```

### Use Appropriate Compression Level

```bash
# Development: fast compression
upx -5 program.exe

# Release: maximum compression
upx --best program.exe
```

### Preserve Originals

```bash
# Always use -k for important files
upx -k --best critical_app.exe
```

### Check File Format First

```bash
# Verify file type before compressing
file myprogram
# Should show: ELF 64-bit, PE32 executable, etc.

# UPX will reject unsupported formats with exit code 2
```

## Related Reference Files

- [Compression Strategies](02-compression-strategies.md) - Advanced compression options and tuning
- [Format-Specific Notes](03-format-notes.md) - Platform-specific considerations
- [Linux Executables](04-linux-executables.md) - Detailed Linux format documentation
