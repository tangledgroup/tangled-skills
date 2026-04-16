# SFTP Operations Reference

## SFTPClient Overview

`SFTPClient` provides remote file operations over an SSH session. Can be created via `SSHClient.open_sftp()` or `SFTPClient.from_transport()`.

```python
import paramiko

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('host.example.com', username='user')

sftp = client.open_sftp()
# or: sftp = paramiko.SFTPClient.from_transport(client.get_transport())
```

## File Operations

### Open Remote File

```python
with sftp.open('/remote/path/file.txt', 'r') as f:
    data = f.read()

# Modes: 'r', 'w', 'a', 'rb', 'wb', 'ab' (same as Python built-in open)
with sftp.open('/remote/file.bin', 'wb') as f:
    f.write(binary_data)
```

### Stat and File Attributes

```python
attr = sftp.stat('/remote/file.txt')
print(f"Size: {attr.st_size}")
print(f"Mode: {oct(attr.st_mode)}")
print(f"UID: {attr.st_uid}, GID: {attr.st_gid}")
print(f"Modified: {attr.st_mtime}")

# Lstat (don't follow symlinks)
lstat = sftp.lstat('/remote/link')

# Normalize path
normalized = sftp.normalize('/remote/../file.txt')  # '/file.txt'
```

### Directory Operations

```python
# List directory (filenames only)
files = sftp.listdir('/remote/dir')

# List with attributes
for attr in sftp.listdir_attr('/remote/dir'):
    name = attr.filename
    size = attr.st_size
    mode = oct(attr.st_mode)
    print(f"{mode} {size:>10} {name}")

# Iterate (memory efficient for large directories)
for attr in sftp.listdir_iter('/remote/dir'):
    print(attr.filename)

# Change directory
sftp.chdir('/remote/new_dir')
current = sftp.getcwd()  # '/remote/new_dir'

# Create directory (single level)
sftp.mkdir('/remote/new_dir', mode=0o755)

# Remove directory (must be empty)
sftp.rmdir('/remote/empty_dir')

# Remove file
sftp.remove('/remote/file.txt')  # or sftp.unlink()
```

### File Metadata

```python
# Change permissions
sftp.chmod('/remote/file.txt', 0o644)

# Change owner/group
sftp.chown('/remote/file.txt', uid=1000, gid=1000)

# Modify timestamps
sftp.utime('/remote/file.txt', (1234567890, 1234567890))

# Truncate file
sftp.truncate('/remote/file.txt', 1024)

# Symlinks
sftp.symlink('target_path', 'link_name')
print(sftp.readlink('link_name'))  # 'target_path'
```

## File Transfer Methods

### put() / get() — Simple Transfers

```python
# Upload local → remote
sftp.put('/local/file.txt', '/remote/file.txt')

# Download remote → local
sftp.get('/remote/file.txt', '/local/file.txt')

# With progress callback
def progress(bytes_transferred, total_size):
    if total_size > 0:
        pct = (bytes_transferred / total_size) * 100
        print(f"\r{pct:.1f}% ({bytes_transferred}/{total_size})", end='')

sftp.put('large_file.bin', '/remote/large_file.bin', callback=progress)
```

### putfo() / getfo() — File-like Object Transfers

```python
import io

# Upload from file-like object
data = b"Content to upload"
buf = io.BytesIO(data)
sftp.putfo(buf, '/remote/from_buffer.txt')

# Download to file-like object
dest = io.BytesIO()
sftp.getfo('/remote/file.bin', dest)
downloaded_data = dest.getvalue()

# Upload from open file handle
with open('/local/large_file.bin', 'rb') as f:
    sftp.putfo(f, '/remote/uploaded.bin')
```

### Confirm Upload/Download

```python
# put() and get() confirm by default (stat the file after transfer)
sftp.put('file.txt', '/remote/file.txt', confirm=True)  # default

# Skip confirmation for speed (risky if transfer fails silently)
sftp.put('file.bin', '/remote/file.bin', confirm=False)
```

## SFTPFile Class

Returned by `sftp.open()`. Behaves like a standard Python file object.

```python
with sftp.open('/remote/file.txt', 'w') as f:
    f.write("Hello")
    f.flush()  # Ensure data is sent
    f.tell()   # Current position
    f.seek(0)  # Rewind
    content = f.read()

# As context manager, file is automatically closed
with sftp.open('/remote/file.txt', 'rb') as f:
    data = f.read()
```

## SFTPClient Methods Summary

| Method | Signature | Description |
|--------|-----------|-------------|
| `open()` | `open(filename, mode='r', bufsize=-1)` | Open remote file, returns SFTPFile |
| `get()` | `get(remotepath, localpath, callback=None, prefetch=True)` | Download file |
| `put()` | `put(localpath, remotepath, callback=None, confirm=True)` | Upload file |
| `getfo()` | `getfo(remotepath, fl, callback=None, prefetch=True)` | Download to file-like object |
| `putfo()` | `putfo(fl, remotepath, file_size=0, callback=None, confirm=True)` | Upload from file-like object |
| `listdir()` | `listdir(path='.')` | List filenames in directory |
| `listdir_attr()` | `listdir_attr(path='.')` | List FileAttributes objects |
| `listdir_iter()` | `listdir_iter(path='.', *, recursive=False)` | Memory-efficient iteration |
| `stat()` | `stat(path)` | Get file attributes |
| `lstat()` | `lstat(path)` | Get attributes without following symlinks |
| `chdir()` | `chdir(path)` | Change working directory |
| `getcwd()` | `getcwd()` | Get current working directory |
| `mkdir()` | `mkdir(path, mode=0o777)` | Create directory |
| `rmdir()` | `rmdir(path)` | Remove empty directory |
| `remove()` | `remove(path)` | Remove file |
| `unlink()` | `unlink(path)` | Same as remove() |
| `rename()` | `rename(oldpath, newpath)` | Rename/move file |
| `posix_rename()` | `posix_rename(oldpath, newpath)` | Atomic rename (if server supports) |
| `chmod()` | `chmod(path, mode)` | Change permissions |
| `chown()` | `chown(path, uid, gid)` | Change owner/group |
| `utime()` | `utime(path, times)` | Set access/modification times |
| `truncate()` | `truncate(path, size)` | Truncate file to size |
| `symlink()` | `symlink(source, link_name)` | Create symbolic link |
| `readlink()` | `readlink(path)` | Read symlink target |
| `normalize()` | `normalize(path)` | Normalize path (resolve `.` and `..`) |
| `close()` | `close()` | Close SFTP session |
| `from_transport()` | `SFTPClient.from_transport(t, ...)` | Create from Transport |
| `get_channel()` | `get_channel()` | Get underlying Channel |

## SFTP Attributes Object

Returned by `stat()`, `lstat()`, `listdir_attr()`:

```python
attr = sftp.stat('/remote/file.txt')

# Standard Unix stat attributes
attr.st_mode      # File type and permissions (stat.S_IFREG | 0o644)
attr.st_size      # Size in bytes
attr.st_uid       # User ID
attr.st_gid       # Group ID
attr.st_atime     # Access time (epoch seconds)
attr.st_mtime     # Modification time (epoch seconds)
attr.st_flags     # Flags (if supported)

# Paramiko-specific
attr.filename     # Base filename
attr.longname     # ls -l style string
```

## Error Handling

```python
import paramiko

try:
    with client.open_sftp() as sftp:
        sftp.put('file.txt', '/remote/path/that/does/not/exist/file.txt')
except paramiko.sftp.SFTPError as e:
    print(f"SFTP error: {e}")
except EOFError:
    print("Connection lost")
except Exception as e:
    print(f"Unexpected error: {e}")
```
