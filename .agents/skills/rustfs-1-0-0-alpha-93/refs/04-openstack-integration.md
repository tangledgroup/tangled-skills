# OpenStack Swift and Keystone Integration

This reference covers RustFS integration with OpenStack Swift API and Keystone authentication.

## Overview

RustFS provides native support for:
- **OpenStack Swift API**: Full compatibility with Swift protocol
- **Keystone Authentication**: X-Auth-Token based authentication from Keystone v3
- **Swift Metadata**: Object and container metadata operations

**Status in alpha.93:**
- ✅ Keystone Auth: Available
- ✅ Swift API: Available  
- 🚧 Swift Metadata Ops: Partial support

## Swift API Quick Start

### Install Swift Client

```bash
# Python Swift client
pip install python-swiftclient

# Or use swift command-line client
pip install swift
```

### Configure Swift Connection

**~/.swiftrc:**
```ini
[DEFAULT]
authurl = http://keystone:5000/v3
username = myuser
password = mypassword
project_name = myproject
region_name = RegionOne
```

**Environment Variables:**
```bash
export OS_AUTH_URL=http://keystone:5000/v3
export OS_PROJECT_NAME=myproject
export OS_USERNAME=myuser
export OS_PASSWORD=mypassword
export OS_REGION_NAME=RegionOne
```

### Basic Swift Operations

```bash
# List containers (equivalent to S3 buckets)
swift list

# Create container
swift upload my-container README.txt

# Or explicitly create
swift container create my-container

# Upload object
swift upload my-container myfile.txt

# Download object
swift download my-container myfile.txt

# Delete object
swift delete my-container myfile.txt

# List container contents
swift list my-container

# Show container info
swift container info my-container
```

## Keystone Integration

### Architecture

```
┌─────────────┐     X-Auth-Token      ┌──────────┐
│   Client    │ ─────────────────────► │  RustFS  │
│             │                        │          │
└─────────────┘                        └────┬─────┘
                                            │
                                            │ Validate token
                                    ┌───────▼───────┐
                                    │   Keystone    │
                                    │   (v3 API)    │
                                    └───────────────┘
```

### Keystone Configuration

#### Prerequisites

1. Running Keystone instance with v3 API
2. Project, user, and role created in Keystone
3. Network connectivity between RustFS and Keystone

#### Create Keystone Resources

```bash
# Source admin credentials
source admin-openrc.sh

# Create project for RustFS users
openstack project create --domain default \
  --description "RustFS Storage Project" \
  rustfs-project

# Create user
openstack user create --domain default \
  --password <password> \
  rustfs-user

# Create role
openstack role create storage-user

# Assign role to user in project
openstack role add --project rustfs-project \
  --user rustfs-user \
  storage-user
```

### RustFS Keystone Configuration

#### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `RUSTFS_KEystone_ENABLE` | Enable Keystone auth | `true` |
| `RUSTFS_KEystone_AUTH_URL` | Keystone authentication URL | `http://keystone:5000/v3` |
| `RUSTFS_KEystone_REGION` | Keystone region | `RegionOne` |

```bash
# Enable Keystone integration
export RUSTFS_KEystone_ENABLE=true
export RUSTFS_KEystone_AUTH_URL=http://keystone:5000/v3
export RUSTFS_KEystone_REGION=RegionOne
```

#### Docker Compose with Keystone

```yaml
services:
  keystone:
    image: library/keystone:latest
    environment:
      - DATABASE_CONNECTION=mysql://keystone:secret@mysql/keystone
      - MEMCACHED_HOST=memcached
      - ADMIN_PASSWORD=adminpassword
    ports:
      - "5000:5000"
    depends_on:
      - mysql
      - memcached

  rustfs:
    image: rustfs/rustfs:1.0.0-alpha.93
    environment:
      - RUSTFS_KEystone_ENABLE=true
      - RUSTFS_KEystone_AUTH_URL=http://keystone:5000/v3
      - RUSTFS_KEystone_REGION=RegionOne
      - RUSTFS_VOLUMES=/data/rustfs{0..3}
    depends_on:
      - keystone

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=keystone
      - MYSQL_USER=keystone
      - MYSQL_PASSWORD=secret

  memcached:
    image: memcached:latest
```

### Authentication Flow

#### Step 1: Get Token from Keystone

```bash
# Request token
curl -i -X POST http://keystone:5000/v3/auth/tokens \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "auth": {
      "identity": {
        "methods": ["password"],
        "password": {
          "user": {
            "domain": {"name": "default"},
            "name": "rustfs-user",
            "password": "<password>"
          }
        }
      },
      "scope": {
        "project": {
          "domain": {"name": "default"},
          "name": "rustfs-project"
        }
      }
    }
  }'

# Response includes X-Subject-Token header
# Copy this token for Swift API calls
```

#### Step 2: Use Token with RustFS Swift API

```bash
# List containers using Keystone token
curl -i http://rustfs:9000/v3 \
  -H "X-Auth-Token: <token-from-keystone>"

# Upload object
curl -i -X PUT "http://rustfs:9000/v3/AUTH_<project-id>/my-container/myfile.txt" \
  -H "X-Auth-Token: <token-from-keystone>" \
  -H "Content-Type: text/plain" \
  --data-binary @myfile.txt
```

## Swift API Reference

### Container Operations

#### Create Container

```bash
# Using swift client
swift container create my-container

# Using curl
curl -i -X PUT http://rustfs:9000/v3/AUTH_<tenant>/my-container \
  -H "X-Auth-Token: <token>"
```

#### List Containers

```bash
# All containers
swift list

# With verbose output
swift list -v

# Using curl
curl -i http://rustfs:9000/v3/AUTH_<tenant> \
  -H "X-Auth-Token: <token>"
```

#### Delete Container

```bash
# Must be empty first
swift delete my-container/object1.txt
swift container delete my-container

# Using curl
curl -i -X DELETE http://rustfs:9000/v3/AUTH_<tenant>/my-container \
  -H "X-Auth-Token: <token>"
```

#### Container Metadata

```bash
# Set container metadata
swift post my-container \
  -m meta-key1:value1 \
  -m meta-key2:value2

# Get container metadata
swift container info my-container

# Using curl
curl -i -X POST "http://rustfs:9000/v3/AUTH_<tenant>/my-container" \
  -H "X-Auth-Token: <token>" \
  -H "X-Container-Meta-Key1: value1" \
  -H "X-Container-Meta-Key2: value2"
```

### Object Operations

#### Upload Object

```bash
# Basic upload
swift upload my-container myfile.txt

# With content type
swift upload my-container image.jpg \
  -H "Content-Type:image/jpeg"

# With object metadata
swift upload my-container document.pdf \
  -H "Content-Type:application/pdf" \
  -m author:JohnDoe \
  -m version:1.0

# Using curl
curl -i -X PUT "http://rustfs:9000/v3/AUTH_<tenant>/my-container/myfile.txt" \
  -H "X-Auth-Token: <token>" \
  -H "Content-Type: text/plain" \
  --data-binary @myfile.txt
```

#### Download Object

```bash
# Download to file
swift download my-container myfile.txt

# Download to stdout
swift download my-container myfile.txt -

# Using curl
curl -i http://rustfs:9000/v3/AUTH_<tenant>/my-container/myfile.txt \
  -H "X-Auth-Token: <token>" \
  -o myfile.txt
```

#### Delete Object

```bash
# Single object
swift delete my-container myfile.txt

# Multiple objects
swift delete my-container file1.txt file2.txt file3.txt

# Using curl
curl -i -X DELETE "http://rustfs:9000/v3/AUTH_<tenant>/my-container/myfile.txt" \
  -H "X-Auth-Token: <token>"
```

#### List Objects

```bash
# Basic listing
swift list my-container

# Verbose listing
swift list -v my-container

# Limit results
swift list my-container -n 10

# With prefix
swift list my-container --prefix docs/

# Using curl
curl -i "http://rustfs:9000/v3/AUTH_<tenant>/my-container" \
  -H "X-Auth-Token: <token>"
```

### Object Metadata

#### Set Object Metadata

```bash
# Using swift client
swift post my-container myfile.txt \
  -m meta-author:JohnDoe \
  -m meta-version:2.0 \
  -m meta-department:Engineering

# Using curl
curl -i -X POST "http://rustfs:9000/v3/AUTH_<tenant>/my-container/myfile.txt" \
  -H "X-Auth-Token: <token>" \
  -H "X-Object-Meta-Author: JohnDoe" \
  -H "X-Object-Meta-Version: 2.0"
```

#### Get Object Metadata

```bash
# Using swift client
swift object info my-container myfile.txt

# Using curl (HEAD request)
curl -i -X HEAD "http://rustfs:9000/v3/AUTH_<tenant>/my-container/myfile.txt" \
  -H "X-Auth-Token: <token>"
```

#### Delete Object Metadata

```bash
# Remove specific metadata key
swift post my-container myfile.txt \
  -m meta-author:

# Using curl
curl -i -X POST "http://rustfs:9000/v3/AUTH_<tenant>/my-container/myfile.txt" \
  -H "X-Auth-Token: <token>" \
  -H "X-Object-Meta-Author:"
```

## Advanced Swift Features

### Bulk Operations

#### Bulk Delete

```bash
# Create delete file with object paths
cat > deletes.txt <<EOF
DELETE /v3/AUTH_<tenant>/my-container/file1.txt
DELETE /v3/AUTH_<tenant>/my-container/file2.txt
DELETE /v3/AUTH_<tenant>/my-container/file3.txt
EOF

# Execute bulk delete
curl -i -X POST "http://rustfs:9000/bulk-delete" \
  -H "X-Auth-Token: <token>" \
  --data-binary @deletes.txt
```

#### Bulk Upload

```bash
# Create upload file
cat > uploads.txt <<EOF
UPLOAD /v3/AUTH_<tenant>/my-container/file1.txt @file1.txt
UPLOAD /v3/AUTH_<tenant>/my-container/file2.txt @file2.txt
UPLOAD /v3/AUTH_<tenant>/my-container/file3.txt @file3.txt
EOF

# Execute bulk upload
curl -i -X POST "http://rustfs:9000/bulk-upload" \
  -H "X-Auth-Token: <token>" \
  --data-binary @uploads.txt
```

### Container Quotas

#### Set Container Quota

```bash
# Limit container to 1GB (1073741824 bytes)
swift post my-container \
  -H "X-Container-Meta-Quota-Bytes: 1073741824"

# Limit to 10000 objects
swift post my-container \
  -H "X-Container-Meta-Quota-Count: 10000"
```

### Versioning (Swift Style)

Swift uses versioned containers differently than S3:

```bash
# Create versioned container
swift container create my-container-versioned

# Create version container
swift container create my-container-versions

# Enable versioning
swift post my-container \
  -H "X-Container-Meta-Old-Container: my-container-versions"

# Upload object (old versions go to version container)
swift upload my-container myfile.txt
swift upload my-container myfile.txt --file myfile-v2.txt
swift upload my-container myfile.txt --file myfile-v3.txt

# List versions
swift list my-container-versions
```

## Python Swift Client Examples

### Basic Usage

```python
from swiftclient import client

# Connect to Swift
conn = client.Connection(
    authurl='http://keystone:5000/v3',
    user='rustfs-user',
    key='password',
    tenant_name='rustfs-project',
    region_name='RegionOne'
)

# List containers
containers = conn.get_account()
for container in containers['containers']:
    print(f"Container: {container['name']}, Objects: {container['object_count']}")

# List objects in container
objects = conn.get_container('my-container')
for obj in objects:
    print(f"Object: {obj['name']}, Size: {obj['bytes']}")

# Upload object
conn.put_object('my-container', 'myfile.txt', file(obj('myfile.txt', 'rb'))

# Download object
content = conn.get_object('my-container', 'myfile.txt')
with open('downloaded.txt', 'wb') as f:
    f.write(content)

# Delete object
conn.delete_object('my-container', 'myfile.txt')
```

### With Keystone Token

```python
from keystoneauth1 import session, identity
from swiftclient import client

# Create Keystone session
auth = identity.V3PasswordAuth(
    auth_url='http://keystone:5000/v3',
    username='rustfs-user',
    password='password',
    project_name='rustfs-project',
    project_domain_id='default',
    user_domain_id='default'
)

sess = session.Session(auth=auth)
token = auth.get_token(sess)

# Use token with Swift client
conn = client.Connection(
    authurl='http://rustfs:9000/v3',
    token=str(token),
    tenant_name='rustfs-project'
)

# Now use conn as normal
containers = conn.get_account()
```

### With Metadata

```python
from swiftclient import client

conn = client.Connection(
    authurl='http://keystone:5000/v3',
    user='rustfs-user',
    key='password',
    tenant_name='rustfs-project'
)

# Upload with metadata
metadata = {
    'author': 'John Doe',
    'version': '1.0',
    'department': 'Engineering'
}

conn.put_object(
    'my-container',
    'document.pdf',
    file('document.pdf', 'rb'),
    headers={'Content-Type': 'application/pdf'},
    resp_meta=metadata
)

# Get object with metadata
obj, metadata = conn.get_object('my-container', 'document.pdf', resp_true_meta=True)
print(f"Author: {metadata.get('author')}")
print(f"Version: {metadata.get('version')}")
```

## Troubleshooting Keystone Integration

### Token Validation Issues

```bash
# Check if Keystone is accessible
curl http://keystone:5000/v3

# Verify token format
curl -i http://keystone:5000/v3/auth/tokens \
  -H "X-Subject-Token: <token>"

# Check RustFS logs for authentication errors
docker logs rustfs | grep -i keystone
```

### Common Issues

**Issue: Token not accepted by RustFS**

```bash
# Verify Keystone URL is correct
export RUSTFS_KEystone_AUTH_URL=http://keystone:5000/v3

# Check network connectivity from RustFS to Keystone
docker exec rustfs curl http://keystone:5000/v3

# Ensure region matches
export RUSTFS_KEystone_REGION=RegionOne
```

**Issue: Permission denied errors**

```bash
# Verify user has correct role
openstack role list --user rustfs-user --project rustfs-project

# Check if role has sufficient permissions
openstack role show storage-user
```

## Migration from Swift to RustFS

### Compatibility Notes

RustFS Swift API is compatible with most standard Swift operations:

| Feature | Status | Notes |
|---------|--------|-------|
| Container CRUD | ✅ Full | Create, list, delete containers |
| Object CRUD | ✅ Full | Upload, download, delete objects |
| Metadata | 🚧 Partial | Basic metadata operations supported |
| Versioning | ✅ Full | Swift-style versioned containers |
| Quotas | ✅ Full | Container quotas supported |
| Bulk Operations | ✅ Full | Bulk delete and upload |
| Account Info | ✅ Full | get_account equivalent |

### Testing Compatibility

```bash
# Test basic operations
swift container create test-container
swift upload test-container test.txt
swift download test-container test.txt
swift delete test-container test.txt
swift container delete test-container

# Test metadata
swift upload test-container meta.txt -m key:value
swift post test-container meta.txt -m key2:value2
swift object info test-container meta.txt

# Test versioning
swift container create versions
swift post main-container -H "X-Container-Meta-Old-Container: versions"
```

## Best Practices

### Security

1. **Use Keystone for centralized authentication**: Don't rely on basic access keys in production
2. **Enable TLS for Keystone communication**: Use HTTPS for Keystone API
3. **Rotate tokens regularly**: Implement token refresh logic in applications
4. **Use least-privilege roles**: Create specific roles for different use cases

### Performance

1. **Cache tokens**: Reuse tokens within their validity period
2. **Batch operations**: Use bulk upload/delete for multiple objects
3. **Parallel uploads**: Upload multiple objects concurrently
4. **Monitor Keystone load**: Token validation adds latency

### Operations

1. **Monitor token expiration**: Implement automatic token refresh
2. **Log authentication failures**: Track failed auth attempts
3. **Test failover**: Ensure applications handle Keystone unavailability
4. **Document integration**: Maintain clear documentation of Keystone setup
