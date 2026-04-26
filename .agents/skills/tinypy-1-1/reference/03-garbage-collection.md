# Garbage Collection

## Overview

TinyPy uses an incremental mark-and-sweep garbage collector with a tri-color algorithm (white, grey, black). It was implemented to eliminate the libgc dependency and is integrated directly into the VM.

## Algorithm

### Color Sets

- **White** — Objects that have not been marked as reachable (candidates for collection)
- **Grey** — Reachable objects whose children have not yet been followed
- **Black** — Reachable objects whose children have all been followed

### Initialization

```c
void tp_gc_init(TP) {
    tp->white = _tp_list_new();
    tp->strings = _tp_dict_new();  /* interned string cache */
    tp->grey = _tp_list_new();
    tp->black = _tp_list_new();
    tp->steps = 0;
}
```

### Marking (tp_grey)

When a new object is created or assigned, `tp_grey` marks it as reachable:

```c
void tp_grey(TP, tp_obj v) {
    if (v.type < TP_STRING || (!v.gci.data) || *v.gci.data) { return; }
    *v.gci.data = 1;
    if (v.type == TP_STRING || v.type == TP_DATA) {
        _tp_list_appendx(tp, tp->black, v);  /* leaf nodes go straight to black */
        return;
    }
    _tp_list_appendx(tp, tp->grey, v);  /* containers go to grey for following */
}
```

Strings and data objects are leaf nodes (no children to follow) so they go directly to black. Lists, dicts, and functions go to grey.

### Following (tp_follow)

For grey objects, `tp_follow` marks all children as reachable:

```c
void tp_follow(TP, tp_obj v) {
    if (v.type == TP_LIST) {
        for (n = 0; n < v.list.val->len; n++)
            tp_grey(tp, v.list.val->items[n]);
    }
    if (v.type == TP_DICT) {
        for (i = 0; i < v.dict.val->len; i++) {
            int n = _tp_dict_next(tp, v.dict.val);
            tp_grey(tp, v.dict.val->items[n].key);
            tp_grey(tp, v.dict.val->items[n].val);
        }
    }
    if (v.type == TP_FNC) {
        tp_grey(tp, v.fnc.info->self);
        tp_grey(tp, v.fnc.info->globals);
    }
}
```

### Incremental Step (tp_gcinc)

Rather than collecting all at once, the GC does a few steps periodically:

```c
void tp_gcinc(TP) {
    tp->steps += 1;
    if (tp->steps < TP_GCMAX || tp->grey->len > 0) {
        _tp_gcinc(tp); _tp_gcinc(tp);  /* process 2 grey items */
    }
    if (tp->steps < TP_GCMAX || tp->grey->len > 0) { return; }
    tp->steps = 0;
    tp_full(tp);  /* full collection if limit reached */
}
```

`TP_GCMAX` is 4096 steps between full collections. Each step processes 2 grey items.

### Full Collection (tp_full)

1. Process all remaining grey items (follow their children)
2. Collect white objects (delete unreferenced ones)
3. Reset colors: black becomes white, white becomes empty

```c
void tp_full(TP) {
    while (tp->grey->len) { _tp_gcinc(tp); }
    tp_collect(tp);
    tp_follow(tp, tp->root);  /* re-mark root reachable objects */
}
```

### Collection (tp_collect)

Walks the white list and deletes any object not marked as reachable:

```c
void tp_collect(TP) {
    for (n = 0; n < tp->white->len; n++) {
        tp_obj r = tp->white->items[n];
        if (*r.gci.data) { continue; }  /* still reachable, skip */
        tp_delete(tp, r);  /* free the object */
    }
    tp->white->len = 0;
    tp_reset(tp);
}
```

### String Interning

Strings are interned in `tp->strings` dictionary via `tp_track`. When a string is tracked, if it already exists in the interning table, the duplicate is deleted and the existing reference is returned. This saves memory for repeated string literals.

## Important Notes

- Cyclic references are NOT handled by this GC — avoid creating cycles in your tinypy code
- The GC was originally implemented with a dict for white items but switched to lists for performance (dict hash lookups were too slow)
- The `gci` field in objects points to bookkeeping data used by the GC
- Numbers (TP_NUMBER) are not tracked — they are value types with no allocation
