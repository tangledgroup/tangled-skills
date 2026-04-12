# JSON and JSONB Functions

Complete reference for SQLite's JSON processing capabilities, including both text-based JSON and binary JSON (JSONB) formats, with examples for data extraction, modification, validation, and transformation.

## Overview

SQLite 3.53 provides thirty functions and two operators for JSON processing:

- **28 scalar functions** for creating, extracting, and modifying JSON
- **4 table-valued functions** for decomposing JSON into rows
- **2 PostgreSQL-compatible operators** (`->` and `->>`)
- **JSONB support** for efficient binary storage and manipulation

### JSON vs JSONB

| Feature | JSON (Text) | JSONB (Binary) |
|---------|-------------|----------------|
| Storage | Text string | Binary format |
| Read performance | Slower (parsing required) | Faster (pre-parsed) |
| Write performance | Faster (no conversion) | Slower (conversion required) |
| Size | Larger (text overhead) | Smaller (compact binary) |
| Use case | Infrequent updates, storage efficiency not critical | Frequent modifications, query performance |

## Interface Overview

### JSON Arguments

JSON functions accept these argument types:

```sql
-- Text JSON (most common)
SELECT json('{"name": "Alice", "age": 30}');

-- NULL becomes JSON null
SELECT json(NULL);  -- Returns: null

-- Empty string is an error
SELECT json('');  -- Error: Invalid JSON

-- BLOB input (treated as UTF-8 text)
SELECT json(X'7B226E616D65223A202254657374227D');  -- {"name": "Test"}
```

### PATH Arguments

JSON path expressions follow JSON Pointer syntax (RFC 6901):

```sql
-- Root level
SELECT json_extract('{"a": 1}', '$');     -- Returns entire object: {"a": 1}

-- Object member
SELECT json_extract('{"a": 1}', '$.a');   -- Returns: 1

-- Nested path
SELECT json_extract('{"a": {"b": 2}}', '$.a.b');  -- Returns: 2

-- Array element (0-indexed)
SELECT json_extract('[1, 2, 3]', '$[0]');   -- Returns: 1
SELECT json_extract('[1, 2, 3]', '$[1]');   -- Returns: 2

-- Nested array access
SELECT json_extract('{"items": [1, 2, 3]}', '$.items[0]');  -- Returns: 1

-- Wildcard (returns array of all matches)
SELECT json_extract('[1, 2, 3]', '$[*]');   -- Returns: [1, 2, 3]

-- Multiple paths (returns array)
SELECT json_extract('{"a": 1, "b": 2}', '$.a, $.b');  -- Returns: [1, 2]
```

### Special Path Escaping

```sql
-- Escape tilde in keys (~ becomes ~0, / becomes ~1)
SELECT json_extract('{"a/b": 1}', '$.a~1b');      -- Key is "a/b"
SELECT json_extract('{"a~b": 1}', '$.a~0b');      -- Key is "a~b"

-- Array indices can be negative (from end)
SELECT json_extract('[1, 2, 3]', '$[-1]');   -- Returns: 3 (last element)
SELECT json_extract('[1, 2, 3]', '$[-2]');   -- Returns: 2
```

## Core JSON Functions

### json() - Canonicalize JSON

Converts any valid JSON to canonical text format:

```sql
-- Normalize whitespace
SELECT json('{"a":  1, "b" : 2}');  
-- Returns: {"a":1,"b":2}

-- Convert NULL to JSON null
SELECT json(NULL);  -- Returns: null

-- Validate and reformat
SELECT json('  [  1  ,  2  ,  3  ] ');  -- Returns: [1,2,3]

-- Error on invalid JSON
SELECT json('{invalid}');  -- Error: Invalid JSON
```

### jsonb() - Convert to Binary JSON

Converts text JSON to binary JSONB format:

```sql
-- Create JSONB from text
SELECT jsonb('{"name": "Alice", "age": 30}');

-- Store in table
CREATE TABLE users (id INTEGER PRIMARY KEY, data JSONB);
INSERT INTO users VALUES (1, jsonb('{"name": "Bob", "active": true}'));

-- JSONB is more compact
SELECT length('{"a":1,"b":2}') AS text_size;      -- e.g., 13 bytes
SELECT length(jsonb('{"a":1,"b":2}')) AS jsonb_size;  -- e.g., 10 bytes

-- JSONB operations are faster for repeated modifications
UPDATE users SET data = jsonb_set(data, '$.age', 31) WHERE id = 1;
```

### json_valid() - Validate JSON

Returns 1 if input is valid JSON, 0 otherwise:

```sql
-- Valid JSON
SELECT json_valid('{"name": "Alice"}');     -- Returns: 1
SELECT json_valid('[1, 2, 3]');             -- Returns: 1
SELECT json_valid('"hello"');               -- Returns: 1
SELECT json_valid('123');                   -- Returns: 1
SELECT json_valid('true');                  -- Returns: 1
SELECT json_valid('null');                  -- Returns: 1

-- Invalid JSON
SELECT json_valid('{invalid}');             -- Returns: 0
SELECT json_valid('[1, 2, 3');              -- Returns: 1 (missing bracket)
SELECT json_valid('');                      -- Returns: 0 (empty string)

-- NULL is valid (becomes JSON null)
SELECT json_valid(NULL);                    -- Returns: 1
```

### json_error_position() - Locate JSON Errors

Returns the character position where a JSON parsing error occurs:

```sql
-- Find error location
SELECT json_error_position('[1, 2, 3');           -- Returns: 8 (missing ']')
SELECT json_error_position('{"a": }');            -- Returns: 6 (missing value)
SELECT json_error_position('{"a" 1}');            -- Returns: 5 (missing ':')

-- Valid JSON returns NULL
SELECT json_error_position('{"a": 1}');           -- Returns: NULL
```

## JSON Extraction Functions

### json_extract() - Extract Values

Extracts values from JSON using path expressions:

```sql
-- Basic extraction
SELECT json_extract('{"name": "Alice", "age": 30}', '$.name');  -- "Alice"
SELECT json_extract('{"name": "Alice", "age": 30}', '$.age');   -- 30

-- Nested extraction
SELECT json_extract('{"user": {"name": "Bob", "contact": {"email": "bob@example.com"}}}', 
    '$.user.name');              -- "Bob"
SELECT json_extract('{"user": {"name": "Bob", "contact": {"email": "bob@example.com"}}}', 
    '$.user.contact.email');     -- "bob@example.com"

-- Array extraction
SELECT json_extract('[10, 20, 30]', '$[0]');   -- 10
SELECT json_extract('[10, 20, 30]', '$[1]');   -- 20
SELECT json_extract('[10, 20, 30]', '$[2]');   -- 30

-- Multiple paths (returns array)
SELECT json_extract('{"a": 1, "b": 2, "c": 3}', '$.a, $.b');  -- [1,2]

-- Non-existent path returns NULL
SELECT json_extract('{"a": 1}', '$.b');        -- NULL

-- Extract entire document
SELECT json_extract('{"a": 1}', '$');          -- {"a":1}
```

### jsonb_extract() - Binary JSON Extraction

Same as json_extract() but operates on JSONB data:

```sql
-- Create JSONB and extract
WITH data AS (
    SELECT jsonb('{"products": [{"name": "Widget", "price": 9.99}, {"name": "Gadget", "price": 14.99}]}') AS jsonb_data
)
SELECT jsonb_extract(jsonb_data, '$.products[0].name') FROM data;  -- "Widget"
SELECT jsonb_extract(jsonb_data, '$.products[1].price') FROM data; -- 14.99

-- More efficient for repeated extractions from same data
CREATE TABLE orders (id INTEGER PRIMARY KEY, data JSONB);
INSERT INTO orders VALUES (1, jsonb('{"items": [{"sku": "A", "qty": 2}, {"sku": "B", "qty": 5}]}'));

SELECT jsonb_extract(data, '$.items[0].sku') FROM orders;  -- "A"
SELECT jsonb_extract(data, '$.items[1].qty') FROM orders;  -- 5
```

### PostgreSQL-Style Operators

SQLite supports PostgreSQL-compatible JSON operators:

```sql
-- -> operator (returns JSON)
SELECT '{"a": 1, "b": 2}'->'$.a';      -- Returns: 1 (as JSON)
SELECT '[1, 2, 3]'->'$[0]';            -- Returns: 1 (as JSON)

-- ->> operator (returns text)
SELECT '{"name": "Alice"}'->>'$.name';  -- Returns: Alice (text, no quotes)
SELECT '[1, 2, 3]'->>'$[1]';            -- Returns: 2 (text)

-- Use in WHERE clauses
SELECT * FROM users 
WHERE json_data->>'$.status' = 'active';

-- Chained operators
SELECT '{"a": {"b": {"c": 3}}}'->'$.a'->'$.b'->'$.c';  -- 3
```

## JSON Construction Functions

### json_array() - Create Array

Creates a JSON array from arguments:

```sql
-- Simple array
SELECT json_array(1, 2, 3);                    -- [1,2,3]
SELECT json_array('a', 'b', 'c');              -- ["a","b","c"]
SELECT json_array(1, 'two', 3.0, true, null);  -- [1,"two",3.0,true,null]

-- Nested arrays
SELECT json_array(json_array(1, 2), json_array(3, 4));  -- [[1,2],[3,4]]

-- Mixed types
SELECT json_array('string', 123, true, null, json_object('key', 'value'));
-- ["string",123,true,null,{"key":"value"}]

-- From query results
SELECT json_array(id, name, email) AS user_data
FROM users 
WHERE id IN (1, 2, 3);
```

### jsonb_array() - Binary Array

Creates a JSONB array (binary format):

```sql
-- Create JSONB array
SELECT jsonb_array(1, 2, 3);

-- More efficient for storage and repeated use
CREATE TABLE products (id INTEGER PRIMARY KEY, tags JSONB);
INSERT INTO products VALUES (1, jsonb_array('electronics', 'gadgets', 'sale'));

-- Query with JSONB array
SELECT * FROM products 
WHERE jsonb_extract(tags, '$[0]') = 'electronics';
```

### json_object() - Create Object

Creates a JSON object from key-value pairs:

```sql
-- Simple object
SELECT json_object('name', 'Alice', 'age', 30, 'active', 1);
-- Returns: {"name":"Alice","age":30,"active":1}

-- With NULL values (key is included with null value)
SELECT json_object('name', 'Bob', 'middle_name', NULL, 'age', 25);
-- Returns: {"name":"Bob","middle_name":null,"age":25}

-- With NULL key (key is omitted)
SELECT json_object(NULL, 'value1', 'key2', 'value2');
-- Returns: {"key2":"value2"}

-- Nested objects
SELECT json_object(
    'person', json_object('name', 'Alice', 'age', 30),
    'address', json_object('city', 'Boston', 'zip', '02101')
);

-- From query columns
SELECT 
    id,
    json_object(
        'user_id', id,
        'username', username,
        'email', email,
        'created', created_at
    ) AS user_json
FROM users;
```

### jsonb_object() - Binary Object

Creates a JSONB object (binary format):

```sql
-- Create JSONB object
SELECT jsonb_object('id', 1, 'name', 'Widget', 'price', 9.99);

-- Store in table
CREATE TABLE config (key TEXT PRIMARY KEY, value JSONB);
INSERT INTO config VALUES ('settings', jsonb_object('theme', 'dark', 'lang', 'en'));

-- Efficient for frequent modifications
UPDATE config 
SET value = jsonb_set(value, '$.theme', 'light')
WHERE key = 'settings';
```

## Array and Object Aggregate Functions

### json_group_array() - Aggregate into Array

Aggregates values into a JSON array:

```sql
-- Collect column values into array
SELECT 
    department,
    json_group_array(name) AS employees
FROM employees
GROUP BY department;

-- Result example:
-- engineering|["Alice","Bob","Charlie"]
-- sales|["Diana","Eve"]

-- Aggregate expressions
SELECT 
    category,
    json_group_array(price) AS prices,
    json_group_array(name || ' - $' || price) AS items
FROM products
GROUP BY category;

-- With ordering (requires subquery or window function)
SELECT 
    department,
    (SELECT json_group_array(name) 
     FROM employees e2 
     WHERE e2.department = e1.department 
     ORDER BY name) AS sorted_employees
FROM employees e1
GROUP BY department;
```

### jsonb_group_array() - Binary Aggregate Array

Aggregates into JSONB array format:

```sql
-- More efficient for large datasets
SELECT 
    category,
    jsonb_group_array(name) AS product_names
FROM products
GROUP BY category;
```

### json_group_object() - Aggregate into Object

Aggregates key-value pairs into a JSON object:

```sql
-- Create object from rows
SELECT json_group_object(key, value) AS config_object
FROM settings;

-- Result example: {"theme":"dark","lang":"en","notifications":true}

-- Build nested structure
SELECT 
    user_id,
    json_group_object(metric, value) AS metrics
FROM analytics
GROUP BY user_id;

-- Example result:
-- 1|{"page_views":150,"time_spent":320,"clicks":25}
-- 2|{"page_views":89,"time_spent":210,"clicks":12}
```

### jsonb_group_object() - Binary Aggregate Object

Aggregates into JSONB object format:

```sql
SELECT 
    product_id,
    jsonb_group_object(attribute, value) AS attributes
FROM product_features
GROUP BY product_id;
```

## JSON Modification Functions

### json_insert() - Insert Values

Inserts values into JSON at specified paths (doesn't overwrite existing):

```sql
-- Insert new key
SELECT json_insert(
    '{"name": "Alice"}', 
    '$.age', 30
);
-- Returns: {"name":"Alice","age":30}

-- Insert into array (at index)
SELECT json_insert(
    '[1, 2, 3]', 
    '$[1]', 99
);
-- Returns: [1,99,2,3] (inserts at position 1)

-- Multiple insertions
SELECT json_insert(
    '{"user": {"name": "Bob"}}',
    '$.user.age', 25,
    '$.user.active', true,
    '$.created', '2024-01-01'
);
-- Returns: {"user":{"name":"Bob","age":25,"active":true},"created":"2024-01-01"}

-- Error if path exists
SELECT json_insert('{"a": 1}', '$.a', 2);  -- Error: cannot insert, key exists

-- Use with table data
UPDATE users 
SET data = json_insert(
    COALESCE(data, '{}'),
    '$.last_login', datetime('now')
)
WHERE id = 1;
```

### jsonb_insert() - Binary Insert

Same as json_insert() but for JSONB:

```sql
-- More efficient for repeated modifications
UPDATE products
SET metadata = jsonb_insert(
    COALESCE(metadata, '{}'),
    '$.views', 
    (SELECT COALESCE(json_extract(metadata, '$.views'), 0) + 1 FROM products p2 WHERE p2.id = products.id)
)
WHERE id = 42;
```

### json_replace() - Replace Values

Replaces values at specified paths (requires path to exist):

```sql
-- Replace existing value
SELECT json_replace(
    '{"name": "Alice", "age": 30}', 
    '$.age', 31
);
-- Returns: {"name":"Alice","age":31}

-- Replace array element
SELECT json_replace(
    '[10, 20, 30]', 
    '$[1]', 25
);
-- Returns: [10,25,30]

-- Multiple replacements
SELECT json_replace(
    '{"user": {"name": "Bob", "age": 25}}',
    '$.user.age', 26,
    '$.user.active', false
);

-- Error if path doesn't exist
SELECT json_replace('{"a": 1}', '$.b', 2);  -- Error: key "b" doesn't exist
```

### jsonb_replace() - Binary Replace

Same as json_replace() but for JSONB:

```sql
UPDATE config
SET value = jsonb_replace(
    value,
    '$.settings.theme', 'dark'
)
WHERE key = 'app_config';
```

### json_set() - Set Values (Insert or Replace)

Combines insert and replace behavior:

```sql
-- Insert if doesn't exist, replace if does
SELECT json_set(
    '{"name": "Alice"}', 
    '$.age', 30          -- Insert (doesn't exist)
);
-- Returns: {"name":"Alice","age":30}

SELECT json_set(
    '{"name": "Alice", "age": 30}', 
    '$.age', 31          -- Replace (exists)
);
-- Returns: {"name":"Alice","age":31}

-- Multiple operations
SELECT json_set(
    '{"user": {"name": "Bob"}}',
    '$.user.age', 25,        -- Insert
    '$.user.name', 'Robert', -- Replace
    '$.created', '2024-01-01' -- Insert
);

-- Common pattern: update nested value
UPDATE users
SET data = json_set(
    COALESCE(data, '{}'),
    '$.profile.bio', 'Updated biography'
)
WHERE id = 1;
```

### jsonb_set() - Binary Set

Same as json_set() but for JSONB:

```sql
-- Efficient for frequent updates
UPDATE products
SET data = jsonb_set(
    data,
    '$.inventory.count', new_count,
    '$.inventory.last_updated', datetime('now')
)
WHERE id = product_id;
```

### json_remove() - Remove Values

Removes values at specified paths:

```sql
-- Remove single key
SELECT json_remove(
    '{"name": "Alice", "age": 30, "email": "alice@example.com"}',
    '$.age'
);
-- Returns: {"name":"Alice","email":"alice@example.com"}

-- Remove multiple keys
SELECT json_remove(
    '{"a": 1, "b": 2, "c": 3, "d": 4}',
    '$.b', '$.d'
);
-- Returns: {"a":1,"c":3}

-- Remove array element
SELECT json_remove('[10, 20, 30, 40]', '$[1]');
-- Returns: [10,30,40] (removes element at index 1)

-- Remove nested value
SELECT json_remove(
    '{"user": {"name": "Bob", "age": 25, "active": true}}',
    '$.user.age'
);
-- Returns: {"user":{"name":"Bob","active":true}}
```

### jsonb_remove() - Binary Remove

Same as json_remove() but for JSONB:

```sql
UPDATE users
SET data = jsonb_remove(data, '$.temporary_field')
WHERE id = 1;
```

### json_patch() - Apply RFC 6902 Patch

Applies a JSON Patch (RFC 6902) to a document:

```sql
-- Single operation patch
SELECT json_patch(
    '{"a": 1, "b": 2}',
    '[{"op": "replace", "path": "/a", "value": 10}]'
);
-- Returns: {"a":10,"b":2}

-- Multiple operations
SELECT json_patch(
    '{"name": "Alice", "age": 30}',
    '[
        {"op": "replace", "path": "/age", "value": 31},
        {"op": "add", "path": "/city", "value": "Boston"},
        {"op": "remove", "path": "/name"}
    ]'
);
-- Returns: {"age":31,"city":"Boston"}

-- Patch operations: add, remove, replace, move, copy, test
SELECT json_patch(
    '{"a": {"b": 1}}',
    '[{"op": "add", "path": "/a/c", "value": 2}]'
);
-- Returns: {"a":{"b":1,"c":2}}
```

### jsonb_patch() - Binary Patch

Same as json_patch() but for JSONB:

```sql
UPDATE documents
SET content = jsonb_patch(
    content,
    '[{"op": "replace", "path": "/status", "value": "published"}]'
)
WHERE id = 1;
```

## Table-Valued Functions

### json_each() - Decompose Array or Object

Returns a table with key, value, and path for each element:

```sql
-- Decompose array
SELECT * FROM json_each('[10, 20, 30]');
-- key | value | path
-- 0   | 10    | $[0]
-- 1   | 20    | $[1]
-- 2   | 30    | $[2]

-- Decompose object
SELECT * FROM json_each('{"name": "Alice", "age": 30}');
-- key | value | path
-- name| Alice | $.name
-- age | 30    | $.age

-- Use in queries
SELECT 
    p.name AS product,
    j.key AS tag,
    j.value AS tag_value
FROM products p, json_each(p.tags) j
WHERE j.value LIKE '%sale%';

-- Flatten nested array
SELECT 
    order_id,
    j.key AS item_index,
    j.value AS item_json
FROM orders, json_each(items) j;
```

### jsonb_each() - Binary Decomposition

Same as json_each() but for JSONB:

```sql
SELECT * FROM jsonb_each(jsonb('{"a": 1, "b": 2, "c": 3}'));
```

### json_tree() - Recursive Tree Traversal

Recursively traverses JSON structure:

```sql
-- Traverse entire document
SELECT * FROM json_tree('{"a": 1, "b": {"c": 2, "d": [3, 4]}}');

-- Columns: id, parent, key, type, value, path

-- Example output:
-- id | parent | key | type   | value | path
-- 1  | NULL   | NULL| object | {...} | $
-- 2  | 1      | a   | integer| 1     | $.a
-- 3  | 1      | b   | object | {...} | $.b
-- 4  | 3      | c   | integer| 2     | $.b.c
-- 5  | 3      | d   | array  | [...] | $.b.d
-- 6  | 5      | 0   | integer| 3     | $.b.d[0]
-- 7  | 5      | 1   | integer| 4     | $.b.d[1]

-- Find all values of specific type
SELECT path, value 
FROM json_tree(data) 
WHERE type = 'text' AND value LIKE '%search%';

-- Calculate document depth
WITH RECURSIVE tree_depth(id, depth) AS (
    SELECT id, 0 FROM json_tree('{"a": {"b": {"c": 1}}}') WHERE parent IS NULL
    UNION ALL
    SELECT jt.id, td.depth + 1 
    FROM json_tree jt
    JOIN tree_depth td ON jt.parent = td.id
)
SELECT MAX(depth) AS max_depth FROM tree_depth;
```

### jsonb_tree() - Binary Tree Traversal

Same as json_tree() but for JSONB:

```sql
SELECT * FROM jsonb_tree(jsonb('{"products": [{"name": "A", "price": 10}, {"name": "B", "price": 20}]}'));
```

## Utility Functions

### json_array_length() - Get Array Length

Returns the number of elements in a JSON array:

```sql
-- Simple array length
SELECT json_array_length('[1, 2, 3, 4, 5]');     -- Returns: 5
SELECT json_array_length('[]');                  -- Returns: 0

-- Nested path
SELECT json_array_length('{"items": [1, 2, 3]}', '$.items');  -- Returns: 3

-- Non-array returns NULL
SELECT json_array_length('{"a": 1}');             -- Returns: NULL
SELECT json_array_length('"string"');             -- Returns: NULL

-- In queries
SELECT 
    product_id,
    json_array_length(tags) AS tag_count
FROM products
WHERE json_array_length(tags) > 3;
```

### json_type() - Get JSON Type

Returns the type of a JSON value as text:

```sql
-- Type names: null, integer, real, boolean, string, array, object

SELECT json_type('null');           -- "null"
SELECT json_type('123');            -- "integer"
SELECT json_type('12.5');           -- "real"
SELECT json_type('true');           -- "boolean"
SELECT json_type('"hello"');        -- "string"
SELECT json_type('[1, 2]');         -- "array"
SELECT json_type('{"a": 1}');       -- "object"

-- With path
SELECT json_type('{"a": 1, "b": [1, 2]}', '$.a');   -- "integer"
SELECT json_type('{"a": 1, "b": [1, 2]}', '$.b');   -- "array"

-- Non-existent path returns NULL
SELECT json_type('{"a": 1}', '$.b');                -- NULL
```

### json_quote() - Quote String for JSON

Returns a quoted string suitable for embedding in JSON:

```sql
-- Basic quoting
SELECT json_quote('hello');           -- "hello"

-- Escape special characters
SELECT json_quote('say "hello"');     -- "say \"hello\""
SELECT json_quote('line1\nline2');    -- "line1\\nline2"
SELECT json_quote('backslash\\here'); -- "backslash\\\\here"

-- NULL returns JSON null
SELECT json_quote(NULL);              -- null

-- Numbers are not quoted
SELECT json_quote(123);               -- 123
```

### json_pretty() - Format JSON

Returns indented, human-readable JSON:

```sql
-- Compact JSON
SELECT '{"a":1,"b":{"c":2,"d":3},"e":[4,5,6]}';
-- Returns: {"a":1,"b":{"c":2,"d":3},"e":[4,5,6]}

-- Pretty-printed
SELECT json_pretty('{"a":1,"b":{"c":2,"d":3},"e":[4,5,6]}');
-- Returns:
-- {
--   "a": 1,
--   "b": {
--     "c": 2,
--     "d": 3
--   },
--   "e": [
--     4,
--     5,
--     6
--   ]
-- }

-- Useful for debugging
SELECT json_pretty(data) FROM users WHERE id = 1;
```

## JSON Array Insert Functions

### json_array_insert() - Insert into Array

Inserts values into a JSON array at specified positions:

```sql
-- Insert at beginning
SELECT json_array_insert('[2, 3]', '$[0]', 1);
-- Returns: [1,2,3]

-- Insert in middle
SELECT json_array_insert('[1, 3]', '$[1]', 2);
-- Returns: [1,2,3]

-- Insert at end (index = length)
SELECT json_array_insert('[1, 2]', '$[2]', 3);
-- Returns: [1,2,3]

-- Multiple insertions
SELECT json_array_insert(
    '[1, 4, 7]', 
    '$[1]', 2, '$[1]', 3, '$[4]', 8
);
-- Returns: [1,2,3,4,7,8]

-- Insert into nested array
SELECT json_array_insert(
    '{"items": [1, 4]}', 
    '$.items[1]', 2, '$.items[2]', 3
);
-- Returns: {"items":[1,2,3,4]}
```

### jsonb_array_insert() - Binary Array Insert

Same as json_array_insert() but for JSONB:

```sql
UPDATE products
SET tags = jsonb_array_insert(
    tags,
    '$[0]', 'featured'
)
WHERE id = 1;
```

## Examples and Patterns

### Storing Semi-Structured Data

```sql
-- Create table with JSON column
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    payload JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert structured data as JSON
INSERT INTO events (event_type, payload) VALUES 
    ('user_signup', json_object('user_id', 123, 'email', 'user@example.com', 'plan', 'premium')),
    ('purchase', json_object('product_id', 456, 'quantity', 2, 'total', 99.98)),
    ('page_view', json_object('path', '/products', 'referrer', 'google.com', 'duration', 45));

-- Query specific fields
SELECT 
    event_type,
    json_extract(payload, '$.user_id') AS user_id,
    created_at
FROM events
WHERE event_type = 'user_signup';

-- Search within JSON
SELECT * FROM events
WHERE json_extract(payload, '$.plan') = 'premium';

-- Index JSON field (SQLite 3.35+)
CREATE INDEX idx_events_user_id ON events(
    json_extract(payload, '$.user_id')
);
```

### Configuration Management

```sql
-- Store application configuration
CREATE TABLE app_config (
    key TEXT PRIMARY KEY,
    value JSONB,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert configuration
INSERT INTO app_config VALUES 
    ('features', jsonb_object('dark_mode', true, 'beta_features', false)),
    ('limits', jsonb_object('max_upload_mb', 100, 'api_rate_limit', 1000));

-- Update nested value
UPDATE app_config 
SET value = jsonb_set(value, '$.max_upload_mb', 500)
WHERE key = 'limits';

-- Read specific setting
SELECT json_extract(value, '$.dark_mode') AS dark_mode_enabled
FROM app_config
WHERE key = 'features';
```

### Audit Logging

```sql
-- Create audit log with JSON
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    old_values JSON,
    new_values JSON,
    user_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Log update
INSERT INTO audit_log (table_name, operation, old_values, new_values, user_id)
VALUES (
    'users',
    'UPDATE',
    json_object('status', 'active', 'role', 'user'),
    json_object('status', 'inactive', 'role', 'admin'),
    42
);

-- Find all changes to specific field
SELECT * FROM audit_log
WHERE 
    json_extract(old_values, '$.status') != json_extract(new_values, '$.status')
    AND table_name = 'users';
```

### Tagging System

```sql
-- Store tags as JSON array
CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT,
    tags JSONB DEFAULT '[]'
);

-- Insert with tags
INSERT INTO articles (title, tags) VALUES 
    ('SQLite Tutorial', jsonb_array('database', 'sqlite', 'beginner')),
    ('Advanced JSON', jsonb_array('json', 'advanced', 'data'));

-- Add tag to article
UPDATE articles
SET tags = jsonb_array_insert(tags, '$[3]', 'tutorial')
WHERE id = 1;

-- Find articles by tag
SELECT a.title, a.tags
FROM articles, json_each(a.tags) j
WHERE j.value = 'sqlite';

-- Count articles per tag
SELECT 
    j.value AS tag,
    COUNT(*) AS article_count
FROM articles, json_each(tags) j
GROUP BY j.value
ORDER BY article_count DESC;
```

## Performance Considerations

### When to Use JSONB

Use JSONB when:
- Frequent modifications to the same document
- Multiple extractions from same JSON value
- Storage size is a concern
- Query performance is critical

```sql
-- JSONB is faster for repeated operations
CREATE TABLE products (id INTEGER PRIMARY KEY, data JSONB);

-- Single conversion, multiple operations
INSERT INTO products SELECT id, jsonb(json_data) FROM temp_import;

-- Fast extraction from pre-converted JSONB
SELECT jsonb_extract(data, '$.price') FROM products WHERE category = 'electronics';
```

### Indexing JSON Fields

```sql
-- Create index on extracted JSON field
CREATE INDEX idx_users_status ON users(
    json_extract(data, '$.status')
);

-- Partial index for specific values
CREATE INDEX idx_active_users ON users(
    json_extract(data, '$.user_id')
) WHERE json_extract(data, '$.active') = 1;

-- Expression index (SQLite 3.9+)
CREATE VIRTUAL TABLE users_fts USING fts5(
    content,
    content='users',
    order='rowid'
);
```

### JSON in WHERE Clauses

```sql
-- Efficient filtering with indexed JSON field
SELECT * FROM orders
WHERE json_extract(data, '$.status') = 'completed'
  AND json_extract(data, '$.total') > 100;

-- Using ->> operator for text comparison
SELECT * FROM products
WHERE data->>'$.category' = 'electronics';
```

## Error Handling

### Common JSON Errors

```sql
-- Invalid JSON syntax
SELECT json('{invalid}');  
-- Error: Invalid JSON

-- Path doesn't exist (returns NULL, not error)
SELECT json_extract('{"a": 1}', '$.b');  -- Returns: NULL

-- Insert at existing path
SELECT json_insert('{"a": 1}', '$.a', 2);
-- Error: Cannot insert, key already exists

-- Replace non-existent path
SELECT json_replace('{"a": 1}', '$.b', 2);
-- Error: Cannot replace, key doesn't exist

-- Array index out of bounds (returns NULL)
SELECT json_extract('[1, 2]', '$[5]');  -- Returns: NULL
```

### Safe JSON Operations

```sql
-- Check validity before processing
SELECT 
    CASE 
        WHEN json_valid(data) THEN json_extract(data, '$.value')
        ELSE NULL
    END AS safe_value
FROM table;

-- Use COALESCE for default values
SELECT 
    COALESCE(json_extract(data, '$.optional'), 'default') AS value
FROM table;

-- Check path existence
SELECT * FROM table
WHERE json_extract(data, '$.required') IS NOT NULL;
```
