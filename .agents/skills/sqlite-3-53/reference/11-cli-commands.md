# SQLite Command Line Interface (CLI)

Comprehensive reference for the SQLite3 command-line interface, including dot-commands, output modes, and interactive features.

## Quick Start

```bash
# Launch SQLite CLI with a database
sqlite3 mydatabase.db

# Create or open a database in read-write mode
sqlite3 -readonly database.db  # Read-only mode
sqlite3 :memory:               # In-memory database

# Execute single command and exit
sqlite3 database.db "SELECT * FROM users LIMIT 5;"

# Read SQL from a file
sqlite3 database.db < queries.sql

# Use here-document
sqlite3 database.db <<EOF
SELECT * FROM users;
.quit
EOF
```

## Dot-Commands (.commands)

Dot-commands are CLI-specific commands that start with `.` and are not part of SQL syntax.

### Database Management

```bash
# Show database information
.databases          # List all attached databases
.schema [pattern]   # Show CREATE statements for matching tables
.schema table_name  # Show schema for specific table

# Attach/detach databases
.attach 'path.db' as alias
.detach alias

# Backup and restore
.backup 'backup.db'              # Backup current database
.restore 'backup.db'             # Restore from backup file
.checkpoint [database]           # Run WAL checkpoint

# Dump and import
.dump [pattern]                  # Output SQL to recreate database
.read filename                   # Execute SQL from file
.source filename                 # Alias for .read
```

### Query Execution and Display

```bash
# Output modes
.mode list              # Default: column-separated output
.mode column            # Padded columns with headers
.mode table             # ASCII table with borders
.mode html              # HTML <table> output
.mode insert table      # INSERT statements
.mode csv               # CSV format
.mode json              # JSON array output (SQLite 3.38.0+)
.mode tcl               # TCL list format

# Display options
.headers on|off         # Show column headers (default: off)
.separator col row      # Set column and row separators
.width col1 col2 ...    # Set column widths for .mode column
.linesize N             # Set limit for line wrapping

# Execution control
.bail on|off            # Stop on first error (default: off)
.echo on|off            # Print commands before execution
.timer on|off           # Show CPU and wall-clock time
.timeout MS             # Set lock timeout in milliseconds
```

### File Operations

```bash
# Output destination
.output filename        # Send output to file
.output stdout          # Send output to terminal (reset)

# Import/export
.import filename table  # Import CSV/data into table
.copy table filename    # Export table to file (SQLite 3.42.0+)

# File system
.files                  # Show open database files
```

### Debugging and Analysis

```bash
# Query analysis
.explain [query]        # Show query plan (EXPLAIN QUERY PLAN)
.analyze [table]        # Update query planner statistics

# Database inspection
.table_info table       # Show column info for table
.indices table          # List indexes on table
.foreign_key table      # Show foreign keys for table
.limit                 # Show current limits
.limit name value      # Set a limit

# Integrity and status
.integrity-check        # Verify database integrity
.quick-check            # Fast integrity check
.prAGMA [pragma]       # Execute pragma command
.status [verbose]      # Show CLI status information
```

### Session Control

```bash
# Exit and reset
.quit                   # Exit SQLite CLI
.exit                   # Alias for .quit
.reset                  # Reset all settings to defaults
.clone newdb.db         # Clone database (SQLite 3.41.0+)
```

### Advanced Features

```bash
# Shell integration
.shell command          # Execute shell command
.system command         # Alias for .shell

# Information
.help [command]         # Show help (or help for specific command)
.version               # Show SQLite version
.indices table          # List indexes on table

# Transaction control within CLI
.begin [transaction]    # BEGIN TRANSACTION
.commit                # COMMIT TRANSACTION
.rollback              # ROLLBACK TRANSACTION
```

## Output Modes in Detail

### List Mode (Default)

```bash
.mode list
.separator | \n         # Pipe-separated columns, newline rows
SELECT * FROM users;
# Output: 1|Alice|alice@example.com
```

### Column Mode

```bash
.mode column
.headers on
.width 5 20 30          # Set widths for first 3 columns
SELECT * FROM users;
# Output:
# id | name  | email                  
#---+-------+-------------------------
# 1  | Alice | alice@example.com      
```

### Table Mode

```bash
.mode table
.headers on
SELECT * FROM users;
# Output:
# ┌────┬───────┬─────────────────┐
# │ id │ name  │ email           │
# ├────┼───────┼─────────────────┤
# │ 1  │ Alice │ alice@example.com│
# └────┴───────┴─────────────────┘
```

### CSV Mode

```bash
.mode csv
.headers on
.output users.csv
SELECT * FROM users;
.output stdout
```

### JSON Mode (SQLite 3.38.0+)

```bash
.mode json
.headers on
SELECT * FROM users LIMIT 2;
# Output:
# [
#   {"id":1,"name":"Alice","email":"alice@example.com"},
#   {"id":2,"name":"Bob","email":"bob@example.com"}
# ]
```

### Insert Mode

```bash
.mode insert users
SELECT * FROM users;
# Output:
# INSERT INTO users VALUES(1,'Alice','alice@example.com');
# INSERT INTO users VALUES(2,'Bob','bob@example.com');
```

## CLI Options (Command Line Flags)

```bash
# Basic options
sqlite3 [OPTIONS] DATABASE [SQL]

# Common flags
-bail              # Quit after first SQL error
-init FILE         # Execute FILE before interactive mode
-readonly          # Open database read-only
-batch             # Force batch I/O mode
-heap SIZE         # Set initial heap size
-memsys ID         # Choose memory allocation system

# Output formatting
-header            # Print headers
-sep CHAR          # Set separator character (default: |)
-html              # Output in HTML format
-css FILE          # Use CSS file for HTML output
-width N           # Set screen width for wrapping

# Modern CLI options (SQLite 3.35.0+)
--align            # Enable auto-alignment
--border on|off    # Show table borders
--csv              # CSV output mode
--html             # HTML output mode
--json             # JSON output mode
--list             # List output mode
--once             # Execute SQL and quit
--quiet            # Suppress prompts and info messages
--table            # Table output mode
--verbose          # Print commands before execution

# Examples
sqlite3 --init ~/.sqliterc database.db      # Use config file
sqlite3 -readonly --csv database.db "SELECT * FROM users;" > out.csv
sqlite3 --json database.db "SELECT json_group_array(*) FROM users;"
```

## Interactive Features

### Tab Completion

```bash
# Enable tab completion (requires readline)
# Complete table names after FROM
SELECT * FROM <TAB>

# Complete column names after table.
SELECT users.<TAB>

# Complete SQL keywords
SE<TAB>  # SELECT, SET, etc.

# Complete dot-commands
.<TAB>   # .help, .headers, .mode, etc.
```

### History

```bash
# Command history is saved to ~/.sqlite_history
# Use up/down arrows to navigate history
```

### Multi-line Statements

```bash
# SQLite automatically detects incomplete statements
sqlite3> SELECT * FROM users
sqlite3> WHERE id > 10
sqlite3> LIMIT 5;
```

## Configuration File (~/.sqliterc)

Create `~/.sqliterc` to set default CLI options:

```bash
# ~/.sqliterc example
.headers on
.mode column
.width 10 20 30
.separator | 
.prompt_main "> "
.prompt_continue   "> "
.timer on
```

## Practical Examples

### Database Inspection Workflow

```bash
sqlite3 production.db
.dbinfo                    # Show database info
.databases                 # List attached databases
.schema users              # Show users table schema
.table_info users          # Show column details
.indices users             # Show indexes
.foreign_key users         # Show foreign keys
.quit
```

### Data Export Workflow

```bash
sqlite3 source.db <<EOF
.mode csv
.headers on
.output backup.csv
SELECT * FROM important_data;
.output stdout
.quit
EOF
```

### Query Analysis Workflow

```bash
sqlite3 database.db <<EOF
.timer on
.explain SELECT * FROM orders WHERE customer_id = 123;
.analyze
.explain SELECT * FROM orders WHERE customer_id = 123;
.quit
EOF
```

### Backup and Verification

```bash
sqlite3 production.db <<EOF
.backup 'production_backup.db'
.integrity-check
.quit
EOF
```

## Error Handling in CLI

```bash
# Stop on first error
.bail on

# Show errors with line numbers
.echo on

# Set timeout for locked databases
.timeout 5000

# Check for warnings
.prAGMA warning_log;  # If enabled
```

## Tips and Best Practices

1. **Use `.headers on`** - Always show column headers for clarity
2. **Set appropriate `.mode`** - Choose output format for your use case
3. **Use `.width` in column mode** - Prevents wrapping issues
4. **Enable `.timer on`** - Monitor query performance
5. **Use `.bail on` for scripts** - Fail fast on errors
6. **Set `.timeout` for production** - Avoid hanging on locks
7. **Initialize with config file** - Use `-init ~/.sqliterc` for defaults
8. **Use `.dump` for migrations** - Portable SQL output

## Differences from SQL

Remember that dot-commands are **not SQL** and will not work:
- In application code (only in CLI)
- Within SQL scripts executed via `EXECUTE IMMEDIATE`
- Through most database connectors

For programmatic access, use the equivalent C API functions or language-specific bindings.

## Related Documentation

- [C API Reference](02-c-api.md) - Programmatic database access
- [SQL Basics](01-sql-basics.md) - SQL language syntax
- [Administration](08-administration.md) - Database maintenance commands
