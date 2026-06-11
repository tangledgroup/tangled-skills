# Lua Scripting

## Registering Scripts

Use `register_script()` to create a `Script` instance that handles caching and retry automatically:

```python
r = redis.Redis()
lua = """
local value = redis.call('GET', KEYS[1])
value = tonumber(value)
return value * ARGV[1]
"""
multiply = r.register_script(lua)
```

## Executing Scripts

Call the script like a function with `keys` and `args`:

```python
r.set('foo', 2)
result = multiply(keys=['foo'], args=[5])
# 10
```

- `keys` — List of key names (becomes `KEYS` in Lua)
- `args` — List of argument values (becomes `ARGV` in Lua)
- `client` — Optional client to execute on (defaults to the creating client)

## Cross-Client Execution

Execute a script on a different Redis server:

```python
r2 = redis.Redis('other-server.example.com')
r2.set('foo', 3)
result = multiply(keys=['foo'], args=[5], client=r2)
# 15
```

## Scripts in Pipelines

Pass the pipeline as the `client` argument:

```python
pipe = r.pipeline()
pipe.set('foo', 5)
multiply(keys=['foo'], args=[5], client=pipe)
results = pipe.execute()
# [True, 25]
```

The script is registered in Redis's cache just prior to pipeline execution.

## Script Object Behavior

The `Script` object ensures the Lua code is loaded into Redis's script cache. On `NOSCRIPT` errors, it automatically loads and retries — no manual `EVALSHA`/`SCRIPT LOAD` management needed.

Under the hood, redis-py supports `EVAL`, `EVALSHA`, and all `SCRIPT` commands directly:

```python
# Direct EVAL
r.eval("return redis.call('GET', KEYS[1])", 1, 'mykey')

# Direct EVALSHA
sha = r.script_load("return 1")
r.evalsha(sha, 0)

# Script management
r.script_exists(sha)
r.script_flush()
```

## Cluster Mode Limitations

Lua scripting in cluster mode has restrictions:

- `EVAL` and `EVALSHA` — Sent to the node determined by the keys. All keys must hash to the same slot. With 0 keys, sent to a random primary.
- `SCRIPT EXISTS` — Sent to all primaries. Returns `True` only if the script exists on every node.
- `SCRIPT FLUSH` — Sent to all primaries.
- `SCRIPT LOAD` — Sent to all primaries.
- `EVAL_RO` and `EVALSHA_RO` — Not supported in cluster mode.
- Scripting within pipelines — Not supported in cluster mode.
