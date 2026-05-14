# Upgrade and Troubleshooting

## Contents
- Upgrade Process
- Breaking Changes in v13.0
- Database Migrations
- Backup and Restore
- Common Issues

## Upgrade Process

Grafana upgrades are backward compatible — dashboards and graphs will not change. Test upgrades in a development environment first.

### Prerequisites

1. Back up the Grafana database and configuration
2. Review breaking changes for the target version
3. Ensure minimum hardware requirements are met
4. Check plugin compatibility with the new version

### Upgrade Steps (Debian/Ubuntu)

```bash
# Stop Grafana
sudo systemctl stop grafana-server

# Backup database
cp /var/lib/grafana/grafana.db /var/lib/grafana/grafana.db.bak

# Update package
sudo apt-get update
sudo apt-get install grafana

# Start Grafana (auto-migrates database)
sudo systemctl start grafana-server
```

### Upgrade Steps (Docker)

```bash
# Stop and remove old container
docker stop grafana
docker rm grafana

# Pull new image
docker pull grafana/grafana:13.0.1

# Run with existing volume
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -v grafana-data:/var/lib/grafana \
  grafana/grafana:13.0.1
```

The database migration runs automatically on startup. Monitor logs for migration progress:

```bash
docker logs -f grafana
```

### Upgrade Steps (Binary)

```bash
# Stop running instance
kill $(pgrep grafana-server)

# Download and extract new version
wget https://dl.grafana.com/oss/release/grafana-13.0.1-linux-amd64.tar.gz
tar -xzf grafana-13.0.1-linux-amd64.tar.gz

# Start new version (uses existing database)
cd grafana-13.0.1/
./bin/grafana-server web
```

## Breaking Changes in v13.0

Review the [What's new in Grafana v13.0](https://grafana.com/docs/grafana/latest/whatsnew/whats-new-in-v13-0/) for the complete list of breaking changes. Key areas to check:

- **Dynamic dashboards** — existing dashboards auto-migrate to new layout engine on first open
- **Docker image** — `grafana/grafana-oss` repository deprecated since v12.4.0; use `grafana/grafana` instead
- **Configuration changes** — some `grafana.ini` settings renamed or removed
- **Plugin API** — plugins may need updates for compatibility
- **Authentication** — changes to default authentication behavior

Always review the full changelog at the [Grafana GitHub repository](https://github.com/grafana/grafana/blob/main/CHANGELOG.md).

## Database Migrations

Grafana automatically runs database migrations on startup when a newer version detects an older schema. Migrations are applied in order and are generally safe.

### Manual Migration Check

Verify migration status:

```bash
# Check current database version
grafana-cli admin portions
```

### Migration Troubleshooting

If migrations fail:
1. Check Grafana logs for the specific migration error
2. Restore from backup if migration partially completed
3. Ensure the database backend (SQLite, MySQL, PostgreSQL) meets minimum version requirements
4. For large databases, migrations may take significant time — monitor disk I/O and memory

### Database Backend Requirements

| Backend | Minimum Version | Notes |
|---------|----------------|-------|
| SQLite3 | 3.x (bundled) | Default, suitable for small deployments |
| MySQL | 5.7+ | Use InnoDB engine |
| PostgreSQL | 9.2+ | Recommended for production |

## Backup and Restore

### What to Back Up

1. **Configuration files**:
   - `/etc/grafana/grafana.ini` (or `custom.ini`)
   - Provisioning directory: `/etc/grafana/provisioning/`
   - Dashboard JSON files if using file-based provisioning

2. **Database**:
   - SQLite: `/var/lib/grafana/grafana.db`
   - MySQL/PostgreSQL: dump via `mysqldump` or `pg_dump`

3. **Plugins**:
   - `/var/lib/grafana/plugins/`

4. **Provisioned dashboards and alert rules**

### Backup Script Example

```bash
#!/bin/bash
BACKUP_DIR="/backup/grafana-$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Config
cp /etc/grafana/grafana.ini "$BACKUP_DIR/" 2>/dev/null
cp -r /etc/grafana/provisioning/ "$BACKUP_DIR/" 2>/dev/null

# Database (SQLite)
cp /var/lib/grafana/grafana.db "$BACKUP_DIR/" 2>/dev/null

# Plugins list
grafana-cli plugins list > "$BACKUP_DIR/plugins.txt" 2>/dev/null

echo "Backup complete: $BACKUP_DIR"
```

### Restore

1. Stop Grafana
2. Restore configuration files
3. Restore database (replace `grafana.db` or import SQL dump)
4. Reinstall plugins from saved list
5. Start Grafana

## Common Issues

### Grafana Won't Start

- Check logs: `journalctl -u grafana-server` or `docker logs grafana`
- Verify configuration file syntax: invalid `grafana.ini` entries prevent startup
- Ensure the data directory is writable by the grafana user
- Check for port conflicts on the configured HTTP port

### Dashboard Queries Return No Data

- Verify data source connectivity: **Connections > Data sources > Save & test**
- Check time range in the dashboard matches available data
- Inspect raw query output using Query inspector in Explore
- Verify data source scrape/ingestion is running

### Slow Dashboard Loading

- Reduce the number of panels querying simultaneously
- Increase data source cache settings
- Use shorter default time ranges
- Check data source server performance independently
- Enable response caching in `grafana.ini`: `[datasources] cache_timeout = 300`

### Authentication Issues

- Verify `grafana.ini` auth settings match the intended provider
- For LDAP: check LDAP server connectivity and bind DN
- For OAuth: verify callback URLs and client credentials
- Check that anonymous access is configured correctly if enabled

### Plugin Installation Fails

- Ensure `grafana-cli` has network access to download plugins
- Check disk space in the plugins directory
- Run as root or the grafana user with proper permissions
- For unsigned plugins, add to `allow_loading_unsigned_plugins` in config
