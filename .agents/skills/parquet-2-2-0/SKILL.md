---
name: parquet-2-2-0
description: Complete toolkit for Apache Parquet 2.2.0 columnar storage format covering physical and logical types, schema definition via Thrift (parquet.thrift), encodings (PLAIN, RLE, Dictionary, Delta Binary Packed, Delta Length Byte Array, Delta String, Byte Stream Split), compression codecs (SNAPPY, GZIP, ZSTD, LZ4_RAW, BROTLI), nested data with definition/repetition levels, bloom filters, page indexes, encryption, and file layout. Use when reading, writing, or optimizing Parquet files, designing columnar storage schemas, tuning compression and encoding strategies, or implementing Parquet readers/writers.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - parquet
  - columnar-storage
  - file-format
  - dremel
  - thrift
category: file-format
external_references:
  - https://parquet.apache.org/docs/
  - https://github.com/apache/parquet-format
---

# Apache Parquet 2.2.0

## Overview

Apache Parquet is an open source, column-oriented data file format designed for efficient data storage and retrieval. It provides high-performance compression and encoding schemes to handle complex nested data in bulk and is supported across many programming languages and analytics tools (Spark, DuckDB, Arrow, Pandas, Polars, Impala, and more).

Parquet was inspired by the Dremel paper's record shredding and assembly algorithm, enabling efficient storage of complex nested structures. The format separates metadata from data, supports per-column compression and encoding, and enables predicate pushdown through column statistics and page indexes.

## When to Use

- Reading or writing Parquet files programmatically
- Designing schemas for columnar storage (choosing physical vs logical types)
- Tuning compression and encoding for storage efficiency or query performance
- Implementing Parquet readers or writers
- Understanding Parquet file layout, row groups, column chunks, and pages
- Working with nested data structures in columnar format
- Optimizing analytics workloads that read Parquet (filter pushdown, pruning)

## Core Concepts

### Hierarchical Structure

A Parquet file is organized hierarchically:

- **File** — Contains one or more row groups plus file-level metadata.
- **Row Group** — Horizontal partition of data into rows. Each row group has exactly one column chunk per column. Typical size: 128MB–1GB.
- **Column Chunk** — Contiguous data for a single column within a row group. Contains one or more pages.
- **Page** — Indivisible unit of compression and encoding. Types: dictionary pages, data pages (v1/v2), and index pages.

### Physical vs Logical Types

Parquet uses minimal **physical types** for on-disk storage: `BOOLEAN`, `INT32`, `INT64`, `INT96` (deprecated), `FLOAT`, `DOUBLE`, `BYTE_ARRAY`, `FIXED_LEN_BYTE_ARRAY`.

**Logical types** annotate physical types to express higher-level semantics: `STRING`, `INT(8/16/32/64, signed/unsigned)`, `DECIMAL`, `DATE`, `TIME`, `TIMESTAMP`, `INTERVAL`, `JSON`, `BSON`, `UUID`, `FLOAT16`, `GEOMETRY`, `GEOGRAPHY`, `VARIANT`. Nested types `LIST` and `MAP` use group annotations.

### Null Handling via Definition Levels

Nulls in nested structures are encoded using **definition levels** — an integer per value indicating how deep the non-null path goes. A definition level of 0 means the value is null; the maximum level means fully populated. This avoids storing explicit null markers for every field.

### Nested Data via Repetition Levels

Repeated elements (lists, arrays) use **repetition levels** — an integer per value indicating whether it starts a new repetition (0) or continues the current one (>0). Combined with definition levels, this enables efficient encoding of arbitrarily nested structures.

## Advanced Topics

**Types and Schema**: Physical types, logical types, LIST/MAP encoding, decimal, temporal, geospatial, variant → [Types and Schema](reference/01-types-and-schema.md)
**Encodings**: PLAIN, RLE/Bit-Packing, Dictionary, Delta Binary Packed, Delta Length/String, Byte Stream Split → [Encodings](reference/02-encodings.md)
**Compression**: SNAPPY, GZIP, ZSTD, LZ4_RAW, BROTLI, LZO and codec selection → [Compression](reference/03-compression.md)
**Pages and Column Chunks**: Data page v1/v2, dictionary pages, column chunk metadata, statistics → [Pages and Column Chunks](reference/04-pages-and-column-chunks.md)
**Metadata and File Layout**: File structure, parquet.thrift, file footer, schema elements → [Metadata and File Layout](reference/05-metadata-and-file-layout.md)
**Optimization Features**: Bloom filters, page indexes, size statistics, error recovery → [Optimization Features](reference/06-optimization-features.md)
**Encryption and Security**: AES/GCM and AES/S2E encryption, footer encryption, key tools → [Encryption and Security](reference/07-encryption-and-security.md)
**Extensibility and Compatibility**: Schema migration, binary protocol extensions, implementation status → [Extensibility and Compatibility](reference/08-extensibility-and-compatibility.md)
