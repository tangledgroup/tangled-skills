# Migration Guide

Strategies for migrating from legacy password hashing algorithms to Argon2.

## Current State Assessment

### Identifying Legacy Hashes

Detect which hashing algorithm is in use:

```python
import re

def detect_hash_algorithm(hash_string):
    """Identify hashing algorithm from hash format."""
    if hash_string.startswith('$2a$') or hash_string.startswith('$2b$') or hash_string.startswith('$2y$'):
        return 'bcrypt'
    elif hash_string.startswith('$argon2'):
        return 'argon2'
    elif hash_string.startswith('$scrypt$'):
        return 'scrypt'
    elif hash_string.startswith('$pbkdf2'):
        return 'pbkdf2'
    elif hash_string.startswith('$yescrypt$'):
        return 'yescrypt'
    elif len(hash_string) == 40:
        return 'sha1'  # Likely plain SHA1
    elif len(hash_string) == 64:
        return 'sha256'  # Likely plain SHA256
    else:
        return 'unknown'

# Scan existing hashes
for user in db.users.find({}):
    algo = detect_hash_algorithm(user.password_hash)
    print(f"{user.username}: {algo}")
```

### Migration Priority

| Current Algorithm | Risk Level | Migration Priority |
|-------------------|------------|-------------------|
| Plain text | Critical | Immediate |
| MD5, SHA1 | Critical | Immediate |
| SHA256 (no salt) | High | ASAP |
| PBKDF2-SHA1 | Medium | Planned |
| bcrypt | Low | Optional |
| scrypt, yescrypt | Low | Optional |
| Argon2 (old params) | Low | Gradual |

## Migration Strategies

### Strategy 1: Progressive Rehashing (Recommended)

Rehash passwords on successful login. Zero downtime, gradual migration.

```python
import argon2
from argon2.exceptions import VerifyMismatchError

ph_argon2 = argon2.PasswordHasher()

def authenticate_with_migration(username, password):
    """Authenticate and migrate hash if needed."""
    user = db.get_user(username)
    
    algo = detect_hash_algorithm(user.password_hash)
    
    if algo == 'argon2':
        # Already using Argon2, just verify
        try:
            ph_argon2.verify(user.password_hash, password)
        except VerifyMismatchError:
            return False
        
        # Check if parameters need update
        if ph_argon2.check_needs_rehash(user.password_hash):
            new_hash = ph_argon2.hash(password)
            db.update_password_hash(username, new_hash)
            print(f"Migrated {username} to current Argon2 parameters")
        
        return True
    
    elif algo == 'bcrypt':
        # Verify with bcrypt first
        import bcrypt
        
        try:
            if not bcrypt.checkpw(
                password.encode('utf-8'),
                user.password_hash.encode('utf-8')
            ):
                return False
            
            # Migrate to Argon2
            new_hash = ph_argon2.hash(password)
            db.update_password_hash(username, new_hash)
            print(f"Migrated {username} from bcrypt to Argon2")
            
            return True
            
        except Exception as e:
            print(f"bcrypt verification failed: {e}")
            return False
    
    elif algo in ('sha256', 'sha1'):
        # Legacy hash - verify then migrate
        import hashlib
        
        if algo == 'sha256':
            computed = hashlib.sha256(password.encode()).hexdigest()
        else:
            computed = hashlib.sha1(password.encode()).hexdigest()
        
        if computed != user.password_hash:
            return False
        
        # Migrate to Argon2
        new_hash = ph_argon2.hash(password)
        db.update_password_hash(username, new_hash)
        print(f"Migrated {username} from {algo} to Argon2")
        
        return True
    
    else:
        print(f"Unknown hash algorithm: {algo}")
        return False
```

**Advantages:**
- No downtime or bulk processing
- Only processes active users
- Maintains security during transition
- Automatic parameter updates

**Disadvantages:**
- Inactive users remain on old algorithm
- Requires multiple authentication code paths temporarily

### Strategy 2: Forced Migration on Next Login

Require password reset for all users with legacy hashes.

```python
from flask import flash, redirect, url_for

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    user = db.get_user(username)
    algo = detect_hash_algorithm(user.password_hash)
    
    if algo in ('sha1', 'md5', 'plain'):
        # Force password reset for insecure hashes
        flash("For security reasons, please reset your password", "warning")
        session['reset_required'] = True
        session['temp_user_id'] = user._id
        return redirect(url_for('force_password_reset'))
    
    # Normal authentication flow
    if authenticate_with_migration(username, password):
        return redirect(url_for('dashboard'))
    
    flash("Invalid credentials", "error")
    return render_template('login.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def force_password_reset():
    """Forced password reset for legacy hash migration."""
    if request.method == 'POST':
        new_password = request.form['new_password']
        
        # Validate password strength
        if not is_strong_password(new_password):
            flash("Password must be stronger", "error")
            return render_template('reset.html')
        
        # Hash with Argon2
        ph = argon2.PasswordHasher()
        new_hash = ph.hash(new_password)
        
        db.update_password_hash(
            session['temp_user_id'],
            new_hash,
            algorithm='argon2'
        )
        
        flash("Password updated successfully", "success")
        return redirect(url_for('login'))
    
    return render_template('reset.html')
```

**Advantages:**
- Complete migration in one pass
- Opportunity to enforce stronger passwords
- Clean break from legacy systems

**Disadvantages:**
- User friction and support burden
- May lock out users who don't log in
- Requires communication campaign

### Strategy 3: Bulk Migration with Exported Passwords

Only viable if passwords were stored reversibly (not recommended).

```python
from argon2 import PasswordHasher

ph = argon2.PasswordHasher()

def bulk_migrate_users():
    """Migrate all users in batch (requires plaintext access)."""
    migrated = 0
    failed = 0
    
    for user in db.users.find({}):
        try:
            # Only works if passwords are decryptable!
            plaintext = decrypt_password(user.encrypted_password)
            new_hash = ph.hash(plaintext)
            
            db.update_one(
                {'_id': user._id},
                {'$set': {
                    'password_hash': new_hash,
                    'hash_algorithm': 'argon2',
                    'migrated_at': datetime.now()
                }}
            )
            migrated += 1
            
        except Exception as e:
            print(f"Failed to migrate {user.username}: {e}")
            failed += 1
    
    print(f"Migrated: {migrated}, Failed: {failed}")
```

**Warning:** This approach should only be used if passwords are currently stored in an insecure reversible manner. The goal is to improve security, not maintain it.

## Algorithm-Specific Migration

### From bcrypt

```python
import bcrypt
import argon2

# Both libraries use similar hash formats
bcrypt_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8LRMYicE5BDrI7gB4iK"
argon2_hash = "$argon2id$v=19$m=65536,t=3,p=4$cuVVYbPjX...

def migrate_bcrypt_to_argon2():
    """Dual-verify during migration period."""
    ph_argon2 = argon2.PasswordHasher()
    
    def authenticate(username, password):
        user = db.get_user(username)
        
        if user.hash_algorithm == 'argon2':
            # Already migrated
            try:
                ph_argon2.verify(user.password_hash, password)
                return True
            except argon2.exceptions.VerifyMismatchError:
                return False
        
        elif user.hash_algorithm == 'bcrypt':
            # Still using bcrypt
            if bcrypt.checkpw(
                password.encode('utf-8'),
                user.password_hash.encode('utf-8')
            ):
                # Migrate on success
                new_hash = ph_argon2.hash(password)
                db.update_password_hash(username, new_hash, 'argon2')
                return True
            
            return False
    
    return authenticate
```

### From PBKDF2

```python
import hashlib
import base64
import argon2

def parse_pbkdf2_hash(hash_string):
    """Parse Django-style PBKDF2 hash."""
    # Format: pbkdf2_sha256$iterations$salt$hash
    algo, iterations, salt, hash_val = hash_string.split('$')[1:]
    iterations = int(iterations)
    salt = base64.standard_b64decode(salt)
    hash_val = base64.standard_b64decode(hash_val)
    
    return algo, iterations, salt, hash_val

def verify_pbkdf2(password, hash_string):
    """Verify PBKDF2 hash."""
    algo, iterations, salt, expected = parse_pbkdf2_hash(hash_string)
    
    if algo == 'pbkdf2_sha256':
        computed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            iterations,
            dklen=len(expected)
        )
    else:
        raise ValueError(f"Unknown PBKDF2 variant: {algo}")
    
    return computed == expected

def migrate_pbkdf2_to_argon2():
    """Migrate from PBKDF2 to Argon2."""
    ph_argon2 = argon2.PasswordHasher()
    
    def authenticate(username, password):
        user = db.get_user(username)
        
        if user.hash_algorithm == 'argon2':
            try:
                ph_argon2.verify(user.password_hash, password)
                return True
            except argon2.exceptions.VerifyMismatchError:
                return False
        
        elif user.hash_algorithm.startswith('pbkdf2'):
            if verify_pbkdf2(password, user.password_hash):
                # Migrate to Argon2
                new_hash = ph_argon2.hash(password)
                db.update_password_hash(username, new_hash, 'argon2')
                return True
            
            return False
    
    return authenticate
```

### From Plain Hash (SHA1/SHA256)

```python
import hashlib
import argon2

def migrate_plain_hash_to_argon2():
    """Migrate from unsalted hashes (high priority!)."""
    ph_argon2 = argon2.PasswordHasher()
    
    def authenticate(username, password):
        user = db.get_user(username)
        
        if user.hash_algorithm == 'argon2':
            try:
                ph_argon2.verify(user.password_hash, password)
                return True
            except argon2.exceptions.VerifyMismatchError:
                return False
        
        elif user.hash_algorithm == 'sha256':
            # Verify with SHA256
            computed = hashlib.sha256(password.encode()).hexdigest()
            
            if computed == user.password_hash:
                # CRITICAL: Migrate immediately
                new_hash = ph_argon2.hash(password)
                db.update_password_hash(username, new_hash, 'argon2')
                print(f"URGENT: Migrated {username} from insecure SHA256")
                return True
            
            return False
    
    return authenticate
```

## Migration Monitoring

### Track Progress

```python
from datetime import datetime
from collections import Counter

def get_migration_stats():
    """Monitor migration progress."""
    users = list(db.users.find({}))
    
    algo_counts = Counter(
        detect_hash_algorithm(u.password_hash) 
        for u in users
    )
    
    total = len(users)
    argon2_count = algo_counts.get('argon2', 0)
    progress = (argon2_count / total * 100) if total > 0 else 0
    
    print(f"Migration Progress: {progress:.1f}%")
    print(f"Total users: {total}")
    print(f"Argon2: {argon2_count}")
    print(f"Remaining by algorithm:")
    
    for algo, count in algo_counts.items():
        if algo != 'argon2':
            print(f"  {algo}: {count} ({count/total*100:.1f}%)")
    
    return {
        'total': total,
        'argon2': argon2_count,
        'progress': progress,
        'by_algorithm': dict(algo_counts)
    }

# Run weekly to track progress
import schedule
schedule.every().monday.do(get_migration_stats)
```

### Alert on Stalled Migration

```python
def check_migration_stall():
    """Alert if migration isn't progressing."""
    stats = get_migration_stats()
    
    # Alert if <50% migrated after 3 months
    if stats['progress'] < 50:
        legacy_users = db.users.find({
            'hash_algorithm': {'$ne': 'argon2'},
            'last_login': {
                '$lt': datetime.now() - timedelta(days=90)
            }
        })
        
        inactive_legacy_count = list(legacy_users).count()
        
        if inactive_legacy_count > 100:
            send_alert(
                f"Migration stalled: {inactive_legacy_count} users "
                f"haven't logged in to migrate"
            )
```

## Post-Migration Cleanup

### Remove Legacy Code

After 100% migration:

```python
# Before: Dual verification code
def authenticate(username, password):
    user = db.get_user(username)
    
    if user.hash_algorithm == 'argon2':
        # Argon2 verification...
        pass
    elif user.hash_algorithm == 'bcrypt':
        # bcrypt verification...
        pass
    # ... more legacy code

# After: Clean Argon2-only code
def authenticate(username, password):
    user = db.get_user(username)
    
    try:
        ph.verify(user.password_hash, password)
        return True
    except argon2.exceptions.VerifyMismatchError:
        return False
```

### Database Cleanup

```python
# Remove algorithm field after full migration
db.users.update_many(
    {},
    {'$unset': {'hash_algorithm': ''}}
)

# Add constraint to prevent non-Argon2 hashes
db.users.create_index(
    'password_hash',
    {'partialFilterExpression': {
        'password_hash': {'$not': {'$regex': '^$argon2'}}
    }}
)
```

## Best Practices

### Do's

✅ Test migration on staging environment first
✅ Keep legacy verification code until 100% migrated
✅ Monitor migration progress weekly
✅ Communicate with users about forced migrations
✅ Log all migration events for audit trail
✅ Use progressive rehashing when possible

### Don'ts

❌ Never delete legacy hashes before successful Argon2 hash created
❌ Don't migrate inactive users in bulk (they'll never login)
❌ Don't remove legacy verification code prematurely
❌ Don't use bulk migration unless passwords are reversible
❌ Don't forget to update parameter checks after migration

### Rollback Plan

```python
# Keep old hashes in separate field during transition
def safe_migrate_with_rollback(username, password):
    """Migration with rollback capability."""
    user = db.get_user(username)
    
    # Verify with current algorithm first
    if not verify_with_current_algo(user.password_hash, password):
        return False
    
    # Create new Argon2 hash
    ph_argon2 = argon2.PasswordHasher()
    new_hash = ph_argon2.hash(password)
    
    # Update with backup of old hash
    db.update_one(
        {'_id': user._id},
        {
            '$set': {
                'password_hash': new_hash,
                'hash_algorithm': 'argon2',
                'password_hash_backup': user.password_hash,  # Keep backup
                'migrated_at': datetime.now()
            }
        }
    )
    
    # After 30 days, verify no issues, then remove backups
    return True
```
