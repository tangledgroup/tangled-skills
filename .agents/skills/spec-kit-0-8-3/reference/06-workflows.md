# Workflows Engine

Workflows automate multi-step Spec-Driven Development processes — chaining commands, prompts, shell steps, and human checkpoints into repeatable sequences. They support conditional logic, loops, fan-out/fan-in, and can be paused and resumed from the exact point of interruption.

## Running Workflows

### Run a Workflow

```bash
specify workflow run <source>
```

| Option              | Description                                              |
| ------------------- | -------------------------------------------------------- |
| `-i` / `--input`    | Pass input values as `key=value` (repeatable)            |

Runs a workflow from a catalog ID, URL, or local file path. Inputs declared by the workflow can be provided via `--input` or will be prompted interactively.

```bash
specify workflow run speckit -i spec="Build a kanban board with drag-and-drop task management" -i scope=full
```

> **Note:** All workflow commands require a project already initialized with `specify init`.

### Resume a Workflow

```bash
specify workflow resume <run_id>
```

Resumes a paused or failed workflow run from the exact step where it stopped. Useful after responding to a gate step or fixing an issue that caused a failure.

### Workflow Status

```bash
specify workflow status [<run_id>]
```

Shows the status of a specific run, or lists all runs if no ID is given. Run states: `created`, `running`, `completed`, `paused`, `failed`, `aborted`.

## Managing Workflows

### List Installed Workflows

```bash
specify workflow list
```

Lists workflows installed in the current project.

### Install a Workflow

```bash
specify workflow add <source>
```

Installs a workflow from the catalog, a URL (HTTPS required), or a local file path.

### Remove a Workflow

```bash
specify workflow remove <workflow_id>
```

Removes an installed workflow from the project.

### Search Available Workflows

```bash
specify workflow search [query]
```

| Option  | Description     |
| ------- | --------------- |
| `--tag` | Filter by tag   |

Searches all active catalogs for workflows matching the query.

### Workflow Info

```bash
specify workflow info <workflow_id>
```

Shows detailed information about a workflow, including its steps, inputs, and requirements.

## Catalog Management

Workflow catalogs control where `search` and `add` look for workflows. Catalogs are checked in priority order.

### List Catalogs

```bash
specify workflow catalog list
```

Shows all active catalog sources.

### Add a Catalog

```bash
specify workflow catalog add <url>
```

| Option          | Description                      |
| --------------- | -------------------------------- |
| `--name <name>` | Optional name for the catalog    |

Adds a custom catalog URL to the project's `.specify/workflow-catalogs.yml`.

### Remove a Catalog

```bash
specify workflow catalog remove <index>
```

Removes a catalog by its index in the catalog list.

## Workflow Features

### Conditional Logic

Workflows support branching based on conditions, allowing different paths through the SDD process depending on inputs, environment state, or previous step results.

### Loops

Iterate over collections of items — for example, running the same validation check across multiple feature specs, or processing a list of user stories.

### Fan-Out / Fan-In

Execute multiple steps in parallel and wait for all to complete before proceeding. Useful for running independent analyses or generating artifacts that don't depend on each other.

### Human Checkpoints

Pause workflow execution to require human input or approval before continuing. The workflow can be resumed later with `specify workflow resume`.

### Pause and Resume

Workflows maintain their state between runs. If a workflow is paused (by a checkpoint or failure), it can be resumed from the exact step where it stopped using the run ID.

## Example: Automated SDD Pipeline

A typical workflow might chain the full SDD lifecycle:

1. Run `/speckit.specify` with user-provided requirements
2. Run `/speckit.clarify` to resolve ambiguities
3. Human checkpoint — review clarified spec
4. Run `/speckit.plan` with tech stack choices
5. Run `/speckit.analyze` for consistency validation
6. Run `/speckit.tasks` to generate task breakdown
7. Fan-out: run `/speckit.checklist` and security review in parallel
8. Human checkpoint — approve implementation plan
9. Run `/speckit.implement` to execute all tasks

This entire pipeline can be triggered with a single `specify workflow run` command, pausing only at the human checkpoints.
