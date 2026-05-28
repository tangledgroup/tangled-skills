# Metadata and File Layout

## Contents
- File Structure
- File Footer
- Schema Elements
- Key-Value Metadata
- Thrift Definition

## File Structure

A Parquet file has a fixed layout:

```
4-byte magic number "PAR1"
<Column 1 Chunk 1>
<Column 2 Chunk 1>
...
<Column N Chunk 1>       // Row Group 1
<Column 1 Chunk 2>
<Column 2 Chunk 2>
...
<Column N Chunk 2>       // Row Group 2
...
<Column 1 Chunk M>
...
<Column N Chunk M>       // Row Group M
<File Metadata>
4-byte length of file metadata (little-endian)
4-byte magic number "PAR1"
```

- File metadata is written **after** all data, enabling single-pass writing.
- Readers first seek to the end, read the 4-byte length + 4-byte magic, then read the metadata to locate column chunks.
- Columns are stored contiguously per row group (all of column 1's chunk, then all of column 2's chunk, etc.).

## File Footer

The file footer (`FileMetaData` struct) contains:

- **version**: Format version (currently 2 or 3).
- **schema**: List of `SchemaElement`s defining the file's schema.
- **num_rows**: Total number of rows in the file.
- **row_groups**: List of `RowGroup` structs, one per row group.
- **key_value_metadata**: Optional list of key-value pairs (arbitrary user metadata).
- **created_by**: Application that created the file (e.g., "parquet-mr version 1.12.0").
- **encryption_type** / **encryption_footer**: For encrypted files (AES/GCM or AES/S2E).

### Row Group

Each `RowGroup` contains:

- **columns**: List of `ColumnMetaData` (one per column in the schema).
- **sorting_columns**: Optional sort order within the row group.
- **total_byte_count**: Total bytes in the row group.
- **num_rows**: Number of rows in this row group.
- **file_offset** / **file_path**: For files split across multiple physical files.

## Schema Elements

Schema is represented as a flat list of `SchemaElement`s:

```thrift
struct SchemaElement {
  1: optional i32 type            // Physical type (for leaf nodes)
  2: optional i32 type_length     // Max length for BYTE_ARRAY / FIXED_LEN_BYTE_ARRAY
  3: optional i32 repetition_type // REQUIRED, OPTIONAL, REPEATED
  4: required string name         // Field name
  5: optional i32 num_children    // Number of children (for groups)
  6: optional ConvertedType converted_type  // Deprecated logical type
  7: optional i32 scale           // For DECIMAL
  8: optional i32 precision       // For DECIMAL
  9: optional string original_name // Original field name (e.g., from JSON)
  10: optional LogicalType logical_type     // Current logical type
  11: optional list<FieldId> field_ids     // Field IDs for schema merging
}
```

- Root element is a group with no name and `num_children` equal to the number of top-level fields.
- Nesting is tracked by `num_children` — a group's children follow it consecutively in the flat list.
- Leaf nodes have a physical type; group nodes do not.

## Key-Value Metadata

Arbitrary key-value string pairs stored at file level, row group level, and column chunk level. Common uses:

- Producer application identification.
- Custom tags for data lineage or partition information.
- Schema version tracking.

Both keys and values are UTF-8 strings. No schema enforcement — consumers ignore unknown keys.

## Thrift Definition

The complete metadata schema is defined in [`parquet.thrift`](https://github.com/apache/parquet-format/blob/master/src/main/thrift/parquet.thrift) (1442 lines). This Thrift file:

- Defines all structs: `FileMetaData`, `RowGroup`, `ColumnMetaData`, `PageHeader`, `SchemaElement`, `Statistics`, etc.
- Can be compiled into any Thrift-supported language (Java, C++, Python, Go, Rust, etc.).
- Is the authoritative reference for metadata field names, types, and optional/required status.

To generate bindings:
```bash
thrift --out . --gen <language> parquet.thrift
```

The Thrift definition is necessary for developing software that reads or writes Parquet files. The parquet-format repository does not contain library implementations — only the specification and Thrift definitions.
