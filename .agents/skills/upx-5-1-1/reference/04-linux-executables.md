# UPX Linux Executable Formats - Detailed Reference

This comprehensive guide covers all aspects of compressing Linux executables with UPX, including the three format types, performance considerations, and troubleshooting.

## Linux Format Overview

UPX recognizes three executable formats for Linux:

1. **linux/elf386** - ELF binary executables (preferred, direct-to-memory)
2. **linux/sh386** - Shell scripts with "-c" argument support
3. **linux/386** - Generic format (uses /tmp and /proc)

Format selection is automatic based on file type.

## Performance Tradeoffs

### Space vs. Time Considerations

Running a compressed executable trades permanent storage space for temporary storage:

- **Permanent:** Hard disk, floppy, CD-ROM, flash memory, EPROM
- **Temporary:** RAM, swap space, /tmp filesystem

**Typical savings:** 30% to 50% of permanent disk space

**CPU overhead:** Decompression speed is typically many MB/sec, often limited by disk or network I/O rather than CPU.

### When Compression Helps

Compressed executables can be **faster** than uncompressed in certain scenarios:

✅ **Medium-sized programs** (access 1/3 to 1/2 of stored bytes)
✅ **Limited disk/flash storage** environments
✅ **Slow disk or network** where reduced I/O helps
✅ **Fast CPU relative to storage** speed

### When Compression Hurts

❌ **Small programs** - Absolute savings is minimal
❌ **Large programs** where each invocation uses small fraction
❌ **Programs with many concurrent instances** (sh, make)
❌ **Systems with limited RAM/swap** space

### Memory Sharing Impact

Compressed executables do **not** share RAM between processes like file-mapped executables:

```bash
# Running 10 instances of uncompressed bash
# Shares common segments in RAM

# Running 10 instances of UPX-compressed bash
# Each instance uses separate RAM/swap
# May cause memory pressure on system
```

**Recommendation:** Avoid compressing shell programs (bash, csh) and `make`.

## linux/elf386 Format

### How It Works

For ELF executables, UPX decompresses directly to memory:

1. Simulates the mapping that OS kernel uses during exec()
2. Includes PT_INTERP program interpreter (if any)
3. Sets brk() via special PT_LOAD segment in compressed executable
4. Wipes stack clean except for arguments, environment variables, Elf_auxv entries
5. Transfers control to program interpreter or e_entry address

**Why this is needed:** Bugs in /lib/ld-linux.so startup code (as of May 2000) require clean stack.

### Technical Details

- **Stub size:** ~1700 bytes
- **Implementation:** Partly assembler, only kernel syscalls
- **Dependencies:** Not linked against any libc
- **Compatibility:** Should run under FreeBSD and other systems that can run Linux binaries

### Advantages

✅ Direct-to-memory decompression (no /tmp needed)
✅ Single exec call (fast startup)
✅ No /proc filesystem required
✅ Byte-identical after uncompression
✅ Works with any ELF binary

### Specific Drawbacks

⚠️ **RAM and swap space** hold entire decompressed program during process lifetime
⚠️ **Out of memory risks:** System can become fragile when swap is full
⚠️ **Kernel OOM killer** may terminate processes arbitrarily

**Monitor swap usage:**
```bash
# Check current swap usage
top  # Look in Mem/Swap sections
free -h

# Monitor during program execution
watch -n 1 'free -h'
```

### No Extra Options

The linux/elf386 format has no format-specific options. All standard UPX options apply.

## linux/sh386 Format

### How It Works

For shell scripts where the shell accepts "-c" argument:

1. Decompresses script into low memory
2. Maps the shell and its PT_INTERP
3. Passes control to shell with entire decompressed file as argument after "-c"

### Supported Shells

✅ sh, ash, bash, bsh, csh, ksh, tcsh, pdksh

### Restriction

Cannot handle scripts with optional string argument after shell name:

```bash
# This WON'T work with linux/sh386:
#!/bin/sh option3
echo "Hello"

# This WILL work:
#!/bin/sh
echo "Hello"
```

### Advantages

✅ No /tmp space used
✅ No /proc required
✅ Byte-identical after uncompression
✅ Fast decompression to memory

### Drawbacks

Same as linux/elf386: relies on RAM and swap space for entire program lifetime.

### No Extra Options

The linux/sh386 format has no format-specific options.

## linux/386 Generic Format

### How It Works

For files that are not ELF and not known shell scripts:

1. Decompress overlay to temporary location in /tmp
2. Open temporary file for reading
3. Try to delete temp file and start via /proc/<pid>/fd/X
4. If that fails, fork subprocess to clean up and start program

### Requirements

**Disk space:** Need additional free space in /tmp for uncompressed program duration

**/proc filesystem:** Must be mounted and accessible:
- /proc/<pid>/exe
- /proc/<pid>/fd/X

**Cannot compress:** Programs used during boot before /proc is mounted

### Technical Details

- **Stub:** Statically linked ELF executable, ~1700 bytes
- **Implementation:** Partly assembler, only kernel syscalls
- **Not linked against libc**

### Performance

Despite temporary disk decompression, often no noticeable delay due to Linux kernel memory management:

> "Because of the good memory management of the Linux kernel, this often does not introduce a noticeable delay, and in fact there will be no disk access at all if you have enough free memory as the entire process takes place within the file system buffers."

**Example:** ~3 MiB emacs compresses to <1 MiB with no noticeable startup delay.

### Drawbacks

⚠️ **/tmp space required** for full uncompressed program
⚠️ **/proc filesystem required** - won't work early in boot sequence
⚠️ **Process name issues:** `top` shows numerical values (e.g., /proc/1234/fd/3)
⚠️ **Slower decompression** than elf386/sh386 due to disk I/O

### Extra Option

```bash
# Force use of generic linux/386 "execve" format
upx --force-execve program
```

**Use case:** SELinux compatibility or when elf386/sh386 fail.

## General Linux Benefits

### Universal Compression

UPX can compress **all** Linux executables:
- AOUT, ELF binaries
- libc4, libc5, libc6 linked programs
- Shell/Perl/Python/Ruby scripts
- Standalone Java .class binaries
- Anything executable

### Self-Contained

Compressed programs are completely self-contained. No external program needed at runtime.

### Original Preserved

UPX keeps original program untouched:
- Byte-identical after decompression
- Can use UPX as reliable file compressor (like gzip)
- Internal checksum ensures reliability

### Portability

Stub only uses syscalls and isn't linked against libc:
- Should run under any Linux configuration that can run ELF binaries
- Compatible with FreeBSD and other ELF-supporting systems

## General Linux Drawbacks

### Process Sharing

Compressed programs won't share common segments between processes:

```bash
# Bad candidates for compression:
# - /bin/bash (many instances running)
# - /bin/sh (frequently used)
# - /usr/bin/make (long-running with multiple jobs)
```

### Tool Compatibility

**`ldd` won't show useful information:**
```bash
$ ldd upx_compressed_program
# Shows only the statically linked stub
```

**`size` won't recognize format:**
Since v0.82, section headers are stripped from UPX stub. `size` doesn't even recognize the file format.

**Patch available:** File `patches/patch-elfcode.h` has a patch to fix this bug in `size` and other programs using GNU BFD.

### Platform Independence Lost

Compressing scripts loses platform independence:

```bash
# Original script works on any Unix system
#!/bin/sh
echo "Hello"

# After UPX compression, only works on the compression platform
# Problematic with NFS-mounted disks across different architectures
```

### Security Restrictions

**SUID/GUID/sticky-bit programs rejected:**
```bash
$ chmod 4755 setuid_program
$ upx setuid_program
# ERROR: cannot compress setuid programs
```

**No sense making compressed programs SUID:**
Even if you bypass the check, it provides no security benefit.

### Self-Reading Executables

UPX won't work with executables that read data from themselves:

```bash
# Perl scripts accessing __DATA__ lines may fail:
#!/usr/bin/perl
__END__
data here
```

## Error Handling

### Exit Code 127

In case of internal errors, the stub aborts with exit code 127.

**Typical reasons:**
- Program modified after compression
- File corruption
- Disk I/O errors

**Debugging:**
```bash
# Trace system calls to diagnose issues
strace -o strace.log compressed_program

# Check strace.log for error details
tail -50 strace.log
```

## Best Practices for Linux

### Strip Before Compression

```bash
# Remove debug symbols for better compression
strip myprogram
upx --best myprogram
```

### Avoid Compressing System Utilities

```bash
# DON'T compress these:
# /bin/bash, /bin/sh, /bin/make, /usr/bin/vim
# (frequently used, many instances)

# DO compress these:
# Rarely used utilities
# One-off scripts
# Application binaries
```

### Monitor System Resources

```bash
# Before compressing frequently-used programs
free -h  # Check available RAM/swap
df -h /tmp  # Check /tmp space (for linux/386 format)
```

### Test Thoroughly

```bash
# Compress
upx --best myprogram

# Test integrity
upx -t myprogram

# Run with typical workloads
./myprogram --version
./myprogram <typical-arguments>

# Monitor resource usage
strace -c ./myprogram  # System call statistics
```

### SELinux Considerations

```bash
# v5.0.0+ uses memfd_create for SELinux Enforcing mode
upx program  # Should work automatically

# If issues persist, use execve format
upx --force-execve program

# Check SELinux status
getenforce
# Enforcing: May need --force-execve
# Permissive: Standard compression should work
```

## Format Detection and Selection

UPX automatically selects the best format:

```bash
# ELF binary -> linux/elf386
upx /usr/bin/ls

# Shell script -> linux/sh386
upx ./myscript.sh

# Other executable -> linux/386
upx ./custom_executable
```

**Force specific format:**
```bash
# Force generic execve format
upx --force-execve program
```

## Troubleshooting Linux Compression

### Program Won't Start After Compression

**Symptoms:** Exit code 127 or immediate crash

**Diagnosis:**
```bash
# Check if file was modified
upx -t program

# Trace execution
strace -o trace.log ./program
tail -100 trace.log

# Look for:
# - Permission denied errors
# - /proc access issues
# - Shared library loading failures
```

**Solutions:**
- Decompress and re-compress with different options
- Use `--force-execve` for SELinux compatibility
- Check /tmp space and permissions
- Verify /proc is mounted

### "Cannot Exec" Errors

**Cause:** /tmp mounted with noexec flag

**Check:**
```bash
mount | grep /tmp
# Look for: noexec option
```

**Solutions:**
- Remount /tmp without noexec (if safe)
- Use `--force-execve` option
- Compress to different location with exec permission

### Memory Pressure Issues

**Symptoms:** System slows down, OOM killer activates

**Diagnosis:**
```bash
# Monitor memory during execution
top -p <pid>

# Check swap usage
free -h
```

**Solutions:**
- Don't compress programs with many concurrent instances
- Add more RAM or swap space
- Decompress critical system utilities

## Related Reference Files

- [Common Operations](01-common-operations.md) - Basic commands and workflows
- [Compression Strategies](02-compression-strategies.md) - Tuning and optimization
- [Format-Specific Notes](03-format-notes.md) - Platform-specific considerations
