# Data Types

## Contents
- Scalar Types
- Nested and Composite Types
- Typecasting
- Performance Considerations

## Scalar Types

### Numeric Types

| Type | Aliases | Size | Description |
|------|---------|------|-------------|
| `TINYINT` | `INT1` | 1 byte | Signed one-byte integer |
| `SMALLINT` | `INT2`, `SHORT` | 2 bytes | Signed two-byte integer |
| `INTEGER` | `INT4`, `INT`, `SIGNED` | 4 bytes | Signed four-byte integer |
| `BIGINT` | `INT8`, `LONG` | 8 bytes | Signed eight-byte integer |
| `HUGEINT` | — | 16 bytes | Signed sixteen-byte integer |
| `UTINYINT` | — | 1 byte | Unsigned one-byte integer |
| `USMALLINT` | — | 2 bytes | Unsigned two-byte integer |
| `UINTEGER` | — | 4 bytes | Unsigned four-byte integer |
| `UBIGINT` | — | 8 bytes | Unsigned eight-byte integer |
| `UHUGEINT` | — | 16 bytes | Unsigned sixteen-byte integer |
| `FLOAT` | `FLOAT4`, `REAL` | 4 bytes | Single precision float |
| `DOUBLE` | `FLOAT8` | 8 bytes | Double precision float |
| `DECIMAL(p,s)` | `NUMERIC(p,s)` | variable | Fixed-precision, default prec=18, scale=3 |
| `BIGNUM` | — | variable | Variable-length integer |

### String Types

| Type | Aliases | Description |
|------|---------|-------------|
| `VARCHAR` | `CHAR`, `BPCHAR`, `TEXT`, `STRING` | Variable-length character string |
| `BLOB` | `BYTEA`, `BINARY`, `VARBINARY` | Variable-length binary data |
| `BIT` | `BITSTRING` | String of 1s and 0s |

### Date and Time Types

| Type | Aliases | Description |
|------|---------|-------------|
| `DATE` | — | Calendar date (year, month, day) |
| `TIME` | — | Time of day (no time zone) |
| `TIMESTAMP` | `DATETIME` | Date and time combination |
| `TIMESTAMP WITH TIME ZONE` | `TIMESTAMPTZ` | Date and time with time zone |
| `INTERVAL` | — | Date/time delta |

### Other Scalar Types

| Type | Description |
|------|-------------|
| `BOOLEAN` | `true` / `false`, aliases: `BOOL`, `LOGICAL` |
| `UUID` | Universally unique identifier |
| `JSON` | JSON object (requires `json` extension) |

## Nested and Composite Types

DuckDB supports six nested data types that can be arbitrarily nested.

### ARRAY — Fixed-Length Ordered Sequence

Fixed number of elements, all same type:

```sql
-- Build from values
SELECT [1, 2, 3];

-- Define in DDL
CREATE TABLE data (scores INTEGER[3]);
```

Each row must have the same number of elements. Arrays use **1-based indexing**.

### LIST — Variable-Length Ordered Sequence

Variable number of elements, all same type:

```sql
SELECT [1, 2, 3];
CREATE TABLE data (tags VARCHAR[]);
```

Each row can have different numbers of elements. Lists use **1-based indexing**.

### MAP — Key-Value Dictionary

Keys share one type, values share another type:

```sql
-- Build from values
SELECT map([1, 2], ['a', 'b']);

-- Define in DDL
CREATE TABLE data (metadata MAP(INTEGER, VARCHAR));
```

MAP keys are **case-sensitive**. Rows may have different keys.

### STRUCT — Named Field Dictionary

Named fields where each field can have a different type:

```sql
-- Build from values
SELECT {'name': 'Alice', 'age': 30};

-- Define in DDL
CREATE TABLE data (info STRUCT(name VARCHAR, age INTEGER));
```

STRUCT keys are **case-insensitive**. Each row must have the same keys.

### UNION — Alternative Type Storage

Stores one of multiple alternative types per value:

```sql
SELECT union_value(num := 42);
SELECT union_value(str := 'hello')::UNION(str VARCHAR, num INTEGER);
CREATE TABLE data (val UNION(text VARCHAR, count INTEGER));
```

Each row can hold a different member type. Includes a discriminator "tag" to inspect the active member.

### VARIANT — Semi-Structured Type

Self-contained values with embedded type information:

```sql
SELECT 42::VARIANT;
SELECT 'hello'::VARIANT;
CREATE TABLE data (payload VARIANT);
```

Each row may hold a value of any type. Useful for semi-structured data like JSON fields.

### Nesting Examples

Struct with lists:

```sql
SELECT {'birds': ['duck', 'goose'], 'amphibians': ['frog', 'toad']};
```

List of maps:

```sql
SELECT [map([1, 5], [42.1, 45]), map([2, 3], [10.0, 20.0])];
```

## Typecasting

Implicit and explicit typecasting between types:

```sql
-- Explicit cast
SELECT '42'::INTEGER;
SELECT CAST('2024-01-15' AS DATE);

-- Implicit cast (string to integer in arithmetic)
SELECT '10' + 5;  -- returns 15
```

Key casting rules:
- Strings cast to numeric types if the string represents a valid number
- `TIMESTAMP` and `TIMESTAMPTZ` cast based on time zone context
- Python `int` values try casts in order: `BIGINT` → `INTEGER` → `UBIGINT` → `UINTEGER` → `DOUBLE`
- Python `float` values try: `DOUBLE` → `FLOAT`

## Performance Considerations

Data type choice strongly affects query performance:
- Use the smallest sufficient integer type (`TINYINT` over `BIGINT` when values fit)
- Prefer `TIMESTAMP` over `TIMESTAMPTZ` when time zones are not needed
- Nested types add overhead — flatten structures when querying large datasets
- `VARIANT` is convenient but slower than typed columns for analytical queries
