# Windows PE Guide

## Overview

UPX supports 32-bit (win32/pe), 64-bit (win64/pe for amd64 and arm64), and ARM
PE formats. The PE support is quite stable but some incompatibilities may exist
with certain files.

## Memory Behavior

Because of how UPX works with PE files, compressed programs show increased
memory usage since the whole program is loaded into memory at startup. If you
start several instances of large compressed programs, common segments won't be
shared across instances. For smaller programs or single-instance applications,
this penalty is smaller but still present.

Running executables from a network benefits — compressed programs load faster
and require less bandwidth during execution.

## DLL Support

DLLs are supported with the restriction that UPX compressed DLLs cannot share
common data and code when used by multiple applications. Compressing
`msvcrt.dll` is a waste of memory, but compressing DLL plugins of a particular
application may be worthwhile.

## Screensaver Support

Screensavers are supported with the restriction that the filename must end with
".scr" (screensavers are handled slightly differently than normal exe files).

## Memory Overhead

UPX compressed PE files have minor memory overhead, usually in the 10-30 KiB
range. Specify `-i` during compression to see details.

## Windows-Specific Options

### Export Compression

```
--compress-exports=0   Don't compress the export section
                       Use if running under Wine
--compress-exports=1   Compress the export section [DEFAULT]
                       Can improve ratio but may not work with all programs
                       UPX never compresses exports of a DLL regardless
```

### Icon Compression

```
--compress-icons=0     Don't compress any icons
--compress-icons=1     Compress all but the first icon
--compress-icons=2     Compress all icons not in first icon directory [DEFAULT]
--compress-icons=3     Compress all icons
```

### Resource Compression

```
--compress-resources=0   Don't compress any resources at all

--keep-resource=list     Don't compress specified resources
                         Members separated by commas
                         Format: Type[/Name]
                         Standard types as decimal numbers
                         User types as decimal IDs or strings
                         Example: --keep-resource=2/MYBITMAP,5,6/12345
```

### Relocation Handling

```
--strip-relocs=0   Don't strip relocation records
--strip-relocs=1   Strip relocation records [DEFAULT]
                   Only works on executables with base address >= 0x400000
                   Usually makes files smaller, but some may become larger
                   Resulting file will not work under Windows 3.x (Win32s)
                   UPX never strips relocations from a DLL regardless
```

### Force Option

```
--force   Force compression even when there is an unexpected value
          in a header field. Use with care.
```

## TLS Callback Support

UPX supports PE files with TLS (Thread Local Storage) callbacks. However,
files with broken PE headers may have filters disabled automatically.

## Wine Compatibility

When planning to run compressed programs under Wine, use
`--compress-exports=0` to avoid potential issues with export section
compression.

## Known Limitations

- .NET files (win32/net) are not supported
- RT_MANIFEST resource types are not compressed
- REGISTRY resources are never compressed
- Programs with TLS callbacks may have restrictions in older UPX versions
- Empty resource sections produce an improved error message
- Files with broken PE headers may be auto-detected and filters disabled
