# Types and Schema

## Contents
- Physical Types
- Logical Types
- String Types
- Numeric Types
- Temporal Types
- Nested Types (LIST, MAP)
- Embedded Types
- Geospatial Types
- Variant Type
- Schema Definition

## Physical Types

Parquet's on-disk types are minimal, focusing on storage efficiency:

| Physical Type | Description |
|---|---|
| `BOOLEAN` | 1-bit boolean value |
| `INT32` | 32-bit signed integer |
| `INT64` | 64-bit signed integer |
| `INT96` | 96-bit signed integer (deprecated; only legacy implementations) |
| `FLOAT` | IEEE 754 32-bit floating point |
| `DOUBLE` | IEEE 754 64-bit floating point |
| `BYTE_ARRAY` | Arbitrarily long byte arrays (length-prefixed) |
| `FIXED_LEN_BYTE_ARRAY` | Fixed-length byte arrays |

16-bit integers are not a separate type — they use `INT32` with efficient encoding.

## Logical Types

Logical types annotate physical types to express higher-level semantics without adding new physical storage formats. Two representations exist:

- **`LogicalType`** — Current representation. A union of structs allowing type parameters (e.g., decimal precision/scale, timestamp unit).
- **`ConvertedType`** — Deprecated enum. Writers must write both `LogicalType` and corresponding `ConvertedType` for backward compatibility. Readers should interpret `ConvertedType` the same way as `LogicalType` when `LogicalType` is absent.

## String Types

### STRING
- Annotates `BYTE_ARRAY` as UTF-8 encoded character string.
- Sort order: unsigned byte-wise comparison.
- Corresponds to `UTF8` ConvertedType.

### ENUM
- Annotates `BYTE_ARRAY` for enumerated types from other data models (Thrift, Avro, Protobuf).
- Applications without native enum support should interpret as UTF-8 string.
- Sort order: unsigned byte-wise comparison.

### UUID
- Annotates 16-byte `FIXED_LEN_BYTE_ARRAY`.
- Encoded big-endian: `00112233-4455-6677-8899-aabbccddeeff` → bytes `00 11 22 33 ...`.
- Sort order: unsigned byte-wise comparison.

## Numeric Types

### Signed Integers — `INT(bitWidth, isSigned=true)`
- Bit widths: 8, 16, 32, 64.
- `INT(8, true)`, `INT(16, true)`, `INT(32, true)` → physical `INT32`.
- `INT(64, true)` → physical `INT64`.
- Sort order: signed.

### Unsigned Integers — `INT(bitWidth, isSigned=false)`
- Same physical type mapping as signed.
- Sort order: unsigned.

### Deprecated ConvertedType integers
`INT_8`, `INT_16`, `INT_32`, `INT_64`, `UINT_8`, `UINT_16`, `UINT_32`, `UINT_64` map to the corresponding `INT` logical types.

### DECIMAL
Represents arbitrary-precision signed decimals: `unscaledValue * 10^(-scale)`.

- **`INT32`**: precision 1–9.
- **`INT64`**: precision 1–18 (precision < 10 produces a warning).
- **`FIXED_LEN_BYTE_ARRAY`**: precision limited by array size. Length `n` stores ≤ `floor(log10(2^(8n-1) - 1))` digits.
- **`BYTE_ARRAY`**: unlimited precision. Use minimum bytes for unscaled value.
- Unscaled value stored as two's complement, big-endian.
- Scale defaults to 0. Precision is required and must be a positive integer.
- Sort order: signed comparison of the represented value.

### FLOAT16
- Half-precision floating-point in 2-byte IEEE little-endian format.
- Physical type: 2-byte `FIXED_LEN_BYTE_ARRAY`.
- Sort order: signed with special NaN/signed zero handling (use IEEE754TotalOrder).

## Temporal Types

### DATE
- Days since Unix epoch (1970-01-01), stored as `INT32`.
- Sort order: signed.

### TIME
- Time without date. Parameters: `isAdjustedToUTC` (boolean), `unit` (`MILLIS`, `MICROS`, `NANOS`).
- `MILLIS` → `INT32` (milliseconds after midnight).
- `MICROS` / `NANOS` → `INT64`.
- Sort order: signed.

### TIMESTAMP
- Parameters: `isAdjustedToUTC` (boolean), `unit` (`MILLIS`, `MICROS`, `NANOS`).
- Stored as `INT64`.

**Instant semantics (`isAdjustedToUTC=true`)**: Value is milliseconds/microseconds/nanoseconds since Unix epoch (1970-01-01 00:00:00 UTC). Each value unambiguously identifies a single instant on the timeline.

**Local semantics (`isAdjustedToUTC=false`)**: Represents local datetime fields regardless of timezone. Does not identify an unambiguous instant. Reference point is 1970-01-01 00:00:00 (local, no UTC).

- `NANOS` unit range: 1677-09-21 to 2262-04-11.
- Sort order: signed.

### INTERVAL
- Duration of time. Physical type: `FIXED_LEN_BYTE_ARRAY` of length 12.
- Stores three little-endian unsigned integers: months, days, milliseconds.
- Each component is independent (no fixed conversion between months and days).
- Sort order: undefined. Do not write min/max statistics.

## Embedded Types

### JSON
- Annotates `BYTE_ARRAY` as UTF-8 encoded valid JSON document.
- Sort order: unsigned byte-wise comparison.

### BSON
- Annotates `BYTE_ARRAY` as encoded BSON document per [BSON spec](http://bsonspec.org/spec.html).
- Sort order: unsigned byte-wise comparison.

## Geospatial Types

### GEOMETRY
- Well-Known Binary (WKB) format with linear/planar edge interpolation.
- Physical type: `BYTE_ARRAY`.
- Parameter: `crs` (optional, defaults to `"OGC:CRS84"` — longitude/latitude on WGS84).
- Sort order: undefined. No min/max statistics.

### GEOGRAPHY
- WKB format with explicit (non-linear/non-planar) edge interpolation.
- Physical type: `BYTE_ARRAY`.
- Parameters: `crs` (optional, defaults to `"OGC:CRS84"`), `algorithm` (`SPHERICAL`, `VINCENTY`, `THOMAS`, `ANDOYER`, `KARNEY`; defaults to `SPHERICAL`).
- CRS must be geographic with longitudes [-180, 180] and latitudes [-90, 90].
- Sort order: undefined. No min/max statistics.

## Variant Type

`VARIANT` annotates a group containing `metadata` (required `binary`) and `value` (optional `binary`). Used for storing either unshredded or shredded Variant values per the [Variant binary encoding specification](https://github.com/apache/parquet-format/blob/master/LogicalTypes.md).

Unshredded:
```
optional group variant (VARIANT(1)) {
  required binary metadata;
  required binary value;
}
```

Shredded: `value` field is optional and may be null when parts are shredded.

## Nested Types

### LIST

Must annotate a 3-level structure:

```
<repetition> group <name> (LIST) {
  repeated group list {
    <element-repetition> <element-type> element;
  }
}
```

- Outer level: `optional` or `required` (determines nullability of the list itself).
- Middle level: must be a `repeated` group named `list`.
- Inner level: `element` field with `required` or `optional` repetition.

**Backward-compatibility**: Older files may use 2-level structures or different field names. Readers should apply 5 backward-compatibility rules to determine element type and nullability.

### MAP

Must annotate a 3-level structure:

```
<repetition> group <name> (MAP) {
  repeated group key_value {
    required <key-type> key;
    <value-repetition> <value-type> value;
  }
}
```

- `key` field: always `required`, always first field.
- `value` field: can be `required`, `optional`, or omitted (all-null values / set of keys).
- If multiple key-value pairs share a key, the last value wins.

**Backward-compatibility**: Groups annotated with `MAP_KEY_VALUE` not contained by a `MAP` group should be treated as `MAP`.

## Schema Definition

Parquet schemas are defined in the Thrift file [`parquet.thrift`](https://github.com/apache/parquet-format/blob/master/src/main/thrift/parquet.thrift). Key structures:

- **`SchemaElement`**: Represents a node in the schema tree. Contains type, repetition type, name, num_children (for groups), and optional logical/converted type annotations.
- **`FieldRepetitionType`**: `REQUIRED`, `OPTIONAL`, `REPEATED`.
- Schema is stored as a flat list of `SchemaElement`s, with nesting tracked via `num_children`.

Implementations use the Thrift definition to serialize/deserialize file metadata. Code can be generated into any Thrift-supported language.
