# Standard Libraries

## Contents
- Core Builtins
- I/O and File Operations
- Networking
- System Information
- Data Processing
- Databases
- Other Modules
- Type Notation Conventions

## Core Builtins

Builtins are accessed with `$` prefix: `$print`, `$typeof`, etc. They are compiler-level constructors and optimized function calls.

### Printing and I/O
- `$print(...)` — print variable arguments to VM output
- `$println(...)` — same with newline

### Type operations
- `$typeof(v)` — return type constant ($tnull=0, $tint=1, $tfloat=2, $tbool=3, $tstring=4, $tobject=5, $tarray=6, $tfunction=7, $tabstract=8)
- `$pcompare(a, b)` — physical (address-based) comparison, faster for integers
- `$compare(a, b)` — semantic comparison per type rules

### Boolean
- `$istrue(v)` — convert to boolean (null/false/0 = false, everything else = true)
- `$not(v)` — inverse of $istrue

### Numeric
- `$int(v)` — string/float to integer
- `$float(v)` — string/int to float
- `$string(v)` — any value to string (calls %%__string%% on objects)
- `$idiv(a, b)` — integer division (raises exception on divide-by-zero)
- `$isinfinite(v)` — test for infinity
- `$isnan(v)` — test for NaN

### Optimized integer ops (skip type checks)
- `$iadd(a, b)`, `$isub(a, b)`, `$imult(a, b)`, `$idiv(a, b)`

### Arrays
- `$array(v1, v2, ...)` — create with values
- `$amake(size)` — create empty
- `$asize(a)` — length
- `$acopy(a)` — deep copy
- `$asub(a, pos, len)` — subarray
- `$ablit(dst, dpos, src, spos, len)` — blit between arrays

### Strings
- `$smake(size)` — allocate
- `$ssize(s)` — length
- `$scopy(s)` — copy
- `$ssub(s, pos, len)` — substring
- `$sget(s, pos)` / `$sset(s, pos, byte)` — byte access
- `$sblit(dst, dpos, src, spos, len)` — blit
- `$sfind(s, start, needle)` — find position

### Objects
- `$new(null|obj)` — create/copy object
- `$hash("field")` — get field hash
- `$field(hash)` — reverse hash to string
- `$objget(o, hash)` / `$objset(o, hash, val)` — runtime field access
- `$objfield(o, hash)` — existence check
- `$objremove(o, hash)` — remove field
- `$objfields(o)` — array of all field identifiers
- `$objgetproto(o)` / `$objsetproto(o, p)` — prototype chain
- `$objcall(o, hash, args_array)` — call method with context

### Functions
- `$nargs(f)` — argument count (-1 = variable)
- `$call(f, context, args)` — call with array of args
- `$closure(f, null, arg1, ...)` — partial application / fix `this`
- `$apply(f, arg1)(arg2)` — delayed call

### Exceptions
- `$throw(v)` — raise exception
- `$rethrow(v)` — re-raise with combined stacks
- `$excstack()` — current exception stack
- `$callstack()` — current call stack

### Hashtables
- `$hnew(size)`, `$hadd(h,k,v)`, `$hset(h,k,v,cmp)`, `$hmem(h,k,cmp)`
- `$hget(h,k,cmp)`, `$hremove(h,k,cmp)`, `$hresize(h,size)`
- `$hsize(h)`, `$hcount(h)`, `$hiter(h,f)`

## I/O and File Operations

**File module** (`file.ndll`): File I/O with abstract `'file` type.

- `file_open(path, mode)` — open file, returns `'file` or null
- `file_read(f)` — read entire file to string
- `file_write(f, s)` — write string to file
- `file_close(f)` — close file
- `file_exists(path)` — existence check
- `file_delete(path)` — delete file
- `file_bytes_read(f, size)` / `file_bytes_write(f, s)` — binary I/O
- Directory operations: `dir_open`, `dir_read`, `dir_close`

**Buffer module** (`buffer.ndll`): In-memory byte buffer for streaming I/O.

- `buffer_new(size)` — create buffer
- `buffer_add(b, s)` — append string
- `buffer_get_bytes(b, pos, size)` — extract bytes
- `buffer_to_string(b)` — convert to string

## Networking

**Socket module** (`socket.ndll`): TCP socket operations with abstract `'socket` type.

- `socket_new()` — create socket
- `socket_connect(s, host, port)` — connect to remote
- `socket_bind(s, port)` — bind to local port
- `socket_listen(s, backlog)` — start listening
- `socket_accept(s)` — accept incoming connection
- `socket_send_bytes(s, data)` / `socket_receive_bytes(s, max_size)` — binary I/O
- `socket_close(s)` — close socket
- `socket_set_broadcast(s, enabled)` — enable broadcast

## System Information

**System module** (`sys.ndll`): OS-level information and operations.

- `sys_get_cwd()` — current working directory
- `sys_set_cwd(path)` — change directory
- `sys_command(cmd)` — execute shell command, return output
- `sys_time()` — current timestamp
- `sys_get_env(name)` — environment variable
- `sys_put_env(name, value)` — set environment variable (pass null to unset)
- `sys_cpu_arch()` — CPU architecture string
- `sys_is64()` — true if 64-bit platform

**Process module** (`process.ndll`): Subprocess management.

- `process_execute(cmd, args)` — spawn process
- `process_stdin(p)` / `process_stdout(p)` / `process_stderr(p)` — get stream handles
- `process_close_input(p)` / `process_close_output(p)` — close streams
- `process_wait(p)` — wait for completion, returns exit code

## Data Processing

**Math module** (`math.ndll`): Mathematical functions (sin, cos, tan, sqrt, pow, log, exp, abs, round, floor, ceil, PI, E).

**Random module** (`random.ndll`): Pseudo-random number generation.

- `random_seed(s)` — set seed
- `random_int(min, max)` — random integer in range
- `random()` — random float 0-1

**MD5 module** (`md5.ndll`): MD5 hashing.

- `md5_new()` — create hasher
- `md5_update(h, data)` — feed data
- `md5_output(h)` — get hex digest string
- `md5(data)` — one-shot hash

**Serialize module** (`serialize.ndll`): Binary serialization of Neko values.

- `serialize(value)` — serialize to string
- `deserialize(s)` — deserialize from string

**String module** (`string.ndll`): String manipulation utilities (split, join, trim, replace, case conversion).

**UTF8 module** (`utf8.ndll`): UTF-8 encoding/decoding for Neko byte strings.

- `utf8_encode(str)` — encode to UTF-8 bytes
- `utf8_decode(bytes)` — decode UTF-8 to string
- `utf8_strlen(s)` — character count (not byte count)
- `utf8_substring(s, start, len)` — character-based substring

**Xml module** (`xml.ndll`): XML parsing and manipulation.

- `xml_parse(str)` — parse XML string
- `xml_parse_file(path)` — parse XML file
- `xml_string(xml)` — serialize to string
- Access: `xml_name`, `xml_kind`, `xml_cdata`, `xml_attributes`, `xml_children`

**Regexp module** (`regexp.ndll`): PCRE2-based regular expressions with abstract `'regexp` type.

- `regexp_match(pattern, str)` — match and return captures array
- `regexp_split(pattern, str)` — split by pattern
- `regexp_replace(pattern, replacement, str)` — replace matches
- `regexp_matched_num()` — count of matched groups

**ZLib module** (`zlib.ndll`): Compression/decompression.

- `zlib_compress(data)` — compress
- `zlib_decompress(data)` — decompress

## Databases

**Sqlite module** (`sqlite.ndll`): SQLite database access with abstract `'db` and `'query` types.

- `sqlite_open(path)` — open/create database
- `sqlite_query(db, sql)` — execute query
- `sqlite_next_row(query)` — advance to next row
- `sqlite_fields(query)` — field names array
- `sqlite_field(query, index)` — get field value
- `sqlite_close(db)` — close database

**Mysql module** (`mysql.ndll`): MySQL/MariaDB connector with abstract `'conn` and `'result` types.

- `mysql_connect(host, user, pass, db)` — connect
- `mysql_query(conn, sql)` — execute query
- `mysql_next_row(result)` — advance row
- `mysql_fields(result)` — field names
- `mysql_field(result, index)` — get value
- `mysql_close(conn)` — disconnect

## Other Modules

**Date module** (`date.ndll`): Date/time operations.

- `date_now()` — current timestamp
- `date_format(ts, format)` — format timestamp
- `date_get_year/month/day/hour/minute/second(ts)` — extract components
- `date_get_tz(ts)` — timezone offset in minutes
- UTC variants: `date_utc_format`, `date_get_utc_day`, `date_get_utc_hours`

**Int32 module** (`int32.ndll`): Full 32-bit integer operations (add, sub, mult, div, bitwise ops).

**Memory module** (`memory.ndll`): Low-level memory operations.

**Thread module** (`thread.ndll`): Neko-side threading API.

- `thread_create(f)` — spawn thread
- `thread_yield()` — yield to other threads
- `thread_sleep(seconds)` — sleep
- `thread_mutex_new()` / `thread_mutex_lock(m)` / `thread_mutex_unlock(m)` — mutex

**Ui module** (`ui.ndll`): GTK3-based UI (Linux only). Window, button, label, text field widgets.

**Module module** (`module.ndll`): Programmatic module loading utilities.

**Misc module** (`misc.ndll`): SHA1 hashing and miscellaneous utilities.

**CGI module** (`cgi.ndll` / `mod_neko`): Web request handling via Apache mod_neko or development web server emulator.

- `cgi_get_params()` — HTTP parameters as string
- `cgi_set_main(f)` — set request handler function (application mode)
- `cgi_header(name, value)` — set response header

## Type Notation Conventions

When documenting Neko libraries, use this type notation:

| Notation | Meaning |
|----------|---------|
| `null`, `int`, `float`, `bool`, `string`, `array`, `object`, `function` | Basic types |
| `any` | Any value accepted |
| `void` | No meaningful return value |
| `number` | Both int and float accepted (shortcut for `int\|float`) |
| `function:n` | Function accepting n parameters |
| `'name` | Abstract type (e.g., `'file`, `'socket`) |
| `int array` | Array of integers |
| `'file array array` | 2D array of abstract files |
| `{ x => int, y => int }` | Object with required fields |
| `int?` | int or null |
| `int\|float` | Either type accepted |
| `#name = ...` | Custom type alias |
