# Caddyfile Directives Reference

### Core HTTP Directives

| Directive | Type | Description |
|-----------|------|-------------|
| `respond` | Handler | Return a fixed response |
| `redir` | Handler | Redirect requests |
| `file_server` | Handler | Serve static files |
| `reverse_proxy` | Handler | Proxy to upstream servers |
| `abort` | Handler | Abort the request immediately |
| `error` | Handler | Generate an error response |
| `route` | Container | Group directives with custom order |
| `handle` | Container | Match and group directives |
| `handle_path` | Container | Strip prefix and match |
| `vars` | Handler | Set variables/placeholders |
| `log` | Config | Configure access logging |
| `skip_log` | Handler | Skip logging for matched requests |

### TLS Directives

| Directive | Type | Description |
|-----------|------|-------------|
| `tls` | Config | Configure TLS certificates and settings |
| `bind` | Config | Specify network interfaces and protocols |

### Authentication & Security

| Directive | Type | Description |
|-----------|------|-------------|
| `basicauth` | Handler | HTTP Basic Authentication |
| `forward_auth` | Handler | Forward authentication to external service |

### Advanced Directives

| Directive | Type | Description |
|-----------|------|-------------|
| `handle_errors` | Config | Configure error page handling |
| `invoke` | Handler | Invoke another named route |
| `templates` | Handler | Render Go templates and markdown with frontmatter |
| `request_body` | Handler | Read request body into variable |
