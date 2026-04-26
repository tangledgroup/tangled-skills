# Configuration & Proxy

## SSHConfig Parser

Paramiko provides an `ssh_config` file parser. Note: Paramiko does **not** automatically read `~/.ssh/config`. You must parse and apply the config yourself (or use a higher-level library like Fabric).

### Loading Config

```python
from paramiko.config import SSHConfig

# From file path
config = SSHConfig.from_path("~/.ssh/config")

# From file-like object
with open("~/.ssh/config") as f:
    config = SSHConfig.from_file(f)

# From text string
config = SSHConfig.from_text("Host myhost\n\tUser admin\n\tPort 2222")

# Legacy style
config = SSHConfig()
with open("~/.ssh/config") as f:
    config.parse(f)
```

### Looking Up Host Configuration

```python
conf = config.lookup("myhost.example.com")

# Keys are normalized to lowercase
print(conf["user"])       # "admin"
print(conf["port"])       # "2222"
print(conf["hostname"])   # actual hostname (defaults to lookup key)

# Type conversion helpers
print(conf.as_bool("passwordauthentication"))  # True/False
print(conf.as_int("port"))                      # 2222
```

### Supported Keywords

Paramiko's SSHConfig parser supports these `ssh_config` directives:

- `Host` / `HostName` — host matching and target hostname
- `User` — remote username
- `Port` — connection port
- `ProxyCommand` — proxy command for routing connections
- `Match` — conditional configuration blocks
- `CanonicalDomains`, `CanonicalizeFallbackLocal`, `CanonicalizeHostname`, `CanonicalizeMaxDots` — hostname canonicalization

### Match Directive Support

The `Match` directive supports keywords: `all`, `canonical`, `exec`, `final`, `host`, `localuser`, `originalhost`, `user`.

For `Match exec`, the optional `invoke` dependency is required (`pip install "paramiko[invoke]"`).

### Expansion Tokens

Supported tokens in config values: `%C`, `%d`, `%h`, `%l`, `%L`, `%n`, `%p`, `%r`, `%u`. Additionally, `~` expands to home directory in ProxyCommand values.

## ProxyCommand Support

The `ProxyCommand` class wraps a subprocess running proxy commands (like `nc`, `ssh -W`, or `connect`):

```python
from paramiko.proxy import ProxyCommand
import paramiko

# Create a proxy connection
proxy = ProxyCommand("ssh -W %h:%p jump_host")

# Pass to Transport instead of a socket
transport = paramiko.Transport(proxy)
transport.start_client()
transport.auth_password(username="user", password="secret")

# Use the connection...
chan = transport.open_session()
chan.exec_command("hostname")
print(chan.recv_exit_status())

proxy.close()
transport.close()
```

ProxyCommand instances can be used as context managers:

```python
with ProxyCommand("ssh -W %h:%p jump_host") as proxy:
    transport = paramiko.Transport(proxy)
    # ... use connection
```

## Applying SSHConfig to Connections

A common pattern for applying ssh_config to SSHClient connections:

```python
from paramiko.config import SSHConfig
from paramiko.proxy import ProxyCommand
import paramiko

config = SSHConfig.from_path("~/.ssh/config")
conf = config.lookup("myhost")

client = paramiko.SSHClient()
client.load_system_host_keys()

# Build connect kwargs from config
connect_kwargs = {
    "hostname": conf["hostname"],
    "username": conf.get("user"),
    "port": int(conf["port"]) if "port" in conf else 22,
}

# Handle ProxyCommand
if "proxycommand" in conf:
    proxy = ProxyCommand(conf["proxycommand"])
    connect_kwargs["sock"] = proxy

client.connect(**connect_kwargs)
```
