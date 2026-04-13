# Authorization Policies

Authorization policies define what permissions each identity has access to. This document covers implementing custom authorization policies with various backends and patterns.

## Basic Structure

All authorization policies must implement `AbstractAuthorizationPolicy`:

```python
from aiohttp_security.abc import AbstractAuthorizationPolicy
from typing import Optional, Union
from enum import Enum


class MyAuthorizationPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity: str) -> Optional[str]:
        """Retrieve the user_id for this identity.
        
        Return the user_id if the identity is valid, None otherwise.
        This is called to determine if a user exists and is authorized.
        """
        pass
    
    async def permits(self, identity: Optional[str], permission: Union[str, Enum],
                     context: Optional[dict] = None) -> bool:
        """Check if the identity has the requested permission.
        
        Return True if the identity is allowed the permission in the
        current context, else return False.
        
        identity is None for anonymous users.
        """
        pass
```

## Dictionary-Based Authorization

Simple in-memory authorization using a dictionary. Good for small apps or demos.

### Basic Example

```python
from aiohttp_security.abc import AbstractAuthorizationPolicy


class DictionaryAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, user_map):
        """
        Args:
            user_map: Dict mapping identity to (username, permissions tuple)
        """
        self.user_map = user_map
    
    async def authorized_userid(self, identity):
        return identity if identity in self.user_map else None
    
    async def permits(self, identity, permission, context=None):
        if identity is None or identity not in self.user_map:
            return False
        
        username, permissions = self.user_map[identity]
        return permission in permissions


# Usage
user_map = {
    "alice_identity": ("alice", ("read", "write", "delete")),
    "bob_identity": ("bob", ("read",)),
    None: (None, ())  # Anonymous user has no permissions
}

policy = DictionaryAuthorizationPolicy(user_map)
```

### With NamedTuple Users

```python
from typing import NamedTuple, Dict, Optional


class User(NamedTuple):
    username: str
    password: str  # For authentication
    permissions: tuple


user_map: Dict[Optional[str], User] = {
    "alice": User("alice", "password123", ("public", "protected")),
    "bob": User("bob", "secret456", ("public",)),
}


class DictionaryAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, user_map):
        self.user_map = user_map
    
    async def authorized_userid(self, identity):
        return identity if identity in self.user_map else None
    
    async def permits(self, identity, permission, context=None):
        user = self.user_map.get(identity)
        return user is not None and permission in user.permissions


# Authentication helper
async def check_credentials(user_map, username, password):
    user = user_map.get(username)
    return user is not None and user.password == password
```

## Database-Backed Authorization

Production-ready authorization using SQLAlchemy with async support.

### Setup

```python
from sqlalchemy import Column, Integer, String, Boolean, Table
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# Database models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # Hashed!
    disabled = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    permissions = relationship("Permission", back_populates="user")


class Permission(Base):
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String, nullable=False)
    
    user = relationship("User", back_populates="permissions")


# Create permissions table (many-to-many if needed)
user_permissions = Table(
    'user_permissions', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('permission_name', String)
)
```

### Authorization Policy Implementation

```python
import sqlalchemy as sa
from aiohttp_security.abc import AbstractAuthorizationPolicy


class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, db_session: async_sessionmaker[AsyncSession]):
        self.db_session = db_session
    
    async def authorized_userid(self, identity: str) -> Optional[str]:
        """Get user_id from username (identity)."""
        # Check if user exists and is not disabled
        stmt = sa.select(User.id).where(
            User.username == identity,
            ~User.disabled
        )
        
        async with self.db_session() as sess:
            user_id = await sess.scalar(stmt)
        
        return str(user_id) if user_id else None
    
    async def permits(self, identity: Optional[str], permission: str, 
                     context: Optional[dict] = None) -> bool:
        """Check if user has the permission."""
        if identity is None:
            return False
        
        # Load user with permissions
        stmt = sa.select(User).options(
            selectinload(User.permissions)
        ).where(
            User.username == identity,
            ~User.disabled
        )
        
        async with self.db_session() as sess:
            user = await sess.scalar(stmt)
        
        if user is None:
            return False
        
        # Superusers have all permissions
        if user.is_superuser:
            return True
        
        # Check if permission exists for user
        return any(p.name == permission for p in user.permissions)


# Authentication helper with password verification
from passlib.hash import sha256_crypt


async def check_credentials(db_session, username: str, password: str) -> bool:
    stmt = sa.select(User.password).where(
        User.username == username,
        ~User.disabled
    )
    
    async with db_session() as sess:
        hashed_password = await sess.scalar(stmt)
    
    if hashed_password is None:
        # Fail securely - always verify even if user doesn't exist
        return sha256_crypt.verify(password, "$5$rounds=535000$fakehash")
    
    return sha256_crypt.verify(password, hashed_password)
```

### Complete Database Example

```python
from aiohttp import web
from aiohttp_session import setup as setup_session, EncryptedCookieStorage
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from cryptography.fernet import Fernet
import base64


async def init_app():
    app = web.Application()
    
    # Setup database
    engine = create_async_engine("sqlite+aiosqlite:///./app.db")
    app["db_session"] = async_sessionmaker(engine, expire_on_commit=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Setup sessions (encrypted cookies)
    fernet_key = Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup_session(app, EncryptedCookieStorage(secret_key))
    
    # Setup security
    from aiohttp_security import SessionIdentityPolicy, setup
    
    setup(app, SessionIdentityPolicy(), DBAuthorizationPolicy(app["db_session"]))
    
    # Add routes
    app.router.add_post('/login', login_handler)
    app.router.add_get('/dashboard', dashboard_handler)
    
    return app


async def login_handler(request):
    post_data = await request.post()
    username = post_data.get('username')
    password = post_data.get('password')
    
    if await check_credentials(app["db_session"], username, password):
        # Use username as identity (or generate UUID)
        response = web.HTTPFound('/dashboard')
        await remember(request, response, username)
        raise response
    
    return web.Response(text="Invalid credentials", status=401)


async def dashboard_handler(request):
    await check_permission(request, 'dashboard')
    user_id = await authorized_userid(request)
    return web.Response(text=f"Welcome, user {user_id}!")
```

## Role-Based Access Control (RBAC)

Implement role-based permissions for scalable authorization.

### RBAC Policy Implementation

```python
from aiohttp_security.abc import AbstractAuthorizationPolicy


class RBACPolicy(AbstractAuthorizationPolicy):
    def __init__(self, user_roles, role_permissions):
        """
        Args:
            user_roles: Dict mapping identity to role name
            role_permissions: Dict mapping role to list of permissions
        """
        self.user_roles = user_roles
        self.role_permissions = role_permissions
    
    async def authorized_userid(self, identity):
        return identity if identity in self.user_roles else None
    
    async def permits(self, identity, permission, context=None):
        if identity is None:
            return False
        
        role = self.user_roles.get(identity)
        if not role:
            return False
        
        # Check if role has permission
        return permission in self.role_permissions.get(role, [])


# Usage
user_roles = {
    "alice_identity": "admin",
    "bob_identity": "editor",
    "charlie_identity": "viewer"
}

role_permissions = {
    "admin": ["read", "write", "delete", "manage_users", "settings"],
    "editor": ["read", "write"],
    "viewer": ["read"]
}

policy = RBACPolicy(user_roles, role_permissions)
```

### Database-Backed RBAC

```python
from sqlalchemy import Column, Integer, String, Table, ForeignKey

# Role model
class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


# User-role mapping
class UserRole(Base):
    __tablename__ = 'user_roles'
    
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    
    user = relationship("User")
    role = relationship("Role")


# Permission-role mapping
class RolePermission(Base):
    __tablename__ = 'role_permissions'
    
    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    permission_name = Column(String, primary_key=True)
    
    role = relationship("Role")


class RBACPolicy(AbstractAuthorizationPolicy):
    def __init__(self, db_session):
        self.db_session = db_session
    
    async def authorized_userid(self, identity):
        stmt = sa.select(User.id).where(User.username == identity)
        async with self.db_session() as sess:
            user_id = await sess.scalar(stmt)
        return str(user_id) if user_id else None
    
    async def permits(self, identity, permission, context=None):
        if identity is None:
            return False
        
        # Get all permissions for user's roles
        stmt = sa.select(RolePermission.permission_name).join(
            UserRole, UserRole.role_id == RolePermission.role_id
        ).join(
            User, User.id == UserRole.user_id
        ).where(
            User.username == identity
        )
        
        async with self.db_session() as sess:
            user_permissions = await sess.scalars(stmt)
            permissions_list = list(user_permissions)
        
        return permission in permissions_list
```

## Resource-Based Access Control

Check permissions based on resource ownership or attributes.

```python
class ResourcePolicy(AbstractAuthorizationPolicy):
    def __init__(self, db_session):
        self.db_session = db_session
    
    async def authorized_userid(self, identity):
        stmt = sa.select(User.id).where(User.username == identity)
        async with self.db_session() as sess:
            user_id = await sess.scalar(stmt)
        return str(user_id) if user_id else None
    
    async def permits(self, identity, permission, context=None):
        if identity is None:
            return False
        
        # Get user ID
        user_id = await self.authorized_userid(identity)
        
        # Resource-specific permissions
        if context and 'resource_id' in context:
            resource_id = context['resource_id']
            
            # Check if user owns the resource
            if permission in ['edit', 'delete']:
                stmt = sa.select(Resource).where(
                    Resource.id == resource_id,
                    Resource.owner_id == user_id
                )
                async with self.db_session() as sess:
                    resource = await sess.scalar(stmt)
                
                if resource:
                    return True
            
            # Check if user has global permission
            return await self.has_global_permission(identity, permission)
        
        # Global permission check
        return await self.has_global_permission(identity, permission)
    
    async def has_global_permission(self, identity, permission):
        """Check if user has global (non-resource-specific) permission."""
        stmt = sa.select(Permission.name).join(
            User, User.id == Permission.user_id
        ).where(
            User.username == identity,
            Permission.name == permission
        )
        
        async with self.db_session() as sess:
            result = await sess.scalar(stmt)
        
        return result is not None


# Usage
async def edit_resource_handler(request):
    resource_id = int(request.match_info['id'])
    
    # Check if user can edit this specific resource
    await check_permission(
        request, 
        'edit',
        context={'resource_id': resource_id}
    )
    
    # User can edit - either owns it or has global edit permission
    return web.json_response({"status": "can_edit"})
```

## Enum-Based Permissions

Use Python enums for type-safe permissions:

```python
from enum import Enum


class Permission(Enum):
    READ = 'read'
    WRITE = 'write'
    DELETE = 'delete'
    ADMIN = 'admin'


class EnumAuthPolicy(AbstractAuthorizationPolicy):
    def __init__(self):
        self.user_permissions = {
            "alice": {Permission.READ, Permission.WRITE, Permission.DELETE},
            "bob": {Permission.READ}
        }
    
    async def authorized_userid(self, identity):
        return identity if identity in self.user_permissions else None
    
    async def permits(self, identity, permission, context=None):
        # Works with both Enum and string permissions
        if isinstance(permission, str):
            try:
                permission = Permission(permission)
            except ValueError:
                return False
        
        user_perms = self.user_permissions.get(identity, set())
        return permission in user_perms


# Usage
await check_permission(request, Permission.WRITE)  # Type-safe!
await check_permission(request, 'write')  # Also works with strings
```

## Context-Based Permissions

Use context for fine-grained access control:

```python
class ContextPolicy(AbstractAuthorizationPolicy):
    async def permits(self, identity, permission, context=None):
        if identity is None:
            return False
        
        user = await self.get_user(identity)
        
        # Time-based permissions
        if permission == 'after_hours_access':
            if context and 'hour' in context:
                hour = context['hour']
                return 9 <= hour <= 17  # Business hours only
        
        # Location-based permissions
        if permission == 'admin_panel':
            if context and 'ip_address' in context:
                ip = context['ip_address']
                return ip in user.allowed_admin_ips
        
        # Data sensitivity permissions
        if permission == 'view_sensitive':
            if context and 'sensitivity_level' in context:
                level = context['sensitivity_level']
                return user.clearance_level >= level
        
        # Default permission check
        return permission in user.permissions
```
