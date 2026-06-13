# Rewrite, Map, and Logging

## rewrite Directive

Change request URI using PCRE regular expressions:

```nginx
location / {
    rewrite ^/old/(.*)$ /new/$1 permanent;   # 301 redirect
    rewrite ^/temp/(.*)$ /other/$1 redirect;  # 302 redirect
    rewrite ^/internal/(.*)$ /actual/$1 last; # internal rewrite
    rewrite ^/stop/(.*)$ /final/$1 break;     # stop processing rewrites
}
```

Flags:
- `last` — stop rewrite processing, restart location search
- `break` — stop rewrite processing, use current location
- `redirect` — return 302 temporary redirect
- `permanent` — return 301 permanent redirect

Rewrite directives execute sequentially in order. If a redirect flag is used, processing stops and the redirect is returned immediately.

## return Directive

Stop processing and return a response:

```nginx
return 404;
return 403 "Access denied";
return 301 https://$host$request_uri;
return 302 /new-page;
```

Supported codes: any standard HTTP code. Codes 301, 302, 303, 307, 308 are treated as redirects. Code 444 is nginx-specific — closes the connection immediately with no response.

## if Directive

Conditional processing (use carefully — "if is evil" in nginx):

```nginx
if ($http_user_agent ~* Bot) {
    return 403;
}

if ($request_method = POST) {
    limit_except POST { deny all; }
}
```

Safe uses: `return`, `rewrite` with redirect/permanent flags. Avoid using `if` for proxy_pass or root — use `map` instead.

## map Module

Create variables based on other variable values:

```nginx
map $http_user_agent $is_bot {
    default 0;
    ~*Bot 1;
    ~*Spider 1;
    ~*Crawl 1;
}

map $http_host $name {
    default 0;
    example.com 1;
    www.example.com 1;
}

map $remote_addr $geo_zone {
    default "unknown";
    ~^192\.168\. "internal";
    ~^10\. "private";
}
```

The `map` block goes in the `http` context. When no match is found, the `default` value is used. If `default` is not specified, empty string is the default.

## log_format

Define custom log formats in the `http` context:

```nginx
log_format main '$remote_addr - $remote_user [$time_local] '
                '"$request" $status $body_bytes_sent '
                '"$http_referer" "$http_user_agent"';

log_format json escape=json
    '{'
        '"remote_addr":"$remote_addr",'
        '"time":"$time_iso8601",'
        '"request":"$request",'
        '"status":"$status",'
        '"bytes_sent":"$body_bytes_sent"'
    '}';

log_format compression '$remote_addr - $remote_user [$time_local] '
                       '"$request" $status $body_bytes_sent '
                       '"$gzip_ratio"';
```

The built-in `combined` format is equivalent to the classic Apache combined log format.

## access_log

Specify access log file and format:

```nginx
access_log /var/log/nginx/access.log combined;
access_log /var/log/nginx/api.log json;
access_log off;  # disable logging for this context
```

Advanced options:

```nginx
# Buffering
access_log /var/log/nginx/access.log combined buffer=32k flush=5m;

# Conditional logging
map $status $loggable {
    ~^[23] 0;
    default 1;
}
access_log /var/log/nginx/access.log combined if=$loggable;

# Per-vhost logging with variable filename
access_log /spool/vhost/logs/$host;

# Gzip compressed
access_log /path/to/log.gz combined gzip flush=5m;
```

## error_log

Control error logging at different levels:

```nginx
error_log /var/log/nginx/error.log debug;
error_log /var/log/nginx/error.log info;
error_log /var/log/nginx/error.log notice;
error_log /var/log/nginx/error.log warn;
error_log /var/log/nginx/error.log error;    # default
error_log /var/log/nginx/error.log crit;
error_log /var/log/nginx/error.log alert;
error_log /var/log/nginx/error.log emerg;
```

Error log levels from most to least verbose: debug, info, notice, warn, error, crit, alert, emerg. Setting a level logs that level and all more severe levels.

## open_log_file_cache

Cache opened log file descriptors for performance:

```nginx
open_log_file_cache max=1000 inactive=20s valid=1m min_uses=2;
open_log_file_cache off;  # disable cache
```

## set Directive

Assign a value to a variable:

```nginx
set $my_var "value";
set $api_version "v2";
```

Variables are scoped to the current request and can be used in subsequent directives.
