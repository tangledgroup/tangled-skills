# Go API

esbuild provides two public Go packages: `github.com/evanw/esbuild/pkg/api` for the build/transform API, and `github.com/evanw/esbuild/pkg/cli` for CLI utilities.

## Build

```go
package main

import (
    "os"
    "github.com/evanw/esbuild/pkg/api"
)

func main() {
    result := api.Build(api.BuildOptions{
        EntryPoints: []string{"app.ts"},
        Bundle:      true,
        Outdir:      "dist",
    })
    if len(result.Errors) > 0 {
        os.Exit(1)
    }
}
```

## Transform

```go
package main

import (
    "fmt"
    "github.com/evanw/esbuild/pkg/api"
)

func main() {
    ts := "let x: number = 1"
    result := api.Transform(ts, api.TransformOptions{
        Loader: api.LoaderTS,
    })
    if len(result.Errors) == 0 {
        fmt.Printf("%s", result.Code)
    }
}
```

## Incremental Build Context

```go
ctx, err := api.Context(api.BuildOptions{
    EntryPoints: []string{"app.ts"},
    Bundle:      true,
    Outdir:      "dist",
})
if err != nil {
    os.Exit(1)
}

// Watch mode
err = ctx.Watch(api.WatchOptions{})

// Serve mode
server, err := ctx.Serve(api.ServeOptions{
    Servedir: "dist",
})

// Manual rebuild
for i := 0; i < 5; i++ {
    result := ctx.Rebuild()
}

// Cancel current build
ctx.Cancel()

// Clean up
ctx.Dispose()
```

## Go-specific option types

Some options use typed enums in Go rather than strings:

```go
api.PlatformBrowser    // default
api.PlatformNode       // for node

api.LoaderJS
api.LoaderTS
api.LoaderTSX
api.LoaderJSX
api.LoaderJSON
api.LoaderCSS
api.LoaderText
api.LoaderBinary
api.LoaderBase64
api.LoaderDataURL
api.LoaderEmpty
api.LoaderCopy

api.FormatIIFE
api.FormatCMS
api.FormatESM

api.JSXTransform    // default: React.createElement
api.JSXPreserve     // keep JSX syntax in output
api.JSXAautomatic   // automatic runtime (React 17+)

api.SourcemapInline
api.SourcemapLinked  // default

api.LogLevelDebug
api.LogLevelInfo
api.LogLevelWarn
api.LogLevelError
api.LogLevelSilent

api.PackagesExternal     // don't bundle node_modules
api.PackagesBundle       // bundle node_modules (default)

api.CharsetUTF8
api.CharsetASCII
```

## Engines (target browsers)

```go
Engines: []api.Engine{
    {api.EngineChrome, "58"},
    {api.EngineFirefox, "57"},
    {api.EngineSafari, "11"},
    {api.EngineEdge, "16"},
    {api.EngineNode, "18"},
}
```

## Loader map

```go
Loader: map[string]api.Loader{
    ".png": api.LoaderBinary,
    ".js":  api.LoaderJSX,
},
```

## Alias map

```go
Alias: map[string]string{
    "react": "preact/compat",
},
```

## External patterns

```go
External: []string{
    "^https?://",
    "^npm:",
},
```
