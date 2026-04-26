# Caddyfile Reference

## Structure

The Caddyfile consists of an optional global options block, followed by one or more site blocks.

```caddy
{
    # Global options block — must be first if present
    email admin@example.com
}

# Snippets (optional, reusable blocks)
(logging) {
    log {
        output file /var/log/caddy.log
        format json
    }
}

# Named routes (experimental, v2.9.x+)
&(app-proxy) {
    reverse_proxy app-01:8080 app-02:8080
}

# Site blocks
example.com {
    root * /var/www
    file_server
    import logging
}

www.example.com {
    redir https://example.com{uri}
}
```

### Blocks

Blocks use curly braces. The opening `{` must be at the end of its line with a preceding space. The closing `}` must be on its own line.

When there is only one site block, curly braces are optional:

```caddy
localhost
reverse_proxy localhost:9000
```

is equivalent to:

```caddy
localhost {
    reverse_proxy localhost:9000
}
```

Multiple sites sharing the same config can be listed together separated by spaces or commas:

```caddy
localhost:8080, example.com, www.example.com {
    file_server
}
```

### Directives

Directives are functional keywords that appear within site blocks. They must be the first word on a line. Arguments follow on the same line. Subdirectives appear at the beginning of lines within directive blocks:

```caddy
example.com {
    reverse_proxy localhost:9000 localhost:9001 {
        lb_policy first
    }
}
```

Unless otherwise documented, directives cannot be nested within other directive blocks — except within `handle`, `handle_path`, and `route` blocks which are designed to group handlers.

### Tokens and Quotes

Whitespace separates tokens. Use double quotes for values containing spaces:

```caddy
directive "value with spaces"
```

Use backticks to avoid escaping inner quotes:

```caddy
directive `{"foo": "bar"}`
```

Heredocs are supported for multi-line content:

```caddy
example.com {
    respond <<HTML
        <html><body>Hello</body></html>
        HTML 200
}
```

## Addresses

An address appears at the top of each site block. Caddy infers scheme, host, and port from it:

- `example.com` — HTTPS with publicly-trusted managed certificate
- `*.example.com` — HTTPS with wildcard certificate
- `localhost` — HTTPS with locally-trusted certificate
- `http://example.com` — HTTP explicitly (no auto-HTTPS)
- `https://` — HTTPS catch-all
- `:8080` — HTTP on non-standard port
- `127.0.0.1` — HTTPS with locally-trusted IP certificate

Placeholders cannot be used in addresses, but environment variables can:

```caddy
{$DOMAIN:localhost} {
    file_server
}
```

By default, sites bind on all network interfaces. Use the `bind` directive or `default_bind` global option to restrict.

## Matchers

Request matchers classify requests so directives apply only to matching requests. Matcher tokens appear as the first argument after a directive:

```caddy
root /index.html /var/www    # path matcher: /index.html
root @post /var/www          # named matcher: @post
root * /var/www              # match all (explicit)
root /var/www                # match all (implicit, same as *)
```

Matcher definitions use `@` prefix within site blocks:

```caddy
example.com {
    @api {
        path /api/*
        method POST
    }
    reverse_proxy @api localhost:9001
}
```

## Placeholders

Placeholders inject dynamic values into configuration. They use `{identifier}` syntax and are typically namespaced with dots:

Global placeholders always available:

- `{env.*}` — Environment variable, e.g., `{env.HOME}`
- `{file.*}` — File contents, e.g., `{file./path/to/secret.txt}`
- `{system.hostname}` — System hostname
- `{time.now}` — Current time
- `{time.now.unix}` — Unix timestamp in seconds
- `{time.now.unix_ms}` — Unix timestamp in milliseconds

Caddyfile shorthand placeholders:

- `{host}` → `{http.request.host}`
- `{uri}` → `{http.request.uri}`
- `{path}` → `{http.request.uri.path}`
- `{method}` → `{http.request.method}`
- `{header.*}` → `{http.request.header.*}`
- `{query}` → `{http.request.uri.query}`
- `{file}` → `{http.request.uri.path.file}`
- `{upstream_hostport}` → `{http.reverse_proxy.upstream.hostport}`
- `{rp.*}` → `{http.reverse_proxy.*}`
- `{tls_cipher}` → `{http.request.tls.cipher_suite}`
- `{client_ip}` → `{http.vars.client_ip}`

Escape placeholder braces with `\{` to prevent replacement.

## Snippets

Snippets define reusable blocks with parenthesized names:

```caddy
(logging) {
    log {
        output file /var/log/caddy.log
        format json
    }
}

example.com {
    import logging
}
```

Pass arguments to snippets:

```caddy
(greeting) {
    respond "Hello, {args[0]}!"
}

a.example.com {
    import greeting "Alice"
}
```

Import files and globs:

```caddy
import sites/*
```

## Named Routes

Named routes (experimental, v2.9.x+) reduce memory usage when the same route is needed across many sites:

```caddy
&(app-proxy) {
    reverse_proxy app-01:8080 app-02:8080 app-03:8080
}

example.com {
    invoke app-proxy
}

www.example.com {
    invoke app-proxy
}
```

## Comments

Comments start with `#` and proceed to end of line:

```caddy
# Full line comment
directive arg  # trailing comment
```

The `#` cannot appear in the middle of a token (must be preceded by whitespace).

## Environment Variables

Use `{$VAR}` syntax for pre-parsing substitution (expands before Caddyfile parsing):

```caddy
example.com {
    reverse_proxy {$UPSTREAMS}
}
```

Default values with `:` delimiter:

```caddy
{$DOMAIN:localhost} {
    file_server
}
```

For runtime substitution, use `{env.*}` placeholders instead (requires module support).
