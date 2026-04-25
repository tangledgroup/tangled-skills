# Troubleshooting

### Common Issues

**"Module not found" errors on Linux:**
- Install platform-specific dependencies (see Installation section)
- Try alternative GUI backends: `pip install pywebview[gtk]` or `pywebview[qt]`

**WebView2 Runtime missing on Windows:**
- Download from: https://developer.microsoft.com/en-us/microsoft-edge/webview2/
- Or use CEF backend: `pip install pywebview[cef]`

**HTTPS errors with local server:**
- Install SSL support: `pip install pywebview[ssl]`
- Or use HTTP for development

**JavaScript exceptions not caught:**
- Wrap `evaluate_js()` calls in try/except blocks
- Catch `webview.errors.JavascriptException`

**Window appears blank:**
- Check console for JavaScript errors
- Verify file paths are correct (relative to application entry point)
- Try loading a remote URL first to confirm pywebview works

See [Debugging Guide](reference/05-debugging.md) for detailed troubleshooting.
