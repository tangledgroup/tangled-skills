# UPX Compression Strategies and Tuning

This reference covers advanced compression options, tuning techniques, and strategies for achieving optimal results.

## Compression Levels in Detail

UPX provides ten numeric levels plus a `--best` option:

### Level Categories

| Levels | Speed | Ratio | Typical Use Case |
|--------|-------|-------|------------------|
| -1 to -3 | Fast (0.5-2s) | 40-50% | Development builds, quick iteration |
| -4 to -6 | Medium (2-10s) | 50-60% | General use, good balance |
| -7 to -9 | Slow (10-60s) | 60-70% | Release candidates, pre-final builds |
| `--best` | Very slow (60s+) | 65-75% | Final distribution, archival |

### Default Behavior

UPX automatically selects compression level based on file size:
- **Files < 512 KiB**: Level `-8` (faster, good ratio)
- **Files ≥ 512 KiB**: Level `-7` (balanced for large files)

```bash
# Small file (<512KB) - defaults to -8
upx small_tool.exe

# Large file (>512KB) - defaults to -7
upx large_application.exe

# Override default
upx -9 small_tool.exe  # Force maximum numeric level
upx -5 large_application.exe  # Faster compression
```

## Advanced Compression Options

### Brute Force Modes

```bash
# Try many compression variants
upx --brute program.exe

# Ultra brute - even more aggressive (very slow)
upx --ultra-brute program.exe

# Combine with other options
upx --ultra-brute --no-lzma program.exe
```

**Performance Note:** `--ultra-brute` can be extremely slow for large files. Only use for critical distribution where every byte matters.

### All Methods and Filters

```bash
# Try all available compression methods
upx --all-methods program.exe

# Try all preprocessing filters
upx --all-filters program.exe

# Combine both (slowest)
upx --all-methods --all-filters program.exe
```

These options try multiple compression algorithms and data preprocessing techniques to find the best combination.

### LZMA Compression

LZMA provides better compression ratios but significantly slower decompression:

```bash
# Enable LZMA compression
upx --lzma program.exe

# Brute force with LZMA
upx --brute --lzma program.exe

# Disable LZMA (faster decompression)
upx --no-lzma program.exe
upx --brute --no-lzma program.exe
```

**When to use LZMA:**
- ✅ Small to medium files (<10MB) where distribution size matters
- ✅ Programs that run infrequently
- ✅ Archival distributions

**When to avoid LZMA:**
- ❌ Large files (>50MB) - decompression becomes very slow
- ❌ Frequently executed programs
- ❌ Real-time applications
- ❌ Systems with limited CPU resources

### Exact Mode

```bash
# Require byte-identical after decompress (work in progress)
upx --exact program.exe
```

**Note:** `--exact` is not yet supported for all formats. As a workaround, compress and decompress once first - subsequent cycles should yield byte-identical results.

## Overlay Handling Strategies

An "overlay" is auxiliary data attached after the logical end of an executable. Common uses include embedded resources, configuration data, or secondary executables.

### Copy Mode (Default)

```bash
# Preserve overlay by copying it after compressed image
upx --overlay=copy program.exe
# Equivalent to default behavior
upx program.exe
```

**Behavior:** The overlay is preserved but may not work correctly if the application accesses it at a specific offset.

### Strip Mode

```bash
# Remove overlay during compression
upx --overlay=strip program.exe
```

**Warning:** This may make the compressed program crash or unusable. Only use if:
- You know the overlay is not needed at runtime
- You've tested thoroughly and verified functionality
- The overlay contains non-critical data (e.g., help text, credits)

### Skip Mode

```bash
# Refuse to compress files with overlays
upx --overlay=skip program.exe
```

**Use case:** Batch processing where you want to avoid potentially problematic files.

**Output when overlay detected:**
```
    program.exe   not packed: overlay present
```

### Overlay Detection and Handling Workflow

```bash
# 1. Check if file has overlay
upx -l program.exe
# Look for "overlay" in output

# 2. Try with copy first (safest)
upx --overlay=copy program.exe
./program.exe  # Test functionality

# 3. If size is critical and overlay not needed
upx --overlay=strip program.exe
./program.exe  # Verify still works

# 4. If unsure, skip files with overlays
upx --overlay=skip *.exe
```

## Platform-Specific Tuning

### Windows PE Files

```bash
# Disable relocation stripping (may improve compatibility)
upx --strip-relocs=0 program.exe

# Compress icons and resources
upx --compress-icons=1 program.exe  # Compress some icons
upx --compress-icons=2 program.exe  # Compress more icons
upx --compress-icons=3 program.exe  # Compress all icons

# Keep specific resources uncompressed
upx --keep-resource=RT_VERSION program.exe
upx --keep-resource=RT_ICON program.exe

# Strip load config section (obsolete since 1.94)
# upx --strip-loadconf program.exe
```

### Linux Executables

```bash
# Force execve format (for SELinux compatibility)
upx --force-execve program

# Unmap all pages (avoid /proc/self/exe)
upx --unmap-all-pages program

# Preserve build ID
upx --preserve-build-id program
```

### DOS Executables

```bash
# Create 8086-compatible executable
upx --8086 program.com

# Disable relocation records
upx --no-reloc program.exe
```

## Size vs. Speed Tradeoffs

### Maximum Speed (Minimum Compression)

```bash
# Fastest compression, lowest ratio
upx -1 fast_build.exe

# Good for development where build time matters
upx -3 dev_tool.exe
```

### Balanced Approach

```bash
# Default behavior - good balance
upx release_candidate.exe

# Slightly better ratio, acceptable speed
upx -7 pre_release.exe
```

### Maximum Compression (Minimum Speed)

```bash
# Best compression ratio
upx --best final_release.exe

# Ultra brute for critical size reduction
upx --ultra-brute --no-lzma distribution.exe
```

## Practical Scenarios

### Scenario 1: Game Distribution

```bash
# Game executable - balance size and load time
upx -8 game.exe

# Game DLLs - maximum compression (loaded once)
upx --best game.dll

# Resource files with overlays - preserve overlay
upx --overlay=copy resources.exe
```

### Scenario 2: Command-Line Tools

```bash
# CLI tools - fast decompression important
upx -7 tool.exe

# Avoid LZMA for frequently used tools
upx --no-lzma common_utility.exe
```

### Scenario 3: Embedded Systems

```bash
# Flash storage limited - maximum compression
upx --best firmware.bin

# RAM limited - avoid LZMA
upx --no-lzma embedded_app.elf
```

### Scenario 4: Software Installer

```bash
# Installer executable - good balance
upx -8 setup.exe

# Included libraries - maximum compression
upx --best lib/*.dll

# Preserve overlays for self-extracting archives
upx --overlay=copy sfx_archive.exe
```

## Performance Monitoring

### Measure Compression Time

```bash
# Time the compression
time upx --best large_program.exe

# Typical output:
# real    0m45.234s
# user    0m42.100s
# sys     0m2.500s
```

### Measure Size Reduction

```bash
# Before
ls -lh program.exe
# -rwxr-xr-x 1 user user 15.2M Jan 15 10:30 program.exe

# Compress
upx --best program.exe

# After
ls -lh program.exe
# -rwxr-xr-x 1 user user 4.8M Jan 15 10:31 program.exe

# Calculate ratio
echo "scale=2; 4.8 / 15.2 * 100" | bc
# Output: 31.58% (68.42% reduction)
```

### Benchmark Different Levels

```bash
for level in 1 5 8 best; do
    cp original.exe test.exe
    echo "Level $level:"
    time upx -$level test.exe
    ls -lh test.exe
    upx -d test.exe
done
```

## Troubleshooting Compression Issues

### "Packed Data Overlap" Error

```bash
# Problem: UPX cannot pack without overlapping data
# Solution 1: Use --force to relocate
upx --force program.exe

# Solution 2: Reduce compression level
upx -5 program.exe

# Solution 3: Strip the binary first
strip program.exe
upx --best program.exe
```

### Compression Fails on PE Files

```bash
# Try disabling relocation stripping
upx --strip-relocs=0 program.exe

# Check for corrupted headers
upx -t program.exe  # Should fail if corrupted

# Try lower compression level
upx -5 program.exe
```

### Program Crashes After Compression

```bash
# 1. Test integrity
upx -t program.exe

# 2. Check for overlay issues
upx -l program.exe  # Look for overlay warning

# 3. Try different overlay handling
upx --overlay=copy program.exe

# 4. Decompress and verify round-trip
upx -d program.exe
diff program.exe original.exe  # Should be identical
```

## Best Practices Summary

1. **Always test compressed files** before distribution with `upx -t`
2. **Strip binaries first** for better compression ratios
3. **Use appropriate levels**: `-5` for development, `--best` for releases
4. **Avoid LZMA** for large files or frequently executed programs
5. **Preserve overlays** unless you've verified they're not needed
6. **Keep backups** with `-k` option for critical files
7. **Monitor compression time** - `--best` can be very slow for large files
8. **Verify round-trip** for critical applications

## Related Reference Files

- [Common Operations](01-common-operations.md) - Basic commands and workflows
- [Format-Specific Notes](03-format-notes.md) - Platform-specific options
- [Linux Executables](04-linux-executables.md) - Detailed Linux documentation
