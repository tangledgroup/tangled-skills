# Extensions and Configuration

## Contents
- Extension Overview
- Installing and Loading Extensions
- Autoloading
- Built-In vs Installable Extensions
- Community Extensions
- Listing Extensions
- Key Configuration Options
- Secrets Manager

## Extension Overview

DuckDB extensions add functionality beyond the core engine. Extensions are categorized as:

- **Built-in**: Statically linked into the binary, available immediately
- **Installable**: Downloaded and loaded on demand
- **Community**: Third-party extensions from the community repository

List available extensions:

```sql
SELECT extension_name, installed, description
FROM duckdb_extensions();
```

## Installing and Loading Extensions

Two-step process for installable extensions:

1. **INSTALL** — Downloads the extension binary and stores it locally (one-time)
2. **LOAD** — Dynamically loads the extension into the current DuckDB instance

```sql
INSTALL spatial;
LOAD spatial;
```

Subsequent `LOAD` or `INSTALL` calls are no-ops if already done.

### Extension Repository

Specify a custom repository:

```sql
INSTALL h3 FROM community;
-- Or direct URL
INSTALL my_ext FROM 'https://my-extensions.example.com';
```

## Autoloading

Many core extensions auto-install and auto-load when first used in a query:

```sql
-- httpfs extension is autoloaded automatically
SELECT * FROM 'https://example.com/data.parquet';
```

Not all extensions can be autoloaded. Some require explicit opt-in due to behavioral changes or technical constraints.

Control autoloading:

```sql
SET autoload_known_extensions = false;
SET autoinstall_known_extensions = false;
```

## Built-In vs Installable Extensions

Built-in extensions vary by platform distribution. Common built-in extensions include:
- `json` — JSON reading and processing
- `parquet` — Parquet file support
- `httpfs` — HTTP/HTTPS file access

For the full list of core extensions and which are built-in per platform, see the [core extensions documentation](https://duckdb.org/docs/current/core_extensions/overview).

## Community Extensions

Community extensions are third-party and maintained outside the core DuckDB repository.

```python
import duckdb

con = duckdb.connect()
con.install_extension("h3", repository="community")
con.load_extension("h3")
```

Allow community extensions (enabled by default):

```sql
SET allow_community_extensions = true;
```

## Listing Extensions

Check installed and available extensions:

```sql
SELECT extension_name, version, installed, description
FROM duckdb_extensions();
```

## Key Configuration Options

Configuration is set with `SET` and queried with `duckdb_settings()`:

```sql
SET threads = 1;
SET memory_limit = '2GB';
SELECT current_setting('threads');
```

### Access Control

| Option | Description | Default |
|--------|-------------|---------|
| `access_mode` | Database access: `AUTOMATIC`, `READ_ONLY`, `READ_WRITE` | `automatic` |
| `enable_external_access` | Allow file I/O, extension loading, COPY | `true` |
| `allowed_directories` | Directories always allowed even when external access disabled | `[]` |
| `allowed_paths` | Files always allowed even when external access disabled | `[]` |

### Performance

| Option | Description | Default |
|--------|-------------|---------|
| `threads` | Number of threads for parallel execution | CPU count |
| `memory_limit` | Maximum memory usage (e.g., `'4GB'`) | System-dependent |
| `checkpoint_threshold` | WAL size before auto-checkpoint | `16 MiB` |
| `disable_parquet_prefetching` | Disable Parquet prefetch optimization | `false` |

### Extensions

| Option | Description | Default |
|--------|-------------|---------|
| `allow_unsigned_extensions` | Load extensions without valid signatures | `false` |
| `allow_community_extensions` | Allow community-built extensions | `true` |
| `autoload_known_extensions` | Auto-load extensions on first use | `true` |
| `autoinstall_known_extensions` | Auto-install extensions on first use | `true` |

### Security

| Option | Description | Default |
|--------|-------------|---------|
| `allow_persistent_secrets` | Store secrets across restarts | `true` |
| `allow_unredacted_secrets` | Print secrets without masking | `false` |
| `enable_curl_server_cert_verification` | Verify SSL certificates for CURL | `true` |

### Query Behavior

| Option | Description | Default |
|--------|-------------|---------|
| `default_null_order` | NULL ordering: `NULLS_FIRST` or `NULLS_LAST` | `NULLS_LAST` |
| `default_order` | Default sort order: `ASCENDING` or `DESCENDING` | `ASCENDING` |
| `enable_progress_bar` | Show progress bar for long queries | `false` |

### Viewing All Settings

```sql
SELECT * FROM duckdb_settings();
```

Query specific settings:

```sql
SELECT * FROM duckdb_settings() WHERE name LIKE '%memory%';
```

Reset to default:

```sql
RESET memory_limit;
```

## Secrets Manager

DuckDB's Secrets Manager provides unified credential management for cloud storage backends.

Create a secret for AWS S3:

```sql
CREATE SECRET my_s3 (
    TYPE s3,
    KEY_ID 'AKIAIOSFODNN7EXAMPLE',
    SECRET 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
    REGION 'us-east-1'
);
```

Query using the secret:

```sql
SELECT * FROM 's3://my-bucket/data.parquet';
```

List secrets:

```sql
SELECT * FROM duckdb_secrets();
```

Drop a secret:

```sql
DROP SECRET my_s3;
```

Secrets can be stored persistently (controlled by `allow_persistent_secrets`) or session-scoped. The default storage backend is `local_file`, configurable via `default_secret_storage`.
