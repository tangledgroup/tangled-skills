# Troubleshooting Guide

Common issues and solutions when using pacote.

## Git Authentication Errors

### Problem: Private Repository Access

```bash
# Error message:
GitUnknownError: An unknown git error occurred
ERROR: Repository not found.
fatal: Could not read from remote repository.
```

**Cause:** Attempting to access a private git repository without authentication.

**Solutions:**

1. **Use HTTPS with token (GitHub):**
   ```bash
   npx pacote manifest "git+https://x-access-token:${GITHUB_TOKEN}@github.com/user/private-repo.git#main"
   ```

2. **Configure git credentials:**
   ```bash
   # Set up SSH key
   ssh-keygen -t ed25519 -C "your@email.com"
   # Add to ssh-agent
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   
   # Then use SSH URL
   npx pacote manifest "git+ssh://git@github.com/user/private-repo.git#main"
   ```

3. **Use netrc file for HTTPS authentication:**
   ```bash
   # Create ~/.netrc
   cat > ~/.netrc << EOF
   machine github.com
   login your-username
   password your-token
   EOF
   chmod 600 ~/.netrc
   ```

4. **For public repos, verify the path:**
   ```bash
   # Correct format
   npx pacote manifest "github:npm/cli#v10.0.0"
   
   # Wrong (missing # before tag)
   npx pacote manifest "github:npm/cli@v10.0.0"  # Error
   ```

### Problem: Git Not Installed

```bash
# Error message:
Error: Command failed: git --version
/bin/sh: 1: git: not found
```

**Solution:** Install git on your system:

```bash
# Debian/Ubuntu
sudo apt install git

# macOS
brew install git

# Arch Linux
sudo pacman -S git

# Or disable git packages
npx pacote --allow-git=none manifest package-name
```

## Cache Issues

### Problem: Corrupted Cache

```bash
# Error message:
Error: Integrity check failed for <package>
 EINTEGRITY
```

**Solutions:**

1. **Clear the entire cache:**
   ```bash
   rm -rf ~/.npm/_cacache
   npx pacote --prefer-online manifest lodash
   ```

2. **Use custom cache directory:**
   ```bash
   npx pacote --cache=/tmp/clean-cache manifest express
   ```

3. **Force revalidation:**
   ```bash
   npx pacote --prefer-online manifest react
   ```

### Problem: Cache Hit Stale Data

```bash
# Issue: Getting old package version despite @latest tag
```

**Solution:** Force online validation:
```bash
npx pacote --prefer-online manifest package-name --json
```

### Problem: No Space on Device (Cache Full)

```bash
# Error message:
Error: ENOSPC: no space left on device
```

**Solutions:**

1. **Clear cache:**
   ```bash
   rm -rf ~/.npm/_cacache/*
   ```

2. **Use different cache location:**
   ```bash
   npx pacote --cache=/mnt/large-disk/npm-cache manifest package
   ```

3. **Disable caching for single operation:**
   ```bash
   npx pacote --cache=/tmp/empty-dir manifest package
   ```

## Network Errors

### Problem: Registry Timeout

```bash
# Error message:
Error: ETIMEDOUT
Request timeout
```

**Solutions:**

1. **Increase timeout:**
   ```bash
   npm config set fetch-timeout 120000
   npx pacote manifest large-package
   ```

2. **Use registry mirror (faster in some regions):**
   ```bash
   # China mirror
   npx pacote --registry=https://registry.npmmirror.com manifest lodash
   
   # Or set globally
   npm config set registry https://registry.npmmirror.com
   ```

3. **Check network connectivity:**
   ```bash
   curl -I https://registry.npmjs.org/
   ping registry.npmjs.org
   ```

### Problem: 404 Not Found

```bash
# Error message:
Error: 404 Not Found - GET https://registry.npmjs.org/nonexistent-package
```

**Causes and Solutions:**

1. **Package doesn't exist:**
   ```bash
   # Verify package name
   npm search package-name
   
   # Try pacote with correct name
   npx pacote packument lodash --json | jq '.name'
   ```

2. **Wrong registry for private package:**
   ```bash
   # Use correct registry
   npx pacote --registry=https://private-registry.com manifest @scope/private-package
   ```

3. **Tarball URL is broken:**
   ```bash
   # Verify tarball exists
   curl -I https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz
   
   # Use correct format
   npx pacote manifest "https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz"
   ```

### Problem: 401/403 Authentication Failed

```bash
# Error message:
Error: 401 Unauthorized
Error: 403 Forbidden
```

**Solutions:**

1. **Verify authentication token:**
   ```bash
   # List tokens
   npm token list
   
   # Create new token
   npm token create --read-only
   
   # Set token
   npm config set //registry.npmjs.org/:_authToken=NPM_TOKEN
   ```

2. **Check token scope:**
   ```bash
   # Token needs read access for pacote
   npm token revoke TOKEN_ID
   npm token create --read-only
   ```

3. **Verify registry URL matches token scope:**
   ```bash
   # Check config
   npm config list | grep registry
   
   # Token must match registry exactly
   npm config set //registry.npmjs.org/:_authToken=NPM_TOKEN
   ```

## Permission Issues

### Problem: Permission Denied on Extract

```bash
# Error message:
Error: EACCES: permission denied, extract 'package/index.js'
```

**Solutions:**

1. **Check destination directory permissions:**
   ```bash
   ls -la /destination/folder
   chmod 755 /destination/folder
   ```

2. **Extract with custom permissions:**
   ```bash
   npx pacote extract package@latest ./dest --umask=0o22 --fmode=0o644 --dmode=0o755
   ```

3. **Run as appropriate user:**
   ```bash
   # Avoid running as root unless necessary
   sudo -u username npx pacote extract package@latest /home/username/project
   ```

4. **Check umask:**
   ```bash
   echo "Current umask: $(umask)"
   umask 022
   npx pacote extract package@latest ./dest
   ```

### Problem: Root-Owned Files in node_modules

```bash
# Issue: Files extracted as root when using sudo
```

**Solution:** Pacote automatically handles this on Unix:

```bash
# When running as root, pacote sets ownership to match destination folder
sudo npx pacote extract package@latest /home/user/project/node_modules/package

# Verify ownership
ls -la /home/user/project/node_modules/package/
# Files should be owned by user, not root
```

## File System Issues

### Problem: Path Too Long

```bash
# Error message:
Error: ENAMETOOLONG: name too long, open 'very/long/path/...'
```

**Solutions:**

1. **Use shorter destination path:**
   ```bash
   npx pacote extract package@latest ./p
   ```

2. **On Windows, use short paths or enable long paths:**
   ```bash
   # Enable long paths in Windows 10+
   reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1
   ```

3. **Extract to root-level directory:**
   ```bash
   npx pacote extract package@latest /tmp/package
   ```

### Problem: No Space Left on Device

```bash
# Error message:
Error: ENOSPC: no space left on device
```

**Solutions:**

1. **Check disk space:**
   ```bash
   df -h /destination
   ```

2. **Free up space:**
   ```bash
   # Clear npm cache
   npm cache clean --force
   
   # Remove old extractions
   rm -rf /tmp/pacote-*
   ```

3. **Use different disk:**
   ```bash
   npx pacote extract package@latest /mnt/large-disk/packages
   ```

## Package-Specific Issues

### Problem: Large Package Downloads Fail

```bash
# Issue: Memory issues with very large packages
```

**Solutions:**

1. **Stream instead of buffering:**
   ```bash
   # Don't use tarball() buffer method
   npx pacote tarball large-package@latest - | tar -xzC ./dest
   ```

2. **Extract directly:**
   ```bash
   npx pacote extract large-package@latest ./dest
   ```

3. **Increase Node.js memory:**
   ```bash
   NODE_OPTIONS="--max-old-space-size=4096" npx pacote manifest large-package
   ```

### Problem: Git Package Prepare Script Fails

```bash
# Error message:
Error: prepare script failed for <package>
```

**Cause:** The package's prepare script requires dependencies or tools not available.

**Solutions:**

1. **Install build dependencies:**
   ```bash
   # Debian/Ubuntu
   sudo apt install build-essential python3
   
   # macOS
   brew install python
   
   # Then retry
   npx pacote extract "github:user/repo#main" ./dest
   ```

2. **Skip prepare scripts (if possible):**
   ```bash
   # Download tarball and extract manually
   npx pacote tarball "github:user/repo#main" package.tgz
   tar -xzf package.tgz -C ./dest
   ```

3. **Use published version instead:**
   ```bash
   # If available on registry
   npx pacote extract package-name@latest ./dest
   ```

### Problem: Version Resolution Fails

```bash
# Error message:
Error: No versions available matching <range>
```

**Solutions:**

1. **Check available versions:**
   ```bash
   npx pacote packument package-name --json | jq 'keys(.versions)'
   ```

2. **Use exact version:**
   ```bash
   # Instead of range
   npx pacote manifest "package@1.2.3" --json
   ```

3. **Check dist-tags:**
   ```bash
   npx pacote packument package-name --json | jq '.dist-tags'
   ```

## Debugging

### Enable Verbose Logging

```bash
# npm debug mode
export NPM_DEBUG=1
npx pacote manifest lodash

# Or use loglevel
npx pacote --loglevel=verbose manifest express

# Debug specific operations
DEBUG=pacote:* npx pacote manifest react
```

### Check Effective Configuration

```bash
# View all configuration
npm config list

# Check registry being used
npm config get registry

# Check cache location
npm config get cache

# Check authentication (don't print values)
npm config list | grep -v "^;.*$" | grep auth
```

### Test Connectivity

```bash
# Test registry connectivity
curl -I https://registry.npmjs.org/

# Test specific package
curl -s https://registry.npmjs.org/lodash | jq '.name'

# Test git connectivity
git ls-remote https://github.com/npm/cli.git

# Test tarball download
curl -I https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz
```

### Inspect Package Without Extracting

```bash
# List files in tarball
npx pacote tarball package@latest - | tar -tz

# View package.json without extracting
npx pacote tarball package@latest - | tar -xzO package/package.json

# Get manifest metadata
npx pacote manifest package@latest --json | jq '{name, version, dependencies}'
```

## Common Error Patterns

### EINTEGRITY - Integrity Mismatch

```bash
# Cause: Downloaded file doesn't match expected hash
# Solution: Clear cache and retry
rm -rf ~/.npm/_cacache
npx pacote --prefer-online manifest package
```

### ENOENT - File Not Found

```bash
# Cause: Local path doesn't exist
# Solution: Verify path exists
ls -la ./path/to/package.json
npx pacote manifest "file:/absolute/path/to/package.json"
```

### E404 - Package Not Found

```bash
# Cause: Package doesn't exist in registry
# Solution: Check package name or use different registry
npm search package-name
npx pacote --registry=https://private-registry.com manifest @scope/package
```

### E401/E403 - Authentication Errors

```bash
# Cause: Invalid or missing authentication
# Solution: Verify token and registry match
npm config set //registry.npmjs.org/:_authToken=NPM_TOKEN
npx pacote packument private-package --json
```

## Getting Help

### Check Documentation

```bash
# CLI help
npx pacote --help

# npm documentation
https://docs.npmjs.com/

# pacote GitHub repo
https://github.com/npm/pacote

# npm-package-arg for specifier formats
https://npm.im/npm-package-arg
```

### Report Issues

If you encounter an unresolved issue:

1. **Collect debug information:**
   ```bash
   NPM_DEBUG=1 npx pacote manifest package 2>&1 | tee pacote-error.log
   npm config list >> pacote-error.log
   node --version >> pacote-error.log
   ```

2. **Check existing issues:**
   - https://github.com/npm/pacote/issues

3. **File new issue with:**
   - Error message and stack trace
   - Package specifier used
   - npm and Node.js versions
   - Relevant configuration (redact tokens)
