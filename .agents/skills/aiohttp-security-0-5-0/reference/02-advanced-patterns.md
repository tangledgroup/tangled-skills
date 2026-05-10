# Advanced Patterns

## Contents
- Database-Backed Authorization Policy
- Enum-Based Permissions
- Complete Application Setup
- Password Verification Pattern
- Identity Best Practices

## Database-Backed Authorization Policy

For real applications, authorization policies typically query a database. Pattern using SQLAlchemy async:

```python
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(sa.String(256), unique=True, index=True)
    password: Mapped[str] = mapped_column(sa.String(256))
    is_superuser: Mapped[bool] = mapped_column(default=False)
    permissions = relationship("Permission", cascade="all, delete")


class Permission(Base):
    __tablename__ = "permissions"
    user_id: Mapped[int] = mapped_column(
        sa.ForeignKey(User.id, ondelete="CASCADE"), primary_key=True
    )
    name: Mapped[str] = mapped_column(sa.String(64), primary_key=True)


class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, db_session: async_sessionmaker[AsyncSession]):
        self.dbsession = db_session

    async def authorized_userid(self, identity: str) -> str | None:
        async with self.dbsession() as sess:
            user_id = await sess.scalar(
                sa.select(User.id).where(User.username == identity)
            )
        return str(user_id) if user_id else None

    async def permits(self, identity: str | None, permission: str,
                      context: dict | None = None) -> bool:
        if identity is None:
            return False
        async with self.dbsession() as sess:
            user = await sess.scalar(
                sa.select(User)
                .options(selectinload(User.permissions))
                .where(User.username == identity)
            )
        if user is None:
            return False
        if user.is_superuser:
            return True
        return any(p.name == permission for p in user.permissions)
```

## Enum-Based Permissions

Permissions can be enums instead of plain strings, providing type safety:

```python
from enum import Enum

class Permissions(Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class MyAuthPolicy(AbstractAuthorizationPolicy):
    async def permits(self, identity, permission, context=None):
        allowed_permissions = await db.get_user_permissions(identity)
        return permission in allowed_permissions

# Usage:
await check_permission(request, Permissions.ADMIN)
```

## Complete Application Setup with Database

```python
async def init_app() -> web.Application:
    app = web.Application()

    # Database setup
    db_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    app["db_session"] = async_sessionmaker(db_engine, expire_on_commit=False)

    # Initialize database with tables and seed data
    await init_db(db_engine, app["db_session"])

    # Session middleware
    setup_session(app, SimpleCookieStorage())

    # Security policies
    setup_security(
        app,
        SessionIdentityPolicy(),
        DBAuthorizationPolicy(app["db_session"])
    )

    # Register routes
    handlers = WebHandlers()
    handlers.configure(app)

    return app
```

## Password Verification Pattern

Use `passlib` or `bcrypt` for credential verification:

```python
from passlib.hash import sha256_crypt

async def check_credentials(db_session, username: str, password: str) -> bool:
    async with db_session() as sess:
        hashed_pw = await sess.scalar(
            sa.select(User.password).where(User.username == username)
        )
    if hashed_pw is None:
        return False
    return sha256_crypt.verify(password, hashed_pw)
```

## Identity Best Practices

- Use random strings (UUIDs, hashes) as identity values — never expose database IDs or emails in cookies/sessions
- The identity string travels between browser and server; treat it as an opaque token
- Map identities to userids server-side through the authorization policy's `authorized_userid()` method
