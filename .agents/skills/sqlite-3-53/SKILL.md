---
name: sqlite-3-53
description: Complete toolkit for SQLite 3.53 covering all official documentation topics including SQL queries, C API integration, JSON/JSONB processing, FTS5 full-text search, virtual tables, R-Tree spatial indexing, transactions and isolation levels, STRICT tables, WITHOUT ROWID optimization, UPSERT/RETURNING patterns, CLI commands, and all built-in extensions (Sessions, CSV, Spellfix, Percentile, DBSTAT, generate_series, CARRAY, Zipfile). Use when building applications requiring embedded SQL databases, performing data analysis, implementing persistent storage, or working with any SQLite feature from basic CRUD to advanced spatial queries, change tracking, and concurrent transaction management.
version: 0.3.0
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - sqlite
  - database
  - sql
  - json
  - fts
  - embedded-database
  - persistence
  - transactions
  - rtree
  - spatial
  - cli
  - extensions
category: database
external_references:
  - https://www.sqlite.org/docs.html
---

# SQLite 3.53

## Overview

SQLite is a C-language library that implements a small, fast, self-contained, high-reliability, full-featured SQL database engine. It is the most widely deployed database engine in the world — present in billions of devices including every Android and iOS device, and bundled in countless applications. SQLite requires no server, no configuration, and stores the entire database in a single cross-platform file.

Key characteristics:
- **Serverless** — No separate process or configuration. The library reads and writes directly to ordinary disk files.
- **Zero-configuration** — No administration or setup required.
- **Self-contained** — Minimal external dependencies; tightly integrated with the host application.
- **Cross-platform** — Runs on Linux, Windows, macOS, and most Unix systems. Available in C, Python, Tcl, Java, Go, Rust, and many other languages through bindings.
- **Small footprint** — The entire library is approximately 1 MB of code.
- **Public domain** — Free for any use, commercial or private.

## When to Use

Use SQLite when:
- Building embedded applications that need local persistent storage
- Prototyping or testing SQL queries without a server database
- Creating self-contained application file formats (replacing XML, JSON, or piles of files)
- Running analytical queries on CSV/text data via the CLI
- Implementing in-memory databases for fast temporary data processing
- Building mobile applications with local data caching
- Needing a single-file, portable database with no deployment complexity

Use a client/server database instead when:
- Multiple processes need concurrent write access across different machines
- The application requires centralized authentication and access control
- Very large concurrent write workloads are expected

## Core Concepts

### Storage Classes

SQLite uses dynamic typing — the type of a value is associated with the value itself, not its container. Every value has one of five storage classes:

- **NULL** — A NULL value
- **INTEGER** — Signed integer stored in 0, 1, 2, 3, 4, 6, or 8 bytes depending on magnitude
- **REAL** — 8-byte IEEE floating point number
- **TEXT** — Text string stored using the database encoding (UTF-8, UTF-16BE, or UTF-16LE)
- **BLOB** — Blob of data stored exactly as input

SQLite does not have separate Boolean or Date/Time storage classes. Booleans are stored as integers 0 (false) and 1 (true). Dates and times are stored as TEXT (ISO8601), REAL (Julian day numbers), or INTEGER (Unix timestamps).

### Type Affinity

Each column has a recommended type called "affinity" — but any column can still store any type. The affinities are TEXT, NUMERIC, INTEGER, REAL, and BLOB. Column affinity is determined by the declared type name in CREATE TABLE. For example, columns declared as INT, INTEGER, TINYINT, SMALLINT, MEDIUMINT, BIGINT, or UNSIGNED BIG INT have INTEGER affinity.

As of version 3.37.0, STRICT tables enforce rigid type checking, rejecting values that do not match the declared type.

### The Rowid

Every table in SQLite has a special column called "rowid" (also accessible as "oid" or "_rowid_") that uniquely identifies each row. This is a 64-bit signed integer that auto-increments. Tables created with `WITHOUT ROWID` use a clustered index instead, which can save space and improve performance in some cases.

## Advanced Topics

**SQL Language Reference**: Core SQL syntax, data types, expressions, operators, and all statement types → See [SQL Language Reference](reference/01-sql-language.md)

**Built-in Functions**: Scalar functions, aggregate functions, date/time functions, math functions, window functions, and JSON/JSONB functions → See [Built-in Functions](reference/02-functions.md)

**C/C++ API**: Database connections, prepared statements, binding parameters, result extraction, error handling, and configuration → See [C/C++ API](reference/03-c-api.md)

**Transactions and Concurrency**: WAL mode, isolation levels, locking, savepoints, and multi-threaded usage → See [Transactions and Concurrency](reference/04-transactions-concurrency.md)

**FTS5 Full-Text Search**: Virtual table module for full-text indexing with tokenizers, prefix queries, BM25 ranking, and auxiliary functions → See [FTS5 Full-Text Search](reference/05-fts5.md)

**R-Tree Spatial Indexing**: Multi-dimensional range queries for geospatial and time-domain data with custom geometry callbacks → See [R-Tree Module](reference/06-rtree.md)

**Virtual Tables and Extensions**: Virtual table mechanism, table-valued functions, loadable extensions, CSV, DBSTAT, generate_series, CARRAY, Spellfix1, Zipfile, Percentile → See [Virtual Tables and Extensions](reference/07-virtual-tables-extensions.md)

**Sessions Extension**: Change capture, changesets and patchsets, conflict resolution, and database synchronization → See [Sessions Extension](reference/08-sessions.md)

**Command-Line Interface**: Dot-commands, output formats, importing/exporting data, schema inspection, and scripting → See [Command-Line Interface](reference/09-cli.md)

**Performance and Limits**: Pragmas, compile-time options, implementation limits, memory-mapped I/O, partial indexes, and optimization → See [Performance and Limits](reference/10-performance-limits.md)
