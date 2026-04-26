# R-Tree Module

## Overview

The R-Tree module is a virtual table that implements an R-Tree index structure for efficient multi-dimensional range queries. It is most commonly used in geospatial systems but also applies to time-domain ranges, collision detection, and any N-dimensional bounding-box search.

Compile with `-DSQLITE_ENABLE_RTREE=1` (included in the amalgamation but may not be enabled by default depending on build configuration).

## Creating an R-Tree Index

An R-Tree virtual table has an odd number of columns: one integer primary key plus pairs of min/max values for each dimension.

```sql
-- 2-dimensional R-Tree (5 columns)
CREATE VIRTUAL TABLE places USING rtree(
    id,            -- Primary key (64-bit signed integer)
    minX, maxX,    -- X dimension bounds
    minY, maxY     -- Y dimension bounds
);

-- 3-dimensional R-Tree (7 columns)
CREATE VIRTUAL TABLE volumes USING rtree(
    id,
    minX, maxX,
    minY, maxY,
    minZ, maxZ
);

-- 1-dimensional (time ranges)
CREATE VIRTUAL TABLE time_events USING rtree(
    id,
    startTime, endTime
);
```

Maximum supported dimensions: 5 (11 columns total).

## Populating an R-Tree

Insert bounding boxes as usual. For point data, use the same value for min and max:

```sql
-- Rectangle
INSERT INTO places VALUES(1, -122.5, -122.3, 37.7, 37.8);

-- Point (min = max)
INSERT INTO places VALUES(2, -122.4194, -122.4194, 37.7749, 37.7749);
```

## Querying an R-Tree

Range queries use comparison operators on the dimension columns:

```sql
-- Find all entries within a bounding box
SELECT id FROM places
WHERE minX >= -122.5 AND maxX <= -122.3
  AND minY >= 37.7  AND maxY <= 37.8;

-- Find overlapping entries
SELECT id FROM places
WHERE minX <= -122.3 AND maxX >= -122.5
  AND minY <= 37.8   AND maxY >= 37.7;
```

## Auxiliary Columns

R-Tree tables support auxiliary columns that store arbitrary data alongside the index:

```sql
CREATE VIRTUAL TABLE places USING rtree(
    id,
    minX, maxX,
    minY, maxY,
    name,          -- Auxiliary column
    description    -- Another auxiliary column
);

INSERT INTO places VALUES(1, -122.5, -122.3, 37.7, 37.8, 'San Francisco', 'City in California');
```

Auxiliary columns are stored in a separate shadow table and are not part of the R-Tree index structure.

Limitations:
- Auxiliary columns cannot be used in WHERE clause constraints for index optimization
- They can only be accessed through the virtual table interface
- Maximum number of auxiliary columns is limited by `SQLITE_MAX_COLUMN`

## Custom Geometry Queries

The R-Tree supports custom geometry callbacks for complex spatial queries. These are registered via the C API using `xQueryFunc`:

```c
// Example: Circle query callback
static int circleQuery(
    void *pContext,           // User data
    int nParam,               // Number of parameters
    sqlite3_value **apParam,  // Parameter values
    int (*xDistance)(void*, double*, double*),
    int *pResult              // Output: 0=outside, 1=inside, 2=overlap
) {
    double cx = sqlite3_value_double(apParam[0]);
    double cy = sqlite3_value_double(apParam[1]);
    double radius = sqlite3_value_double(apParam[2]);
    // Compute distance and set *pResult
}
```

Legacy geometry callbacks use the `xGeom` interface. The newer `xQueryFunc` is preferred.

## Shadow Tables

Each R-Tree virtual table creates several internal shadow tables:
- `%_node` — Stores the R-Tree node data
- `%_parent` — Parent pointers for each node
- `%_rowid` — Maps rowids to leaf entries
- `%_data` — Auxiliary column data (if any)

These tables are managed automatically and should not be modified directly.

## Integrity Check

Verify the R-Tree index integrity:

```sql
SELECT rtreecheck();
```

Returns 0 if the index is valid, or a non-zero error code.

## Roundoff Error

R-Tree coordinates are stored as IEEE 754 double-precision floating point. Be aware of floating-point precision issues when working with very large or very small coordinate values. For integer-valued coordinates, use integer types to avoid precision loss.
