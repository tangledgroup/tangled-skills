# Client APIs

## Python API

### Installation

```bash
pip install duckdb==1.5.2
```

Or with conda:
```bash
conda install python-duckdb -c conda-forge
```

**Python version**: Requires Python 3.9 or newer.

### Basic Usage

#### Quick Queries (In-Memory)

```python
import duckdb

# Simple query using global in-memory database
result = duckdb.sql("SELECT 42 AS answer")
result.show()

# Output:
# ┌────────┐
# │ answer │
# │ int32  │
# ├────────┤
# │     42 │
# └────────┘
```

#### Connection Management

```python
import duckdb

# In-memory database (default)
con = duckdb.connect()

# Persistent database
con = duckdb.connect('my_database.db')

# Using context manager (auto-closes)
with duckdb.connect('my_database.db') as con:
    con.sql("CREATE TABLE users (id INTEGER, name VARCHAR)")
    con.sql("INSERT INTO users VALUES (1, 'Alice')")

# Explicit close
con = duckdb.connect()
con.sql("SELECT 1")
con.close()
```

### Data Ingestion

#### From Files

```python
import duckdb

# CSV files
df = duckdb.read_csv('data.csv')
df = duckdb.read_csv('data.csv', header=True, delimiter=',')

# Parquet files
df = duckdb.read_parquet('data.parquet')
df = duckdb.read_parquet('data_*.parquet')  # Wildcard

# JSON files
df = duckdb.read_json('data.json')
df = duckdb.read_json_auto('data.json')  # Auto-detect schema

# Direct SQL on files
result = duckdb.sql("SELECT * FROM 'data.csv'")
result = duckdb.sql("SELECT * FROM read_csv('data.csv', header=false)")
```

#### From DataFrames

```python
import duckdb
import pandas as pd
import polars as pl
import pyarrow as pa

# Register Pandas DataFrame
pandas_df = pd.DataFrame({'a': [1, 2, 3], 'b': ['x', 'y', 'z']})
duckdb.sql("SELECT * FROM pandas_df WHERE a > 1").show()

# Register Polars DataFrame
polars_df = pl.DataFrame({'a': [1, 2, 3]})
duckdb.sql("SELECT SUM(a) FROM polars_df").show()

# Register PyArrow Table
arrow_table = pa.Table.from_pydict({'a': [1, 2, 3]})
duckdb.sql("SELECT * FROM arrow_table").show()

# Multiple DataFrames in one query
df1 = pd.DataFrame({'key': [1, 2], 'val1': [10, 20]})
df2 = pd.DataFrame({'key': [1, 2], 'val2': [100, 200]})
duckdb.sql("""
    SELECT df1.key, df1.val1, df2.val2
    FROM df1 JOIN df2 ON df1.key = df2.key
""").show()
```

### Result Conversion

```python
import duckdb

result = duckdb.sql("SELECT * FROM users")

# Convert to Pandas DataFrame
pandas_df = result.df()

# Convert to Polars DataFrame
polars_df = result.pl()

# Convert to PyArrow Table
arrow_table = result.arrow()

# Fetch as Python objects (list of tuples)
rows = result.fetchall()

# Fetch single row
row = result.fetchone()

# Fetch as NumPy arrays
numpy_arrays = result.fetchnumpy()

# Display in terminal
result.show()
result.show(max_rows=10, max_col_width=20)
```

### Writing Data

```python
import duckdb

# Write to Parquet
duckdb.sql("SELECT * FROM users").write_parquet('users.parquet')
duckdb.sql("SELECT * FROM users").write_parquet('users.parquet', compression='snappy')

# Write to CSV
duckdb.sql("SELECT * FROM users").write_csv('users.csv')
duckdb.sql("SELECT * FROM users").write_csv('users.csv', header=True, delimiter=',')

# Using COPY statement
duckdb.sql("COPY (SELECT * FROM users) TO 'users.csv' (HEADER)")
duckdb.sql("COPY (SELECT * FROM users) TO 'users.parquet'")
```

### Advanced Features

#### Prepared Statements

```python
import duckdb

con = duckdb.connect()

# Prepare statement
stmt = con.prepare("SELECT * FROM users WHERE age > ? AND city = ?")

# Execute with parameters
result = stmt.execute(18, 'NYC')
result.show()

# Reuse with different parameters
result = stmt.execute(25, 'LA')
result.show()
```

#### Transactions

```python
import duckdb

con = duckdb.connect('mydb.db')

# Begin transaction
con.begin()

try:
    con.sql("INSERT INTO users VALUES (1, 'Alice', 30)")
    con.sql("INSERT INTO users VALUES (2, 'Bob', 25)")
    con.commit()
except Exception as e:
    con.rollback()
    raise

# Using context manager
with con.transaction():
    con.sql("INSERT INTO users VALUES (3, 'Charlie', 35)")
```

#### Configuration

```python
import duckdb

# Set configuration at connection
con = duckdb.connect(
    'mydb.db',
    config={
        'memory_limit': '4GB',
        'threads': 4,
        'max_memory': '8GB'
    }
)

# Using PRAGMA
con.sql("PRAGMA memory_limit = '2GB'")
con.sql("PRAGMA threads = 2")

# Check current settings
con.sql("PRAGMA memory_limit").show()
con.sql("PRAGMA threads").show()
```

### DBAPI Compliance

DuckDB supports Python DBAPI 2.0:

```python
import duckdb

# Standard DBAPI usage
conn = duckdb.connect('mydb.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM users WHERE age > ?", (18,))
rows = cursor.fetchall()

cursor.execute("INSERT INTO users (name, age) VALUES (%s, %s)", ('Alice', 30))
conn.commit()

cursor.close()
conn.close()
```

### Relational API

For functional programming style:

```python
import duckdb

# Create relation from CSV
users = duckdb.read_csv('users.csv')

# Chain operations
result = (
    users
    .filter("age > 18")
    .select("name, email")
    .order_by("name")
    .limit(10)
)

# Execute and fetch
result.show()

# Join relations
orders = duckdb.read_csv('orders.csv')
joined = users.join(orders, "users.id = orders.user_id")
joined.show()
```

## R API

### Installation

```r
install.packages("duckdb")
```

### Basic Usage

```r
library(duckdb)

# Connect to database
con <- dbConnect(duckdb(), "mydb.db")

# Execute query
result <- dbExecute(con, "SELECT * FROM users WHERE age > 18")

# Fetch results
data <- dbFetch(result)

# Read CSV directly
data <- duckdb_read_csv("data.csv")

# Close connection
dbDisconnect(con)
```

### Duckplyr Integration

```r
library(duckdb)
library(dplyr)

# Use dplyr syntax with DuckDB backend
con <- dbConnect(duckdb(), ":memory:")

df %>%
  filter(age > 18) %>%
  select(name, email) %>%
  mutate(adult = TRUE) %>%
  collect(con)
```

## Java API (JDBC)

### Installation

Add to Maven `pom.xml`:

```xml
<dependency>
    <groupId>org.duckdb</groupId>
    <artifactId>duckdb_jdbc</artifactId>
    <version>1.5.2.0</version>
</dependency>
```

### Basic Usage

```java
import org.duckdb.DuckDBDriver;
import java.sql.*;

public class Example {
    public static void main(String[] args) throws SQLException {
        // Load driver
        Driver driver = new DuckDBDriver();
        
        // Connect to database
        Connection conn = ((DuckDBDriver) driver).connect("duckdb:mydb.db", null);
        
        // Execute query
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT * FROM users WHERE age > 18");
        
        // Process results
        while (rs.next()) {
            String name = rs.getString("name");
            int age = rs.getInt("age");
            System.out.println(name + ": " + age);
        }
        
        // Close resources
        rs.close();
        stmt.close();
        conn.close();
    }
}
```

### Prepared Statements

```java
String sql = "INSERT INTO users (name, age) VALUES (?, ?)";
PreparedStatement pstmt = conn.prepareStatement(sql);
pstmt.setString(1, "Alice");
pstmt.setInt(2, 30);
pstmt.executeUpdate();
```

## Node.js API

### Installation

```bash
npm install @duckdb/node-api
```

### Basic Usage

```javascript
const duckdb = require('@duckdb/node-api');

// Create connection
const db = new duckdb.Database('mydb.db');

// Execute query
const result = db.query("SELECT * FROM users WHERE age > 18");

// Get results as array
const rows = result.rows;
const columns = result.columns;

// Close database
db.close();
```

### Async API

```javascript
const duckdb = require('@duckdb/node-api');

async function queryDatabase() {
    const db = await duckdb.open('mydb.db');
    
    const result = await db.queryAsync("SELECT * FROM users");
    console.log(result.rows);
    
    await db.close();
}
```

## CLI (Command Line Interface)

### Installation

```bash
# macOS
brew install duckdb

# Linux (Ubuntu/Debian)
sudo apt install duckdb

# Or download from GitHub releases
wget https://github.com/duckdb/duckdb/releases/download/v1.5.2/duckdb_cli-linux-amd64.zip
```

### Basic Usage

```bash
# Start CLI with in-memory database
duckdb

# Start with persistent database
duckdb my_database.db

# Execute single query
duckdb -c "SELECT 42 AS answer"

# Execute query from file
duckdb mydb.db < queries.sql

# Read from stdin
echo "SELECT * FROM users;" | duckdb mydb.db
```

### CLI Commands

```sql
-- Inside DuckDB CLI

.list          -- List tables
.schema         -- Show schema
.help           -- Show all commands
.quit or .exit  -- Exit CLI

-- Output formatting
.mode table     -- Table format (default)
.mode csv       -- CSV format
.mode json      -- JSON format

-- Import/export
.output file.csv
SELECT * FROM users;
.output stdout

-- Timing
.timer on
.timer off
```

### Dot Commands

```sql
.read file.sql              -- Execute SQL from file
.dump                       -- Dump database as SQL
.backup 'backup.db'         -- Backup to file
.restore 'backup.db'        -- Restore from file
.headers on/off             -- Toggle headers
.width 10 20 30             -- Set column widths
```

## C/C++ API

### Building

```bash
git clone https://github.com/duckdb/duckdb.git
cd duckdb
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
```

### Basic Usage (C++)

```cpp
#include "duckdb.hpp"
#include <iostream>

int main() {
    // Create database and connection
    duckdb::Database db("mydb.db");
    duckdb::Connection con(db);
    
    // Execute query
    auto result = con.Query("SELECT * FROM users WHERE age > 18");
    
    // Iterate results
    idx_t row_count = result->RowCount();
    for (idx_t i = 0; i < row_count; i++) {
        std::string name = (*result)[1][i];
        std::cout << name << std::endl;
    }
    
    return 0;
}
```

### Prepared Statements (C)

```c
#include "duckdb.h"

duckdb_database database;
duckdb_connection connection;

duckdb_open("mydb.db", &database, NULL);
duckdb_connect(database, &connection, NULL);

duckdb_prepared_statement prepared;
const char *query = "SELECT * FROM users WHERE age > ?";
duckdb_prepare(connection, query, &prepared, NULL);

duckdb_parameter_value prepared_params[1];
prepared_params[0].value_type = DUCKDB_TYPE_INTEGER;
prepared_params[0].value = (void *)18;

duckdb_bind_parameter_data(prepared, 1, DUCKDB_TYPE_INTEGER, &prepared_params[0], sizeof(int));

duckdb_result result;
duckdb_execute_prepared(prepared, &result, NULL);

// Clean up
duckdb_destroy_result(&result);
duckdb_destroy_prepare(&prepared);
duckdb_disconnect(&connection, NULL);
duckdb_close(&database, NULL);
```

## Go API

### Installation

```bash
go get github.com/marcboeker/go-duckdb
```

### Basic Usage

```go
package main

import (
    "database/sql"
    _ "github.com/marcboeker/go-duckdb"
    "log"
)

func main() {
    db, err := sql.Open("duckdb", "mydb.db")
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    rows, err := db.Query("SELECT * FROM users WHERE age > ?", 18)
    if err != nil {
        log.Fatal(err)
    }
    defer rows.Close()

    for rows.Next() {
        var name string
        var age int
        if err := rows.Scan(&name, &age); err != nil {
            log.Fatal(err)
        }
        log.Printf("%s: %d", name, age)
    }
}
```

## Rust API

### Installation

Add to `Cargo.toml`:

```toml
[dependencies]
duckdb = "1.5.2"
```

### Basic Usage

```rust
use duckdb::Connection;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let conn = Connection::open("mydb.db")?;
    
    // Execute query
    let mut stmt = conn.prepare("SELECT * FROM users WHERE age > 18")?;
    let user_iter = stmt.query_map([], |row| {
        Ok((row.get::<_, String>(0)?, row.get::<_, i32>(1)?))
    })?;
    
    for user in user_iter {
        let (name, age) = user?;
        println!("{}: {}", name, age);
    }
    
    Ok(())
}
```

## WebAssembly (WASM)

### Browser Usage

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.jsdelivr.net/npm/duckdb-wasm@1.5.2/dist/duckdb.mjs"></script>
</head>
<body>
    <script type="module">
        import { DuckDB } from 'https://cdn.jsdelivr.net/npm/duckdb-wasm@1.5.2/dist/duckdb.mjs';
        
        const duckdb = new DuckDB();
        await duckdb.instantiate();
        
        const conn = duckdb.connect();
        const result = conn.query("SELECT 42 AS answer");
        console.log(result.rows);
    </script>
</body>
</html>
```

## API Comparison

| Feature | Python | R | Java | Node.js | CLI | C/C++ | Go | Rust |
|---------|--------|---|------|---------|-----|-------|----|----|
| Installation | pip | install.packages() | Maven | npm | brew/apt | build from source | go get | cargo |
| Query Execution | `sql()` | `dbExecute()` | `Statement` | `query()` | Direct | `Query()` | `db.Query()` | `conn.prepare()` |
| DataFrames | pandas/Polars | native | - | - | - | - | - | - |
| Prepared Statements | ✓ | ✓ | ✓ | ✓ | Limited | ✓ | ✓ | ✓ |
| Transactions | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Async Support | asyncio | - | JDBC async | async/await | - | - | goroutines | tokio |

## Best Practices

### Connection Management

1. **Use context managers** (Python) or try-with-resources (Java) for automatic cleanup
2. **Reuse connections** within a session rather than creating new ones
3. **Close connections explicitly** when done to release resources

### Performance

1. **Use prepared statements** for repeated queries with different parameters
2. **Batch operations** instead of row-by-row inserts
3. **Use COPY** for bulk data loading
4. **Leverage vectorized operations** in Python/R APIs

### Error Handling

```python
import duckdb
from duckdb import DuckDBException

try:
    result = duckdb.sql("SELECT * FROM nonexistent_table")
    result.fetchall()
except DuckDBException as e:
    print(f"Database error: {e}")
```
