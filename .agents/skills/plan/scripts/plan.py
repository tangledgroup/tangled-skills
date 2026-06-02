#!/usr/bin/env python3
"""plan.py — deterministic PLAN.md manager.

All reads and writes of PLAN.md are done via this script.
Uses only Python 3.10+ built-in modules.
"""

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STATUS_TODO = "\u2610"       # ☐ Not Started / To Do
STATUS_QUESTION = "\u2753"   # ❓ Needs Clarification / Question
STATUS_DOING = "\u2699\uFE0F"  # ⚙️ Active / Doing
STATUS_ERROR = "\u274C"      # ❌ Blocked / Error
STATUS_DONE = "\u2611"       # ☑ Completed / Done

ALL_STATUSES = {STATUS_TODO, STATUS_QUESTION, STATUS_DOING, STATUS_ERROR, STATUS_DONE}

# Valid transitions: from_emoji -> set of allowed to_emojis
VALID_TRANSITIONS = {
    STATUS_TODO:     {STATUS_DOING, STATUS_QUESTION},
    STATUS_DOING:    {STATUS_QUESTION, STATUS_ERROR, STATUS_DONE},
    STATUS_QUESTION: {STATUS_DOING},
    STATUS_ERROR:    {STATUS_DOING, STATUS_QUESTION},
}

# ---------------------------------------------------------------------------
# Helpers — file I/O
# ---------------------------------------------------------------------------

def read_plan(path: str) -> str:
    """Read PLAN.md and return its contents."""
    p = Path(path)
    if not p.exists():
        print(f"Error: {path} does not exist", file=sys.stderr)
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def write_plan(path: str, content: str) -> None:
    """Write content to PLAN.md atomically via temp file."""
    p = Path(path)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.rename(p)


# ---------------------------------------------------------------------------
# Helpers — YAML-like header parsing
# ---------------------------------------------------------------------------
# The header is NOT YAML; it's markdown bold fields.
# We parse lines like:
#   **Depends On:** ...
#   **Created:** ...
#   **Updated:** ...
#   **Current Phase:** ...
#   **Current Task:** ...

_HEADER_FIELDS = {
    "depends_on": r"^\*\*Depends On:\*\*(.+)$",
    "created": r"^\*\*Created:\*\*(.+)$",
    "updated": r"^\*\*Updated:\*\*(.+)$",
    "current_phase": r"^\*\*Current Phase:\*\*(.+)$",
    "current_task": r"^\*\*Current Task:\*\*(.+)$",
}


def _parse_header(title_line: str, body_lines: list[str]) -> dict:
    """Return dict with header field values."""
    header = {}
    for key, pattern in _HEADER_FIELDS.items():
        for line in body_lines:
            m = re.match(pattern, line.strip())
            if m:
                header[key] = m.group(1).strip()
                break
        else:
            header[key] = ""
    return header


def _find_header_field_line(lines: list[str], field_name: str) -> int:
    """Return index of line containing **Field:** or -1."""
    pattern = rf"^\*\*{re.escape(field_name)}:\*\*"
    for i, line in enumerate(lines):
        if re.match(pattern, line.strip()):
            return i
    return -1


def _update_header_field(lines: list[str], field_name: str, value: str) -> list[str]:
    """Update or append a header field line. Returns new lines."""
    pattern = rf"^\*\*{re.escape(field_name)}:\*\*"
    idx = -1
    for i, line in enumerate(lines):
        if re.match(pattern, line.strip()):
            idx = i
            break
    if idx >= 0:
        lines[idx] = f"**{field_name}:** {value}"
    else:
        # Insert after **Current Task:** or before first phase heading
        current_task_idx = _find_header_field_line(lines, "Current Task")
        if current_task_idx >= 0:
            lines.insert(current_task_idx + 1, f"**{field_name}:** {value}")
        else:
            # Find first ## Phase line and insert before it
            for i, line in enumerate(lines):
                if re.match(r"^## ", line):
                    lines.insert(i, f"**{field_name}:** {value}")
                    break
            else:
                lines.append(f"**{field_name}:** {value}")
    return lines


def _strip_header_comment(line: str) -> str:
    """Remove inline comment from header template line."""
    return re.sub(r"\s*<!--.*?-->\s*$", "", line).strip()


# ---------------------------------------------------------------------------
# Helpers — plan title parsing
# ---------------------------------------------------------------------------

_TITLE_RE = re.compile(r"^#\s*(\u2610|\u2753|\u2699\uFE0F|\u274C|\u2611)?\s*Plan:\s*(.+)$")


def parse_plan_title(line: str) -> tuple[str, str]:
    """Return (emoji, title) from the plan title line."""
    m = _TITLE_RE.match(line.strip())
    if not m:
        print(f"Error: invalid plan title line: {line!r}", file=sys.stderr)
        sys.exit(1)
    emoji = m.group(1) or STATUS_TODO
    title = m.group(2).strip()
    return emoji, title


def format_plan_title(emoji: str, title: str) -> str:
    """Format plan title line."""
    return f"# {emoji} Plan: {title}"


# ---------------------------------------------------------------------------
# Helpers — phase parsing
# ---------------------------------------------------------------------------

_PHASE_RE = re.compile(r"^##\s*(\u2610|\u2753|\u2699\uFE0F|\u274C|\u2611)?\s*Phase\s+(\d+)\s+(.+)$")


def parse_phase_heading(line: str) -> tuple[str, int, str] | None:
    """Return (emoji, phase_number, title) or None."""
    m = _PHASE_RE.match(line.strip())
    if not m:
        return None
    emoji = m.group(1) or STATUS_TODO
    num = int(m.group(2))
    title = m.group(3).strip()
    return emoji, num, title


def format_phase_heading(emoji: str, num: int, title: str) -> str:
    return f"## {emoji} Phase {num} {title}"


# ---------------------------------------------------------------------------
# Helpers — task parsing
# ---------------------------------------------------------------------------

_TASK_RE = re.compile(
    r"^- (\u2610|\u2753|\u2699\uFE0F|\u274C|\u2611) Task (\d+)\.(\d+)\s+(.+)$"
)


def parse_task_line(line: str) -> tuple[str, int, int, str] | None:
    """Return (emoji, phase_num, task_num, title) or None."""
    m = _TASK_RE.match(line.strip())
    if not m:
        return None
    emoji = m.group(1)
    phase = int(m.group(2))
    task = int(m.group(3))
    title = m.group(4).strip()
    return emoji, phase, task, title


def format_task_line(emoji: str, phase_num: int, task_num: int, title: str) -> str:
    """Format a task line. Title may already include (depends on: ...) suffix."""
    return f"- {emoji} Task {phase_num}.{task_num} {title}"


# ---------------------------------------------------------------------------
# Helpers — structure extraction
# ---------------------------------------------------------------------------

def extract_phases(content: str) -> list[tuple[str, int, str, list[tuple[str, int, int, str]]]]:
    """Extract all phases with their tasks.

    Returns list of (emoji, phase_num, title, [(emoji, phase, task, title), ...]).
    """
    lines = content.splitlines()
    phases: list[tuple[str, int, str, list[tuple[str, int, int, str]]]] = []
    current_phase: tuple[str, int, str] | None = None
    current_tasks: list[tuple[str, int, int, str]] = []

    for line in lines:
        phase_match = parse_phase_heading(line)
        if phase_match:
            # Save previous phase
            if current_phase is not None:
                phases.append((current_phase[0], current_phase[1], current_phase[2], current_tasks))
            current_phase = phase_match
            current_tasks = []
            continue

        if current_phase is not None:
            task_match = parse_task_line(line)
            if task_match:
                current_tasks.append(task_match)

    # Save last phase
    if current_phase is not None:
        phases.append((current_phase[0], current_phase[1], current_phase[2], current_tasks))

    return phases


def extract_phases_lines(content: str) -> list[tuple[int, int]]:
    """Return list of (start_line, end_line) for each phase section (0-indexed).

    start_line = line with ## Phase heading
    end_line = last line before next ## or EOF
    """
    lines = content.splitlines()
    ranges: list[tuple[int, int]] = []
    phase_starts: list[int] = []

    for i, line in enumerate(lines):
        if parse_phase_heading(line) is not None:
            phase_starts.append(i)

    for idx, start in enumerate(phase_starts):
        end = phase_starts[idx + 1] - 1 if idx + 1 < len(phase_starts) else len(lines) - 1
        ranges.append((start, end))

    return ranges


# ---------------------------------------------------------------------------
# Status derivation
# ---------------------------------------------------------------------------

def derive_phase_status(tasks: list[tuple[str, int, int, str]], warn: bool = False) -> str:
    """Derive phase emoji from its tasks."""
    if not tasks:
        if warn:
            print(f"Warning: Phase has zero tasks — it can never reach {STATUS_DONE}", file=sys.stderr)
        return STATUS_TODO

    emojis = {t[0] for t in tasks}

    if all(t[0] == STATUS_DONE for t in tasks):
        return STATUS_DONE
    if STATUS_DOING in emojis:
        return STATUS_DOING
    if STATUS_QUESTION in emojis:
        return STATUS_QUESTION
    if STATUS_ERROR in emojis:
        return STATUS_ERROR
    return STATUS_TODO


def derive_plan_status(phases: list[tuple[str, int, str, list]]) -> str:
    """Derive plan emoji from all phases."""
    if not phases:
        return STATUS_TODO

    # Derive each phase status from its tasks
    phase_statuses = [derive_phase_status(tasks) for _, _, _, tasks in phases]

    if all(s == STATUS_DONE for s in phase_statuses):
        return STATUS_DONE
    if STATUS_DOING in phase_statuses:
        return STATUS_DOING
    if STATUS_QUESTION in phase_statuses:
        return STATUS_QUESTION
    if STATUS_ERROR in phase_statuses:
        return STATUS_ERROR
    return STATUS_TODO


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_transition(current: str, new: str) -> bool:
    """Check if transition is valid. Returns True if valid."""
    if current == new:
        return True
    allowed = VALID_TRANSITIONS.get(current, set())
    return new in allowed


def check_dependency_cycle(plan_path: str, depends_on: list[str]) -> None:
    """Check for cycles in dependency graph. Exits with error if cycle found.

    Walks from each dependency transitively and checks if we can reach back
    to plan_path.
    """
    base_resolved = str(Path(plan_path).resolve())
    visited = set()
    stack = [str(Path(d).resolve()) for d in depends_on]

    while stack:
        current_resolved = stack.pop()
        if current_resolved == base_resolved:
            print(f"Error: dependency cycle detected involving {plan_path}", file=sys.stderr)
            sys.exit(1)
        if current_resolved in visited:
            continue
        visited.add(current_resolved)

        # Resolve the original path for reading
        # We need to find a path that resolves to current_resolved
        # Read from the resolved path directly
        try:
            dep_content = Path(current_resolved).read_text(encoding="utf-8")
            dep_header = _parse_header("", dep_content.splitlines())
            deps_str = dep_header.get("depends_on", "NONE").strip()
            if deps_str and deps_str != "NONE":
                deps = [d.strip() for d in deps_str.split(",")]
                for d in deps:
                    resolved_d = str(Path(d).resolve())
                    stack.append(resolved_d)
        except (FileNotFoundError, SystemExit, PermissionError):
            pass  # plan doesn't exist, skip


def validate_status_set(content: str) -> str:
    """Re-derive all phase and plan statuses from tasks. Returns updated content."""
    lines = content.splitlines()
    phases = extract_phases("\n".join(lines))

    # Update phase headings with derived statuses
    for emoji, num, title, tasks in phases:
        derived = derive_phase_status(tasks)
        old_heading = format_phase_heading(emoji, num, title)
        new_heading = format_phase_heading(derived, num, title)
        for i, line in enumerate(lines):
            if line.strip() == old_heading:
                lines[i] = new_heading
                break

    # Update plan title with derived status
    plan_status = derive_plan_status(phases)
    for i, line in enumerate(lines):
        m = _TITLE_RE.match(line.strip())
        if m:
            title_text = m.group(2).strip()
            lines[i] = format_plan_title(plan_status, title_text)
            break

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Commands — create
# ---------------------------------------------------------------------------

def cmd_create(args: argparse.Namespace) -> None:
    """Create a new PLAN.md with header."""
    path = args.path
    title = args.title
    depends = getattr(args, "depends", []) or []

    if Path(path).exists():
        print(f"Error: {path} already exists", file=sys.stderr)
        sys.exit(1)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    deps_str = "NONE"
    if depends:
        deps_str = " , ".join(depends)

    content = f"""# {STATUS_TODO} Plan: {title}

**Depends On:** {deps_str}

**Created:** {now}

**Updated:** {now}

**Current Phase:** NONE

**Current Task:** NONE
"""
    write_plan(path, content)
    print(f"Created {path}")

    # Check for dependency cycles
    if depends:
        check_dependency_cycle(path, depends)


# ---------------------------------------------------------------------------
# Commands — get (header reads)
# ---------------------------------------------------------------------------

def cmd_get_plan_title(args: argparse.Namespace) -> None:
    content = read_plan(args.path)
    lines = content.splitlines()
    for line in lines:
        m = _TITLE_RE.match(line.strip())
        if m:
            print(m.group(2).strip())
            return
    print("Error: no plan title found", file=sys.stderr)
    sys.exit(1)


def cmd_get_plan_depends_on(args: argparse.Namespace) -> None:
    content = read_plan(args.path)
    header = _parse_header("", content.splitlines())
    print(header.get("depends_on", "NONE"))


def cmd_get_plan_created(args: argparse.Namespace) -> None:
    content = read_plan(args.path)
    header = _parse_header("", content.splitlines())
    print(header.get("created", ""))


def cmd_get_plan_updated(args: argparse.Namespace) -> None:
    content = read_plan(args.path)
    header = _parse_header("", content.splitlines())
    print(header.get("updated", ""))


def cmd_get_plan_current_phase(args: argparse.Namespace) -> None:
    content = read_plan(args.path)
    header = _parse_header("", content.splitlines())
    print(header.get("current_phase", "NONE"))


def cmd_get_plan_current_task(args: argparse.Namespace) -> None:
    content = read_plan(args.path)
    header = _parse_header("", content.splitlines())
    print(header.get("current_task", "NONE"))


# ---------------------------------------------------------------------------
# Commands — set (header writes)
# ---------------------------------------------------------------------------

def _touch_updated(path: str, content: str) -> str:
    """Update the Updated timestamp in content."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = content.splitlines()
    return "\n".join(_update_header_field(lines, "Updated", now))


def cmd_set_plan_title(args: argparse.Namespace) -> None:
    content = read_plan(args.path)
    lines = content.splitlines()
    new_title = args.title
    for i, line in enumerate(lines):
        m = _TITLE_RE.match(line.strip())
        if m:
            current_emoji = m.group(1) or STATUS_TODO
            lines[i] = format_plan_title(current_emoji, new_title)
            break
    content = "\n".join(lines)
    content = _touch_updated(args.path, content)
    content = validate_status_set(content)
    write_plan(args.path, content)
    print(f"Set plan title to: {new_title}")


def cmd_set_plan_depends_on(args: argparse.Namespace) -> None:
    content = read_plan(args.path)
    deps = getattr(args, "deps", []) or []
    deps_str = "NONE" if not deps else " , ".join(deps)
    lines = content.splitlines()
    lines = _update_header_field(lines, "Depends On", deps_str)
    content = "\n".join(lines)
    content = _touch_updated(args.path, content)
    write_plan(args.path, content)

    # Check for cycles
    if deps:
        check_dependency_cycle(args.path, deps)
    print(f"Set depends on to: {deps_str}")


def cmd_set_plan_created(args: argparse.Namespace) -> None:
    content = read_plan(args.path)
    val = args.value
    if val in ("--now", "__NOW__"):
        val = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = content.splitlines()
    lines = _update_header_field(lines, "Created", val)
    content = "\n".join(lines)
    content = _touch_updated(args.path, content)
    write_plan(args.path, content)
    print(f"Set created to: {val}")


def cmd_set_plan_updated(args: argparse.Namespace) -> None:
    content = read_plan(args.path)
    val = args.value
    if val in ("--now", "__NOW__"):
        val = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = content.splitlines()
    lines = _update_header_field(lines, "Updated", val)
    content = "\n".join(lines)
    write_plan(args.path, content)
    print(f"Set updated to: {val}")


def cmd_set_plan_current_phase(args: argparse.Namespace) -> None:
    content = read_plan(args.path)
    phase_ref = args.phase_ref  # e.g. "Phase 2"
    lines = content.splitlines()

    # Find the phase and copy its emoji + full heading
    target_emoji = None
    target_text = None
    for line in lines:
        m = parse_phase_heading(line)
        if m:
            emoji, num, title = m
            if f"Phase {num}" == phase_ref.strip():
                target_emoji = emoji
                target_text = f"{emoji} Phase {num}"
                break

    if target_text is None:
        print(f"Error: {phase_ref} not found", file=sys.stderr)
        sys.exit(1)

    lines = _update_header_field(lines, "Current Phase", target_text)
    content = "\n".join(lines)
    content = _touch_updated(args.path, content)
    write_plan(args.path, content)
    print(f"Set current phase to: {target_text}")


def cmd_set_plan_current_task(args: argparse.Namespace) -> None:
    content = read_plan(args.path)
    task_ref = args.task_ref  # e.g. "Task 2.3"
    lines = content.splitlines()

    # Parse task ref
    m = re.match(r"Task\s+(\d+)\.(\d+)", task_ref.strip())
    if not m:
        print(f"Error: invalid task ref: {task_ref!r}", file=sys.stderr)
        sys.exit(1)
    target_phase = int(m.group(1))
    target_task = int(m.group(2))

    # Find the task and copy its emoji + full reference
    target_text = None
    for line in lines:
        t = parse_task_line(line)
        if t and t[1] == target_phase and t[2] == target_task:
            target_text = f"{t[0]} Task {target_phase}.{target_task}"
            break

    if target_text is None:
        print(f"Error: {task_ref} not found", file=sys.stderr)
        sys.exit(1)

    lines = _update_header_field(lines, "Current Task", target_text)
    content = "\n".join(lines)
    content = _touch_updated(args.path, content)
    write_plan(args.path, content)
    print(f"Set current task to: {target_text}")


# ---------------------------------------------------------------------------
# Commands — status reads
# ---------------------------------------------------------------------------

def cmd_get_plan_status(args: argparse.Namespace) -> None:
    content = read_plan(args.path)
    lines = content.splitlines()
    for line in lines:
        m = _TITLE_RE.match(line.strip())
        if m:
            print(m.group(1) or STATUS_TODO)
            return
    print(STATUS_TODO)


def cmd_get_phase_status(args: argparse.Namespace) -> None:
    content = read_plan(args.path)
    phase_ref = args.phase_ref  # e.g. "Phase 2"
    lines = content.splitlines()
    m = re.match(r"Phase\s+(\d+)", phase_ref.strip())
    if not m:
        print(f"Error: invalid phase ref: {phase_ref!r}", file=sys.stderr)
        sys.exit(1)
    target = int(m.group(1))

    for line in lines:
        p = parse_phase_heading(line)
        if p and p[1] == target:
            print(p[0])
            return
    print(f"Error: {phase_ref} not found", file=sys.stderr)
    sys.exit(1)


def cmd_get_task_status(args: argparse.Namespace) -> None:
    content = read_plan(args.path)
    task_ref = args.task_ref  # e.g. "Task 2.3"
    lines = content.splitlines()
    m = re.match(r"Task\s+(\d+)\.(\d+)", task_ref.strip())
    if not m:
        print(f"Error: invalid task ref: {task_ref!r}", file=sys.stderr)
        sys.exit(1)
    target_phase = int(m.group(1))
    target_task = int(m.group(2))

    for line in lines:
        t = parse_task_line(line)
        if t and t[1] == target_phase and t[2] == target_task:
            print(t[0])
            return
    print(f"Error: {task_ref} not found", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Commands — status writes
# ---------------------------------------------------------------------------

def cmd_set_all_statuses(args: argparse.Namespace) -> None:
    """Set plan, all phases, and all tasks to the same status."""
    content = read_plan(args.path)
    new_status = args.status

    if new_status not in ALL_STATUSES:
        print(f"Error: invalid status {new_status!r}", file=sys.stderr)
        sys.exit(1)

    lines = content.splitlines()

    # Update plan title
    for i, line in enumerate(lines):
        m = _TITLE_RE.match(line.strip())
        if m:
            title_text = m.group(2).strip()
            lines[i] = format_plan_title(new_status, title_text)
            break

    # Update all phase headings
    for i, line in enumerate(lines):
        p = parse_phase_heading(line)
        if p:
            lines[i] = format_phase_heading(new_status, p[1], p[2])

    # Update all tasks
    for i, line in enumerate(lines):
        t = parse_task_line(line)
        if t:
            lines[i] = format_task_line(new_status, t[1], t[2], t[3])

    content = "\n".join(lines)
    content = _touch_updated(args.path, content)
    write_plan(args.path, content)
    print(f"Set all statuses to: {new_status}")


def cmd_set_plan_status(args: argparse.Namespace) -> None:
    """Set plan status (emoji in title)."""
    content = read_plan(args.path)
    new_status = args.status

    if new_status not in ALL_STATUSES:
        print(f"Error: invalid status {new_status!r}", file=sys.stderr)
        sys.exit(1)

    lines = content.splitlines()
    for i, line in enumerate(lines):
        m = _TITLE_RE.match(line.strip())
        if m:
            title_text = m.group(2).strip()
            lines[i] = format_plan_title(new_status, title_text)
            break

    content = "\n".join(lines)
    content = _touch_updated(args.path, content)
    write_plan(args.path, content)
    print(f"Set plan status to: {new_status}")


def cmd_set_phase_status(args: argparse.Namespace) -> None:
    """Set phase status (emoji in heading)."""
    content = read_plan(args.path)
    phase_ref = args.phase_ref
    new_status = args.status

    if new_status not in ALL_STATUSES:
        print(f"Error: invalid status {new_status!r}", file=sys.stderr)
        sys.exit(1)

    m = re.match(r"Phase\s+(\d+)", phase_ref.strip())
    if not m:
        print(f"Error: invalid phase ref: {phase_ref!r}", file=sys.stderr)
        sys.exit(1)
    target = int(m.group(1))

    lines = content.splitlines()
    found = False
    for i, line in enumerate(lines):
        p = parse_phase_heading(line)
        if p and p[1] == target:
            # Validate transition
            if not validate_transition(p[0], new_status):
                print(
                    f"Error: invalid transition {p[0]} -> {new_status} for {phase_ref}",
                    file=sys.stderr,
                )
                sys.exit(1)
            lines[i] = format_phase_heading(new_status, p[1], p[2])
            found = True
            break

    if not found:
        print(f"Error: {phase_ref} not found", file=sys.stderr)
        sys.exit(1)

    content = "\n".join(lines)
    content = _touch_updated(args.path, content)
    write_plan(args.path, content)
    print(f"Set {phase_ref} status to: {new_status}")


def cmd_set_task_status(args: argparse.Namespace) -> None:
    """Set task status (emoji in task line)."""
    content = read_plan(args.path)
    task_ref = args.task_ref
    new_status = args.status

    if new_status not in ALL_STATUSES:
        print(f"Error: invalid status {new_status!r}", file=sys.stderr)
        sys.exit(1)

    m = re.match(r"Task\s+(\d+)\.(\d+)", task_ref.strip())
    if not m:
        print(f"Error: invalid task ref: {task_ref!r}", file=sys.stderr)
        sys.exit(1)
    target_phase = int(m.group(1))
    target_task = int(m.group(2))

    lines = content.splitlines()
    found = False
    for i, line in enumerate(lines):
        t = parse_task_line(line)
        if t and t[1] == target_phase and t[2] == target_task:
            # Validate transition
            if not validate_transition(t[0], new_status):
                print(
                    f"Error: invalid transition {t[0]} -> {new_status} for {task_ref}",
                    file=sys.stderr,
                )
                sys.exit(1)
            lines[i] = format_task_line(new_status, t[1], t[2], t[3])
            found = True
            break

    if not found:
        print(f"Error: {task_ref} not found", file=sys.stderr)
        sys.exit(1)

    content = "\n".join(lines)
    content = _touch_updated(args.path, content)
    # Re-derive phase and plan statuses
    content = validate_status_set(content)
    write_plan(args.path, content)
    print(f"Set {task_ref} status to: {new_status}")


# ---------------------------------------------------------------------------
# Commands — Phase CRUD
# ---------------------------------------------------------------------------

def cmd_add_phase(args: argparse.Namespace) -> None:
    """Add a new phase at the end of the plan."""
    content = read_plan(args.path)
    phase_title = args.phase_title
    description = getattr(args, "description", "") or ""

    lines = content.splitlines()
    phases = extract_phases(content)

    # Determine next phase number
    next_num = len(phases) + 1

    # Build new phase section
    new_phase_lines = [
        "",
        format_phase_heading(STATUS_TODO, next_num, phase_title),
    ]
    if description:
        new_phase_lines.append(description)

    content = "\n".join(lines) + "\n" + "\n".join(new_phase_lines) + "\n"
    content = _touch_updated(args.path, content)
    write_plan(args.path, content)
    print(f"Added Phase {next_num} ({phase_title}) with status {STATUS_TODO}")


def cmd_update_phase(args: argparse.Namespace) -> None:
    """Update phase description/title."""
    content = read_plan(args.path)
    phase_ref = args.phase_ref
    new_description = args.description

    m = re.match(r"Phase\s+(\d+)", phase_ref.strip())
    if not m:
        print(f"Error: invalid phase ref: {phase_ref!r}", file=sys.stderr)
        sys.exit(1)
    target = int(m.group(1))

    lines = content.splitlines()
    found = False
    for i, line in enumerate(lines):
        p = parse_phase_heading(line)
        if p and p[1] == target:
            found = True
            break

    if not found:
        print(f"Error: {phase_ref} not found", file=sys.stderr)
        sys.exit(1)

    # Replace the phase heading line's title with new description if it looks like a title update
    # or append/update description lines after the heading
    # For simplicity: replace the phase title part of the heading
    for i, line in enumerate(lines):
        p = parse_phase_heading(line)
        if p and p[1] == target:
            current_emoji = p[0]
            lines[i] = format_phase_heading(current_emoji, target, new_description)
            break

    content = "\n".join(lines)
    content = _touch_updated(args.path, content)
    # Set phase status to question as per spec
    content = validate_status_set(content)
    write_plan(args.path, content)
    print(f"Updated {phase_ref} description to: {new_description}")


def cmd_remove_phase(args: argparse.Namespace) -> None:
    """Remove a phase and all its tasks."""
    content = read_plan(args.path)
    phase_ref = args.phase_ref

    m = re.match(r"Phase\s+(\d+)", phase_ref.strip())
    if not m:
        print(f"Error: invalid phase ref: {phase_ref!r}", file=sys.stderr)
        sys.exit(1)
    target = int(m.group(1))

    lines = content.splitlines()
    phase_ranges = extract_phases_lines("\n".join(lines))

    # Find the phase range to remove
    remove_start = None
    remove_end = None
    for start, end in phase_ranges:
        p = parse_phase_heading(lines[start])
        if p and p[1] == target:
            remove_start = start
            remove_end = end + 1  # exclusive
            break

    if remove_start is None:
        print(f"Error: {phase_ref} not found", file=sys.stderr)
        sys.exit(1)

    # Remove lines for this phase (including trailing blank line if any)
    # Also remove one leading blank line if present
    if remove_start > 0 and lines[remove_start - 1].strip() == "":
        remove_start -= 1

    new_lines = lines[:remove_start] + lines[remove_end:]

    content = "\n".join(new_lines)
    content = _touch_updated(args.path, content)
    content = validate_status_set(content)
    write_plan(args.path, content)
    print(f"Removed {phase_ref}")


# ---------------------------------------------------------------------------
# Commands — Task CRUD
# ---------------------------------------------------------------------------

def cmd_add_task(args: argparse.Namespace) -> None:
    """Add a new task to an existing phase."""
    content = read_plan(args.path)
    phase_ref = args.phase_ref
    task_title = args.task_title  # e.g. "Task 2.4" or just the title text

    m = re.match(r"Task\s+(\d+)\.(\d+)", task_title.strip())
    if not m:
        # User provided just a description, auto-number
        phase_m = re.match(r"Phase\s+(\d+)", phase_ref.strip())
        if not phase_m:
            print(f"Error: invalid phase ref: {phase_ref!r}", file=sys.stderr)
            sys.exit(1)
        target_phase = int(phase_m.group(1))
        # Find max task number in this phase
        phases = extract_phases(content)
        max_task = 0
        for emoji, num, title, tasks in phases:
            if num == target_phase:
                for t in tasks:
                    if t[2] > max_task:
                        max_task = t[2]
        next_task = max_task + 1
        task_title = f"Task {target_phase}.{next_task} {task_title}"

    lines = content.splitlines()

    # Find the phase and add task after its last task (or right after heading)
    phase_m = re.match(r"Phase\s+(\d+)", phase_ref.strip())
    if not phase_m:
        print(f"Error: invalid phase ref: {phase_ref!r}", file=sys.stderr)
        sys.exit(1)
    target_phase = int(phase_m.group(1))

    insert_idx = None
    for i, line in enumerate(lines):
        p = parse_phase_heading(line)
        if p and p[1] == target_phase:
            # Find the last task in this phase
            insert_idx = i + 1
            for j in range(i + 1, len(lines)):
                t = parse_task_line(lines[j])
                if t and t[1] == target_phase:
                    # Also skip sub-bullets
                    insert_idx = j + 1
                    k = j + 1
                    while k < len(lines) and lines[k].strip().startswith("- "):
                        k += 1
                    insert_idx = k
                elif lines[j].strip() == "" and j > i:
                    # blank line after heading, skip
                    insert_idx = j + 1
                elif parse_phase_heading(lines[j]) is not None:
                    # next phase, stop
                    break
                else:
                    insert_idx = j
                    break
            break

    if insert_idx is None:
        print(f"Error: {phase_ref} not found", file=sys.stderr)
        sys.exit(1)

    task_line = f"- {STATUS_TODO} {task_title}"
    lines.insert(insert_idx, task_line)

    content = "\n".join(lines)
    content = _touch_updated(args.path, content)
    content = validate_status_set(content)
    write_plan(args.path, content)
    print(f"Added {task_title} to {phase_ref} with status {STATUS_TODO}")


def cmd_update_task(args: argparse.Namespace) -> None:
    """Update task description."""
    content = read_plan(args.path)
    phase_ref = args.phase_ref
    task_ref = args.task_ref
    new_description = args.description

    m = re.match(r"Task\s+(\d+)\.(\d+)", task_ref.strip())
    if not m:
        print(f"Error: invalid task ref: {task_ref!r}", file=sys.stderr)
        sys.exit(1)
    target_phase = int(m.group(1))
    target_task = int(m.group(2))

    lines = content.splitlines()
    found = False
    for i, line in enumerate(lines):
        t = parse_task_line(line)
        if t and t[1] == target_phase and t[2] == target_task:
            found = True
            # Build new task line with updated title
            current_emoji = t[0]
            lines[i] = format_task_line(current_emoji, target_phase, target_task, new_description)
            break

    if not found:
        print(f"Error: {task_ref} not found in {phase_ref}", file=sys.stderr)
        sys.exit(1)

    content = "\n".join(lines)
    content = _touch_updated(args.path, content)
    content = validate_status_set(content)
    write_plan(args.path, content)
    print(f"Updated {task_ref} description to: {new_description}")


def cmd_remove_task(args: argparse.Namespace) -> None:
    """Remove a task from a phase."""
    content = read_plan(args.path)
    phase_ref = args.phase_ref
    task_ref = args.task_ref

    m = re.match(r"Task\s+(\d+)\.(\d+)", task_ref.strip())
    if not m:
        print(f"Error: invalid task ref: {task_ref!r}", file=sys.stderr)
        sys.exit(1)
    target_phase = int(m.group(1))
    target_task = int(m.group(2))

    lines = content.splitlines()
    remove_start = None
    remove_end = None

    for i, line in enumerate(lines):
        t = parse_task_line(line)
        if t and t[1] == target_phase and t[2] == target_task:
            remove_start = i
            # Skip sub-bullets
            remove_end = i + 1
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith("- "):
                remove_end = j + 1
                j += 1
            break

    if remove_start is None:
        print(f"Error: {task_ref} not found in {phase_ref}", file=sys.stderr)
        sys.exit(1)

    new_lines = lines[:remove_start] + lines[remove_end:]

    content = "\n".join(new_lines)
    content = _touch_updated(args.path, content)
    content = validate_status_set(content)
    write_plan(args.path, content)
    print(f"Removed {task_ref}")


# ---------------------------------------------------------------------------
# CLI — Argument Parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="plan.py",
        description="Deterministic PLAN.md manager — all reads/writes via script.",
    )
    parser.add_argument("path", help="Path to PLAN.md file")

    sub = parser.add_subparsers(dest="command", required=True)

    # --- create ---
    p_create = sub.add_parser("create", help="Create a new PLAN.md")
    p_create.add_argument("title", help="Plan title")
    p_create.add_argument("depends", nargs="*", default=[], help="Dependency PLAN.md paths")

    # --- get (header reads) ---
    sub.add_parser("get-plan-title", help="Get plan title")
    sub.add_parser("get-plan-depends-on", help="Get dependencies")
    sub.add_parser("get-plan-created", help="Get created timestamp")
    sub.add_parser("get-plan-updated", help="Get updated timestamp")
    sub.add_parser("get-plan-current-phase", help="Get current phase")
    sub.add_parser("get-plan-current-task", help="Get current task")

    # --- set (header writes) ---
    p_set_title = sub.add_parser("set-plan-title", help="Set plan title")
    p_set_title.add_argument("title", help="New plan title")

    p_set_deps = sub.add_parser("set-plan-depends-on", help="Set dependencies")
    p_set_deps.add_argument("deps", nargs="*", default=[], help="Dependency PLAN.md paths or NONE")

    p_set_created = sub.add_parser("set-plan-created", help="Set created timestamp")
    p_set_created.add_argument("value", nargs="?", default="--now", help="ISO 8601 timestamp or --now (default: --now)")

    p_set_updated = sub.add_parser("set-plan-updated", help="Set updated timestamp")
    p_set_updated.add_argument("value", nargs="?", default="--now", help="ISO 8601 timestamp or --now (default: --now)")

    p_set_cp = sub.add_parser("set-plan-current-phase", help="Set current phase")
    p_set_cp.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2"')

    p_set_ct = sub.add_parser("set-plan-current-task", help="Set current task")
    p_set_ct.add_argument("task_ref", help='Task reference, e.g. "Task 2.3"')

    # --- status reads ---
    sub.add_parser("get-plan-status", help="Get plan status emoji")

    p_gps = sub.add_parser("get-phase-status", help="Get phase status emoji")
    p_gps.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2"')

    p_gts = sub.add_parser("get-task-status", help="Get task status emoji")
    p_gts.add_argument("task_ref", help='Task reference, e.g. "Task 2.3"')

    # --- status writes ---
    p_sas = sub.add_parser("set-all-statuses", help="Set all statuses to same value")
    p_sas.add_argument("status", help="Status emoji")

    p_sps = sub.add_parser("set-plan-status", help="Set plan status")
    p_sps.add_argument("status", help="Status emoji")

    p_sphs = sub.add_parser("set-phase-status", help="Set phase status")
    p_sphs.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2"')
    p_sphs.add_argument("status", help="Status emoji")

    p_sts = sub.add_parser("set-task-status", help="Set task status")
    p_sts.add_argument("task_ref", help='Task reference, e.g. "Task 2.3"')
    p_sts.add_argument("status", help="Status emoji")

    # --- phase CRUD ---
    p_add_phase = sub.add_parser("add-phase", help="Add a new phase")
    p_add_phase.add_argument("phase_title", help="Phase title")
    p_add_phase.add_argument("description", nargs="?", default="", help="Optional description")

    p_upd_phase = sub.add_parser("update-phase", help="Update phase title/description")
    p_upd_phase.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2"')
    p_upd_phase.add_argument("description", help="New description/title")

    p_rm_phase = sub.add_parser("remove-phase", help="Remove a phase and its tasks")
    p_rm_phase.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2"')

    # --- task CRUD ---
    p_add_task = sub.add_parser("add-task", help="Add a new task")
    p_add_task.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2"')
    p_add_task.add_argument("task_title", help="Task title (e.g. 'Task 2.4 Do thing' or just 'Do thing')")

    p_upd_task = sub.add_parser("update-task", help="Update task description")
    p_upd_task.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2"')
    p_upd_task.add_argument("task_ref", help='Task reference, e.g. "Task 2.4"')
    p_upd_task.add_argument("description", help="New description")

    p_rm_task = sub.add_parser("remove-task", help="Remove a task")
    p_rm_task.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2"')
    p_rm_task.add_argument("task_ref", help='Task reference, e.g. "Task 2.4"')

    return parser


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

COMMAND_MAP = {
    "create": cmd_create,
    "get-plan-title": cmd_get_plan_title,
    "get-plan-depends-on": cmd_get_plan_depends_on,
    "get-plan-created": cmd_get_plan_created,
    "get-plan-updated": cmd_get_plan_updated,
    "get-plan-current-phase": cmd_get_plan_current_phase,
    "get-plan-current-task": cmd_get_plan_current_task,
    "set-plan-title": cmd_set_plan_title,
    "set-plan-depends-on": cmd_set_plan_depends_on,
    "set-plan-created": cmd_set_plan_created,
    "set-plan-updated": cmd_set_plan_updated,
    "set-plan-current-phase": cmd_set_plan_current_phase,
    "set-plan-current-task": cmd_set_plan_current_task,
    "get-plan-status": cmd_get_plan_status,
    "get-phase-status": cmd_get_phase_status,
    "get-task-status": cmd_get_task_status,
    "set-all-statuses": cmd_set_all_statuses,
    "set-plan-status": cmd_set_plan_status,
    "set-phase-status": cmd_set_phase_status,
    "set-task-status": cmd_set_task_status,
    "add-phase": cmd_add_phase,
    "update-phase": cmd_update_phase,
    "remove-phase": cmd_remove_phase,
    "add-task": cmd_add_task,
    "update-task": cmd_update_task,
    "remove-task": cmd_remove_task,
}


def _preprocess_args(argv: list[str]) -> list[str]:
    """Replace --now with a safe token before argparse sees it."""
    return ["__NOW__" if a == "--now" else a for a in argv]


def main() -> None:
    parser = build_parser()
    args = parser.parse_args(_preprocess_args(sys.argv[1:]))

    handler = COMMAND_MAP.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    try:
        handler(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
