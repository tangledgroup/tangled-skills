# SFTP Operations

## Opening SFTP Sessions

```python
import paramiko

client = paramiko.SSHClient()
client.connect("hostname", username="user", password="secret")

# Via SSHClient
sftp = client.open_sftp()

# Via Transport
transport = client.get_transport()
sftp = transport.open_sftp_client()
```

## File Operations

### Open and Read/Write

```python
# Open remote file (modes: r, w, a, r+, w+, a+, x)
with sftp.open("/remote/file.txt", "r") as f:
    content = f.read()

# Write to remote file
with sftp.open("/remote/output.txt", "w") as f:
    f.write("Hello, world!\n")

# Binary mode (SSH treats all files as binary, 'b' flag is ignored)
with sftp.open("/remote/data.bin", "rb") as f:
    data = f.read()

# Exclusive create ('x' — fails if file exists)
with sftp.open("/remote/new.txt", "x") as f:
    f.write("created\n")
```

### Upload and Download

```python
# Upload local file to remote
sftp.put("/local/file.txt", "/remote/file.txt")

# With progress callback
def progress(transferred, total):
    print(f"{transferred}/{total} bytes")

sftp.put("/local/large.bin", "/remote/large.bin", callback=progress)

# Download remote file to local
sftp.get("/remote/file.txt", "/local/file.txt")

# Upload from file object
with open("/local/data.bin", "rb") as f:
    sftp.putfo(f, "/remote/data.bin", file_size=os.path.getsize("/local/data.bin"))
```

## Directory Operations

```python
# List directory (names only)
entries = sftp.listdir("/remote/dir")

# List with attributes
attrs = sftp.listdir_attr("/remote/dir")
for attr in attrs:
    print(attr.filename, attr.st_size, attr.st_mtime)

# Iterator version (memory efficient for large dirs)
for attr in sftp.listdir_iter("/remote/dir"):
    print(attr.filename)

# Create directory
sftp.mkdir("/remote/newdir", mode=0o755)

# Remove directory (must be empty)
sftp.rmdir("/remote/emptydir")

# Get file attributes (follows symlinks)
stat = sftp.stat("/remote/file.txt")
print(stat.st_size, stat.st_mode, stat.st_mtime)

# Lstat (does not follow symlinks)
lstat = sftp.lstat("/remote/link")
```

## File Management

```python
# Remove file
sftp.remove("/remote/old_file.txt")
sftp.unlink("/remote/old_file.txt")  # alias

# Rename file/directory
sftp.rename("/remote/old_name", "/remote/new_name")

# POSIX rename (overwrites target if exists, requires server support)
sftp.posix_rename("/remote/src", "/remote/dst")

# Truncate file
sftp.truncate("/remote/file.txt", size=1024)

# Create symbolic link
sftp.symlink("/remote/target", "/remote/link_name")

# Read symlink target
target = sftp.readlink("/remote/link_name")

# Set access/modify times
sftp.utime("/remote/file.txt", (atime, mtime))
sftp.utime("/remote/file.txt", None)  # set to current time

# Normalize path (resolve symlinks, get canonical path)
canonical = sftp.normalize("/remote/../other/./file")
```

## SFTPAttributes

The `SFTPAttributes` object mirrors Python's `stat` structure:

- `st_mode` — file mode/permissions
- `st_size` — file size in bytes
- `st_uid` — owner UID
- `st_gid` — group GID
- `st_atime` — access time (epoch seconds)
- `st_mtime` — modification time (epoch seconds)
- `longname` — formatted unix-style listing string (from `listdir_attr`)

## Server-Side SFTP

To serve SFTP in an SSH server, register the subsystem handler:

```python
from paramiko.sftp_server import SFTPServer
from paramiko.sftp_si import SFTPServerInterface

# Register SFTP subsystem on Transport
transport.set_subsystem_handler("sftp", SFTPServer)

# Custom SFTP interface
class MySFTPHandler(SFTPServerInterface):
    def __init__(self, sftp_server, server, *args):
        super().__init__(sftp_server, server, *args)

    def list_folder(self, path):
        # Return list of SFTPAttributes for directory listing
        pass

    def open_file(self, path, flags, attr):
        # Handle file open request
        pass

# Use custom handler
transport.set_subsystem_handler("sftp", SFTPServer, MySFTPHandler)
```

### SFTPServer Helper Methods

```python
# Convert errno to SFTP error code
err_code = SFTPServer.convert_errno(os_error.errno)

# Set file attributes from SFTPAttributes
SFTPServer.set_file_attr("/path/to/file", attr)
```

## Window Size Considerations

When using `exec_command` or channels, large remote output can cause `recv_exit_status()` to hang if the output exceeds the transport's window size. Ensure you call `chan.recv()` to drain output before calling `recv_exit_status()`, or use background threads for reading.
