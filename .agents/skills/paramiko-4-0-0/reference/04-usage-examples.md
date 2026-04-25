# Usage Examples

### Basic SSH Client Connection

```python
import paramiko

# Create client and load system host keys
client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect
client.connect(
    hostname='ssh.example.com',
    port=22,
    username='user',
    password='secret',       # or use key_filename / pkey
    key_filename='~/.ssh/id_ed25519',
    timeout=10
)

# Execute command
stdin, stdout, stderr = client.exec_command('ls -la /tmp')
print(stdout.read().decode())
print(stderr.read().decode())

# Close connection
client.close()
```

### Key-Based Authentication

```python
import paramiko

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.RejectPolicy())

# Connect with specific key
client.connect(
    hostname='ssh.example.com',
    username='user',
    key_filename='/path/to/private/key',
    # If key has a password:
    # password='key_password'
)

# Or load key manually
private_key = paramiko.Ed25519Key.from_private_key_file('/path/to/key')
client.connect(
    hostname='ssh.example.com',
    username='user',
    pkey=private_key
)
```

### Remote Command Execution with Environment Variables

```python
import paramiko

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('host.example.com', username='user')

# Execute with environment variables and PTY
stdin, stdout, stderr = client.exec_command(
    'echo $HOME && ls -la',
    environment={'MY_VAR': 'value'},
    get_pty=True  # Request a pseudo-terminal
)

# Get exit status
stdout.channel.recv_exit_status()

client.close()
```

### Interactive Shell Session

```python
import paramiko
import select

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('host.example.com', username='user')

# Open interactive shell with PTY
chan = client.invoke_shell()
chan.get_pty(width=80, height=24)

# Send command
chan.send('ls -la\n')

# Read response
while not chan.exit_status_ready():
    if chan.recv_ready():
        output = chan.recv(1024).decode()
        print(output, end='')
    if chan.recv_stderr_ready():
        error = chan.recv_stderr(1024).decode()
        print(f"STDERR: {error}", end='')

client.close()
```

### SFTP File Transfer

```python
import paramiko

# Method 1: Using SSHClient.open_sftp()
client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('host.example.com', username='user')

sftp = client.open_sftp()

# Upload a file
sftp.put('/local/file.txt', '/remote/file.txt')

# Download a file
sftp.get('/remote/file.txt', '/local/file.txt')

# List directory
for attr in sftp.listdir_attr('/remote/'):
    print(f"{attr.filename:20} {attr.size:10} {attr.st_mode}")

# Upload with progress callback
def progress(bytes_transferred, total_size):
    pct = (bytes_transferred / total_size) * 100
    print(f"\r{pct:.1f}%", end='')

sftp.put('large_file.bin', '/remote/large_file.bin', callback=progress)

sftp.close()
client.close()
```

### SFTP with Context Manager (Paramiko 4.x style)

```python
import paramiko

with paramiko.SSHClient() as client:
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('host.example.com', username='user')

    with client.open_sftp() as sftp:
        # File operations
        sftp.mkdir('/remote/dir')
        sftp.chdir('/remote/dir')
        sftp.put('./local.txt', './remote.txt')
        files = sftp.listdir('.')
```

### SFTP Low-Level Operations

```python
import paramiko

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('host.example.com', username='user')

sftp = client.open_sftp()

# Open file for writing (returns SFTPFile)
with sftp.open('/remote/file.bin', 'wb') as f:
    f.write(b'hello world')
    f.flush()

# Read with stat info
stat = sftp.stat('/remote/file.bin')
print(f"Size: {stat.st_size}, Mode: {stat.st_mode}")

# Chmod/chown
sftp.chmod('/remote/file.bin', 0o644)
sftp.chown('/remote/file.bin', uid=1000, gid=1000)

# Symlink
sftp.symlink('target.txt', 'link.txt')
print(sftp.readlink('link.txt'))  # 'target.txt'

# Rename / remove
sftp.rename('old.txt', 'new.txt')
sftp.remove('temp.txt')
sftp.rmdir('/remote/empty_dir')

sftp.close()
client.close()
```

### Port Forwarding (Tunneling)

```python
import paramiko
import threading

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('jump-host.example.com', username='user')

# Local port forwarding: localhost:8080 -> target:3306
client.forward_tcpip(('target-db.example.com', 3306), ('localhost', 8080))

# Or use request_port_forward for remote forwarding
def handle_channel(channel, src_addr):
    # Handle incoming connection on forwarded port
    print(f"Connection from {src_addr}")
    channel.send("Hello from forwarder!")
    channel.close()

transport = client.get_transport()
transport.request_port_forward('localhost', 9090, handler=handle_channel)

# Now connect to localhost:9090 will be tunneled through the SSH connection
client.close()
```

### Running an SSH Server

```python
import paramiko
import threading

class MyServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        # Simple password check
        if username == "admin" and password == "secret":
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return "password"

# Generate a host key
from cryptography.hazmat.primitives.asymmetric import ed25519
private_key = ed25519.Ed25519PrivateKey.generate()
pkey = paramiko.Ed25519Key.from_private_key(private_key)

# Start server
server = MyServer()
transport = paramiko.Transport(('0.0.0.0', 2222))
transport.add_server_key(pkey)
transport.start_server(server=server)

# Wait for a client to connect
chan = transport.accept(20)  # Wait up to 20 seconds
if chan:
    chan.send("Welcome!\n")
    chan.close()
transport.close()
```

### SSH Agent Integration

```python
import paramiko

# Connect to local SSH agent
agent = paramiko.Agent()
agent_keys = agent.get_keys()

print(f"Available keys: {len(agent_keys)}")
for key in agent_keys:
    print(f"  - {key.get_name()}: {key.get_fingerprint().hex()}")

# Use agent key for authentication
client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

for key in agent_keys:
    try:
        client.connect(
            'host.example.com',
            username='user',
            pkey=key,
            look_for_keys=False  # Skip file-based keys
        )
        print("Connected with agent key!")
        break
    except paramiko.AuthenticationException:
        continue

client.close()
agent.close()
```

### Using ProxyCommand (SSH Jump Host)

```python
import paramiko

# Create a proxy command connection
proxy = paramiko.ProxyCommand('ssh -W %h:%p jump-host.example.com')

# Use it as the socket for Transport
transport = paramiko.Transport(proxy)
transport.start_client()

# Authenticate
transport.auth_password(username='user', password='secret')

# Now use channels normally
chan = transport.open_session()
chan.exec_command('hostname')
print(chan.recv(1024).decode())

transport.close()
```

### SSH Config File Parsing

```python
import paramiko

# Parse an OpenSSH config file
config = paramiko.SSHConfig.from_file('/home/user/.ssh/config')

# Look up a host
host_config = config.lookup('my-server.example.com')
print(f"Hostname: {host_config.get('hostname')}")
print(f"User: {host_config.get('user')}")
print(f"Port: {host_config.get('port')}")
print(f"IdentityFile: {host_config.get('identityfile')}")

# Supports %l, %L, %r, %h tokens and Host/Match directives
```

### Low-Level Transport API

```python
import paramiko
import socket

# For full control, use Transport directly
sock = socket.create_connection(('host.example.com', 22))
transport = paramiko.Transport(sock)
transport.start_client()

# Authenticate
transport.auth_password(username='user', password='secret')

# Open a session channel
chan = transport.open_session()
chan.get_pty()
chan.invoke_shell()

# Or execute a command directly
chan = transport.open_session()
chan.exec_command('uptime')
print(chan.recv(1024).decode())

# Port forwarding at transport level
transport.request_port_forward('localhost', 8080)

transport.close()
```
