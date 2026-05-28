# ☑ Plan: htmx 2.0.10 Skill Generation

**Depends On:** NONE

**Created:** 2026-05-28T00:00:00Z

**Updated:** 2026-05-28T00:00:00Z

**Current Phase:** ☑ Phase 8

**Current Task:** ☑ Task 8.4

## ☑ Phase 1 Content Collection

- ☑ Task 1.1 Fetch remaining community extension docs (loading-states, class-tools, multi-swap, path-deps, path-params, client-side-templates, json-enc, alpine-morph, debug, event-header, remove-me, morphdom-swap, ajax-header, no-cache, restorted, safe-nonce, dynamic-url, optimistic, form-json, signalr, attribute-tools)
- ☑ Task 1.2 Fetch key example pages for detailed patterns (active-search, file-upload, animations, sortable, modal-custom, tabs-hateoas, inline-validation, infinite-scroll, progress-bar, web-components, keyboard-shortcuts, confirm, async-auth)
- ☑ Task 1.3 Fetch quirks page and migration guide details
- ☑ Task 1.4 Organize all collected source material by domain

## ☑ Phase 2 Structure Design

- ☑ Task 2.1 Define reference file breakdown (depends on: Task 1.4)
  - Core: AJAX requests, swapping/settling, attributes reference, events/API, config
  - Extensions: Each core extension gets its own section within extensions ref; community extensions grouped by category
  - Integrations: Third-party library patterns (Alpine.js, jQuery, hyperscript, SortableJS, Web Components, etc.)
  - Patterns: Common UX patterns with full examples
  - Advanced: History, boosting, security, validation, caching, 1.x migration
- ☑ Task 2.2 Draft SKILL.md outline with YAML header, sections, and reference links (depends on: Task 2.1)

## ☑ Phase 3 Write Core Reference Files

- ☑ Task 3.1 Write `reference/01-ajax-requests.md` — core AJAX attributes (hx-get, hx-post, etc.), triggers (modifiers, filters, special events, polling, load polling), targets (extended CSS selectors), parameters (hx-include, hx-params, hx-vals, hx-vars, file upload, extra values), request indicators, synchronization (hx-sync)
- ☑ Task 3.2 Write `reference/02-swapping-and-settling.md` — swap styles (innerHTML, outerHTML, beforebegin, etc., delete, none), morph swaps overview, view transitions API, swap options/modifiers (transition, swap delay, settle delay, ignoreTitle, scroll, show), CSS transitions (swap & settle model), out of band swaps (hx-swap-oob, template for table rows), selecting content (hx-select, hx-select-oob), preserving content (hx-preserve)
- ☑ Task 3.3 Write `reference/03-attributes-reference.md` — complete attribute catalog: core 10 attributes + all additional attributes (hx-boost, hx-confirm, hx-delete, hx-disable, hx-disabled-elt, hx-disinherit, hx-encoding, hx-ext, hx-headers, hx-history, hx-history-elt, hx-include, hx-indicator, hx-inherit, hx-params, hx-patch, hx-preserve, hx-prompt, hx-put, hx-replace-url, hx-request, hx-sync, hx-validate, hx-vars), with descriptions and usage examples
- ☑ Task 3.4 Write `reference/04-events-and-api.md` — full event reference (all 40+ events grouped by lifecycle: request, swap, settle, history, validation, SSE, error), JavaScript API (htmx.on, htmx.off, htmx.onLoad, htmx.find, htmx.findAll, htmx.closest, htmx.trigger, htmx.ajax, htmx.swap, htmx.process, htmx.values, htmx.logAll, htmx.logger, DOM manipulation helpers), scripting patterns (hx-on* attributes, inline scripting, 3rd party integration via events)
- ☑ Task 3.5 Write `reference/05-configuration.md` — all config variables (historyEnabled, historyCacheSize, refreshOnHistoryMiss, defaultSwapStyle, allowEval, allowScriptTags, selfRequestsOnly, responseHandling, etc.), meta tag configuration, response handling configuration with examples

## ☑ Phase 4 Write Extensions Reference Files

- ☑ Task 4.1 Write `reference/06-core-extensions-sse-ws.md` — SSE extension (sse-connect, sse-swap, trigger callbacks, named/unnamed events, reconnection, events) and WebSocket extension (ws-connect, ws-send, OOB swap in messages, JSON serialization with HEADERS, reconnection with full-jitter, message queue, socket wrapper API, all events)
- ☑ Task 4.2 Write `reference/07-core-extensions-head-idiomorph.md` — head-support extension (merge algorithm for boosted vs non-boosted, title/link/style/script merging) and idiomorph extension (morph/morph:outerHTML/morph:innerHTML swap strategies, morph options, configuration)
- ☑ Task 4.3 Write `reference/08-core-extensions-preload-response-targets.md` — preload extension (preload attribute, trigger events, cache behavior, configuration) and response-targets extension (hx-target-[CODE], hx-target-error, wildcard codes, CSS selector targets, HX-Retarget interaction)
- ☑ Task 4.4 Write `reference/09-core-extensions-1-compat.md` — htmx-1-compat extension (obsolete attributes restored: hx-ws, hx-sse, hx-on, default changes reverted, what it does not cover)
- ☑ Task 4.5 Write `reference/10-community-extensions-ui.md` — loading-states (hx-loading, hx-disabling-external-elt, classes, configuration), class-tools (classes attribute, adding/removing classes), attribute-tools, multi-swap (multiple elements with per-element swap methods), remove-me (timed element removal), morphdom-swap, alpine-morph
- ☑ Task 4.6 Write `reference/11-community-extensions-data.md` — client-side-templates (mustache, nunjucks, handlebars support, JSON/XML to HTML), json-enc (JSON body encoding), form-json (type preservation, nested structures), json-enc-custom, htmx-json
- ☑ Task 4.7 Write `reference/12-community-extensions-utility.md` — path-deps (inter-element dependencies by path), path-params (path variable population), event-header (Triggering-Event header), ajax-header (X-Requested-With), debug (console logging per element), no-cache, restored (back button events with hx-boost), safe-nonce (CSP nonce for inline scripts), dynamic-url (path templating), optimistic (optimistic UI updates), disable-element (legacy)
- ☑ Task 4.8 Write `reference/13-community-extensions-integrations.md` — signalr (.NET SignalR integration), amz-content-sha256 (AWS content hash), hx-drag (drag-drop requests), replace-params (parameter replacement)
- ☑ Task 4.9 Write `reference/14-building-extensions.md` — extension API (htmx.defineExtension, init, getSelectors, onEvent, transformResponse, isInlineSwap, handleSwap, encodeParameters), extension lifecycle, best practices, publishing

## ☑ Phase 5 Write Patterns and Integrations Reference Files

- ☑ Task 5.1 Write `reference/15-ux-patterns.md` — detailed patterns with full HTML examples: active search, click-to-edit, bulk update, click-to-load, delete row, edit row, lazy loading, inline validation, infinite scroll, progress bar, value select (dependent dropdowns), file upload with progress, preserving file inputs after errors, reset user input, dialogs (browser confirm/prompt, UIKit modal, Bootstrap modal, custom modal), tabs (HATEOAS and JavaScript), keyboard shortcuts, drag-drop/sortable, updating other content (OOB), custom confirm, async authentication, web components integration
- ☑ Task 5.2 Write `reference/16-third-party-integrations.md` — Alpine.js (reactive patterns, x-if with htmx.process, event interoperability), jQuery (event handling, DOM manipulation), hyperscript (pairing with htmx, event-driven scripting), VanillaJS (htmx.onLoad, event listeners), SortableJS (drag-drop with hidden inputs, initialization via htmx.onLoad), Web Components (shadow DOM, custom elements, htmx.process after template rendering), SweetAlert2 (custom confirm dialogs), Tom Select (history cleanup with htmx:beforeHistorySave)

## ☑ Phase 6 Write Advanced Topics Reference Files

- ☑ Task 6.1 Write `reference/17-history-and-boosting.md` — hx-push-url (history snapshots, back button restoration, cache miss handling), hx-replace-url, hx-history-elt (custom snapshot element), hx-history (disabling history cache), hx-boost (progressive enhancement, graceful degradation), 3rd party library cleanup for history (htmx:beforeHistorySave)
- ☑ Task 6.2 Write `reference/18-security-and-validation.md` — validation (HTML5 Validation API integration, hx-validate, reportValidityOfForms, htmx:validation events, custom validation with hx-on), security (escaping user content, hx-disable, hx-history false, CSP options, selfRequestsOnly, allowScriptTags, allowEval, htmx:validateUrl event, CSRF prevention with hx-headers), inheritance (hx-disinherit, hx-inherit, disableInheritance config)
- ☑ Task 6.3 Write `reference/19-caching-and-performance.md` — HTTP caching (Last-Modified, If-Modified-Since, ETag, Vary header with HX-Request), getCacheBusterParam, preload extension for perceived performance, triggerSpecsCache
- ☑ Task 6.4 Write `reference/20-migration-and-quirks.md` — 1.x to 2.x migration guide (breaking changes, new defaults, removed attributes, htmx-1-compat extension), intercooler.js migration, Hotwire/Turbo migration patterns, quirks page (known edge cases and workarounds)

## ☑ Phase 7 Write SKILL.md

- ☑ Task 7.1 Write SKILL.md with YAML header, Overview, When to Use, Core Concepts, Quick Start example, Installation (CDN, npm, download), Usage Examples (basic AJAX, boosted navigation, form with validation), Advanced Topics navigation hub linking all 20 reference files organized by category (depends on: Task 6.4)

## ☑ Phase 8 Validate and Finalize

- ☑ Task 8.1 Run structural validator (`validate-skill.sh`) against the skill directory (depends on: Task 7.1)
- ☑ Task 8.2 Fix any validation errors or warnings
- ☑ Task 8.3 Perform LLM judgment checks: content accuracy, no hallucination, concise writing, consistent terminology, single recommended approach, all cross-references valid (depends on: Task 8.2)
- ☑ Task 8.4 Regenerate README.md skills table via `gen-skills-table.sh` (depends on: Task 8.3)
