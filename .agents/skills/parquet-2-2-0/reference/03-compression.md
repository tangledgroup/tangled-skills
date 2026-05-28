# Compression

## Contents
- Overview
- Supported Codecs
- Codec Selection Guide

## Overview

Parquet allows the data block inside dictionary pages and data pages to be compressed. Compression is applied **per column chunk** (not per file), enabling different codecs for different columns based on data characteristics.

For all codecs except the deprecated `LZ4`, raw page data is fed *as-is* to the compression library — no additional framing or padding. Compressed and uncompressed sizes are stored in the `PageHeader` struct for precise buffer allocation.

## Supported Codecs

### UNCOMPRESSED
No-op codec. Data left uncompressed. Useful for debugging or when encoding alone provides sufficient size reduction.

### SNAPPY
Based on [Google Snappy format](https://github.com/google/snappy/blob/master/format_description.txt). Fast compression/decompression with moderate ratio. Default choice in many implementations (Spark, Hive).

### GZIP
Based on [RFC 1952 GZIP format](https://tools.ietf.org/html/rfc1952) — not "zlib" or raw "deflate". Reference implementation: [zlib library](https://zlib.net/).

- Readers should support pages with multiple GZIP members.
- Writers should avoid creating such pages for better interoperability.

### LZO
Based on or interoperable with the [LZO compression library](https://www.oberhumer.com/opensource/lzo/). Legacy codec, less common in modern implementations.

### BROTLI
Based on [RFC 7932 Brotli format](https://tools.ietf.org/html/rfc7932). Reference implementation: [Brotli library](https://github.com/google/brotli). High compression ratio at the cost of slower decompression.

### LZ4 (Deprecated)
Loosely based on LZ4 with an additional undocumented framing scheme from the original Hadoop compression library. Historically copied into parquet-mr and emulated with mixed results by parquet-cpp.

**Recommendation**: Deprecate this codec in writer APIs. Advise users to switch to `LZ4_RAW`.

### ZSTD
Based on [RFC 8478 Zstandard format](https://tools.ietf.org/html/rfc8478). Reference implementation: [Facebook zstd library](https://facebook.github.io/zstd/). Excellent balance of compression ratio and speed. Supports configurable compression levels.

### LZ4_RAW
Based on [LZ4 block format](https://github.com/lz4/lz4/blob/dev/doc/lz4_Block_format.md). Reference implementation: [LZ4 library](https://www.lz4.org/). Interoperable LZ4 without the framing issues of the deprecated `LZ4` codec.

## Codec Selection Guide

| Priority | Codec | Trade-off |
|---|---|---|
| Speed-first | SNAPPY, LZ4_RAW | Fast decompression, moderate ratio. Best for latency-sensitive workloads. |
| Balanced | ZSTD | Good ratio with acceptable speed. Default for many modern systems. |
| Ratio-first | GZIP, BROTLI | Smallest files, slower decompression. Best for archival or bandwidth-constrained storage. |
| Legacy | LZO, LZ4 (deprecated) | Maintain for reading old data; avoid in new writes. |

Common defaults:
- **Spark**: SNAPPY (default), configurable per file.
- **DuckDB**: SNAPPY (default).
- **Arrow C++**: SNAPPY (default).
- **Pandas/PyArrow**: SNAPPY (default).

Compression is specified at the column chunk level via the `compression` field in `ColumnMetaData`. Each column chunk can use a different codec.
