# Optimization Features

## Contents
- Bloom Filters
- Page Indexes
- Size Statistics
- Error Recovery

## Bloom Filters

Bloom filters enable fast rejection of row groups that do not contain a sought value, avoiding full column scans.

### Structure

Each bloom filter is stored per column chunk as a separate data block in the file. The `ColumnIndex` and `OffsetIndex` structures reference bloom filter locations.

**Format**:
- Uses XxHash for hashing values.
- Stores the number of hash functions, seed, and bitset size in the bloom filter header.
- The bitset is stored as a sequence of bytes.

### Usage

When querying for a specific value:
1. Hash the value using the same hash functions as the bloom filter.
2. Check if all corresponding bits are set in the bitset.
3. If any bit is not set, the value is **definitely not** in the column chunk → skip it.
4. If all bits are set, the value **may** be present → read and scan the column chunk.

False positives are possible (bloom filter says "maybe" when value is absent); false negatives are not.

### Configuration

- Number of hash functions and bitset size should be tuned based on expected cardinality and acceptable false positive rate.
- Typical configuration: 10 bits per entry for ~1% false positive rate with 5 hash functions.

## Page Indexes

Page indexes enable readers to skip pages within a column chunk that cannot contain relevant data.

### Column Index

Stored as a separate data block. Contains one entry per data page in a column chunk:

- **`min_values`** / **`max_values`**: Min/max for each page (using column order).
- **`null_counts`**: Null count per page.
- **`null_pages`**: Boolean flags indicating if a page is entirely null.
- **`offsets`**: Offset index references.

Readers use min/max values to prune pages during filtered scans.

### Offset Index

Contains one entry per data page:

- **`column`**: Column path in schema.
- **`min_value`** / **`max_value`**: Per-page statistics (optional).
- **`offset`**: Byte offset of the page within the file.
- **`compressed_page_size` / `uncompressed_page_size`**: Page sizes.
- **`first_row_index`**: Row number of the first row in the page (within the row group).

Enables direct seeking to specific pages without scanning the entire column chunk.

## Size Statistics

The `SizeStatistics` struct provides metadata for estimating unencoded, uncompressed data size:

- **`unencoded_byte_array_data_bytes`**: Bytes for BYTE_ARRAY values assuming no encoding. Equivalent to `(PLAIN-encoded size) - (4 bytes * number of values)`.
- **`repetition_level_histogram`**: Count of each repetition level observed. Size = max_repetition_level + 1. Can be omitted if max_repetition_level is 0.
- **`definition_level_histogram`**: Count of each definition level observed. Can be omitted if max_definition_level is 0 or 1.

Useful for:
- Memory allocation estimates before decompression.
- Fine-grained filter pushdown on nested structures.
- Determining null counts and list lengths at specific nesting levels.

## Error Recovery

Parquet supports limited error recovery through checksums and page-level metadata:

- **CRC checksums**: Optional checksums for data pages (see Checksumming).
- **Page-level sizes**: Both compressed and uncompressed sizes are stored, allowing detection of corrupted pages.
- **Column chunk boundaries**: Known offsets allow skipping corrupted column chunks without invalidating the entire file.

Readers should handle:
- Missing optional fields gracefully.
- Unknown encodings or compression codecs (skip the column/page).
- Truncated files (process complete row groups/column chunks before the truncation point).
