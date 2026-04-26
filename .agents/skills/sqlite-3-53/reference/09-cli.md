# Command-Line Interface

## Getting Started

The `sqlite3` program (or `sqlite3.exe` on Windows) provides an interactive SQL shell:

```bash
# Create or open a database
sqlite3 mydatabase.db

# In-memory database (discarded on exit)
sqlite3

# Read-only mode
sqlite3 --readonly mydatabase.db

# Execute a single command and exit
sqlite3 mydatabase.db "SELECT count(*) FROM users;"
```

A WASM build of the CLI runs in the browser at https://sqlite.org/fiddle.

## Dot-Commands

Dot-commands are special commands that start with `.` and are processed by the CLI itself (not passed to SQLite):

**Output formatting:**
- `.mode MODE` — Set output mode: `list`, `column`, `csv`, `html`, `json`, `tabs`, `line`, `quote`, `ascii`, `markdown`, `yaml`, `tcl`
- `.headers ON|OFF` — Show column headers
- `.separator SEP` — Set separator character (default: `|`)
- `.width N1 N2 ...` — Set column widths for column mode
- `.nullvalue STRING` — String to display for NULL values

**File I/O:**
- `.output FILENAME` — Send output to a file
- `.output stdout` — Resume output to terminal
- `.import FILE TABLE` — Import data from a file into a table
- `.dump ?TABLE?` — Output SQL text to recreate the database
- `.backup ?DB? FILE` — Create an online backup of the database
- `.restore FILE` — Restore database contents from a file

**Schema inspection:**
- `.tables ?PATTERN?` — List table names (optional LIKE pattern)
- `.schema ?TABLE?` — Show CREATE statements
- `.indices TABLE` — List indexes for a table
- `.databases` — List attached databases

**Execution:**
- `.read FILENAME` — Execute SQL from a file
- `.timer ON|OFF` — Turn CPU timer measurement on/off
- `.explain ON|OFF` — Enable EXPLAIN output mode
- `.eqp SELECT...` — Explain Query Plan

**Other:**
- `.help` — Show help
- `.quit` or `.exit` — Exit the program
- `.clone NEWDB` — Clone the database
- `.open ?FILE?` — Close and open a new database

## Output Modes

```bash
# Column mode (default, with headers)
sqlite> .mode column
sqlite> .headers on
sqlite> SELECT * FROM users LIMIT 3;
┌────┬─────────┬───────────────────┐
│ id │   name  │       email       │
├────┼─────────┼───────────────────┤
│  1 │ Alice   │ alice@example.com │
│  2 │ Bob     │ bob@example.com   │
│  3 │ Carol   │ carol@example.com │
└────┴─────────┴───────────────────┘

# CSV mode
sqlite> .mode csv
sqlite> .output results.csv
sqlite> SELECT * FROM users;

# JSON mode (available in recent versions)
sqlite> .mode json
sqlite> SELECT id, name FROM users LIMIT 2;
[{"id":1,"name":"Alice"},{"id":2,"name":"Bob"}]

# Markdown table
sqlite> .mode markdown
sqlite> SELECT id, name FROM users;
| id |   name  |
|----|---------|
|  1 | Alice   |
|  2 | Bob     |
```

## Importing and Exporting Data

**Import CSV:**
```bash
# Create the table first
sqlite> CREATE TABLE data (id INTEGER, name TEXT, value REAL);

# Import CSV file
sqlite> .import --csv data.csv data
```

The `--csv` flag tells the CLI to parse the file as CSV. Without it, the separator is determined by `.separator`.

**Export to CSV:**
```bash
sqlite> .mode csv
sqlite> .headers on
sqlite> .output export.csv
sqlite> SELECT * FROM users;
sqlite> .output stdout
```

**Dump schema and data:**
```bash
# Full database dump
sqlite3 mydatabase.db .dump > backup.sql

# Single table dump
sqlite3 mydatabase.db ".dump users"

# Restore from dump
sqlite3 new_database.db < backup.sql
```

## Scripting with sqlite3

Use sqlite3 in shell scripts for automated tasks:

```bash
#!/bin/bash
DB="mydatabase.db"

# Create database and table
sqlite3 "$DB" <<'EOF'
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY,
    timestamp TEXT DEFAULT (datetime('now')),
    level TEXT NOT NULL,
    message TEXT NOT NULL
);
EOF

# Query and process results
sqlite3 -separator '|' "$DB" "SELECT level, count(*) FROM logs GROUP BY level;" |
while IFS='|' read -r level count; do
    echo "Level $level: $count entries"
done
```

Command-line options for scripting:
- `-cmd CMD` — Run CMD before reading stdin
- `-bail` — Stop on first error
- `-batch` — Force batch I/O mode
- `-init FILE` — Read and execute SQL from FILE on startup
- `-header` — Turn headers on
- `-column` — Set default mode to column
- `-separator SEP` — Change separator for csv and list modes
- `-nullvalue STRING` — String to use in place of NULL values
- `-echo` — Print commands before execution
- `-html` — Emit HTML tables
- `-csv` — Set mode to CSV
- `-json` — Set mode to JSON

## Querying the Schema

The database schema is stored in special tables:

```sql
-- All schema objects
SELECT type, name, tbl_name, sql FROM sqlite_schema;

-- Just tables
SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%';

-- Table information
PRAGMA table_info(users);

-- Index information
PRAGMA index_list(users);
PRAGMA index_info(idx_users_email);
```

## Working with Multiple Databases

Attach additional databases:

```sql
ATTACH 'other_database.db' AS other;
SELECT * FROM main.users JOIN other.orders ON main.users.id = other.orders.user_id;
DETACH other;
```

## Safe Mode

The `--safe` flag restricts potentially dangerous operations:

```bash
sqlite3 --safe mydatabase.db
```

In safe mode, the following are disabled by default:
- Loading extensions
- Writing to files (`.output`, `.import`)
- Network access
- System command execution

Use `.unsafe CMD` to bypass restrictions for specific commands with explicit approval.
