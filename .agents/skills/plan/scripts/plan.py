#!/usr/bin/env python3
"""plan.py — deterministic PLAN.md manager with atomic updates.

All reads and writes of PLAN.md are done via this script.
Uses only Python 3.10+ built-in modules.

Concurrency model:
  - All mutating commands use _safe_edit() which holds an exclusive
    file lock (fcntl.flock) for the entire read-transform-write cycle.
  - Read-only commands use a shared lock so they never see partial state.
  - Writes are crash-safe: temp file + fsync + atomic rename on same
    filesystem. Orphaned temp files from crashes are cleaned up.
  - A SHA-256 checksum comment at the bottom of each PLAN.md allows
    detecting corruption after any write.
"""

import argparse
import fcntl
import hashlib
import os
import re
import sys
import tempfile
import time
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

# Default lock-acquire timeout in seconds.
# Raised with TimeoutError if another process holds the lock longer.
LOCK_TIMEOUT = 10.0

# ---------------------------------------------------------------------------
# Atomic file I/O + locking + checksums
# ---------------------------------------------------------------------------

def _lock_path(plan_path: str) -> str:
    """Return the lock file path for a given PLAN.md."""
    return plan_path + ".lock"


def _acquire_exclusive_lock(plan_path: str, timeout: float = LOCK_TIMEOUT) -> int:
    """Acquire an exclusive (write) advisory lock on the plan.

    Returns the file descriptor holding the lock.
    Caller must call _release_lock(fd) when done.

    The lock is held for the ENTIRE read-transform-write cycle so
    concurrent editors serialize deterministically — no lost updates.
    """
    fd = os.open(_lock_path(plan_path), os.O_CREAT | os.O_RDWR)
    # Write our PID so waiters can diagnose contention
    os.write(fd, str(os.getpid()).encode())
    os.lseek(fd, 0, os.SEEK_SET)

    deadline = time.monotonic() + timeout
    while True:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return fd
        except BlockingIOError:
            if time.monotonic() > deadline:
                os.lseek(fd, 0, os.SEEK_SET)
                holder_pid = os.read(fd, 32).decode().strip()
                os.close(fd)
                raise TimeoutError(
                    f"Lock on {plan_path} held by PID {holder_pid}, "
                    f"timeout after {timeout}s"
                )
            time.sleep(0.05)


def _acquire_shared_lock(plan_path: str) -> int:
    """Acquire a shared (read) advisory lock on the plan.

    Multiple readers coexist; blocks only when a writer holds LOCK_EX.
    Returns the file descriptor holding the lock.
    Caller must call _release_lock(fd) when done.
    """
    fd = os.open(_lock_path(plan_path), os.O_CREAT | os.O_RDWR)
    fcntl.flock(fd, fcntl.LOCK_SH)
    return fd


def _release_lock(fd: int) -> None:
    """Release an advisory lock and close its file descriptor."""
    fcntl.flock(fd, fcntl.LOCK_UN)
    os.close(fd)


def write_plan_atomic(path: str, content: str) -> None:
    """Write content to PLAN.md atomically.

    1. Write to a temp file in the SAME directory (same filesystem).
    2. fsync() to flush to disk — crash after this point is safe.
    3. rename() temp → target — atomic on same filesystem.
    4. Preserve original file permissions.

    After a crash: PLAN.md is either the old version or the new one,
    never partial. The orphaned .tmp is cleaned up next invocation.
    """
    p = Path(path)
    dir_ = p.parent
    content_bytes = content.encode("utf-8")

    fd, tmp_path = tempfile.mkstemp(
        dir=str(dir_), prefix=".plan.tmp.", suffix=".md"
    )
    closed = False
    try:
        written = os.write(fd, content_bytes)
        if written != len(content_bytes):
            raise IOError(
                f"Short write: {written} != {len(content_bytes)} bytes"
            )
        os.fsync(fd)
        os.close(fd)
        closed = True

        # Preserve permissions of original file if it exists
        if p.exists():
            st = p.stat()
            os.chmod(tmp_path, st.st_mode)

        os.rename(tmp_path, str(p))
    except BaseException:
        if not closed:
            try:
                os.close(fd)
            except OSError:
                pass
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise


def _cleanup_orphans(plan_path: str) -> None:
    """Remove stale .tmp files from crashed writes.

    Must be called under exclusive lock so no live writer is racing.
    """
    dir_ = Path(plan_path).parent
    for f in dir_.glob(".plan.tmp.*.md"):
        try:
            f.unlink()
        except FileNotFoundError:
            pass


# ---------------------------------------------------------------------------
# Checksums — content integrity verification
# ---------------------------------------------------------------------------

_CHECKSUM_RE = re.compile(r"^<!-- checksum: ([a-f0-9]{16}) -->$")


def _compute_checksum(content: str) -> str:
    """Compute a 16-char hex SHA-256 digest of content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _add_checksum(content: str) -> str:
    """Strip any old checksum line, then append a fresh one.

    The checksum covers everything in the file EXCEPT the checksum
    comment itself, so reads can verify integrity without self-
    reference issues.
    """
    lines = [
        l for l in content.splitlines()
        if not _CHECKSUM_RE.match(l.strip())
    ]
    # Rejoin preserving original line endings style (always \n)
    body = "\n".join(lines)
    if not body.endswith("\n"):
        body += "\n"
    checksum = _compute_checksum(body)
    return body + f"<!-- checksum: {checksum} -->\n"


def _strip_checksum(content: str) -> str:
    """Remove the checksum comment line from content."""
    return "\n".join(
        l for l in content.splitlines()
        if not _CHECKSUM_RE.match(l.strip())
    )


def _verify_checksum(content: str) -> bool:
    """Verify the file's integrity against its stored checksum.

    Returns True if checksum matches or file has no checksum yet
    (pre-atomic era). Returns False on mismatch (corruption detected).
    """
    lines = content.splitlines()
    stored = None
    for line in reversed(lines):
        m = _CHECKSUM_RE.match(line.strip())
        if m:
            stored = m.group(1)
            break
    if stored is None:
        return True  # No checksum — assume valid (new file or legacy)

    # Body is everything except the checksum line
    body_lines = [
        l for l in lines if not _CHECKSUM_RE.match(l.strip())
    ]
    body = "\n".join(body_lines)
    if not body.endswith("\n"):
        body += "\n"
    computed = _compute_checksum(body)
    return stored == computed


# ---------------------------------------------------------------------------
# Safe edit wrapper — lock → read → transform → write → unlock
# ---------------------------------------------------------------------------

def read_plan(path: str) -> str:
    """Read PLAN.md and return its contents (checksum stripped)."""
    p = Path(path)
    if not p.exists():
        print(f"Error: {path} does not exist", file=sys.stderr)
        sys.exit(1)
    raw = p.read_text(encoding="utf-8")
    return _strip_checksum(raw)


def read_plan_raw(path: str) -> str:
    """Read PLAN.md including the checksum line (for verification)."""
    p = Path(path)
    if not p.exists():
        print(f"Error: {path} does not exist", file=sys.stderr)
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def _safe_edit(plan_path: str, transform_fn) -> str:
    """Exclusive lock → read → transform → atomic write → unlock.

    The lock is held for the ENTIRE operation so concurrent editors
    serialize deterministically. No lost updates possible.

    Args:
        plan_path: Path to the PLAN.md file.
        transform_fn: Pure function(content: str) -> str that produces
                      the new file content (without checksum).

    Returns:
        The final written content (with checksum appended).
    """
    fd = _acquire_exclusive_lock(plan_path)
    try:
        # 1. Clean orphaned temp files from any prior crash
        _cleanup_orphans(plan_path)

        # 2. Read fresh content under lock (no one else can modify)
        raw = read_plan_raw(plan_path)

        # 3. Verify integrity
        if not _verify_checksum(raw):
            print(
                f"Warning: checksum mismatch in {plan_path} — "
                "file may be corrupted",
                file=sys.stderr,
            )

        content = _strip_checksum(raw)

        # 4. Transform (pure function, no I/O)
        new_content = transform_fn(content)

        # 5. Append checksum and write atomically
        final_content = _add_checksum(new_content)
        write_plan_atomic(plan_path, final_content)

        return final_content
    finally:
        _release_lock(fd)


def _safe_read(plan_path: str) -> str:
    """Shared lock → read → unlock.

    Readers don't block each other but block during writes, ensuring
    they never see partial state.
    """
    fd = _acquire_shared_lock(plan_path)
    try:
        raw = read_plan_raw(plan_path)
        if not _verify_checksum(raw):
            print(
                f"Warning: checksum mismatch in {plan_path} — "
                "file may be corrupted",
                file=sys.stderr,
            )
        return _strip_checksum(raw)
    finally:
        _release_lock(fd)


def write_plan(path: str, content: str) -> None:
    """Write content to PLAN.md atomically via temp file.

    Kept for backward compatibility / non-locked writes (e.g. cmd_create
    which creates a new file that doesn't need locking).
    """
    write_plan_atomic(path, content)


# ---------------------------------------------------------------------------
# Helpers — header parsing
# ---------------------------------------------------------------------------
# The header is NOT YAML; it's markdown bullet fields.
# We parse lines like:
#   - Depends On: ...
#   - Created: ...
#   - Updated: ...
#   - Current Phase: ...
#   - Current Task: ...

_HEADER_FIELDS = {
    "depends_on": r"^- Depends On:(.+)$",
    "created": r"^- Created:(.+)$",
    "updated": r"^- Updated:(.+)$",
    "current_phase": r"^- Current Phase:(.+)$",
    "current_task": r"^- Current Task:(.+)$",
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
    """Return index of line containing `- Field:` or -1."""
    pattern = rf"^- {re.escape(field_name)}:"
    for i, line in enumerate(lines):
        if re.match(pattern, line.strip()):
            return i
    return -1


def _update_header_field(lines: list[str], field_name: str, value: str) -> list[str]:
    """Update or append a header field line. Returns new lines."""
    pattern = rf"^- {re.escape(field_name)}:"
    idx = -1
    for i, line in enumerate(lines):
        if re.match(pattern, line.strip()):
            idx = i
            break
    if idx >= 0:
        lines[idx] = f"- {field_name}: {value}"
    else:
        # Insert after `- Current Task:` or before first phase heading
        current_task_idx = _find_header_field_line(lines, "Current Task")
        if current_task_idx >= 0:
            lines.insert(current_task_idx + 1, f"- {field_name}: {value}")
        else:
            # Find first ## Phase line and insert before it
            for i, line in enumerate(lines):
                if re.match(r"^## ", line):
                    lines.insert(i, f"- {field_name}: {value}")
                    break
            else:
                lines.append(f"- {field_name}: {value}")
    return lines


def _strip_header_comment(line: str) -> str:
    """Remove inline comment from header template line."""
    return re.sub(r"\s*<!--.*?-->\s*$", "", line).strip()


# ---------------------------------------------------------------------------
# Helpers — argument parsing (phase_ref / task_ref with optional description)
# ---------------------------------------------------------------------------

def parse_phase_arg(arg: str) -> int:
    """Extract phase number from a phase argument.

    Accepts: 'Phase 2', 'Phase 2 ➖ Description...'
    Returns: phase number (int).
    """
    # Split on first ' ➖ ' to strip optional description
    id_part = arg.split(" ➖ ", 1)[0].strip()
    m = re.match(r"Phase\s+(\d+)", id_part)
    if not m:
        print(f"Error: invalid phase ref: {arg!r}", file=sys.stderr)
        sys.exit(1)
    return int(m.group(1))


def parse_task_arg(arg: str) -> tuple[int, int]:
    """Extract (phase_num, task_num) from a task argument.

    Accepts: 'Task 2.4', 'Task 2.4 ➖ Description...'
    Returns: (phase_num, task_num).
    """
    id_part = arg.split(" ➖ ", 1)[0].strip()
    m = re.match(r"Task\s+(\d+)\.(\d+)", id_part)
    if not m:
        print(f"Error: invalid task ref: {arg!r}", file=sys.stderr)
        sys.exit(1)
    return int(m.group(1)), int(m.group(2))


def parse_phase_add_arg(arg: str) -> tuple[int, str]:
    """Parse add-phase argument. Returns (phase_num, title).

    If arg matches 'Phase N ➖ Title...', use explicit N.
    Otherwise treat entire arg as the title and return (0, title) for auto-numbering.
    """
    m = re.match(r"^Phase\s+\d+\s*➖\s+(.+)$", arg.strip())
    if m:
        # Has explicit phase number
        num_m = re.match(r"Phase\s+(\d+)", arg.strip())
        return int(num_m.group(1)), m.group(1).strip()
    return 0, arg.strip()


def parse_task_add_arg(arg: str) -> tuple[int, int, str]:
    """Parse add-task argument. Returns (phase_num, task_num, title).

    If arg matches 'Task X.Y ➖ Title...', use explicit numbers.
    Otherwise treat entire arg as the title and return (0, 0, title) for auto-numbering.
    """
    m = re.match(r"^Task\s+\d+\.\d+\s*➖\s+(.+)$", arg.strip())
    if m:
        num_m = re.match(r"Task\s+(\d+)\.(\d+)", arg.strip())
        return int(num_m.group(1)), int(num_m.group(2)), m.group(1).strip()
    return 0, 0, arg.strip()


# ---------------------------------------------------------------------------
# Helpers — plan title parsing
# ---------------------------------------------------------------------------

_TITLE_RE = re.compile(r"^#\s*(\u2610|\u2753|\u2699\uFE0F|\u274C|\u2611)?\s*Plan\s*➖\s*(.+)$")


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
    return f"# {emoji} Plan ➖ {title}"


# ---------------------------------------------------------------------------
# Helpers — phase parsing
# ---------------------------------------------------------------------------

_PHASE_RE = re.compile(r"^##\s*(\u2610|\u2753|\u2699\uFE0F|\u274C|\u2611)?\s*Phase\s+(\d+)\s*➖\s*(.+)$")


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
    return f"## {emoji} Phase {num} ➖ {title}"


# ---------------------------------------------------------------------------
# Helpers — task parsing
# ---------------------------------------------------------------------------

_TASK_RE = re.compile(
    r"^- (\u2610|\u2753|\u2699\uFE0F|\u274C|\u2611) Task (\d+)\.(\d+)\s*➖\s+(.+)$"
)

# Matches the ⚓ anchor dependency suffix at end of a task title.
# e.g. "Do thing ⚓ Task 2.1 , Task 2.2" → clean="Do thing", deps="Task 2.1 , Task 2.2"
_DEPS_ANCHOR_RE = re.compile(r"^(.+?)\s*⚓\s*(.+)$")

# Matches a single dependency reference: "Task X.Y" or "Phase X - Task X.Y"
_SINGLE_DEP_RE = re.compile(r"(?:Phase\s+\d+\s*-\s*)?Task\s+\d+\.\d+")


def parse_task_deps(raw_title: str) -> tuple[str, list[str]]:
    """Split a task title into (clean_title, [dependency_refs]).

    Handles titles like:
      - "Do thing" → ("Do thing", [])
      - "Do thing ⚓ Task 2.1 , Task 2.2" → ("Do thing", ["Task 2.1", "Task 2.2"])
      - "Do thing ⚓ Phase 3 - Task 3.1" → ("Do thing", ["Phase 3 - Task 3.1"])
    """
    m = _DEPS_ANCHOR_RE.match(raw_title.strip())
    if not m:
        return raw_title.strip(), []

    clean = m.group(1).strip()
    deps_str = m.group(2).strip()
    deps = [d.strip() for d in deps_str.split(",")]
    # Validate each dep ref looks like a task reference
    for d in deps:
        if not _SINGLE_DEP_RE.fullmatch(d):
            print(f"Warning: malformed dependency ref {d!r}", file=sys.stderr)
    return clean, deps


def format_task_deps(deps: list[str]) -> str:
    """Format dependency refs as ' ⚓ Task A.B , Task C.D' or empty string."""
    if not deps:
        return ""
    return " ⚓ " + " , ".join(deps)


def parse_task_line(line: str) -> tuple[str, int, int, str, list[str]] | None:
    """Return (emoji, phase_num, task_num, clean_title, [deps]) or None.

    clean_title does NOT include the ⚓ anchor suffix.
    deps is a list of dependency references (e.g. ["Task 2.1", "Phase 3 - Task 3.1"]).
    """
    m = _TASK_RE.match(line.strip())
    if not m:
        return None
    emoji = m.group(1)
    phase = int(m.group(2))
    task = int(m.group(3))
    raw_title = m.group(4).strip()
    clean_title, deps = parse_task_deps(raw_title)
    return emoji, phase, task, clean_title, deps


def format_task_line(emoji: str, phase_num: int, task_num: int, title: str, deps: list[str] | None = None) -> str:
    """Format a task line with optional ⚓ dependency anchor.

    title should be the clean title (without ⚓ suffix).
    deps is a list of dependency references.
    """
    suffix = format_task_deps(deps or [])
    return f"- {emoji} Task {phase_num}.{task_num} ➖ {title}{suffix}"


# ---------------------------------------------------------------------------
# Helpers — structure extraction
# ---------------------------------------------------------------------------

def extract_phases(content: str) -> list[tuple[str, int, str, list[tuple[str, int, int, str, list[str]]]]]:
    """Extract all phases with their tasks.

    Returns list of (emoji, phase_num, title, [(emoji, phase, task, clean_title, [deps]), ...]).
    """
    lines = content.splitlines()
    phases: list[tuple[str, int, str, list[tuple[str, int, int, str, list[str]]]]] = []
    current_phase: tuple[str, int, str] | None = None
    current_tasks: list[tuple[str, int, int, str, list[str]]] = []

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


def check_task_deps_satisfied(content: str, task_phase: int, task_num: int) -> bool:
    """Check if all dependencies of a task are in ☑ (Done) state.

    Returns True if satisfied (no deps or all deps are ☑), False otherwise.
    """
    lines = content.splitlines()
    phases = extract_phases("\n".join(lines))

    # Build a lookup: (phase, task) -> emoji
    task_status_map: dict[tuple[int, int], str] = {}
    for _, phase_num, _, tasks in phases:
        for t in tasks:
            task_status_map[(t[1], t[2])] = t[0]

    # Find the target task and its deps
    for _, phase_num, _, tasks in phases:
        for t in tasks:
            if t[1] == task_phase and t[2] == task_num:
                deps = t[4]  # list of dep refs like "Task 2.1" or "Phase 3 - Task 3.1"
                if not deps:
                    return True
                for dep_ref in deps:
                    dep_phase, dep_task = _resolve_dep_ref(dep_ref, task_phase)
                    if dep_phase is None:
                        continue  # malformed ref, skip
                    dep_status = task_status_map.get((dep_phase, dep_task))
                    if dep_status != STATUS_DONE:
                        return False
                return True

    return True  # task not found, let caller handle error


def _resolve_dep_ref(dep_ref: str, current_phase: int) -> tuple[int | None, int | None]:
    """Resolve a dependency reference to (phase_num, task_num).

    Handles:
      - "Task X.Y" → (X, Y)
      - "Phase X - Task X.Y" → (X, Y)
    """
    dep_ref = dep_ref.strip()
    # Cross-phase: "Phase X - Task X.Y"
    m = re.match(r"Phase\s+(\d+)\s*-\s*Task\s+(\d+)\.(\d+)", dep_ref)
    if m:
        return int(m.group(1)), int(m.group(3))
    # Same-phase or explicit: "Task X.Y"
    m = re.match(r"Task\s+(\d+)\.(\d+)", dep_ref)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


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

    content = f"""# {STATUS_TODO} Plan ➖ {title}
- Depends On: {deps_str}
- Created: {now}
- Updated: {now}
- Current Phase: NONE
- Current Task: NONE
"""
    # Atomically write the new file (no lock needed — file doesn't exist yet)
    final = _add_checksum(content)
    write_plan_atomic(path, final)
    print(f"Created {path}")

    # Check for dependency cycles
    if depends:
        check_dependency_cycle(path, depends)


# ---------------------------------------------------------------------------
# Commands — get (header reads)
# ---------------------------------------------------------------------------

def cmd_get_plan_title(args: argparse.Namespace) -> None:
    content = _safe_read(args.path)
    lines = content.splitlines()
    for line in lines:
        m = _TITLE_RE.match(line.strip())
        if m:
            print(m.group(2).strip())
            return
    print("Error: no plan title found", file=sys.stderr)
    sys.exit(1)


def cmd_get_plan_depends_on(args: argparse.Namespace) -> None:
    content = _safe_read(args.path)
    header = _parse_header("", content.splitlines())
    print(header.get("depends_on", "NONE"))


def cmd_get_plan_created(args: argparse.Namespace) -> None:
    content = _safe_read(args.path)
    header = _parse_header("", content.splitlines())
    print(header.get("created", ""))


def cmd_get_plan_updated(args: argparse.Namespace) -> None:
    content = _safe_read(args.path)
    header = _parse_header("", content.splitlines())
    print(header.get("updated", ""))


def cmd_get_plan_current_phase(args: argparse.Namespace) -> None:
    content = _safe_read(args.path)
    header = _parse_header("", content.splitlines())
    print(header.get("current_phase", "NONE"))


def cmd_get_plan_current_task(args: argparse.Namespace) -> None:
    content = _safe_read(args.path)
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
    def _transform(content: str) -> str:
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
        return content

    _safe_edit(args.path, _transform)
    print(f"Set plan title to: {args.title}")


def cmd_set_plan_depends_on(args: argparse.Namespace) -> None:
    deps = getattr(args, "deps", []) or []
    deps_str = "NONE" if not deps else " , ".join(deps)

    def _transform(content: str) -> str:
        lines = content.splitlines()
        lines = _update_header_field(lines, "Depends On", deps_str)
        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        return content

    _safe_edit(args.path, _transform)

    # Check for cycles (after write is committed)
    if deps:
        check_dependency_cycle(args.path, deps)
    print(f"Set depends on to: {deps_str}")


def cmd_set_plan_created(args: argparse.Namespace) -> None:
    val = args.value
    if val in ("--now", "__NOW__"):
        val = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _transform(content: str) -> str:
        lines = content.splitlines()
        lines = _update_header_field(lines, "Created", val)
        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        return content

    _safe_edit(args.path, _transform)
    print(f"Set created to: {val}")


def cmd_set_plan_updated(args: argparse.Namespace) -> None:
    val = args.value
    if val in ("--now", "__NOW__"):
        val = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _transform(content: str) -> str:
        lines = content.splitlines()
        lines = _update_header_field(lines, "Updated", val)
        content = "\n".join(lines)
        return content

    _safe_edit(args.path, _transform)
    print(f"Set updated to: {val}")


def cmd_set_plan_current_phase(args: argparse.Namespace) -> None:
    phase_ref = args.phase_ref  # e.g. "Phase 2" or "Phase 2 - Description..."
    target = parse_phase_arg(phase_ref)

    def _transform(content: str) -> str:
        lines = content.splitlines()

        # Find the phase and copy its emoji + full heading
        target_text = None
        for line in lines:
            m = parse_phase_heading(line)
            if m:
                emoji, num, title = m
                if num == target:
                    target_text = f"{emoji} Phase {num}"
                    break

        if target_text is None:
            print(f"Error: {phase_ref} not found", file=sys.stderr)
            sys.exit(1)

        lines = _update_header_field(lines, "Current Phase", target_text)
        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        return content

    # Resolve target_text before locking for the print message
    existing = read_plan(args.path)
    target_text = None
    for line in existing.splitlines():
        m = parse_phase_heading(line)
        if m and m[1] == target:
            target_text = f"{m[0]} Phase {m[1]}"
            break
    if target_text is None:
        print(f"Error: {phase_ref} not found", file=sys.stderr)
        sys.exit(1)

    _safe_edit(args.path, _transform)
    print(f"Set current phase to: {target_text}")


def cmd_set_plan_current_task(args: argparse.Namespace) -> None:
    task_ref = args.task_ref  # e.g. "Task 2.3" or "Task 2.3 - Description..."
    target_phase, target_task = parse_task_arg(task_ref)

    def _transform(content: str) -> str:
        lines = content.splitlines()

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
        return content

    # Resolve target_text before locking for the print message
    existing = read_plan(args.path)
    target_text = None
    for line in existing.splitlines():
        t = parse_task_line(line)
        if t and t[1] == target_phase and t[2] == target_task:
            target_text = f"{t[0]} Task {target_phase}.{target_task}"
            break
    if target_text is None:
        print(f"Error: {task_ref} not found", file=sys.stderr)
        sys.exit(1)

    _safe_edit(args.path, _transform)
    print(f"Set current task to: {target_text}")


# ---------------------------------------------------------------------------
# Commands — status reads
# ---------------------------------------------------------------------------

def cmd_get_plan_status(args: argparse.Namespace) -> None:
    content = _safe_read(args.path)
    lines = content.splitlines()
    for line in lines:
        m = _TITLE_RE.match(line.strip())
        if m:
            print(m.group(1) or STATUS_TODO)
            return
    print(STATUS_TODO)


def cmd_get_phase_status(args: argparse.Namespace) -> None:
    content = _safe_read(args.path)
    phase_ref = args.phase_ref  # e.g. "Phase 2" or "Phase 2 - Description..."
    lines = content.splitlines()
    target = parse_phase_arg(phase_ref)

    for line in lines:
        p = parse_phase_heading(line)
        if p and p[1] == target:
            print(p[0])
            return
    print(f"Error: {phase_ref} not found", file=sys.stderr)
    sys.exit(1)


def cmd_get_task_status(args: argparse.Namespace) -> None:
    content = _safe_read(args.path)
    task_ref = args.task_ref  # e.g. "Task 2.3" or "Task 2.3 - Description..."
    lines = content.splitlines()
    target_phase, target_task = parse_task_arg(task_ref)

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
    new_status = args.status

    if new_status not in ALL_STATUSES:
        print(f"Error: invalid status {new_status!r}", file=sys.stderr)
        sys.exit(1)

    def _transform(content: str) -> str:
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
                lines[i] = format_task_line(new_status, t[1], t[2], t[3], t[4])

        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        return content

    _safe_edit(args.path, _transform)
    print(f"Set all statuses to: {new_status}")


def cmd_set_plan_status(args: argparse.Namespace) -> None:
    """Set plan status (emoji in title)."""
    new_status = args.status

    if new_status not in ALL_STATUSES:
        print(f"Error: invalid status {new_status!r}", file=sys.stderr)
        sys.exit(1)

    def _transform(content: str) -> str:
        lines = content.splitlines()
        for i, line in enumerate(lines):
            m = _TITLE_RE.match(line.strip())
            if m:
                title_text = m.group(2).strip()
                lines[i] = format_plan_title(new_status, title_text)
                break

        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        return content

    _safe_edit(args.path, _transform)
    print(f"Set plan status to: {new_status}")


def cmd_set_phase_status(args: argparse.Namespace) -> None:
    """Set phase status (emoji in heading)."""
    phase_ref = args.phase_ref  # e.g. "Phase 2" or "Phase 2 - Description..."
    new_status = args.status

    if new_status not in ALL_STATUSES:
        print(f"Error: invalid status {new_status!r}", file=sys.stderr)
        sys.exit(1)

    target = parse_phase_arg(phase_ref)

    def _transform(content: str) -> str:
        lines = content.splitlines()
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
                break
        else:
            print(f"Error: {phase_ref} not found", file=sys.stderr)
            sys.exit(1)

        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        return content

    _safe_edit(args.path, _transform)
    print(f"Set {phase_ref} status to: {new_status}")


def cmd_set_task_status(args: argparse.Namespace) -> None:
    """Set task status (emoji in task line)."""
    task_ref = args.task_ref  # e.g. "Task 2.3" or "Task 2.3 - Description..."
    new_status = args.status

    if new_status not in ALL_STATUSES:
        print(f"Error: invalid status {new_status!r}", file=sys.stderr)
        sys.exit(1)

    target_phase, target_task = parse_task_arg(task_ref)

    def _transform(content: str) -> str:
        lines = content.splitlines()
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
                # Check dependency satisfaction before transitioning to ⚙️ (Doing)
                if new_status == STATUS_DOING:
                    if not check_task_deps_satisfied(content, target_phase, target_task):
                        print(
                            f"Error: cannot start {task_ref} — dependencies not satisfied (all deps must be {STATUS_DONE})",
                            file=sys.stderr,
                        )
                        sys.exit(1)
                lines[i] = format_task_line(new_status, t[1], t[2], t[3], t[4])
                break
        else:
            print(f"Error: {task_ref} not found", file=sys.stderr)
            sys.exit(1)

        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        # Re-derive phase and plan statuses
        content = validate_status_set(content)
        return content

    _safe_edit(args.path, _transform)
    print(f"Set {task_ref} status to: {new_status}")


# ---------------------------------------------------------------------------
# Commands — Phase CRUD
# ---------------------------------------------------------------------------

def cmd_add_phase(args: argparse.Namespace) -> None:
    """Add a new phase at the end of the plan."""
    phase_arg = args.phase_title  # e.g. "Phase 2 - Description..." or just "Description..."
    description = getattr(args, "description", "") or ""

    # Resolve title before locking (pure computation from user input)
    explicit_num, title = parse_phase_add_arg(phase_arg)
    # phase_num is resolved inside _transform since it depends on existing content

    def _transform(content: str) -> str:
        lines = content.splitlines()
        phases = extract_phases(content)

        nonlocal explicit_num
        if explicit_num > 0:
            phase_num = explicit_num
        else:
            phase_num = len(phases) + 1

        # Build new phase section
        new_phase_lines = [
            "",
            format_phase_heading(STATUS_TODO, phase_num, title),
        ]
        if description:
            new_phase_lines.append(description)

        content = "\n".join(lines) + "\n" + "\n".join(new_phase_lines) + "\n"
        content = _touch_updated(args.path, content)
        return content

    # For explicit numbers, we know phase_num ahead of time.
    # For auto-numbering, read current phase count to report accurately.
    if explicit_num > 0:
        phase_num = explicit_num
    else:
        existing = read_plan(args.path)
        phase_num = len(extract_phases(existing)) + 1

    _safe_edit(args.path, _transform)
    print(f"Added Phase {phase_num} ({title}) with status {STATUS_TODO}")


def cmd_update_phase(args: argparse.Namespace) -> None:
    """Update phase description/title."""
    phase_ref = args.phase_ref  # e.g. "Phase 2" or "Phase 2 - Description..."
    new_description = args.description

    target = parse_phase_arg(phase_ref)

    def _transform(content: str) -> str:
        lines = content.splitlines()

        # Verify phase exists
        found = False
        for line in lines:
            p = parse_phase_heading(line)
            if p and p[1] == target:
                found = True
                break

        if not found:
            print(f"Error: {phase_ref} not found", file=sys.stderr)
            sys.exit(1)

        # Replace the phase heading line's title
        for i, line in enumerate(lines):
            p = parse_phase_heading(line)
            if p and p[1] == target:
                current_emoji = p[0]
                lines[i] = format_phase_heading(current_emoji, target, new_description)
                break

        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        content = validate_status_set(content)
        return content

    _safe_edit(args.path, _transform)
    print(f"Updated {phase_ref} description to: {new_description}")


def cmd_remove_phase(args: argparse.Namespace) -> None:
    """Remove a phase and all its tasks."""
    phase_ref = args.phase_ref  # e.g. "Phase 2" or "Phase 2 - Description..."

    target = parse_phase_arg(phase_ref)

    def _transform(content: str) -> str:
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
        return content

    _safe_edit(args.path, _transform)
    print(f"Removed {phase_ref}")


# ---------------------------------------------------------------------------
# Commands — Task CRUD
# ---------------------------------------------------------------------------

def cmd_add_task(args: argparse.Namespace) -> None:
    """Add a new task to an existing phase."""
    phase_ref = args.phase_ref  # e.g. "Phase 2" or "Phase 2 - Description..."
    task_arg = args.task_title  # e.g. "Task 2.4 ➖ Do thing ⚓ Task 2.1 , Task 2.2" or just "Do thing"

    target_phase = parse_phase_arg(phase_ref)
    explicit_p, explicit_t, raw_title = parse_task_add_arg(task_arg)

    # Split raw_title into clean title and deps
    clean_title, deps = parse_task_deps(raw_title)

    if explicit_p > 0 and explicit_t > 0:
        task_phase = explicit_p
        task_num = explicit_t
    else:
        task_phase = target_phase
        # Pre-read to determine task number for the print message
        existing = read_plan(args.path)
        phases = extract_phases(existing)
        max_task = 0
        for emoji, num, t_title, tasks in phases:
            if num == target_phase:
                for t in tasks:
                    if t[2] > max_task:
                        max_task = t[2]
        task_num = max_task + 1

    task_title = f"Task {task_phase}.{task_num} {clean_title}"

    def _transform(content: str) -> str:
        lines = content.splitlines()
        phases = extract_phases(content)

        # Re-resolve task_num inside transform (content may differ from pre-read)
        if explicit_p > 0 and explicit_t > 0:
            tp = explicit_p
            tn = explicit_t
        else:
            tp = target_phase
            max_task = 0
            for emoji, num, t_title, tasks in phases:
                if num == target_phase:
                    for t in tasks:
                        if t[2] > max_task:
                            max_task = t[2]
            tn = max_task + 1

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

        task_line = format_task_line(STATUS_TODO, tp, tn, clean_title, deps)
        lines.insert(insert_idx, task_line)

        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        content = validate_status_set(content)
        return content

    _safe_edit(args.path, _transform)
    print(f"Added {task_title} to {phase_ref} with status {STATUS_TODO}")


def cmd_update_task(args: argparse.Namespace) -> None:
    """Update task description (preserves existing dependencies)."""
    phase_ref = args.phase_ref  # e.g. "Phase 2" or "Phase 2 - Description..."
    task_ref = args.task_ref  # e.g. "Task 2.4" or "Task 2.4 - Description..."
    new_description = args.description

    target_phase, target_task = parse_task_arg(task_ref)

    def _transform(content: str) -> str:
        lines = content.splitlines()
        for i, line in enumerate(lines):
            t = parse_task_line(line)
            if t and t[1] == target_phase and t[2] == target_task:
                # Build new task line with updated title, preserving deps
                current_emoji = t[0]
                existing_deps = t[4]
                lines[i] = format_task_line(current_emoji, target_phase, target_task, new_description, existing_deps)
                break
        else:
            print(f"Error: {task_ref} not found in {phase_ref}", file=sys.stderr)
            sys.exit(1)

        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        content = validate_status_set(content)
        return content

    _safe_edit(args.path, _transform)
    print(f"Updated {task_ref} description to: {new_description}")


def cmd_remove_task(args: argparse.Namespace) -> None:
    """Remove a task from a phase."""
    phase_ref = args.phase_ref  # e.g. "Phase 2" or "Phase 2 - Description..."
    task_ref = args.task_ref  # e.g. "Task 2.4" or "Task 2.4 - Description..."

    target_phase, target_task = parse_task_arg(task_ref)

    def _transform(content: str) -> str:
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
        return content

    _safe_edit(args.path, _transform)
    print(f"Removed {task_ref}")


# ---------------------------------------------------------------------------
# Helpers — task dependency cycle detection
# ---------------------------------------------------------------------------

def _build_task_dep_graph(phases) -> dict[tuple[int, int], list[tuple[int, int]]]:
    """Build a task dependency graph from extracted phases.

    Returns dict mapping (phase, task) -> [(dep_phase, dep_task), ...].
    """
    graph: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for _, phase_num, _, tasks in phases:
        for t in tasks:
            # t = (emoji, phase, task, clean_title, deps)
            key = (t[1], t[2])
            dep_targets = []
            for dep_ref in t[4]:
                dp, dt = _resolve_dep_ref(dep_ref, t[1])
                if dp is not None:
                    dep_targets.append((dp, dt))
            graph[key] = dep_targets
    return graph


def _check_task_dep_cycle(graph: dict[tuple[int, int], list[tuple[int, int]]], new_dep_from: tuple[int, int], new_dep_to: tuple[int, int]) -> None:
    """Check if adding an edge from new_dep_from -> new_dep_to would create a cycle.

    A cycle exists if new_dep_to (or any of its transitive dependencies)
    can reach back to new_dep_from.

    Exits with error if cycle detected.
    """
    # BFS/DFS from new_dep_to through existing edges, see if we reach new_dep_from
    visited = set()
    stack = [new_dep_to]

    while stack:
        current = stack.pop()
        if current == new_dep_from:
            from_p, from_t = new_dep_from
            to_p, to_t = new_dep_to
            print(
                f"Error: adding dependency Task {from_p}.{from_t} -> Task {to_p}.{to_t} "
                f"would create a dependency cycle",
                file=sys.stderr,
            )
            sys.exit(1)
        if current in visited:
            continue
        visited.add(current)
        for dep_target in graph.get(current, []):
            stack.append(dep_target)


# ---------------------------------------------------------------------------
# Commands — add-task-dependency / remove-task-dependency
# ---------------------------------------------------------------------------

def cmd_add_task_dependency(args: argparse.Namespace) -> None:
    """Add a dependency to an existing task.

    Takes: phase_ref, task_ref (the task to modify), dep_task_ref (the dependency).
    Appends dep_task_ref to the ⚓ anchor of task_ref.

    State logic: if the target task's status is ☐ after modification, plan and
    phase statuses remain derived as ☐ (via validate_status_set). Otherwise,
    validate_status_set derives the correct status from actual task states.
    """
    phase_ref = args.phase_ref
    task_ref = args.task_ref
    dep_task_ref = args.dep_task_ref

    target_phase, target_task = parse_task_arg(task_ref)

    # Validate that dep_task_ref is a valid task reference
    dep_phase, dep_task = parse_task_arg(dep_task_ref)

    # Build the canonical dep ref string for comparison
    # If dep is in same phase as target, use "Task X.Y" form
    # If different phase, use "Phase X - Task X.Y" form
    if dep_phase == target_phase:
        canonical_dep = f"Task {dep_phase}.{dep_task}"
    else:
        canonical_dep = f"Phase {dep_phase} - Task {dep_phase}.{dep_task}"

    def _transform(content: str) -> str:
        lines = content.splitlines()
        phases = extract_phases(content)

        # Verify target task exists
        target_found = False
        for _, phase_num, _, tasks in phases:
            for t in tasks:
                if t[1] == target_phase and t[2] == target_task:
                    target_found = True
                    break
        if not target_found:
            print(f"Error: {task_ref} not found in {phase_ref}", file=sys.stderr)
            sys.exit(1)

        # Verify dependency task exists
        dep_found = False
        for _, phase_num, _, tasks in phases:
            for t in tasks:
                if t[1] == dep_phase and t[2] == dep_task:
                    dep_found = True
                    break
        if not dep_found:
            print(f"Error: dependency {dep_task_ref} not found", file=sys.stderr)
            sys.exit(1)

        # Build current dependency graph for cycle detection (before adding new edge)
        graph = _build_task_dep_graph(phases)

        # Check for cycles: adding edge from (target_phase, target_task) -> (dep_phase, dep_task)
        # means target depends on dep. A cycle exists if dep (or its transitive deps) can reach target.
        _check_task_dep_cycle(graph, (target_phase, target_task), (dep_phase, dep_task))

        # Now update the task line
        for i, line in enumerate(lines):
            t = parse_task_line(line)
            if t and t[1] == target_phase and t[2] == target_task:
                current_deps = list(t[4])  # existing deps

                # Check for duplicate (compare canonical forms)
                if canonical_dep in current_deps:
                    print(
                        f"Error: {task_ref} already depends on {dep_task_ref}",
                        file=sys.stderr,
                    )
                    sys.exit(1)

                # Also check self-dependency
                if target_phase == dep_phase and target_task == dep_task:
                    print(
                        f"Error: task cannot depend on itself",
                        file=sys.stderr,
                    )
                    sys.exit(1)

                current_deps.append(canonical_dep)
                lines[i] = format_task_line(t[0], t[1], t[2], t[3], current_deps)
                break

        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        content = validate_status_set(content)
        return content

    _safe_edit(args.path, _transform)
    print(f"Added dependency: {task_ref} -> {dep_task_ref}")


def cmd_remove_task_dependency(args: argparse.Namespace) -> None:
    """Remove a dependency from an existing task.

    Takes: phase_ref, task_ref (the task to modify), dep_task_ref (the dependency to remove).
    Removes dep_task_ref from the ⚓ anchor of task_ref.

    State logic: if the target task's status is ☐ after modification, plan and
    phase statuses remain derived as ☐ (via validate_status_set). Otherwise,
    validate_status_set derives the correct status from actual task states.
    """
    phase_ref = args.phase_ref
    task_ref = args.task_ref
    dep_task_ref = args.dep_task_ref

    target_phase, target_task = parse_task_arg(task_ref)
    dep_phase, dep_task = parse_task_arg(dep_task_ref)

    # Build the canonical dep ref string for comparison
    if dep_phase == target_phase:
        canonical_dep = f"Task {dep_phase}.{dep_task}"
    else:
        canonical_dep = f"Phase {dep_phase} - Task {dep_phase}.{dep_task}"

    def _transform(content: str) -> str:
        lines = content.splitlines()

        # Verify target task exists
        phases = extract_phases(content)
        target_found = False
        for _, phase_num, _, tasks in phases:
            for t in tasks:
                if t[1] == target_phase and t[2] == target_task:
                    target_found = True
                    break
        if not target_found:
            print(f"Error: {task_ref} not found in {phase_ref}", file=sys.stderr)
            sys.exit(1)

        # Find and update the task line
        removed = False
        for i, line in enumerate(lines):
            t = parse_task_line(line)
            if t and t[1] == target_phase and t[2] == target_task:
                current_deps = list(t[4])

                # Check if dependency actually exists
                # Compare against canonical form and also raw forms (in case of format mismatch)
                found_dep = False
                for raw_dep in current_deps:
                    rd_phase, rd_task = _resolve_dep_ref(raw_dep, target_phase)
                    if rd_phase == dep_phase and rd_task == dep_task:
                        found_dep = True
                        break

                if not found_dep:
                    print(
                        f"Error: {task_ref} does not depend on {dep_task_ref}",
                        file=sys.stderr,
                    )
                    sys.exit(1)

                # Remove matching deps (could have both "Task X.Y" and "Phase X - Task X.Y" forms)
                new_deps = [
                    d for d in current_deps
                    if _resolve_dep_ref(d, target_phase) != (dep_phase, dep_task)
                ]

                lines[i] = format_task_line(t[0], t[1], t[2], t[3], new_deps)
                removed = True
                break

        if not removed:
            print(f"Error: {task_ref} not found in {phase_ref}", file=sys.stderr)
            sys.exit(1)

        content = "\n".join(lines)
        content = _touch_updated(args.path, content)
        content = validate_status_set(content)
        return content

    _safe_edit(args.path, _transform)
    print(f"Removed dependency: {task_ref} -> {dep_task_ref}")


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

    # --- task dependency management ---
    p_add_dep = sub.add_parser("add-task-dependency", help="Add a dependency to a task")
    p_add_dep.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2"')
    p_add_dep.add_argument("task_ref", help='Task reference, e.g. "Task 2.4"')
    p_add_dep.add_argument("dep_task_ref", help='Dependency task reference, e.g. "Task 2.1"')

    p_rm_dep = sub.add_parser("remove-task-dependency", help="Remove a dependency from a task")
    p_rm_dep.add_argument("phase_ref", help='Phase reference, e.g. "Phase 2"')
    p_rm_dep.add_argument("task_ref", help='Task reference, e.g. "Task 2.4"')
    p_rm_dep.add_argument("dep_task_ref", help='Dependency task reference, e.g. "Task 2.1"')

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
    "add-task-dependency": cmd_add_task_dependency,
    "remove-task-dependency": cmd_remove_task_dependency,
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
