# Pages and Column Chunks

## Contents
- Page Types
- Data Page v1
- Data Page v2
- Dictionary Pages
- Column Chunk Metadata
- Statistics

## Page Types

Column chunks are divided into pages — the indivisible unit of compression and encoding. Three page types:

| Page Type | Purpose |
|---|---|
| **Dictionary Page** | Stores the dictionary for dictionary-encoded columns. Written once, before data pages. |
| **Data Page v1** | Basic data page with definition/repetition levels, then values. |
| **Data Page v2** | Improved data page separating sizes of levels/values and supporting uncompressed data with compressed offsets. |

## Data Page v1

Layout:
```
<page header>
<definition levels>
<repetition levels>
<values>
```

- Definition and repetition levels are encoded using RLE/Bit-Packing (with 4-byte length prefix for v1).
- Values follow, encoded with the page's specified encoding.
- The entire page (levels + values) is compressed as one unit if compression is enabled.

## Data Page v2

Layout:
```
<page header>
  num_values
  serialization_size_of_definition_levels
  serialization_size_of_repetition_levels
  is_compressed
<definition levels>        // uncompressed
<repetition levels>        // uncompressed
<values>                   // compressed if is_compressed=true
```

Advantages over v1:
- Definition and repetition levels are **always uncompressed**, allowing fast decoding without decompressing the entire page.
- Only the values section is compressed (when `is_compressed` is true).
- Explicit size fields allow random access within the page.

## Dictionary Pages

Written once per column chunk, before any data pages. Contains all distinct dictionary entries stored using PLAIN encoding. The dictionary page itself can be compressed using the column chunk's compression codec.

Dictionary pages enable efficient encoding when cardinality is low (many repeated values). If cardinality is too high, writers fall back to PLAIN encoding in data pages and may omit the dictionary page entirely.

## Column Chunk Metadata

Each column chunk has a `ColumnMetaData` structure containing:

- **type**: Physical type of the column.
- **encodings**: List of encodings used in this column chunk (must include all encodings present in any page).
- **path_in_schema**: Path from root to this column (list of field names).
- **compression**: Compression codec used for this column chunk.
- **num_values**: Total number of values in the column chunk.
- **total_compressed_size** / **total_uncompressed_size**: Size metrics.
- **key_value_metadata**: Optional key-value pairs.
- **data_page_offset** / **index_page_offset** / **dictionary_page_offset**: Byte offsets within the file.
- **statistics**: Column-level statistics (see below).

## Statistics

Statistics are stored per row group (in column chunk metadata) and per page (in page headers). All fields are optional except where noted.

### Row Group Statistics (`Statistics` struct)

| Field | Type | Description |
|---|---|---|
| `max` / `min` | binary | Deprecated. Use `max_value` / `min_value`. PLAIN-encoded, no length prefix for byte arrays. Signed comparison only. |
| `null_count` | i64 | Count of null values. Writers SHOULD always write this. Readers MUST distinguish between absent and zero. |
| `distinct_count` | i64 | Count of distinct values. |
| `max_value` / `min_value` | binary | Min/max determined by the column's `ColumnOrder` (logical type-aware ordering). May be approximated values (e.g., "B" / "C" instead of full strings). |
| `max_is_exact` / `min_is_exact` | bool | Whether the value is the actual min/max or an approximation. |

### Page-Level Statistics

Same structure as row group statistics, stored in each data page header. Enables page-level pruning during reads.

### Column Order

Determines how min/max values are compared:

- **`TYPE_ORDER`**: Deprecated. Signed comparison for all types (incorrect for many logical types).
- **`UNSIGNED`**: Unsigned byte-wise comparison.
- **`TYPE_DEFINED_ORDER`**: Correct ordering per logical type. This is the recommended column order.
