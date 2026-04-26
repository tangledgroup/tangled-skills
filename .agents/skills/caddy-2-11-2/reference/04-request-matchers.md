# Request Matchers

Request matchers classify incoming HTTP requests so directives apply only to matching requests. They can be used inline with directives or defined as named matchers.

## Syntax

Inline matcher tokens appear as the first argument after a directive:

```caddy
respond /hello "Hello!" 200          # path matcher
respond @api "API response" 200      # named matcher
respond * "Catch-all" 200            # match all
```

Named matcher definitions use `@` prefix within site blocks:

```caddy
example.com {
    @mobile {
        header User-Agent "*Mobile*"
    }
    redir @mobile https://m.example.com{uri}
}
```

Multiple conditions in a named matcher are ANDed together.

## Path Matchers

### `path`

Match request URI paths:

```caddy
@api path /api/*
@static path /static/* /assets/*
```

Path matchers support wildcards (`*` matches zero or more characters within a path segment). `/foo*` matches `/foobar` but not `/foo/bar`. Use `/*` for recursive matching: `/foo/*` matches `/foo/bar/baz`.

### `path_regexp`

Regular expression path matching (RE2 syntax):

```caddy
@images path_regexp images ^/[^/]+\.(png|jpg|gif|webp)$
```

Capture groups accessible via `{re.<name>.<n>}` placeholders.

## Method Matchers

### `method`

Match HTTP methods:

```caddy
@post method POST
@write method POST PUT PATCH DELETE
```

## Header Matchers

### `header`

Match request headers by name and value:

```caddy
@json header Content-Type "application/json"
@not-bot header User-Agent "!*bot*"
@has-auth header Authorization
```

- Exact match: `header Name "value"`
- Wildcard: `header Name "*prefix*"`
- Negation: `header Name "!value"`
- Existence check: `header Name` (no value = exists)

### `header_regexp`

Regular expression header matching:

```caddy
@version header_regexp Accept-Version ^application/vnd.api\+(?:json|yaml); version=(\d+)$
```

Capture groups accessible via `{re.<name>.<n>}`.

## Query Matchers

### `query`

Match URL query strings:

```caddy
@format query format json
@search query q
```

- Exact match on value: `query key "value"`
- Existence check: `query key` (no value = key exists)
- Multiple values ANDed: `query a "1" b "2"`

## Protocol Matchers

### `protocol`

Match protocol version:

```caddy
@h2 protocol h2
@h3 protocol h3
```

## Remote IP Matchers

### `remote_ip`

Match client IP addresses:

```caddy
@internal remote_ip 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16
@blocked remote_ip !10.0.0.0/8
```

Supports CIDR notation, IP ranges, and negation with `!`.

### `not_remote_ip`

Negated form (shorthand):

```caddy
@external not_remote_ip 10.0.0.0/8
```

## Host Matchers

### `host`

Match Host header:

```caddy
@www host www.example.com
```

Usually handled by site block addresses instead.

## Named Matcher Examples

```caddy
# Complex matcher combining multiple conditions
@api {
    path /api/*
    method POST PUT
    header Content-Type "application/json"
}

# Mobile detection
@mobile {
    header_regexp User-Agent "(?i)(android|iphone|ipad)"
}

# Static assets with cache
@static-assets {
    path_regexp static ^/static/.*\.(css|js|png|jpg|gif|svg|woff2)$
}

# Admin panel access
@admin {
    remote_ip 10.0.0.0/8
    path /admin/*
}
```

## Expression Matchers (CEL)

### `expression`

Common Expression Language for complex matching logic:

```caddy
@complex expression request.Method == "POST" && requestURI.Path.startsWith("/api") && request.Headers["Content-Type"].contains("json")
```

Supports access to request properties and placeholder evaluation.

## Variable Matchers

### `vars`

Match on variables set by the `vars` directive:

```caddy
vars {my_var} "hello"
@matched vars {my_var} "hello"
```

### `vars_regexp`

Regular expression variable matching:

```caddy
@magic vars_regexp magic_number ^(4.*)
```

## Response Matchers

Used within `handle_response` blocks of `reverse_proxy`:

```caddy
reverse_proxy localhost:8080 {
    handle_response {
        @success {
            expression {hp.Response.Status} >= 200 && {hp.Response.Status} < 300
        }
        @redirect {
            response_status 3xx
        }
        copy_response @success
    }
}
```

Response matcher types: `response_status`, `response_header`, `expression`.

## Matcher Precedence in Directive Sorting

When multiple same-named directives exist, they are sorted by matcher specificity:

1. Single path matcher — most specific to least (by path length)
2. Other matchers — in file order
3. No matcher — last

Exception: `vars` directive reverses this ordering so most specific is evaluated last.
