# HAProxy Lua Integration

## Overview

HAProxy embeds Lua 5.3 for custom logic, enabling extension of the native configuration language with complex conditionals, protocol analysis, and full services.

## Loading Lua Scripts

```haproxy
global
    lua-load /etc/haproxy/lua/myscript.lua
```

Multiple scripts can be loaded; they are executed in order.

## Registration Functions

### core.register_action()

Register an action callable from configuration rules:

```lua
core.register_action("my_action", { "http-req" }, function(txn)
    -- txn: transaction object
    -- Return true to continue, false to stop
    txn:set_var("txn.my_var", "hello")
    return true
end)
```

Action types: `http-req`, `http-res`, `tcp-req`, `tcp-rsp`, `http-act` (all HTTP rules), `tcp-act` (all TCP rules)

### core.register_fetches()

Register a sample fetch function:

```lua
core.register_fetches("my_fetch", function(txn)
    return txn:set_var("txn.result", "computed")
end)
```

### core.register_converters()

Register a converter that transforms fetched samples:

```lua
core.register_converters("my_conv", { "str" }, function(src, dst, val)
    -- Transform val and write to dst
    return true
end)
```

### core.register_service()

Register a full service (e.g., stats-like):

```lua
core.register_service("my_svc", "http", function(env)
    env:add_fetches("path")
    env:set_handler(function(txn)
        txn:response():set_status(200)
        txn:response():body():add("Hello from Lua service!")
        txn:response():commit()
    end)
end)
```

## HAProxy Lua API Objects

### Transaction (txn)

| Method | Description |
|--------|-------------|
| `txn:var(name)` / `txn:set_var(name, value)` | Access internal variables |
| `txn:req()` / `txn:rsp()` | Get request/response channel |
| `txn:loglevel(level)` | Set log level for this stream |
| `txn:srv(name)` | Set the server to forward to |
| `txn:backend(name)` | Set the backend to use |
| `txn:frontend(name)` | Set the frontend name |

### Sample Fetches from Lua

```lua
-- Access request data
local path = txn:req():path()
local host = txn:req():hdr("Host")
local src_ip = txn:smp_fetch_src(nil, txn:sess(), {"src"})

-- ACL matching
if txn:acktbl("my_table"):get(src_ip) then
    -- IP is in the stick-table
end
```

### Channel Manipulation (HTTP)

```lua
local req = txn:req()
req:header("X-Custom-Header"):set("value")
req:body():add("new body content")
```

**Warning**: Modifying HTTP requests via channels can produce invalid HTTP. Prefer using `txn:set_var()` and native HAProxy actions when possible.

### Service Object

```lua
env:add_acl("my_acl", "str")
env:set_acl("my_acl", function(txn, val)
    return true  -- match or not
end)
env:set_sample_fetch("path", function(txn)
    return txn:req():path()
end)
```

## Time and Execution Limits

Lua execution is limited by:
- **Instructions per transaction**: Configurable via `tune.lua.maxmem` and instruction counters
- **Non-blocking requirement**: No blocking syscalls allowed; use HAProxy's event system for async operations

## Example: Custom Authentication

```lua
core.register_action("auth_check", { "http-req" }, function(txn)
    local api_key = txn:req():hdr("X-API-Key")
    if api_key and core.lookup_key("userlist_api", api_key) then
        return true  -- authorized
    end
    return false  -- deny
end)
```

## Example: Rate Limiting with Lua Tables

```lua
local rate_table = {}

core.register_action("rate_limit", { "http-req" }, function(txn)
    local src = txn:sess():src()
    local now = os.time()
    
    -- Clean old entries
    for ip, ts in pairs(rate_table) do
        if now - ts > 10 then
            rate_table[ip] = nil
        end
    end
    
    -- Check rate
    local count = rate_table[src] and (now == rate_table[src]) and 1 or 0
    rate_table[src] = now
    
    if count > 100 then
        txn:response():set_status(429)
        txn:response():body():add("Rate limited")
        return false  -- stop processing
    end
    return true
end)
```

## References

- HAProxy Lua API documentation (source tree): `doc/lua-api/`
- Lua 5.3 manual: https://www.lua.org/manual/5.3/
- Original Lua integration guide: https://github.com/haproxy/haproxy/blob/v3.3.0/doc/lua.txt
