#!/usr/bin/env bun
// _vega-lite.js — Vega-Lite spec validator using AJV + bundled JSON schema
//
// Imports: ajv, ajv-formats (resolved by bun at runtime)
// Schema:  vega-lite-schema.json (bundled in scripts/ for offline use)
// Usage:   vega-lite.sh validate [OPTIONS] <file|directory|->

import Ajv from "ajv";
import addFormats from "ajv-formats";
import { readFileSync } from "node:fs";
import { stat, readdir } from "node:fs/promises";
import { join, basename, dirname } from "node:path";
import { fileURLToPath } from "node:url";

// --- Schema config ---
const SCHEMA_VERSION = "6.4.3";
const SCRIPTS_DIR = dirname(fileURLToPath(import.meta.url));
const BUNDLED_SCHEMA = join(SCRIPTS_DIR, "vega-lite-schema.json");

// --- Color constants ---
const RED = "\x1b[31m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const CYAN = "\x1b[36m";
const RESET = "\x1b[0m";

// --- CLI helpers ---
function printUsage() {
    console.log(`
Usage: vega-lite.sh validate [OPTIONS] <file|directory|->

Validate Vega-Lite JSON specs against the official v${SCHEMA_VERSION} schema.
Schema is bundled offline — no network required.

Options:
  -q, --quiet   Only output errors (suppress valid file markers)
  --json        Output results as JSON
  --schema      Print schema version and path info, then exit
  -h, --help    Show this help message

Arguments:
  <file>       Single .json, .vl.json file, or .md/.markdown with code blocks
  <directory>  Recursively validate all matching files
  -            Read spec from stdin

Notes:
  - Files ending with _broken.vl.json are skipped (intentionally invalid)
  - Files ending with _future.vl.json skip schema validation (future features)
  - Markdown files: extracts \`\`\`vega-lite or \`\`\`json code blocks as specs
  - Compiled Vega specs (.vg.json) are skipped

Exit codes:
  0  All specs valid (or no specs found)
  1  One or more specs have schema errors
  2  Usage error`);
}

// --- Schema loading (bundled, offline) ---

function loadSchema() {
    try {
        const content = readFileSync(BUNDLED_SCHEMA, "utf-8");
        return JSON.parse(content);
    } catch (e) {
        throw new Error(
            `Failed to load bundled schema from ${BUNDLED_SCHEMA}:\n${e.message}\n` +
            `Ensure vega-lite-schema.json exists in the scripts directory.`
        );
    }
}

// --- AJV setup (matches official vega-lite test config) ---

function createValidator(schema) {
    const ajv = new Ajv({
        strict: false,
        allowUnionTypes: true,
    });
    addFormats(ajv);

    // Vega-Lite schema uses custom formats that AJV doesn't know about
    ajv.addFormat("color-hex", () => true);

    return ajv.compile(schema);
}

// --- Code block extraction from markdown ---

/**
 * Extract vega-lite / json code blocks from markdown content.
 * Returns array of { code: string, startLine: number }
 */
function extractVlBlocks(content) {
    const blocks = [];
    const lines = content.split("\n");

    let inBlock = false;
    let blockStart = 0;
    let blockLines = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();

        // Match ```vega-lite or ```json fenced code blocks
        if (/^```[^\S\r\n]*(vega-lite|json)$/i.test(line)) {
            inBlock = true;
            blockStart = i + 1;
            blockLines = [];
        } else if (inBlock && line === "```") {
            inBlock = false;
            const code = blockLines.join("\n").trim();
            if (code) {
                blocks.push({
                    code,
                    startLine: blockStart + 1, // 1-indexed
                });
            }
        } else if (inBlock) {
            blockLines.push(lines[i]);
        }
    }

    return blocks;
}

// --- File discovery ---

const SPEC_EXTENSIONS = /\.(json|vl\.json)$/i;
const COMPILED_VEGA = /\.vg\.json$/i;
const MARKDOWN_EXTENSIONS = /\.(md|markdown|mdx)$/i;
const BROKEN_SUFFIX = "_broken.vl.json";
const FUTURE_SUFFIX = "_future.vl.json";

async function findFiles(dir) {
    const results = [];

    async function scan(currentDir) {
        const entries = await readdir(currentDir, { withFileTypes: true });
        for (const entry of entries) {
            const fullPath = join(currentDir, entry.name);
            if (entry.isDirectory()) {
                // Skip hidden dirs and node_modules
                if (entry.name.startsWith(".") || entry.name === "node_modules") continue;
                await scan(fullPath);
            } else if (
                (SPEC_EXTENSIONS.test(entry.name) && !COMPILED_VEGA.test(entry.name)) ||
                MARKDOWN_EXTENSIONS.test(entry.name)
            ) {
                results.push(fullPath);
            }
        }
    }

    await scan(dir);
    return results.sort();
}

// --- Validation ---

async function validateSpec(spec, validator) {
    const errors = [];

    // Check $schema presence
    if (!spec.$schema) {
        errors.push({
            message: "Missing $schema field",
            path: "$",
        });
    }

    // Run AJV validation
    const valid = validator(spec);
    if (!valid) {
        for (const err of validator.errors || []) {
            errors.push({
                message: err.message || "Unknown error",
                path: err.instancePath || "$",
                keyword: err.keyword,
            });
        }
    }

    return { valid: errors.length === 0, errors };
}

// --- Output formatting ---

function formatError(error, indent = "  ") {
    const lines = [];
    lines.push(`${indent}${RED}${error.path || "$"}${RESET}: ${error.message}`);
    if (error.keyword) {
        lines.push(`${indent}  keyword: ${error.keyword}`);
    }
    return lines.join("\n");
}

// --- Main command handlers ---

async function cmdValidate(args) {
    let quiet = false;
    let jsonOutput = false;
    let input = null;

    for (const arg of args) {
        if (arg === "-h" || arg === "--help") {
            printUsage();
            process.exit(0);
        } else if (arg === "-q" || arg === "--quiet") {
            quiet = true;
        } else if (arg === "--json") {
            jsonOutput = true;
        } else if (arg === "--schema") {
            console.log(`Schema: vega-lite v${SCHEMA_VERSION}`);
            console.log(`Bundled: ${BUNDLED_SCHEMA}`);
            process.exit(0);
        } else if (arg === "-") {
            input = "-";
        } else if (arg.startsWith("-")) {
            console.error(`${RED}Error: Unknown option: ${arg}${RESET}`);
            printUsage();
            process.exit(2);
        } else {
            input = arg;
        }
    }

    if (!input) {
        console.error(`${RED}Error: No input specified. Provide a file, directory, or '-' for stdin.${RESET}`);
        printUsage();
        process.exit(2);
    }

    // Load bundled schema and create validator
    const schema = loadSchema();
    const validator = createValidator(schema);

    // --- Stdin mode ---
    if (input === "-") {
        const stdinText = await Bun.stdin.text();
        let spec;
        try {
            spec = JSON.parse(stdinText);
        } catch (e) {
            if (jsonOutput) {
                console.log(
                    JSON.stringify(
                        { valid: false, error: `Invalid JSON: ${e.message}` },
                        null,
                        2
                    )
                );
            } else {
                console.log(`${RED}Invalid JSON${RESET}`);
                console.log(e.message);
            }
            process.exit(1);
        }

        const result = await validateSpec(spec, validator);

        if (jsonOutput) {
            console.log(
                JSON.stringify(
                    {
                        valid: result.valid,
                        errors: result.errors,
                        schema: `vega-lite v${SCHEMA_VERSION}`,
                    },
                    null,
                    2
                )
            );
        } else if (result.valid) {
            console.log(`${GREEN}Valid${RESET}`);
        } else {
            console.log(`${RED}Invalid${RESET}`);
            for (const err of result.errors) {
                console.log(formatError(err));
            }
        }

        process.exit(result.valid ? 0 : 1);
    }

    // --- Check path exists and type ---
    let isDir = false;
    try {
        const statResult = await stat(input);
        isDir = statResult.isDirectory();
    } catch {
        console.error(`${RED}Error: Path does not exist: ${input}${RESET}`);
        process.exit(2);
    }

    let files = [];
    if (isDir) {
        files = await findFiles(input);
    } else {
        files = [input];
    }

    if (files.length === 0) {
        if (jsonOutput) {
            console.log(JSON.stringify({ totalValid: 0, totalInvalid: 0, results: [] }, null, 2));
        } else {
            console.log(`${YELLOW}No spec files found${RESET}`);
        }
        process.exit(0);
    }

    // --- Validate all files ---
    let totalValid = 0;
    let totalInvalid = 0;
    let totalSkipped = 0;
    const allResults = [];

    for (const filePath of files) {
        const fileName = basename(filePath);
        const isMarkdown = MARKDOWN_EXTENSIONS.test(fileName);
        const isBroken = fileName.endsWith(BROKEN_SUFFIX);
        const isFuture = fileName.endsWith(FUTURE_SUFFIX);

        // --- Markdown files: extract code blocks ---
        if (isMarkdown) {
            const content = await Bun.file(filePath).text();
            const blocks = extractVlBlocks(content);

            if (blocks.length === 0) {
                continue; // Skip files with no vega-lite/json blocks
            }

            for (let i = 0; i < blocks.length; i++) {
                const block = blocks[i];
                let spec;
                try {
                    spec = JSON.parse(block.code);
                } catch (e) {
                    totalInvalid++;
                    if (!jsonOutput) {
                        console.log(
                            `${RED}✗${RESET} ${filePath}:block${i + 1} (line ${block.startLine}): Invalid JSON — ${e.message}`
                        );
                    }
                    allResults.push({
                        file: `${filePath}:block${i + 1}`,
                        lineNumber: block.startLine,
                        valid: false,
                        error: `Invalid JSON: ${e.message}`,
                    });
                    continue;
                }

                const result = await validateSpec(spec, validator);

                if (result.valid) {
                    totalValid++;
                    if (!quiet && !jsonOutput) {
                        console.log(
                            `${GREEN}✓${RESET} ${filePath}:block${i + 1} (line ${block.startLine})`
                        );
                    }
                    allResults.push({
                        file: `${filePath}:block${i + 1}`,
                        lineNumber: block.startLine,
                        valid: true,
                    });
                } else {
                    totalInvalid++;
                    if (!jsonOutput) {
                        console.log(
                            `${RED}✗${RESET} ${filePath}:block${i + 1} (line ${block.startLine})`
                        );
                        for (const err of result.errors) {
                            console.log(formatError(err));
                        }
                    }
                    allResults.push({
                        file: `${filePath}:block${i + 1}`,
                        lineNumber: block.startLine,
                        valid: false,
                        errors: result.errors,
                    });
                }
            }
            continue;
        }

        // --- JSON spec files ---

        // Parse JSON
        let spec;
        try {
            const content = await Bun.file(filePath).text();
            spec = JSON.parse(content);
        } catch (e) {
            totalInvalid++;
            if (!jsonOutput) {
                console.log(`${RED}✗${RESET} ${filePath}: Invalid JSON — ${e.message}`);
            }
            allResults.push({
                file: filePath,
                valid: false,
                error: `Invalid JSON: ${e.message}`,
            });
            continue;
        }

        // Handle _broken files — skip validation (they're intentionally invalid)
        if (isBroken) {
            totalSkipped++;
            if (!quiet && !jsonOutput) {
                console.log(`${YELLOW}⊘${RESET} ${filePath} (skipped: broken example)`);
            }
            allResults.push({ file: filePath, skipped: true, reason: "broken example" });
            continue;
        }

        // Handle _future files — skip schema validation
        if (isFuture) {
            totalSkipped++;
            if (!quiet && !jsonOutput) {
                console.log(`${YELLOW}⊘${RESET} ${filePath} (skipped: future features)`);
            }
            allResults.push({ file: filePath, skipped: true, reason: "future features" });
            continue;
        }

        // Validate
        const result = await validateSpec(spec, validator);

        if (result.valid) {
            totalValid++;
            if (!quiet && !jsonOutput) {
                console.log(`${GREEN}✓${RESET} ${filePath}`);
            }
            allResults.push({ file: filePath, valid: true });
        } else {
            totalInvalid++;
            if (!jsonOutput) {
                console.log(`${RED}✗${RESET} ${filePath}`);
                for (const err of result.errors) {
                    console.log(formatError(err));
                }
            }
            allResults.push({ file: filePath, valid: false, errors: result.errors });
        }
    }

    // --- Output summary ---
    if (jsonOutput) {
        console.log(
            JSON.stringify(
                {
                    totalValid,
                    totalInvalid,
                    totalSkipped,
                    schema: `vega-lite v${SCHEMA_VERSION}`,
                    results: allResults,
                },
                null,
                2
            )
        );
    } else {
        console.log("");
        const summaryParts = [
            `${GREEN}${totalValid} valid${RESET}`,
            `${totalInvalid > 0 ? RED : ""}${totalInvalid} invalid${RESET}`,
            `${totalSkipped > 0 ? YELLOW : ""}${totalSkipped} skipped${RESET}`,
        ];
        console.log(`Summary: ${summaryParts.join(", ")}`);
    }

    process.exit(totalInvalid > 0 ? 1 : 0);
}

// --- Schema info subcommand ---

async function cmdSchema() {
    console.log(`Vega-Lite Schema Info`);
    console.log(`  Version: ${SCHEMA_VERSION}`);
    console.log(`  Bundled: ${BUNDLED_SCHEMA}`);

    // Check if bundled schema exists
    try {
        await stat(BUNDLED_SCHEMA);
        const size = (await stat(BUNDLED_SCHEMA)).size;
        console.log(`  Size: ${(size / 1024).toFixed(1)} KB`);
        console.log(`  Status: ${GREEN}bundled (offline)${RESET}`);
    } catch {
        console.log(`  Status: ${RED}missing — validator will fail${RESET}`);
    }
}

// --- Main entry point ---
async function main() {
    const args = process.argv.slice(2);

    if (args.length === 0 || args[0] === "-h" || args[0] === "--help") {
        printUsage();
        process.exit(0);
    }

    const subcommand = args[0];
    const subArgs = args.slice(1);

    switch (subcommand) {
        case "validate":
            await cmdValidate(subArgs);
            break;
        case "schema":
            await cmdSchema();
            break;
        default:
            console.error(`${RED}Error: Unknown subcommand: ${subcommand}${RESET}`);
            printUsage();
            process.exit(2);
    }
}

main().catch((e) => {
    console.error(`${RED}Error: ${e.message}${RESET}`);
    process.exit(2);
});
