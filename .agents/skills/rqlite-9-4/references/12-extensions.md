# SQLite Extensions

Extending rqlite functionality with SQLite extensions.

## Overview

rqlite supports loading SQLite extensions, allowing you to extend database capabilities beyond standard SQL. This includes vector search, cryptography, full-text search enhancements, and custom functions.

## Available Extensions

### Vector Search (sqlite-vec)

Add vector similarity search for AI/ML applications:

```sql
-- Load the extension
LOAD 'libsqlite_vec.so';

-- Create a table with vector column
CREATE TABLE documents (
  id INTEGER PRIMARY KEY,
  content TEXT,
  embedding vec(768)  -- 768-dimensional vector
);

-- Insert document with embedding
INSERT INTO documents (content, embedding) 
VALUES ('Machine learning tutorial', vec('[0.1, 0.2, ..., 0.9]'));

-- Find similar documents
SELECT id, content, vec_distance_cosine(embedding, vec('[0.15, 0.25, ..., 0.85]')) as similarity
FROM documents
ORDER BY similarity
LIMIT 10;
```

**Use cases:**
- Semantic search
- Recommendation systems
- Document similarity
- Image/video similarity (with embeddings)

### Cryptographic Functions (sqlean/crypto)

Add encryption and hashing functions:

```sql
-- Load crypto extension
LOAD 'libsqlcrypto.so';

-- Hash passwords
INSERT INTO users (username, password_hash) 
VALUES ('alice', crypto_pbkdf2('user_password', 'salt', 100000));

-- Verify passwords
SELECT * FROM users 
WHERE username = 'alice' 
AND crypto_pbkdf2('input_password', 'salt', 100000) = password_hash;

-- Encrypt sensitive data
INSERT INTO records (id, encrypted_data) 
VALUES (1, crypto_aes256_encrypt('sensitive_info', 'encryption_key'));

-- Decrypt data
SELECT crypto_aes256_decrypt(encrypted_data, 'encryption_key') as decrypted
FROM records WHERE id = 1;

-- Generate secure random values
SELECT crypto_random_bytes(16);  -- 16 bytes of random data
```

**Functions available:**
- `crypto_pbkdf2()` - Password hashing
- `crypto_aes256_encrypt/decrypt()` - AES encryption
- `crypto_hmac()` - HMAC signatures
- `crypto_random_bytes()` - Secure random generation

### Full-Text Search (FTS5)

SQLite includes FTS5 for advanced text search:

```sql
-- Create FTS5 virtual table
CREATE VIRTUAL TABLE documents_fts USING fts5(
  content,
  title,
  tokenize='porter'  -- Use Porter stemmer
);

-- Insert documents
INSERT INTO documents_fts (content, title) 
VALUES ('Machine learning basics', 'ML Introduction');
INSERT INTO documents_fts (content, title) 
VALUES ('Deep neural networks', 'Advanced ML');

-- Search for documents
SELECT * FROM documents_fts 
WHERE documents_fts MATCH 'machine AND learning';

-- Ranked search
SELECT rank, * FROM documents_fts 
WHERE documents_fts MATCH 'learning'
ORDER BY rank
LIMIT 10;

-- Phrase search
SELECT * FROM documents_fts 
WHERE documents_fts MATCH '"machine learning"';

-- Prefix search
SELECT * FROM documents_fts 
WHERE documents_fts MATCH 'learn*';
```

### Geographic Functions (spatialite)

Add GIS capabilities for location-based queries:

```sql
-- Load SpatiaLite extension
LOAD 'mod_spatialite.so';

-- Initialize spatialite
SELECT InitSpatialMetadata(0);

-- Create table with geometry
CREATE TABLE locations (
  id INTEGER PRIMARY KEY,
  name TEXT,
  point GEOMETRY
);

-- Add spatial index
SELECT AddGeometryColumn('locations', 'point', 4326, 'POINT', 2);

-- Insert location (WKT format)
INSERT INTO locations (name, point) 
VALUES ('New York', GeomFromText('POINT(-74.0060 40.7128)', 4326));

-- Find nearby locations
SELECT name, Distance(point, GeomFromText('POINT(-74.0000 40.7000)', 4326)) as distance_meters
FROM locations
WHERE Within(point, Buffer(GeomFromText('POINT(-74.0000 40.7000)', 4326), 10000))
ORDER BY distance_meters;
```

### JSON Functions (json1)

SQLite includes JSON support built-in:

```sql
-- Store JSON data
CREATE TABLE events (
  id INTEGER PRIMARY KEY,
  payload JSON
);

INSERT INTO events (payload) 
VALUES ('{"type": "click", "element": "button", "timestamp": 1234567890}');

-- Query JSON fields
SELECT json_extract(payload, '$.type') as event_type FROM events;
SELECT json_extract(payload, '$.element') as element FROM events;

-- Filter by JSON content
SELECT * FROM events 
WHERE json_extract(payload, '$.type') = 'click';

-- Update JSON field
UPDATE events 
SET payload = json_set(payload, '$.metadata', 'processed')
WHERE id = 1;

-- JSON aggregation
SELECT json_group_array(name) as names FROM users;
```

## Loading Extensions

### Command-Line Flag

Load extensions at startup:

```bash
rqlited -node-id=1 \
  -extension=/path/to/libsqlite_vec.so \
  -extension=/path/to/libsqlcrypto.so \
  /var/lib/rqlite/node1
```

### Multiple Extensions

```bash
rqlited -node-id=1 \
  -extension=/path/to/vec.so \
  -extension=/path/to/crypto.so \
  -extension=/path/to/spatialite.so \
  /var/lib/rqlite/node1
```

### Docker with Extensions

```yaml
version: '3'
services:
  rqlite:
    image: rqlite/rqlite:latest
    command:
      - "-node-id=1"
      - "-extension=/extensions/vec.so"
      - "-extension=/extensions/crypto.so"
    volumes:
      - ./data:/rqlite
      - ./extensions:/extensions:ro
```

## Building Custom Extensions

### Basic Extension Structure (C)

```c
#include "sqlite3ext.h"
SQLITE_EXTENSION_INIT1

// Custom function: double the input
static void doubleFunc(sqlite3_context *ctx, int argc, sqlite3_value **argv) {
    if (argc > 0 && sqlite3_value_type(argv[0]) == SQLITE_REAL) {
        double val = sqlite3_value_double(argv[0]) * 2.0;
        sqlite3_result_double(ctx, val);
    } else {
        sqlite3_result_null(ctx);
    }
}

// Register functions with SQLite
int sqlite3_extension_init(
    sqlite3 *db, 
    char **pzErrMsg, 
    const sqlite3_api_routines *pApi
) {
    SQLITE_EXTENSION_INIT2(pApi)
    
    return sqlite3_create_function(
        db, 
        "double_val", 
        1, 
        SQLITE_ANY, 
        NULL, 
        doubleFunc, 
        NULL, 
        NULL
    );
}
```

### Compile Extension

```bash
gcc -shared -fPIC -o libmyext.so myext.c \
  -I/usr/include/sqlite3 \
  -lsqlite3
```

### Load in rqlite

```bash
rqlited -node-id=1 \
  -extension=./libmyext.so \
  /var/lib/rqlite/node1
```

```sql
-- Use custom function
SELECT double_val(21);  -- Returns 42
```

## Extension Considerations for Clustering

### Deterministic Functions

Extensions used in clustered rqlite should be **deterministic** (same input always produces same output):

```sql
-- GOOD: Deterministic
SELECT crypto_sha256('fixed_input');  -- Always same result

-- BAD: Non-deterministic (may cause replication issues)
SELECT random_value();  -- Different on each node
```

### Read-Only vs Write Functions

- **Read functions** (SELECT): Safe to use in queries
- **Write functions** (INSERT/UPDATE): Replicated across cluster
- **Side-effect functions**: May behave unexpectedly in distributed setting

### Performance Impact

Extensions add overhead:
- Load time at startup
- Memory usage while loaded
- CPU for function execution

Profile extensions in production-like conditions.

## Use Case Examples

### AI-Powered Search

Combine vector search with traditional filtering:

```sql
-- Load vector extension
LOAD 'libsqlite_vec.so';

-- Create product catalog with embeddings
CREATE TABLE products (
  id INTEGER PRIMARY KEY,
  name TEXT,
  category TEXT,
  price REAL,
  embedding vec(768)
);

-- Find similar products in same category and price range
SELECT id, name, price, 
       vec_distance_cosine(embedding, vec('[0.1, 0.2, ..., 0.9]')) as similarity
FROM products
WHERE category = 'electronics'
  AND price BETWEEN 50 AND 200
ORDER BY similarity
LIMIT 10;
```

### Encrypted User Data

Store sensitive data encrypted at rest:

```sql
-- Load crypto extension
LOAD 'libsqlcrypto.so';

-- Create users table with encrypted fields
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username TEXT,
  ssn_encrypted BLOB,
  credit_card_encrypted BLOB
);

-- Insert with encryption
INSERT INTO users (username, ssn_encrypted, credit_card_encrypted)
VALUES (
  'alice',
  crypto_aes256_encrypt('123-45-6789', '$SSN_KEY'),
  crypto_aes256_encrypt('4111-1111-1111-1111', '$CC_KEY')
);

-- Decrypt for authorized access
SELECT 
  username,
  crypto_aes256_decrypt(ssn_encrypted, '$SSN_KEY') as ssn,
  crypto_aes256_decrypt(credit_card_encrypted, '$CC_KEY') as credit_card
FROM users WHERE id = 1;
```

### Geospatial Analytics

Location-based queries with clustering:

```sql
-- Load SpatiaLite
LOAD 'mod_spatialite.so';
SELECT InitSpatialMetadata(0);

-- Create delivery zones
CREATE TABLE deliveries (
  id INTEGER PRIMARY KEY,
  customer_name TEXT,
  location GEOMETRY,
  delivery_time TEXT
);
SELECT AddGeometryColumn('deliveries', 'location', 4326, 'POINT', 2);

-- Find all deliveries in a zone
SELECT customer_name, delivery_time,
       Distance(location, GeomFromText('POINT(-74.0060 40.7128)', 4326)) as distance
FROM deliveries
WHERE Within(location, 
  Buffer(GeomFromText('POINT(-74.0060 40.7128)', 4326), 5000))
ORDER BY distance;

-- Optimal route planning (simplified)
SELECT * FROM deliveries
WHERE Within(location, 
  Buffer(GeomFromText('POINT(-74.0060 40.7128)', 4326), 10000))
ORDER BY Azimuth(
  GeomFromText('POINT(-74.0060 40.7128)', 4326),
  location
);
```

### Audit Logging with Hashing

Create tamper-evident audit logs:

```sql
-- Load crypto extension
LOAD 'libsqlcrypto.so';

-- Create audit log with hash chain
CREATE TABLE audit_log (
  id INTEGER PRIMARY KEY,
  timestamp TEXT,
  action TEXT,
  details JSON,
  hash_chain TEXT
);

-- Insert audit entry with hash of previous entry
INSERT INTO audit_log (timestamp, action, details, hash_chain)
VALUES (
  datetime('now'),
  'USER_LOGIN',
  '{"user": "alice", "ip": "192.168.1.100"}',
  (
    SELECT crypto_sha256(
      COALESCE(MAX(hash_chain), '') || 
      datetime('now') || 
      'USER_LOGIN' || 
      '{"user": "alice", "ip": "192.168.1.100"}'
    )
    FROM audit_log
  )
);

-- Verify chain integrity
SELECT 
  id,
  hash_chain,
  crypto_sha256(
    LAG(hash_chain) OVER (ORDER BY id) ||
    timestamp || action || details
  ) as computed_hash
FROM audit_log;
-- All computed_hash should match the next row's hash_chain
```

## Troubleshooting Extensions

### Extension Won't Load

**Check path:**
```bash
ls -la /path/to/libextension.so
```

**Check architecture:**
```bash
file /path/to/libextension.so
# Should match rqlite architecture (x86_64, arm64, etc.)
```

**Check dependencies:**
```bash
ldd /path/to/libextension.so
# All dependencies should resolve
```

### Function Not Found

**Verify extension loaded:**
```sql
SELECT * FROM sqlite_master WHERE type='function';
-- Or check rqlite logs for load confirmation
```

**Check function name:**
```sql
-- List all available functions
SELECT name FROM sqlite_master 
UNION ALL 
SELECT 'double_val'  -- Your extension function names
```

### Performance Issues

**Profile extension usage:**
```sql
EXPLAIN QUERY PLAN
SELECT double_val(column) FROM large_table;
```

**Consider caching results** for expensive computations.

## Next Steps

- Set up [monitoring](10-monitoring.md) for extension performance
- Optimize [performance](09-performance.md) with extension usage patterns
- Configure [security](08-security.md) for cryptographic extensions
- Use [CDC](11-cdc.md) to stream extension-generated data
