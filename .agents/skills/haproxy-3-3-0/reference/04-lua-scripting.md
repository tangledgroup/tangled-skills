# Lua Scripting

## Overview

HAProxy embeds Lua 5.3 for extending functionality beyond native configuration capabilities. Lua scripts register sample fetches, converters, actions, services, and tasks that integrate with HAProxy's event-driven architecture.

### Loading Lua Scripts

```
global
    # Shared context (visible to all threads, single global state)
    lua-load /etc/haproxy/lua/my-script.lua

    # Per-thread context (independent copy per thread, highly scalable)
    lua-load-per-thread /etc/haproxy/lua/per-thread.lua

    # Adjust Lua package path
    lua-prepend-path /usr/share/haproxy-lua/?.lua
    lua-prepend-path /usr/share/haproxy-lua/?/init.lua
```

- `lua-load` — single global Lua state shared by all threads. Simplest approach but creates contention under heavy Lua usage.
- `lua-load-per-thread` — independent Lua state per thread. Recommended for high-throughput scenarios. Check `core.thread` to identify which thread is initializing.

### Global Tuning

```
global
    tune.lua.maxmem 128              # Max RAM in MB for Lua (0 = unlimited)
    tune.lua.session-timeout 4s      # Timeout for actions/filters (default 4s)
    tune.lua.service-timeout 4s      # Timeout for services (default 4s)
    tune.lua.task-timeout 0          # Timeout for tasks (default: none)
    tune.lua.burst-timeout 1000ms    # Max time between yields (default 1000ms)
    tune.lua.forced-yield 10000      # Instructions between forced yields
    tune.lua.bool-sample-conversion normal  # Boolean handling mode
```

## Architecture and Design

### Non-Blocking Design

HAProxy is event-driven. Blocking system calls in Lua will freeze the entire process. During runtime, these functions are **prohibited**:

- `os.remove()`, `os.rename()`, `os.tmpname()`
- `package.*()`, `io.*()`, `file.*()`
- `os.execute()` — blocks waiting for command completion
- `os.exit()` — not the proper way to exit HAProxy
- `print()` — may block on stdout; use `core.log()` or `TXN.log()` instead

Filesystem access is allowed during initialization (`core.register_init()`).

### Yield Concept

Lua execution is periodically interrupted (yielded) to let HAProxy process other tasks:
- Automatic yield after `tune.lua.forced-yield` instructions
- Manual yield via `core.sleep()`, `core.msleep()`, or `core.yield()`
- Socket operations yield automatically while waiting for data

Code running inside `pcall()` cannot yield — keep such code fast.

### Register Functions

Entry points for Lua integration, all in the `core` collection:

- `core.register_action(<name>, <flags>, <function>)` — HTTP/TCP action
- `core.register_fetches(<name>, <function>)` — sample fetch
- `core.register_converters(<name>, <function>)` — sample converter
- `core.register_service(<name>, <flags>, <function>)` — service
- `core.register_task(<function>, <period>)` — periodic background task
- `core.register_init(<function>)` — initialization callback

## Common HAProxy Lua Objects

- **TXN** — transaction object (manipulates client-server transaction)
- **HTTP** — HTTP manipulation object
- **Channel** — data channel between client and server
- **Socket** — TCP connection to external servers (IPv4/IPv6/SSL/UNIX)
- **Map** — HAProxy map manipulation
- **Fetches** — access to all HAProxy sample fetches
- **Converters** — access to all HAProxy sample converters
- **AppletTCP** — process client requests like a TCP server
- **AppletHTTP** — process client requests like an HTTP server

## Writing Actions

Actions are the most common Lua extension. They execute during request or response processing.

### HTTP Action Example

```lua
core.register_action("add-custom-header", { "http-req" }, function(txn)
    txn.http:set_headers({
        ["X-Custom-Header"] = "value",
        ["X-Request-ID"] = core.uuid4()
    })
end)
```

Usage in configuration:
```
http-request lua.add-custom-header
```

### Action with Conditions

```lua
local function rate_limit_check(txn)
    local src_ip = txn:get_var("src")
    if src_ip and txn:req_rate(src_ip) > 100 then
        txn:http_reply(429, { ["Content-Type"] = "text/plain" }, "Rate limited\n")
    end
end

core.register_action("rate-limit", { "http-req" }, rate_limit_check)
```

## Writing Sample Fetches

Fetches extract data and return it as a sample value.

```lua
local function get_custom_value(txn, smp, args)
    -- Return a string sample
    return core.SAMPLE_T_STR, "custom-value"
end

core.register_fetches("my-fetch", get_custom_value)
```

Usage:
```
acl check_value lua.my-fetch -m str custom-value
http-request set-var(txn.fetched) lua.my-fetch
```

## Writing Services

Services are autonomous entities that behave like external clients or servers. They can process HTTP requests independently.

### HTTP Service Example

```lua
local function my_service_handler(applet)
    applet:http_reply(200, { ["Content-Type"] = "application/json" },
        '{"status": "ok", "service": "my-lua-service"}')
end

core.register_service("my-service", nil, my_service_handler)
```

Usage in configuration:
```
use_service lua.my-service
```

### Full HTTP Server Service

```lua
local function http_service(applet)
    local method, path, ver, headers = applet:http_req()
    if not method then
        return -- connection closed
    end

    if path == "/health" then
        applet:http_reply(200, { ["Content-Type"] = "text/plain" }, "OK\n")
    elseif path == "/info" then
        local info = string.format('{"version": "%s", "pid": %d}',
            core.get_info("version"), core.get_info("pid"))
        applet:http_reply(200, { ["Content-Type"] = "application/json" }, info)
    else
        applet:http_reply(404, { ["Content-Type"] = "text/plain" }, "Not found\n")
    end
end

core.register_service("http-api", nil, http_service)
```

## Tasks

Tasks run periodically in the background. They cannot yield and must complete quickly.

```lua
local function periodic_task()
    -- Log every 60 seconds
    core.log("Periodic task executed at " .. os.date("%Y-%m-%d %H:%M:%S"))
    return 60 -- next execution in 60 seconds
end

core.register_task(periodic_task, 60)
```

## Sockets

HAProxy Lua sockets establish TCP connections to external servers. They use full HAProxy sessions internally, supporting SSL, UNIX sockets, and namespaces.

### Basic Socket Usage

```lua
local function proxy_request(txn)
    local socket = core.new_socket()
    local ok, err = socket:connect("127.0.0.1:8080")

    if not ok then
        txn:http_reply(502, { ["Content-Type"] = "text/plain" },
            "Backend error: " .. err)
        return
    end

    socket:send("GET /health HTTP/1.1\r\nHost: localhost\r\n\r\n")
    local response = socket:receive()
    socket:shutdown()

    if response and string.find(response, "200 OK") then
        txn:http_reply(200, { ["Content-Type"] = "text/plain" }, "Healthy\n")
    else
        txn:http_reply(503, { ["Content-Type"] = "text/plain" }, "Unhealthy\n")
    end
end

core.register_action("check-backend", { "http-req" }, proxy_request)
```

### SSL Socket

```lua
local socket = core.new_socket()
local ok, err = socket:connect("api.example.com:443", { ssl = true, verify = true })
```

### UNIX Socket

```lua
local socket = core.new_socket()
local ok, err = socket:connect("/var/run/app.sock")
```

## Initialization

```lua
core.register_init(function()
    -- Load configuration files
    local file = io.open("/etc/haproxy/lua/config.json", "r")
    if file then
        local data = file:read("*all")
        file:close()
        -- Parse and store configuration
    end

    core.log("Lua script initialized successfully")
end)
```

## Passing Arguments

```
global
    lua-load /etc/haproxy/lua/script.lua arg1 arg2 value3
```

In Lua:
```lua
local args = table.pack(...)
-- args[1] = "arg1", args[2] = "arg2", args[3] = "value3"
```

## Using Fetches and Converters from Lua

```lua
local function analyze_request(txn)
    -- Access HAProxy fetches
    local fetches = core.fetches
    local converters = core.converters

    -- Get source IP
    local src = txn:fetch_value(fetches.src)

    -- Get HTTP method
    local method = txn:fetch_value(fetches.meth)

    -- Apply converter
    local lower_method = converters:lower(method)

    txn:set_var("txn.method_lower", lower_method)
end

core.register_action("analyze", { "http-req" }, analyze_request)
```

## Best Practices

- Use `lua-load-per-thread` for high-throughput scripts to avoid global Lua state contention
- Keep fetches and converters fast — they cannot yield
- Use `core.log()` instead of `print()` for logging
- Force garbage collection after socket usage: `collectgarbage()`
- Set `tune.lua.maxmem` to prevent memory exhaustion from buggy scripts
- Avoid `pcall()` wrapping around code that needs to yield
- Test with `tune.lua.burst-timeout` to catch infinite loops
- Use `core.sleep()` for non-blocking delays instead of busy-waiting
