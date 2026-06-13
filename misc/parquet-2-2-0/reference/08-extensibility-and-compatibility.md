# Extensibility and Compatibility

## Contents
- Schema Migration
- Binary Protocol Extensions
- Implementation Status
- Cross-Implementation Compatibility

## Schema Migration

Parquet supports schema evolution through additive changes:

### Adding Columns
New columns can be added to the schema. Readers that don't recognize the new column simply ignore it. The new column's data is written in the row groups but older readers skip it using the schema structure.

### Removing Columns
Columns can be removed from the schema. Newer readers that expect a removed column will see it as all-null (if the column is optional) or fail (if required). Writers should not remove columns with active readers expecting them.

### Type Changes
Changing a column's type is **not** safe without coordination. Readers and writers must agree on compatible types. For example, changing `INT32` to `INT64` may work if all values fit in 32 bits, but the reverse will truncate data.

### Schema Merging
When reading files with different schemas, implementations can merge schemas by:
1. Unifying column sets (union of all schemas).
2. Treating missing columns as all-null.
3. Using `FieldId` annotations to match columns across schema versions.

## Binary Protocol Extensions

Parquet supports extending the file format through binary protocol extensions:

- **Custom metadata**: Key-value pairs at file, row group, and column chunk levels allow implementations to store custom information without breaking compatibility.
- **Unknown encodings**: Readers should skip pages with unknown encodings rather than failing.
- **Unknown compression codecs**: Similarly, readers should handle unknown codecs gracefully.

The format is designed so that new features can be added without requiring all implementations to support them simultaneously.

## Implementation Status

Not all Parquet implementations support the same features. Key areas of variation:

| Feature | Widespread Support | Limited Support |
|---|---|---|
| Physical types (BOOLEAN, INT32, INT64, FLOAT, DOUBLE, BYTE_ARRAY) | All | — |
| Logical types (STRING, INT, DECIMAL, DATE, TIMESTAMP) | Most | INTERVAL, UUID, FLOAT16 |
| Encodings (PLAIN, RLE, Dictionary) | All | Byte Stream Split |
| Compression (SNAPPY, GZIP, ZSTD) | Most | BROTLI, LZO |
| Data page v2 | Most | Some legacy readers only support v1 |
| Bloom filters | Growing | Not universal |
| Page indexes | Growing | Not universal |
| Encryption (AES/GCM, AES/S2E) | Limited | Most implementations |
| Geospatial types (GEOMETRY, GEOGRAPHY) | Limited | Most implementations |
| Variant type | Limited | Most implementations |

Check the [Implementation Status](https://parquet.apache.org/docs/file-format/implementationstatus/) page for current feature support across implementations.

## Cross-Implementation Compatibility

When integrating multiple Parquet implementations:

1. **Test interoperability**: Write files with one implementation, read with another. Verify data integrity and schema interpretation.
2. **Use common features**: Stick to widely-supported encodings (PLAIN, Dictionary, RLE) and compression (SNAPPY, ZSTD) for maximum compatibility.
3. **Avoid deprecated features**: Don't write INT96, use `RLE_DICTIONARY` instead of `PLAIN_DICTIONARY`, prefer `LZ4_RAW` over `LZ4`.
4. **Write both LogicalType and ConvertedType**: Ensures old readers can interpret new files.
5. **Use TYPE_DEFINED_ORDER column order**: Ensures correct min/max comparison for all logical types.

### Parquet Testing

The [parquet-testing](https://github.com/apache/parquet-testing) repository contains test files that verify implementations can read and write each other's files. Use these to validate compatibility.
