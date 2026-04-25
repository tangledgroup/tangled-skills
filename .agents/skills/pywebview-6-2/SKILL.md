---
name: pywebview-6-2
description: A skill for building cross-platform desktop applications with native webview components using pywebview 6.2, enabling HTML/CSS/JavaScript UIs in Python applications with two-way Python-JavaScript communication, window management, and built-in HTTP server capabilities. Use when creating desktop GUI applications, wrapping web interfaces in native windows, or building hybrid applications that combine Python backend logic with modern web frontend technologies on Windows, macOS, Linux, and Android.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - python
  - desktop-gui
  - webview
  - cross-platform
  - native-apps
  - javascript-bridge
  - html-ui
category: development
external_references:
  - https://pywebview.flowrl.com/
  - https://github.com/r0x0r/pywebview
---
## Overview
A skill for building cross-platform desktop applications with native webview components using pywebview 6.2, enabling HTML/CSS/JavaScript UIs in Python applications with two-way Python-JavaScript communication, window management, and built-in HTTP server capabilities. Use when creating desktop GUI applications, wrapping web interfaces in native windows, or building hybrid applications that combine Python backend logic with modern web frontend technologies on Windows, macOS, Linux, and Android.

pywebview is a lightweight BSD-licensed cross-platform wrapper around native webview components that allows displaying HTML content in native GUI windows. It provides the power of web technologies (HTML, CSS, JavaScript) in desktop applications while hiding the browser-based nature of the GUI. pywebview ships with a built-in HTTP server, DOM support in Python, and comprehensive window management functionality.

**Key capabilities:**
- Cross-platform support (Windows, macOS, Linux, Android)
- Two-way JavaScript ↔ Python communication without HTTP/REST
- Built-in HTTP server for serving static files
- Window management (size, position, title, multiple windows)
- Native GUI components (menus, dialogs, message boxes)
- DOM manipulation from Python
- Drag-and-drop file support
- Bundler-friendly (PyInstaller, Nuitka, py2app)

## When to Use
- Building desktop applications with web-based UIs
- Creating native wrappers for existing web applications
- Developing hybrid apps with Python backend and JavaScript frontend
- Needing cross-platform GUI without learning platform-specific toolkits
- Requiring two-way communication between Python and JavaScript
- Building simple browsers or kiosk applications
- Creating tools that benefit from modern CSS frameworks (React, Vue, etc.)

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.

## Advanced Topics
## Advanced Topics

- [Installation](reference/01-installation.md)
- [Js Api](reference/02-js-api.md)
- [Window Api](reference/03-window-api.md)
- [Native Components](reference/04-native-components.md)
- [Debugging](reference/05-debugging.md)
- [Setup](reference/06-setup.md)
- [Quick Start](reference/07-quick-start.md)
- [Common Operations](reference/08-common-operations.md)
- [Application Architecture](reference/09-application-architecture.md)
- [Backend Logic Execution](reference/10-backend-logic-execution.md)
- [Troubleshooting](reference/11-troubleshooting.md)
- [Additional Resources](reference/12-additional-resources.md)
- [Security Considerations](reference/13-security-considerations.md)

## Usage Examples
See the official pywebview repository for complete examples:
- https://github.com/r0x0r/pywebview/tree/master/examples

Notable examples:
- **todos** - Serverless app with JS API
- **flask_app** - Flask integration
- **simple_browser** - Basic browser implementation
- **multiple_windows** - Window management demo
- **menu_demo** - Native menu system

