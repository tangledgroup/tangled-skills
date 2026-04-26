# Sessions Extension

## Overview

The Sessions extension records changes made to tables in an SQLite database, packages those changes into a "changeset" or "patchset" file, and later applies the same set of changes to another compatible database. Changesets can also be inverted to implement undo functionality.

Typical use case: Two users work on copies of the same database in parallel, then merge their changes at the end of the day by exchanging changesets.

Compile with `-DSQLITE_ENABLE_SESSION=1`.

## Concepts

### Changesets and Patchsets

- **Changeset** — A binary blob that records all INSERT, UPDATE, and DELETE operations performed during a session. Contains before-values and after-values for each changed row. Larger but more complete.
- **Patchset** — A more compact format that omits some data. Smaller on disk but requires the target database to have compatible starting data.

### Conflicts

When applying a changeset, conflicts occur if:
- An INSERT conflicts with an existing row (primary key collision)
- An UPDATE references a row that has been deleted
- An UPDATE references a row whose before-values have changed

Conflicts are reported to a conflict handler callback that decides how to resolve each one.

## Using the Session Extension

### Capturing a Changeset

```c
// 1. Create a session object attached to a database connection
sqlite3_session *session;
sqlite3_session_create(db, "main", &session);

// 2. Optionally track specific tables only
sqlite3_session_table_filter(session, myTableFilter, (void*)userData);

// 3. Make changes to the database using the normal SQL interface
sqlite3_exec(db, "UPDATE users SET name = 'Alice' WHERE id = 1", NULL, NULL, NULL);
sqlite3_exec(db, "INSERT INTO logs (msg) VALUES ('hello')", NULL, NULL, NULL);

// 4. Generate a changeset
char *changeset;
int changeset_size;
sqlite3_changeset_bytes(session, &changeset_size, &changeset);

// 5. Write the changeset to disk or transmit it
// ...

// 6. Clean up
free(changeset);
sqlite3_session_delete(session);
```

### Applying a Changeset

```c
// Read the changeset from disk
char *changeset = load_changeset_from_file("changes.dat", &changeset_size);

// Apply to target database
sqlite3_changeset_open(target_db, changeset_size, changeset, &iterator);

int rc;
do {
    int op;  // SQLITE_INSERT, SQLITE_UPDATE, or SQLITE_DELETE
    rc = sqlite3_changeset_next(iterator, &op, &table_name, &n_col, &a_col);

    if (rc == SQLITE_ROW) {
        // Process the change — it's automatically applied
        // Or use conflict handler for custom resolution
    }
} while (rc == SQLITE_ROW);

sqlite3_changeset_close(iterator);
```

### Conflict Handling

Register a conflict handler when opening the changeset:

```c
int conflictHandler(void *userData, int eConflict, sqlite3_changeset_iter *iter) {
    switch (eConflict) {
        case SQLITE_CHANGESET_DATA:
            // Row data has changed — choose to skip, abort, or apply anyway
            return SQLITE_CHANGESET_SKIP;

        case SQLITE_CHANGESET_NOTFOUND:
            // Row was deleted before the update
            return SQLITE_CHANGESET_ABORT;

        case SQLITE_CHANGESET_CONFLICT:
            // Primary key conflict on insert
            return SQLITE_CHANGESET_REPLACE;  // Replace existing row
    }
    return SQLITE_CHANGESET_OMIT;
}

sqlite3_changeset_apply(target_db, changeset_size, changeset,
                        conflictHandler, (void*)userData);
```

Resolution options:
- `SQLITE_CHANGESET_ABORT` — Stop applying the changeset
- `SQLITE_CHANGESET_OMIT` — Skip this change, continue with others
- `SQLITE_CHANGESET_REPLACE` — Replace the conflicting row
- `SQLITE_CHANGESET_SKIP` — Skip this change silently

### Inverting a Changeset (Undo)

```c
char *undo_changeset;
int undo_size;
sqlite3_invert_changeset(changeset, changeset_size,
                         &undo_size, &undo_changeset);

// Apply the inverted changeset to undo the original changes
sqlite3_changeset_apply(original_db, undo_size, undo_changeset,
                        conflictHandler, NULL);
```

### Merging Changesets

Combine multiple changesets into one:

```c
char *merged;
int merged_size;
sqlite3_changeset_concat(
    size1, changeset1,
    size2, changeset2,
    &merged_size, &merged,
    conflictHandler, NULL
);
```

### Patchsets

Patchsets are generated and applied similarly but use different API functions:

```c
// Generate patchset (smaller than changeset)
char *patchset;
int patchset_size;
sqlite3_patchset_bytes(session, &patchset_size, &patchset);

// Apply patchset
sqlite3_patchset_apply(target_db, patchset_size, patchset,
                       conflictHandler, NULL);
```

### Inspecting Changesets

Iterate through a changeset to examine its contents:

```c
sqlite3_changeset_iter *iter;
sqlite3_changeset_open(db, changeset_size, changeset, &iter);

int op, n_col;
const char *table;
while (sqlite3_changeset_next(iter, &op, &table, &n_col) == SQLITE_ROW) {
    for (int i = 0; i < n_col; i++) {
        int indicator;  // SQLITE_CHANGESET_OMIT, _INSERT, _DELETE, _UPDATE
        const unsigned char *value;
        int value_size;
        sqlite3_changeset_old(iter, i, &value, &value_size, &indicator);
    }
}
sqlite3_changeset_close(iter);
```

## Limitations

- The Sessions extension requires compile-time enabling (`-DSQLITE_ENABLE_SESSION`)
- Changesets are only valid for databases with compatible schemas
- WITHOUT ROWID tables have limited session support
- Virtual table changes may not be captured depending on the implementation
- The target database must have the same schema as the source when the session was active
