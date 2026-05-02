# Tools and Web

## Contents
- neko Command
- nekoc Compiler
- nekotools Utilities
- nekoml Compiler
- mod_neko Apache Module
- Development Web Server

## neko Command

Run compiled Neko bytecode files:

```bash
neko program           # extension optional for .n files
neko -version          # display version
```

Bytecode files are searched in the current directory and `NEKOPATH` paths.

## nekoc Compiler

Primary tool for compiling `.neko` source to `.n` bytecode. Output file replaces extension with `.n`.

### Compile

```bash
nekoc hello.neko       # produces hello.n
nekoc -v hello.neko    # verbose mode
nekoc -o output/ hello.neko  # set output directory
```

### Link multiple modules

Join several bytecode files into one:

```bash
nekoc -link combined.n module1.n module2.n module3.n
```

Useful before creating standalone executables with `nekotools boot`.

### Console REPL

Interactive read-execute-print loop. Type code and press `!` to execute:

```bash
nekoc -console
```

### Dump bytecode

Disassemble compiled bytecode for inspection:

```bash
nekoc -d program.n     # produces program.dump
```

### Strip debug info

Remove debug information and global names (in-place):

```bash
nekoc -z program.n
```

### Prettify source

Reformat Neko source code:

```bash
nekoc -p source.neko   # produces source.prettified.neko
```

### Generate documentation

Produce HTML documentation from comments in Neko source:

```bash
nekoc -doc source.neko
```

## nekotools Utilities

### Web server

Development web server that serves `.n` files as CGI scripts. Mimics `mod_neko` API for local development:

```bash
nekotools server
```

Options:
- `-h [domain]` — set hostname (default localhost)
- `-p [port]` — set port (default 2000)
- `-d [directory]` — set base directory
- `-log [file]` — set log file
- `-rewrite` — enable pseudo mod_rewrite for smart URLs

URLs map to `.n` files: `http://localhost:2000/test/` executes `test.n`. Configuration page at `/server:config`.

### Standalone executable

Embed bytecode into a standalone binary:

```bash
nekotools boot program.n    # produces executable named "program"
nekotools boot -c *.n       # generate C file containing the bytecode
```

The resulting executable still needs `libneko.so`/`neko.dll` unless statically linked. The `-c` flag outputs a `.c` file instead of a compiled binary, useful for custom build integration.

## nekoml Compiler

Compile NekoML files (an alternative Neko language variant):

```bash
nekoml source.nekoml    # produces source.n
```

Requires `nekoml.std` (NekoML standard library) in the Neko installation directory.

## mod_neko Apache Module

Embed NekoVM into Apache for server-side Neko execution. `.n` files are executed as CGI scripts.

### Apache 2.x Configuration

Add to Apache configuration:

```apache
# mods-available/neko.load
LoadModule neko_module /usr/local/lib/neko/mod_neko2.ndll

# mods-available/neko.conf
AddHandler neko-handler .n
```

Add `index.n` to `DirectoryIndex` in `dir.conf`. Set `NEKOPATH` in Apache environment:

```bash
echo 'export NEKOPATH=/usr/local/lib/neko' >> /etc/apache2/envvars
```

Enable and restart:

```bash
sudo a2enmod neko
sudo systemctl restart apache2
```

### Neko CGI API

Access HTTP parameters from within Neko:

```neko
get_params = $loader.loadprim("mod_neko@get_params", 0);
// For Apache 2.x, use "mod_neko2@get_params"
$print("PARAMS = " + get_params());
```

HTTP parameters are passed as `?p1=v1;p2=v2` in the URL.

### Application Mode

By default, mod_neko loads and executes the module on every request. For persistent state, use application mode with `cgi_set_main`:

```neko
$print("Initializing...");  // Runs once at module load time

// Entry point called for each request
entry = function() {
    $print("Main...\n");
}

// Register the entry point
set_main = $loader.loadprim("mod_neko@cgi_set_main", 1);
set_main(entry);

// Handle first request immediately
entry();
```

Recompiling changes the `.n` file timestamp, triggering a reload and re-initialization. This enables hot-reloading during development.

### Development Alternative

If Apache is not available, use `nekotools server` as a mod_neko emulator — it provides the same CGI API for local development:

```bash
nekotools server -d /path/to/website
```

Then browse to `http://localhost:2000/`.
