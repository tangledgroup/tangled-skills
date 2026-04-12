# UI Applications

Third-party graphical applications for interacting with rqlite.

## Overview

Several third-party tools provide graphical interfaces for rqlite. These can be useful for:
- Ad-hoc queries and exploration
- Schema browsing and management
- Data visualization
- Administrative tasks

**Important:** Evaluate any third-party tool for:
- Security requirements and data protection
- Feature compatibility with your rqlite version
- Active maintenance and community support
- License terms appropriate for your use case

## Available Tools

### Dataflare

Web-based database management tool with rqlite support.

**Features:**
- Visual query builder
- Schema browser
- Data grid with filtering
- Multi-database support

**Connection:**
- Protocol: HTTP/HTTPS
- Supports TLS and authentication
- Compatible with rqlite clusters

**Use case:** Web-based administration without installing desktop software.

### LibSQL Studio

Modern database IDE with rqlite connectivity.

**Features:**
- SQL editor with syntax highlighting
- Query result visualization
- Schema management
- Multi-tab interface

**Connection:**
- Direct HTTP API connection
- Supports read consistency levels
- Cluster node selection

**Use case:** Desktop application for development and administration.

### Generic SQLite Tools (Limited Support)

Some standard SQLite tools can connect to rqlite with modifications:

**DB Browser for SQLite:**
- Can read rqlite database files directly (read-only only!)
- ⚠️ **Warning:** Follow [Direct Access](18-direct-access.md) guidelines
- Not recommended for production use

**SQLite Command-Line:**
- Can query via HTTP API using custom wrappers
- Requires scripting to translate SQL to HTTP requests

## Security Considerations

### Data Protection

When using third-party UI tools:

1. **Encrypt connections:** Always use HTTPS/TLS
   ```bash
   rqlited -http-cert=/path/to/cert.pem -http-key=/path/to/key.pem ...
   ```

2. **Use authentication:** Require username/password
   ```bash
   rqlited -auth=/path/to/auth.json ...
   ```

3. **Limit permissions:** Create read-only users for UI tools
   ```json
   {
     "users": {
       "ui_user": {
         "password": "...",
         "permissions": ["status", "query"]
       }
     }
   }
   ```

4. **Network isolation:** Restrict UI tool access to trusted networks
   ```bash
   # Firewall rule example
   iptables -A INPUT -p tcp --dport 4001 -s 10.0.0.0/24 -j ACCEPT
   ```

### Audit Logging

Enable logging to track UI tool activity:

```bash
rqlited -log-level=info ...
```

Monitor logs for:
- Unusual query patterns
- Access from unexpected IPs
- Failed authentication attempts

## Best Practices

### Development vs Production

**Development:**
- UI tools are convenient for exploration
- Can use less restrictive security
- Helpful for schema design and testing

**Production:**
- Prefer HTTP API for application access
- Use UI tools only for administration
- Implement strict access controls
- Audit all UI tool usage

### Read-Only Access for UI Tools

Create dedicated read-only users for UI applications:

```json
// auth.json
{
  "users": {
    "admin": {
      "password": "${ADMIN_PASSWORD}",
      "permissions": ["status", "query", "execute", "remove_node"]
    },
    "ui_readonly": {
      "password": "${UI_PASSWORD}",
      "permissions": ["status", "query"]
    }
  }
}
```

### Use Read-Only Nodes

For heavy UI tool usage, connect to read-only nodes:

```bash
# Start read-only node
rqlited -node-id=ui-node \
  -join=leader:4002 \
  -raft-voter=false \
  /var/lib/rqlite/ui-node

# Connect UI tool to read-only node
# Doesn't affect cluster consensus performance
```

## Alternatives to Third-Party Tools

### Built-in rqlite Shell

rqlite includes a powerful command-line interface:

```bash
rqlite -H localhost -u admin:password

# Interactive features
.tables          # List tables
.schema          # Show schema
.nodes           # Cluster status
.backup file.db  # Create backup
```

See [rqlite Shell](02-shell.md) for details.

### Custom Web Interface

Build simple web interface using HTTP API:

```html
<!DOCTYPE html>
<html>
<body>
  <textarea id="query">SELECT * FROM users</textarea>
  <button onclick="runQuery()">Run</button>
  <pre id="results"></pre>
  
  <script>
    async function runQuery() {
      const q = document.getElementById('query').value;
      const resp = await fetch(`/db/query?q=${encodeURIComponent(q)}`);
      const data = await resp.json();
      document.getElementById('results').textContent = JSON.stringify(data, null, 2);
    }
  </script>
</body>
</html>
```

### API Clients and Libraries

Use official client libraries for programmatic access:

- **Go:** `github.com/rqlite/gorqlite`
- **Python:** `rqlite-client`
- **JavaScript:** `rqlite`
- **Java:** `rqlite-java`

See [Client Libraries](https://rqlite.io/docs/api/client-libraries/) for complete list.

## Troubleshooting

### Connection Failed

**Check:**
- rqlite node is running: `curl http://localhost:4001/status`
- Correct host/port in UI tool configuration
- Network connectivity: `telnet host 4001`
- Firewall rules allow connection

### Authentication Error

**Verify:**
- Username/password correct
- User has required permissions
- Auth file loaded by rqlite: `-auth=/path/to/auth.json`

### TLS/SSL Errors

**Ensure:**
- Using HTTPS in UI tool configuration
- CA certificate trusted
- Certificate not expired
- Hostname matches certificate

## Next Steps

- Use [rqlite shell](02-shell.md) for built-in CLI access
- Configure [security](08-security.md) for UI tool connections
- Set up [monitoring](10-monitoring.md) to track UI usage
- Implement [CDC](11-cdc.md) for real-time dashboards
