# Command-Line Reference

## Synopsis

```
upx [ command ] [ options ] filename...
```

## Commands

- **Compress** (default) — `upx yourfile.exe` compresses the specified file
- **Decompress** (`-d`) — `upx -d yourfile.exe` unpacks a previously compressed
  file
- **Test** (`-t`) — `upx -t yourfile.exe` tests integrity of compressed and
  uncompressed data. Note: this does not replace a virus checker
- **List** (`-l`) — `upx -l yourfile.exe` shows compressed/uncompressed size
  and compression ratio

## General Options

- `-q` — Be quiet, suppress warnings
- `-qq` — Be very quiet, suppress errors
- `-qqq` — Produce no output at all
- `--help` — Print help
- `--version` — Print UPX version
- `--exact` — Require byte-identical file after decompress (work in progress,
  not supported for all formats yet)
- `-k` — Keep backup files (original preserved as filename.upx.bak)
- `-o file` — Write output to specified file
- `-f` / `--force` — Force compression even when there is an unexpected value
  in a header field. Use with care
- `--no-env` — Ignore the UPX environment variable

## Compression Levels

UPX offers ten levels from -1 to -9, plus --best:

- Levels **1-3**: Fast compression
- Levels **4-6**: Good time/ratio balance
- Levels **7-9**: Favor compression ratio over speed
- Level **--best**: May take a long time, best for final releases

Default is -8 for files under 512 KiB, -7 otherwise.

## Compression Tuning Options

- `--all-methods` — Try all available compression methods. May improve ratio in
  some cases but usually the default method is best
- `--all-filters` — Try all available preprocessing filters
- `--brute` — Enable --all-methods, --all-filters, and --lzma
- `--ultra-brute` — Even more aggressive than --brute, tries even more variants
- `--lzma` — Enable LZMA compression (better ratio, significantly slower
  decompression). Auto-enabled by --all-methods and --brute
- `--no-lzma` — Disable LZMA (overrides --brute or --ultra-brute)
- `--crp-ms=N` — Set memory limit for compression in bytes. Higher values may
  give slightly better ratio at cost of more memory during compression. Try
  `upx --best --crp-ms=100000`

## Overlay Handling

An "overlay" is auxiliary data attached after the logical end of an executable,
often containing application-specific data.

- `--overlay=copy` — Copy any extra data attached to the file (default)
- `--overlay=strip` — Strip any overlay from the program. May make the
  compressed program crash or otherwise unusable
- `--overlay=skip` — Refuse to compress any program with an overlay

## Environment Variable

The environment variable `UPX` can hold default options:

```bash
# sh/ksh/zsh
UPX="-9 --compress-icons=0"; export UPX

# csh/tcsh
setenv UPX "-9 --compress-icons=0"
```

Under DOS/Windows, use `#` instead of `=` due to COMMAND.COM limitations:

```cmd
set UPX=-9 --compress-icons#0
```

Use `--no-env` to ignore the environment variable.

## Exit Status

- **0** — Success
- **1** — Error occurred
- **2** — Warning occurred

## Preservation Options

- `--no-mode` — Do not preserve file permissions (mode)
- `--no-owner` — Do not preserve file ownership
- `--no-time` — Do not preserve timestamps
- `--link` — Preserve hard links (Unix only, use with care)

## Format-Specific Common Options

Many formats support these extra options:

- `--8086` — Create an executable that works on any 8086 CPU (DOS formats)
- `--all-methods` — Try all compression methods
- `--all-filters` — Try all preprocessing filters
