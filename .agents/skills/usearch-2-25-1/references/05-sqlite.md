# SQLite Extensions

> **Source:** https://github.com/unum-cloud/usearch
> **Loaded from:** SKILL.md (via progressive disclosure)

## Overview

USearch provides SQLite extensions that expose SIMD-accelerated distance functions directly in SQL. This enables vector search, fuzzy string matching, and geospatial queries without leaving the database. Functions come from NumKong (vectors) and StringZilla (strings), with AVX2, AVX-512, ARM NEON, and SVE acceleration.

## Installation

```sh
pip install usearch  # SQLite extensions are included in Python wheels
```

## Loading the Extension

```python
import sqlite3
import usearch

conn = sqlite3.connect(":memory:")
conn.enable_load_extension(True)
conn.load_extension(usearch.sqlite_path())
```

## Dense Vector Functions

Functions follow the naming pattern `distance_<metric>_<type>`:

- **Metrics:** `cosine`, `inner`, `sqeuclidean`, `divergence`
- **Types:** `f64`, `f32`, `f16`, `i8`

Available functions:
- `distance_sqeuclidean_f64`, `distance_cosine_f64`, `distance_inner_f64`, `distance_divergence_f64`
- `distance_sqeuclidean_f32`, `distance_cosine_f32`, `distance_inner_f32`, `distance_divergence_f32`
- `distance_sqeuclidean_f16`, `distance_cosine_f16`, `distance_inner_f16`, `distance_divergence_f16`
- `distance_sqeuclidean_i8`, `distance_cosine_i8`, `distance_inner_i8`, `distance_divergence_i8`

### Example: Cosine Distance on JSON Vectors

```sql
CREATE TABLE vectors_table (
    id INTEGER PRIMARY KEY,
    vector JSON NOT NULL
);

INSERT INTO vectors_table (id, vector)
VALUES
    (42, '[1.0, 2.0, 3.0]'),
    (43, '[4.0, 5.0, 6.0]');

SELECT
    id,
    distance_cosine_f32(vt.vector, '[7.0, 8.0, 9.0]') AS distance
FROM vectors_table AS vt
ORDER BY distance;
```

Vectors can be stored as BLOBs (most efficient) or JSONs (for compatibility).

## Binary Vector Functions

For bit-level similarity:

- `distance_hamming_binary` — Number of differing bits
- `distance_jaccard_binary` — Jaccard distance (differing bits / union bits)

```sql
CREATE TABLE binary_vectors (
    id INTEGER PRIMARY KEY,
    vector BLOB NOT NULL
);

INSERT INTO binary_vectors (id, vector)
VALUES
    (42, X'FFFFFF'),  -- 111111111111111111111111
    (43, X'000000');  -- 000000000000000000000000

SELECT
    bv.id,
    distance_hamming_binary(bv.vector, X'FFFF00') AS hamming_distance,
    distance_jaccard_binary(bv.vector, X'FFFF00') AS jaccard_distance
FROM binary_vectors AS bv;
```

## String Distance Functions

Four string distance functions, each with `_bytes` and `_unicode` variants:

- `distance_levenshtein_bytes` / `distance_levenshtein_unicode` — Edit distance (insertions, deletions, substitutions)
- `distance_hamming_bytes` / `distance_hamming_unicode` — Substitutions only

The `_bytes` variants count bytes; `_unicode` variants count Unicode code points (UTF-8 assumed).

```sql
CREATE TABLE strings_table (
    id INTEGER PRIMARY KEY,
    word TEXT NOT NULL
);

INSERT INTO strings_table (id, word)
VALUES
    (42, 'école'),   -- 6 code points, 7 bytes
    (43, 'école');    -- 5 code points, 6 bytes

SELECT
    st.id,
    distance_levenshtein_bytes(st.word, 'écolé') AS lb,
    distance_levenshtein_unicode(st.word, 'écolé') AS lu,
    distance_hamming_bytes(st.word, 'écolé') AS hb,
    distance_hamming_unicode(st.word, 'écolé') AS hu
FROM strings_table AS st;
```

### Bounded Distance (Early Stopping)

Pass a third argument to cap the maximum computed distance. Useful for autocomplete features:

```sql
SELECT
    distance_levenshtein_bytes(st.word, 'écolé', 2) AS lbb,
    distance_hamming_unicode(st.word, 'écolé', 2) AS hub
FROM strings_table AS st;
```

## Geographical Coordinates

- `distance_haversine_meters` — Haversine distance multiplied by Earth's radius in meters

```sql
SELECT
    id,
    distance_haversine_meters(
        location,
        '[40.7128, -74.0060]'  -- New York City
    ) AS distance_meters
FROM locations;
```

## Performance Notes

- BLOB storage is most efficient for vectors
- Functions are SIMD-accelerated (AVX2, AVX-512, NEON, SVE)
- Bounded distance functions use early stopping for faster autocomplete-style queries
- String functions handle UTF-8 encoding correctly with the `_unicode` variants
